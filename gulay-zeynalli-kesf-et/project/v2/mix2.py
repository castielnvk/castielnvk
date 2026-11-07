"""v2 mix: ORIGINAL camera audio (gain only, short crossfades) + v2 score + restrained SFX."""
import numpy as np, subprocess
from timeline2 import build
SR = 48000
items, T = build()
N = int((T + 0.3) * SR)
def load(f, ch):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-map', '0:a:0', '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(r, np.float32).astype(np.float64).reshape(-1, ch)
SRC = load('../dl1/IMG_7215.MOV', 2)          # untouched original audio
rng = np.random.default_rng(5)

# ---- voice: original audio, per-answer gain matching only ----
voice = np.zeros((N, 2))
def speech_level(seg):
    m = seg.mean(1); fr = int(0.05 * SR); n = len(m) // fr
    e = np.sqrt((m[:n * fr].reshape(n, fr) ** 2).mean(1)); return 20 * np.log10(np.percentile(e, 80) + 1e-9)
levels = []
for it in items:
    if it['kind'] != 'clip': continue
    seg = np.concatenate([SRC[int(p['src_in'] * SR):int(p['src_out'] * SR)] for p in it['parts']])
    levels.append(speech_level(seg))
ref = np.median(levels); li = 0
for it in items:
    if it['kind'] != 'clip': continue
    g = 10 ** (np.clip(ref - levels[li], -4, 4) / 20); li += 1
    for k, p in enumerate(it['parts']):
        seg = SRC[int(p['src_in'] * SR):int(p['src_out'] * SR)].copy() * g
        fi = int(0.02 * SR); fo = int(0.012 * SR)  # short fades: cut points sit on word boundaries, never fade over a syllable
        seg[:fi] *= (np.sin(np.linspace(0, np.pi / 2, fi)) ** 2)[:, None]
        seg[-fo:] *= (np.cos(np.linspace(0, np.pi / 2, fo)) ** 2)[:, None]
        o = int(p['out_in'] * SR); voice[o:o + len(seg)] += seg
print('per-answer level (dBFS):', [round(x, 1) for x in levels], 'ref', round(ref, 1))

# ---- music automation ----
st = {k: np.load(f'stems2/{k}.npy').astype(np.float64)[:N] for k in ['drums', 'bass', 'chords', 'arp', 'pad']}
t = np.arange(N) / SR
keys = {k: [] for k in ['bed', 'drums', 'arp', 'chords']}
for it in items:
    s, e = it['start'], it['end']; kd = it['kind']
    if kd == 'clip': v = dict(bed=0.10, drums=0.6, arp=0.0, chords=0.7)
    elif kd in ('card', 'title'): v = dict(bed=0.42, drums=1.0, arp=1.0, chords=1.0)
    elif kd == 'follow': v = dict(bed=0.30, drums=1.0, arp=0.6, chords=1.0)
    elif kd == 'freeze': v = dict(bed=0.36, drums=0.0 if it.get('last') else 0.5, arp=1.0, chords=1.0)
    else: v = dict(bed=0.40, drums=0.0, arp=1.0, chords=1.0)
    if it.get('tag') == 'hook': v = dict(bed=0.08, drums=0.0, arp=0.6, chords=0.0)
    d0 = 0.18 if kd in ('freeze', 'title') else 0.03  # let the last spoken syllable finish before the music lifts
    for k in keys: keys[k] += [(s + d0, v[k]), (e - 0.03, v[k])]
keys['bed'] += [(T - 1.4, 0.40), (T + 0.2, 0.0)]
def curve(kv):
    kv = sorted(kv); return np.interp(t, [a for a, _ in kv], [b for _, b in kv])
def smooth(x, sec):
    k = max(1, int(sec * SR / 40)); xs = x[::40]; xs = np.convolve(np.pad(xs, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    return np.interp(np.arange(len(x)), np.arange(len(xs)) * 40, xs)
C = {k: smooth(curve(v), 0.12) for k, v in keys.items()}
music = (st['drums'] * C['drums'][:, None] + st['bass'] * 0.9 + st['chords'] * C['chords'][:, None] + st['arp'] * C['arp'][:, None] + st['pad'] * 0.8)
music *= C['bed'][:, None]

# ---- SFX ----
sfx = np.zeros((N, 2))
def fftf(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); H = np.ones_like(f)
    if hi: H /= np.sqrt(1 + (f / hi) ** 4)
    if lo: H /= np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X * H, n)
def put(sig, at, g, pan=0.0):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    sig = sig[:N - i]; l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
    sfx[i:i + len(sig), 0] += sig * g * l; sfx[i:i + len(sig), 1] += sig * g * r
def shutter():
    n = int(0.16 * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    for d, a in ((0.0, 1.0), (0.055, 0.7)):
        k = (tt >= d); x = fftf(rng.standard_normal(n), lo=1800, hi=9000) * np.exp(-np.clip(tt - d, 0, None) * 160) * k
        out += a * (x + 0.5 * np.sin(2 * np.pi * 180 * tt) * np.exp(-np.clip(tt - d, 0, None) * 90) * k)
    return out
def flash():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    up = fftf(rng.standard_normal(n), lo=3000, hi=14000) * np.exp(-tt * 9) * np.minimum(1, tt / 0.01)
    return up * 0.6
def thump():
    n = int(0.5 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(55 + 60 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 9)
def swish(d=0.3):
    n = int(d * SR); tt = np.arange(n) / SR
    return fftf(rng.standard_normal(n), lo=600, hi=6000) * np.sin(np.pi * tt / d) ** 2
for it in items:
    s = it['start']
    if it['kind'] == 'card': put(shutter(), s - 0.05, 0.10, 0.2); put(swish(0.35), s - 0.25, 0.05)
    if it['kind'] == 'follow': put(swish(0.3), s - 0.15, 0.05, -0.2)
    if it['kind'] in ('title', 'freeze'): put(shutter(), s + 0.04, 0.12, -0.2); put(flash(), s + 0.04, 0.08); put(thump(), s + 0.2, 0.18)
    if it['kind'] == 'end': put(swish(0.4), s - 0.2, 0.05)

music_out = music * 0.55 * 0.075
mix = voice + music_out + sfx * 0.09
def wr(name, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', name], input=np.asarray(x, np.float32).tobytes(), check=True)
wr('v2_voice.wav', voice); wr("v2_music.wav", music_out); wr("v2_sfx.wav", sfx * 0.09); wr('v2_mix_raw.wav', mix)
