"""String theory: one closed string, different vibration modes = different particles."""
import numpy as np
from manim import *

from style import ACCENT, FIELD, FONT, MUTED, PARTICLE, TEXT

MODES = [(2, FIELD), (3, PARTICLE), (5, ACCENT)]


def loop(center, R, amps, t, color, width=6):
    """Closed string whose radius is modulated by a mix of modes."""
    def f(th):
        r = R
        for (n, _), a in zip(MODES, amps):
            r += a * np.sin(n * th + 0.3 * n) * np.cos(n * 1.4 * t)
        return center + np.array([r * np.cos(th), r * np.sin(th), 0])
    return ParametricFunction(f, t_range=[0, TAU], color=color, stroke_width=width)


class Main(Scene):
    def construct(self):
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t)
        amps = [ValueTracker(0.0) for _ in MODES]
        col = ValueTracker(0)

        def big_color():
            c = col.get_value()
            i = int(np.clip(np.floor(c), 0, 2))
            j = min(i + 1, 2)
            return interpolate_color(ManimColor(MODES[i][1]), ManimColor(MODES[j][1]), c - i)

        center = UP * 0.45
        big = always_redraw(lambda: VGroup(
            loop(center, 1.6, [a.get_value() for a in amps], t.get_value(), big_color(), 14).set_stroke(opacity=0.18),
            loop(center, 1.6, [a.get_value() for a in amps], t.get_value(), big_color(), 6),
        ))

        title = Text("弦論", font=FONT, font_size=52, color=TEXT).to_corner(UR, buff=0.55)
        sub = Text("最基本的是一維的弦", font=FONT, font_size=28, color=MUTED).next_to(title, DOWN, aligned_edge=RIGHT)
        caps = [Text(f"振動模式 {k}", font=FONT, font_size=34, color=c) for k, (_, c) in enumerate(MODES, 1)]
        for c in caps:
            c.move_to(DOWN * 2.0)

        self.add(big)
        self.play(amps[0].animate.set_value(0.35), FadeIn(caps[0]), run_time=1.5)
        self.play(FadeIn(title), FadeIn(sub), run_time=1)
        self.wait(1.3)
        self.play(amps[0].animate.set_value(0), amps[1].animate.set_value(0.3), col.animate.set_value(1),
                  FadeTransform(caps[0], caps[1]), run_time=1.4)
        self.wait(1.3)
        self.play(amps[1].animate.set_value(0), amps[2].animate.set_value(0.22), col.animate.set_value(2),
                  FadeTransform(caps[1], caps[2]), run_time=1.4)
        self.wait(1.3)

        # split into three strings side by side, each a different "particle"
        small = VGroup()
        labels = VGroup()
        for k, (n, c) in enumerate(MODES):
            ctr = np.array([-4.3 + 4.3 * k, 0.55, 0])
            a = [0.0, 0.0, 0.0]
            a[k] = [0.28, 0.24, 0.17][k]
            m = always_redraw(lambda ctr=ctr, a=a, c=c: VGroup(
                loop(ctr, 1.15, a, t.get_value(), c, 12).set_stroke(opacity=0.18),
                loop(ctr, 1.15, a, t.get_value(), c, 5)))
            small.add(m)
            lab = Text(f"模式 {k + 1} → 粒子 {'ABC'[k]}", font=FONT, font_size=30, color=c).move_to(ctr + DOWN * 1.75)
            labels.add(lab)
        self.play(FadeOut(big), FadeOut(caps[2]), *[FadeIn(m, scale=0.5) for m in small], run_time=1.5)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in labels], lag_ratio=0.35), run_time=2)
        msg = Text("不同的振動 ＝ 不同的粒子", font=FONT, font_size=36, color=TEXT).move_to(DOWN * 2.45)
        self.play(Write(msg), run_time=1.5)
        self.wait(4.5)
