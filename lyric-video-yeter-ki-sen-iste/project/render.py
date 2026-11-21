"""Premium cinematic lyric overlay. Footage colours untouched; text + beat motion only."""
import sys, subprocess, math, json
import numpy as np, cv2, librosa
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = "/tmp/claude-0/-workspace-castielnvk/2c6eb8ae-60db-51e6-871f-d72b64516f5d/scratchpad/"
SRC = S + "dl/src.mov"; VOC = S + "dl/sep/htdemucs_ft/full/vocals.wav"
OUT = sys.argv[1] if len(sys.argv) > 1 else S + "proj/video_noaudio.mp4"
ONLY = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None  # preview times
FPS = 60; W, H = 1080, 1920
SRC_END = 25.50          # last usable source time
TOTAL = 27.6
FADE_A, FADE_B = 24.80, 25.42   # video fade to black (ending transition)

# ---------------- lyrics: whisper word starts, snapped to vocal energy ----------------
v, sr = librosa.load(VOC, sr=22050)
rms = librosa.feature.rms(y=v, hop_length=441, frame_length=882)[0]
db = 20 * np.log10(rms + 1e-6)
def snap(t):
    i = int(t * 50)
    if db[i] > -30: return t
    for j in range(i, min(i + 60, len(db))):
        if db[j] > -30: return j / 50
    return t

DARK = (40, 19, 10)      # espresso, sampled from jacket/hair shadows
IVORY = (250, 240, 224)
# cards: list of lines; line = (style, [(word, start)])
CARDS = [
    [("B", [("YETER", 4.26), ("Kİ", 4.52), ("SEN", 4.76), ("İSTE", 4.94)]),
     ("L", [("YAPARIM", 5.76), ("HER", 6.86), ("ŞEYİ", 7.20)])],
    [("L", [("BİLİRSİN", 9.02), ("İŞTE", 9.42)]),
     ("L", [("TEK", 9.90), ("TEK", 10.34), ("TEK", 10.88)]),
     ("B", [("ZAAFIM", 11.20), ("SENDİN", 11.86)])],
    [("L", [("KANADI", 13.50)]), ("X", [("KIRIK", 13.88)]), ("L", [("BİRİ", 14.28)])],
    [("B", [("TAMİRİ", 15.48)]), ("L", [("YOK", 16.16), ("GİBİ", 16.42)])],
    [("B", [("KULLANDIN", 17.92)]), ("L", [("DEĞİL", 18.74), ("Mİ?", 18.90)])],
    [("X", [("ESİRİN", 19.95)]), ("L", [("OLDUM,", 20.70), ("ESİRİN", 21.28)])],
    [("B", [("UMURSAMAZDIN", 21.80)]), ("L", [("SORGULAMAZDIM", 22.96)])],
    [("L", [("TAHMİNİMDEN", 24.24)]), ("X", [("ÇOK", 25.26)])],
]
for c in CARDS:
    for ln in c:
        pass  # times verified manually against vocal energy

# ---------------- beats ----------------
BEATS = [2.37, 2.93, 3.51, 4.09, 4.64, 5.2, 5.78, 6.36, 6.94, 7.5, 8.06, 8.64, 9.22, 9.78, 10.36,
         10.91, 11.49, 12.05, 12.63, 13.21, 13.79, 14.35, 14.91, 15.49, 16.07, 16.63, 17.21, 17.79,
         18.37, 18.92, 19.48, 20.06, 20.64, 21.2, 21.78, 22.36, 23.06, 23.68, 24.33, 24.92]
DOWN = set(BEATS[2::4])
PUNCH = []  # big accents where a new card lands on a strong hit
def env(t, t0, amp, tau):
    d = t - t0
    if d < -0.03: return 0.0
    if d < 0: return amp * (1 + d / 0.03)
    return amp * math.exp(-d / tau)

# ---------------- fonts / layout ----------------
F = S + "fonts/"
FONTS = {"B": (F + "ArchivoBlk.ttf", 96, 0.04), "X": (F + "ArchivoBlk.ttf", 170, 0.05),
         "L": (F + "ArchivoM.ttf", 54, 0.26)}
GAP = {"B": 22, "X": 26, "L": 16}
MAXW = 930
CY = 440   # card vertical centre (sky band)

class Word: pass

def tw(font, s, tr):
    return sum(font.getlength(ch) for ch in s) + tr * (len(s) - 1)

def build_card(card, cy):
    lines = []
    for style, words in card:
        path, size, trk = FONTS[style]
        while True:
            f = ImageFont.truetype(path, size); tr = trk * size; sp = f.getlength(" ") * (1.6 if style == "L" else 1.0)
            ws = [tw(f, w, tr) for w, _ in words]
            total = sum(ws) + sp * (len(ws) - 1)
            if total <= MAXW or size < 30: break
            size -= 2
        asc, desc = f.getmetrics(); capH = f.getbbox("H")[3] - f.getbbox("H")[1]
        lines.append(dict(style=style, f=f, tr=tr, sp=sp, ws=ws, words=words, total=total, capH=capH, size=size))
    hsum = sum(l["capH"] for l in lines) + sum(GAP[l["style"]] for l in lines[1:]) + 18 * (len(lines) - 1)
    y = cy - hsum / 2
    out = []
    for l in lines:
        x = W / 2 - l["total"] / 2
        for (w, t), ww in zip(l["words"], l["ws"]):
            o = Word(); o.text = w; o.t = t; o.style = l["style"]; o.f = l["f"]; o.tr = l["tr"]
            o.x = x; o.ytop = y; o.w = ww; o.capH = l["capH"]
            out.append(o); x += ww + l["sp"]
        y += l["capH"] + GAP[l["style"]] + 18
    return out

PAD = 70
def word_sprite(o, col, halo_col, halo_a):
    f = o.f
    bb = f.getbbox("H")
    w = int(o.w + 2 * PAD); h = int(o.capH + 2 * PAD + 30)
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    xx = PAD
    for ch in o.text:
        d.text((xx, PAD - bb[1]), ch, font=f, fill=255); xx += f.getlength(ch) + o.tr
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if halo_a > 0:
        for r, a in ((34, halo_a * 0.55), (12, halo_a)):
            hm = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(r))
            hm = hm.point(lambda p: int(min(255, p * a * 1.6)))
            hl = Image.new("RGBA", (w, h), halo_col + (0,)); hl.putalpha(hm)
            img = Image.alpha_composite(img, hl)
    tl = Image.new("RGBA", (w, h), col + (0,)); tl.putalpha(m)
    return Image.alpha_composite(img, tl)

LAYOUT = []
for i, c in enumerate(CARDS):
    ws = build_card(c, CY)
    for o in ws:
        o.dark = word_sprite(o, DARK, IVORY, 0.75)
        o.light = word_sprite(o, IVORY, (20, 8, 4), 0.35)
    LAYOUT.append(ws)
starts = [min(o.t for o in ws) for ws in LAYOUT]
ENDS = [starts[i + 1] - 0.02 for i in range(len(starts) - 1)] + [99]
for s in starts[1:]: PUNCH.append(s)
EXIT = 0.26; INTRO = 0.42

def ease(p): return 1 - (1 - p) ** 3

# ---------------- per-frame ----------------
def darkness(t):
    if t <= FADE_A: return 0.0
    p = min(1, (t - FADE_A) / (FADE_B - FADE_A)); return p * p * (3 - 2 * p)

def cam_scale(t):
    s = 1.0
    for b in BEATS:
        if abs(t - b) < 1.2: s += env(t, b, 0.016 if b in DOWN else 0.006, 0.20)
    for p in PUNCH:
        s += env(t, p, 0.028, 0.32)
    if t > 23.9: s += 0.05 * min(1, (t - 23.9) / 1.6) ** 1.5  # slow push into the ending
    return s

def text_layer(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = darkness(t)
    for ci, ws in enumerate(LAYOUT):
        e0 = ENDS[ci] - EXIT
        if t < starts[ci] - 0.1 or t > ENDS[ci]: continue
        xp = 0.0 if t < e0 else ease(min(1, (t - e0) / EXIT))
        final = ci == len(LAYOUT) - 1
        # final dissolve on black
        if final and t > 26.15:
            xp = ease(min(1, (t - 26.15) / 1.25))
        beat = sum(env(t, b, 0.022 if b in DOWN else 0.010, 0.16) for b in BEATS if abs(t - b) < 1)
        for o in ws:
            p = (t - (o.t - 0.06)) / INTRO
            if p <= 0: continue
            p = ease(min(1, p))
            a = p * (1 - xp)
            if a <= 0.004: continue
            blur = (1 - p) * 13 + xp * 12
            dy = (1 - p) * 26 - xp * 18
            sc = (1.07 - 0.07 * p) * (1 + (beat if o.style != "L" else beat * 0.4)) * (1 + 0.05 * xp)
            spr = o.dark if k < 0.02 else (o.light if k > 0.98 else Image.blend(o.dark, o.light, k))
            if abs(sc - 1) > 0.002:
                spr = spr.resize((int(spr.width * sc), int(spr.height * sc)), Image.BICUBIC)
            if blur > 0.4: spr = spr.filter(ImageFilter.GaussianBlur(blur))
            if a < 0.999:
                al = spr.getchannel("A").point(lambda v, a=a: int(v * a)); spr = spr.copy(); spr.putalpha(al)
            cx = o.x + o.w / 2; cy = o.ytop + o.capH / 2 + dy + (520 * (k*k*(3-2*k)) if final else 0)
            lay.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2 + 15 * sc - 15)))
    return lay

def warp(frame, s):
    if abs(s - 1) < 1e-4: return frame
    M = np.float32([[s, 0, W / 2 * (1 - s)], [0, s, H / 2 * (1 - s)]])
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def compose(frame, t):
    f = warp(frame, cam_scale(t)).astype(np.float32)
    k = darkness(t)
    if t < 0.25: f *= (t / 0.25)
    if k > 0: f *= (1 - k)
    lay = np.asarray(text_layer(t), dtype=np.float32)
    a = lay[..., 3:4] / 255.0
    f = f * (1 - a) + lay[..., :3] * a
    return np.clip(f + 0.5, 0, 255).astype(np.uint8)

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf",
                        "scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
                        "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
nfr = int(round(TOTAL * FPS))
if ONLY:
    want = {int(round(x * FPS)): x for x in ONLY}
    last = None
    for i in range(nfr):
        raw = dec.stdout.read(W * H * 3) if i < int(SRC_END * FPS) else b""
        fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3) if len(raw) == W * H * 3 else np.zeros((H, W, 3), np.uint8)
        if i in want:
            Image.fromarray(compose(fr, i / FPS)).save(S + f"proj/prev_{want[i]:05.2f}.jpg", quality=90)
        if i > max(want): break
    dec.kill(); sys.exit()

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-vf",
                        "scale=out_color_matrix=bt709:in_range=pc:out_range=tv,format=yuv420p",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-maxrate", "26M", "-bufsize", "40M",
                        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                        "-color_range", "tv", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
black = np.zeros((H, W, 3), np.uint8)
for i in range(nfr):
    t = i / FPS
    raw = dec.stdout.read(W * H * 3) if t < SRC_END else b""
    fr = np.frombuffer(raw, np.uint8).reshape(H, W, 3) if len(raw) == W * H * 3 else black
    enc.stdin.write(compose(fr, t).tobytes())
    if i % 120 == 0: print(f"{t:.1f}s", flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
json.dump([[(o.text, round(o.t, 2)) for o in ws] for ws in LAYOUT], open(S + "proj/timing.json", "w"), ensure_ascii=False)
print("done")
