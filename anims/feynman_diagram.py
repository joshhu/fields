import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT
from g2util import wavy_line, wavy_arc

DUR = 22.0
PANEL_X = [-4.8, -0.4, 3.9]
YB, YT = -1.7, 1.7      # diagram vertical extent


def fermion(a, b, color=PARTICLE, reverse=False):
    """Straight fermion line with an arrow at its midpoint."""
    a, b = np.array(a, float), np.array(b, float)
    line = Line(a, b, color=color, stroke_width=4)
    d = (b - a) / np.linalg.norm(b - a) * (-1 if reverse else 1)
    mid = (a + b) / 2
    tip = Triangle(color=color, fill_opacity=1, stroke_width=0).scale(0.11)
    tip.rotate(np.arctan2(d[1], d[0]) - PI / 2).move_to(mid)
    return VGroup(line, tip)


def vertex(p):
    return Dot(p, radius=0.08, color=TEXT)


class Main(Scene):
    def construct(self):
        # time axis on the far left
        t_axis = Arrow([-6.9, YB, 0], [-6.9, YT, 0], buff=0, color=MUTED, stroke_width=3)
        t_lab = Text("時間", font=FONT, font_size=26, color=MUTED).next_to(t_axis, RIGHT, buff=0.1).shift(DOWN * 1.2)

        # (a) electron-electron scattering via photon exchange
        cx = PANEL_X[0]
        v1, v2 = np.array([cx - 0.9, 0, 0]), np.array([cx + 0.9, 0, 0])
        a_lines = VGroup(
            fermion([cx - 1.6, YB, 0], v1), fermion(v1, [cx - 1.6, YT, 0]),
            fermion([cx + 1.6, YB, 0], v2), fermion(v2, [cx + 1.6, YT, 0]))
        a_ph = wavy_line(v1, v2, amp=0.12, waves=6, color=FIELD)
        a_dots = VGroup(vertex(v1), vertex(v2))
        a_lab = Text("電子散射", font=FONT, font_size=32, color=TEXT).move_to([cx, -2.4, 0])
        a_ph_lab = Text("γ", font=FONT, font_size=30, color=FIELD).next_to(a_ph, UP, buff=0.15)

        self.play(Create(t_axis), FadeIn(t_lab), run_time=0.8)
        self.play(LaggedStart(*[Create(l) for l in a_lines[:2]], lag_ratio=0.5), run_time=1.4)
        self.play(LaggedStart(*[Create(l) for l in a_lines[2:]], lag_ratio=0.5), run_time=1.4)
        self.play(Create(a_ph), FadeIn(a_dots), FadeIn(a_ph_lab), run_time=1.2)
        self.play(FadeIn(a_lab, shift=UP * 0.2), run_time=0.7)

        head = Text("每一張圖 ＝ 微擾展開裡的一項", font=FONT, font_size=44, color=PARTICLE).move_to(UP * 3.0)
        self.play(Write(head), run_time=1.4)

        # (b) electron self-energy
        cx = PANEL_X[1]
        w1, w2 = np.array([cx, -0.75, 0]), np.array([cx, 0.75, 0])
        b_lines = VGroup(fermion([cx, YB, 0], w1), fermion(w1, w2), fermion(w2, [cx, YT, 0]))
        b_loop = wavy_arc([cx, 0, 0], 0.75, -PI / 2, PI / 2, amp=0.08, waves=7, color=FIELD)
        b_dots = VGroup(vertex(w1), vertex(w2))
        b_lab = Text("電子自能", font=FONT, font_size=32, color=TEXT).move_to([cx, -2.4, 0])
        plus1 = Text("+", font=FONT, font_size=64, color=TEXT).move_to([(PANEL_X[0] + PANEL_X[1]) / 2 + 0.1, 0, 0])
        self.play(FadeIn(plus1), run_time=0.4)
        self.play(Create(b_lines), run_time=1.6)
        self.play(Create(b_loop), FadeIn(b_dots), run_time=1.2)
        self.play(FadeIn(b_lab, shift=UP * 0.2), run_time=0.7)

        # (c) vacuum polarization
        cx = PANEL_X[2]
        u1, u2 = np.array([cx, -0.65, 0]), np.array([cx, 0.65, 0])
        c_ph1 = wavy_line([cx, YB, 0], u1, amp=0.1, waves=4, color=FIELD)
        c_ph2 = wavy_line(u2, [cx, YT, 0], amp=0.1, waves=4, color=FIELD)
        c_loop_r = ArcBetweenPoints(u1, u2, angle=PI, color=PARTICLE, stroke_width=4)
        c_loop_l = ArcBetweenPoints(u2, u1, angle=PI, color=PARTICLE, stroke_width=4)
        tip_r = Triangle(color=PARTICLE, fill_opacity=1, stroke_width=0).scale(0.11).move_to([cx + 0.65, 0, 0])
        tip_l = Triangle(color=PARTICLE, fill_opacity=1, stroke_width=0).scale(0.11).rotate(PI).move_to([cx - 0.65, 0, 0])
        c_dots = VGroup(vertex(u1), vertex(u2))
        c_lab = Text("真空極化", font=FONT, font_size=32, color=TEXT).move_to([cx, -2.4, 0])
        c_pair = Text("e⁺e⁻", font=FONT, font_size=26, color=PARTICLE).move_to([cx - 1.3, 0, 0])
        plus2 = Text("+", font=FONT, font_size=64, color=TEXT).move_to([(PANEL_X[1] + PANEL_X[2]) / 2 - 0.1, 0, 0])
        self.play(FadeIn(plus2), run_time=0.4)
        self.play(Create(c_ph1), run_time=0.8)
        self.play(Create(c_loop_r), Create(c_loop_l), FadeIn(tip_r), FadeIn(tip_l), FadeIn(c_dots), run_time=1.2)
        self.play(Create(c_ph2), FadeIn(c_pair), run_time=0.8)
        self.play(FadeIn(c_lab, shift=UP * 0.2), run_time=0.7)

        dots = Text("+ …", font=FONT, font_size=56, color=TEXT).move_to([6.2, 0, 0])
        self.play(FadeIn(dots), run_time=0.6)

        note = Text("不是粒子軌跡，而是場的量子理論的計算工具", font=FONT, font_size=30, color=MUTED)
        note.move_to(UP * 2.25)
        self.play(FadeIn(note), run_time=1.0)

        # keep things alive: photons shimmer
        photons = [a_ph, b_loop, c_ph1, c_ph2]
        for ph in photons:
            ph.add_updater(lambda m, dt: m.set_stroke(opacity=0.75 + 0.25 * np.sin(self.renderer.time * 4)))
        remaining = DUR - self.renderer.time
        self.wait(max(1.0, remaining))
