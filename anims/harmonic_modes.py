import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

PHOTON = "#FFF59D"


def photon_icon():
    w = ParametricFunction(lambda s: [s, 0.13 * np.sin(14 * s) * np.exp(-(s / 0.28) ** 2), 0],
                           t_range=[-0.5, 0.5], color=PHOTON, stroke_width=4)
    g = Text("γ", font="Cambria Math", font_size=28, color=PHOTON).next_to(w, UP, buff=0.02)
    return VGroup(w, g)


class Main(Scene):
    def construct(self):
        head = Text("電磁場 ＝ 許多振動模式", font=FONT, font_size=40, color=FIELD).move_to([0.8, -2.45, 0])
        self.play(FadeIn(head), run_time=1)
        t = ValueTracker(0)
        X0, X1 = -6.2, -1.4
        YS = [2.1, 0.55, -1.0]
        H = 0.55
        walls = VGroup(Line([X0, 2.9, 0], [X0, -1.75, 0]), Line([X1, 2.9, 0], [X1, -1.75, 0])).set_stroke(MUTED, 5)
        self.play(Create(walls), run_time=0.8)
        modes = VGroup()
        for n, y in enumerate(YS, start=1):
            def mk(n=n, y=y):
                a = H * np.cos(2.2 * n * t.get_value())
                L = X1 - X0
                return VGroup(
                    ParametricFunction(lambda x: [x, y + a * np.sin(n * PI * (x - X0) / L), 0],
                                       t_range=[X0, X1], color=FIELD, stroke_width=4),
                    ParametricFunction(lambda x: [x, y - a * np.sin(n * PI * (x - X0) / L), 0],
                                       t_range=[X0, X1], color=FIELD, stroke_width=1.5).set_stroke(opacity=0.35))
            modes.add(always_redraw(mk))
        labels = VGroup(*[Text(f"n = {n}", font="Cambria Math", font_size=30, color=MUTED).move_to([X0 - 0.0, y, 0]).shift(RIGHT * 0.6 + UP * 0.55)
                          for n, y in zip([1, 2, 3], YS)])
        self.add(modes)
        self.play(t.animate.increment_value(1.5), FadeIn(labels), run_time=1.5, rate_func=linear)

        # ladders (quantum harmonic oscillators)
        LX = 0.2
        ladders = VGroup()
        for y in YS:
            rungs = VGroup(*[Line([LX - 0.45, y - 0.6 + 0.28 * k, 0], [LX + 0.45, y - 0.6 + 0.28 * k, 0],
                                  color=MUTED, stroke_width=2.5) for k in range(5)])
            ladders.add(rungs)
        arrows = VGroup(*[Arrow([X1 + 0.15, y, 0], [LX - 0.6, y, 0], buff=0, color=MUTED, stroke_width=2,
                                max_tip_length_to_length_ratio=0.25) for y in YS])
        osc = Text("量子諧振子", font=FONT, font_size=30, color=MUTED).move_to([LX, 3.15, 0])
        self.play(Create(ladders, lag_ratio=0.2), FadeIn(arrows, lag_ratio=0.2),
                  FadeIn(osc), t.animate.increment_value(2), run_time=2, rate_func=linear)
        levels = [0, 0, 0]
        marks = VGroup(*[Dot([LX, y - 0.6, 0], radius=0.11, color=PARTICLE) for y in YS])
        self.play(FadeIn(marks), t.animate.increment_value(0.8), run_time=0.8, rate_func=linear)

        icons = VGroup()
        slots = [[] for _ in YS]
        steps = [0, 1, 0, 2, 1, 0, 2, 1]
        cap = Text("能量升高一格 ＝ 多一個光子", font=FONT, font_size=40, color=PHOTON).move_to([0.8, -2.45, 0])
        for i, m in enumerate(steps):
            levels[m] += 1
            y = YS[m]
            ic = photon_icon().scale(0.9)
            k = len(slots[m])
            ic.move_to([1.6 + 0.95 * k, y - 0.05, 0])
            slots[m].append(ic)
            anims = [marks[m].animate.move_to([LX, y - 0.6 + 0.28 * levels[m], 0]),
                     FadeIn(ic, shift=RIGHT * 0.4, scale=0.5), t.animate.increment_value(1.05)]
            if i == 1:
                anims.append(FadeOut(head))
            if i == 2:
                anims.append(FadeIn(cap))
            self.play(*anims, run_time=1.05, rate_func=linear)
            icons.add(ic)
        self.play(Indicate(icons, color=PARTICLE, scale_factor=1.1), t.animate.increment_value(1.5),
                  run_time=1.5, rate_func=linear)
        self.play(t.animate.increment_value(2), run_time=2, rate_func=linear)
