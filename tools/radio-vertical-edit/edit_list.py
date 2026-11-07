# Edit decision list, captions, gags, sound design (source times in seconds)
from engine import YEL, MAG, CYA, INK, WHITE, PURP

HEADER = 'ƏMƏLİYYAT QABAĞI ZƏNG'

G = '/tmp/claude-0/-workspace-castielnvk/84104dec-feb8-5707-9b55-a4257893035a/scratchpad/gen/'
WHT = (255, 255, 255)
FREEZE_FX = [dict(kind='label', text='DİAQNOZ:\nBABASİL', t0=0.08, t1=1.30, xy=(540, 1150), size=54, bg=WHT, fg=(200, 20, 60), rot=-5, emoji='1fa7a'),
             dict(kind='emoji', code='1f6a8', t0=0.3, t1=1.30, xy=(880, 420), size=170, rot=8, wob=10, wob_f=12)]
def INS(img, cap, extra=()):
    return [dict(kind='image', path=G+img, t0=0.0, t1=2.35, xy=(540, 860), size=840, cap=cap, rot=-3)] + list(extra)
INS_SFX = [('whoosh', 0.0, 0.25), ('pop', 0.12, 0.22), ('sparkle', 0.35, 0.16)]
_C = [
    ('hook',   dict(a=33.95, b=36.30, lay='stack')),
    ('greet',  dict(a=0.05,  b=3.62,  lay='call', trans='cut')),
    ('yawn',   dict(a=3.62,  b=4.96,  lay='stack')),
    ('flu',    dict(a=4.96,  b=7.42,  lay='stack')),
    ('call1',  dict(a=7.42,  b=10.42, lay='call')),
    ('what',   dict(a=13.12, b=17.40, lay='soloR', trans='cut')),
    ('diag',   dict(a=17.40, b=18.48, lay='call')),
    ('freeze', dict(hold=1.30, at=18.50, lay='punchR', hold_zoom=True, trans='cut', fx=FREEZE_FX,
                    sfx=[('shutter', 0, 0.3), ('scratch', 0, 0.2), ('bonk', 0.35, 0.25)])),
    ('allah',  dict(a=18.48, b=23.74, lay='stack')),
    ('hook2',  dict(a=33.95, b=38.25, lay='stack', trans='cut')),
    ('strain', dict(a=38.25, b=43.50, lay='soloR')),
    ('after',  dict(a=43.85, b=47.00, lay='stack')),
    ('days',   dict(a=48.36, b=52.80, lay='stack', trans='cut')),
    ('slow',   dict(a=52.80, b=54.26, lay='punchL', trans='cut')),
    ('guest',  dict(a=77.05, b=84.22, lay='call', trans='cut')),
    ('sit1',   dict(a=84.22, b=88.85, lay='soloR')),
    ('sit2',   dict(a=88.85, b=91.98, lay='stack')),
    ('lor',    dict(a=110.25, b=120.62, lay='punchR', trans='cut')),
    ('bye',    dict(a=122.02, b=126.97, lay='stack', trans='cut')),
    ('ask',    dict(a=129.18, b=131.62, lay='stack', trans='cut')),
    ('punch',  dict(a=131.62, b=133.70, lay='punchR', trans='cut')),
    ('laughL', dict(a=133.70, b=134.70, lay='punchL', trans='cut')),
    ('laugh',  dict(a=134.70, b=136.15, lay='stack', trans='cut')),
    ('cell',   dict(a=136.15, b=139.35, lay='call', trans='cut')),
    ('end',    dict(a=140.48, b=141.80, lay='stack', trans='cut')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}

# who is talking (source time) -> active frame highlight + balancing gain
SPEAKERS = [
    (0.0, 3.62, 'P'), (3.62, 4.96, 'L'), (4.96, 6.10, 'R'), (6.10, 6.76, 'L'), (6.76, 7.42, 'R'), (7.42, 10.45, 'P'),
    (13.10, 17.40, 'R'), (17.40, 18.48, 'P'), (18.48, 23.74, 'R'),
    (33.95, 43.55, 'R'), (43.85, 52.80, 'R'), (52.80, 54.30, 'L'),
    (77.0, 84.24, 'P'), (84.24, 92.0, 'R'), (110.2, 120.7, 'R'), (122.0, 127.0, 'R'),
    (129.1, 131.48, 'R'), (131.48, 131.70, 'P'), (131.70, 133.70, 'R'), (136.1, 139.4, 'P'),
    (140.4, 141.8, 'R'),
]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.95}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

def ci(name): return IDX[name]

# (speaker, src_start, src_end, text, opts)
CAPTIONS = [
    ('R', 34.02, 34.95, 'Qardaş, çox gülmə,', dict(clip=ci('hook'), hi=['gülmə,'])),
    ('R', 35.10, 36.20, 'əməliyyat qabağıdır!', dict(clip=ci('hook'), hi=['əməliyyat'])),
    ('P', 0.05, 1.10, 'Efiriniz uğurlu olsun!', dict(hi=['uğurlu'])),
    ('P', 1.14, 3.55, '... bəy də salamlayıram.', {}),
    ('L', 3.68, 4.94, 'Siz əsnə-əsnə danışırsınız bizimlə?', dict(hi=['əsnə-əsnə'])),
    ('R', 4.96, 6.08, 'Elə bil ki, yox, qrip olub.', dict(hi=['qrip'])),
    ('L', 6.14, 6.74, 'Qrip olub?', {}),
    ('R', 6.80, 7.40, 'Qrip olub.', {}),
    ('P', 7.44, 9.50, 'Qrip olmuram, əməliyyata gedirəm, ona görə.', dict(hi=['əməliyyata'])),
    ('P', 9.64, 10.40, 'Əməliyyat qabağıdır.', {}),
    ('R', 13.18, 14.62, 'Nədən əməliyyat olunursunuz?', dict(hi=['Nədən'])),
    ('R', 15.00, 17.40, 'Siz keçən il də əməliyyata gedirdiniz, xəstələnmişdiniz.', dict(hi=['keçən', 'il'])),
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
    ('P', 77.06, 80.95, 'İmkan olsa, əgər Xəzər Mediada keçirilsə Komedixana,', dict(hi=['Komedixana,'])),
    ('P', 81.00, 84.20, 'sizin xüsusi qonağınız olaraq gələ bilərəmmi? Yoxsa yox?', dict(hi=['xüsusi', 'qonağınız'])),
    ('R', 84.26, 85.90, 'Hə, sən bir dənə əməliyyatı sağ-salamat keçir.', dict(hi=['sağ-salamat'])),
    ('R', 85.92, 88.80, 'Sən bir dənə əməliyyata gir, görək vəziyyət nədir.', {}),
    ('R', 88.92, 91.95, 'Sən hələ orda 2 saat yarım, 3 saat əyləşmək lazımdır!', dict(hi=['əyləşmək', '3', 'saat'])),
    ('R', 110.42, 112.60, 'Babasildən qabaq, məncə sən LOR-a get, qardaş.', dict(hi=['LOR-a'])),
    ('R', 113.40, 115.50, 'Sən əvvəl nəfəs almağı düzəlt,', dict(hi=['nəfəs'])),
    ('R', 116.00, 120.50, 'sonra digər məsələlərlə bağlı həkimə gedərsən, Nihat.', dict(hi=['digər'])),
    ('R', 122.10, 124.90, 'Siz əməliyyata sağ-salamat gedin, ondan sonra qulluğunuzdayıq, valla.', dict(hi=['qulluğunuzdayıq,'])),
    ('R', 125.30, 126.95, 'Komedixana istəyirsən, nə istəyirsən...', dict(hi=['Komedixana'])),
    ('R', 129.28, 131.00, 'Nihat, bir dənə də sual verim, sonra get.', dict(hi=['sual'])),
    ('P', 131.48, 131.64, 'Buyur.', {}),
    ('R', 131.70, 133.66, 'Niyə babasil var, nənəsil yox?', dict(clip=ci('punch'), big=True, hi=['babasil', 'nənəsil'])),
    ('P', 136.54, 139.25, 'Azercell var, Bakcell var, nə bilim... o da yoxdur da.', dict(hi=['Azercell', 'Bakcell'])),
    ('R', 140.56, 141.72, 'Sağ olun, Nihat, sağ olun.', {}),
]

# laughs counted by the recurring "GÜLMƏK QADAĞAN" badge: (src time, clip index or None)
LAUGHS = [(35.6, ci('hook')), (19.6, None), (21.2, None), (36.3, ci('hook2')), (40.4, None),
          (50.0, None), (89.6, None), (133.85, ci('laughL')), (135.0, None), (137.0, ci('cell'))]
def COUNTER_START(s2o): return s2o(34.85, ci('hook'))

def FLASHES(s2o):
    return [s2o(0.05, ci('greet')), s2o(131.62, ci('punch')), s2o(133.70, ci('laughL'))]

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
    # hook
    em('1f6ab', o(34.60, 'hook'), o(36.25, 'hook'), 900, 830, 170, rot=-8)
    em('1f602', o(34.65, 'hook'), o(36.25, 'hook'), 900, 830, 120, rot=-8)
    # Nihat greets (call layout: stickers over presenter tiles)
    lab('ƏVVƏLƏ QAYIDAQ', o(0.05, 'greet'), o(1.10, 'greet'), 540, 560, 40, bg=WHITE, fg=INK, rot=-3, emoji='23ea')
    em('1f44b', o(0.30), o(3.55), 960, 330, 130, rot=10, wob=14, wob_f=9)
    # yawning
    em('1f971', o(3.80), o(4.94), 900, 1180, 200, rot=8, wob=8)
    em('1f927', o(5.50), o(7.40), 170, 1180, 180, rot=8)
    em('1f914', o(6.14), o(7.40), 170, 360, 150, rot=-10)
    em('1f3e5', o(7.98), o(10.40), 960, 330, 140, rot=6)
    em('1f489', o(9.64), o(10.40), 120, 330, 130, rot=-20)
    em('2753', o(13.40), o(14.62), 860, 380, 170, rot=10, wob=8)
    lab('KEÇƏN İL DƏ...', o(15.30), o(17.40), 300, 1060, 40, bg=WHITE, fg=INK, rot=-4, emoji='1f3e5')
    em('1f633', o(17.80, 'diag'), o(18.48, 'diag'), 960, 330, 150)
    em('1f64f', o(18.62), o(19.70), 170, 1200, 170, rot=6)
    em('1f923', o(19.50), o(22.80), 170, 430, 190, rot=-12, wob=10, wob_f=9)
    em('1f602', o(20.40), o(22.80), 170, 1200, 170, rot=10, wob=10, wob_f=8)
    em('1f62d', o(21.40), o(22.80), 880, 400, 140, rot=10, wob=8, wob_f=10)
    lab('HƏKİM QADAĞASI', o(36.80, 'hook2'), o(38.20, 'hook2'), 290, 1130, 34, bg=WHITE, fg=(200, 20, 60), rot=-5, emoji='1fa7a')
    em('1f910', o(39.88), o(40.60), 880, 420, 170, rot=8)
    lab('GÜCƏ SALMA!', o(42.80), o(43.50), 560, 1120, 52, bg=YEL, fg=INK, rot=-4, emoji='26a0')
    em('1f4a5', o(42.80), o(43.50), 880, 420, 170, rot=10)
    em('1f6ab', o(45.70), o(47.00), 170, 1280, 150, rot=6)
    lab('3–5 GÜN', o(49.86), o(50.90), 300, 1180, 58, bg=MAG, fg=WHITE, rot=6, emoji='23f0')
    em('1f642', o(51.70), o(52.80), 170, 1200, 170, rot=-6)
    lab('TƏHLÜKƏSİZ GÜLÜŞ REJİMİ', o(53.10), o(54.26), 540, 1080, 36, bg=CYA, fg=INK, rot=-3, emoji='1f92d')
    # Nihat's request
    em('1f3ac', o(79.40), o(84.20), 960, 330, 140, rot=8, wob=6)
    em('1f39f', o(81.70), o(84.20), 120, 330, 140, rot=-10, wob=6)
    em('1f64f', o(82.90), o(84.20), 540, 700, 130, wob=8)
    em('2728', o(85.20), o(85.90), 880, 420, 120)
    lab('2,5–3 SAAT OTURMAQ', o(89.44), o(91.98), 540, 1700, 40, bg=WHITE, fg=INK, rot=-3, emoji='23f0')
    em('1fa91', o(91.20), o(91.98), 170, 1250, 170, rot=-10)
    # ENT
    em('1f443', o(111.70), o(113.30), 870, 420, 190, rot=8, wob=6)
    lab('ƏVVƏLCƏ LOR,\nSONRA BABASİL', o(111.95), o(115.50), 300, 1080, 40, bg=YEL, fg=INK, rot=-5, emoji='1fa7a')
    em('1f927', o(114.28), o(115.50), 880, 420, 170, rot=-8)
    em('1f9d1-200d-2695-fe0f', o(117.0), o(120.6), 880, 420, 180, rot=6)
    # goodbye + guest-list payoff
    em('1f64f', o(122.20), o(124.98), 170, 1200, 170, rot=6)
    lab('QONAQ SİYAHISI: NİHAT', o(125.30), o(126.97), 540, 1180, 40, bg=YEL, fg=INK, rot=-4, emoji='2705')
    # the question
    em('1f3a4', o(130.10, 'ask'), o(131.62, 'ask'), 170, 1200, 150, rot=8)
    lab('SON SUAL', o(130.10, 'ask'), o(131.62, 'ask'), 260, 560, 40, bg=WHITE, fg=INK, rot=-5, emoji='1f914')
    em('1f474', o(132.28, 'punch'), o(133.70, 'punch'), 200, 600, 230, rot=-8, wob=6)
    em('1f475', o(133.04, 'punch'), o(133.70, 'punch'), 880, 600, 230, rot=8, wob=6)
    em('2753', o(133.40, 'punch'), o(133.70, 'punch'), 540, 420, 200, wob=10)
    em('1f923', o(133.72, 'laughL'), o(134.70, 'laughL'), 200, 420, 230, rot=-14, wob=14, wob_f=11)
    em('1f602', o(133.80, 'laughL'), o(134.70, 'laughL'), 880, 460, 210, rot=12, wob=14, wob_f=12)
    em('1f480', o(134.75, 'laugh'), o(136.15, 'laugh'), 170, 1240, 170, rot=10, wob=8)
    em('1f62d', o(134.75, 'laugh'), o(136.15, 'laugh'), 170, 420, 170, rot=-10, wob=8, wob_f=10)
    # Nihat's comeback
    em('1f4f1', o(136.54, 'cell'), o(139.35, 'cell'), 960, 330, 140, rot=10, wob=6)
    em('1f4f6', o(137.30, 'cell'), o(139.35, 'cell'), 120, 330, 130, rot=-8, wob=6)
    lab('NİHAT, SAĞ-SALAMAT QAYIT!', o(140.60, 'end'), o(141.80, 'end'), 540, 1700, 38, bg=YEL, fg=INK, rot=-3, emoji='1f64f')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []   # filled by compose (freeze-frame label needs output time of the hold clip)

MUSIC_LEVEL = 0.15
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (0, o(36.30, 'hook'), 0.0),                       # cold open: dry
        (o(17.40, 'diag'), o(18.48, 'diag'), 0.0),         # stop for the diagnosis
        (o(84.22, 'sit1'), o(84.60, 'sit1'), 0.0),         # beat of silence after Nihat's request
        (o(130.30, 'ask'), o(131.62, 'ask'), 0.06),
        (o(131.62, 'punch'), o(133.70, 'punch'), 0.0),    # silence for the punchline
        (o(133.70, 'laughL'), o(136.15, 'laugh'), 0.22),  # groove kicks back in with the laugh
        (o(136.15, 'cell'), o(139.35, 'cell'), 0.11),     # keep Nihat's phone audio clear
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    S = [
        ('pop', o(34.60, 'hook'), 0.30), ('scratch', o(36.15, 'hook'), 0.20),
        ('whoosh', o(0.05, 'greet'), 0.30), ('ding', o(0.30, 'greet'), 0.14),
        ('boing', o(3.80), 0.20),
        ('pop2', o(5.50), 0.25), ('pop', o(6.14), 0.2),
        ('whoosh_up', o(7.42, 'call1'), 0.22), ('ding', o(7.98), 0.14), ('pop', o(9.64), 0.2),
        ('boing', o(13.40), 0.22), ('tick', o(15.30), 0.25),
        ('riser', (o(17.40, 'diag') or 0)-0.9, 0.15), ('pop2', o(17.80, 'diag'), 0.22),
        ('ding', o(18.62), 0.14), ('honk', o(19.55), 0.10), ('pop', o(20.40), 0.18), ('pop2', o(21.40), 0.18),
        ('whoosh', o(33.92, 'hook2'), 0.22), ('bonk', o(36.80, 'hook2'), 0.2), ('pop', o(39.88), 0.2),
        ('slide_up', o(42.70), 0.16), ('bonk', o(42.85), 0.25),
        ('pop', o(45.70), 0.18), ('tick', o(49.90), 0.3), ('tick', o(50.20), 0.3), ('ding', o(50.36), 0.14),
        ('pop2', o(51.70), 0.18), ('sparkle', o(53.10), 0.18),
        ('whoosh_up', o(77.05, 'guest'), 0.22), ('pop', o(79.40), 0.18), ('pop2', o(81.70), 0.18), ('sparkle', o(82.90), 0.14),
        ('scratch', o(84.20, 'sit1'), 0.16),
        ('sparkle', o(85.20), 0.14), ('tick', o(89.50), 0.26), ('tick', o(90.25), 0.26), ('tick', o(90.95), 0.26),
        ('slide_down', o(91.25), 0.24),
        ('whoosh', o(110.23, 'lor'), 0.22), ('honk', o(111.75), 0.10), ('pop', o(111.95), 0.18), ('pop2', o(114.30), 0.18), ('pop', o(117.0), 0.16),
        ('sparkle', o(122.20), 0.14), ('ding', o(125.30), 0.16),
        ('tick', o(130.12, 'ask'), 0.26), ('riser', o(130.40, 'ask'), 0.18),
        ('scratch', o(131.60, 'punch'), 0.16), ('pop', o(132.28, 'punch'), 0.22), ('pop2', o(133.04, 'punch'), 0.22),
        ('badumtss', o(133.66, 'punch'), 0.28), ('whoosh', o(134.68, 'laugh'), 0.18),
        ('whoosh_up', o(136.15, 'cell'), 0.2), ('pop', o(136.54, 'cell'), 0.16), ('pop2', o(137.30, 'cell'), 0.16),
        ('sparkle', o(140.70, 'end'), 0.18),
    ]
    for t, c in LAUGHS:
        tt = s2o(t, c)
        if tt is not None: S.append(('pop2', tt, 0.10))
    return S
