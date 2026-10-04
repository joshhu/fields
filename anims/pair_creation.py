import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

PHOTON = "#FFF59D"


def packet(center, direction, length=1.4, color=PHOTON, amp=0.16, k=16):
    u = direction / np.linalg.norm(direction)
    n = np.array([-u[1], u[0], 0])
    return ParametricFunction(
        lambda s: center + u * s + n * amp * np.sin(k * s) * np.exp(-(s / (length / 2.5)) ** 2),
        t_range=[-length / 2, length / 2], color=color, stroke_width=4)


class Main(Scene):
    def construct(self):
        div = DashedLine([0, 3.6, 0], [0, -2.7, 0], color=MUTED, stroke_width=2).set_opacity(0.5)
        h1 = Text("成對產生", font=FONT, font_size=42, color=FIELD).move_to([-3.6, 3.2, 0])
        h2 = Text("湮滅", font=FONT, font_size=42, color=ACCENT).move_to([3.6, 3.2, 0])
        self.add(div)
        self.play(FadeIn(h1), FadeIn(h2), run_time=1)

        # --- left: photon -> e- e+ ---
        t = ValueTracker(0)
        V0 = np.array([-3.4, 0.4, 0])
        def left_photon():
            tt = t.get_value()
            if tt > 1.0:
                return VGroup()
            c = V0 + np.array([-4.0 * (1 - tt), 0, 0])
            return packet(c, RIGHT)
        lp = always_redraw(left_photon)
        gl = Text("γ", font="Cambria Math", font_size=40, color=PHOTON)
        gl.add_updater(lambda m: m.move_to(V0 + np.array([-4.0 * (1 - min(t.get_value(), 1)), 0.55, 0])).set_opacity(1 if t.get_value() < 0.98 else 0))
        cnt_l = always_redraw(lambda: Text(
            "粒子數：1" if t.get_value() < 1 else "粒子數：1 → 2", font=FONT, font_size=34, color=TEXT
        ).move_to([-3.6, -2.4, 0]))
        self.add(lp, gl, cnt_l)
        self.play(t.animate.set_value(1.0), run_time=2.5, rate_func=linear)
        flash = Flash(V0, color=PHOTON, line_length=0.4, flash_radius=0.4)
        em = Dot(V0, radius=0.17, color=PARTICLE)
        ep = Dot(V0, radius=0.17, color=ACCENT)
        ml = Text("e⁻", font="Cambria Math", font_size=36, color=PARTICLE)
        pl = Text("e⁺", font="Cambria Math", font_size=36, color=ACCENT)
        ml.add_updater(lambda m: m.next_to(em, UP, buff=0.12))
        pl.add_updater(lambda m: m.next_to(ep, DOWN, buff=0.12))
        tr1 = TracedPath(em.get_center, stroke_color=PARTICLE, stroke_width=3)
        tr2 = TracedPath(ep.get_center, stroke_color=ACCENT, stroke_width=3)
        self.add(tr1, tr2, em, ep, ml, pl)
        p1 = ArcBetweenPoints(V0, V0 + np.array([2.3, 1.9, 0]), angle=-0.6)
        p2 = ArcBetweenPoints(V0, V0 + np.array([2.3, -1.9, 0]), angle=0.6)
        self.play(flash, MoveAlongPath(em, p1), MoveAlongPath(ep, p2), t.animate.set_value(1.2),
                  run_time=2.5, rate_func=smooth)

        # --- right: e- e+ -> two photons ---
        V1 = np.array([3.6, 0.4, 0])
        em2 = Dot(V1 + np.array([-2.6, 1.6, 0]), radius=0.17, color=PARTICLE)
        ep2 = Dot(V1 + np.array([2.6, -1.6, 0]), radius=0.17, color=ACCENT)
        ml2 = Text("e⁻", font="Cambria Math", font_size=36, color=PARTICLE)
        pl2 = Text("e⁺", font="Cambria Math", font_size=36, color=ACCENT)
        ml2.add_updater(lambda m: m.next_to(em2, UP, buff=0.12))
        pl2.add_updater(lambda m: m.next_to(ep2, DOWN, buff=0.12))
        s = ValueTracker(0)
        cnt_r = always_redraw(lambda: Text(
            "粒子數：2" if s.get_value() < 1 else "粒子數：2 → 0", font=FONT, font_size=34, color=TEXT
        ).move_to([3.6, -2.4, 0]))
        tr3 = TracedPath(em2.get_center, stroke_color=PARTICLE, stroke_width=3, dissipating_time=1.5)
        tr4 = TracedPath(ep2.get_center, stroke_color=ACCENT, stroke_width=3, dissipating_time=1.5)
        self.play(FadeIn(em2), FadeIn(ep2), FadeIn(ml2), FadeIn(pl2), FadeIn(cnt_r), run_time=0.8)
        self.add(tr3, tr4)
        self.play(em2.animate.move_to(V1), ep2.animate.move_to(V1), run_time=2.2, rate_func=rush_into)
        ml2.clear_updaters(); pl2.clear_updaters()
        self.remove(em2, ep2, ml2, pl2)
        s.set_value(1)
        boom = Flash(V1, color=PHOTON, line_length=0.5, flash_radius=0.5, num_lines=16)
        d1 = np.array([1, 0.45, 0]); d2 = -d1
        def right_photons():
            ss = s.get_value() - 1
            g = VGroup()
            for d in (d1, d2):
                u = d / np.linalg.norm(d)
                g.add(packet(V1 + u * (0.4 + 2.6 * ss), u))
            return g
        rp = always_redraw(right_photons)
        gam = Text("2γ", font="Cambria Math", font_size=36, color=PHOTON).move_to(V1 + np.array([0.9, -0.75, 0]))
        self.add(rp)
        self.play(boom, s.animate.set_value(2.05), FadeIn(gam), run_time=2.2, rate_func=linear)
        note = Text("粒子可以產生、也可以消失", font=FONT, font_size=40, color=PARTICLE, weight=BOLD)
        note.add_background_rectangle(color=BG, opacity=0.85, buff=0.15)
        note.move_to([0, -1.25, 0])
        self.play(s.animate.set_value(2.25), FadeOut(rp), FadeIn(note, shift=UP * 0.2), run_time=1.3, rate_func=linear)
        rp.clear_updaters()
        self.play(Indicate(note[1], scale_factor=1.05, color=PARTICLE),
                  em.animate.shift(np.array([0.3, 0.08, 0])), ep.animate.shift(np.array([0.3, -0.08, 0])),
                  run_time=2.5, rate_func=linear)
        self.wait(2.5)
