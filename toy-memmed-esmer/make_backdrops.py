#!/usr/bin/env python3
"""Məmməd & Əsmər — toy səhnəsi üçün LED arxa fon videoları (1920x1080, 15 s, qüsursuz loop).

İstifadə:
  python3 make_backdrops.py --list
  python3 make_backdrops.py --preview [id ...]   # hər variantdan bir kadr (PNG)
  python3 make_backdrops.py [id ...]             # videoları render et
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'fonts')
OUT = os.path.join(HERE, 'videolar')
W, H = 1920, 1080
FPS, DUR = 30, 15
N = FPS * DUR
LS = 3
LW, LH = W // LS, H // LS
TAU = 2 * math.pi

NAMEF = {'AB': 'AlexBrush-Regular.ttf', 'GV': 'GreatVibes-Regular.ttf', 'AL': 'Allura-Regular.ttf'}
AMPF = 'Parisienne-Regular.ttf'


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), int(size))
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def C(*v):
    return np.array(v, np.float32) / 255.0


# --------------------------------------------------------------------- palettes
PAL = {
    'blush': dict(bg_in=C(252, 237, 235), bg_out=C(228, 180, 186), bloom=C(255, 250, 248), bloom_k=0.10,
                  name_top=C(132, 88, 64), name_bot=C(72, 42, 32), metal=0.25,
                  sub=C(128, 86, 68), orn=C(186, 142, 98),
                  shadow=(C(110, 50, 55), 0.22), glow=(C(255, 252, 250), 0.35),
                  shimmer=C(255, 238, 205), sparkle=C(255, 222, 180), spark_k=0.9,
                  bokeh=(C(255, 255, 255), 0.30), ribbons=(C(255, 247, 245), 0.20), beams=None,
                  petals=[C(255, 249, 242), C(246, 210, 212), C(236, 190, 196)], glitter=None),
    'night': dict(bg_in=C(62, 28, 40), bg_out=C(9, 5, 7), bloom=C(120, 50, 70), bloom_k=0.20,
                  name_top=C(255, 242, 218), name_bot=C(212, 164, 102), metal=0.35,
                  sub=C(236, 200, 156), orn=C(212, 170, 110),
                  shadow=None, glow=(C(255, 190, 140), 0.55),
                  shimmer=C(255, 255, 245), sparkle=C(255, 224, 175), spark_k=1.0,
                  bokeh=(C(255, 196, 140), 0.45), ribbons=None, beams=(C(255, 238, 222), 0.20),
                  petals=None, glitter=C(255, 214, 150)),
    'rose': dict(bg_in=C(238, 132, 160), bg_out=C(126, 28, 64), bloom=C(255, 190, 205), bloom_k=0.20,
                 name_top=C(255, 252, 252), name_bot=C(255, 222, 232), metal=0.0,
                 sub=C(255, 238, 242), orn=C(255, 230, 236),
                 shadow=(C(100, 10, 45), 0.30), glow=(C(255, 222, 232), 0.55),
                 shimmer=C(255, 255, 255), sparkle=C(255, 242, 246), spark_k=1.0,
                 bokeh=(C(255, 222, 232), 0.40), ribbons=(C(255, 205, 220), 0.40), beams=(C(255, 240, 245), 0.10),
                 petals=[C(255, 238, 242), C(255, 250, 250)], glitter=None),
    'champagne': dict(bg_in=C(253, 248, 242), bg_out=C(230, 210, 190), bloom=C(255, 255, 252), bloom_k=0.10,
                      name_top=C(200, 156, 98), name_bot=C(128, 88, 50), metal=0.35,
                      sub=C(146, 108, 72), orn=C(198, 156, 102),
                      shadow=(C(110, 72, 40), 0.20), glow=(C(255, 253, 248), 0.40),
                      shimmer=C(255, 244, 214), sparkle=C(226, 184, 116), spark_k=0.9,
                      bokeh=(C(255, 255, 255), 0.40), ribbons=(C(255, 252, 246), 0.20), beams=None,
                      petals=[C(248, 214, 214), C(255, 240, 236), C(240, 198, 204)], glitter=None),
    'mauve': dict(bg_in=C(190, 128, 138), bg_out=C(112, 56, 72), bloom=C(255, 220, 220), bloom_k=0.07,
                  name_top=C(255, 251, 246), name_bot=C(250, 228, 212), metal=0.0,
                  sub=C(255, 244, 236), orn=C(255, 234, 212),
                  shadow=(C(70, 20, 34), 0.45), glow=(C(255, 238, 232), 0.18),
                  shimmer=C(255, 255, 255), sparkle=C(255, 240, 222), spark_k=1.0,
                  bokeh=(C(255, 240, 236), 0.35), ribbons=(C(255, 220, 222), 0.22), beams=None,
                  petals=[C(255, 247, 241), C(250, 226, 220)], glitter=None),
}

# --------------------------------------------------------------------- variants
AZ = ('Məmməd', 'Əsmər')
EN = ('Mammad', 'Asmar')
VARIANTS = [
    # Azərbaycanca
    dict(id='az1', group='AZ', style='blush', layout='stack', font='AB', names=AZ),
    dict(id='az2', group='AZ', style='night', layout='stack', font='GV', names=AZ),
    dict(id='az3', group='AZ', style='rose', layout='stack', font='AL', names=AZ),
    dict(id='az4', group='AZ', style='champagne', layout='stack', font='GV', names=AZ),
    dict(id='az5', group='AZ', style='mauve', layout='stack', font='AB', names=AZ),
    dict(id='az6', group='AZ', style='night', layout='stack', font='AB', names=AZ),
    # English
    dict(id='en1', group='EN', style='blush', layout='stack', font='GV', names=EN),
    dict(id='en2', group='EN', style='night', layout='stack', font='AB', names=EN),
    dict(id='en3', group='EN', style='rose', layout='stack', font='GV', names=EN),
    dict(id='en4', group='EN', style='champagne', layout='stack', font='AL', names=EN),
    dict(id='en5', group='EN', style='mauve', layout='stack', font='AL', names=EN),
    dict(id='en6', group='EN', style='night', layout='stack', font='GV', names=EN),
    # Monoqram (baş hərflər)
    dict(id='mono1', group='MONO', style='blush', layout='mono', font='AB', letters=('M', 'Ə')),
    dict(id='mono2', group='MONO', style='night', layout='mono', font='GV', letters=('M', 'Ə')),
    dict(id='mono3', group='MONO', style='rose', layout='mono', font='AL', letters=('M', 'Ə')),
    dict(id='mono4', group='MONO', style='champagne', layout='mono', font='GV', letters=('M', 'A')),
    dict(id='mono5', group='MONO', style='mauve', layout='mono', font='AB', letters=('M', 'A')),
    dict(id='mono6', group='MONO', style='night', layout='mono', font='AL', letters=('M', 'A')),
]

FILENAMES = {'AZ': 'Azerbaycanca', 'EN': 'English', 'MONO': 'Monoqram'}


def out_name(v):
    return f"{v['id']}_{FILENAMES[v['group']]}_{v['style']}.mp4"


# --------------------------------------------------------------------- helpers
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def tracked(draw, text, fnt, cx, baseline, tracking, fill=255):
    """Draw spaced capitals centred at cx."""
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, baseline), ch, font=fnt, fill=fill, anchor='ls')
        x += w + tracking
    return total


def runs_width(runs):
    return sum(f.getlength(t) for t, f in runs)


STROKE = {'AB': 2, 'GV': 1, 'AL': 2}


def draw_runs(draw, runs, cx, baseline, fill=255, stroke=0):
    x = cx - runs_width(runs) / 2
    for t, f in runs:
        draw.text((x, baseline), t, font=f, fill=fill, anchor='ls', stroke_width=stroke if t.strip() != '&' else max(0, stroke - 1), stroke_fill=fill)
        x += f.getlength(t)


def mask_from(img):
    return np.asarray(img, np.float32) / 255.0


# --------------------------------------------------------------------- text layer
def build_text_layer(v, pal):
    """Returns dict with rgb (H,W,3), alpha (H,W), glow (H,W), shadow (H,W), bbox."""
    SS = 4  # supersampling for ornaments
    name_m = Image.new('L', (W, H), 0)
    sub_m = Image.new('L', (W, H), 0)
    dn, ds = ImageDraw.Draw(name_m), ImageDraw.Draw(sub_m)
    orn_big = Image.new('L', (W * SS, H * SS), 0)
    do = ImageDraw.Draw(orn_big)
    cx = W / 2
    fname = NAMEF[v['font']]
    serif_w = 520 if pal is PAL['blush'] or pal is PAL['champagne'] else 500
    line_fade = []  # (y, half_length) for fading divider lines

    def divider(y, L):
        y4 = y * SS
        do.line([(cx * SS - L * SS, y4), (cx * SS - 26 * SS, y4)], fill=255, width=int(1.6 * SS))
        do.line([(cx * SS + 26 * SS, y4), (cx * SS + L * SS, y4)], fill=255, width=int(1.6 * SS))
        d = 11 * SS
        do.polygon([(cx * SS, y4 - d), (cx * SS + d * 0.7, y4), (cx * SS, y4 + d), (cx * SS - d * 0.7, y4)], fill=255)
        for s in (-1, 1):
            r = 3.2 * SS
            px = cx * SS + s * 17 * SS
            do.ellipse([px - r, y4 - r, px + r, y4 + r], fill=255)
        line_fade.append((y, L))

    if v['layout'] in ('line', 'stack'):
        n1, n2 = v['names']
        if v['layout'] == 'line':
            size = 230
            while True:
                nf, af = font(fname, size), font(AMPF, size * 0.78)
                runs = [(n1, nf), ('  &  ', af), (n2, nf)]
                if runs_width(runs) <= 1480:
                    break
                size -= 6
            has_top, has_sub = 'top' in v, 'sub' in v
            base = 590 if has_top else (545 if has_sub else 590)
            if has_top:
                tf = font('Cormorant.ttf', 46, serif_w)
                tracked(ds, v['top'], tf, cx, 330, 14)
                divider(372, 230)
            draw_runs(dn, runs, cx, base, stroke=STROKE[v['font']])
            if has_sub:
                divider(base + 95, 300)
                sf = font('Cormorant.ttf', 50, serif_w)
                tracked(ds, v['sub'], sf, cx, base + 180, 12)
        else:  # stack
            size = 250
            nf, af = font(fname, size), font(AMPF, 135)
            # like the stage examples: name / & / name, staggered, & never touching letters
            w1, w2 = runs_width([(n1, nf)]), runs_width([(n2, nf)])
            draw_runs(dn, [(n1, nf)], cx - 110, 455, stroke=STROKE[v['font']])
            x2 = cx + 150
            draw_runs(dn, [(n2, nf)], x2, 775, stroke=STROKE[v['font']])
            ax = x2 - w2 / 2 - af.getlength('&') / 2 - 10
            draw_runs(dn, [('&', af)], ax, 610)
    else:  # mono
        cy, R = 505, 330
        lf, af = font(fname, 430), font(AMPF, 200)
        a, b = v['letters']
        runs = [(a, lf), (' & ', af), (b, lf)]
        draw_runs(dn, runs, cx, 690, stroke=STROKE[v['font']])
        for rr, wd in ():
            do.ellipse([(cx - rr) * SS, (cy - rr) * SS, (cx + rr) * SS, (cy + rr) * SS], outline=255, width=int(wd * SS))
        # dotted ring + four diamonds
        for k in range(0):
            ang = TAU * k / 120
            if min(abs((ang % (TAU / 4)) - 0), abs((ang % (TAU / 4)) - TAU / 4)) < 0.09:
                continue
            r = (1.6 if k % 2 else 2.6) * SS
            px, py = (cx + (R + 16) * math.cos(ang)) * SS, (cy + (R + 16) * math.sin(ang)) * SS
            do.ellipse([px - r, py - r, px + r, py + r], fill=255)
        for k in range(0):
            ang = TAU * k / 4
            px, py = (cx + (R + 16) * math.cos(ang)) * SS, (cy + (R + 16) * math.sin(ang)) * SS
            d = 12 * SS
            do.polygon([(px, py - d), (px + d * 0.7, py), (px, py + d), (px - d * 0.7, py)], fill=255)
        if 'sub' in v:
            sf = font('Cormorant.ttf', 50, serif_w)
            tracked(ds, v['sub'], sf, cx, 960, 14)

    orn = mask_from(orn_big.resize((W, H), Image.LANCZOS))
    if line_fade:
        xs = np.abs(np.arange(W, dtype=np.float32) - cx)
        fade = np.ones((H, W), np.float32)
        for y, L in line_fade:
            rows = slice(max(0, int(y) - 16), min(H, int(y) + 17))
            fade[rows] = np.clip(1 - xs / L, 0, 1)[None, :] ** 0.7 + (xs < 40)[None, :]
        orn = orn * np.clip(fade, 0, 1)

    nm, sm = mask_from(name_m), mask_from(sub_m)
    alpha = np.clip(np.maximum(np.maximum(nm, sm), orn), 0, 1)

    # name gradient (vertical, metallic band)
    ys = np.where(nm.max(1) > 0)[0]
    top, bot = (ys.min(), ys.max()) if len(ys) else (0, H)
    if v['layout'] == 'stack':
        g_rows = np.zeros(H, np.float32)
        # per-line gradient so each line has its own metal sheen
        g_rows = ((np.arange(H) - 280) % 240) / 240.0
    else:
        g_rows = np.clip((np.arange(H) - top) / max(1, bot - top), 0, 1)
    g = g_rows[:, None, None].astype(np.float32)
    name_col = pal['name_top'] * (1 - g) + pal['name_bot'] * g
    if pal['metal']:
        band = np.exp(-((g - 0.42) / 0.10) ** 2)
        name_col = name_col + pal['metal'] * band * (1 - name_col)
    name_col = np.broadcast_to(name_col, (H, W, 3))

    rgb = np.zeros((H, W, 3), np.float32)
    acc = np.zeros((H, W), np.float32)
    for m, col in ((orn, pal['orn']), (sm, pal['sub']), (nm, name_col)):
        rgb = rgb * (1 - m[..., None]) + (np.broadcast_to(col, (H, W, 3))) * m[..., None]
        acc = acc + m * (1 - acc)
    rgb = rgb / np.maximum(acc[..., None], 1e-4)

    a_img = Image.fromarray((alpha * 255).astype(np.uint8))
    glow = mask_from(a_img.filter(ImageFilter.GaussianBlur(26))) * 1.6
    glow2 = mask_from(a_img.filter(ImageFilter.GaussianBlur(70))) * 1.2
    glow = np.clip(glow * 0.6 + glow2 * 0.6, 0, 1)
    shadow = mask_from(a_img.filter(ImageFilter.GaussianBlur(7)))
    shadow = np.roll(shadow, 5, axis=0)

    ys, xs = np.where(glow > 0.004)
    y0, y1 = max(0, ys.min() - 4), min(H, ys.max() + 5)
    x0, x1 = max(0, xs.min() - 4), min(W, xs.max() + 5)
    sl = (slice(y0, y1), slice(x0, x1))
    # shimmer coordinate (diagonal) over the text bbox
    tys, txs = np.where(alpha > 0.02)
    ty0, ty1, tx0, tx1 = tys.min(), tys.max(), txs.min(), txs.max()
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    u = ((xx - tx0) + 0.45 * (yy - ty0)) / ((tx1 - tx0) + 0.45 * (ty1 - ty0))
    ring = None
    if False:
        ang = np.arctan2(yy - 505, xx - cx)
        ring = dict(ang=ang, mask=orn[sl].copy())
    return dict(rgb=rgb[sl].copy(), alpha=alpha[sl].copy(), glow=glow[sl].copy(), shadow=shadow[sl].copy(),
                sl=sl, u=u, ring=ring)


# --------------------------------------------------------------------- sprites
def star_sprite(s):
    r = np.arange(-s, s + 1, dtype=np.float32)
    y, x = np.meshgrid(r, r, indexing='ij')
    d = np.sqrt(x * x + y * y)
    core = np.exp(-(d / (0.10 * s)) ** 2)
    halo = np.exp(-(d / (0.35 * s)) ** 2) * 0.25
    rays = (np.exp(-(np.abs(y) / (0.025 * s + 0.5)) ** 2) * np.exp(-(np.abs(x) / (0.75 * s)) ** 1.5) +
            np.exp(-(np.abs(x) / (0.025 * s + 0.5)) ** 2) * np.exp(-(np.abs(y) / (0.75 * s)) ** 1.5))
    xd, yd = (x + y) / 1.414, (x - y) / 1.414
    rays2 = (np.exp(-(np.abs(yd) / (0.02 * s + 0.5)) ** 2) * np.exp(-(np.abs(xd) / (0.35 * s)) ** 1.5) +
             np.exp(-(np.abs(xd) / (0.02 * s + 0.5)) ** 2) * np.exp(-(np.abs(yd) / (0.35 * s)) ** 1.5)) * 0.4
    return np.clip(core + halo + rays + rays2, 0, 1.5)


def dot_sprite(s):
    r = np.arange(-s, s + 1, dtype=np.float32)
    y, x = np.meshgrid(r, r, indexing='ij')
    d = np.sqrt(x * x + y * y)
    return np.exp(-(d / (0.35 * s)) ** 2)


def petal_sprites(size, nrot=32, nsq=5):
    """Returns sprites[rot][sq] -> (alpha, shade) arrays."""
    S4 = size * 4
    base = Image.new('L', (S4 * 2, S4 * 2), 0)
    d = ImageDraw.Draw(base)
    pts = []
    for k in range(100):
        t = TAU * k / 100
        rx = math.cos(t)
        ry = math.sin(t) * (0.62 + 0.25 * math.cos(t)) * (1 - 0.12 * abs(math.sin(2 * t)))
        pts.append((S4 + rx * S4 * 0.95, S4 + ry * S4 * 0.95))
    d.polygon(pts, fill=255)
    shade = Image.linear_gradient('L').rotate(90).resize((S4 * 2, S4 * 2))
    out = []
    for i in range(nrot):
        row = []
        for j in range(nsq):
            sq = 0.25 + 0.75 * j / (nsq - 1)
            a = base.resize((S4 * 2, max(2, int(S4 * 2 * sq))), Image.LANCZOS)
            sh = shade.resize(a.size)
            pad = Image.new('L', (S4 * 2, S4 * 2), 0)
            pad2 = Image.new('L', (S4 * 2, S4 * 2), 0)
            pad.paste(a, (0, (S4 * 2 - a.size[1]) // 2))
            pad2.paste(sh, (0, (S4 * 2 - a.size[1]) // 2))
            ang = 360 * i / nrot
            a2 = pad.rotate(ang, Image.BICUBIC).resize((size * 2, size * 2), Image.LANCZOS)
            s2 = pad2.rotate(ang, Image.BICUBIC).resize((size * 2, size * 2), Image.LANCZOS)
            row.append((mask_from(a2), 0.82 + 0.18 * mask_from(s2)))
        out.append(row)
    return out


def blit_add(frame, spr, x, y, col, k):
    h, w = spr.shape
    x0, y0 = int(x) - w // 2, int(y) - h // 2
    sx0, sy0 = max(0, -x0), max(0, -y0)
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    s = spr[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0]
    frame[fy0:fy1, fx0:fx1] += s[..., None] * (col * k)


def blit_over(frame, a, sh, x, y, col, k):
    h, w = a.shape
    x0, y0 = int(x) - w // 2, int(y) - h // 2
    sx0, sy0 = max(0, -x0), max(0, -y0)
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    al = a[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0][..., None] * k
    shd = sh[sy0:sy0 + fy1 - fy0, sx0:sx0 + fx1 - fx0][..., None]
    reg = frame[fy0:fy1, fx0:fx1]
    frame[fy0:fy1, fx0:fx1] = reg * (1 - al) + (col * shd) * al


# --------------------------------------------------------------------- scene
class Scene:
    def __init__(self, v):
        self.v = v
        self.pal = pal = PAL[v['style']]
        rng = np.random.default_rng(sum(ord(ch) * 31 ** k for k, ch in enumerate(v['id'])) % (2 ** 32))
        self.rng = rng
        # static background
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H * 0.46) / (H * 0.78)) ** 2)
        s = smoothstep(0.0, 1.15, d)[..., None]
        self.bg = pal['bg_in'] * (1 - s) + pal['bg_out'] * s
        self.bg = self.bg.astype(np.float32)
        ly, lx = np.mgrid[0:LH, 0:LW].astype(np.float32)
        self.lx, self.ly = lx, ly
        self.bloom = np.exp(-(((lx - LW / 2) / (LW * 0.30)) ** 2 + ((ly - LH * 0.48) / (LH * 0.30)) ** 2))
        # text
        self.txt = build_text_layer(v, pal)
        # bokeh (low-res)
        nb = 46
        self.bk = dict(x=rng.uniform(0, LW, nb), y=rng.uniform(0, LH + 60, nb), r=rng.uniform(3, 15, nb),
                       ph=rng.uniform(0, 1, nb), sw=rng.uniform(4, 16, nb), m=rng.choice([1, 1, 2], nb),
                       tw=rng.choice([1, 2, 3], nb))
        # sparkles
        ns = 55
        self.sp_sizes = [10, 16, 24, 34]
        self.sp_spr = [star_sprite(s) for s in self.sp_sizes]
        self.sp = dict(x=rng.uniform(40, W - 40, ns), y=rng.uniform(40, H - 40, ns),
                       si=rng.choice(len(self.sp_sizes), ns, p=[0.4, 0.3, 0.2, 0.1]),
                       ph=rng.uniform(0, 1, ns), f=rng.choice([1, 2, 3], ns))
        # petals
        self.petals = None
        if pal['petals']:
            sizes = [22, 30, 40]
            self.pet_spr = [petal_sprites(s) for s in sizes]
            npet = 22
            self.pet = dict(x=rng.uniform(0, W, npet), y=rng.uniform(0, 1, npet), si=rng.choice(3, npet),
                            m=rng.choice([1, 1, 2], npet), sw=rng.uniform(30, 90, npet), ph=rng.uniform(0, 1, npet),
                            rot=rng.choice([-2, -1, 1, 2], npet), r0=rng.integers(0, 32, npet),
                            fl=rng.choice([1, 2, 3], npet), ci=rng.integers(0, len(pal['petals']), npet),
                            front=np.zeros(npet, bool))
            self.petals = True
        self.gl = None
        if pal['glitter'] is not None:
            ng = 90
            self.gl_spr = [dot_sprite(s) for s in (3, 4, 6)]
            self.gl = dict(x=rng.uniform(0, W, ng), y=rng.uniform(0, 1, ng), si=rng.choice(3, ng),
                           m=rng.choice([1, 2], ng), sw=rng.uniform(10, 40, ng), ph=rng.uniform(0, 1, ng),
                           tw=rng.choice([2, 3, 4], ng))
        self.noise = [rng.uniform(-0.5, 0.5, (H, W, 1)).astype(np.float32) / 255 * 1.6 for _ in range(4)]

    # low-res animated light
    def lowres(self, p):
        pal, lx, ly = self.pal, self.lx, self.ly
        acc = np.zeros((LH, LW, 3), np.float32)
        acc += self.bloom[..., None] * pal['bloom'] * pal['bloom_k'] * (0.85 + 0.15 * math.sin(TAU * p * 2))
        if pal['ribbons']:
            col, k = pal['ribbons']
            xr = lx[0]
            for i, (yb, amp, w) in enumerate(((0.80, 0.07, 0.050), (0.90, 0.05, 0.065), (0.14, 0.05, 0.045))):
                yc = (LH * yb + LH * amp * np.sin(TAU * (xr / LW * 0.8 + i * 0.37) + TAU * p) +
                      LH * 0.03 * np.sin(TAU * (xr / LW * 1.6 + i * 0.11) - TAU * 2 * p) -
                      (0.10 if i < 2 else -0.06) * (xr - LW / 2))
                ww = LH * w * (1 + 0.35 * np.sin(TAU * (xr / LW * 1.1 + i * 0.2) + TAU * p))
                dy = (ly - yc[None, :]) / ww[None, :]
                body = np.exp(-dy ** 2) * 0.45
                edge = np.exp(-((dy - 0.55) / 0.12) ** 2) * 0.9
                trav = 0.45 + 0.55 * (0.5 + 0.5 * np.sin(TAU * (xr / LW * 0.6 - p) + i))
                acc += ((body + edge) * trav[None, :])[..., None] * col * k
        if pal['beams']:
            col, k = pal['beams']
            for i in range(7):
                sx = LW * (0.08 + 0.84 * i / 6)
                base = (i - 3) * 0.11
                a = base + 0.13 * math.sin(TAU * p * (1 + i % 2) + i * 1.3)
                dx, dy = lx - sx, ly + 6
                along = dx * math.sin(a) + dy * math.cos(a)
                perp = dx * math.cos(a) - dy * math.sin(a)
                inten = np.exp(-(perp / (3 + np.maximum(along, 0) * 0.085)) ** 2) * np.exp(-along / (LH * 1.2)) * (along > 0)
                inten *= 0.75 + 0.25 * math.sin(TAU * p * 2 + i)
                acc += inten[..., None] * col * k
                # source glow
                acc += (np.exp(-((dx / 5) ** 2 + ((ly - 2) / 5) ** 2)) * 1.2)[..., None] * col * k * 2
        # bokeh
        col, k = pal['bokeh']
        b = self.bk
        span = LH + 60
        for i in range(len(b['x'])):
            yy = (b['y'][i] - p * b['m'][i] * span) % span - 30
            xx = b['x'][i] + b['sw'][i] * math.sin(TAU * (p + b['ph'][i]))
            r = b['r'][i]
            x0, x1 = int(max(0, xx - r - 2)), int(min(LW, xx + r + 3))
            y0, y1 = int(max(0, yy - r - 2)), int(min(LH, yy + r + 3))
            if x1 <= x0 or y1 <= y0:
                continue
            d = np.sqrt((lx[y0:y1, x0:x1] - xx) ** 2 + (ly[y0:y1, x0:x1] - yy) ** 2)
            disc = np.clip((r - d) / 1.3, 0, 1)
            rim = np.exp(-((d - r * 0.88) / (r * 0.12 + 0.4)) ** 2) * 0.5
            tw = 0.55 + 0.45 * math.sin(TAU * (p * b['tw'][i] + b['ph'][i]))
            acc[y0:y1, x0:x1] += ((disc * 0.35 + rim * disc.clip(0.2)) * tw)[..., None] * col * k
        return acc

    def upscale(self, lo):
        out = np.empty((H, W, 3), np.float32)
        for c in range(3):
            out[..., c] = np.asarray(Image.fromarray(lo[..., c], 'F').resize((W, H), Image.BILINEAR))
        return out

    def render(self, i):
        p = i / N
        pal = self.pal
        f = self.bg + self.upscale(self.lowres(p))
        if not pal['shadow']:
            pass
        # petals behind text
        if self.petals:
            self.draw_petals(f, p, front=False)
        if self.gl:
            g = self.gl
            span = H + 40
            for j in range(len(g['x'])):
                yy = (g['y'][j] * span + p * g['m'][j] * span) % span - 20
                xx = g['x'][j] + g['sw'][j] * math.sin(TAU * (p * 2 + g['ph'][j]))
                tw = max(0.0, math.sin(TAU * (p * g['tw'][j] + g['ph'][j]))) ** 2
                blit_add(f, self.gl_spr[g['si'][j]], xx, yy, pal['glitter'], 0.35 + 0.65 * tw)
        # text
        t = self.txt
        sl = t['sl']
        reg = f[sl]
        breathe = 0.85 + 0.15 * math.sin(TAU * p * 2)
        gcol, gk = pal['glow']
        ga = (t['glow'] * gk * breathe)[..., None]
        reg = reg * (1 - ga) + gcol * ga if pal is not PAL['night'] else reg + gcol * ga * 0.55
        if pal['shadow']:
            scol, sk = pal['shadow']
            sa = (t['shadow'] * sk)[..., None]
            reg = reg * (1 - sa) + scol * sa
        rgb = t['rgb']
        # shimmer sweep, twice per loop
        q = (p * 2) % 1.0
        if q < 0.45:
            pos = -0.25 + 1.5 * (q / 0.45)
            band = np.exp(-((t['u'] - pos) / 0.045) ** 2)[..., None]
            rgb = rgb + band * (pal['shimmer'] - rgb) * 0.85
        if t['ring'] is not None:
            angd = np.angle(np.exp(1j * (t['ring']['ang'] - (TAU * p - math.pi / 2))))
            glint = (np.exp(-(angd / 0.35) ** 2) * t['ring']['mask'])[..., None]
            rgb = rgb + glint * (pal['shimmer'] - rgb) * 0.95
        a = t['alpha'][..., None]
        reg = reg * (1 - a) + rgb * a
        f[sl] = reg
        if self.petals:
            self.draw_petals(f, p, front=True)
        # sparkles (additive)
        s = self.sp
        for j in range(len(s['x'])):
            tw = max(0.0, math.sin(TAU * (p * s['f'][j] + s['ph'][j]))) ** 4
            if tw < 0.01:
                continue
            blit_add(f, self.sp_spr[s['si'][j]], s['x'][j], s['y'][j], pal['sparkle'], tw * pal['spark_k'])
        f += self.noise[i % 4]
        return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)

    def draw_petals(self, f, p, front):
        pe, pal = self.pet, self.pal
        span = H + 160
        for j in range(len(pe['x'])):
            if bool(pe['front'][j]) != front:
                continue
            yy = (pe['y'][j] * span + p * pe['m'][j] * span) % span - 80
            xx = (pe['x'][j] + pe['sw'][j] * math.sin(TAU * (p * 2 + pe['ph'][j])) + p * 0) % (W + 0)
            ri = int(pe['r0'][j] + p * pe['rot'][j] * 32) % 32
            sq = abs(math.cos(TAU * (p * pe['fl'][j] + pe['ph'][j])))
            qi = min(4, int(sq * 4.999))
            a, sh = self.pet_spr[pe['si'][j]][ri][qi]
            col = pal['petals'][pe['ci'][j]]
            blit_over(f, a, sh, xx, yy, col, 0.92 if front else 0.75)


def render_video(v):
    sc = Scene(v)
    path = os.path.join(OUT, out_name(v))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
           '-profile:v', 'high', '-movflags', '+faststart', path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        proc.stdin.write(sc.render(i).tobytes())
    proc.stdin.close()
    proc.wait()
    print('OK', path, flush=True)


def preview(v, i=N // 8):
    sc = Scene(v)
    os.makedirs(os.path.join(HERE, 'preview'), exist_ok=True)
    pth = os.path.join(HERE, 'preview', v['id'] + '.jpg')
    Image.fromarray(sc.render(i)).save(pth, quality=92)
    print('preview', pth, flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]
    os.makedirs(OUT, exist_ok=True)
    if '--list' in args:
        for v in VARIANTS:
            print(v['id'], out_name(v))
        sys.exit()
    pv = '--preview' in args
    ids = [a for a in args if not a.startswith('--')]
    sel = [v for v in VARIANTS if not ids or v['id'] in ids]
    for v in sel:
        (preview if pv else render_video)(v)
