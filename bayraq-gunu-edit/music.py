"""Original score + sound design for the Bayraq Günü Reel (31.5 s). Self-composed, no samples.

Writes music.wav (score) and sfx.wav (wind, flag flutter, impacts) at 48 kHz stereo.
Usage: python3 music.py <out_dir>
"""
import sys
import numpy as np
from scipy import signal

SR = 48000
DUR = 31.5
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(9)
OUT = sys.argv[1]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def lp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, "low", fs=SR, output="sos"), x)


def bp(x, f1, f2, o=2):
    return signal.sosfilt(signal.butter(o, [f1, f2], "band", fs=SR, output="sos"), x)


def reverb(x, secs=3.2, mix=0.35, seed=1):
    r = np.random.default_rng(seed)
    n = int(secs * SR)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * 6.9 / secs)
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    wet = signal.fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix * 2.2


def place(buf, x, at, gain=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


# ---------------------------------------------------------------- pad (warm strings-like)
def pad_note(m, dur, a=1.2, r=1.6, bright=1800):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = np.zeros(n)
    for det in (-0.07, 0.0, 0.06):
        f = hz(m + det)
        ph = rng.uniform(0, 2 * np.pi)
        for k in range(1, 9):
            x += np.sin(2 * np.pi * f * k * tt + ph * k) / k ** 1.25
    x *= 1 + 0.04 * np.sin(2 * np.pi * 4.8 * tt)
    return lp(x, bright) * env(n, a, r)


def piano_note(m, dur=3.5, vel=1.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = hz(m)
    x = np.zeros(n)
    for k, g in zip(range(1, 7), (1, 0.45, 0.25, 0.12, 0.07, 0.04)):
        x += g * np.sin(2 * np.pi * f * k * 1.0007 ** k * tt) * np.exp(-tt * (1.4 + k * 0.7))
    x *= np.minimum(1, tt / 0.004)
    return lp(x, 3500) * vel


L = np.zeros(N); R = np.zeros(N)

# Harmony in D minor (Dm – B♭ – F – C), the slow-motion holds on D,
# then the final phrase resolves to D major on the end card (27.0 s).
CH = [  # (start, end, midi notes, gain)
    (0.0, 5.9, [38, 50, 57, 62, 65], 0.55),     # Dm
    (5.6, 11.2, [34, 46, 53, 58, 62], 0.62),    # Bb
    (10.9, 16.0, [41, 53, 57, 60, 65], 0.70),   # F
    (15.7, 19.8, [36, 48, 55, 60, 64], 0.78),   # C
    (19.5, 23.2, [38, 50, 57], 0.45),           # slow-mo: bare D fifth
    (23.0, 27.3, [34, 46, 53, 58, 62, 65], 0.85),  # Bb (lift)
    (27.0, 31.5, [38, 50, 57, 62, 66, 69], 0.95),  # D major — resolution
]
for a, b, notes, g in CH:
    for i, m in enumerate(notes):
        x = pad_note(m, b - a + 0.3, a=1.0 if a > 0 else 2.2, r=1.4, bright=1400 + 900 * g)
        pan = 0.5 + 0.35 * np.sin(i * 1.9)
        place(L, x * (1 - pan), a, g * 0.05)
        place(R, x * pan, a, g * 0.05)

# Sparse piano motif (a rising question, answered at the end)
MOTIF = [
    (0.9, 69), (2.3, 72), (3.6, 74), (6.2, 70), (7.6, 74), (9.0, 77),
    (11.4, 72), (12.8, 76), (14.2, 77), (16.2, 76), (17.4, 74), (18.6, 72),
    (20.2, 69), (22.0, 74),
    (23.4, 70), (24.4, 74), (25.4, 77), (26.4, 79),
    (27.0, 78), (27.0, 74), (27.0, 66), (28.6, 81), (29.6, 78),
]
for at, m in MOTIF:
    x = piano_note(m, 3.8, 0.9 if at < 27 else 1.1)
    place(L, x, at, 0.055); place(R, x, at + 0.012, 0.05)

# Low "heartbeat" on the slow-motion section
for at in (19.6, 20.45, 21.3, 22.15):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    k = np.sin(2 * np.pi * (52 * tt + 18 * (1 - np.exp(-tt * 30)) / 30)) * np.exp(-tt * 9)
    place(L, k, at, 0.32); place(R, k, at, 0.32)

L, R = reverb(L, 3.6, 0.42, 1), reverb(R, 3.6, 0.42, 2)
music = np.stack([L, R], 1)
music *= env(N, 0.01, 1.2)[:, None]

# ---------------------------------------------------------------- SFX
SL = np.zeros(N); SRr = np.zeros(N)
# wind bed: brown-ish noise, band-limited, with slow gusts; low-passed (no harsh hiss)
for ch, buf in enumerate((SL, SRr)):
    w = np.cumsum(rng.standard_normal(N)); w -= lp(w, 20)
    w = bp(w, 120, 1500)
    g = lp(rng.standard_normal(N), 0.6, 2); g /= np.abs(g).max()
    gust = 0.75 + 0.6 * g
    gust = np.clip(gust, 0.2, 1.6)
    level = np.interp(t, [0, 1, 3, 9, 13.6, 19.5, 23, 27, 29, 31.5],
                         [0, 1, 0.8, 0.9, 1.0, 1.15, 0.7, 0.6, 0.3, 0])
    buf += w / np.abs(w).max() * gust * level * 0.16

# flag flutter during close shots (flapping cloth: noise gated at 9–14 Hz)
def flutter(dur, seed):
    r = np.random.default_rng(seed); n = int(dur * SR); tt = np.arange(n) / SR
    rate = 11 + 3 * np.sin(2 * np.pi * 0.7 * tt)
    gate = (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(rate) / SR)) ** 3
    x = bp(r.standard_normal(n), 300, 2600) * gate
    return lp(x, 3000) * env(n, 0.4, 0.6)
place(SL, flutter(3.0, 3), 0.0, 0.05); place(SRr, flutter(3.0, 4), 0.0, 0.05)
place(SL, flutter(3.4, 5), 19.5, 0.03); place(SRr, flutter(3.4, 6), 19.5, 0.03)

# soft low impacts on the key turns
def boom(g=1.0, seed=0):
    n = int(2.5 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * (44 * tt + 40 * (1 - np.exp(-tt * 12)) / 12)) * np.exp(-tt * 2.6)
    x += lp(np.random.default_rng(seed).standard_normal(n), 250) * np.exp(-tt * 6) * 0.6
    return x * g
for at, g in ((2.8, 0.35), (19.5, 0.45), (27.0, 0.75)):
    b = boom(g, int(at * 10))
    place(SL, b, at, 0.5); place(SRr, b, at, 0.5)

# reverse swell into slow-mo and end card
def swell(dur, seed):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = bp(np.random.default_rng(seed).standard_normal(n), 200, 2200)
    return lp(x, 2500) * (tt / dur) ** 3
for at, d in ((18.3, 1.2), (25.4, 1.6)):
    s = swell(d, int(at))
    place(SL, s, at, 0.10); place(SRr, s, at, 0.10)

sfx = np.stack([SL, SRr], 1)
sfx = reverb(sfx[:, 0], 1.6, 0.2, 3)[:, None] * [1, 0] + reverb(sfx[:, 1], 1.6, 0.2, 4)[:, None] * [0, 1]

import soundfile as sf
sf.write(f"{OUT}/music.wav", music.astype(np.float32), SR)
sf.write(f"{OUT}/sfx.wav", sfx.astype(np.float32), SR)
print("ok", np.abs(music).max(), np.abs(sfx).max())
