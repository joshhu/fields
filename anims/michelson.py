import numpy as np
from manim import *
from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

LIGHT = "#FFF59D"


def poly_point(pts, s):
    """Point at arclength s along polyline pts (s wraps)."""
    segs = list(zip(pts[:-1], pts[1:]))
    lens = [np.linalg.norm(b - a) for a, b in segs]
    s = s % sum(lens)
    for (a, b), L in zip(segs, lens):
        if s <= L:
            return a + (b - a) * s / L
        s -= L
    return pts[-1]


class Main(Scene):
    def construct(self):
        O = np.array([-1.5, 0.6, 0])  # beam splitter
        src = O + LEFT * 3.6
        m1 = O + RIGHT * 3.4
        m2 = O + UP * 2.7
        det = O + DOWN * 2.6

        source = VGroup(Rectangle(width=0.9, height=0.6, fill_color=PARTICLE, fill_opacity=1, stroke_width=0),
                        Text("光源", font=FONT, font_size=26, color=PARTICLE).shift(DOWN * 0.6)).move_to(src + DOWN * 0.25)
        source[0].move_to(src)
        bs = Line(O + (-0.45, -0.45, 0), O + (0.45, 0.45, 0), color="#B3E5FC", stroke_width=8)
        bs_l = Text("分光鏡", font=FONT, font_size=26, color=MUTED).next_to(O, DR, buff=0.35)
        mir1 = Line(m1 + DOWN * 0.55, m1 + UP * 0.55, color=TEXT, stroke_width=10)
        mir2 = Line(m2 + LEFT * 0.55, m2 + RIGHT * 0.55, color=TEXT, stroke_width=10)
        l1 = Text("鏡子", font=FONT, font_size=26, color=MUTED).next_to(mir1, RIGHT, buff=0.2)
        l2 = Text("鏡子", font=FONT, font_size=26, color=MUTED).next_to(mir2, RIGHT, buff=0.2)
        detector = Square(0.6, fill_color="#455A64", fill_opacity=1, stroke_color=TEXT, stroke_width=2).move_to(det)
        ld = Text("偵測器", font=FONT, font_size=26, color=MUTED).next_to(detector, LEFT, buff=0.25)
        app = VGroup(source, bs, bs_l, mir1, mir2, l1, l2, detector, ld)

        self.play(FadeIn(app, lag_ratio=0.1), run_time=1.5)

        beams = VGroup(Line(src, O), Line(O, m1), Line(O, m2), Line(O, det)).set_color(LIGHT).set_stroke(width=3, opacity=0.7)
        self.play(Create(beams[0]), run_time=0.8)
        self.play(Create(beams[1]), Create(beams[2]), run_time=1.0)
        self.play(Create(beams[3]), run_time=0.7)

        t = ValueTracker(0)
        pathA = [src, O, m1, O, det]
        pathB = [src, O, m2, O, det]

        def pulses():
            g = VGroup()
            tt = t.get_value()
            for path, col in [(pathA, LIGHT), (pathB, "#FFE082")]:
                for k in range(5):
                    p = poly_point([np.array(q) for q in path], tt * 3.0 + k * 3.0)
                    g.add(Dot(p, radius=0.09, color=col).set_glow_factor(0) if hasattr(Dot, "set_glow_factor") else Dot(p, radius=0.09, color=col))
            return g
        pul = always_redraw(pulses)
        self.add(pul)

        # ether wind arrows
        ang = ValueTracker(PI)  # wind blowing towards the left
        def wind():
            g = VGroup()
            tt = t.get_value()
            d = np.array([np.cos(ang.get_value()), np.sin(ang.get_value()), 0])
            perp = np.array([-d[1], d[0], 0])
            c0 = np.array([4.6, 1.75, 0])
            for k in range(-2, 3):
                off = ((tt * 0.8 + k * 0.37) % 1.0 - 0.5) * 1.6
                base = c0 + perp * k * 0.35 + d * off
                g.add(Arrow(base - d * 0.35, base + d * 0.35, buff=0, color=MUTED, stroke_width=3,
                            max_tip_length_to_length_ratio=0.3).set_opacity(0.8))
            return g
        wnd = always_redraw(wind)
        wl = Text("以太風？", font=FONT, font_size=34, color=MUTED).move_to([4.6, 3.35, 0])
        self.play(t.animate.increment_value(2), FadeIn(wnd), FadeIn(wl), run_time=2, rate_func=linear)

        # interference fringes inset
        frame = Rectangle(width=3.0, height=1.5, stroke_color=TEXT, stroke_width=2).move_to([4.6, -1.1, 0])
        stripes = VGroup(*[Rectangle(width=0.15, height=1.5, stroke_width=0, fill_color=LIGHT,
                                     fill_opacity=0.25 + 0.65 * (0.5 + 0.5 * np.cos(i * 0.9)))
                           for i in range(20)]).arrange(RIGHT, buff=0).move_to(frame)
        fl = Text("干涉條紋", font=FONT, font_size=28, color=TEXT).next_to(frame, UP, buff=0.15)
        self.play(FadeIn(frame), FadeIn(stripes), FadeIn(fl), t.animate.increment_value(1.5), run_time=1.5, rate_func=linear)

        # rotate the wind direction: fringes do not move
        self.play(ang.animate.set_value(PI / 2), t.animate.increment_value(2.5), run_time=2.5, rate_func=linear)
        self.play(ang.animate.set_value(-PI / 4), t.animate.increment_value(2.5), run_time=2.5, rate_func=linear)
        nochg = Text("條紋完全不動", font=FONT, font_size=30, color=ACCENT).next_to(frame, DOWN, buff=0.1)
        self.play(FadeIn(nochg), t.animate.increment_value(1), run_time=1, rate_func=linear)
        final = Text("光速在各個方向都一樣", font=FONT, font_size=32, color=PARTICLE, weight=BOLD)
        final.move_to([4.4, -2.6, 0])
        self.play(FadeIn(final, shift=UP * 0.2), Indicate(stripes, scale_factor=1.03, color=LIGHT),
                  t.animate.increment_value(1.5), run_time=1.5, rate_func=linear)
        self.play(t.animate.increment_value(3.5), ang.animate.set_value(-PI), run_time=3.5, rate_func=linear)
