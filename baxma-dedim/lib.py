"""Small vector-type toolkit: turns font glyphs into SVG path outlines.

Every letter becomes its own <path>, so the SVGs open in Illustrator/Figma/Inkscape
as editable vector shapes and render identically everywhere (no font needed).
"""
import math
import os

from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

# ---- palette ---------------------------------------------------------------
INK = "#0D0C0B"     # near-black
INK2 = "#171513"    # lifted near-black
BONE = "#E8E1D3"    # bone white
ASH = "#7A7266"     # warm grey
RED = "#B3241C"     # restrained red
LIGHT = "#FFF1CF"   # warm door light


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


class Font:
    def __init__(self, *files, name=""):
        self.name = name
        self.parts = []
        for fn in files:
            f = TTFont(os.path.join(FONT_DIR, fn))
            self.parts.append((f, f.getBestCmap(), f.getGlyphSet()))
        self.upm = self.parts[0][0]["head"].unitsPerEm

    def lookup(self, ch):
        for f, cmap, gs in self.parts:
            if ord(ch) in cmap:
                n = cmap[ord(ch)]
                rec = DecomposingRecordingPen(gs)
                gs[n].draw(rec)
                return rec, f["hmtx"][n][0]
        raise KeyError(f"{ch!r} missing in {self.name}")


class FlatPen(BasePen):
    """Flattens curves to polylines and pushes every point through `fn` (for lens distortion)."""

    def __init__(self, fn, steps=12):
        super().__init__(None)
        self.fn, self.steps, self.out, self.cur = fn, steps, [], (0, 0)

    def _pt(self, p):
        x, y = self.fn(*p)
        return f"{fmt(x)} {fmt(y)}"

    def _moveTo(self, p):
        self.out.append("M" + self._pt(p))
        self.cur = p

    def _lineTo(self, p):
        a, n = self.cur, self.steps
        for i in range(1, n + 1):
            t = i / n
            self.out.append("L" + self._pt((a[0] + (p[0] - a[0]) * t, a[1] + (p[1] - a[1]) * t)))
        self.cur = p

    def _curveToOne(self, p1, p2, p3):
        a, n = self.cur, self.steps
        for i in range(1, n + 1):
            t = i / n
            mt = 1 - t
            x = mt**3 * a[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
            y = mt**3 * a[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
            self.out.append("L" + self._pt((x, y)))
        self.cur = p3

    def _qCurveToOne(self, p1, p2):
        a, n = self.cur, self.steps
        for i in range(1, n + 1):
            t = i / n
            mt = 1 - t
            x = mt * mt * a[0] + 2 * mt * t * p1[0] + t * t * p2[0]
            y = mt * mt * a[1] + 2 * mt * t * p1[1] + t * t * p2[1]
            self.out.append("L" + self._pt((x, y)))
        self.cur = p2

    def _closePath(self):
        self.out.append("Z")

    def d(self):
        return "".join(self.out)


class Glyph:
    def __init__(self, ch, d, bbox, x, adv):
        self.ch, self.d, self.bbox, self.x, self.adv = ch, d, bbox, x, adv


class Run:
    def __init__(self, glyphs, width, size):
        self.glyphs, self.width, self.size = glyphs, width, size

    @property
    def bbox(self):
        bs = [g.bbox for g in self.glyphs if g.bbox]
        return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))

    def paths(self, fill="", extra="", only=None, skip=None, idp=""):
        out = []
        for i, g in enumerate(self.glyphs):
            if only is not None and i not in only:
                continue
            if skip is not None and i in skip:
                continue
            gid = f' id="{idp}{glyph_id(g.ch)}-{i}"' if idp else ""
            f = f' fill="{fill}"' if fill else ""
            out.append(f'<path{gid}{f}{extra} d="{g.d}"/>')
        return "\n".join(out)

    def index(self, ch):
        return [i for i, g in enumerate(self.glyphs) if g.ch == ch]


def glyph_id(ch):
    return {"İ": "Idot", ".": "period", " ": "space"}.get(ch, ch)


def run(font, text, size, track=0.0, x=0.0, y=0.0, distort=None):
    """Lay out `text` with baseline at y, starting at x. track is in em."""
    s = size / font.upm
    cx = x
    glyphs = []
    for ch in text:
        rec, adv = font.lookup(ch)
        if ch != " ":
            t = (s, 0, 0, -s, cx, y)
            if distort:
                pen = FlatPen(distort)
                rec.replay(TransformPen(pen, t))
                d = pen.d()
            else:
                sp = SVGPathPen(None, ntos=fmt)
                rec.replay(TransformPen(sp, t))
                d = sp.getCommands()
            bp = BoundsPen(None)
            rec.replay(TransformPen(bp, t))
            glyphs.append(Glyph(ch, d, bp.bounds, cx, adv * s))
        cx += adv * s + track * size
    return Run(glyphs, cx - track * size - x, size)


def cap_height(font, size):
    r = run(font, "H", size)
    return -r.bbox[1]


def svg_doc(w, h, inner, title=""):
    t = f"<title>{title}</title>\n" if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{fmt(w)}" height="{fmt(h)}" viewBox="0 0 {fmt(w)} {fmt(h)}">\n{t}{inner}\n</svg>\n'
    )


def place(inner, bbox, cx, cy, width=None, height=None):
    """Scale+translate a group (with given bbox) so it is centered on cx,cy at the given width."""
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    s = width / bw if width else height / bh
    tx = cx - (bbox[0] + bw / 2) * s
    ty = cy - (bbox[1] + bh / 2) * s
    return f'<g transform="translate({fmt(tx)} {fmt(ty)}) scale({s:.5f})">\n{inner}\n</g>'


def circle_clip(pid, size=512):
    r = size / 2
    return f'<clipPath id="{pid}clip"><circle cx="{r}" cy="{r}" r="{r}"/></clipPath>'
