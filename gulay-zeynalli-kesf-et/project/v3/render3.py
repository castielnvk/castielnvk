"""v3 renderer — social-media / paparazzi magazine cut.
usage: python3 render3.py [t0 t1 out.mp4] | --stills t,t,... dir"""
import numpy as np, cv2, subprocess, sys, os, math, time
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import render as R
from render import W, H, F, text_rgba, blit, eo3, eio3, eoexp, prog, clamp, reframe, blurred, VIG, IVORY, GOLD, draw_rule
from timeline3 import build, caption_chunks, FPS, BEAT

items, TOTAL, GRID0 = build()
CH = caption_chunks(items)
RD = R.Reader()
BERRY = (214, 36, 116); DGc = (8, 58, 45); INK = (18, 18, 20); HI = (255, 204, 64); RED = (226, 38, 38)
WORK = os.environ.get('WORK', '../work/')

# ---------------- user's logo overlay, 1:1, soft shadow only ----------------
ov = Image.open('assets/kesfet_araz_overlay.png').convert('RGBA')
al = ov.getchannel('A').filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.6))
sh = Image.new('RGBA', ov.size, (0, 0, 0, 0)); sh.putalpha(al)
sh2 = Image.new('RGBA', ov.size, (0, 0, 0, 0)); sh2.paste(sh, (0, 3)); sh2.alpha_composite(ov)
bb = sh2.getchannel('A').getbbox(); LOGO_Y0 = bb[1]
LOGO = np.asarray(sh2.crop((0, bb[1], W, bb[3]))).astype(np.float32) / 255
def draw_logos(fr): blit(fr, LOGO, 0, LOGO_Y0, 1.0)

# ---------------- helpers ----------------
_c = {}
def rgba(im): return np.asarray(im).astype(np.float32) / 255
def eob(x, s=1.70158):  # ease-out-back
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def flash(fr, k, strength=1.0):
    I = [0.92, 0.75, 0.5, 0.28, 0.12, 0.04]
    if 0 <= k < len(I): fr += (255 - fr) * I[k] * strength
GRAIN = [np.random.default_rng(s).normal(0, 9, (H // 2, W // 2)).astype(np.float32) for s in range(4)]
def grain(fr, k, amt=1.0):
    g = cv2.resize(GRAIN[k % 4], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]; fr += g * amt
def grade(fr):
    """social 'pop': gentle contrast + a touch of saturation, skin stays natural."""
    fr -= 128; fr *= 1.05; fr += 126
    g = fr.mean(axis=2, keepdims=True); fr -= g; fr *= 1.05; fr += g
    return fr

def box_text(txt, font, fg, bg, padx=22, pady=12, radius=10, stroke=0):
    key = ('box', txt, font.path, font.size, fg, bg, padx, pady, radius)
    if key in _c: return _c[key]
    asc, desc = font.getmetrics(); w = int(font.getlength(txt)) + 2 * padx; h = asc + int(desc * 0.4) + 2 * pady
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=bg + (255,))
    d.text((padx, pady - 1), txt, font=font, fill=fg + (255,))
    _c[key] = rgba(im); return _c[key]

def rotate_rgba(arr, ang, scale=1.0):
    h, w = arr.shape[:2]; c = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(c, ang, scale)
    cos, sin = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * sin + w * cos) + 2, int(h * cos + w * sin) + 2
    M[0, 2] += nw / 2 - c[0]; M[1, 2] += nh / 2 - c[1]
    return cv2.warpAffine(arr, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

def with_shadow(arr, r=16, a=0.5, off=12):
    h, w = arr.shape[:2]; P = r * 2 + off
    out = np.zeros((h + 2 * P, w + 2 * P, 4), np.float32)
    al = np.zeros(out.shape[:2], np.float32); al[P + off:P + off + h, P:P + w] = arr[..., 3]
    al = cv2.GaussianBlur(al, (0, 0), r) * a
    out[..., 3] = al
    # composite arr over shadow
    sub = out[P:P + h, P:P + w]; aa = arr[..., 3:4]
    sub[..., :3] = arr[..., :3] * aa + sub[..., :3] * (1 - aa)
    sub[..., 3:4] = aa + sub[..., 3:4] * (1 - aa)
    return out, P

# ---------------- footage access ----------------
def src_frame(t_src, z):
    sf = int(round(t_src * FPS)); return reframe(RD.get(sf), z, sf)

class SM:
    """graded 120 fps slow-motion clips (stored at 60 fps)."""
    cache = {}
    @classmethod
    def frames(cls, start):
        if start not in cls.cache:
            p = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{WORK}sm/sm_{start}.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            cls.cache[start] = np.frombuffer(p, np.uint8).reshape(-1, H, W, 3)
        return cls.cache[start]
def sm_frame(start, frac, z):
    fr = SM.frames(start); i = min(len(fr) - 1, int(frac * (len(fr) - 1)))
    t_src = start + i / 60.0; sf = int(round(t_src * FPS))
    return reframe(fr[i], z, sf)

# ---------------- captions (word-by-word) ----------------
FCAP = F('Archivo-Black.ttf', 84)
def chunk_img(txt, active):
    key = ('chunk', txt, active)
    if key in _c: return _c[key]
    words = txt.split(' '); clean = [w.lstrip('*') for w in words]; emph = [w.startswith('*') for w in words]
    sp = FCAP.getlength(' ')
    widths = [FCAP.getlength(w) for w in clean]
    lines = [[0]]; cur = widths[0]
    for i in range(1, len(clean)):
        if cur + sp + widths[i] > 920: lines.append([i]); cur = widths[i]
        else: lines[-1].append(i); cur += sp + widths[i]
    lh = 100; pad = 26
    Wd = int(max(sum(widths[i] for i in L) + sp * (len(L) - 1) for L in lines)) + 2 * pad; Hd = lh * len(lines) + 2 * pad
    im = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, L in enumerate(lines):
        lw = sum(widths[i] for i in L) + sp * (len(L) - 1); x = (Wd - lw) / 2; y = pad + li * lh
        for i in L:
            col = HI if i == active else ((255, 255, 255) if not emph[i] or active < i else (255, 255, 255))
            if emph[i] and i <= active: col = HI if i == active else (255, 226, 140)
            d.text((x, y), clean[i], font=FCAP, fill=col + (255,), stroke_width=7, stroke_fill=(10, 10, 10, 255))
            x += widths[i] + sp
    a = im.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55))
    shd = Image.new('RGBA', im.size, (0, 0, 0, 0)); shd.putalpha(a)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(shd, (0, 6)); out.alpha_composite(im)
    _c[key] = rgba(out); return _c[key]

def caption_overlay(fr, t):
    for (a, b, txt) in CH:
        if a <= t < b:
            words = txt.split(' '); L = [len(w.lstrip('*')) + 1 for w in words]
            dur = max(0.2, min(b - a, 0.33 * len(words) + 0.15))
            cum = np.cumsum(L) / sum(L); fr_ = (t - a) / dur
            active = int(np.searchsorted(cum, min(fr_, 0.999), side='right')); active = min(active, len(words) - 1)
            arr = chunk_img(txt, active)
            p = prog(t, a, 0.12); s = 0.86 + 0.14 * eob(p)
            if s < 0.995: arr = cv2.resize(arr, None, fx=s, fy=s, interpolation=cv2.INTER_LINEAR)
            blit(fr, arr, W / 2 - arr.shape[1] / 2, 1270 - arr.shape[0] / 2, min(1, p * 3))

# ---------------- top pill (show tag + question progress) ----------------
FPILL = F('ArchivoX-Bold.ttf', 23)
def top_pill(fr, t, qn, alpha=1.0):
    if alpha <= 0: return
    key = ('pill', qn)
    if key not in _c:
        txt = 'GÜLAY ZEYNALLI'; tw = FPILL.getlength(txt) + 6 * (len(txt) - 1) * 0
        w, h = int(tw) + 92, 50
        im = Image.new('RGBA', (w, h + 22), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=25, fill=(12, 12, 14, 200))
        d.ellipse([20, 18, 34, 32], fill=RED + (255,))
        d.text((48, 11), txt, font=FPILL, fill=(255, 255, 255, 255))
        bw = (w - 40 - 4 * 8) / 5
        for k in range(5):
            x = 20 + k * (bw + 8)
            d.rounded_rectangle([x, h + 10, x + bw, h + 16], radius=3, fill=(HI + (255,)) if k < qn else (255, 255, 255, 110))
        _c[key] = rgba(im)
    arr = _c[key]
    blit(fr, arr, W / 2 - arr.shape[1] / 2, 192, alpha)
    # blinking live dot handled by alpha of a red overlay
    if int(t * 2) % 2 == 1:
        pass

def current_q(t):
    n = 0
    for it in items:
        if it['start'] > t: break
        if it['kind'] == 'q': n = it['n']
    return n

# ---------------- viewfinder ----------------
FVF = F('ArchivoX-SemiBold.ttf', 24)
def viewfinder(fr, t, alpha=1.0):
    if alpha <= 0: return
    if 'vf' not in _c:
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        x0, y0, x1, y1, L, th = 70, 340, W - 70, 1700, 70, 5
        for (x, y, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(x, y), (x + dx * L, y)], fill=(255, 255, 255, 230), width=th); d.line([(x, y), (x, y + dy * L)], fill=(255, 255, 255, 230), width=th)
        cx, cy = W // 2, 900
        d.line([(cx - 24, cy), (cx + 24, cy)], fill=(255, 255, 255, 150), width=2); d.line([(cx, cy - 24), (cx, cy + 24)], fill=(255, 255, 255, 150), width=2)
        d.text((W - 300, 1640), 'ISO 400   1/250', font=FVF, fill=(255, 255, 255, 210))
        _c['vf'] = rgba(im)
    blit(fr, _c['vf'], 0, 0, alpha)
    if int(t * 2.5) % 2 == 0:
        rec = box_text('● REC', FVF, (255, 255, 255), (200, 20, 20), padx=14, pady=6, radius=6)
        blit(fr, rec, 100, 362, alpha)
    tc = f'00:00:{int(t):02d}:{int((t % 1) * 30):02d}'
    arr, pad, lh, wd = text_rgba(tc, FVF, (255, 255, 255), shadow=3)
    blit(fr, arr, 100 - pad, 1640 - pad, alpha * 0.9)

# ---------------- question sticker ----------------
FQS = F('Archivo-ExtraBold.ttf', 58); FQH = F('ArchivoX-Bold.ttf', 25)
def wrap(text, font, maxw):
    words = text.split(); lines = []; cur = ''
    for w_ in words:
        tst = (cur + ' ' + w_).strip()
        if font.getlength(tst) <= maxw: cur = tst
        else: lines.append(cur); cur = w_
    lines.append(cur); return lines
def sticker(header, text, small=False):
    key = ('stk', header, text, small)
    if key in _c: return _c[key]
    fq = F('Archivo-ExtraBold.ttf', 52 if small else 58)
    lines = wrap(text, fq, 740); lh = 66 if small else 72
    w = 860; hh = 64; h = hh + 40 + lh * len(lines) + 30
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=(255, 255, 255, 255))
    d.rounded_rectangle([0, 0, w - 1, hh + 30], radius=34, fill=BERRY + (255,)); d.rectangle([0, hh, w - 1, hh + 30], fill=(255, 255, 255, 255))
    hw = FQH.getlength(header); d.text(((w - hw) / 2, 18), header, font=FQH, fill=(255, 255, 255, 255))
    for i, ln in enumerate(lines):
        lw = fq.getlength(ln); d.text(((w - lw) / 2, hh + 34 + i * lh), ln, font=fq, fill=INK + (255,))
    arr, P = with_shadow(rgba(im), 22, 0.45, 14)
    _c[key] = arr; return arr

def sticker_overlay(fr, it, t, header, text, small=False, y=930):
    s, e = it['start'], it['end']
    p = prog(t, s + 0.04, 0.32); pe = prog(t, e - 0.16, 0.16)
    if p <= 0: return
    sc = (0.55 + 0.45 * eob(p, 2.2)) * (1 - 0.25 * eio3(pe))
    arr = rotate_rgba(sticker(header, text, small), -2.5 + 2.5 * (1 - eo3(p)) * -1, sc)
    blit(fr, arr, W / 2 - arr.shape[1] / 2, y - arr.shape[0] / 2, min(1, p * 2.5) * (1 - eio3(pe)))

# ---------------- press prints (collage / callback) ----------------
def print_photo(t_src, z=1.18, wpx=430, crop_ratio=1.25):
    key = ('print', t_src, z, wpx)
    if key in _c: return _c[key]
    img = src_frame(t_src, z)
    ch = int(W * crop_ratio); y0 = 180
    img = img[y0:y0 + ch]
    hpx = int(wpx * crop_ratio)
    img = cv2.resize(img, (wpx, hpx), interpolation=cv2.INTER_AREA)
    B = 14; Bb = 14
    canvas = np.full((hpx + B + Bb, wpx + 2 * B, 4), 255, np.uint8); canvas[B:B + hpx, B:B + wpx, :3] = img
    arr = canvas.astype(np.float32) / 255
    _c[key] = arr; return arr

def red_circle(fr, cx, cy, rx, ry, p, ang=-8):
    if p <= 0: return
    key = ('circ', rx, ry, ang)
    if key not in _c:
        _c[key] = None
    n = 60; th = np.linspace(-0.6, -0.6 + 2 * np.pi * 1.08 * p, max(2, int(n * p)))
    pts = np.stack([cx + rx * np.cos(th) * (1 + 0.04 * np.sin(3 * th)), cy + ry * np.sin(th)], 1)
    a = math.radians(ang); R_ = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    pts = (pts - [cx, cy]) @ R_.T + [cx, cy]
    tmp = fr.copy(); cv2.polylines(tmp, [pts.astype(np.int32)], False, RED, 9, cv2.LINE_AA)
    fr[:] = tmp

FBIG = F('Archivo-Black.ttf', 92); FSUB = F('ArchivoX-Bold.ttf', 34)
def collage(fr_bg, it, t):
    s = it['start']; lt = t - s
    fr = fr_bg
    photos = [(71.60, 300, 640, -8), (27.60, 790, 610, 7), (16.40, 320, 1250, 5), (75.95, 770, 1270, -6)]
    hit = [0.0, 0.2, 0.4, 0.6]
    for k, (ts, cx, cy, ang) in enumerate(photos):
        p = prog(lt, hit[k], 0.16)
        if p <= 0: continue
        sc = 1.35 - 0.35 * eo3(p)
        arr, P = with_shadow(print_photo(ts), 18, 0.5, 12) if ('ps', ts) not in _c else _c[('ps', ts)]
        _c[('ps', ts)] = (arr, P)
        ra = rotate_rgba(arr, ang, sc)
        blit(fr, ra, cx - ra.shape[1] / 2, cy - ra.shape[0] / 2, min(1, p * 3))
    red_circle(fr, 790, 520, 120, 150, eo3(prog(lt, 0.85, 0.35)), 7)
    # title
    pt = prog(lt, 0.95, 0.3)
    if pt > 0:
        a1 = box_text('GÜLAY ZEYNALLI', FBIG, (255, 255, 255), DGc, padx=26, pady=14, radius=12)
        a2 = box_text('5 TƏƏCCÜBLÜ SUAL, 5 CAVAB', FSUB, (255, 255, 255), BERRY, padx=20, pady=12, radius=10)
        s1 = 1.2 - 0.2 * eob(pt)
        b1 = cv2.resize(a1, None, fx=s1, fy=s1) if abs(s1 - 1) > 0.01 else a1
        blit(fr, b1, W / 2 - b1.shape[1] / 2, 900 - b1.shape[0] / 2, min(1, pt * 3))
        p2 = eo3(prog(lt, 1.15, 0.25)); blit(fr, a2, W / 2 - a2.shape[1] / 2 + (1 - p2) * 120, 975, p2)
    return fr

# ---------------- frame ----------------
def seg_at(t):
    for i, it in enumerate(items):
        if it['start'] - 1e-6 <= t < it['end'] - 1e-6: return i, it
    return len(items) - 1, items[-1]

def clip_frame(it, t):
    for p in it['parts']:
        if t < p['out_out'] - 1e-6 or p is it['parts'][-1]: break
    lt = t - p['out_in']; dur = p['out_out'] - p['out_in']; st_ = p['src_in'] + lt
    z = p['z0'] + (p['z1'] - p['z0']) * eio3(lt / dur)
    if 'zcut' in p and st_ >= p['zcut'][0]:
        z = p['zcut'][1] + 0.025 * eio3((st_ - p['zcut'][0]) / max(0.1, p['src_out'] - p['zcut'][0]))
    return src_frame(st_, z).astype(np.float32), p, st_

def render_frame(t):
    i, it = seg_at(t); kd = it['kind']; lt = t - it['start']; k = int(round(lt * FPS))
    prev = items[i - 1] if i else None
    qn = current_q(t)
    if kd == 'clip':
        fr, p, st_ = clip_frame(it, t); fr *= VIG; fr = grade(fr)
        vf = it.get('vf') or ('vf_from' in it and st_ >= it['vf_from'])
        if vf: viewfinder(fr, t)
        caption_overlay(fr, t)
        if it.get('tag') != 'hook': top_pill(fr, t, qn)
        if prev and prev['kind'] in ('q', 'follow') and k < 3: flash(fr, 3 + k, 0.6)
        if it.get('tag') == 'hook' and k < 6: flash(fr, k)
        # punch-in cut flash
        if 'zcut' in p and abs(p['src_in'] + (t - p['out_in']) - p['zcut'][0]) < 0.5 / FPS: flash(fr, 2, 0.5)
    elif kd == 'q':
        frac = lt / (it['end'] - it['start'])
        fr = sm_frame(it['sm'], frac, 1.12).astype(np.float32); fr *= VIG; fr = grade(fr); fr *= 0.62
        sticker_overlay(fr, it, t, f"SUAL {it['n']:02d} / 05  ·  {it['cat']}", it['text'])
        top_pill(fr, t, qn)
    elif kd == 'follow':
        fr = src_frame(it['src'] + lt, 1.14).astype(np.float32); fr = grade(fr); fr *= 0.62
        sticker_overlay(fr, it, t, 'ƏLAVƏ SUAL', it['text'], small=True)
        top_pill(fr, t, qn)
    elif kd == 'collage':
        still = src_frame(it['freeze_sf'] / FPS, it['freeze_z'])
        bg = blurred(still) * 0.38 + np.array(DGc, np.float32) * 0.3
        fr = collage(bg, it, t); grain(fr, k, 0.8)
        for h_ in (0.0, 0.2, 0.4, 0.6):
            kk = int(round((lt - h_) * FPS))
            if 0 <= kk < 4: flash(fr, kk + 1, 0.85)
    elif kd == 'burst':
        still = src_frame(it['freeze_sf'] / FPS, it['freeze_z']).astype(np.float32)
        step = 0 if lt < 0.33 else (1 if lt < 0.66 else 2)
        z = [1.0, 1.06, 1.12][step]
        if z > 1: still = cv2.resize(still, None, fx=z, fy=z)[int(H * (z - 1) * 0.35):][:H, int(W * (z - 1) / 2):][:, :W]
        gry = still.mean(axis=2, keepdims=True); fr = gry * 0.85 + still * 0.15; fr = (fr - 128) * 1.15 + 128
        grain(fr, k, 1.4)
        for h_ in (0.0, 0.33, 0.66):
            kk = int(round((lt - h_) * FPS))
            if 0 <= kk < 5: flash(fr, kk)
        top_pill(fr, t, qn)
    elif kd == 'callback':
        still = src_frame(items[0]['parts'][0]['src_out'] - 1 / FPS, 1.30)
        bg = blurred(still) * 0.36 + np.array(DGc, np.float32) * 0.32; fr = bg
        ph = print_photo(items[0]['parts'][0]['src_out'] - 0.1, 1.24, 560)
        arr, P = with_shadow(ph, 20, 0.5, 14)
        p = eo3(prog(lt, 0.0, 0.25)); ra = rotate_rgba(arr, -4, 1.25 - 0.25 * p)
        blit(fr, ra, W / 2 - ra.shape[1] / 2, 760 - ra.shape[0] / 2, min(1, p * 3))
        red_circle(fr, W / 2 + 5, 680, 115, 145, eo3(prog(lt, 0.3, 0.35)), -6)
        lines = it['quote'].split('\n'); y = 1150
        tag = box_text('GÜLAY ZEYNALLI', FSUB, INK, HI, padx=16, pady=8, radius=8)
        pt = eo3(prog(lt, 0.4, 0.2)); blit(fr, tag, W / 2 - tag.shape[1] / 2, y - 60, pt)
        for j, ln in enumerate(lines):
            b = box_text(('“' if j == 0 else '') + ln + ('”' if j == len(lines) - 1 else ''), FBIG, (255, 255, 255), [BERRY, DGc][j % 2], padx=24, pady=12)
            pj = prog(lt, 0.48 + j * 0.1, 0.25); sc = 1.25 - 0.25 * eob(pj)
            if pj > 0:
                bj = cv2.resize(b, None, fx=sc, fy=sc) if abs(sc - 1) > 0.01 else b
                blit(fr, bj, W / 2 - bj.shape[1] / 2, y + j * 120 + (b.shape[0] - bj.shape[0]) / 2, min(1, pj * 3))
        grain(fr, k, 0.7)
        flash(fr, k)
        top_pill(fr, t, qn)
    else:  # end
        frac = lt / (it['end'] - it['start'])
        fr = sm_frame(it['sm'], frac, 1.10 + 0.05 * frac).astype(np.float32); fr *= VIG; fr = grade(fr)
        flash(fr, k)
        tg = box_text('TAM SÖHBƏT', FSUB, INK, HI, padx=16, pady=8, radius=8)
        p1 = eo3(prog(lt, 0.3, 0.25)); blit(fr, tg, W / 2 - tg.shape[1] / 2, 1180 + (1 - p1) * 30, p1)
        b = box_text('ARAZ 103.3 FM', FBIG, (255, 255, 255), DGc, padx=26, pady=14, radius=12)
        p2 = prog(lt, 0.42, 0.25); s2 = 1.2 - 0.2 * eob(p2)
        if p2 > 0:
            bj = cv2.resize(b, None, fx=s2, fy=s2) if abs(s2 - 1) > 0.01 else b
            blit(fr, bj, W / 2 - bj.shape[1] / 2, 1250, min(1, p2 * 3))
        b3 = box_text('KƏŞF ET', FSUB, (255, 255, 255), BERRY, padx=18, pady=10, radius=10)
        p3 = eo3(prog(lt, 0.6, 0.25)); blit(fr, b3, W / 2 - b3.shape[1] / 2 + (1 - p3) * 100, 1390, p3)
        top_pill(fr, t, 5)
    draw_logos(fr)
    return np.clip(fr, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--stills':
        od = a[2]; os.makedirs(od, exist_ok=True)
        for ts in a[1].split(','):
            Image.fromarray(render_frame(float(ts))).save(f'{od}/s_{float(ts):06.2f}.png')
        sys.exit()
    t0 = float(a[0]) if a else 0.0; t1 = float(a[1]) if len(a) > 1 else TOTAL; out = a[2] if len(a) > 2 else 'v3_video.mp4'
    nf = int(round((t1 - t0) * FPS))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-x264-params', 'keyint=60', out], stdin=subprocess.PIPE)
    st = time.time()
    for k in range(nf):
        enc.stdin.write(render_frame(t0 + k / FPS).tobytes())
        if k % 150 == 0: print(f'{k}/{nf} {time.time() - st:.0f}s', flush=True)
    enc.stdin.close(); enc.wait(); print('done', time.time() - st)
