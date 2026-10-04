import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

DUR = 25.0
PURPLE = "#9575CD"
NEWTON = "#CFD8DC"


class Main(Scene):
    def construct(self):
        newton = Circle(radius=0.82, color=NEWTON, stroke_width=4).move_to([0, -0.05, 0])
        newton.set_fill(NEWTON, opacity=0.10)
        n_lab = Text("牛頓力學", font=FONT, font_size=24, color=NEWTON).move_to(newton)

        sr = Circle(radius=1.5, color=FIELD, stroke_width=4).move_to([0, 0.15, 0]).set_fill(FIELD, opacity=0.06)
        sr_lab = Text("狹義相對論", font=FONT, font_size=26, color=FIELD).move_to([0, 1.17, 0])

        gr = Ellipse(width=6.0, height=4.8, color=PURPLE, stroke_width=4).move_to([-1.2, 0.3, 0])
        gr.set_fill(PURPLE, opacity=0.06)
        gr_lab = Text("廣義相對論", font=FONT, font_size=30, color=PURPLE).move_to([-3.0, 0.45, 0])
        gr_sub = Text("（重力、彎曲時空）", font=FONT, font_size=18, color=PURPLE).next_to(gr_lab, DOWN, buff=0.12)

        qft = Ellipse(width=6.0, height=4.8, color=PARTICLE, stroke_width=4).move_to([1.2, 0.3, 0])
        qft.set_fill(PARTICLE, opacity=0.06)
        qft_lab = Text("量子場論", font=FONT, font_size=30, color=PARTICLE).move_to([3.0, 0.45, 0])
        qft_sub = Text("（標準模型）", font=FONT, font_size=20, color=PARTICLE).next_to(qft_lab, DOWN, buff=0.12)

        outer = DashedVMobject(Ellipse(width=10.8, height=6.3, color=ACCENT, stroke_width=4), num_dashes=70)
        outer.move_to([0, 0.3, 0])
        o_lab = Text("？ 更深層的理論", font=FONT, font_size=32, color=ACCENT).move_to([0, 3.02, 0])

        self.play(Create(newton), run_time=1.0)
        self.play(FadeIn(n_lab), run_time=0.6)
        self.wait(1.0)
        self.play(TransformFromCopy(newton, sr), run_time=1.4)
        self.play(FadeIn(sr_lab), run_time=0.6)
        lo = Text("低速極限", font=FONT, font_size=18, color=MUTED).move_to([0, -1.08, 0])
        self.play(FadeIn(lo), run_time=0.5)
        self.wait(0.8)
        self.play(GrowFromCenter(gr), run_time=1.4)
        self.play(FadeIn(gr_lab), FadeIn(gr_sub), run_time=0.7)
        self.wait(0.5)
        self.play(GrowFromCenter(qft), run_time=1.4)
        self.play(FadeIn(qft_lab), FadeIn(qft_sub), run_time=0.7)
        self.wait(0.8)
        self.play(Create(outer), run_time=2.0)
        self.play(Write(o_lab), run_time=1.0)

        cap = Text("新理論包容舊理論，舊理論是新理論的特例", font=FONT, font_size=32, color=TEXT)
        cap.move_to([0, -2.55, 0])
        cap_bg = BackgroundRectangle(cap, color=BG, fill_opacity=0.85, buff=0.1)
        self.play(FadeIn(cap_bg), FadeIn(cap, shift=UP * 0.15), run_time=1.0)

        layers = [newton, sr, gr, qft]
        k = 0
        while DUR - self.renderer.time > 1.2:
            m = layers[k % 4]
            self.play(m.animate.set_stroke(width=9), rate_func=there_and_back, run_time=1.0)
            k += 1
        self.wait(max(0.1, DUR - self.renderer.time))
