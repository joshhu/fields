# fields — 場比粒子更基本

一支約 20 分鐘、1080p 的繁體中文科普影片：〈物理學三百年終極轉向，為什麼場比粒子更基本？〉。
從牛頓的超距作用、法拉第的力線、馬克士威的電磁場、愛因斯坦的時空場，一路講到量子場論、重整化、
規範場論與標準模型，以及彎曲時空中的量子場。

整支影片由程式自動產生：

| 元素 | 做法 |
|---|---|
| 旁白配音 | [edge-tts](https://github.com/rany2/edge-tts)，`zh-TW-YunJheNeural` |
| 字幕 | 依 TTS 的 WordBoundary 時間碼切句，燒錄進影片，另輸出 `.srt` / `.ass` |
| 動畫 | [Manim Community](https://www.manim.community/) 29 段（`anims/`） |
| 圖片、影片 | Wikimedia Commons / NASA / ESA 等可再利用授權素材（`pipeline/fetch_media.py`），出處列在片尾與 `assets/credits.json` |
| 配樂 | Commons 上的 CC0 / CC BY 氛圍音樂，旁白出現時自動壓低（sidechain） |
| 剪輯 | ffmpeg + NVENC：圖片 Ken Burns 推鏡、交叉淡化、章節字卡、響度正規化（-16 LUFS） |

## 需求

- Windows / Linux，`uv`、`ffmpeg`（需 libass 與 `h264_nvenc`，也就是 NVIDIA GPU）
- 微軟正黑體（`msjh.ttc` / `msjhbd.ttc`），Linux 請改 `pipeline/compose.py` 的字型路徑
- 不需要 LaTeX（動畫裡的數學式都是 Unicode 文字）

## 使用方式

```bash
uv sync
uv run python pipeline/tts.py            # 1. 產生旁白 build/audio/*.mp3 + 時間碼
uv run python pipeline/fetch_media.py    # 2. 下載圖片、影片、配樂到 assets/
cd anims && for f in [a-z]*.py; do n=${f%.py}; [ "$n" = style ] || [ "$n" = g2util ] || ./render.sh $n; done; cd ..
                                         # 3. 渲染動畫到 assets/anim/
uv run python pipeline/compose.py        # 4. 合成 output/fields.mp4
```

只重做某一場：`uv run python pipeline/compose.py --only s03_maxwell`。片段有快取，改了素材才會重算。

## 專案結構

```
script/scenes.yaml     分場稿：旁白、章節標題、每場的視覺清單
script/anim_spec.md    動畫規格與風格指南
pipeline/tts.py        旁白 TTS
pipeline/fetch_media.py 素材下載（固定來源，可重跑）
pipeline/timeline.py   時間軸、畫面切點對齊停頓、字幕切句（純函式）
pipeline/compose.py    算圖與合成
anims/                 Manim 動畫原始碼（style.py 為共用配色）
tests/                 單元、功能、端對端測試
```

## 測試

```bash
uv run pytest -q
```

- `test_timeline.py`：時間分配、停頓對齊、字幕切句等單元測試
- `test_pipeline.py`：分場稿引用的素材都存在、出處完整、時間軸與配音長度一致；成品存在時再驗證 1920×1080、h264/aac、長度 19–22 分鐘、字幕數量

## 授權

影片中使用的第三方素材依各自授權（公有領域、CC0、CC BY、CC BY-SA），
詳見 `assets/credits.json` 與片尾字幕。原始文字改寫自網路長文〈物理學三百年終極轉向，為什麼場比粒子更基本？〉。
