import sys, subprocess, numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import common
from common import FPS, W, H, OFF, DUR, CHUNKS, CHUNK_END

PF = 'fonts/package/%s/PlayfairDisplay_%s.ttf'
F_PLAY = PF % ('500Medium', '500Medium'); F_PLAYI = PF % ('500Medium_Italic', '500Medium_Italic')
F_PLAYB = PF % ('700Bold', '700Bold')
F_INT = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'; F_INTB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
F_INTM = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
IVORY = (244, 238, 226); GOLD = (236, 200, 132)

# ---------------- clips ----------------
def load_clip(n):
    p = f'src/c{n:02d}.mp4'
    info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                           '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip().split(',')
    w, h = int(info[0]), int(info[1])
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-map', '0:v:0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
CL = {n: load_clip(n) for n in range(1, 12)}

# ---------------- grades (float32 rgb 0..1) ----------------
def lum(x): return x[..., 0] * .2126 + x[..., 1] * .7152 + x[..., 2] * .0722
def sat(x, s):
    l = lum(x)[..., None]; return l + (x - l) * s
def scurve(x, k):
    return x + k * (x - .5) * (1 - 4 * (x - .5) ** 2) * -1 if False else np.clip(x + k * np.sin((x - .5) * 2 * np.pi) * -0.08, 0, 1)
def tone(x, amt, warm=1.0):
    l = lum(x)
    sh = np.array([.035, .028, .03]); mid = np.array([.50, .455 + .0 * warm, .40 if warm >= 1 else .44]); hi = np.array([.95, .915, .85 if warm >= 1 else .89])
    l3 = l[..., None]
    t = np.where(l3 < .5, sh + (mid - sh) * (l3 / .5), mid + (hi - mid) * ((l3 - .5) / .5))
    return x * (1 - amt) + t * amt
def rolloff(x, knee=.72):
    return np.where(x > knee, knee + (1 - knee) * np.tanh((x - knee) / (1 - knee) * 1.1) * .86, x)

def grade(x, g, k=0.0):
    if g == 'modern':
        x = sat(x, .78) * np.array([.95, .99, 1.04]) * .93
        x = scurve(rolloff(x, .78), 1.0)
    elif g == 'hook':
        x = sat(x, .6) * np.array([.92, .97, 1.05]) * .74
        x = scurve(rolloff(x, .7), 1.4)
    elif g == 'fade':      # modern -> forgotten monochrome, k 0..1
        a = sat(x, .78) * np.array([.95, .99, 1.04]) * .93
        a = scurve(rolloff(a, .78), 1.0)
        b = tone(a, 1.0, .5) * .82
        x = a * (1 - k) + b * k
    elif g == 'sepia':
        x = tone(rolloff(x, .74), .88) * .95
        x = scurve(x, 1.0)
    elif g == 'sepia_soft':    # already sepia sources: keep character, unify
        x = tone(x, .6) * .97
        x = scurve(x, .8)
    elif g == 'silver':     # b/w passage, slightly warm silver
        x = tone(rolloff(x, .70), .9, .5) * .94
        x = scurve(x, .9)
    elif g == 'ninety':
        x = sat(x, .72) * np.array([.97, .99, 1.02]) * .93
        x = scurve(rolloff(x, .74), .9)
    elif g == 'today':
        x = sat(x, .86) * np.array([.98, .99, 1.02]) * .9
        x = scurve(rolloff(x, .8), 1.0)
    elif g == 'soviet':
        x = sat(x, .8) * np.array([1.0, .985, .92])
        x = x * .9 + .035
        x = scurve(x, .7)
    return np.clip(x, 0, 1)


# ---------------- shots ----------------
def S(t0, t1, clip, src, grade_, z=(1.0, 1.05), c=(.5, .5, .5, .5), speed=1.0, tr=('cut', 0), film=0.0, vig=.34, grain=.025, photo=None, dim=0.0):
    return dict(t0=t0, t1=t1, clip=clip, src=src, speed=speed, grade=grade_, z=z, c=c, tr=tr, film=film, vig=vig, grain=grain, photo=photo, dim=dim)
SHOTS = [
 S(0.0, 4.9, 5, 3.1, 'sepia_soft', (1.32, 1.16), (.45, .62, .72, .66), film=.5),
 S(4.9, 9.55, 2, 0.6, 'today', (1.0, 1.04), vig=.26, grain=.014),
 S(9.55, 13.9, 10, 0.0, 'silver', (1.02, 1.10), (.5, .5, .5, .52), vig=.5),
 S(13.9, 16.05, 4, 0.0, 'sepia_soft', (1.0, 1.02), tr=('diss', .45), film=.5),
 S(16.05, 18.3, 4, 2.15, 'sepia_soft', (1.4, 1.46), (.5, .8, .5, .8), film=.5),
 S(18.3, 22.25, 5, 0.0, 'sepia_soft', (1.12, 1.2), (.45, .55, .5, .55), speed=.8, film=.5),
 S(22.25, 27.45, 6, 0.0, 'silver', (1.0, 1.06), (.5, .5, .5, .47), speed=.8, dim=.12),
 S(27.45, 32.35, 7, 0.0, 'silver', (1.0, 1.05), speed=.82),
 S(32.35, 37.1, 7, 4.0, 'silver', (1.3, 1.36), (.42, .62, .46, .62), speed=.85),
 S(37.1, 43.65, 6, 4.2, 'silver', (1.25, 1.36), (.5, .64, .5, .68), speed=.58, tr=('diss', .4), dim=.3),
 S(43.65, 47.25, 1, 0.0, 'soviet', (1.0, 1.03), tr=('diss', .6)),
 S(47.25, 49.45, 1, 3.6, 'soviet', (1.28, 1.33), (.45, .56, .5, .56)),
 S(49.45, 53.0, 8, 0.6, 'ninety', (1.0, 1.04)),
 S(53.0, 56.6, 8, 4.15, 'ninety', (1.3, 1.36), (.45, .62, .45, .62)),
 S(56.6, 61.2, 9, 0.0, 'ninety', (1.0, 1.04)),
 S(61.2, 65.4, 10, 5.0, 'silver', (1.0, 1.06), vig=.45),
 S(65.4, 70.15, 11, 0.6, 'silver', (1.0, 1.04), tr=('dip', .5)),
 S(70.15, 72.45, 11, 5.35, 'silver', (1.2, 1.25), (.5, .5, .5, .5)),
 S(72.45, 77.65, 3, 2.8, 'sepia_soft', (1.0, 1.10), (.5, .5, .58, .52), tr=('diss', .5), film=.4),
 S(77.65, 80.7, 2, 5.0, 'today', (1.04, 1.07), vig=.26, grain=.014),
 S(80.7, 83.95, 4, 4.4, 'sepia_soft', (1.0, 1.04), photo=-2.2),
 S(83.95, 86.8, 1, 5.6, 'soviet', (1.0, 1.04), photo=1.8),
 S(86.8, 89.3, 9, 4.6, 'ninety', (1.0, 1.03), photo=-1.2),
 S(89.3, 96.2, 5, 1.6, 'sepia_soft', (1.0, 1.05), (.6, .5, .62, .5), speed=.93, film=.4),
]
SPLIT_OLD = S(4.9, 9.55, 3, 0.0, 'sepia_soft', (1.0, 1.04), speed=.6, film=.4)
END_T0, END_SLIDE, FIN_OUT, LOGO_IN = 92.4, 95.05, 98.2, 98.85

def shot_frame(s, t):
    cl = CL[s['clip']]
    st = (s['src'] + (t - s['t0']) * s['speed']) * 24
    i0 = min(max(int(st + 1e-6), 0), len(cl) - 1)
    x = cl[i0].astype(np.float32) / 255.
    if s['speed'] < 1 and i0 + 1 < len(cl):
        f = st - i0
        if f > .02: x = x * (1 - f) + cl[i0 + 1].astype(np.float32) / 255. * f
    x = grade(x, s['grade'])
    if s['dim']: x = x * (1 - s['dim'])
    if s['film'] > 0:
        fl = 1 + s['film'] * (.028 * math.sin(t * 2 * math.pi * 7.3) + .018 * math.sin(t * 2 * math.pi * 11.7 + 1))
        x = np.clip(x * fl, 0, 1)
    p = np.clip((t - s['t0']) / (s['t1'] - s['t0']), 0, 1.15)
    z = s['z'][0] + (s['z'][1] - s['z'][0]) * p
    cx = s['c'][0] + (s['c'][2] - s['c'][0]) * p; cy = s['c'][1] + (s['c'][3] - s['c'][1]) * p
    sh, sw = x.shape[:2]
    sc = max(W / sw, H / sh) * z
    hw = W / sc / 2; hh = H / sc / 2
    px = min(max(cx * sw, hw), sw - hw); py = min(max(cy * sh, hh), sh - hh)
    M = np.array([[sc, 0, W / 2 - px * sc], [0, sc, H / 2 - py * sc]], np.float32)
    y = cv2.warpAffine(x, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.GaussianBlur(y, (0, 0), 1.6)
    return np.clip(y + (y - bl) * .45, 0, 1)

# ---------------- static layers ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
RAD = np.sqrt(((xx - W / 2) / (W * .78)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
VIG = np.clip((RAD - .45) / .75, 0, 1) ** 1.6
BOT = (np.clip((yy - 1080) / 620, 0, 1) ** 1.3 * .62)[..., None]
TOP = (np.clip((560 - yy) / 560, 0, 1) ** 1.4)[..., None]
rng = np.random.default_rng(7)
GR = []
for i in range(12):
    g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), .7)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    GR.append((g / g.std())[..., None])
LEAK = np.exp(-(((xx - W / 2) / 620) ** 2 + ((yy - H * .42) / 1100) ** 2))[..., None] * np.array([1.0, .58, .24], np.float32)

def ease(p): p = min(max(p, 0), 1); return p * p * (3 - 2 * p)
def eout(p): p = min(max(p, 0), 1); return 1 - (1 - p) ** 3

# ---------------- text ----------------
_fc = {}
def font(path, size):
    if (path, size) not in _fc: _fc[(path, size)] = ImageFont.truetype(path, size)
    return _fc[(path, size)]

def text_img(txt, path, size, color, track=0, shadow=.75, blur=9):
    f = font(path, size)
    widths = [f.getlength(ch) for ch in txt] if track else None
    tw = int(sum(widths) + track * (len(txt) - 1)) if track else int(f.getlength(txt))
    asc, desc = f.getmetrics(); pad = 40
    im = Image.new('L', (tw + pad * 2, asc + desc + pad * 2), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = pad
        for ch, wd in zip(txt, widths):
            d.text((x, pad), ch, font=f, fill=255); x += wd + track
    else:
        d.text((pad, pad), txt, font=f, fill=255)
    a = np.asarray(im, np.float32) / 255.
    sh = np.asarray(im.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.
    sh = np.clip(sh * 1.9, 0, 1) * shadow
    sh = np.roll(sh, 3, axis=0)
    return dict(a=a, sh=sh, col=np.array(color, np.float32) / 255., w=tw, h=asc + desc, pad=pad, asc=asc)

def blit(fr, ti, x, y, op=1.0):
    """x,y = top-left of text box (without pad)"""
    if op <= 0.003: return
    x0 = int(round(x)) - ti['pad']; y0 = int(round(y)) - ti['pad']
    a = ti['a']; sh = ti['sh']; h, w = a.shape
    xa, ya = max(x0, 0), max(y0, 0); xb, yb = min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb: return
    a = a[ya - y0:yb - y0, xa - x0:xb - x0, None] * op; sh = sh[ya - y0:yb - y0, xa - x0:xb - x0, None] * op
    reg = fr[ya:yb, xa:xb]
    reg *= (1 - sh)
    reg[:] = reg * (1 - a) + ti['col'] * a

# subtitles
SUB_SIZE = 70; SUB_Y = 1390; SUB_MAXW = 950; LINE_H = 92
SUBS = []
for ci, ch in enumerate(CHUNKS[:-1]):
    words = []
    for w, t, hl in ch:
        dim = text_img(w, F_INTB if hl else F_INT, SUB_SIZE, GOLD if hl else IVORY)
        words.append(dict(ti=dim, t=t + OFF, hl=hl))
    sp = font(F_INT, SUB_SIZE).getlength(' ')
    lines = [[]]; cw = 0
    for wd in words:
        if lines[-1] and cw + sp + wd['ti']['w'] > SUB_MAXW:
            lines.append([]); cw = 0
        cw += (sp if lines[-1] else 0) + wd['ti']['w']; lines[-1].append(wd)
    for wd, (w0, _, _) in zip(words, ch): wd['gap'] = 0 if w0.endswith('–') else sp
    if len(lines) == 2 and len(lines[1]) == 1 and len(lines[0]) > 2:   # avoid orphan
        lines[1].insert(0, lines[0].pop())
    ytop = SUB_Y - len(lines) * LINE_H / 2
    for li, ln in enumerate(lines):
        lw = sum(w['ti']['w'] + w['gap'] for w in ln) - ln[-1]['gap']; x = (W - lw) / 2
        for wd in ln:
            wd['x'] = x; wd['y'] = ytop + li * LINE_H; x += wd['ti']['w'] + wd['gap']
    t_in = ch[0][1] + OFF - .10
    t_out = CHUNKS[ci + 1][0][1] + OFF - .10 if ci + 1 < len(CHUNKS) - 1 else CHUNK_END[ci] + OFF + .25
    t_out = min(t_out, CHUNK_END[ci] + OFF + .55)
    SUBS.append(dict(words=words, t_in=t_in, t_out=t_out))

def draw_subs(fr, t):
    for s in SUBS:
        if s['t_in'] <= t < s['t_out']:
            a_in = eout((t - s['t_in']) / .16); a_out = 1 - ease((t - (s['t_out'] - .10)) / .10)
            op = a_in * a_out; dy = (1 - a_in) * 12
            for wd in s['words']:
                k = ease((t - (wd['t'] - .06)) / .14)
                blit(fr, wd['ti'], wd['x'], wd['y'] + dy, op * (.42 + .58 * k))


def T(txt, path, size, col, cx, y, t_in, t_out, track=0, fi=.4, fo=.35, top=True, align='c'):
    return dict(ti=text_img(txt, path, size, col, track, shadow=.8, blur=12), cx=cx, y=y, t_in=t_in, t_out=t_out, fi=fi, fo=fo, top=top, align=align)
V = lambda vo: vo + OFF
TITLES = [
 T('Bakıda tramvaylar', F_PLAYI, 78, IVORY, 540, 292, -1, 1.32, fi=.01, fo=.2),
 T('NİYƏ YOX OLDU?', F_PLAYB, 102, GOLD, 540, 392, -1, 1.32, fi=.01, fo=.2),
 T('117', F_PLAYB, 250, IVORY, 440, 270, V(1.24), 4.75, fi=.22),
 T('KM', F_PLAYB, 110, GOLD, 800, 398, V(1.9), 4.75, fi=.25),
 T('BU GÜN', F_INTB, 30, GOLD, 540, 1010, 5.1, 9.4, track=14, top=False),
 T('BİR VAXTLAR', F_INTB, 30, GOLD, 540, 300, 5.1, 9.4, track=14),
 T('80 İL', F_INTB, 40, GOLD, 540, 292, V(10.06), 13.75, track=18),
 T('NİYƏ YOX OLDU?', F_PLAYB, 102, IVORY, 540, 348, V(12.0), 13.75, fi=.3),
 T('1924', F_PLAYB, 190, IVORY, 540, 330, V(14.16), 18.15, fi=.3),
 T('8 FEVRAL', F_INTB, 40, GOLD, 540, 292, V(15.9), 18.15, track=18),
 T('İLK ELEKTRİK TRAMVAYI', F_INTM, 28, GOLD, 540, 318, V(19.58), 22.1, track=12),
 T('İLK MARŞRUT', F_INTM, 26, GOLD, 540, 300, 22.6, 27.3, track=14),
 T('Dəmiryol Vağzalı', F_PLAYI, 52, IVORY, 110, 352, V(23.64), 27.3, align='l'),
 T('Azneft meydanı', F_PLAYI, 52, IVORY, 970, 352, V(24.58), 27.3, align='r'),
 T('1939', F_PLAYB, 190, IVORY, 540, 280, V(36.96), 43.5, fi=.3),
 T('Bir gün sonuncu xətt də', F_PLAYI, 68, IVORY, 540, 300, V(43.9), 46.85),
 T('bağlanacaq…', F_PLAYB, 92, GOLD, 540, 388, V(44.7), 46.85),
 T('1960-cı illər', F_PLAYI, 84, IVORY, 540, 320, V(47.11), 52.0),
 T('1990-cı illər', F_PLAYI, 84, IVORY, 540, 320, V(56.48), 61.0),
 T('2004', F_PLAYB, 210, IVORY, 540, 280, V(65.82), 72.3, fi=.25),
 T('Xətai metrosu — Montin bazarı', F_PLAYI, 50, IVORY, 540, 540, V(67.36), 72.3),
 T('SONUNCU XƏTT', F_INTB, 34, GOLD, 540, 634, V(70.04), 72.3, track=16),
]
GOLDF = np.array(GOLD, np.float32) / 255.
_cnt = {}
def overlays(fr, t):
    # first route: schematic (not a geographic map)
    if 23.4 < t < 27.3:
        op = 1 - ease((t - 26.95) / .35)
        y = 470; x0, x1 = 130, 950
        p = ease((t - V(23.9)) / 1.0)
        xe = int(x0 + (x1 - x0) * p)
        a0 = ease((t - V(23.64)) / .3) * op
        fr[y - 2:y + 2, x0:xe] = fr[y - 2:y + 2, x0:xe] * (1 - .9 * op) + GOLDF * .9 * op
        cv2.circle(fr, (x0, y), 13, tuple(float(v) for v in GOLDF * a0 + fr[y, x0] * (1 - a0)), -1, cv2.LINE_AA)
        a1 = ease((t - V(24.75)) / .3) * op
        if a1 > 0: cv2.circle(fr, (x1, y), 13, tuple(float(v) for v in GOLDF * a1 + fr[y, x1] * (1 - a1)), -1, cv2.LINE_AA)
    # today: 117 km -> 0
    if 5.1 <= t < 9.4:
        op = ease((t - 5.1) / .4) * (1 - ease((t - 9.05) / .35))
        p = min(max((t - V(7.36)) / (V(8.25) - V(7.36)), 0), 1); p = p * p * (3 - 2 * p)
        n = int(round(117 * (1 - p)))
        k = ('d', n)
        if k not in _cnt: _cnt[k] = text_img(f'{n} KM', F_PLAYB, 170, GOLD if n == 0 else IVORY, shadow=.85, blur=14)
        ti = _cnt[k]; blit(fr, ti, (W - ti['w']) / 2, 690, op)
    # 1939: network length counter
    if V(39.1) <= t < 43.5:
        op = ease((t - V(39.1)) / .4) * (1 - ease((t - 43.15) / .35))
        p = min(max((t - V(39.3)) / (V(41.06) - V(39.3)), 0), 1); p = 1 - (1 - p) ** 2
        n = int(round(117 * p))
        y = 548; x0, x1 = 150, 930
        xe = int(x0 + (x1 - x0) * p)
        fr[y - 1:y + 1, x0:x1] = fr[y - 1:y + 1, x0:x1] * (1 - .35 * op) + .35 * op
        fr[y - 3:y + 3, x0:xe] = fr[y - 3:y + 3, x0:xe] * (1 - .95 * op) + GOLDF * .95 * op
        if n not in _cnt: _cnt[n] = text_img(f'{n} KM', F_PLAYB, 120, GOLD, shadow=.8, blur=12)
        ti = _cnt[n]; blit(fr, ti, (W - ti['w']) / 2, 580, op)
FIN = [(text_img(w, F_PLAYI, 104, IVORY, shadow=0), V(t)) for w, t in [('kadr', 95.44), ('xaricində', 95.72), ('qaldı.', 96.44)]]
fsp = 30; fw = sum(f[0]['w'] for f in FIN) + fsp * 2
lg = np.asarray(Image.open('src/logo.png').convert('RGBA'), np.float32)[402 - 14:558 + 14, 126 - 14:833 + 14] / 255.
def logo_img(wd):
    hgt = int(lg.shape[0] * wd / lg.shape[1])
    r = cv2.resize(lg, (wd, hgt), interpolation=cv2.INTER_AREA)
    a = r[..., 3]
    sh = np.clip(cv2.GaussianBlur(a, (0, 0), wd / 40.) * 1.5, 0, 1) * .55
    return dict(a=np.pad(a, 40), sh=np.pad(sh, 40), col=np.array([1, 1, 1], np.float32) * .98, w=wd, h=hgt, pad=40)
LOGO_S = logo_img(236); LOGO_B = logo_img(700)
BG = (0.012, 0.011, 0.012)

# ---------------- frame ----------------
def render(t, gi):
    act = [s for s in SHOTS if s['t0'] <= t < s['t1']]
    if not act:
        fr = np.zeros((H, W, 3), np.float32); cur = None
    else:
        cur = act[-1]
        fr = shot_frame(cur, t)
        kind, d = cur['tr']; p = (t - cur['t0']) / d if d else 1
        if p < 1:
            if kind == 'diss':
                prev = SHOTS[SHOTS.index(cur) - 1]
                k = ease(p); fr = shot_frame(prev, t) * (1 - k) + fr * k
            elif kind == 'dip':
                fr *= ease(p)
        if 4.9 <= t < 9.55:      # then / now: the past stays on top until it goes dark at "0 KM"
            old = shot_frame(SPLIT_OLD, t)
            k = 1 - .78 * ease((t - V(8.25)) / .7)
            oldc = old[400:1360]; g = oldc.mean(2, keepdims=True)
            fr = np.vstack([(oldc * k + g * (1 - k)) * (.35 + .65 * k), fr[480:1440]])
            fr[957:963] = GOLDF * .9
        fr *= (1 - cur['vig'] * VIG)[..., None]
        fr += GR[gi % 12] * cur['grain'] * (.35 + .65 * (1 - np.abs(lum(fr) - .45)[..., None]))
        nxt = SHOTS[SHOTS.index(cur) + 1] if SHOTS.index(cur) + 1 < len(SHOTS) else None
        if nxt and nxt['tr'][0] == 'dip' and nxt['t0'] - t < .3: fr *= 1 - ease(1 - (nxt['t0'] - t) / .3)
        if cur['photo'] is not None:      # "köhnə fotolarda": the shot becomes a print on a dark table
            q = eout((t - cur['t0']) / .5)
            cv2.rectangle(fr, (0, 0), (W - 1, H - 1), (.93, .9, .84), 30)
            M = cv2.getRotationMatrix2D((W / 2, H / 2), cur['photo'] * (.6 + .4 * q), .86 - .04 * q + .012 * (t - cur['t0']))
            M[1, 2] += -110
            fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=BG)
    # final photograph leaving the frame
    if END_T0 <= t and cur is not None and cur is SHOTS[-1]:
        p = ease((t - END_T0) / 2.4)
        sc = 1 - .22 * p; ang = -1.6 * p
        q = max((t - END_SLIDE) / .62, 0); q = q * q
        bw = int(12 * p)
        if bw > 0: cv2.rectangle(fr, (0, 0), (W - 1, H - 1), (.93, .9, .84), bw * 2)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), ang - 5 * q, sc)
        M[1, 2] += -70 * p + 2300 * q; M[0, 2] += 160 * q
        fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=BG)
    if cur is not None:
        fr *= 1 - BOT * (1.0 if t < END_SLIDE - .1 else 0)
        ta = 0.0
        for tt in TITLES:
            if tt['top'] and tt['t_in'] <= t < tt['t_out']:
                ta = max(ta, ease((t - tt['t_in']) / .5) * (1 - ease((t - (tt['t_out'] - .35)) / .35)))
        if cur['photo'] is None: fr *= 1 - TOP * (.30 + .34 * ta)
    np.clip(fr, 0, 1, out=fr)
    overlays(fr, t)
    for tt in TITLES:
        if tt['t_in'] <= t < tt['t_out']:
            a = eout((t - tt['t_in']) / tt['fi']); o = 1 - ease((t - (tt['t_out'] - tt['fo'])) / tt['fo'])
            w = tt['ti']['w']; x = tt['cx'] - (w / 2 if tt['align'] == 'c' else 0 if tt['align'] == 'l' else w)
            blit(fr, tt['ti'], x, tt['y'] + (1 - a) * 16, a * o)
    draw_subs(fr, t)
    if t >= FIN[0][1] - .1:
        x = (W - fw) / 2; out = 1 - ease((t - FIN_OUT) / .6)
        for ti, tw in FIN:
            a = ease((t - (tw - .08)) / .5)
            blit(fr, ti, x, 880 + (1 - a) * 10, a * out); x += ti['w'] + fsp
    wm = 1 - ease((t - (END_SLIDE - .15)) / .5)
    blit(fr, LOGO_S, 54, 150, wm * .9)
    if t >= LOGO_IN:
        a = ease((t - LOGO_IN) / 1.1)
        blit(fr, LOGO_B, (W - LOGO_B['w']) / 2, 960 - LOGO_B['h'] / 2 - 10 + (1 - a) * 8, a)
        ln = ease((t - LOGO_IN - .65) / 1.0)
        if ln > 0:
            hw = int(150 * ln); fr[1078:1080, 540 - hw:540 + hw] = fr[1078:1080, 540 - hw:540 + hw] * .2 + GOLDF * .8
    if t > DUR - .6: fr *= 1 - ease((t - (DUR - .6)) / .55)
    return fr

if __name__ == '__main__':
    out = sys.argv[1]
    t_a = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t_b = float(sys.argv[3]) if len(sys.argv) > 3 else DUR
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709',
                           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-vf', 'scale=out_color_matrix=bt709:out_range=tv', out], stdin=subprocess.PIPE)
    for i in range(int(round(t_a * FPS)), int(round(t_b * FPS))):
        ff.stdin.write((render(i / FPS, i) * 255 + .5).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
