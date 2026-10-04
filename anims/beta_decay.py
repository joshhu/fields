import numpy as np
from manim import *

from style import BG, FIELD, PARTICLE, ACCENT, MUTED, TEXT, FONT

DUR = 21.0
T_DECAY = 7.0
X0, X1 = -4.0, 6.9
XN = 1.0
XS = np.linspace(X0, X1, 500)
rng = np.random.default_rng(5)

# name, color, y, symbol
FIELDS = [
    ("中子場", "#B39DDB", 1.6, "n"),
    ("質子場", ACCENT, 0.4, "p"),
    ("電子場", FIELD, -0.8, "e⁻"),
    ("微中子場", "#81C784", -2.0, "nubar"),
]
NOISE = [[(rng.uniform(1.5, 5), rng.uniform(0, 6.3), rng.uniform(1, 3)) for _ in range(5)] for _ in FIELDS]


def nu_bar(font_size, color, sub=False):
    nu = Text("ν", font=FONT, font_size=font_size, color=color)
    bar = Line(LEFT, RIGHT, color=color, stroke_width=font_size / 14).set_width(nu.width * 0.9)
    bar.next_to(nu, UP, buff=font_size / 400)
    g = VGroup(nu, bar)
    if sub:
        g.add(Text("e", font=FONT, font_size=font_size * 0.55, color=color).next_to(nu, DR, buff=0.02).shift(UP * 0.12))
    return g


def ease(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def packet_state(i, t):
    """Return (center_x, amplitude) of the wave packet living on field i."""
    td = t - T_DECAY
    if i == 0:
        return XN, 0.45 * (1 - ease(td / 1.0))
    grow = 0.45 * ease(td / 1.0)
    if td <= 0:
        return XN, 0.0
    speed = {1: -0.07, 2: 0.36, 3: -0.30}[i]
    return XN + speed * td, grow


def field_curve(i, t):
    _, _, y, _ = FIELDS[i]
    h = np.zeros_like(XS)
    for k, ph, w in NOISE[i]:
        h += 0.022 * np.sin(k * XS + ph + w * t)
    c, a = packet_state(i, t)
    k = {0: 6.0, 1: 6.0, 2: 9.0, 3: 11.0}[i]
    h += a * np.exp(-((XS - c) ** 2) / 0.35) * np.cos(k * (XS - c) - 7 * t)
    return np.stack([XS, y + h, np.zeros_like(XS)], 1)


class Main(Scene):
    def construct(self):
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        curves, labels, tags = VGroup(), VGroup(), VGroup()
        for i, (name, col, y, sym) in enumerate(FIELDS):
            c = VMobject().set_points_smoothly(field_curve(i, 0)).set_stroke(col, 3.5)
            c.add_updater(lambda m, i=i: m.set_points_smoothly(field_curve(i, clock.get_value())))
            curves.add(c)
            labels.add(Text(name, font=FONT, font_size=34, color=col).move_to([-5.6, y, 0]))

            def tag_upd(m, i=i, y=y):
                cx, a = packet_state(i, clock.get_value())
                m.move_to([cx, y + 0.62, 0])
                m.set_opacity(float(np.clip(a / 0.45, 0, 1)))

            tag = nu_bar(36, col) if sym == "nubar" else Text(sym, font=FONT, font_size=36, color=col, weight=BOLD)
            tag.add_updater(tag_upd)
            tags.add(tag)

        self.play(LaggedStart(*[Create(c) for c in curves], lag_ratio=0.25),
                  LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.25), run_time=2.5)
        self.add(tags)
        self.wait(2.0)

        eq = VGroup(Text("n  →  p  +  e⁻  +", font=FONT, font_size=56, color=TEXT), nu_bar(56, TEXT, sub=True))
        eq.arrange(RIGHT, buff=0.3).move_to(UP * 3.05)
        self.play(Write(eq), run_time=1.5)
        self.wait(T_DECAY - clock.get_value())

        flash = Circle(radius=0.2, color=PARTICLE, stroke_width=6).move_to([XN, 1.6, 0])
        self.play(flash.animate.scale(5).set_stroke(opacity=0), run_time=1.0)
        self.remove(flash)
        self.wait(2.5)

        cap = Text("不是粒子拆開，而是不同的場被激發", font=FONT, font_size=38, color=PARTICLE)
        cap.move_to(UP * 2.3)
        self.play(FadeIn(cap, shift=UP * 0.2), run_time=1.2)
        self.wait(DUR - clock.get_value() - 0.1)
