"""Hawking radiation: virtual pairs at the horizon, one falls in, one escapes."""
import numpy as np
from manim import *

from style import ACCENT, FIELD, FONT, MUTED, PARTICLE, TEXT

CENTER = np.array([-1.2, 0.35, 0])


class Main(Scene):
    def construct(self):
        rng = np.random.default_rng(7)
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t)

        # twinkling star field
        stars = VGroup(*[Dot(np.array([rng.uniform(-7, 7), rng.uniform(-3.6, 3.9), 0]),
                             radius=rng.uniform(0.008, 0.025), color=WHITE) for _ in range(160)])
        phases = rng.uniform(0, TAU, len(stars))
        stars.add_updater(lambda g: [d.set_opacity(0.25 + 0.35 * (1 + np.sin(t.get_value() * 1.5 + p)) / 2)
                                     for d, p in zip(g, phases)])
        self.add(stars)

        R = ValueTracker(1.7)

        def make_hole():
            r = R.get_value()
            glow = VGroup(*[Circle(radius=r + 0.04 * k, stroke_color=PARTICLE, stroke_width=6,
                                   stroke_opacity=0.5 * (1 - k / 9) ** 2) for k in range(9)])
            core = Circle(radius=r, fill_color=BLACK, fill_opacity=1, stroke_color="#FFE0B2", stroke_width=3)
            return VGroup(glow, core).move_to(CENTER)

        hole = always_redraw(make_hole)

        pairs = VGroup()
        state = []  # per pair: [angle, age]

        def spawn():
            ang = rng.uniform(0, TAU)
            a = Dot(radius=0.075, color=FIELD)
            b = Dot(radius=0.06, color=ACCENT)
            link = Line(ORIGIN, RIGHT, stroke_width=2, color=MUTED)
            g = VGroup(a, b, link)
            pairs.add(g)
            state.append([ang, 0.0, rng.uniform(0.9, 1.3)])

        def update_pairs(group, dt):
            if rng.random() < dt * 4.0:
                spawn()
            r = R.get_value()
            dead = []
            for i, (g, st) in enumerate(zip(group, state)):
                st[1] += dt
                ang, age, sp = st
                u = np.array([np.cos(ang), np.sin(ang), 0])
                v = np.array([-u[1], u[0], 0])
                base = CENTER + u * (r + 0.1)
                if age < 0.6:  # pair pops out of the vacuum, separates sideways
                    s = age / 0.6
                    pa = base + v * 0.18 * s
                    pb = base - v * 0.18 * s
                    g[0].move_to(pa).set_opacity(s)
                    g[1].move_to(pb).set_opacity(s)
                    g[2].put_start_and_end_on(pa + 1e-3 * RIGHT, pb).set_stroke(opacity=0.6 * s)
                else:
                    s = age - 0.6
                    pa = base + v * 0.18 + u * sp * 1.6 * s  # escapes
                    pb = base - v * 0.18 - u * min(s * 0.6, 0.45)  # falls in
                    g[0].move_to(pa).set_opacity(max(0, 1 - s / 4.5))
                    g[1].move_to(pb).set_opacity(max(0, 1 - s * 2.2))
                    g[2].set_stroke(opacity=0)
                    if s > 4.5:
                        dead.append(i)
            for i in reversed(dead):
                group.remove(group[i])
                state.pop(i)

        pairs.add_updater(update_pairs)

        title = Text("霍金輻射", font=FONT, font_size=48, color=TEXT).to_corner(UR, buff=0.55)
        leg1 = VGroup(Dot(color=FIELD), Text("逃逸 → 輻射", font=FONT, font_size=28, color=FIELD)).arrange(RIGHT)
        leg2 = VGroup(Dot(color=ACCENT), Text("掉入黑洞", font=FONT, font_size=28, color=ACCENT)).arrange(RIGHT)
        legend = VGroup(leg1, leg2).arrange(DOWN, aligned_edge=LEFT).next_to(title, DOWN, buff=0.4, aligned_edge=RIGHT)
        horizon = Text("事件視界", font=FONT, font_size=28, color=PARTICLE)
        horizon.move_to(CENTER + np.array([2.6, -1.85, 0]))
        h_arrow = Arrow(horizon.get_left(), CENTER + np.array([1.2, -1.2, 0]), buff=0.1,
                        color=PARTICLE, stroke_width=3, max_tip_length_to_length_ratio=0.15)
        msg = Text("黑洞並不全黑，它會慢慢蒸發", font=FONT, font_size=34, color=TEXT).move_to(DOWN * 2.45 + RIGHT * 3.3)

        self.play(FadeIn(hole), run_time=1.5)
        self.add(pairs)
        self.wait(2.5)
        self.play(FadeIn(title), FadeIn(horizon), GrowArrow(h_arrow), run_time=1.5)
        self.play(FadeIn(legend), run_time=1.2)
        self.wait(3)
        self.play(FadeIn(msg), FadeOut(horizon), FadeOut(h_arrow), run_time=1.3)
        self.play(R.animate.set_value(0.95), run_time=10, rate_func=rate_functions.ease_in_quad)
