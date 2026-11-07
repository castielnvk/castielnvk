"""v2 score: original energetic fashion/house instrumental, 120 BPM, synthesised from scratch.
Stems -> stems2/*.npy (48 kHz stereo float32): drums, bass, chords, arp, pad."""
import numpy as np, os, sys
SR = 48000; BPM = 120; BEAT = 60 / BPM; BAR = 4 * BEAT
T = float(sys.argv[1]) if len(sys.argv) > 1 else 56.0
N = int(T * SR) + SR * 3
rng = np.random.default_rng(21)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def fftf(x, lo=None, hi=None, order=2):
    n = len(x); X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1 / SR); H = np.ones_like(f)
    if hi: H /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo: H /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if X.ndim == 2: H = H[:, None]
    return np.fft.irfft(X * H, n, axis=0)
def place(buf, sig, t, pan=0.0, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    sig = sig[:len(buf) - i]; l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
    buf[i:i + len(sig), 0] += sig * g * l; buf[i:i + len(sig), 1] += sig * g * r

PROG = [(45, [57, 60, 64, 67, 71]),   # Am9
        (41, [57, 60, 64, 65, 69]),   # Fmaj7 (add)
        (48, [55, 60, 64, 67, 71]),   # Cmaj7
        (43, [55, 59, 62, 64, 67])]   # G6

def kick():
    n = int(0.42 * SR); t = np.arange(n) / SR
    f = 46 + 90 * np.exp(-t * 38); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    click = fftf(rng.standard_normal(n), lo=2000, hi=6000) * np.exp(-t * 300) * 0.25
    return np.tanh(1.6 * (s + click)) / np.tanh(1.6)
def clap():
    n = int(0.3 * SR); t = np.arange(n) / SR; nz = fftf(rng.standard_normal(n), lo=900, hi=5200)
    env = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.022]): env += (t >= d) * np.exp(-np.clip(t - d, 0, None) * (90 if k < 2 else 20))
    return nz * env * 0.6
def hat(open_=False, v=1.0):
    n = int((0.22 if open_ else 0.05) * SR); t = np.arange(n) / SR
    nz = fftf(rng.standard_normal(n), lo=7500, hi=15000)
    return nz * np.exp(-t * (14 if open_ else 80)) * v
def saw(f, n, harm=14):
    t = np.arange(n) / SR; s = np.zeros(n)
    for h in range(1, harm + 1):
        if f * h > 16000: break
        s += np.sin(2 * np.pi * f * h * t) / h
    return s
def bass(m, dur):
    n = int((dur + 0.05) * SR); t = np.arange(n) / SR; f = mtof(m)
    sw = saw(f, n, 10); s = 0.6 * np.sin(2 * np.pi * f * t) + 0.4 * (fftf(sw, hi=420) * (1 - np.exp(-t * 18)) + fftf(sw, hi=1400) * np.exp(-t * 18))
    e = np.minimum(1, t / 0.004) * np.exp(-t * 4.5) * (t < dur) + (t >= dur) * np.exp(-dur * 4.5) * np.exp(-(t - dur) * 60)
    return np.tanh(1.3 * s * e)
def stab(notes, dur):
    n = int((dur + 0.6) * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for d in (-0.06, 0.06): s += saw(mtof(m) * 2 ** (d / 12), n, 10)
    s = fftf(s, lo=180, hi=2600)
    e = np.minimum(1, t / 0.003) * np.exp(-t * 7) * np.where(t < dur, 1, np.exp(-(t - dur) * 30))
    return s * e / len(notes) * 0.5
def pluck(m):
    n = int(0.5 * SR); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2 * np.pi * f * t + 1.4 * np.exp(-t * 18) * np.sin(2 * np.pi * f * 2 * t))
    return s * np.exp(-t * 9) * np.minimum(1, t / 0.002)
def pad(notes, dur):
    n = int((dur + 1.0) * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes[:4]:
        for d in (-0.1, 0.0, 0.1): s += saw(mtof(m) * 2 ** (d / 12), n, 8)
    s = fftf(s, lo=150, hi=1600)
    e = np.minimum(1, t / 0.6) * np.where(t < dur, 1, np.exp(-(t - dur) * 3))
    return s * e / 12

S = {k: np.zeros((N, 2)) for k in ['drums', 'bass', 'chords', 'arp', 'pad']}
nb = int(T / BAR) + 2
for b in range(nb):
    t0 = b * BAR; root, notes = PROG[b % 4]
    place(S['pad'], pad(notes, BAR), t0, 0, 0.5)
    for k in range(4):
        place(S['drums'], kick(), t0 + k * BEAT, 0, 0.9)
        place(S['drums'], hat(True, 0.32), t0 + k * BEAT + BEAT / 2, 0.25, 1)
        for s16 in (1, 3): place(S['drums'], hat(False, 0.22 if s16 == 1 else 0.3), t0 + k * BEAT + s16 * BEAT / 4 + (0.012 if s16 == 1 else 0), -0.3, 1)
    place(S['drums'], clap(), t0 + BEAT, 0.05, 0.55); place(S['drums'], clap(), t0 + 3 * BEAT, 0.05, 0.55)
    # bass: offbeat octave groove
    for k in range(8):
        m = root - 12 + (12 if k % 2 else 0) if k not in (0,) else root - 12
        if k % 2 == 1 or k == 0: place(S['bass'], bass(m + 12, BEAT * 0.38), t0 + k * BEAT / 2, 0, 0.55)
    # chord stabs: syncopated
    for pos in (0.5, 1.75, 2.5, 3.5):
        place(S['chords'], stab(notes, BEAT * 0.22), t0 + pos * BEAT, 0.0, 0.55)
    # arp 16ths
    arpn = [notes[0] + 12, notes[2] + 12, notes[4], notes[1] + 12]
    for s16 in range(16):
        place(S['arp'], pluck(arpn[s16 % 4] + (12 if s16 % 8 == 6 else 0)), t0 + s16 * BEAT / 4, 0.5 if s16 % 2 else -0.5, 0.18 * (1 if s16 % 4 == 0 else 0.7))

def ir(sec):
    n = int(sec * SR); t = np.arange(n) / SR
    x = rng.standard_normal((n, 2)) * np.exp(-t * 6.9 / sec)[:, None]; x = fftf(x, lo=250, hi=6500)
    return x / np.sqrt((x ** 2).sum())
def conv(x, h):
    n = len(x) + len(h); nf = 1 << (n - 1).bit_length(); out = np.zeros_like(x)
    for c in range(2): out[:, c] = np.fft.irfft(np.fft.rfft(x[:, c], nf) * np.fft.rfft(h[:, c], nf), nf)[:len(x)]
    return out
H = ir(1.4)
# simple ping-pong-ish delay for arp
d = int(BEAT * 0.75 * SR); a = S['arp']; dl = np.zeros_like(a); dl[d:, 1] += a[:-d, 0] * 0.4; dl[2 * d:, 0] += a[:-2 * d, 1] * 0.25
S['arp'] = a + dl
for k, w in [('chords', 0.3), ('arp', 0.35), ('pad', 0.35), ('drums', 0.06)]:
    S[k] = S[k] * (1 - w * 0.4) + conv(S[k], H) * w * 5
S['bass'] = fftf(S['bass'], hi=1200)
os.makedirs('stems2', exist_ok=True)
for k, v in S.items():
    v = v.astype(np.float32); np.save(f'stems2/{k}.npy', v); print(k, round(20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-9), 1))
