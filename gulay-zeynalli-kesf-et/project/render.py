"""Frame renderer: Kəşf Et — Gülay Zeynallı. Reads graded master.mp4, writes video_only.mp4 (1080x1920, 30 fps).
usage: python3 render.py [start_s end_s] [--preview out.mp4] [--stills t1,t2,...]"""
import numpy as np, cv2, json, subprocess, sys, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from timeline import build, caption_events, quote_events, FPS

W, H = 1080, 1920
A = 'assets/'
MASTER = os.environ.get('MASTER', '../work/master.mp4')
items, TOTAL = build()
CAPS = caption_events(items)
QUOTES = quote_events(items)

# ---------------- palette ----------------
DG = np.array([7, 50, 39], np.float32)      # deep green
DG2 = np.array([4, 33, 26], np.float32)
GOLD = (222, 174, 92)
PEACH = (240, 200, 150)
IVORY = (255, 248, 236)
MINT = (96, 224, 168)

def F(name, size): return ImageFont.truetype(A + name, size)

# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo3(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio3(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def eoexp(x): x = clamp(x); return 1 if x >= 1 else 1 - 2 ** (-10 * x)
def prog(t, t0, d): return clamp((t - t0) / d)

# ---------------- text rendering ----------------
_cache = {}
def text_rgba(txt, font, fill, tracking=0, shadow=0, shadow_alpha=0.6, stroke=0, align='left', lh=None):
    key = (txt, font.path, font.size, fill, tracking, shadow, shadow_alpha, stroke, align, lh)
    if key in _cache: return _cache[key]
    lines = txt.split('\n')
    asc, desc = font.getmetrics(); lh = lh or int((asc + desc) * 1.08)
    def line_w(s):
        if not tracking: return font.getlength(s)
        return sum(font.getlength(c) for c in s) + tracking * (len(s) - 1)
    widths = [line_w(s) for s in lines]
    pad = shadow * 3 + 8
    w = int(max(widths)) + 2 * pad; h = lh * len(lines) + (asc + desc - lh if asc + desc > lh else 0) + 2 * pad
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for i, s in enumerate(lines):
        x0 = pad + (0 if align == 'left' else (max(widths) - widths[i]) / (2 if align == 'center' else 1)); y0 = pad + i * lh
        if tracking:
            x = x0
            for c in s:
                d.text((x, y0), c, font=font, fill=fill + (255,)); x += font.getlength(c) + tracking
        else:
            d.text((x0, y0), s, font=font, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255) if stroke else None)
    if shadow:
        a = img.getchannel('A').filter(ImageFilter.GaussianBlur(shadow))
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * shadow_alpha)))
        sh2 = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh2.paste(sh, (0, 3)); sh2.alpha_composite(img); img = sh2
    arr = np.asarray(img).astype(np.float32) / 255.0
    res = (arr, pad, lh, widths)
    _cache[key] = res
    return res

def blit(frame, rgba, x, y, alpha=1.0, clip=None):
    """alpha-composite float rgba (h,w,4 in 0..1) onto uint8->float frame (H,W,3 float32 0..255) at x,y."""
    if alpha <= 0.003: return
    h, w = rgba.shape[:2]; x, y = int(round(x)), int(round(y))
    X0, Y0, X1, Y1 = 0, 0, W, H
    if clip: X0, Y0, X1, Y1 = max(0, int(round(clip[0]))), max(0, int(round(clip[1]))), min(W, int(round(clip[2]))), min(H, int(round(clip[3])))
    fx0, fy0 = max(x, X0), max(y, Y0); fx1, fy1 = min(x + w, X1), min(y + h, Y1)
    if fx1 <= fx0 or fy1 <= fy0: return
    src = rgba[fy0 - y:fy1 - y, fx0 - x:fx1 - x]
    a = src[..., 3:4] * alpha
    region = frame[fy0:fy1, fx0:fx1]
    region *= (1 - a); region += src[..., :3] * 255 * a

# ---------------- logos ----------------
def prep_logos():
    araz = Image.open(A + 'araz_logo.png').convert('RGBA')
    lw = 218; araz = araz.resize((lw, round(araz.height * lw / araz.width)), Image.LANCZOS)
    px, py = 22, 17
    pill = Image.new('RGBA', (lw + 2 * px, araz.height + 2 * py), (0, 0, 0, 0))
    m = Image.new('L', pill.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, pill.width - 1, pill.height - 1], radius=22, fill=255)
    bg = Image.new('RGBA', pill.size, IVORY + (236,)); pill.paste(bg, (0, 0), m)
    pill.alpha_composite(araz, (px, py))
    def with_shadow(im, r=14, a=0.38, off=6):
        P = r * 2 + off
        out = Image.new('RGBA', (im.width + 2 * P, im.height + 2 * P), (0, 0, 0, 0))
        sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
        al = Image.new('L', out.size, 0); al.paste(im.getchannel('A'), (P, P + off))
        al = al.filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * a)); sh.putalpha(al)
        out.alpha_composite(sh); out.alpha_composite(im, (P, P)); return out, P
    araz_s, pa = with_shadow(pill)
    k = Image.open(A + 'kesfet_logo.png').convert('RGBA')
    bb = k.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox(); k = k.crop(bb)
    ks = 176; k = k.resize((ks, round(k.height * ks / k.width)), Image.LANCZOS)
    D = ks + 14; disc = Image.new('RGBA', (D, D), (0, 0, 0, 0)); ImageDraw.Draw(disc).ellipse([0, 0, D - 1, D - 1], fill=IVORY + (225,))
    disc.alpha_composite(k, (7, (D - k.height) // 2)); k = disc
    k_s, pk = with_shadow(k, 12, 0.45, 5)
    big = Image.open(A + 'kesfet_logo.png').convert('RGBA').crop(bb)
    big = big.resize((420, round(big.height * 420 / big.width)), Image.LANCZOS)
    big_s, pb = with_shadow(big, 22, 0.5, 10)
    araz_big = Image.open(A + 'araz_logo.png').convert('RGBA')
    aw = 300; araz_big = araz_big.resize((aw, round(araz_big.height * aw / araz_big.width)), Image.LANCZOS)
    pill2 = araz_big
    f = lambda im: np.asarray(im).astype(np.float32) / 255
    return dict(araz=(f(araz_s), pa, pill.size), kesfet=(f(k_s), pk, k.size), big=(f(big_s), pb, big.size), araz_big=(f(pill2), 0, pill2.size))
LOGO = prep_logos()
TOP_Y = 112; SIDE = 54
def draw_logos(fr, alpha):
    a, p, (w, h) = LOGO['araz']; k, pk, (kw, kh) = LOGO['kesfet']
    cy = TOP_Y + kh / 2  # align vertical centres
    blit(fr, a, SIDE - p, cy - h / 2 - p, alpha)
    blit(fr, k, W - SIDE - kw - pk, TOP_Y - pk, alpha)

# ---------------- face track ----------------
def face_track(nframes):
    d = json.load(open(A + 'face.json'))
    xs, ys, ws, idx = [], [], [], []
    for i, x, y, w in d:
        if x is None: continue
        if y > 900 or y < 250 or w < 180: continue
        idx.append(i); xs.append(x); ys.append(y); ws.append(w)
    idx = np.array(idx); xs = np.array(xs); ys = np.array(ys)
    # robust: median filter over 7 detections
    def med(a, k=7):
        p = np.pad(a, k // 2, mode='edge'); return np.array([np.median(p[j:j + k]) for j in range(len(a))])
    xs, ys = med(xs), med(ys)
    fi = np.arange(nframes)
    X = np.interp(fi, idx, xs); Y = np.interp(fi, idx, ys)
    k = 45  # 1.5 s smoothing
    ker = np.ones(k) / k
    X = np.convolve(np.pad(X, k // 2, mode='edge'), ker, 'valid')[:nframes]; Y = np.convolve(np.pad(Y, k // 2, mode='edge'), ker, 'valid')[:nframes]
    return X, Y
FX, FY = face_track(2600)

def reframe(img, z, sf):
    """crop by zoom z around the tracked face of source frame index sf."""
    if z <= 1.001: return img
    cw, ch = W / z, H / z
    fx, fy = FX[min(sf, len(FX) - 1)], FY[min(sf, len(FY) - 1)]
    x0 = clamp(fx - cw / 2, 0, W - cw); y0 = clamp(fy - ch * 0.36, 0, H - ch)
    M = np.array([[z, 0, -x0 * z], [0, z, -y0 * z]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# ---------------- source reader ----------------
class Reader:
    def __init__(self): self.p = None; self.next = None
    def get(self, sf):
        if self.p is None or sf != self.next:
            if self.p: self.p.kill()
            self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{sf / FPS:.4f}', '-i', MASTER, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
            self.next = sf; self.last = None
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            return self.last if self.last is not None else np.zeros((H, W, 3), np.uint8)
        self.next = sf + 1; self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        return self.last
RD = Reader()

# vignette
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.22 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2, 0, 1) ** 1.4)[..., None]
# bottom gradient for caption legibility
BOT = np.clip((yy - H * 0.66) / (H * 0.34), 0, 1)[..., None] ** 1.6 * 0.42
# panel colour field
grad = (yy / H)[..., None]
PANEL = DG[None, None] * (1 - grad) + DG2[None, None] * grad
glow = np.exp(-(((xx - W * 0.85) / 520) ** 2 + ((yy - H * 0.22) / 520) ** 2))[..., None]
PANEL = PANEL + glow * np.array([30, 90, 64], np.float32) * 0.35
IVP = np.array([255, 249, 238], np.float32)[None, None] * (1 - grad) + np.array([246, 234, 212], np.float32)[None, None] * grad

def blurred(img):
    s = cv2.resize(img, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), 6)
    return cv2.resize(s, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32)

# ---------------- segment helpers ----------------
PANEL_KINDS = ('title', 'card', 'follow', 'end')
def seg_at(t):
    for i, it in enumerate(items):
        if it['start'] - 1e-6 <= t < it['end'] - 1e-6: return i, it
    return len(items) - 1, items[-1]

WIPE = 0.5
def panel_state(t, i, it):
    """returns (cover_mode, edge_y). cover_mode: 'none' | 'below' (panel covers y>edge) | 'above' (covers y<edge)."""
    kind = it['kind']
    prev = items[i - 1] if i > 0 else None; nxt = items[i + 1] if i + 1 < len(items) else None
    if kind in PANEL_KINDS:
        if kind == 'end':
            p = prog(t, it['start'] + 1.45, 0.6)
            if p <= 0: return 'none', H
            return 'below', H * (1 - eio3(p))
        if not (prev and prev['kind'] in PANEL_KINDS):
            p = prog(t, it['start'], WIPE)
            if p < 1: return 'below', H * (1 - eio3(p))
        if not (nxt and nxt['kind'] in PANEL_KINDS):
            p = prog(t, it['end'] - WIPE, WIPE)
            if p > 0: return 'above', H * (1 - eio3(p))
        return 'full', 0
    return 'none', H

def draw_wipe_edge(fr, mode, ey):
    if mode not in ('below', 'above') or ey <= 2 or ey >= H - 2: return
    y = int(ey)
    fr[max(0, y - 2):y + 2] = fr[max(0, y - 2):y + 2] * 0.0 + np.array(GOLD, np.float32)

def compose_panel(base, t, i, it, strength=0.80):
    mode, ey = panel_state(t, i, it)
    if mode == 'none': return base
    bl = blurred(base.astype(np.uint8))
    if it['kind'] == 'end': pan = bl * 0.06 + IVP * 0.94
    else: pan = bl * (1 - strength) + PANEL * strength
    if mode == 'full': return pan
    out = base.copy(); y = int(ey)
    if mode == 'below': out[y:] = pan[y:]
    else: out[:y] = pan[:y]
    draw_wipe_edge(out, mode, ey)
    return out

# ---------------- overlays ----------------
FONT_CAP = F('Archivo-SemiBold.ttf', 56)
FONT_Q = F('Playfair-500-italic.ttf', 76)
FONT_FQ = F('Playfair-500-italic.ttf', 70)
FONT_NUM = F('ArchivoX-ExtraBold.ttf', 150)
FONT_OF = F('ArchivoX-SemiBold.ttf', 40)
FONT_CAT = F('ArchivoX-Medium.ttf', 32)
FONT_SMALL = F('ArchivoX-SemiBold.ttf', 22)
FONT_QUOTE = F('Playfair-500-italic.ttf', 64)
FONT_QMARK = F('Playfair-700-normal.ttf', 200)
FONT_TITLE = F('ArchivoX-ExtraBold.ttf', 132)
FONT_SUB = F('Playfair-400-italic.ttf', 62)
FONT_KICK = F('ArchivoX-Medium.ttf', 26)

def wrap(text, font, maxw):
    words = text.split(); lines = []; cur = ''
    for w_ in words:
        tst = (cur + ' ' + w_).strip()
        if font.getlength(tst) <= maxw: cur = tst
        else: lines.append(cur); cur = w_
    lines.append(cur); return '\n'.join(lines)

def reveal_lines(fr, txt, font, x, y, t0, t, fill=IVORY, stagger=0.11, dur=0.55, align='left', lh=None, alpha=1.0, exit_t=None, maxw=None):
    """mask-reveal each line sliding up; returns bottom y."""
    arr, pad, lh_, widths = text_rgba(txt, font, fill, align=align, lh=lh)
    nl = len(txt.split('\n')); hh = arr.shape[0]
    if align == 'center': x = W / 2 - arr.shape[1] / 2
    for k in range(nl):
        p = eo3(prog(t, t0 + k * stagger, dur))
        if p <= 0: continue
        a = alpha
        if exit_t is not None:
            pe = prog(t, exit_t + k * 0.05, 0.3); a *= 1 - eo3(pe); dy_e = -30 * eo3(pe)
        else: dy_e = 0
        ly0 = pad + k * lh_; ly1 = ly0 + lh_ + (pad if k == nl - 1 else 0) + 14
        dy = (1 - p) * lh_ * 0.9
        sub = arr[max(0, ly0 - 6):min(hh, ly1)]
        top = y + max(0, ly0 - 6)
        blit(fr, sub, x, top + dy + dy_e, a * min(1, p * 1.6), clip=(0, top + dy_e, W, top + sub.shape[0] + dy_e))
    return y + pad + nl * lh_

def draw_rule(fr, x, y, length, thick=3, color=GOLD, alpha=1.0):
    if length < 1: return
    fr[int(y):int(y) + thick, int(x):int(x + length)] = fr[int(y):int(y) + thick, int(x):int(x + length)] * (1 - alpha) + np.array(color, np.float32) * alpha

def card_overlay(fr, t, it, i):
    s, e = it['start'], it['end']
    first = not (i > 0 and items[i - 1]['kind'] in PANEL_KINDS)
    t0 = s + (0.32 if first else 0.18)
    exit_t = e - WIPE - 0.12
    LX = 92
    if it['kind'] == 'card':
        n = it['n']
        # big number
        arr, pad, lh, wd = text_rgba(f'{n:02d}', FONT_NUM, GOLD)
        p = eo3(prog(t, t0, 0.6)); pe = eo3(prog(t, exit_t, 0.3))
        blit(fr, arr, LX - pad - 6 + (1 - p) * -40, 760 - pad, p * (1 - pe))
        arr2, pad2, _, _ = text_rgba('/ 05', FONT_OF, IVORY)
        p2 = eo3(prog(t, t0 + 0.12, 0.5))
        blit(fr, arr2, LX + wd[0] + 18 - pad2, 760 + 98 - pad2, p2 * (1 - pe) * 0.85)
        draw_rule(fr, LX, 970, 150 * eoexp(prog(t, t0 + 0.2, 0.7)), 3, GOLD, 1 - pe)
        arr3, pad3, _, _ = text_rgba(it['cat'], FONT_CAT, PEACH, tracking=7)
        p3 = eo3(prog(t, t0 + 0.3, 0.5))
        blit(fr, arr3, LX - pad3 + (1 - p3) * 24, 1000 - pad3, p3 * (1 - pe))
        q = wrap(it['text'], FONT_Q, W - 2 * LX)
        reveal_lines(fr, q, FONT_Q, LX - 8, 1080, t0 + 0.45, t, IVORY, lh=94, exit_t=exit_t)
    elif it['kind'] == 'follow':
        pe = eo3(prog(t, exit_t, 0.3))
        arr3, pad3, _, _ = text_rgba('ƏLAVƏ SUAL', FONT_CAT, PEACH, tracking=7)
        p3 = eo3(prog(t, t0, 0.45))
        draw_rule(fr, LX, 930, 110 * eoexp(prog(t, t0, 0.6)), 3, GOLD, 1 - pe)
        blit(fr, arr3, LX - pad3 + (1 - p3) * 24, 960 - pad3, p3 * (1 - pe))
        q = wrap(it['text'], FONT_FQ, W - 2 * LX)
        reveal_lines(fr, q, FONT_FQ, LX - 8, 1040, t0 + 0.15, t, IVORY, lh=88, exit_t=exit_t)
    elif it['kind'] == 'title':
        nxt_card = True
        exit_t = e - 0.42
        a, pad, lh, wd = text_rgba('KƏŞF ET   ·   ARAZ 103.3 FM', FONT_KICK, GOLD, tracking=5)
        p = eo3(prog(t, t0, 0.5)); pe = eo3(prog(t, exit_t, 0.3))
        blit(fr, a, W / 2 - a.shape[1] / 2, 730 - pad + (1 - p) * 20 - pe * 30, p * (1 - pe))
        reveal_lines(fr, 'GÜLAY\nZEYNALLI', FONT_TITLE, 0, 800, t0 + 0.15, t, IVORY, stagger=0.13, dur=0.6, align='center', lh=140, exit_t=exit_t)
        draw_rule(fr, W / 2 - 70 * eoexp(prog(t, t0 + 0.45, 0.7)), 1120, 140 * eoexp(prog(t, t0 + 0.45, 0.7)), 3, GOLD, 1 - pe)
        reveal_lines(fr, '5 təəccüblü sual, 5 cavab', FONT_SUB, 0, 1150, t0 + 0.55, t, GOLD, align='center', exit_t=exit_t)

def end_overlay(fr, t, it):
    t0 = it['start'] + 1.85
    if t < t0 - 0.05: return
    big, pb, (bw, bh) = LOGO['big']
    p = eo3(prog(t, t0, 0.8)); sc = 0.9 + 0.1 * p
    if p > 0:
        arr = big
        if sc < 0.999:
            arr = cv2.resize(big, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
        blit(fr, arr, W / 2 - arr.shape[1] / 2, 800 - arr.shape[0] / 2, p)
    reveal_lines(fr, 'GÜLAY ZEYNALLI', F('ArchivoX-Bold.ttf', 58), 0, 1080, t0 + 0.35, t, (12, 74, 56), align='center')
    reveal_lines(fr, '5 təəccüblü sual, 5 cavab', F('Playfair-400-italic.ttf', 50), 0, 1158, t0 + 0.5, t, (176, 124, 44), align='center')
    a, _, (aw, ah) = LOGO['araz_big']
    pa = eo3(prog(t, t0 + 0.7, 0.6))
    blit(fr, a, W / 2 - aw / 2, 1370 + (1 - pa) * 20, pa)
    # final gentle fade
    pf = prog(t, it['end'] - 0.6, 0.6)
    if pf > 0: fr *= (1 - 0.0 * eio3(pf))

def caption_overlay(fr, t):
    for ci, (a, b, txt) in enumerate(CAPS):
        nxt_a = CAPS[ci + 1][0] if ci + 1 < len(CAPS) else 1e9
        hard_end = min(b + 0.12, nxt_a - 0.001)
        if a - 0.01 <= t < hard_end:
            arr, pad, lh, wd = text_rgba(txt, FONT_CAP, IVORY, shadow=7, shadow_alpha=0.85, align='center', lh=68)
            p = eo3(prog(t, a, 0.16)); pe = prog(t, min(b, hard_end - 0.12), 0.12)
            nl = txt.count('\n') + 1
            y = 1600 - nl * 68
            blit(fr, arr, W / 2 - arr.shape[1] / 2, y - pad + (1 - p) * 14, p * (1 - pe))

def quote_overlay(fr, t):
    for (a, d, txt) in QUOTES:
        if a <= t < a + d + 0.3:
            pe = eo3(prog(t, a + d, 0.3))
            LX = 96; Y = 1190
            # dark band for depth
            pb = eo3(prog(t, a, 0.4)) * (1 - pe)
            if pb > 0:
                band = np.clip(1 - np.abs((np.arange(H)[:, None] - (Y + 120)) / 260.0), 0, 1) ** 1.5 * 0.55 * pb
                fr *= (1 - band[..., None] if band.ndim == 2 else 1 - band[:, :, None])
            arr, pad, lh, wd = text_rgba('“', FONT_QMARK, GOLD)
            pq = eo3(prog(t, a, 0.45))
            blit(fr, arr, LX - pad - 10, Y - 120 - pad + (1 - pq) * 30, pq * (1 - pe))
            yb = reveal_lines(fr, txt, FONT_QUOTE, LX - 8, Y, a + 0.12, t, IVORY, stagger=0.12, dur=0.5, lh=80, alpha=1 - pe)
            draw_rule(fr, LX, yb + 14, 120 * eoexp(prog(t, a + 0.35, 0.6)), 3, GOLD, 1 - pe)

def minilabel_overlay(fr, t, i, it):
    if it['kind'] != 'answer': return
    prev = items[i - 1]
    if prev['kind'] != 'card': return
    s = it['start']
    p = eo3(prog(t, s + 0.15, 0.4)); pe = eo3(prog(t, s + 3.2, 0.4))
    if p <= 0 or pe >= 1: return
    txt = f"{prev['n']:02d} / 05   ·   {prev['cat']}"
    arr, pad, lh, wd = text_rgba(txt, FONT_SMALL, IVORY, tracking=4)
    w_, h_ = int(wd[0]) + 44, 52
    key = ('pill', w_)
    if key not in _cache:
        im = Image.new('RGBA', (w_, h_), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, w_ - 1, h_ - 1], radius=26, fill=(7, 50, 39, 205), outline=GOLD + (200,), width=2)
        _cache[key] = np.asarray(im).astype(np.float32) / 255
    pill = _cache[key]
    y = 318 + (1 - p) * -12
    blit(fr, pill, W / 2 - w_ / 2, y, p * (1 - pe))
    blit(fr, arr, W / 2 - wd[0] / 2 - pad, y + (h_ - lh) / 2 - pad + 2, p * (1 - pe))

# ---------------- frame ----------------
END_SRC = None
def render_frame(t):
    global END_SRC
    i, it = seg_at(t); kind = it['kind']
    if kind in ('hook', 'answer'):
        for p in it['parts']:
            if t < p['out_out'] - 1e-6 or p is it['parts'][-1]: break
        lt = t - p['out_in']; dur = p['out_out'] - p['out_in']
        sf = int(round((p['src_in'] + lt) * FPS))
        z = p['z0'] + (p['z1'] - p['z0']) * eio3(lt / dur)
        img = reframe(RD.get(sf), z, sf)
    elif kind == 'end':
        if END_SRC is None:
            prev = items[i - 1]['parts'][-1]; sf = int(round(prev['src_out'] * FPS)) - 1
            img0 = RD.get(sf); z = prev['z1']; END_SRC = (img0.copy(), z, sf)
        img0, z, sf = END_SRC
        z2 = z * (1 + 0.04 * eio3(prog(t, it['start'], it['end'] - it['start'])))
        img = reframe(img0, z2, sf)
    else:
        lt = t - it['start']; a, b = it['src']
        sf = int(round((a + lt * (b - a) / (it['end'] - it['start'])) * FPS))
        img = reframe(RD.get(sf), 1.06, sf)
    fr = img.astype(np.float32)
    fr *= VIG
    if kind in ('hook', 'answer', 'end'):
        fr *= (1 - BOT)
    fr = compose_panel(fr, t, i, it)
    if kind in ('title', 'card', 'follow'): card_overlay(fr, t, it, i)
    if kind == 'end': end_overlay(fr, t, it)
    quote_overlay(fr, t)
    caption_overlay(fr, t)
    minilabel_overlay(fr, t, i, it)
    la = 1.0
    if kind == 'end': la = 1 - eo3(prog(t, it['start'] + 1.45, 0.5))
    if t < 0.25: la *= eo3(t / 0.25)
    draw_logos(fr, la)
    return np.clip(fr, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--stills':
        od = args[2] if len(args) > 2 else 'stills'; os.makedirs(od, exist_ok=True)
        for ts in args[1].split(','):
            t = float(ts); END_SRC = None
            Image.fromarray(render_frame(t)).save(f'{od}/s_{t:06.2f}.png')
        sys.exit()
    t0 = float(args[0]) if args else 0.0; t1 = float(args[1]) if len(args) > 1 else TOTAL
    out = args[2] if len(args) > 2 else 'video_only.mp4'
    nf = int(round((t1 - t0) * FPS))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                            '-x264-params', 'keyint=60', out], stdin=subprocess.PIPE)
    import time; st = time.time()
    for k in range(nf):
        t = t0 + k / FPS
        enc.stdin.write(render_frame(t).tobytes())
        if k % 150 == 0: print(f'{k}/{nf} t={t:.2f} {time.time() - st:.0f}s', flush=True)
    enc.stdin.close(); enc.wait(); print('done', time.time() - st)
