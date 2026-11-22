#!/usr/bin/env python3
"""Düymə olsa — four logo concepts.

Generates, for each concept 01–04:
  NN-<name>/wordmark.svg   full logo (lettering converted to outlines)
  NN-<name>/avatar.svg     circular profile picture
  NN-<name>/endcard.svg    1080×1920 end-card
and board.html, which render.js turns into PNGs.

Type: Inter Display / JetBrains Mono (OFL). All lettering is outlined so the SVGs open
identically anywhere; every element sits in a named <g id> for editing.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
INTER = '/usr/share/fonts/opentype/inter/'
MONO = '/usr/share/fonts/truetype/jetbrains-mono/'
_fonts = {}


def font(path):
    if path not in _fonts:
        f = TTFont(path)
        _fonts[path] = (f, f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm, f['hmtx'])
    return _fonts[path]


def find_mono():
    for root, _, files in os.walk('/usr/share/fonts'):
        for n in files:
            if n.startswith('JetBrainsMono-ExtraBold.'):
                return os.path.join(root, n)
    raise SystemExit('JetBrains Mono ExtraBold not found')


def text(s, fpath, size, x=0.0, y=0.0, track=0.0, kern=None):
    """Outline a string. Returns (svg path d, advance width). y = baseline.
    track is in em; kern maps index -> extra em after that glyph (manual kerning)."""
    f, gs, cmap, upm, hmtx = font(fpath)
    k = size / upm
    pen = SVGPathPen(gs)
    cx = x
    for i, ch in enumerate(s):
        if ch == ' ':
            cx += hmtx[cmap[32]][0] * k + track * size
            continue
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += hmtx[g][0] * k + track * size
        if kern and i in kern:
            cx += kern[i] * size
    return pen.getCommands(), cx - x - track * size


def width(s, fpath, size, track=0.0, kern=None):
    return text(s, fpath, size, track=track, kern=kern)[1]


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'<title>{title}</title>\n{body}\n</svg>\n')


def save(folder, name, content):
    d = os.path.join(HERE, folder)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), 'w', encoding='utf-8') as fh:
        fh.write(content)


BLACK = INTER + 'InterDisplay-Black.otf'
XBOLD = INTER + 'InterDisplay-ExtraBold.otf'
BOLD = INTER + 'InterDisplay-Bold.otf'
SEMI = INTER + 'InterDisplay-SemiBold.otf'
MONOXB = find_mono()

# ───────────────────────────── 01 · BUTTON WORDMARK ─────────────────────────────
# The O of OLSA is a round push-button that sits in the lettering like a real letter.
C1 = dict(bg='#C8102E', bg2='#E0263F', ink='#FFF3DF', btn='#FFB81C', lip='#C77700', hole='#8E0A20')


def button_o(cx, cy, r, c, pressed=False):
    """Round push-button that doubles as the letter O."""
    ring = r * 0.30
    cap = r - ring
    dy = cap * (0.05 if pressed else -0.10)
    return (f'<g id="button-O">'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{c["ink"]}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{cap + ring*0.18:.1f}" fill="{c["hole"]}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy + cap*0.10:.1f}" r="{cap:.1f}" fill="{c["lip"]}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy + dy:.1f}" r="{cap:.1f}" fill="{c["btn"]}"/>'
            f'</g>')


def c1_lockup(x, y, S, c, lines=1):
    """Return (svg, w, h). y = top. lines=1: one line, lines=2: stacked."""
    capH = S * 1490 / 2048
    r = capH * 0.535
    tr = -0.01
    out = []
    if lines == 1:
        base = y + capH
        d1, w1 = text('DÜYMƏ', BLACK, S, x, base, tr)
        gap = S * 0.24
        ox = x + w1 + gap + r
        d2, w2 = text('LSA', BLACK, S, ox + r + S * 0.035, base, tr)
        out.append(f'<path id="DUYME" d="{d1}" fill="{c["ink"]}"/>')
        out.append(button_o(ox, base - capH / 2, r, c))
        out.append(f'<path id="LSA" d="{d2}" fill="{c["ink"]}"/>')
        W = (ox + r + S * 0.035 + w2) - x
        return '\n'.join(out), W, capH
    # stacked: DÜYMƏ over (O)LSA, left aligned
    lead = capH * 1.42
    base1 = y + capH * 1.0
    d1, w1 = text('DÜYMƏ', BLACK, S, x, base1, tr)
    base2 = base1 + lead
    ox = x + r
    d2, w2 = text('LSA', BLACK, S, ox + r + S * 0.035, base2, tr)
    out.append(f'<path id="DUYME" d="{d1}" fill="{c["ink"]}"/>')
    out.append(button_o(ox, base2 - capH / 2, r, c))
    out.append(f'<path id="LSA" d="{d2}" fill="{c["ink"]}"/>')
    W = max(w1, 2 * r + S * 0.035 + w2)
    return '\n'.join(out), W, base2 - y


def concept1():
    c = C1
    S = 200
    body, W, H = c1_lockup(0, 0, S, c)
    pad = 90
    VW, VH = W + pad * 2, H + pad * 2 + 70  # room for umlaut/schwa above cap height
    wm = (f'<rect id="background" width="{VW:.0f}" height="{VH:.0f}" fill="{c["bg"]}"/>'
          f'<g id="logo" transform="translate({pad},{pad + 70})">{body}</g>')
    save('01-button-wordmark', 'wordmark.svg', svg(round(VW), round(VH), wm, 'Düymə olsa — 01 Button wordmark'))
    # avatar: the button-O alone, slightly pressed glow ring
    av = (f'<defs><clipPath id="circle"><circle cx="256" cy="256" r="256"/></clipPath></defs>'
          f'<g clip-path="url(#circle)"><rect id="background" width="512" height="512" fill="{c["bg"]}"/>'
          f'{button_o(256, 256, 150, c)}</g>')
    save('01-button-wordmark', 'avatar.svg', svg(512, 512, av, 'Düymə olsa — 01 avatar'))
    # end-card
    S2 = 210
    body2, W2, H2 = c1_lockup(0, 0, S2, c, lines=2)
    ex = (1080 - W2) / 2
    ec = (f'<defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">'
          f'<stop offset="0" stop-color="{c["bg2"]}"/><stop offset="1" stop-color="{c["bg"]}"/></linearGradient></defs>'
          f'<rect id="background" width="1080" height="1920" fill="url(#g1)"/>'
          f'<g id="logo" transform="translate({ex:.1f},700)">{body2}</g>'
          + follow_pill(540, 1330, c['ink'], c['bg'], c['btn'], style='round'))
    save('01-button-wordmark', 'endcard.svg', svg(1080, 1920, ec, 'Düymə olsa — 01 end-card'))


def follow_pill(cx, cy, fill, txt, accent, style='round'):
    """'İzlə' follow button drawn in each concept's own interface style."""
    s = 46
    label = 'İzlə'
    f = BOLD if style != 'mono' else MONOXB
    w = width(label, f, s)
    pw, ph = w + 150, 104
    x, y = cx - pw / 2, cy - ph / 2
    d, _ = text(label, f, s, x + 100, cy + s * 0.36)
    plus = (f'<path d="M{x+52:.1f} {cy:.1f}h32M{x+68:.1f} {cy-16:.1f}v32" stroke="{accent if style!="mono" else txt}" '
            f'stroke-width="9" stroke-linecap="round"/>')
    if style == 'round':
        return (f'<g id="follow-button"><rect x="{x:.1f}" y="{y:.1f}" width="{pw:.1f}" height="{ph}" rx="{ph/2}" fill="{fill}"/>'
                f'<circle cx="{x+68:.1f}" cy="{cy:.1f}" r="30" fill="{accent}"/>'
                f'<path d="M{x+52:.1f} {cy:.1f}h32M{x+68:.1f} {cy-16:.1f}v32" stroke="{fill}" stroke-width="8" stroke-linecap="round"/>'
                f'<path d="{d}" fill="{txt}"/></g>')
    if style == 'soft':
        return (f'<g id="follow-button"><rect x="{x:.1f}" y="{y+8:.1f}" width="{pw:.1f}" height="{ph}" rx="30" fill="#000" opacity=".25"/>'
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{pw:.1f}" height="{ph}" rx="30" fill="{fill}"/>'
                f'{plus}<path d="{d}" fill="{txt}"/></g>')
    if style == 'mono':
        off = 12
        return (f'<g id="follow-button"><rect x="{x+off:.1f}" y="{y+off:.1f}" width="{pw:.1f}" height="{ph}" rx="14" fill="{txt}"/>'
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{pw:.1f}" height="{ph}" rx="14" fill="{fill}" stroke="{txt}" stroke-width="7"/>'
                f'{plus}<path d="{d}" fill="{txt}"/></g>')
    # outline
    return (f'<g id="follow-button"><rect x="{x:.1f}" y="{y:.1f}" width="{pw:.1f}" height="{ph}" rx="{ph/2}" fill="none" stroke="{fill}" stroke-width="5"/>'
            f'{plus}<path d="{d}" fill="{fill}"/></g>')


# ───────────────────────────── 02 · THE D ICON ─────────────────────────────
# A geometric D whose round counter is a push-button, caught mid-press.
C2 = dict(bg='#0B2545', bg2='#13396B', ink='#F4F1EA', btn='#FF5B4A', well='#071830', lip='#B8352A')


def d_icon(x, y, s, c, on_bg=None):
    """D mark in an s×s box. Stem + half-round bowl; counter = button well."""
    u = s / 100
    well = on_bg or c['well']
    P = lambda v: f'{v*u:.2f}'
    d = (f'M{x+0*u:.2f} {y:.2f}H{x+46*u:.2f}A{50*u:.2f} {50*u:.2f} 0 0 1 {x+46*u:.2f} {y+100*u:.2f}'
         f'H{x:.2f}Z')
    cx, cy, r = x + 46 * u, y + 50 * u, 25 * u
    cap = 17.5 * u
    return (f'<g id="D-mark">'
            f'<path id="D" d="{d}" fill="{c["ink"]}"/>'
            f'<circle id="button-well" cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{well}"/>'
            f'<circle id="button-lip" cx="{cx:.2f}" cy="{cy+3.2*u:.2f}" r="{cap:.2f}" fill="{c["lip"]}"/>'
            f'<circle id="button" cx="{cx:.2f}" cy="{cy+1.6*u:.2f}" r="{cap:.2f}" fill="{c["btn"]}"/>'
            f'<path id="press-arc" d="M{cx-cap*0.62:.2f} {cy-cap*0.30:.2f}A{cap*0.72:.2f} {cap*0.72:.2f} 0 0 1 {cx+cap*0.25:.2f} {cy-cap*0.62:.2f}" '
            f'fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="{3.2*u:.2f}" stroke-linecap="round"/>'
            f'</g>'), 96 * u


def concept2():
    c = C2
    S = 150  # type size
    icon_s = 200
    mark, mw = d_icon(0, 0, icon_s, c)
    gap = 56
    xh = S * 1118 / 2048
    base = icon_s / 2 + xh / 2  # center x-height on icon
    d1, w1 = text('düymə olsa', BOLD, S, mw + gap, base, -0.012)
    pad = 90
    VW, VH = mw + gap + w1 + pad * 2, icon_s + pad * 2
    wm = (f'<rect id="background" width="{VW:.0f}" height="{VH:.0f}" fill="{c["bg"]}"/>'
          f'<g id="logo" transform="translate({pad},{pad})">{mark}'
          f'<path id="name" d="{d1}" fill="{c["ink"]}"/></g>')
    save('02-d-icon', 'wordmark.svg', svg(round(VW), round(VH), wm, 'Düymə olsa — 02 D icon'))
    s = 300
    m2, mw2 = d_icon(0, 0, s, c, on_bg=c['bg'])
    av = (f'<defs><clipPath id="circle"><circle cx="256" cy="256" r="256"/></clipPath></defs>'
          f'<g clip-path="url(#circle)"><rect id="background" width="512" height="512" fill="{c["bg"]}"/>'
          f'<g transform="translate({256 - mw2/2 + 6:.1f},{256 - s/2:.1f})">{m2}</g></g>')
    save('02-d-icon', 'avatar.svg', svg(512, 512, av, 'Düymə olsa — 02 avatar'))
    s3 = 300
    m3, mw3 = d_icon(0, 0, s3, c, on_bg=c['bg2'])
    S3 = 120
    d3, w3 = text('düymə olsa', BOLD, S3, 0, 0, -0.012)
    ec = (f'<defs><radialGradient id="g2" cx=".5" cy=".45" r=".75">'
          f'<stop offset="0" stop-color="{c["bg2"]}"/><stop offset="1" stop-color="{c["bg"]}"/></radialGradient></defs>'
          f'<rect id="background" width="1080" height="1920" fill="url(#g2)"/>'
          f'<g id="mark" transform="translate({540 - mw3/2 + 8:.1f},600)">{m3}</g>'
          f'<path id="name" transform="translate({540 - w3/2:.1f},1060)" d="{d3}" fill="{c["ink"]}"/>'
          + follow_pill(540, 1330, c['btn'], c['ink'], c['ink'], style='soft'))
    save('02-d-icon', 'endcard.svg', svg(1080, 1920, ec, 'Düymə olsa — 02 end-card'))


# ───────────────────────────── 03 · THE TAP ─────────────────────────────
# DÜYMƏ stands raised on its shadow; OLSA has been pressed flat into it.
C3 = dict(bg='#FFC629', bg2='#FFD65C', ink='#1C1A33', face='#FFF8E8', ghost='#1C1A33')


def tap_word(s, x, base, S, c, pressed, depth, sw):
    d, w = text(s, MONOXB, S, x, base, -0.02)
    if pressed:
        # remnant of where the letters stood: hairline outline at the raised position
        return (f'<g id="{s}-pressed">'
                f'<path d="{d}" fill="none" stroke="{c["ghost"]}" stroke-opacity=".5" stroke-width="{sw*0.45:.1f}" '
                f'stroke-dasharray="{sw*1.2:.1f} {sw*1.1:.1f}" stroke-linejoin="round"/>'
                f'<path d="{d}" transform="translate(0,{depth:.1f})" fill="{c["face"]}" stroke="{c["ink"]}" '
                f'stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke"/></g>'), w
    return (f'<g id="{s}-raised">'
            f'<path d="{d}" transform="translate(0,{depth:.1f})" fill="{c["ink"]}" stroke="{c["ink"]}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="{c["face"]}" stroke="{c["ink"]}" stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke"/></g>'), w


def c3_lockup(x, y, S, c, stacked=False):
    capH = S * 0.73
    depth, sw = S * 0.13, S * 0.05
    if not stacked:
        base = y + capH
        g1, w1 = tap_word('DÜYMƏ', x, base, S, c, False, depth, sw)
        g2, w2 = tap_word('OLSA', x + w1 + S * 0.42, base, S, c, True, depth, sw)
        return g1 + g2, w1 + S * 0.42 + w2, capH + depth
    base1 = y + capH
    g1, w1 = tap_word('DÜYMƏ', x, base1, S, c, False, depth, sw)
    base2 = base1 + capH * 1.55
    w2 = width('OLSA', MONOXB, S, -0.02)
    g2, _ = tap_word('OLSA', x + (w1 - w2) / 2, base2, S, c, True, depth, sw)
    return g1 + g2, w1, base2 - y + depth


def concept3():
    c = C3
    S = 190
    body, W, H = c3_lockup(0, 0, S, c)
    pad = 90
    VW, VH = W + pad * 2, H + pad * 2 + 60
    wm = (f'<rect id="background" width="{VW:.0f}" height="{VH:.0f}" fill="{c["bg"]}"/>'
          f'<g id="logo" transform="translate({pad},{pad + 60})">{body}</g>')
    save('03-the-tap', 'wordmark.svg', svg(round(VW), round(VH), wm, 'Düymə olsa — 03 The tap'))
    # avatar: D raised, O pressed — the whole joke in two keys
    S2 = 250
    depth, sw = S2 * 0.13, S2 * 0.055
    capH = S2 * 0.73
    wD = width('D', MONOXB, S2)
    gapk = S2 * 0.06
    tot = wD * 2 + gapk
    x0 = 256 - tot / 2
    base = 256 + capH / 2 - depth / 2
    gD, _ = tap_word('D', x0, base, S2, c, False, depth, sw)
    gO, _ = tap_word('O', x0 + wD + gapk, base, S2, c, True, depth, sw)
    av = (f'<defs><clipPath id="circle"><circle cx="256" cy="256" r="256"/></clipPath></defs>'
          f'<g clip-path="url(#circle)"><rect id="background" width="512" height="512" fill="{c["bg"]}"/>{gD}{gO}</g>')
    save('03-the-tap', 'avatar.svg', svg(512, 512, av, 'Düymə olsa — 03 avatar'))
    S3 = 200
    b3, W3, H3 = c3_lockup(0, 0, S3, c, stacked=True)
    ec = (f'<rect id="background" width="1080" height="1920" fill="{c["bg"]}"/>'
          f'<g id="grid" stroke="{c["ink"]}" stroke-opacity=".07" stroke-width="2">'
          + ''.join(f'<path d="M{i} 0V1920"/>' for i in range(60, 1080, 120))
          + ''.join(f'<path d="M0 {j}H1080"/>' for j in range(0, 1920, 120)) + '</g>'
          f'<g id="logo" transform="translate({540 - W3/2:.1f},700)">{b3}</g>'
          + follow_pill(540, 1330, c['face'], c['ink'], c['ink'], style='mono'))
    save('03-the-tap', 'endcard.svg', svg(1080, 1920, ec, 'Düymə olsa — 03 end-card'))


# ───────────────────────────── 04 · XALANIN BUTASI ─────────────────────────────
# The buta — the paisley on every aunt's kəlağayı — becomes the fingertip that taps.
C4 = dict(bg='#3B0D2E', bg2='#5A1645', ink='#FFF1E2', buta='#F5B027', eye='#3B0D2E', tap='#FF6F7D')

# Buta drawn in a 100×100 box, tip at upper right curling over.
BUTA = 'M92 30C90 10 74 -2 54 2C26 8 4 32 4 60C4 82 20 98 42 98C68 98 86 80 86 58C86 46 80 38 80 30C80 26 84 26 92 30Z'
BUTA_INNER = 'M40 86C26 86 16 76 16 61C16 44 30 26 52 16C40 34 70 40 70 60C70 76 56 86 40 86Z'


def buta_mark(x, y, s, c, eye=True):
    """Buta whose bent tip presses a small round button. 100-unit box."""
    u = s / 100
    g = (f'<g id="buta-mark" transform="translate({x:.2f},{y:.2f}) scale({u:.4f})">'
         f'<g id="tap-ripple" fill="none" stroke="{c["tap"]}" stroke-width="5" stroke-linecap="round">'
         f'<path d="M111 22l7-6"/><path d="M114 38l9 1"/><path d="M100 14l0-9"/></g>'
         f'<circle id="button" cx="101" cy="34" r="8" fill="{c["tap"]}"/>'
         f'<path id="buta" d="{BUTA}" fill="{c["buta"]}"/>')
    if eye:
        g += f'<path id="buta-inner" d="{BUTA_INNER}" fill="none" stroke="{c["eye"]}" stroke-width="5.5" stroke-linejoin="round"/>'
    return g + '</g>'


def c4_name(x, base, S, c):
    """lowercase 'düymə olsa' with the ə in buta saffron."""
    pre, wpre = text('düym', XBOLD, S, x, base, -0.025)
    e, we = text('ə', XBOLD, S, x + wpre - 0.025 * S, base)
    post, wpost = text(' olsa', XBOLD, S, x + wpre - 0.025 * S + we - 0.025 * S, base, -0.025)
    return (f'<g id="name"><path d="{pre}" fill="{c["ink"]}"/><path id="schwa" d="{e}" fill="{c["buta"]}"/>'
            f'<path d="{post}" fill="{c["ink"]}"/></g>'), wpre + we + wpost - 0.05 * S


def concept4():
    c = C4
    s = 210
    S = 150
    pad = 90
    name, wn = c4_name(s + 70, s * 0.62 + S * 0.27, S, c)
    VW, VH = s + 70 + wn + pad * 2 + 20, s + pad * 2 + 30
    wm = (f'<rect id="background" width="{VW:.0f}" height="{VH:.0f}" fill="{c["bg"]}"/>'
          f'<g id="logo" transform="translate({pad},{pad + 30})">{buta_mark(0, 0, s, c)}{name}</g>')
    save('04-xala-butasi', 'wordmark.svg', svg(round(VW), round(VH), wm, 'Düymə olsa — 04 Xalanın butası'))
    av = (f'<defs><clipPath id="circle"><circle cx="256" cy="256" r="256"/></clipPath></defs>'
          f'<g clip-path="url(#circle)"><rect id="background" width="512" height="512" fill="{c["bg"]}"/>'
          f'{buta_mark(112, 138, 270, c)}</g>')
    save('04-xala-butasi', 'avatar.svg', svg(512, 512, av, 'Düymə olsa — 04 avatar'))
    # end-card: faint kəlağayı-style buta field, mark + name
    field = []
    for row in range(9):
        for col in range(6):
            bx = col * 200 - 40 + (100 if row % 2 else 0)
            by = row * 230 - 60
            field.append(f'<path d="{BUTA}" transform="translate({bx},{by}) scale(.9)"/>')
    S3 = 128
    n3, w3 = c4_name(0, 0, S3, c)
    ec = (f'<defs><linearGradient id="g4" x1="0" y1="0" x2="0" y2="1">'
          f'<stop offset="0" stop-color="{c["bg2"]}"/><stop offset="1" stop-color="{c["bg"]}"/></linearGradient></defs>'
          f'<rect id="background" width="1080" height="1920" fill="url(#g4)"/>'
          f'<g id="kelagayi-field" fill="{c["ink"]}" opacity=".045">{"".join(field)}</g>'
          f'{buta_mark(540 - 150, 560, 300, c)}'
          f'<g transform="translate({540 - w3/2:.1f},1070)">{n3}</g>'
          + follow_pill(540, 1330, c['ink'], c['ink'], c['tap'], style='outline'))
    save('04-xala-butasi', 'endcard.svg', svg(1080, 1920, ec, 'Düymə olsa — 04 end-card'))


if __name__ == '__main__':
    concept1(); concept2(); concept3(); concept4()
    print('SVGs written')
