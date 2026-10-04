"""Helpers for group-2 animations: projected wireframe surfaces and wavy lines."""
import numpy as np
from manim import VGroup, VMobject, interpolate_color, ManimColor

from style import FIELD, PARTICLE


class Wireframe(VGroup):
    """A height field h(X, Z, t) drawn as a perspective wireframe.

    `height(X, Z, t)` receives meshgrids and returns heights of the same shape.
    """

    def __init__(self, height, x_range=(-11, 11), z_range=(-3.5, 6), nx=70, nz=26,
                 res=110, color=FIELD, hot=PARTICLE, y_offset=-0.9, tilt=0.42,
                 dist=14.0, scale=0.95, stroke=1.6, **kw):
        super().__init__(**kw)
        self.height_fn = height
        self.color = ManimColor(color)
        self.hot = ManimColor(hot)
        self.y_offset, self.tilt, self.dist, self.sc = y_offset, tilt, dist, scale
        self.phi = 0.0
        self.t = 0.0
        xs = np.linspace(*x_range, res)
        zs = np.linspace(*z_range, nz)
        self.rows = [(xs, np.full_like(xs, z)) for z in zs]          # lines along X
        zz = np.linspace(*z_range, res // 2)
        self.cols = [(np.full_like(zz, x), zz) for x in np.linspace(*x_range, nx // 2)]
        self.zr = z_range
        self.lines = VGroup(*[VMobject().set_stroke(self.color, stroke) for _ in self.rows + self.cols])
        self.glows = VGroup(*[VMobject() for _ in self.rows + self.cols])
        self.hot_thresh = 0.35
        self.add(self.lines, self.glows)
        self.stroke = stroke
        self.redraw()

    def project(self, X, Z, H):
        c, s = np.cos(self.phi), np.sin(self.phi)
        X1 = X * c - Z * s
        Z1 = X * s + Z * c
        k = self.dist / (self.dist + Z1)
        sx = X1 * k * self.sc
        sy = (H + Z1 * self.tilt) * k * self.sc + self.y_offset
        return np.stack([sx, sy, np.zeros_like(sx)], axis=1), Z1

    def redraw(self):
        for mob, glow, (X, Z) in zip(self.lines, self.glows, self.rows + self.cols):
            H = self.height_fn(X, Z, self.t)
            pts, Z1 = self.project(X, Z, H)
            mob.set_points_as_corners(pts)
            depth = np.clip((Z1.mean() - self.zr[0]) / (self.zr[1] - self.zr[0]), 0, 1)
            mob.set_stroke(self.color, self.stroke, opacity=0.95 - 0.6 * depth)
            hot = np.nonzero(H > self.hot_thresh)[0]
            glow.clear_points()
            if len(hot) >= 2:
                # one sub-path per contiguous hot run, so separate bumps are not joined
                runs = np.split(hot, np.nonzero(np.diff(hot) > 1)[0] + 1)
                for run in runs:
                    if len(run) < 2:
                        continue
                    a, b = max(run[0] - 1, 0), min(run[-1] + 2, len(H))
                    glow.start_new_path(pts[a])
                    glow.add_points_as_corners(pts[a + 1:b])
                k = float(np.clip(H.max() / 1.0, 0, 1))
                glow.set_stroke(self.hot, self.stroke * 1.6, opacity=0.35 + 0.6 * k)
        return self


def wavy_points(start, end, amp=0.12, waves=8, n=240):
    start, end = np.array(start, float), np.array(end, float)
    d = end - start
    L = np.linalg.norm(d)
    u = d / L
    perp = np.array([-u[1], u[0], 0.0])
    s = np.linspace(0, 1, n)
    return start + np.outer(s, d) + np.outer(amp * np.sin(2 * np.pi * waves * s), perp)


def wavy_line(start, end, amp=0.12, waves=8, color=FIELD, width=4):
    m = VMobject().set_points_smoothly(wavy_points(start, end, amp, waves))
    return m.set_stroke(color, width)


def wavy_arc(center, radius, a0, a1, amp=0.09, waves=10, color=FIELD, width=4, n=300):
    """A wiggly (photon-style) circular arc from angle a0 to a1."""
    th = np.linspace(a0, a1, n)
    r = radius + amp * np.sin(waves * 2 * np.pi * (th - a0) / (a1 - a0))
    pts = np.stack([center[0] + r * np.cos(th), center[1] + r * np.sin(th), np.zeros(n)], 1)
    return VMobject().set_points_smoothly(pts).set_stroke(color, width)
