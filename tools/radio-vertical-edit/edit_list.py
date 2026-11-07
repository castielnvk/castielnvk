# Edit decision list, captions, gags, sound design (source times in seconds)
from engine import YEL, MAG, CYA, INK, WHITE, PURP

HEADER = 'ƏMƏLİYYAT QABAĞI ZƏNG'

_C = [
    ('hook',   dict(a=33.95, b=36.30, lay='stack')),
    ('flu',    dict(a=4.90,  b=7.42,  lay='stack', trans='cut')),
    ('call1',  dict(a=7.42,  b=10.42, lay='call')),
    ('what',   dict(a=13.12, b=14.60, lay='soloR')),
    ('diag',   dict(a=17.40, b=18.48, lay='call')),
    ('freeze', dict(hold=1.25, at=18.50, lay='punchR', hold_zoom=True, trans='cut')),
    ('allah',  dict(a=18.48, b=23.74, lay='stack')),
    ('hook2',  dict(a=33.95, b=38.25, lay='stack', trans='cut')),
    ('strain', dict(a=38.25, b=43.50, lay='soloR')),
    ('after',  dict(a=43.85, b=47.00, lay='stack')),
    ('days',   dict(a=48.36, b=52.80, lay='stack', trans='cut')),
    ('slow',   dict(a=52.80, b=54.26, lay='punchL', trans='cut')),
    ('sit1',   dict(a=84.05, b=88.85, lay='soloR')),
    ('sit2',   dict(a=88.85, b=91.98, lay='stack')),
    ('lor',    dict(a=110.25, b=115.56, lay='punchR', trans='cut')),
    ('bye',    dict(a=122.02, b=124.98, lay='stack')),
    ('ask',    dict(a=129.18, b=131.62, lay='stack', trans='cut')),
    ('punch',  dict(a=131.62, b=133.70, lay='punchR', trans='cut')),
    ('laughL', dict(a=133.70, b=134.70, lay='punchL', trans='cut')),
    ('laugh',  dict(a=134.70, b=136.45, lay='stack', trans='cut')),
    ('replay', dict(a=131.62, b=133.70, lay='stack', trans='cut', gain=0.9)),
    ('cell',   dict(a=136.45, b=139.28, lay='stack', trans='cut')),
    ('end',    dict(a=140.48, b=141.80, lay='stack')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}

# who is talking (source time) -> active frame highlight + balancing gain
SPEAKERS = [
    (4.90, 6.10, 'R'), (6.10, 6.76, 'L'), (6.76, 7.42, 'R'), (7.42, 10.45, 'P'),
    (13.10, 14.62, 'R'), (17.40, 18.48, 'P'), (18.48, 23.74, 'R'),
    (33.95, 43.55, 'R'), (43.85, 52.80, 'R'), (52.80, 54.30, 'L'),
    (84.0, 92.0, 'R'), (110.2, 115.6, 'R'), (122.0, 125.0, 'R'),
    (129.1, 131.48, 'R'), (131.48, 131.70, 'P'), (131.70, 133.70, 'R'),
    (140.4, 141.8, 'R'),
]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.86}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

def ci(name): return IDX[name]

# (speaker, src_start, src_end, text, opts)
CAPTIONS = [
    ('R', 34.02, 34.95, 'Qardaş, çox gülmə,', dict(clip=ci('hook'), hi=['gülmə,'])),
    ('R', 35.10, 36.20, 'əməliyyat qabağıdır!', dict(clip=ci('hook'), hi=['əməliyyat'])),
    ('R', 4.96, 6.08, 'Elə bil ki, yox, qrip olub.', dict(hi=['qrip'])),
    ('L', 6.14, 6.74, 'Qrip olub?', {}),
    ('R', 6.80, 7.40, 'Qrip olub.', {}),
    ('P', 7.44, 9.50, 'Qrip olmuram, əməliyyata gedirəm, ona görə.', dict(hi=['əməliyyata'])),
    ('P', 9.64, 10.40, 'Əməliyyat qabağıdır.', {}),
    ('R', 13.18, 14.58, 'Nədən əməliyyat olunursunuz?', dict(hi=['Nədən'])),
    ('P', 17.48, 18.46, 'Bu, babasildi.', dict(hi=['babasildi.'])),
    ('R', 18.60, 22.90, 'Allah kömək... olsun.', dict(clip=ci('allah'))),
    ('R', 22.96, 23.70, 'Allah kömək olsun.', dict(clip=ci('allah'))),
    ('R', 34.02, 34.95, 'Qardaş, çox gülmə,', dict(clip=ci('hook2'), hi=['gülmə,'])),
    ('R', 35.10, 36.20, 'əməliyyat qabağıdır!', dict(clip=ci('hook2'))),
    ('R', 36.72, 38.20, 'Həkim deyib axı, gülmə.', dict(hi=['Həkim'])),
    ('R', 38.32, 40.54, 'Elə bir əməliyyatın olacaq ki, çox gülmə.', {}),
    ('R', 40.64, 43.45, 'Yəni, sən hal-hazırda özünü çox gücə salma.', dict(hi=['gücə'])),
    ('R', 43.92, 45.70, 'Yox, təkcə əməliyyat öncəsi yox,', {}),
    ('R', 45.76, 46.94, 'əməliyyatdan sonra da həmçinin.', dict(hi=['sonra'])),
    ('R', 48.42, 49.80, 'Əməliyyatdan sonra ümumiyyətlə gülmə.', dict(hi=['ümumiyyətlə'])),
    ('R', 49.86, 50.86, '3-5 gün gülmə.', dict(hi=['3-5', 'gün'])),
    ('R', 50.94, 52.76, 'Yox, gülə bilər, gülümsəyə bilərsiniz.', dict(hi=['gülümsəyə'])),
    ('L', 53.50, 54.24, 'Yavaş, yavaş...', dict(big=True)),
    ('R', 84.26, 85.90, 'Sən bir dənə əməliyyatı sağ-salamat keçir.', dict(hi=['sağ-salamat'])),
    ('R', 85.92, 88.80, 'Sən bir dənə əməliyyata gir, görək vəziyyət nədir.', {}),
    ('R', 88.92, 91.95, 'Sən hələ orda 2 saat yarım, 3 saat əyləşmək lazımdır!', dict(hi=['əyləşmək', '3', 'saat'])),
    ('R', 110.42, 112.60, 'Babasildən qabaq, məncə sən LOR-a get, qardaş.', dict(hi=['LOR-a'])),
    ('R', 113.40, 115.50, 'Sən əvvəl nəfəs almağı düzəlt.', dict(hi=['nəfəs'])),
    ('R', 122.10, 124.90, 'Siz əməliyyata sağ-salamat gedin, ondan sonra qulluğunuzdayıq, valla.', {}),
    ('R', 129.28, 131.00, 'Nihat, bir dənə də sual verim, sonra get.', dict(hi=['sual'])),
    ('P', 131.48, 131.64, 'Buyur.', {}),
    ('R', 131.70, 133.66, 'Niyə babasil var, nənəsil yox?', dict(clip=ci('punch'), big=True, hi=['babasil', 'nənəsil'])),
    ('R', 131.70, 133.66, 'Niyə babasil var, nənəsil yox?', dict(clip=ci('replay'), big=True, hi=['babasil', 'nənəsil'])),
    ('X', 136.54, 139.20, 'Azercell, Bakcell var, nə bilim, o da yoxdur da.', dict(hi=['Azercell,', 'Bakcell'])),
    ('R', 140.56, 141.72, 'Sağ olun, Nihat, sağ olun.', {}),
]

# laughs counted by the recurring "GÜLMƏK QADAĞAN" badge: (src time, clip index or None)
LAUGHS = [(35.6, ci('hook')), (19.6, None), (21.2, None), (36.3, ci('hook2')), (40.4, None),
          (50.0, None), (89.6, None), (133.85, ci('laughL')), (135.0, None), (138.0, None)]
def COUNTER_START(s2o): return s2o(34.85, ci('hook'))

def FLASHES(s2o):
    return [s2o(4.90, ci('flu')), s2o(18.50, None) if False else None,
            s2o(131.62, ci('punch')), s2o(133.70, ci('laughL')), s2o(131.62, ci('replay'))]

def SHAKES(s2o):
    return [(s2o(17.80, ci('diag')), 0), (s2o(133.72, ci('laughL')), 16), (s2o(134.0, ci('laughL')), 10),
            (s2o(91.30, ci('sit2')), 8)]

def _o(s2o, t, c=None): return s2o(t, ci(c) if c else None)

def GAGS(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    G = []
    def em(code, t0, t1, x, y, size=220, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='emoji', code=code, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    def lab(text, t0, t1, x, y, size=46, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='label', text=text, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    # --- hook ---
    em('1f6ab', o(34.60, 'hook'), o(36.25, 'hook'), 900, 820, 170, rot=-8)
    em('1f602', o(34.65, 'hook'), o(36.25, 'hook'), 900, 820, 120, rot=-8)
    lab('📞', 0, 0, 0, 0)  # placeholder removed below
    G.pop()
    # rewind sticker at cut to the start
    lab('ƏVVƏLƏ QAYIDAQ', o(4.90, 'flu'), o(5.95, 'flu'), 540, 610, 44, bg=WHITE, fg=INK, rot=-3, emoji='23ea')
    # flu
    em('1f927', o(5.50), o(7.40), 900, 1180, 180, rot=8)
    em('1f914', o(6.14), o(7.40), 170, 360, 150, rot=-10)
    # caller: surgery
    em('1f3e5', o(7.98), o(10.40), 930, 360, 170, rot=6)
    em('1f489', o(9.64), o(10.40), 150, 1200, 150, rot=-20)
    # what for?
    em('2753', o(13.40), o(14.58), 860, 330, 170, rot=10, wob=8)
    em('1f9d0', o(13.70), o(14.58), 190, 1240, 170, rot=-6)
    # diagnosis + freeze
    em('1f633', o(18.05, 'diag'), o(18.48, 'diag'), 900, 1180, 170)
    fz0 = s2o(18.50, None)
    # (freeze clip has no source mapping; computed in GAG_EXTRA)
    # allah komek olsun + laughter
    em('1f64f', o(18.62), o(19.70), 880, 1200, 170, rot=6)
    em('1f923', o(19.50), o(22.80), 170, 430, 190, rot=-12, wob=10, wob_f=9)
    em('1f602', o(20.40), o(22.80), 900, 1200, 170, rot=10, wob=10, wob_f=8)
    em('1f62d', o(21.40), o(22.80), 880, 400, 140, rot=10, wob=8, wob_f=10)
    # don't laugh section
    lab('HƏKİM QADAĞASI', o(36.80, 'hook2'), o(38.20, 'hook2'), 270, 1110, 34, bg=WHITE, fg=(200, 20, 60), rot=-5, emoji='1fa7a')
    em('1f910', o(39.88), o(40.60), 880, 1260, 170, rot=8)
    lab('GÜCƏ SALMA!', o(42.80), o(43.50), 560, 1150, 52, bg=YEL, fg=INK, rot=-4, emoji='26a0')
    em('1f4a5', o(42.80), o(43.50), 880, 360, 170, rot=10)
    em('1f6ab', o(45.70), o(47.00), 880, 1280, 150, rot=6)
    lab('3–5 GÜN', o(49.86), o(50.90), 820, 1180, 58, bg=MAG, fg=WHITE, rot=6, emoji='23f0')
    em('1f642', o(51.70), o(52.80), 880, 1200, 170, rot=-6)
    lab('TƏHLÜKƏSİZ GÜLÜŞ REJİMİ', o(53.10), o(54.26), 540, 1080, 36, bg=CYA, fg=INK, rot=-3, emoji='1f92d')
    # sitting gag (recurring doughnut cushion)
    em('2728', o(85.20), o(85.90), 880, 300, 120)
    lab('2,5–3 SAAT OTURMAQ', o(89.44), o(91.98), 540, 1600, 40, bg=WHITE, fg=INK, rot=-3, emoji='23f0')
    em('1fa91', o(91.20), o(91.98), 170, 1250, 170, rot=-10)
    em('1f369', o(91.30), o(91.98), 880, 1250, 200, rot=12, fly=(0, -60), fly_t=0.5)
    # ENT first
    em('1f443', o(111.70), o(113.30), 870, 360, 190, rot=8, wob=6)
    lab('ƏVVƏLCƏ LOR,\nSONRA BABASİL', o(111.95), o(115.56), 300, 1120, 40, bg=YEL, fg=INK, rot=-5, emoji='1fa7a')
    em('1f927', o(114.28), o(115.56), 880, 400, 170, rot=-8)
    # goodbye wishes
    em('1f64f', o(122.20), o(124.98), 900, 1180, 170, rot=6)
    em('1f64f', o(122.40), o(124.98), 170, 400, 140, rot=-8)
    # the question
    em('1f3a4', o(130.10, 'ask'), o(131.62, 'ask'), 900, 1200, 150, rot=8)
    lab('SON SUAL', o(130.10, 'ask'), o(131.62, 'ask'), 260, 1130, 40, bg=WHITE, fg=INK, rot=-5, emoji='1f914')
    em('1f474', o(132.28, 'punch'), o(133.70, 'punch'), 200, 560, 230, rot=-8, wob=6)
    em('1f475', o(133.04, 'punch'), o(133.70, 'punch'), 880, 560, 230, rot=8, wob=6)
    em('2753', o(133.40, 'punch'), o(133.70, 'punch'), 540, 360, 200, wob=10)
    # laugh explosion
    em('1f923', o(133.72, 'laughL'), o(134.70, 'laughL'), 200, 380, 230, rot=-14, wob=14, wob_f=11)
    em('1f602', o(133.80, 'laughL'), o(134.70, 'laughL'), 880, 420, 210, rot=12, wob=14, wob_f=12)
    em('1f480', o(134.75, 'laugh'), o(136.45, 'laugh'), 880, 1240, 170, rot=10, wob=8)
    em('1f62d', o(134.75, 'laugh'), o(136.45, 'laugh'), 170, 400, 170, rot=-10, wob=8, wob_f=10)
    lab('🔁', 0, 0, 0, 0); G.pop()
    lab('BİR DAHA EŞİDƏK', o(131.62, 'replay'), o(133.70, 'replay'), 540, 1530, 40, bg=WHITE, fg=INK, rot=-3, emoji='1f501')
    # cell punchline annotation
    em('1f4f1', o(136.54, 'cell'), o(139.28, 'cell'), 880, 1220, 170, rot=10, wob=6)
    lab('NƏNƏSİL:\nŞƏBƏKƏ TAPILMADI', o(137.60, 'cell'), o(139.28, 'cell'), 330, 1150, 36, bg=MAG, fg=WHITE, rot=-5, emoji='1f4f6')
    # ending
    lab('NİHAT, SAĞ-SALAMAT QAYIT!', o(140.70, 'end'), o(141.80, 'end'), 540, 1530, 38, bg=YEL, fg=INK, rot=-3, emoji='1f64f')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []   # filled by compose (freeze-frame label needs output time of the hold clip)

MUSIC_LEVEL = 0.20
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (0, o(36.30, 'hook'), 0.0),                 # cold open: dry
        (o(17.40, 'diag'), o(18.48, 'diag'), 0.07),  # tension before diagnosis
        (o(18.48, 'allah'), o(18.48, 'allah')+1.25, 0.0),  # (freeze handled separately)
        (o(130.30, 'ask'), o(131.62, 'ask'), 0.08),
        (o(131.62, 'punch'), o(133.70, 'punch'), 0.0),    # silence for the punchline
        (o(133.70, 'laughL'), o(136.45, 'laugh'), 0.30),  # music slams back with the laugh
        (o(131.62, 'replay'), o(133.70, 'replay'), 0.05),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    S = [
        ('pop', o(34.60, 'hook'), 0.35),
        ('scratch', o(36.15, 'hook'), 0.45),
        ('whoosh', o(4.88, 'flu'), 0.35),
        ('pop2', o(5.50), 0.30), ('pop', o(6.14), 0.22),
        ('whoosh_up', o(7.40, 'call1'), 0.25), ('ding', o(7.98), 0.18), ('pop', o(9.64), 0.22),
        ('boing', o(13.40), 0.25),
        ('riser', o(17.40, 'diag')-0.9 if o(17.40, 'diag') else None, 0.18),
        ('pop2', o(18.05, 'diag'), 0.25),
        ('ding', o(18.62), 0.16), ('honk', o(19.55), 0.20), ('pop', o(20.40), 0.2), ('pop2', o(21.40), 0.2),
        ('whoosh', o(33.92, 'hook2'), 0.25),
        ('bonk', o(36.80, 'hook2'), 0.22), ('pop', o(39.88), 0.22),
        ('slide_up', o(42.70), 0.20), ('bonk', o(42.85), 0.30),
        ('pop', o(45.70), 0.2), ('tick', o(49.90), 0.35), ('tick', o(50.20), 0.35), ('ding', o(50.36), 0.18),
        ('pop2', o(51.70), 0.2), ('sparkle', o(53.10), 0.22),
        ('sparkle', o(85.20), 0.18), ('tick', o(89.50), 0.3), ('tick', o(90.25), 0.3), ('tick', o(90.95), 0.3),
        ('slide_down', o(91.25), 0.30), ('boing', o(91.35), 0.22),
        ('whoosh', o(110.23, 'lor'), 0.25), ('honk', o(111.75), 0.22), ('pop', o(111.95), 0.2), ('pop2', o(114.30), 0.2),
        ('sparkle', o(122.20), 0.18),
        ('tick', o(130.12, 'ask'), 0.3), ('riser', o(130.40, 'ask'), 0.22),
        ('scratch', o(131.60, 'punch'), 0.30),
        ('pop', o(132.28, 'punch'), 0.25), ('pop2', o(133.04, 'punch'), 0.25),
        ('badumtss', o(133.66, 'punch'), 0.45),
        ('whoosh', o(134.68, 'laugh'), 0.2),
        ('scratch', o(131.58, 'replay'), 0.30),
        ('pop', o(136.54, 'cell'), 0.2), ('sadtrombone', o(137.62, 'cell'), 0.16),
        ('sparkle', o(140.70, 'end'), 0.2),
    ]
    # laugh counter dings
    for t, c in LAUGHS:
        tt = s2o(t, c)
        if tt is not None: S.append(('pop2', tt, 0.12))
    return S
