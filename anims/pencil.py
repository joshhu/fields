import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

DUR = 19.0
LX, RX = -3.6, 3.6
TABLE_Y = -1.5
L = 2.7          # pencil length (tip to eraser)
T_FALL = 8.0


def make_pencil():
    tip_h, er_h, w = 0.42, 0.28, 0.26
    body_h = L - tip_h - er_h
    graphite = Polygon([0, 0, 0], [-0.06, 0.12, 0], [0.06, 0.12, 0], color="#424242", fill_opacity=1, stroke_width=0)
    wood = Polygon([-0.06, 0.12, 0], [0.06, 0.12, 0], [w / 2, tip_h, 0], [-w / 2, tip_h, 0],
                   color="#FFE0B2", fill_opacity=1, stroke_width=0)
    body = Rectangle(width=w, height=body_h, color="#FFC107", fill_opacity=1, stroke_width=0)
    body.move_to([0, tip_h + body_h / 2, 0])
    stripe = Line([0, tip_h, 0], [0, tip_h + body_h, 0], color="#FFA000", stroke_width=2)
    band = Rectangle(width=w, height=0.08, color="#B0BEC5", fill_opacity=1, stroke_width=0).move_to([0, tip_h + body_h + 0.04, 0])
    eraser = RoundedRectangle(width=w, height=er_h, corner_radius=0.06, color="#F48FB1", fill_opacity=1, stroke_width=0)
    eraser.move_to([0, L - er_h / 2, 0])
    return VGroup(graphite, wood, body, stripe, band, eraser)


class Main(Scene):
    def construct(self):
        # ----- side view -----
        table = VGroup(Line([LX - 2.6, TABLE_Y, 0], [LX + 3.1, TABLE_Y, 0], color=MUTED, stroke_width=4),
                       Rectangle(width=5.7, height=0.35, color=MUTED, fill_opacity=0.15, stroke_width=0)
                       .move_to([LX + 0.25, TABLE_Y - 0.18, 0]))
        pencil = make_pencil().shift([LX, TABLE_Y, 0])
        pivot = np.array([LX, TABLE_Y, 0])
        angle = ValueTracker(0.0)
        base = pencil.copy()
        pencil.add_updater(lambda m: m.become(base.copy().rotate(-angle.get_value(), about_point=pivot).shift(UP * 0.13 * np.sin(angle.get_value()))))

        # ----- top view -----
        ring = DashedVMobject(Circle(radius=1.8, color=MUTED, stroke_width=2), num_dashes=48).move_to([RX, 0, 0])
        dirs = VGroup()
        for k in range(12):
            a = k * TAU / 12
            dirs.add(Arrow([RX, 0, 0], [RX + 1.65 * np.cos(a), 1.65 * np.sin(a), 0], buff=0.25,
                           color=FIELD, stroke_width=4, max_tip_length_to_length_ratio=0.18))
        top_pencil = Circle(radius=0.15, color="#FFC107", fill_opacity=1, stroke_width=0).move_to([RX, 0, 0])
        top_tip = Dot([RX, 0, 0], radius=0.05, color="#424242")

        self.play(Create(table), FadeIn(pencil), Create(ring), FadeIn(top_pencil), FadeIn(top_tip), run_time=1.2)
        self.play(LaggedStart(*[GrowArrow(d) for d in dirs], lag_ratio=0.08), run_time=1.5)

        # wobble while balanced
        wob = ValueTracker(0)
        dirs.add_updater(lambda m: m.set_opacity(0.55 + 0.35 * np.sin(3 * self.renderer.time)))

        cap = Text("對稱：每個方向都一樣", font=FONT, font_size=32, color=FIELD).move_to([RX, -2.4, 0])
        self.play(angle.animate.set_value(0.04), run_time=0.6, rate_func=there_and_back)
        self.play(FadeIn(cap), run_time=0.5)
        self.play(angle.animate.set_value(-0.035), run_time=0.7, rate_func=there_and_back)

        lab_s = Text("側視", font=FONT, font_size=30, color=MUTED).move_to([LX, 2.35, 0])
        lab_t = Text("俯視", font=FONT, font_size=30, color=MUTED).move_to([RX, 2.35, 0])
        self.wait(max(0.1, 4.2 - self.renderer.time))
        self.play(FadeIn(lab_s), FadeIn(lab_t), run_time=0.6)
        while self.renderer.time < T_FALL - 1.2:
            self.play(angle.animate.set_value(0.05), run_time=0.7, rate_func=there_and_back)
            self.play(angle.animate.set_value(-0.04), run_time=0.6, rate_func=there_and_back)
        self.play(angle.animate.set_value(0.08), run_time=0.8)

        # fall to the right (angle measured from vertical)
        self.play(angle.animate.set_value(PI / 2 - 0.03), run_time=1.1, rate_func=rate_functions.rush_into)
        self.play(angle.animate.set_value(PI / 2 - 0.12), run_time=0.15, rate_func=rate_functions.rush_from)
        self.play(angle.animate.set_value(PI / 2 - 0.03), run_time=0.15, rate_func=rate_functions.rush_into)

        dirs.clear_updaters()
        chosen = dirs[0]
        lying = Rectangle(width=1.7, height=0.24, color="#FFC107", fill_opacity=1, stroke_width=0)
        lying.move_to([RX + 0.85, 0, 0])
        cap2 = Text("倒下：選定了某一個方向", font=FONT, font_size=32, color=PARTICLE).move_to([RX, -2.4, 0])
        self.play(*[d.animate.set_opacity(0.12) for d in dirs[1:]],
                  chosen.animate.set_color(PARTICLE).set_stroke(width=8),
                  FadeTransform(top_pencil, lying), FadeOut(top_tip),
                  Transform(cap, cap2), run_time=1.0)
        self.wait(0.8)

        title = Text("自發對稱性破缺", font=FONT, font_size=60, color=PARTICLE, weight=BOLD).move_to([0, 3.15, 0])
        self.play(Write(title), run_time=1.5)
        sub = Text("定律本身對稱，但實際的狀態不對稱", font=FONT, font_size=30, color=TEXT).move_to([LX + 0.3, -2.4, 0])
        self.play(FadeIn(sub), run_time=0.8)
        while DUR - self.renderer.time > 1.3:
            self.play(chosen.animate.scale(1.08, about_point=[RX, 0, 0]), rate_func=there_and_back, run_time=1.2)
        self.wait(max(0.1, DUR - self.renderer.time))
