#!/usr/bin/env python3
"""Şəkildəki bayrağı dalğalanan (seamless loop) videoya çevirir. 1920x1080, 30 fps."""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1920, 1080, 30, 10
N = FPS * DUR
TAU = 2 * math.pi
OVER = 1.07  # overscan so warped edges never show

src = Image.open(os.path.join(HERE, 'bayraq_orijinal.jpg')).convert('RGB')
sc = max(W / src.width, H / src.height) * OVER
big = src.resize((round(src.width * sc), round(src.height * sc)), Image.LANCZOS)
big = big.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
img = np.asarray(big, np.float32) / 255.0
BH, BW = img.shape[:2]
ox, oy = (BW - W) / 2, (BH - H) / 2

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# waves: (wavelength px, temporal cycles per loop, amplitude px, vertical tilt, phase)
WAVES = [(1150, 1, 14.0, 0.35, 0.0), (620, 2, 7.0, -0.25, 1.7), (380, 3, 3.0, 0.5, 4.1)]


def frame(i):
    p = i / N
    dy = np.zeros((H, W), np.float32)
    dx = np.zeros((H, W), np.float32)
    shade = np.zeros((H, W), np.float32)
    for lam, cyc, amp, tilt, ph in WAVES:
        ph_xy = TAU * ((xx + tilt * yy) / lam - cyc * p) + ph
        s, c = np.sin(ph_xy), np.cos(ph_xy)
        dy += amp * s
        dx += amp * 0.35 * c
        shade += (amp / 14.0) * c  # slope -> light/shadow
    sx = np.clip(xx + ox + dx, 0, BW - 1.001)
    sy = np.clip(yy + oy + dy, 0, BH - 1.001)
    x0, y0 = sx.astype(np.int32), sy.astype(np.int32)
    fx, fy = (sx - x0)[..., None], (sy - y0)[..., None]
    a = img[y0, x0]; b = img[y0, x0 + 1]; c_ = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    out = (a * (1 - fx) + b * fx) * (1 - fy) + (c_ * (1 - fx) + d * fx) * fy
    k = 1.0 + 0.075 * shade[..., None]
    out = out * k + np.maximum(shade[..., None] - 0.9, 0) * 0.05  # soft satin sheen on crests
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


if __name__ == '__main__':
    if '--preview' in sys.argv:
        Image.fromarray(frame(N // 4)).save(os.path.join(HERE, 'preview.jpg'), quality=92)
        sys.exit()
    path = os.path.join(HERE, 'Bayraq_Azerbaycan_Ukrayna_dalgalanan_1920x1080.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
           '-movflags', '+faststart', path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        pr.stdin.write(frame(i).tobytes())
    pr.stdin.close(); pr.wait()
    print('OK', path)
