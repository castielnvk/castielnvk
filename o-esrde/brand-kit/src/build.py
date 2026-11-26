#!/usr/bin/env python3
"""O Əsrdə brand kit generator (direction 2 · Saat).

Writes outlined SVGs (no font needed to open them) plus a render job list.
Run:  python3 build.py && node render.js && bash outro.sh
"""
import json, math, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
FONTS = os.path.join(HERE, "fonts")
OUT_SVG = os.path.join(KIT, "svg")
FRAMES = os.path.join(HERE, "_frames")
for d in (OUT_SVG, FRAMES):
    os.makedirs(d, exist_ok=True)

INK, WHITE = "#111418", "#FFFFFF"
HOURKEYS = [(0, "#22304F"), (5, "#6E5E95"), (6, "#F1A78A"), (7, "#F4CB62"), (10, "#E9E39A"),
            (13, "#9CCBE6"), (16, "#F0B35E"), (19, "#D9695A"), (21, "#4A4F86"), (24, "#22304F")]


def rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def hexc(c): return "#" + "".join(f"{round(v):02X}" for v in c)
def mix(a, b, t): return hexc([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


def hour_color(h):
    for (a, ca), (b, cb) in zip(HOURKEYS, HOURKEYS[1:]):
        if a <= h <= b:
            return mix(ca, cb, (h - a) / (b - a))
    return HOURKEYS[0][1]


def lum(h):
    r, g, b = [v / 255 for v in rgb(h)]
    return .2126 * r + .7152 * g + .0722 * b


def on_color(h): return INK if lum(h) > .42 else WHITE


class Face:
    def __init__(self, fn):
        self.f = TTFont(os.path.join(FONTS, fn))
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]
        self.cap = self.f["OS/2"].sCapHeight / self.upm

    def width(self, txt, size, ls=0):
        s = size / self.upm
        return sum(self.hmtx[self.cmap[ord(c)]][0] * s for c in txt) + ls * size * (len(txt) - 1)

    def path(self, txt, size, x, y, ls=0):
        """Outlined text, baseline at y. ls = letter spacing in em."""
        s = size / self.upm
        pen = SVGPathPen(self.gs)
        cx = x
        for c in txt:
            g = self.cmap[ord(c)]
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cx += self.hmtx[g][0] * s + ls * size
        return pen.getCommands()


BS9 = Face("Big_Shoulders_Display_wght_900.ttf")
BS8 = Face("Big_Shoulders_Display_wght_800.ttf")
JB = Face("JetBrains_Mono_wght_600.ttf")


def svg(w, h, body, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{b}{body}</svg>')


def text(face, txt, size, x, y, fill, ls=0, anchor="start", opacity=1):
    if anchor == "middle":
        x -= face.width(txt, size, ls) / 2
    elif anchor == "end":
        x -= face.width(txt, size, ls)
    op = f' opacity="{opacity:.3f}"' if opacity < 1 else ""
    return f'<path d="{face.path(txt, size, x, y, ls)}" fill="{fill}"{op}/>'


# ---------- wordmark: "O ƏSRDƏ" + time stamp box ----------
def wordmark(F, x, y, color, stamp="06:00", hc="#F1A78A", stamp_scale=1.0):
    """Cap-top at y. Returns (svg, width, height)."""
    cap = BS9.cap * F
    word = "O ƏSRDƏ"
    tw = BS9.width(word, F, .005)
    out = text(BS9, word, F, x, y + cap, color, .005)
    w = tw
    if stamp:
        s = .31 * F
        dcap = BS8.cap * s
        pv, ph = .2 * s, .2 * s
        dw = BS8.width(stamp, s, .02)
        bx, bw, bh = x + tw + .085 * F, dw + 2 * ph, dcap + 2 * pv
        k = stamp_scale
        cxm, cym = bx + bw / 2, y + bh / 2
        out += (f'<g transform="translate({cxm:.2f} {cym:.2f}) scale({k:.4f}) translate({-cxm:.2f} {-cym:.2f})">'
                f'<rect x="{bx:.2f}" y="{y:.2f}" width="{bw:.2f}" height="{bh:.2f}" fill="{hc}"/>'
                + text(BS8, stamp, s, bx + ph, y + pv + dcap, INK, .02) + "</g>")
        w = bx + bw - x
    return out, w, cap


# ---------- symbol: 24h-dial "O" with an hour hand ----------
def dial(cx, cy, scale, hour=6, color=INK, hand=None):
    """Drawn in the 100-unit design space around (50,50), scaled."""
    hand = hand or color
    rot = (hour - 6) * 15
    return (f'<g transform="translate({cx - 50 * scale:.2f} {cy - 50 * scale:.2f}) scale({scale:.4f})">'
            f'<ellipse cx="50" cy="50" rx="21" ry="32" fill="none" stroke="{color}" stroke-width="11"/>'
            f'<g transform="rotate({rot:.2f} 50 50)"><rect x="49" y="46" width="17" height="8" fill="{hand}"/></g>'
            f'<circle cx="50" cy="50" r="6" fill="{hand}"/></g>')


jobs = []


def save(name, content, w, h, transparent=True, png=True, folder=OUT_SVG, png_dir=None):
    p = os.path.join(folder, name + ".svg")
    with open(p, "w") as f:
        f.write(content)
    if png:
        jobs.append({"svg": p, "png": os.path.join(png_dir or os.path.join(KIT, "png"), name + ".png"),
                     "w": w, "h": h, "transparent": transparent})


# ---------- 1. logos ----------
F = 400
M = 40
for name, col in (("ink", INK), ("white", WHITE)):
    body, w, h = wordmark(F, M, M, col)
    W, H = math.ceil(w + 2 * M), math.ceil(h + 2 * M)
    save(f"logo-wordmark-{name}", svg(W, H, body), W, H)
    body, w, h = wordmark(F, M, M, col, stamp=None)
    W, H = math.ceil(w + 2 * M), math.ceil(h + 2 * M)
    save(f"logo-wordmark-plain-{name}", svg(W, H, body), W, H)

S = 1000
save("symbol-disc", svg(S, S, f'<circle cx="500" cy="500" r="500" fill="{hour_color(6)}"/>' + dial(500, 500, 10, 6, INK)), S, S)
save("symbol-ink", svg(S, S, dial(500, 500, 13, 6, INK)), S, S)
save("symbol-white", svg(S, S, dial(500, 500, 13, 6, WHITE)), S, S)

# 1080x1920 Reel overlays: wordmark upper left, inside mobile-safe margins
for name, col in (("white", WHITE), ("ink", INK)):
    body, w, h = wordmark(118, 72, 150, col)
    save(f"overlay-1080x1920-{name}", svg(1080, 1920, body), 1080, 1920)

# ---------- 2. profile pictures (Instagram + TikTok, 1080x1080, circle-safe) ----------
save("profile-main", svg(1080, 1080, dial(540, 540, 8.6, 6, INK), bg=hour_color(6)), 1080, 1080, transparent=False)
save("profile-alt-ink", svg(1080, 1080, dial(540, 540, 8.6, 6, WHITE, hand=hour_color(6)), bg=INK), 1080, 1080, transparent=False)

# ---------- 3. Instagram highlight covers (1080x1920, content inside the centre circle) ----------
HL = [(6, "BÖLÜMLƏR"), (9, "ƏSRLƏR"), (12, "KADR ARXASI"), (15, "SUALLAR"), (18, "HAQQIMIZDA"), (21, "YENİ")]
for i, (hr, label) in enumerate(HL, 1):
    bg = hour_color(hr + .01)
    fg = on_color(bg)
    body = (text(JB, f"{hr:02d}:00", 52, 540, 640, fg, .04, "middle", .8)
            + dial(540, 880, 5.4, hr, fg)
            + text(BS9, label, 112, 540, 1218, fg, .01, "middle"))
    slug = f"{i:02d}-" + label.lower().replace(" ", "-").translate(str.maketrans("əöüşçğı", "eousçgi")).replace("ç", "c").replace("i̇", "i")
    save(f"highlight-{slug}", svg(1080, 1920, body, bg=bg), 1080, 1920, transparent=False)

# ---------- 4. outro (1080x1920, 30 fps, 5.5 s) ----------
FPS, DUR = 30, 5.5
N = int(FPS * DUR)


def ease(t): return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def clamp(v, a=0., b=1.): return max(a, min(b, v))


def outro_frame(t):
    W_, H_ = 1080, 1920
    band_h = 404
    # phase A: 22:00 -> 24:00 (night) in 2.0 s
    k = ease(clamp((t - .25) / 1.75))
    mins = 22 * 60 + k * 120
    hr_f = mins / 60
    hc = hour_color(min(hr_f, 24))
    shown = int(mins) // 5 * 5 if k < 1 else 24 * 60
    hh, mm = divmod(shown, 60)
    hh %= 24
    fg = on_color(hc)
    o = ""
    o += f'<rect width="{W_}" height="{band_h}" fill="{hc}"/>'
    o += text(BS9, f"{hh:02d}:{mm:02d}", 330, 60, band_h - 44, fg, .005)
    o += dial(940, band_h - 150, 1.35, hr_f, fg)
    # day bar
    x0, x1, gy, gh, gap = 64, 1016, band_h + 26, 17, 5
    sw = (x1 - x0 - gap * 23) / 24
    new_day = k >= 1
    for i in range(24):
        sx = x0 + i * (sw + gap)
        o += f'<rect x="{sx:.2f}" y="{gy}" width="{sw:.2f}" height="{gh}" fill="#FFFFFF" opacity=".28"/>'
        if not new_day:
            if i < int(hr_f):
                o += f'<rect x="{sx:.2f}" y="{gy}" width="{sw:.2f}" height="{gh}" fill="#FFFFFF"/>'
            elif i == int(hr_f):
                o += f'<rect x="{sx:.2f}" y="{gy}" width="{sw * (hr_f % 1):.2f}" height="{gh}" fill="{hc}"/>'
    # flash when the day resets
    fl = clamp(1 - abs(t - 2.05) / .18)
    if fl > 0:
        o += f'<rect width="{W_}" height="{H_}" fill="#FFFFFF" opacity="{.18 * fl:.3f}"/>'
    # phase B: closing line
    for j, ln in enumerate(("Sabah başqa", "əsrdə oyanırsan.")):
        a = ease(clamp((t - 2.35 - j * .14) / .55))
        if a > 0:
            dy = (1 - a) * 60
            o += f'<g transform="translate(0 {dy:.1f})">' + text(BS8, ln, 148, 64, 900 + j * 150, WHITE, .0, opacity=a) + "</g>"
    # phase C: wordmark with next-morning stamp
    a = ease(clamp((t - 3.35) / .5))
    if a > 0:
        pop = 1 + .18 * math.sin(math.pi * clamp((t - 3.75) / .35)) if t > 3.75 else (0.0001 if t < 3.6 else ease(clamp((t - 3.6) / .15)))
        wm, w, h = wordmark(190, 64, 1300, WHITE, hc=hour_color(6), stamp_scale=max(pop, .0001))
        o += f'<g opacity="{a:.3f}">{wm}</g>'
        b = ease(clamp((t - 3.9) / .45))
        o += text(JB, "BİZİ İZLƏYİN", 44, 68, 1560, WHITE, .12, opacity=.7 * b)
    return svg(W_, H_, o, bg=INK)


for f in range(N):
    save(f"outro_{f:04d}", outro_frame(f / FPS), 1080, 1920, transparent=False, folder=FRAMES, png_dir=FRAMES)

with open(os.path.join(HERE, "_jobs.json"), "w") as fh:
    json.dump(jobs, fh)
print(len(jobs), "render jobs")
