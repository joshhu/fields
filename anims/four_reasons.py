"""Four walls the particle picture hit, each with a mini animation; camera tours the 2x2 grid."""
import numpy as np
from manim import *

from style import ACCENT, BG, FIELD, FONT, MUTED, PARTICLE, TEXT

QUADS = [np.array([-3.5, 1.45, 0]), np.array([3.5, 1.45, 0]),
         np.array([-3.5, -1.55, 0]), np.array([3.5, -1.55, 0])]
BW, BH = 6.6, 2.7
HEADERS = ["① 超距作用說不通", "② 相對論量子力學不自洽", "③ 多種交互作用無法統一", "④ 局域對稱性無法實現"]
NOTES = ["場：以有限速度、逐點傳遞", "粒子會產生與湮滅，數目不守恆", "規範場論用對稱性統一三種力", "每一點各自旋轉，需要規範場來連接"]
DIM = 0.3


class Quad:
    def __init__(self, i):
        self.c = QUADS[i]
        self.b = ValueTracker(DIM)       # brightness multiplier
        self.speed = ValueTracker(0)     # local clock runs only once activated
        self.lt = ValueTracker(0)
        self.lt.add_updater(lambda m, dt: m.increment_value(dt * self.speed.get_value()))
        self.box = RoundedRectangle(corner_radius=0.2, width=BW, height=BH, stroke_color=MUTED, stroke_width=2.5,
                                    fill_color=FIELD, fill_opacity=0.05).move_to(self.c)
        self.box.add_updater(lambda m: m.set_stroke(opacity=self.b.get_value()).set_fill(
            opacity=0.06 * self.b.get_value()))
        self.head = Text(HEADERS[i], font=FONT, font_size=28, color=TEXT).move_to(self.c + UP * 1.0)
        self.head.add_updater(lambda m: m.set_opacity(self.b.get_value()))
        self.note = Text(NOTES[i], font=FONT, font_size=22, color=PARTICLE).move_to(self.c + DOWN * 1.08)
        self.note_on = ValueTracker(0)
        self.note.add_updater(lambda m: m.set_opacity(
            self.note_on.get_value() * max(0.0, (self.b.get_value() - DIM) / (1 - DIM))))

    def static(self):
        return VGroup(self.box, self.head, self.note)


def ripples(q):
    """A jiggles, wavefronts travel at finite speed, B responds only after they arrive."""
    y = q.c[1] - 0.25
    xa, xb = q.c[0] - 2.4, q.c[0] + 2.4
    c = 1.3
    dist = xb - xa
    A = Dot(radius=0.13, color=PARTICLE)
    B = Dot(radius=0.13, color=PARTICLE)
    la = Text("A", font=FONT, font_size=22, color=TEXT)
    lb = Text("B", font=FONT, font_size=22, color=TEXT)

    def upd_ab(g):
        t = q.lt.get_value()
        b = q.b.get_value()
        A.move_to([xa, y + 0.18 * np.sin(5 * t) * min(t, 1), 0])
        tb = t - dist / c
        B.move_to([xb, y + (0.18 * np.sin(5 * tb) * min(tb, 1) if tb > 0 else 0), 0])
        la.next_to(A, DOWN, buff=0.12)
        lb.next_to(B, DOWN, buff=0.12)
        for m in g:
            m.set_opacity(b)
    ab = VGroup(A, B, la, lb)
    ab.add_updater(upd_ab)

    def waves():
        t = q.lt.get_value()
        b = q.b.get_value()
        g = VGroup()
        k0 = int(max(0, (t - dist / c - 0.6) // 0.7))
        for k in range(k0, int(t / 0.7) + 1):
            r = c * (t - 0.7 * k)
            if 0.05 < r < dist + 0.25:
                ang = min(0.26, 0.75 / r)
                g.add(Arc(radius=r, start_angle=-ang, angle=2 * ang, arc_center=[xa, y, 0], color=FIELD,
                          stroke_width=4, stroke_opacity=b * (1 - 0.6 * r / dist)))
        if not len(g):
            g.add(VectorizedPoint([xa, y, 0]))
        return g
    return VGroup(always_redraw(waves), ab)


def pairs(q):
    """Photon -> e- e+ -> annihilate, looping, with a particle counter."""
    cx, cy = q.c[0] - 0.5, q.c[1] - 0.2
    P = 4.0
    em = Dot(radius=0.12, color=PARTICLE)
    ep = Dot(radius=0.12, color=ACCENT)
    lem = Text("e⁻", font=FONT, font_size=22, color=PARTICLE)
    lep = Text("e⁺", font=FONT, font_size=22, color=ACCENT)
    counts = {n: Text(f"粒子數：{n}", font=FONT, font_size=24, color=TEXT).move_to([q.c[0] + 2.15, cy + 0.15, 0])
              for n in (1, 2, 0)}

    def phase():
        return (q.lt.get_value() % P) / P

    def photon():
        p = phase()
        b = q.b.get_value()
        if p < 0.3:
            head = cx - 1.8 + 1.8 * (p / 0.3)
            tail = max(head - 0.9, q.c[0] - 3.05)
            return ParametricFunction(lambda s: np.array([s, cy + 0.12 * np.sin(14 * s), 0]),
                                      t_range=[tail, head], color=FIELD, stroke_width=4, stroke_opacity=b)
        if p > 0.9:
            s = (p - 0.9) / 0.1
            return Circle(radius=0.1 + 0.9 * s, color=WHITE, stroke_width=5,
                          stroke_opacity=b * (1 - s)).move_to([cx, cy, 0])
        return VectorizedPoint([cx, cy, 0])

    def upd(g):
        p = phase()
        b = q.b.get_value()
        if 0.3 <= p < 0.65:
            s = rate_functions.ease_out_sine((p - 0.3) / 0.35)
        elif 0.65 <= p < 0.9:
            s = 1 - rate_functions.ease_in_sine((p - 0.65) / 0.25)
        else:
            s = 0
        vis = 1.0 if 0.3 <= p < 0.9 else 0.0
        em.move_to([cx + 1.4 * s, cy + 0.35 * s, 0]).set_opacity(b * vis)
        ep.move_to([cx + 1.4 * s, cy - 0.35 * s, 0]).set_opacity(b * vis)
        lem.next_to(em, RIGHT, buff=0.08).set_opacity(b * vis)
        lep.next_to(ep, RIGHT, buff=0.08).set_opacity(b * vis)
        n = 1 if p < 0.3 else (2 if p < 0.9 else 0)
        for k, m in counts.items():
            m.set_opacity(b if k == n else 0)
    g = VGroup(em, ep, lem, lep, *counts.values())
    g.add_updater(upd)
    return VGroup(always_redraw(photon), g)


def unify(q):
    """Three forces flow together into one gauge group."""
    cx, cy = q.c[0], q.c[1] - 0.12
    merge = np.array([cx + 0.35, cy, 0])
    specs = [("電磁", FIELD, 0.5), ("弱力", ACCENT, 0.0), ("強力", PARTICLE, -0.5)]
    curves, labels, dots = VGroup(), VGroup(), VGroup()
    for name, col, dy in specs:
        start = np.array([cx - 2.2, cy + dy, 0])
        cv = CubicBezier(start, start + RIGHT * 1.3, merge + LEFT * 1.2, merge, color=col, stroke_width=4)
        curves.add(cv)
        labels.add(Text(name, font=FONT, font_size=22, color=col).next_to(start, LEFT, buff=0.12))
        for k in range(3):
            dots.add(Dot(radius=0.07, color=col))
    grp = Text("SU(3)×SU(2)×U(1)", font=FONT, font_size=22, color=TEXT)
    frame = RoundedRectangle(corner_radius=0.12, width=grp.width + 0.3, height=0.7, stroke_color=TEXT,
                             stroke_width=2.5).move_to([cx + 1.75, cy, 0])
    grp.move_to(frame)

    def upd(g):
        t = q.lt.get_value()
        b = q.b.get_value()
        for i, d in enumerate(dots):
            cv = curves[i // 3]
            a = (0.35 * t + (i % 3) / 3) % 1
            d.move_to(cv.point_from_proportion(a)).set_opacity(b * np.sin(np.pi * a) ** 0.5)
        for m in (*curves, frame):
            m.set_stroke(opacity=b)
        for m in (*labels, grp):
            m.set_opacity(b)
        pulse = 0.5 + 0.5 * np.sin(3 * t)
        frame.set_fill(FIELD, opacity=b * 0.15 * pulse)
    g = VGroup(curves, labels, frame, grp, dots)
    g.add_updater(upd)
    return g


def local_sym(q):
    """Arrows on a grid rotate independently; gauge links appear to connect them."""
    cx, cy = q.c[0], q.c[1] - 0.15
    xs = np.linspace(-2.4, 2.4, 7)
    ys = np.array([0.45, 0.0, -0.45])
    link_on = ValueTracker(0)

    def ang(x, y, t):
        return 1.3 * np.sin(0.9 * t + 1.3 * x) + 0.9 * np.cos(0.7 * t + 2.1 * y)

    def draw():
        t = q.lt.get_value()
        b = q.b.get_value()
        g = VGroup()
        lo = link_on.get_value()
        if lo > 0:
            for x in xs:
                for y in ys:
                    for dx, dy in ((0.8, 0), (0, -0.45)):
                        if x + dx <= 2.41 and y + dy >= -0.46:
                            p0 = np.array([cx + x, cy + y, 0])
                            p1 = np.array([cx + x + dx, cy + y + dy, 0])
                            mid = (p0 + p1) / 2
                            wob = 0.06 * np.sin(4 * t + 3 * x + 5 * y)
                            nrm = np.array([-(p1 - p0)[1], (p1 - p0)[0], 0])
                            nrm = nrm / np.linalg.norm(nrm)
                            g.add(Line(p0, mid + nrm * wob, color=ACCENT, stroke_width=3,
                                       stroke_opacity=lo * b * 0.8))
                            g.add(Line(mid + nrm * wob, p1, color=ACCENT, stroke_width=3,
                                       stroke_opacity=lo * b * 0.8))
        for x in xs:
            for y in ys:
                a = ang(x, y, t)
                p = np.array([cx + x, cy + y, 0])
                d = 0.22 * np.array([np.cos(a), np.sin(a), 0])
                g.add(Arrow(p - d, p + d, buff=0, color=FIELD, stroke_width=4, max_tip_length_to_length_ratio=0.35,
                            stroke_opacity=b, fill_opacity=b))
        return g
    return always_redraw(draw), link_on


class Main(MovingCameraScene):
    def construct(self):
        frame = self.camera.frame
        quads = [Quad(i) for i in range(4)]
        for q in quads:
            self.add(q.lt)

        top = Text("粒子圖像的四次碰壁", font=FONT, font_size=40, color=TEXT).move_to(UP * 3.42)
        final = Text("場論：唯一在每個層面都自洽的框架", font=FONT, font_size=40, color=FIELD).move_to(UP * 3.42)

        minis = [ripples(quads[0]), pairs(quads[1]), unify(quads[2])]
        ls, link_on = local_sym(quads[3])
        minis.append(ls)

        self.play(LaggedStart(*[FadeIn(q.static()) for q in quads], lag_ratio=0.25), run_time=2)
        self.add(*minis)
        self.play(FadeIn(top), run_time=1.0)

        def focus(i, prev=None):
            q = quads[i]
            anims = [frame.animate.set(width=8.6).move_to(q.c + DOWN * 0.35), q.b.animate.set_value(1)]
            if prev is not None:
                anims.append(quads[prev].b.animate.set_value(DIM))
            else:
                anims.append(FadeOut(top))
            self.play(*anims, run_time=1.6)
            q.speed.set_value(1)

        for i in range(4):
            focus(i, i - 1 if i else None)
            self.wait(2.5)
            self.play(quads[i].note_on.animate.set_value(1), run_time=1.0)
            if i == 3:
                self.wait(1.5)
                self.play(link_on.animate.set_value(1), run_time=2.0)
                self.wait(5.4)
            else:
                self.wait(8.9)

        # zoom back out to see all four at once
        self.play(frame.animate.set(width=config.frame_width).move_to(ORIGIN),
                  *[q.b.animate.set_value(1) for q in quads], run_time=2.2)
        self.play(FadeIn(final, shift=DOWN * 0.2), run_time=1.6)
        glow = SurroundingRectangle(VGroup(*[q.box for q in quads]), color=FIELD, buff=0.12, corner_radius=0.25,
                                    stroke_width=4)
        self.play(Create(glow), run_time=1.5)
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        glow.add_updater(lambda m: m.set_stroke(opacity=0.5 + 0.5 * np.sin(2.5 * t.get_value())))
        self.add(t)
        self.wait(5.5)
