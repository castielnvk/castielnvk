"""Synthesised, restrained sound design mixed under the untouched original recording."""
import subprocess, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
SR, DUR = 44100, 56.9
N = int(SR * DUR); t = np.arange(N) / SR
r = np.random.RandomState(4)
db = lambda x: 10 ** (x / 20)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], btype='band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, btype='low', fs=SR, output='sos'), x)
def env_keys(ks): return np.interp(t, [k[0] for k in ks], [k[1] for k in ks])
def pan(x, p): return np.stack([x * np.cos(p * np.pi / 2), x * np.sin(p * np.pi / 2)], 1)   # p 0=L 1=R
def place(sig, at):
    out = np.zeros(N); i = int(at * SR); n = min(len(sig), N - i)
    if n > 0: out[i:i + n] = sig[:n]
    return out
def norm(x): return x / (np.abs(x).max() + 1e-9)
ir_t = np.arange(int(SR * 1.6)) / SR
IR = [r.randn(len(ir_t)) * np.exp(-ir_t / 0.38) for _ in range(2)]
def verb(st, wet=0.35):
    w = np.stack([fftconvolve(st[:, c], IR[c])[:N] for c in range(2)], 1)
    return st + wet * w / 60

feat = np.load("feat.npz")['full']
gain = 0.22 + 1.75 * np.interp(t, np.arange(len(feat)) / 30, feat) ** 1.4     # same curve that moves the grass
mix = np.zeros((N, 2))

# wind through the field: follows the same energy curve as the picture
for c in range(2):
    slow = 0.75 + 0.25 * np.sin(2 * np.pi * (0.07 * t + r.rand())) * np.sin(2 * np.pi * (0.031 * t + r.rand()))
    w = norm(bp(r.randn(N), 140, 700)) * (0.4 + 0.6 * gain / gain.max()) * slow
    rustle = norm(bp(r.randn(N), 2200, 6500)) * (gain / gain.max()) ** 2 * slow
    mix[:, c] += w * db(-18) + rustle * db(-30)

# crickets: stop when the light goes out, and never come back
ck = np.zeros(N)
for f0, rate, ph in ((4300, 2.3, 0.0), (4750, 1.9, 0.37), (3900, 2.7, 0.71)):
    chirp = ((t * rate + ph) % 1.0) < 0.32
    ck += np.sin(2 * np.pi * f0 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 58 * t)) ** 3 * chirp * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t + ph * 9))
ck *= env_keys([(0, 0), (2.5, 1), (15.4, 1), (15.9, 0.25), (17.2, 0), (DUR, 0)])
mix += pan(norm(ck) * db(-26), 0.35) + pan(np.roll(norm(ck), 9000) * db(-31), 0.8)

# firefly: a small warm shimmer crossing left to right, faltering and cutting at "died"
fl = sum(np.sin(2 * np.pi * f * t + i) * a for i, (f, a) in enumerate(((1760, 1), (2637, 0.5), (3520, 0.22))))
fl *= 0.6 + 0.4 * np.sin(2 * np.pi * 7.3 * t) * np.sin(2 * np.pi * 0.9 * t)
fl *= env_keys([(0, 0), (8.2, 0), (10.9, 1), (12.8, 0.7), (15.5, 0.7), (15.6, 0.15), (15.72, 0.55), (15.86, 0.08), (16.0, 0.25), (16.22, 0), (DUR, 0)])
pp = env_keys([(0, 0.1), (8.2, 0.1), (12.8, 0.7), (15.5, 0.55), (DUR, 0.55)])
mix += np.stack([fl * np.cos(pp * np.pi / 2), fl * np.sin(pp * np.pi / 2)], 1) / 1.7 * db(-25)

# distant firework: the flash is at 29.38, the sound arrives late, muffled, then a little crackle
tt = np.arange(int(SR * 2.5)) / SR
boom = np.sin(2 * np.pi * (58 * tt - 9 * tt ** 2).clip(0)) * np.exp(-tt / 0.42) + lp(r.randn(len(tt)), 180) * np.exp(-tt / 0.3) * 0.5
boom *= np.minimum(1, tt / 0.012)
cr = np.zeros(int(SR * 1.4))
for _ in range(34):
    i = int(r.rand() ** 0.7 * (len(cr) - 400)); cr[i:i + 300] += r.randn(300) * np.exp(-np.arange(300) / 50) * r.rand()
cr = lp(cr, 2400) * np.exp(-np.arange(len(cr)) / SR / 0.6)
fw = verb(pan(place(norm(boom), 30.28) * db(-15) + place(norm(cr), 30.75) * db(-30), 0.6), 0.5)
mix += fw

# hawk: wing beats crossing the top of the frame
wing = norm(bp(r.randn(N), 250, 1100)) * np.clip(np.sin(2 * np.pi * 1.25 * t), 0, 1) ** 2
wing *= env_keys([(0, 0), (34.3, 0), (35.3, 1), (36.5, 0.8), (37.2, 0), (DUR, 0)])
pp = env_keys([(0, 0.1), (34.4, 0.1), (37.3, 0.95), (DUR, 0.95)])
mix += np.stack([wing * np.cos(pp * np.pi / 2), wing * np.sin(pp * np.pi / 2)], 1) * db(-28)

# the drop lets go on "cry", and lands
td = np.arange(int(SR * 0.5)) / SR
plink = (np.sin(2 * np.pi * (1500 * td - 1400 * td ** 2).clip(0)) + 0.4 * np.sin(2 * np.pi * (2900 * td - 2500 * td ** 2).clip(0))) * np.exp(-td / 0.07) * np.minimum(1, td / 0.002)
tick = bp(r.randn(len(td)), 3000, 8000) * np.exp(-td / 0.006)
mix += verb(pan(place(norm(plink), 39.42) * db(-18) + place(norm(tick), 38.56) * db(-33), 0.4), 0.8)

mix *= env_keys([(0, 0), (1.5, 1), (53.5, 1), (56.0, 0), (DUR, 0)])[:, None]
print("sfx peak dBFS", 20 * np.log10(np.abs(mix).max()), "rms", 20 * np.log10(np.sqrt((mix ** 2).mean())))

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "audio.m4a", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
mus = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
m = np.zeros((N, 2)); n = min(N, len(mus)); m[:n] = mus[:n]
print("music peak", np.abs(m).max(), "rms dB", 20 * np.log10(np.sqrt((m ** 2).mean())))
out = m + mix
k = 0.92; over = np.abs(out) > k      # only peaks above the knee are rounded; everything else is bit-for-bit the sum
out[over] = np.sign(out[over]) * (k + (0.995 - k) * np.tanh((np.abs(out[over]) - k) / (0.995 - k)))
print("samples touched by limiter: %.4f%%" % (over.mean() * 100))
for name, x in (("mix.wav", out), ("sfx_only.wav", mix)):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", name], input=x.astype(np.float32).tobytes())
