import numpy as np
from PIL import Image
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

DUR = 25.0
N = 256
SIZE = 4.6
rng = np.random.default_rng(7)


def ising_critical(n=N, sweeps=1200, T=2.269):
    s = rng.choice([-1, 1], size=(n, n)).astype(np.int8)
    ii, jj = np.indices((n, n))
    masks = [((ii + jj) % 2 == k) for k in (0, 1)]
    beta = 1.0 / T
    for _ in range(sweeps):
        for m in masks:
            nb = (np.roll(s, 1, 0) + np.roll(s, -1, 0) + np.roll(s, 1, 1) + np.roll(s, -1, 1))
            dE = 2 * s * nb
            flip = (dE <= 0) | (rng.random((n, n)) < np.exp(-beta * np.clip(dE, 0, None)))
            s = np.where(m & flip, -s, s).astype(np.int8)
    return s


def block(s):
    n = s.shape[0] // 2
    b = s.reshape(n, 2, n, 2).sum(axis=(1, 3))
    tie = rng.choice([-1, 1], size=b.shape)
    return np.where(b > 0, 1, np.where(b < 0, -1, tie)).astype(np.int8)


def to_image(s, px=1024):
    up = np.array([79, 195, 247], np.uint8)
    dn = np.array([18, 34, 64], np.uint8)
    rgb = np.where(s[..., None] > 0, up, dn).astype(np.uint8)
    img = Image.fromarray(rgb, "RGB").resize((px, px), Image.NEAREST)
    return np.array(img)


class Main(Scene):
    def construct(self):
        levels = [ising_critical()]
        for _ in range(4):
            levels.append(block(levels[-1]))
        imgs = [to_image(l) for l in levels]

        def mk(i, x):
            m = ImageMobject(imgs[i]).set_height(SIZE).move_to([x, 0.3, 0])
            return m

        left = mk(0, -3.5)
        right = mk(0, 3.5)
        frame_l = SurroundingRectangle(left, buff=0.03, color=MUTED, stroke_width=2)
        frame_r = SurroundingRectangle(right, buff=0.03, color=PARTICLE, stroke_width=3)
        self.play(FadeIn(left, scale=0.96), FadeIn(right, scale=0.96), Create(frame_l), Create(frame_r), run_time=1.5)
        arrow = Arrow([-0.9, 0.3, 0], [0.9, 0.3, 0], buff=0, color=PARTICLE, stroke_width=6)
        rule = Text("2×2\n多數決", font=FONT, font_size=26, color=PARTICLE, line_spacing=0.8).next_to(arrow, UP, buff=0.15)
        self.play(GrowArrow(arrow), FadeIn(rule), run_time=1.0)
        self.wait(2.0)

        lab_l = Text("微觀：256 × 256", font=FONT, font_size=32, color=TEXT).move_to([-3.5, 2.95, 0])
        lab_r = Text("原始格點", font=FONT, font_size=32, color=PARTICLE).move_to([3.5, 2.95, 0])
        self.play(FadeIn(lab_l), FadeIn(lab_r), run_time=0.8)
        self.wait(0.7)

        for k in range(1, 5):
            n = N >> k
            new = mk(k, 3.5)
            new_lab = Text(f"粗粒化 {k} 次：{n} × {n}", font=FONT, font_size=32, color=PARTICLE).move_to([3.5, 2.95, 0])
            self.play(arrow.animate.set_color(TEXT), rate_func=there_and_back, run_time=0.5)
            self.play(FadeOut(right), FadeIn(new), FadeTransform(lab_r, new_lab), run_time=1.0)
            right = new
            lab_r = new_lab
            self.wait(2.4)

        cap = Text("細節被洗掉，大尺度的輪廓留了下來", font=FONT, font_size=34, color=TEXT).move_to([0, -2.55, 0])
        self.play(FadeIn(cap, shift=UP * 0.15), run_time=1.0)
        self.wait(max(0.5, DUR - self.renderer.time))
