import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

A = 1.3  # pole half-separation
Y0 = 0.45  # vertical center of the picture


def bfield(p):
    x, y = p[0], p[1] - Y0
    out = np.zeros(3)
    for q, px in [(1, A), (-1, -A)]:  # N on the right
        dx, dy = x - px, y
        r3 = (dx * dx + dy * dy + 0.05) ** 1.5
        out[0] += q * dx / r3
        out[1] += q * dy / r3
    return out


class Main(Scene):
    def construct(self):
        mag_s = Rectangle(width=A * 1.3, height=0.7, fill_color="#42A5F5", fill_opacity=1, stroke_width=0)
        mag_n = Rectangle(width=A * 1.3, height=0.7, fill_color="#EF5350", fill_opacity=1, stroke_width=0)
        mag_s.move_to([-A * 0.65, Y0, 0])
        mag_n.move_to([A * 0.65, Y0, 0])
        ns = VGroup(Text("S", font=FONT, font_size=40, weight=BOLD).move_to(mag_s),
                    Text("N", font=FONT, font_size=40, weight=BOLD).move_to(mag_n))
        magnet = VGroup(mag_s, mag_n, ns)

        rng = np.random.default_rng(3)
        pts = []
        while len(pts) < 900:
            x, y = rng.uniform(-7, 7), rng.uniform(-2.75, 3.85)
            if abs(x) < A * 1.45 and abs(y - Y0) < 0.55:
                continue
            pts.append((x, y))
        rand_ang = rng.uniform(0, PI, len(pts))
        field_ang = np.array([np.arctan2(*bfield(np.array([x, y, 0]))[[1, 0]]) for x, y in pts])
        # shortest rotation (filings are headless lines => mod pi)
        diff = (field_ang - rand_ang + PI / 2) % PI - PI / 2
        s = ValueTracker(0)
        L = 0.17

        def filings():
            g = VGroup()
            k = s.get_value()
            for (x, y), a0, d in zip(pts, rand_ang, diff):
                a = a0 + d * k
                v = np.array([np.cos(a), np.sin(a), 0]) * L / 2
                c = np.array([x, y, 0])
                g.add(Line(c - v, c + v, stroke_width=2.2, color="#B0BEC5"))
            return g
        fil = always_redraw(filings)

        self.play(FadeIn(magnet), run_time=1)
        def cap(t, c=TEXT):
            tx = Text(t, font=FONT, font_size=40, color=c)
            return VGroup(BackgroundRectangle(tx, color=BG, fill_opacity=0.9, buff=0.2), tx).move_to([0, -2.4, 0])
        cap1 = cap("撒上鐵屑……")
        self.play(FadeIn(fil, lag_ratio=0.01), FadeIn(cap1), run_time=2)
        self.wait(0.5)
        cap2 = cap("輕敲紙面，鐵屑自動排列")
        self.play(s.animate.set_value(1), FadeTransform(cap1, cap2), run_time=4, rate_func=smooth)
        self.wait(1)

        stream = StreamLines(bfield, x_range=[-7.2, 7.2, 0.35], y_range=[-2.8, 3.9, 0.35],
                             stroke_width=2.5, max_anchors_per_line=60, padding=0.5,
                             colors=[FIELD, "#81D4FA", "#E1F5FE"], virtual_time=4)
        fil.clear_updaters()
        cap3 = cap("法拉第：空間中真實存在的「力線」", FIELD)
        self.play(fil.animate.set_opacity(0.25), FadeTransform(cap2, cap3), run_time=1.5)
        self.add(stream)
        self.bring_to_front(magnet, cap3)
        stream.start_animation(warm_up=True, flow_speed=1.2, time_width=0.5)
        self.wait(13)
