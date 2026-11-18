# Episode 4: vegetarian son / Gent / asteroid quiz. Authored in SOURCE times, mapped to w10/combo.mov.
import json, os, random
from engine import YEL, MAG, CYA, INK, WHITE, PURP, WDIR
HEADER = ''
OBA_Y = (255, 205, 0); GREEN = (130, 230, 140); PINK = (255, 140, 180); SKY = (140, 200, 255)
_M = json.load(open(os.path.join(WDIR, 'map.json')))
def mp(t):
    for x in _M:
        if x['a']-0.05 <= t <= x['b']+0.05: return x['c0']+(t-x['a'])
    raise ValueError(t)
def caller_name(st): return 'DİNLƏYİCİ'
_S = [
    ('plan',   23.70, 30.20, 'call',   dict()),
    ('rice',   30.20, 38.30, 'stack',  dict()),
    ('veg',    38.30, 48.30, 'call',   dict()),
    ('veg2',   48.30, 51.85, 'stack',  dict()),
    ('nope',   51.85, 55.98, 'call',   dict()),
    ('tired',  55.98, 61.50, 'punchR', dict()),
    ('bring',  61.50, 65.70, 'stack',  dict()),
    ('meat',   65.70, 69.50, 'stack',  dict()),
    ('help',   103.20, 109.50, 'stack', dict(trans='cut')),
    ('phone',  109.50, 118.30, 'soloR', dict()),
    ('swear',  118.30, 123.00, 'stack', dict()),
    ('gel',    123.00, 124.80, 'punchR', dict()),
    ('fam',    130.30, 138.90, 'stack', dict(trans='cut')),
    ('oba',    235.60, 241.05, 'stack', dict(trans='cut')),
    ('chick',  241.05, 249.10, 'punchR', dict()),
    ('fish',   249.10, 256.60, 'stack', dict()),
    ('potato', 256.60, 268.90, 'punchR', dict()),
    ('pan',    268.90, 276.80, 'stack', dict()),
    ('end',    276.80, 282.10, 'stack', dict()),
]
_C = [(n, dict(a=mp(a), b=mp(b)-0.01, lay=l, **x)) for n, a, b, l, x in _S]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

_SPK = [
    (23.7, 26.0, 'R'), (26.0, 30.2, 'P'), (30.2, 33.6, 'R'), (33.6, 34.6, 'P'), (34.6, 35.3, 'R'), (35.3, 38.3, 'P'),
    (38.3, 41.9, 'P'), (41.9, 51.85, 'R'), (51.85, 55.98, 'P'), (55.98, 65.0, 'R'), (65.0, 65.8, 'P'), (65.8, 69.5, 'R'),
    (103.2, 104.95, 'R'), (104.95, 106.4, 'P'), (106.4, 124.8, 'R'),
    (130.3, 135.1, 'R'), (135.1, 136.8, 'P'), (136.8, 138.9, 'R'),
    (235.6, 239.5, 'R'), (239.5, 241.05, 'P'), (241.05, 251.0, 'R'), (251.0, 253.5, 'P'), (253.5, 255.25, 'R'),
    (255.25, 256.55, 'P'), (256.55, 282.1, 'R'),
]
def _ranges(a, b):
    out = []
    for x in _M:
        lo, hi = max(a, x['a']), min(b, x['b'])
        if hi > lo: out.append((x['c0']+(lo-x['a']), x['c0']+(hi-x['a'])))
    return out
SPEAKERS = [(r0, r1, k) for a, b, k in _SPK for r0, r1 in _ranges(a, b)]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.95}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

_CAP = [
    ('R', 23.78, 25.82, 'Axşama nə bişirməyi planınızda var?', dict(hi=['bişirməyi'])),
    ('P', 26.10, 30.14, 'İnanın, çox fikirləşirəm ona. Mənim oğlum vegetariandır.', dict(hi=['vegetariandır.'])),
    ('R', 30.26, 33.20, 'Yaxşı, dünən nə bişirmişdiniz o vegetarian oğlunuz üçün?', dict(hi=['vegetarian'])),
    ('P', 33.84, 34.36, 'Düyü.', dict(big=True)),
    ('R', 34.76, 35.28, 'Düyü?', dict(big=True)),
    ('P', 39.78, 41.70, 'Yox, əti yemir axı. Vegetariandır.', dict(hi=['əti', 'yemir'])),
    ('R', 44.74, 46.10, 'Heç kəsə qismət olmasın!', dict(hi=['qismət'])),
    ('P', 51.92, 53.64, 'Onu yemirəm, bunu yemirəm.', dict(big=True, hi=['YEMİRƏM,', 'YEMİRƏM.'])),
    ('P', 55.02, 55.90, '...soğanı olmasın.', dict(hi=['soğanı'])),
    ('R', 58.48, 59.10, 'Adam yorulur!', dict(big=True)),
    ('R', 61.82, 64.00, 'Onu gətirin... söhbət eləsin.', {}),
    ('R', 65.80, 67.42, 'Ətsevər dostunuz buradadır.', dict(hi=['Ətsevər'])),
    ('R', 103.24, 104.90, 'Sizə kimsə kömək elədimi bu barədə?', {}),
    ('P', 104.98, 106.30, 'Mənim o vegetarian oğlum.', dict(hi=['vegetarian'])),
    ('R', 106.54, 108.34, 'Vegetarian oğlunuz kömək elədi.', dict(hi=['Vegetarian'])),
    ('R', 110.76, 114.90, 'Vegetarian oğlunuz da telefona yaxın qalsın, sualı dinləyin.', dict(hi=['Vegetarian'])),
    ('R', 118.36, 120.30, 'Həmin o vegetarian oğlum.', dict(hi=['vegetarian'])),
    ('R', 120.56, 122.90, 'Elə deyirsiniz, elə bil söyürsünüz!', dict(big=True, hi=['SÖYÜRSÜNÜZ!'])),
    ('R', 123.10, 124.68, 'Gəl bura, vegetarian oğlum, gəl bura!', dict(hi=['vegetarian'])),
    ('R', 130.34, 131.70, 'Sualdan əvvəl bir sual...', {}),
    ('R', 131.94, 135.12, 'Sizdə ailədə oğlunuzdan başqa vegetarian var? Məsələn, atası?', dict(hi=['atası?'])),
    ('P', 135.12, 136.66, 'Xeyr, yox, yox, hamı ət yeyəndir.', dict(hi=['ət'])),
    ('R', 136.90, 138.56, 'Hamı ət yeyəndir, bir dənə bu uşaq...', {}),
    ('R', 235.70, 239.28, 'Oğlunuzdan gedib OBA-dan ət alarsınız.', dict(hi=['OBA-dan', 'ət'])),
    ('P', 239.58, 241.02, 'Bizim qapımızın ağzındadır OBA.', dict(hi=['OBA.'])),
    ('R', 241.02, 248.00, 'Bu şərəfə oğlunuza bu gün bir toyuq... düyünün altında bir toyuq gizlədin.', dict(hi=['toyuq', 'gizlədin.'])),
    ('R', 248.06, 249.00, 'Gizlədin, qoy bilməsin!', dict(big=True, hi=['GİZLƏDİN,'])),
    ('R', 249.64, 250.62, 'Balıq da yemir?', dict(hi=['Balıq'])),
    ('P', 251.24, 253.44, 'Yox, heç balığı yaxın qoymur.', {}),
    ('R', 253.56, 254.38, 'Heç nə yemir.', {}),
    ('R', 254.46, 255.24, 'Kartof yeyir?', dict(hi=['Kartof'])),
    ('P', 255.30, 256.52, 'Kartof yeyir. Yeyir, yeyir.', dict(hi=['Kartof'])),
    ('R', 256.52, 259.38, 'Yaxşı, ona sual verin ki...', {}),
    ('R', 259.60, 261.00, 'Kartof da bir canlıdır da!', dict(big=True, hi=['CANLIDIR'])),
    ('R', 261.22, 263.90, 'Onu da əkirlər, becərirlər axı, onu da dərirlər...', {}),
    ('R', 269.08, 272.10, 'Yəni onu da kəsib, doğrayıb, atırlar tavaya...', dict(hi=['tavaya...'])),
    ('R', 274.12, 276.50, 'Nəsə, vegetarianlarla bir söhbət eləmək lazımdır.', dict(hi=['söhbət'])),
    ('R', 276.90, 279.96, 'Onların fikrini eşitib danışmaq lazımdır. Amma sizi təbrik edirik.', {}),
    ('R', 280.10, 282.00, 'Sağ olun, Allah razı olsun hamınızdan.', {}),
]
CAPTIONS = [(k, mp(a), mp(b), t, o) for k, a, b, t, o in _CAP]

LAUGHS = []
def COUNTER_START(s2o): return 1e9
def FLASHES(s2o): return []
def SHAKES(s2o): return []
def _o(s2o, t, c=None):
    try: ct = mp(t)
    except ValueError: return None
    if c:
        cl = CLIPS[ci(c)]
        ct = min(max(ct, cl['a']), cl['b'])
        return s2o(ct, ci(c))
    return s2o(ct)

def GAGS(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    G = []
    def em(code, t0, t1, x, y, size=170, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='emoji', code=code, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    def lab(text, t0, t1, x, y, size=44, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='label', text=text, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    def kin(text, t0, t1, x=540, y=1560, size=96, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='kinetic', text=text, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    def burst(code, t, c, n=6, dur=1.6, size=110):
        t0 = o(t, c)
        if t0 is None: return
        r = random.Random(int(t*100))
        for i in range(n):
            side = -1 if i % 2 == 0 else 1
            x0 = 540+side*r.uniform(440, 500); y0 = 1650+r.uniform(-20, 60)
            G.append(dict(kind='float', code=code, t0=t0+i*0.12, t1=t0+i*0.12+dur, xy=(x0, y0),
                          to=(x0+side*r.uniform(-10, 20), y0-r.uniform(900, 1300)), size=int(size*0.85*r.uniform(0.8, 1.2)), rot=r.uniform(-20, 20)))
    lab('QALA MASSİVİNDƏN ZƏNG', o(23.75, 'plan'), o(26.30, 'plan'), 540, 1480, 46, emoji='1f4de')
    em('1f468-200d-1f373', o(23.90, 'plan'), o(26.00, 'plan'), 950, 330, 130)
    kin('OĞLUM VEGETARİANDIR', o(28.10, 'plan'), o(30.20, 'plan'), 540, 1560, 70, accent=GREEN)
    em('1f966', o(28.20, 'plan'), o(30.20, 'plan'), 950, 330, 130)
    burst('1f966', 28.3, 'plan', n=5, dur=1.8)
    em('1f35a', o(33.84, 'rice'), o(35.35, 'rice'), 880, 420, 190)
    em('1f914', o(34.76, 'rice'), o(35.35, 'rice'), 170, 1200, 160)
    em('1f6ab', o(39.80, 'veg'), o(41.80, 'veg'), 950, 330, 130)
    em('1f969', o(39.80, 'veg'), o(41.80, 'veg'), 120, 330, 130)
    em('1f62e', o(44.80, 'veg'), o(48.30, 'veg'), 950, 330, 130)
    em('1f644', o(52.00, 'nope'), o(55.98, 'nope'), 950, 330, 130)
    em('1f9c5', o(55.00, 'nope'), o(55.98, 'nope'), 120, 330, 130)
    em('1f35a', o(56.10, 'tired'), o(57.70, 'tired'), 880, 420, 170)
    em('1f62b', o(58.40, 'tired'), o(61.50, 'tired'), 880, 420, 190)
    em('1f357', o(65.80, 'meat'), o(69.50, 'meat'), 880, 420, 190)
    kin('ƏTSEVƏR DOST', o(66.00, 'meat'), o(69.40, 'meat'), 540, 1560, 80, accent=(255, 170, 110))
    burst('1f602', 68.6, 'meat', n=5, dur=1.4)
    em('1f966', o(105.00, 'help'), o(109.50, 'help'), 880, 420, 170)
    lab('KÖMƏKÇİ: VEGETARİAN OĞUL', o(105.10, 'help'), o(109.40, 'help'), 540, 1560, 40, accent=GREEN, emoji='1f966')
    em('1f44b', o(123.10, 'gel'), o(124.80, 'gel'), 880, 420, 180)
    em('1f4f1', o(110.80, 'phone'), o(118.30, 'phone'), 900, 330, 150)
    em('1f966', o(111.00, 'phone'), o(118.30, 'phone'), 160, 330, 140)
    em('1f92c', o(120.60, 'swear'), o(123.00, 'swear'), 880, 420, 190)
    em('1f602', o(121.20, 'swear'), o(123.00, 'swear'), 170, 1200, 170)
    burst('1f923', 121.6, 'swear', n=6, dur=1.5)
    em('1f914', o(130.40, 'fam'), o(131.90, 'fam'), 880, 420, 160)
    em('1f64f', o(280.20, 'end'), o(282.10, 'end'), 880, 420, 170)
    burst('1f966', 280.3, 'end', n=6, dur=1.6)
    burst('1f966', 123.2, 'gel', n=4, dur=1.5)
    em('1f468', o(132.00, 'fam'), o(135.12, 'fam'), 880, 420, 160)
    em('1f357', o(135.20, 'fam'), o(138.90, 'fam'), 880, 420, 180)
    em('1f966', o(136.80, 'fam'), o(138.90, 'fam'), 170, 1200, 150)
    kin('HAMI ƏT YEYƏNDİR', o(135.30, 'fam'), o(138.50, 'fam'), 540, 1560, 78, accent=(255, 170, 110))
    em('1f6d2', o(237.20, 'oba'), o(241.05, 'oba'), 880, 420, 190)
    kin('OBA', o(239.60, 'oba'), o(241.05, 'oba'), 540, 1560, 120, accent=OBA_Y)
    em('1f414', o(242.00, 'chick'), o(249.10, 'chick'), 880, 420, 190)
    em('1f35a', o(245.00, 'chick'), o(249.10, 'chick'), 170, 1200, 170)
    kin('DÜYÜNÜN ALTINDA TOYUQ', o(245.50, 'chick'), o(248.00, 'chick'), 540, 1560, 62, accent=(255, 200, 120))
    em('1f92b', o(248.06, 'chick'), o(249.10, 'chick'), 170, 1200, 180)
    burst('1f357', 246.0, 'chick', n=6, dur=1.8)
    burst('1f923', 248.0, 'chick', n=6, dur=1.1)
    em('1f41f', o(249.60, 'fish'), o(253.50, 'fish'), 880, 420, 180)
    em('1f6ab', o(251.30, 'fish'), o(253.50, 'fish'), 170, 1200, 160)
    em('1f954', o(254.46, 'fish'), o(256.60, 'fish'), 880, 420, 190)
    burst('1f954', 255.3, 'fish', n=5, dur=1.4)
    em('1f914', o(256.60, 'potato'), o(259.50, 'potato'), 880, 420, 170)
    em('1f954', o(259.70, 'potato'), o(268.90, 'potato'), 880, 420, 190)
    em('1f331', o(261.30, 'potato'), o(264.00, 'potato'), 170, 1200, 160)
    burst('1f954', 259.8, 'potato', n=7, dur=2.0)
    em('1f373', o(269.10, 'pan'), o(272.40, 'pan'), 880, 420, 190)
    em('1f62d', o(271.20, 'pan'), o(274.00, 'pan'), 170, 1200, 170)
    burst('1f923', 272.0, 'pan', n=6, dur=1.6)
    lab('VEGETARİANLARLA SÖHBƏT LAZIMDIR', o(274.20, 'pan'), o(276.80, 'pan'), 540, 1760, 38, accent=GREEN, emoji='1f966')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

def PUNCHES(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [o(120.60, 'swear'), o(122.10, 'swear'), o(110.80, 'phone'), o(28.10, 'plan'), o(33.84, 'rice'), o(34.76, 'rice'), o(51.95, 'nope'), o(58.50, 'tired'), o(66.00, 'meat'),
            o(105.00, 'help'), o(123.10, 'gel'), o(135.20, 'fam'), o(239.60, 'oba'), o(245.50, 'chick'), o(248.06, 'chick'),
            o(249.64, 'fish'), o(254.46, 'fish'), o(259.60, 'potato'), o(269.10, 'pan'), o(271.20, 'pan')]

MUSIC_LEVEL = 0.13
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (o(26.10, 'plan'), o(30.20, 'plan'), 0.09), (o(38.30, 'veg'), o(48.30, 'veg'), 0.09), (o(51.85, 'nope'), o(55.98, 'nope'), 0.09), (o(120.50, 'swear'), o(120.70, 'swear'), 0.0), (o(121.00, 'swear'), o(123.00, 'swear'), 0.20),
        (o(248.00, 'chick'), o(249.10, 'chick'), 0.22),
        (o(259.40, 'potato'), o(259.70, 'potato'), 0.0),
        (o(271.00, 'pan'), o(274.00, 'pan'), 0.20),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(23.75, 'plan'), 0.12), ('pop', o(23.90, 'plan'), 0.09), ('sparkle', o(28.10, 'plan'), 0.10), ('pop2', o(28.30, 'plan'), 0.08),
        ('pop', o(33.84, 'rice'), 0.10), ('boing', o(34.76, 'rice'), 0.11), ('bonk', o(39.80, 'veg'), 0.10), ('pop', o(44.80, 'veg'), 0.08),
        ('whoosh', o(51.90, 'nope'), 0.10), ('bonk', o(51.95, 'nope'), 0.11), ('pop', o(55.00, 'nope'), 0.08),
        ('pop', o(56.10, 'tired'), 0.08), ('slide_down', o(58.40, 'tired'), 0.10), ('bonk', o(58.60, 'tired'), 0.10),
        ('pop2', o(65.80, 'meat'), 0.09), ('sparkle', o(66.00, 'meat'), 0.09), ('pop', o(68.60, 'meat'), 0.07),
        ('whoosh', o(103.25, 'help'), 0.10), ('sparkle', o(105.00, 'help'), 0.09), ('pop', o(106.60, 'help'), 0.07),
        ('whoosh', o(110.70, 'phone'), 0.09), ('pop', o(111.00, 'phone'), 0.08), ('pop', o(118.40, 'swear'), 0.07),
        ('bonk', o(120.60, 'swear'), 0.11), ('badumtss', o(122.20, 'swear'), 0.13), ('pop', o(130.40, 'fam'), 0.08),
        ('sparkle', o(280.20, 'end'), 0.10), ('pop', o(280.40, 'end'), 0.07),
        ('boing', o(123.10, 'gel'), 0.11), ('pop', o(123.40, 'gel'), 0.08),
        ('whoosh', o(131.85, 'fam'), 0.09), ('pop', o(134.00, 'fam'), 0.08), ('bonk', o(135.20, 'fam'), 0.10),
        ('whoosh', o(235.65, 'oba'), 0.10), ('pop', o(237.20, 'oba'), 0.08), ('sparkle', o(239.60, 'oba'), 0.11),
        ('whoosh', o(241.10, 'chick'), 0.10), ('pop', o(242.00, 'chick'), 0.08), ('pop2', o(245.00, 'chick'), 0.08), ('sparkle', o(245.50, 'chick'), 0.10),
        ('boing', o(248.06, 'chick'), 0.12), ('badumtss', o(248.40, 'chick'), 0.13),
        ('pop', o(249.70, 'fish'), 0.08), ('bonk', o(251.30, 'fish'), 0.09), ('pop2', o(254.50, 'fish'), 0.09), ('pop', o(255.40, 'fish'), 0.08),
        ('tick', o(257.00, 'potato'), 0.08), ('riser', o(258.40, 'potato'), 0.07), ('bonk', o(259.60, 'potato'), 0.12), ('sparkle', o(259.80, 'potato'), 0.10),
        ('whoosh', o(269.10, 'pan'), 0.09), ('bonk', o(271.20, 'pan'), 0.11), ('badumtss', o(272.20, 'pan'), 0.14), ('ding', o(274.20, 'pan'), 0.09),
    ]
