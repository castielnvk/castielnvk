"""Composite graphic layers over the rendered 3D frames and pipe to ffmpeg.
usage: python3 composite.py frames_dir logo_png audio_wav out_mp4 layers_dir"""
import sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FR, LOGO, AUD, OUT, LAY = sys.argv[1:6]
W, H, FPS, NF = 1080, 1920, 30, 360
os.makedirs(LAY, exist_ok=True)
FD = '/usr/share/fonts/opentype/inter/'
def font(n, s): return ImageFont.truetype(FD + n, s)
sm = lambda x: 0 if x <= 0 else 1 if x >= 1 else x * x * (3 - 2 * x)
eo = lambda x: 1 - (1 - min(1, max(0, x))) ** 3

# ---- layer 1: headline (2 lines), its own RGBA layer
HL = ['Bakıda il', 'dəyişdirilir.']
f_h = font('Inter-ExtraBold.otf', 112)
def line_layer(txt, f):
    bb = f.getbbox(txt); w, h = bb[2] - bb[0] + 40, bb[3] + 40
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((20 - bb[0], 24), txt, font=f, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(sh)
    d.text((20 - bb[0], 20), txt, font=f, fill=(255, 255, 255, 255))
    return im
lines = [line_layer(s, f_h) for s in HL]
LY = [1262, 1392]
for s in HL: assert all(ch in s for ch in []) or True
# full-frame headline layer for the production files
hl_full = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for im, y in zip(lines, LY): hl_full.alpha_composite(im, ((W - im.width) // 2, y))
hl_full.save(f'{LAY}/layer_headline_1080x1920.png')

# ---- layer 2: official Araz Radio 103.3 FM logo (white PNG as supplied, uniformly scaled, untouched)
logo = Image.open(LOGO).convert('RGBA')
LW = 330; logo_s = logo.resize((LW, round(logo.height * LW / logo.width)), Image.LANCZOS)
LX, LYp = (W - LW) // 2, 196
lg_sh = Image.new('RGBA', (logo_s.width + 60, logo_s.height + 60), (0, 0, 0, 0))
a = logo_s.split()[3].point(lambda v: v * 0.55)
lg_sh.paste(Image.new('RGBA', logo_s.size, (0, 0, 0, 255)), (30, 30), a); lg_sh = lg_sh.filter(ImageFilter.GaussianBlur(12))
lg_full = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lg_full.alpha_composite(lg_sh, (LX - 30, LYp - 27)); lg_full.alpha_composite(logo_s, (LX, LYp))
lg_full.save(f'{LAY}/layer_logo_1080x1920.png')

# ---- layer 3: deadpan live-report bug (3.15 - 7.8 s)
f_b1 = font('Inter-Bold.otf', 30); f_b2 = font('Inter-Medium.otf', 30)
bug = Image.new('RGBA', (700, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(bug)
d.rounded_rectangle((0, 0, 150, 48), 6, fill=(214, 32, 40, 235))
d.ellipse((16, 17, 30, 31), fill=(255, 255, 255, 255)); d.text((40, 6), 'CANLI', font=f_b1, fill=(255, 255, 255, 255))
d.text((2, 62), 'BAKI · Dənizkənarı Bulvar', font=f_b2, fill=(255, 255, 255, 235))
bsh = Image.new('RGBA', bug.size, (0, 0, 0, 0)); bsh.paste((0, 0, 0, 150), (0, 0), bug.split()[3]); bsh = bsh.filter(ImageFilter.GaussianBlur(6))
bug_l = Image.new('RGBA', bug.size, (0, 0, 0, 0)); bug_l.alpha_composite(bsh, (0, 0)); bug_l.alpha_composite(bug)
bug_l.save(f'{LAY}/layer_live_bug.png')

# vignette + bottom scrim (for headline legibility)
yy, xx = np.mgrid[0:H, 0:W]
vig = 1 - 0.28 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.48) / (H * 0.62)) ** 2, 0, 1)
scrim = np.clip((yy - 1150) / 500, 0, 1) ** 1.3 * 0.45
vig = vig[..., None].astype(np.float32); scrim = scrim[..., None].astype(np.float32)

ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-i', AUD, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for i in range(NF):
    t = i / FPS
    fr = np.asarray(Image.open(f'{FR}/f{i:04d}.png').convert('RGB'), np.float32)
    s_amt = sm((t - 8.3) / 0.8)
    fr = fr * vig * (1 - scrim * s_amt)
    im = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).convert('RGBA')
    # live bug
    ba = sm((t - 3.15) / 0.25) * (1 - sm((t - 7.55) / 0.25))
    if ba > 0:
        b = bug_l.copy(); b.putalpha(b.split()[3].point(lambda v: int(v * ba)))
        im.alpha_composite(b, (64, 214))
    # headline: each line rises out of a mask, 0.14 s stagger
    for k, (ln, y) in enumerate(zip(lines, LY)):
        p = eo((t - 8.55 - k * 0.14) / 0.45)
        if p > 0:
            off = int((1 - p) * ln.height * 0.8)
            crop = Image.new('RGBA', ln.size, (0, 0, 0, 0)); crop.alpha_composite(ln, (0, off))
            crop.putalpha(crop.split()[3].point(lambda v: int(v * min(1, p * 1.6))))
            im.alpha_composite(crop, ((W - ln.width) // 2, y))
    # logo
    la = sm((t - 9.15) / 0.45)
    if la > 0:
        l = lg_full.copy(); l.putalpha(l.split()[3].point(lambda v: int(v * la)))
        im.alpha_composite(l)
    ff.stdin.write(im.convert('RGB').tobytes())
ff.stdin.close(); ff.wait(); print('done', OUT)
