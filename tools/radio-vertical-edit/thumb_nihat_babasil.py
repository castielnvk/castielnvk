import sys, os
sys.argv = ['x']
import glass_render as G
import compose as C
from engine import *
from premium_grade import premium
from PIL import Image, ImageDraw, ImageFilter
T = os.path.join(BASE, '..', 'thumb')
def panel(t, k):
    im = np.asarray(Image.open(f'{T}/f_{t}.png').convert('RGB'))
    x0 = 90 if k == 'L' else 1031
    return np.ascontiguousarray(im[138:138+756, x0:x0+804])
def crop(p, x0, y0, w, h, ow, oh):
    c = p[y0:y0+h, x0:x0+w]
    return cv2.resize(c, (ow, oh), interpolation=cv2.INTER_LANCZOS4)
Lp = premium(panel('121.0', 'L'), 'L'); Rp = premium(panel('117.0', 'R'), 'R')
dst = G.bg_frame(0)
PW_, PH_ = 1020, 600
LOGO_Y = 322   # inside the 3:4 profile-grid crop (y 240..1680)
tiles = [(crop(Lp, 104, 186, 700, 412, PW_, PH_), 30, 420, (253, 224, 140)),
         (crop(Rp, 104, 40, 700, 412, PW_, PH_), 30, 1080, (125, 211, 252))]
for img, x, y, col in tiles:
    sh, sp = shadow(PW_, PH_, 44, 30, 170)
    blend(dst, np.zeros((sh.shape[0], sh.shape[1], 3), np.float32), sh, x-sp, y-sp)
    blend(dst, img.astype(np.float32), rr_mask(PW_, PH_, 44), x, y)
    g, pad = glow_frame(PW_, PH_, 44, (255, 255, 255), 2, 16)
    rgba_blend(dst, g, x-pad, y-pad)
a_, m_ = C.logo_png('araz_white', 96, 0)
rgba_blend(dst, a_, 52-m_, LOGO_Y-a_.shape[0]/2)
b_, m_ = C.logo_png('show', 132, 0)
rgba_blend(dst, b_, W-52+m_-b_.shape[1], LOGO_Y-b_.shape[0]/2)
# title on dark glass across the seam
f = font(FONT_CAP, 84)
lines = [[('NİYƏ ', WHITE), ('BABASİL', G.GOLD), (' VAR,', WHITE)], [('NƏNƏSİL', G.GOLD), (' YOX?', WHITE)]]
lw = [sum(f.getbbox(t)[2] for t, _ in ln) for ln in lines]
bw, bh = max(lw)+80, 2*100+56
bx, by = W/2-bw/2, 1050-bh/2
G.glass(dst, bx, by, bw, bh, r=40, tint_a=0.62, blur=30, border_a=0.30, shadow_a=0.5)
im = Image.new('RGBA', (int(bw), int(bh)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
yy = 26
for ln, w_ in zip(lines, lw):
    xx = (bw-w_)/2
    for t, col in ln:
        d.text((xx+3, yy+5), t, font=f, fill=(0, 0, 0, 120))
        d.text((xx, yy), t, font=f, fill=col+(255,))
        xx += f.getbbox(t)[2]
    yy += 100
rgba_blend(dst, np.asarray(im), bx, by)
# small glass tag: who is calling
tag = G.tag_content('NİHAT · CANLI ZƏNG', 26, WHITE, '1f4de')
tx, ty = W/2-tag.size[0]/2, LOGO_Y-tag.size[1]/2
G.glass(dst, tx, ty, tag.size[0], tag.size[1], r=tag.size[1]//2, tint_a=0.55)
rgba_blend(dst, np.asarray(tag), tx, ty)
# icon badges
for code, cx, cy in [('1f923', 905, 505), ('1f474', 170, 1225), ('1f475', 910, 1225)]:
    s = 150
    G.glass(dst, cx-s/2, cy-s/2, s, s, r=s//2, tint_a=0.45)
    paste_center(dst, emoji(code, 94, 0), cx, cy)
out = np.clip(dst, 0, 255).astype(np.uint8)
Image.fromarray(out).save(f'{T}/thumb_nihat_babasil.png')
Image.fromarray(out).convert('RGB').save(f'{T}/thumb_nihat_babasil.jpg', quality=95)
print('ok')
