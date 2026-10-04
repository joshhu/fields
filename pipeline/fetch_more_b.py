"""Second media batch, group B (chapters 9-17): see script/media_more.md.

Reuses the helpers in fetch_media.py. Every key maps to a fixed, freely
licensed Commons file. Re-runnable: files already on disk are skipped.
Writes assets/credits_b.json.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_media import (ASSETS, TMP, credit, download, fetch_image, ffprobe_duration,  # noqa: E402
                         file_info, video_url)

IMAGES = {
    "bethe": "Hans Bethe.jpg",
    "shelter_island": "Lamb Pais Wheeler Feynman Feshback and Schwinger at Shelter Island Conference.jpg",
    # No freely licensed photo of the Feynman van; Feynman at a blackboard instead.
    "feynman_van": "Richard Feynman 1988.png",
    "g2_ring": "Fermilab g-2 (E989) ring.jpg",
    "nobel_medal": ("Nobel prize medal for medicine, Sweden, 1945, to Sir Alexander Fleming (1881-1955) "
                    "who discovered Penicillin. On display at the National Museum of Scotland.jpg"),
    # Ethane cell below / at / above the critical point (middle panel shows opalescence).
    "critical_opalescence": "CriticalPointMeasurementEthane.jpg",
    # Maze domains in a garnet film (magneto-optical microscope); source is small and upscaled.
    "magnetic_domains": "CMOS Mäanderdomänen.jpg",
    "princeton_ias": "Fuld Hall, Institute for Advanced Study, Princeton, NJ.jpg",
    "yang_lee": "C N Yang &T D Lee couples.jpg",
    # The Bohr/Pauli spinning-top photo is not on Commons; Pauli with Dirac and Peierls instead.
    "bohr_pauli": "The physicists Paul Dirac, Wolfgang Pauli and Rudolf Peierls, c 1953. (9660575591).jpg",
    "nambu": "YoichiroNambu.jpg",
    "weinberg": "Steven Weinberg 2010.jpg",
    "salam": "Abdus Salam 1987 (cropped).jpg",
    "glashow": "Sheldon Glashow.jpg",
    "gross": "David Gross LANL.jpg",
    "politzer": "H.D. Politzer.jpg",
    "wilczek": "Frank Wilczek. 01.jpg",
    "higgs_event": "CMS-PHO-EVENTS-2012-007-1.png",
    "atlas": "Installing the ATLAS Calorimeter - edit1.jpg",
    "cern_aerial": "CERN Aerial View.jpg",
    "lhc_tunnel": "LHC near point 5.jpg",
    # Higgs and Englert together at a 2013 press conference (no free 2012 CERN photo).
    "higgs_englert": "DIMG 7502 (11253392096).jpg",
    "sgr_a": "EHT Saggitarius A black hole.tif",
    "unruh_photo": "BillUnruh.jpg",
    "bullet_cluster": "1e0657 scale.jpg",
    "planck_satellite": "Planck Spacecraft (Artist Concept) (PIA13953).tiff",
    "calabi_yau": "CalabiYau5.jpg",
    "supercomputer": "Frontier Supercomputer (3).jpg",
    "hubble_deep": "NASA-HS201427a-HubbleUltraDeepField2014-20140603.jpg",
}

# key -> (Commons file, start second, max seconds kept, extra crop filter or "")
VIDEOS = {
    # crop off the timestamp burnt into the top-left corner
    "aurora": ("Aurora Australis as seen from ISS (SVS31281 - 1080p25).webm", 0, 40,
               "crop=iw*0.92:ih*0.92:iw*0.08:ih*0.08,"),
    # skip the French title card (0-5 s) and closing credits (23 s+)
    "superconductor_vid": ("Levitation of a magnet on a superconductor.ogv", 5.2, 17.6, ""),
    "rocket_launch": ("Artemis I Launch from NASA Causeway (Slo Mo) (GX010506).webm", 28, 50, ""),
    "milky_way": ("A timelapse of the Milky Way's movement against the backdrop of the Assy-Turgen "
                  "Observatory at an altitude of 2,750 m. Kazakhstan.webm", 0, 20, ""),
}

MIN_VIDEO_SEC = 12

AUTHOR_OVERRIDES = {
    "unruh_photo": "Underbar dk",  # extmetadata only says "me" (own work)
}


def fetch_video_b(key: str, title: str, start: float, max_len: float, crop: str) -> dict:
    ii = file_info(title)
    dest = ASSETS / "vid" / f"{key}.mp4"
    if not dest.exists():
        src = TMP / f"{key}{Path(title).suffix}"
        if not src.exists():
            download(video_url(title), src)
        dur = min(ffprobe_duration(src) - start, max_len)
        factor = max(1.0, MIN_VIDEO_SEC / dur) if dur > 0 else 1.0
        vf = (f"{crop}setpts={factor:.4f}*PTS,"
              "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", str(src),
                        "-t", f"{dur * factor:.2f}", "-an", "-vf", vf, "-c:v", "h264_nvenc", "-preset", "p5",
                        "-cq", "21", str(dest)], check=True)
        print("vid", key, "ok", f"{ffprobe_duration(dest):.1f}s")
    return credit(key, "video", title, ii)


def main() -> int:
    for d in ("img", "vid"):
        (ASSETS / d).mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    credits, failed = [], []
    jobs = ([(fetch_image, k, (t,)) for k, t in IMAGES.items()]
            + [(fetch_video_b, k, v) for k, v in VIDEOS.items()])
    for fn, key, args in jobs:
        try:
            c = fn(key, *args)
            if key in AUTHOR_OVERRIDES:
                c["author"] = AUTHOR_OVERRIDES[key]
            credits.append(c)
        except Exception as e:  # keep going; report at the end
            print("FAILED", key, e, file=sys.stderr)
            failed.append(key)
        time.sleep(1)
    (ASSETS / "credits_b.json").write_text(
        json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    print("failed:", failed or "none")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
