# Original score + sound design for «Zənəxdan» (edited timeline, seconds)
exec(open('../audiolib.py').read())
DUR = 58.7; N = int(SR * DUR)
import json; LINES = json.loads(open('proj/data.js').read().split('const LINES=')[1].rstrip(';\n'))

def guitar(note, dur=2.6, vel=0.5):
    out = np.zeros(int(dur * SR)); f = hz(note); L = int(SR / f); n = len(out)
    y = np.zeros(n + L + 1); y[1:L + 1] = lpf(rng.standard_normal(L) * vel, 1800 + 2500 * vel, 1)
    d = 0.5 * 0.9975
    for k in range(1, (n // L) + 1):
        a = k * L + 1; b = min(a + L, n + 1); y[a:b] = d * (y[a - L:b - L] + y[a - L - 1:b - L - 1])
    out = y[1:n + 1] * np.exp(-tt(dur) * 0.9); out = lpf(out, 3500)
    out[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR)); return out * 0.6
def glock(note, dur=2.2, vel=0.5):
    t = tt(dur); f = hz(note)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)) * np.minimum(1, t / 0.002) * vel * 0.28
def marimba(note, vel=0.5):
    t = tt(0.9); f = hz(note); return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 20)) * np.exp(-t * 6) * vel * 0.4

mus = Bus()
CH = {'G': [43, 55, 59, 62, 67], 'Em': [40, 52, 55, 59, 64], 'C': [36, 52, 55, 60, 64], 'D': [38, 54, 57, 62, 66], 'Am': [45, 52, 57, 60, 64], 'F': [41, 53, 57, 60, 65], 'Bm': [47, 54, 59, 62, 66]}
def strum(t0, ch, beats, step=0.33, vel=0.4, pat=(0, 2, 3, 4, 3, 2)):
    ns = CH[ch]; mus.put(t0, guitar(ns[0], 3.2, vel * 1.1), 1)
    for i in range(int(beats / step)):
        if i == 0: continue
        n = ns[1 + pat[i % len(pat)] % 4]; mus.put(t0 + i * step, guitar(n, 2.2, vel * (0.75 + 0.25 * rng.random())), 1, 0.35 * np.sin(i * 1.3))
# 0–8.4 verse: a gentle old-song guitar under the poetry
for i, ch in enumerate(['G', 'Em', 'C', 'D']): strum(0.05 + i * 2.1, ch, 2.1, 0.35, 0.34)
mus.put(6.66, glock(83, 2.0, 0.35), 0.8, 0.3)                       # zənəxdana — a small bright note
# 8.4–12.5: rising to the word
mus.put(8.4, pad([55, 59, 62, 67], 4.2, att=1.5, rel=1.5, bright=900), 0.8); strum(8.4, 'C', 3.2, 0.4, 0.3)
for i, n in enumerate([67, 71, 74, 79, 83]): mus.put(11.4 + i * 0.07, glock(n, 2.0, 0.4), 0.8, (i - 2) / 3)
# 12.5–18.3: meaning; the smile on "güləndə" lifts in glockenspiel
for i, ch in enumerate(['G', 'D', 'Em', 'C']): strum(12.5 + i * 1.45, ch, 1.45, 0.36, 0.3); mus.put(12.5 + i * 1.45, pad(CH[ch][1:4], 2.2, att=0.6, rel=1.0, bright=800), 0.6)
for i, n in enumerate([71, 74, 79]): mus.put(15.36 + i * 0.12, glock(n, 2.0, 0.42), 0.8)
# 18.3–24.6: traffic — muted, cool; a low ticking pulse in E minor; the frown descends
mus.put(18.3, pad([40, 47, 52], 6.4, att=0.6, rel=1.2, bright=420), 0.9)
for tb in np.arange(18.4, 24.4, 0.5): mus.put(tb, thump(52, 0.25, 0.35), 1)
for i, n in enumerate([64, 62, 59, 55, 52]): mus.put(23.04 + i * 0.26, guitar(n, 1.8, 0.35), 1)
# 24.6–33: doors open onto warmth — C → G, full smile on "təbəssüm"
mus.put(24.6, pad([40, 47, 52, 55], 2.2, att=0.4, rel=1.0, bright=500), 0.7)
mus.put(26.7, pad([48, 55, 60, 64, 67], 3.0, att=0.5, rel=1.5, bright=1300), 0.9); strum(26.78, 'C', 2.0, 0.33, 0.36)
strum(28.8, 'Am', 1.6, 0.33, 0.33); strum(30.4, 'D', 1.7, 0.33, 0.35)
mus.put(32.1, pad(CH['G'][1:], 3.0, att=0.2, rel=1.8, bright=1500), 1.0); strum(32.12, 'G', 1.3, 0.22, 0.4)
for i, n in enumerate([74, 79, 83, 86]): mus.put(32.12 + i * 0.09, glock(n, 2.2, 0.42), 0.8, (i - 1.5) / 2)
# 33–39.6: tension knot — a trembling cluster, released into G on "gülümsəmək"
tm = tt(4.6); trem = (np.sin(2 * np.pi * hz(57) * tm) + np.sin(2 * np.pi * hz(58) * tm) + 0.6 * np.sin(2 * np.pi * hz(45) * tm)) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tm)) * env_ar(len(tm), 0.8, 0.5) * 0.06
mus.put(33.5, lpf(trem, 2500), 1)
mus.put(38.2, pad(CH['G'][1:], 2.6, att=0.15, rel=1.6, bright=1400), 1.0); strum(38.24, 'G', 1.4, 0.28, 0.38)
for i, n in enumerate([67, 71, 74, 79]): mus.put(38.24 + i * 0.1, glock(n, 2.0, 0.4), 0.8)
# 39.5–49.6: warmth — C G Am F C G
for i, ch in enumerate(['C', 'G', 'Am', 'F', 'C', 'G']):
    strum(39.6 + i * 1.66, ch, 1.66, 0.33, 0.3); mus.put(39.6 + i * 1.66, pad(CH[ch][1:4], 2.4, att=0.6, rel=1.0, bright=800), 0.6)
mus.put(45.86, glock(79, 2.0, 0.4), 0.8); mus.put(48.4, glock(83, 2.4, 0.4), 0.8); mus.put(48.52, glock(86, 2.4, 0.35), 0.7)
# 49.4–58.7: the word smiles — one note per letter, then the closing chord
for i, n in enumerate([67, 69, 71, 74, 76, 79, 81, 83]): mus.put(50.45 + i * 0.19 + 0.6, glock(n, 2.0, 0.38), 0.8, (i - 3.5) / 5)
strum(50.0, 'G', 2.6, 0.4, 0.28); strum(52.6, 'C', 1.6, 0.4, 0.26); strum(54.2, 'D', 1.5, 0.4, 0.26)
mus.put(55.8, pad([43, 55, 59, 62, 67, 71], 2.9, att=0.4, rel=2.0, bright=1100), 1.0); strum(55.8, 'G', 1.0, 0.18, 0.34)
mL, mR = reverb(mus.L, mus.R, 2.8, 0.32, 3500)
fade = np.ones(N); fi = int(0.8 * SR); fade[-fi:] = np.linspace(1, 0, fi) ** 2; mL *= fade; mR *= fade

# ================= SOUND DESIGN =================
fx = Bus()
def nib(d=0.25, g=1.0):  # pen nib on paper
    x = bpf(noise(d), 2500, 9000) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 14 * tt(d)))); return x * np.sin(np.linspace(0, np.pi, len(x))) * g
def silk(d, g=1.0):  # soft brush: low band, smooth swell, no hiss
    x = lpf(bpf(noise(d), 600, 2600), 2200); return x * np.sin(np.linspace(0, np.pi, len(x))) ** 3 * g
def creak(d=0.8, f0=120, f1=200, g=1.0):
    t = tt(d); f = np.linspace(f0, f1, len(t)); saw = ((np.cumsum(f) / SR) % 1) * 2 - 1
    grain = (rng.random(len(t)) < 0.02) * 1.0
    return bpf(saw * (0.4 + lpf(grain, 60) * 30), 300, 2400) * np.sin(np.linspace(0, np.pi, len(t))) * g
def slide(f0, f1, d=1.2, g=1.0):
    t = tt(d); f = np.geomspace(f0, f1, len(t)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.linspace(0, np.pi, len(t))) * g * 0.3
fx.put(0.02, thump(180, 0.2, 0.4) + np.pad(bpf(noise(0.05), 1500, 6000) * 0.3, (0, int(0.15 * SR))), 0.5)   # the quotation mark — an ink dab
fx.put(0.3, lpf(nib(1.3, 0.5), 3500), 0.15)                                                  # "Molla Vəli Vidadi" written
for w in LINES[1]['w'] + LINES[2]['w']: fx.put(w[1], lpf(nib(0.22, 0.45), 3500), 0.12, rng.random() * 0.6 - 0.3)
fx.put(2.3, silk(1.8, 0.4), 0.22); fx.put(5.2, silk(2.0, 0.3), 0.18)                # strands fall
fx.put(7.0, bell(2637, 1.4, 0.4), 0.2)                                            # the dimple
pt = bpf(noise(1.2), 400, 5000) * (rng.random(int(1.2 * SR)) < 0.15) * np.sin(np.linspace(0, np.pi, int(1.2 * SR)))
fx.put(8.9, pt + whoosh(1.2, 600, 2500, 0.25), 0.4)                               # paper gives way to dawn
fx.put(11.2, whoosh(0.8, 500, 3500, 0.35), 0.45)                                  # the word lifts
fx.put(11.75, silk(0.9, 0.5), 0.25)                                               # the fine line is drawn
fx.put(15.36, slide(600, 1100, 0.5, 0.8), 0.5); fx.put(15.92, bell(3136, 1.0, 0.35), 0.18, -0.4); fx.put(16.0, bell(3136, 1.0, 0.35), 0.18, 0.4)  # smile + dimples
amb = lpf(noise(6.4), 220) * 0.6 + bpf(noise(6.4), 300, 1200) * 0.08
fx.put(18.3, amb * env_ar(len(amb), 1.0, 1.2), 0.5)                               # traffic hum
for st, f in [(19.6, 392), (21.0, 349)]: hn = tt(0.45); fx.put(st, lpf((np.sign(np.sin(2 * np.pi * f * hn)) * 0.3) * env_ar(len(hn), 0.02, 0.15), 1500), 0.12, 0.6)  # distant horns
for k in range(8): fx.put(20.4 + k * 0.42, click(0.03, 0.4, 1800), 0.25)          # indicator
fx.put(23.04, slide(500, 160, 1.4, 1.0), 0.5); fx.put(24.1, thump(60, 0.4, 0.6), 0.45)   # the smile droops, drags down
fx.put(25.38, creak(0.6, 100, 130, 0.35), 0.4); fx.put(26.78, creak(1.0, 90, 70, 0.45), 0.45); fx.put(26.8, whoosh(1.4, 300, 1500, 0.35), 0.4)   # doors open, light
zz = bpf(noise(1.0), 800, 4000) * (np.abs(((tt(1.0) * 12) % 1) - 0.5) * 2); fx.put(27.8, zz * 0.5, 0.35)   # jagged
fx.put(28.82, whoosh(1.0, 1500, 500, 0.3), 0.35)                                  # softening
for i, f in enumerate([1568, 1976, 2349]): fx.put(31.46 + i * 0.08, bell(f, 2.2, 0.4), 0.15, (i - 1) / 2)
fx.put(33.5, creak(2.8, 160, 220, 0.3), 0.35)                                     # rope under tension
mur = sum(bpf(noise(1.4), 400 + 250 * k, 650 + 300 * k) * (0.5 + 0.5 * np.sin(2 * np.pi * (4 + k) * tt(1.4))) for k in range(5))
fx.put(35.7, mur * np.sin(np.linspace(0, np.pi, len(mur))) * 0.2, 0.35)          # long words
fx.put(38.1, whoosh(1.1, 1800, 400, 0.4), 0.4); fx.put(38.3, creak(0.5, 200, 90, 0.25), 0.3)   # knot released
fx.put(41.86, mur[:int(1.4 * SR)] * 0.15, 0.3); fx.put(43.28, whoosh(1.0, 400, 3000, 0.45), 0.4)   # worries crowd, pushed away
fx.put(45.86, bell(2637, 1.4, 0.4), 0.2)
sq = bpf(noise(0.9), 1200, 3500) * (0.5 + 0.5 * np.sin(2 * np.pi * 30 * tt(0.9))); fx.put(47.5, sq * np.sin(np.linspace(0, np.pi, len(sq))) * 0.25, 0.35, 0.0)   # eraser pass
for i in range(8): fx.put(50.45 + i * 0.19 + 0.6, marimba(60 + [0, 2, 4, 7, 9, 12, 14, 16][i], 0.5), 0.45, (i - 3.5) / 5)  # letters land
fx.put(55.75, bell(1568, 2.6, 0.5), 0.2); fx.put(55.9, bell(2349, 2.6, 0.4), 0.14)
fL, fR = reverb(fx.L, fx.R, 1.8, 0.22, 6500)
def save(name, L, R):
    st = np.stack([L, R], 1); w = wave.open(name, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
pk = max(np.abs(mL).max(), np.abs(mR).max()); save('music.wav', mL / pk * 0.7, mR / pk * 0.7)
pk = max(np.abs(fL).max(), np.abs(fR).max()); save('sfx.wav', fL / pk * 0.7, fR / pk * 0.7)
print('ok')
