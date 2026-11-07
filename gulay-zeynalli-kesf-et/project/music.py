"""Original instrumental score, synthesised from scratch (no samples, no third-party audio).
100 BPM, Fmaj9 - Am9 - Dm9 - G9sus progression; stems written to stems/*.npy (48 kHz stereo float32)."""
import numpy as np, os, sys
SR = 48000; BPM = 100; BEAT = 60 / BPM; BAR = 4 * BEAT
T = float(sys.argv[1]) if len(sys.argv) > 1 else 92.0
N = int(T * SR) + SR * 4
rng = np.random.default_rng(7)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def env_adsr(n, a, d, s, r, sus_len):
    a, d, r = int(a * SR), int(d * SR), int(r * SR); sl = max(int(sus_len * SR), a + d)
    e = np.zeros(sl + r)
    e[:a] = np.linspace(0, 1, a, endpoint=False) if a else 0
    e[a:a + d] = np.linspace(1, s, d, endpoint=False)
    e[a + d:sl] = s
    e[sl:] = s * np.exp(-np.linspace(0, 6, r))
    return e
def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); z = 0.0
    # vectorised via lfilter-like recursion in chunks (simple python loop is slow) -> use FFT-domain filter instead
    return x
def fft_filter(x, lo=None, hi=None, order=2):
    n = len(x); X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1 / SR)
    H = np.ones_like(f)
    if hi: H *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo: H *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if X.ndim == 2: H = H[:, None]
    return np.fft.irfft(X * H, n, axis=0)
def place(buf, sig, t, pan=0.0, gain=1.0):
    i = int(t * SR); 
    if i >= len(buf): return
    sig = sig[:len(buf) - i]
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414

# progression (2 bars each chord would be slow; 1 bar each, 4-bar loop)
PROG = [  # bass root, chord tones
    (41, [57, 60, 64, 67]),      # Fmaj9 (A C E G over F)
    (45, [55, 60, 64, 71]),      # Am9  (G C E B over A)
    (38, [53, 57, 60, 64]),      # Dm9  (F A C E over D)
    (43, [53, 57, 62, 65]),      # G9sus (F A D F over G)
]
def chord_at(bar): return PROG[bar % 4]

def ep_note(f, dur, vel):
    # FM electric piano: carrier + modulator ratio 1 (bark) and 14 (tine), decaying index
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    idx = 1.6 * np.exp(-t * 3.0) * vel + 0.2
    tine = 0.35 * np.exp(-t * 12) * np.sin(2 * np.pi * f * 14 * t)
    car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t) + tine * vel)
    e = np.exp(-t * 1.1) * np.minimum(1, t / 0.004)
    rel = np.ones(n); k = int(dur * SR); rel[k:] = np.exp(-np.arange(n - k) / SR * 9)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.6 * t)
    return car * e * rel * trem * vel

def pad_chord(notes, dur):
    n = int((dur + 1.5) * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        f = mtof(m)
        for det in (-0.07, 0.0, 0.08):
            ph = rng.uniform(0, 2 * np.pi)
            ff = f * 2 ** (det / 12)
            # band-limited-ish saw: 8 harmonics
            for h in range(1, 9):
                s += np.sin(2 * np.pi * ff * h * t + ph * h) / h * (0.8 ** h)
    e = env_adsr(n, 0.9, 0.5, 0.8, 1.4, dur); e = np.pad(e, (0, max(0, n - len(e))))[:n]
    return s * e / (len(notes) * 3)

def bass_note(f, dur):
    n = int((dur + 0.3) * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    s = np.tanh(1.4 * s) / np.tanh(1.4)
    e = np.minimum(1, t / 0.01) * np.where(t < dur, np.exp(-t * 0.8), np.exp(-dur * 0.8) * np.exp(-(t - dur) * 25))
    return s * e

def kick():
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 48 + 70 * np.exp(-t * 30); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * np.minimum(1, t / 0.002)
def snap():
    n = int(0.25 * SR); t = np.arange(n) / SR
    nz = fft_filter(rng.standard_normal(n), lo=1500, hi=6000)
    return (nz * 0.7 + 0.3 * np.sin(2 * np.pi * 1850 * t)) * np.exp(-t * 32)
def shaker(v):
    n = int(0.09 * SR); t = np.arange(n) / SR
    nz = fft_filter(rng.standard_normal(n), lo=6500, hi=13000)
    return nz * np.exp(-t * 55) * np.minimum(1, t / 0.006) * v

def bell(f):
    n = int(2.6 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t + 1.1 * np.exp(-t * 4) * np.sin(2 * np.pi * f * 3.5 * t))
    return s * np.exp(-t * 2.0) * np.minimum(1, t / 0.003)

stems = {k: np.zeros((N, 2), np.float32) for k in ['pad', 'ep', 'bass', 'drums', 'bell']}
nbars = int(T / BAR) + 2
for b in range(nbars):
    t0 = b * BAR; root, notes = chord_at(b)
    stems['pad'][:] += 0  # placeholder
    place(stems['pad'], pad_chord(notes, BAR), t0, 0.0, 0.5)
    # EP: chord on 1 (spread), stab on 2&, light on 4&
    for k, m in enumerate(notes):
        place(stems['ep'], ep_note(mtof(m), BEAT * 1.6, 0.55), t0 + k * 0.012, -0.35 + 0.23 * k, 0.32)
    for k, m in enumerate(notes[1:]):
        place(stems['ep'], ep_note(mtof(m), BEAT * 0.4, 0.35), t0 + 1.5 * BEAT + k * 0.01, 0.25 - 0.2 * k, 0.22)
    if b % 2 == 1:
        for k, m in enumerate(notes[2:]):
            place(stems['ep'], ep_note(mtof(m + 12), BEAT * 0.3, 0.3), t0 + 3.5 * BEAT, 0.3, 0.16)
    # bass
    place(stems['bass'], bass_note(mtof(root), BEAT * 1.4), t0, 0, 0.55)
    place(stems['bass'], bass_note(mtof(root), BEAT * 0.45), t0 + 2.5 * BEAT, 0, 0.4)
    place(stems['bass'], bass_note(mtof(root + 12 if b % 2 else root + 7), BEAT * 0.4), t0 + 3.5 * BEAT, 0, 0.3)
    # drums
    place(stems['drums'], kick(), t0, 0, 0.8); place(stems['drums'], kick(), t0 + 2.5 * BEAT, 0, 0.45)
    place(stems['drums'], snap(), t0 + BEAT, 0.1, 0.22); place(stems['drums'], snap(), t0 + 3 * BEAT, 0.1, 0.22)
    for s16 in range(16):
        v = [0.5, 0.18, 0.32, 0.2][s16 % 4]
        sw = 0.025 if s16 % 2 else 0
        place(stems['drums'], shaker(v), t0 + s16 * BEAT / 4 + sw, 0.45, 0.25)
    # bell motif every 2 bars
    if b % 2 == 0:
        mot = [notes[-1] + 12, notes[-2] + 12, notes[-1] + 12 + 2]
        for k, m in enumerate(mot):
            place(stems['bell'], bell(mtof(m)), t0 + (2 + k * 0.5) * BEAT, -0.4 + 0.4 * k, 0.12)

# reverb (synthetic stereo IR) for ep, pad, bell, snap
def ir(sec, seed):
    r = np.random.default_rng(seed); n = int(sec * SR); t = np.arange(n) / SR
    x = r.standard_normal((n, 2)) * np.exp(-t * 6.9 / sec)[:, None]
    x = fft_filter(x, lo=200, hi=7000); x[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return x / np.sqrt((x ** 2).sum())
def conv(x, h):
    n = len(x) + len(h); nf = 1 << (n - 1).bit_length()
    out = np.zeros((len(x), 2))
    for c in range(2):
        out[:, c] = np.fft.irfft(np.fft.rfft(x[:, c], nf) * np.fft.rfft(h[:, c], nf), nf)[:len(x)]
    return out
H = ir(2.4, 3)
for k, wet in [('ep', 0.35), ('pad', 0.4), ('bell', 0.55), ('drums', 0.12)]:
    x = stems[k].astype(np.float64)
    stems[k] = (x * (1 - wet * 0.5) + conv(x, H) * wet * 6).astype(np.float32)
stems['pad'] = fft_filter(stems['pad'].astype(np.float64), lo=120, hi=2200).astype(np.float32)
stems['bass'] = fft_filter(stems['bass'].astype(np.float64), hi=900).astype(np.float32)
stems['ep'] = fft_filter(stems['ep'].astype(np.float64), lo=150, hi=7500).astype(np.float32)
os.makedirs('stems', exist_ok=True)
for k, v in stems.items():
    np.save(f'stems/{k}.npy', v); print(k, 20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-9))
