import numpy as np, subprocess, scipy.signal as sg, scipy.io.wavfile as wf
from common import load_audio, OFF, DUR
SR = 48000; N = int(DUR * SR)
def db(x): return 10 ** (np.asarray(x) / 20)
def rms(a): return np.sqrt((a ** 2).mean() + 1e-12)
def lp(a, f, order=2): return sg.sosfilt(sg.butter(order, f, 'low', fs=SR, output='sos'), a, axis=0)
def hp(a, f, order=2): return sg.sosfilt(sg.butter(order, f, 'high', fs=SR, output='sos'), a, axis=0)
def seg(path, s, d):
    a = load_audio(path); return a[int(s * SR):int((s + d) * SR)].copy()
def place(bus, a, t, level_db, fi=.4, fo=.6, norm=True, env=None):
    a = a.astype(np.float64)
    a = a / rms(a) * db(level_db) if norm else a * db(level_db)
    n = len(a); e = np.ones(n)
    k = max(int(fi * SR), 1); e[:k] = np.linspace(0, 1, k) ** 1.5
    k = max(int(fo * SR), 1); e[-k:] *= np.linspace(1, 0, k) ** 1.5
    if env is not None: e *= np.interp(np.arange(n) / SR, [p[0] for p in env], db([p[1] for p in env]))
    i = int(t * SR); a = (a * e[:, None])[:max(0, N - i)]
    bus[i:i + len(a)] += a
X = 'dl/sfx/'
t = np.arange(N) / SR
# ---- voice ----
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'src/vo.mp3', '-af',
    'highpass=f=70,equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=1.2,deesser=i=0.25,'
    'acompressor=threshold=-22dB:ratio=2:attack=12:release=160:makeup=1.5,aresample=48000', '-ac', '2', 'vo_p.wav'], check=True)
vo = load_audio('vo_p.wav').astype(np.float64)
vo = vo / rms(vo[np.abs(vo).max(1) > .01]) * db(-19)
voice = np.zeros((N, 2)); i = int(OFF * SR); voice[i:i + len(vo)] = vo[:N - i]
voice *= np.interp(t, [0, 95.3, 95.55, DUR], [1, 1, db(1.5), db(1.5)])[:, None]
ve = sg.sosfiltfilt(sg.butter(1, 4, 'low', fs=SR, output='sos'), np.abs(voice).max(1))
duck = sg.sosfiltfilt(sg.butter(1, 1.5, 'low', fs=SR, output='sos'), np.clip(ve / .03, 0, 1))

# ---- music: Colorless Aura ----
mus = seg('dl/music/Colorless Aura.mp3', 0.0, DUR + 1)[:N].astype(np.float64)
mus = mus / rms(mus[SR * 5:SR * 90])
menv = np.interp(t, [0, .25, 4.7, 4.95, 9.4, 13.6, 42.9, 43.15, 43.55, 44.0, 64.9, 65.6, 71.8, 76.5, 77.3, 80.5, 94.9, 97.2, 98.9, 100.2, DUR - .1, DUR],
                 db([-34, -30, -30, -37, -31, -30, -30, -44, -44, -28.5, -29.5, -34, -32, -38, -44, -31, -38, -43, -26, -27, -60, -60]))
mus_bus = mus * (menv * db(-6.5 * np.clip(duck, 0, 1) + 4))[:, None]

# ---- tram bell motif (struck gong bell, double strike) ----
b0 = hp(load_audio(X + '2115.flac').astype(np.float64), 250)
def bell(strikes=2, gap=.3, decay=3.0):
    n = int((gap * (strikes - 1) + 4.5) * SR); out = np.zeros((n, 2))
    for k in range(strikes):
        j = int(k * gap * SR); s = b0[:n - j]; out[j:j + len(s)] += s * (1.0 if k == 0 else .85)
    return out * np.exp(-np.arange(n) / SR * decay)[:, None]
fx = np.zeros((N, 2))
# opening: bell from the first frame, tram rolling, hard cut at the modern street
place(fx, bell(2, .28, 2.5), 0.0, -7, fi=.001, fo=.3, norm=False)
place(fx, bell(2, .28, 2.5), 2.75, -12, fi=.001, fo=.3, norm=False)
tr = lp(seg(X + '3374.flac', 1.6, 4.9 - .0), 6000)
place(fx, tr, 0.0, -27, fi=.05, fo=.02)
fx[int(4.9 * SR):] = 0                                   # sound of the past is cut off
place(fx, lp(seg(X + '3030.flac', 20, 4.75), 7000), 4.88, -31, fi=.03, fo=.5)
place(fx, lp(seg(X + '3372.flac', 2.5, 3.4), 1600), 4.9, -38, fi=.2, fo=1.6)   # the past, muffled, fading out on top        # today: traffic
place(fx, lp(seg(X + '1714.flac', 30, 4.5), 1500), 9.5, -36, fi=.6, fo=.6)           # depot: empty air
place(fx, lp(seg(X + '3346.flac', 30, 4.6), 3000), 13.8, -39, fi=.5, fo=.6)          # 1924 crowd
place(fx, bell(2, .3, 2.2), 18.35, -10, fi=.001, fo=.3, norm=False)                  # first tram sets off
place(fx, lp(seg(X + '3538.flac', 1.0, 4.4), 4500), 18.2, -30, fi=.4, fo=.7)
place(fx, lp(seg(X + '0527.wav', 10, 5.3), 2500), 22.2, -38, fi=.6, fo=.6)           # route street air
place(fx, lp(seg(X + '3372.flac', 1.5, 5.2), 4500), 27.4, -30, fi=.6, fo=.8)         # life with trams
place(fx, lp(seg(X + '0526.wav', 20, 9.6), 4000), 27.4, -37, fi=.6, fo=.8)
place(fx, bell(2, .3, 2.4), 32.45, -13, fi=.001, fo=.3, norm=False)
place(fx, lp(seg(X + '0278.wav', 1.0, 4.6), 4500), 32.4, -31, fi=.5, fo=.9)
place(fx, lp(seg(X + '0527.wav', 30, 5.9), 1800), 37.1, -40, fi=.6, fo=.5)
place(fx, lp(seg(X + '3540.flac', 2.0, 5.8), 4500), 43.7, -32, fi=.8, fo=.8)         # soviet tram, change begins
place(fx, lp(seg(X + '2762.flac', 20, 13.0), 4500), 43.7, -38, fi=.8, fo=.8)
place(fx, lp(seg(X + '3030.flac', 60, 7.0), 3500), 49.5, -35, fi=.6, fo=.8)          # buses
place(fx, lp(seg(X + '3373.flac', 5.5, 4.7), 5000), 56.55, -30, fi=.5, fo=.6)        # 1990s tram passes
place(fx, lp(seg(X + '1714.flac', 60, 4.3), 1500), 61.2, -36, fi=.5, fo=.5)          # depot
place(fx, lp(seg(X + '3541.flac', 9.5, 7.0), 4500), 65.5, -31, fi=1.2, fo=.5)        # last line tram approaches
place(fx, lp(seg(X + '3346.flac', 70, 7.0), 3000), 65.5, -40, fi=.8, fo=.5)          # market
# the bells fall silent: tram recedes, one last single strike rings out
place(fx, lp(seg(X + '3539.flac', 12.0, 4.6), 3000), 72.4, -34, fi=.5, fo=3.2)
place(fx, bell(1, .3, 1.5), 75.62, -6, fi=.001, fo=2.5, norm=False)
place(fx, lp(seg(X + '3030.flac', 100, 3.2), 6000), 77.62, -34, fi=.25, fo=.5)       # other transport took their place
# memory photos: soft "print laid down" low thuds are synthesised below; faint echo of the bell
place(fx, lp(bell(2, .3, 2.0), 1800), 86.95, -14, fi=.001, fo=.5, norm=False)        # "hələ də yaşayır": distant bell memory
place(fx, lp(seg(X + '3372.flac', 2.0, 5.5), 2200), 89.3, -37, fi=1.0, fo=2.5)       # bookend tram, far away
wh = load_audio(X + '1795.flac'); wh = lp(sg.resample(wh, int(len(wh) * 1.7)), 2200)
for tt, lv in [(80.3, -31), (83.6, -32), (86.45, -32), (94.75, -27)]:
    place(fx, wh, tt, lv, fi=.05, fo=.3)
def thump(d=2.6, f0=62, f1=34):
    n = int(d * SR); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.2)
    body = lp(np.random.default_rng(3).normal(0, 1, n)[:, None], 180)[:, 0] * np.exp(-tt * 7) * .5
    a = (s + body) * np.minimum(tt / .006, 1)
    return np.stack([a, a], 1)
place(fx, thump(2.4), OFF + 1.24, -14, fi=.002, fo=.5, norm=False)     # 117
place(fx, thump(2.0, 50, 32), 4.9, -18, fi=.002, fo=.5, norm=False)    # cut to today
place(fx, thump(2.2, 48, 30), OFF + 8.25, -15, fi=.002, fo=.5, norm=False)   # 0 KM
place(fx, thump(2.4), OFF + 14.16, -17, fi=.002, fo=.5, norm=False)    # 1924
place(fx, thump(2.6, 52, 30), 43.6, -15, fi=.002, fo=.5, norm=False)   # change begins
place(fx, thump(3.2), OFF + 65.82, -11, fi=.002, fo=.5, norm=False)    # 2004
place(fx, thump(3.0, 50, 30), 98.85, -17, fi=.002, fo=.5, norm=False)  # logo
fx *= db(-3 * duck)[:, None]
for name, b in [('voice', voice), ('music', mus_bus), ('sfx', fx)]:
    wf.write(f'stem_{name}.wav', SR, np.clip(b, -1, 1).astype(np.float32))
wf.write('premix.wav', SR, (voice + mus_bus + fx).astype(np.float32))
st = {'voice': voice, 'music': mus_bus, 'sfx': fx}
print('t voice music sfx')
for tt in range(0, int(DUR), 3):
    print(tt, *[round(20 * np.log10(rms(st[n][tt * SR:(tt + 3) * SR]) + 1e-9)) for n in st])
