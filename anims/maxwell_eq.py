import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

MATH = "Cambria Math"


class Main(Scene):
    def construct(self):
        # faint travelling wave in the background so the frame never sits still
        t = ValueTracker(0)
        def bgwave():
            g = VGroup()
            for k in range(3):
                g.add(FunctionGraph(lambda x, k=k: 0.35 * np.sin(1.2 * x - 2.2 * t.get_value() + k) - 2.0 + 0.0 * k,
                                    x_range=[-7.5, 7.5], color=FIELD, stroke_width=2).set_stroke(opacity=0.12 + 0.05 * k))
            return g
        bg = always_redraw(bgwave)
        self.add(bg)

        rows = [
            ("高斯定律", "∇ · E = ρ / ε₀"),
            ("磁的高斯定律", "∇ · B = 0"),
            ("法拉第定律", "∇ × E = − ∂B / ∂t"),
            ("安培－馬克士威定律", "∇ × B = μ₀J + μ₀ε₀ ∂E / ∂t"),
        ]
        header = Text("馬克士威方程組", font=FONT, font_size=50, color=FIELD, weight=BOLD)
        header.move_to([0, 3.1, 0])
        self.play(FadeIn(header, shift=DOWN * 0.2), t.animate.increment_value(1.5), run_time=1.5, rate_func=linear)

        lines = VGroup()
        for i, (name, eq) in enumerate(rows):
            n = Text(name, font=FONT, font_size=32, color=MUTED)
            e = Text(eq, font=MATH, font_size=46, color=TEXT)
            y = 2.0 - i * 0.95
            n.move_to([-2.7, y, 0], aligned_edge=RIGHT)
            e.move_to([-2.2, y, 0], aligned_edge=LEFT)
            lines.add(VGroup(n, e))
        for row in lines:
            self.play(FadeIn(row[0], shift=RIGHT * 0.3), Write(row[1]), t.animate.increment_value(2.2),
                      run_time=2.2, rate_func=linear)
        self.play(t.animate.increment_value(1.5), run_time=1.5, rate_func=linear)

        # highlight the two curl equations: changing E makes B, changing B makes E
        box = SurroundingRectangle(VGroup(lines[2], lines[3]), color=ACCENT, buff=0.18, corner_radius=0.1)
        hint = Text("變化的電場產生磁場，變化的磁場產生電場", font=FONT, font_size=30, color=ACCENT)
        hint.next_to(box, DOWN, buff=0.2)
        self.play(Create(box), FadeIn(hint), t.animate.increment_value(2), run_time=2, rate_func=linear)
        self.play(t.animate.increment_value(1.5), run_time=1.5, rate_func=linear)

        c = Text("c = 1 / √(μ₀ε₀) ≈ 3 × 10⁸ m/s", font=MATH, font_size=50, color=PARTICLE)
        eqlight = Text("＝ 光速", font=FONT, font_size=50, color=PARTICLE, weight=BOLD).next_to(c, RIGHT, buff=0.4)
        VGroup(c, eqlight).move_to([0, -2.15, 0])
        self.play(FadeOut(hint), lines.animate.set_opacity(0.55), box.animate.set_stroke(opacity=0.4),
                  Write(c), t.animate.increment_value(2.5), run_time=2.5, rate_func=linear)
        self.play(FadeIn(eqlight, scale=1.5), t.animate.increment_value(1.2), run_time=1.2, rate_func=linear)
        self.play(Circumscribe(VGroup(c, eqlight), color=PARTICLE, buff=0.15),
                  t.animate.increment_value(2), run_time=2, rate_func=linear)
        self.play(t.animate.increment_value(4), run_time=4, rate_func=linear)
