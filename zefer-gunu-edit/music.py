"""Original score for the 'Zəfər Günü' edit: piano + strings, D major, gradual build.
Bar length is tuned so bar 17 lands on the title break (59.4 s) and bar 35 on the end-card arrival."""
import mido, sys
BAR = 59.4 / 17                      # seconds per bar (4/4)
BPM = 60 * 4 / BAR
TPB = 480
mid = mido.MidiFile(ticks_per_beat=TPB)
def track(ch, prog, vol, pan=64, rev=90, cho=20):
    t = mido.MidiTrack(); mid.tracks.append(t)
    t.append(mido.Message('program_change', channel=ch, program=prog, time=0))
    for cc, v in ((7, vol), (10, pan), (91, rev), (93, cho), (11, 127)):
        t.append(mido.Message('control_change', channel=ch, control=cc, value=v, time=0))
    return t
meta = mido.MidiTrack(); mid.tracks.insert(0, meta)
meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0))
events = {}   # ch -> list of (tick, msg)
def add(ch, tick, msg): events.setdefault(ch, []).append((int(tick), msg))
def note(ch, bar, beat, dur_beats, pitch, vel):
    s = (bar * 4 + beat) * TPB
    add(ch, s, mido.Message('note_on', channel=ch, note=pitch, velocity=max(1, min(127, int(vel)))))
    add(ch, s + dur_beats * TPB - 10, mido.Message('note_off', channel=ch, note=pitch, velocity=0))
def expr(ch, bar0, bar1, v0, v1, steps=24):
    for i in range(steps + 1):
        tick = (bar0 + (bar1 - bar0) * i / steps) * 4 * TPB
        add(ch, tick, mido.Message('control_change', channel=ch, control=11, value=int(v0 + (v1 - v0) * i / steps)))
N = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def p(name, octv): return 12 * (octv + 1) + N[name]
CH = {  # root, chord tones (pitch classes), 'sus' variants
 'D': ('D', ['D','F#','A']), 'Bm': ('B', ['B','D','F#']), 'G': ('G', ['G','B','D']),
 'A': ('A', ['A','C#','E']), 'Asus': ('A', ['A','D','E']), 'Em': ('E', ['E','G','B']),
 'F#m': ('F#', ['F#','A','C#']), 'Gmaj7': ('G', ['G','B','D','F#']), 'Dadd9': ('D', ['D','E','F#','A'])}
prog = (['Bm','G','D','A'] * 2 + ['Em','Asus'] +                   # 0-9   President, listening
        ['D','Bm','G','A', 'Bm','G','Asus'] +                       # 10-16 her entrance -> build
        ['D'] +                                                     # 17    title break
        ['Bm','G','D','A', 'Bm','G','Em','A'] +                     # 18-25
        ['D','F#m','Gmaj7','A', 'Bm','G','D','A'] +                 # 26-33 melody, build
        ['G'] + ['Dadd9','D'])                                      # 34 rise, 35-36 arrival
PAD, PNO, CEL, STR, WARM, HARP = 0, 1, 2, 3, 4, 5
pad = track(PAD, 49, 92, 64, 110, 40)     # slow strings
pno = track(PNO, 0, 104, 60, 85, 10)      # grand piano
cel = track(CEL, 42, 88, 54, 95, 20)      # cello
strm = track(STR, 48, 96, 74, 110, 40)    # string section melody
warm = track(WARM, 89, 70, 64, 120, 60)   # warm pad bed
harp = track(HARP, 46, 70, 80, 110, 20)   # harp shimmer at key moments
def voicing(ch_name, octv=4):
    root, tones = CH[ch_name]
    out = []
    for t in tones:
        q = p(t, octv)
        if q < p(root, octv): q += 12
        out.append(q)
    return sorted(out)
for b, c in enumerate(prog):
    root, tones = CH[c]
    # pad: sustained chord whole bar (tied feel)
    v = 48 if b < 10 else 56 if b < 17 else 70 if b == 17 else 60 if b < 26 else 68 if b < 34 else 84
    for q in voicing(c, 3 if b < 10 else 4): note(PAD, b, 0, 4, q, v)
    if b < 34 or b >= 35: note(WARM, b, 0, 4, p(root, 2), 50 if b < 17 else 58)
    # cello bass from bar 10
    if b >= 10:
        note(CEL, b, 0, 2.5 if b != 17 else 4, p(root, 2) + (12 if p(root,2) < 40 else 0), 62 if b < 26 else 74)
        if b not in (16, 17, 34) and b < 35: note(CEL, b, 2.5, 1.5, voicing(c, 3)[1] - 12 if voicing(c,3)[1]-12 > 38 else voicing(c,3)[1], 52 if b < 26 else 62)
    # piano
    if b < 10:          # sparse, high, gentle under the President's speech
        if b % 2 == 0: note(PNO, b, 0, 3.5, voicing(c, 5)[0], 34)
        else: note(PNO, b, 1, 3, voicing(c, 5)[-1], 30)
    elif b < 35:        # flowing 8th-note arpeggios
        vc = voicing(c, 4); arp = [p(root, 3)] + vc + [vc[0] + 12, vc[1] + 12 if len(vc)>1 else vc[0]+12] + vc[::-1]
        arp = (arp * 2)[:8]
        base = 40 if b < 17 else 46 if b < 26 else 52 if b < 30 else 58
        if b == 17: base = 56
        for i, q in enumerate(arp):
            note(PNO, b, i * 0.5, 0.9, q, base + (8 if i == 0 else 0) + (b - 26 if b >= 26 else 0))
    else:               # arrival: rolled chord, ring out
        for i, q in enumerate([p('D',2), p('D',3), p('A',3), p('D',4), p('F#',4), p('A',4), p('D',5)]):
            if b == 35: note(PNO, b, i * 0.12, 7.5, q, 70 - i * 2)
# string melody (bars 26-34) and a quieter answer at bars 18-21
mel = [(26,[(0,1.5,'F#',5),(1.5,0.5,'E',5),(2,2,'D',5)]),
       (27,[(0,1.5,'C#',5),(1.5,0.5,'B',4),(2,2,'A',4)]),
       (28,[(0,1,'B',4),(1,1,'D',5),(2,2,'F#',5)]),
       (29,[(0,3,'E',5),(3,1,'A',4)]),
       (30,[(0,1.5,'F#',5),(1.5,0.5,'G',5),(2,2,'A',5)]),
       (31,[(0,1.5,'G',5),(1.5,0.5,'F#',5),(2,2,'D',5)]),
       (32,[(0,1,'F#',5),(1,1,'A',5),(2,2,'D',6)]),
       (33,[(0,2,'C#',6),(2,2,'E',5)]),
       (34,[(0,2,'D',5),(2,2,'E',5)]),
       (35,[(0,8,'F#',5)])]
for b, ns in mel:
    for (bt, d, n, o) in ns:
        note(STR, b, bt, d, p(n, o), 70 + (b - 26) * 3)
        if b >= 30: note(STR, b, bt, d, p(n, o) - 12, 60 + (b - 30) * 3)
for b, ns in [(18,[(0,2,'F#',4),(2,2,'E',4)]),(19,[(0,4,'D',4)]),(20,[(0,2,'A',4),(2,2,'F#',4)]),(21,[(0,4,'E',4)])]:
    for (bt, d, n, o) in ns: note(STR, b, bt, d, p(n, o), 52)
# harp glints: entrance, title, end
for b, tones in [(10, ['D','F#','A','D']), (17, ['D','F#','A','D','F#','A']), (35, ['D','F#','A','D','F#','A','D'])]:
    for i, t in enumerate(tones): note(HARP, b, i * 0.18, 3, p(t, 4 + (i // 3)), 50 + i * 3)
# dynamics (expression CC11)
expr(PAD, 0, 1.5, 0, 100); expr(WARM, 0, 2, 0, 110)
expr(PAD, 15, 17, 100, 127); expr(PAD, 17.5, 18.5, 127, 105)
expr(PAD, 26, 34, 105, 127); expr(STR, 26, 34, 95, 127)
expr(PAD, 35.5, 37, 127, 0, 30); expr(WARM, 35.5, 37, 110, 0, 30); expr(STR, 35.5, 37, 127, 0, 30)
expr(CEL, 35.5, 37, 127, 0, 30)
for ch, trk in [(PAD, pad), (PNO, pno), (CEL, cel), (STR, strm), (WARM, warm), (HARP, harp)]:
    ev = sorted(events.get(ch, []), key=lambda e: (e[0], 0 if e[1].type == 'note_off' else 1))
    last = 0
    for tick, msg in ev:
        trk.append(msg.copy(time=tick - last)); last = tick
mid.save(sys.argv[1])
print(f"BPM={BPM:.3f} bar={BAR:.4f}s bars={len(prog)} length~{len(prog)*BAR:.1f}s")
