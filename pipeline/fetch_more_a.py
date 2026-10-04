"""Second batch of media, group A (chapters 0-8). See script/media_more.md.

Every key maps to a fixed, freely licensed Wikimedia Commons file.
Re-runnable: files already on disk are skipped. Writes assets/credits_a.json.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from fetch_media import (ASSETS, TMP, api, credit, download, ffprobe_duration,  # noqa: E402
                         file_info, video_url)

IMAGES = {
    "bubble_chamber": "Leptonic event in Gargamelle bubble chamber.jpg",  # CERN Gargamelle
    "superconductor": "Magnetic Levitation Experiment, Science Gallery Dublin, Ireland.jpg",
    "apple_tree": "Newton's apple tree, Woolsthorpe Manor - geograph.org.uk - 6730001.jpg",
    "halley_comet": "Lspn comet halley.jpg",
    "newton_1702": "Sir Isaac Newton by Sir Godfrey Kneller, Bt.jpg",
    "leibniz": "Christoph Bernhard Francke - Bildnis des Philosophen Leibniz (ca. 1695) (cropped).jpg",
    "ampere": "André-Marie Ampère, PA00379.jpg",
    "faraday_photo": "Michael Faraday. Photograph by Maull & Polyblank. Wellcome M0017169.jpg",
    "royal_institution": "Royal Institution of Great Britain.JPG",
    "faraday_ring": ("Apparatus from which the first magnetic electric current was obtained, 1831, Science Museum, "
                     "South Kensington, Acme Newspictures, c. December 1929, from the Digital Commonwealth - "
                     "1 22 10 001309 0006 A.jpg"),
    "maxwell_young": "YoungJamesClerkMaxwell.jpg",
    "heaviside": "Oliver Heaviside, ET Library Archives.jpg",
    # Hertz's own circular resonator (museum object)
    "hertz_apparatus": "Kreisförmiger Resonator mit Messingspirale von H. Herz.jpg",
    "prism": "Dispersion of White Light Through a Prism.jpg",
    "lightning": "Lightning Pritzerbe 01 (MK).jpg",
    "antenna": "VLA Antennas.jpg",
    "michelson_morley": "Michelson morley experiment 1887.jpg",
    "morley": "Morley, Edward 1885 - DPLA - 14e3c8f7e1c1b3728376637d7c07405e.jpg",
    "einstein_1921": "Albert Einstein 1921 (cropped).jpg",
    "gr_paper": "Einstein Die Grundlage der allgemeinen Relativitätstheorie Sonderdruck 1916 Titel.jpg",
    "eddington": "Portrait of Arthur Stanley Eddington (1882-1944), Astronomer (2575160361).jpg",
    "lensing": "The galaxy cluster Abell 2218 (heic0113c).jpg",
    "ligo": "LIGO Hanford aerial 05.jpg",
    "einstein_old": "Albert Einstein 1947.jpg",
    "klein": "OskarKlein.jpg",
    "anderson": "Carl David Anderson.jpg",
    "born": "Max Born.jpg",
    "jordan": "Pascual Jordan 1920s.jpg",
    "ocean_waves": "Breaking waves (Pacific Ocean shoreline at Heceta Head beach, Oregon, USA) 22.jpg",
}

# key -> (Commons PDF, page number)
PDF_PAGES = {
    "maxwell_paper": ("A Dynamical Theory of the Electromagnetic Field (IA jstor-108892).pdf", 1),
    # original Annalen der Physik scan of "Zur Elektrodynamik bewegter Körper"
    "annalen_1905": ("Einstein-Elektrodynamik.djvu", 1),
}

# key -> (files, direction): "h" = side by side (same height), "v" = stacked (same width)
COMPOSITES = {
    "tides": (["Bay of Fundy - Tide In.jpg", "Bay of Fundy - Tide Out.jpg"], "h"),
    # glowing hydrogen discharge tube above its real emission spectrum (no text)
    "hydrogen_spectrum": (["Hydrogen discharge tube.jpg", "Hydrogen emission spectrum.png"], "v"),
}

# key -> (Commons file, start second, max seconds kept); starts skip titles/text found by inspection
VIDEOS = {
    # real Newton's cradle (Technische Sammlungen Dresden); skips the title overlay in the first seconds
    "newtons_cradle": ("Kugelstoßpendel, Technische Sammlungen Dresden.ogv", 5, 23),
    "water_ripples": ("Capillary waves from rain drops - Kanagawa - 2026 June 20.webm", 0, 40),
    # only the part without burned-in captions
    "cloud_chamber": ("Wilson chamber.webm", 43.5, 16),
    "ocean": ("Aerial view of sand beach. Top view sea waves. Drone footage.webm", 0, 40),
}

# key -> (Commons file, [(start, end), ...]) joined back to back; avoids hands / wide shots
VIDEO_SEGMENTS = {
    "iron_filings_vid": ("16. Магнетни силови линии.ogv", [(43.5, 47.5), (49.5, 57.5), (61.5, 65.0)]),
}

# extmetadata fields that came back as URLs / page boilerplate, fixed from the file pages
CREDIT_OVERRIDES = {
    "faraday_photo": {"author": "Maull & Polyblank (Wellcome Collection)"},
    "morley": {"author": "Unknown author"},
    "newton_1702": {"title": "Portrait of Sir Isaac Newton (1702), Godfrey Kneller"},
}

MIN_VIDEO_SEC = 12
CREDITS = ASSETS / "credits_a.json"


def _img_dest(key: str) -> Path | None:
    found = [p for p in (ASSETS / "img").glob(f"{key}.*") if p.suffix.lower() in (".jpg", ".png")]
    return found[0] if found else None


def _save_jpg(src: Path, dest: Path) -> None:
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.getchannel("A"))
        im = bg
    im.convert("RGB").save(dest, quality=93)


def fetch_image(key: str, title: str) -> dict:
    ii = file_info(title, width=1920)
    if not _img_dest(key):
        url = ii.get("thumburl") or ii["url"]
        if ii["width"] <= 1920:
            url = ii["url"]  # original is already small enough
        raw = TMP / f"{key}_raw{Path(url.split('?')[0]).suffix or '.jpg'}"
        download(url, raw)
        _save_jpg(raw, ASSETS / "img" / f"{key}.jpg")
        print("img", key, "ok")
    return credit(key, "image", title, ii)


def fetch_pdf_page(key: str, title: str, page: int) -> dict:
    r = api({"action": "query", "titles": f"File:{title}", "prop": "imageinfo",
             "iiprop": "url|size|extmetadata", "iiurlparam": f"page{page}-1920px"})
    ii = next(iter(r["query"]["pages"].values()))["imageinfo"][0]
    if not _img_dest(key):
        url = ii["thumburl"].split("?")[0].replace("-960px-", "-1920px-")
        raw = TMP / f"{key}_raw.jpg"
        try:
            download(url, raw)
        except RuntimeError:
            download(ii["thumburl"], raw)
        _save_jpg(raw, ASSETS / "img" / f"{key}.jpg")
        print("img", key, "ok (pdf page)")
    c = credit(key, "image", title, ii)
    c["title"] += f" (p. {page})"
    return c


def fetch_composite(key: str, titles: list[str], direction: str = "h") -> dict:
    infos = [file_info(t, width=1920) for t in titles]
    if not _img_dest(key):
        parts = []
        for i, ii in enumerate(infos):
            raw = TMP / f"{key}_{i}.jpg"
            download(ii.get("thumburl") or ii["url"], raw)
            parts.append(Image.open(raw).convert("RGB"))
        gap = 24
        if direction == "h":
            h = min(p.height for p in parts)
            parts = [p.resize((int(p.width * h / p.height), h), Image.LANCZOS) for p in parts]
            out = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), h), (11, 16, 32))
            x = 0
            for p in parts:
                out.paste(p, (x, 0))
                x += p.width + gap
        else:
            w = 1920
            parts = [p.resize((w, int(p.height * w / p.width)), Image.LANCZOS) for p in parts]
            out = Image.new("RGB", (w, sum(p.height for p in parts) + gap * (len(parts) - 1)), (0, 0, 0))
            y = 0
            for p in parts:
                out.paste(p, (0, y))
                y += p.height + gap
        out.save(ASSETS / "img" / f"{key}.jpg", quality=93)
        print("img", key, "ok (composite)")
    cs = [credit(key, "image", t, ii) for t, ii in zip(titles, infos)]
    return {
        "key": key, "kind": "image",
        "title": " / ".join(c["title"] for c in cs),
        "author": " / ".join(dict.fromkeys(c["author"] for c in cs)),
        "license": " / ".join(dict.fromkeys(c["license"] for c in cs)),
        "source_url": " ".join(c["source_url"] for c in cs),
    }


def fetch_video(key: str, title: str, start: float, max_len: float) -> dict:
    ii = file_info(title)
    dest = ASSETS / "vid" / f"{key}.mp4"
    if not dest.exists():
        src = TMP / f"{key}{Path(title).suffix}"
        if not src.exists():
            download(video_url(title), src)
        dur = min(ffprobe_duration(src) - start, max_len)
        factor = max(1.0, MIN_VIDEO_SEC / dur) if dur > 0 else 1.0
        vf = (f"setpts={factor:.4f}*PTS,"
              "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", str(src),
                        "-t", f"{dur * factor:.2f}", "-an", "-vf", vf, "-c:v", "h264_nvenc", "-preset", "p5",
                        "-cq", "21", str(dest)], check=True)
        print("vid", key, "ok", f"{ffprobe_duration(dest):.1f}s")
    return credit(key, "video", title, ii)


def fetch_video_segments(key: str, title: str, segments: list[tuple[float, float]]) -> dict:
    ii = file_info(title)
    dest = ASSETS / "vid" / f"{key}.mp4"
    if not dest.exists():
        src = TMP / f"{key}{Path(title).suffix}"
        if not src.exists():
            download(video_url(title), src)
        norm = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p,setsar=1"
        parts = [f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,{norm}[s{i}]" for i, (a, b) in enumerate(segments)]
        graph = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(len(segments))) +             f"concat=n={len(segments)}:v=1:a=0[v]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", graph, "-map", "[v]",
                        "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "21", str(dest)], check=True)
        print("vid", key, "ok", f"{ffprobe_duration(dest):.1f}s")
    return credit(key, "video", title, ii)


def main() -> int:
    for d in ("img", "vid"):
        (ASSETS / d).mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    jobs = ([(fetch_image, k, (t,)) for k, t in IMAGES.items()]
            + [(fetch_pdf_page, k, v) for k, v in PDF_PAGES.items()]
            + [(fetch_composite, k, v) for k, v in COMPOSITES.items()]
            + [(fetch_video, k, v) for k, v in VIDEOS.items()]
            + [(fetch_video_segments, k, v) for k, v in VIDEO_SEGMENTS.items()])
    only = set(sys.argv[1:])
    credits, failed = [], []
    for fn, key, args in jobs:
        if only and key not in only:
            continue
        try:
            credits.append(fn(key, *args))
        except Exception as e:  # keep going; report at the end
            print("FAILED", key, e, file=sys.stderr)
            failed.append(key)
        time.sleep(1)
    old = json.loads(CREDITS.read_text(encoding="utf-8")) if CREDITS.exists() else []
    merged = {c["key"]: c for c in old}
    merged.update({c["key"]: c for c in credits})
    for k, fix in CREDIT_OVERRIDES.items():
        if k in merged:
            merged[k].update(fix)
    order = [k for _, k, _ in jobs]
    CREDITS.write_text(json.dumps([merged[k] for k in order if k in merged], ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print("failed:", failed or "none")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
