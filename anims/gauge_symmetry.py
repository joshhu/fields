import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

DUR = 21.0
LX, RX = -3.0, 3.9          # circle / triad centers
TOP_Y, BOT_Y = 1.2, -1.1
ALPHA, BETA = 50 * DEGREES, 80 * DEGREES
GREEN = "#81C784"


def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


VIEW = rot_x(-62 * DEGREES) @ rot_z(-35 * DEGREES)


def proj(v):
    w = VIEW @ v
    return np.array([w[0], w[1], 0.0])


def triad(center, R, length=0.95):
    cols = ["#EF5350", GREEN, FIELD]
    g = VGroup()
    for k in range(3):
        e = np.zeros(3)
        e[k] = length
        end = np.array(center) + proj(R @ e)
        g.add(Arrow(center, end, buff=0, color=cols[k], stroke_width=6, max_tip_length_to_length_ratio=0.22))
    return g


class Main(Scene):
    def construct(self):
        # ---------- U(1): phase rotations on a circle ----------
        circ_t = Circle(radius=0.85, color=MUTED, stroke_width=3).move_to([LX, TOP_Y, 0])
        circ_b = Circle(radius=0.85, color=MUTED, stroke_width=3).move_to([LX, BOT_Y, 0])
        th_t, th_b = ValueTracker(0), ValueTracker(0)

        def phase_arrow(c, tr):
            return always_redraw(lambda: Arrow(
                c.get_center(), c.get_center() + 0.85 * np.array([np.cos(tr.get_value()), np.sin(tr.get_value()), 0]),
                buff=0, color=TEXT, stroke_width=6, max_tip_length_to_length_ratio=0.25))

        arr_t, arr_b = phase_arrow(circ_t, th_t), phase_arrow(circ_b, th_b)

        # ---------- SU(2)/rotations in 3D: a triad on a sphere ----------
        sph_t = VGroup(Circle(radius=1.0, color=MUTED, stroke_width=2).set_stroke(opacity=0.5),
                       Ellipse(width=2.0, height=0.6, color=MUTED, stroke_width=1.5).set_stroke(opacity=0.4)).move_to([RX, TOP_Y, 0])
        sph_b = sph_t.copy().move_to([RX, BOT_Y, 0])
        a1_t, a2_t, a1_b, a2_b = (ValueTracker(0) for _ in range(4))
        # top: A (x-rotation) then B (z-rotation); bottom: B then A
        tri_t = always_redraw(lambda: triad([RX, TOP_Y, 0], rot_z(a2_t.get_value()) @ rot_x(a1_t.get_value())))
        tri_b = always_redraw(lambda: triad([RX, BOT_Y, 0], rot_x(a2_b.get_value()) @ rot_z(a1_b.get_value())))

        self.play(Create(circ_t), Create(circ_b), FadeIn(arr_t), FadeIn(arr_b),
                  FadeIn(sph_t), FadeIn(sph_b), FadeIn(tri_t), FadeIn(tri_b), run_time=1.0)

        row_t = Text("先 α 再 β", font=FONT, font_size=28, t2c={"α": PARTICLE, "β": ACCENT}).move_to([LX - 2.2, TOP_Y, 0])
        row_b = Text("先 β 再 α", font=FONT, font_size=28, t2c={"α": PARTICLE, "β": ACCENT}).move_to([LX - 2.2, BOT_Y, 0])
        self.play(FadeIn(row_t), FadeIn(row_b), run_time=0.5)

        def arc(c, a0, a1, col):
            return Arc(radius=0.55, start_angle=a0, angle=a1 - a0, color=col, stroke_width=7).shift(c.get_center())

        self.play(th_t.animate.set_value(ALPHA), th_b.animate.set_value(BETA), run_time=1.0)
        a_t1, a_b1 = arc(circ_t, 0, ALPHA, PARTICLE), arc(circ_b, 0, BETA, ACCENT)
        self.add(a_t1, a_b1)
        self.play(th_t.animate.set_value(ALPHA + BETA), th_b.animate.set_value(ALPHA + BETA), run_time=1.0)
        a_t2, a_b2 = arc(circ_t, ALPHA, ALPHA + BETA, ACCENT), arc(circ_b, BETA, ALPHA + BETA, PARTICLE)
        self.add(a_t2, a_b2)
        eq = Text("＝", font=FONT, font_size=60, color=GREEN).move_to([LX + 1.45, (TOP_Y + BOT_Y) / 2, 0])
        same = Text("結果相同", font=FONT, font_size=26, color=GREEN).next_to(eq, DOWN, buff=0.1)
        self.play(FadeIn(eq, scale=1.4), FadeIn(same), run_time=0.6)
        self.wait(4.3 - self.renderer.time if self.renderer.time < 4.3 else 0.1)

        title_l = Text("U(1)：可交換（阿貝爾群）", font=FONT, font_size=32, color=TEXT).move_to([LX - 0.6, 2.65, 0])
        title_r = Text("SU(2)：不可交換（非阿貝爾群）", font=FONT, font_size=32, color=TEXT).move_to([RX - 0.4, 2.65, 0])
        self.play(FadeIn(title_l), FadeIn(title_r), run_time=0.8)

        rt = Text("先 A 再 B", font=FONT, font_size=28, t2c={"A": PARTICLE, "B": ACCENT}).move_to([RX - 2.15, TOP_Y, 0])
        rb = Text("先 B 再 A", font=FONT, font_size=28, t2c={"A": PARTICLE, "B": ACCENT}).move_to([RX - 2.15, BOT_Y, 0])
        self.play(FadeIn(rt), FadeIn(rb), run_time=0.5)

        def run_3d():
            self.play(a1_t.animate.set_value(PI / 2), a1_b.animate.set_value(PI / 2), run_time=1.6)
            self.play(a2_t.animate.set_value(PI / 2), a2_b.animate.set_value(PI / 2), run_time=1.6)

        run_3d()
        neq = Text("≠", font=FONT, font_size=64, color="#FF5252").move_to([RX + 1.55, (TOP_Y + BOT_Y) / 2, 0])
        diff = Text("結果不同", font=FONT, font_size=26, color="#FF5252").next_to(neq, DOWN, buff=0.1)
        self.play(FadeIn(neq, scale=1.4), FadeIn(diff), run_time=0.6)
        self.wait(1.0)

        ym = Text("楊－米爾斯理論（1954）：把規範對稱性推廣到非阿貝爾群", font=FONT, font_size=32, color=PARTICLE)
        ym.move_to([0, -2.6, 0])
        self.play(Write(ym), run_time=1.6)

        # replay the 3D comparison to keep the frame alive
        while DUR - self.renderer.time > 4.6:
            self.play(*[t.animate.set_value(0) for t in (a1_t, a2_t, a1_b, a2_b)], run_time=1.0)
            run_3d()
        self.wait(max(0.1, DUR - self.renderer.time))
