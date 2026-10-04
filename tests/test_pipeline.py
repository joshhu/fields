"""Functional + end-to-end checks on the build products (skipped if not built yet)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

from timeline import parse_visual  # noqa: E402
from tts import load_scenes  # noqa: E402

AUDIO = ROOT / "build" / "audio"
FINAL = ROOT / "output" / "fields.mp4"


def ffprobe(path: Path) -> dict:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    return json.loads(out)


def test_scenes_reference_existing_assets():
    missing = []
    for s in load_scenes():
        assert s["text"] and s["visuals"], s["id"]
        for v in s["visuals"]:
            kind, name, _ = parse_visual(v)
            folder = {"anim": "anim", "img": "img", "vid": "vid"}[kind]
            if not list((ROOT / "assets" / folder).glob(f"{name}.*")):
                missing.append(v)
    assert not missing, missing


def test_credits_cover_all_downloaded_media():
    credits = {c["key"] for c in json.loads((ROOT / "assets" / "credits.json").read_text(encoding="utf-8"))}
    used = {parse_visual(v)[1] for s in load_scenes() for v in s["visuals"] if not v.startswith("anim:")}
    assert used <= credits, used - credits


@pytest.mark.skipif(not AUDIO.exists(), reason="TTS not generated")
def test_plan_matches_audio():
    from compose import plan_scenes
    plans = plan_scenes(load_scenes())
    for p in plans:
        total = sum(c["dur"] for c in p["clips"]) - 0.6 * (len(p["clips"]) - 1)
        assert abs(total - p["duration"]) < 0.05, p["id"]
    assert 1100 < sum(p["duration"] for p in plans) < 1300


@pytest.mark.skipif(not FINAL.exists(), reason="final video not built")
def test_final_video_e2e():
    info = ffprobe(FINAL)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert (v["width"], v["height"]) == (1920, 1080)
    assert v["codec_name"] == "h264" and a["codec_name"] == "aac"
    assert 19 * 60 <= float(info["format"]["duration"]) <= 22 * 60
    srt = (ROOT / "output" / "fields.zh-TW.srt").read_text(encoding="utf-8")
    assert srt.count("-->") > 300
