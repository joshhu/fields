import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

DUR = 25.0
FP = np.array([1.6, -0.3, 0.0])


def flow(p):
    x, y = p[0] - FP[0], p[1] - FP[1]
    return np.array([-0.45 * x, -1.1 * y + 0.07 * x * x, 0.0])


def trajectory(p0, t_end=12.0, dt=0.02):
    pts = [np.array(p0, float)]
    for _ in range(int(t_end / dt)):
        pts.append(pts[-1] + flow(pts[-1]) * dt)
    return np.array(pts)


class Main(Scene):
    def construct(self):
        ax_x = Arrow([-6.4, -2.65, 0], [6.6, -2.65, 0], buff=0, color=MUTED, stroke_width=3)
        ax_y = Arrow([-6.4, -2.65, 0], [-6.4, 3.3, 0], buff=0, color=MUTED, stroke_width=3)

        stream = StreamLines(flow, x_range=[-6.1, 6.3, 0.6], y_range=[-2.45, 3.0, 0.6],
                             stroke_width=2.2, max_anchors_per_line=40, padding=0.3,
                             colors=[FIELD, "#B3E5FC"], opacity=0.8)
        self.add(ax_x, ax_y)
        self.play(stream.create(), run_time=2.0)
        self.add(stream)
        stream.start_animation(warm_up=False, flow_speed=1.4, time_width=0.5)
        self.wait(2.5)

        gx = Text("耦合常數 g₁", font=FONT, font_size=28, color=MUTED).next_to(ax_x.get_end(), UP, buff=0.15).shift(LEFT * 0.9)
        gy = Text("g₂", font=FONT, font_size=28, color=MUTED).next_to(ax_y.get_end(), RIGHT, buff=0.15)
        self.play(FadeIn(gx), FadeIn(gy), run_time=0.8)

        fp = Dot(FP, radius=0.14, color=PARTICLE)
        halo = Circle(radius=0.3, color=PARTICLE, stroke_width=3).move_to(FP)
        halo.add_updater(lambda m, dt: m.become(Circle(
            radius=0.3 + 0.12 * np.sin(4 * self.renderer.time), color=PARTICLE, stroke_width=3).move_to(FP)))
        fp_lab = Text("不動點（低能量）", font=FONT, font_size=32, color=PARTICLE).next_to(fp, DOWN, buff=0.45)
        bg = BackgroundRectangle(fp_lab, color=BG, fill_opacity=0.75, buff=0.08)
        self.play(FadeIn(fp, scale=2), FadeIn(halo), FadeIn(bg), FadeIn(fp_lab), run_time=1.0)
        self.wait(1.0)

        hi = Text("高能量：微觀細節各不相同", font=FONT, font_size=30, color=TEXT)
        hi.move_to([2.6, 2.95, 0])
        hi_bg = BackgroundRectangle(hi, color=BG, fill_opacity=0.75, buff=0.08)
        self.play(FadeIn(hi_bg), FadeIn(hi), run_time=0.8)

        starts = [((-5.6, 2.6, 0), "流體", "#81C784"), ((-5.4, -2.2, 0), "磁鐵", ACCENT), ((6.0, 2.3, 0), "合金", "#FFF176")]
        movers, labels, anims = [], [], []
        for p0, name, col in starts:
            path_pts = trajectory(p0)
            path = VMobject().set_points_smoothly(path_pts[::10]).set_stroke(col, 5)
            d = Dot(p0, radius=0.12, color=col)
            lab = Text(name, font=FONT, font_size=32, color=col, weight=BOLD)
            lab.next_to(d, DOWN if p0[1] > 0 else UP, buff=0.15)
            lab_bg = BackgroundRectangle(lab, color=BG, fill_opacity=0.7, buff=0.06)
            movers.append((d, path))
            labels.append(VGroup(lab_bg, lab))
        self.play(*[FadeIn(d, scale=2) for d, _ in movers], *[FadeIn(l) for l in labels], run_time=0.8)
        self.play(*[Create(p) for _, p in movers], *[MoveAlongPath(d, p) for d, p in movers],
                  run_time=7.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        uni = Text("普適性：微觀不同，低能行為相同", font=FONT, font_size=44, color=PARTICLE, weight=BOLD)
        uni.move_to([0.6, 1.6, 0])
        uni_bg = BackgroundRectangle(uni, color=BG, fill_opacity=0.8, buff=0.15)
        self.play(FadeIn(uni_bg), Write(uni), run_time=1.5)
        self.wait(max(0.5, DUR - self.renderer.time))
