"""Caption style C for BAXMA DEDİM. (user's choice, EP05 on).

A card is a centred stack of elements in reading order:
  ("s", "text", t_in)  small spaced capitals (Cormorant Garamond), bone
  ("k", "word", t_in)  the key word: big red italic (Cormorant Garamond Italic)
The full sentence is always kept: the key word sits on its own line in its place.
Elements fade in slowly (no slide). A key word lands with a thud + a camera flinch (see edit.py).
"""
import os
from itertools import combinations

import compose as C
from lib import Font, run, svg_doc

W, H = C.W, C.H
SMALL = Font("cormorant-garamond-latin-500-normal.woff2", "cormorant-garamond-latin-ext-500-normal.woff2",
             name="Cormorant Garamond Medium")
KEY = Font("cormorant-garamond-latin-500-italic.woff2", "cormorant-garamond-latin-ext-500-italic.woff2",
           name="Cormorant Garamond Medium Italic")
S_SIZE, S_TRACK, S_COLOR, S_LEAD = 46, 0.16, "#E4DDCF", 1.55
K_MAX, K_COLOR = 150, "#D8352A"
MAXW = 900


def az_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def _w(font, s, size, track=0.0):
    r = run(font, s, size, track=track)
    return r.bbox[2] - r.bbox[0]


def wrap(text, maxw=MAXW):
    words = text.split()
    for k in range(1, len(words) + 1):
        best = None
        for cuts in combinations(range(1, len(words)), k - 1):
            parts = [" ".join(words[a:b]) for a, b in zip((0,) + cuts, cuts + (len(words),))]
            ws = [_w(SMALL, p, S_SIZE, S_TRACK) for p in parts]
            if max(ws) <= maxw and (best is None or max(ws) - min(ws) < best[0]):
                best = (max(ws) - min(ws), parts)
        if best:
            return best[1]
    return [text]


def _line_paths(font, s, size, y, color, track=0.0):
    r = run(font, s, size, track=track)
    b = r.bbox
    r = run(font, s, size, track=track, x=W / 2 - (b[0] + b[2]) / 2, y=y)
    return r.paths(color)


def build_card(name, elements, cy, layers_dir):
    """returns [(png, t_in, kind)] after writing one SVG per element (rendered by the caller)."""
    rows = []                                  # (kind, text, t_in, size, height)
    for kind, text, t_in in elements:
        if kind == "s":
            for part in wrap(az_upper(text)):
                rows.append(("s", part, t_in, S_SIZE, S_SIZE * S_LEAD))
        else:
            size = min(K_MAX, K_MAX * MAXW / _w(KEY, text, K_MAX))
            rows.append(("k", text, t_in, size, size * 1.08))
    total = sum(r[4] for r in rows)
    y = cy - total / 2
    out, jobs = [], []
    for i, (kind, text, t_in, size, h) in enumerate(rows):
        base = y + h * (0.70 if kind == "s" else 0.78)
        font, color, track = (SMALL, S_COLOR, S_TRACK) if kind == "s" else (KEY, K_COLOR, 0.0)
        svg = os.path.join(layers_dir, f"{name}-{i + 1}{kind}.svg")
        with open(svg, "w", encoding="utf-8") as f:
            f.write(svg_doc(W, H, C.SHADOW + f'<g id="{name}-{i + 1}" filter="url(#sh)">'
                            + _line_paths(font, text, size, base, color, track) + "</g>", f"{name} {kind}"))
        jobs.append([svg, svg[:-4] + ".png", W, H, 1])
        out.append(dict(png=svg[:-4] + ".png", t_in=t_in, kind=kind, band=(y, y + h)))
        y += h
    return out, jobs
