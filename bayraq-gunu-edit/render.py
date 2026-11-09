"""Bayraq Günü (9 Noyabr) — cinematic 9:16 Reel from the viral "child and the flag" clip.

Usage: python3 render.py <frames_dir> <out_video_noaudio.mp4>
frames_dir holds the source frames as 0001.jpg … (ffmpeg -vsync 0, 30 fps, 720x1280).
"""
import sys, math, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FR = sys.argv[1]
OUT = sys.argv[2]
HERE = __file__.rsplit("/", 1)[0]
W, H, FPS = 1080, 1920, 30
SW, SH = 720, 1280
NSRC = 879

INTER_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
INTER_SB = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
PF_I = f"{HERE}/fonts/PlayfairDisplay-400-italic.ttf"
PF_BI = f"{HERE}/fonts/PlayfairDisplay-700-italic.ttf"
LOGO = f"{HERE}/../logos/individual/araz-radio_white.png"

IVORY = (246, 241, 230)
BLUE, RED, GREEN = (0, 181, 226), (239, 51, 64), (80, 158, 47)

# ---------------------------------------------------------------- timeline
# (out_start, out_end, kind, params)
#  clip:  src_start, speed, zoom0, zoom1, cx, cy
SEGS = [
    (0.00, 2.80, "clip", dict(s=18.0, sp=1.0, z0=1.42, z1=1.55, cx=430, cy=470)),
    (2.80, 8.60, "clip", dict(s=0.5, sp=1.0, z0=1.00, z1=1.08, cx=360, cy=680)),
    (8.60, 13.60, "clip", dict(s=11.6, sp=1.0, z0=1.12, z1=1.22, cx=390, cy=640)),
    (13.60, 19.50, "clip", dict(s=18.4, sp=1.0, z0=1.10, z1=1.20, cx=400, cy=660)),
    (19.50, 21.30, "clip", dict(s=24.0, sp=0.5, z0=1.45, z1=1.60, cx=400, cy=560)),
    (21.30, 23.00, "freeze", dict(s=24.9, z0=1.60, z1=1.70, cx=400, cy=560)),
    (23.00, 27.00, "clip", dict(s=25.5, sp=0.95, z0=1.18, z1=1.10, cx=420, cy=700)),
    (27.00, 31.50, "end", dict(s=29.2)),
]
DUR = 31.5
NFR = int(DUR * FPS)
XFADE = {2.80: 0.30, 8.60: 0.25, 13.60: 0.25, 19.50: 0.20, 23.00: 0.30, 27.00: 0.60}

# Text cues: (start, end, kind, text)
CUES = [  # (start, end, kind, text, y)  — y chosen per shot so text never covers the child
    (0.45, 2.65, "line", "Külək bayrağı\ndirəkdən qopardı.", 330),
    (3.50, 7.90, "line", "Amma bir uşaq\nbuna biganə qalmadı.", 1570),
    (9.20, 13.30, "line", "Külək güclü idi,\ndirək isə hündür.", 1570),
    (14.20, 19.10, "line", "O, dəfələrlə\ncəhd etdi.", 1570),
    (20.10, 22.90, "big", "Geri çəkilmədi.", 1010),
    (23.60, 26.85, "line", "Çünki bayrağa sevgi\nyaşla ölçülmür.", 1570),
]

_cache = {}


def src_frame(t):
    """Float RGB array of source at time t (linear blend between frames)."""
    f = t * FPS
    i0 = int(math.floor(f)); a = f - i0
    i0 = max(0, min(NSRC - 1, i0)); i1 = min(NSRC - 1, i0 + 1)
    def load(i):
        if i not in _cache:
            if len(_cache) > 40:
                _cache.clear()
            _cache[i] = np.asarray(Image.open(f"{FR}/{i+1:04d}.jpg").convert("RGB"), np.float32)
        return _cache[i]
    if a < 0.02 or i1 == i0:
        return load(i0)
    return load(i0) * (1 - a) + load(i1) * a


def frame_crop(arr, z, cx, cy):
    cw, ch = SW / z, SH / z
    x0 = min(max(cx - cw / 2, 0), SW - cw); y0 = min(max(cy - ch / 2, 0), SH - ch)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return np.asarray(im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)), np.float32)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = 1 - 0.38 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.48) / (H * 0.60)) ** 2, 0, 1) ** 1.4
SCRIM = np.clip((yy - H * 0.66) / (H * 0.34), 0, 1) ** 1.2 * 0.66 + np.clip((H * 0.12 - yy) / (H * 0.12), 0, 1) * 0.35


def grade(a):
    # gentle filmic contrast, slightly cool shadows / warm highlights, natural saturation
    x = a / 255.0
    x = x + 0.06 * np.sin((x - 0.5) * math.pi) * (1 - np.abs(2 * x - 1)) * 2
    lum = (x * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    x = lum + (x - lum) * 1.04
    x = x * (1 + (lum - 0.5) * np.array([0.05, 0.0, -0.05]))
    x = x * VIG[..., None]
    x = x * (1 - SCRIM[..., None])
    return np.clip(x * 255, 0, 255)


def seg_at(t):
    for s in SEGS:
        if s[0] <= t < s[1]:
            return s
    return SEGS[-1]


def render_seg(seg, t):
    a, b, kind, p = seg
    u = (t - a) / (b - a)
    if kind == "clip":
        st = p["s"] + (t - a) * p["sp"]
        z = p["z0"] + (p["z1"] - p["z0"]) * ease(u)
        return frame_crop(src_frame(st), z, p["cx"], p["cy"])
    if kind == "freeze":
        z = p["z0"] + (p["z1"] - p["z0"]) * u
        return frame_crop(src_frame(p["s"]), z, p["cx"], p["cy"])
    # end card background: frozen final frame, blurred and sunk into navy
    im = Image.fromarray(frame_crop(src_frame(p["s"]), 1.05 + 0.04 * u, 380, 640).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(10 + 14 * ease(u * 2)))
    arr = np.asarray(im, np.float32)
    navy = np.array([8, 18, 34], np.float32)
    k = 0.55 + 0.2 * ease(u * 2)
    return arr * (1 - k) + navy * k


def base_frame(t):
    seg = seg_at(t)
    out = render_seg(seg, t)
    # crossfade from previous segment
    idx = SEGS.index(seg)
    if idx > 0 and seg[0] in XFADE and t < seg[0] + XFADE[seg[0]]:
        prev = SEGS[idx - 1]
        k = ease((t - seg[0]) / XFADE[seg[0]])
        out = render_seg(prev, min(t, prev[1] + 0.5)) * (1 - k) + out * k
    out = grade(out) if seg[2] != "end" else out
    if t < 0.5:
        out = out * ease(t / 0.5)
    return out


# ---------------------------------------------------------------- typography
F_LINE = ImageFont.truetype(PF_I, 70)
F_BIG = ImageFont.truetype(PF_BI, 118)
F_KICK = ImageFont.truetype(INTER_SB, 30)
F_DATE = ImageFont.truetype(INTER_B, 210)
F_DAY = ImageFont.truetype(PF_I, 84)
F_MUB = ImageFont.truetype(INTER_SB, 46)
logo_full = Image.open(LOGO).convert("RGBA")
LOGO_SM = logo_full.resize((220, round(220 * logo_full.height / logo_full.width)), Image.LANCZOS)
LOGO_LG = logo_full.resize((380, round(380 * logo_full.height / logo_full.width)), Image.LANCZOS)


def draw_words(layer, text, font, cx, y, t_in, t, stagger=0.09, rise=26, alpha=1.0, fill=IVORY):
    """Word-by-word fade/rise; multiline centred. Returns bottom y."""
    d = ImageDraw.Draw(layer)
    lines = text.split("\n")
    asc, desc = font.getmetrics(); lh = int((asc + desc) * 1.12)
    wi = 0
    for li, line in enumerate(lines):
        words = line.split(" ")
        sp = font.getlength(" ")
        widths = [font.getlength(w) for w in words]
        x = cx - (sum(widths) + sp * (len(words) - 1)) / 2
        for w, ww in zip(words, widths):
            k = ease((t - t_in - wi * stagger) / 0.45)
            if k > 0:
                yy_ = y + li * lh + rise * (1 - k)
                a = int(255 * k * alpha)
                # soft shadow
                sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
                ImageDraw.Draw(sh).text((x + 2, yy_ + 4), w, font=font, fill=(0, 0, 0, int(a * 0.55)))
                layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
                d.text((x, yy_), w, font=font, fill=fill + (a,))
            x += ww + sp; wi += 1
    return y + len(lines) * lh


def tricolor(layer, cx, y, width, k, alpha=1.0, h=5):
    d = ImageDraw.Draw(layer)
    w = width * ease(k)
    for i, c in enumerate((BLUE, RED, GREEN)):
        d.rectangle([cx - w / 2, y + i * (h + 3), cx + w / 2, y + i * (h + 3) + h - 1], fill=c + (int(255 * alpha),))


def overlay(t):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # station logo, upper right, mobile-safe (hidden on end card where it appears large)
    la = 1.0 - ease((t - 26.9) / 0.4)
    la *= ease((t - 0.2) / 0.6)
    if la > 0:
        lg = LOGO_SM.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * la)))
        L.alpha_composite(lg, (W - 64 - lg.width, 96))
    # kicker, upper left
    if t < 27.0:
        ka = ease((t - 0.6) / 0.6) * (1 - ease((t - 26.6) / 0.4))
        if ka > 0:
            d = ImageDraw.Draw(L)
            d.text((66, 118), "9 NOYABR", font=F_KICK, fill=IVORY + (int(235 * ka),))
            tricolor(L, 66 + 70, 162, 140, ka, ka, h=3)
    for a, b, kind, text, y in CUES:
        if a - 0.05 <= t <= b + 0.5:
            out = 1 - ease((t - b) / 0.35)
            if kind == "line":
                bot = draw_words(L, text, F_LINE, W / 2, y, a, t, alpha=out)
                tricolor(L, W / 2, bot + 18, 180, (t - a - 0.2) / 0.7, out)
            else:
                bot = draw_words(L, text, F_BIG, W / 2, y, a, t, stagger=0.22, rise=40, alpha=out)
                tricolor(L, W / 2, bot + 10, 300, (t - a - 0.5) / 0.9, out)
    # end card
    if t >= 27.0:
        u = t - 27.0
        tricolor(L, W / 2, 640, 520, (u - 0.1) / 0.9, 1.0, h=7)
        draw_words(L, "9 NOYABR", F_DATE, W / 2, 700, 27.3, t, stagger=0.0, rise=50)
        draw_words(L, "Dövlət Bayrağı Günü", F_DAY, W / 2, 960, 27.8, t, stagger=0.12)
        draw_words(L, "MÜBARƏK!", F_MUB, W / 2, 1100, 28.5, t, stagger=0.0)
        lk = ease((u - 1.8) / 0.7)
        if lk > 0:
            lg = LOGO_LG.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * lk)))
            L.alpha_composite(lg, (int(W / 2 - lg.width / 2), 1330 + int(20 * (1 - lk))))
    return L


def render(n):
    t = n / FPS
    base = Image.fromarray(base_frame(t).astype(np.uint8)).convert("RGBA")
    base.alpha_composite(overlay(t))
    if t > DUR - 0.35:
        k = 1 - ease((t - (DUR - 0.35)) / 0.35)
        return (np.asarray(base.convert("RGB"), np.float32) * k).astype(np.uint8).tobytes()
    return base.convert("RGB").tobytes()


if __name__ == "__main__":
    only = [float(x) for x in sys.argv[3:]]
    if only:  # stills for review
        for t in only:
            Image.frombytes("RGB", (W, H), render(int(t * FPS))).save(f"{OUT}_{t:05.2f}.jpg", quality=90)
        sys.exit()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                            "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", OUT],
                           stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fb in enumerate(pool.imap(render, range(NFR), chunksize=8)):
            enc.stdin.write(fb)
            if i % 100 == 0:
                print(i, "/", NFR, flush=True)
    enc.stdin.close(); enc.wait()
