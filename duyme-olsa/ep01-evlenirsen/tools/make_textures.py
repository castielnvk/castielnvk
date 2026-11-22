#!/usr/bin/env python3
"""Procedural textures for the tabletop: süfrə (tablecloth) with buta + 8-point stars,
and a wall carpet. Writes scene/textures/*.png."""
import math, os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), '..', 'scene', 'textures')
os.makedirs(OUT, exist_ok=True)

BUTA = [((92, 30), (90, 10), (74, -2), (54, 2)), ((54, 2), (26, 8), (4, 32), (4, 60)),
        ((4, 60), (4, 82), (20, 98), (42, 98)), ((42, 98), (68, 98), (86, 80), (86, 58)),
        ((86, 58), (86, 46), (80, 38), (80, 30)), ((80, 30), (80, 26), (84, 26), (92, 30))]


def bez(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; d = t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


BUTA_PTS = [p for seg in BUTA for p in bez(*seg)]


def buta(draw, cx, cy, s, rot, fill, inner=None):
    out = []
    for x, y in BUTA_PTS:
        x, y = (x - 48) * s / 100, (y - 50) * s / 100
        c, si = math.cos(rot), math.sin(rot)
        out.append((cx + x * c - y * si, cy + x * si + y * c))
    draw.polygon(out, fill=fill)
    if inner:
        pts = [(cx + (p[0] - cx) * 0.62, cy + (p[1] - cy) * 0.62 + s * 0.06) for p in out]
        draw.polygon(pts, fill=inner)


def star8(draw, cx, cy, r, fill):
    pts = []
    for i in range(16):
        a = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.62
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill)


def tablecloth(N=2048):
    base, gold, cream, deep = (104, 18, 32), (188, 132, 58), (214, 182, 128), (74, 10, 22)
    im = Image.new('RGB', (N, N), base)
    d = ImageDraw.Draw(im)
    cell = N // 4
    for gy in range(4):
        for gx in range(4):
            cx, cy = gx * cell + cell / 2, gy * cell + cell / 2
            # lattice diamonds
            d.polygon([(cx, cy - cell * .5), (cx + cell * .5, cy), (cx, cy + cell * .5), (cx - cell * .5, cy)],
                      outline=deep, width=10)
            buta(d, cx, cy, cell * .50, (gx + gy) % 2 * math.pi, gold)
            buta(d, cx, cy + cell * .03, cell * .30, (gx + gy) % 2 * math.pi, deep)
            buta(d, cx, cy + cell * .05, cell * .14, (gx + gy) % 2 * math.pi, cream)
            star8(d, gx * cell, gy * cell, cell * .12, cream)
            star8(d, gx * cell, gy * cell, cell * .06, base)
    # tile seams (stars at edges repeat)
    for i in range(5):
        for j in range(5):
            star8(d, i * cell, j * cell, cell * .12, cream); star8(d, i * cell, j * cell, cell * .06, base)
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    im.save(os.path.join(OUT, 'tablecloth.png'))
    # woven bump: fine cross-hatch
    b = Image.new('L', (512, 512), 128)
    db = ImageDraw.Draw(b)
    for i in range(0, 512, 4):
        db.line([(i, 0), (i, 512)], fill=150, width=1)
        db.line([(0, i + 2), (512, i + 2)], fill=105, width=1)
    b.filter(ImageFilter.GaussianBlur(.6)).save(os.path.join(OUT, 'weave.png'))


def carpet(W=1024, H=1536):
    red, navy, gold, cream = (140, 28, 30), (24, 30, 64), (200, 150, 70), (226, 206, 170)
    im = Image.new('RGB', (W, H), navy)
    d = ImageDraw.Draw(im)
    d.rectangle([60, 60, W - 60, H - 60], fill=gold)
    d.rectangle([100, 100, W - 100, H - 100], fill=red)
    cx, cy = W / 2, H / 2
    d.polygon([(cx, cy - 420), (cx + 300, cy), (cx, cy + 420), (cx - 300, cy)], fill=navy)
    d.polygon([(cx, cy - 300), (cx + 200, cy), (cx, cy + 300), (cx - 200, cy)], fill=cream)
    star8(d, cx, cy, 120, red)
    for x, y in [(230, 260), (W - 230, 260), (230, H - 260), (W - 230, H - 260)]:
        star8(d, x, y, 90, gold); star8(d, x, y, 45, navy)
    for k in range(6):
        buta(d, 200 + k * 125, H / 2 + (380 if k % 2 else -380) * 0, 70, 0, gold) if False else None
    im.filter(ImageFilter.GaussianBlur(2)).save(os.path.join(OUT, 'carpet.png'))


if __name__ == '__main__':
    tablecloth(); carpet(); print('textures ok')
