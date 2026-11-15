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
voice *= np.interp(t, [0, 84.9, 85.1, DUR], [1, 1, db(1.5), db(1.5)])[:, None]
ve = sg.sosfiltfilt(sg.butter(1, 4, 'low', fs=SR, output='sos'), np.abs(voice).max(1))
duck = sg.sosfiltfilt(sg.butter(1, 1.5, 'low', fs=SR, output='sos'), np.clip(ve / .03, 0, 1))


V = lambda x: x + OFF
# ---- music: Lightless Dawn ----
mus = seg('dl/music/Lightless Dawn.mp3', 0.0, DUR + 1)[:N].astype(np.float64)
mus = mus / rms(mus[SR * 5:SR * 90])
pts = [(0, -60), (.3, -32), (3.4, -32), (3.62, -30), (9.0, -30), (9.06, -37), (12.2, -32.5), (32.4, -32.5), (32.7, -30.5), (50.0, -31),
       (55.6, -32), (66.7, -32), (66.9, -28), (70.6, -28), (70.7, -60), (72.2, -60), (73.4, -34), (78.0, -31), (84.4, -35), (86.4, -38),
       (88.0, -27), (89.8, -27), (DUR - .1, -60), (DUR, -60)]
menv = np.interp(t, [p[0] for p in pts], db([p[1] for p in pts]))
mus_bus = mus * (menv * db(-6.5 * np.clip(duck, 0, 1) + 4))[:, None]

fx = np.zeros((N, 2))
room = lp(seg(X + '2135.flac', 5, DUR), 1200)               # hollow room tone, under every "present" scene
wind = lp(seg(X + '1714.flac', 10, DUR), 1500)
pres = np.interp(t, [0, 3.5, 3.62, 9.0, 9.06, 32.0, 32.7, 50.15, 55.7, 66.85, 66.9, 70.66, 70.68, 82.0, 86.4, 88.0, DUR],
                    [1, 1, .15, .15, 1, 1, .15, .15, 1, 1, .1, .1, 1.25, 1, .6, 0, 0])
place(fx, room * pres[:len(room), None], 0, -37, fi=.02, fo=1.0)
place(fx, wind * pres[:len(wind), None], 0, -40, fi=.02, fo=1.0)
# --- present: footsteps, door ---
steps = lp(load_audio(X + '0514.flac'), 4500)
place(fx, steps[:int(3.5 * SR)], 0.05, -33, fi=.02, fo=.2)
place(fx, lp(load_audio(X + '3206.flac'), 5000)[:int(2.6 * SR)], 0.6, -30, fi=.01, fo=.6)        # door creak
place(fx, steps[int(3 * SR):int(7 * SR)], 22.6, -34, fi=.2, fo=.3)                                 # walking in
place(fx, steps[int(.5 * SR):int(6.2 * SR)], 26.7, -35, fi=.2, fo=.8)
place(fx, lp(seg(X + '0527.wav' if False else X + '1081.flac', 30, 13.6), 1500), 9.05, -44, fi=.05, fo=.6)  # muffled outside
# --- past: water, murmur ---
water = lp(seg(X + '0913.wav', 3, 30), 7000)
murmur = lp(hp(seg(X + '3542.flac', 20, 30), 200), 2600)
place(fx, water[:int(5.5 * SR)], 3.55, -33, fi=.35, fo=.05)
place(fx, murmur[:int(5.5 * SR)], 3.55, -36, fi=.45, fo=.05)
place(fx, murmur[int(5 * SR):int(10 * SR)], 29.0, -42, fi=2.5, fo=.3)                              # life heard at the end of the corridor
place(fx, lp(seg(X + '1081.flac', 60, 3.0), 6000), 32.55, -31, fi=.4, fo=.6)                       # fountain hall
place(fx, water[int(6 * SR):int(24 * SR)], 32.6, -37, fi=.4, fo=1.0)
place(fx, murmur[int(10 * SR):int(28 * SR)], 32.6, -38, fi=.5, fo=1.0)
place(fx, lp(seg(X + '1384.flac', 2, 2.5), 6000), 37.3, -34, fi=.05, fo=.5)                        # vannalar: water drops
place(fx, lp(seg(X + '0642.wav', 40, 8), 2400), 45.85, -41, fi=1.0, fo=.4)
# return to silence: life fades across the courtyard shot
place(fx, murmur[int(2 * SR):int(8 * SR)], 50.1, -39, fi=.05, fo=5.4)
place(fx, water[int(2 * SR):int(8 * SR)], 50.1, -38, fi=.05, fo=5.4)
# --- decay: drips, pigeons ---
drip = lp(seg(X + '1386.flac', 0, 21), 5000)
place(fx, drip[:int(10 * SR)], 56.0, -40, fi=.3, fo=.6)
place(fx, lp(load_audio(X + '0476.wav'), 5000)[:int(3.2 * SR)], 61.1, -34, fi=.05, fo=1.0)        # pigeons under the broken roof
# --- işıq, su, səs, insanlar: life floods back, then is cut ---
place(fx, water[int(10 * SR):int(13.8 * SR)], 66.85, -32, fi=.2, fo=.02)
place(fx, lp(seg(X + '0507.wav', 4, 3.1), 6000), 67.58, -33, fi=.1, fo=.02)
place(fx, murmur[int(14 * SR):int(16.6 * SR)], 68.1, -32, fi=.15, fo=.02)
place(fx, lp(seg(X + '0642.wav', 70, 1.8), 3500), 68.88, -31, fi=.15, fo=.02)
fx[int(70.68 * SR):int(70.70 * SR)] *= np.linspace(1, 0, int(.02 * SR))[:, None]
fx[int(70.70 * SR):int(72.0 * SR)] *= 0          # silence, apart from the room (added below)
place(fx, drip[int(11 * SR):int(16 * SR)], 71.2, -41, fi=.05, fo=1.5)                              # a single drip in the silence
place(fx, room[int(20 * SR):int(28 * SR)], 70.69, -38, fi=.05, fo=.5)
# split screen: the past whispers above the present
place(fx, water[int(16 * SR):int(20.6 * SR)], 73.55, -42, fi=.6, fo=.8)
place(fx, murmur[int(18 * SR):int(22.6 * SR)], 73.55, -44, fi=.6, fo=.8)
# outside again
place(fx, lp(seg(X + '1081.flac', 100, 8.0), 1800), 78.15, -43, fi=.6, fo=2.5)
wh = load_audio(X + '1795.flac'); wh = lp(sg.resample(wh, int(len(wh) * 1.7)), 2200)
for tt, lv in [(3.3, -31), (32.3, -32), (66.65, -34), (84.3, -27)]:
    place(fx, wh, tt, lv, fi=.05, fo=.3)
def thump(d=2.6, f0=62, f1=34):
    n = int(d * SR); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.2)
    body = lp(np.random.default_rng(3).normal(0, 1, n)[:, None], 180)[:, 0] * np.exp(-tt * 7) * .5
    a = (s + body) * np.minimum(tt / .006, 1)
    return np.stack([a, a], 1)
place(fx, thump(2.0, 50, 32), 9.05, -18, fi=.002, fo=.5, norm=False)      # back to today
place(fx, thump(2.4), V(12.62), -16, fi=.002, fo=.5, norm=False)          # «Fantaziya»
place(fx, thump(2.6, 52, 30), V(55.93), -15, fi=.002, fo=.5, norm=False)  # 2012
place(fx, thump(3.0, 48, 28), 70.68, -12, fi=.002, fo=.5, norm=False)     # indi səssizdir
place(fx, thump(3.0, 50, 30), 88.6, -17, fi=.002, fo=.5, norm=False)      # logo
fx *= db(-3 * duck)[:, None]
for name, b in [('voice', voice), ('music', mus_bus), ('sfx', fx)]:
    wf.write(f'stem_{name}.wav', SR, np.clip(b, -1, 1).astype(np.float32))
wf.write('premix.wav', SR, (voice + mus_bus + fx).astype(np.float32))
st = {'voice': voice, 'music': mus_bus, 'sfx': fx}
print('t voice music sfx')
for tt in range(0, int(DUR), 3):
    print(tt, *[round(20 * np.log10(rms(st[n][tt * SR:(tt + 3) * SR]) + 1e-9)) for n in st])
