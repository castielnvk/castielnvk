import sys, subprocess, numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import common
from common import SKIP_SUBS, FPS, W, H, OFF, DUR, CHUNKS, CHUNK_END

PF = 'fonts/package/%s/PlayfairDisplay_%s.ttf'
F_PLAY = PF % ('500Medium', '500Medium'); F_PLAYI = PF % ('500Medium_Italic', '500Medium_Italic')
F_PLAYB = PF % ('700Bold', '700Bold')
F_INT = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'; F_INTB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
F_INTM = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
IVORY = (244, 238, 226); GOLD = (236, 200, 132)

# ---------------- clips ----------------
def load_clip(n):
    import glob; p = glob.glob(f'src/c{n:02d}.*')[0]
    info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                           '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip().split(',')
    w, h = int(info[0]), int(info[1])
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-map', '0:v:0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
CL = {n: load_clip(n) for n in range(1, 16)}

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



# ---------------- two worlds: past (warm, alive) / present (cold, dusty) ----------------
def g_past(x):
    x = rolloff(x, .8)
    x = sat(x, 1.0) * np.array([1.07, .985, .87]) * 1.03
    return np.clip(scurve(x, .9), 0, 1)
def g_now(x):
    x = rolloff(x, .78)
    x = sat(x, .58) * np.array([.93, .98, 1.05]) * .86 + .04
    return np.clip(scurve(x, .55), 0, 1)
def glow(x, amt):
    if amt <= .01: return x
    s = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(np.maximum(s - .55, 0), (0, 0), 9)
    s = cv2.resize(s, (W, H), interpolation=cv2.INTER_LINEAR)
    return np.clip(x + s * np.array([1.0, .82, .55], np.float32) * 1.25 * amt, 0, 1)

def S(t0, t1, clip, src, k=(1, 1), z=(1.0, 1.05), c=(.5, .5, .5, .5), speed=1.0, tr=('cut', 0), vig=.36, grain=.026, dim=0.0):
    return dict(t0=t0, t1=t1, clip=clip, src=src, k=k, speed=speed, z=z, c=c, tr=tr, vig=vig, grain=grain, dim=dim)
P, N = (0, 0), (1, 1)
SHOTS = [
 S(0.0, 3.62, 13, 0.0, N, (1.0, 1.07), vig=.5),
 S(3.62, 9.05, 10, 2.7, P, (1.04, 1.1), (.5, .45, .5, .4), tr=('bloom', .7)),
 S(9.05, 12.3, 4, 0.0, N, (1.0, 1.04), speed=.92),
 S(12.3, 15.15, 1, 0.0, (.85, .85), (1.0, 1.04)),
 S(15.15, 18.6, 5, 0.0, (.85, .85), (1.0, 1.04)),
 S(18.6, 22.6, 15, 3.3, (.85, .85), (1.0, 1.03)),
 S(22.6, 26.7, 6, 0.0, N, (1.0, 1.02), tr=('diss', .4), vig=.45),
 S(26.7, 32.6, 7, 0.0, (1, .3), (1.0, 1.03), speed=.98, vig=.45),
 S(32.6, 35.4, 9, 0.0, P, (1.0, 1.03), tr=('bloom', .6)),
 S(35.4, 37.3, 12, 3.5, P, (1.0, 1.03)),
 S(37.3, 40.0, 8, 0.0, P, (1.0, 1.03)),
 S(40.0, 42.8, 10, 0.0, P, (1.0, 1.04)),
 S(42.8, 45.85, 12, 0.0, P, (1.0, 1.03), dim=.42, speed=.95, tr=('diss', .35)),
 S(45.85, 50.15, 8, 3.2, P, (1.0, 1.04), tr=('diss', .35)),
 S(50.15, 55.75, 14, 0.0, (0, 1), (1.0, 1.05), tr=('diss', .6)),
 S(55.75, 56.85, 2, 0.0, N, (1.0, 1.02)),
 S(56.85, 58.65, 3, 0.0, N, (1.0, 1.03)),
 S(58.65, 60.75, 13, 3.6, N, (1.0, 1.03)),
 S(60.75, 64.4, 11, 0.0, N, (1.0, 1.04), vig=.42),
 S(64.4, 66.87, 11, 3.65, N, (1.28, 1.34), (.5, .3, .5, .28), vig=.42),
 S(66.87, 67.6, 10, 5.5, P, (1.06, 1.08), tr=('bloom', .22)),
 S(67.6, 68.2, 9, 3.2, P, (1.04, 1.06)),
 S(68.2, 68.92, 12, 3.0, P, (1.04, 1.06)),
 S(68.92, 70.68, 8, 4.2, P, (1.02, 1.05)),
 S(70.68, 78.15, 9, 1.0, N, (1.0, 1.06), speed=.67, vig=.55),
 S(78.15, 82.9, 5, 3.5, N, (1.0, 1.04), speed=.74, tr=('diss', .5)),
 S(82.9, 87.0, 1, 2.0, N, (1.0, 1.04)),
]
SPLIT_PAST = S(73.5, 78.15, 10, 3.6, P, (1.08, 1.12), (.5, .42, .5, .4), speed=.8)
SPLIT_T0 = 73.53
END_T0, END_SLIDE, FIN_OUT, LOGO_IN = 82.95, 84.56, 88.0, 88.6

def shot_frame(s, t):
    cl = CL[s['clip']]
    st = (s['src'] + (t - s['t0']) * s['speed']) * 24
    i0 = min(max(int(st + 1e-6), 0), len(cl) - 1)
    x = cl[i0].astype(np.float32) / 255.
    if s['speed'] < 1 and i0 + 1 < len(cl):
        f = st - i0
        if f > .02: x = x * (1 - f) + cl[i0 + 1].astype(np.float32) / 255. * f
    p = np.clip((t - s['t0']) / (s['t1'] - s['t0']), 0, 1.15)
    k = s['k'][0] + (s['k'][1] - s['k'][0]) * min(p, 1)
    k = k * k * (3 - 2 * k)
    if k >= .999: x = g_now(x)
    elif k <= .001: x = g_past(x)
    else: x = g_past(x) * (1 - k) + g_now(x) * k
    z = s['z'][0] + (s['z'][1] - s['z'][0]) * p
    cx = s['c'][0] + (s['c'][2] - s['c'][0]) * p; cy = s['c'][1] + (s['c'][3] - s['c'][1]) * p
    sh, sw = x.shape[:2]
    sc = max(W / sw, H / sh) * z
    hw = W / sc / 2; hh = H / sc / 2
    px = min(max(cx * sw, hw), sw - hw); py = min(max(cy * sh, hh), sh - hh)
    M = np.array([[sc, 0, W / 2 - px * sc], [0, sc, H / 2 - py * sc]], np.float32)
    y = cv2.warpAffine(x, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.GaussianBlur(y, (0, 0), 1.6)
    y = np.clip(y + (y - bl) * .4, 0, 1)
    warm = 1 - k
    if warm > .01:
        y = glow(y, warm * .9)
        y = np.clip(y * (1 + warm * .018 * math.sin(t * 2 * math.pi * .9) + warm * .01 * math.sin(t * 2 * math.pi * 2.3)), 0, 1)
    if s['dim']: y = y * (1 - s['dim'])
    return y

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
    if ci in SKIP_SUBS: continue
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
 T('BAKININ MƏRKƏZİNDƏ', F_INTB, 30, GOLD, 540, 266, -1, 3.45, track=14, fi=.01, fo=.25),
 T('Bura bir vaxtlar', F_PLAYI, 78, IVORY, 540, 318, -1, 3.45, fi=.01, fo=.25),
 T('NƏ İDİ?', F_PLAYB, 124, GOLD, 540, 410, -1, 3.45, fi=.01, fo=.25),
 T('BAKI', F_INTB, 30, GOLD, 540, 292, 12.35, 15.05, track=18),
 T('«Fantaziya»', F_PLAYI, 132, IVORY, 540, 334, V(12.62), 15.05, fi=.35),
 T('HAMAMI', F_INTB, 34, GOLD, 540, 528, V(13.46), 15.05, track=22),
 T('XIX', F_PLAYB, 190, IVORY, 540, 282, V(15.5), 18.5),
 T('ƏSRİN SONLARI', F_INTB, 30, GOLD, 540, 540, V(16.5), 18.5, track=16),
 T('İlk Avropa tipli', F_PLAYI, 70, IVORY, 540, 300, V(19.46), 22.5),
 T('hamamlardan biri', F_PLAYI, 70, GOLD, 540, 386, V(20.44), 22.5),
 T('MƏNBƏLƏRƏ GÖRƏ', F_INTB, 30, GOLD, 110, 268, V(32.63), 42.65, track=14, align='l'),
 T('01', F_INTB, 30, GOLD, 110, 352, V(34.02), 42.65, align='l'),
 T('Fəvvarəli zal', F_PLAYI, 62, IVORY, 172, 330, V(34.02), 42.65, align='l'),
 T('02', F_INTB, 30, GOLD, 110, 432, V(35.61), 42.65, align='l'),
 T('Dəbdəbəli interyer', F_PLAYI, 62, IVORY, 172, 410, V(35.61), 42.65, align='l'),
 T('03', F_INTB, 30, GOLD, 110, 512, V(37.22), 42.65, align='l'),
 T('Müalicəvi vannalar', F_PLAYI, 62, IVORY, 172, 490, V(37.22), 42.65, align='l'),
 T('«Fantaziya»', F_PLAYI, 128, IVORY, 540, 780, V(42.98), 45.75, top=False),
 T('adi hamam deyildi.', F_PLAYB, 82, GOLD, 540, 948, V(44.38), 45.75, top=False),
 T('2012', F_PLAYB, 200, IVORY, 540, 278, V(55.93), 60.65),
 T('İSTİFADƏSİZ', F_INTB, 34, GOLD, 540, 548, V(59.0), 60.65, track=20),
 T('TARİXİ ABİDƏ', F_INTB, 30, GOLD, 540, 292, V(60.85), 66.8, track=16),
 T('baxımsız · yarıuçuq', F_PLAYI, 72, IVORY, 540, 340, V(63.24), 66.8),
 T('İşıq.', F_PLAYI, 96, IVORY, 540, 290, V(66.72), 70.69, fi=.2, fo=.01),
 T('Su.', F_PLAYI, 96, IVORY, 540, 392, V(67.46), 70.69, fi=.2, fo=.01),
 T('Səs.', F_PLAYI, 96, IVORY, 540, 494, V(68.06), 70.69, fi=.2, fo=.01),
 T('İnsanlar.', F_PLAYI, 96, GOLD, 540, 596, V(68.78), 70.69, fi=.2, fo=.01),
 T('KEÇMİŞ', F_INTB, 30, GOLD, 540, 892, V(73.94), 78.1, track=20, top=False),
 T('BU GÜN', F_INTB, 30, IVORY, 540, 992, V(75.32), 78.1, track=20, top=False),
]
GOLDF = np.array(GOLD, np.float32) / 255.
FIN = [(text_img(w, F_PLAYI, 104, IVORY, shadow=0), V(t)) for w, t in [('kadr', 84.91), ('xaricində', 85.16), ('qaldı.', 85.82)]]
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
WARMF = np.array([1.0, .78, .48], np.float32)

def render(t, gi):
    act = [s for s in SHOTS if s['t0'] <= t < s['t1']]
    if not act:
        fr = np.zeros((H, W, 3), np.float32); cur = None
    else:
        cur = act[-1]
        fr = shot_frame(cur, t)
        kind, d = cur['tr']; p = (t - cur['t0']) / d if d else 1
        if p < 1 and kind in ('diss', 'bloom'):
            prev = SHOTS[SHOTS.index(cur) - 1]
            k = ease(p); fr = shot_frame(prev, t) * (1 - k) + fr * k
            if kind == 'bloom':     # entering memory: a soft wash of warm light
                b = math.sin(math.pi * min(max(p, 0), 1)) ** 1.5
                fr = np.clip(fr + WARMF * .55 * b + fr * .3 * b, 0, 1)
        if SPLIT_T0 <= t < 78.15:    # the past slides in above the present
            a = ease((t - SPLIT_T0) / .7)
            top = shot_frame(SPLIT_PAST, t)[480:1440]
            spl = np.vstack([top, fr[480:1440]])
            spl[957:963] = GOLDF * .9
            fr = fr * (1 - a) + spl * a
        fr *= (1 - cur['vig'] * VIG)[..., None]
        fr += GR[gi % 12] * cur['grain'] * (.35 + .65 * (1 - np.abs(lum(fr) - .45)[..., None]))
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
        fr *= 1 - TOP * (.30 + .36 * ta)
    np.clip(fr, 0, 1, out=fr)
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
