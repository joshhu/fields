"""Assemble the final 1080p documentary from narration, animations, images and videos.

Usage: uv run python pipeline/compose.py [--only s03_maxwell] [--preview]
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from timeline import LEAD, TAIL, allocate, parse_visual, pauses, subtitle_chunks  # noqa: E402
from tts import load_scenes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
BUILD = ROOT / "build"
CLIPS = BUILD / "clips"
SCENES = BUILD / "scenes"
OUTPUT = ROOT / "output"
W, H, FPS = 1920, 1080, 30
XF = 0.6           # crossfade between visuals inside a scene
CREDITS_DUR = 22.0
FONT_B = "C:/Windows/Fonts/msjhbd.ttc"
FONT_R = "C:/Windows/Fonts/msjh.ttc"
ACCENT = (79, 195, 247)
ENC = ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "17", "-b:v", "0",
       "-pix_fmt", "yuv420p", "-r", str(FPS)]

CAPTIONS = {
    "newton": "艾薩克．牛頓（1642–1727）",
    "principia": "《自然哲學的數學原理》，1687 年",
    "faraday": "麥可．法拉第（1791–1867）",
    "iron_filings": "鐵屑排列出磁鐵周圍的「力線」",
    "faraday_lab": "法拉第與皇家研究院",
    "maxwell": "詹姆斯．克拉克．馬克士威（1831–1879）",
    "hertz": "海因里希．赫茲（1857–1894）",
    "michelson": "阿爾伯特．邁克生（1852–1931）",
    "einstein_1905": "愛因斯坦，約 1905 年",
    "einstein": "阿爾伯特．愛因斯坦（1879–1955）",
    "eclipse_1919": "1919 年日食：光線被重力彎曲的觀測",
    "schrodinger": "埃爾溫．薛丁格（1887–1961）",
    "dirac": "保羅．狄拉克（1902–1984）",
    "positron": "1932 年安德森在雲霧室拍到的正電子軌跡",
    "heisenberg": "維爾納．海森堡（1901–1976）",
    "solvay_1927": "1927 年第五屆索爾維會議",
    "fermi": "恩里科．費米（1901–1954）",
    "feynman": "理查．費曼（1918–1988）",
    "tomonaga": "朝永振一郎（1906–1979）",
    "schwinger": "朱利安．施溫格（1918–1994）",
    "wilson": "肯尼斯．威爾森（1936–2013）",
    "yang": "楊振寧（1922–2025）",
    "pauli": "沃夫岡．包立（1900–1958）",
    "oppenheimer": "羅伯特．歐本海默（1904–1967）",
    "higgs": "彼得．希格斯（1929–2024）",
    "noether": "艾米．諾特（1882–1935）",
    "hawking": "史蒂芬．霍金（1942–2018）",
    "m87": "事件視界望遠鏡拍攝的 M87* 黑洞，2019 年",
    "cmb": "普朗克衛星觀測的宇宙微波背景",
    "lhc_detector": "CERN 大型強子對撞機的偵測器",
}


# credit-roll labels for footage and music (images reuse CAPTIONS)
CREDIT_LABELS = {
    "galaxy": "影片：哈伯傳承場深空影像",
    "earth_orbit": "影片：太陽系行星運行",
    "sun": "影片：太陽超高畫質影像",
    "black_hole": "影片：雙黑洞重力透鏡模擬",
    "lhc": "影片：同步加速器動畫",
    "earth": "影片：國際太空站拍攝的地球縮時",
    "ambient1": "配樂：Ambient (10 minutes)",
    "ambient2": "配樂：Ambient Seattle 2024",
}

# fractional crop boxes (l, t, r, b) for images with printed captions etc.
CROP = {"heisenberg": (0.04, 0.017, 0.966, 0.826)}
# cap on displayed foreground height (output px) for low-resolution sources
FG_MAX_H = {"wilson": 620}


# ---------------------------------------------------------------- helpers
def run(cmd: list[str], **kw) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))[:400]}\n{r.stderr[-2000:]}")


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(path)], text=True)
    return float(out.strip())


def find_asset(kind: str, name: str) -> Path | None:
    folder = {"anim": "anim", "img": "img", "vid": "vid"}[kind]
    for ext in ((".mp4",) if kind != "img" else (".jpg", ".jpeg", ".png", ".webp")):
        p = ASSETS / folder / f"{name}{ext}"
        if p.exists():
            return p
    return None


def ease(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0.0), 1.0))


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- image clips
def _base_canvas(img: Image.Image, scale: float, max_h: int | None = None) -> Image.Image:
    """Image on a 16:9 canvas (scale x output size): cover if near 16:9, else blurred-bg contain."""
    cw, ch = int(W * scale), int(H * scale)
    ar = img.width / img.height
    if 1.45 <= ar <= 2.1:
        r = max(cw / img.width, ch / img.height)
        im = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.LANCZOS)
        x, y = (im.width - cw) // 2, (im.height - ch) // 2
        return im.crop((x, y, x + cw, y + ch))
    r = max(cw / img.width, ch / img.height)
    bg = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.BILINEAR)
    x, y = (bg.width - cw) // 2, (bg.height - ch) // 2
    bg = bg.crop((x, y, x + cw, y + ch)).filter(ImageFilter.GaussianBlur(40 * scale))
    bg = Image.blend(bg, Image.new("RGB", bg.size, (8, 12, 26)), 0.55)
    r = min(cw * 0.86 / img.width, ch * 0.86 / img.height)
    if max_h:
        r = min(r, max_h * scale / img.height)
    fg = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
    shadow = Image.new("L", (fg.width + 80, fg.height + 80), 0)
    ImageDraw.Draw(shadow).rectangle((40, 40, fg.width + 40, fg.height + 40), fill=170)
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    px, py = (cw - fg.width) // 2, int((ch - fg.height) * 0.42)
    bg.paste((0, 0, 0), (px - 40 + 10, py - 40 + 14), shadow)
    bg.paste(fg, (px, py))
    return bg


def _caption_layer(text: str) -> Image.Image:
    f = font(FONT_B, 38)
    tw = int(f.getlength(text))
    layer = Image.new("RGBA", (tw + 70, 68), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((0, 0, tw + 69, 67), radius=10, fill=(10, 16, 34, 200))
    d.rectangle((0, 0, 7, 67), fill=ACCENT + (255,))
    d.text((32, 11), text, font=f, fill=(236, 239, 241, 255))
    return layer


def render_image_clip(src: Path, dur: float, out: Path, caption: str | None, variant: int) -> None:
    img = Image.open(src).convert("RGB")
    if src.stem in CROP:
        l, t, r, b = CROP[src.stem]
        img = img.crop((int(l * img.width), int(t * img.height), int(r * img.width), int(b * img.height)))
    scale = 1.5
    base = _base_canvas(img, scale, FG_MAX_H.get(src.stem))
    cap = _caption_layer(caption) if caption else None
    n = int(round(dur * FPS))
    zoom0, zoom1 = (1.0, 1.10) if variant % 2 == 0 else (1.10, 1.0)
    dx = [0.03, -0.03, 0.0, 0.02][variant % 4]
    dy = [0.0, 0.015, -0.02, 0.01][variant % 4]
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", *ENC, str(out)], stdin=subprocess.PIPE)
    bw, bh = base.size
    for i in range(n):
        t = ease(i / max(n - 1, 1))
        z = zoom0 + (zoom1 - zoom0) * t
        vw, vh = bw / z, bh / z
        cx = bw / 2 + dx * bw * (t - 0.5)
        cy = bh / 2 + dy * bh * (t - 0.5)
        x0, y0 = cx - vw / 2, cy - vh / 2
        x0 = min(max(x0, 0), bw - vw)
        y0 = min(max(y0, 0), bh - vh)
        sx = vw / W
        frame = base.transform((W, H), Image.AFFINE, (sx, 0, x0, 0, sx, y0), resample=Image.BICUBIC)
        if cap is not None:
            ti = i / FPS
            a = min(1.0, max(0.0, (ti - 0.5) / 0.5)) * min(1.0, max(0.0, (dur - 0.4 - ti) / 0.5))
            if a > 0:
                c = cap.copy()
                c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
                frame.paste(c, (64, 840), c)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"image clip failed: {src}")


# ---------------------------------------------------------------- video / anim clips
def render_video_clip(src: Path, dur: float, out: Path, kind: str) -> None:
    length = probe_duration(src)
    vf = [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}", "setsar=1"]
    inp = ["-i", str(src)]
    if kind == "anim":
        ratio = length / dur
        if ratio > 1.0:
            # play the whole animation slightly faster if it is a bit long, else trim
            if ratio <= 1.35:
                vf.append(f"setpts=PTS/{ratio:.5f}")
        else:
            if ratio >= 0.8:
                vf.append(f"setpts=PTS/{ratio:.5f}")
            else:
                vf.append(f"setpts=PTS/0.8,tpad=stop_mode=clone:stop_duration={dur:.3f}")
    else:
        if length < dur:
            if length / dur >= 0.7:
                vf.append(f"setpts=PTS/{length / dur:.5f}")
            else:
                inp = ["-stream_loop", "-1", "-i", str(src)]
    vf.append(f"fps={FPS}")
    run(["ffmpeg", "-v", "error", "-y", *inp, "-t", f"{dur:.3f}", "-an", "-vf", ",".join(vf), *ENC, str(out)])


def render_placeholder(name: str, dur: float, out: Path) -> None:
    img = Image.new("RGB", (W, H), (11, 16, 32))
    d = ImageDraw.Draw(img)
    d.text((W // 2, H // 2), f"[{name}]", font=font(FONT_B, 60), fill=(120, 140, 160), anchor="mm")
    p = out.with_suffix(".png")
    img.save(p)
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(p), "-t", f"{dur:.3f}", *ENC, str(out)])


def render_clip(job: dict) -> str:
    out = Path(job["out"])
    kind, name, dur = job["kind"], job["name"], job["dur"]
    sig = json.dumps(job, sort_keys=True)
    sig_file = out.with_suffix(".sig")
    src = find_asset(kind, name)
    sig += str(src.stat().st_mtime if src else "missing")
    if out.exists() and sig_file.exists() and sig_file.read_text(encoding="utf-8") == sig:
        return f"cached {out.name}"
    if src is None:
        render_placeholder(f"{kind}:{name}", dur, out)
    elif kind == "img":
        render_image_clip(src, dur, out, CAPTIONS.get(name), job["variant"])
    else:
        render_video_clip(src, dur, out, kind)
    sig_file.write_text(sig, encoding="utf-8")
    return f"rendered {out.name}" + ("" if src else " (PLACEHOLDER)")


# ---------------------------------------------------------------- chapter cards
def chapter_card(title: str, out: Path) -> None:
    f = font(FONT_B, 50)
    tw = int(f.getlength(title))
    img = Image.new("RGBA", (tw + 110, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, tw + 109, 99), radius=14, fill=(10, 16, 34, 215))
    d.rectangle((0, 0, 9, 99), fill=ACCENT + (255,))
    d.text((48, 18), title, font=f, fill=(236, 239, 241, 255))
    img.save(out)


# ---------------------------------------------------------------- scene assembly
def build_scene(scene: dict, plan: dict) -> Path:
    out = SCENES / f"{scene['id']}.mp4"
    clips = plan["clips"]
    D = plan["duration"]
    inputs, filt = [], []
    for c in clips:
        inputs += ["-i", c["out"]]
    n = len(clips)
    last = "[0:v]"
    for k in range(1, n):
        lbl = f"[x{k}]"
        filt.append(f"{last}[{k}:v]xfade=transition=fade:duration={XF}:offset={clips[k]['start']:.3f}{lbl}")
        last = lbl
    idx = n
    if scene.get("title") and scene["id"] != "s00_intro" and scene.get("card") != "none":
        card = BUILD / "cards" / f"{scene['id']}.png"
        chapter_card(scene["title"], card)
        inputs += ["-loop", "1", "-t", f"{D:.3f}", "-i", str(card)]
        filt.append(f"[{idx}:v]format=rgba,fade=in:st=0.3:d=0.6:alpha=1,fade=out:st=5.0:d=0.7:alpha=1[card]")
        cx = {"left": "60", "center": "(W-w)/2", "right": "W-w-60"}[scene.get("card", "left")]
        filt.append(f"{last}[card]overlay={cx}:50:shortest=1[ov]")
        last = "[ov]"
    filt.append(f"{last}fade=in:st=0:d=0.4,fade=out:st={D - 0.45:.3f}:d=0.45,format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[v]",
         "-t", f"{D:.3f}", *ENC, str(out)])
    return out


def scene_audio(scene: dict, D: float) -> Path:
    out = BUILD / "audio_scene" / f"{scene['id']}.wav"
    src = BUILD / "audio" / f"{scene['id']}.mp3"
    ms = int(LEAD * 1000)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
         f"adelay={ms}|{ms},apad=whole_dur={D:.3f}", "-ac", "2", "-ar", "48000", "-t", f"{D:.3f}", str(out)])
    return out


# ---------------------------------------------------------------- credits
def build_credits(out: Path) -> None:
    credits_path = ASSETS / "credits.json"
    items = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else []
    lines: list[tuple[str, int, tuple]] = [("場比粒子更基本", 64, (236, 239, 241)), ("", 30, (0, 0, 0)),
                                           ("旁白配音　Microsoft Edge TTS（zh-TW YunJhe）", 34, (176, 190, 197)),
                                           ("動畫製作　Manim Community Edition", 34, (176, 190, 197)),
                                           ("", 30, (0, 0, 0)), ("素材來源", 44, ACCENT)]
    used = {name for s in load_scenes() for v in s["visuals"] for kind, name, _ in [parse_visual(v)] if kind != "anim"}
    for it in items:
        if it.get("kind") in ("img", "vid", "image", "video") and it.get("key") not in used:
            continue
        author = (it.get("author") or "").strip()
        if len(author) > 70:
            author = author[:67].rsplit(" ", 1)[0] + " 等"
        lic = (it.get("license") or "").strip()
        key = it.get("key", "")
        title = CREDIT_LABELS.get(key) or CAPTIONS.get(key) or (it.get("title") or key).strip()
        if len(title) > 60:
            title = title[:57] + "…"
        lines.append((title, 28, (236, 239, 241)))
        lines.append((f"{author}　｜　{lic}" if author else lic, 24, (144, 164, 174)))
    lines += [("", 40, (0, 0, 0)), ("感謝收看", 56, (236, 239, 241))]
    heights = [int(s * 1.7) for _, s, _ in lines]
    tall = Image.new("RGB", (W, sum(heights) + H * 2), (11, 16, 32))
    d = ImageDraw.Draw(tall)
    y = H
    for (txt, size, col), h in zip(lines, heights):
        if txt:
            d.text((W // 2, y), txt, font=font(FONT_B if size >= 34 else FONT_R, size), fill=col, anchor="mt")
        y += h
    n = int(CREDITS_DUR * FPS)
    travel = tall.height - H
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-vf", f"fade=in:st=0:d=0.8,fade=out:st={CREDITS_DUR - 1.2}:d=1.2",
         *ENC, str(out)], stdin=subprocess.PIPE)
    arr = np.asarray(tall)
    for i in range(n):
        y0 = int(round(travel * i / (n - 1)))
        proc.stdin.write(np.ascontiguousarray(arr[y0:y0 + H]).tobytes())
    proc.stdin.close()
    proc.wait()


# ---------------------------------------------------------------- subtitles
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Microsoft JhengHei,54,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,1,0,1,3.2,1.2,2,80,80,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_time(t: float) -> str:
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ---------------------------------------------------------------- main
def plan_scenes(scenes: list[dict]) -> list[dict]:
    plans, t0 = [], 0.0
    for s in scenes:
        meta = json.loads((BUILD / "audio" / f"{s['id']}.json").read_text(encoding="utf-8"))
        audio = probe_duration(BUILD / "audio" / f"{s['id']}.mp3")
        D = LEAD + audio + TAIL
        vis = [parse_visual(v) for v in s["visuals"]]
        snaps = [p + LEAD for p in pauses(meta["words"])]
        durs = allocate(D, [w for _, _, w in vis], snaps)
        clips, start = [], 0.0
        for i, ((kind, name, _), d) in enumerate(zip(vis, durs)):
            clen = d + (XF if i < len(vis) - 1 else 0.0)
            clips.append({"kind": kind, "name": name, "dur": round(clen, 3), "start": round(start, 3),
                          "variant": (len(plans) + i) % 4,
                          "out": str(CLIPS / f"{s['id']}_{i}_{kind}_{name}.mp4")})
            start += d
        plans.append({"id": s["id"], "t0": t0, "duration": D, "clips": clips, "words": meta["words"],
                      "text": meta["text"]})
        t0 += D
    return plans


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="build only this scene id (no final mux)")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    for d in (CLIPS, SCENES, BUILD / "cards", BUILD / "audio_scene", OUTPUT):
        d.mkdir(parents=True, exist_ok=True)

    scenes = load_scenes()
    plans = plan_scenes(scenes)
    todo = [p for p in plans if not args.only or p["id"] == args.only]

    jobs = [{k: c[k] for k in ("kind", "name", "dur", "variant", "out")} for p in todo for c in p["clips"]]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for msg in ex.map(render_clip, jobs):
            print(msg, flush=True)

    scene_by_id = {s["id"]: s for s in scenes}
    for p in todo:
        build_scene(scene_by_id[p["id"]], p)
        scene_audio(scene_by_id[p["id"]], p["duration"])
        print("scene", p["id"], f"{p['duration']:.1f}s", flush=True)
    if args.only:
        return

    # subtitles (absolute times)
    ass, srt, k = [ASS_HEADER], [], 1
    for p in plans:
        for c in subtitle_chunks(p["text"], p["words"]):
            a, b = p["t0"] + LEAD + c["start"], p["t0"] + LEAD + c["end"]
            ass.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Sub,,0,0,0,,{c['text']}")
            srt.append(f"{k}\n{srt_time(a)} --> {srt_time(b)}\n{c['text']}\n")
            k += 1
    (BUILD / "subs.ass").write_text("\n".join(ass) + "\n", encoding="utf-8")
    (OUTPUT / "fields.zh-TW.srt").write_text("\n".join(srt), encoding="utf-8")

    credits = SCENES / "zz_credits.mp4"
    build_credits(credits)

    # concat video and narration
    concat = BUILD / "concat.txt"
    concat.write_text("".join(f"file 'scenes/{p['id']}.mp4'\n" for p in plans) + "file 'scenes/zz_credits.mp4'\n",
                      encoding="utf-8")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy",
         "video_nosub.mp4"], cwd=BUILD)
    aconcat = BUILD / "aconcat.txt"
    aconcat.write_text("".join(f"file 'audio_scene/{p['id']}.wav'\n" for p in plans), encoding="utf-8")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "aconcat.txt",
         "-af", f"apad=pad_dur={CREDITS_DUR}", "-c:a", "pcm_s16le", "narration.wav"], cwd=BUILD)

    total = sum(p["duration"] for p in plans) + CREDITS_DUR
    music = sorted((ASSETS / "music").glob("*.mp3")) if (ASSETS / "music").exists() else []
    final = OUTPUT / "fields.mp4"
    # inputs: 0 = video, 1 = narration, 2 = music (optional)
    audio_in = ["-i", "narration.wav"]
    afilt = "[1:a]anull[a]"
    if music:
        (BUILD / "music.txt").write_text("".join(f"file '{m.as_posix()}'\n" for m in music), encoding="utf-8")
        audio_in += ["-stream_loop", "-1", "-f", "concat", "-safe", "0", "-i", "music.txt"]
        afilt = (f"[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.32,"
                 f"afade=in:st=0:d=3,afade=out:st={total - 5:.2f}:d=5[m];"
                 f"[1:a]asplit=2[n][sc];"
                 f"[m][sc]sidechaincompress=threshold=0.015:ratio=10:attack=30:release=900[md];"
                 f"[n][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", "video_nosub.mp4", *audio_in,
         "-filter_complex", f"[0:v]subtitles=subs.ass[v];{afilt}",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "h264_nvenc", "-preset", "p7", "-rc", "vbr", "-cq", "20", "-b:v", "8M", "-maxrate", "14M",
         "-bufsize", "20M", "-pix_fmt", "yuv420p", "-profile:v", "high",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)], cwd=BUILD)
    shutil.copy(BUILD / "subs.ass", OUTPUT / "fields.zh-TW.ass")
    print("final", final, f"{probe_duration(final):.1f}s")


if __name__ == "__main__":
    main()
