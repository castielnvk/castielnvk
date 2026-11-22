"""Shared picture tools for BAXMA DEDİM. episodes: vector text layers, compositing,
graded source decoding, push-ins, grain, and the two-beat logo ending."""
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
from lib import Font, run, svg_doc, place  # noqa: E402
from concepts import c01  # noqa: E402

W, H = 1080, 1920
BONE, INK = "#EEE8DC", "#0D0C0B"
LIGHT = (1.0, 0.945, 0.81)
F_SEMI = Font("inter-tight-latin-600-normal.woff2", "inter-tight-latin-ext-600-normal.woff2")
F_MED = Font("inter-tight-latin-500-normal.woff2", "inter-tight-latin-ext-500-normal.woff2")
F_BOLD = Font("inter-tight-latin-800-normal.woff2", "inter-tight-latin-ext-800-normal.woff2")

SHADOW = ('<defs><filter id="sh" x="-10%" y="-60%" width="120%" height="220%">'
          '<feGaussianBlur in="SourceAlpha" stdDeviation="14" result="b"/>'
          '<feFlood flood-color="#000" flood-opacity="0.78"/><feComposite in2="b" operator="in" result="s"/>'
          '<feGaussianBlur in="SourceAlpha" stdDeviation="3" result="b2"/>'
          '<feFlood flood-color="#000" flood-opacity="0.6"/><feComposite in2="b2" operator="in" result="s2"/>'
          '<feMerge><feMergeNode in="s"/><feMergeNode in="s2"/><feMergeNode in="SourceGraphic"/></feMerge>'
          '</filter></defs>')


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def seg_width(segs, size, track=-0.005):
    return sum(run(f, t, size, track=track).width for t, f in segs)


def text_layer_svg(name, lines, size, x, base, lead, align="left", shadow=True, track=-0.005, opacity=1.0):
    """lines: [[(text, Font), ...], ...] -> SVG string (W×H, transparent)."""
    body = []
    for i, segs in enumerate(lines):
        lw = seg_width(segs, size, track)
        cx = x if align == "left" else (W - lw) / 2
        y = base + i * lead
        for t, f in segs:
            r = run(f, t, size, track=track, x=cx, y=y)
            body.append(r.paths(BONE))
            cx += r.width
    g = "".join(body)
    o = f' opacity="{opacity}"' if opacity < 1 else ""
    inner = (SHADOW + f'<g id="{name}" filter="url(#sh)"{o}>{g}</g>') if shadow else f'<g id="{name}"{o}>{g}</g>'
    return svg_doc(W, H, inner, name)


def render_svgs(jobs, jobs_path):
    with open(jobs_path, "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", os.path.join(ROOT, "render.js"), jobs_path], check=True)
    os.remove(jobs_path)


def load_rgba(p):
    a = np.asarray(Image.open(p).convert("RGBA"), dtype=np.float32) / 255.0
    return a[..., :3], a[..., 3:4]


def over(bg, rgb, a, o=1.0, dy=0, mask=None):
    if o <= 0:
        return bg
    if dy:
        rgb, a = np.roll(rgb, dy, axis=0), np.roll(a, dy, axis=0)
    k = a * o if mask is None else a * o * mask
    return bg * (1 - k) + rgb * k


class Source:
    """Sequential reader of a graded, upscaled source clip (muted)."""

    def __init__(self, path, crop, grade):
        cx, cy, cw, ch = crop
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", path, "-an", "-vf",
             f"crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos,{grade},unsharp=5:5:0.35,format=rgb24",
             "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
        self.idx, self.cur = -1, None

    def frame(self, n):
        while self.idx < n:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            self.cur = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            self.idx += 1
        return self.cur

    def close(self):
        self.p.kill()


def push_in(img, z, center):
    if z <= 1.0001:
        return img
    bw, bh = W / z, H / z
    x0 = min(max(center[0] - bw / 2, 0), W - bw)
    y0 = min(max(center[1] - bh / 2, 0), H - bh)
    return np.asarray(Image.fromarray(img).resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh)))


_grain_rng = np.random.default_rng(21)


def grain(frame, amount=0.022):
    """fine moving film grain (keeps still-frame holds alive)."""
    g = _grain_rng.standard_normal((H // 2, W // 2)).astype(np.float32)
    g = np.asarray(Image.fromarray(g).resize((W, H), Image.BILINEAR))[..., None]
    return frame + g * amount


def ink_frame():
    f = np.empty((H, W, 3), np.float32)
    f[:] = [int(INK[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return f


# ---------------------------------------------------------------------------
# Two-beat logo ending (reusable for every episode)
#   0.00  a thin strip of light opens on BAXMA
#   DEDIM_AT  DEDİM. appears at once (pair with sfx.dry_tick)
#   CUT_AT  hard cut to black (the tick's tail keeps ringing)
ENDING = dict(STRIP=0.40, DEDIM_AT=0.80, CUT_AT=1.55, LENGTH=2.0, LOGO_WIDTH=820, LOGO_CY=930)
# (start, end, brightness) — the light stutters like a dying bulb, then holds
FLICKER = [(0.00, 0.06, 1.0), (0.06, 0.10, 0.08), (0.10, 0.15, 0.9), (0.15, 0.21, 0.0),
           (0.21, 0.25, 0.55), (0.25, 0.29, 0.05), (0.29, 9.9, 1.0)]


def flicker(t):
    for a, b, v in FLICKER:
        if a <= t < b:
            return v
    return 1.0


class LogoEnding:
    def __init__(self, layers_dir):
        c = c01("end")
        inner, bbox = c["wordmark"]
        bax, ded = c["parts"]
        E = ENDING
        jobs = []
        for name, g in (("logo-baxma", bax), ("logo-dedim", ded), ("logo-full", inner)):
            svg = os.path.join(layers_dir, name + ".svg")
            with open(svg, "w", encoding="utf-8") as f:
                f.write(svg_doc(W, H, place(g, bbox, W / 2, E["LOGO_CY"], width=E["LOGO_WIDTH"]), name))
            jobs.append([svg, svg[:-4] + ".png", W, H, 1])
        render_svgs(jobs, os.path.join(layers_dir, "ending-jobs.json"))
        self.bax = load_rgba(os.path.join(layers_dir, "logo-baxma.png"))
        self.ded = load_rgba(os.path.join(layers_dir, "logo-dedim.png"))
        # BAXMA pixel extent
        a = self.bax[1][..., 0]
        rows, cols = np.where(a.sum(1) > 0)[0], np.where(a.sum(0) > 0)[0]
        self.y0, self.y1, self.x0, self.x1 = rows.min(), rows.max(), cols.min(), cols.max()
        self.cy = (self.y0 + self.y1) / 2
        yy = np.arange(H)[:, None]
        self.yy = yy.astype(np.float32)
        xx = np.arange(W)[None, :].astype(np.float32)
        span = 70
        self.xfade = np.clip(np.minimum(xx - (self.x0 - span), (self.x1 + span) - xx) / span, 0, 1)[..., None]

    def frame(self, t):
        E = ENDING
        f = ink_frame()
        if t >= E["CUT_AT"]:
            return f
        p = ease_out(t / E["STRIP"])
        half = 1.5 + p * ((self.y1 - self.y0) / 2 + 6)
        band = (np.abs(self.yy - self.cy) <= half).astype(np.float32)[..., None]
        fl = flicker(t)                               # faulty-bulb stutter while the strip opens
        f = over(f, *self.bax, fl, mask=band)
        # light: the strip edges glow, brightest while the gap is thin, then fade away
        glow_amt = (1 - smooth(t / (E["STRIP"] + 0.25))) * fl
        if glow_amt > 0:
            d = np.minimum(np.abs(self.yy - (self.cy - half)), np.abs(self.yy - (self.cy + half)))[..., None]
            g = (np.exp(-(d / 2.2) ** 2) * 0.9 + np.exp(-(d / 16) ** 2) * 0.22) * self.xfade * glow_amt
            f = f + g * np.array(LIGHT, np.float32)
        if t >= E["DEDIM_AT"]:
            f = over(f, *self.ded, 1.0)
        return f
