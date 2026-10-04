"""Closing timeline of the 300-year journey toward field theory."""
import numpy as np
from manim import *

from style import ACCENT, BG, FIELD, FONT, MUTED, PARTICLE, TEXT

EVENTS = [
    ("1687", "牛頓"), ("1830s", "法拉第"), ("1865", "馬克士威"), ("1905/15", "愛因斯坦"),
    ("1927", "QED"), ("1954", "楊－米爾斯"), ("1973", "標準模型"), ("2012", "希格斯"),
]


class Main(Scene):
    def construct(self):
        rng = np.random.default_rng(5)
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t)

        # drifting dust + faint background waves
        n = 90
        px, py = rng.uniform(-7.2, 7.2, n), rng.uniform(-3.6, 4.0, n)
        vx = rng.uniform(-0.12, 0.12, n)
        dust = VGroup(*[Dot(radius=rng.uniform(0.01, 0.03), color=FIELD) for _ in range(n)])
        dust.add_updater(lambda g: [d.move_to([((px[i] + vx[i] * t.get_value() + 7.2) % 14.4) - 7.2,
                                               py[i] + 0.1 * np.sin(t.get_value() * 0.5 + i), 0]).set_opacity(0.35)
                                    for i, d in enumerate(g)])
        waves = always_redraw(lambda: VGroup(*[
            FunctionGraph(lambda x, k=k: -1.3 + 0.5 * k + 0.12 * np.sin(0.9 * x - 0.8 * t.get_value() + k),
                          x_range=[-7.2, 7.2], color=FIELD, stroke_width=1.5, stroke_opacity=0.12)
            for k in range(5)]))
        self.add(waves, dust)

        y0 = 0.6
        x0, x1 = -6.1, 6.1
        line = Line([x0 - 0.4, y0, 0], [x1 + 0.4, y0, 0], color=MUTED, stroke_width=3)
        xs = np.linspace(x0, x1, len(EVENTS))
        nodes, years, names = VGroup(), VGroup(), VGroup()
        for i, ((yr, nm), x) in enumerate(zip(EVENTS, xs)):
            d = Dot([x, y0, 0], radius=0.11, color=MUTED)
            nodes.add(d)
            years.add(Text(yr, font=FONT, font_size=26, color=PARTICLE).move_to([x, y0 + 0.55, 0]))
            names.add(Text(nm, font=FONT, font_size=26, color=TEXT).move_to([x, y0 - 0.55 - 0.42 * (i % 2), 0]))

        self.play(Create(line), FadeIn(nodes), run_time=1.5)
        for i in range(len(EVENTS)):
            halo = Circle(radius=0.11, color=FIELD, stroke_width=4).move_to(nodes[i])
            self.play(nodes[i].animate.set_color(FIELD).scale(1.4), FadeIn(years[i], shift=DOWN * 0.15),
                      FadeIn(names[i], shift=UP * 0.15), halo.animate.scale(3.5).set_stroke(opacity=0),
                      run_time=1.05)
            self.remove(halo)
        glow_path = Line([x0, y0, 0], [x1, y0, 0], color=FIELD, stroke_width=6)
        self.play(Create(glow_path), run_time=1.5)

        tl = VGroup(line, glow_path, nodes, years, names)
        final = Text("空間，才是宇宙真正的主角", font=FONT, font_size=60, color=TEXT)
        final.move_to(DOWN * 0.9)
        underline = Line(final.get_left(), final.get_right(), color=FIELD, stroke_width=3).next_to(final, DOWN, 0.2)
        self.play(tl.animate.scale(0.8).move_to(UP * 2.3).set_opacity(0.55), run_time=1.6)
        self.play(Write(final), run_time=2.4)
        self.play(Create(underline), run_time=1)
        self.wait(3)
