import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

POS = [0.8, 1.35, 1.9, 2.45, 3.0]
NEG = [-0.9, -1.35, -1.8, -2.25, -2.7]
XS = np.arange(-5.4, -0.79, 0.5)


def photon(start, end, color=PARTICLE):
    d = end - start
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0], 0])
    return ParametricFunction(lambda s: start + u * s * L + n * 0.12 * np.sin(s * L * 14),
                              t_range=[0, 1], color=color, stroke_width=3)


class Main(Scene):
    def construct(self):
        axis = Arrow([-6.4, -2.85, 0], [-6.4, 3.7, 0], buff=0, color=MUTED, stroke_width=3)
        elab = Text("能量 E", font=FONT, font_size=30, color=MUTED).next_to(axis, RIGHT, buff=0.1).shift(UP * 3.0)
        zero = DashedLine([-6.4, 0, 0], [-0.5, 0, 0], color=MUTED, stroke_width=2)
        zl = Text("E = 0", font="Cambria Math", font_size=28, color=MUTED).next_to(zero, RIGHT, buff=0.15)
        pos = VGroup(*[Line([-5.7, y, 0], [-0.6, y, 0], color=FIELD, stroke_width=2.5) for y in POS])
        neg = VGroup(*[Line([-5.7, y, 0], [-0.6, y, 0], color=ACCENT, stroke_width=2.5) for y in NEG])
        pl = Text("正能態", font=FONT, font_size=30, color=FIELD).next_to(pos, RIGHT, buff=0.25).shift(UP * 0.4)
        nl = Text("負能態", font=FONT, font_size=30, color=ACCENT).next_to(neg, RIGHT, buff=0.25).shift(DOWN * 0.2)
        inf = Text("⋮  → −∞", font="Cambria Math", font_size=30, color=ACCENT).next_to(nl, DOWN, buff=0.15)
        self.play(GrowArrow(axis), FadeIn(elab), Create(zero), FadeIn(zl), run_time=1.2)
        self.play(LaggedStartMap(Create, pos, lag_ratio=0.1), LaggedStartMap(Create, neg, lag_ratio=0.1),
                  FadeIn(pl), FadeIn(nl), FadeIn(inf), run_time=1.8)

        # Part 1: electron keeps falling
        title = Text("狄拉克方程式的負能量解", font=FONT, font_size=38, color=TEXT).move_to([3.2, 3.0, 0])
        title.to_edge(RIGHT, buff=0.5)
        e = Dot([-3.15, POS[2], 0], radius=0.16, color=PARTICLE)
        el = Text("e⁻", font="Cambria Math", font_size=30, color=PARTICLE)
        el.add_updater(lambda m: m.next_to(e, UR, buff=0.02))
        self.play(FadeIn(title), FadeIn(e), FadeIn(el), run_time=0.8)
        q = Text("電子會一直往下掉？", font=FONT, font_size=36, color=ACCENT).to_edge(RIGHT, buff=0.5).shift(UP * 1.2)
        levels = [POS[1], POS[0], NEG[0], NEG[1], NEG[2], NEG[3], NEG[4]]
        for i, y in enumerate(levels):
            start = e.get_center()
            self.play(e.animate.move_to([-3.15, y, 0]), run_time=0.45, rate_func=rush_into)
            ph = photon(start + RIGHT * 0.2, start + RIGHT * 2.2 + UP * 0.3)
            anims = [ShowPassingFlash(ph, time_width=0.6)]
            if i == 2:
                anims.append(FadeIn(q))
            self.play(*anims, run_time=0.4)
        boom = Text("不斷釋放能量 → 世界崩潰", font=FONT, font_size=34, color=ACCENT).next_to(q, DOWN, buff=0.3)
        boom.align_to(q, RIGHT)
        self.play(e.animate.move_to([-3.15, -3.4, 0]).set_opacity(0), FadeIn(boom), run_time=1.0)
        el.clear_updaters()
        self.remove(el)

        # Part 2: Dirac sea
        sea = VGroup(*[Dot([x, y, 0], radius=0.13, color=FIELD) for y in NEG for x in XS])
        self.play(FadeOut(q), FadeOut(boom), LaggedStartMap(FadeIn, sea, lag_ratio=0.01), run_time=2)
        sea_l = Text("狄拉克海：負能態早已填滿", font=FONT, font_size=36, color=FIELD).to_edge(RIGHT, buff=0.5).shift(UP * 1.2)
        self.play(FadeIn(sea_l), run_time=0.8)
        e2 = Dot([-3.15, POS[1], 0], radius=0.16, color=PARTICLE)
        self.play(FadeIn(e2), run_time=0.4)
        for _ in range(2):
            self.play(e2.animate.move_to([-3.15, -0.35, 0]), run_time=0.5, rate_func=rush_into)
            self.play(e2.animate.move_to([-3.15, POS[0], 0]), run_time=0.5, rate_func=rush_from)
        pauli = Text("包立不相容原理：無處可掉", font=FONT, font_size=32, color=MUTED).next_to(sea_l, DOWN, buff=0.25)
        pauli.align_to(sea_l, RIGHT)
        self.play(FadeIn(pauli), sea.animate.set_color("#29B6F6"), run_time=1.0)

        # Part 3: photon kicks an electron out -> hole = positron
        idx = 2 * len(XS) + 3  # an electron in the middle of the sea
        target = sea[idx]
        hp = target.get_center()
        ph = photon(hp + LEFT * 3.5 + DOWN * 0.0 + UP * 0.0, hp, color="#FFF59D")
        self.play(FadeOut(sea_l), FadeOut(pauli), ShowPassingFlash(ph, time_width=0.8), run_time=0.8)
        hole = Circle(radius=0.16, color=PARTICLE, stroke_width=4).move_to(hp)
        self.play(target.animate.move_to([hp[0], POS[2], 0]).set_color(PARTICLE), FadeIn(hole), run_time=1.0)
        e_up = Text("e⁻", font="Cambria Math", font_size=32, color=PARTICLE).next_to(target, UR, buff=0.02)
        h_lab = Text("電洞", font=FONT, font_size=30, color=PARTICLE, weight=BOLD)
        h_lab.add_background_rectangle(color=BG, opacity=0.9, buff=0.06)
        h_lab.next_to(hole, DOWN, buff=0.05)
        self.play(FadeIn(e_up), FadeIn(h_lab), Flash(hole, color=PARTICLE), run_time=1.0)
        res = VGroup(Text("電洞 ＝ 帶正電的粒子", font=FONT, font_size=36, color=PARTICLE),
                     Text("正電子 e⁺（1932 年發現）", font=FONT, font_size=36, color=PARTICLE, weight=BOLD)
                     ).arrange(DOWN, aligned_edge=RIGHT, buff=0.25).to_edge(RIGHT, buff=0.5).shift(UP * 1.0)
        self.play(FadeIn(res[0], shift=LEFT * 0.3), run_time=1.0)
        self.play(FadeIn(res[1], shift=LEFT * 0.3), Indicate(hole, scale_factor=1.6, color=ACCENT), run_time=1.5)
        # hole drifts (behaves like a particle)
        self.play(hole.animate.shift(RIGHT * 1.5), sea[idx + 3].animate.shift(LEFT * 1.5),
                  h_lab.animate.shift(RIGHT * 1.5), run_time=2.0)
        self.wait(1.5)
