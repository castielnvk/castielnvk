"""Generate the HyperFrames composition (graphics + captions + reframing) from the edit data.
Rule: every answer is revealed 0.15 s AFTER the spoken answer word ends (word-end times measured
on the source audio); no caption contains an answer before it is spoken."""
import json, sys
sys.path.insert(0, '.')
from segs import timeline, m

tl, T = timeline()
seg = {s['id']: s for s in tl}
def o(sid): return round(seg[sid]['ostart'], 3)
def oe(sid): return round(seg[sid]['ostart'] + seg[sid]['odur'], 3)
def round_end(r):
    ss = [s for s in tl if s['round'] == r and s['id'] != 'FE']
    return round(ss[-1]['ostart'] + ss[-1]['odur'], 3)

DELAY = 0.15
# ---- question cards: round, name, letter, card-in (src), letter spoken (src)
ROUNDS = [
  ("nigar", "NİGAR CAMAL", "M", 68.98, 70.30),
  ("aygun", "AYGÜN KAZIMOVA", "P", 5.15, 6.55),
  ("ayaz", "AYAZ BABAYEV", "D", 10.42, 11.67),
  ("roya", "RÖYA AYXAN", "Q", 61.15, 63.45),
  ("roza", "ROZA ZƏRGƏRLİ", "G", 38.05, 39.32),
  ("samra", "SAMRA", "Ə", 80.05, 81.45),
  ("promete", "PROMETE", "Z", 95.32, 96.38),
  ("natavan", "NATAVAN HƏBİBİ", "L", 108.62, 110.06),
  ("zamiq", "ZAMİQ", "S", 115.10, 116.40),
  ("nuran", "NURAN", "İ", 165.50, 166.70),
  ("elza", "ELZA SEYİDCAHAN", "R", 132.15, 134.30),
]
TITLE_END = 1.55
cards = []
for i, (r, name, letter, cin, lt) in enumerate(ROUNDS):
    t_in = max(m(cin), TITLE_END) if i == 0 else m(cin)
    cards.append(dict(i=i + 1, n=len(ROUNDS), name=name, letter=letter, t_in=t_in,
                      t_letter=max(m(lt), t_in + 0.25), t_end=round_end(r) if r != "elza" else o("FE")))

# ---- captions (src times) — none of these contain an answer before it is spoken
CAPS = [
  (17.40, 18.90, "Ayaz Babayev çox…", []),
  (64.48, 66.20, "Röya Ayxan çox…", []),
  (39.90, 41.04, "Gü…", []),
  (43.80, 45.40, "Qeyrətdi də…", ["Qeyrətdi"]),
  (45.45, 46.85, "qeyrətdi də… yox", []),
  (46.90, 48.41, "Nə deyim… gü…", []),
  (51.60, 52.58, "Gü ola bilər də…", []),
  (83.88, 85.75, "Samra… Ə…", []),
  (89.05, 90.97, "Doğrudan, Ə… başqa nə ola bilər?", []),
  (101.70, 103.33, "Niyə bilmirəm?", []),
  (105.10, 107.99, "…çox zarafatcıldır!", ["zarafatcıldır!"]),   # after the ZARAFATCIL reveal
  (128.73, 129.85, "Zamiq çox…", []),
  (192.00, 193.42, "Nuran çox…", []),
  (136.30, 137.03, "R…", []),
  (147.10, 149.25, "R deyəndə ağlıma heç gəlmir…", []),
  (149.65, 150.55, "Qəribə.", []),
  (150.85, 152.80, "Rus gəldi ilk ağlıma.", ["Rus"]),
  (152.82, 153.99, "Rus sözü.", ["Rus"]),
  (162.55, 164.71, "Elza Seyidcahan çox…", []),
]
caps = [dict(a=m(c[0]), b=m(c[1]), text=c[2], hl=c[3], late={}) for c in CAPS]

# ---- answer reveals: (word, src time the spoken answer word ENDS, round, style, extra)
REV = [
  ("MATANDIR", 76.30, "nigar", "main", {}),
  ("PEŞƏKARDIR", 9.62, "aygun", "main", {}),
  ("DÜRÜSTDÜR", 21.62, "ayaz", "main", {}),
  ("QÜSURSUZDUR", 67.96, "roya", "main", {}),
  ("GÖZƏLDİR!", 51.24, "roza", "main", {}),
  ("ƏLADIR!", 87.36, "samra", "combo", {"n": 1, "until": 88.25}),
  ("ƏYLƏNCƏLİDİR!", 91.70, "samra", "combo", {"n": 2, "until": 92.60}),
  ("ƏNTİQƏDİR!", 94.95, "samra", "combo", {"n": 3}),
  ("ZARAFATCIL…", 104.16, "promete", "main", {"until": 105.05}),
  ("LAQEYDDİR", 113.50, "natavan", "main", {}),
  ("SADƏDİR.", 130.48, "zamiq", "main", {}),
  ("İSTEDADLIDIR", 194.90, "nuran", "main", {}),
  ("RƏNGARƏNGDİR!", 161.84, "elza", "rainbow", {"pulse": 164.48}),
]
revs = []
for (w, end, r, st, ex) in REV:
    a = round(m(end) + DELAY, 3)
    b = m(ex['until']) if 'until' in ex else (o("FE") if r == "elza" else round_end(r) + 0.25)
    if r == "elza": b = o("FE") + 0.05
    d = dict(word=w, a=a, b=round(b, 3), style=st)
    if 'n' in ex: d['n'] = ex['n']
    if 'pulse' in ex: d['pulse'] = round(m(ex['pulse']) + DELAY, 3)
    revs.append(d)

# ---- reframing (scale on the footage layer). (time, scale, originX, originY, dur 0 = cut)
Z = [
  (0, 1.0, 600, 690, 0),
  (o("N2"), 1.22, 589, 702, 0),
  (o("HN"), 1.22, 589, 702, 0), (o("HN") + 0.01, 1.27, 589, 702, 0.45),
  (o("A1"), 1.0, 600, 690, 0),
  (o("HA"), 1.0, 600, 690, 0), (o("HA") + 0.01, 1.04, 600, 690, 0.25),
  (o("Y1"), 1.0, 600, 690, 0),
  (m(18.90), 1.0, 667, 699, 0), (m(18.95), 1.13, 667, 699, 2.6),   # slow push through the pause before "dürüstdür"
  (o("HY"), 1.13, 667, 699, 0), (o("HY") + 0.01, 1.18, 667, 699, 0.7),
  (o("R1"), 1.0, 640, 660, 0),
  (m(66.95), 1.16, 640, 660, 0),
  (o("Z1"), 1.0, 600, 690, 0),
  (o("FZ"), 1.08, 579, 620, 0), (o("FZ") + 0.01, 1.2, 579, 620, 0.95),
  (o("Z3"), 1.0, 600, 690, 0),
  (m(91.05), 1.18, 644, 712, 0),
  (o("S5"), 1.36, 644, 712, 0),
  (o("HS"), 1.36, 644, 712, 0), (o("HS") + 0.01, 1.4, 644, 712, 0.55),
  (o("P1"), 1.0, 600, 690, 0),
  (m(103.60), 1.2, 597, 679, 0),
  (o("T1"), 1.0, 600, 690, 0),
  (m(112.45), 1.2, 529, 714, 0),
  (o("Q1"), 1.0, 600, 690, 0),
  (m(129.90), 1.15, 635, 690, 0),
  (o("U1"), 1.0, 600, 690, 0),
  (m(193.40), 1.15, 564, 683, 0),
  (o("E1"), 1.0, 600, 690, 0),
  (o("E2"), 1.07, 599, 729, 0),
  (o("E4"), 1.0, 586, 690, 0),
  (m(163.76), 1.18, 586, 690, 0), (o("FE"), 1.18, 586, 690, 0), (o("FE") + 0.01, 1.27, 586, 690, 2.1),
]
zooms = [dict(t=round(a, 3), s=s, x=x, y=y, d=d) for (a, s, x, y, d) in Z]

extras = dict(
  freeze=dict(a=o("FZ"), b=oe("FZ")),
  later=dict(a=o("E2"), b=o("E2") + 1.6, text="+10 SANİYƏ"),
  end=dict(a=o("FE"), b=T),
)
DATA = dict(T=round(T, 3), cards=cards, caps=caps, revs=revs, zooms=zooms, extras=extras, title_end=TITLE_END)
json.dump(DATA, open('gfx.json', 'w'), ensure_ascii=False, indent=1)

HTML = open('template.html', encoding='utf-8').read()
HTML = HTML.replace('__DATA__', json.dumps(DATA, ensure_ascii=False)).replace('__T__', str(round(T, 3)))
open(sys.argv[1], 'w', encoding='utf-8').write(HTML)
print("ok", round(T, 2), len(cards), len(caps), len(revs))
for r in revs: print(" ", r['word'], r['a'], r['b'], round(r['b'] - r['a'], 2))
