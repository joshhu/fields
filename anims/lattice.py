"""Lattice gauge theory: continuous spacetime chopped into a lattice of sites and links."""
import itertools

import numpy as np
from manim import *

from style import ACCENT, FIELD, FONT, MUTED, PARTICLE, TEXT

N = (6, 6, 3)
A = 0.85


def site(i, j, k):
    return np.array([(i - (N[0] - 1) / 2) * A, (j - (N[1] - 1) / 2) * A, (k - (N[2] - 1) / 2) * A + 0.7])


class Main(ThreeDScene):
    def construct(self):
        rng = np.random.default_rng(11)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-40 * DEGREES, zoom=0.8)
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t)

        # 1) a smooth continuous field sheet
        sheet = Surface(
            lambda u, v: np.array([u, v, 0.35 * np.sin(1.3 * u) * np.cos(1.1 * v) - 0.3]),
            u_range=[-2.6, 2.6], v_range=[-2.6, 2.6], resolution=(30, 30),
            fill_opacity=0.65, stroke_width=0.3, stroke_color=FIELD,
            checkerboard_colors=[FIELD, "#1E5A87"],
        )

        title = Text("晶格 QCD", font=FONT, font_size=50, color=TEXT).to_corner(UR, buff=0.55)
        cont = Text("連續的時空", font=FONT, font_size=32, color=FIELD).move_to(DOWN * 2.35)
        disc = Text("切成離散的格點：格點放夸克，連線放膠子場", font=FONT, font_size=32, color=TEXT).move_to(DOWN * 2.35)
        for m in (title, cont, disc):
            self.add_fixed_in_frame_mobjects(m)
            m.set_opacity(0)

        self.begin_ambient_camera_rotation(rate=0.1)
        self.play(FadeIn(sheet), cont.animate.set_opacity(1), run_time=2)
        self.wait(1.5)

        # 2) lattice: sites + links whose colours flicker like fluctuating gauge links
        idx = list(itertools.product(range(N[0]), range(N[1]), range(N[2])))
        dots = VGroup(*[Dot3D(site(*p), radius=0.07, color=PARTICLE, resolution=(6, 6)) for p in idx])
        links = VGroup()
        phases = []
        for (i, j, k) in idx:
            for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                q = (i + d[0], j + d[1], k + d[2])
                if q[0] < N[0] and q[1] < N[1] and q[2] < N[2]:
                    links.add(Line(site(i, j, k), site(*q), stroke_width=2.5))
                    phases.append(rng.uniform(0, TAU))
        phases = np.array(phases)
        fc, ac = ManimColor(FIELD), ManimColor(ACCENT)
        link_on = ValueTracker(0)

        def upd(g):
            tt = t.get_value()
            on = link_on.get_value()
            for l, p in zip(g, phases):
                s = (1 + np.sin(1.8 * tt + p)) / 2
                l.set_stroke(color=interpolate_color(fc, ac, s), opacity=on * (0.35 + 0.6 * s))
        links.add_updater(upd)

        self.add(links)
        self.play(FadeOut(sheet), FadeIn(dots, lag_ratio=0.01), link_on.animate.set_value(1),
                  title.animate.set_opacity(1), cont.animate.set_opacity(0), run_time=3)
        self.play(disc.animate.set_opacity(1), run_time=1.2)
        self.wait(4)
        self.move_camera(phi=58 * DEGREES, zoom=0.9, run_time=4)
        self.wait(2.5)
        self.stop_ambient_camera_rotation()
