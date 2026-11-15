import numpy as np, cv2
from PIL import Image
import render as R
from render import W, H, g_past, g_now, glow, text_img, blit, logo_img, GOLD, IVORY, F_PLAYB, F_PLAYI, F_INTB, VIG, GR
def frame(clip, t, g, z, cx, cy, wout, hout):
    x = R.CL[clip][int(t * 24)].astype(np.float32) / 255.
    x = g(x); sh, sw = x.shape[:2]; sc = max(wout / sw, hout / sh) * z
    hw, hh = wout / sc / 2, hout / sc / 2
    px = min(max(cx * sw, hw), sw - hw); py = min(max(cy * sh, hh), sh - hh)
    M = np.array([[sc, 0, wout / 2 - px * sc], [0, sc, hout / 2 - py * sc]], np.float32)
    y = cv2.warpAffine(x, M, (wout, hout), flags=cv2.INTER_LANCZOS4)
    return np.clip(y + (y - cv2.GaussianBlur(y, (0, 0), 1.6)) * .5, 0, 1)
top = frame(10, 6.0, g_past, 1.0, .5, .42, W, 1000)
s = cv2.GaussianBlur(np.maximum(cv2.resize(top, (W // 4, 250)) - .55, 0), (0, 0), 9)
top = np.clip(top + cv2.resize(s, (W, 1000)) * np.array([1, .82, .55], np.float32) * 1.1, 0, 1)
bot = frame(11, 1.5, g_now, 1.0, .5, .5, W, 1040)
fr = np.zeros((H, W, 3), np.float32); fr[:1000] = top
yy = np.arange(H, dtype=np.float32); xx = np.arange(W, dtype=np.float32)[None, :, None]
m = np.clip((yy - 880) / 120, 0, 1)[:, None, None]
cb = np.zeros_like(fr); cb[880:] = bot
fr = fr * (1 - m) + cb * m
fr *= 1 - .82 * np.exp(-((yy - 1010) / 310) ** 2)[:, None, None]
fr *= (1 - .45 * VIG)[..., None]
fr *= 1 - (np.clip((300 - yy) / 300, 0, 1) * .45)[:, None, None]
fr *= 1 - .6 * np.exp(-((yy[:, None, None] - 495) / 95) ** 2 - ((xx - 540) / 330) ** 2)
fr += GR[0] * .022; fr = np.clip(fr, 0, 1)
def ctext(txt, font, size, col, y, track=0):
    ti = text_img(txt, font, size, col, track, shadow=.85, blur=14); blit(fr, ti, (W - ti['w']) / 2, y)
ctext('BAKININ MƏRKƏZİNDƏ', F_INTB, 36, GOLD, 706, track=18)
fr[772:775, 440:640] = np.array(GOLD, np.float32) / 255.
ctext('«FANTAZİYA»', F_PLAYB, 128, IVORY, 812, track=2)
ctext('NƏ OLDU?', F_PLAYB, 150, GOLD, 990, track=3)
ctext('Dəbdəbədən səssizliyə', F_PLAYI, 62, IVORY, 1196)
lg = logo_img(360); blit(fr, lg, (W - 360) / 2, 452, .97)
Image.fromarray((fr * 255 + .5).astype(np.uint8)).save('Fantaziya_Kadr_Xarici_thumbnail.jpg', quality=93)
