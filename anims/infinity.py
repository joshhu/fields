import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

DUR = 22.0
EY = 0.2           # electron line height
EX = -3.8          # electron center


def loop_arc(cx, r, phase, up=True, waves=None, amp=0.055, n=260):
    """Virtual-photon loop: wiggly semicircle starting/ending on the electron line."""
    waves = waves or max(3, int(round(5 * r)))
    th = np.linspace(0, np.pi, n) if up else np.linspace(np.pi, 2 * np.pi, n)
    rr = r + amp * np.sin(waves * 2 * th + phase)
    pts = np.stack([cx + rr * np.cos(th), EY + rr * np.sin(th), np.zeros(n)], 1)
    return VMobject().set_points_smoothly(pts)


# (center offset, radius, up?, appear time)
LOOPS = [(0.0, 1.0, True, 0.6), (-0.5, 0.45, True, 2.0), (0.6, 0.5, False, 3.0),
         (0.3, 1.6, True, 4.2), (-0.9, 0.8, False, 5.0), (0.0, 2.2, True, 5.8),
         (1.0, 0.35, True, 6.4), (-1.3, 0.4, True, 6.9), (0.2, 1.3, False, 7.4),
         (-0.2, 0.25, False, 7.8), (0.8, 2.6, True, 8.3)]


class Main(Scene):
    def construct(self):
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        line = Line([-6.8, EY, 0], [-0.8, EY, 0], color=PARTICLE, stroke_width=4)
        arrow_tip = Arrow([-1.6, EY, 0], [-0.8, EY, 0], buff=0, color=PARTICLE, stroke_width=4)
        e = Dot([EX, EY, 0], radius=0.16, color=PARTICLE)
        glow = Dot([EX, EY, 0], radius=0.32, color=PARTICLE).set_opacity(0.25)
        e_lab = Text("e⁻", font=FONT, font_size=34, color=PARTICLE).next_to(e, DOWN, buff=0.2)
        self.play(Create(line), FadeIn(arrow_tip), FadeIn(e), FadeIn(glow), FadeIn(e_lab), run_time=1.0)

        loops = VGroup()
        for off, r, up, t0 in LOOPS:
            m = always_redraw(lambda off=off, r=r, up=up, t0=t0: loop_arc(
                EX + off, r, 6 * clock.get_value(), up).set_stroke(
                FIELD, 3, opacity=float(np.clip((clock.get_value() - t0) / 0.6, 0, 1)) * 0.9))
            loops.add(m)
        self.add(loops)
        self.wait(3.2)

        se = Text("電子自能：電子與自己的場作用", font=FONT, font_size=30, color=TEXT)
        se.move_to([EX, -2.35, 0])
        self.play(FadeIn(se, shift=UP * 0.2), run_time=1.0)

        title = Text("算出來的修正量", font=FONT, font_size=40, color=TEXT).move_to([3.4, 2.3, 0])
        self.play(FadeIn(title), run_time=0.8)

        growth = ValueTracker(0)

        def make_num():
            n = int(10 ** growth.get_value())
            t = Text(f"{n:,}", font=FONT, font_size=80, color=TEXT)
            if t.width > 6.0:
                t.scale_to_fit_width(6.0)
            return t.move_to([3.4, 0.6, 0])

        num = make_num()
        num.add_updater(lambda m: m.become(make_num()))
        self.add(num)
        self.play(growth.animate.set_value(11.9), run_time=3.5, rate_func=rate_functions.ease_in_quad)
        num.clear_updaters()
        inf = Text("∞", font=FONT, font_size=220, color="#FF5252").move_to([3.4, 0.6, 0])
        self.play(ReplacementTransform(num, inf), run_time=0.5)
        for _ in range(3):
            self.play(inf.animate.scale(1.15).set_color("#FF8A80"), run_time=0.35)
            self.play(inf.animate.scale(1 / 1.15).set_color("#FF5252"), run_time=0.35)
        warn = Text("發散！", font=FONT, font_size=44, color="#FF5252").move_to([3.4, -1.3, 0])
        self.play(FadeIn(warn, scale=1.3), run_time=0.6)
        self.wait(0.8)

        # --- renormalization ---
        ren = Text("重整化", font=FONT, font_size=60, color=PARTICLE, weight=BOLD).move_to([3.4, 2.4, 0])
        self.play(FadeOut(title), FadeOut(warn), FadeIn(ren, shift=DOWN * 0.2), run_time=1.0)

        box = RoundedRectangle(width=3.0, height=1.5, corner_radius=0.2, color=ACCENT, stroke_width=4)
        box.move_to([1.6, 0.0, 0])
        box_lab = Text("裸質量 m₀\n裸電荷 e₀", font=FONT, font_size=30, color=ACCENT, line_spacing=0.8)
        box_lab.move_to(box)
        self.play(Create(box), FadeIn(box_lab), run_time=1.0)
        self.play(inf.animate.scale(0.25).move_to(box.get_top() + DOWN * 0.05), run_time=1.0)
        self.play(FadeOut(inf, scale=0.3), box.animate.set_fill(ACCENT, opacity=0.18), run_time=0.6)

        arr = Arrow(box.get_right(), box.get_right() + RIGHT * 1.2, buff=0.1, color=TEXT, stroke_width=5)
        res = Text("m、e\n實驗測得的值", font=FONT, font_size=30, color="#81C784", line_spacing=0.8)
        res.next_to(arr, RIGHT, buff=0.2)
        ok = Text("有限 ✓", font=FONT, font_size=40, color="#81C784").next_to(res, DOWN, buff=0.35)
        self.play(GrowArrow(arr), FadeIn(res, shift=LEFT * 0.2), run_time=1.0)
        self.play(FadeIn(ok, scale=1.2), run_time=0.6)
        cap = Text("把無窮大吸收進參數，剩下的都是有限值", font=FONT, font_size=30, color=TEXT)
        cap.scale(0.9).move_to([3.4, -1.75, 0])
        self.play(FadeIn(cap), run_time=0.8)
        self.wait(max(0.5, DUR - clock.get_value() - 0.1))
