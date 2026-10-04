import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT


class Main(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-62 * DEGREES, zoom=0.8)
        t = ValueTracker(0)
        K, W, AMP = 1.1, 2.4, 1.25
        Z0 = 0.9
        xs = np.linspace(-6.5, 6.5, 52)

        def efield():
            g = VGroup()
            tt = t.get_value()
            for x in xs:
                a = AMP * np.sin(K * x - W * tt)
                g.add(Line([x, 0, Z0], [x, 0, Z0 + a], color=FIELD, stroke_width=3))
            g.add(ParametricFunction(lambda x: [x, 0, Z0 + AMP * np.sin(K * x - W * tt)], t_range=[-6.5, 6.5],
                                     color=FIELD, stroke_width=5))
            return g

        def bfield():
            g = VGroup()
            tt = t.get_value()
            for x in xs:
                a = AMP * np.sin(K * x - W * tt)
                g.add(Line([x, 0, Z0], [x, a, Z0], color=ACCENT, stroke_width=3))
            g.add(ParametricFunction(lambda x: [x, AMP * np.sin(K * x - W * tt), Z0], t_range=[-6.5, 6.5],
                                     color=ACCENT, stroke_width=5))
            return g

        axis = Arrow3D([-7, 0, Z0], [7.2, 0, Z0], color=MUTED, thickness=0.01)
        E = always_redraw(efield)
        B = always_redraw(bfield)
        lab_e = Text("電場 E", font=FONT, font_size=38, color=FIELD)
        lab_b = Text("磁場 B", font=FONT, font_size=38, color=ACCENT)
        lab_c = Text("傳播方向 →  速度 c", font=FONT, font_size=34, color=TEXT)
        VGroup(lab_e, lab_b, lab_c).arrange(DOWN, aligned_edge=RIGHT, buff=0.25).to_corner(UR, buff=0.7)
        self.add_fixed_in_frame_mobjects(lab_e, lab_b, lab_c)
        lab_e.set_opacity(0); lab_b.set_opacity(0); lab_c.set_opacity(0)

        self.add(axis, E, B)
        self.begin_ambient_camera_rotation(rate=0.07)
        self.play(t.animate.set_value(2), lab_e.animate.set_opacity(1), lab_b.animate.set_opacity(1),
                  run_time=2, rate_func=linear)
        self.play(t.animate.set_value(4), lab_c.animate.set_opacity(1), run_time=2, rate_func=linear)
        self.play(t.animate.set_value(11), run_time=7, rate_func=linear)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(E), FadeOut(B), FadeOut(axis), FadeOut(lab_e), FadeOut(lab_b), FadeOut(lab_c),
                  run_time=0.8)
        E.clear_updaters(); B.clear_updaters()
        self.remove(E, B)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1)

        # ---- 2D: charge A shakes, ripple travels at finite speed, then B responds ----
        s = ValueTracker(0)
        V = 1.9
        pa = np.array([-4.8, 0.5, 0])
        pb = np.array([4.8, 0.5, 0])
        dist = np.linalg.norm(pb - pa)
        WIG_T = 2.0

        def wig(tau):
            return 0.35 * np.sin(2 * PI * 1.5 * tau) if 0 < tau < WIG_T else 0.0

        A = Dot(radius=0.22, color=PARTICLE)
        A.add_updater(lambda m: m.move_to(pa + UP * wig(s.get_value())))
        Bd = Dot(radius=0.22, color=PARTICLE)
        Bd.add_updater(lambda m: m.move_to(pb + UP * 0.6 * wig(s.get_value() - dist / V)))
        la = Text("電荷 A", font=FONT, font_size=32, color=PARTICLE).move_to(pa + DOWN * 0.8)
        lb = Text("電荷 B", font=FONT, font_size=32, color=PARTICLE).move_to(pb + DOWN * 0.8)

        def rings():
            g = VGroup()
            tt = s.get_value()
            for k in range(14):
                te = k * WIG_T / 14
                r = V * (tt - te)
                if tt > te and r > 0.05:
                    op = 0.85 * max(0.0, 1 - r / 11)
                    g.add(Circle(radius=r, color=FIELD, stroke_width=3).set_stroke(opacity=op).move_to(pa))
            return g
        rg = always_redraw(rings)
        clock = always_redraw(lambda: Text(f"t = {s.get_value():.1f}", font="Cambria Math", font_size=36,
                                           color=MUTED).move_to([5.3, 3.3, 0]))
        cap = Text("擾動以光速一圈圈向外擴散", font=FONT, font_size=40, color=FIELD).move_to([0, -2.45, 0])
        cap2 = Text("傳到 B，B 才感受到力", font=FONT, font_size=40, color=PARTICLE).move_to(cap)
        self.play(FadeIn(A), FadeIn(Bd), FadeIn(la), FadeIn(lb), FadeIn(clock), run_time=1)
        self.add(rg)
        self.play(s.animate.set_value(dist / V - 0.4), FadeIn(cap), run_time=dist / V - 0.4, rate_func=linear)
        self.play(s.animate.set_value(dist / V + 2.6), Succession(FadeOut(cap, run_time=0.5), FadeIn(cap2, run_time=0.8)), run_time=3.0, rate_func=linear)
        self.play(s.animate.set_value(dist / V + 4.5), run_time=1.9, rate_func=linear)
