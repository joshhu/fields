"""Unruh effect: inertial observer sees vacuum, accelerated observer sees a thermal bath."""
import numpy as np
from manim import *

from style import ACCENT, BG, FIELD, FONT, MUTED, PARTICLE, TEXT

LX, RX = -3.55, 3.55
OBS_Y = -0.1


def rocket():
    body = RoundedRectangle(corner_radius=0.18, width=0.55, height=1.3, fill_color="#CFD8DC", fill_opacity=1,
                            stroke_color=WHITE, stroke_width=2)
    nose = Triangle(fill_color=ACCENT, fill_opacity=1, stroke_width=0).scale(0.33).next_to(body, UP, buff=-0.02)
    win = Circle(radius=0.12, fill_color=FIELD, fill_opacity=1, stroke_color=WHITE, stroke_width=2).move_to(
        body.get_center() + UP * 0.25)
    finl = Polygon([-0.27, -0.3, 0], [-0.5, -0.7, 0], [-0.27, -0.65, 0], fill_color=ACCENT, fill_opacity=1,
                   stroke_width=0).move_to(body.get_center() + np.array([-0.36, -0.45, 0]))
    finr = finl.copy().flip(UP).move_to(body.get_center() + np.array([0.36, -0.45, 0]))
    return VGroup(body, nose, win, finl, finr)


def floater():
    # an astronaut-ish probe drifting freely
    c = Circle(radius=0.38, fill_color="#CFD8DC", fill_opacity=1, stroke_color=WHITE, stroke_width=2)
    v = Circle(radius=0.22, fill_color=FIELD, fill_opacity=1, stroke_width=0).move_to(c.get_center() + UP * 0.05)
    ant = Line(c.get_top(), c.get_top() + UP * 0.3 + RIGHT * 0.15, stroke_width=3, color=WHITE)
    return VGroup(ant, c, v)


class Main(Scene):
    def construct(self):
        rng = np.random.default_rng(3)
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t)

        divider = DashedLine(UP * 2.95, DOWN * 2.0, color=MUTED, dash_length=0.12)

        # shared quantum field across both halves
        field = always_redraw(lambda: VGroup(*[
            FunctionGraph(lambda x, k=k: 2.25 + 0.15 * k + 0.12 * np.sin(1.6 * x - 2.2 * t.get_value() + k * 1.3)
                          * np.cos(0.7 * x + 0.6 * t.get_value()),
                          x_range=[-7.1, 7.1], color=FIELD, stroke_width=2, stroke_opacity=0.35 + 0.2 * k)
            for k in range(3)]))
        field_lab = Text("同一個量子場", font=FONT, font_size=28, color=FIELD).move_to(UP * 3.25)
        bg_field_lab = BackgroundRectangle(field_lab, color=BG, fill_opacity=1, buff=0.12)

        lab_l = Text("慣性觀察者", font=FONT, font_size=34, color=TEXT).move_to([LX, 1.45, 0])
        lab_r = Text("加速觀察者", font=FONT, font_size=34, color=TEXT).move_to([RX, 1.45, 0])
        see_l = Text("看到：一片真空", font=FONT, font_size=28, color=MUTED).move_to([LX, -1.65, 0])
        see_r = Text("看到：熱粒子浴", font=FONT, font_size=28, color=PARTICLE).move_to([RX, -1.65, 0])

        probe = floater().move_to([LX, OBS_Y, 0])
        probe.add_updater(lambda m: m.move_to([LX + 0.15 * np.sin(t.get_value() * 0.7),
                                               OBS_Y + 0.12 * np.sin(t.get_value() * 0.9), 0]).rotate(0.002))

        rk = rocket().move_to([RX, OBS_Y, 0])
        flame = always_redraw(lambda: Polygon(
            rk[0].get_bottom() + LEFT * 0.18, rk[0].get_bottom() + RIGHT * 0.18,
            rk[0].get_bottom() + DOWN * (0.55 + 0.18 * np.sin(t.get_value() * 25)),
            fill_color=PARTICLE, fill_opacity=0.95, stroke_width=0))

        # speed streaks rushing downward on the right to suggest acceleration
        streaks = VGroup(*[Line(UP * 0.0, UP * 0.5, stroke_width=2, color=MUTED, stroke_opacity=0.5) for _ in range(18)])
        sx = rng.uniform(RX - 3.0, RX + 3.0, len(streaks))
        sy0 = rng.uniform(0, 4.5, len(streaks))
        sp = rng.uniform(2.5, 4.5, len(streaks))
        streak_on = ValueTracker(0)

        def upd_streaks(g):
            for i, l in enumerate(g):
                y = 1.0 - ((sy0[i] + sp[i] * t.get_value()) % 3.6)
                l.put_start_and_end_on([sx[i], y, 0], [sx[i], y + 0.5, 0])
                l.set_stroke(opacity=0.45 * streak_on.get_value())
        streaks.add_updater(upd_streaks)

        # thermal particle cloud around the rocket
        N = 70
        ang = rng.uniform(0, TAU, N)
        rad = rng.uniform(0.7, 2.2, N)
        jit = rng.uniform(0, TAU, N)
        cols = [PARTICLE if rng.random() < 0.6 else ACCENT for _ in range(N)]
        cloud = VGroup(*[Dot(radius=rng.uniform(0.04, 0.08), color=c) for c in cols])
        heat = ValueTracker(0)

        def upd_cloud(g):
            tt = t.get_value()
            h = heat.get_value()
            for i, d in enumerate(g):
                a = ang[i] + 0.25 * tt * (1 if i % 2 else -1)
                r = rad[i] + 0.12 * np.sin(3 * tt + jit[i])
                x = RX + r * np.cos(a) * 1.25
                y = OBS_Y + r * np.sin(a) * 0.68
                x = max(min(x, 7.0), 0.25)
                d.move_to([x + 0.05 * np.sin(11 * tt + jit[i]), y + 0.05 * np.cos(13 * tt + jit[i]), 0])
                d.set_opacity(h * (0.55 + 0.45 * np.sin(5 * tt + jit[i])))
        cloud.add_updater(upd_cloud)

        msg = Text("粒子取決於觀察者，場才是客觀的", font=FONT, font_size=36, color=TEXT).move_to(DOWN * 2.5)
        msg_bg = BackgroundRectangle(msg, color=BG, fill_opacity=0.85, buff=0.15)

        self.add(field)
        self.play(Create(divider), run_time=1.2)
        self.play(FadeIn(lab_l), FadeIn(probe), run_time=1.3)
        self.wait(1.5)
        self.play(FadeIn(see_l), run_time=1)
        self.add(streaks, cloud)
        self.play(FadeIn(lab_r), FadeIn(rk), FadeIn(flame), streak_on.animate.set_value(1), run_time=1.5)
        self.play(heat.animate.set_value(1), run_time=3)
        self.play(FadeIn(see_r), run_time=1)
        self.wait(1.5)
        self.add(bg_field_lab)
        self.play(FadeIn(field_lab), run_time=1.2)
        self.wait(1.3)
        self.play(FadeIn(msg_bg), Write(msg), run_time=2)
        self.wait(6)
