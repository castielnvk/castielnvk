# Vertical comedy-edit compositor: source panels -> 1080x1920 designed layout
import numpy as np, cv2, json, subprocess, math, os, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SRC = '/tmp/claude-0/-workspace-castielnvk/84104dec-feb8-5707-9b55-a4257893035a/scratchpad/w4/combo.mov'
BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, '..', 'assets')
WDIR = os.path.join(BASE, '..', 'w4')
PANEL = {'L': (88, 132), 'R': (1034, 132)}
PW, PH = 800, 758
FONT_CAP = os.path.join(ASSETS, 'Montserrat-900.ttf')
FONT_CAP8 = os.path.join(ASSETS, 'Montserrat-800.ttf')
FONT_DISP = os.path.join(ASSETS, 'Montserrat-900.ttf')

YEL = (255, 214, 10); MAG = (255, 61, 154); CYA = (34, 211, 238); WHITE = (255, 255, 255)
PURP = (124, 58, 237); INK = (17, 10, 38)
SPK_COL = {'L': YEL, 'R': CYA, 'P': MAG, 'X': WHITE}

@functools.lru_cache(None)
def font(path, size):
    return ImageFont.truetype(path, size)

def ease(x):  # easeInOutCubic
    x = min(1, max(0, x)); return 4*x*x*x if x < .5 else 1-(-2*x+2)**3/2
def ease_out_back(x, s=1.9):
    x = min(1, max(0, x)); c3 = s+1; return 1+c3*(x-1)**3+s*(x-1)**2
def ease_out(x):
    x = min(1, max(0, x)); return 1-(1-x)**3

# ---------- colour matching (gentle) ----------
def lut_gamma(g):
    x = np.arange(256)/255.0
    return np.stack([np.clip(255*x**gi, 0, 255).astype(np.uint8) for gi in g], 0)
LUTS = {'L': lut_gamma((0.64, 0.64, 0.67)),   # RGB: strong lift for backlit face (episode 2)
        'R': lut_gamma((1.04, 1.03, 1.02))}
from premium_grade import premium as _premium
def grade(img, k):
    return _premium(np.ascontiguousarray(img), k)
def grade_old(img, k):
    l = LUTS[k]
    out = np.empty_like(img)
    for c in range(3): out[..., c] = l[c][img[..., c]]
    return out

# ---------- face tracks ----------
def load_tracks():
    F = json.load(open(os.path.join(WDIR, 'faces.json')))
    t = np.array([r['t'] for r in F])
    tr = {}
    for k in 'LR':
        cx, cy, fh = [], [], []
        last = (402, 330, 300)
        for r in F:
            b = r[k]
            if b:
                x, y, w, h = b; last = (x+w/2, y+h/2, h)
            cx.append(last[0]); cy.append(last[1]); fh.append(last[2])
        arr = np.array([cx, cy, fh], float)
        # median + smoothing (about 1.2 s window) to avoid jitter
        from numpy.lib.stride_tricks import sliding_window_view as sw
        pad = 3
        arr = np.stack([np.median(sw(np.pad(a, pad, mode='edge'), 2*pad+1), 1) for a in arr])
        ker = np.ones(9)/9
        arr = np.stack([np.convolve(np.pad(a, 4, mode='edge'), ker, 'valid') for a in arr])
        tr[k] = arr
    return t, tr
TT, TRK = load_tracks()
def focus(k, st):
    i = np.interp(st, TT, np.arange(len(TT)))
    a = TRK[k]; i0 = int(i); i1 = min(i0+1, a.shape[1]-1); f = i-i0
    return a[:, i0]*(1-f)+a[:, i1]*f

# ---------- source reader ----------
class Reader:
    """Sequential reader of the two panels at 30 fps for a source interval."""
    def __init__(self, t0, t1):
        x0 = PANEL['L'][0]; w = 1746; self.roff = PANEL['R'][0]-x0
        self.w = w
        cmd = ['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-i', SRC, '-t', f'{t1-t0+0.2:.3f}',
               '-vf', f'fps={FPS},crop={w}:{PH}:{x0}:{PANEL["L"][1]}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)
        self.last = None
    def next(self):
        n = self.w*PH*3
        b = self.p.stdout.read(n)
        if len(b) == n:
            self.last = np.frombuffer(b, np.uint8).reshape(PH, self.w, 3)
        f = self.last
        return {'L': grade(f[:, :PW], 'L'), 'R': grade(f[:, self.roff:self.roff+PW], 'R')}
    def close(self):
        self.p.stdout.close(); self.p.kill()

# ---------- background ----------
def make_bg():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    c0 = np.array([22, 8, 48]); c1 = np.array([58, 16, 110]); c2 = np.array([12, 6, 30])
    t = np.clip(0.6*y+0.4*x, 0, 1)[..., None]
    g = c0*(1-t)+c1*t
    v = np.clip(1-((x-0.5)**2+(y-0.45)**2)*1.3, 0.55, 1)[..., None]
    g = g*v+c2*(1-v)
    return g.astype(np.float32)
BG = make_bg()
def bg_frame(fi):
    img = BG.copy()
    # drifting dot grid
    off = (fi*0.6) % 48
    ys = np.arange(-48, H+48, 48)+off; xs = np.arange(-48, W+48, 48)+off*0.5
    out = img
    yy, xx = np.meshgrid(ys.astype(int), xs.astype(int), indexing='ij')
    m = (yy >= 0) & (yy < H-3) & (xx >= 0) & (xx < W-3)
    for dy in range(3):
        for dx in range(3):
            out[yy[m]+dy, xx[m]+dx] = out[yy[m]+dy, xx[m]+dx]*0.6+np.array([150, 90, 255])*0.4*0.35
    return out

# ---------- shapes ----------
@functools.lru_cache(64)
def rr_mask(w, h, r):
    m = Image.new('L', (w*2, h*2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w*2-1, h*2-1], r*2, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32)/255

def blend(dst, src_rgb, alpha, x, y):
    """alpha-blend src (h,w,3 float/uint8) with alpha (h,w) 0..1 onto dst float at x,y (clipped)."""
    h, w = alpha.shape
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x+w), min(H, y+h)
    if x1 <= x0 or y1 <= y0: return
    s = src_rgb[y0-y:y1-y, x0-x:x1-x].astype(np.float32); a = alpha[y0-y:y1-y, x0-x:x1-x, None]
    d = dst[y0:y1, x0:x1]
    d *= (1-a); d += s*a

def rgba_blend(dst, rgba, x, y, opacity=1.0):
    a = rgba[..., 3].astype(np.float32)/255*opacity
    blend(dst, rgba[..., :3], a, int(round(x)), int(round(y)))

@functools.lru_cache(64)
def glow_frame(w, h, r, col, thick, glow):
    pad = glow+thick+4
    im = Image.new('RGBA', (w+2*pad, h+2*pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if glow:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle([pad-thick, pad-thick, pad+w+thick, pad+h+thick], r+thick, outline=col+(255,), width=thick*2)
        g = g.filter(ImageFilter.GaussianBlur(glow/2))
        im = Image.alpha_composite(im, g)
        d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad-thick, pad-thick, pad+w+thick-1, pad+h+thick-1], r+thick, outline=col+(255,), width=thick)
    return np.asarray(im), pad

@functools.lru_cache(64)
def shadow(w, h, r, blur=26, op=150):
    pad = blur*2
    im = Image.new('L', (w+2*pad, h+2*pad), 0)
    ImageDraw.Draw(im).rounded_rectangle([pad, pad+14, pad+w, pad+h+14], r, fill=op)
    im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im).astype(np.float32)/255, pad

# ---------- presenter view ----------
def render_view(dst, panel, k, st, rect, zoom=1.0, headroom=0.42, bright=1.0, border=None, radius=40, shake=(0, 0), extra_scale=1.0):
    x, y, w, h = rect
    w = int(round(w)); h = int(round(h))
    if w < 8 or h < 8: return
    cx, cy, fh = focus(k, st)
    # biggest crop with dest aspect inside panel
    asp = w/h
    cw0 = min(PW, PH*asp); ch0 = cw0/asp
    z = zoom*extra_scale
    cw, ch = cw0/z, ch0/z
    # centre: face at 'headroom' fraction of crop height
    ccx = cx; ccy = cy - (headroom-0.5)*ch
    ccx = min(max(ccx, cw/2), PW-cw/2); ccy = min(max(ccy, ch/2), PH-ch/2)
    s = w/cw
    M = np.array([[s, 0, -(ccx-cw/2)*s+shake[0]], [0, s, -(ccy-ch/2)*s+shake[1]]], np.float32)
    img = cv2.warpAffine(panel, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    img = img.astype(np.float32)
    if bright != 1.0: img *= bright
    sh, sp = shadow(w, h, radius)
    blend(dst, np.zeros((sh.shape[0], sh.shape[1], 3), np.float32), sh, int(x)-sp, int(y)-sp)
    blend(dst, img, rr_mask(w, h, radius), int(x), int(y))
    if border:
        col, thick, glow = border
        g, pad = glow_frame(w, h, radius, col, thick, glow)
        rgba_blend(dst, g, int(x)-pad, int(y)-pad)

# ---------- text ----------
def text_img(txt, size, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), path=FONT_CAP, shadow_px=0, spacing=0):
    f = font(path, size)
    bb = f.getbbox(txt, stroke_width=stroke)
    w = bb[2]-bb[0]+stroke*2+shadow_px*2+8; h = bb[3]-bb[1]+stroke*2+shadow_px*2+8
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = -bb[0]+stroke+4, -bb[1]+stroke+4
    if shadow_px:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((ox+shadow_px, oy+shadow_px*1.4), txt, font=f, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(shadow_px*0.8))
        im = Image.alpha_composite(im, sh); d = ImageDraw.Draw(im)
    d.text((ox, oy), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def scale_rgba(im, s, rot=0):
    if s <= 0.01: return None
    w, h = im.size
    im2 = im.resize((max(1, int(w*s)), max(1, int(h*s))), Image.BICUBIC)
    if rot: im2 = im2.rotate(rot, Image.BICUBIC, expand=True)
    return im2

def paste_center(dst, im, cx, cy, opacity=1.0):
    if im is None: return
    a = np.asarray(im)
    rgba_blend(dst, a, cx-a.shape[1]/2, cy-a.shape[0]/2, opacity)

# ---------- emoji stickers ----------
@functools.lru_cache(None)
def emoji(code, size, outline=10):
    p = os.path.join(ASSETS, 'emoji', code+'.png')
    im = Image.open(p).convert('RGBA').resize((size, size), Image.LANCZOS)
    if not outline: return im
    pad = outline+12
    big = Image.new('RGBA', (size+2*pad, size+2*pad), (0, 0, 0, 0))
    big.paste(im, (pad, pad), im)
    a = big.split()[3]
    dil = a.filter(ImageFilter.MaxFilter(outline*2+1)).filter(ImageFilter.GaussianBlur(1.2))
    sh = dil.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v*0.45))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    shadow_l = Image.new('RGBA', big.size, (0, 0, 0, 255)); shadow_l.putalpha(sh)
    out = Image.alpha_composite(out, shadow_l.transform(big.size, Image.AFFINE, (1, 0, -4, 0, 1, -8)))
    white = Image.new('RGBA', big.size, (255, 255, 255, 255)); white.putalpha(dil)
    out = Image.alpha_composite(out, white)
    out = Image.alpha_composite(out, big)
    return out

@functools.lru_cache(None)
def label_sticker(txt, size=46, bg=YEL, fg=INK, path=FONT_DISP, pad=(26, 16), rot=-4, outline=True, emoji_code=None):
    f = font(path, size)
    lines = txt.split('\n')
    bbs = [f.getbbox(l) for l in lines]
    lw = max(b[2]-b[0] for b in bbs); lh = [b[3]-b[1] for b in bbs]
    gap = int(size*0.28)
    em = int(size*1.25) if emoji_code else 0
    w = lw+pad[0]*2+(em+14 if em else 0); h = sum(lh)+gap*(len(lines)-1)+pad[1]*2
    if em: h = max(h, em+pad[1]*2)
    m = 14
    im = Image.new('RGBA', (w+2*m, h+2*m), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([m+5, m+9, m+w+5, m+h+9], 22, fill=(0, 0, 0, 140))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(im)
    if outline: d.rounded_rectangle([m-5, m-5, m+w+5, m+h+5], 26, fill=(255, 255, 255, 255))
    d.rounded_rectangle([m, m, m+w, m+h], 22, fill=bg+(255,))
    x = m+pad[0]
    if em:
        e = emoji(emoji_code, em, 0); im.paste(e, (x, m+(h-em)//2), e); x += em+14
    y = m+pad[1]
    for l, b, hh in zip(lines, bbs, lh):
        d.text((x+(lw-(b[2]-b[0]))/2-b[0], y-b[1]), l, font=f, fill=fg)
        y += hh+gap
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    return im
