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
CL = {n: load_clip(n) for n in range(1, 9)}

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




# ---------------- archival grade: one consistent look for all colorised photographs ----------------
def g_arch(x, w=0.0):
    x = rolloff(x, .78)
    x = sat(x, .78 + .1 * max(w, 0))
    l = lum(x)[..., None]
    x = x * ((1 - l) * np.array([.97, 1.0, 1.04]) + l * np.array([1.03, 1.0, .95]))
    x = x * np.array([1 + .06 * w, 1 + .012 * w, 1 - .07 * w])
    x = x * .98 + .015
    return np.clip(scurve(np.clip(x, 0, 1), .8), 0, 1)

def S(t0, t1, clip, src, w=(0, 0), wt=None, z=(1.0, 1.05), c=(.5, .5, .5, .5), speed=1.0, tr=('cut', 0), vig=.38, grain=.03):
    return dict(t0=t0, t1=t1, clip=clip, src=src, w=w, wt=wt or (t0, t1), speed=speed, z=z, c=c, tr=tr, vig=vig, grain=grain)
SHOTS = [
 S(0.0, 4.05, 5, 0.0, (-.3, -.3), z=(1.0, 1.06)),                                    # POV into the ruins
 S(4.05, 9.0, 6, 0.0, (-.25, -.25), z=(1.0, 1.04), speed=.8),                         # street, minaret
 S(9.0, 12.0, 5, 4.05, (-.3, -.3), z=(1.0, 1.03)),                                    # arches, rubble
 S(12.0, 15.0, 7, 2.3, (-.2, -.2), z=(1.03, 1.07), speed=.9),                        # a ruined town
 S(15.0, 17.7, 4, 0.0, (-.15, -.15), z=(1.0, 1.05)),                                  # domed mosque
 S(17.7, 20.0, 7, 0.0, (-.2, -.2), z=(1.02, 1.05)),                                   # damaged domed building
 S(20.0, 24.0, 3, 0.0, (-.4, -.4), z=(1.5, 1.56), c=(.68, .62, .68, .6), speed=.75, tr=('diss', .5)),  # rubble only (child kept OUT of frame)
 S(24.0, 27.0, 2, 0.5, (-.35, -.35), z=(1.0, 1.04)),                                  # families in the ruined street
 S(27.0, 30.3, 8, 0.0, (-.6, -.6), z=(1.0, 1.04), tr=('diss', .5)),                  # winter tent camp
 S(30.3, 33.0, 4, 2.6, (-.4, -.4), z=(1.04, 1.08), speed=.9),                         # carrying from the ruins
 S(33.0, 39.0, 5, 7.05, (-.25, .35), wt=(36.6, 38.0), z=(1.0, 1.05), speed=.49, tr=('diss', .6)),  # rubble and minaret, no people (no photo of Ümmü exists here); warm light on "sağ çıxarıldı"
 S(39.0, 42.0, 1, 3.4, (.15, .15), z=(1.02, 1.06), speed=.53, tr=('diss', .4)),       # food crates
 S(42.0, 45.0, 8, 4.9, (.1, .1), z=(1.04, 1.08)),                                     # relief camp
 S(45.0, 48.2, 3, 2.1, (-.1, -.1), z=(1.5, 1.0), c=(.68, .62, .5, .5), tr=('diss', .5)),  # pull back: the child just outside the earlier frame
]
END_T0, END_SLIDE, LOGO_IN = 46.6, 47.62, 47.95

def shot_frame(s, t):
    cl = CL[s['clip']]
    st = (s['src'] + (t - s['t0']) * s['speed']) * 24
    i0 = min(max(int(st + 1e-6), 0), len(cl) - 1)
    x = cl[i0].astype(np.float32) / 255.
    if s['speed'] < 1 and i0 + 1 < len(cl):
        f = st - i0
        if f > .02: x = x * (1 - f) + cl[i0 + 1].astype(np.float32) / 255. * f
    q = np.clip((t - s['wt'][0]) / max(s['wt'][1] - s['wt'][0], 1e-3), 0, 1); q = q * q * (3 - 2 * q)
    x = g_arch(x, s['w'][0] + (s['w'][1] - s['w'][0]) * q)
    p = np.clip((t - s['t0']) / (s['t1'] - s['t0']), 0, 1.15)
    pe = p * p * (3 - 2 * p) if p <= 1 else p
    z = s['z'][0] + (s['z'][1] - s['z'][0]) * pe
    cx = s['c'][0] + (s['c'][2] - s['c'][0]) * pe; cy = s['c'][1] + (s['c'][3] - s['c'][1]) * pe
    sh, sw = x.shape[:2]
    sc = max(W / sw, H / sh) * z
    hw = W / sc / 2; hh = H / sc / 2
    px = min(max(cx * sw, hw), sw - hw); py = min(max(cy * sh, hh), sh - hh)
    M = np.array([[sc, 0, W / 2 - px * sc], [0, sc, H / 2 - py * sc]], np.float32)
    y = cv2.warpAffine(x, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.GaussianBlur(y, (0, 0), 1.6)
    return np.clip(y + (y - bl) * .4, 0, 1)

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
SUB_SIZE = 60; SUB_Y = 1478; SUB_MAXW = 930; LINE_H = 80
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




def T(txt, path, size, col, cx, y, t_in, t_out, track=0, fi=.4, fo=.35, top=True, align='c', op=1.0):
    return dict(ti=text_img(txt, path, size, col, track, shadow=.85, blur=12), cx=cx, y=y, t_in=t_in, t_out=t_out, fi=fi, fo=fo, top=top, align=align, op=op)
TITLES = [
 T('ŞAMAXI · 1902', F_INTB, 32, GOLD, 540, 252, -1, 3.95, track=16, fi=.01, fo=.25),
 T('4.000', F_PLAYB, 210, IVORY, 540, 286, -1, 3.95, fi=.01, fo=.25),
 T('5.000 EVDƏN', F_INTB, 34, GOLD, 540, 566, -1, 3.95, track=18, fi=.01, fo=.25),
 T('13 FEVRAL 1902-Cİ İL', F_INTB, 32, GOLD, 540, 262, 4.1, 8.95, track=14, fi=.3),
 T('ŞAMAXI İLƏ YANAŞI', F_INTB, 32, GOLD, 540, 262, 9.1, 14.95, track=16),
 T('KƏND', F_INTB, 36, GOLD, 540, 560, 12.55, 14.95, track=22),
 T('İNSAN HƏLAK OLDU', F_INTB, 32, GOLD, 540, 478, 22.3, 23.95, track=14),
 T('2.000-dən çox', F_PLAYB, 124, IVORY, 540, 300, 21.95, 23.95, fi=.6),
 T('20.000-ə yaxın', F_PLAYB, 124, IVORY, 540, 300, 24.1, 26.95, fi=.6),
 T('SAKİN EVSİZ QALDI', F_INTB, 32, GOLD, 540, 478, 24.5, 26.95, track=14),
 T('QIŞ · FEVRAL 1902', F_INTB, 30, GOLD, 540, 262, 27.15, 32.95, track=16),
 T('9 GÜN', F_PLAYB, 190, IVORY, 540, 282, 33.4, 38.95, track=4, fi=.5),
 T('SONRA', F_INTB, 32, GOLD, 540, 512, 33.9, 38.95, track=22),
 T('Ümmü', F_PLAYI, 120, GOLD, 540, 566, 35.15, 38.95, fi=.6),
 T('BAKIDAN YARDIM', F_INTB, 32, GOLD, 540, 262, 39.15, 44.95, track=16),
 T('Hacı Zeynalabdin Tağıyev', F_PLAYI, 64, IVORY, 540, 312, 42.05, 44.95, fi=.5),
 T('Arxiv fotoları süni intellektlə', F_INTM, 23, IVORY, 1026, 154, 39.0, 47.5, align='r', op=.72),
 T('rəngləndirilib və canlandırılıb.', F_INTM, 23, IVORY, 1026, 184, 39.0, 47.5, align='r', op=.72),
]
GOLDF = np.array(GOLD, np.float32) / 255.
_cnt = {}
def num_img(txt, size=200, col=IVORY):
    k = (txt, size, col)
    if k not in _cnt: _cnt[k] = text_img(txt, F_PLAYB, size, col, shadow=.85, blur=12)
    return _cnt[k]
def overlays(fr, t):
    if 4.1 <= t < 8.95:                       # the clock: 12:49 -> 12:50
        op = ease((t - 4.1) / .35) * (1 - ease((t - 8.6) / .35))
        ti = num_img('12:49' if t < 5.15 else '12:50', 190)
        blit(fr, ti, (W - ti['w']) / 2, 300 + (1 - ease((t - 4.1) / .35)) * 14, op)
    if 11.7 <= t < 14.95:                     # 0 -> 125 villages
        op = ease((t - 11.7) / .25) * (1 - ease((t - 14.6) / .35))
        p = min(max((t - 11.8) / .9, 0), 1); p = 1 - (1 - p) ** 3
        ti = num_img(str(int(round(125 * p))), 200, GOLD if p >= 1 else IVORY)
        blit(fr, ti, (W - ti['w']) / 2, 296, op)
FIN = [(text_img(w, F_PLAYI, 104, IVORY, shadow=0), t) for w, t in CHUNKS[-1] and [(w[0], w[1]) for w in CHUNKS[-1]]]
fsp = 30; fw = sum(f[0]['w'] for f in FIN) + fsp * 2
lg = np.asarray(Image.open('src/logo.png').convert('RGBA'), np.float32)[402 - 14:558 + 14, 126 - 14:833 + 14] / 255.
def logo_img(wd):
    hgt = int(lg.shape[0] * wd / lg.shape[1])
    r = cv2.resize(lg, (wd, hgt), interpolation=cv2.INTER_AREA)
    a = r[..., 3]
    sh = np.clip(cv2.GaussianBlur(a, (0, 0), wd / 40.) * 1.5, 0, 1) * .55
    return dict(a=np.pad(a, 40), sh=np.pad(sh, 40), col=np.array([1, 1, 1], np.float32) * .98, w=wd, h=hgt, pad=40)
LOGO_S = logo_img(236); LOGO_B = logo_img(720)
BG = (0.012, 0.011, 0.012)
FLASH = [(0.0, .45, .38), (5.15, .5, .22), (12.55, .3, .1), (36.8, 1.6, .0)]

def render(t, gi):
    act = [s for s in SHOTS if s['t0'] <= t < s['t1']]
    cur = act[-1] if act else None
    if cur is None:
        fr = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32)
    else:
        fr = shot_frame(cur, t)
        kind, d = cur['tr']; p = (t - cur['t0']) / d if d else 1
        if p < 1 and kind == 'diss':
            prev = SHOTS[SHOTS.index(cur) - 1]
            k = ease(p); fr = shot_frame(prev, t) * (1 - k) + fr * k
        fr *= (1 - cur['vig'] * VIG)[..., None]
        fr += GR[gi % 12] * cur['grain'] * (.35 + .65 * (1 - np.abs(lum(fr) - .45)[..., None]))
        for t0, d, a in FLASH:               # exposure flashes on the impacts (no shake)
            if a and t0 <= t < t0 + d:
                k = (1 - (t - t0) / d) ** 2 * a
                fr = fr + (1 - fr) * k * np.array([1, .96, .9], np.float32)
        if cur is SHOTS[-1] and t >= END_T0:   # the photograph shrinks and slides out
            p = ease((t - END_T0) / 1.1)
            sc = 1 - .2 * p; ang = -1.6 * p
            q = max((t - END_SLIDE) / .5, 0); q = q * q
            bw = int(12 * p)
            if bw > 0: cv2.rectangle(fr, (0, 0), (W - 1, H - 1), (.93, .9, .84), bw * 2)
            M = cv2.getRotationMatrix2D((W / 2, H / 2), ang - 5 * q, sc)
            M[1, 2] += -70 * p + 2300 * q; M[0, 2] += 160 * q
            fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=BG)
        fr *= 1 - BOT * (1.0 if t < END_SLIDE else 0)
        ta = 0.0
        for tt in TITLES:
            if tt['top'] and tt['t_in'] <= t < tt['t_out'] and tt['op'] >= 1:
                ta = max(ta, ease((t - tt['t_in']) / .5) * (1 - ease((t - (tt['t_out'] - .35)) / .35)))
        if 4.1 <= t < 15: ta = max(ta, .9)
        fr *= 1 - TOP * (.34 + .36 * ta) * (1.0 if t < END_T0 else 0)
    np.clip(fr, 0, 1, out=fr)
    overlays(fr, t)
    for tt in TITLES:
        if tt['t_in'] <= t < tt['t_out']:
            a = eout((t - tt['t_in']) / tt['fi']); o = 1 - ease((t - (tt['t_out'] - tt['fo'])) / tt['fo'])
            w = tt['ti']['w']; x = tt['cx'] - (w / 2 if tt['align'] == 'c' else 0 if tt['align'] == 'l' else w)
            blit(fr, tt['ti'], x, tt['y'] + (1 - a) * 14, a * o * tt['op'])
    draw_subs(fr, t)
    wm = 1 - ease((t - (END_T0 + .4)) / .5)
    blit(fr, LOGO_S, 54, 150, wm * .9)
    if t >= LOGO_IN:
        a = ease((t - LOGO_IN) / .9)          # the logo alone completes the sentence (no text)
        ly = (H - LOGO_B['h']) / 2 - 20
        blit(fr, LOGO_B, (W - LOGO_B['w']) / 2, ly + (1 - a) * 8, a)
        ln = ease((t - LOGO_IN - .6) / .8)
        if ln > 0:
            y0 = int(ly + LOGO_B['h'] + 40); hw = int(150 * ln)
            fr[y0:y0 + 2, 540 - hw:540 + hw] = fr[y0:y0 + 2, 540 - hw:540 + hw] * .2 + GOLDF * .8
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
