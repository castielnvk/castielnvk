"""Audio for the 'Zəfər Günü' edit: original voices (light cleanup only) + original score + subtle sound design.
Usage: python mix_audio.py SOURCE.mov SCORE.wav OUT.wav"""
import subprocess, sys, numpy as np

SR = 48000; TOTAL = 128.8
def load(path, extra=()):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, *extra, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

# Voice cleanup: rumble high-pass, gentle broadband denoise, light de-ess. No reverb, no heavy NR.
voice_src = load(sys.argv[1], ['-af', 'highpass=f=75,afftdn=nr=6:nf=-42:tn=1,deesser=i=0.15,'
                                     'equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3500:t=q:w=1.5:g=1'])
voice_src = np.repeat(voice_src.mean(1, keepdims=True), 2, 1)          # centred dialogue

out_len = int(TOTAL * SR)
voice = np.zeros((out_len, 2), np.float32)
def place(src_a, src_b, ot, fin=0.012, fout=0.012):
    a, b = int(round(src_a * SR)), int(round(src_b * SR)); seg = voice_src[a:b].copy()
    n = len(seg); fi, fo = int(fin * SR), int(fout * SR)
    seg[:fi] *= np.linspace(0, 1, fi)[:, None]; seg[n - fo:] *= np.linspace(1, 0, fo)[:, None]
    o = int(round(ot * SR)); voice[o:o + n] += seg
place(0.0, 59.4, 0.0, fin=0.002)
place(59.4, 103.6333, 61.8)
place(106.5, 120.8667, 106.0333, fout=0.05)

# Loudness: bring dialogue to ~-16 LUFS integrated with a gentle leveller (measured, not guessed)
def lufs(x):
    r = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'ebur128', '-f', 'null', '-'],
                       input=x.astype(np.float32).tobytes(), capture_output=True).stderr.decode()
    return float(r.split('Integrated loudness:')[1].split('I:')[1].split('LUFS')[0])
speech_mask = np.abs(voice[:, 0]) > 0
g = 10 ** ((-16.0 - lufs(voice[speech_mask])) / 20)
voice *= g

# voice activity envelope (for gentle music ducking)
hop = SR // 100
env = np.sqrt(np.convolve(voice[:, 0] ** 2, np.ones(hop * 4) / (hop * 4), 'same'))
vad = (env > 10 ** (-38 / 20)).astype(np.float32)
k = np.ones(int(0.35 * SR)) / int(0.35 * SR)
vad = np.clip(np.convolve(vad, k, 'same') * 1.6, 0, 1)

# Music: score with a hand-set level curve (dB) + light ducking under words
music = load(sys.argv[2])[:out_len]
music = np.pad(music, ((0, out_len - len(music)), (0, 0)))
pts = [(0.0, -2), (33.0, -2), (34.0, 1.5), (35.3, 1.5), (36.5, -3),        # breath between President and Elnarə
       (58.9, -3), (59.5, 4.5), (61.4, 4.5), (62.4, -4),                  # title break swell
       (99.0, -6), (105.9, -7.5), (106.2, -7.5), (119.6, -8),
       (120.45, -1), (121.5, 1), (128.8, 1)]                              # music rises at the conclusion
t = np.arange(out_len) / SR
curve = np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
duck = -3.0 * vad
mg = 10 ** ((curve + duck) / 20)
music *= mg[:, None]
fade_end = np.clip((TOTAL - t) / 1.6, 0, 1); music *= fade_end[:, None] ** 1.5

# Sound design (soft, airy – no impacts over words)
rng = np.random.default_rng(11)
def swell(at, dur, peak_db, lp_hz=3500, rise=0.75):
    n = int(dur * SR); x = rng.normal(0, 1, (n, 2)).astype(np.float32)
    # one-pole low-pass, cutoff opening during the swell
    y = np.zeros_like(x); a0 = np.exp(-2 * np.pi * lp_hz / SR)
    for i in range(1, n):
        y[i] = a0 * y[i - 1] + (1 - a0) * x[i]
    tt = np.linspace(0, 1, n)
    shape = np.where(tt < rise, (tt / rise) ** 2, ((1 - tt) / (1 - rise)) ** 1.5)
    y *= (shape * 10 ** (peak_db / 20) / (np.abs(y).max() + 1e-9))[:, None]
    o = int(at * SR); return o, y
sd = np.zeros_like(music)
for at, dur, pk, lp in [(58.95, 1.3, -30, 2800), (120.35, 2.2, -29, 3200)]:
    o, y = swell(at, dur, pk, lp); sd[o:o + len(y)] += y
# shimmer on the title (high, quiet sine cluster)
for at, dur, pk in [(59.45, 2.6, -36), (122.2, 4.0, -35)]:
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * tt + ph) for f, ph in [(1174.7, 0), (1479.98, 1), (1760, 2), (2349.3, .5)]) / 4
    s *= np.exp(-tt * 1.4) * (1 - np.exp(-tt * 18)) * 10 ** (pk / 20)
    o = int(at * SR); sd[o:o + n] += np.stack([s * 0.9, s * 1.1], 1)

mix = voice + music + sd
peak = np.abs(mix).max()
if peak > 0.89: mix *= 0.89 / peak                       # ~-1 dBTP safety
raw = mix.astype(np.float32).tobytes()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                '-af', 'alimiter=limit=0.89:attack=3:release=60:level=disabled', '-c:a', 'pcm_s24le', sys.argv[3]],
               input=raw, check=True)
print('voice gain dB', round(20 * np.log10(g), 2), 'peak', round(float(peak), 3))
