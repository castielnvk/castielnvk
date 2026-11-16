# Şəfəq xanım viral reel. Times on combined source w7/combo.mov (see w7/map.json).
# Caption rule: only clearly heard words, as spoken; unclear speech (her name attempts) gets NO caption.
from engine import YEL, MAG, CYA, INK, WHITE, PURP
HEADER = ''
OBA_Y = (255, 205, 0)
def caller_name(st): return 'ŞƏFƏQ XANIM'
_C = [
    ('city',   dict(a=0.00,   b=9.20,   lay='stack')),
    ('addr',   dict(a=11.20,  b=15.50,  lay='call', trans='cut')),
    ('cow',    dict(a=15.50,  b=32.45,  lay='stack')),
    ('q',      dict(a=32.50,  b=38.40,  lay='stack', trans='cut')),
    ('prob',   dict(a=38.40,  b=44.50,  lay='call')),
    ('try',    dict(a=44.50,  b=55.60,  lay='stack', hide='L')),
    ('lol',    dict(a=55.60,  b=72.75,  lay='stack', hide='L', trans='cut')),
    ('try2',   dict(a=72.80,  b=77.55,  lay='stack', trans='cut')),
    ('belə',   dict(a=77.60,  b=81.45,  lay='stack', hide='L', trans='cut')),
    ('slo',    dict(a=81.50,  b=83.25,  lay='stack', trans='cut')),
    ('quiz0',  dict(a=83.30,  b=91.35,  lay='stack', trans='cut')),
    ('quiz',   dict(a=91.40,  b=103.85, lay='soloR', trans='cut')),
    ('sura',   dict(a=103.90, b=105.95, lay='stack', trans='cut')),
    ('ok',     dict(a=106.00, b=108.15, lay='stack', trans='cut')),
    ('win',    dict(a=108.20, b=109.25, lay='stack', trans='cut')),
    ('route',  dict(a=109.25, b=113.00, lay='stack', hide='L')),
    ('route2', dict(a=113.00, b=115.90, lay='stack')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

SPEAKERS = [
    (0.0, 3.3, 'R'), (3.3, 6.1, 'P'), (6.1, 9.2, 'R'), (11.2, 12.9, 'R'), (12.9, 15.5, 'P'),
    (15.5, 32.5, 'R'), (32.5, 35.6, 'R'), (35.6, 37.4, 'P'), (37.4, 38.3, 'R'), (38.3, 41.0, 'P'),
    (41.0, 42.6, 'R'), (42.6, 44.6, 'P'), (44.6, 46.5, 'R'), (46.5, 53.4, 'P'), (53.4, 61.0, 'R'),
    (61.0, 64.5, 'P'), (72.8, 75.3, 'P'), (75.3, 76.3, 'R'), (76.3, 77.6, 'P'), (77.6, 83.3, 'R'),
    (83.3, 115.9, 'R'),
]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.95}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

CAPTIONS = [
    ('R', 0.00, 2.90, 'Şəfəq xanım, Sabirabadın özündəsiniz, ya kəndində?', dict(hi=['kəndində?'])),
    ('R', 6.18, 6.70, 'Nə deyir?', {}),
    ('R', 7.08, 9.10, 'Güya özüdür, amma bilinmir harda.', dict(hi=['bilinmir'])),
    ('P', 13.10, 15.20, 'Sabirabad şəhəri, Şəhriyar küçəsi.', dict(hi=['şəhəri,'])),
    ('R', 16.32, 17.60, 'Şəhərin mərkəzində inək olur.', dict(big=True, hi=['İNƏK', 'inək'])),
    ('R', 17.78, 20.80, 'Mərkəzində inək olanda, deyək ki, niyə bura şəhərdir?', dict(hi=['şəhərdir?'])),
    ('R', 22.40, 23.60, 'İnək rast gəlmir sizə?', dict(hi=['İnək'])),
    ('R', 26.54, 27.70, 'Sabirabad, inək olurmu?', dict(hi=['inək'])),
    ('R', 32.50, 35.30, 'Hansı şəhərdir bizim Instagram səhifəsində?', dict(hi=['şəhərdir'])),
    ('P', 38.48, 40.95, 'Mənim də problemim var.', dict(hi=['problemim'])),
    ('R', 45.04, 45.90, 'Nə dediniz?', {}),
    ('R', 53.90, 55.40, 'Rüfət öldü...', dict(big=True, hi=['ÖLDÜ...', 'öldü...'])),
    ('R', 56.46, 59.00, 'Şəfəq xanım, bir də mən tam fon səsi də alıram.', {}),
    ('R', 75.44, 75.90, 'Nə?', dict(big=True)),
    ('R', 77.60, 78.95, 'Lyublyana, belə.', dict(big=True, hi=['LYUBLYANA,', 'Lyublyana,'])),
    ('R', 81.86, 83.20, 'Sloveniya şəhəri idi.', dict(hi=['Sloveniya'])),
    ('R', 83.30, 84.50, 'İndi sual verəcəyik sizə.', {}),
    ('R', 84.50, 85.94, 'Sualı təqdim edirik, diqqətli olun.', {}),
    ('R', 88.62, 91.20, 'O sualı kartof məsələsinə çevirməyin, diqqətli olun.', dict(hi=['kartof'])),
    ('R', 91.96, 98.50, 'Vaxtilə Xəzərdə neft daşıyan bir tanker sonradan muzeyə çevrildi.', {}),
    ('R', 99.18, 103.40, 'Gəmi Bakının hansı qəsəbəsinin adını daşıyır?', dict(hi=['qəsəbəsinin'])),
    ('R', 103.90, 105.80, 'Suraxanı, qəbul edək?', dict(hi=['Suraxanı,'])),
    ('R', 106.00, 107.90, 'Qəbul edirik, cavab doğrudur.', dict(hi=['doğrudur.'])),
    ('R', 108.20, 109.90, 'Cavab doğrudur. Sizi təbrik edirik.', dict(hi=['təbrik'])),
    ('R', 111.24, 115.70, 'Lyublyanadan gəlib çıxarsınız Sabirabada, oradan da gəlib çıxarsınız Suraxanıya.', dict(hi=['Lyublyanadan', 'Sabirabada,', 'Suraxanıya.'])),
]

LAUGHS = []
def COUNTER_START(s2o): return 1e9
def FLASHES(s2o): return []
def SHAKES(s2o): return []
def _o(s2o, t, c=None): return s2o(t, ci(c) if c else None)

def GAGS(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    G = []
    def em(code, t0, t1, x, y, size=170, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='emoji', code=code, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    def lab(text, t0, t1, x, y, size=44, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='label', text=text, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    lab('ŞƏFƏQ XANIM · SABİRABAD', o(0.05, 'city'), o(4.00, 'city'), 540, 1755, 50, emoji='1f4de')
    em('1f3d9', o(13.10, 'addr'), o(15.50, 'addr'), 120, 330, 140)
    em('1f404', o(16.40, 'cow'), o(21.00, 'cow'), 880, 420, 190)
    em('1f923', o(23.40, 'cow'), o(26.40, 'cow'), 170, 1200, 170)
    em('1f404', o(26.60, 'cow'), o(29.00, 'cow'), 880, 420, 170)
    em('1f914', o(33.00, 'q'), o(38.40, 'q'), 880, 420, 170)
    em('1f5fa', o(33.50, 'q'), o(38.40, 'q'), 170, 1200, 160)
    em('1f605', o(38.60, 'prob'), o(44.50, 'prob'), 120, 330, 130)
    em('1f923', o(47.20, 'try'), o(55.60, 'try'), 880, 420, 190)
    em('1f602', o(54.00, 'try'), o(55.60, 'try'), 170, 1200, 170)
    em('1f480', o(60.50, 'lol'), o(72.75, 'lol'), 880, 420, 190)
    em('1f923', o(61.50, 'lol'), o(72.75, 'lol'), 170, 1200, 180)
    em('2753', o(75.40, 'try2'), o(77.55, 'try2'), 880, 420, 160)
    em('1f1f8-1f1ee', o(77.80, 'belə'), o(81.45, 'belə'), 880, 420, 170)
    em('1f1f8-1f1ee', o(81.60, 'slo'), o(83.25, 'slo'), 880, 420, 170)
    em('1f954', o(89.10, 'quiz0'), o(91.35, 'quiz0'), 880, 420, 190)
    em('1f6a2', o(93.00, 'quiz'), o(103.85, 'quiz'), 900, 330, 150)
    em('2753', o(99.50, 'quiz'), o(103.85, 'quiz'), 160, 330, 140)
    em('2705', o(106.80, 'ok'), o(108.15, 'ok'), 880, 420, 170)
    em('1f389', o(108.40, 'win'), o(109.25, 'win'), 170, 1200, 160)
    em('1f5fa', o(111.30, 'route'), o(113.00, 'route'), 880, 420, 170)
    lab('LYUBLYANA → SABİRABAD → SURAXANI', o(111.40, 'route'), o(113.00, 'route'), 540, 1755, 40, accent=OBA_Y, emoji='2708')
    lab('LYUBLYANA → SABİRABAD → SURAXANI', o(113.00, 'route2'), o(115.90, 'route2'), 540, 1755, 40, accent=OBA_Y, emoji='2708')
    em('1f923', o(113.40, 'route2'), o(115.90, 'route2'), 880, 420, 170)
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

MUSIC_LEVEL = 0.12
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (o(16.20, 'cow'), o(17.70, 'cow'), 0.0),             # beat of silence on "inək olur"
        (o(32.50, 'q'), o(55.60, 'try'), 0.07),               # let her attempts + laughter breathe
        (o(55.60, 'lol'), o(72.75, 'lol'), 0.16),
        (o(77.60, 'belə'), o(79.00, 'belə'), 0.0),
        (o(103.90, 'sura'), o(105.95, 'sura'), 0.04),
        (o(106.00, 'ok'), o(109.25, 'win'), 0.20),
        (o(111.20, 'route'), o(113.00, 'route'), 0.0),       # silence for the final callback
        (o(113.00, 'route2'), o(115.90, 'route2'), 0.18),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(0.05, 'city'), 0.10), ('pop', o(13.10, 'addr'), 0.06), ('pop', o(16.40, 'cow'), 0.08),
        ('pop', o(33.00, 'q'), 0.06), ('sparkle', o(77.80, 'belə'), 0.08), ('pop', o(89.10, 'quiz0'), 0.08),
        ('ding', o(106.80, 'ok'), 0.12), ('sparkle', o(108.40, 'win'), 0.09), ('whoosh', o(111.30, 'route'), 0.08),
    ]
