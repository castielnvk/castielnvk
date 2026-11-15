# Procedural, horizontally tileable textures for the Araz FM lower-third film.
import numpy as np
from PIL import Image, ImageFilter

def pnoise(h, w, beta, seed, ax=1.0, ay=1.0):
    """Periodic (tileable) 1/f^beta noise via FFT; ax/ay stretch features along x/y."""
    rng = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None] * h * ay
    fx = np.fft.fftfreq(w)[None, :] * w * ax
    f = np.sqrt(fx ** 2 + fy ** 2); f[0, 0] = 1
    spec = (rng.normal(size=(h, w)) + 1j * rng.normal(size=(h, w))) / f ** beta
    spec[0, 0] = 0
    n = np.fft.ifft2(spec).real
    return (n - n.min()) / (n.max() - n.min())

def grade(v, stops):
    v = np.clip(v, 0, 1)[..., None]; out = np.zeros(v.shape[:2] + (3,))
    for (a, ca), (b, cb) in zip(stops[:-1], stops[1:]):
        m = (v >= a) & (v <= b); tt = (v - a) / (b - a)
        out = np.where(m, np.array(ca) + (np.array(cb) - np.array(ca)) * tt, out)
    return out

# 1. brushed teal metal (dial faceplate) 2048x216
H, W = 216, 2048
streak = pnoise(H, W, 1.1, 1, ax=6.0, ay=0.02)          # long horizontal brush lines
soft = pnoise(H, W, 2.6, 2)
v = 0.62 * streak + 0.38 * soft
img = grade(v, [(0, (5, 58, 66)), (0.5, (9, 93, 106)), (1, (30, 132, 146))])
y = np.linspace(0, 1, H)[:, None, None]
img = img * (1.12 - 0.38 * y) + 14 * np.exp(-((y - 0.12) / 0.07) ** 2)
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save('metal.jpg', quality=93)

# 2. water: dark base + two caustic layers (drawn additively, drifting against each other)
H, W = 432, 2048
base = pnoise(H, W, 2.4, 3, ax=0.6, ay=1.6)
img = grade(base, [(0, (2, 30, 36)), (0.55, (7, 78, 90)), (1, (20, 122, 136))])
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save('water_base.jpg', quality=92)
for k, seed in enumerate((11, 23)):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    n1 = pnoise(H, W, 3.0, seed) - .5; n2 = pnoise(H, W, 3.0, seed + 50) - .5; n3 = pnoise(H, W, 2.6, seed + 9) - .5
    u = xx / 128 + 2.6 * n1 + (k * .37); v = yy / 54 + 2.6 * n2
    c1 = (1 - np.abs(np.sin(np.pi * (u + 1.3 * n3)))) ** 9
    c2 = (1 - np.abs(np.sin(np.pi * (v + 1.3 * n3)))) ** 9
    c3 = (1 - np.abs(np.sin(np.pi * (u * .5 + v * .5 + 2.0 * n3)))) ** 7
    ridge = np.clip(.55 * c1 + .65 * c2 + .5 * c3, 0, 1) * (0.35 + 0.65 * pnoise(H, W, 2.8, seed + 7))
    col = ridge[..., None] * np.array([215, 244, 240])
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
    im.save(f'caustic_{k}.jpg', quality=92)

# 3. stylised land seen from above: field parcels, contour lines
H, W = 432, 2048
n = pnoise(H, W, 2.7, 31); n2 = pnoise(H, W, 2.2, 32)
patch = np.floor(n2 * 7) / 7
v = 0.35 + 0.35 * patch + 0.2 * n
img = grade(v, [(0, (4, 38, 44)), (0.6, (8, 72, 82)), (1, (14, 100, 112))])
contour = (np.abs(((n * 14) % 1) - 0.5) < 0.035)
edges = np.abs(np.gradient(patch)[0]) + np.abs(np.gradient(patch)[1]) > 0
img[contour] = img[contour] * 0.75 + np.array([150, 205, 205]) * 0.25
img[edges] = img[edges] * 0.6 + np.array([190, 225, 220]) * 0.4
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)).save('land.jpg', quality=92)
print('ok')
