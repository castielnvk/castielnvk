"""Audio for the 20 s Reel: anthem finale (public domain) + soft whooshes on the flag wipes.
Usage: python3 audio.py <anthem.mp3> <out.wav>"""
import sys, subprocess, numpy as np, soundfile as sf
from scipy import signal
SR = 48000; START = 109.66; DUR = 20.0
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(START), "-t", str(DUR), "-i", sys.argv[1],
                      "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
n = len(x); t = np.arange(n) / SR
x[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
fo = int(1.0 * SR); x[-fo:] *= (np.linspace(1, 0, fo) ** 1.5)[:, None]
rng = np.random.default_rng(3)
sos = signal.butter(2, [180, 1800], "band", fs=SR, output="sos")
for c in (3.72, 11.02, 17.28):          # wipes: swell into the cut, quick tail after
    a, b = c - 0.32, c + 0.25
    i0, i1 = int(a * SR), int(b * SR)
    tt = np.linspace(0, 1, i1 - i0); split = 0.32 / 0.57
    e = np.where(tt < split, (tt / split) ** 2.5, (1 - (tt - split) / (1 - split)) ** 2)
    w = signal.sosfilt(sos, rng.standard_normal((i1 - i0, 2)), axis=0) * e[:, None]
    x[i0:i1] += w / np.abs(w).max() * 0.06
sf.write(sys.argv[2], x, SR)
