import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))

from timeline import allocate, char_times, clean_sub, parse_visual, pauses, split_phrases, subtitle_chunks, visible_len  # noqa: E402
from tts import clean_text  # noqa: E402


def test_parse_visual_weight():
    assert parse_visual("img:newton") == ("img", "newton", 1.0)
    assert parse_visual("anim:em_wave*2") == ("anim", "em_wave", 2.0)


def test_allocate_sums_to_total_and_respects_min():
    d = allocate(60.0, [1, 1, 1, 1])
    assert abs(sum(d) - 60.0) < 1e-9
    assert all(x >= 4.0 for x in d)


def test_allocate_snaps_to_pause():
    d = allocate(40.0, [1, 1], snap_points=[21.5])
    assert abs(d[0] - 21.5) < 1e-9


def test_allocate_min_len_enforced_on_tiny_total():
    d = allocate(10.0, [1, 1], snap_points=[0.5])
    assert all(x >= 4.0 for x in d)


def test_pauses_detects_gaps():
    words = [{"start": 0, "end": 1}, {"start": 1.05, "end": 2}, {"start": 2.5, "end": 3}]
    assert pauses(words) == [2.25]


def test_clean_text_removes_yaml_fold_spaces():
    assert clean_text("第一行，\n 第二行 SU(2) 乘 U(1)。") == "第一行，第二行SU(2)乘U(1)。"


def test_split_phrases_respects_max_len():
    text = "這是一個非常非常長而且完全沒有任何標點符號的句子用來測試自動斷行功能是否正常運作。"
    parts = split_phrases(text)
    assert "".join(parts) == text
    assert all(visible_len(p) <= 22 for p in parts)


def test_char_times_and_chunks():
    text = "你好，世界。再見！"
    words = [{"text": "你好", "start": 0.0, "end": 0.5}, {"text": "世界", "start": 0.7, "end": 1.2},
             {"text": "再見", "start": 1.6, "end": 2.0}]
    times = char_times(text, words)
    assert times[0] == (0.0, 0.25) and times[2] is None
    chunks = subtitle_chunks(text, words)
    assert chunks[0]["text"] == "你好，世界"
    assert chunks[0]["start"] == 0.0 and chunks[-1]["end"] == 2.0
    assert chunks[-1]["text"] == "再見！"


def test_clean_sub_strips_trailing_punct():
    assert clean_sub("你好，") == "你好"
    assert clean_sub("為什麼？") == "為什麼？"
