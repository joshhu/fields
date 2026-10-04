"""Newton's force-first logic vs. gauge theory's symmetry-first logic."""
import numpy as np
from manim import *

from style import ACCENT, FIELD, FONT, MUTED, PARTICLE, TEXT


def box(txt, color, w=2.6):
    t = Text(txt, font=FONT, font_size=30, color=TEXT)
    r = RoundedRectangle(corner_radius=0.18, width=max(w, t.width + 0.45), height=1.0, stroke_color=color,
                         stroke_width=3, fill_color=color, fill_opacity=0.12)
    t.move_to(r)
    return VGroup(r, t)


def flowing_dots(arrow, color, t, n=3):
    dots = VGroup(*[Dot(radius=0.07, color=color) for _ in range(n)])

    def upd(g):
        s, e = arrow.get_start(), arrow.get_end()
        for i, d in enumerate(g):
            a = (t.get_value() * 0.8 + i / n) % 1
            d.move_to(s + (e - s) * a)
            d.set_opacity(np.sin(np.pi * a))
    dots.add_updater(upd)
    return dots


class Main(Scene):
    def construct(self):
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t)

        # top row: Newton
        lab1 = Text("牛頓的時代", font=FONT, font_size=34, color=MUTED)
        n1 = box("觀察到一種力", PARTICLE)
        n2 = box("寫出方程式", PARTICLE)
        row1 = VGroup(n1, n2).arrange(RIGHT, buff=1.2)

        # bottom row: gauge theory
        lab2 = Text("規範場論", font=FONT, font_size=34, color=FIELD)
        g1 = box("指定對稱性", FIELD)
        g2 = box("拉格朗日量", FIELD)
        g3 = box("所有交互作用", FIELD)
        row2 = VGroup(g1, g2, g3).arrange(RIGHT, buff=0.8)
        lab2.next_to(row2, LEFT, buff=0.45)
        VGroup(lab2, row2).move_to(DOWN * 0.6)
        row1.align_to(row2, LEFT).set_y(1.6)
        lab1.next_to(row1, LEFT, buff=0.45).align_to(lab2, RIGHT)
        a1 = Arrow(n1.get_right(), n2.get_left(), buff=0.12, color=PARTICLE, stroke_width=5)
        a2 = Arrow(g1.get_right(), g2.get_left(), buff=0.1, color=FIELD, stroke_width=5)
        a3 = Arrow(g2.get_right(), g3.get_left(), buff=0.1, color=FIELD, stroke_width=5)

        self.wait(0.5)
        self.play(FadeIn(lab1, shift=RIGHT * 0.3), FadeIn(n1, shift=UP * 0.2), run_time=1.2)
        self.play(GrowArrow(a1), run_time=0.8)
        self.add(flowing_dots(a1, PARTICLE, t))
        self.play(FadeIn(n2, shift=UP * 0.2), run_time=1)
        self.wait(1.2)

        self.play(FadeIn(lab2, shift=RIGHT * 0.3), FadeIn(g1, shift=UP * 0.2), run_time=1.2)
        self.play(GrowArrow(a2), run_time=0.7)
        self.add(flowing_dots(a2, FIELD, t))
        self.play(FadeIn(g2, shift=UP * 0.2), run_time=0.9)
        self.play(GrowArrow(a3), run_time=0.7)
        self.add(flowing_dots(a3, FIELD, t))
        self.play(FadeIn(g3, shift=UP * 0.2), run_time=0.9)
        self.wait(0.8)

        # dim Newton, make the gauge row glow
        glow = SurroundingRectangle(VGroup(g1, g3), color=FIELD, buff=0.25, corner_radius=0.3, stroke_width=4)
        self.play(VGroup(lab1, n1, n2, a1).animate.set_opacity(0.35), Create(glow),
                  *[g[0].animate.set_fill(opacity=0.3) for g in (g1, g2, g3)], run_time=1.5)
        glow.add_updater(lambda m: m.set_stroke(opacity=0.55 + 0.45 * np.sin(t.get_value() * 3)))

        noether = VGroup(
            Text("諾特定理：", font=FONT, font_size=34, color=ACCENT),
            Text("對稱性 ⇔ 守恆律", font=FONT, font_size=34, color=TEXT),
        ).arrange(RIGHT, buff=0.2).move_to(DOWN * 2.3)
        self.play(Write(noether), run_time=1.6)
        self.wait(5)
