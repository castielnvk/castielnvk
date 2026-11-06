"""Generate the HyperFrames composition (graphics + captions + reframing) from the edit data."""
import json, sys
sys.path.insert(0, '.')
from segs import timeline, m

tl, T = timeline()
seg = {s['id']: s for s in tl}
def o(sid): return round(seg[sid]['ostart'], 3)
def oe(sid): return round(seg[sid]['ostart'] + seg[sid]['odur'], 3)

# ---- question cards: round, index, name, letter, card-in (src), letter spoken (src), last seg of round
ROUNDS = [
  ("nigar", "NİGAR CAMAL", "M", 68.50, 70.30, "N2"),
  ("aygun", "AYGÜN KAZIMOVA", "P", 5.15, 6.55, "A2"),
  ("ayaz", "AYAZ BABAYEV", "D", 10.35, 11.67, "Y2"),
  ("roya", "RÖYA AYXAN", "Q", 61.15, 63.45, "R2"),
  ("roza", "ROZA ZƏRGƏRLİ", "G", 38.05, 39.32, "Z3"),
  ("samra", "SAMRA", "Ə", 80.05, 81.45, "S5"),
  ("promete", "PROMETE", "Z", 95.10, 96.38, "P2"),
  ("zamiq", "ZAMİQ", "S", 115.10, 116.40, "Q3"),
  ("elza", "ELZA SEYİDCAHAN", "R", 132.15, 134.30, "E4"),
]
TITLE_END = 1.55
cards = []
for i, (r, name, letter, cin, lt, last) in enumerate(ROUNDS):
    t_in = max(m(cin), TITLE_END) if i == 0 else m(cin)
    cards.append(dict(i=i + 1, n=len(ROUNDS), name=name, letter=letter, t_in=t_in,
                      t_letter=m(lt), t_end=oe(last) if last != "E4" else o("FE")))

# ---- captions (src times). hl = highlighted words; late = {word: src time} words that appear later
CAPS = [
  (72.45, 73.50, "Birinci ağlıma…", []),
  (73.52, 74.95, "gizli-gizli şeylər gəlir", ["gizli-gizli"]),
  (17.40, 18.84, "Ayaz Babayev çox…", []),
  (64.48, 66.22, "Röya Ayxan çox…", []),
  (39.90, 41.04, "Gü…", []),
  (43.80, 45.40, "Qeyrətdi də…", ["Qeyrətdi"]),
  (45.45, 46.85, "qeyrətdi də… yox", []),
  (46.90, 48.41, "Nə deyim… gü…", []),
  (51.45, 52.58, "Gü ola bilər də…", []),
  (83.88, 85.75, "Samra… Ə…", []),
  (89.05, 90.97, "Doğrudan, Ə… başqa nə ola bilər?", []),
  (101.70, 103.33, "Niyə bilmirəm?", []),
  (105.10, 107.99, "…çox zarafatcıldır!", ["zarafatcıldır!"]),
  (128.73, 129.85, "Zamiq çox…", []),
  (136.30, 137.03, "R…", []),
  (147.10, 149.25, "R deyəndə ağlıma heç gəlmir…", []),
  (149.65, 150.55, "Qəribə.", []),
  (150.85, 152.80, "Rus gəldi ilk ağlıma.", ["Rus"]),
  (152.82, 153.99, "Rus sözü.", ["Rus"]),
  (162.55, 164.71, "Elza Seyidcahan çox rəngarəngdir.", ["rəngarəngdir."], {"rəngarəngdir.": 163.76}),
]
caps = []
for c in CAPS:
    late = c[4] if len(c) > 4 else {}
    caps.append(dict(a=m(c[0]), b=m(c[1]), text=c[2], hl=c[3], late={k: m(v) for k, v in late.items()}))

# ---- answer reveals (stamp). style: main | combo | tease | rainbow ; until = src end
REV = [
  ("PEŞƏKARDIR", 8.72, 9.96, "main", {}),
  ("DÜRÜSTDÜR", 18.86, 22.02, "main", {}),
  ("QÜSURSUZDUR", 66.25, 68.19, "main", {}),
  ("GÖZƏLDİR!", 50.86, 53.14, "main", {"pulse": 52.62}),
  ("ƏLADI!", 86.42, 87.74, "combo", {"n": 1}),
  ("ƏYLƏNCƏLİDİR!", 91.05, 92.59, "combo", {"n": 2}),
  ("ƏNTİQƏDİR!", 93.98, 95.04, "combo", {"n": 3}),
  ("ZARAFATCIL…", 103.66, 105.05, "main", {}),
  ("SEKSİ…", 119.39, 120.69, "tease", {}),
  ("SADƏDİR.", 129.90, 130.88, "main", {"strike": "SEKSİ"}),
  ("RƏNGARƏNGDİR!", 161.10, 162.50, "rainbow", {}),
]
revs = [dict(word=w, a=m(a), b=m(b), style=st, **{k:(m(v) if k=='pulse' else v) for k,v in ex.items()}) for (w, a, b, st, ex) in REV]

# ---- reframing (scale on the footage layer). (time, scale, originX, originY, dur 0 = cut)
Z = [
  (0, 1.0, 600, 690, 0),
  (m(73.52), 1.30, 617, 679, 0),             # punch-in on "gizli-gizli"
  (o("A1"), 1.0, 600, 690, 0),
  (m(18.86), 1.0, 667, 699, 0), (m(18.90), 1.13, 667, 699, 3.0),  # slow push across drawn-out "dürüstdür"
  (o("R1"), 1.0, 640, 660, 0),
  (m(66.25), 1.16, 640, 660, 0),
  (o("Z1"), 1.0, 600, 690, 0),
  (o("FZ"), 1.08, 579, 620, 0), (o("FZ") + 0.01, 1.2, 579, 620, 0.95),
  (o("Z3"), 1.0, 600, 690, 0),
  (m(91.05), 1.18, 644, 712, 0),
  (o("S5"), 1.36, 644, 712, 0),
  (o("P1"), 1.0, 600, 690, 0),
  (m(103.66), 1.2, 597, 679, 0),
  (o("Q1"), 1.0, 600, 690, 0),
  (o("Q2"), 1.42, 596, 740, 0),               # whisper-quiet "seksi" close-up
  (o("Q3"), 1.0, 635, 690, 0),
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
