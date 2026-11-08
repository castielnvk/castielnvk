# Original score + sound design for «Müjgan» (original timeline, intro kept)
exec(open('audiolib.py').read())

def santur(note, dur=2.5, vel=0.5, bright=0.5):
    """Plucked/hammered string (block-vectorised Karplus–Strong), double course slightly detuned."""
    out = np.zeros(int(dur * SR))
    for det in (0.0, 0.0035):
        f = hz(note) * (1 + det); L = int(SR / f); n = len(out)
        y = np.zeros(n + L + 1)
        burst = rng.standard_normal(L) * vel
        burst = lpf(burst, 2500 + 7000 * bright, 1)
        y[1:L + 1] = burst
        d = 0.5 * (0.996 + 0.0035 * min(1, f / 1000))
        for k in range(1, (n // L) + 1):
            a = k * L + 1; b = min(a + L, n + 1)
            y[a:b] = d * (y[a - L:b - L] + y[a - L - 1:b - L - 1])
        out += y[1:n + 1]
    out *= np.exp(-tt(dur) * (0.6 + note / 120))
    out[-int(0.2 * SR):] *= np.linspace(1, 0, int(0.2 * SR))
    return out * 0.45
def pluck(note, dur=1.2, vel=0.5):  # clean modern sine pluck (salon)
    t = tt(dur); f = hz(note)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 5) * np.minimum(1, t / 0.003) * vel * 0.35
def framedrum(g=1.0, low=True):
    t = tt(0.6); body = np.sin(2 * np.pi * (70 if low else 180) * t * (1 + 0.4 * np.exp(-t * 30))) * np.exp(-t * (9 if low else 18))
    slap = bpf(noise(0.6), 800, 4000) * np.exp(-t * 60) * 0.25
    return (body + slap) * g

mus = Bus()
# D "Hijaz" colour: D Eb F# G A Bb C
HJ = [50, 51, 54, 55, 57, 58, 60, 62, 63, 66, 67, 69, 70, 72, 74]
def run(t0, notes, step, vel=0.45, pan=0.0, inst=santur, dur=2.4):
    for i, n in enumerate(notes): mus.put(t0 + i * step, inst(n, dur, vel * (0.85 + 0.2 * rng.random())), 1, pan + 0.3 * np.sin(i * 1.7))
# 0–4: opening — a tremolo roll on D grows with the golden lid; drone
mus.put(0.0, drone(38, 13.0, att=1.5, rel=4.0, bright=500), 0.9)
mus.put(0.2, drone(45, 12.5, att=2.5, rel=4.0, bright=450), 0.6, 0.2)
run(0.15, [62] * 10, 0.11, 0.18)
run(1.0, [66, 69, 74, 72, 70, 69], 0.2, 0.32)
# 4–12.8: proverb & spiral — sparse, listening
run(4.1, [62, 63, 66], 0.65, 0.3); run(5.28, [69], 1, 0.38); run(6.4, [67, 66], 0.5, 0.28)
run(7.5, [62, 66, 69, 70, 69, 66], 0.55, 0.26); run(10.6, [74, 72, 70, 69, 67, 66, 63, 62], 0.14, 0.22)
# 12.9–15: the reveal — swell, bright flourish at 14.3
mus.put(12.9, pad([50, 57, 62, 66], 4.0, att=1.2, rel=2.0, bright=900), 0.9)
run(14.25, [62, 66, 69, 74, 78, 81], 0.07, 0.4)
# 15–25.5: origin & classical poetry — santur ostinato, frame drum heartbeat from the manuscript
mus.put(15.0, drone(38, 11.0, att=1.0, rel=2.0, bright=550), 0.9); mus.put(15.0, drone(45, 11.0, att=1.5, rel=2.0, bright=500), 0.6)
pat = [50, 57, 62, 63, 62, 57, 54, 57]
for bar in range(5):
    tb = 15.1 + bar * 2.08; base = [0, 1, 0, -2, 0][bar]
    run(tb, [n + base for n in pat], 0.26, 0.3)
for k, tb in enumerate(np.arange(19.4, 25.5, 1.04)): mus.put(tb, framedrum(0.35), 1)
run(22.9, [69, 70, 72, 74, 75], 0.18, 0.35)  # lashes -> arrows rising
mus.put(23.84, pad([50, 54, 57, 62, 66], 2.4, att=0.2, rel=1.8, bright=1500), 0.7)
# 25.5–32.3: bow — tension: low pulse accelerates to the release
mus.put(25.5, drone(38, 7.0, att=0.8, rel=1.2, bright=420), 1.0)
beats = list(np.arange(26.36, 28.5, 0.52)) + list(np.arange(28.5, 30.8, 0.34))
for b in beats: mus.put(b, framedrum(0.3), 1)
run(26.36, [62, 63], 0.62, 0.3); run(27.48, [66, 67], 0.54, 0.3); run(28.58, [69, 70, 72, 74], 0.55, 0.3)
mus.put(31.28, pad([50, 54, 57, 62, 66, 69], 2.0, att=0.02, rel=1.6, bright=2200), 0.9); run(31.28, [74, 78, 81, 86], 0.06, 0.35)
# 32.3–38.4: today — clean modern plucks in D major, light pulse
salon = [62, 66, 69, 73, 74, 73, 69, 66]
for i, tb in enumerate(np.arange(32.3, 38.3, 0.375)): mus.put(tb, pluck(salon[i % 8] + 12, 1.0, 0.5), 1, 0.4 * np.sin(i))
mus.put(32.3, pad([50, 57, 61, 66], 6.4, att=0.8, rel=1.6, bright=1600, det=0.004), 0.55)
for tb in np.arange(32.3, 38.3, 0.75): mus.put(tb, thump(55, 0.3, 0.35), 1)
# 38.4–44.7: the past returns — santur and drone; boom on collapse
mus.put(38.4, drone(38, 7.0, att=0.8, rel=2.0, bright=520), 1.0); mus.put(38.6, drone(45, 6.6, att=1.2, rel=2.0, bright=480), 0.6)
run(38.6, [62, 63, 66, 67, 69, 67, 66, 63], 0.42, 0.28)
run(41.34, [74, 70, 69, 66], 0.22, 0.32)
mus.put(42.3, framedrum(0.9), 1); mus.put(42.3, pad([38, 45, 50], 2.5, att=0.02, rel=2.0, bright=300), 1.0)
run(42.86, [69, 74, 78], 0.25, 0.3)
# 44.7–50: night road — soft driving pulse, names
mus.put(44.7, pad([50, 57, 62, 65], 5.6, att=1.0, rel=1.5, bright=800), 0.8)
for i, tb in enumerate(np.arange(47.4, 50.1, 0.25)): mus.put(tb, thump(45, 0.22, 0.35 + 0.1 * (i % 2 == 0)), 1)
run(45.96, [74, 69, 72, 66, 70, 62], 0.15, 0.22)
run(49.16, [62, 66, 69, 74], 0.12, 0.35)
# 50–57.5: reflection
mus.put(50.0, pad([46, 53, 62, 65], 3.7, att=0.8, rel=1.5, bright=700), 0.85); mus.put(53.6, pad([48, 55, 60, 64], 4.0, att=0.8, rel=1.5, bright=650), 0.8)
run(50.2, [62, 65, 69, 70], 0.8, 0.26); run(53.7, [67, 64, 62], 0.9, 0.24)
# 57.5–62.6: the heart — build to release, warm resolution
mus.put(57.5, drone(38, 5.2, att=1.0, rel=1.5, bright=500), 0.9)
for tb in np.arange(58.5, 60.1, 0.4): mus.put(tb, framedrum(0.25), 1)
run(59.1, [62, 63, 66, 67, 69], 0.2, 0.28)
mus.put(60.85, pad([50, 54, 57, 62, 66, 69], 3.0, att=0.05, rel=2.2, bright=1600), 1.0); run(60.85, [74, 78, 81], 0.09, 0.35)
# 62.6–68: letters fall into place — one note per letter, rising
for i, n in enumerate([62, 66, 69, 70, 74, 78]): mus.put(63.42 + i * 0.21 + 0.52, santur(n, 2.8, 0.5), 1, (i - 2.5) / 3)
mus.put(64.95, pad([50, 57, 62, 66], 4.0, att=0.3, rel=2.5, bright=900), 0.8)
run(66.2, [69, 66, 62], 0.55, 0.22)
# 68–71.8: the closing — final D chord, shimmer
mus.put(68.5, pad([38, 50, 57, 62, 66], 3.4, att=0.3, rel=2.6, bright=900), 1.0)
run(68.55, [62, 66, 69, 74, 78, 81, 86], 0.08, 0.32)
mL, mR = reverb(mus.L, mus.R, 3.4, 0.36, 3200)
fade = np.ones(N); fi = int(0.9 * SR); fade[-fi:] = np.linspace(1, 0, fi) ** 2; mL *= fade; mR *= fade

# ================= SOUND DESIGN =================
fx = Bus()
def silk(d, g=1.0):  # lash growth: soft brushed hiss
    x = bpf(noise(d), 4000, 12000); return x * np.sin(np.linspace(0, np.pi, len(x))) ** 2 * g
def scratch(d=0.35, g=1.0):
    x = bpf(noise(d), 1500, 6000); m = (np.sin(2 * np.pi * 38 * tt(d)) > 0.2) * 1.0; return x * lpf(m, 200) * np.exp(-tt(d) * 3) * g
def creak(d=0.8, f0=120, f1=200, g=1.0):
    t = tt(d); f = np.linspace(f0, f1, len(t)); saw = ((np.cumsum(f) / SR) % 1) * 2 - 1
    grain = (rng.random(len(t)) < 0.02) * 1.0
    return bpf(saw * (0.4 + lpf(grain, 60) * 30), 300, 2400) * np.sin(np.linspace(0, np.pi, len(t))) * g
def twang():
    t = tt(0.9); return (np.sin(2 * np.pi * 98 * t) + 0.5 * np.sin(2 * np.pi * 196 * t) + 0.2 * np.sin(2 * np.pi * 294 * t)) * np.exp(-t * 6)
def rubble(d=1.6, g=1.0):
    out = np.zeros(int(d * SR))
    for _ in range(60): i = int(rng.random() ** 1.6 * (len(out) - 6000)); c = thump(80 + rng.random() * 160, 0.12, 0.3 + rng.random() * 0.5); out[i:i + len(c)] += c
    return (out + lpf(noise(d), 300) * np.exp(-tt(d) * 2) * 0.6) * g
def static(d=0.5, g=1.0):
    x = bpf(noise(d), 2000, 8000) * (rng.random(int(d * SR)) < 0.3); return lpf(x, 7000) * np.sin(np.linspace(0, np.pi, len(x))) * g
# opening: glass tone along the drawing lid; a chime per title letter; silk lashes
t = tt(1.4); gl = sum(np.sin(2 * np.pi * f * t) for f in (1568, 2349, 3136)) * np.sin(np.linspace(0, np.pi, len(t))) ** 2 * 0.1
fx.put(0.1, gl, 0.6)
pent = [74, 76, 78, 81, 83, 86, 88, 90, 93, 95, 98, 100]
for i in range(12): fx.put(0.97 + i * 0.09, bell(hz(pent[i] - 12), 1.5, 0.35), 0.18, (i - 5.5) / 8)
fx.put(1.4, silk(2.2, 0.35), 0.6)
# proverb: low gong ring on "söz"; muffled on "kar olar"
fx.put(5.25, bell(196, 4.0, 0.9), 0.35); fx.put(6.2, lpf(whoosh(0.9, 1800, 200, 0.4), 900), 0.5)
# spiral pulls inward; collapse to a point
fx.put(10.2, whoosh(1.8, 300, 3000, 0.35) * np.linspace(0.2, 1, int(1.8 * SR)), 0.5); fx.put(12.15, bell(2637, 1.2, 0.6), 0.2)
# reveal: eye opens
fx.put(13.9, whoosh(1.0, 500, 5000, 0.4), 0.45); fx.put(14.3, bell(1175, 3.2), 0.4); fx.put(14.45, silk(1.0, 0.4), 0.6)
# origin journey L->R
for k in range(4): fx.put(15.5 + k * 0.18, whoosh(0.5, 900, 1800, 0.18), 0.4, -0.8 + k * 0.5)
fx.put(17.3, scratch(1.0, 0.12), 0.5)                    # eye drawn in ink
fx.put(19.3, lpf(bpf(noise(1.3), 600, 5000) * (rng.random(int(1.3 * SR)) < 0.08), 6000) * np.sin(np.linspace(0, np.pi, int(1.3 * SR))), 0.4)  # parchment
fx.put(22.36, scratch(0.3, 0.45), 0.6)                   # strike-through
fx.put(22.9, creak(0.9, 150, 260, 0.35), 0.45)           # lashes tighten into arrows
for k in range(6): fx.put(23.82 + k * 0.06, whoosh(0.45, 700 + k * 120, 2600, 0.3), 0.4, (k - 2.5) / 3)
for k in range(5): fx.put(24.38 + k * 0.05, thump(110, 0.12, 0.4), 0.45)
fx.put(24.45, thump(52, 0.5, 0.7), 0.6)                   # heart takes it
fx.put(26.36, creak(0.7, 90, 120, 0.4), 0.45)             # eye bends into bow
fx.put(27.85, creak(0.9, 140, 320, 0.45), 0.5)            # drawing the string
fx.put(29.45, bell(330, 1.6, 0.5), 0.2)                   # target appears
fx.put(30.84, twang(), 0.5); fx.put(30.88, whoosh(0.45, 900, 4000, 0.6), 0.6)
fx.put(31.27, thump(85, 0.35, 1.0), 0.8); fx.put(31.27, click(0.04, 0.8, 2200), 0.5)
t = tt(0.9); hum = (np.sin(2 * np.pi * 100 * t) + 0.3 * np.sin(2 * np.pi * 200 * t) + 0.1 * bpf(noise(0.9), 3000, 8000)) * np.minimum(1, t / 0.05) * np.exp(-t * 2)
fx.put(31.95, hum * 0.3, 0.45)                            # ring light switches on
for k in range(26): fx.put(33.7 + k * 0.055, click(0.02, 0.35, 5500 + rng.random() * 2000), 0.25, rng.random() - 0.5)   # tweezers: lash extensions
tick_t = 35.14; iv = 0.5
while tick_t < 37.7: fx.put(tick_t, click(0.03, 0.5, 2800), 0.28); iv = max(0.12, iv * 0.88); tick_t += iv   # clock accelerates
fx.put(38.3, whoosh(1.0, 6000, 300, 0.6), 0.5)            # rewind to the past
for k in range(7): fx.put(39.75 + k * 0.1, thump(140 - k * 6, 0.18, 0.5), 0.45)   # wall stacks up
fx.put(40.58, bpf(noise(0.5), 1500, 7000) * (rng.random(int(0.5 * SR)) < 0.12) * np.exp(-tt(0.5) * 4), 0.6)   # cracks
fx.put(41.3, whoosh(1.0, 300, 1200, 0.3), 0.35)          # languid glance opens
fx.put(42.3, rubble(1.8), 0.6)
for k in range(6): fx.put(45.96 + k * 0.13, bell(hz(86 + [0, 3, 5, 7, 10, 12][k]), 1.2, 0.35), 0.12, (k - 2.5) / 3)   # names appear
fx.put(47.3, whoosh(1.2, 400, 3000, 0.55), 0.5, 0.0)
fx.put(47.6, lpf(noise(2.6), 260) * env_ar(int(2.6 * SR), 0.6, 0.8), 0.35)   # road hum
fx.put(48.3, static(0.45, 0.5), 0.3)                       # radio tuning
fx.put(49.16, bell(1175, 2.5), 0.3)
grain = np.zeros(int(1.2 * SR))
for _ in range(220): i = rng.integers(0, len(grain) - 300); grain[i:i + 200] += bpf(noise(0.005), 5000, 11000)[:200] * rng.random()
fx.put(53.3, grain * np.linspace(1, 0, len(grain)), 0.3)  # letters dissolve to dust
fx.put(55.1, bell(2093, 1.4, 0.5), 0.15)                  # hairline divider
fx.put(56.2, whoosh(0.8, 800, 2200, 0.45), 0.45, -0.4); fx.put(56.95, bell(3136, 1.6, 0.4), 0.15, 0.3)   # glides in, stops short
fx.put(57.6, silk(0.9, 0.3), 0.5)                          # heart drawn
fx.put(59.1, creak(0.9, 130, 180, 0.3), 0.4)              # aiming
fx.put(60.08, whoosh(0.85, 700, 3200, 0.55), 0.5, -0.5)
fx.put(60.85, thump(50, 0.7, 1.0), 0.75); fx.put(61.6, thump(50, 0.45, 0.6), 0.5); fx.put(62.35, thump(50, 0.4, 0.4), 0.4)   # heartbeat
fx.put(62.7, gl, 0.45)                                     # the lid line
for i in range(6): fx.put(63.42 + i * 0.21 + 0.52, thump(160 + i * 12, 0.15, 0.5) + np.pad(click(0.02, 0.4, 1800), (0, int(0.13 * SR))), 0.5, (i - 2.5) / 3)   # letters land
fx.put(65.9, silk(2.1, 0.3), 0.5)
fx.put(68.0, lpf(whoosh(1.3, 1500, 200, 0.4), 1500), 0.4)  # word sinks behind the lid
fL, fR = reverb(fx.L, fx.R, 2.0, 0.22, 6500)

def save(name, L, R):
    st = np.stack([L, R], 1); w = wave.open(name, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
pk = max(np.abs(mL).max(), np.abs(mR).max()); save('music_m.wav', mL / pk * 0.7, mR / pk * 0.7)
pk = max(np.abs(fL).max(), np.abs(fR).max()); save('sfx_m.wav', fL / pk * 0.7, fR / pk * 0.7)
print('ok')
