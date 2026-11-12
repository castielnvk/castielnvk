# Premium "glass" theme: frosted dark-glass captions, cards and tags, aurora background,
# smooth eased motion (no bounce/wobble/flash/shake). Overrides drawing functions of compose.py.
import sys, os, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.argv = [sys.argv[0]] + sys.argv[1:]
import compose as C
from engine import *
M = C.M

INTER_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INTER_XB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
GOLD = (255, 211, 110)
ACCENT = {'R': (125, 211, 252), 'L': (253, 224, 140), 'P': (244, 154, 210), 'X': (255, 255, 255)}

def eo(x):  # ease-out cubic
    x = min(1, max(0, x)); return 1-(1-x)**3
def eio(x):
    x = min(1, max(0, x)); return x*x*(3-2*x)

# ---------------- aurora background ----------------
_BGS = (270, 480)
def bg_frame(fi):
    t = fi/FPS
    w, h = _BGS
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    img = np.zeros((h, w, 3), np.float32)
    img[:] = (14, 10, 30)
    blobs = [((0.25+0.10*math.sin(t*0.13), 0.22+0.06*math.cos(t*0.11)), 0.55, (88, 40, 170)),
             ((0.80+0.08*math.cos(t*0.09), 0.55+0.08*math.sin(t*0.12)), 0.60, (30, 70, 150)),
             ((0.35+0.12*math.cos(t*0.07), 0.90+0.05*math.sin(t*0.1)), 0.55, (120, 40, 120))]
    for (cx, cy), r, col in blobs:
        d = ((x/w-cx)**2+((y/h-cy)*1.6)**2)/(r*r)
        a = np.exp(-d*2.2)[..., None]
        img += np.array(col, np.float32)*a*0.55
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_CUBIC)
    # fine film grain for richness (very subtle)
    return img
C.bg_frame = bg_frame

# ---------------- glass primitive ----------------
@functools.lru_cache(256)
def _rr(w, h, r):
    return rr_mask(w, h, r)

@functools.lru_cache(256)
def _glass_overlay(w, h, r, border_a, hi_a):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # top sheen
    sheen = Image.new('L', (w, h), 0)
    sd = ImageDraw.Draw(sheen)
    for i in range(int(h*0.5)):
        sd.line([(0, i), (w, i)], fill=int(255*hi_a*(1-i/(h*0.5))**2))
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], r, fill=255)
    sheen = Image.fromarray((np.asarray(sheen).astype(np.float32)*np.asarray(m)/255).astype(np.uint8))
    white = Image.new('RGBA', (w, h), (255, 255, 255, 0)); white.putalpha(sheen)
    im = Image.alpha_composite(im, white)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w-1, h-1], r, outline=(255, 255, 255, int(255*border_a)), width=2)
    return np.asarray(im)

def glass(dst, x, y, w, h, r=30, tint=(16, 12, 32), tint_a=0.55, blur=26, border_a=0.22, hi_a=0.10, op=1.0, shadow_a=0.35):
    x, y, w, h = int(x), int(y), int(w), int(h)
    if w < 8 or h < 8 or op <= 0.01: return
    pad = 40
    x0, y0, x1, y1 = max(0, x-pad), max(0, y-pad), min(W, x+w+pad), min(H, y+h+pad)
    reg = dst[y0:y1, x0:x1]
    small = cv2.resize(reg, (max(1, (x1-x0)//4), max(1, (y1-y0)//4)), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), blur/4)
    bl = cv2.resize(small, (x1-x0, y1-y0), interpolation=cv2.INTER_LINEAR)
    # soft drop shadow
    if shadow_a > 0:
        sh, sp = shadow(w, h, r, 22, int(255*shadow_a))
        blend(dst, np.zeros((sh.shape[0], sh.shape[1], 3), np.float32), sh*op, x-sp, y-sp)
    gx0, gy0 = x-x0, y-y0
    gx0c, gy0c = max(0, gx0), max(0, gy0)
    gx1c, gy1c = min(x1-x0, gx0+w), min(y1-y0, gy0+h)
    if gx1c <= gx0c or gy1c <= gy0c: return
    frost = bl[gy0c:gy1c, gx0c:gx1c]*(1-tint_a)+np.array(tint, np.float32)*tint_a
    m = _rr(w, h, r)[gy0c-gy0:gy1c-gy0, gx0c-gx0:gx1c-gx0]*op
    d = dst[y0+gy0c:y0+gy1c, x0+gx0c:x0+gx1c]
    d *= (1-m[..., None]); d += frost*m[..., None]
    ov = _glass_overlay(w, h, r, border_a, hi_a)
    rgba_blend(dst, ov, x, y, op)

# ---------------- layouts: hide a presenter when needed ----------------
_orig_layout = C.layout
def layout(name):
    base, _, hide = name.partition('-no')
    d = _orig_layout(base)
    if hide:
        d.pop(hide, None)
        keep = 'R' if hide == 'L' else 'L'
        if base == 'call':
            d[keep] = (M, 250, W-2*M, 600, 1.15, .42)
        elif base == 'stack':
            d[keep] = (M, 250, W-2*M, 1170, 1.0, .40)
        else:  # solo/punch: drop the picture-in-picture bubble
            pass
    return d
C.layout = layout
for c in C.clips:
    if c.get('hide'):
        c['lay'] = c['lay']+'-no'+c['hide']

# ---------------- captions on dark glass ----------------
@functools.lru_cache(4096)
def word_rgba(w, size, col, big):
    f = font(FONT_CAP8 if not big else FONT_CAP, size)
    bb = f.getbbox(w)
    tw, th = bb[2]-bb[0]+16, bb[3]-bb[1]+22
    im = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    sh = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((8-bb[0], 8-bb[1]+2), w, font=f, fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(im).text((8-bb[0], 8-bb[1]), w, font=f, fill=col+(255,))
    return im

def caption_layout(cap):
    size = 60 if not cap['big'] else 76
    words = [w.upper() if cap['big'] else w for w, _ in cap['words']]
    imgs = [word_rgba(w, size, GOLD if C.norm(cap['words'][i][0]) in {C.norm(h) for h in cap['hi']} else WHITE, cap['big'])
            for i, w in enumerate(words)]
    sp = int(size*0.26)-16
    maxw = 900
    lines = [[]]; lw = 0
    for j, im in enumerate(imgs):
        if lines[-1] and lw+im.size[0]+sp > maxw: lines.append([]); lw = 0
        lines[-1].append(j); lw += im.size[0]+sp
    return imgs, lines, sp

def draw_captions(dst, ot):
    for cap in C.CAPS:
        if not (cap['o0']-0.02 <= ot <= cap['vis_end']): continue
        lay = C.clips[C.o2s(ot)[0]]['lay']
        if cap['spk'] == 'P' and lay.startswith('call'): continue
        cy = cap['pos'] or C.caption_y(ot) or 1330
        imgs, lines, sp = caption_layout(cap)
        lh = imgs[0].size[1]-10
        widths = [sum(imgs[j].size[0] for j in ln)+sp*(len(ln)-1) for ln in lines]
        bw = max(widths)+64; bh = lh*len(lines)+34
        a_in = eo((ot-cap['o0'])/0.25)
        a_out = 1.0 if ot <= cap['o1'] else max(0, 1-(ot-cap['o1'])/0.25)
        op = min(a_in, a_out) if cap.get('last', True) else a_in
        gy = cy-bh/2+(1-a_in)*14
        glass(dst, W/2-bw/2, gy, bw, bh, r=26, tint_a=0.58, op=op)
        # speaker accent: small coloured dot left of the pill
        acc = ACCENT.get(cap['spk'], WHITE)
        cv2.circle(dst, (int(W/2-bw/2+22), int(gy+bh/2)), 6, tuple(float(c*op+0) for c in acc), -1, cv2.LINE_AA) if op > 0.3 else None
        y = gy+17
        for ln, wsum in zip(lines, widths):
            x = W/2-wsum/2+8
            for j in ln:
                wt = cap['words'][j][1]
                if ot >= wt-0.03:
                    k = eo((ot-wt+0.03)/0.18)
                    paste_center(dst, imgs[j], x+imgs[j].size[0]/2, y+lh/2+(1-k)*8, k*op)
                x += imgs[j].size[0]+sp
            y += lh
C.draw_captions = draw_captions

# ---------------- glass tags (labels) and icon badges ----------------
@functools.lru_cache(256)
def tag_content(text, size, accent, emoji_code):
    lines = text.split('\n')
    f = font(INTER_XB, size)
    bbs = [f.getbbox(l) for l in lines]
    lw = max(b[2]-b[0] for b in bbs); lh = [b[3]-b[1] for b in bbs]; gap = int(size*0.35)
    em = int(size*1.15) if emoji_code else 0
    padx, pady = 30, 20
    w = lw+padx*2+(em+16 if em else 0); h = sum(lh)+gap*(len(lines)-1)+pady*2
    h = max(h, em+pady*2) if em else h
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = padx
    if em:
        e = emoji(emoji_code, em, 0); im.paste(e, (x, (h-em)//2), e); x += em+16
    y = pady
    for l, b, hh in zip(lines, bbs, lh):
        d.text((x-b[0], y-b[1]), l, font=f, fill=accent+(255,))
        y += hh+gap
    return im

def draw_gags(dst, ot):
    if C._GAGS is None: C._GAGS = C.E.GAGS(C.s2o)
    for g in C._GAGS:
        t0, t1 = g['t0'], g['t1']
        if t0 is None or not (t0 <= ot <= t1): continue
        a_in = eo((ot-t0)/0.35); a_out = 1 if ot < t1-0.25 else max(0, (t1-ot)/0.25)
        op = min(a_in, a_out)
        if op <= 0.02: continue
        x, y = g['xy']
        if g['kind'] == 'emoji':
            s = int(min(170, max(132, g.get('size', 170)*0.85)))
            im = emoji(g['code'], int(s*0.62), 0)
            gx, gy = x-s/2, y-s/2+(1-a_in)*18
            glass(dst, gx, gy, s, s, r=s//2, tint_a=0.45, op=op)
            paste_center(dst, im, x, gy+s/2, op)
            continue
        if g['kind'] in ('label', 'title'):
            acc = g.get('accent', WHITE)
            im = tag_content(g['text'], max(26, int(g.get('size', 44)*0.72)), acc, g.get('emoji'))
            w_, h_ = im.size
            gx, gy = x-w_/2, y-h_/2+(1-a_in)*20
            glass(dst, gx, gy, w_, h_, r=min(28, h_//2), tint_a=0.55, op=op)
            if g.get('bar'):
                bc = g['bar']; cv2.rectangle(dst, (int(gx+10), int(gy+14)), (int(gx+15), int(gy+h_-14)), tuple(float(c) for c in bc), -1)
            rgba_blend(dst, np.asarray(im), gx, gy, op)
C.draw_gags = draw_gags

# ---------------- glass call card ----------------
def draw_call_card(dst, ot, alpha):
    if alpha <= 0: return
    x, y, w, h = M, 880, W-2*M, 520
    a = eio(alpha)
    yy = y+(1-a)*30
    glass(dst, x, yy, w, h, r=40, tint_a=0.55, op=a, border_a=0.25)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # avatar ring
    d.ellipse([34, 30, 134, 130], outline=(255, 255, 255, 90), width=2)
    av = emoji('1f3a7', 62, 0); im.paste(av, (53, 49), av)
    name = C.E.caller_name(C.o2s(ot)[1])
    d.text((160, 34), name, font=font(INTER_XB, 50), fill=(255, 255, 255, 255))
    pa = 0.55+0.45*math.sin(ot*5)
    d.ellipse([162, 103, 176, 117], fill=(255, 80, 90, int(255*pa)))
    d.text((186, 96), 'DİNLƏYİCİ  ·  CANLI XƏTT', font=font(INTER_SB, 24), fill=(255, 255, 255, 170))
    # waveform
    sp = C.E.speaker_at(C.o2s(ot)[1]) == 'P'
    lv = C.caller_level(ot) if sp else 0.04
    nb = 56; bw = (w-80)/nb
    for b in range(nb):
        k = abs(math.sin(b*0.9+ot*11))*0.6+abs(math.sin(b*0.37-ot*7))*0.4
        env = 1-abs(b-nb/2)/(nb/2)
        hh = 4+min(1, lv*1.3)*58*k*env
        cx = 40+b*bw
        d.rounded_rectangle([cx, 190-hh/2, cx+bw*0.45, 190+hh/2], 3, fill=(255, 255, 255, int(110+120*env)))
    # caller caption
    cap = None
    for c in C.CAPS:
        if c['spk'] == 'P' and c['o0']-0.02 <= ot <= c['vis_end']+0.3: cap = c
    if cap:
        f2 = font(FONT_CAP8, 50)
        lines = [[]]; xx = 0
        for wd, wt in cap['words']:
            bw2 = f2.getbbox(wd+' ')[2]
            if xx+bw2 > w-90 and lines[-1]: lines.append([]); xx = 0
            lines[-1].append((wd, wt, bw2)); xx += bw2
        ty = 260 if len(lines) > 2 else 290
        for ln in lines[:3]:
            tw = sum(b for _, _, b in ln); tx = (w-tw)/2
            for wd, wt, bw2 in ln:
                if ot >= wt-0.03:
                    k = eo((ot-wt+0.03)/0.18)
                    hi = C.norm(wd) in {C.norm(q) for q in cap['hi']}
                    col = GOLD if hi else (255, 255, 255)
                    d.text((tx, ty+(1-k)*6), wd, font=f2, fill=col+(int(255*k),))
                tx += bw2
            ty += 68
    rgba_blend(dst, np.asarray(im), x, yy, a)
C.draw_call_card = draw_call_card

# ---------------- glass "on the line" chip ----------------
def draw_chip(dst, ot, lay):
    if lay.startswith('call'): return
    name = C.E.caller_name(C.o2s(ot)[1])
    f = font(INTER_B, 24); tw = f.getbbox(name+' XƏTDƏ')[2]
    w, h = 64+tw+86, 64
    x, y = W/2-w/2, 136-h/2
    glass(dst, x, y, w, h, r=32, tint_a=0.5)
    im = Image.new('RGBA', (int(w), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    e = emoji('1f4de', 34, 0); im.paste(e, (20, 15), e)
    d.text((64, 18), name+' XƏTDƏ', font=f, fill=(255, 255, 255, 235))
    lv = C.caller_level(ot) if C.E.speaker_at(C.o2s(ot)[1]) == 'P' else 0.0
    for b in range(5):
        hh = 5+min(1, lv*1.4)*30*abs(math.sin(b*1.3+ot*12))
        d.rounded_rectangle([w-66+b*10, 32-hh/2, w-61+b*10, 32+hh/2], 2, fill=(255, 255, 255, 200))
    rgba_blend(dst, np.asarray(im), x, y)
C.draw_chip = draw_chip

# ---------------- frame ----------------
def render_frame(fi, panels):
    ot = fi/FPS
    dst = bg_frame(fi)
    vs, ci, st = C.views_at(ot)
    c = C.clips[ci]
    spk = C.E.speaker_at(st)
    for k in ['L', 'R']:
        if k not in vs: continue
        x, y, w, h, z, hr = vs[k]
        small = w < 400
        if c['lay'].startswith('punch') and not small:
            z *= 1+0.04*eio(min(1, (ot-c['o0'])/0.6))     # slow push-in instead of a bounce
        active = (spk == k)
        border = ((255, 255, 255), 2, 16) if active else None
        render_view(dst, panels[k], k, st, (x, y, w, h), zoom=z, headroom=hr, bright=1.0 if (active or small or spk not in ('L', 'R')) else 0.94,
                    border=border, radius=150 if small else 44)
    ca = 0
    if c['lay'].startswith('call'):
        ca = min(1, (ot-c['o0'])/0.35) if (ci == 0 or not C.clips[ci-1]['lay'].startswith('call')) else 1
    C.draw_call_card(dst, ot, ca)
    C.draw_logos(dst)
    C.draw_chip(dst, ot, c['lay'])
    C.draw_captions(dst, ot)
    C.draw_gags(dst, ot)
    # gentle cross-fade at hard cuts
    if ci > 0 and c.get('trans', 'slide') == 'cut':
        k = (ot-c['o0'])/0.12
        if k < 1: dst *= (0.82+0.18*eio(k))
    return np.clip(dst, 0, 255).astype(np.uint8)
C.render_frame = render_frame
def caption_y(ot):
    lay = C.clips[C.o2s(ot)[0]]['lay']
    if lay == 'stack': return 952
    if lay.startswith('call'): return 770 if lay == 'call' else 810
    return 1330
C.caption_y = caption_y

if __name__ == '__main__':
    C.main()
