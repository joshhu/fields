import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT


class Main(Scene):
    def construct(self):
        center = np.array([-0.5, 0.2, 0])
        sun = VGroup(*[Circle(radius=0.55 + 0.06 * i, stroke_width=0, fill_color=PARTICLE,
                              fill_opacity=0.12) for i in range(6)],
                     Circle(radius=0.55, stroke_width=0, fill_color=PARTICLE, fill_opacity=1))
        sun.move_to(center)
        sun_lbl = Text("太陽", font=FONT, font_size=30, color=PARTICLE)
        sun_lbl.add_updater(lambda m: m.next_to(sun, DOWN, buff=0.25))

        R = 2.6
        phase = ValueTracker(0.0)
        earth = Dot(radius=0.2, color=FIELD)
        earth.add_updater(lambda m: m.move_to(sun.get_center() + R * np.array(
            [np.cos(phase.get_value()), 0.8 * np.sin(phase.get_value()), 0])))
        earth_lbl = Text("地球", font=FONT, font_size=28, color=FIELD)
        earth_lbl.add_updater(lambda m: m.next_to(earth, UP, buff=0.15))
        orbit = always_redraw(lambda: Ellipse(width=2 * R, height=1.6 * R, color=MUTED,
                                              stroke_width=1.5).set_stroke(opacity=0.4).move_to(sun.get_center()))
        link = always_redraw(lambda: DashedLine(sun.get_center(), earth.get_center(),
                                                color=ACCENT, stroke_width=3, dash_length=0.12))

        formula = Text("F = G · m₁m₂ / r²", font="Cambria Math", font_size=48, color=TEXT)
        formula.to_corner(UR, buff=0.6).shift(DOWN * 0.4)
        name = Text("萬有引力定律", font=FONT, font_size=32, color=MUTED).next_to(formula, DOWN, buff=0.2)

        self.add(orbit)
        self.play(FadeIn(sun), FadeIn(sun_lbl), FadeIn(earth), FadeIn(earth_lbl), run_time=1.5)
        self.play(phase.animate.increment_value(PI), Write(formula), FadeIn(name), run_time=4, rate_func=linear)
        self.play(Create(link), phase.animate.increment_value(PI * 0.6), run_time=2.5, rate_func=linear)
        self.play(phase.animate.increment_value(PI * 0.8), run_time=3, rate_func=linear)

        # sun jumps: link follows instantly
        flash = Text("太陽一動，地球「瞬間」感受到", font=FONT, font_size=40, color=ACCENT)
        flash.move_to([-0.5, -2.45, 0])
        self.play(FadeIn(flash, shift=DOWN * 0.2), run_time=1)
        for shift_vec in [RIGHT * 1.2 + UP * 0.3, LEFT * 1.6 + DOWN * 0.4, RIGHT * 0.4 + UP * 0.1]:
            self.play(sun.animate.shift(shift_vec), phase.animate.increment_value(0.25),
                      run_time=0.35, rate_func=rush_into)
            self.play(Flash(earth, color=ACCENT, line_length=0.3, flash_radius=0.35),
                      phase.animate.increment_value(0.4), run_time=0.8, rate_func=linear)

        q1 = Text("瞬間？", font=FONT, font_size=48, color=ACCENT)
        q2 = Text("沒有介質？", font=FONT, font_size=48, color=ACCENT)
        q1.next_to(formula, DOWN, buff=1.4)
        q2.next_to(q1, DOWN, buff=0.4)
        self.play(FadeIn(q1, scale=1.4), phase.animate.increment_value(0.8), run_time=1.5, rate_func=linear)
        self.play(FadeIn(q2, scale=1.4), phase.animate.increment_value(0.8), run_time=1.5, rate_func=linear)
        # pulsing "?" marks along the link
        qs = VGroup(*[Text("?", font=FONT, font_size=36, color=TEXT) for _ in range(3)])
        def place_qs(m):
            a, b = sun.get_center(), earth.get_center()
            for i, q in enumerate(m):
                q.move_to(a + (b - a) * (i + 1) / 4 + UP * 0.3)
        qs.add_updater(place_qs)
        self.play(FadeIn(qs), phase.animate.increment_value(1.0), run_time=2, rate_func=linear)
        self.play(phase.animate.increment_value(2.6), run_time=6.5, rate_func=linear)
        self.play(Indicate(q1, color=PARTICLE), Indicate(q2, color=PARTICLE),
                  phase.animate.increment_value(1.0), run_time=2, rate_func=linear)
