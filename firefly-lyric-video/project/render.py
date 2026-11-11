"""Firefly — procedural 9:16 lyric film. numpy + OpenCV + PIL, piped to ffmpeg.
usage: render.py still T[,T..] outdir | render.py all out.mp4 audio
"""
import sys, os, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 24, 56.9
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "CormorantGaramond-SemiBold.ttf")
FONT_I = os.path.join(HERE, "fonts", "CormorantGaramond-MediumItalic.ttf")
rs = np.random.RandomState(7)


def lerp(a, b, u): return a + (b - a) * u
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def sstep(a, b, x):
    u = clamp((x - a) / (b - a)); return u * u * (3 - 2 * u)
def sstep_np(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)
def keys(t, ks):
    """smooth piecewise interpolation through (time, value) keys"""
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1: return lerp(v0, v1, sstep(t0, t1, t))
    return ks[-1][1]
C = lambda r, g, b: np.array([r, g, b], np.float32)

# ------------------------------------------------------------------ timeline
T_B, T_C, T_TILT0, T_TILT1 = 12.78, 20.8, 25.0, 28.9
T_FW, T_F, T_CLOUD2, T_G = 29.38, 40.9, 45.05, 48.4
T_DIE = 15.5
HY_BLADE, HY_SKY, HY_FOREST = 800, 1570, 1235
PAN_A, PAN_B = 60.0, 170.0

def dawn_at(t, mode='take'):
    if mode == 'G': return keys(t, [(47.0, 0.78), (57.0, 0.92)])
    return keys(t, [(0, 0.0), (12.8, 0.07), (25, 0.17), (29, 0.22), (41, 0.38), (45, 0.46), (49, 0.52)])

# ------------------------------------------------------------------ palettes (RGB)
ZEN = (C(24, 22, 52), C(74, 72, 104));  HOR = (C(66, 58, 98), C(176, 142, 138))
FAR = (C(34, 42, 46), C(84, 90, 74));   NEAR = (C(13, 21, 17), C(40, 50, 34))
TREE_N = (C(11, 10, 19), C(24, 21, 28)); TREE_F = (C(36, 32, 58), C(92, 76, 92))
WARM = C(255, 186, 92)
def pal(p, d): return lerp(p[0], p[1], d)

# ------------------------------------------------------------------ precomputed textures
TW, TH, TX0, TY0 = 1800, 2900, 300, 2700     # sky texture; world x=-300.., world y=-2700..
def fbm(h, w, octs, seed, ax=2.0):
    r = np.random.RandomState(seed); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for s in octs:
        g = r.rand(int(h / s) + 3, int(w / (s * ax)) + 3).astype(np.float32)
        out += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC); tot += amp; amp *= 0.5
    return out / tot

def build_sky_tex():
    n = fbm(TH, TW, [520, 260, 130, 64, 32, 16], 11)
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    cx, cy = 520 + TX0, -800 + TY0                      # hero cloud centre (world 520,-800)
    hero = np.exp(-((xx - cx) / 330) ** 2 - ((yy - cy) / 105) ** 2)
    hero += 0.6 * np.exp(-((xx - cx - 190) / 210) ** 2 - ((yy - cy + 50) / 70) ** 2)
    hero += 0.5 * np.exp(-((xx - cx + 230) / 190) ** 2 - ((yy - cy - 25) / 60) ** 2)
    band = 0.10 * np.exp(-((yy - (TY0 - 1750)) / 260) ** 2) + 0.07 * np.exp(-((yy - (TY0 - 330)) / 120) ** 2)
    clear = 1 - 0.9 * np.exp(-((xx - cx) / 800) ** 2 - ((yy - cy) / 420) ** 2)   # empty sky round hero
    d = sstep_np(0.56, 0.80, n + band * clear * (1 - 0.55 * np.clip(hero, 0, 1)) + 0.60 * np.clip(hero, 0, 1.2) * (0.30 + 1.25 * n) + 0.30 * np.clip(hero, 0, 1) - 0.06)
    d = cv2.GaussianBlur(d, (0, 0), 3)
    below = np.roll(d, -55, axis=0)
    hm = np.clip(hero * 1.6, 0, 1)
    ul = d * (1 - 0.85 * below) * 1.5 + 0.22 * d
    fx, fy = 640 + TX0, TY0 - 40
    ul *= hm * np.exp(-(((xx - fx) / 620) ** 2 + ((yy - fy) / 1000) ** 2))
    ul = cv2.GaussianBlur(ul, (0, 0), 9)
    st = np.zeros((TH, TW), np.float32); r = np.random.RandomState(5)
    for _ in range(420):
        x, y = r.randint(2, TW - 2), int(r.rand() ** 1.4 * (TY0 - 250)) + 2
        st[y, x] += r.rand() ** 3 * 150 + 22
    st = cv2.GaussianBlur(st, (0, 0), 0.9) * 5
    return d.astype(np.float32), ul.astype(np.float32), st

def conifer(mask, x, base, h, r, jag=1.0):
    n = max(4, int(h / 16)); pts_l = [(x, base - h)]; pts_r = []
    for i in range(1, n + 1):
        y = base - h + h * i / n; wb = h * 0.17 * (i / n) ** 0.85 * (0.8 + 0.4 * r.rand()) * jag
        pts_l += [(x - wb, y), (x - wb * 0.45, y - h / n * 0.25)]
        pts_r += [(x + wb, y), (x + wb * 0.45, y - h / n * 0.25)]
    poly = np.array(pts_l + pts_r[::-1], np.float32)
    cv2.fillPoly(mask, [np.round(poly * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
    cv2.line(mask, (int(x), int(base - h * 0.5)), (int(x), int(base + 4)), 255, max(1, int(h / 60)), cv2.LINE_AA)

def build_trees():
    r = np.random.RandomState(3); Wt, Ht = 1900, 420
    far = np.zeros((Ht, Wt), np.uint8); near = np.zeros((Ht, Wt), np.uint8)
    prof = fbm(1, Wt, [300, 120, 50], 21, ax=1)[0]
    for x in np.sort(r.rand(260) * Wt):
        conifer(far, x, Ht - 20, 50 + 80 * prof[int(x)] + 30 * r.rand(), r)
    far[Ht - 62:, :] = 255
    prof2 = fbm(1, Wt, [420, 160, 60], 22, ax=1)[0]
    for x in np.sort(r.rand(150) * Wt):
        hh = 70 + 250 * prof2[int(x)] ** 1.6 + 45 * r.rand()
        conifer(near, x, Ht - 4, hh, r)
    near[Ht - 34:, :] = 255
    return far.astype(np.float32) / 255, near.astype(np.float32) / 255

NB = 3600
def build_blades():
    r = np.random.RandomState(9)
    z = r.rand(NB) ** 0.95
    b = dict(z=z, x=r.rand(NB) * 2100 - 450, wy=3 + 1260 * z ** 1.7,
             h=(9 + 330 * z ** 1.5) * (0.55 + 0.9 * r.rand(NB)), w=0.9 + 6.5 * z ** 1.3,
             lean=r.randn(NB) * 0.2, ph=r.rand(NB) * 6.28, var=0.72 + 0.56 * r.rand(NB),
             glint=(r.rand(NB) < 0.11).astype(np.float32) * r.rand(NB))
    o = np.argsort(b['wy']); return {k: v[o].astype(np.float32) for k, v in b.items()}

SKY_D, SKY_UL, SKY_ST = build_sky_tex()
TREE_FAR, TREE_NEAR = build_trees()
BL = build_blades()
FOG = sstep_np(0.36, 0.78, fbm(700, 3000, [300, 150, 70, 35], 51, ax=2.6))
GRAIN = [cv2.GaussianBlur(np.random.RandomState(100 + i).randn(H, W).astype(np.float32), (0, 0), 0.7) * 2.6 for i in range(7)]
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.30 * (((_xx - W / 2) / (W * 0.78)) ** 2 + ((_yy - H / 2) / (H * 0.72)) ** 2))[..., None].astype(np.float32)
SS = np.linspace(0, 1, 7, dtype=np.float32)


_F = np.load(os.path.join(HERE, "feat.npz")); F_FULL, F_VOC = _F['full'], _F['voc']
def feat(a, t): return float(a[min(len(a) - 1, max(0, int(t * 30)))])
def wind_gain(t): return 0.22 + 1.75 * feat(F_FULL, t) ** 1.4

def wind(x, t, ph):
    return _wind(x, t, ph) * wind_gain(t)

def _wind(x, t, ph):
    g = np.sin(0.37 * t - 0.0019 * x) * np.sin(0.23 * t + 1.3 - 0.0011 * x)
    return 0.07 * np.sin(1.35 * t + 0.004 * x + ph) + 0.19 * g + 0.025 * np.sin(3.1 * t + ph * 2)

def add_glow(img, x, y, sig, col, k):
    R = int(sig * 3.2) + 1; x0, x1, y0, y1 = int(x) - R, int(x) + R + 1, int(y) - R, int(y) + R + 1
    a0, a1, b0, b1 = max(x0, 0), min(x1, W), max(y0, 0), min(y1, H)
    if a0 >= a1 or b0 >= b1: return
    yy, xx = np.mgrid[b0:b1, a0:a1].astype(np.float32)
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sig * sig)) * k
    img[b0:b1, a0:a1] += g[..., None] * col

# ------------------------------------------------------------------ background world
def background(t, d, hy, pan, fw=0.0, trees=True, fw_t=None, fly=None):
    hy = int(round(hy)); wy = (np.arange(H, dtype=np.float32) - hy)
    u = np.clip(-wy / 1500, 0, 1) ** 0.8
    col = pal(HOR, d)[None, :] + (pal(ZEN, d) - pal(HOR, d))[None, :] * u[:, None]
    img = np.repeat(col[:, None, :], W, axis=1)
    wx = np.arange(W, dtype=np.float32) + pan
    gx = 700.0
    cold = np.exp(-((wy + 30) / 270) ** 2)[:, None] * np.exp(-((wx - gx) / 640) ** 2)[None, :]
    amb = np.exp(-((wy + 6) / 130) ** 2)[:, None] * np.exp(-((wx - gx) / 330) ** 2)[None, :]
    img += cold[..., None] * C(66, 50, 52) * (0.55 + 0.9 * d) + amb[..., None] * C(92, 50, 14) * (0.7 + 1.0 * d)
    # clouds / stars
    drift = 1.4 * t
    r0 = TY0 - hy; r1 = r0 + H
    a0, a1 = max(r0, 0), min(r1, TH)
    if a1 > a0:
        c0 = int(TX0 + pan - drift)
        sl = (slice(a0, a1), slice(c0, c0 + W)); dst = slice(a0 - r0, a1 - r0)
        D = SKY_D[sl][..., None]; sub = img[dst]
        ccol = sub * (0.60 - 0.05 * d) + C(5, 7, 14)
        st = SKY_ST[sl][..., None] * max(0.0, 1 - 2.6 * d) * (1 - D)
        sub[:] = sub * (1 - 0.9 * D) + ccol * 0.9 * D + st * C(0.8, 0.86, 1.0)
        if fw > 0: sub += SKY_UL[sl][..., None] * C(255, 158, 112) * (0.62 * fw)
    if fw > 0:   # the distant burst itself, far beyond the trees
        fxs, fys = 640 - pan + drift * 0, hy - 52
        add_glow(img, fxs, fys, 150, C(255, 170, 120), 0.20 * fw)
        add_glow(img, fxs, fys, 34, C(255, 205, 165), 0.45 * fw)
        if fw_t is not None:
            r = np.random.RandomState(77); rad = 16 + 46 * (1 - math.exp(-fw_t * 3.2))
            for i in range(26):
                a = r.rand() * 6.28; rr = rad * (0.45 + 0.55 * r.rand())
                add_glow(img, fxs + rr * math.cos(a), fys + rr * math.sin(a) * 0.9 + 14 * fw_t ** 2, 1.5,
                         C(255, 214, 180), 0.9 * fw * (0.5 + 0.5 * r.rand()))
    # tree line
    if trees:
        Ht = TREE_FAR.shape[0]
        for mask, colp, off, par in ((TREE_FAR, TREE_F, 20, 0.85), (TREE_NEAR, TREE_N, 12, 1.0)):
            y1 = hy + off; y0 = y1 - Ht; b0, b1 = max(y0, 0), min(y1, H)
            if b1 <= b0: continue
            c0 = int(360 + pan * par)
            m = mask[b0 - y0:b1 - y0, c0:c0 + W][..., None]
            img[b0:b1] = img[b0:b1] * (1 - m) + pal(colp, d) * m
    # field base
    if hy < H:
        z = np.clip(wy[hy:] / 1150, 0, 1) ** 0.7
        fc = pal(FAR, d)[None, :] + (pal(NEAR, d) - pal(FAR, d))[None, :] * z[:, None]
        tex = fbm(8, W, [40, 12], 4, ax=1)[0]  # cheap static streaks
        img[hy:] = fc[:, None, :] * (0.92 + 0.16 * tex[None, :, None])
    img8 = np.clip(img + GRAIN[int(t * FPS) % 7][..., None] * 0.25 + 0.5, 0, 255).astype(np.uint8)
    tips = draw_blades(img8, t, d, hy, pan)
    img = img8.astype(np.float32)
    if tips is not None:
        tx, ty, tg, tz, tp = tips
        cold = (0.10 + (0.95 * feat(F_VOC, t) if t > T_DIE + 0.7 else 0.0)) * (0.6 + 0.6 * d)
        tw = 0.35 + 0.65 * np.sin(1.7 * t + tp * 3) ** 2
        for j in range(len(tx)):
            if not (2 < tx[j] < W - 2 and 2 < ty[j] < H - 2): continue
            sg = 1.1 + 1.7 * tz[j]; kk = tg[j] * tw[j]
            if cold > 0.01: add_glow(img, tx[j], ty[j], sg, C(214, 200, 196), kk * cold * 0.8)
            wk = fw * 1.1
            if fly is not None: wk += fly[2] * math.exp(-((tx[j] - fly[0]) ** 2 + (ty[j] - fly[1]) ** 2) / (2 * 230.0 ** 2)) * 1.3
            if wk > 0.02: add_glow(img, tx[j], ty[j], sg, WARM, kk * wk * 0.8)
    mist = (np.exp(-((wy - 14) / 62) ** 2) * 0.55 + np.exp(-((wy - 60) / 190) ** 2) * 0.22)[:, None, None]
    mist = mist * (0.75 + 0.25 * np.sin(wx * 0.004 + 0.05 * t + 1.0))[None, :, None]
    img = img * (1 - mist) + lerp(C(52, 50, 70), C(140, 122, 116), d) * mist
    r0 = max(0, hy - 250); r1 = min(H, hy + 450)
    if r1 > r0:
        c0 = int(300 + pan + 9 * t) % 1900
        fg_ = FOG[r0 - (hy - 250):r1 - (hy - 250), c0:c0 + W] * (0.40 * np.exp(-((wy[r0:r1] - 40) / 190) ** 2))[:, None]
        img[r0:r1] = img[r0:r1] * (1 - fg_[..., None]) + lerp(C(70, 62, 82), C(168, 142, 132), d) * fg_[..., None]
    return img

def draw_blades(img8, t, d, hy, pan):
    by = hy + BL['wy']; bx = BL['x'] - pan + 300
    vis = (by - BL['h'] < H + 10) & (bx > -260) & (bx < W + 260)
    idx = np.nonzero(vis)[0]
    if len(idx) == 0: return None
    bx, by = bx[idx], by[idx]; h, w, z = BL['h'][idx], BL['w'][idx], BL['z'][idx]
    sway = (BL['lean'][idx] + wind(BL['x'][idx], t, BL['ph'][idx])) * h
    bend = np.minimum(1, np.abs(sway) / h)
    cx = bx[:, None] + sway[:, None] * SS[None] ** 2
    cy = by[:, None] - h[:, None] * SS[None] * (1 - 0.28 * SS[None] * bend[:, None])
    hw = w[:, None] * (1 - SS[None]) ** 0.8
    pts = np.concatenate([np.stack([cx - hw, cy], -1), np.stack([cx + hw, cy], -1)[:, ::-1]], 1)
    pts = np.round(pts * 16).astype(np.int32)
    zc = (z ** 0.7)[:, None]
    col = (pal(FAR, d)[None] * (1 - zc) + pal(NEAR, d)[None] * zc) * BL['var'][idx][:, None] * 1.12
    gl = (BL['glint'][idx] * (0.35 + 0.65 * z))[:, None]
    col = col * (1 - 0.5 * gl) + (lerp(C(70, 98, 112), C(120, 150, 150), d))[None] * 0.5 * gl
    col = np.clip(col, 0, 255)
    for i in range(len(idx)):
        cv2.fillPoly(img8, [pts[i]], (float(col[i, 0]), float(col[i, 1]), float(col[i, 2])), cv2.LINE_AA, 4)
    g = BL['glint'][idx]; m = g > 0.12
    return cx[m, -2], cy[m, -2], g[m], z[m], BL['ph'][idx][m]

# ------------------------------------------------------------------ foreground blades (layer with alpha)
FG = [  # base x, height, lean, width, phase, shade
    (-40, 1250, 250, 60, 0.3, 0.55), (1010, 1050, -210, 52, 2.1, 0.5), (860, 620, 130, 40, 4.0, 0.7),
    (120, 520, -90, 36, 5.2, 0.75), (640, 400, -60, 30, 1.2, 0.8), (1000, 1230, -300, 66, 3.3, 0.45),
    (420, 330, 70, 26, 2.7, 0.85)]

def curve_poly(P, hw):
    dP = np.gradient(P, axis=0); n = np.stack([-dP[:, 1], dP[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-6
    return P + n * hw[:, None], P - n * hw[:, None]

def poly16(a): return [np.round(a * 16).astype(np.int32)]

def fg_layer(t, d, dx, dy, hmax=9999):
    lay = np.zeros((H, W, 3), np.uint8); al = np.zeros((H, W), np.uint8)
    s = np.linspace(0, 1, 24, dtype=np.float32)
    for bx, h, lean, w, ph, sh in FG:
        if h > hmax: continue
        sw = lean + h * float(wind(np.float32(bx), t, ph)) * 0.7
        P = np.stack([bx + dx + sw * s ** 2, H + 60 + dy - h * s * (1 - 0.2 * s * min(1, abs(sw) / h))], 1)
        L, R = curve_poly(P, w * 0.5 * (1 - s) ** 0.7)
        poly = poly16(np.concatenate([L, R[::-1]]))
        c = pal(NEAR, d) * sh * 1.25
        cv2.fillPoly(lay, poly, tuple(float(v) for v in c), cv2.LINE_AA, 4); cv2.fillPoly(al, poly, 255, cv2.LINE_AA, 4)
    return lay, al

HERO_BASE = np.array([300.0, 2060.0])
def hero_curve(t, n=90, sway=1.0):
    s = np.linspace(0, 1, n, dtype=np.float32)
    sw = 520 * float(wind(np.float32(300), t, 0.8)) * 0.42 * sway
    x = HERO_BASE[0] + 380 * s ** 1.8 + sw * s ** 2.2
    y = HERO_BASE[1] - 1500 * s + 125 * s ** 3 + abs(sw) * 0.25 * s ** 2
    return s, np.stack([x, y], 1)

def hero_point(s, P, q, side=0.0, hwf=None):
    i = q * (len(s) - 1); i0 = int(i); f = i - i0; i1 = min(i0 + 1, len(s) - 1)
    p = P[i0] * (1 - f) + P[i1] * f; tg = P[i1] - P[i0]; nrm = np.array([-tg[1], tg[0]]); nrm /= np.linalg.norm(nrm) + 1e-6
    return p + nrm * side

def hero_hw(s): return 31 * (1 - s) ** 0.62 * (0.55 + 0.45 * np.minimum(1, s * 5))

def draw_drop(lay, al, cx, cy, r, d, warm, hang=0.0):
    R = int(r * 1.6 + hang) + 3; x0, y0 = int(cx) - R, int(cy) - R
    if x0 < 0 or y0 < 0 or x0 + 2 * R >= W or y0 + 2 * R >= H: return
    yy, xx = np.mgrid[0:2 * R, 0:2 * R].astype(np.float32); dx = xx - (cx - x0); dy = yy - (cy - y0)
    dyn = np.where(dy > 0, dy / (1 + hang / r), dy)      # teardrop stretch below
    rr = np.sqrt(dx * dx + dyn * dyn) / r
    a = np.clip((1 - rr) * r / 1.3, 0, 1)
    v = np.clip((dyn / r + 1) / 2, 0, 1)[..., None]       # 0 top .. 1 bottom
    top = lerp(C(18, 26, 26), C(40, 50, 42), d); bot = lerp(C(110, 100, 136), C(210, 176, 160), d)
    body = top + (bot - top) * v ** 2.2
    body *= (1 - 0.55 * np.clip(rr, 0, 1)[..., None] ** 6)
    if warm > 0:
        wv = np.clip(1.15 - np.sqrt((dx + r * 0.25) ** 2 + (dyn - r * 0.2) ** 2) / (r * 1.25), 0, 1)[..., None]
        body = body * (1 - 0.8 * warm) + (WARM * (0.45 + 0.75 * wv ** 1.5)) * warm * 1.0
    hl = np.exp(-(((dx + r * 0.36) ** 2 + (dyn + r * 0.42) ** 2) / (2 * (r * 0.17) ** 2)))[..., None]
    body = body + hl * lerp(lerp(C(170, 190, 225), C(225, 232, 245), d), C(255, 240, 205), warm) * (0.9 + 0.5 * warm)
    sub = lay[y0:y0 + 2 * R, x0:x0 + 2 * R].astype(np.float32)
    lay[y0:y0 + 2 * R, x0:x0 + 2 * R] = np.clip(sub * (1 - a[..., None]) + body * a[..., None], 0, 255).astype(np.uint8)
    sa = al[y0:y0 + 2 * R, x0:x0 + 2 * R]; al[y0:y0 + 2 * R, x0:x0 + 2 * R] = np.maximum(sa, (a * 255).astype(np.uint8))

DROPS = [(0.765, 1.0, 17, 7.0), (0.60, -1.0, 8.5, 0.0), (0.47, -1.0, 6.5, 0.0), (0.66, 1.0, 5.5, 2.0), (0.86, -1.0, 4.5, 0.0), (0.33, 1.0, 7.0, 3.0)]
def hero_layer(t, d, dx, dy, warm=0.0, k=1.0, B=None, main=('on', 7.0), sway=1.0):
    lay = np.zeros((H, W, 3), np.uint8); al = np.zeros((H, W), np.uint8)
    s, P = hero_curve(t, 90 if k == 1 else 240, sway); hw = hero_hw(s)
    if B is not None:
        A = hero_point(s, P, DROPS[0][0]); P = (P - A) * k + np.array(B, np.float32); hw = hw * k
    P = (P + np.array([dx, dy], np.float32)).astype(np.float32)
    L, R = curve_poly(P, hw); e = 8 if k == 1 else 22
    base = lerp(C(18, 31, 23), C(48, 64, 40), d)
    full = poly16(np.concatenate([L, R[::-1]]))
    cv2.fillPoly(lay, full, tuple(map(float, base)), cv2.LINE_AA, 4); cv2.fillPoly(al, full, 255, cv2.LINE_AA, 4)
    Li = P + (L - P) * 0.55
    cv2.fillPoly(lay, poly16(np.concatenate([L, Li[::-1]])), tuple(map(float, base * 1.5 + C(8, 12, 16))), cv2.LINE_AA, 4)
    Le = P + (L - P) * 0.86
    sheen = lerp(C(96, 100, 110), C(170, 156, 140), d)
    cv2.fillPoly(lay, poly16(np.concatenate([L[e:], Le[e:][::-1]])), tuple(map(float, sheen)), cv2.LINE_AA, 4)
    cv2.polylines(lay, poly16(P[:-6] + (R[:-6] - P[:-6]) * 0.08), False, tuple(map(float, base * 0.6)), max(2, int(2 * k)), cv2.LINE_AA, 4)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.1 * k ** 0.9)
    pos = []
    for i, (q, side, r, hang) in enumerate(DROPS):
        r *= k; hang *= k
        hwq = float(np.interp(q, s, hw)); p = hero_point(s, P, q, -side * (hwq + r * 0.45)); pos.append(p)
        if i == 0:
            if main[0] == 'on': hang = main[1] * k
            else:
                pr = hero_point(s, P, q, -side * (hwq + r * 0.1))
                draw_drop(lay, al, pr[0], pr[1], r * 0.3, d, 0, 0)
                if main[0] == 'fall': draw_drop(lay, al, p[0], p[1] + main[1], r * 0.92, d, 0, r * 0.3)
                continue
        draw_drop(lay, al, p[0], p[1], r, d, warm if i == 0 else warm * 0.35, hang)
    return lay, al, pos[0]

T_TEAR, T_DROP = 37.6, 38.56
def tear_shot(t, d):
    img = blur(background(t, d, HY_BLADE, PAN_B), 24)
    img = cv2.warpAffine(img, cv2.getRotationMatrix2D((540, 800), 0, 1.5), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    lay, al = fg_layer(t, d, 0, 0); img, _ = comp(img, lay, al, 34)
    tau = t - T_DROP
    if tau < 0:
        u = sstep(T_TEAR - 0.5, T_DROP, t); main = ('on', 7 + 15 * u * u); off = 6 * u
    else:
        main = ('fall', 40 * tau + 0.5 * 1500 * tau * tau)
        off = 6 - 30 * (1 - math.exp(-7 * tau)) - 13 * math.exp(-2.2 * tau) * math.sin(10.5 * tau)
    Bp = (296 - 4 * (t - T_TEAR), 640 + off)
    hl, ha, _ = hero_layer(t, d, 0, 0, 0.0, 2.6, Bp, main, sway=0.22)
    img, _ = comp(img, hl, ha, 0)
    return img

def comp(img, lay, al, sig):
    a = al.astype(np.float32) / 255; l = lay.astype(np.float32)
    if sig > 0.3:
        k = 2 if sig > 6 else 1
        if k == 2:   # blur at half res for speed
            a = cv2.resize(cv2.GaussianBlur(cv2.resize(a, (W // 2, H // 2), interpolation=cv2.INTER_AREA), (0, 0), sig / 2), (W, H), interpolation=cv2.INTER_LINEAR)
            l = cv2.resize(cv2.GaussianBlur(cv2.resize(l, (W // 2, H // 2), interpolation=cv2.INTER_AREA), (0, 0), sig / 2), (W, H), interpolation=cv2.INTER_LINEAR)
        else:
            a = cv2.GaussianBlur(a, (0, 0), sig); l = cv2.GaussianBlur(l, (0, 0), sig)
    return img * (1 - a[..., None]) + l, a

def blur(img, sig):
    if sig < 0.3: return img
    if sig > 6:
        s = cv2.GaussianBlur(cv2.resize(img, (W // 2, H // 2), interpolation=cv2.INTER_AREA), (0, 0), sig / 2)
        return cv2.resize(s, (W, H), interpolation=cv2.INTER_CUBIC)
    return cv2.GaussianBlur(img, (0, 0), sig)

def bokeh(img, x, y, r, k):
    R = int(r) + 6; x0, y0 = int(x) - R, int(y) - R
    a0, a1, b0, b1 = max(x0, 0), min(x0 + 2 * R, W), max(y0, 0), min(y0 + 2 * R, H)
    if a0 >= a1 or b0 >= b1: return
    yy, xx = np.mgrid[b0:b1, a0:a1].astype(np.float32); dd = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
    disc = np.clip((r - dd) / 5, 0, 1) * (0.62 + 0.38 * (dd / r) ** 3)
    img[b0:b1, a0:a1] += disc[..., None] * WARM * k
    add_glow(img, x, y, r * 1.5, WARM, 0.10 * k)

# ------------------------------------------------------------------ firefly path
def fly_screen(t):
    if t < T_B:
        x = keys(t, [(8.2, -90), (10.95, 548), (T_B, 706)]); y = keys(t, [(8.2, 1130), (10.95, 968), (T_B, 884)])
        x = -90 + (548 + 90) * clamp((t - 8.2) / 2.75) if t < 10.95 else x
    else:
        x = keys(t, [(T_B, 706), (14.2, 668), (T_DIE + 0.3, 604)]); y = keys(t, [(T_B, 884), (14.0, 930), (T_DIE + 0.3, 902)])
    wob = sstep(8.2, 9.2, t)
    return x + wob * (9 * math.sin(2.1 * t) + 4 * math.sin(5.3 * t)), y + wob * (12 * math.sin(1.7 * t + 1) + 5 * math.sin(4.1 * t))

def fly_light(t):
    base = 0.66 + 0.10 * math.sin(2.6 * t) + 0.42 * feat(F_VOC, t)
    if t < T_DIE: return base
    return base * keys(t, [(T_DIE, 1), (T_DIE + 0.10, 0.25), (T_DIE + 0.22, 0.8), (T_DIE + 0.36, 0.12), (T_DIE + 0.5, 0.35), (T_DIE + 0.72, 0.0)])

# ------------------------------------------------------------------ bird
def draw_bird(img, x, y, t, d, sc=1.0):
    flap = math.sin(t * 2 * math.pi * 1.25); glide = sstep(-0.2, 0.5, math.sin(t * 0.9 + 0.6))
    a = lerp(flap * 0.55, 0.12, glide)                         # wing angle
    pad = 90; lay = np.zeros((pad * 2, pad * 2), np.uint8); c = np.array([pad, pad], np.float32)
    for sgn in (-1, 1):
        sh = c + np.array([sgn * 5, 0]) * sc
        el = sh + np.array([sgn * 26 * math.cos(a), -26 * math.sin(a)]) * sc
        tip = el + np.array([sgn * 30 * math.cos(a * 0.4 - 0.1), -30 * math.sin(a * 0.4 - 0.1) + 4]) * sc
        wing = np.array([sh + [0, -3 * sc], el + [0, -4 * sc], tip, el + [-sgn * 4 * sc, 7 * sc], sh + [0, 6 * sc]], np.float32)
        cv2.fillPoly(lay, poly16(wing), 255, cv2.LINE_AA, 4)
    cv2.ellipse(lay, (pad, pad + 2), (int(7 * sc), int(4 * sc)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    cv2.fillPoly(lay, poly16(np.array([c + [-4 * sc, 2], c + [4 * sc, 2], c + [5 * sc, 15 * sc], c + [-5 * sc, 15 * sc]], np.float32)), 255, cv2.LINE_AA, 4)
    m = cv2.GaussianBlur(lay, (0, 0), 0.9).astype(np.float32) / 255
    M = np.float32([[1, 0, x - pad], [0, 1, y - pad]])
    mm = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    return img * (1 - mm * 0.92) + lerp(C(8, 11, 24), C(16, 22, 36), d) * mm * 0.92

# ------------------------------------------------------------------ forest shot
def build_forest():
    r = np.random.RandomState(31); out = []
    for n, y0, y1, w0, w1, crown in ((120, 905, 1222, 2, 6, 0.5), (46, 800, 1240, 6, 15, 0.42)):
        m = np.zeros((H, W + 200), np.uint8)
        for x in np.sort(r.rand(n) * (W + 200)):
            top = y0 + r.rand() * (y1 - y0) * 0.22; w = w0 + r.rand() * (w1 - w0); leanx = r.randn() * 6
            poly = np.array([[x - w / 2, y1 + 8], [x + leanx - w * 0.22, top], [x + leanx + w * 0.22, top], [x + w / 2, y1 + 8]], np.float32)
            cv2.fillPoly(m, poly16(poly), 255, cv2.LINE_AA, 4)
            if r.rand() < 0.62:      # living conifer crown
                hh = (y1 - top) * (crown + 0.25 * r.rand())
                sub = np.zeros_like(m); conifer(sub, x + leanx, top + hh, hh * 1.12, r, 0.75 + 0.5 * r.rand()); m = np.maximum(m, sub)
            else:                     # burnt snag: a few broken stubs
                for _ in range(r.randint(2, 6)):
                    yy = top + r.rand() * (y1 - top) * 0.6; ln = (8 + r.rand() * 26) * (1 if r.rand() < 0.5 else -1) * (w1 / 15)
                    cv2.line(m, (int(x + leanx * (1 - (yy - top) / (y1 - top))), int(yy)), (int(x + ln), int(yy - abs(ln) * 0.5)), 255, max(1, int(w / 4)), cv2.LINE_AA)
        out.append(m.astype(np.float32) / 255)
    return out
FOREST = build_forest()

def forest_shot(t, d):
    u = (t - 40.3) / 5.3; hy = HY_FOREST
    wy = np.arange(H, dtype=np.float32) - hy
    uu = np.clip(-wy / 1500, 0, 1) ** 0.8
    col = pal(HOR, d)[None] * 0.92 + (pal(ZEN, d) - pal(HOR, d) * 0.92)[None] * uu[:, None]
    img = np.repeat(col[:, None, :], W, axis=1)
    wx = np.arange(W, dtype=np.float32)
    low = np.exp(-((wy + 46) / 120) ** 2)[:, None] * (0.55 + 0.45 * np.exp(-((wx - 610) / 520) ** 2))[None]
    amb = np.exp(-((wy + 30) / 70) ** 2)[:, None] * np.exp(-((wx - 610) / 250) ** 2)[None]
    img += low[..., None] * C(48, 40, 40) + amb[..., None] * C(84, 46, 14)
    sl = SKY_D[150:150 + H, 420:420 + W][..., None] * np.clip(-wy / 500, 0, 1)[:, None, None]
    img = img * (1 - 0.5 * sl) + (img * 0.6) * 0.5 * sl
    px = 14 * u
    for m, colp, par, haze in ((FOREST[0], TREE_F, 0.6, 0.0), (FOREST[1], TREE_N, 1.0, 1.0)):
        c0 = int(100 + px * par - 7 * par); mm = m[:, c0:c0 + W][..., None]
        tc = pal(colp, d) * (0.9 if haze == 0 else 1.25) + (C(10, 12, 16) if haze else 0)
        img = img * (1 - mm) + tc * mm
        mist = np.exp(-((wy + 40) / 85) ** 2)[:, None, None] * (0.24 if haze == 0 else 0.10)
        img = img * (1 - mist) + lerp(C(120, 108, 118), C(172, 150, 140), d) * mist
    z = np.clip(wy[hy:] / 1150, 0, 1) ** 0.7
    fc = pal(FAR, d)[None] + (pal(NEAR, d) - pal(FAR, d))[None] * z[:, None]
    img[hy:] = fc[:, None, :]
    img8 = np.clip(img + GRAIN[int(t * FPS) % 7][..., None] * 0.25 + 0.5, 0, 255).astype(np.uint8)
    draw_blades(img8, t, d, hy, 120)
    img = img8.astype(np.float32)
    mist = (np.exp(-((wy - 10) / 55) ** 2) * 0.6 + np.exp(-((wy - 60) / 190) ** 2) * 0.22)[:, None, None]
    img = img * (1 - mist) + lerp(C(52, 50, 70), C(140, 122, 116), d) * mist
    img = cv2.GaussianBlur(img, (0, 0), 1.6)
    sc = 1.0 + 0.04 * u
    M = cv2.getRotationMatrix2D((540, 1090), 0, sc)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

# ------------------------------------------------------------------ typography
LYR = [  # lines [(text, y)], words [(start, word)], out time, size
    dict(lines=[("The evil it spread", 372), ("like a fever ahead", 458)], out=12.42, fo=0.3,
         w=[(9.25, "The"), (9.85, "evil"), (10.16, "it"), (10.38, "spread"), (10.9, "like"), (11.5, "a"), (11.74, "fever"), (12.1, "ahead")]),
    dict(lines=[("It was night when you died,", 372), ("my firefly", 458)], out=20.0,
         w=[(12.88, "It"), (13.24, "was"), (13.42, "night"), (14.14, "when"), (15.18, "you"), (15.4, "died,"), (16.52, "my"), (16.76, "firefly")]),
    dict(lines=[("What could I have said", 372), ("to raise you from the dead?", 458)], out=25.75, fo=0.9, drift=True,
         w=[(21.26, "What"), (22.0, "could"), (22.5, "I"), (22.64, "have"), (22.78, "said"), (23.04, "to"), (23.46, "raise"), (23.94, "you"), (24.18, "from"), (24.48, "the"), (24.74, "dead?")]),
    dict(lines=[("Oh could I be the sky", 1052), ("on the Fourth of July?", 1138)], out=31.9,
         w=[(25.6, "Oh"), (25.78, "could"), (26.02, "I"), (26.5, "be"), (27.2, "the"), (27.4, "sky"), (27.92, "on"), (28.52, "the"), (28.7, "Fourth"), (28.96, "of"), (29.32, "July?")]),
    dict(lines=[("Well you do enough talk", 1094)], out=35.45, fo=0.4,
         w=[(32.74, "Well"), (33.46, "you"), (33.68, "do"), (34.06, "enough"), (34.68, "talk")]),
    dict(lines=[("My little hawk,", 1052), ("why do you cry?", 1138)], out=40.3,
         w=[(35.82, "My"), (36.0, "little"), (36.48, "hawk,"), (37.66, "why"), (38.02, "do"), (38.26, "you"), (38.48, "cry?")]),
    dict(lines=[("Tell me what did you learn", 392), ("from the Tillamook burn?", 478)], out=44.8, fo=0.3,
         w=[(41.1, "Tell"), (41.46, "me"), (41.92, "what"), (42.04, "did"), (42.3, "you"), (42.54, "learn"), (43.04, "from"), (43.52, "the"), (43.8, "Tillamook"), (44.58, "burn?")]),
    dict(lines=[("Or the Fourth of July?", 1094)], out=47.9,
         w=[(45.1, "Or"), (45.52, "the"), (45.72, "Fourth"), (46.0, "of"), (46.46, "July?")]),
    dict(lines=[("We’re all gonna die", 420)], out=54.6, fo=1.5, size=80, whole=48.86),
]
CREDIT = dict(text="Rahib Mirzoev", y=1452, t0=3.4, t1=7.3)

def build_text():
    for L in LYR:
        f = ImageFont.truetype(FONT, L.get('size', 70)); L['items'] = []; wi = 0
        for text, y in L['lines']:
            tw = f.getlength(text); x0 = (W - tw) / 2; words = text.split(" "); pre = ""
            for wd in words:
                x = x0 + f.getlength(pre); pre += wd + " "
                bb = f.getbbox(wd); pad = 6
                im = Image.new("L", (bb[2] - bb[0] + 2 * pad, 130), 0)
                ImageDraw.Draw(im).text((pad - bb[0], 18), wd, font=f, fill=255)
                start = L['whole'] if 'whole' in L else L['w'][wi][0]
                assert 'whole' in L or L['w'][wi][1] == wd, (wd, L['w'][wi])
                L['items'].append((int(round(x + bb[0] - pad)), y - 18, np.asarray(im, np.float32) / 255, start)); wi += 1
        assert 'whole' in L or wi == len(L['w'])
    f = ImageFont.truetype(FONT_I, 40); sp = 3.2; text = CREDIT['text']
    tw = sum(f.getlength(ch) + sp for ch in text) - sp
    im = Image.new("L", (int(tw) + 20, 80), 0); dr = ImageDraw.Draw(im); x = 10.0
    for ch in text:
        dr.text((x, 10), ch, font=f, fill=255); x += f.getlength(ch) + sp
    CREDIT['im'] = np.asarray(im, np.float32) / 255; CREDIT['x'] = int((W - im.width) / 2)
build_text()
TXT = C(246, 239, 226)

def put_text(img, items_alpha, yoff=0.0, blur_px=0.0, col=None):
    col = TXT if col is None else col
    A = np.zeros((H, W), np.float32); any_ = False; ys = []
    for x, y, m, a in items_alpha:
        if a <= 0.003: continue
        y = int(round(y + yoff)); h, w = m.shape
        if y < 0 or y + h > H or x < 0 or x + w > W: continue
        A[y:y + h, x:x + w] = np.maximum(A[y:y + h, x:x + w], m * a); any_ = True; ys += [y, y + h]
    if not any_: return img
    y0, y1 = max(0, min(ys) - 60), min(H, max(ys) + 60)
    a = A[y0:y1]
    if blur_px > 0.3: a = cv2.GaussianBlur(a, (0, 0), blur_px)
    sh = np.clip(cv2.GaussianBlur(a, (0, 0), 9) * 1.5 + cv2.GaussianBlur(a, (0, 0), 2.5) * 0.5, 0, 1)[..., None]
    sub = img[y0:y1] * (1 - 0.6 * sh) + C(6, 9, 20) * 0.6 * sh * 0.3
    img[y0:y1] = sub * (1 - a[..., None]) + col * a[..., None]
    return img

def typography(img, t, tilt_shift):
    for L in LYR:
        fo = L.get('fo', 0.7); out = L['out']
        if t > out + fo: continue
        fade = 1 - sstep(out, out + fo, t); its = []; rise = 0
        for x, y, m, st in L['items']:
            dur = 1.1 if 'whole' in L else 0.55
            a = sstep(st - 0.1, st - 0.1 + dur, t)
            its.append((x, y + (1 - a) * 7, m, a * fade * 0.96))
        yoff = 0.34 * tilt_shift if L.get('drift') else 0
        if L is LYR[1]:      # "firefly" arrives still warm, then cools
            img = put_text(img, its[:-1], yoff)
            img = put_text(img, its[-1:], yoff, col=lerp(C(255, 208, 140), TXT, sstep(17.2, 19.6, t)))
        else:
            img = put_text(img, its, yoff)
    a = sstep(CREDIT['t0'], CREDIT['t0'] + 1.2, t) * (1 - sstep(CREDIT['t1'] - 1.2, CREDIT['t1'], t))
    if a > 0: img = put_text(img, [(CREDIT['x'], CREDIT['y'], CREDIT['im'], a * 0.88)])
    return img

# ------------------------------------------------------------------ frame
def scene(t, mode):
    d = dawn_at(t, mode)
    if mode == 'tear': return tear_shot(t, d), 0
    if mode == 'forest': return forest_shot(t, d), 0
    f = 0.0; fw = 0.0; fwt = None; sc = 1.0
    if mode == 'G':
        pan = PAN_B; hy = HY_BLADE; bgs, hs = 9.0, 0.0; fdx = hdx = 0.0
        sc = 1.012 + 0.035 * sstep(47.5, 57.0, t)
    elif mode == 'sky2':
        pan = PAN_B; hy = HY_SKY + 8 + 5 * (t - 44.5) / 4.5; bgs, hs = 1.8, 33.0; fdx = hdx = 0.0; f = 1.0
        sc = 1.0 + 0.02 * sstep(44.5, 49.0, t)
    else:
        if t < T_B: pan = PAN_A * clamp((t - 11.3) / (T_B - 11.3)) ** 2
        else: pan = PAN_A + (PAN_B - PAN_A) * (1 - (1 - clamp((t - T_B) / (T_DIE + 0.4 - T_B))) ** 2)
        f = keys(t, [(11.5, 0), (13.3, 1), (20.4, 1), (21.5, 0), (22.2, 0), (22.95, 0.72), (23.35, 0.48), (24.0, 0.96), (24.4, 0.84), (24.95, 1)])
        tilt = sstep(T_TILT0, T_TILT1, t); tilt = tilt * tilt * (3 - 2 * tilt) * 0.5 + tilt * 0.5
        hy = HY_BLADE + (HY_SKY - HY_BLADE) * tilt + 8 * sstep(T_TILT1, 41.0, t)
        bgs = (2.6 + 13.4 * (1 - f)) * (1 - 0.3 * tilt); hs = 32.0 * f
        back = sstep(20.2, 21.8, t); fdx = -pan * 1.8 * (1 - back); hdx = -pan * 2.4 * (1 - back)
        sc = 1.055 - 0.055 * sstep(0, 11.3, t) + 0.014 * (1 - f)
        if T_FW <= t < T_FW + 2.6:
            fwt = t - T_FW
            fw = min(1, fwt / 0.07) * math.exp(-fwt / 0.5) * (0.82 + 0.18 * math.sin(fwt * 47) * math.exp(-fwt * 2))
    fly = None; flying = mode == 'take' and 8.0 < t < T_DIE + 0.8
    if flying:
        fx, fy = fly_screen(t); fk = fly_light(t); fly = (fx, fy, fk * f)
    img = background(t, d, hy, pan, fw, True, fwt, fly)
    img = blur(img, bgs)
    shift = hy - HY_BLADE
    if flying and fk > 0:           # one light: a soft disc while out of focus, a point once the lens finds it
        if f < 0.98: bokeh(img, fx, fy, 8 + 42 * (1 - f), 0.50 * fk * (1 - f) ** 0.7)
        if f > 0.02:
            add_glow(img, fx, fy, 210, WARM, 0.13 * fk * f); add_glow(img, fx, fy, 34, WARM, 0.5 * fk * f)
            add_glow(img, fx, fy, 5.0, C(255, 240, 200), 1.25 * fk * f)
    if mode == 'take' and 34.4 < t < 37.4:
        u = (t - 34.4) / 2.9
        img = draw_bird(img, -70 + 1230 * u, 420 - 215 * u ** 1.6 + 16 * math.sin(t * 2.3) * wind_gain(t) * 0.6, t, d, 1.5)
    if shift * 1.7 < 1500:
        lay, al = fg_layer(t, d, fdx, shift * 1.7)
        img, _ = comp(img, lay, al, 15 + 0.45 * hs)
        if shift * 1.45 < 1500:
            warm = 0.0
            if flying and t < 13.6:
                s_, P_ = hero_curve(t)
                dp = hero_point(s_, P_, DROPS[0][0], -(float(np.interp(DROPS[0][0], s_, hero_hw(s_))) + 8)) + [hdx, 0]
                warm = math.exp(-(math.hypot(fx - dp[0], fy - dp[1]) / 120) ** 2) * fk * (1 - f)
            hl, ha, dpos = hero_layer(t, d, hdx, shift * 1.45, warm, main=('gone',) if mode == 'G' else ('on', 7.0))
            img, a = comp(img, hl, ha, hs)
            if warm > 0.01:
                add_glow(img, dpos[0], dpos[1], 44, WARM, 0.30 * warm)
                yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
                rim = np.exp(-(((xx - dpos[0]) ** 2 + (yy - dpos[1]) ** 2) / (2 * 190 ** 2))) * a
                img += rim[..., None] * WARM * 0.17 * warm
    if sc > 1.0005:
        img = cv2.warpAffine(img, cv2.getRotationMatrix2D((540, 1000), 0, sc), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return img, shift

SEGS = [('take', 37.0), ('tear', 40.3), ('forest', 44.5), ('sky2', 47.6), ('G', 99.0)]   # (mode, last pure time)
XD = [1.0, 1.3, 1.1, 1.5]                                                                # dissolve lengths
_mr = np.random.RandomState(12)
MOTES = [(_mr.rand() * (W + 300), _mr.rand() * H, _mr.rand() ** 2, _mr.rand() * 6.28) for _ in range(34)]

def frame(i):
    t = i / FPS; tshift = 0
    for k, (mode, end) in enumerate(SEGS):
        if t <= end:
            img, sh = scene(t, mode); tshift = sh if mode == 'take' else 0; break
        if t < end + XD[k]:
            w = sstep(end, end + XD[k], t)
            a, _ = scene(t, mode); b, _ = scene(t, SEGS[k + 1][0]); img = a * (1 - w) + b * w; break
    # drifting motes close to the lens
    wg = wind_gain(t)
    for x0, y0, z, ph in MOTES:
        x = (x0 + (14 + 40 * z) * t + 30 * math.sin(0.3 * t + ph)) % (W + 300) - 150
        y = (y0 - (5 + 10 * z) * t + 45 * math.sin(0.21 * t + ph * 2)) % H
        add_glow(img, x, y, 2.5 + 15 * z, C(230, 205, 190), (0.05 - 0.032 * z) * (0.5 + 0.5 * math.sin(0.5 * t + ph) ** 2) * (0.6 + 0.4 * wg))
    # halation
    hi = np.maximum(img - 150.0, 0)
    img = img + blur(hi, 26) * 0.6 + blur(hi, 7) * 0.2
    # a camera that is held, not locked
    ang = 0.11 * math.sin(0.21 * t) + 0.06 * math.sin(0.37 * t + 1)
    M = cv2.getRotationMatrix2D((540, 960), ang, 1.018)
    M[0, 2] += 5 * math.sin(0.33 * t + 2) + 2.5 * math.sin(0.71 * t); M[1, 2] += 6 * math.sin(0.27 * t) + 3 * math.sin(0.63 * t + 1)
    img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    img = img * VIG * C(1.05, 1.0, 0.93) + C(5, 2.5, 0)
    img = typography(img, t, tshift)
    g = sstep(0.15, 2.8, t) * (1 - sstep(54.7, 56.25, t))
    img = img * g + GRAIN[i % 7][..., None] * (0.55 + 0.45 * g)
    return np.clip(img + 0.5, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        os.makedirs(sys.argv[3], exist_ok=True)
        for ts in sys.argv[2].split(","):
            f = frame(int(round(float(ts) * FPS)))
            Image.fromarray(f).save(os.path.join(sys.argv[3], f"f_{float(ts):06.2f}.png"))
    else:
        from multiprocessing import Pool
        n = int(round(DUR * FPS)); a = int(sys.argv[4]) if len(sys.argv) > 4 else 0; b = int(sys.argv[5]) if len(sys.argv) > 5 else n
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-maxrate", "16M", "-bufsize", "32M", "-pix_fmt", "yuv420p", sys.argv[2]], stdin=subprocess.PIPE)
        with Pool(4) as p:
            for k, f in enumerate(p.imap(frame, range(a, b), chunksize=4)):
                ff.stdin.write(f.tobytes())
                if k % 150 == 0: print(k, flush=True)
        ff.stdin.close(); ff.wait()
