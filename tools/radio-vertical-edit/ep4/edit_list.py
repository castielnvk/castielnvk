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
    ('rice',   30.20, 35.35, 'stack',  dict()),
    ('veg',    38.30, 48.30, 'call',   dict(trans='cut')),
    ('nope',   51.85, 53.70, 'punchL', dict(trans='cut')),
    ('meat',   65.70, 69.50, 'stack',  dict(trans='cut')),
    ('gent',   72.20, 74.40, 'stack',  dict(trans='cut')),
    ('gentN',  74.40, 75.70, 'stack',  dict(hide='L')),
    ('gent2',  75.70, 81.70, 'stack',  dict()),
    ('step',   89.60, 95.00, 'punchL', dict(trans='cut')),
    ('ok1',    101.90, 108.50, 'stack', dict(trans='cut')),
    ('fam',    131.80, 138.60, 'stack', dict(trans='cut')),
    ('quiz',   145.80, 156.10, 'soloR', dict(trans='cut')),
    ('ans',    168.40, 170.20, 'call',  dict(trans='cut')),
    ('ast',    178.40, 183.90, 'stack', dict(trans='cut')),
    ('astN',   183.90, 185.60, 'punchR', dict(hide='L')),
    ('bravo',  223.40, 225.60, 'stack', dict(trans='cut')),
    ('oba',    235.60, 241.05, 'stack', dict(trans='cut')),
    ('chick',  241.05, 249.10, 'punchR', dict(trans='cut')),
]
_C = [(n, dict(a=mp(a), b=mp(b)-0.01, lay=l, **x)) for n, a, b, l, x in _S]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

_SPK = [
    (23.7, 26.0, 'R'), (26.0, 30.2, 'P'), (30.2, 33.6, 'R'), (33.6, 34.6, 'P'), (34.6, 35.35, 'R'),
    (38.3, 41.9, 'P'), (41.9, 48.3, 'R'), (51.85, 53.7, 'P'), (65.7, 69.5, 'R'),
    (72.2, 77.1, 'R'), (77.1, 78.4, 'P'), (78.4, 79.3, 'R'), (79.3, 80.1, 'P'), (80.1, 81.7, 'L'),
    (89.6, 94.2, 'L'), (94.2, 95.0, 'P'), (101.9, 104.95, 'R'), (104.95, 106.4, 'P'), (106.4, 108.5, 'R'),
    (131.8, 135.1, 'R'), (135.1, 136.8, 'P'), (136.8, 138.6, 'R'), (145.8, 156.1, 'R'),
    (168.4, 170.2, 'P'), (178.4, 180.7, 'R'), (180.7, 181.4, 'P'), (181.4, 185.6, 'R'),
    (223.4, 225.6, 'R'), (235.6, 239.5, 'R'), (239.5, 241.05, 'P'), (241.05, 249.1, 'R'),
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
    ('R', 65.80, 67.42, 'Ətsevər dostunuz buradadır.', dict(hi=['Ətsevər'])),
    ('R', 73.32, 77.12, 'Nə şəkli gördünüz, haranı gördünüz Instagram hekayəmizdə?', {}),
    ('P', 77.12, 78.30, 'Gent şəhəri.', dict(hi=['Gent'])),
    ('R', 78.50, 79.06, 'Gent?', dict(big=True)),
    ('P', 79.48, 80.04, 'Bəli.', {}),
    ('L', 80.16, 81.64, 'Qala massivinə yaxındır bu Gent?', dict(hi=['yaxındır'])),
    ('L', 89.70, 94.10, 'Deməli, Belçikanın Gent şəhəri Qala massivinin tam bir addımlığındadır, eləmi?', dict(hi=['addımlığındadır,'])),
    ('P', 94.38, 94.94, 'Bəli.', dict(big=True)),
    ('R', 102.06, 103.08, 'Cavab doğrudur!', dict(hi=['doğrudur!'])),
    ('R', 103.24, 104.90, 'Sizə kimsə kömək elədimi bu barədə?', {}),
    ('P', 104.98, 106.30, 'Mənim o vegetarian oğlum.', dict(hi=['vegetarian'])),
    ('R', 106.54, 108.34, 'Vegetarian oğlunuz kömək elədi.', dict(hi=['Vegetarian'])),
    ('R', 131.94, 135.12, 'Sizdə ailədə oğlunuzdan başqa vegetarian var? Məsələn, atası?', dict(hi=['atası?'])),
    ('P', 135.12, 136.66, 'Xeyr, yox, yox, hamı ət yeyəndir.', dict(hi=['ət'])),
    ('R', 145.90, 150.82, 'Müslüm Maqomayevin adı təkcə konsert afişalarında qalmayıb,', dict(hi=['Maqomayevin'])),
    ('R', 151.36, 155.96, 'kosmosa da çıxıb. Onun adı hansı növ göy cisminə verilib?', dict(hi=['kosmosa', 'cisminə'])),
    ('P', 168.50, 170.06, 'Asteroid, kiçik planet.', dict(hi=['Asteroid,'])),
    ('R', 178.56, 180.58, 'Asteroid? Asteroid dediniz?', {}),
    ('P', 180.82, 181.32, 'Bəli.', {}),
    ('R', 181.46, 182.70, 'Asteroidə olmuşsunuz, ümumiyyətlə?', dict(big=True, hi=['ASTEROİDƏ'])),
    ('R', 224.08, 224.72, 'Bravo!', dict(big=True)),
    ('R', 235.70, 239.28, 'Oğlunuzdan gedib OBA-dan ət alarsınız.', dict(hi=['OBA-dan', 'ət'])),
    ('P', 239.58, 241.02, 'Bizim qapımızın ağzındadır OBA.', dict(hi=['OBA.'])),
    ('R', 241.02, 248.00, 'Bu şərəfə oğlunuza bu gün bir toyuq... düyünün altında bir toyuq gizlədin.', dict(hi=['toyuq', 'gizlədin.'])),
    ('R', 248.06, 249.00, 'Gizlədin, qoy bilməsin!', dict(big=True, hi=['GİZLƏDİN,'])),
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
    # intro
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
    em('1f644', o(52.00, 'nope'), o(53.70, 'nope'), 880, 420, 180)
    em('1f357', o(65.80, 'meat'), o(69.50, 'meat'), 880, 420, 190)
    kin('ƏTSEVƏR DOST', o(66.00, 'meat'), o(69.40, 'meat'), 540, 1560, 80, accent=(255, 170, 110))
    burst('1f602', 68.6, 'meat', n=5, dur=1.4)
    # Gent quiz
    em('1f4f8', o(73.40, 'gent'), o(74.40, 'gent'), 880, 420, 170)
    em('1f1e7-1f1ea', o(77.20, 'gent2'), o(81.70, 'gent2'), 880, 420, 180)
    em('1f3f0', o(80.20, 'gent2'), o(81.70, 'gent2'), 170, 1200, 160)
    lab('GENT = QALA MASSİVİ?', o(80.20, 'gent2'), o(81.70, 'gent2'), 540, 1560, 44, accent=SKY)
    kin('BİR ADDIMLIQ!', o(92.50, 'step'), o(95.00, 'step'), 540, 1560, 96, accent=SKY)
    em('1f9d0', o(90.00, 'step'), o(95.00, 'step'), 880, 420, 180)
    burst('1f923', 94.5, 'step', n=6, dur=1.6)
    em('2705', o(102.10, 'ok1'), o(103.20, 'ok1'), 880, 420, 170)
    em('1f966', o(105.00, 'ok1'), o(108.50, 'ok1'), 880, 420, 170)
    lab('KÖMƏKÇİ: VEGETARİAN OĞUL', o(105.10, 'ok1'), o(108.40, 'ok1'), 540, 1560, 40, accent=GREEN, emoji='1f966')
    em('1f468', o(134.00, 'fam'), o(135.12, 'fam'), 880, 420, 160)
    em('1f357', o(135.20, 'fam'), o(138.60, 'fam'), 880, 420, 180)
    em('1f966', o(136.80, 'fam'), o(138.60, 'fam'), 170, 1200, 150)
    # asteroid
    em('1f3a4', o(146.00, 'quiz'), o(150.80, 'quiz'), 900, 330, 150)
    em('1fa90', o(151.40, 'quiz'), o(156.10, 'quiz'), 900, 330, 150)
    em('1f52d', o(153.50, 'quiz'), o(156.10, 'quiz'), 160, 330, 140)
    kin('ASTEROİD', o(168.55, 'ans'), o(170.20, 'ans'), 540, 1480, 92, accent=(200, 170, 255))
    em('2604', o(168.60, 'ans'), o(170.20, 'ans'), 950, 330, 130)
    em('1f680', o(181.60, 'ast'), o(183.90, 'ast'), 880, 420, 190)
    burst('1f923', 182.8, 'ast', n=8, dur=2.0)
    em('1f923', o(183.95, 'astN'), o(185.60, 'astN'), 880, 420, 190)
    burst('2604', 184.0, 'astN', n=5, dur=1.6, size=100)
    burst('1f389', 224.1, 'bravo', n=8, dur=1.5)
    # OBA + chicken ending
    em('1f6d2', o(237.20, 'oba'), o(241.05, 'oba'), 880, 420, 190)
    kin('OBA', o(239.60, 'oba'), o(241.05, 'oba'), 540, 1560, 120, accent=OBA_Y)
    em('1f414', o(242.00, 'chick'), o(249.10, 'chick'), 880, 420, 190)
    em('1f35a', o(245.00, 'chick'), o(249.10, 'chick'), 170, 1200, 170)
    kin('DÜYÜNÜN ALTINDA TOYUQ', o(245.50, 'chick'), o(248.00, 'chick'), 540, 1560, 62, accent=(255, 200, 120))
    em('1f92b', o(248.06, 'chick'), o(249.10, 'chick'), 170, 1200, 180)
    burst('1f357', 246.0, 'chick', n=6, dur=1.8)
    burst('1f923', 248.0, 'chick', n=6, dur=1.1)
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

def PUNCHES(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [o(28.10, 'plan'), o(33.84, 'rice'), o(34.76, 'rice'), o(51.95, 'nope'), o(66.00, 'meat'), o(78.50, 'gent2'),
            o(92.50, 'step'), o(94.40, 'step'), o(102.10, 'ok1'), o(105.00, 'ok1'), o(135.20, 'fam'), o(168.55, 'ans'),
            o(181.50, 'ast'), o(183.95, 'astN'), o(224.10, 'bravo'), o(239.60, 'oba'), o(245.50, 'chick'), o(248.06, 'chick')]

MUSIC_LEVEL = 0.13
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (o(26.10, 'plan'), o(30.20, 'plan'), 0.09), (o(38.30, 'veg'), o(48.30, 'veg'), 0.09),
        (o(145.80, 'quiz'), o(156.10, 'quiz'), 0.06),        # quiz: tension
        (o(168.40, 'ans'), o(170.20, 'ans'), 0.0),
        (o(181.40, 'ast'), o(183.90, 'ast'), 0.0),           # silence on the punchline
        (o(183.90, 'astN'), o(185.60, 'astN'), 0.22),
        (o(223.40, 'bravo'), o(225.60, 'bravo'), 0.24),
        (o(248.00, 'chick'), o(249.10, 'chick'), 0.22),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(23.75, 'plan'), 0.12), ('pop', o(23.90, 'plan'), 0.09), ('sparkle', o(28.10, 'plan'), 0.10), ('pop2', o(28.30, 'plan'), 0.08),
        ('pop', o(33.84, 'rice'), 0.10), ('boing', o(34.76, 'rice'), 0.11), ('bonk', o(39.80, 'veg'), 0.10), ('pop', o(44.80, 'veg'), 0.08),
        ('whoosh', o(51.90, 'nope'), 0.10), ('bonk', o(51.95, 'nope'), 0.11), ('pop', o(52.40, 'nope'), 0.08),
        ('pop2', o(65.80, 'meat'), 0.09), ('sparkle', o(66.00, 'meat'), 0.09), ('pop', o(68.60, 'meat'), 0.07),
        ('whoosh', o(72.25, 'gent'), 0.10), ('pop', o(73.40, 'gent'), 0.08), ('ding', o(77.20, 'gent2'), 0.09), ('boing', o(78.50, 'gent2'), 0.11), ('pop', o(80.20, 'gent2'), 0.08),
        ('riser', o(90.60, 'step'), 0.08), ('bonk', o(92.50, 'step'), 0.12), ('badumtss', o(94.40, 'step'), 0.15), ('pop', o(94.60, 'step'), 0.07),
        ('ding', o(102.10, 'ok1'), 0.12), ('sparkle', o(105.00, 'ok1'), 0.09), ('pop', o(106.60, 'ok1'), 0.07),
        ('whoosh', o(131.85, 'fam'), 0.09), ('pop', o(134.00, 'fam'), 0.08), ('bonk', o(135.20, 'fam'), 0.10),
        ('whoosh', o(145.85, 'quiz'), 0.10), ('tick', o(150.0, 'quiz'), 0.09), ('tick', o(151.0, 'quiz'), 0.09), ('tick', o(152.0, 'quiz'), 0.09), ('tick', o(153.0, 'quiz'), 0.09), ('tick', o(154.0, 'quiz'), 0.09), ('tick', o(155.0, 'quiz'), 0.09),
        ('sparkle', o(168.55, 'ans'), 0.12), ('whoosh_up', o(168.60, 'ans'), 0.09),
        ('pop', o(178.60, 'ast'), 0.08), ('slide_up', o(181.40, 'ast'), 0.08), ('bonk', o(182.70, 'ast'), 0.12), ('pop2', o(183.00, 'ast'), 0.08), ('pop', o(183.30, 'ast'), 0.08),
        ('ding', o(224.08, 'bravo'), 0.14), ('sparkle', o(224.20, 'bravo'), 0.12), ('pop', o(224.50, 'bravo'), 0.08),
        ('whoosh', o(235.65, 'oba'), 0.10), ('pop', o(237.20, 'oba'), 0.08), ('sparkle', o(239.60, 'oba'), 0.11),
        ('whoosh', o(241.10, 'chick'), 0.10), ('pop', o(242.00, 'chick'), 0.08), ('pop2', o(245.00, 'chick'), 0.08), ('sparkle', o(245.50, 'chick'), 0.10),
        ('boing', o(248.06, 'chick'), 0.12), ('badumtss', o(248.40, 'chick'), 0.14),
    ]
