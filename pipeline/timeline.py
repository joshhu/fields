"""Pure timing logic: scene layout, visual cut points, subtitle chunks."""
from __future__ import annotations

import re

LEAD = 1.0   # silence before narration in each scene (chapter card fades in)
TAIL = 0.6   # silence after narration
PUNCT = set("，。：；！？、「」『』（）,.;:!?()　 ")
BREAK = set("，。：；！？、")
MAX_SUB = 18  # max CJK chars per subtitle line


def parse_visual(v: str | dict) -> tuple[str, str, float]:
    """'img:newton*1.5' -> ('img', 'newton', 1.5). Segment suffix '@a-b' is dropped."""
    if isinstance(v, dict):
        v = v["v"]
    kind, _, rest = v.partition(":")
    name, _, w = rest.partition("*")
    name = name.split("@")[0]
    return kind, name, float(w) if w else 1.0


def parse_item(v: str | dict) -> dict:
    """Full visual spec: kind, name, weight, segment (a, b) or None, anchor phrase or None."""
    anchor = v.get("at") if isinstance(v, dict) else None
    spec = v["v"] if isinstance(v, dict) else v
    kind, _, rest = spec.partition(":")
    body, _, w = rest.partition("*")
    name, _, seg = body.partition("@")
    segment = None
    if seg:
        a, _, b = seg.partition("-")
        segment = (float(a), float(b) if b else None)
    return {"kind": kind, "name": name, "weight": float(w) if w else 1.0, "segment": segment, "at": anchor}


def anchor_time(text: str, times: list, phrase: str, start_pos: int = 0) -> tuple[float, int] | None:
    """Time (scene-relative, without LEAD) at which `phrase` starts being spoken."""
    idx = text.find(phrase, start_pos)
    if idx < 0:
        idx = text.find(phrase)
    if idx < 0:
        return None
    for t in times[idx:idx + len(phrase) + 6]:
        if t:
            return t[0], idx + len(phrase)
    return None


def plan_cuts(total: float, weights: list[float], anchors: list[float | None],
              snap_points: list[float] | None = None, min_len: float = 2.5) -> list[float]:
    """Durations for visuals; anchored items start at their anchor time, others fill evenly."""
    n = len(weights)
    fixed = [0.0] + [None] * (n - 1)
    for i in range(1, n):
        if anchors[i] is not None:
            fixed[i] = anchors[i]
    starts: list[float] = [0.0] * n
    i = 0
    while i < n:
        j = i + 1
        while j < n and fixed[j] is None:
            j += 1
        seg_start = fixed[i]
        seg_end = fixed[j] if j < n else total
        durs = allocate(seg_end - seg_start, weights[i:j],
                        [p - seg_start for p in (snap_points or []) if seg_start < p < seg_end],
                        min_len=min(min_len, (seg_end - seg_start) / (j - i)))
        t = seg_start
        for k, d in zip(range(i, j), durs):
            starts[k] = t
            t += d
        i = j
    # enforce monotonic + min length
    for k in range(1, n):
        starts[k] = max(starts[k], starts[k - 1] + min_len)
    for k in range(n - 1, 0, -1):
        end = starts[k + 1] if k + 1 < n else total
        starts[k] = min(starts[k], end - min_len)
    bounds = starts + [total]
    return [b - a for a, b in zip(bounds, bounds[1:])]


def pauses(words: list[dict], min_gap: float = 0.18) -> list[float]:
    """Mid-points of silent gaps between consecutive words (sentence breaks)."""
    out = []
    for a, b in zip(words, words[1:]):
        if b["start"] - a["end"] >= min_gap:
            out.append((a["end"] + b["start"]) / 2)
    return out


def allocate(total: float, weights: list[float], snap_points: list[float] | None = None,
             window: float = 0.3, min_len: float = 4.0) -> list[float]:
    """Split `total` seconds by weight, snapping each cut to a nearby pause."""
    s = sum(weights)
    cuts, acc = [], 0.0
    for w in weights[:-1]:
        acc += total * w / s
        cuts.append(acc)
    if snap_points:
        avg = total / len(weights)
        snapped = []
        for c in cuts:
            near = [p for p in snap_points if abs(p - c) <= avg * window]
            snapped.append(min(near, key=lambda p: abs(p - c)) if near else c)
        cuts = snapped
    # enforce monotonic cuts with a minimum segment length
    bounds = [0.0] + cuts + [total]
    for i in range(1, len(bounds) - 1):
        bounds[i] = max(bounds[i], bounds[i - 1] + min_len)
    for i in range(len(bounds) - 2, 0, -1):
        bounds[i] = min(bounds[i], bounds[i + 1] - min_len)
    return [b - a for a, b in zip(bounds, bounds[1:])]


def char_times(text: str, words: list[dict]) -> list[tuple[float, float] | None]:
    """Map every character of `text` to (start, end) using word boundaries.

    Punctuation gets None. Characters are matched greedily against the
    concatenated word texts; unmatched spans are interpolated.
    """
    times: list[tuple[float, float] | None] = [None] * len(text)
    pos = 0
    for w in words:
        wt = w["text"].strip()
        if not wt:
            continue
        idx = text.find(wt, pos)
        if idx < 0 or idx - pos > 12:
            # fallback: walk forward char by char matching the first char
            idx = text.find(wt[0], pos)
            if idx < 0:
                continue
            wt = wt[:1]
        n = len(wt)
        dur = (w["end"] - w["start"]) / max(n, 1)
        for k in range(n):
            times[idx + k] = (w["start"] + k * dur, w["start"] + (k + 1) * dur)
        pos = idx + n
    # interpolate non-punctuation gaps
    last = None
    for i, ch in enumerate(text):
        if times[i] is None and ch not in PUNCT and last is not None:
            times[i] = (times[last][1], times[last][1] + 0.15)
        if times[i] is not None:
            last = i
    return times


def split_phrases(text: str) -> list[str]:
    """Split on break punctuation, keeping the punctuation attached."""
    parts, cur = [], ""
    for ch in text:
        cur += ch
        if ch in BREAK:
            parts.append(cur)
            cur = ""
    if cur:
        parts.append(cur)
    out = []
    for p in parts:
        while visible_len(p) > MAX_SUB + 4:
            cut = _soft_cut(p)
            out.append(p[:cut])
            p = p[cut:]
        out.append(p)
    return out


def _soft_cut(p: str) -> int:
    """Cut a too-long phrase near the middle, avoiding splitting ASCII words."""
    mid = len(p) // 2
    for d in range(0, mid):
        for c in (mid + d, mid - d):
            if 0 < c < len(p) and not (p[c - 1].isascii() and p[c].isascii() and p[c].isalnum()):
                return c
    return mid


def visible_len(s: str) -> float:
    return sum(0.55 if ch.isascii() else 1.0 for ch in s if ch not in PUNCT)


def subtitle_chunks(text: str, words: list[dict]) -> list[dict]:
    """Group phrases into subtitle lines with start/end times (scene-relative)."""
    times = char_times(text, words)
    phrases = split_phrases(text)
    # merge short phrases
    merged: list[str] = []
    for p in phrases:
        if merged and visible_len(merged[-1]) + visible_len(p) <= MAX_SUB and merged[-1][-1] not in "。！？":
            merged[-1] += p
        else:
            merged.append(p)
    chunks, pos = [], 0
    for m in merged:
        span = [t for t in times[pos:pos + len(m)] if t]
        pos += len(m)
        if not span:
            continue
        chunks.append({"text": clean_sub(m), "start": span[0][0], "end": span[-1][1]})
    # extend ends to close tiny gaps
    for a, b in zip(chunks, chunks[1:]):
        if 0 < b["start"] - a["end"] < 0.5:
            a["end"] = b["start"]
    return [c for c in chunks if c["text"]]


def clean_sub(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[，。、；：]+$", "", s)
    return s
