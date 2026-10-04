"""Higgs 'Mexican hat' potential with a ball rolling into one vacuum."""
import numpy as np
from manim import *

from style import ACCENT, FIELD, FONT, MUTED, PARTICLE, TEXT

S = 2.0  # radial scale
H = 1.1  # height scale


def hat(r):
    return H * (r**2 - 1) ** 2


def pos(r, th):
    return np.array([S * r * np.cos(th), S * r * np.sin(th), hat(r) + 0.12])


class Main(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=55 * DEGREES, theta=-58 * DEGREES, zoom=1.0)
        self.camera.frame_center = np.array([0, 0, 0.6])

        surf = Surface(
            lambda u, v: np.array([S * u * np.cos(v), S * u * np.sin(v), hat(u)]),
            u_range=[0, 1.45],
            v_range=[0, TAU],
            resolution=(28, 48),
            fill_opacity=0.6,
            stroke_width=0.6,
            stroke_color=FIELD,
        )
        surf.set_fill_by_value(axes=ThreeDAxes(), colorscale=[(FIELD, 0), ("#1A3A6B", 0.6), (ACCENT, 1.6)], axis=2)

        trough = ParametricFunction(lambda t: np.array([S * np.cos(t), S * np.sin(t), 0.02]),
                                    t_range=[0, TAU], color=PARTICLE, stroke_width=4)
        trough.set_stroke(opacity=0)

        title = Text("希格斯位勢", font=FONT, font_size=44, color=TEXT).to_corner(UR, buff=0.5)
        sub = Text("對稱的山頂並不穩定", font=FONT, font_size=30, color=MUTED).next_to(title, DOWN, aligned_edge=RIGHT)
        msg = Text("真空選定了一個方向 → 對稱性自發破缺", font=FONT, font_size=34, color=PARTICLE)
        msg.move_to(DOWN * 2.35)
        for m in (title, sub, msg):
            self.add_fixed_in_frame_mobjects(m)
            m.set_opacity(0)

        r_t = ValueTracker(0.0)
        th = 0.62
        wobble = ValueTracker(0.0)
        ball = Sphere(radius=0.22, resolution=(14, 14)).set_color(PARTICLE).set_opacity(1)
        ball.set_sheen(0.4, UL)

        def place(m):
            r = r_t.get_value()
            w = wobble.get_value()
            m.move_to(pos(r + 0.012 * np.sin(w * 9), th))

        ball.add_updater(place)

        self.play(Create(surf), run_time=3)
        self.add(ball)
        self.begin_ambient_camera_rotation(rate=0.03)
        self.play(title.animate.set_opacity(1), sub.animate.set_opacity(1), wobble.animate.set_value(1.5), run_time=2.5)
        # ball tips over and rolls down into the trough, then settles with damped oscillation
        self.play(r_t.animate.set_value(1.12), run_time=2.6, rate_func=rate_functions.ease_in_quad)
        self.play(r_t.animate.set_value(0.95), run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.play(r_t.animate.set_value(1.03), run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        self.play(r_t.animate.set_value(1.0), run_time=0.6, rate_func=rate_functions.ease_in_out_sine)
        self.play(trough.animate.set_stroke(opacity=0.9), run_time=1.5)
        marker = Line(pos(1.0, th) + np.array([0, 0, 0.25]), pos(1.0, th) + np.array([0, 0, 1.4]),
                      color=PARTICLE, stroke_width=4)
        self.play(Create(marker), msg.animate.set_opacity(1), run_time=1.5)
        self.wait(5.5)
        self.stop_ambient_camera_rotation()
