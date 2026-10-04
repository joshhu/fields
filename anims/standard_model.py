"""Standard Model particle table with SU(3)xSU(2)xU(1) groupings."""
import numpy as np
from manim import *

from style import ACCENT, FIELD, FONT, MUTED, PARTICLE, TEXT

CELL = 1.12
PITCH = 1.24
QUARK = "#CE93D8"
LEPTON = "#81C784"
BOSON = "#FF8A65"
HIGGS = "#FFD54F"

# (symbol markup, name, row, col, color)
PARTICLES = [
    ("u", "上夸克", 0, 0, QUARK), ("c", "魅夸克", 0, 1, QUARK), ("t", "頂夸克", 0, 2, QUARK),
    ("d", "下夸克", 1, 0, QUARK), ("s", "奇夸克", 1, 1, QUARK), ("b", "底夸克", 1, 2, QUARK),
    ("e", "電子", 2, 0, LEPTON), ("μ", "緲子", 2, 1, LEPTON), ("τ", "τ 子", 2, 2, LEPTON),
    ("ν<sub>e</sub>", "電微中子", 3, 0, LEPTON), ("ν<sub>μ</sub>", "緲微中子", 3, 1, LEPTON),
    ("ν<sub>τ</sub>", "τ 微中子", 3, 2, LEPTON),
    ("g", "膠子", 0, 3, BOSON), ("γ", "光子", 1, 3, BOSON), ("Z", "Z 玻色子", 2, 3, BOSON),
    ("W", "W 玻色子", 3, 3, BOSON),
    ("H", "希格斯", 1.5, 4.25, HIGGS),
]


def cell(sym, name, color):
    box = RoundedRectangle(corner_radius=0.12, width=CELL, height=CELL, stroke_color=color,
                           stroke_width=3, fill_color=color, fill_opacity=0.12)
    s = MarkupText(sym, font=FONT, font_size=46, color=TEXT).move_to(box.get_center() + UP * 0.12)
    n = Text(name, font=FONT, font_size=17, color=color).move_to(box.get_center() + DOWN * 0.36)
    return VGroup(box, s, n)


class Main(Scene):
    def construct(self):
        origin = np.array([-3.4, 1.75, 0])
        cells = {}
        for sym, name, r, c, col in PARTICLES:
            g = cell(sym, name, col)
            g.move_to(origin + np.array([c * PITCH, -r * PITCH, 0]))
            cells[name] = g
        grid = VGroup(*cells.values())
        grid.move_to(np.array([0, -0.35, 0]))

        # gentle breathing glow so the table never sits still
        t = ValueTracker(0)
        for i, g in enumerate(grid):
            g[0].add_updater(lambda m, i=i: m.set_fill(opacity=0.10 + 0.08 * np.sin(t.get_value() * 2 + i * 0.6)))

        self.add(t)
        self.play(t.animate.set_value(1), LaggedStart(*[FadeIn(g, scale=0.6) for g in grid], lag_ratio=0.18),
                  run_time=4.2)

        title_parts = [
            Text("SU(3)", font=FONT, font_size=50, color=ACCENT),
            Text("×", font=FONT, font_size=50, color=TEXT),
            Text("SU(2)", font=FONT, font_size=50, color=FIELD),
            Text("×", font=FONT, font_size=50, color=TEXT),
            Text("U(1)", font=FONT, font_size=50, color=PARTICLE),
        ]
        title = VGroup(*title_parts).arrange(RIGHT, buff=0.25).move_to(UP * 3.35)
        self.play(t.animate.set_value(2.5), Write(title), run_time=2)

        def frame(names, color, label, label_dir):
            mobs = VGroup(*[cells[n] for n in names])
            rect = SurroundingRectangle(mobs, color=color, buff=0.08, corner_radius=0.15, stroke_width=5)
            lab = Text(label, font=FONT, font_size=24, color=color).next_to(rect, label_dir, buff=0.12)
            return rect, lab

        quark_names = ["上夸克", "魅夸克", "頂夸克", "下夸克", "奇夸克", "底夸克", "膠子"]
        r1, l1 = frame(quark_names[:6], ACCENT, "SU(3) 強作用", LEFT)
        l1.rotate(PI / 2).next_to(r1, LEFT, buff=0.15)
        r1g = SurroundingRectangle(cells["膠子"], color=ACCENT, buff=0.06, stroke_width=5)
        self.play(t.animate.set_value(4.5), Indicate(title_parts[0], color=ACCENT), Create(r1), Create(r1g),
                  FadeIn(l1), run_time=2)
        self.play(t.animate.set_value(5.5), run_time=1)

        ew = ["電子", "緲子", "τ 子", "電微中子", "緲微中子", "τ 微中子"]
        r2, l2 = frame(ew, FIELD, "SU(2)×U(1) 電弱", LEFT)
        l2.rotate(PI / 2).next_to(r2, LEFT, buff=0.15)
        r2b = SurroundingRectangle(VGroup(cells["光子"], cells["Z 玻色子"], cells["W 玻色子"]), color=FIELD,
                                   buff=0.06, stroke_width=5)
        self.play(t.animate.set_value(7.5), Indicate(title_parts[2], color=FIELD),
                  Indicate(title_parts[4], color=PARTICLE), r1.animate.set_stroke(opacity=0.35),
                  r1g.animate.set_stroke(opacity=0.35), l1.animate.set_opacity(0.45),
                  Create(r2), Create(r2b), FadeIn(l2), run_time=2)
        self.play(t.animate.set_value(8.5), run_time=1)

        rh = SurroundingRectangle(cells["希格斯"], color=HIGGS, buff=0.08, stroke_width=6)
        lh = Text("給予質量", font=FONT, font_size=26, color=HIGGS).next_to(rh, DOWN, buff=0.15)
        self.play(t.animate.set_value(10), Create(rh), FadeIn(lh), cells["希格斯"].animate.scale(1.12), run_time=2)
        self.play(t.animate.set_value(11.5), r1.animate.set_stroke(opacity=1), r1g.animate.set_stroke(opacity=1),
                  l1.animate.set_opacity(1), run_time=1.5)
        self.play(t.animate.set_value(15), run_time=3.5, rate_func=linear)
