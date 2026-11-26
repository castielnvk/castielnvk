import sys, os, math
sys.argv = ['x']
import glass_render as G
import compose as C
from engine import *
from premium_grade import premium
from PIL import Image, ImageDraw, ImageFilter
T = os.path.join(BASE, '..', 'thumb5')
def panel(t, k):
    im = np.asarray(Image.open(f'{T}/f_{t}.png').convert('RGB'))
    x0 = 88 if k == 'L' else 1034
    return premium(np.ascontiguousarray(im[132:132+758, x0:x0+800]), k)
R = Image.fromarray(panel('52.5', 'R')); L = Image.fromarray(panel('48.2', 'L'))
GOLD = (255, 211, 110)
FB = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
def fnt(sz, p=FONT_CAP): return font(p, sz)
def logos(im, y=322):
    a, m = C.logo_png('araz_white', 96, 0); b, m2 = C.logo_png('show', 132, 0)
    A = Image.fromarray(a); B = Image.fromarray(b)
    im.alpha_composite(A, (int(52-m), int(y-A.size[1]/2))); im.alpha_composite(B, (int(W-52+m2-B.size[0]), int(y-B.size[1]/2)))
def fill(img, w, h, cx=0.5, cy=0.4, zoom=1.0):
    iw, ih = img.size; s = max(w/iw, h/ih)*zoom
    r = img.resize((int(iw*s), int(ih*s)), Image.LANCZOS)
    x = int((r.size[0]-w)*cx); y = int((r.size[1]-h)*cy)
    return r.crop((x, y, x+w, y+h))
def rmask(w, h, r):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], r, fill=255); return m
def text_center(d, y, txt, f, col, shadow=True):
    w = f.getbbox(txt)[2]
    if shadow: d.text(((W-w)/2+4, y+6), txt, font=f, fill=(0, 0, 0, 140))
    d.text(((W-w)/2, y), txt, font=f, fill=col)
def bg():
    return Image.fromarray(np.clip(G.bg_frame(0), 0, 255).astype(np.uint8)).convert('RGBA')

# A: full-bleed hero
def A():
    im = fill(R, W, H, cx=0.42, cy=0.25, zoom=1.0).convert('RGBA')
    im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32)*[1,1,1,1], 0, 255).astype(np.uint8))
    g = Image.new('L', (W, H), 0); gd = ImageDraw.Draw(g)
    for y in range(H):
        v = 0
        if y < 520: v = int(200*(1-y/520)**1.6)
        if y > 1050: v = int(235*min(1, (y-1050)/500)**1.2)
        gd.line([(0, y), (W, y)], fill=v)
    dark = Image.new('RGBA', (W, H), (12, 8, 28, 255)); dark.putalpha(g); im.alpha_composite(dark)
    logos(im)
    d = ImageDraw.Draw(im)
    text_center(d, 1330, 'MƏZAHİR', fnt(150), GOLD+(255,))
    text_center(d, 1490, 'DAYI', fnt(150), (255, 255, 255, 255))
    t = G.tag_content('NOYABR ŞEİRİ', 30, WHITE, '1f4dc'); a = np.array(im).astype(np.float32)[..., :3]
    out = a.copy(); G.glass(out, W/2-t.size[0]/2, 1250-t.size[1], t.size[0], t.size[1], r=t.size[1]//2, tint_a=0.5)
    im2 = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA'); im2.alpha_composite(t, (int(W/2-t.size[0]/2), int(1250-t.size[1])))
    return im2
# B: hero + circle inset, poster title on top
def B():
    im = bg()
    logos(im)
    d = ImageDraw.Draw(im)
    text_center(d, 420, 'MƏZAHİR DAYI', fnt(118), GOLD+(255,))
    text_center(d, 560, 'ŞEİR DEYİR', fnt(80), (255, 255, 255, 255))
    ph = fill(R, 980, 900, cx=0.45, cy=0.15)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([50, 715, 1030, 1625], 56, fill=(0, 0, 0, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    ImageDraw.Draw(im).rounded_rectangle([44, 694, 1036, 1606], 60, fill=GOLD+(255,))
    im.paste(ph, (50, 700), rmask(980, 900, 54))
    c = fill(L, 320, 320, cx=0.48, cy=0.3, zoom=1.15)
    cm = Image.new('L', (320, 320), 0); ImageDraw.Draw(cm).ellipse([0, 0, 319, 319], fill=255)
    ImageDraw.Draw(im).ellipse([690, 1310, 1030, 1650], fill=GOLD+(255,))
    im.paste(c, (700, 1320), cm)
    return im
# C: diagonal split
def C_():
    im = bg()
    top = fill(R, W, 900, cx=0.45, cy=0.2).convert('RGBA'); bot = fill(L, W, 900, cx=0.5, cy=0.3).convert('RGBA')
    mt = Image.new('L', (W, 900), 0); ImageDraw.Draw(mt).polygon([(0, 0), (W, 0), (W, 760), (0, 900)], fill=255)
    mb = Image.new('L', (W, 900), 0); ImageDraw.Draw(mb).polygon([(0, 140), (W, 0), (W, 900), (0, 900)], fill=255)
    im.paste(bot, (0, 920), mb); im.paste(top, (0, 240), mt)
    d = ImageDraw.Draw(im)
    d.polygon([(0, 1140-10), (W, 1000-10), (W, 1060+10), (0, 1200+10)], fill=GOLD+(255,))
    band = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    f = fnt(96); txt = 'MƏZAHİR DAYI'; w = f.getbbox(txt)[2]
    bd.text(((W-w)/2+4, 70+6), txt, font=f, fill=(0, 0, 0, 160)); bd.text(((W-w)/2, 70), txt, font=f, fill=(255, 255, 255, 255))
    band = band.rotate(7.4, Image.BICUBIC, expand=False)
    im.alpha_composite(band, (0, 960))
    g = Image.new('RGBA', (W, 240), (12, 8, 28, 235)); im.alpha_composite(g, (0, 0))
    logos(im, 140)
    ImageDraw.Draw(im).rectangle([0, 1820-0, W, H], fill=(12, 8, 28, 255))
    return im
# D: minimal circle portrait
def D():
    im = bg(); logos(im)
    d = ImageDraw.Draw(im)
    cx, cy, r = 540, 880, 400
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([cx-r-30, cy-r-30, cx+r+30, cy+r+30], fill=GOLD+(110,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    ImageDraw.Draw(im).ellipse([cx-r-12, cy-r-12, cx+r+12, cy+r+12], fill=GOLD+(255,))
    ph = fill(R, 2*r, 2*r, cx=0.45, cy=0.12, zoom=1.05); m = Image.new('L', (2*r, 2*r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2*r-1, 2*r-1], fill=255)
    im.paste(ph, (cx-r, cy-r), m)
    d = ImageDraw.Draw(im)
    text_center(d, 1330, 'MƏZAHİR DAYI', fnt(112), (255, 255, 255, 255))
    f2 = fnt(56); 
    text_center(d, 1475, '„ŞEİRİM BİTMƏYİB, ARDI VAR"', fnt(46, FONT_CAP8), GOLD+(255,), shadow=False)
    return im
outs = {'B': B()}
for k, v in outs.items(): v.convert('RGB').save(f'{T}/opt_{k}.jpg', quality=93)

b = outs['B'].convert('RGB')
g = b.crop((0, 240, 1080, 1680)).resize((360, 480))
full = b.resize((270, 480)); dd = ImageDraw.Draw(full); dd.rectangle([0, 60, 269, 420], outline=(255, 60, 60), width=3)
o = Image.new('RGB', (650, 480), (255, 255, 255)); o.paste(full, (0, 0)); o.paste(g, (290, 0)); o.save(f'{T}/grid_B.jpg', quality=92)
print('ok')
