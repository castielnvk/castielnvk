"""The six BAXMA DEDİM. logo concepts.

Each concept returns:
  wordmark: (svg_inner, bbox)  – transparent, in its own coordinates
  avatar:   svg_inner for a 512×512 circle avatar
  endcard:  svg_inner for a 1080×1920 end card
  panel:    background colour the wordmark is designed for
"""
import math

from lib import (ASH, BONE, INK, INK2, LIGHT, RED, Font, cap_height, circle_clip, fmt, place, run)

NAME1, NAME2 = "BAXMA", "DEDİM."

ANTON = Font("anton-latin-400-normal.woff2", "anton-latin-ext-400-normal.woff2", name="Anton")
ISERIF_I = Font("instrument-serif-latin-400-italic.woff2", "instrument-serif-latin-ext-400-italic.woff2",
                name="Instrument Serif Italic")
OSWALD = Font("oswald-latin-600-normal.woff2", "oswald-latin-ext-600-normal.woff2", name="Oswald SemiBold")
ITIGHT = Font("inter-tight-latin-700-normal.woff2", "inter-tight-latin-ext-700-normal.woff2", name="Inter Tight Bold")
ITIGHT5 = Font("inter-tight-latin-500-normal.woff2", "inter-tight-latin-ext-500-normal.woff2", name="Inter Tight Medium")
ARCHIVO = Font("archivo-black-latin-400-normal.woff2", "archivo-black-latin-ext-400-normal.woff2", name="Archivo Black")
MONO = Font("space-mono-latin-700-normal.woff2", "space-mono-latin-ext-700-normal.woff2", name="Space Mono Bold")
MONO4 = Font("space-mono-latin-400-normal.woff2", "space-mono-latin-ext-400-normal.woff2", name="Space Mono")
DMSERIF = Font("dm-serif-display-latin-400-normal.woff2", "dm-serif-display-latin-ext-400-normal.woff2",
               name="DM Serif Display")

CAPTION = "Abunə ol — növbəti daha pisdir."


def caption(y, color, font=ITIGHT5, size=34, track=0.02, text=CAPTION, cx=540):
    r = run(font, text, size, track)
    return f'<g id="caption" transform="translate({fmt(cx - r.width / 2)} {fmt(y)})">{r.paths(color)}</g>'


def bg_rect(w, h, color, pid=""):
    return f'<rect id="{pid}background" width="{w}" height="{h}" fill="{color}"/>'


def grain(pid, opacity=0.06):
    """Very subtle film grain for end cards (filter, keeps file vector)."""
    return (f'<filter id="{pid}grain" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 {opacity} 0"/></filter>'
            f'<rect width="1080" height="1920" filter="url(#{pid}grain)"/>')


def avatar_frame(pid, bg, body):
    return (f'<defs>{circle_clip(pid)}</defs><g clip-path="url(#{pid}clip)">'
            f'<rect width="512" height="512" fill="{bg}"/>{body}</g>')


# ---------------------------------------------------------------------------
# 01 — The warning
# ---------------------------------------------------------------------------
def c01(pid="c01"):
    top = run(ANTON, NAME1, 400, track=0.005)
    x0, y0, x1, _ = top.bbox
    W = x1 - x0
    cap = -y0
    probe = run(ISERIF_I, NAME2, 100)
    size = 100 * (0.50 * W) / probe.width
    probe = run(ISERIF_I, NAME2, size)
    pcap = cap_height(ISERIF_I, size)
    base2 = cap * 0.0 + 0.16 * cap + pcap          # small gap under BAXMA
    xr = x1 + 0.045 * W                            # overhangs the right edge: the "correction"
    low = run(ISERIF_I, NAME2, size, x=xr - probe.width, y=base2)
    inner = (f'<g id="{pid}-BAXMA">{top.paths(BONE, idp=pid + "-")}</g>\n'
             f'<g id="{pid}-DEDIM">{low.paths(RED, idp=pid + "-")}</g>')
    lb = low.bbox
    m = 0.08 * W
    bbox = (x0 - m, y0 - m, max(x1, lb[2]) + m, lb[3] + m)

    # avatar: big B, red italic D. dropped just below and past its right side (the late correction).
    # The serif D. gets a same-colour stroke so it survives 48 px.
    B = run(ANTON, "B", 380)
    bx0, by0, bx1, by1 = B.bbox
    dsize = 300
    dcap = cap_height(ISERIF_I, dsize)
    D = run(ISERIF_I, "D.", dsize, x=bx1 - 0.06 * dsize, y=by1 + 0.36 * dcap)
    db = D.bbox
    thick = f' stroke="{RED}" stroke-width="{fmt(0.035 * dsize)}" stroke-linejoin="round"'
    grp = f'{B.paths(BONE)}{D.paths(RED, extra=thick)}'
    av = avatar_frame(pid + "a", INK, place(grp, (bx0, by0, db[2], db[3]), 252, 256, width=290))

    ec = (bg_rect(1080, 1920, INK) + place(inner, bbox, 540, 900, width=900) +
          f'<rect x="490" y="1560" width="100" height="3" fill="{RED}"/>' + caption(1640, ASH) + grain(pid))
    parts = (f'<g id="{pid}-BAXMA">{top.paths(BONE, idp=pid + "-")}</g>',
             f'<g id="{pid}-DEDIM">{low.paths(RED, idp=pid + "-")}</g>')
    return dict(wordmark=(inner, bbox), parts=parts, baxma_bbox=top.bbox, avatar=av, endcard=ec, panel=INK,
                fonts="Anton · Instrument Serif Italic")


# ---------------------------------------------------------------------------
# 02 — The door gap
# ---------------------------------------------------------------------------
def c02(pid="c02"):
    size = 300
    cap = cap_height(OSWALD, size)
    left = run(OSWALD, NAME1, size, track=0.03)
    gap = 0.34 * cap
    right = run(OSWALD, NAME2, size, track=0.03, x=left.width + gap)
    lx0 = left.bbox[0]
    rx1 = right.bbox[2]
    cx = left.width + gap / 2
    top_y, bot_y = -cap * 1.30, cap * 0.10
    wt, wb = 0.030 * cap, 0.060 * cap
    slit = (f'M{fmt(cx - wt / 2)} {fmt(top_y)}L{fmt(cx + wt / 2)} {fmt(top_y)}'
            f'L{fmt(cx + wb / 2)} {fmt(bot_y)}L{fmt(cx - wb / 2)} {fmt(bot_y)}Z')
    spill = (f'M{fmt(cx - wb / 2)} {fmt(bot_y)}L{fmt(cx + wb / 2)} {fmt(bot_y)}'
             f'L{fmt(cx + 1.9 * cap)} {fmt(cap * 0.95)}L{fmt(cx - 0.9 * cap)} {fmt(cap * 0.95)}Z')
    defs = f'''<defs>
<linearGradient id="{pid}gl" gradientUnits="userSpaceOnUse" x1="{fmt(lx0)}" y1="0" x2="{fmt(cx)}" y2="0">
  <stop offset="0" stop-color="#6E675D"/><stop offset="0.75" stop-color="#B9B2A4"/><stop offset="1" stop-color="{BONE}"/></linearGradient>
<linearGradient id="{pid}gr" gradientUnits="userSpaceOnUse" x1="{fmt(cx)}" y1="0" x2="{fmt(rx1)}" y2="0">
  <stop offset="0" stop-color="{BONE}"/><stop offset="0.25" stop-color="#B9B2A4"/><stop offset="1" stop-color="#6E675D"/></linearGradient>
<linearGradient id="{pid}gs" gradientUnits="userSpaceOnUse" x1="0" y1="{fmt(top_y)}" x2="0" y2="{fmt(bot_y)}">
  <stop offset="0" stop-color="{LIGHT}" stop-opacity="0.55"/><stop offset="0.35" stop-color="#FFFFFF"/><stop offset="1" stop-color="{LIGHT}"/></linearGradient>
<linearGradient id="{pid}gf" gradientUnits="userSpaceOnUse" x1="0" y1="{fmt(bot_y)}" x2="0" y2="{fmt(cap * 0.95)}">
  <stop offset="0" stop-color="{LIGHT}" stop-opacity="0.30"/><stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>
<filter id="{pid}glow" x="-400%" y="-20%" width="900%" height="140%"><feGaussianBlur stdDeviation="{fmt(0.05 * cap)}"/></filter>
</defs>'''
    inner = (defs +
             f'<path id="{pid}-floor-light" d="{spill}" fill="url(#{pid}gf)"/>\n'
             f'<path id="{pid}-glow" d="{slit}" fill="{LIGHT}" opacity="0.7" filter="url(#{pid}glow)"/>\n'
             f'<path id="{pid}-door-gap" d="{slit}" fill="url(#{pid}gs)"/>\n'
             f'<g id="{pid}-BAXMA">{left.paths(f"url(#{pid}gl)", idp=pid + "-")}</g>\n'
             f'<g id="{pid}-DEDIM">{right.paths(f"url(#{pid}gr)", idp=pid + "-")}</g>')
    m = 0.25 * cap
    bbox = (lx0 - m, top_y - m, rx1 + m, cap * 0.95)

    # avatar: B | D with the gap
    s2 = 300
    c2 = cap_height(OSWALD, s2)
    B = run(OSWALD, "B", s2)
    g2 = 0.36 * c2
    D = run(OSWALD, "D", s2, x=B.width + g2)
    ax = B.width + g2 / 2
    at, ab = -c2 * 1.25, c2 * 0.12
    sl2 = (f'M{fmt(ax - 4)} {fmt(at)}L{fmt(ax + 4)} {fmt(at)}L{fmt(ax + 8)} {fmt(ab)}L{fmt(ax - 8)} {fmt(ab)}Z')
    sp2 = (f'M{fmt(ax - 8)} {fmt(ab)}L{fmt(ax + 8)} {fmt(ab)}L{fmt(ax + 1.6 * c2)} {fmt(c2 * 0.9)}'
           f'L{fmt(ax - 0.8 * c2)} {fmt(c2 * 0.9)}Z')
    adefs = f'''<defs>
<linearGradient id="{pid}agl" gradientUnits="userSpaceOnUse" x1="{fmt(B.bbox[0])}" y1="0" x2="{fmt(ax)}" y2="0">
  <stop offset="0" stop-color="#857D71"/><stop offset="1" stop-color="{BONE}"/></linearGradient>
<linearGradient id="{pid}agr" gradientUnits="userSpaceOnUse" x1="{fmt(ax)}" y1="0" x2="{fmt(D.bbox[2])}" y2="0">
  <stop offset="0" stop-color="{BONE}"/><stop offset="1" stop-color="#857D71"/></linearGradient>
<linearGradient id="{pid}agf" gradientUnits="userSpaceOnUse" x1="0" y1="{fmt(ab)}" x2="0" y2="{fmt(c2 * 0.9)}">
  <stop offset="0" stop-color="{LIGHT}" stop-opacity="0.35"/><stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>
<filter id="{pid}aglow" x="-400%" y="-20%" width="900%" height="140%"><feGaussianBlur stdDeviation="9"/></filter></defs>'''
    agrp = (adefs + f'<path d="{sp2}" fill="url(#{pid}agf)"/><path d="{sl2}" fill="{LIGHT}" filter="url(#{pid}aglow)"/>'
            f'<path d="{sl2}" fill="#FFFFFF"/>{B.paths(f"url(#{pid}agl)")}{D.paths(f"url(#{pid}agr)")}')
    av = avatar_frame(pid + "a", INK, place(agrp, (B.bbox[0], at, D.bbox[2], c2 * 0.9), 256, 262, width=330))

    ec = (bg_rect(1080, 1920, INK) +
          f'<defs><radialGradient id="{pid}ev" cx="0.5" cy="0.47" r="0.6"><stop offset="0" stop-color="#1A1815"/>'
          f'<stop offset="1" stop-color="{INK}"/></radialGradient></defs><rect width="1080" height="1920" fill="url(#{pid}ev)"/>' +
          place(inner, bbox, 540, 900, width=960) + caption(1640, ASH) + grain(pid))
    return dict(wordmark=(inner, bbox), avatar=av, endcard=ec, panel=INK, fonts="Oswald SemiBold")


# ---------------------------------------------------------------------------
# 03 — The second look (one wrong shadow)
# ---------------------------------------------------------------------------
def _shadowed(r, size, wrong, pid, fill=INK, dx=0.10, dy=0.045, blur=0.016, op=0.17):
    sh = []
    for i, g in enumerate(r.glyphs):
        sx = -dx if i in wrong else dx
        sh.append(f'<path transform="translate({fmt(sx * size)} {fmt(dy * size)})" d="{g.d}"/>')
    return (f'<defs><filter id="{pid}soft" x="-20%" y="-20%" width="140%" height="140%">'
            f'<feGaussianBlur stdDeviation="{fmt(blur * size)}"/></filter></defs>'
            f'<g id="{pid}-shadows" fill="{INK}" opacity="{op}" filter="url(#{pid}soft)">{"".join(sh)}</g>\n'
            f'<g id="{pid}-letters">{r.paths(fill, idp=pid + "-")}</g>')


def c03(pid="c03"):
    size = 220
    r = run(ITIGHT, NAME1 + " " + NAME2, size, track=0.045)
    wrong = set(r.index("İ"))
    inner = _shadowed(r, size, wrong, pid)
    b = r.bbox
    m = 0.22 * size
    bbox = (b[0] - m, b[1] - m, b[2] + m, b[3] + m)

    a = run(ITIGHT, "BD", 300, track=0.16)
    av_inner = _shadowed(a, 300, {1}, pid + "a", dx=0.12, dy=0.05, op=0.24)
    ab = a.bbox
    av = avatar_frame(pid + "a", BONE, place(av_inner, (ab[0] - 20, ab[1], ab[2] + 20, ab[3] + 16), 256, 256, width=330))

    ec = (bg_rect(1080, 1920, BONE) +
          f'<defs><radialGradient id="{pid}ev" cx="0.28" cy="0.30" r="0.95"><stop offset="0" stop-color="#F1ECE1"/>'
          f'<stop offset="1" stop-color="#CFC6B5"/></radialGradient></defs><rect width="1080" height="1920" fill="url(#{pid}ev)"/>' +
          place(inner, bbox, 540, 900, width=980) +
          caption(1640, "#6A6256") + grain(pid, 0.05))
    return dict(wordmark=(inner, bbox), avatar=av, endcard=ec, panel=BONE, fonts="Inter Tight Bold")


# ---------------------------------------------------------------------------
# 04 — The red dot (still recording)
# ---------------------------------------------------------------------------
def c04(pid="c04"):
    size = 300
    cap = cap_height(ARCHIVO, size)
    l1 = run(ARCHIVO, NAME1, size, track=0.0)
    w1 = l1.bbox[2] - l1.bbox[0]
    rdot = 0.15 * cap
    dgap = 0.10 * cap

    def line2(track):
        r = run(ARCHIVO, "DEDİM", size, track=track, y=cap * 1.36)
        return r, (r.bbox[2] + dgap + 2 * rdot) - r.bbox[0]

    lo, hi = -0.1, 0.3
    for _ in range(40):
        mid = (lo + hi) / 2
        if line2(mid)[1] < w1:
            lo = mid
        else:
            hi = mid
    l2, _ = line2(lo)
    x0 = l1.bbox[0]
    l2s = x0 - l2.bbox[0]
    dcx = l2.bbox[2] + l2s + dgap + rdot
    dcy = cap * 1.36 - rdot
    top = l1.bbox[1]
    bottom = cap * 1.36
    x1 = x0 + w1

    def brackets(x0, y0, x1, y1, arm, sw, color):
        p = (f'M{fmt(x0)} {fmt(y0 + arm)}V{fmt(y0)}H{fmt(x0 + arm)}'
             f'M{fmt(x1 - arm)} {fmt(y0)}H{fmt(x1)}V{fmt(y0 + arm)}'
             f'M{fmt(x1)} {fmt(y1 - arm)}V{fmt(y1)}H{fmt(x1 - arm)}'
             f'M{fmt(x0 + arm)} {fmt(y1)}H{fmt(x0)}V{fmt(y1 - arm)}')
        return f'<path id="{pid}-viewfinder" d="{p}" fill="none" stroke="{color}" stroke-width="{fmt(sw)}" stroke-linecap="square"/>'

    pad = 0.38 * cap
    rec = (f'<defs><radialGradient id="{pid}halo"><stop offset="0.35" stop-color="{RED}" stop-opacity="0.55"/>'
           f'<stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient></defs>'
           f'<circle id="{pid}-rec-halo" cx="{fmt(dcx)}" cy="{fmt(dcy)}" r="{fmt(rdot * 2.6)}" fill="url(#{pid}halo)"/>'
           f'<circle id="{pid}-rec-dot" cx="{fmt(dcx)}" cy="{fmt(dcy)}" r="{fmt(rdot)}" fill="#D7261C"/>')
    inner = (rec +
             f'<g id="{pid}-BAXMA">{l1.paths(BONE, idp=pid + "-")}</g>\n'
             f'<g id="{pid}-DEDIM" transform="translate({fmt(l2s)} 0)">{l2.paths(BONE, idp=pid + "-")}</g>\n' +
             brackets(x0 - pad, top - pad, x1 + pad, bottom + pad, 0.34 * cap, 0.05 * cap, BONE))
    m = 0.08 * cap
    bbox = (x0 - pad - m, top - pad - m, x1 + pad + m, bottom + pad + m)

    # avatar: B over D + dot, inside viewfinder
    s = 300
    c = cap_height(ARCHIVO, s)
    B = run(ARCHIVO, "BD", s, track=0.02)
    rd = 0.2 * c
    ex = B.bbox[2] + 0.12 * c + rd
    ey = -rd
    ab = (B.bbox[0], B.bbox[1], ex + rd, 0)
    p2 = 0.42 * c
    agrp = (f'<defs><radialGradient id="{pid}ahalo"><stop offset="0.35" stop-color="{RED}" stop-opacity="0.6"/>'
            f'<stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient></defs>'
            f'<circle cx="{fmt(ex)}" cy="{fmt(ey)}" r="{fmt(rd * 2.5)}" fill="url(#{pid}ahalo)"/>'
            f'<circle cx="{fmt(ex)}" cy="{fmt(ey)}" r="{fmt(rd)}" fill="#D7261C"/>' + B.paths(BONE) +
            brackets(ab[0] - p2, ab[1] - p2, ab[2] + p2, ab[3] + p2, 0.4 * c, 0.075 * c, BONE))
    av = avatar_frame(pid + "a", INK, place(agrp, (ab[0] - p2, ab[1] - p2, ab[2] + p2, ab[3] + p2), 256, 256, width=360))

    tc = run(MONO4, "REC  00:00:13", 30, track=0.08)
    ec = (bg_rect(1080, 1920, INK) +
          f'<circle cx="112" cy="139" r="11" fill="#D7261C"/>'
          f'<g transform="translate(136 150)">{tc.paths(ASH)}</g>' +
          place(inner, bbox, 540, 900, width=820) + caption(1640, ASH) + grain(pid))
    return dict(wordmark=(inner, bbox), avatar=av, endcard=ec, panel=INK, fonts="Archivo Black")


# ---------------------------------------------------------------------------
# 05 — The redaction
# ---------------------------------------------------------------------------
def _redacted(r, size, i0, i1, pid, ink=INK, ghost="#3E3933", red_last=True, padl=0.10):
    cap = -r.glyphs[0].bbox[1]
    gx0 = r.glyphs[i0].bbox[0]
    gx1 = r.glyphs[i1].bbox[2]
    bx0, bx1 = gx0 - padl * size, gx1 + 0.07 * size
    by0, by1 = -cap * 0.60, cap * 0.17
    bar = f'M{fmt(bx0)} {fmt(by0)}H{fmt(bx1)}V{fmt(by1)}H{fmt(bx0)}Z'
    last = len(r.glyphs) - 1
    body = r.paths(ink, skip={last} if red_last else None, idp=pid + "-")
    per = r.paths(RED, only={last}, idp=pid + "-") if red_last else ""
    ghost_g = r.paths(ghost, only=set(range(i0, i1 + 1)))
    return (f'<defs><clipPath id="{pid}barclip"><path d="{bar}"/></clipPath></defs>'
            f'<g id="{pid}-letters">{body}{per}</g>\n'
            f'<path id="{pid}-redaction-bar" d="{bar}" fill="#050505"/>\n'
            f'<g id="{pid}-seen-through" clip-path="url(#{pid}barclip)">{ghost_g}</g>')


def c05(pid="c05"):
    size = 200
    r = run(MONO, NAME1 + " " + NAME2, size, track=-0.02)
    d0 = 5  # glyph index of first D in DEDİM (space is not a glyph)
    inner = _redacted(r, size, d0, d0 + 4, pid)
    b = r.bbox
    m = 0.2 * size
    bbox = (b[0] - m, b[1] - m, b[2] + m, b[3] + m)

    a = run(MONO, "BD.", 300, track=0.04)
    av_in = _redacted(a, 300, 1, 1, pid + "a", padl=0.03)
    ab = a.bbox
    av = avatar_frame(pid + "a", BONE, place(av_in, ab, 256, 256, width=360))

    # end card: a slip of bone paper on near-black
    slip_w, slip_h = 940, 330
    paper = (f'<g transform="rotate(-1.6 540 900)">'
             f'<rect x="{540 - slip_w / 2 + 10}" y="{900 - slip_h / 2 + 16}" width="{slip_w}" height="{slip_h}" fill="#000" opacity="0.5"/>'
             f'<rect x="{540 - slip_w / 2}" y="{900 - slip_h / 2}" width="{slip_w}" height="{slip_h}" fill="{BONE}"/>' +
             place(inner, bbox, 540, 900, width=900) +
             f'<g transform="translate({540 - slip_w / 2 + 40} {900 + slip_h / 2 - 30})">'
             f'{run(MONO4, "GİZLİ · ARXİV 013 · BİR BAXIŞ", 20, 0.06).paths("#8C8477")}</g></g>')
    ec = bg_rect(1080, 1920, INK) + paper + caption(1640, ASH) + grain(pid)
    return dict(wordmark=(inner, bbox), avatar=av, endcard=ec, panel=BONE, fonts="Space Mono Bold")


# ---------------------------------------------------------------------------
# 06 — The peephole (own concept)
# ---------------------------------------------------------------------------
def _peephole(pid, lines, R=300, size=None, avatar=False):
    """Door viewer: the words seen through a fisheye lens."""
    # lay out the lines in flat space first, centred at 0,0
    font = DMSERIF
    size = size or 150
    cap = cap_height(font, size)
    lead = cap * 1.32
    runs = [run(font, t, size, track=0.02) for t in lines]
    n = len(runs)
    flat = []
    for k, t in enumerate(lines):
        w = runs[k].bbox[2] - runs[k].bbox[0]
        by = (k - (n - 1) / 2) * lead + cap / 2
        flat.append((t, -w / 2 - runs[k].bbox[0], by))
    # radius of the flat text block corner
    Rt = R * 0.97
    maxr = 0
    for k, (t, x, y) in enumerate(flat):
        rr = run(font, t, size, track=0.02, x=x, y=y).bbox
        for px in (rr[0], rr[2]):
            for py in (rr[1], rr[3]):
                maxr = max(maxr, math.hypot(px, py))
    k_fit = (R * 0.80) / maxr  # pre-scale so flat block sits inside the lens

    def lens(x, y):
        x, y = x * k_fit, y * k_fit
        r = math.hypot(x, y)
        if r == 0:
            return x, y
        u = min(r / Rt, 1.0)
        f = 0.62 * math.sin(u * math.pi / 2) + 0.38 * u
        s = (f * Rt) / r
        return x * s, y * s

    text = []
    for t, x, y in flat:
        text.append(run(font, t, size, track=0.02, x=x, y=y, distort=lens).paths(BONE, idp="" if avatar else pid + "-"))
    ring = R * 1.24
    defs = f'''<defs>
<radialGradient id="{pid}view" cx="0.5" cy="0.46" r="0.55"><stop offset="0" stop-color="#2A2622"/><stop offset="0.75" stop-color="#15130F"/><stop offset="1" stop-color="#050404"/></radialGradient>
<linearGradient id="{pid}metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9C9383"/><stop offset="0.45" stop-color="#4A453D"/><stop offset="1" stop-color="#151311"/></linearGradient>
<linearGradient id="{pid}metal2" x1="1" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#8E8576"/><stop offset="1" stop-color="#1B1916"/></linearGradient>
<radialGradient id="{pid}rim" cx="0.5" cy="0.5" r="0.5"><stop offset="0.86" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.85"/></radialGradient>
<clipPath id="{pid}lensclip"><circle r="{fmt(R)}"/></clipPath>
</defs>'''
    body = (defs +
            f'<circle id="{pid}-ring" r="{fmt(ring)}" fill="url(#{pid}metal)"/>'
            f'<circle r="{fmt(R * 1.07)}" fill="url(#{pid}metal2)"/>'
            f'<circle id="{pid}-lens" r="{fmt(R)}" fill="url(#{pid}view)"/>'
            f'<g id="{pid}-seen-through-lens" clip-path="url(#{pid}lensclip)">{"".join(text)}</g>'
            f'<circle r="{fmt(R)}" fill="url(#{pid}rim)"/>'
            f'<path id="{pid}-glass-glint" d="M{fmt(-R * 0.72)} {fmt(-R * 0.30)}A{fmt(R * 0.78)} {fmt(R * 0.78)} 0 0 1 {fmt(-R * 0.18)} {fmt(-R * 0.74)}" '
            f'fill="none" stroke="#FFFFFF" stroke-opacity="0.16" stroke-width="{fmt(R * 0.045)}" stroke-linecap="round"/>')
    return body, ring


def c06(pid="c06"):
    inner, ring = _peephole(pid, [NAME1, NAME2])
    m = ring * 0.06
    bbox = (-ring - m, -ring - m, ring + m, ring + m)
    ab, aring = _peephole(pid + "a", ["BD."], R=300, size=260, avatar=True)
    av = avatar_frame(pid + "a", INK, place(ab, (-aring, -aring, aring, aring), 256, 256, width=512))
    ec = (bg_rect(1080, 1920, INK) +
          f'<defs><radialGradient id="{pid}door" cx="0.5" cy="0.47" r="0.7"><stop offset="0" stop-color="#211E1A"/>'
          f'<stop offset="1" stop-color="{INK}"/></radialGradient></defs><rect width="1080" height="1920" fill="url(#{pid}door)"/>' +
          place(inner, bbox, 540, 880, width=820) + caption(1640, ASH) + grain(pid))
    return dict(wordmark=(inner, bbox), avatar=av, endcard=ec, panel=INK, fonts="DM Serif Display")


CONCEPTS = [
    ("01", "xeberdarliq", "The warning", c01,
     "An oversized BAXMA shouts the warning, and the small red DEDİM. sits just off its edge like the quiet correction that came a second too late."),
    ("02", "qapi-araligi", "The door gap", c02,
     "A thin strip of light between the two words turns the space into a door left slightly open, so the name is lit only where you shouldn't be looking."),
    ("03", "ikinci-baxis", "The second look", c03,
     "A calm, precise wordmark where every letter's shadow agrees except the İ's, which falls toward the light. Once you see it, you can't stop seeing it."),
    ("04", "qirmizi-noqte", "The red dot", c04,
     "The period becomes a live REC light inside a viewfinder, a compact block that says the warning came too late because you're already being recorded."),
    ("05", "senzura", "The redaction", c05,
     "A black bar slides over DEDİM. but doesn't quite hide it, leaving only the red period, like a file you were allowed to glimpse for one second."),
    ("06", "qapi-gozu", "The peephole", c06,
     "The name is seen through a door viewer's fisheye lens, so reading the logo means doing exactly what it tells you not to: looking."),
]
