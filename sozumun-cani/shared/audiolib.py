# Original score + sound design for «Məlal» (edited timeline, seconds)
import numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt
SR = 48000; DUR = 71.83; N = int(SR * DUR)
rng = np.random.default_rng(7)
def tt(d): return np.arange(int(d * SR)) / SR
def hz(note):  # MIDI -> Hz
    return 440 * 2 ** ((note - 69) / 12)
def lpf(x, f, o=2): return sosfilt(butter(o, f / (SR / 2), 'low', output='sos'), x)
def hpf(x, f, o=2): return sosfilt(butter(o, f / (SR / 2), 'high', output='sos'), x)
def bpf(x, a, b, o=2): return sosfilt(butter(o, [a / (SR / 2), b / (SR / 2)], 'band', output='sos'), x)
class Bus:
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N)
    def put(s, t, sig, g=1.0, pan=0.0):
        i = int(t * SR); m = min(len(sig), N - i)
        if m <= 0: return
        s.L[i:i + m] += sig[:m] * g * np.sqrt((1 - pan) / 2) * 1.414
        s.R[i:i + m] += sig[:m] * g * np.sqrt((1 + pan) / 2) * 1.414
def env_ar(n, a, r):
    e = np.ones(n); ai = int(a * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai) ** 2
    if ri: e[-ri:] *= np.linspace(1, 0, ri) ** 1.5
    return e
# ---------- instruments ----------
def piano(note, dur=4.0, vel=0.6):
    f = hz(note); t = tt(dur); y = np.zeros_like(t); B = 0.00035
    for n in range(1, 10):
        fn = f * n * np.sqrt(1 + B * n * n)
        if fn > 9000: break
        amp = vel ** (1 + n * 0.12) / n ** 1.25
        y += amp * np.sin(2 * np.pi * fn * t + rng.random() * 6) * np.exp(-t * (0.55 + 0.42 * n) * (1 + note / 160))
    y *= np.minimum(1, t / 0.004)
    y = lpf(y, 1800 + 4000 * vel)  # felt-like softness
    y[-int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR))
    return y * 0.5
def pad(notes, dur, att=2.0, rel=2.5, bright=900, det=0.006):
    t = tt(dur); y = np.zeros_like(t)
    for note in notes:
        for d in (-det, 0, det):
            f = hz(note) * (1 + d)
            for n in range(1, 14):
                if f * n > 6000: break
                y += np.sin(2 * np.pi * f * n * t + rng.random() * 6) / n * (0.6 if n > 1 else 1)
    y = lpf(y, bright, 2) * env_ar(len(t), att, rel)
    return y / (len(notes) * 9)
def drone(note, dur, att=2.5, rel=3.0, bright=700):
    t = tt(dur); vib = 1 + 0.003 * np.sin(2 * np.pi * 4.8 * t) * np.minimum(1, t / 2)
    ph = 2 * np.pi * np.cumsum(hz(note) * vib) / SR; y = sum(np.sin(ph * n) / n ** 1.1 for n in range(1, 16))
    return lpf(y, bright, 2) * env_ar(len(t), att, rel) * 0.12
def bell(f, dur=3.0, g=1.0):
    t = tt(dur); y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * dcy) for r, a, dcy in [(1, 1, 1.6), (2.76, 0.45, 3.2), (5.4, 0.25, 6), (8.9, 0.1, 9)])
    return y * np.minimum(1, t / 0.002) * g * 0.3
def noise(d): return rng.standard_normal(int(d * SR))
def whoosh(d, f0, f1, g=1.0):
    x = noise(d); n = len(x); out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        k = i / n; f = f0 * (f1 / f0) ** k; out[i:i + seg] = bpf(x[i:i + seg + 0][:seg], max(40, f * 0.6), min(20000, f * 1.6), 1)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return lpf(out, 9000) * e * g
def drop(f=900, g=1.0):  # water droplet: fast upward chirp
    t = tt(0.12); f_t = f * (1 + 1.6 * t / 0.12); y = np.sin(2 * np.pi * np.cumsum(f_t) / SR) * np.exp(-t * 45)
    return y * g
def thump(f=60, d=0.5, g=1.0):
    t = tt(d); return np.sin(2 * np.pi * f * t * (1 + 0.5 * np.exp(-t * 25))) * np.exp(-t * 8) * g
def click(d=0.03, g=1.0, f=3000):
    t = tt(d); return (bpf(noise(d), f * 0.5, min(f * 2, 20000)) * 0.6 + np.sin(2 * np.pi * f * t) * 0.3) * np.exp(-t * 160) * g
def rainbed(d, g=1.0):
    x = bpf(noise(d), 1200, 9000) * 0.25
    n = len(x); drops = np.zeros(n)
    for _ in range(int(d * 26)):
        i = rng.integers(0, n - 7000)
        dd = drop(1500 + rng.random() * 2500, 0.1 + rng.random() * 0.2); drops[i:i + len(dd)] += dd
    return (x + drops) * g
def reverb(L, R, secs=3.6, wet=0.35, damp=2500):
    n = int(secs * SR); t = np.arange(n) / SR
    irL = rng.standard_normal(n) * np.exp(-t * 6.9 / secs); irR = rng.standard_normal(n) * np.exp(-t * 6.9 / secs)
    irL = lpf(irL, damp); irR = lpf(irR, damp); irL[:int(0.012 * SR)] = 0; irR[:int(0.015 * SR)] = 0
    irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
    wl = fftconvolve(L, irL)[:len(L)]; wr = fftconvolve(R, irR)[:len(R)]
    return L * (1 - wet) + wl * wet * 1.0, R * (1 - wet) + wr * wet * 1.0

