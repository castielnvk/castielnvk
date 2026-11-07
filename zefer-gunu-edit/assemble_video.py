"""Builds the graded 1080x1920 picture timeline (no text) for the 'Zəfər Günü' edit.

Source: 16:9 vMix programme captured as an iPhone screen recording (rotated landscape, 2622x1206,
programme area x 239..2382). Cameras in the recording:
  CU    0.00 - 44.39  Elnarə close-up          (President's speech is audio over this shot)
  WIDE 44.39 - 98.20  studio wide (guests)     -> tight crop on Elnarə only
  SPLIT 98.20 - end   three-way split          -> Elnarə's centre panel only
Edit decision list (output time OT, all points on the 30 fps grid):
  OT   0.0000 -  59.4000  src = OT                     protected opening, untouched order
  OT  59.4000 -  61.8000  title break (flag scene, no speech)
  OT  61.8000 - 106.0333  src = OT - 2.4               (src 59.4000 - 103.6333)
  OT 106.0333 - 120.4000  src = OT + 0.4667            (src 106.5000 - 120.8667)  trimmed repetition
  OT 120.4000 - 128.8000  end card
"""
import json, subprocess, sys, numpy as np, cv2

FPS, W, H = 30, 1080, 1920
SRC_W, SRC_H = 2622, 1206
PROG_X0, PROG_X1, BANNER_Y = 239, 2382, 1020
TOTAL = 128.8
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
cu = [(t, x, y) for t, x, y, w, s in faces if t < 44.3 and w > 150 and s > 0.8]
ts = np.array([c[0] for c in cu]); xs = np.array([c[1] for c in cu], float)
grid = np.arange(0, 44.5, 1 / FPS)
med = np.array([np.median(xs[(ts > g - 0.6) & (ts < g + 0.6)]) if ((ts > g - 0.6) & (ts < g + 0.6)).any() else np.nan for g in grid])
idx = np.arange(len(med)); good = ~np.isnan(med)
med = np.interp(idx, idx[good], med[good])
def ema(v, tau):
    a = 1 - np.exp(-1 / (FPS * tau)); o = v.copy()
    for i in range(1, len(o)): o[i] = o[i - 1] + a * (v[i] - o[i - 1])
    for i in range(len(o) - 2, -1, -1): o[i] = o[i + 1] + a * (o[i] - o[i + 1])
    return o
cu_x = ema(med, 0.9)

def crop_rect(src_t):
    """returns (cx, cy, crop_h) in source coords; crop_w = crop_h * 9/16"""
    if src_t < 44.39:                                           # CU
        x = float(np.interp(src_t, grid, cu_x))
        z = 1.0 + 0.06 * smoothstep(1.0, 31.0, src_t) + 0.035 * smoothstep(35.4, 44.3, src_t)
        h = 1020 / z
        cy = 510 + (600 - 510) * (1 - 1 / z)
        return x + 20, cy, h
    if src_t < 98.2:                                            # WIDE, tight on Elnarə
        if src_t < 59.4:   h = lerp(680, 610, smoothstep(44.39, 59.4, src_t))
        elif src_t < 69.2: h = lerp(640, 600, smoothstep(59.4, 69.2, src_t))
        elif src_t < 87.0: h = lerp(660, 600, smoothstep(73.0, 87.0, src_t))
        else:              h = lerp(560, 530, smoothstep(87.0, 98.2, src_t))   # punch-in on "amma 6 il..."
        return 1512, 468 - 0.38 * h + h / 2, h
    # SPLIT – centre panel x 1017..1603, y 142..998
    if src_t < 103.7: h = lerp(850, 800, smoothstep(98.2, 103.7, src_t))
    else:             h = lerp(700, 625, smoothstep(106.5, 120.9, src_t))
    w = h * 9 / 16
    cx = np.clip(1455 - 0.58 * w + w / 2, 1017 + w / 2, 1603 - w / 2)
    cy = np.clip(560 - 0.40 * h + h / 2, 142 + h / 2, 998 - h / 2)
    return cx, cy, h

def render_crop(frame, cx, cy, ch):
    cw = ch * 9 / 16
    # keep inside programme area and above the station banner
    cx = float(np.clip(cx, PROG_X0 + cw / 2, PROG_X1 - cw / 2))
    cy = float(np.clip(cy, ch / 2, BANNER_Y - ch / 2)) if ch <= BANNER_Y else BANNER_Y / 2
    s = W / cw
    M = np.array([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]], np.float32)
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)

# ---------- grade ----------
def build_lut():
    x = np.arange(256) / 255.0
    y = x.copy()
    y = y + 0.035 * np.sin(np.pi * (x - 0.08) / 0.84) * (x > 0.08) * (x < 0.92)   # gentle S / mid lift
    knee = 0.80                                                                     # highlight roll-off
    over = np.clip(y - knee, 0, None)
    y = np.where(y > knee, knee + over / (1 + over / 0.16), y)
    y = 0.012 + y * (1 - 0.012)                                                     # keep shadow detail (no crush)
    return np.clip(y * 255, 0, 255).astype(np.uint8)
LUT = build_lut()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.20 * np.clip(np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2) - 0.45, 0, 1) ** 1.6)[..., None]
rng = np.random.default_rng(3)
GRAIN = [rng.normal(0, 3.0, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]

def grade(img):
    img = cv2.LUT(img, LUT)
    f = img.astype(np.float32)
    # restrained warmth in mids, a whisper of depth in shadows
    lum = (0.2126 * f[..., 0] + 0.7152 * f[..., 1] + 0.0722 * f[..., 2])[..., None] / 255.0
    mid = 4 * lum * (1 - lum)
    f = f * (1 + np.array([0.012, 0.0, -0.014], np.float32) * mid) + np.array([-1.5, 0.0, 1.8], np.float32) * (1 - lum) ** 3
    # luminous highlight bloom
    hi = np.clip(f - 205, 0, None)
    bloom = cv2.GaussianBlur(cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 9)
    f = f + 0.22 * cv2.resize(bloom, (W, H), interpolation=cv2.INTER_LINEAR)
    # clarity: mild luma sharpening after the upscale
    blur = cv2.GaussianBlur(f, (0, 0), 1.6)
    f = f + 0.45 * (f - blur)
    f = f * VIG
    return f

def finish(f, k):
    g = cv2.resize(GRAIN[k % 8], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return np.clip(f + g, 0, 255).astype(np.uint8)

# ---------- readers ----------
class SrcReader:
    def __init__(self, path):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={FPS}', '-f', 'rawvideo',
                                   '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        self.idx = -1; self.cur = None
    def get(self, src_t):
        want = F(src_t)
        while self.idx < want:
            buf = self.p.stdout.read(SRC_W * SRC_H * 3)
            if len(buf) < SRC_W * SRC_H * 3: break
            self.cur = np.frombuffer(buf, np.uint8).reshape(SRC_H, SRC_W, 3); self.idx += 1
        return self.cur

class ClipReader:
    def __init__(self, path): self.cap = cv2.VideoCapture(path); self.idx = -1; self.cur = None
    def get(self, t):
        want = F(t)
        while self.idx < want:
            ok, fr = self.cap.read()
            if not ok: break
            self.cur = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB); self.idx += 1
        return self.cur

if len(sys.argv) > 5:          # preview mode: python assemble_video.py SRC FACES SCENES OUTDIR preview t1,t2,...
    for t in [float(v) for v in sys.argv[6].split(',')]:
        st = ot_to_src(t)
        fr = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{st:.3f}', '-i', sys.argv[1], '-frames:v', '1', '-f', 'rawvideo',
                             '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        fr = np.frombuffer(fr, np.uint8).reshape(SRC_H, SRC_W, 3)
        img = finish(grade(render_crop(fr, *crop_rect(st))), 0)
        cv2.imwrite(f'{sys.argv[4]}/prev_{t:06.2f}.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    sys.exit(0)

src = SrcReader(sys.argv[1])
scenes = sys.argv[3]
title = ClipReader(f'{scenes}/flag_title.mp4')     # OT 59.4 - 65.6
dawn = ClipReader(f'{scenes}/flag_dawn.mp4')       # OT 71.6 - 76.2
endc = ClipReader(f'{scenes}/flag_end.mp4')        # OT 120.4 - 128.8

TITLE_IN, TITLE_OUT = 59.4, 65.6
DAWN_IN, DAWN_OUT = 71.6, 76.2
END_IN = 120.4
XF = 0.40   # dissolve length

out = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '13', '-pix_fmt', 'yuv420p',
                        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', sys.argv[4]],
                       stdin=subprocess.PIPE)
last_her = None
n = F(TOTAL)
for k in range(n):
    ot = k / FPS
    st = ot_to_src(ot)
    her = None
    if st is not None:
        fr = src.get(st)
        her = grade(render_crop(fr, *crop_rect(st)))
        last_her = her
    def scene(reader, t0):
        return reader.get(ot - t0).astype(np.float32)
    if TITLE_IN <= ot < TITLE_OUT:
        img = scene(title, TITLE_IN)
        if ot < TITLE_IN + XF and last_her is not None:                       # dissolve in (from held last frame)
            a = smoothstep(TITLE_IN, TITLE_IN + XF, ot); img = lerp(last_her, img, a)
        if ot >= TITLE_OUT - XF and her is not None:                          # dissolve back to Elnarə
            a = smoothstep(TITLE_OUT - XF, TITLE_OUT, ot); img = lerp(img, her, a)
    elif DAWN_IN <= ot < DAWN_OUT:
        img = scene(dawn, DAWN_IN)
        if ot < DAWN_IN + XF: img = lerp(her, img, smoothstep(DAWN_IN, DAWN_IN + XF, ot))
        if ot >= DAWN_OUT - XF: img = lerp(img, her, smoothstep(DAWN_OUT - XF, DAWN_OUT, ot))
    elif ot >= END_IN:
        img = scene(endc, END_IN)
        if ot < END_IN + 0.7: img = lerp(last_her, img, smoothstep(END_IN, END_IN + 0.7, ot))
    else:
        img = her
    if ot < 0.6: img = img * smoothstep(0, 0.6, ot)                            # open from black
    out.stdin.write(finish(img, k).tobytes())
    if k % 300 == 0: print(f'{ot:6.1f}s', flush=True)
out.stdin.close(); out.wait()
print('done')
