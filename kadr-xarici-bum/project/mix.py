import numpy as np, subprocess, scipy.signal as sg, scipy.io.wavfile as wf
from common import load_audio, OFF, DUR
SR = 48000; N = int(DUR * SR)
def db(x): return 10 ** (x / 20)
def rms(a): return np.sqrt((a ** 2).mean() + 1e-12)
def lp(a, f, order=2):
    return sg.sosfilt(sg.butter(order, f, 'low', fs=SR, output='sos'), a, axis=0)
def hp(a, f, order=2):
    return sg.sosfilt(sg.butter(order, f, 'high', fs=SR, output='sos'), a, axis=0)
def seg(path, s, d):
    a = load_audio(path); return a[int(s * SR):int((s + d) * SR)].copy()
def place(bus, a, t, level_db, fi=.4, fo=.6, norm=True, env=None):
    a = a.astype(np.float64)
    if norm: a = a / rms(a) * db(level_db)
    else: a = a * db(level_db)
    n = len(a); e = np.ones(n)
    k = int(fi * SR); e[:k] = np.linspace(0, 1, k) ** 1.5
    k = int(fo * SR); e[-k:] *= np.linspace(1, 0, k) ** 1.5
    if env is not None: e *= np.interp(np.arange(n) / SR, [p[0] for p in env], [db(p[1]) for p in env])
    i = int(t * SR); a = (a * e[:, None])[:max(0, N - i)]
    bus[i:i + len(a)] += a
X = 'dl/sfx/'
# ---- voice ----
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'src/vo.mp3', '-af',
    'highpass=f=70,equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=1.2,deesser=i=0.25,'
    'acompressor=threshold=-22dB:ratio=2:attack=12:release=160:makeup=1.5,aresample=48000', '-ac', '2', 'vo_p.wav'], check=True)
vo = load_audio('vo_p.wav').astype(np.float64)
vo = vo / rms(vo[np.abs(vo).max(1) > .01]) * db(-19)
voice = np.zeros((N, 2)); i = int(OFF * SR); voice[i:i + len(vo)] = vo[:N - i]
# intimate close for the whisper: tiny lift
t = np.arange(N) / SR
voice *= np.interp(t, [0, 78.2, 78.5, 85], [1, 1, db(1.5), db(1.5)])[:, None]

# ---- music ----
mus = seg('dl/music/Echoes of Time v2.mp3', 9.0, DUR + 1)[:N].astype(np.float64)
mus = mus / rms(mus[SR * 10:SR * 60]) 
menv = np.interp(t, [0, 1.2, 30.9, 31.75, 32.05, 33, 60, 72.0, 77.8, 80.0, 81.4, 83.0, DUR - .1, DUR],
                 [db(-60), db(-31), db(-31), db(-40), db(-28), db(-31), db(-33), db(-35), db(-41), db(-40), db(-27), db(-28), db(-60), db(-60)])
# sidechain ducking from voice envelope
ve = np.abs(voice).max(1); k = int(.05 * SR)
ve = sg.sosfiltfilt(sg.butter(1, 4, 'low', fs=SR, output='sos'), np.maximum(ve, 0))
duck = np.clip(ve / .03, 0, 1)
duck = sg.sosfiltfilt(sg.butter(1, 1.5, 'low', fs=SR, output='sos'), duck)
mus_bus = mus * (menv * db(-6.5 * np.clip(duck, 0, 1) + 4))[:, None]

# ---- sfx / ambience ----
fx = np.zeros((N, 2))
proj = lp(load_audio(X + '0065.flac'), 5500)
proj_run = proj[int(8 * SR):]
place(fx, proj[:int(4.4 * SR)], 2.05, -33, fi=.25, fo=.5)                       # hook: projector
place(fx, lp(seg(X + '0979.wav', 4, 14), 3500), 6.1, -37, fi=1.0, fo=1.2)      # horse steps, old street
place(fx, lp(seg(X + '0527.wav', 10, 14), 2500), 6.1, -39, fi=1.0, fo=1.2)     # street air
place(fx, lp(seg(X + '3346.flac', 20, 7.0), 3500), 24.6, -37, fi=.5, fo=.9)    # passage crowd
place(fx, proj[:int(5.9 * SR)], 31.95, -34, fi=.05, fo=.3)                     # 1907: projector starts
place(fx, lp(seg(X + '0642.wav', 30, 5.9), 4000), 31.95, -36, fi=.3, fo=.5)    # crowd at the cinema door
place(fx, proj_run[:int(6.7 * SR)], 37.6, -30, fi=.25, fo=.4)                  # inside the hall
place(fx, lp(seg(X + '0642.wav', 60, 6.7), 2500), 37.6, -42, fi=.3, fo=.4)
place(fx, proj_run[int(7 * SR):int(10.3 * SR)], 44.05, -36, fi=.3, fo=.8)
place(fx, lp(seg(X + '0642.wav', 80, 3.3), 4000), 44.05, -37, fi=.3, fo=.8)
place(fx, lp(seg(X + '3348.flac', 40, 5.7), 4500), 47.15, -36, fi=.5, fo=.7)   # soviet department store
place(fx, lp(seg(X + '1714.flac', 20, 9.0), 1800), 52.5, -38, fi=1.0, fo=.5)   # airy hall under the glass roof
place(fx, lp(seg(X + '3346.flac', 60, 8.8), 1500), 52.5, -43, fi=1.0, fo=.4)
place(fx, lp(seg(X + '0646.wav', 30, 2.0), 1400), 61.25, -38, fi=.15, fo=.3)   # covered: muffled modern interior
place(fx, lp(seg(X + '0526.wav', 20, 3.5), 5000), 62.95, -36, fi=.3, fo=.4)    # today, street
place(fx, lp(seg(X + '0646.wav', 50, 3.2), 2200), 66.2, -38, fi=.3, fo=1.2)
place(fx, proj_run[int(12 * SR):int(16.6 * SR)], 67.7, -38, fi=1.5, fo=.8)     # ghost of the cinema
place(fx, lp(seg(X + '0526.wav', 40, 4.6), 4000), 73.2, -38, fi=.3, fo=2.5)
# whooshes (soft, low-passed, slowed)
wh = load_audio(X + '1795.flac'); 
wh = lp(sg.resample(wh, int(len(wh) * 1.7)), 2200)
for tt, lv in [(1.75, -27), (71.65, -31), (72.3, -32), (72.85, -31), (77.75, -27)]:
    place(fx, wh, tt, lv, fi=.05, fo=.3)
# low impacts (synthesised sub thump + soft body)
def thump(d=2.6, f0=62, f1=34, lvl=1.0):
    n = int(d * SR); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.2)
    body = lp(np.random.default_rng(3).normal(0, 1, n)[:, None], 180)[:, 0] * np.exp(-tt * 7) * .5
    a = (s + body) * np.minimum(tt / .006, 1)
    return np.stack([a, a], 1) * lvl
place(fx, thump(), 2.22, -17, fi=.002, fo=.5, norm=False)
place(fx, thump(3.2), 31.98, -11, fi=.002, fo=.5, norm=False)
place(fx, thump(2.4, 55, 30), 61.3, -13, fi=.002, fo=.5, norm=False)
place(fx, thump(3.0, 50, 30), 81.05, -17, fi=.002, fo=.5, norm=False)
# riser before 1907: low-passed swell
n = int(1.3 * SR); r = lp(np.random.default_rng(5).normal(0, 1, (n, 2)), 500) * (np.linspace(0, 1, n) ** 3)[:, None]
place(fx, r, 30.35, -30, fi=.01, fo=.04)
# sfx duck slightly under voice
fx *= db(-3 * duck)[:, None]

for name, b in [('voice', voice), ('music', mus_bus), ('sfx', fx)]:
    wf.write(f'stem_{name}.wav', SR, np.clip(b, -1, 1).astype(np.float32))
    print(name, 'rms dB', round(20 * np.log10(rms(b)), 1), 'peak', round(np.abs(b).max(), 3))
wf.write('premix.wav', SR, (voice + mus_bus + fx).astype(np.float32))
