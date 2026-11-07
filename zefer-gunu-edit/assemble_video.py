"""Builds the 1080x1920 picture (no text) for the 'Zəfər Günü' edit in a framed, premium layout:
a 1000x1250 (4:5) video panel with rounded corners, hairline gold border and soft shadow, on a deep
«Qəbul Vaxtı» teal background (#0B6E62 sampled from the programme graphics). Captions are added
later (captions.py) in the clean teal area below the panel.

Source: 16:9 vMix programme captured as an iPhone screen recording (rotated landscape, 2622x1206,
programme area x 239..2382, station banner from y~1027). Cameras:
  CU    0.00 - 44.39  Elnarə close-up          (President's speech is audio over this shot)
  WIDE 44.39 - 98.20  studio wide (guests)     -> 4:5 crop on Elnarə only
  SPLIT 98.20 - end   three-way split          -> Elnarə's centre panel only
Edit decision list (output time OT, all points on the 30 fps grid):
  OT   0.0000 -  59.4000  src = OT                     protected opening, untouched order
  OT  59.4000 -  61.8000  title break (flag scene, no speech)
  OT  61.8000 - 106.0333  src = OT - 2.4               (src 59.4000 - 103.6333)
  OT 106.0333 - 120.4000  src = OT + 0.4667            (src 106.5000 - 120.8667)  trimmed repetition
  OT 120.4000 - 128.8000  end card
Usage: [SR_ONNX=model.onnx] python assemble_video.py SRC FACES.json SCENES_DIR OUT.mp4 [preview t1,t2,..]
"""
import json, os, subprocess, sys, numpy as np, cv2

FPS, W, H = 30, 1080, 1920
PW, PH = 1000, 1250                      # video panel (4:5)
PX, PY = (W - PW) // 2, 262              # panel position
RADIUS = 30
SRC_W, SRC_H = 2622, 1206
PROG_X0, PROG_X1, BANNER_Y = 239, 2382, 1020
TOTAL = 128.8
ASPECT = PW / PH
F = lambda t: int(round(t * FPS))

def ot_to_src(ot):
    if ot < 59.4: return ot
    if ot < 61.8: return None
    if ot < 106.0333: return ot - 2.4
    if ot < 120.4: return ot + 0.4667
    return None

def smoothstep(a, b, t):
    x = np.clip((t - a) / (b - a), 0, 1); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x

# ---------- face track for the close-up (smoothed "camera operator" pan) ----------
faces = json.load(open(sys.argv[2]))
cu = [(t, x) for t, x, y, w, s in faces if t < 44.3 and w > 150 and s > 0.8]
ts = np.array([c[0] for c in cu]); xs = np.array([c[1] for c in cu], float)
grid = np.arange(0, 44.5, 1 / FPS)
win = lambda g: (ts > g - 0.6) & (ts < g + 0.6)
med = np.array([np.median(xs[win(g)]) if win(g).any() else np.nan for g in grid])
idx = np.arange(len(med)); good = ~np.isnan(med)
med = np.interp(idx, idx[good], med[good])
def ema(v, tau):
    a = 1 - np.exp(-1 / (FPS * tau)); o = v.copy()
    for i in range(1, len(o)): o[i] = o[i - 1] + a * (v[i] - o[i - 1])
    for i in range(len(o) - 2, -1, -1): o[i] = o[i + 1] + a * (o[i] - o[i + 1])
    return o
cu_x = ema(med, 1.1)

def crop_rect(st):
    """(cx, cy, crop_h, bounds) in source coords; crop_w = crop_h * 4/5. Wider framings than before."""
    if st < 44.39:                                                  # CU: full height above the banner
        z = 1.0 + 0.035 * smoothstep(1.0, 31.0, st) + 0.025 * smoothstep(35.4, 44.3, st)
        h = 1020 / z
        cy = 510 + (600 - 510) * (1 - 1 / z)
        return float(np.interp(st, grid, cu_x)) + 30, cy, h, (PROG_X0, 0, PROG_X1, BANNER_Y)
    if st < 98.2:                                                   # WIDE: Elnarə only
        if st < 59.4:   h = lerp(800, 760, smoothstep(44.39, 59.4, st))
        elif st < 69.2: h = lerp(780, 750, smoothstep(59.4, 69.2, st))
        elif st < 87.0: h = lerp(790, 740, smoothstep(73.0, 87.0, st))
        else:           h = lerp(700, 670, smoothstep(87.0, 98.2, st))     # gentle punch-in on "amma 6 il..."
        return 1500, 468 - 0.36 * h + h / 2, h, (1160, 0, 2382, BANNER_Y)   # x>=1160 keeps guests out
    # SPLIT – Elnarə's centre panel x 1017..1603, y 142..998
    h = lerp(732, 700, smoothstep(98.2, 103.7, st)) if st < 103.7 else lerp(680, 630, smoothstep(106.5, 120.9, st))
    return 1455 - 0.02 * h, 560 - 0.38 * h + h / 2, h, (1017, 142, 1603, 998)

SR_MODEL = None
SR_MIX = 0.6          # share of AI detail; the rest is a natural Lanczos resample (keeps skin honest)
def render_crop(frame, cx, cy, ch, bounds, use_sr=False):
    cw = ch * ASPECT
    bx0, by0, bx1, by1 = bounds
    cx = float(np.clip(cx, bx0 + cw / 2, bx1 - cw / 2)); cy = float(np.clip(cy, by0 + ch / 2, by1 - ch / 2))
    s = PW / cw
    M = np.array([[s, 0, PW / 2 - s * cx], [0, s, PH / 2 - s * cy]], np.float32)
    lan = cv2.warpAffine(frame, M, (PW, PH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    if not (use_sr and SR_MODEL):
        return lan
    x0 = max(0, int(cx - cw / 2) - 6); x1 = min(SRC_W, int(cx + cw / 2) + 7)
    y0 = max(0, int(cy - ch / 2) - 6); y1 = min(SRC_H, int(cy + ch / 2) + 7)
    pre = 0.72                                    # the stream itself is soft; SR from a 0.72x copy is as sharp, 2x faster
    small = cv2.resize(frame[y0:y1, x0:x1], None, fx=pre, fy=pre, interpolation=cv2.INTER_AREA)
    up = SR_MODEL(np.ascontiguousarray(small))    # 4x of the small copy -> 2.88x of the source crop
    k = 4 * pre                                   # SR px per source px
    sk = s / k
    # SR pixel u (centre) <-> source x0 + (u + 0.5)/k - 0.5
    M2 = np.array([[sk, 0, PW / 2 - s * (cx - x0) + s * (0.5 / k - 0.5)],
                   [0, sk, PH / 2 - s * (cy - y0) + s * (0.5 / k - 0.5)]], np.float32)
    srimg = cv2.warpAffine(up, M2, (PW, PH), flags=cv2.INTER_AREA if sk < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    return np.clip(SR_MIX * srimg + (1 - SR_MIX) * lan.astype(np.float32), 0, 255).astype(np.uint8)

# ---------- grade (panel) ----------
def build_lut():
    x = np.arange(256) / 255.0
    y = x + 0.035 * np.sin(np.pi * (x - 0.08) / 0.84) * (x > 0.08) * (x < 0.92)   # gentle S / mid lift
    knee = 0.80; over = np.clip(y - knee, 0, None)
    y = np.where(y > knee, knee + over / (1 + over / 0.16), y)                      # highlight roll-off
    y = 0.012 + y * (1 - 0.012)                                                     # no crushed blacks
    return np.clip(y * 255, 0, 255).astype(np.uint8)
LUT = build_lut()
pyy, pxx = np.mgrid[0:PH, 0:PW].astype(np.float32)
PVIG = (1 - 0.16 * np.clip(np.sqrt(((pxx - PW / 2) / (PW * 0.75)) ** 2 + ((pyy - PH * 0.45) / (PH * 0.7)) ** 2) - 0.45, 0, 1) ** 1.6)[..., None]

def grade(img, sharpen=0.35):
    f = cv2.LUT(img, LUT).astype(np.float32)
    lum = (0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2])[..., None] / 255.0
    f = f * (1 + np.array([0.012, 0.0, -0.014], np.float32) * 4 * lum * (1 - lum)) + np.array([-1.5, 0.0, 1.8], np.float32) * (1 - lum) ** 3
    hi = np.clip(f - 205, 0, None)
    bloom = cv2.GaussianBlur(cv2.resize(hi, (PW // 4, PH // 4), interpolation=cv2.INTER_AREA), (0, 0), 9)
    f = f + 0.20 * cv2.resize(bloom, (PW, PH), interpolation=cv2.INTER_LINEAR)
    blur = cv2.GaussianBlur(f, (0, 0), 1.4)
    f = f + sharpen * (f - blur)
    return f * PVIG

# ---------- premium teal background, shadow, frame ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def srgb2lin(c): c = np.asarray(c, np.float32) / 255; return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255
TEAL = srgb2lin([11, 110, 98]); DEEP = srgb2lin([2, 30, 30]); GLOW = srgb2lin([40, 150, 132])
r = np.sqrt(((xx - W * 0.5) / (W * 0.95)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2)[..., None]
BG_BASE = DEEP + (TEAL - DEEP) * np.clip(1.15 - r, 0, 1) ** 1.3
sat = (np.sin((xx * 0.7 + yy) * 0.018) * 0.5 + 0.5)[..., None]       # fine diagonal satin texture
BG_BASE = (BG_BASE * (1 + 0.035 * sat)).astype(np.float32)
def rounded_mask(w, h, rad, feather=1.2):
    qx = np.clip(np.abs(np.arange(w, dtype=np.float32) - (w - 1) / 2) - (w / 2 - rad), 0, None)
    qy = np.clip(np.abs(np.arange(h, dtype=np.float32) - (h - 1) / 2) - (h / 2 - rad), 0, None)
    d = np.sqrt(qx[None, :] ** 2 + qy[:, None] ** 2) - rad
    return np.clip(0.5 - d / feather, 0, 1).astype(np.float32)
PMASK = rounded_mask(PW, PH, RADIUS)
full_mask = np.zeros((H, W), np.float32); full_mask[PY:PY + PH, PX:PX + PW] = PMASK
SHADOW = cv2.GaussianBlur(np.roll(full_mask, 22, axis=0), (0, 0), 34)[..., None]
ring_outer = np.zeros((H, W), np.float32); ring_outer[PY - 6:PY + PH + 6, PX - 6:PX + PW + 6] = rounded_mask(PW + 12, PH + 12, RADIUS + 6)
RING = cv2.GaussianBlur(np.clip(ring_outer - cv2.dilate(full_mask, np.ones((3, 3))), 0, 1), (0, 0), 0.7)[..., None]
GOLD_SRGB = np.array([232, 199, 122], np.float32)
GLOW_DIR = (GLOW - TEAL * 0.5).astype(np.float32)
rng = np.random.default_rng(3)
GRAIN = [rng.normal(0, 2.6, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]
LIGHT_Y = np.exp(-((yy[:, :1] - 300) / 520) ** 2)

def background(t):
    lx = W * (0.25 + 0.5 * (0.5 + 0.5 * np.sin(t * 0.11)))           # very slow drifting light
    light = (LIGHT_Y * np.exp(-((xx[:1, :] - lx) / 700) ** 2))[..., None]
    return (BG_BASE + 0.10 * light * GLOW_DIR) * (1 - 0.55 * SHADOW)

def compose(panel_rgb_f, t, k, fade=1.0):
    """panel: PHxPWx3 float sRGB 0..255 -> full frame uint8"""
    canvas = lin2srgb(background(t)).astype(np.float32)
    canvas = canvas * (1 - 0.55 * RING) + 0.55 * RING * GOLD_SRGB
    m = PMASK[..., None]
    region = canvas[PY:PY + PH, PX:PX + PW]
    canvas[PY:PY + PH, PX:PX + PW] = region * (1 - m) + panel_rgb_f * m
    if fade < 1: canvas = canvas * fade
    g = cv2.resize(GRAIN[k % 8], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return np.clip(canvas + g, 0, 255).astype(np.uint8)

# ---------- readers ----------
class SrcReader:
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={FPS}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                  stdout=subprocess.PIPE)
        self.idx = -1; self.cur = None
    def get(self, st):
        want = F(st)
        while self.idx < want:
            buf = self.p.stdout.read(SRC_W * SRC_H * 3)
            if len(buf) < SRC_W * SRC_H * 3: break
            self.cur = np.frombuffer(buf, np.uint8).reshape(SRC_H, SRC_W, 3); self.idx += 1
        return self.cur

class ClipReader:
    """flag scenes are rendered full-frame 1080x1920; the panel shows their central 4:5 window"""
    def __init__(self, path): self.cap = cv2.VideoCapture(path); self.idx = -1; self.cur = None
    def get(self, t):
        want = F(t)
        while self.idx < want:
            ok, fr = self.cap.read()
            if not ok: break
            self.cur = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB); self.idx += 1
        y0 = (H - PH) // 2 + 40
        return self.cur[y0:y0 + PH, PX:PX + PW].astype(np.float32)

def her_panel(fr, st):
    sr_on = st >= 44.39
    return grade(render_crop(fr, *crop_rect(st), use_sr=sr_on), 0.15 if (sr_on and SR_MODEL) else 0.35)

if os.environ.get('SR_ONNX'):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sr import SR
    SR_MODEL = SR(os.environ['SR_ONNX'])

if len(sys.argv) > 5:          # preview stills
    for t in [float(v) for v in sys.argv[6].split(',')]:
        st = ot_to_src(t)
        b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{st:.3f}', '-i', sys.argv[1], '-frames:v', '1', '-f', 'rawvideo',
                            '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        fr = np.frombuffer(b, np.uint8).reshape(SRC_H, SRC_W, 3)
        img = compose(her_panel(fr, st), t, 0)
        cv2.imwrite(f'{sys.argv[4]}/prev_{t:06.2f}.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    sys.exit(0)

src = SrcReader(sys.argv[1])
scenes = sys.argv[3]
title = ClipReader(f'{scenes}/flag_title.mp4')     # OT 59.4 - 65.6
dawn = ClipReader(f'{scenes}/flag_dawn.mp4')       # OT 71.6 - 76.2
endc = ClipReader(f'{scenes}/flag_end.mp4')        # OT 120.4 - 128.8 (has its own fade-out)
TITLE_IN, TITLE_OUT, DAWN_IN, DAWN_OUT, END_IN, XF = 59.4, 65.6, 71.6, 76.2, 120.4, 0.40

out = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p',
                        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', sys.argv[4]], stdin=subprocess.PIPE)
last_her = None
for k in range(F(TOTAL)):
    ot = k / FPS
    st = ot_to_src(ot)
    her = None
    if st is not None:
        her = her_panel(src.get(st), st); last_her = her
    if TITLE_IN <= ot < TITLE_OUT:
        img = title.get(ot - TITLE_IN)
        if ot < TITLE_IN + XF: img = lerp(last_her, img, smoothstep(TITLE_IN, TITLE_IN + XF, ot))
        if ot >= TITLE_OUT - XF and her is not None: img = lerp(img, her, smoothstep(TITLE_OUT - XF, TITLE_OUT, ot))
    elif DAWN_IN <= ot < DAWN_OUT:
        img = dawn.get(ot - DAWN_IN)
        if ot < DAWN_IN + XF: img = lerp(her, img, smoothstep(DAWN_IN, DAWN_IN + XF, ot))
        if ot >= DAWN_OUT - XF: img = lerp(img, her, smoothstep(DAWN_OUT - XF, DAWN_OUT, ot))
    elif ot >= END_IN:
        img = endc.get(ot - END_IN)
        if ot < END_IN + 0.7: img = lerp(last_her, img, smoothstep(END_IN, END_IN + 0.7, ot))
    else:
        img = her
    fade = smoothstep(0, 0.7, ot) * (1 - smoothstep(TOTAL - 1.3, TOTAL - 0.05, ot))
    out.stdin.write(compose(img, ot, k, fade).tobytes())
    if k % 300 == 0: print(f'{ot:6.1f}s', flush=True)
out.stdin.close(); out.wait()
print('done')
