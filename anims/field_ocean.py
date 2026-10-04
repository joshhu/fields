import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT
from g2util import Wireframe

DUR = 21.0
rng = np.random.default_rng(11)
EVENTS = []
t = 1.0
while t < DUR - 1.5:
    EVENTS.append((t, rng.uniform(-7, 7), rng.uniform(-1.0, 5.5), rng.uniform(1.8, 2.6)))
    t += rng.uniform(1.1, 1.9)
SWELL = [(0.35, 0.15, 0.0, 0.9), (0.22, -0.3, 1.7, 1.3), (0.5, 0.4, 3.1, 0.7), (0.15, 0.6, 4.2, 1.6)]


def height(X, Z, t):
    h = np.zeros_like(X)
    for kx, kz, ph, w in SWELL:
        h += 0.06 * np.sin(kx * X + kz * Z + ph + w * t)
    for t0, x0, z0, a in EVENTS:
        dt = t - t0
        if dt < 0 or dt > 5:
            continue
        env = a * (dt / 0.5 if dt < 0.5 else np.exp(-(dt - 0.5) / 0.9))
        r = np.sqrt((X - x0) ** 2 + (Z - z0) ** 2)
        h += env * np.exp(-r ** 2 / 0.45)
        ring = 1.6 * dt
        h += 0.18 * np.exp(-dt / 1.6) * np.exp(-(r - ring) ** 2 / 0.4) * np.cos(3 * (r - ring))
    return h


class Main(Scene):
    def construct(self):
        surf = Wireframe(height, nx=84, nz=32, z_range=(-2.5, 7), y_offset=-1.2, tilt=0.5)
        surf.hot_thresh = 0.3
        clock = ValueTracker(0)

        def upd(m, dt):
            clock.increment_value(dt)
            m.t = clock.get_value()
            m.phi = 0.12 - 0.24 * m.t / DUR
            m.redraw()

        surf.add_updater(upd)
        self.add(surf)
        self.wait(4.5)

        sea = Text("場：大海（一直都在）", font=FONT, font_size=40, color=FIELD)
        foam = Text("粒子：浪花（可生可滅）", font=FONT, font_size=40, color=PARTICLE)
        sea.move_to(LEFT * 3.5 + UP * 3.0)
        foam.move_to(RIGHT * 3.5 + UP * 3.0)
        self.play(FadeIn(sea, shift=DOWN * 0.2), run_time=1.2)
        self.wait(2.5)
        self.play(FadeIn(foam, shift=DOWN * 0.2), run_time=1.2)
        self.wait(DUR - clock.get_value() - 0.1)
