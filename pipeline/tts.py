"""Generate narration audio + word timings for every scene with edge-tts."""
import asyncio
import json
import re
import sys
from pathlib import Path

import edge_tts
import yaml

ROOT = Path(__file__).resolve().parent.parent
VOICE = "zh-TW-YunJheNeural"
RATE = "-3%"
OUT = ROOT / "build" / "audio"

CJK = r"　-〿一-鿿＀-￯「」『』（）"


def clean_text(text: str) -> str:
    """Remove the spaces YAML folding inserts between CJK lines."""
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(rf"(?<=[{CJK}]) (?=[{CJK}A-Za-z0-9])", "", text)
    text = re.sub(rf"(?<=[A-Za-z0-9)]) (?=[{CJK}])", "", text)
    return text


def load_scenes(path: Path = ROOT / "script" / "scenes.yaml") -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for s in data["scenes"]:
        s["text"] = clean_text(s["text"])
    return data["scenes"]


async def synth(scene: dict, force: bool = False) -> dict:
    mp3 = OUT / f"{scene['id']}.mp3"
    meta = OUT / f"{scene['id']}.json"
    if meta.exists() and mp3.exists() and not force:
        cached = json.loads(meta.read_text(encoding="utf-8"))
        if cached.get("text") == scene["text"]:
            return cached
    words = []
    for attempt in range(4):
        try:
            comm = edge_tts.Communicate(scene["text"], voice=VOICE, rate=RATE, boundary="WordBoundary")
            words = []
            with open(mp3, "wb") as f:
                async for ch in comm.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        words.append({
                            "text": ch["text"],
                            "start": ch["offset"] / 1e7,
                            "end": (ch["offset"] + ch["duration"]) / 1e7,
                        })
            break
        except Exception as e:  # network hiccups
            print(f"retry {scene['id']}: {e}", file=sys.stderr)
            await asyncio.sleep(3)
    else:
        raise RuntimeError(f"TTS failed for {scene['id']}")
    result = {"id": scene["id"], "text": scene["text"], "words": words}
    meta.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return result


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    force = "--force" in sys.argv
    for s in load_scenes():
        r = await synth(s, force)
        print(s["id"], len(r["words"]), r["words"][-1]["end"] if r["words"] else None)


if __name__ == "__main__":
    asyncio.run(main())
