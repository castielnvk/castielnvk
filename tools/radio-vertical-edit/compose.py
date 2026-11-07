# Main renderer: reads edit_list.py (EDL, captions, gags), renders video + mixes audio
import sys, os, json, math, subprocess, wave, importlib, time
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import edit_list as E

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'out.mp4')
PREVIEW = os.environ.get('PREVIEW')  # "t0,t1" output seconds -> only render that span
SR = 48000

# ---------------- timeline ----------------
clips = []
t = 0.0
for c in E.CLIPS:
    c = dict(c)
    if 'hold' in c:
        c['dur'] = c['hold']
    else:
        c['dur'] = c['b']-c['a']
    c['o0'] = t; t += c['dur']; c['o1'] = t
    clips.append(c)
TOTAL = t
HOLDS = [c for c in clips if 'hold' in c]
for c in HOLDS:
    for g in c.get('fx', []):
        g = dict(g); g['t0'] = c['o0']+g['t0']; g['t1'] = c['o0']+g['t1']; g['fixed'] = True
        E.GAG_EXTRA.append(g)
NF = int(round(TOTAL*FPS))
print('total', round(TOTAL, 2), 's', NF, 'frames')

def o2s(ot):
    for i, c in enumerate(clips):
        if c['o0'] <= ot < c['o1']:
            if 'hold' in c: return i, c['at']
            return i, c['a']+(ot-c['o0'])
    c = clips[-1]; return len(clips)-1, c.get('b', c.get('at'))

def s2o(st, ci=None):
    """source time -> output time (first clip containing it, or a given clip index)"""
    rng = [ci] if ci is not None else range(len(clips))
    for i in rng:
        c = clips[i]
        if 'hold' in c: continue
        if c['a']-1e-6 <= st <= c['b']+1e-6: return c['o0']+(st-c['a'])
    return None

# ---------------- layouts ----------------
M = 30
def layout(name):
    """return dict of view rects: k -> (x,y,w,h, zoom, headroom)"""
    if name == 'stack':
        return {'L': (M, 250, W-2*M, 690, 1.0, .44), 'R': (M, 965, W-2*M, 690, 1.0, .44)}
    if name == 'call':
        return {'L': (M, 250, 495, 600, 1.0, .42), 'R': (W-M-495, 250, 495, 600, 1.0, .42)}
    if name in ('soloL', 'soloR'):
        k = name[-1]; o = 'R' if k == 'L' else 'L'
        d = {k: (M, 250, W-2*M, 1170, 1.0, .40)}
        # the other presenter parks as a small picture-in-picture bubble
        d[o] = (W-M-270, 1440, 270, 270, 1.55, .48) if k == 'L' else (W-M-270, 1440, 270, 270, 1.55, .48)
        return d
    if name in ('punchL', 'punchR'):
        k = name[-1]; o = 'R' if k == 'L' else 'L'
        d = {k: (M, 250, W-2*M, 1170, 1.45, .45)}
        d[o] = (W-M-270, 1440, 270, 270, 1.55, .48)
        return d
    if name in ('fullL', 'fullR'):
        k = name[-1]
        return {k: (M, 250, W-2*M, 1170, 1.0, .40)}
    raise ValueError(name)

def lerp(a, b, f): return tuple(x*(1-f)+y*f for x, y in zip(a, b))

def views_at(ot):
    i, st = o2s(ot)
    c = clips[i]
    cur = layout(c['lay'])
    for k, v in c.get('override', {}).items(): cur[k] = v
    # animated transition from previous layout
    if i > 0 and c.get('trans', 'slide') == 'slide' and clips[i-1]['lay'] != c['lay']:
        f = (ot-c['o0'])/0.32
        if f < 1:
            prev = layout(clips[i-1]['lay'])
            f = ease(f); out = {}
            for k in set(cur) | set(prev):
                if k in cur and k in prev: out[k] = lerp(prev[k], cur[k], f)
                elif k in cur:  # grow in
                    x, y, w, h, z, hr = cur[k]; s = max(0.01, f)
                    out[k] = (x+w*(1-s)/2, y+h*(1-s)/2, w*s, h*s, z, hr)
                else:
                    x, y, w, h, z, hr = prev[k]; s = max(0.0, 1-f)
                    if s > 0.05: out[k] = (x+w*(1-s)/2, y+h*(1-s)/2, w*s, h*s, z, hr)
            return out, i, st
    return cur, i, st

# ---------------- captions ----------------
TR = json.load(open(os.path.join(WDIR, 'tr2.json')))
WORDS = [(w[0], w[1], w[2].strip()) for s in TR for w in s['w']]

def norm(s):
    return ''.join(ch for ch in s.lower() if ch.isalnum())

TR3 = [(w[0], w[1], w[2].strip()) for s in json.load(open(os.path.join(WDIR, 'tr3.json'))) if not s['p'] for w in s['w']]
def word_times(text, s0, s1):
    ws = text.split()
    cand = [w for w in TR3 if w[0] >= s0-0.25 and w[0] < s1]
    if len(cand) != len(ws): cand = [w for w in WORDS if w[0] >= s0-0.25 and w[0] < s1]
    if len(cand) == len(ws):
        st = [max(s0, c[0]) for c in cand]
    else:
        L = np.cumsum([0]+[len(w)+1 for w in ws]); st = list(s0+(s1-s0)*L[:-1]/L[-1])
    return list(zip(ws, st))

CAPS = []
for cap in E.CAPTIONS:
    spk, s0, s1, text = cap[:4]
    opts = cap[4] if len(cap) > 4 else {}
    wt = word_times(text, s0, s1)
    o0 = s2o(s0, opts.get('clip')); o1 = s2o(s1, opts.get('clip'))
    if o0 is None or o1 is None:
        print('caption outside edit:', text); continue
    words = [(w, s2o(t_, opts.get('clip')) or o0) for w, t_ in wt]
    big = opts.get('big', False)
    whole = big or spk == 'P'
    chunks = [words] if whole else []
    if not whole:
        cur = []
        for w in words:
            if cur and (len(cur) >= 4 or sum(len(x[0])+1 for x in cur)+len(w[0]) > 24):
                chunks.append(cur); cur = []
            cur.append(w)
            if w[0][-1] in ',.?!' and len(cur) >= 2: chunks.append(cur); cur = []
        if cur:
            if len(cur) == 1 and chunks and len(chunks[-1]) < 4: chunks[-1] = chunks[-1]+cur
            else: chunks.append(cur)
    for j, ch in enumerate(chunks):
        c_o1 = (chunks[j+1][0][1]-0.02) if j+1 < len(chunks) else o1
        c_o0 = ch[0][1] if j else o0
        CAPS.append(dict(spk=spk, o0=c_o0, o1=c_o1, words=ch, hi=set(opts.get('hi', [])), big=big, pos=opts.get('pos'), last=(j+1 == len(chunks))))

_srt = sorted(CAPS, key=lambda c: c['o0'])
for j, c in enumerate(_srt):
    nxt = _srt[j+1]['o0'] if j+1 < len(_srt) else 1e9
    c['vis_end'] = min(c['o1']+0.25, nxt-0.01)

@functools.lru_cache(4096)
def word_img(w, size, col, stroke):
    return text_img(w, size, fill=col, stroke=stroke, stroke_fill=(10, 4, 24), path=FONT_CAP, shadow_px=6)

def layout_caption(cap, maxw=960):
    size = 74 if not cap['big'] else 92
    sp = int(size*0.26) - 38
    imgs = []
    for w, _ in cap['words']:
        hi = norm(w) in {norm(x) for x in cap['hi']}
        imgs.append(word_img(w.upper() if cap['big'] else w, size, YEL if hi else WHITE, 9))
    lines = [[]]; lw = 0
    for j, im in enumerate(imgs):
        if lines[-1] and lw+im.size[0]+sp > maxw:
            lines.append([]); lw = 0
        lines[-1].append(j); lw += im.size[0]+sp
    return imgs, lines, sp

def caption_y(ot):
    _, i, _ = views_at(ot)
    lay = clips[i]['lay']
    if lay == 'stack': return 952
    if lay == 'call': return 770
    return 1330

def draw_captions(dst, ot):
    for cap in CAPS:
        if not (cap['o0']-0.02 <= ot <= cap['vis_end']): continue
        cy = cap['pos'] or caption_y(ot)
        if cap['spk'] == 'P' and clips[o2s(ot)[0]]['lay'] == 'call': continue
        if cy is None: cy = 1330
        imgs, lines, sp = layout_caption(cap)
        lh = imgs[0].size[1]-14
        tot_h = lh*len(lines)
        y = cy-tot_h/2
        fade = 1.0 if ot <= cap['o1'] else (max(0, 1-(ot-cap['o1'])/0.25) if cap.get('last', True) else 0)
        for line in lines:
            wsum = sum(imgs[j].size[0] for j in line)+sp*(len(line)-1)
            x = W/2-wsum/2
            for j in line:
                wt = cap['words'][j][1]
                if ot >= wt-0.03:
                    a = (ot-wt+0.03)/0.12
                    s = 0.75+0.25*ease_out_back(a) if a < 1 else 1.0
                    im = imgs[j]
                    if s != 1.0:
                        im = scale_rgba(im, s)
                    hi = norm(cap['words'][j][0]) in {norm(h) for h in cap['hi']}
                    if hi and a < 2.5:
                        bump = 1+0.12*math.sin(min(1, a/2.5)*math.pi)
                        im = scale_rgba(imgs[j], s*bump)
                    paste_center(dst, im, x+imgs[j].size[0]/2, y+lh/2, fade)
                x += imgs[j].size[0]+sp
            y += lh
        # speaker colour tick
        col = SPK_COL[cap['spk']]
        bar_w = 70
        if fade > 0:
            dst[int(cy-tot_h/2-24):int(cy-tot_h/2-16), int(W/2-bar_w/2):int(W/2+bar_w/2)] = \
                dst[int(cy-tot_h/2-24):int(cy-tot_h/2-16), int(W/2-bar_w/2):int(W/2+bar_w/2)]*(1-fade)+np.array(col, np.float32)*fade

# ---------------- call card ----------------
def draw_call_card(dst, ot, alpha):
    if alpha <= 0: return
    x, y, w, h = M, 880, W-2*M, 530
    s_ = 0.85+0.15*ease_out_back(alpha)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w-1, h-1], 44, fill=(255, 255, 255, 252))
    d.rounded_rectangle([0, 0, w-1, 150], 44, fill=MAG+(255,))
    d.rectangle([0, 110, w-1, 150], fill=MAG+(255,))
    # avatar disc with headset (no invented face)
    d.ellipse([28, 18, 142, 132], fill=(255, 255, 255, 255))
    av = emoji('1f3a7', 84, 0); im.paste(av, (43, 33), av)
    d.text((168, 20), 'NİHAT', font=font(FONT_CAP, 62), fill=WHITE)
    d.text((170, 92), 'DİNLƏYİCİ · TELEFON XƏTTİ', font=font(FONT_CAP8, 28), fill=(255, 225, 240))
    # pulsing live dot
    pa = 0.5+0.5*math.sin(ot*6)
    d.ellipse([w-170, 50, w-142, 78], fill=(255, int(60+80*pa), int(60+80*pa), 255))
    d.text((w-130, 44), 'CANLI', font=font(FONT_CAP, 32), fill=WHITE)
    ph = emoji('1f4de', 70, 0).rotate(math.sin(ot*14)*10 if caller_level(ot) > 0.25 else 0, Image.BICUBIC)
    im.paste(ph, (w-250, 40), ph)
    # waveform
    lv = caller_level(ot) if E.speaker_at(o2s(ot)[1]) == 'P' else 0.05
    nb = 46; bw = (w-80)/nb
    for b in range(nb):
        k = abs(math.sin(b*0.9+ot*11))*0.6+abs(math.sin(b*0.37-ot*7))*0.4
        hh = 6+min(1, lv*1.3)*70*k*(1-abs(b-nb/2)/nb)
        cx = 40+b*bw
        d.rounded_rectangle([cx, 210-hh/2, cx+bw*0.55, 210+hh/2], 4, fill=PURP+(255,))
    # caller caption (karaoke reveal), large
    cap = None
    for c in CAPS:
        if c['spk'] == 'P' and c['o0']-0.02 <= ot <= c['vis_end']+0.3: cap = c
    if cap:
        f2 = font(FONT_CAP, 54)
        lines = [[]]; xx = 0
        for wd, wt in cap['words']:
            bw2 = f2.getbbox(wd+' ')[2]
            if xx+bw2 > w-80 and lines[-1]: lines.append([]); xx = 0
            lines[-1].append((wd, wt, bw2)); xx += bw2
        yy = 268 if len(lines) > 2 else 300
        for ln in lines[:3]:
            tw = sum(b for _, _, b in ln); xx = (w-tw)/2
            for wd, wt, bw2 in ln:
                if ot >= wt-0.03:
                    hi = norm(wd) in {norm(hh) for hh in cap['hi']}
                    d.text((xx, yy), wd, font=f2, fill=MAG if hi else INK)
                xx += bw2
            yy += 70
    sh, sp = shadow(w, h, 44)
    blend(dst, np.zeros((sh.shape[0], sh.shape[1], 3), np.float32), sh*min(1, alpha*2), x-sp, y-sp)
    im = scale_rgba(im, s_)
    paste_center(dst, im, x+w/2, y+h/2, min(1, alpha*2))

# mini "on the line" chip shown outside the call layout
@functools.lru_cache(None)
def chip_base():
    im = Image.new('RGBA', (360, 74), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 359, 73], 37, fill=(255, 255, 255, 240))
    e = emoji('1f4de', 46, 0); im.paste(e, (16, 14), e)
    d.text((72, 18), 'NİHAT XƏTDƏ', font=font(FONT_CAP, 30), fill=MAG)
    return im
def draw_chip(dst, ot, lay):
    if lay == 'call': return
    im = chip_base().copy(); d = ImageDraw.Draw(im)
    lv = caller_level(ot) if E.speaker_at(o2s(ot)[1]) == 'P' else 0.0
    for b in range(5):
        hh = 6+min(1, lv*1.4)*40*abs(math.sin(b*1.3+ot*12))
        d.rounded_rectangle([300+b*10, 37-hh/2, 306+b*10, 37+hh/2], 3, fill=PURP+(255,))
    paste_center(dst, im, W/2, 136, 1.0)

# logos
@functools.lru_cache(None)
def logo_png(name, height, glow):
    """transparent logo, smooth LANCZOS scaling, soft drop shadow (+ optional faint light glow for dark-on-dark)"""
    lg = Image.open(os.path.join(ASSETS, f'logo_{name}.png')).convert('RGBA')
    # supersample: up 4x, then down for smooth edges
    s = height/lg.size[1]
    big = lg.resize((round(lg.size[0]*s*4), height*4), Image.LANCZOS)
    lg = big.resize((round(lg.size[0]*s), height), Image.LANCZOS)
    m = 56
    im = Image.new('RGBA', (lg.size[0]+2*m, lg.size[1]+2*m), (0, 0, 0, 0))
    a = lg.split()[3]
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); blk = Image.new('RGBA', lg.size, (0, 0, 0, 170)); blk.putalpha(a.point(lambda v: v*170//255))
    sh.paste(blk, (m+3, m+6), blk); sh = sh.filter(ImageFilter.GaussianBlur(7))
    im = Image.alpha_composite(im, sh)
    if glow:
        # soft light halo: wide, blurred, keeps logo colours intact
        gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
        mask = Image.new('L', im.size, 0); mask.paste(a, (m, m))
        halo = mask.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(14))
        halo = halo.point(lambda v: min(255, v*glow//110))
        wt = Image.new('RGBA', im.size, (245, 248, 250, 255)); wt.putalpha(halo)
        im = Image.alpha_composite(im, wt)
    im.alpha_composite(lg, (m, m))
    return np.asarray(im), m
def draw_logos(dst):
    a, m = logo_png('araz_white', 108, 0)
    rgba_blend(dst, a, 46-m, 136-a.shape[0]/2)
    b, m = logo_png('show', 150, 0)
    rgba_blend(dst, b, W-46+m-b.shape[1], 136-b.shape[0]/2)


# caller loudness envelope (for waveform)
_aw = wave.open(os.path.join(WDIR, 'a.wav'))
SRC_SR = _aw.getframerate()
SRC_AUD = np.frombuffer(_aw.readframes(_aw.getnframes()), np.int16).reshape(-1, 2).astype(np.float32)/32768
_env = None
def caller_level(ot):
    global _env
    if _env is None: _env = np.sqrt(np.maximum(boxsmooth(SRC_AUD.mean(1)**2, 2048), 0))
    _, st = o2s(ot)
    i = int(st*SRC_SR)
    if i >= len(_env): return 0
    return float(min(1, _env[i]*6))

# ---------------- gags / stickers ----------------
def anim_scale(ot, t0, t1, pop=0.22, out=0.18):
    if ot < t0 or ot > t1: return 0
    if ot < t0+pop: return ease_out_back((ot-t0)/pop)
    if ot > t1-out: return max(0, 1-ease((ot-(t1-out))/out))
    return 1

@functools.lru_cache(None)
def insert_img(path, size):
    im = Image.open(path).convert('RGB').resize((size, size), Image.LANCZOS)
    return im
def draw_insert(dst, g, ot, s):
    size = g.get('size', 860)
    prog = (ot-g['t0'])/max(0.1, g['t1']-g['t0'])
    z = 1.0+0.07*prog
    base = insert_img(g['path'], size)
    crop = base.resize((int(size*z), int(size*z)), Image.BICUBIC)
    o = (crop.size[0]-size)//2
    crop = crop.crop((o, o, o+size, o+size))
    b = 18; fr = Image.new('RGBA', (size+2*b, size+2*b+70), (255, 255, 255, 255))
    fr.paste(crop, (b, b))
    d = ImageDraw.Draw(fr)
    f = font(FONT_CAP, 40); t = g.get('cap', '')
    tw = f.getbbox(t)[2]; d.text(((fr.size[0]-tw)/2, size+b+12), t, font=f, fill=INK)
    m = Image.new('L', fr.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, fr.size[0]-1, fr.size[1]-1], 28, fill=255)
    fr.putalpha(m)
    sh = Image.new('RGBA', (fr.size[0]+80, fr.size[1]+80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 52, 40+fr.size[0], 52+fr.size[1]], 28, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(16)); sh.alpha_composite(fr, (40, 40))
    rot = g.get('rot', -3)+math.sin((ot-g['t0'])*3)*1.2
    im = scale_rgba(sh, s*0.98, rot)
    x, y = g['xy']
    paste_center(dst, im, x, y)
    tag = label_sticker('AI TƏSƏVVÜRÜ', 30, YEL, INK, emoji_code='1f3a8', rot=0)
    paste_center(dst, scale_rgba(tag, s, 6), x-size/2+150, y-size/2-10)

_GAGS = None
def draw_gags(dst, ot):
    global _GAGS
    if _GAGS is None: _GAGS = E.GAGS(s2o)
    for g in _GAGS:
        t0, t1 = g['t0'], g['t1']
        if t0 is None or not (t0 <= ot <= t1): continue
        s = anim_scale(ot, t0, t1)
        if s <= 0.01: continue
        x, y = g['xy']
        if g['kind'] == 'emoji' and not g.get('fixed'):
            lay = clips[o2s(t0+0.01)[0]]['lay']
            if lay == 'stack' and y > 960 and x > 540: x = 170
            if lay != 'stack' and lay != 'call' and 1100 < y < 1480: y = 1010
        rot = g.get('rot', 0)+math.sin((ot-t0)*g.get('wob_f', 5))*g.get('wob', 4)
        if g.get('fly'):
            fx, fy = g['fly']; fr = min(1, (ot-t0)/g.get('fly_t', 0.6))
            x += fx*ease_out(fr); y += fy*ease_out(fr)
        if g.get('float'): y -= (ot-t0)*g['float']
        if g['kind'] == 'emoji':
            im = emoji(g['code'], g.get('size', 220))
        elif g['kind'] == 'label':
            im = label_sticker(g['text'], g.get('size', 46), g.get('bg', YEL), g.get('fg', INK), emoji_code=g.get('emoji'), rot=0)
        elif g['kind'] == 'image':
            draw_insert(dst, g, ot, s); continue
        elif g['kind'] == 'title':
            im = label_sticker(g['text'], g.get('size', 64), g.get('bg', MAG), g.get('fg', WHITE), emoji_code=g.get('emoji'), rot=0)
        im = scale_rgba(im, s*g.get('scale', 1.0), rot)
        paste_center(dst, im, x, y, g.get('op', 1.0))

# ---------------- header & laugh counter ----------------
@functools.lru_cache(None)
def header_img(txt):
    return label_sticker(txt, 42, INK, WHITE, path=FONT_DISP, pad=(24, 14), rot=0, outline=False, emoji_code='1f3e5')

def draw_header(dst, ot):
    im = header_img(E.HEADER)
    a = min(1, ot/0.4)
    paste_center(dst, scale_rgba(im, 0.9+0.1*ease_out_back(a)), W/2, 108, a)

def draw_counter(dst, ot):
    hits = [s2o(t, ci) for t, ci in E.LAUGHS]
    hits = sorted(h for h in hits if h is not None)
    if not hits or ot < E.COUNTER_START(s2o): return
    n = sum(1 for h in hits if h <= ot)
    a = min(1, (ot-E.COUNTER_START(s2o))/0.3)
    last = max([h for h in hits if h <= ot], default=-9)
    bump = 1+0.35*max(0, 1-(ot-last)/0.35)
    im = counter_img(n)
    x = M+10+im.size[0]/2; y = 1730
    paste_center(dst, scale_rgba(im, ease_out_back(a)*bump, math.sin(ot*3)*2), x, y)

@functools.lru_cache(None)
def counter_img(n):
    return label_sticker(f'GÜLMƏK QADAĞAN\nPOZUNTU: {n}', 26, (255, 255, 255), (200, 20, 60), path=FONT_DISP, pad=(18, 12), rot=0, emoji_code='1f6ab')

# ---------------- frame ----------------
FLASH_T = E.FLASHES(s2o) + [c['o0'] for c in HOLDS if c.get('flash', True)]
SHAKE_T = E.SHAKES(s2o)
def flash(dst, ot):
    for t0 in FLASH_T:
        if t0 is not None and 0 <= ot-t0 < 0.18:
            a = 1-(ot-t0)/0.18
            dst *= (1-0.55*a); dst += 255*0.55*a

def render_frame(fi, panels):
    ot = fi/FPS
    dst = bg_frame(fi)
    vs, ci, st = views_at(ot)
    c = clips[ci]
    spk = E.speaker_at(st)
    shake = (0, 0)
    for t0, amp in SHAKE_T:
        if t0 is not None and 0 <= ot-t0 < 0.4:
            k = 1-(ot-t0)/0.4
            shake = (math.sin(ot*90)*amp*k, math.cos(ot*77)*amp*k)
    # punch zoom pulse at clip start
    for k in ['L', 'R']:
        if k not in vs: continue
        x, y, w, h, z, hr = vs[k]
        small = w < 400
        if 'hold' in c and c.get('hold_zoom'):
            z *= 1+0.15*ease_out((ot-c['o0'])/c['hold'])
        if c['lay'].startswith('punch') and not small:
            z *= 1+0.05*ease_out_back(min(1, (ot-c['o0'])/0.3))
        active = (spk == k)
        col = SPK_COL[k] if active else (255, 255, 255)
        border = (col, 7, 22) if active else ((255, 255, 255), 3, 0)
        if small: border = (SPK_COL[k], 6, 0)
        bright = 1.0 if (active or spk not in ('L', 'R') or small) else 0.93
        render_view(dst, panels[k], k, st, (x, y, w, h), zoom=z, headroom=hr, bright=bright, border=border,
                    radius=150 if small else 40, shake=shake if not small else (0, 0))
    # call card
    ca = 0
    if c['lay'] == 'call':
        ca = min(1, (ot-c['o0'])/0.3) if (ci == 0 or clips[ci-1]['lay'] != 'call') else 1
    if 'hold' in c and c.get('dim'):
        dst *= 0.55
    draw_call_card(dst, ot, ca)
    draw_logos(dst)
    draw_chip(dst, ot, c['lay'])
    draw_counter(dst, ot)
    draw_captions(dst, ot)
    draw_gags(dst, ot)
    if 'hold' in c:  # freeze-frame treatment: slight vignette + label handled by gags
        pass
    flash(dst, ot)
    return np.clip(dst, 0, 255).astype(np.uint8)

# ---------------- audio ----------------
def boxsmooth(x, k):
    k = max(1, int(k)); c = np.cumsum(np.concatenate([[0.0], x.astype(np.float64)]))
    y = (c[k:]-c[:-k])/k
    pad_l = (len(x)-len(y))//2
    return np.pad(y, (pad_l, len(x)-len(y)-pad_l), mode='edge').astype(np.float32)
def load_wav(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(np.float32)/32768
    if a.shape[1] == 1: a = np.repeat(a, 2, 1)
    if w.getframerate() != SR:
        n = int(len(a)*SR/w.getframerate()); xi = np.linspace(0, len(a)-1, n)
        a = np.stack([np.interp(xi, np.arange(len(a)), a[:, c]) for c in range(2)], 1).astype(np.float32)
    return a

def build_audio():
    src = load_wav(os.path.join(WDIR, 'a.wav'))
    n = int(TOTAL*SR)+SR
    dia = np.zeros((n, 2), np.float32)
    gain_env = np.ones(n, np.float32)
    for c in clips:
        o = int(c['o0']*SR)
        if 'hold' in c: continue
        a0 = int(c['a']*SR); a1 = int(c['b']*SR)
        seg = src[a0:a1].copy()
        # per-speaker balancing gain over the segment
        g = np.ones(len(seg), np.float32)
        for (s0, s1, k) in E.SPEAKERS:
            i0 = max(0, int((s0-c['a'])*SR)); i1 = min(len(seg), int((s1-c['a'])*SR))
            if i1 > i0: g[i0:i1] = E.SPK_GAIN.get(k, 1.0)
        g = boxsmooth(g, 2400) if len(g) > 2400 else g
        seg *= g[:, None]*c.get('gain', 1.0)
        fl = min(int(0.012*SR), len(seg)//2)
        seg[:fl] *= np.linspace(0, 1, fl)[:, None]; seg[-fl:] *= np.linspace(1, 0, fl)[:, None]
        dia[o:o+len(seg)] += seg[:n-o]
    # mono-ize dialogue (source is near-mono) for a centred voice
    dia[:] = dia.mean(1, keepdims=True)
    # music bed with ducking + stops
    mus = load_wav(os.path.join(BASE, 'music.wav'))
    mus = np.tile(mus, (int(np.ceil(n/len(mus)))+1, 1))[:n]
    menv = np.full(n, E.MUSIC_LEVEL, np.float32)
    for (t0, t1, lev) in E.MUSIC_AUTOMATION(s2o) + [(c['o0'], c['o1'], c.get('music', 0.0)) for c in HOLDS]:
        if t0 is None or t1 is None: continue
        i0, i1 = int(t0*SR), int(t1*SR)
        menv[i0:i1] = lev
    menv = boxsmooth(menv, 0.08*SR)
    # side-chain-ish ducking from dialogue envelope
    de = np.sqrt(np.maximum(boxsmooth(dia[:, 0]**2, 4800), 0))
    duck = 1/(1+de*9)
    mix = dia+mus*(menv*duck)[:, None]
    # sfx
    sfx = np.zeros_like(mix)
    for name, t0, lev in E.SFX(s2o) + [(n, c['o0']+dt, lv) for c in HOLDS for (n, dt, lv) in c.get('sfx', [])]:
        if t0 is None: continue
        s = load_wav(os.path.join(BASE, f'sfx_{name}.wav'))*lev
        i = int(t0*SR); m = min(len(s), n-i)
        if m > 0: sfx[i:i+m] += s[:m]
    mix += sfx
    mix = mix[:int(TOTAL*SR)]
    # fade out tail
    fo = int(0.6*SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    w = wave.open(os.path.join(BASE, 'mix_raw.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1)*32767).astype(np.int16).tobytes()); w.close()

# ---------------- main ----------------
def main():
    build_audio()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(BASE, 'mix_raw.wav'), '-af',
                    'acompressor=threshold=-20dB:ratio=2.5:attack=8:release=200,loudnorm=I=-14:TP=-1.5:LRA=9',
                    '-ar', '48000', os.path.join(BASE, 'mix.wav')], check=True)
    f0, f1 = 0, NF
    if PREVIEW:
        a, b = map(float, PREVIEW.split(',')); f0, f1 = int(a*FPS), int(b*FPS)
    vid = os.path.join(BASE, 'video_only.mp4')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                            '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', vid], stdin=subprocess.PIPE)
    reader = None; cur_clip = None; tstart = time.time()
    held = None
    for fi in range(f0, f1):
        ot = fi/FPS
        ci, st = o2s(ot)
        c = clips[ci]
        if ci != cur_clip:
            if reader: reader.close()
            cur_clip = ci
            if 'hold' in c:
                r = Reader(c['at'], c['at']+0.1); held = r.next(); r.close(); reader = None
            else:
                start = c['a']+(ot-c['o0'])
                reader = Reader(start, c['b']); held = None
        panels = held if held is not None else reader.next()
        frame = render_frame(fi, panels)
        enc.stdin.write(frame.tobytes())
        if fi % 150 == 0: print(f'frame {fi}/{f1} {time.time()-tstart:.0f}s', flush=True)
    if reader: reader.close()
    enc.stdin.close(); enc.wait()
    a_args = ['-ss', f'{f0/FPS:.3f}', '-t', f'{(f1-f0)/FPS:.3f}']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid] + a_args + ['-i', os.path.join(BASE, 'mix.wav'),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-movflags', '+faststart', '-shortest', OUT], check=True)
    print('wrote', OUT)

if __name__ == '__main__':
    main()
