import numpy as np, subprocess, json, sys
from timeline import build, FPS
SR = 48000
items, T = build()
N = int((T + 0.5) * SR)
def load(f, ch=1):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True).stdout
    a = np.frombuffer(r, np.float32).astype(np.float64)
    return a.reshape(-1, ch) if ch > 1 else a
V = load('voice_proc.wav')
rng = np.random.default_rng(11)
# ---------- voice assembly ----------
voice = np.zeros(N)
FADE = int(0.025 * SR)
for it in items:
    if it['kind'] not in ('hook', 'answer'): continue
    for p in it['parts']:
        a = int(p['src_in'] * SR); b = int(min(p['src_out'], p['a_out']) * SR)
        seg = V[a:b].copy()
        f_in = FADE; f_out = int(0.12 * SR) if p['a_out'] < p['src_out'] else FADE
        if it.get('last'): f_out = int(0.6 * SR)
        seg[:f_in] *= np.sin(np.linspace(0, np.pi / 2, f_in)) ** 2
        seg[-f_out:] *= np.cos(np.linspace(0, np.pi / 2, f_out)) ** 2
        o = int(p['out_in'] * SR); voice[o:o + len(seg)] += seg
# normalise speech to a consistent level (speech-gated RMS -> -20 dBFS)
fr = int(0.05 * SR); e = np.sqrt(np.convolve(voice ** 2, np.ones(fr) / fr, 'same'))
g = e > 10 ** (-45 / 20) * np.abs(voice).max() * 3
rms = np.sqrt((voice[g] ** 2).mean()); voice *= 10 ** (-20 / 20) / rms
print('voice gated rms set; peak dB', 20 * np.log10(np.abs(voice).max()))
# ---------- music automation ----------
st = {k: np.load(f'stems/{k}.npy').astype(np.float64)[:N] for k in ['pad', 'ep', 'bass', 'drums', 'bell']}
for k in st:
    if len(st[k]) < N: st[k] = np.pad(st[k], ((0, N - len(st[k])), (0, 0)))
t = np.arange(N) / SR
def curve(keys):
    ks = sorted(keys); xs = [k[0] for k in ks]; ys = [k[1] for k in ks]
    return np.interp(t, xs, ys)
bed = []; drums = []; bellk = []; bassk = []
R = 0.45
reflective = {('answer', 4), ('follow', 4), ('card', 5), ('answer', 5)}
for it in items:
    s, e_ = it['start'], it['end']; kind = it['kind']; n = it.get('n')
    if kind == 'hook': lv, dr, bl, bs = 0.55, 0.0, 0.0, 0.0
    elif kind == 'title': lv, dr, bl, bs = 1.0, 1.0, 1.0, 1.0
    elif kind in ('card', 'follow'): lv, dr, bl, bs = (0.9 if kind == 'card' else 0.6), 0.8, 1.0, 1.0
    elif kind == 'answer': lv, dr, bl, bs = 0.21, 0.45, 0.0, 0.8
    else: lv, dr, bl, bs = 0.9, 0.0, 1.0, 0.6
    if (kind, n) in reflective and kind != 'end': dr *= 0.0 if kind == 'answer' else 0.4; bs *= 0.6
    for (arr, v) in ((bed, lv), (drums, dr), (bellk, bl), (bassk, bs)):
        arr += [(s + 0.02, v), (e_ - 0.02, v)]
endT = T
bed += [(0, 0.0), (0.6, 0.55), (endT - 2.0, 0.85), (endT + 0.4, 0.0)]
BED = curve(bed); DR = curve(drums); BL = curve(bellk); BS = curve(bassk)
# smooth automation (300 ms)
def smooth(x, sec=0.3):
    k = int(sec * SR / 50); xs = x[::50]; xs = np.convolve(np.pad(xs, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    return np.interp(np.arange(len(x)), np.arange(len(xs)) * 50, xs)
BED, DR, BL, BS = [smooth(x) for x in (BED, DR, BL, BS)]
music = st['pad'] * 0.9 + st['ep'] * 0.75 + st['bass'] * BS[:, None] * 0.75 + st['drums'] * DR[:, None] * 0.9 + st['bell'] * BL[:, None] * 0.8
music *= BED[:, None]
# speech-driven ducking (extra up to -5 dB)
ve = np.sqrt(np.convolve(voice ** 2, np.ones(int(0.2 * SR)) / int(0.2 * SR), 'same'))
duck = 1 - 0.45 * np.clip(ve / (np.percentile(ve[ve > 1e-4], 70) + 1e-9), 0, 1)
duck = smooth(duck, 0.15)
music *= duck[:, None]
# ---------- SFX ----------
sfx = np.zeros((N, 2))
def fftf(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); H = np.ones_like(f)
    if hi: H /= np.sqrt(1 + (f / hi) ** 4)
    if lo: H /= np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X * H, n)
def whoosh(d=0.55, lo=300, hi=5000, up=False):
    n = int(d * SR); tt = np.arange(n) / SR; nz = rng.standard_normal(n)
    # sweep via chunks of bandpass
    out = np.zeros(n); K = 12
    for k in range(K):
        a, b = k * n // K, (k + 1) * n // K
        frac = k / (K - 1); fc = (lo * (hi / lo) ** (frac if up else 1 - frac))
        out[a:b] = fftf(nz, lo=fc * 0.6, hi=fc * 1.6)[a:b]
    env = np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 2
    return out * env
def riser(d=1.3):
    n = int(d * SR); tt = np.arange(n) / SR
    w = whoosh(d, 400, 7000, up=True) * (tt / d) ** 2.2
    tone = np.sin(2 * np.pi * np.cumsum(220 + 440 * (tt / d) ** 2) / SR) * 0.08 * (tt / d) ** 3
    return w + tone
def tick():
    n = int(0.08 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 90) * 0.5 + np.sin(2 * np.pi * 3600 * tt) * np.exp(-tt * 120) * 0.25
def boom():
    n = int(1.6 * SR); tt = np.arange(n) / SR
    f = 42 + 30 * np.exp(-tt * 8); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.6)
    sh = fftf(rng.standard_normal(n), lo=4000, hi=12000) * np.exp(-tt * 3) * 0.15
    return s + sh
def put(sig, at, g, pan=0.0):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    sig = sig[:N - i]; l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
    sfx[i:i + len(sig), 0] += sig * g * l; sfx[i:i + len(sig), 1] += sig * g * r
for k, it in enumerate(items):
    if it['kind'] in ('card', 'follow', 'title', 'end'):
        s = it['start']; big = it['kind'] in ('card', 'title', 'end')
        if it['kind'] != 'title': put(riser(1.2), s - 1.2, 0.05 if big else 0.03)
        put(whoosh(0.5, 2500, 300), s - 0.12, 0.07 if big else 0.045, -0.2)
        if it['kind'] == 'card':
            put(tick(), s + 0.38, 0.05, 0.3); put(tick(), s + 0.62, 0.035, -0.3)
        nxt = items[k + 1] if k + 1 < len(items) else None
        if nxt and nxt['kind'] in ('answer',):
            put(whoosh(0.45, 400, 3500, up=True), nxt['start'] - 0.3, 0.04, 0.2)
    if it['kind'] == 'title': put(boom(), it['start'] - 0.02, 0.22)
    if it['kind'] == 'end': put(boom(), it['start'] + 1.45, 0.12)
music_out = music * 0.55 * 0.40
mix = voice[:, None] + music_out + sfx
np.save('voice_track.npy', voice.astype(np.float32))
def wr(name, x):
    x = np.asarray(x, np.float32)
    if x.ndim == 1: x = np.stack([x, x], 1)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', name], input=x.tobytes(), check=True)
wr('stem_voice.wav', voice); wr('stem_music.wav', music_out); wr('stem_sfx.wav', sfx); wr('mix_raw.wav', mix)
print('peak mix dB', 20 * np.log10(np.abs(mix).max()))
