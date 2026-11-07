"""v2 renderer — paparazzi / celebrity-magazine cut.  usage: python3 render2.py [t0 t1 out.mp4] | --stills t,t,.. dir"""
import numpy as np, cv2, subprocess, sys, os, math, time
from PIL import Image, ImageDraw, ImageFilter
import render as R                       # shared helpers (text, blit, easing, reader, reframe, face track)
from render import W, H, F, text_rgba, blit, eo3, eio3, eoexp, prog, clamp, reframe, blurred, VIG, BOT, IVORY, GOLD, wrap, reveal_lines, draw_rule
from timeline2 import build, caption_events, live_quote_events, FPS

items, TOTAL = build()
CAPS = caption_events(items)
LQ = live_quote_events(items)
RD = R.Reader()
BERRY = (205, 38, 112); DGc = (8, 58, 45); DARK = (10, 12, 12)

# ---------- user's logo overlay: exact PNG, 1:1, plus soft shadow only ----------
ov = Image.open('assets/kesfet_araz_overlay.png').convert('RGBA')
al = ov.getchannel('A').filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.55))
sh = Image.new('RGBA', ov.size, (0, 0, 0, 0)); sh.putalpha(al)
sh2 = Image.new('RGBA', ov.size, (0, 0, 0, 0)); sh2.paste(sh, (0, 3)); sh2.alpha_composite(ov)
bb = sh2.getchannel('A').getbbox()
LOGO_Y0 = bb[1]; LOGO = np.asarray(sh2.crop((0, bb[1], W, bb[3]))).astype(np.float32) / 255
def draw_logos(fr, a):
    blit(fr, LOGO, 0, LOGO_Y0, a)

# ---------- fonts ----------
FCAP = F('Archivo-SemiBold.ttf', 56)
FTAG = F('ArchivoX-Bold.ttf', 28)
FQ = F('Playfair-500-italic.ttf', 68)
FFQ = F('Playfair-500-italic.ttf', 64)
FBIGNUM = F('ArchivoX-ExtraBold.ttf', 560)
def fit_font(lines, name, size, maxw):
    while size > 30:
        f = F(name, size)
        if max(f.getlength(l) for l in lines) <= maxw: return f
        size -= 2
    return F(name, size)

# ---------- generic pieces ----------
_c = {}
def box_text(txt, font, fg, bg, padx=22, pady=12, radius=6):
    key = (txt, font.path, font.size, fg, bg, padx, pady)
    if key in _c: return _c[key]
    asc, desc = font.getmetrics(); w = int(font.getlength(txt)) + 2 * padx; h = asc + desc + 2 * pady - int(desc * 0.6)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=bg + (255,))
    d.text((padx, pady - 2), txt, font=font, fill=fg + (255,))
    arr = np.asarray(im).astype(np.float32) / 255; _c[key] = arr; return arr

def flash(fr, k):
    """k = frames since flash peak (0..5)."""
    I = [0.92, 0.78, 0.55, 0.3, 0.14, 0.05]
    if 0 <= k < len(I): fr += (255 - fr) * I[k]

def shutter(fr, c):
    """c 0..1 coverage: black bars closing from top & bottom."""
    if c <= 0: return
    h = int(c * H / 2 + 1)
    fr[:h] *= 0.0; fr[:h] += 8; fr[H - h:] *= 0.0; fr[H - h:] += 8
    if c < 0.98:
        fr[max(0, h - 3):h] = np.array(GOLD, np.float32); fr[H - h:H - h + 3] = np.array(GOLD, np.float32)

def slam_lines(fr, lines, font, x, y, t0, t, colors, fg=IVORY, lh_pad=10, align='left', alpha=1.0, stagger=0.08):
    yy = y
    for k, ln in enumerate(lines):
        arr = box_text(ln, font, fg if colors[k % len(colors)] != GOLD else DARK, colors[k % len(colors)])
        p = eo3(prog(t, t0 + k * stagger, 0.28))
        if p > 0:
            xx = (W - arr.shape[1]) / 2 if align == 'center' else x
            dx = (1 - p) * (-140 if k % 2 == 0 else 140)
            blit(fr, arr, xx + dx, yy, min(1, p * 1.5) * alpha)
        yy += arr.shape[0] + lh_pad
    return yy

# ---------- press photo (freeze) ----------
_photo = {}
def press_photo(it):
    key = id(it)
    if key in _photo: return _photo[key]
    still = reframe(RD.get(it['freeze_sf']), it['freeze_z'], it['freeze_sf']).copy()
    bgb = blurred(still) * 0.42 + np.array(DGc, np.float32) * 0.25
    B = 18
    ph = np.full((H + 2 * B, W + 2 * B, 3), 250, np.uint8); ph[B:B + H, B:B + W] = still
    _photo[key] = (still, bgb, ph); return _photo[key]

def photo_frame(it, t, angle, final_scale=0.80, yshift=-140):
    still, bgb, ph = press_photo(it)
    p = eio3(prog(t, it['start'] + 0.10, 0.38))
    if p <= 0: return still.astype(np.float32)
    s = 1 + (final_scale - 1) * p; a = angle * p; dy = yshift * p
    fr = bgb.copy()
    ctr = ((W + 36) / 2, (H + 36) / 2)
    M = cv2.getRotationMatrix2D(ctr, a, s); M[0, 2] += W / 2 - ctr[0]; M[1, 2] += H / 2 - ctr[1] + dy
    # shadow
    mask = np.zeros(ph.shape[:2], np.uint8) + 255
    m = cv2.warpAffine(mask, M, (W, H), flags=cv2.INTER_LINEAR)
    shd = cv2.GaussianBlur(cv2.warpAffine(mask, M + np.array([[0, 0, 10], [0, 0, 22]], np.float32), (W, H)), (0, 0), 18).astype(np.float32)[..., None] / 255
    fr *= (1 - 0.55 * shd)
    img = cv2.warpAffine(ph, M, (W, H), flags=cv2.INTER_CUBIC).astype(np.float32)
    mm = (m.astype(np.float32) / 255)[..., None]
    return fr * (1 - mm) + img * mm

# ---------- segment helpers ----------
def seg_at(t):
    for i, it in enumerate(items):
        if it['start'] - 1e-6 <= t < it['end'] - 1e-6: return i, it
    return len(items) - 1, items[-1]

def clip_frame(it, t):
    for p in it['parts']:
        if t < p['out_out'] - 1e-6 or p is it['parts'][-1]: break
    lt = t - p['out_in']; dur = p['out_out'] - p['out_in']
    sf = int(round((p['src_in'] + lt) * FPS)); st_ = p['src_in'] + lt
    z = p['z0'] + (p['z1'] - p['z0']) * eio3(lt / dur)
    if 'zcut' in p and st_ >= p['zcut'][0]:
        z = p['zcut'][1] + 0.03 * eio3((st_ - p['zcut'][0]) / max(0.1, p['src_out'] - p['zcut'][0]))
    return reframe(RD.get(sf), z, sf).astype(np.float32)

def card_bg(it, t):
    a, b = it['src']; lt = t - it['start']
    sf = int(round((a + lt * (b - a) / (it['end'] - it['start'])) * FPS))
    img = reframe(RD.get(sf), 1.08, sf)
    return blurred(img) * 0.32 + np.array(DGc, np.float32) * 0.62

def card_overlay(fr, it, t):
    s, e = it['start'], it['end']; n = it['n']
    pe = eo3(prog(t, e - 0.22, 0.2))
    # giant faint number
    arr, pad, lh, wd = text_rgba(f'{n:02d}', FBIGNUM, IVORY)
    pz = eo3(prog(t, s, 0.9))
    blit(fr, arr, W - arr.shape[1] + 120 + (1 - pz) * 80, 330, 0.07 * (1 - pe))
    tag = box_text(f'SUAL {n:02d} / 05', FTAG, IVORY, BERRY)
    p = eo3(prog(t, s + 0.10, 0.25))
    blit(fr, tag, 90 + (1 - p) * -60, 690, p * (1 - pe))
    cat = it['cat']
    fcat = fit_font([cat], 'ArchivoX-ExtraBold.ttf', 112, W - 180)
    carr, cpad, clh, cwd = text_rgba(cat, fcat, IVORY)
    pc = prog(t, s + 0.18, 0.22); sc = 1.25 - 0.25 * eo3(pc)
    if pc > 0:
        a2 = cv2.resize(carr, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR) if sc > 1.001 else carr
        blit(fr, a2, 90 - cpad * sc - (a2.shape[1] - carr.shape[1]) * 0.0, 770 - cpad * sc - (a2.shape[0] - carr.shape[0]) / 2, min(1, pc * 2) * (1 - pe))
    yq = 770 + fcat.size + 40
    draw_rule(fr, 92, yq, 170 * eoexp(prog(t, s + 0.3, 0.5)), 4, GOLD, 1 - pe)
    reveal_lines(fr, it['text'], FQ, 84, yq + 30, s + 0.38, t, IVORY, stagger=0.09, dur=0.35, lh=84, alpha=1 - pe)

def follow_overlay(fr, it, t):
    s, e = it['start'], it['end']
    pe = eo3(prog(t, e - 0.18, 0.18)); p = eo3(prog(t, s, 0.22))
    arr, pad, lh, wd = text_rgba(it['text'], FFQ, IVORY, align='center', lh=78)
    bw, bh = arr.shape[1] + 40, arr.shape[0] + 60
    key = ('fbox', bw, bh)
    if key not in _c:
        im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=18, fill=(8, 40, 32, 215))
        _c[key] = np.asarray(im).astype(np.float32) / 255
    y = 1080; sc = 0.9 + 0.1 * p
    blit(fr, _c[key], W / 2 - bw / 2, y + (1 - p) * 30, p * (1 - pe))
    blit(fr, arr, W / 2 - arr.shape[1] / 2, y + 30 - pad + (1 - p) * 30, p * (1 - pe))
    tag = box_text('ƏLAVƏ SUAL', FTAG, IVORY, BERRY)
    blit(fr, tag, W / 2 - tag.shape[1] / 2, y - tag.shape[0] / 2 + (1 - p) * 30, p * (1 - pe))

def caption_overlay(fr, t):
    for ci, (a, b, txt) in enumerate(CAPS):
        nxt = CAPS[ci + 1][0] if ci + 1 < len(CAPS) else 1e9
        end = min(b + 0.1, nxt - 0.001)
        if a - 0.01 <= t < end:
            arr, pad, lh, wd = text_rgba(txt, FCAP, IVORY, shadow=7, shadow_alpha=0.85, align='center', lh=68)
            p = eo3(prog(t, a, 0.12)); pe = prog(t, end - 0.1, 0.1)
            nl = txt.count('\n') + 1
            blit(fr, arr, W / 2 - arr.shape[1] / 2, 1600 - nl * 68 - pad + (1 - p) * 12, p * (1 - pe))

def live_quote_overlay(fr, t):
    for (a, d, txt) in LQ:
        if a <= t < a + d:
            pe = eo3(prog(t, a + d - 0.2, 0.2)); lines = txt.split('\n')
            f = fit_font(lines, 'ArchivoX-ExtraBold.ttf', 60, W - 200)
            slam_lines(fr, lines, f, 80, 1110, a, t, [BERRY, DGc], alpha=1 - pe)

def freeze_overlay(fr, it, t):
    s = it['start']; lines = it['quote'].split('\n')
    f = fit_font(lines, 'ArchivoX-ExtraBold.ttf', 74, W - 170)
    tag = box_text('GÜLAY ZEYNALLI', FTAG, DARK, GOLD)
    p = eo3(prog(t, s + 0.25, 0.25))
    y0 = 1330 if len(lines) < 3 else 1290
    blit(fr, tag, 80 + (1 - p) * -60, y0 - tag.shape[0] - 14, p)
    slam_lines(fr, lines, f, 80, y0, s + 0.32, t, [BERRY, DGc, BERRY])

def title_overlay(fr, it, t):
    s = it['start']
    f = F('ArchivoX-ExtraBold.ttf', 118)
    tag = box_text('KƏŞF ET  ·  ARAZ 103.3 FM', FTAG, DARK, GOLD)
    p = eo3(prog(t, s + 0.3, 0.25)); blit(fr, tag, 80 + (1 - p) * -60, 1250, p)
    y = slam_lines(fr, ['GÜLAY', 'ZEYNALLI'], f, 80, 1310, s + 0.38, t, [DGc, BERRY], stagger=0.1)
    sub = box_text('5 təəccüblü sual, 5 cavab', F('Playfair-500-italic.ttf', 54), IVORY, (20, 20, 20))
    ps = eo3(prog(t, s + 0.62, 0.3)); blit(fr, sub, 80 + (1 - ps) * 60, y + 6, ps)

def end_overlay(fr, it, t):
    s = it['start']
    p = eo3(prog(t, s + 0.15, 0.3))
    reveal_lines(fr, 'GÜLAY ZEYNALLI', F('ArchivoX-ExtraBold.ttf', 74), 0, 760, s + 0.15, t, IVORY, align='center')
    reveal_lines(fr, '5 təəccüblü sual, 5 cavab', F('Playfair-500-italic.ttf', 58), 0, 870, s + 0.3, t, GOLD, align='center')
    draw_rule(fr, W / 2 - 80 * eoexp(prog(t, s + 0.4, 0.5)), 980, 160 * eoexp(prog(t, s + 0.4, 0.5)), 4, GOLD, 1)
    tag = box_text('KƏŞF ET  ·  ARAZ RADİO 103.3 FM', FTAG, IVORY, BERRY)
    pt = eo3(prog(t, s + 0.5, 0.3)); blit(fr, tag, W / 2 - tag.shape[1] / 2, 1020 + (1 - pt) * 20, pt)

# ---------- frame ----------
def render_frame(t):
    i, it = seg_at(t); kd = it['kind']
    prev = items[i - 1] if i else None; nxt = items[i + 1] if i + 1 < len(items) else None
    if kd == 'clip':
        fr = clip_frame(it, t); fr *= VIG; fr *= (1 - BOT)
    elif kd in ('card',):
        fr = card_bg(it, t)
    elif kd == 'follow':
        a, b = it['src']; sf = int(round((a + (t - it['start'])) * FPS))
        fr = reframe(RD.get(sf), 1.12, sf).astype(np.float32) * 0.55
    elif kd == 'title':
        fr = photo_frame(it, t, 2.6, 0.66, -40)
    elif kd == 'freeze':
        fr = photo_frame(it, t, -2.4 if it.get('last') is None else 2.2, 0.66, -40)
    else:  # end
        ref = items[i - 1]; still, bgb, ph = press_photo(ref)
        fr = bgb.copy() * 0.85
    # overlays
    if kd == 'card': card_overlay(fr, it, t)
    if kd == 'follow': follow_overlay(fr, it, t)
    if kd == 'title': title_overlay(fr, it, t)
    if kd == 'freeze': freeze_overlay(fr, it, t)
    if kd == 'end': end_overlay(fr, it, t)
    if kd == 'clip':
        live_quote_overlay(fr, t); caption_overlay(fr, t)
    # transitions
    k = int(round((t - it['start']) * FPS))
    if kd in ('title', 'freeze'): flash(fr, k)
    if t < 0.2: flash(fr, int(round(t * FPS)) + 1)
    if kd == 'card':
        shutter(fr, [1.0, 0.72, 0.42, 0.15][k] if k < 4 else 0)
    if nxt and nxt['kind'] == 'card':
        kb = int(round((nxt['start'] - t) * FPS))
        if 1 <= kb <= 3: shutter(fr, [0, 0.82, 0.55, 0.28][kb])
    if kd == 'clip' and prev and prev['kind'] in ('card', 'follow'):
        if k < 3: flash(fr, 3 + k)  # soft pop into answer
    if kd == 'end':
        pf = prog(t, it['end'] - 0.5, 0.5); fr *= (1 - 0.0 * pf)
    draw_logos(fr, 1.0)
    return np.clip(fr, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--stills':
        od = a[2]; os.makedirs(od, exist_ok=True)
        for ts in a[1].split(','):
            Image.fromarray(render_frame(float(ts))).save(f'{od}/s_{float(ts):06.2f}.png')
        sys.exit()
    t0 = float(a[0]) if a else 0.0; t1 = float(a[1]) if len(a) > 1 else TOTAL; out = a[2] if len(a) > 2 else 'v2_video.mp4'
    nf = int(round((t1 - t0) * FPS))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-x264-params', 'keyint=60', out], stdin=subprocess.PIPE)
    st = time.time()
    for k in range(nf):
        enc.stdin.write(render_frame(t0 + k / FPS).tobytes())
        if k % 150 == 0: print(f'{k}/{nf} {time.time() - st:.0f}s', flush=True)
    enc.stdin.close(); enc.wait(); print('done', time.time() - st)
