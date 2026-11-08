# Original score + sound design for «Məlal» (edited timeline, seconds)
import numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt
SR = 48000; DUR = 59.4; N = int(SR * DUR)
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

# ================= SCORE =================
mus = Bus()
D = 50  # D3 reference
# chords (MIDI): Dm, Bb, F, C, Gm, A, Dmaj, Dm(add9)
CH = {'Dm': [50, 57, 62, 65], 'Bb': [46, 58, 62, 65], 'F': [53, 57, 60, 65], 'C': [48, 55, 60, 64], 'Gm': [43, 55, 58, 62], 'A': [45, 57, 61, 64], 'D': [50, 57, 62, 66], 'Dm9': [50, 57, 64, 65]}
def arp(t0, chord, beats=4, step=0.5, vel=0.4, top=True, pan=0.0):
    ns = CH[chord]; seq = [ns[0], ns[1], ns[2], ns[3], ns[2], ns[1], ns[2], ns[3]]
    for i in range(int(beats / step)):
        n = seq[i % len(seq)] + 12; mus.put(t0 + i * step, piano(n, 3.0, vel * (0.85 + 0.15 * rng.random())), 1, pan + 0.25 * np.sin(i))
    mus.put(t0, piano(ns[0] - 12, 5.0, vel * 1.1), 1)
# 0–2.2: a single low D under the rain, shimmer at the word
mus.put(0.05, piano(38, 6, 0.5), 0.9)
mus.put(1.45, piano(74, 4, 0.35), 0.6, 0.3); mus.put(1.6, piano(81, 4, 0.3), 0.4, -0.3)
mus.put(0.0, pad([50, 57, 64], 4.5, att=1.5, rel=2.5, bright=700), 0.9)
# 2.2–12.9: gentle arpeggios (Dm – Bb – F – C – Dm), könül warms at 11.7
for i, ch in enumerate(['Dm', 'Bb', 'F', 'C']):
    arp(2.2 + i * 2.6, ch, beats=2.6, step=0.65, vel=0.34)
    mus.put(2.2 + i * 2.6, pad([n for n in CH[ch][1:]], 3.6, att=1.2, rel=1.6, bright=650), 0.8)
mus.put(12.6, pad([46, 53, 62, 69], 2.0, att=0.5, rel=1.4, bright=800), 0.9)   # könül lift (Bb add9) – fades at clinical cut
mus.put(11.5, piano(69, 3, 0.4), 0.7)
# 12.9–17.9: clinical — piano stops; cold sterile pulse
pt = tt(5.0); pulse = np.sin(2 * np.pi * 880 * pt) * (np.sin(2 * np.pi * 2 * pt) > 0.92) * 0.1
pulse += np.sin(2 * np.pi * 110 * pt) * 0.05 * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * pt)); pulse *= env_ar(len(pt), 0.2, 1.0)
mus.put(12.95, lpf(pulse, 5000), 0.9)
mus.put(12.95, pad([62, 69], 5.0, att=0.3, rel=1.0, bright=2500, det=0.002), 0.35)
# 17.9–21.8: ancients — warm low drone (D + A), slow
mus.put(17.9, drone(38, 11.0, att=1.2, rel=3.5), 1.0, -0.2); mus.put(18.2, drone(45, 10.5, att=1.8, rel=3.5), 0.8, 0.2)
mus.put(18.6, piano(62, 4, 0.3), 0.6); mus.put(20.4, piano(65, 4, 0.28), 0.55)
# 21.8–28.7: noise — slight dissonance (Eb) creeps in, then thins to one sustained note
mus.put(23.6, drone(51, 2.6, att=1.0, rel=1.2, bright=1400), 0.55, 0.4)
mus.put(26.0, pad([62, 69], 3.4, att=1.0, rel=1.6, bright=500), 0.8)
# 28.7–35: fullness — piano returns, warmer, swelling (Bb – F – Gm – A)
for i, ch in enumerate(['Bb', 'F', 'Gm', 'A']):
    arp(28.7 + i * 1.6, ch, beats=1.6, step=0.4, vel=0.32 + 0.04 * i)
    mus.put(28.7 + i * 1.6, pad(CH[ch][1:], 2.4, att=0.6, rel=1.2, bright=800 + 150 * i), 0.8)
mus.put(35.0, piano(57, 3, 0.25), 0.35)  # the last word before silence
# 35.1–39.5: sükut — almost nothing. a very low D, barely there; dive swell at "dərin"
mus.put(35.4, drone(26, 5.0, att=2.5, rel=1.5, bright=250), 0.45)
mus.put(38.0, pad([38, 45, 50], 3.0, att=1.2, rel=1.2, bright=300), 1.0)
# 39.5–50.5: rising warmth: F – C – Dm – Bb, then D major on "qorxmayın"
for i, ch in enumerate(['F', 'C', 'Dm']):
    arp(39.6 + i * 1.33, ch, beats=1.33, step=0.44, vel=0.3)
    mus.put(39.6 + i * 1.33, pad(CH[ch][1:], 2.2, att=0.6, rel=1.0, bright=900), 0.8)
mus.put(43.55, pad(CH['D'], 3.5, att=0.4, rel=2.0, bright=1300), 1.0); mus.put(43.55, piano(66 + 12, 4, 0.36), 0.7); mus.put(43.55, piano(38, 5, 0.5), 0.9)
for i, ch in enumerate(['Bb', 'F', 'C', 'D']):
    arp(45.0 + i * 1.4, ch, beats=1.4, step=0.7, vel=0.28)
    mus.put(45.0 + i * 1.4, pad(CH[ch][1:], 2.2, att=0.8, rel=1.2, bright=800), 0.75)
# 50.5–59.4: word settles; Dm(add9) – Bb – Dm, fading with the rain
for i, ch in enumerate(['Dm9', 'Bb', 'Dm9']):
    arp(50.6 + i * 2.6, ch, beats=2.6, step=0.65, vel=0.3 - 0.04 * i)
    mus.put(50.6 + i * 2.6, pad(CH[ch][1:], 3.6, att=1.0, rel=2.0, bright=650), 0.75)
mus.put(56.2, pad([50, 57, 64, 69], 3.2, att=0.8, rel=2.6, bright=700), 0.8); mus.put(56.2, piano(74, 3.2, 0.3), 0.5)
mL, mR = reverb(mus.L, mus.R, 4.2, 0.42, 2600)
fade = np.ones(N); fi = int(1.0 * SR); fade[-fi:] = np.linspace(1, 0, fi) ** 2; mL *= fade; mR *= fade

# ================= SOUND DESIGN =================
fx = Bus()
fx.put(0.0, rainbed(3.6, 1.0) * env_ar(int(3.6 * SR), 0.05, 2.0), 0.55)
fx.put(1.42, bell(1175, 3.0), 0.5, 0.0); fx.put(1.5, drop(900, 0.8), 0.6, 0)                      # word formed + ripple
fx.put(2.0, whoosh(1.1, 300, 2400, 0.25), 0.6)                                                  # lift
fx.put(3.05, drop(1300, 0.5), 0.5, 0)                                                           # drop slides down the thread
fx.put(3.9, bell(1568, 2.0, 0.6), 0.25, -0.5); fx.put(4.66, bell(1397, 2.0, 0.6), 0.25, 0.5)    # şairanə / kübar
fx.put(6.22, drop(700, 1.0), 0.8, 0.25); fx.put(6.25, bpf(noise(0.6), 300, 1800) * np.exp(-tt(0.6) * 6) * 0.15, 0.6, 0.25)  # kədər drop
sq = whoosh(1.1, 900, 160, 0.4); fx.put(6.46, sq, 0.6); fx.put(7.4, thump(48, 0.6, 0.6), 0.6)   # sıxıntı tightening
fx.put(7.35, thump(55, 0.4, 0.7), 0.6); fx.put(8.25, thump(52, 0.4, 0.5), 0.45)                  # tired heartbeat
fx.put(10.3, whoosh(0.8, 2500, 800, 0.2), 0.5)                                                  # "deyil" – letters hollow out
fx.put(11.65, pad([62, 69, 74], 2.0, att=0.3, rel=1.5, bright=1600), 0.6)                       # könül warm swell
cr = np.zeros(int(1.8 * SR))
for _ in range(14): i = rng.integers(0, len(cr) - 800); cr[i:i + 600] += click(0.0125, 0.25, 1800 + rng.random() * 2000)[:600]
fx.put(11.8, cr, 0.5)
for st in (13.96, 14.66): fx.put(st - 0.02, thump(90, 0.25, 0.9) + np.pad(click(0.05, 0.9, 1800), (0, int(0.2 * SR))), 0.6)   # stamps
for i in range(26):  # capsules landing
    d0 = 15.94 - 0.2 + rng.random() * 0.7; fx.put(d0 + 0.62 + rng.random() * 0.05, click(0.03, 0.35, 3500 + rng.random() * 2500), 0.55, rng.random() * 1.2 - 0.6)
fx.put(16.85, whoosh(1.0, 400, 6000, 0.5), 0.6, -0.4)                                           # tez keçib getsin — swipe
fx.put(18.15, bpf(noise(0.35), 1500, 7000) * np.exp(-tt(0.35) * 9), 0.35, 0.1)                  # match strike
fx.put(18.25, whoosh(0.9, 200, 900, 0.5), 0.45)                                                 # flame takes
crk = np.zeros(int(3.4 * SR))
for _ in range(30): i = rng.integers(0, len(crk) - 800); crk[i:i + 600] += click(0.0125, 0.18, 1200 + rng.random() * 1500)[:600]
fx.put(18.4, crk, 0.4)
mur = np.zeros(int(3.2 * SR)); mt = tt(3.2)
for k in range(9):  # world's murmur: modulated vocal-band noise
    mur += bpf(noise(3.2), 250 + 180 * k, 400 + 200 * k) * (0.5 + 0.5 * np.sin(2 * np.pi * (3 + rng.random() * 5) * mt + rng.random() * 6))
mur *= np.minimum(1, mt / 1.6) * np.where(mt > 2.0, np.exp(-(mt - 2.0) * 3.5), 1)
fx.put(23.2, lpf(mur, 3000) * 0.5, 0.35)
fx.put(25.5, whoosh(1.0, 3000, 200, 0.4), 0.45)                                                 # receding inward
fx.put(27.0, bell(1760, 2.5, 0.5), 0.25, 0.0); fx.put(27.3, bell(880, 2.5, 0.5), 0.2, 0.0)       # light meets its reflection
ht = tt(1.4); hollow = bpf(noise(1.4), 380, 460, 2) * np.sin(np.pi * ht / 1.4) ** 2
fx.put(29.0, hollow * 2.0, 0.5)                                                                 # boşluq — hollow
pour = np.zeros(int(1.4 * SR))
for _ in range(40): i = rng.integers(0, len(pour) - 6000); b = drop(400 + rng.random() * 900, 0.3); pour[i:i + len(b)] += b
fx.put(30.25, lpf(pour, 4000) + lpf(noise(1.4), 900) * 0.04 * np.sin(np.pi * tt(1.4) / 1.4), 0.6)  # doluluq — filling
fx.put(31.0, bell(1318, 2.5, 0.6), 0.25)                                                        # circle becomes heart
for i in range(40):  # words dropping into the heart: soft paper flutters
    st = 31.52 + (34.32 - 0.4 - 31.52) * i / 40 + 0.45
    fx.put(st, bpf(noise(0.06), 2000, 7000) * np.exp(-tt(0.06) * 60) * 0.25, 0.4, rng.random() * 0.8 - 0.4)
fx.put(34.6, bell(587, 4.0, 0.5), 0.3)                                                          # qalmaz — settle into silence
fx.put(38.05, lpf(whoosh(1.4, 200, 1200, 0.8), 700), 0.9); fx.put(38.1, thump(40, 1.2, 0.5), 0.5)  # plunge
bub = np.zeros(int(1.6 * SR))
for _ in range(18): i = rng.integers(0, len(bub) - 6000); b = drop(300 + rng.random() * 500, 0.35); bub[i:i + len(b)] += b
fx.put(38.4, lpf(bub, 2000), 0.45)
fx.put(39.4, lpf(whoosh(1.2, 150, 900, 0.5), 1200), 0.5)                                         # rising
fx.put(42.3, crk[:int(1.3 * SR)], 0.35)                                                          # ember wakes
for st, f, pn in [(45.6, 1047, 0.15), (46.25, 784, -0.15), (47.5, 1175, 0.15), (48.65, 880, -0.15)]:
    fx.put(st, bell(f, 3.0, 0.45), 0.2, pn)                                                      # the silent dialogue
for i in range(5): fx.put(50.9 + i * 0.3 + 0.7, drop(1000 - i * 90, 0.9), 0.55, (i - 2) / 3)     # letters land on water
fx.put(55.0, rainbed(4.4, 1.0) * env_ar(int(4.4 * SR), 1.5, 1.5), 0.45)
fx.put(56.1, bell(1397, 3.0, 0.5), 0.25); fx.put(56.25, bell(2093, 3.0, 0.4), 0.15)            # end card
fL, fR = reverb(fx.L, fx.R, 2.2, 0.25, 6000)

def save(name, L, R, peak=None):
    st = np.stack([L, R], 1)
    w = wave.open(name, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
pk = max(np.abs(mL).max(), np.abs(mR).max()); save('music.wav', mL / pk * 0.7, mR / pk * 0.7)
pk = max(np.abs(fL).max(), np.abs(fR).max()); save('sfx.wav', fL / pk * 0.7, fR / pk * 0.7)
print('ok')
