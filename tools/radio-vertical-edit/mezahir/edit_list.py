# Məzahir dayı poem — continuous, nothing cut. Source w13/combo.mov (watermark cleaned).
import json, os, random
from engine import YEL, MAG, CYA, INK, WHITE, PURP, WDIR
HEADER = ''
OBA_Y = (255, 205, 0); GOLD2 = (255, 211, 110); SKY = (140, 200, 255); PINK = (255, 140, 180)
def caller_name(st): return ''
_C = [
    ('intro',  dict(a=0.00,  b=3.70,  lay='stack')),
    ('l1',     dict(a=3.70,  b=7.80,  lay='soloR')),
    ('l2',     dict(a=7.80,  b=11.60, lay='punchR')),
    ('l3',     dict(a=11.60, b=14.70, lay='stack')),
    ('l4',     dict(a=14.70, b=19.80, lay='soloR')),
    ('l5',     dict(a=19.80, b=25.50, lay='stack')),
    ('l6',     dict(a=25.50, b=28.65, lay='soloR')),
    ('l7',     dict(a=28.65, b=32.00, lay='stack')),
    ('l8',     dict(a=32.00, b=36.15, lay='punchR')),
    ('l9',     dict(a=36.15, b=40.15, lay='stack')),
    ('l10',    dict(a=40.15, b=45.10, lay='punchR')),
    ('outro',  dict(a=45.10, b=49.40, lay='stack')),
    ('host',   dict(a=49.40, b=54.23, lay='stack')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]
SPEAKERS = [(0.0, 49.4, 'R'), (49.4, 54.24, 'R')]
SPK_GAIN = {'R': 1.0, 'L': 1.0, 'P': 1.0}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

CAPTIONS = [
    ('R', 3.74, 7.40, 'Artıq sona çatır Noyabr ayı.', dict(hi=['Noyabr', 'ayı.'])),
    ('R', 8.06, 11.20, 'Hardasan, darıxdıq Məzahir dayı.', dict(hi=['Məzahir', 'dayı.'])),
    ('R', 11.86, 14.60, 'Traktor alırsan Prior lizinqdən.', dict(hi=['Prior', 'lizinqdən.'])),
    ('R', 14.84, 18.90, 'İşləsin dörd fəsil, gözləmə yayı.', dict(hi=['dörd', 'fəsil,'])),
    ('R', 20.02, 24.70, 'Küləkli hava, əsir xəzri-gilavar.', dict(hi=['xəzri-gilavar.'])),
    ('R', 25.70, 28.60, 'Bir restoran var, adı Gilavar.', dict(hi=['Gilavar.'])),
    ('R', 28.76, 31.95, 'Səhər yeməyinin öz ləzzəti var.', dict(hi=['ləzzəti'])),
    ('R', 32.08, 36.10, 'Maşının Jaecoo J8, yanında gözəl bir yar.', dict(hi=['Jaecoo', 'J8,', 'yar.'])),
    ('R', 36.22, 40.10, 'Şeirim bitməyib hələ, bunun ardı var.', dict(hi=['ardı'])),
    ('R', 40.18, 45.00, 'Şeirim bitməyib hələ, bunun ardı var!', dict(big=True, hi=['ARDI', 'VAR!'])),
]

LAUGHS = []
def COUNTER_START(s2o): return 1e9
def FLASHES(s2o): return []
def SHAKES(s2o): return []
def _o(s2o, t, c=None):
    if c:
        cl = CLIPS[ci(c)]
        t = min(max(t, cl['a']), cl['b'])
        return s2o(t, ci(c))
    return s2o(t)

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
    def burst(code, t, c, n=6, dur=1.6, size=100):
        t0 = o(t, c)
        if t0 is None: return
        r = random.Random(int(t*100))
        for i in range(n):
            side = -1 if i % 2 == 0 else 1
            x0 = 540+side*r.uniform(440, 500); y0 = 1650+r.uniform(-20, 60)
            G.append(dict(kind='float', code=code, t0=t0+i*0.12, t1=t0+i*0.12+dur, xy=(x0, y0),
                          to=(x0+side*r.uniform(-10, 20), y0-r.uniform(900, 1300)), size=int(size*0.85*r.uniform(0.8, 1.2)), rot=r.uniform(-20, 20)))
    kin('MƏZAHİR DAYI', o(0.20, 'intro'), o(3.65, 'intro'), 540, 1560, 100, accent=GOLD2)
    lab('ŞEİR VAXTI', o(0.40, 'intro'), o(3.65, 'intro'), 540, 1720, 40, emoji='1f4dc')
    em('1f3a4', o(0.30, 'intro'), o(3.65, 'intro'), 880, 420, 170)
    em('1f342', o(4.60, 'l1'), o(7.80, 'l1'), 900, 330, 150)
    burst('1f342', 5.8, 'l1', n=6, dur=2.0)
    em('1f9d3', o(9.80, 'l2'), o(11.60, 'l2'), 880, 420, 190)
    burst('1f60d', 10.0, 'l2', n=5, dur=1.5)
    em('1f69c', o(11.90, 'l3'), o(14.70, 'l3'), 880, 420, 190)
    em('1f4b8', o(13.30, 'l3'), o(14.70, 'l3'), 170, 1200, 160)
    em('2600', o(15.80, 'l4'), o(16.60, 'l4'), 900, 330, 140)
    em('1f342', o(16.60, 'l4'), o(17.40, 'l4'), 900, 330, 140)
    em('2744', o(17.40, 'l4'), o(18.20, 'l4'), 900, 330, 140)
    em('1f338', o(18.20, 'l4'), o(19.80, 'l4'), 900, 330, 140)
    em('1f32c', o(20.10, 'l5'), o(25.50, 'l5'), 880, 420, 180)
    burst('1f32c', 23.0, 'l5', n=6, dur=1.8)
    em('1f37d', o(26.50, 'l6'), o(28.65, 'l6'), 900, 330, 150)
    em('1f373', o(29.90, 'l7'), o(32.00, 'l7'), 880, 420, 180)
    em('1f697', o(33.30, 'l8'), o(36.15, 'l8'), 880, 420, 190)
    em('1f60d', o(35.20, 'l8'), o(36.15, 'l8'), 170, 1200, 170)
    burst('2764', 35.3, 'l8', n=6, dur=1.6)
    em('23f3', o(38.30, 'l9'), o(40.15, 'l9'), 880, 420, 170)
    em('1f4dc', o(42.60, 'l10'), o(45.10, 'l10'), 880, 420, 190)
    burst('1f44f', 43.5, 'l10', n=7, dur=1.8)
    em('1f3b6', o(45.20, 'outro'), o(49.40, 'outro'), 880, 420, 180)
    burst('1f3b6', 45.4, 'outro', n=8, dur=2.0)
    kin('ARDI VAR...', o(45.20, 'outro'), o(49.30, 'outro'), 540, 1560, 100, accent=GOLD2)
    lab('MƏZAHİR DAYI · 100% SƏHƏR ŞOUSU', o(51.00, 'host'), o(54.20, 'host'), 540, 1740, 40, emoji='1f44f')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []
def PUNCHES(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [o(0.20, 'intro'), o(9.88, 'l2'), o(13.30, 'l3'), o(23.00, 'l5'), o(27.80, 'l6'), o(33.40, 'l8'),
            o(35.70, 'l8'), o(39.00, 'l9'), o(43.20, 'l10'), o(45.20, 'outro')]

MUSIC_LEVEL = 0.11
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [(o(45.10, 'outro'), o(49.40, 'outro'), 0.16)]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(0.15, 'intro'), 0.12), ('sparkle', o(0.30, 'intro'), 0.10),
        ('pop', o(4.60, 'l1'), 0.07), ('sparkle', o(9.88, 'l2'), 0.10), ('pop', o(11.90, 'l3'), 0.08), ('pop2', o(13.30, 'l3'), 0.07),
        ('pop', o(15.80, 'l4'), 0.06), ('pop', o(16.60, 'l4'), 0.06), ('pop', o(17.40, 'l4'), 0.06), ('pop', o(18.20, 'l4'), 0.06),
        ('whoosh', o(20.10, 'l5'), 0.09), ('pop', o(26.50, 'l6'), 0.07), ('pop2', o(29.90, 'l7'), 0.07),
        ('whoosh', o(33.30, 'l8'), 0.09), ('sparkle', o(35.30, 'l8'), 0.10), ('tick', o(38.30, 'l9'), 0.08),
        ('sparkle', o(43.20, 'l10'), 0.11), ('ding', o(44.90, 'l10'), 0.10), ('sparkle', o(51.00, 'host'), 0.09),
    ]
