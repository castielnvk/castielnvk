"""Bayraq Günü (9 Noyabr) — 20 s cinematic 9:16 Reel, cut to the finale of the national anthem.

Usage: python3 render.py <frames_dir> <out.mp4> [still times...]
frames_dir holds the source frames as 0001.jpg … (ffmpeg -vsync 0, 30 fps, 720x1280).
Music: anthem (U. Hacıbəyli, US Navy Band, public domain) from 109.66 s; accents land at
3.72, 7.33, 11.02, 14.79 and the final chord at 17.28 s of the Reel.
"""
import sys, math, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FR, OUT = sys.argv[1], sys.argv[2]
HERE = __file__.rsplit("/", 1)[0]
W, H, FPS = 1080, 1920, 30
SW, SH, NSRC = 720, 1280, 879
DUR = 20.0
NFR = int(DUR * FPS)

INTER_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
INTER_SB = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
PF_I = f"{HERE}/fonts/PlayfairDisplay-400-italic.ttf"
LOGO = f"{HERE}/../logos/individual/araz-radio_white.png"

IVORY = (247, 242, 232)
BLUE, RED, GREEN = (0, 181, 226), (239, 51, 64), (80, 158, 47)

# (start, end, kind, params) — clip: s=src start, sp=speed, z0→z1 zoom, (cx,cy)→(cx1,cy1) drift
SEGS = [
    (0.00, 1.85, "clip", dict(s=18.0, sp=1.0, z0=1.50, z1=1.38, cx=440, cy=430, cx1=420, cy1=440)),
    (1.85, 3.72, "clip", dict(s=1.6, sp=1.0, z0=1.06, z1=1.00, cx=380, cy=660, cx1=360, cy1=650)),
    (3.72, 7.33, "clip", dict(s=3.05, sp=1.0, z0=1.00, z1=1.10, cx=340, cy=660, cx1=350, cy1=650)),
    (7.33, 11.02, "clip", dict(s=12.0, sp=1.0, z0=1.10, z1=1.02, cx=390, cy=620, cx1=380, cy1=620)),
    (11.02, 14.79, "clip", dict(s=20.4, sp=1.0, z0=1.00, z1=1.10, cx=400, cy=610, cx1=390, cy1=600)),
    (14.79, 16.62, "clip", dict(s=24.17, sp=0.4, z0=1.22, z1=1.32, cx=400, cy=590, cx1=400, cy1=590)),
    (16.62, 17.28, "freeze", dict(s=24.9, z0=1.32, z1=1.36, cx=400, cy=590, cx1=400, cy1=590)),
    (17.28, 20.00, "end", dict(s=24.9)),
]
# transitions at segment starts: zoom-through, tricolour wipe, bloom flash
TRANS = {1.85: "zoom", 3.72: "wipe", 7.33: "zoom", 11.02: "wipe", 14.79: "bloom", 17.28: "wipe"}

# text cues: (start, end, lines[(text, delay)], y, size)
CUES = [
    (0.25, 3.30, [("Külək bayrağı", 0), ("dirəkdən qopardı.", 0.25)], 330, "m"),
    (3.95, 7.15, [("Amma bir uşaq", 0), ("buna biganə qalmadı.", 0.25)], 1560, "m"),
    (7.55, 10.65, [("Külək güclü idi,", 0), ("dirək isə hündür.", 0.25)], 1560, "m"),
    (11.25, 14.55, [("O, dəfələrlə cəhd etdi.", 0), ("Geri çəkilmədi.", 1.63)], 1560, "m"),
    (14.95, 16.85, [("Çünki bayrağa sevgi", 0), ("yaşla ölçülmür.", 0.35)], 960, "l"),
]

_cache = {}


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def eo(x):  # ease-out cubic
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def src_frame(t):
    f = t * FPS
    i0 = max(0, min(NSRC - 1, int(math.floor(f)))); a = f - math.floor(f)
    i1 = min(NSRC - 1, i0 + 1)

    def load(i):
        if i not in _cache:
            if len(_cache) > 30:
                _cache.clear()
            _cache[i] = np.asarray(Image.open(f"{FR}/{i+1:04d}.jpg").convert("RGB"), np.float32)
        return _cache[i]
    if a < 0.03 or i1 == i0:
        return load(i0)
    return load(i0) * (1 - a) + load(i1) * a


WIN_TOP, WIN_H = 280, 1160   # letterbox window; footage is framed for this window, bars are black


def crop(arr, z, cx, cy):
    """Frame the source for the letterbox window (z=1: full source width)."""
    cw = SW / z; ch = cw * WIN_H / W
    x0 = min(max(cx - cw / 2, 0), SW - cw); y0 = min(max(cy - ch / 2, 0), SH - ch)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    win = im.resize((W, WIN_H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    out = np.zeros((H, W, 3), np.float32)
    out[WIN_TOP:WIN_TOP + WIN_H] = np.asarray(win, np.float32)
    return out


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = 1 - 0.36 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.42)) ** 2, 0, 1) ** 1.4
SCRIM = np.zeros((H, W), np.float32)


def grade(a):
    x = a / 255.0
    x = x + 0.07 * np.sin((x - 0.5) * math.pi) * (1 - np.abs(2 * x - 1)) * 2   # filmic contrast
    lum = (x * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    x = lum + (x - lum) * 1.06
    x = x * (1 + (lum - 0.5) * np.array([0.07, 0.01, -0.07]))                  # warm highs / cool lows
    # soft bloom on highlights
    small = Image.fromarray(np.clip(x * 255, 0, 255).astype(np.uint8)).resize((W // 6, H // 6), Image.BILINEAR)
    hl = np.asarray(small, np.float32) / 255.0
    hl = np.clip(hl - 0.62, 0, 1) * 1.6
    hl = np.asarray(Image.fromarray((hl * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
                    .resize((W, H), Image.BILINEAR), np.float32) / 255.0
    x = x + hl * 0.22
    x = x * VIG[..., None] * (1 - SCRIM[..., None])
    return np.clip(x * 255, 0, 255)


def seg_index(t):
    for i, s in enumerate(SEGS):
        if s[0] <= t < s[1]:
            return i
    return len(SEGS) - 1


def end_bg(t):
    p = SEGS[-1][3]; u = t - SEGS[-1][0]
    im = Image.fromarray(crop(src_frame(p["s"]), 1.0 + 0.03 * u, 380, 600).astype(np.uint8))
    im = im.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    arr = np.asarray(im, np.float32)
    navy_top, navy_bot = np.array([10, 26, 48.]), np.array([4, 10, 22.])
    g = (yy / H)[..., None]
    navy = navy_top * (1 - g) + navy_bot * g
    return arr * 0.22 + navy * 0.78


def render_seg(i, t, zoom_mul=1.0):
    a, b, kind, p = SEGS[i]
    u = (t - a) / (b - a)
    if kind == "end":
        return end_bg(t)
    st = p["s"] + (t - a) * p.get("sp", 0) if kind == "clip" else p["s"]
    k = ease(u) if kind == "clip" else u
    z = (p["z0"] + (p["z1"] - p["z0"]) * k) * zoom_mul
    cx = p["cx"] + (p["cx1"] - p["cx"]) * k; cy = p["cy"] + (p["cy1"] - p["cy"]) * k
    return grade(crop(src_frame(st), z, cx, cy))


def radial_blur(arr, amt):
    if amt < 0.01:
        return arr
    im = Image.fromarray(arr.astype(np.uint8)); acc = arr.copy(); n = 1
    for s in (1 + amt * 0.04, 1 + amt * 0.08, 1 + amt * 0.12):
        w, h = int(W * s), int(H * s)
        acc += np.asarray(im.resize((w, h), Image.BILINEAR).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H)), np.float32)
        n += 1
    return acc / n


SKEW = math.tan(math.radians(14))


BW = 520.0
WSPAN = W + H * SKEW + 3 * BW + 20


def wipe(old, new, p):
    """Diagonal flag-colour bands sweep left→right: old ahead of them, new behind them."""
    pos = -10 + ease(p) * WSPAN
    rel = xx + (H - yy) * SKEW - pos
    out = np.where((rel >= 0)[..., None], old, new)
    for k, c in enumerate((GREEN, RED, BLUE)):  # reads blue · red · green left→right
        out[(rel < -k * BW) & (rel >= -(k + 1) * BW)] = c
    return out


def base_frame(t):
    i = seg_index(t)
    # flag-colour wipe windows (0.3 s either side of the cut)
    for j, s in enumerate(SEGS):
        c = s[0]
        if TRANS.get(c) == "wipe" and c - 0.3 <= t < c + 0.3:
            p = (t - (c - 0.3)) / 0.6
            pos = -10 + ease(p) * WSPAN
            need_old = pos < W + H * SKEW + 5
            need_new = pos > 3 * BW
            old = render_seg(j - 1, t) if need_old else 0
            new = render_seg(j, max(t, c - 0.0)) if need_new else 0
            if not need_old:
                old = np.zeros((H, W, 3), np.float32)
            if not need_new:
                new = np.zeros((H, W, 3), np.float32)
            return wipe(old, new, p)
    a = SEGS[i][0]
    if i + 1 < len(SEGS):
        nb = SEGS[i + 1][0]
        if TRANS.get(nb) == "zoom" and t > nb - 0.16:
            q = (t - (nb - 0.16)) / 0.16
            return radial_blur(render_seg(i, t, 1 + 0.18 * q * q), q * 2.2)
    kind = TRANS.get(a)
    if kind == "zoom" and t < a + 0.16:
        q = 1 - (t - a) / 0.16
        return radial_blur(render_seg(i, t, 1 + 0.16 * q * q), q * 2.0)
    out = render_seg(i, t)
    if kind == "bloom" and t < a + 0.45:
        k = (1 - (t - a) / 0.45) ** 2
        out = out + (255 - out) * 0.75 * k
    return out


# ---------------------------------------------------------------- typography (style A: cinematic letterbox)
MS_XB = f"{HERE}/fonts/montserrat-800-normal.ttf"
MS_SB = f"{HERE}/fonts/montserrat-600-normal.ttf"
F_CAP = ImageFont.truetype(MS_XB, 50)
F_DATE = ImageFont.truetype(MS_XB, 140)
F_DAY = ImageFont.truetype(MS_SB, 44)
F_MUB = ImageFont.truetype(MS_XB, 50)
WHITE = (255, 255, 255)
BAR_TOP, BAR_BOT = 280, 1440      # footage window; black bars above and below
TEXT_Y = 1482                     # captions live in the lower bar (above the Instagram UI zone)
logo_full = Image.open(LOGO).convert("RGBA")
LOGO_SM = logo_full.resize((230, round(230 * logo_full.height / logo_full.width)), Image.LANCZOS)
LOGO_LG = logo_full.resize((340, round(340 * logo_full.height / logo_full.width)), Image.LANCZOS)


def azup(s):
    return s.replace("i", "İ").upper()


def text_img(text, font, tracking=0.0, fill=IVORY):
    asc, desc = font.getmetrics()
    widths = [font.getlength(c) for c in text]
    tw = sum(widths) + tracking * (len(text) - 1)
    im = Image.new("RGBA", (int(tw) + 8, asc + desc + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = 4
    for c, w in zip(text, widths):
        d.text((x, 4), c, font=font, fill=fill + (255,)); x += w + tracking
    return im


def with_alpha(im, a):
    if a >= 0.999:
        return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im


def reveal_line(L, im, cx, y, k, out_k):
    """Mask reveal: line rises from behind its own baseline clip; exits upward with fade."""
    if k <= 0 or out_k <= 0:
        return
    h = im.height
    dy = int((1 - eo(k)) * h * 0.9) - int((1 - out_k) * 24)
    vis = im.crop((0, 0, im.width, max(1, h - max(dy, 0))))
    L.alpha_composite(with_alpha(vis, min(1, k * 1.6) * out_k), (int(cx - im.width / 2), int(y + max(dy, 0))))


def tricolor(L, cx, y, width, k, alpha=1.0, h=4, left=None):
    d = ImageDraw.Draw(L); w = width * eo(k)
    if w < 1:
        return
    for i, c in enumerate((BLUE, RED, GREEN)):
        x0 = cx - w / 2 if left is None else left
        d.rectangle([x0, y + i * (h + 3), x0 + w, y + i * (h + 3) + h - 1], fill=c + (int(255 * alpha),))


def overlay(t):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for a, b, lines, _y, _sz in CUES:
        if a - 0.05 <= t <= b + 0.4:
            out_k = 1 - ease((t - b) / 0.3)
            for li, (txt, dl) in enumerate(lines):
                reveal_line(L, text_img(azup(txt), F_CAP, 4, WHITE), W / 2, TEXT_Y + li * 72, (t - a - dl) / 0.5, out_k)
            tricolor(L, W / 2, TEXT_Y + len(lines) * 72 + 22, 150, (t - a - 0.3) / 0.6, out_k, h=4)
    if t >= 17.28:
        u = t - 17.28
        reveal_line(L, text_img("9 NOYABR", F_DATE, 30 * (1 - eo(u / 1.4)) + 4, WHITE), W / 2, 500, (u - 0.12) / 0.6, 1)
        tricolor(L, W / 2, 705, 470, (u - 0.35) / 0.7, 1.0, h=5)
        reveal_line(L, text_img(azup("Dövlət Bayrağı Günü"), F_DAY, 9, WHITE), W / 2, 755, (u - 0.55) / 0.6, 1)
        reveal_line(L, text_img("MÜBARƏK!", F_MUB, 12 + 14 * (1 - eo((u - 0.9) / 1.2)), WHITE), W / 2, TEXT_Y + 30, (u - 0.9) / 0.5, 1)
        lk = eo((u - 1.2) / 0.6)
        if lk > 0:
            L.alpha_composite(with_alpha(LOGO_LG, lk), (int(W / 2 - LOGO_LG.width / 2), 1000 + int(24 * (1 - lk))))
    a = L.getchannel("A").resize((W // 2, H // 2)).filter(ImageFilter.GaussianBlur(5)).resize((W, H))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * 0.5)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # letterbox bars (always on top of footage and wipes), hairline edge for a premium finish
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, W, BAR_TOP - 1], fill=(0, 0, 0, 255))
    d.rectangle([0, BAR_BOT, W, H], fill=(0, 0, 0, 255))
    d.line([0, BAR_TOP, W, BAR_TOP], fill=(255, 255, 255, 28)); d.line([0, BAR_BOT - 1, W, BAR_BOT - 1], fill=(255, 255, 255, 28))
    out.alpha_composite(sh, (2, 4)); out.alpha_composite(L)
    la = ease((t - 0.15) / 0.5) * (1 - ease((t - 17.0) / 0.25))
    if la > 0:
        out.alpha_composite(with_alpha(LOGO_SM, la), (int(W / 2 - LOGO_SM.width / 2), (BAR_TOP - LOGO_SM.height) // 2))
    return out


def render(n):
    t = n / FPS
    base = Image.fromarray(np.clip(base_frame(t), 0, 255).astype(np.uint8)).convert("RGBA")
    base.alpha_composite(overlay(t))
    rgb = base.convert("RGB")
    if t < 0.2:
        rgb = Image.fromarray((np.asarray(rgb, np.float32) * ease(t / 0.2)).astype(np.uint8))
    return rgb.tobytes()


if __name__ == "__main__":
    only = [float(x) for x in sys.argv[3:]]
    if only:
        for t in only:
            Image.frombytes("RGB", (W, H), render(int(round(t * FPS)))).save(f"{OUT}_{t:05.2f}.jpg", quality=90)
        sys.exit()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                            "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", OUT],
                           stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fb in enumerate(pool.imap(render, range(NFR), chunksize=6)):
            enc.stdin.write(fb)
            if i % 60 == 0:
                print(i, "/", NFR, flush=True)
    enc.stdin.close(); enc.wait()
