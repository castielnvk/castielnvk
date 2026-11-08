# Zənəxdan — calm original score (felt piano + warm pads), same approach as Məlal
exec(open('../audiolib.py').read())
DUR = 58.7; N = int(SR * DUR)
mus = Bus()
CH = {'G': [43, 55, 59, 62], 'Gadd9': [43, 55, 57, 59, 62], 'D/F#': [42, 54, 57, 62], 'Em': [40, 52, 55, 59], 'C': [36, 52, 55, 60],
      'Cmaj7': [36, 52, 55, 59], 'Am': [45, 52, 57, 60], 'D': [38, 54, 57, 62], 'F': [41, 53, 57, 60], 'Dsus': [38, 55, 57, 62], 'Em7': [40, 52, 55, 62]}
def arp(t0, ch, beats, step=0.7, vel=0.3, pan=0.0):
    ns = CH[ch]; seq = [ns[1], ns[2], ns[3], ns[2]]
    mus.put(t0, piano(ns[0], 5.0, vel * 1.05), 0.9)
    for i in range(1, int(beats / step)):
        mus.put(t0 + i * step, piano(seq[(i - 1) % 4] + 12, 3.2, vel * (0.8 + 0.2 * rng.random())), 1, pan + 0.25 * np.sin(i * 1.3))
def bed(t0, ch, d, bright=700, g=0.75):
    mus.put(t0, pad(CH[ch][1:], d, att=min(1.5, d / 3), rel=min(2.0, d / 2.5), bright=bright), g)
# 0–8.4: the verse — sparse, almost still; a few soft notes under the poetry
bed(0.0, 'Gadd9', 8.8, 650, 0.7)
for st, n in [(0.1, 43), (2.28, 71), (3.98, 74), (5.2, 69), (6.66, 79), (7.44, 74)]: mus.put(st, piano(n, 4, 0.26 if n > 60 else 0.4), 0.8)
# 8.4–12.5: rising to the word
bed(8.3, 'Cmaj7', 4.6, 800, 0.8)
for i, n in enumerate([67, 71, 74, 79]): mus.put(11.4 + i * 0.18, piano(n, 3.5, 0.28), 0.8, (i - 1.5) / 3)
# 12.5–18.3: the meaning — gentle arpeggios
for i, ch in enumerate(['G', 'D/F#', 'Em', 'C']): arp(12.5 + i * 1.45, ch, 1.45, 0.48, 0.28); bed(12.5 + i * 1.45, ch, 2.2, 750, 0.6)
mus.put(15.36, piano(83, 3.5, 0.24), 0.6)   # a soft high note for the smile
# 18.3–24.6: traffic — the piano stops; a quiet, cool held chord; the frown descends
bed(18.3, 'Em7', 6.5, 420, 0.75)
for i, n in enumerate([71, 67, 64, 59]): mus.put(23.04 + i * 0.32, piano(n, 3.0, 0.24), 0.7)
# 24.6–33: doors open onto warmth
bed(24.6, 'Am', 2.4, 500, 0.6)
arp(26.78, 'C', 2.0, 0.5, 0.28); bed(26.7, 'C', 2.2, 900, 0.75)
arp(28.8, 'Am', 1.6, 0.53, 0.27); bed(28.8, 'Am', 1.8, 850, 0.65)
arp(30.4, 'D', 1.7, 0.57, 0.28); bed(30.4, 'D', 1.9, 900, 0.65)
arp(32.12, 'G', 1.4, 0.47, 0.3); bed(32.1, 'G', 2.6, 1000, 0.8)
# 33–39.6: tension — a held suspended chord (no tremolo), released into G on "gülümsəmək"
bed(33.4, 'Dsus', 4.9, 450, 0.75)
mus.put(35.0, piano(69, 3.5, 0.2), 0.5)
arp(38.24, 'G', 1.4, 0.47, 0.3); bed(38.2, 'G', 2.0, 950, 0.8); mus.put(38.3, piano(83, 3.5, 0.22), 0.55)
# 39.5–49.6: warm and steady — C G Am F C G
for i, ch in enumerate(['C', 'G', 'Am', 'F', 'C', 'G']): arp(39.6 + i * 1.66, ch, 1.66, 0.55, 0.26); bed(39.6 + i * 1.66, ch, 2.3, 750, 0.6)
mus.put(48.4, piano(79, 3.5, 0.22), 0.55)
# 49.4–58.7: the word smiles — one soft note per landing letter, then the closing chord
for i, n in enumerate([67, 69, 71, 74, 76, 79, 81, 83]): mus.put(50.45 + i * 0.19 + 0.6, piano(n, 3.0, 0.22), 0.7, (i - 3.5) / 5)
bed(50.0, 'G', 3.0, 700, 0.6); bed(53.0, 'C', 2.8, 700, 0.55)
bed(55.7, 'Gadd9', 3.0, 800, 0.8); mus.put(55.75, piano(43, 3.0, 0.4), 0.8); mus.put(55.9, piano(74, 2.8, 0.24), 0.6)
mL, mR = reverb(mus.L, mus.R, 4.0, 0.42, 2600)
fade = np.ones(N); fi = int(1.0 * SR); fade[-fi:] = np.linspace(1, 0, fi) ** 2; mL *= fade; mR *= fade
st = np.stack([mL, mR], 1); pk = np.abs(st).max(); st = st / pk * 0.7
w = wave.open('music_v3.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes()); w.close(); print('ok')
