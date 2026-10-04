import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT
from g2util import Wireframe

rng = np.random.default_rng(3)
MODES = [(rng.uniform(0.4, 1.6), rng.uniform(0.4, 1.6), rng.uniform(0, 6.3),
          rng.uniform(0.8, 2.2), rng.choice([-1, 1])) for _ in range(9)]
DUR = 24.0


def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def bump_x(t):
    return -6.5 + 13.0 * smooth01((t - 4.0) / 18.0)


def bump_amp(t):
    return 1.5 * smooth01((t - 2.5) / 2.0)


def height(X, Z, t):
    h = np.zeros_like(X)
    for kx, kz, ph, w, sg in MODES:
        h += 0.045 * np.sin(kx * X + sg * kz * Z + ph + w * t)
    x0, z0 = bump_x(t), 0.6
    r2 = (X - x0) ** 2 + (Z - z0) ** 2
    h += bump_amp(t) * np.exp(-r2 / 1.3) * (0.8 + 0.2 * np.cos(4.0 * (X - x0) - 6.0 * t))
    return h


class Main(Scene):
    def construct(self):
        surf = Wireframe(height)
        clock = ValueTracker(0)

        def upd(m, dt):
            clock.increment_value(dt)
            m.t = clock.get_value()
            m.phi = -0.22 + 0.44 * m.t / DUR
            m.redraw()

        surf.add_updater(upd)
        self.add(surf)
        self.wait(4.5)

        lab_field = Text("量子場：瀰漫整個空間", font=FONT, font_size=36, color=FIELD)
        lab_field.to_corner(UR, buff=0.6)
        self.play(FadeIn(lab_field, shift=DOWN * 0.2), run_time=1.2)
        self.wait(2.0)

        def bump_screen():
            t = clock.get_value()
            x0 = bump_x(t)
            pts, _ = surf.project(np.array([x0]), np.array([0.6]), np.array([bump_amp(t)]))
            return pts[0]

        lab_p = Text("粒子 ＝ 場的激發", font=FONT, font_size=48, color=PARTICLE)
        lab_p.move_to(UP * 2.55)
        arrow = always_redraw(lambda: Arrow(
            lab_p.get_bottom() + DOWN * 0.05, bump_screen() + UP * 0.35,
            buff=0.05, color=PARTICLE, stroke_width=4, max_tip_length_to_length_ratio=0.12))
        self.play(Write(lab_p), run_time=1.5)
        self.play(Create(arrow), run_time=0.8)
        self.wait(DUR - clock.get_value() - 0.1)
