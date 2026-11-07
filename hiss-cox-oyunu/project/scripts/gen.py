"""v3 graphics/sfx/music data. Rule: every answer graphic/sticker/caption that reveals an answer starts
DELAY s after the spoken answer word ENDS (word ends measured on the source audio)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from segs import timeline, m

tl, T = timeline()
seg = {s['id']: s for s in tl}
def o(i): return round(seg[i]['ostart'], 3)
def oe(i): return round(seg[i]['ostart'] + seg[i]['odur'], 3)
def round_end(r):
    ss = [s for s in tl if s['round'] == r and s['id'] != 'FE']; return round(ss[-1]['ostart'] + ss[-1]['odur'], 3)
DELAY = 0.15
FX, FY = 600, 690           # face centre in output frame (tracked framing keeps it here)

ROUNDS = [  # round, card name, letter, card-in src, letter-spoken src
  ("nigar", "NİGAR CAMAL", "M", 68.98, 70.30), ("aygun", "AYGÜN KAZIMOVA", "P", 5.15, 6.55),
  ("ayaz", "AYAZ BABAYEV", "D", 10.42, 11.67), ("roya", "RÖYA AYXAN", "Q", 61.15, 63.45),
  ("roza", "ROZA ZƏRGƏRLİ", "G", 38.05, 39.32), ("samra", "SAMRA", "Ə", 80.05, 81.45),
  ("promete", "PROMETE", "Z", 95.32, 96.38), ("natavan", "NATAVAN HƏBİBİ", "L", 108.62, 110.06),
  ("zamiq", "ZAMİQ", "S", 115.10, 116.40), ("nuran", "NURAN", "İ", 165.50, 166.70),
  ("elza", "ELZA SEYİDCAHAN", "R", 132.15, 134.30)]
TITLE_AT = o("N1"); TITLE_END = TITLE_AT + 1.6
cards = []
PFX = {"nigar": "N", "aygun": "A", "ayaz": "Y", "roya": "R", "roza": "Z", "samra": "S", "promete": "P", "natavan": "T",
       "zamiq": "Q", "nuran": "U", "elza": "E"}
for i, (r, name, letter, cin, lt) in enumerate(ROUNDS):
    t_in = max(m(cin, PFX[r]), TITLE_END) if i == 0 else m(cin, PFX[r])
    cards.append(dict(i=i + 1, n=len(ROUNDS), name=name, letter=letter, t_in=t_in,
                      t_letter=max(m(lt, PFX[r]), t_in + 0.25), t_end=round_end(r) if r != "elza" else o("FE")))

CAPS = [  # src a, src b, text, highlighted words, prefer-seg   (no caption contains an unspoken answer)
  (150.85, 152.80, "Rus gəldi ilk ağlıma.", ["Rus"], "HK"), (152.82, 153.99, "Rus sözü.", ["Rus"], "HK"),
  (17.40, 18.95, "Ayaz Babayev çox…", [], None), (64.48, 66.20, "Röya Ayxan çox…", [], None),
  (39.90, 41.04, "Gü…", [], None), (43.80, 45.40, "Qeyrətdi də…", ["Qeyrətdi"], None),
  (45.45, 46.85, "qeyrətdi də… yox", [], None), (46.90, 48.41, "Nə deyim… gü…", [], None),
  (51.60, 52.58, "Gü ola bilər də…", [], None), (83.88, 85.75, "Samra… Ə…", [], None),
  (89.05, 90.97, "Doğrudan, Ə… başqa nə ola bilər?", [], None), (101.70, 103.33, "Niyə bilmirəm?", [], None),
  (105.10, 107.99, "…çox zarafatcıldır!", ["zarafatcıldır!"], None), (128.73, 129.85, "Zamiq çox…", [], None),
  (192.00, 193.42, "Nuran çox…", [], None), (136.30, 137.03, "R…", [], None),
  (147.10, 149.25, "R deyəndə ağlıma heç gəlmir…", [], "E2"), (149.65, 150.55, "Qəribə.", [], "E2"),
  (162.55, 164.71, "Elza Seyidcahan çox…", [], None)]
caps = [dict(a=m(a, p), b=m(b, p), text=t, hl=h) for (a, b, t, h, p) in CAPS]

# answers: word, src END of spoken word, round, style
REV = [("MATANDIR", 76.30, "nigar", "main"), ("PEŞƏKARDIR", 9.62, "aygun", "pro"),
       ("DÜRÜSTDÜR", 21.62, "ayaz", "halo"), ("QÜSURSUZDUR", 67.96, "roya", "gloss"),
       ("GÖZƏLDİR!", 51.24, "roza", "love"), ("ƏLADIR!", 87.36, "samra", "combo1"),
       ("ƏYLƏNCƏLİDİR!", 91.70, "samra", "combo2"), ("ƏNTİQƏDİR!", 94.95, "samra", "combo3"),
       ("ZARAFATCIL…", 104.16, "promete", "main"), ("LAQEYDDİR", 113.50, "natavan", "flat"),
       ("SADƏDİR.", 130.48, "zamiq", "plain"), ("İSTEDADLIDIR", 194.90, "nuran", "gold"),
       ("RƏNGARƏNGDİR!", 161.84, "elza", "rainbow")]
UNTIL = {"ƏLADIR!": 88.25, "ƏYLƏNCƏLİDİR!": 92.60, "ZARAFATCIL…": 105.05}
revs = []
for (w, end, r, st) in REV:
    a = round(m(end) + DELAY, 3)
    b = m(UNTIL[w]) if w in UNTIL else (o("FE") + 0.05 if r == "elza" else round_end(r) + 0.25)
    revs.append(dict(word=w, a=a, b=round(b, 3), style=st, round=r))
R = {x['word']: x for x in revs}
def ra(w): return R[w]['a']

# stickers: emoji, x, y (centre), size px, t_in, t_out, anim, rot   — placed beside the head, never on the chest
STK = [
  ("🤔", 870, 600, 170, m(151.10), oe("HK") - 0.05, "bob", 10),
  ("😌", 860, 640, 160, ra("MATANDIR") + 0.10, oe("HN"), "pop", 8),
  ("🎤", 200, 640, 170, ra("PEŞƏKARDIR") + 0.08, oe("HA") + 0.15, "pop", -14),
  ("😇", 870, 550, 170, ra("DÜRÜSTDÜR") + 0.12, oe("HY"), "pop", 10),
  ("💎", 870, 600, 150, ra("QÜSURSUZDUR") + 0.10, oe("R2") + 0.2, "spin", 0),
  ("🙈", 860, 640, 180, o("FZ") + 0.30, oe("FZ"), "pop", 10),
  ("😍", 870, 600, 170, ra("GÖZƏLDİR!") + 0.10, m(51.60), "pop", 8),
  ("😅", 870, 620, 160, m(51.65), oe("Z3"), "bob", 8),
  ("🤷‍♀️", 190, 640, 160, m(89.40), m(90.97), "pop", -8),
  ("🔥", 870, 560, 170, ra("ƏNTİQƏDİR!") + 0.10, oe("HS"), "shake", 6),
  ("😩", 200, 620, 160, m(102.40), m(103.33), "shake", -8),
  ("😜", 870, 600, 160, ra("ZARAFATCIL…") + 0.10, m(107.9), "bob", 8),
  ("😐", 870, 620, 160, ra("LAQEYDDİR") + 0.45, oe("T2"), "none", 0),
  ("🙂", 860, 640, 120, ra("SADƏDİR.") + 0.35, oe("Q3"), "none", 0),
  ("👏", 200, 640, 170, ra("İSTEDADLIDIR") + 0.10, oe("U2") + 0.2, "clap", -10),
  ("🤯", 870, 560, 170, m(147.6, "E2"), m(150.6, "E2"), "shake", 8),
  ("⏳", 300, 550, 90, o("E4"), o("E4") + 1.4, "spin", 0),
  ("🌈", 860, 550, 180, ra("RƏNGARƏNGDİR!") + 0.10, o("FE") + 0.3, "pop", 8),
]
stickers = [dict(e=e, x=x, y=y, s=s, a=round(a, 3), b=round(b, 3), anim=an, rot=rot) for (e, x, y, s, a, b, an, rot) in STK]

fx = dict(
  title=dict(a=TITLE_AT, b=TITLE_END),
  hook_label=dict(a=0.15, b=oe("HK") - 0.1),
  smash=o("N1"),
  loading=dict(a=m(18.95), b=ra("DÜRÜSTDÜR") - 0.02),           # "Hiss düşünür…" during the long pause
  halo=dict(a=ra("DÜRÜSTDÜR") + 0.05, b=oe("HY")),
  gloss=ra("QÜSURSUZDUR") + 0.05,
  freeze=dict(a=o("FZ"), b=oe("FZ")),
  hearts=dict(a=ra("GÖZƏLDİR!") + 0.08, b=ra("GÖZƏLDİR!") + 1.6),
  combo=dict(a=ra("ƏNTİQƏDİR!") + 0.08, b=oe("HS")),
  deadpan=dict(a=ra("LAQEYDDİR"), b=oe("T2")),
  stars=dict(a=ra("İSTEDADLIDIR") + 0.05),
  later=dict(a=o("E4"), b=o("E4") + 1.4, text="+10 SANİYƏ"),
  confetti=dict(a=ra("RƏNGARƏNGDİR!") + 0.05),
  final_pulse=m(164.48) + DELAY,
  end=dict(a=o("FE"), b=T),
)
# reframing on top of the tracked base framing (relative scale, origin = face)
Z = [(0, 1.0, 0)]   # no zoom anywhere: full original frame keeps the ARAZ wall visible
zooms = [dict(t=round(t, 3), s=s, d=d) for (t, s, d) in Z]

# sound design events (t, kind, gain dB) and music automation
SFX = [(0.0, "whoosh", -8), (o("N1") - 0.02, "smash", -2), (o("N1") + 0.05, "whoosh", -6)]
for c in cards:
    if c['i'] > 1: SFX.append((c['t_in'] - 0.08, "whoosh", -8))
    SFX.append((c['t_letter'] - 0.04, "tick", -7))
for rv in revs:
    k = {"main": "stamp", "pro": "stamp", "halo": "angel", "gloss": "sparkle", "love": "stamp", "combo1": "ding1", "combo2": "ding2",
         "combo3": "ding3", "flat": "boop", "plain": "pop", "gold": "tada", "rainbow": "stamp"}[rv['style']]
    if k not in ("boop", "pop"): SFX.append((rv['a'] - 0.01, "stamp" if k not in ("angel", "sparkle", "tada") else "stamp_soft", -3))
    SFX.append((rv['a'] + 0.02, k, -5))
for st in stickers:
    if st['anim'] != 'none': SFX.append((st['a'], "pop", -12))
SFX += [(fx['freeze']['a'], "tapestop", -3), (fx['freeze']['a'] + 0.28, "buzzer", -8), (o("FZ") + 0.32, "boing", -9),
        (fx['loading']['a'], "ticktock", -10), (fx['later']['a'] + 0.02, "ticktock", -11),
        (ra("RƏNGARƏNGDİR!") - 0.9, "riser", -10), (fx['final_pulse'], "tick", -8), (fx['end']['a'] + 0.35, "stamp", -6),
        (m(102.40), "boing", -12)]
sfx = [dict(t=round(t, 3), k=k, g=g) for (t, k, g) in SFX]
music = dict(start=o("N1"),                                    # music enters on the title smash (hook plays dry)
             stops=[[fx['loading']['a'] - 0.05, ra("DÜRÜSTDÜR")],  # silence during Ayaz's long pause
                    [fx['freeze']['a'], fx['freeze']['b']],        # record-stop on Q ≠ G
                    [ra("LAQEYDDİR") - 0.05, oe("T2")]],           # deadpan: music drops out for "laqeyddir"
             outro=o("FE"))

DATA = dict(T=round(T, 3), FX=FX, FY=FY, cards=cards, caps=caps, revs=revs, stickers=stickers, fx=fx, zooms=zooms,
            sfx=sfx, music=music)
json.dump(DATA, open('gfx.json', 'w'), ensure_ascii=False, indent=1)
if len(sys.argv) > 1:
    HTML = open('template.html', encoding='utf-8').read()
    open(sys.argv[1], 'w', encoding='utf-8').write(HTML.replace('__DATA__', json.dumps(DATA, ensure_ascii=False)).replace('__T__', str(round(T, 3))))
print("ok", round(T, 2), len(cards), len(caps), len(revs), len(stickers), len(sfx))
for r in revs: print(" ", r['word'], r['a'], r['b'])
