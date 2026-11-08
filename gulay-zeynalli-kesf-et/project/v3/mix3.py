"""v3 mix: ORIGINAL camera audio (gain only, 12 ms fades at verified word boundaries) + 124 BPM score aligned so the drop lands on the collage + paparazzi SFX."""
import numpy as np, subprocess
from timeline3 import build, BEAT
SR = 48000
items, T, GRID0 = build()
N = int((T + 0.3) * SR)
def load(f, ch):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-map', '0:a:0', '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(r, np.float32).astype(np.float64).reshape(-1, ch)
SRC = load('../dl1/IMG_7215.MOV', 2)
rng = np.random.default_rng(9)

# ---- voice ----
voice = np.zeros((N, 2))
def lvl(seg):
    m = seg.mean(1); fr = int(0.05 * SR); n = len(m) // fr
    e = np.sqrt((m[:n * fr].reshape(n, fr) ** 2).mean(1)); return 20 * np.log10(np.percentile(e, 80) + 1e-9)
clips = [it for it in items if it['kind'] == 'clip']
L = [lvl(np.concatenate([SRC[int(p['src_in'] * SR):int(p['src_out'] * SR)] for p in it['parts']])) for it in clips]
ref = np.median(L)
for it, l in zip(clips, L):
    g = 10 ** (np.clip(ref - l, -4, 4) / 20)
    for p in it['parts']:
        seg = SRC[int(p['src_in'] * SR):int(p['src_out'] * SR)].copy() * g
        fi, fo = int(0.02 * SR), int(0.012 * SR)
        seg[:fi] *= (np.sin(np.linspace(0, np.pi / 2, fi)) ** 2)[:, None]; seg[-fo:] *= (np.cos(np.linspace(0, np.pi / 2, fo)) ** 2)[:, None]
        o = int(p['out_in'] * SR); voice[o:o + len(seg)] += seg

# ---- music (bar 0 of the score = GRID0, the collage drop) ----
BAR = 4 * BEAT; off = int((4 * BAR - GRID0) * SR)
st = {}
for k in ['drums', 'bass', 'chords', 'arp', 'pad']:
    a = np.load(f'stems3/{k}.npy').astype(np.float64)[off:off + N]
    st[k] = np.pad(a, ((0, max(0, N - len(a))), (0, 0)))
t = np.arange(N) / SR
def fftf(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1 / SR); Hh = np.ones_like(f)
    if hi: Hh /= np.sqrt(1 + (f / hi) ** 4)
    if lo: Hh /= np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    if X.ndim == 2: Hh = Hh[:, None]
    return np.fft.irfft(X * Hh, n, axis=0)
full = st['drums'] + st['bass'] * 0.9 + st['chords'] + st['arp'] + st['pad'] * 0.8
nodrum = st['bass'] * 0.9 + st['chords'] + st['arp'] + st['pad'] * 0.8
lp = fftf(st['pad'] * 0.8 + st['chords'] + st['bass'] * 0.9, hi=550)
keys = {'bed': [], 'drum': [], 'lp': []}
for it in items:
    s, e, kd = it['start'], it['end'], it['kind']
    v = {'clip': (0.13, 0.7, 0), 'q': (0.48, 1, 0), 'follow': (0.36, 1, 0), 'collage': (0.55, 1, 0), 'burst': (0.40, 0, 0),
         'callback': (0.44, 1, 0), 'end': (0.46, 1, 0)}[kd]
    if it.get('tag') == 'hook': v = (0.17, 0, 1)
    for kk, val in zip(('bed', 'drum', 'lp'), v): keys[kk] += [(s + 0.02, val), (e - 0.02, val)]
keys['bed'] += [(T - 0.7, 0.46), (T + 0.1, 0.0)]
def curve(kv): kv = sorted(kv); return np.interp(t, [a for a, _ in kv], [b for _, b in kv])
def smooth(x, sec):
    k = max(1, int(sec * SR / 40)); xs = x[::40]; xs = np.convolve(np.pad(xs, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    return np.interp(np.arange(len(x)), np.arange(len(xs)) * 40, xs)
BED, DR, LPk = smooth(curve(keys['bed']), 0.06), smooth(curve(keys['drum']), 0.06), smooth(curve(keys['lp']), 0.03)
music = (nodrum + st['drums'] * DR[:, None]) * (1 - LPk[:, None]) + lp * LPk[:, None] * 1.4
music *= BED[:, None]

# ---- SFX ----
sfx = np.zeros((N, 2))
def put(sig, at, g, pan=0.0):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    sig = sig[:N - i]; l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
    sfx[i:i + len(sig), 0] += sig * g * l; sfx[i:i + len(sig), 1] += sig * g * r
def f1(x, lo=None, hi=None): return fftf(x[:, None], lo, hi)[:, 0]
def shutter():
    n = int(0.16 * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    for d, a in ((0.0, 1.0), (0.055, 0.7)):
        k = tt >= d; x = f1(rng.standard_normal(n), 1800, 9000) * np.exp(-np.clip(tt - d, 0, None) * 160) * k
        out += a * (x + 0.5 * np.sin(2 * np.pi * 180 * tt) * np.exp(-np.clip(tt - d, 0, None) * 90) * k)
    return out
def flashs():
    n = int(0.4 * SR); tt = np.arange(n) / SR
    return f1(rng.standard_normal(n), 3000, 14000) * np.exp(-tt * 10) * np.minimum(1, tt / 0.008) * 0.6
def pop():
    n = int(0.14 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(520 + 700 * (1 - np.exp(-tt * 40))) / SR) * np.exp(-tt * 30) * 0.8
def swish(d=0.28, up=True):
    n = int(d * SR); tt = np.arange(n) / SR
    return f1(rng.standard_normal(n), 800, 7000) * np.sin(np.pi * tt / d) ** 2 * (tt / d if up else 1 - tt / d)
def thump():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(52 + 70 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 9)
def riser(d):
    n = int(d * SR); tt = np.arange(n) / SR
    return f1(rng.standard_normal(n), 1500, 9000) * (tt / d) ** 2.5
put(shutter(), 0.0, 0.11); put(flashs(), 0.0, 0.07)
for it in items:
    s, e, kd = it['start'], it['end'], it['kind']
    if kd == 'collage':
        put(riser(1.2), s - 1.2, 0.05); put(thump(), s, 0.22)
        for h in (0.0, 0.2, 0.4, 0.6): put(shutter(), s + h, 0.10, -0.3 + h); put(flashs(), s + h, 0.04)
    if kd in ('q', 'follow'): put(swish(0.25), s - 0.2, 0.05); put(pop(), s + 0.08, 0.07); put(swish(0.22, False), e - 0.16, 0.035)
    if kd == 'burst':
        for h in (0.0, 0.33, 0.66): put(shutter(), s + h, 0.12, 0.2 - h * 0.4); put(flashs(), s + h, 0.05)
    if kd == 'callback': put(shutter(), s, 0.12); put(flashs(), s, 0.06); put(thump(), s + 0.48, 0.16)
    if kd == 'end': put(shutter(), s, 0.11); put(flashs(), s, 0.06); put(thump(), s + 0.42, 0.14)
music_out = music * 0.55 * 0.075
mix = voice + music_out + sfx * 0.09
def wr(name, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', name], input=np.asarray(x, np.float32).tobytes(), check=True)
wr('v3_voice.wav', voice); wr('v3_music.wav', music_out); wr('v3_sfx.wav', sfx * 0.09); wr('v3_mix_raw.wav', mix)
db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
for it in items:
    a, b = int(it['start'] * SR), int(it['end'] * SR)
    print(f"{it['kind']:8s} voice {db(voice[a:b]):6.1f} music {db(music_out[a:b]):6.1f} sfx {db(sfx[a:b] * 0.09):6.1f}")
