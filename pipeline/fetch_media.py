"""Download images, video clips and music used by script/scenes.yaml.

Every key maps to a fixed, freely licensed source file (Wikimedia Commons).
Re-runnable: files already on disk are skipped. Writes assets/credits.json.
"""
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TMP = ROOT / "build" / "media_tmp"
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "fields-video/1.0 (https://github.com/joshhu/fields; educational documentary build) python-requests"}

IMAGES = {
    "newton": "Portrait of Sir Isaac Newton, 1689 (brightened).jpg",
    "principia": "Newton - Principia (1687), title, p. 5, color.jpg",
    "faraday": "Michael Faraday sitting.jpg",
    "iron_filings": "Iron-filings-around-magnet.jpg",
    "faraday_lab": "Michael Faraday lecturing at the Royal Institution; Prince A Wellcome V0013854.jpg",
    "maxwell": "James Clerk Maxwell, G.J. Stodart, 1890.jpg",
    "hertz": "HEINRICH HERTZ.JPG",
    "michelson": "Portrait of Albert Abraham Michelson (1852-1931), Physicist (2551015907).jpg",
    "einstein_1905": "Einstein patentoffice full.jpg",
    "einstein": "Einstein 1921 by F Schmutzer - restoration.jpg",
    "eclipse_1919": "1919 eclipse negative.jpg",
    "schrodinger": "Erwin Schrödinger - Narodowe Archiwum Cyfrowe (1-E-939).jpg",
    "dirac": "Paul Dirac, 1933.jpg",
    "positron": "PositronDiscovery.jpg",
    "heisenberg": "Werner Heisenberg - B&W Portrait by Max Löhrich, 1933 - SIL.jpg",
    "solvay_1927": "Solvay conference 1927.jpg",
    "fermi": "Enrico Fermi 1943-49.jpg",
    "feynman": "Richard Feynman 1959.png",
    "tomonaga": "Shinichiro Tomonaga by Shigeru Tamura.jpg",
    "schwinger": "Julian Schwinger, 1965.jpg",
    # Only freely licensed portrait of Kenneth G. Wilson on Commons is tiny;
    # it is upscaled. wilson_alt is a higher-resolution fallback.
    "wilson": "Kenneth G. Wilson.121.png",
    "wilson_alt": "Kenneth Wilson's name on the Nobel Monument in NYC.jpg",
    "yang": "楊振寧 Chen Ning Yang.jpg",
    "pauli": "Wolfgang Pauli.jpg",
    "oppenheimer": "Oppenheimer (cropped).jpg",
    "higgs": "Peter W. Higgs (50372668271) (cropped).jpg",
    "noether": "Noether.jpg",
    "hawking": "Stephen Hawking NASA 50th 200804210001HQ.jpg",
    "m87": "Black hole - Messier 87 crop max res.jpg",
    "cmb": "Cosmic Microwave Background (CMB).jpeg",
    "lhc_detector": "CMS-Experiment (LHC).jpg",
}

# key -> (Commons file, start second, max seconds kept)
# Start offsets skip title cards / text overlays found by inspecting each clip.
VIDEOS = {
    "galaxy": ("NASA-HubbleLegacyFieldZoomOut-20190502.webm", 0, 90),
    "earth_orbit": ("Solar System Resource Page (SVS20391).webm", 0, 90),
    "sun": ("NASA Thermonuclear Art – The Sun In Ultra-HD (4K) (1080p).webm", 60, 45),
    "black_hole": ("BBH gravitational lensing of gw150914.webm", 0, 90),
    # No freely licensed LHC footage on Commons; SOLEIL synchrotron animation (text-free part).
    "lhc": ("Comment fonctionne un accélérateur circulaire.webm", 26, 34),
    "earth": ("Alexander Gerst’s Earth timelapses (2017 reissue) ESA380570.webm", 272, 50),
}

MUSIC = {
    "ambient1": "Raspberrymusic - Ambient (10 minutes).flac",
    "ambient2": "Paul Kuniholm Ambient Seattle 2024 (WayVSumtInThWay).wav",
}

MIN_VIDEO_SEC = 25

# Authors missing from extmetadata, taken from the file description page.
AUTHOR_OVERRIDES = {
    "iron_filings": "Benjamin Crowell (lightandmatter.com)",
    "einstein_1905": "Lucien Chavan",
    "noether": "Unknown author",
}


def api(params: dict) -> dict:
    params = {"format": "json", **params}
    for i in range(8):
        r = requests.get(API, params=params, headers=UA, timeout=60)
        if r.status_code == 200:
            try:
                return r.json()
            except ValueError:
                pass
        time.sleep(5 * (i + 1))
    raise RuntimeError(f"Commons API failed: {params}")


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", " ", html.unescape(s)).strip()
    s = re.sub(r"\s*\[\d+\]|</?ref>", "", s)  # footnote markers
    return re.sub(r"^(.{4,}?)\1+$", r"\1", s)  # "Unknown authorUnknown author" -> "Unknown author"


def file_info(title: str, width: int | None = None) -> dict:
    params = {
        "action": "query", "titles": f"File:{title}", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
    }
    if width:
        params["iiurlwidth"] = width
    page = next(iter(api(params)["query"]["pages"].values()))
    if "imageinfo" not in page:
        raise FileNotFoundError(title)
    return page["imageinfo"][0]


def credit(key: str, kind: str, title: str, ii: dict) -> dict:
    m = ii.get("extmetadata", {})
    val = lambda k: strip_html(m.get(k, {}).get("value", ""))  # noqa: E731
    return {
        "key": key,
        "kind": kind,
        "title": val("ObjectName") or title.rsplit(".", 1)[0],
        "author": AUTHOR_OVERRIDES.get(key) or val("Artist") or val("Credit") or "Unknown",
        "license": val("LicenseShortName") or val("UsageTerms"),
        "source_url": ii.get("descriptionurl", ""),
    }


def download(url: str, dest: Path) -> None:
    for i in range(6):
        with requests.get(url, headers=UA, stream=True, timeout=120) as r:
            if r.status_code == 200:
                tmp = dest.with_suffix(dest.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
                tmp.replace(dest)
                return
        time.sleep(5 * (i + 1))
    raise RuntimeError(f"download failed: {url}")


def ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path)])
    return float(out)


def fetch_image(key: str, title: str) -> dict:
    ii = file_info(title, width=1920)  # standard Commons thumb size
    existing = list((ASSETS / "img").glob(f"{key}.*"))
    if not existing:
        url = ii.get("thumburl") or ii["url"]
        ext = ".png" if url.lower().endswith(".png") else ".jpg"
        dest = ASSETS / "img" / f"{key}{ext}"
        download(url, dest)
        if ii["width"] < 800:  # upscale tiny sources so the compositor gets usable pixels
            up = dest.with_name(f"{key}_up{ext}")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(dest), "-vf",
                            "scale=iw*4:ih*4:flags=lanczos", str(up)], check=True)
            up.replace(dest)
        print("img", key, "ok")
    return credit(key, "image", title, ii)


def video_url(title: str) -> str:
    """Prefer Commons' 1080p transcode over (possibly huge) 4K originals."""
    page = next(iter(api({"action": "query", "titles": f"File:{title}", "prop": "videoinfo",
                          "viprop": "url|derivatives"})["query"]["pages"].values()))
    vi = page["videoinfo"][0]
    derivs = [d for d in vi.get("derivatives", []) if d.get("height") and d["height"] <= 1080]
    if derivs:
        return max(derivs, key=lambda d: (d["height"], "vp9" in d.get("transcodekey", "")))["src"]
    return vi["url"]


def fetch_video(key: str, title: str, start: float, max_len: float) -> dict:
    ii = file_info(title)
    dest = ASSETS / "vid" / f"{key}.mp4"
    if not dest.exists():
        src = TMP / f"{key}{Path(title).suffix}"
        if not src.exists():
            download(video_url(title), src)
        dur = min(ffprobe_duration(src) - start, max_len)
        # slow down short clips so they last at least MIN_VIDEO_SEC
        factor = max(1.0, MIN_VIDEO_SEC / dur) if dur > 0 else 1.0
        vf = (f"setpts={factor:.4f}*PTS,"
              "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", str(src),
                        "-t", f"{dur * factor:.2f}", "-an", "-vf", vf, "-c:v", "h264_nvenc", "-preset", "p5",
                        "-cq", "21", str(dest)], check=True)
        print("vid", key, "ok", f"{ffprobe_duration(dest):.1f}s")
    return credit(key, "video", title, ii)


def fetch_music(key: str, title: str) -> dict:
    ii = file_info(title)
    dest = ASSETS / "music" / f"{key}.mp3"
    if not dest.exists():
        src = TMP / f"{key}{Path(title).suffix}"
        if not src.exists():
            download(ii["url"], src)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "2", "-ar", "44100",
                        "-c:a", "libmp3lame", "-b:a", "192k", str(dest)], check=True)
        print("music", key, "ok", f"{ffprobe_duration(dest):.1f}s")
    return credit(key, "music", title, ii)


def main() -> int:
    for d in ("img", "vid", "music"):
        (ASSETS / d).mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    credits, failed = [], []
    jobs = ([(fetch_image, k, (t,)) for k, t in IMAGES.items()]
            + [(fetch_video, k, v) for k, v in VIDEOS.items()]
            + [(fetch_music, k, (t,)) for k, t in MUSIC.items()])
    for fn, key, args in jobs:
        try:
            credits.append(fn(key, *args))
        except Exception as e:  # keep going; report at the end
            print("FAILED", key, e, file=sys.stderr)
            failed.append(key)
        time.sleep(1)
    (ASSETS / "credits.json").write_text(
        json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    print("failed:", failed or "none")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
