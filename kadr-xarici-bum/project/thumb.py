import numpy as np, cv2
from PIL import Image
import render as R
from render import W, H, grade, text_img, blit, logo_img, GOLD, IVORY, F_PLAYB, F_PLAYI, F_INTB, F_INTM, VIG, GR, lum
def frame(clip, t, g, z, cx, cy, wout=W, hout=H):
    x = R.CL[clip][int(t * 24)].astype(np.float32) / 255.
    x = grade(x, g); sh, sw = x.shape[:2]; sc = max(wout / sw, hout / sh) * z
    hw, hh = wout / sc / 2, hout / sc / 2
    px = min(max(cx * sw, hw), sw - hw); py = min(max(cy * sh, hh), sh - hh)
    M = np.array([[sc, 0, wout / 2 - px * sc], [0, sc, hout / 2 - py * sc]], np.float32)
    y = cv2.warpAffine(x, M, (wout, hout), flags=cv2.INTER_LANCZOS4)
    return np.clip(y + (y - cv2.GaussianBlur(y, (0, 0), 1.6)) * .5, 0, 1)
top = frame(6, 4.0, 'sepia_soft', 1.5, .5, .36, W, 1100) * 1.12        # projector beam
bot = frame(1, 2.6, 'hook', 1.12, .5, .42, W, 1040) * 1.3               # BUM today
fr = np.zeros((H, W, 3), np.float32)
fr[:1100] = top
yy = np.arange(H, dtype=np.float32)
m = np.clip((yy - 880) / 220, 0, 1)[:, None, None]
canvas_b = np.zeros_like(fr); canvas_b[880:] = bot
fr = fr * (1 - m) + canvas_b * m
# dark band for the title
band = np.exp(-((yy - 1000) / 330) ** 2)[:, None, None]
fr *= 1 - .80 * band
fr *= (1 - .45 * VIG)[..., None]
fr *= 1 - (np.clip((300 - yy) / 300, 0, 1) * .45)[:, None, None]
xx = np.arange(W, dtype=np.float32)[None, :, None]
fr *= 1 - .62 * np.exp(-((yy[:, None, None] - 495) / 95) ** 2 - ((xx - 540) / 330) ** 2)
fr += GR[0] * .022
fr = np.clip(fr, 0, 1)
# warm glow behind title
def ctext(txt, font, size, col, y, track=0, sh=.85):
    ti = text_img(txt, font, size, col, track, shadow=sh, blur=14); blit(fr, ti, (W - ti['w']) / 2, y); return ti
ctext('UNUDULMUŞ TARİX', F_INTB, 34, GOLD, 706, track=16)
fr[772:775, 440:640] = np.array(GOLD, np.float32) / 255.
ctext('BUM-da', F_PLAYB, 210, IVORY, 770)
ctext('KİNOTEATR?', F_PLAYB, 142, GOLD, 1000, track=2)
ctext('100 ildən çox əvvəl…', F_PLAYI, 62, IVORY, 1196)
lg = logo_img(360); blit(fr, lg, (W - 360) / 2, 452, .97)
Image.fromarray((fr * 255 + .5).astype(np.uint8)).save('out_thumb.jpg', quality=93)
