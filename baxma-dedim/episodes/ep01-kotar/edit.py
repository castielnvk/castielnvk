"""BAXMA DEDİM. — Episode 01 «Kotar sindromu»: editable edit + render source.

    cd baxma-dedim/episodes/ep01-kotar && python3 edit.py
    -> Baxma_Dedim_EP01_Kotar.mp4  (1080×1920, H.264, 24 fps, NO audio stream)

To make Episode 02: copy this folder, swap SOURCE, set FREEZE/TOUCH/KITCHEN_END to the new
shot's action, change the text in CARDS and keep everything else. All layout is in the CONFIG block.
Text is set as vector outlines (layers/*.svg are editable), then rendered to PNG and composited.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
from lib import Font, fmt, place, run, svg_doc  # noqa: E402
from concepts import c01  # noqa: E402  (approved logo: concept 01, exact artwork)

# =============================== CONFIG ======================================
OUT = os.path.join(HERE, "Baxma_Dedim_EP01_Kotar.mp4")
SOURCE = os.path.join(HERE, "source", "kitchen_gemini.mp4")   # 720×1280, 24 fps, 10 s
W, H, FPS, DUR = 1080, 1920, 24, 14.0

SRC_CROP = (4, 14, 704, 1252)    # x, y, w, h in source px: trims the bright edge line on the right
FREEZE = 1.0                     # hold source frame 0 (still) for this long at the start
SPOON_TOUCH_SRC_FRAME = 100      # source frame where the spoon lands on the table (4.17 s)
TOUCH = FREEZE + SPOON_TOUCH_SRC_FRAME / 24   # = 5.17 s in the edit
KITCHEN_END = 9.0                # hard cut to near-black
LOGO_IN = 12.0

# slow push-in over the kitchen shot: zoom and centre (output px) at start -> end
ZOOM = (1.0, 1.085)
CENTER = ((540, 960), (548, 1060))

# grade: deep shadows, cool table light, natural skin (ffmpeg filters)
GRADE = ("eq=contrast=1.06:brightness=-0.012:saturation=0.93,"
         "curves=all='0/0 0.12/0.085 0.45/0.43 0.8/0.81 1/1',"
         "colorbalance=rh=-0.015:bh=0.025:bm=0.01,"
         "vignette=angle=PI/4.6")

BONE, INK, ASH = "#EEE8DC", "#0D0C0B", "#8C8477"
F_TXT = Font("inter-tight-latin-600-normal.woff2", "inter-tight-latin-ext-600-normal.woff2")
F_REG = Font("inter-tight-latin-500-normal.woff2", "inter-tight-latin-ext-500-normal.woff2")
F_BOLD = Font("inter-tight-latin-800-normal.woff2", "inter-tight-latin-ext-800-normal.woff2")

# Kitchen text: two lines, left-aligned in the dark ceiling above the lamp, clear of the face,
# the spoon and the IG/TikTok UI (top ~230 px, right icon column, bottom ~480 px).
KX, KBASE, KMAXW, KMAXSIZE = 84, 352, 880, 66
LABEL = dict(text="Canlandırma", size=24, left=84, base=262)

# Each card: lines -> list of (text, font) segments. t_in/t_out in edit seconds.
CARDS = [
    dict(id="k1", kind="kitchen", t_in=0.0, t_out=TOUCH - 0.10,
         lines=[[("Bəzi insanlar sağ ola-ola", F_TXT)], [("öldüklərinə inanırlar.", F_TXT)]]),
    dict(id="k2", kind="kitchen", t_in=TOUCH, t_out=KITCHEN_END, cut_out=True,
         lines=[[("Bəziləri buna o qədər inanır ki,", F_TXT)], [("yeməkdən də imtina edir.", F_TXT)]]),
    dict(id="rv", kind="reveal", t_in=KITCHEN_END + 0.15, t_out=LOGO_IN - 0.08,
         lines=[[("Bu hal", F_REG)], [("Kotar sindromu", F_BOLD), (" adlanır.", F_REG)]]),
]
REVEAL_SIZE, REVEAL_CY = 74, 930
LOGO_WIDTH, LOGO_CY = 820, 930
# ============================================================================

LAYERS = os.path.join(HERE, "layers")
os.makedirs(LAYERS, exist_ok=True)


def seg_runs(segs, size, x, y):
    out = []
    for text, font in segs:
        r = run(font, text, size, track=-0.005, x=x, y=y)
        out.append(r)
        x += r.width
    return out


def line_width(segs, size):
    return sum(run(f, t, size, track=-0.005).width for t, f in segs)


SHADOW = ('<defs><filter id="sh" x="-10%" y="-60%" width="120%" height="220%">'
          '<feGaussianBlur in="SourceAlpha" stdDeviation="14" result="b"/>'
          '<feFlood flood-color="#000" flood-opacity="0.75"/><feComposite in2="b" operator="in" result="s"/>'
          '<feGaussianBlur in="SourceAlpha" stdDeviation="3" result="b2"/>'
          '<feFlood flood-color="#000" flood-opacity="0.55"/><feComposite in2="b2" operator="in" result="s2"/>'
          '<feMerge><feMergeNode in="s"/><feMergeNode in="s2"/><feMergeNode in="SourceGraphic"/></feMerge>'
          '</filter></defs>')

# one shared size for both kitchen cards so the layout doesn't jump
ksize = KMAXSIZE
for c in CARDS:
    if c["kind"] == "kitchen":
        for segs in c["lines"]:
            ksize = min(ksize, KMAXSIZE * KMAXW / line_width(segs, KMAXSIZE))
ksize = math.floor(ksize)
KLEAD = round(ksize * 1.24)

jobs, layers = [], []  # layers: dict(png, card, line_index)
for c in CARDS:
    for i, segs in enumerate(c["lines"]):
        if c["kind"] == "kitchen":
            runs = seg_runs(segs, ksize, KX, KBASE + i * KLEAD)
            body = SHADOW + '<g filter="url(#sh)">' + "".join(r.paths(BONE) for r in runs) + "</g>"
        else:
            lw = line_width(segs, REVEAL_SIZE)
            lead = round(REVEAL_SIZE * 1.3)
            y = REVEAL_CY - lead / 2 + REVEAL_SIZE * 0.36 + i * lead
            runs = seg_runs(segs, REVEAL_SIZE, (W - lw) / 2, y)
            body = "".join(r.paths(BONE) for r in runs)
        name = f'{c["id"]}-line{i + 1}'
        svg = os.path.join(LAYERS, name + ".svg")
        with open(svg, "w", encoding="utf-8") as f:
            f.write(svg_doc(W, H, f'<g id="{name}">{body}</g>', name))
        jobs.append([svg, svg[:-4] + ".png", W, H, 1])
        layers.append(dict(png=svg[:-4] + ".png", card=c, i=i))

# "Canlandırma" label (whole kitchen shot)
lx = LABEL["left"]
lbl = run(F_REG, LABEL["text"], LABEL["size"], track=0.06, x=lx, y=LABEL["base"])
with open(os.path.join(LAYERS, "label.svg"), "w", encoding="utf-8") as f:
    f.write(svg_doc(W, H, SHADOW.replace('"sh"', '"shl"') + f'<g id="label" filter="url(#shl)" opacity="0.72">'
                    f'{lbl.paths(BONE)}</g>', "Canlandırma label"))
jobs.append([os.path.join(LAYERS, "label.svg"), os.path.join(LAYERS, "label.png"), W, H, 1])

# approved logo (concept 01 wordmark, unmodified) on transparent
inner, bbox = c01("logo")["wordmark"]
with open(os.path.join(LAYERS, "logo.svg"), "w", encoding="utf-8") as f:
    f.write(svg_doc(W, H, place(inner, bbox, W / 2, LOGO_CY, width=LOGO_WIDTH), "BAXMA DEDİM. logo"))
jobs.append([os.path.join(LAYERS, "logo.svg"), os.path.join(LAYERS, "logo.png"), W, H, 1])

with open(os.path.join(LAYERS, "jobs.json"), "w") as f:
    json.dump(jobs, f)
subprocess.run(["node", os.path.join(ROOT, "render.js"), os.path.join(LAYERS, "jobs.json")], check=True)


def load(p):
    a = np.asarray(Image.open(p).convert("RGBA"), dtype=np.float32) / 255.0
    return a[..., :3], a[..., 3:4]


for L in layers:
    L["rgb"], L["a"] = load(L["png"])
LBL = load(os.path.join(LAYERS, "label.png"))
LOGO = load(os.path.join(LAYERS, "logo.png"))


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def card_state(c, i, t):
    """opacity and vertical offset for line i of card c at time t."""
    if c["kind"] == "kitchen":
        d_in, stag, rise, d_out = 0.30, 0.09, 22, 0.16
    else:
        d_in, stag, rise, d_out = 0.45, 0.22, 14, 0.12
    t0 = c["t_in"] + i * stag
    if t < t0 or t >= c["t_out"]:
        return 0.0, 0
    p = ease_out((t - t0) / d_in)
    o = p
    if not c.get("cut_out"):
        o *= 1 - smooth((t - (c["t_out"] - d_out)) / d_out)
    return o, round(rise * (1 - p))


def over(bg, rgb, a, o, dy=0):
    if o <= 0:
        return bg
    if dy:
        rgb = np.roll(rgb, dy, axis=0)
        a = np.roll(a, dy, axis=0)
    k = a * o
    return bg * (1 - k) + rgb * k


# ---- source frames: crop, upscale and grade in ffmpeg, read sequentially ---------------
cx, cy, cw, ch = SRC_CROP
dec = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-i", SOURCE, "-an", "-vf",
     f"crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos,{GRADE},unsharp=5:5:0.35,format=rgb24",
     "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
FRAME_BYTES = W * H * 3
src_frames, src_idx = [], -1


def src_frame(n):
    global src_idx
    while src_idx < n:
        buf = dec.stdout.read(FRAME_BYTES)
        if len(buf) < FRAME_BYTES:
            break
        src_frames[:] = [np.frombuffer(buf, np.uint8).reshape(H, W, 3)]
        src_idx += 1
    return src_frames[0]


def push_in(img, t):
    p = smooth(t / KITCHEN_END)
    z = ZOOM[0] + (ZOOM[1] - ZOOM[0]) * p
    if z <= 1.0001:
        return img
    ccx = CENTER[0][0] + (CENTER[1][0] - CENTER[0][0]) * p
    ccy = CENTER[0][1] + (CENTER[1][1] - CENTER[0][1]) * p
    bw, bh = W / z, H / z
    x0 = min(max(ccx - bw / 2, 0), W - bw)
    y0 = min(max(ccy - bh / 2, 0), H - bh)
    return np.asarray(Image.fromarray(img).resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh)))


enc = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
     "-i", "-", "-an", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
     "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level", "4.1",
     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
     "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

ink = np.array([int(INK[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0
total = round(DUR * FPS)
for n in range(total):
    t = n / FPS
    if t < KITCHEN_END:
        sn = 0 if t < FREEZE else round((t - FREEZE) * 24)
        frame = push_in(src_frame(sn), t).astype(np.float32) / 255.0
        frame = over(frame, *LBL, 1.0)
    else:
        frame = np.empty((H, W, 3), np.float32)
        frame[:] = ink
    for L in layers:
        o, dy = card_state(L["card"], L["i"], t)
        frame = over(frame, L["rgb"], L["a"], o, dy)
    if t >= LOGO_IN:
        p = ease_out((t - LOGO_IN) / 0.35)
        frame = over(frame, *LOGO, p, round(10 * (1 - p)))
    enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())

enc.stdin.close()
enc.wait()
dec.kill()
print("wrote", OUT, f"touch at {TOUCH:.2f}s, kitchen text size {ksize}px")
