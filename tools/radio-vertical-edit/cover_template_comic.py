import sys, os, math, random
sys.argv = ['x']
import glass_render as G
import compose as C
from engine import *
from PIL import Image, ImageDraw, ImageFilter, ImageOps
T = os.path.join(BASE, '..', 'thumb5')
BANG = os.path.join(ASSETS, 'Bangers.ttf')
def bf(sz): return ImageFont.truetype(BANG, sz)
R = Image.open(f'{T}/cut_R_u2net_human_seg.png').convert('RGBA')
L = Image.open(f'{T}/cut_L_u2net_human_seg.png').convert('RGBA')
def trim(im):
    bb = im.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox(); return im.crop(bb)
R = trim(R); L = trim(L)
YEL = (255, 214, 10); RED = (230, 40, 60); BLK = (15, 10, 20); WHT = (255, 255, 255); CY = (40, 200, 240); PNK = (255, 70, 170); PUR = (110, 40, 200)

def sticker(im, w, outline=14, black=5, shadow=(10, 14)):
    s = w/im.size[0]; im = im.resize((w, int(im.size[1]*s)), Image.LANCZOS)
    pad = outline+black+30
    big = Image.new('RGBA', (im.size[0]+2*pad, im.size[1]+2*pad), (0, 0, 0, 0)); big.alpha_composite(im, (pad, pad))
    a = big.split()[3].point(lambda v: 255 if v > 90 else 0)
    w1 = a.filter(ImageFilter.MaxFilter(2*outline+1)); b1 = w1.filter(ImageFilter.MaxFilter(2*black+1)) if black > 0 else w1
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    sh = Image.new('RGBA', big.size, BLK+(255,)); sh.putalpha(b1)
    out.alpha_composite(sh, shadow)
    bl = Image.new('RGBA', big.size, BLK+(255,)); bl.putalpha(b1); out.alpha_composite(bl)
    wt = Image.new('RGBA', big.size, WHT+(255,)); wt.putalpha(w1); out.alpha_composite(wt)
    out.alpha_composite(big)
    return out

def comic_text(txt, size, fill, stroke=10, shadow=8, rot=0, stroke_col=BLK):
    f = bf(size); bb = f.getbbox(txt, stroke_width=stroke)
    w, h = bb[2]-bb[0]+shadow+20, bb[3]-bb[1]+shadow+20
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox, oy = 10-bb[0], 10-bb[1]
    d.text((ox+shadow, oy+shadow), txt, font=f, fill=stroke_col, stroke_width=stroke, stroke_fill=stroke_col)
    d.text((ox, oy), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_col)
    return im.rotate(rot, Image.BICUBIC, expand=True) if rot else im

def halftone(w, h, col_bg, col_dot, step=26, rmax=9, cx=0.5, cy=0.5):
    im = Image.new('RGBA', (w, h), col_bg+(255,)); d = ImageDraw.Draw(im)
    for y in range(0, h+step, step):
        for x in range(0, w+step, step):
            xo = x+(step/2 if (y//step) % 2 else 0)
            dist = math.hypot((xo/w-cx)*1.2, (y/h-cy))
            r = rmax*min(1, dist*1.6)
            if r > 0.8: d.ellipse([xo-r, y-r, xo+r, y+r], fill=col_dot+(255,))
    return im

def rays(w, h, c1, c2, n=28, cx=540, cy=900):
    im = Image.new('RGBA', (w, h), c1+(255,)); d = ImageDraw.Draw(im)
    for i in range(n):
        if i % 2: continue
        a0 = 2*math.pi*i/n; a1 = 2*math.pi*(i+1)/n; R_ = 3000
        d.polygon([(cx, cy), (cx+R_*math.cos(a0), cy+R_*math.sin(a0)), (cx+R_*math.cos(a1), cy+R_*math.sin(a1))], fill=c2+(255,))
    return im

def burst(text, size, fill=YEL, txtcol=BLK, spikes=16, r1=1.0, r2=0.72, rot=-8, w=None):
    f = bf(size); bb = f.getbbox(text); tw, th = bb[2]-bb[0], bb[3]-bb[1]
    W_ = w or int(tw*1.6); H_ = int(W_*0.75)
    im = Image.new('RGBA', (W_+40, H_+40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = (W_+40)/2, (H_+40)/2; pts = []; pts2 = []
    rnd = random.Random(len(text))
    for i in range(spikes*2):
        a = math.pi*i/spikes; rr = (r1 if i % 2 == 0 else r2)*(0.92+0.16*rnd.random())
        pts.append((cx+math.cos(a)*W_/2*rr, cy+math.sin(a)*H_/2*rr))
    d.polygon([(x+8, y+10) for x, y in pts], fill=BLK+(255,))
    d.polygon(pts, fill=fill+(255,), outline=BLK+(255,), width=7)
    d.text((cx-tw/2-bb[0], cy-th/2-bb[1]), text, font=f, fill=txtcol)
    return im.rotate(rot, Image.BICUBIC, expand=True)

def bubble(lines, size, w, tail=(0.2, 1.0), rot=0):
    f = bf(size); lh = int(size*1.05)
    h = lh*len(lines)+60
    im = Image.new('RGBA', (w+60, h+140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 20, 20, w+20, h+20
    tx = x0+(x1-x0)*tail[0]
    for off, col in [((8, 10), BLK), ((0, 0), None)]:
        ox, oy = off
        poly = [(tx-40+ox, y1-6+oy), (tx+30+ox, y1-6+oy), (tx-30+ox, y1+110+oy)]
        if col:
            d.ellipse([x0+ox, y0+oy, x1+ox, y1+oy], fill=BLK+(255,)); d.polygon(poly, fill=BLK+(255,))
        else:
            d.polygon(poly, fill=WHT+(255,), outline=BLK+(255,), width=7)
            d.ellipse([x0, y0, x1, y1], fill=WHT+(255,), outline=BLK+(255,), width=7)
            d.polygon([(tx-34, y1-14), (tx+24, y1-14), (tx-24, y1+6)], fill=WHT+(255,))
    y = y0+30
    for ln in lines:
        tw = f.getbbox(ln)[2]; d.text(((x0+x1)/2-tw/2, y), ln, font=f, fill=BLK); y += lh
    return im.rotate(rot, Image.BICUBIC, expand=True) if rot else im

def logos(im, y=300, plate=True):
    a, m = C.logo_png('araz_white', 92, 0); b, m2 = C.logo_png('show', 128, 0)
    A = Image.fromarray(a); B = Image.fromarray(b)
    if plate:
        d = ImageDraw.Draw(im)
        for (x, ww) in [(34, A.size[0]-2*m+36), (W-34-(B.size[0]-2*m2+28), B.size[0]-2*m2+28)]:
            d.rounded_rectangle([x+6, y-78+8, x+ww+6, y+78+8], 22, fill=BLK+(255,))
            d.rounded_rectangle([x, y-78, x+ww, y+78], 22, fill=(30, 20, 60, 255), outline=BLK+(255,), width=6)
    im.alpha_composite(A, (int(52-m), int(y-A.size[1]/2))); im.alpha_composite(B, (int(W-48+m2-B.size[0]), int(y-B.size[1]/2)))

def paste_c(im, el, cx, cy): im.alpha_composite(el, (int(cx-el.size[0]/2), int(cy-el.size[1]/2)))
def border(im, col=BLK, w=14):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W-1, H-1], outline=col+(255,), width=w)


def plogos(im, y=300):
    a, m = C.logo_png('araz_white', 100, 0); b, m2 = C.logo_png('show', 140, 0)
    A = Image.fromarray(a); B = Image.fromarray(b)
    for L_, pos in [(A, (int(56-m), int(y-A.size[1]/2))), (B, (int(W-52+m2-B.size[0]), int(y-B.size[1]/2)))]:
        al = L_.split()[3].filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(16)).point(lambda v: min(255, int(v*1.6)))
        sh = Image.new('RGBA', L_.size, (20, 10, 40, 255)); sh.putalpha(al.point(lambda v: int(v*0.85)))
        im.alpha_composite(sh, pos); im.alpha_composite(L_, pos)
def esticker(code, size, rot=0):
    e = emoji(code, size, 12)
    a = e.split()[3]
    out = Image.new('RGBA', (e.size[0]+20, e.size[1]+20), (0, 0, 0, 0))
    bl = Image.new('RGBA', e.size, BLK+(255,)); bl.putalpha(a.filter(ImageFilter.MaxFilter(9)))
    out.alpha_composite(bl, (10, 14)); out.alpha_composite(bl, (6, 6)); out.alpha_composite(e, (6, 6))
    return out.rotate(rot, Image.BICUBIC, expand=True)
def speedlines(im, cx, cy, col=WHT, n=70, r0=520, r1=1600, a=150, seed=3):
    d = ImageDraw.Draw(im, 'RGBA'); rnd = random.Random(seed)
    for i in range(n):
        ang = rnd.uniform(0, 2*math.pi); w = rnd.uniform(4, 14); ra = r0*rnd.uniform(0.9, 1.3)
        x0, y0 = cx+math.cos(ang)*ra, cy+math.sin(ang)*ra; x1, y1 = cx+math.cos(ang)*r1, cy+math.sin(ang)*r1
        nx, ny = -math.sin(ang)*w, math.cos(ang)*w
        d.polygon([(x0, y0), (x1+nx, y1+ny), (x1-nx, y1-ny)], fill=col+(a,))
def bottom_person(im, src, w, cx, bottom=H, outline=14):
    st = sticker(src, w, outline=outline)
    im.alpha_composite(st, (int(cx-st.size[0]/2), int(bottom-st.size[1]+outline+40)))
def label(txt, size, bg, fg, rot=0):
    f = bf(size); bb = f.getbbox(txt); w, h = bb[2]-bb[0]+50, bb[3]-bb[1]+34
    im = Image.new('RGBA', (w+16, h+16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([10, 12, w+10, h+12], fill=BLK+(255,)); d.rectangle([0, 0, w, h], fill=bg+(255,), outline=BLK+(255,), width=6)
    d.text((25-bb[0], 17-bb[1]), txt, font=f, fill=fg)
    return im.rotate(rot, Image.BICUBIC, expand=True) if rot else im

# 1 — dense POW
def n1():
    im = rays(W, H, (255, 200, 0), (255, 160, 0), n=32, cx=540, cy=1100)
    ht = halftone(W, H, (255, 160, 0), (235, 110, 0), step=28, rmax=8, cy=0.6)
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse([-300, 1000, 1380, 2400], fill=170); im.paste(ht, (0, 0), m.filter(ImageFilter.GaussianBlur(60)))
    speedlines(im, 540, 1150, col=WHT, a=110)
    plogos(im)
    paste_c(im, comic_text('MƏZAHİR', 190, WHT, stroke=14, shadow=14, rot=4), 520, 520)
    paste_c(im, comic_text('DAYI!', 200, RED, stroke=14, shadow=14, rot=4), 560, 720)
    bottom_person(im, R, 1060, 560, H)
    st = sticker(L, 450, outline=12); im.alpha_composite(st, (int(240-st.size[0]/2), 1290))
    paste_c(im, bubble(['ŞEİRİM BİTMƏYİB,', 'ARDI VAR!'], 50, 440, tail=(0.25, 1.0), rot=0), 820, 930)
    paste_c(im, esticker('1f69c', 150, -12), 140, 880)
    paste_c(im, esticker('1f697', 140, 10), 950, 1290)
    paste_c(im, esticker('1f342', 110, 15), 960, 1100)
    paste_c(im, burst('HA-HA!', 56, fill=CY, txtcol=BLK, rot=-14, w=270), 150, 1100)
    paste_c(im, label('NOYABR ŞEİRİ', 48, WHT, BLK, rot=-4), 820, 1600)
    border(im)
    return im
# 2 — 4-panel comic page, every panel busy
def n2():
    im = Image.new('RGBA', (W, H), BLK+(255,))
    plogos(im, 200)
    panels = [([(30, 330), (1050, 310), (1050, 1150), (30, 1180)], (255, 214, 10), (255, 160, 0)),
              ([(30, 1215), (540, 1200), (530, 1560), (30, 1570)], (40, 200, 240), (20, 140, 220)),
              ([(575, 1198), (1050, 1185), (1050, 1550), (565, 1558)], (255, 70, 170), (210, 30, 130)),
              ([(30, 1605), (1050, 1585), (1050, 1890), (30, 1890)], (130, 60, 230), (100, 40, 190))]
    def panel_layer(poly, bgc, dotc, content):
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]; bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay.paste(halftone(bx1-bx0, by1-by0, bgc, dotc, step=22, rmax=7), (bx0, by0))
        content(lay)
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
        lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.split()[3]), np.asarray(m))))
        im.alpha_composite(lay); ImageDraw.Draw(im).polygon(poly, outline=WHT+(255,), width=10)
    def c1(l):
        speedlines(l, 540, 760, col=WHT, a=120, r0=380)
        r = sticker(R, 980); l.alpha_composite(r, (int(560-r.size[0]/2), int(1200-r.size[1]+40)))
    def c2(l):
        s_ = esticker('1f69c', 230, -8); l.alpha_composite(s_, (130, 1250))
    def c3(l):
        s_ = esticker('1f697', 210, 8); l.alpha_composite(s_, (700, 1250))
    def c4(l):
        p = sticker(L, 420, outline=12); l.alpha_composite(p, (int(780-p.size[0]/2), 1590))
    for (poly, a, b), fn in zip(panels, [c1, c2, c3, c4]): panel_layer(poly, a, b, fn)
    paste_c(im, comic_text('MƏZAHİR DAYI', 120, YEL, stroke=11, shadow=10, rot=-3), 400, 420)
    paste_c(im, bubble(['ŞEİRİM BİTMƏYİB,', 'ARDI VAR!'], 50, 430, tail=(0.3, 1.0)), 820, 600)
    paste_c(im, comic_text('TRAKTOR!', 70, WHT, stroke=8, shadow=7, rot=-6), 285, 1500)
    paste_c(im, comic_text('JAECOO J8!', 66, WHT, stroke=8, shadow=7, rot=6), 810, 1490)
    paste_c(im, comic_text('HA-HA-HA!', 110, YEL, stroke=10, shadow=9, rot=-5), 290, 1730)
    return im
# 3 — split poster, two big heroes
def n3():
    im = halftone(W, H, (110, 40, 210), (150, 80, 250), step=30, rmax=10, cy=0.4)
    d = ImageDraw.Draw(im)
    d.polygon([(0, 1250), (W, 1050), (W, H), (0, H)], fill=(255, 70, 170, 255))
    ht2 = halftone(W, 900, (255, 70, 170), (220, 40, 140), step=26, rmax=8, cy=0.2)
    mm = Image.new('L', (W, 900), 0); ImageDraw.Draw(mm).polygon([(0, 230), (W, 30), (W, 900), (0, 900)], fill=255); im.paste(ht2, (0, 1020), mm)
    ImageDraw.Draw(im).line([(0, 1250), (W, 1050)], fill=YEL+(255,), width=22)
    speedlines(im, 540, 700, col=WHT, a=70, r0=420)
    plogos(im)
    r = sticker(R, 900); im.alpha_composite(r, (int(540-r.size[0]/2), int(1300-r.size[1]+40)))
    bottom_person(im, L, 640, 720, H, outline=13)
    paste_c(im, comic_text('MƏZAHİR', 170, YEL, stroke=13, shadow=13, rot=-7), 330, 1240)
    paste_c(im, comic_text('DAYI', 170, WHT, stroke=13, shadow=13, rot=-7), 300, 1420)
    paste_c(im, burst('ŞEİR!', 80, fill=YEL, txtcol=RED, rot=12, w=300), 900, 560)
    paste_c(im, esticker('1f342', 120, -15), 120, 560); paste_c(im, esticker('1f4dc', 130, 10), 930, 900)
    paste_c(im, burst('HA-HA!', 60, fill=CY, txtcol=BLK, rot=-10, w=300), 220, 1680)
    border(im)
    return im
# 4 — deluxe comic magazine
def n4():
    im = rays(W, H, (30, 18, 70), (52, 30, 110), n=40, cx=540, cy=1150)
    d = ImageDraw.Draw(im)
    top = halftone(W, 640, RED, (200, 20, 40), step=22, rmax=6, cy=1.0); im.paste(top, (0, 0))
    d = ImageDraw.Draw(im); d.rectangle([0, 630, W, 650], fill=BLK+(255,)); d.rectangle([0, 650, W, 662], fill=YEL+(255,))
    plogos(im, 290)
    paste_c(im, comic_text('MƏZAHİR DAYI', 150, YEL, stroke=12, shadow=12), 540, 500)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([100, 760, 980, 1640], fill=(255, 200, 80, 140)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    speedlines(im, 540, 1150, col=(255, 220, 120), a=60)
    bottom_person(im, R, 1000, 600, H)
    bottom_person(im, L, 430, 210, H, outline=12)
    paste_c(im, label('1-Cİ BÖLÜM · NOYABR', 42, WHT, RED, rot=-5), 230, 760)
    paste_c(im, label('TRAKTOR · JAECOO · GİLAVAR', 36, YEL, BLK, rot=3), 700, 760)
    paste_c(im, burst('YENİ ŞEİR!', 70, fill=YEL, txtcol=BLK, rot=-12, w=400), 860, 1100)
    paste_c(im, esticker('1f4dc', 130, -10), 120, 1000)
    paste_c(im, burst('HA-HA!', 56, fill=CY, txtcol=BLK, rot=12, w=290), 430, 1580)
    border(im, YEL, 12)
    return im
outs = {}
for k, fn in [('1', n1)]:
    outs[k] = fn()
for k, v in outs.items(): v.convert('RGB').save(f'{T}/comic2_{k}.jpg', quality=93)
print('ok')
