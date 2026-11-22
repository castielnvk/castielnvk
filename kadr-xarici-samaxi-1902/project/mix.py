"""Şamaxı 1902 — no voice: music ("Dark Walk", last 50 s of the track) + sound design."""
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wf
from common import load_audio, DUR
SR = 48000; N = int(DUR * SR); t = np.arange(N) / SR
def db(x): return 10 ** (np.asarray(x) / 20)
def rms(a): return np.sqrt((a ** 2).mean() + 1e-12)
def lp(a, f, order=2): return sg.sosfilt(sg.butter(order, f, 'low', fs=SR, output='sos'), a, axis=0)
def hp(a, f, order=2): return sg.sosfilt(sg.butter(order, f, 'high', fs=SR, output='sos'), a, axis=0)
def seg(path, s, d):
    a = load_audio(path); return a[int(s * SR):int((s + d) * SR)].copy()
def place(bus, a, t0, level_db, fi=.4, fo=.6, norm=True):
    a = a.astype(np.float64); a = a / rms(a) * db(level_db) if norm else a * db(level_db)
    n = len(a); e = np.ones(n)
    k = max(int(fi * SR), 1); e[:k] = np.linspace(0, 1, k) ** 1.5
    k = max(int(fo * SR), 1); e[-k:] *= np.linspace(1, 0, k) ** 1.5
    i = int(t0 * SR); a = (a * e[:, None])[:max(0, N - i)]
    bus[i:i + len(a)] += a
def thump(d=2.6, f0=62, f1=34):
    n = int(d * SR); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.2)
    body = lp(np.random.default_rng(3).normal(0, 1, n)[:, None], 180)[:, 0] * np.exp(-tt * 7) * .5
    a = (s + body) * np.minimum(tt / .006, 1)
    return np.stack([a, a], 1)
X = 'dl/sfx/'
# ---- music ----
MUS_OFF = 31.0
mus = seg('dl/music/Dark Walk.mp3', MUS_OFF, DUR)[:N].astype(np.float64)
mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
mus = mus / rms(mus[:SR * 30])
pts = [(0, -40), (.12, -21), (9, -21), (12, -19.5), (20, -20), (20.6, -22.5), (27, -23), (27.5, -24.5), (33, -23.5),
       (36.6, -23), (37.8, -18.5), (39, -19), (45, -18.5), (48, -18), (DUR, -18)]
music = mus * db(np.interp(t, [p[0] for p in pts], [p[1] for p in pts]))[:, None]
# ---- sound design ----
fx = np.zeros((N, 2))
wind_v = lp(seg(X + '0625.flac' if False else X + '0625.wav', 5, DUR), 2600) if False else None
def wind(path, s, d): return lp(seg(path, s, d), 2600)
import os
W1 = X + ('0625.wav' if os.path.exists(X + '0625.wav') else '0625.flac')
W2 = X + ('0147.wav' if os.path.exists(X + '0147.wav') else '0147.flac')
# opening: hit + deep rumble, POV footsteps on gravel
place(fx, thump(3.2, 58, 28), 0.0, -12, fi=.002, fo=.8, norm=False)
place(fx, lp(seg(X + '3114.flac', 0.0, 4.4), 160, 4), 0.0, -20, fi=.01, fo=1.2)
place(fx, lp(seg(X + '1117.flac', 6, 4.05), 4500), 0.05, -34, fi=.2, fo=.15)
place(fx, wind(W1, 10, DUR - 4), 3.6, -36, fi=1.0, fo=3.0)                     # winter wind through the ruins, whole film
# 12:50 — the moment: rumble, falling stones (no screams, no collapse effects over people)
place(fx, thump(3.4, 52, 26), 5.15, -14, fi=.002, fo=.8, norm=False)
place(fx, lp(seg(X + '3113.flac', 0.0, 4.6), 170, 4), 5.1, -21, fi=.05, fo=1.6)
place(fx, lp(seg(X + '1022.flac', 3.0, 3.0), 3500), 5.5, -33, fi=.05, fo=1.2)
# scale of destruction: stones shifting, soft whooshes on cuts, a riser into the buildings
place(fx, lp(seg(X + '1635.flac', 10, 6.0), 2800), 9.0, -38, fi=.6, fo=1.0)
wh = load_audio(X + '1795.flac'); wh = lp(sg.resample(wh, int(len(wh) * 1.7)), 2000)
for tt, lv in [(8.75, -33), (11.75, -34), (14.75, -33), (47.45, -29)]:
    place(fx, wh, tt, lv, fi=.05, fo=.3)
place(fx, thump(2.2, 50, 30), 12.55, -19, fi=.002, fo=.5, norm=False)        # 125
n = int(1.2 * SR); r = lp(np.random.default_rng(5).normal(0, 1, (n, 2)), 380) * (np.linspace(0, 1, n) ** 3)[:, None]
place(fx, r, 13.8, -34, fi=.01, fo=.05)
place(fx, lp(load_audio(X + '3206.flac'), 4000)[:int(2.2 * SR)], 17.8, -36, fi=.05, fo=.8)   # timber creak
place(fx, lp(seg(X + '1117.flac', 20, 2.6), 4000), 15.1, -40, fi=.2, fo=.4)  # man walking past the mosque
# human losses: strip back — only wind and a faint settling of stones
place(fx, lp(seg(X + '1022.flac', 12, 3.0), 2500), 20.4, -42, fi=.2, fo=1.5)
# winter shelters: colder wind, canvas moving, slow steps
place(fx, wind(W2, 20, 6.2), 27.0, -35, fi=.6, fo=1.0)
place(fx, lp(seg(X + '1632.flac', 20, 6.0), 3500), 27.0, -36, fi=.5, fo=1.0)
place(fx, lp(seg(X + '3202.flac', 10, 2.8), 4000), 30.3, -37, fi=.2, fo=.5)
# relief: canvas, footsteps, quieter wind
place(fx, lp(seg(X + '1632.flac', 40, 6.0), 3000), 39.0, -40, fi=.8, fo=1.0)
place(fx, lp(seg(X + '3202.flac', 30, 3.0), 3500), 39.2, -41, fi=.4, fo=.8)
# logo
place(fx, thump(3.0, 50, 30), 47.95, -18, fi=.002, fo=1.0, norm=False)
# the wind is pulled back under the delicate moment and the ending
fx *= np.interp(t, [0, 32.8, 33.4, 38.8, 39.2, 46.6, 48.0, DUR], [1, 1, .45, .45, .8, .8, .25, .15])[:, None]
for name, b in [('music', music), ('sfx', fx)]:
    wf.write(f'stem_{name}.wav', SR, np.clip(b, -1, 1).astype(np.float32))
wf.write('premix.wav', SR, (music + fx).astype(np.float32))
print('t music sfx')
for tt in range(0, int(DUR), 3):
    print(tt, round(20 * np.log10(rms(music[tt * SR:(tt + 3) * SR]) + 1e-9)), round(20 * np.log10(rms(fx[tt * SR:(tt + 3) * SR]) + 1e-9)))
