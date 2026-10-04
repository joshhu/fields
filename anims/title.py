import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT


class Main(Scene):
    def construct(self):
        rng = np.random.default_rng(1)
        # drifting star/particle dots
        dots = VGroup()
        vel = []
        for _ in range(160):
            d = Dot(point=[rng.uniform(-7.5, 7.5), rng.uniform(-4.2, 4.2), 0],
                    radius=rng.uniform(0.01, 0.035),
                    color=rng.choice([TEXT, FIELD, PARTICLE]))
            d.set_opacity(rng.uniform(0.3, 0.9))
            dots.add(d)
            vel.append(rng.normal(0, 0.08, 3) * np.array([1, 1, 0]))

        def drift(m, dt):
            for d, v in zip(m, vel):
                d.shift(v * dt)
                x, y, _ = d.get_center()
                if abs(x) > 7.6:
                    d.shift([-np.sign(x) * 15.2, 0, 0])
                if abs(y) > 4.3:
                    d.shift([0, -np.sign(y) * 8.6, 0])
        dots.add_updater(drift)
        self.add(dots)

        # expanding ripples from the center
        t = ValueTracker(0)
        def ripples():
            g = VGroup()
            tt = t.get_value()
            for k in range(7):
                r = ((tt * 0.9 + k * 1.2) % 8.4) + 0.05
                op = max(0, 1 - r / 8.4) * 0.7
                g.add(Circle(radius=r, color=FIELD, stroke_width=3).set_stroke(opacity=op))
            return g
        rip = always_redraw(ripples)
        self.add(rip)
        self.play(t.animate.set_value(3), run_time=3, rate_func=linear)

        title = Text("場比粒子更基本", font=FONT, font_size=110, color=TEXT, weight=BOLD)
        sub = Text("物理學三百年的終極轉向", font=FONT, font_size=48, color=FIELD)
        sub.next_to(title, DOWN, buff=0.5)
        glow = title.copy().set_fill(opacity=0).set_stroke(FIELD, width=10, opacity=0.25)
        self.play(t.animate.set_value(7), FadeIn(glow), Write(title, run_time=3), run_time=4, rate_func=linear)
        self.play(t.animate.set_value(10), FadeIn(sub, shift=UP * 0.3), run_time=3, rate_func=linear)
        self.play(t.animate.set_value(16), run_time=6, rate_func=linear)
        grp = VGroup(title, glow, sub)
        self.play(t.animate.set_value(19), grp.animate.scale(0.6).to_edge(UP, buff=0.8), run_time=3, rate_func=linear)
        self.play(t.animate.set_value(24), run_time=5, rate_func=linear)
