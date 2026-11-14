import sys, subprocess, numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import common
from common import FPS, W, H, OFF, DUR, CHUNKS, CHUNK_END

common.snap_words('src/vo.mp3')
CHUNKS[36][1][1] = 62.98   # "gün"
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
CL = {n: load_clip(n) for n in range(1, 11)}

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
    elif g == 'soviet':
        x = sat(x, .8) * np.array([1.0, .985, .92])
        x = x * .9 + .035
        x = scurve(x, .7)
    return np.clip(x, 0, 1)

# ---------------- shots ----------------
# t0,t1, clip, src_in, speed, grade, (z0,z1), (cx0,cy0,cx1,cy1), trans(type,dur), flags
def S(t0, t1, clip, src, grade_, z=(1.0, 1.05), c=(.5, .5, .5, .5), speed=1.0, tr=('cut', 0), film=0.0, vig=.34, grain=.025):
    return dict(t0=t0, t1=t1, clip=clip, src=src, speed=speed, grade=grade_, z=z, c=c, tr=tr, film=film, vig=vig, grain=grain)
SHOTS = [
 S(0.0, 2.25, 1, 0.0, 'hook', (1.0, 1.05), tr=('fadein', .5), vig=.5, grain=.022),
 S(2.25, 6.15, 6, 0.2, 'sepia_soft', (1.22, 1.34), (.5, .40, .5, .36), tr=('leak', .5), film=1.0),
 S(6.15, 12.4, 3, 0.0, 'sepia', (1.0, 1.06), (.5, .5, .5, .47), tr=('diss', .5)),
 S(12.4, 19.85, 2, 0.4, 'sepia', (1.03, 1.10), (.5, .52, .47, .52)),
 S(19.85, 24.7, 4, 1.0, 'sepia_soft', (1.0, 1.06), (.5, .5, .5, .46), tr=('diss', .45)),
 S(24.7, 27.0, 7, 0.0, 'silver', (1.0, 1.03)),
 S(27.0, 32.0, 7, 2.3, 'silver', (1.16, 1.24), (.5, .56, .5, .6)),
 S(32.0, 37.7, 5, 0.0, 'sepia_soft', (1.0, 1.05), speed=.7, tr=('leak', .55), film=1.0),
 S(37.7, 44.15, 6, 1.5, 'sepia_soft', (1.0, 1.07), (.5, .5, .5, .46), film=1.0),
 S(44.15, 47.25, 5, 3.9, 'sepia_soft', (1.05, 1.10), (.5, .46, .5, .44), film=.8),
 S(47.25, 52.65, 9, 0.8, 'soviet', (1.0, 1.05), tr=('diss', .45), grain=.024),
 S(52.65, 61.65, 10, 0.0, 'silver', (1.0, 1.05), tr=('diss', .5)),
 S(61.2, 63.05, 8, 5.0, 'modern', (1.0, 1.03), tr=('wipe', .45), vig=.3, grain=.018),
 S(63.05, 66.3, 1, 1.0, 'modern', (1.04, 1.09), (.5, .52, .5, .5), vig=.3, grain=.018),
 S(66.3, 69.0, 8, 0.0, 'modern', (1.0, 1.05), vig=.34, grain=.018),
 S(67.6, 72.1, 6, 3.3, 'sepia_soft', (1.10, 1.18), (.5, .42, .5, .40), tr=('diss', 1.4), film=.8),
 S(72.1, 72.75, 3, 6.3, 'sepia', (1.08, 1.10), (.5, .48, .5, .48)),
 S(72.75, 73.3, 9, 6.6, 'soviet', (1.04, 1.06), grain=.024),
 S(73.3, 78.7, 1, 4.25, 'fade', (1.0, 1.05), vig=.3, grain=.02),
]

def shot_frame(s, t):
    cl = CL[s['clip']]
    st = s['src'] + (t - s['t0']) * s['speed']
    idx = min(max(int(st * 24 + 1e-6), 0), len(cl) - 1)
    x = cl[idx].astype(np.float32) / 255.
    k = 0.0
    if s['grade'] == 'fade':
        k = float(np.clip((t - 74.6) / 3.0, 0, 1))
    x = grade(x, s['grade'], k)
    if s['film'] > 0:      # projector flicker for the 1907 material
        fl = 1 + s['film'] * (.028 * math.sin(t * 2 * math.pi * 7.3) + .018 * math.sin(t * 2 * math.pi * 11.7 + 1))
        x = np.clip(x * fl, 0, 1)
    p = np.clip((t - s['t0']) / (s['t1'] - s['t0']), 0, 1.15)
    z = s['z'][0] + (s['z'][1] - s['z'][0]) * p
    cx = s['c'][0] + (s['c'][2] - s['c'][0]) * p; cy = s['c'][1] + (s['c'][3] - s['c'][1]) * p
    sh, sw = x.shape[:2]
    sc = max(W / sw, H / sh) * z
    # keep crop inside the source
    hw = W / sc / 2; hh = H / sc / 2
    px = min(max(cx * sw, hw), sw - hw); py = min(max(cy * sh, hh), sh - hh)
    M = np.array([[sc, 0, W / 2 - px * sc], [0, sc, H / 2 - py * sc]], np.float32)
    y = cv2.warpAffine(x, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.GaussianBlur(y, (0, 0), 1.6)
    y = np.clip(y + (y - bl) * .45, 0, 1)
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
SUB_SIZE = 56; SUB_Y = 1418; SUB_MAXW = 900; LINE_H = 76
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

# titles: (text, font, size, color, track, cx, y, t_in, t_out, kind)
def T(txt, path, size, col, cx, y, t_in, t_out, track=0, fi=.4, fo=.35, top=True):
    return dict(ti=text_img(txt, path, size, col, track, shadow=.8, blur=12), cx=cx, y=y, t_in=t_in, t_out=t_out, fi=fi, fo=fo, top=top)
V = lambda vo: vo + OFF
TITLES = [
 T('BAKI', F_INTM, 26, GOLD, 540, 318, 6.5, 12.2, track=14),
 T('1896', F_PLAY, 128, IVORY, 372, 352, V(7.06), 12.2),
 T('—', F_PLAY, 90, GOLD, 540, 372, V(8.2), 12.2),
 T('1898', F_PLAY, 128, IVORY, 708, 352, V(8.32), 12.2),
 T('MEMAR', F_INTM, 26, GOLD, 540, 318, V(12.2), V(15.3), track=14),
 T('Kazimir Skureviç', F_PLAYI, 76, IVORY, 540, 356, V(12.58), V(15.3)),
 T('1903', F_PLAY, 120, IVORY, 540, 1040, V(19.65), 24.55, top=False),
 T('Hacı Zeynalabdin Tağıyev', F_PLAYI, 58, GOLD, 540, 1190, V(21.32), 24.55, top=False),
 T('TAĞIYEV PASAJI', F_PLAY, 66, IVORY, 540, 352, V(24.41), 31.4, track=10),
 T('1907', F_PLAYB, 210, IVORY, 540, 300, V(31.7), 37.55, fi=.25),
 T('«Fransız Elektro-Bioqraf»', F_PLAYI, 64, GOLD, 540, 560, V(33.5), 37.55),
 T('KİNOTEATR', F_INTM, 26, IVORY, 540, 668, V(35.98), 37.55, track=14),
 T('«Təyyarə»', F_PLAYI, 104, IVORY, 540, 330, V(45.14), 47.1),
 T('SOVET DÖVRÜ', F_INTM, 26, GOLD, 540, 318, V(47.03), 52.5, track=14),
 T('Köhnə Univermaq', F_PLAYI, 76, IVORY, 540, 356, V(48.58), 52.5),
 T('BUM', F_PLAYB, 150, IVORY, 540, 452, V(50.4), 52.5, track=18, fi=.3),
 T('BU GÜN', F_INTM, 26, GOLD, 540, 318, 63.3, 66.15, track=14),
]
AI_TAG = text_img('Sİ ilə canlandırma', F_INTM, 23, IVORY, track=1, shadow=.6, blur=6)
FIN = [(text_img(w, F_PLAYI, 104, IVORY, shadow=0), V(t)) for w, t in [('kadr', 78.09), ('xaricində', 78.36), ('qaldı.', 79.02)]]
fsp = 30; fw = sum(f[0]['w'] for f in FIN) + fsp * 2
# logo
lg = np.asarray(Image.open('src/logo.png').convert('RGBA'), np.float32)[402 - 14:558 + 14, 126 - 14:833 + 14] / 255.
def logo_img(wd):
    hgt = int(lg.shape[0] * wd / lg.shape[1])
    r = cv2.resize(lg, (wd, hgt), interpolation=cv2.INTER_AREA)
    a = r[..., 3]
    sh = np.clip(cv2.GaussianBlur(a, (0, 0), wd / 40.) * 1.5, 0, 1) * .55
    return dict(a=np.pad(a, 40), sh=np.pad(sh, 40), col=np.array([1, 1, 1], np.float32) * .98, w=wd, h=hgt, pad=40)
LOGO_S = logo_img(236); LOGO_B = logo_img(700)

# ---------------- frame ----------------
def find(t):
    act = [s for s in SHOTS if s['t0'] <= t < s['t1']]
    return act

def render(t, gi):
    act = find(t)
    if not act:
        fr = np.zeros((H, W, 3), np.float32); cur = None
    else:
        cur = act[-1]
        fr = shot_frame(cur, t)
        kind, d = cur['tr']; p = (t - cur['t0']) / d if d else 1
        if p < 1:
            if kind == 'fadein': fr *= ease(p)
            elif kind in ('diss', 'wipe'):
                prev = act[-2] if len(act) > 1 else SHOTS[SHOTS.index(cur) - 1]
                pf = shot_frame(prev, t)
                if kind == 'diss':
                    k = ease(p); fr = pf * (1 - k) + fr * k
                else:
                    edge = -160 + (H + 320) * ease(p)
                    m = np.clip((edge - yy) / 160, 0, 1)[..., None]
                    fr = pf * (1 - m) + fr * m
                    fr *= 1 - .5 * np.clip(1 - np.abs(yy - edge) / 260, 0, 1)[..., None] * (1 - abs(2 * p - 1)) ** .5
        # vignette + grain
        fr *= (1 - cur['vig'] * VIG)[..., None]
        fr += GR[gi % 12] * cur['grain'] * (.35 + .65 * (1 - np.abs(lum(fr) - .45)[..., None]))
    # dip to black before 1907
    if 31.5 <= t < 32.0: fr *= 1 - ease((t - 31.5) / .38)
    # light leaks around leak cuts
    for s in SHOTS:
        if s['tr'][0] == 'leak':
            dt = t - s['t0']
            if -.22 < dt < .6:
                k = (1 - abs(dt) / .22) if dt < 0 else (1 - dt / .6) ** 2
                if s['t0'] > 30 and dt < 0: k = 0
                shift = int((dt + .1) * 900)
                fr += np.roll(LEAK, shift, axis=1) * k * .85
                fr *= 1 + .35 * k
    # final "photograph" leaving the frame
    if 74.8 <= t < 78.7 and cur is not None:
        p = ease((t - 74.8) / 2.6)
        sc = 1 - .22 * p; ang = -1.6 * p
        q = (t - 78.05) / .62; q = max(q, 0); q = q * q
        bw = int(12 * p)
        if bw > 0:
            cv2.rectangle(fr, (0, 0), (W - 1, H - 1), (.93, .9, .84), bw * 2)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), ang - 5 * q, sc)
        M[1, 2] += -70 * p + 2300 * q; M[0, 2] += 160 * q
        fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0.012, 0.011, 0.012))
    # scrims
    sub_on = any(s['t_in'] <= t < s['t_out'] for s in SUBS)
    if cur is not None:
        fr *= 1 - BOT * (1.0 if t < 77.9 else 0)
        ta = 0.0
        for tt in TITLES:
            if tt['top'] and tt['t_in'] <= t < tt['t_out']:
                ta = max(ta, ease((t - tt['t_in']) / .5) * (1 - ease((t - (tt['t_out'] - .35)) / .35)))
        fr *= 1 - TOP * (.30 + .30 * ta)
    np.clip(fr, 0, 1, out=fr)
    # titles
    for tt in TITLES:
        if tt['t_in'] <= t < tt['t_out']:
            a = eout((t - tt['t_in']) / tt['fi']); o = 1 - ease((t - (tt['t_out'] - tt['fo'])) / tt['fo'])
            blit(fr, tt['ti'], tt['cx'] - tt['ti']['w'] / 2, tt['y'] + (1 - a) * 16, a * o)
    draw_subs(fr, t)
    # final words
    if t >= FIN[0][1] - .1:
        x = (W - fw) / 2; out = 1 - ease((t - 80.35) / .6)
        for ti, tw in FIN:
            a = ease((t - (tw - .08)) / .5)
            blit(fr, ti, x, 880 + (1 - a) * 10, a * out); x += ti['w'] + fsp
    # watermark + AI tag
    wm = ease((t - .5) / .6) * (1 - ease((t - 77.9) / .5))
    blit(fr, LOGO_S, 54, 150, wm * .9)

    # end logo
    if t >= 81.05:
        a = ease((t - 81.05) / 1.1)
        blit(fr, LOGO_B, (W - LOGO_B['w']) / 2, 960 - LOGO_B['h'] / 2 - 10 + (1 - a) * 8, a)
        ln = ease((t - 81.7) / 1.0)
        if ln > 0:
            hw = int(150 * ln); fr[1078:1080, 540 - hw:540 + hw] = fr[1078:1080, 540 - hw:540 + hw] * (1 - .8) + np.array(GOLD, np.float32) / 255. * .8
    if t > DUR - .6: fr *= 1 - ease((t - (DUR - .6)) / .55)
    return fr

if __name__ == '__main__':
    out = sys.argv[1]
    if out.endswith('.jpg'):   # contact sheet of stills
        ts = [float(x) for x in sys.argv[2].split(',')]
        ims = [cv2.resize((render(t, int(t * FPS)) * 255).astype(np.uint8), (360, 640), interpolation=cv2.INTER_AREA) for t in ts]
        Image.fromarray(np.hstack(ims)).save(out, quality=88); sys.exit()
    t_a = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t_b = float(sys.argv[3]) if len(sys.argv) > 3 else DUR
    step = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709',
                           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-vf', 'scale=out_color_matrix=bt709:out_range=tv', out], stdin=subprocess.PIPE)
    for i in range(int(round(t_a * FPS)), int(round(t_b * FPS)), step):
        fr = render(i / FPS, i)
        ff.stdin.write((fr * 255 + .5).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
