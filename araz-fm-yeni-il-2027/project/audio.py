"""Original sound design for the 12 s Baku year-swap film. Writes mix + stems (48 kHz WAV)."""
import numpy as np, wave, sys, os
SR = 48000; DUR = 12.0; N = int(SR * DUR)
rng = np.random.default_rng(2027)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio'
os.makedirs(out, exist_ok=True)
t = np.arange(N) / SR

def lp(x, fc):  # one-pole low-pass, applied twice
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        y = np.empty_like(x); z = 0.0
        for i in range(len(x)):
            z = (1 - a) * x[i] + a * z; y[i] = z
        x = y
    return x
def lpf(x, fc):  # fast FFT brickwall-ish low-pass with soft knee
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hpf(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4); return np.fft.irfft(X, len(x))
def bpf(x, lo, hi): return hpf(lpf(x, hi), lo)
def env(t0, a, d, length=None):
    e = np.zeros(N); i0 = int(t0 * SR)
    n = N - i0 if length is None else min(N - i0, int(length * SR))
    tt = np.arange(n) / SR
    e[i0:i0 + n] = np.minimum(tt / max(a, 1e-4), 1) * np.exp(-np.maximum(tt - a, 0) / d)
    return e
def reverb(x, rt=1.6, mix=0.3, pre=0.02):
    L = int(rt * SR); ir = rng.standard_normal(L) * np.exp(-6.9 * np.arange(L) / L)
    ir = lpf(ir, 5000); ir[:int(pre * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
    wet = np.fft.irfft(np.fft.rfft(x, N + L) * np.fft.rfft(ir, N + L))[:N]
    return x * (1 - mix) + wet * mix
def db(v): return 10 ** (v / 20)
def pan(x, p):  # p in [-1,1]
    a = (p + 1) * np.pi / 4; return np.stack([x * np.cos(a), x * np.sin(a)])

# ---------- AMBIENCE: distant city + Caspian wash + faint wind
city = lpf(np.cumsum(rng.standard_normal(N)) * 0.02, 380); city -= lpf(city, 25)
city = city / np.max(np.abs(city))
sea = np.zeros(N)
for k, (c, p) in enumerate([(1.2, 0), (4.6, .3), (7.9, .1), (10.6, .5)]):
    sea += bpf(rng.standard_normal(N), 250, 2400) * env(c, 1.2, 1.3) * 0.5
wind = bpf(rng.standard_normal(N), 500, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + 1))
cars = np.zeros(N)
for c in (2.0, 6.4, 9.8):  # distant passing traffic
    sw = np.exp(-((t - c) / 1.1) ** 2)
    cars += bpf(rng.standard_normal(N), 120, 900) * sw
amb_l = city * 0.5 + sea * 0.35 + wind * 0.05 + cars * 0.35
amb_r = np.roll(city, 1700) * 0.5 + np.roll(sea, 9000) * 0.35 + np.roll(wind, 4000) * 0.05 + np.roll(cars, 2400) * 0.35
amb = np.stack([amb_l, amb_r]); amb /= np.max(np.abs(amb)); amb *= db(-24)

# crane diesel idle (low, steady), slightly louder in close shots
eng = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) / (i + 1) for i, f in enumerate([31, 62, 93, 124, 155]))
eng *= 1 + 0.25 * np.sin(2 * np.pi * 7.75 * t)  # firing ripple
eng = lpf(eng, 300) / 3
eng_gain = np.interp(t, [0, 3, 3.1, 5.4, 5.5, 8.0, 8.2, 12], [0.5, 0.5, 0.35, 0.35, 0.8, 0.8, 0.25, 0.2])
engine = pan(eng * eng_gain * db(-24), 0.2)

# winch motor under the 7's descent (3.0 - 7.85)
wf = 95 + 18 * np.clip((t - 3) / 4.8, 0, 1)
ph = 2 * np.cumsum(np.pi * wf / SR)
winch = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)) * (np.clip((t - 3.0) / 0.3, 0, 1) * np.clip((7.85 - t) / 0.12, 0, 1))
winch = lpf(winch, 900) * db(-27)
winch = pan(winch, 0.3)

# ---------- CABLE CREAK: stick-slip friction (resonant pulses), at swing extremes of the 6, and in the cable close-up
def creak(t0, length, rate0, rate1, gain, res=(410, 930, 1720)):
    n = int(length * SR); x = np.zeros(N); i0 = int(t0 * SR)
    pos = 0.0; tt = 0
    rates = np.linspace(rate0, rate1, n)
    while tt < n:
        r = rates[tt] * (0.85 + 0.3 * rng.random())
        if i0 + tt < N: x[i0 + tt] = (0.6 + 0.4 * rng.random()) * np.sin(np.pi * tt / n) ** 0.6
        tt += max(1, int(SR / r))
    y = np.zeros(N)
    for f in res:  # resonate the pulse train
        L = int(0.05 * SR); k = np.arange(L) / SR
        ir = np.sin(2 * np.pi * f * k) * np.exp(-k * 60)
        y += np.convolve(x, ir)[:N]
    y += bpf(rng.standard_normal(N), 1500, 5000) * np.convolve(x, np.ones(200) / 200, 'same') * 3
    y = lpf(y, 4200)
    return y / (np.max(np.abs(y)) + 1e-9) * gain
cr = creak(0.32, 0.75, 35, 90, db(-17)) + creak(2.35, 0.65, 80, 30, db(-19), (380, 870, 1610)) \
   + creak(5.55, 0.55, 40, 120, db(-18), (450, 1010, 1900)) + creak(6.95, 0.45, 110, 50, db(-21))
creaks = np.stack([reverb(cr, 0.9, 0.22) * 1.0, reverb(np.roll(cr, 300), 0.9, 0.22) * 0.85])

# ---------- REVERSE BEEP: distant crane backup alarm, 3 short beeps, outdoors (filtered + reverb)
bp = np.zeros(N)
for k in range(3):
    t0 = 3.12 + k * 0.42
    g = np.clip((t - t0) / 0.01, 0, 1) * np.clip((t0 + 0.2 - t) / 0.015, 0, 1)
    tone = np.sign(np.sin(2 * np.pi * 1180 * t)) * 0.5 + np.sin(2 * np.pi * 1180 * t) * 0.5
    bp += tone * g
bp = bpf(bp, 600, 2600)
beep = np.stack([reverb(bp, 1.4, 0.45), reverb(np.roll(bp, 500), 1.4, 0.45)]) * db(-25)

# ---------- METALLIC LOCK CLICK at 7.85 s: latch transient + steel modes + low thump, then a tiny rattle
LOCK = 7.85
i0 = int(LOCK * SR)
click = np.zeros(N)
tr = rng.standard_normal(N) * env(LOCK, 0.0005, 0.006); click += hpf(tr, 1800) * 1.0
modes = [(212, 0.09, 0.8), (517, 0.07, 0.6), (893, 0.05, 0.55), (1377, 0.04, 0.4), (2140, 0.03, 0.35), (3311, 0.02, 0.2)]
for f, d, a in modes:
    click += a * np.sin(2 * np.pi * f * (t - LOCK)) * env(LOCK, 0.0008, d)
click += 1.3 * np.sin(2 * np.pi * 58 * (t - LOCK)) * env(LOCK, 0.002, 0.07)       # weight landing
for dt, a in ((0.075, 0.25), (0.13, 0.12)):                                       # settle rattle
    click += a * hpf(rng.standard_normal(N), 2000) * env(LOCK + dt, 0.0005, 0.004)
    for f, d, aa in modes[1:4]: click += a * aa * np.sin(2 * np.pi * f * 1.02 * (t - LOCK - dt)) * env(LOCK + dt, 0.0005, d * 0.6)
click /= np.max(np.abs(click))
clickS = np.stack([reverb(click, 1.2, 0.25), reverb(click, 1.2, 0.25)]) * db(-6)

# ---------- LIGHT-UP: four breaker thunks following the chase, then a warm musical accent
LIGHT = 8.0
th = np.zeros(N)
for i in range(4):
    c = LIGHT + i * 0.07
    th += np.sin(2 * np.pi * 70 * (t - c)) * env(c, 0.002, 0.05) + 0.4 * lpf(rng.standard_normal(N), 1200) * env(c, 0.001, 0.012)
th = np.stack([pan(th, -0.6 + i * 0.0)[0], pan(th, 0.6)[1]]) * db(-12)

def voice(f, t0, dur, amp, bright=1.0):  # soft electric-piano / bell partials
    tt = t - t0; m = tt >= 0; y = np.zeros(N)
    for h, a, d in ((1, 1, 2.6), (2, 0.35 * bright, 1.4), (3, 0.12 * bright, 0.8), (4.02, 0.06 * bright, 0.5)):
        y[m] += a * np.sin(2 * np.pi * f * h * tt[m]) * np.exp(-tt[m] / d)
    y *= np.clip(tt / 0.006, 0, 1)
    return y * amp
def pad(f, t0, amp):
    tt = t - t0; y = np.zeros(N); m = tt >= 0
    for det in (-0.12, 0, 0.11):
        y[m] += np.sin(2 * np.pi * f * (1 + det / 100) * tt[m] + np.sin(2 * np.pi * 0.3 * tt[m]))
    a = np.clip(tt / 0.9, 0, 1) * np.clip((12 - t) / 1.6, 0, 1)
    return lpf(y, 1800) * a * amp / 3
# D major add9 voiced warm (D3 A3 E4 F#4 A4) + bell D6 sparkle
mus = np.zeros(N)
for f, dl in ((146.83, 0.0), (220.0, 0.012), (329.63, 0.024), (369.99, 0.036), (440.0, 0.05)):
    mus += voice(f, LIGHT + 0.02 + dl, 4, 0.22)
mus += voice(1174.66, LIGHT + 0.1, 3, 0.05, 0.5) + voice(1479.98, LIGHT + 0.42, 3, 0.035, 0.5)
for f in (73.42, 146.83, 220.0, 293.66, 369.99):
    mus += pad(f, LIGHT, 0.12)
mus += 0.5 * np.sin(2 * np.pi * 36.7 * (t - LIGHT)) * env(LIGHT, 0.01, 0.6)  # sub swell
music = np.stack([reverb(mus, 2.4, 0.4), reverb(np.roll(mus, 600), 2.4, 0.4)])
music = music / np.max(np.abs(music)) * db(-9)

stems = {'ambience': amb + engine + winch, 'creak': creaks, 'reverse_beep': beep, 'lock_click': clickS,
         'lightup_thunks': th, 'music_accent': music}
# ambience dips slightly under the music
duck = np.interp(t, [0, 8.0, 8.6, 12], [1, 1, 0.6, 0.55])
stems['ambience'] = stems['ambience'] * duck
mix = sum(stems.values())
fade = np.clip(t / 0.03, 0, 1) * np.clip((12 - t) / 0.4, 0, 1)
mix *= fade
mix /= np.max(np.abs(mix)) / db(-1.5)

def wr(fn, x):
    x = np.clip(x, -1, 1); d = (x.T * 32767).astype('<i2')
    with wave.open(fn, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
wr(f'{out}/mix.wav', mix)
for k, v in stems.items(): wr(f'{out}/stem_{k}.wav', v * fade)
print('ok')
