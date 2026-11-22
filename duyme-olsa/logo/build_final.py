#!/usr/bin/env python3
"""Düymə olsa — final logo package (concept 02, the D icon).

Writes svg/*.svg, anim/endcard.html (frame-driven animation) and anim/click.wav.
Then run:  node render_final.js   (PNGs + animated end-card MP4)
"""
import os, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'logo-concepts'))
from build import text, width, BOLD  # noqa: E402  (outlined Inter Display Bold)

NAVY, NAVY2, WELL = '#0B2545', '#13396B', '#071830'
CREAM, CORAL, LIP = '#F4F1EA', '#FF5B4A', '#B8352A'
NAME = 'düymə olsa'
TRACK = -0.012

# Button positions (in mark units, relative to counter centre)
UP, REST, DOWN = -2.2, 1.6, 3.2


def d_path(x, y, u):
    """Refined D: half-round bowl, softly rounded stem corners."""
    r = 5 * u
    return (f'M{x+r:.2f} {y:.2f}H{x+46*u:.2f}A{50*u:.2f} {50*u:.2f} 0 0 1 {x+46*u:.2f} {y+100*u:.2f}'
            f'H{x+r:.2f}Q{x:.2f} {y+100*u:.2f} {x:.2f} {y+100*u-r:.2f}V{y+r:.2f}Q{x:.2f} {y:.2f} {x+r:.2f} {y:.2f}Z')


def mark(x, y, s, d=CREAM, well=WELL, btn=CORAL, lip=LIP, btn_off=REST, ids=True):
    """Full-colour D mark in an s-tall box (width 0.96·s)."""
    u = s / 100
    cx, cy, r, cap = x + 46 * u, y + 50 * u, 25 * u, 17.5 * u
    i = (lambda n: f' id="{n}"') if ids else (lambda n: '')
    return (f'<g{i("D-mark")}>'
            f'<path{i("D")} d="{d_path(x, y, u)}" fill="{d}"/>'
            f'<circle{i("button-well")} cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{well}"/>'
            f'<circle{i("button-lip")} cx="{cx:.2f}" cy="{cy+DOWN*u:.2f}" r="{cap:.2f}" fill="{lip}"/>'
            f'<g{i("button")} transform="translate(0 {btn_off*u:.2f})">'
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{cap:.2f}" fill="{btn}"/>'
            f'<path d="M{cx-cap*0.62:.2f} {cy-cap*0.30:.2f}A{cap*0.72:.2f} {cap*0.72:.2f} 0 0 1 {cx+cap*0.25:.2f} {cy-cap*0.62:.2f}" '
            f'fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="{3.2*u:.2f}" stroke-linecap="round"/></g>'
            f'</g>'), 96 * u


def mark_mono(x, y, s, color):
    """One-colour version: D with the counter cut out, button as a solid disc."""
    u = s / 100
    cx, cy, r, cap = x + 46 * u, y + 50 * u, 25 * u, 17.5 * u
    hole = (f'M{cx-r:.2f} {cy:.2f}a{r:.2f} {r:.2f} 0 1 0 {2*r:.2f} 0a{r:.2f} {r:.2f} 0 1 0 {-2*r:.2f} 0Z')
    return (f'<g id="D-mark"><path id="D" fill-rule="evenodd" d="{d_path(x, y, u)}{hole}" fill="{color}"/>'
            f'<circle id="button" cx="{cx:.2f}" cy="{cy+REST*u*0.6:.2f}" r="{cap*0.92:.2f}" fill="{color}"/></g>'), 96 * u


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">\n'
            f'<title>{title}</title>\n{body}\n</svg>\n')


def save(rel, content):
    p = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(content)


def name_path(x, base, S, color, idn='name'):
    d, w = text(NAME, BOLD, S, x, base, TRACK)
    return f'<path id="{idn}" d="{d}" fill="{color}"/>', w


def horizontal(bg, dcol, well, namecol, title, pad=90):
    s, S, gap = 200, 150, 56
    m, mw = mark(0, 0, s, d=dcol, well=well)
    xh = S * 1118 / 2048
    n, wn = name_path(mw + gap, s / 2 + xh / 2, S, namecol)
    W, H = mw + gap + wn + 2 * pad, s + 2 * pad
    bgr = f'<rect id="background" width="{W:.0f}" height="{H:.0f}" fill="{bg}"/>' if bg else ''
    return svg(W, H, f'{bgr}<g id="logo" transform="translate({pad},{pad})">{m}{n}</g>', title)


def stacked(bg, dcol, well, namecol, title, pad=90):
    s, S = 260, 120
    wn = width(NAME, BOLD, S, TRACK)
    W = max(wn, s) + 2 * pad
    m, mw = mark(W / 2 - 0.96 * s / 2 + 6, pad, s, d=dcol, well=well)
    n, _ = name_path(W / 2 - wn / 2, pad + s + 70 + S * 0.73, S, namecol)
    H = pad + s + 70 + S * 0.73 + S * 0.25 + pad
    bgr = f'<rect id="background" width="{W:.0f}" height="{H:.0f}" fill="{bg}"/>' if bg else ''
    return svg(W, H, f'{bgr}{m}{n}', title)


def follow_pill(cx, cy):
    s, label = 46, 'İzlə'
    w = width(label, BOLD, s)
    pw, ph = w + 150, 104
    x, y = cx - pw / 2, cy - ph / 2
    d, _ = text(label, BOLD, s, x + 100, cy + s * 0.36)
    return (f'<g id="follow-button">'
            f'<rect x="{x:.1f}" y="{y+8:.1f}" width="{pw:.1f}" height="{ph}" rx="30" fill="#000" opacity=".25"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{pw:.1f}" height="{ph}" rx="30" fill="{CORAL}"/>'
            f'<path d="M{x+52:.1f} {cy:.1f}h32M{x+68:.1f} {cy-16:.1f}v32" stroke="{CREAM}" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="{d}" fill="{CREAM}"/></g>')


# End-card geometry (shared by static SVG and animation)
EC_S, EC_Y = 300, 600
EC_X = 540 - 0.96 * EC_S / 2 + 8
EC_NAME_S, EC_NAME_BASE = 120, 1060
EC_PILL_Y = 1330
BG_DEFS = (f'<defs><radialGradient id="bg-glow" cx=".5" cy=".42" r=".75">'
           f'<stop offset="0" stop-color="{NAVY2}"/><stop offset="1" stop-color="{NAVY}"/></radialGradient></defs>'
           f'<rect id="background" width="1080" height="1920" fill="url(#bg-glow)"/>')


def endcard_static():
    m, _ = mark(EC_X, EC_Y, EC_S, well=NAVY2)
    wn = width(NAME, BOLD, EC_NAME_S, TRACK)
    n, _ = name_path(540 - wn / 2, EC_NAME_BASE, EC_NAME_S, CREAM)
    return svg(1080, 1920, BG_DEFS + m + n + follow_pill(540, EC_PILL_Y), 'Düymə olsa — end-card')


def endcard_anim_html():
    """Same end-card, split into animatable parts; window.setT(t) poses a frame."""
    u = EC_S / 100
    bx, by = EC_X + 46 * u, EC_Y + 50 * u
    m, _ = mark(EC_X, EC_Y, EC_S, well=NAVY2, btn_off=UP)
    letters, x = [], 540 - width(NAME, BOLD, EC_NAME_S, TRACK) / 2
    for ch in NAME:
        d, adv = text(ch, BOLD, EC_NAME_S, x, EC_NAME_BASE)
        if ch != ' ':
            letters.append(f'<path class="ltr" d="{d}" fill="{CREAM}" style="transform-box:fill-box;transform-origin:50% 100%"/>')
        x += adv + TRACK * EC_NAME_S
    body = (BG_DEFS
            + f'<circle id="ripple" cx="{bx:.1f}" cy="{by+DOWN*u:.1f}" r="10" fill="none" stroke="{CORAL}" stroke-width="10" opacity="0"/>'
            + f'<g id="markwrap" style="transform-origin:{bx:.1f}px {EC_Y+100*u:.1f}px">{m}</g>'
            + ''.join(letters)
            + f'<g id="pillwrap" style="transform-origin:540px {EC_PILL_Y}px">{follow_pill(540, EC_PILL_Y)}</g>')
    js = f"""
const U={u:.4f}, UP={UP}, REST={REST}, DOWN={DOWN};
const cl=(v,a=0,b=1)=>Math.min(b,Math.max(a,v)), seg=(t,a,b)=>cl((t-a)/(b-a));
const eo=x=>1-Math.pow(1-x,3), eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const back=x=>{{const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);}};
window.setT=function(t){{
  // 1) mark pops in
  const a=seg(t,0,.42), sc=.55+.45*back(a);
  // 2) press: hover-up -> fully down (0.58-0.66) -> settle to rest (0.70-0.95)
  let off=UP, sq=1;
  if(t>=.58&&t<.66){{const p=eio(seg(t,.58,.66));off=UP+(DOWN-UP)*p;sq=1-.035*p;}}
  else if(t>=.66&&t<.70){{off=DOWN;sq=.965;}}
  else if(t>=.70){{const p=eo(seg(t,.70,.95));off=DOWN+(REST-DOWN)*p;sq=.965+.035*p;}}
  const mw=document.getElementById('markwrap');
  mw.style.transform=`scale(${{sc}},${{sc*sq}})`; mw.style.opacity=cl(a*2.5);
  document.getElementById('button').setAttribute('transform',`translate(0 ${{off*U}})`);
  // 3) ripple from the button
  const r=seg(t,.64,1.25), rp=document.getElementById('ripple');
  rp.setAttribute('r',18*U+eo(r)*62*U); rp.setAttribute('opacity',t<.64?0:(1-r)*.9);
  rp.setAttribute('stroke-width',(1-r)*10+1);
  // 4) name, letter by letter
  document.querySelectorAll('.ltr').forEach((l,i)=>{{
    const p=eo(seg(t,.80+i*.045,1.10+i*.045));
    l.style.opacity=p; l.style.transform=`translateY(${{(1-p)*34}}px)`;}});
  // 5) follow pill
  const q=seg(t,1.55,1.95), pw=document.getElementById('pillwrap');
  pw.style.opacity=cl(q*3); pw.style.transform=`scale(${{q?.6+.4*back(q):.6}})`;
}};
window.setT(0);
"""
    return ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#0B2545}</style></head><body>'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">{body}</svg>'
            f'<script>{js}</script></body></html>')


def click_wav(path, dur=3.6, sr=48000):
    """Soft, low-passed press click + release tick + pill pop (no harsh highs)."""
    n = int(dur * sr)
    out = np.zeros(n)
    rng = np.random.default_rng(7)

    def lp(x, a):
        y = np.zeros_like(x)
        for i in range(1, len(x)):
            y[i] = y[i - 1] + a * (x[i] - y[i - 1])
        return y

    def place(sig, t, g):
        i = int(t * sr)
        out[i:i + len(sig)] += g * sig[:n - i]

    tt = np.arange(int(.09 * sr)) / sr
    thump = np.sin(2 * np.pi * (150 - 500 * tt) * tt) * np.exp(-tt / .022)
    tick = lp(rng.standard_normal(len(tt)), .25) * np.exp(-tt / .004)
    place(thump + .6 * tick, .64, .55)                       # press bottoms out
    place(lp(rng.standard_normal(len(tt)), .2) * np.exp(-tt / .003), .72, .18)  # release
    tp = np.arange(int(.08 * sr)) / sr
    pop = np.sin(2 * np.pi * (520 + 2600 * tp) * tp) * np.exp(-tp / .018) * np.minimum(1, tp / .004)
    place(pop, 1.58, .16)                                    # İzlə pops in
    out = out / max(1e-9, np.abs(out).max()) * 10 ** (-6 / 20)
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    save('svg/icon.svg', svg(96 * 4, 400, mark(0, 0, 400)[0], 'Düymə olsa — icon'))
    save('svg/icon-on-light.svg', svg(96 * 4, 400, mark(0, 0, 400, d=NAVY, well=CREAM)[0], 'Düymə olsa — icon (light bg)'))
    save('svg/icon-mono-white.svg', svg(96 * 4, 400, mark_mono(0, 0, 400, '#FFFFFF')[0], 'Düymə olsa — icon mono white'))
    save('svg/icon-mono-navy.svg', svg(96 * 4, 400, mark_mono(0, 0, 400, NAVY)[0], 'Düymə olsa — icon mono navy'))
    save('svg/logo-horizontal.svg', horizontal(NAVY, CREAM, WELL, CREAM, 'Düymə olsa — horizontal'))
    save('svg/logo-horizontal-light.svg', horizontal(CREAM, NAVY, CREAM, NAVY, 'Düymə olsa — horizontal (light)'))
    save('svg/logo-horizontal-transparent.svg', horizontal(None, CREAM, NAVY, CREAM, 'Düymə olsa — horizontal (for dark footage)'))
    save('svg/logo-stacked.svg', stacked(NAVY, CREAM, WELL, CREAM, 'Düymə olsa — stacked'))
    save('svg/logo-stacked-light.svg', stacked(CREAM, NAVY, CREAM, NAVY, 'Düymə olsa — stacked (light)'))
    # Avatar: square, full-bleed — Instagram/TikTok crop the circle themselves.
    am, aw = mark(0, 0, 560, well=NAVY)
    save('svg/avatar.svg', svg(1080, 1080, f'<rect id="background" width="1080" height="1080" fill="{NAVY}"/>'
                               f'<g transform="translate({540 - aw/2 + 12:.1f},{540 - 280})">{am}</g>', 'Düymə olsa — avatar'))
    save('svg/endcard.svg', endcard_static())
    save('anim/endcard.html', endcard_anim_html())
    click_wav(os.path.join(HERE, 'anim', 'click.wav'))
    print('ok')
