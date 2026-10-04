import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

Z0 = 0.6


def well(x, y, d):
    r2 = x * x + y * y
    return Z0 - d * 2.4 / np.sqrt(1 + r2 / 0.9)


class Main(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=62 * DEGREES, theta=-50 * DEGREES, zoom=0.72)
        depth = ValueTracker(0.0)
        N = 6.0
        ticks = np.arange(-N, N + 0.01, 0.6)

        def grid():
            d = depth.get_value()
            g = VGroup()
            for c in ticks:
                g.add(ParametricFunction(lambda s, c=c: [s, c, well(s, c, d) + 2.4 * d / np.sqrt(1 + 2 * N * N / 0.9) * 0],
                                         t_range=[-N, N, 0.15], color=FIELD, stroke_width=1.6))
                g.add(ParametricFunction(lambda s, c=c: [c, s, well(c, s, d)],
                                         t_range=[-N, N, 0.15], color=FIELD, stroke_width=1.6))
            g.set_stroke(opacity=0.75)
            return g
        G = always_redraw(grid)
        self.add(G)

        big = Sphere(radius=0.55, resolution=(18, 18)).set_color(PARTICLE).set_opacity(1)
        big.set_sheen(0.3, UL) if hasattr(big, "set_sheen") else None
        big.move_to([0, 0, Z0 + 3.0])
        big.add_updater(lambda m: m.move_to([0, 0, max(well(0, 0, depth.get_value()) + 0.55,
                                                     m.get_center()[2])]))

        lab1 = Text("質量彎曲時空", font=FONT, font_size=44, color=PARTICLE)
        lab2 = Text("時空告訴物質如何運動", font=FONT, font_size=44, color=FIELD)
        for l in (lab1, lab2):
            l.to_corner(UR, buff=0.6)
        lab2.next_to(lab1, DOWN, buff=0.3, aligned_edge=RIGHT)
        self.add_fixed_in_frame_mobjects(lab1, lab2)
        lab1.set_opacity(0); lab2.set_opacity(0)

        self.play(Create(G), run_time=1.2)
        self.begin_ambient_camera_rotation(rate=0.05)
        self.add_foreground_mobject(big)
        big.clear_updaters()
        self.play(big.animate.move_to([0, 0, Z0 + 0.55]), run_time=1.0, rate_func=rush_into)
        big.add_updater(lambda m: m.move_to([0, 0, well(0, 0, depth.get_value()) + 0.55]))
        self.play(depth.animate.set_value(1.0), lab1.animate.set_opacity(1), run_time=3, rate_func=smooth)
        G.clear_updaters()
        d = 1.0

        # small ball spiralling in the well
        t = ValueTracker(0)
        def rpos(tt):
            r = 2.3 + 2.2 * np.exp(-tt / 5.0)
            om = 1.6 * (3.0 / r) ** 1.5
            return r, om
        def ball_pos():
            tt = t.get_value()
            # integrate angle numerically (cheap closed form approximation)
            ts = np.linspace(0, tt, 200)
            ang = np.trapezoid([rpos(x)[1] for x in ts], ts) if tt > 0 else 0.0
            r, _ = rpos(tt)
            x, y = r * np.cos(ang + 0.3), r * np.sin(ang + 0.3)
            return np.array([x, y, well(x, y, d) + 0.17])
        small = Sphere(radius=0.17, resolution=(10, 10)).set_color("#81D4FA").set_opacity(1)
        small.add_updater(lambda m: m.move_to(ball_pos()))
        trail = TracedPath(small.get_center, stroke_color="#E1F5FE", stroke_width=3, dissipating_time=2.5)
        self.add(trail)
        self.add_foreground_mobject(small)
        self.play(t.animate.set_value(4), run_time=4, rate_func=linear)
        self.play(t.animate.set_value(7), lab2.animate.set_opacity(1), run_time=3, rate_func=linear)
        self.play(t.animate.set_value(12), run_time=5, rate_func=linear)

        # Einstein field equations
        Gm = Text("G", font="Cambria Math", font_size=64, color=TEXT)
        s1 = Text("μν", font="Cambria Math", font_size=36, color=TEXT).next_to(Gm, DR, buff=0.02).shift(UP * 0.18)
        eq = Text("= 8πG", font="Cambria Math", font_size=64, color=TEXT).next_to(s1, RIGHT, buff=0.25).align_to(Gm, DOWN)
        T = Text("T", font="Cambria Math", font_size=64, color=TEXT).next_to(eq, RIGHT, buff=0.2).align_to(Gm, DOWN)
        s2 = Text("μν", font="Cambria Math", font_size=36, color=TEXT).next_to(T, DR, buff=0.02).shift(UP * 0.18)
        efe = VGroup(Gm, s1, eq, T, s2)
        name = Text("愛因斯坦場方程式", font=FONT, font_size=36, color=ACCENT)
        box = VGroup(efe, name).arrange(DOWN, buff=0.25)
        bg = BackgroundRectangle(box, color=BG, fill_opacity=0.75, buff=0.3)
        panel = VGroup(bg, box).to_corner(UL, buff=0.6).shift(DOWN * 0.3)
        self.add_fixed_in_frame_mobjects(panel)
        panel.set_opacity(0)
        self.play(t.animate.set_value(14), panel.animate.set_opacity(1), run_time=2, rate_func=linear)
        bg.set_fill(opacity=0.75)
        self.play(t.animate.set_value(20), run_time=6, rate_func=linear)
