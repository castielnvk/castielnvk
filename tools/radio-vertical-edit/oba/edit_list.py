# OBA compilation: Bəhruz call (1st hour, ep "Qohumlarla dost olmaq") + Şəfəq xanım (3rd hour).
# Times are on the combined source w4/combo.mov (see w4/map.json).
from engine import YEL, MAG, CYA, INK, WHITE, PURP
HEADER = ''
WHT = (255, 255, 255); OBA_Y = (255, 205, 0); OBA_R = (200, 20, 60)
def caller_name(st): return 'BƏHRUZ' if st < 72.3 else 'ŞƏFƏQ XANIM'
_C = [
    # --- Part 1: Bəhruz ---
    ('greet',  dict(a=0.00,  b=3.50,  lay='call')),
    ('topic',  dict(a=3.50,  b=10.60, lay='stack')),
    ('heart',  dict(a=10.70, b=13.30, lay='call')),
    ('pct',    dict(a=14.50, b=23.05, lay='call')),
    ('nb1',    dict(a=29.15, b=43.90, lay='call')),
    ('nb2',    dict(a=43.90, b=53.45, lay='stack')),
    ('oba',    dict(a=53.45, b=57.90, lay='punchR', trans='cut')),
    ('obalaf', dict(a=57.90, b=62.40, lay='stack', trans='cut')),
    ('age',    dict(a=62.60, b=65.45, lay='call', trans='cut')),
    ('grip',   dict(a=65.45, b=72.20, lay='stack')),
    # --- Part 2: Şəfəq xanım ---
    ('s_intro',dict(a=72.30, b=81.15, lay='stack', trans='cut')),
    ('s_app',  dict(a=81.20, b=101.85, lay='stack', trans='cut')),
    ('s_luck', dict(a=101.95, b=110.40, lay='stack', trans='cut')),
    ('s_umb',  dict(a=110.40, b=122.50, lay='call')),
    ('s_trust',dict(a=122.50, b=125.40, lay='punchR', trans='cut')),
    ('s_quiz', dict(a=125.45, b=137.85, lay='stack', trans='cut')),
    ('s_ans',  dict(a=137.95, b=150.45, lay='stack', trans='cut')),
    ('s_toy',  dict(a=150.55, b=157.85, lay='stack', trans='cut')),
    ('s_win',  dict(a=157.95, b=163.85, lay='stack', trans='cut')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

SPEAKERS = [
    (0.0, 1.5, 'R'), (1.5, 3.5, 'P'), (3.5, 10.6, 'R'), (10.7, 13.3, 'P'), (14.5, 23.1, 'P'),
    (29.1, 43.95, 'P'), (43.95, 50.5, 'R'), (50.5, 53.45, 'P'), (53.45, 60.3, 'R'),
    (62.6, 64.2, 'R'), (64.2, 65.45, 'P'), (65.45, 72.2, 'R'),
    (72.3, 80.2, 'R'), (80.2, 81.1, 'P'), (81.2, 82.9, 'R'), (82.9, 85.5, 'P'), (85.5, 89.6, 'R'), (89.6, 93.4, 'P'),
    (93.4, 95.96, 'R'), (95.96, 98.85, 'P'), (98.85, 101.9, 'R'), (101.9, 110.45, 'R'), (110.45, 112.84, 'P'),
    (112.84, 113.6, 'R'), (113.6, 122.4, 'P'), (122.4, 137.9, 'R'), (137.9, 140.4, 'R'), (140.4, 143.4, 'P'),
    (143.4, 163.9, 'R'),
]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.95}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

CAPTIONS = [
    ('R', 0.00, 1.00, 'Bəhruz bəy, salam!', {}),
    ('P', 1.70, 3.34, 'Salam, sabahınız xeyir olsun!', {}),
    ('R', 3.66, 10.46, 'Qardaş, siz qohumlarla bağlı nə deyə bilərsiniz? Qohumlarla dost olmaq mümkündürmü, yoxsa yox?', dict(hi=['dost'])),
    ('P', 10.82, 13.12, 'Ürəyim doludur bu məsələ ilə bağlı.', dict(hi=['Ürəyim'])),
    ('P', 14.58, 22.90, 'Bu, hamısına şamil deyil. Haradasa sizə deyim ki, 50-60%-inə aiddir, 40%-i mənim canım-ciyərimdir.', dict(hi=['40%-i', 'canım-ciyərimdir.'])),
    ('P', 29.40, 34.80, 'Valla, bizim bir sözümüz var: uzaq qohumdan yaxın qonşu yaxşıdır.', dict(hi=['yaxın', 'qonşu'])),
    ('P', 34.90, 37.80, 'Mən Kürdəxanada yaşayıram, bir dənə qonşum var.', dict(hi=['qonşum'])),
    ('P', 37.98, 43.90, 'O 60%-dəki qohumların heç birinə dəyişmirəm o insanı. Elə gözəl insandır, elə can yandırır.', dict(hi=['dəyişmirəm'])),
    ('R', 43.96, 45.20, 'Qonşusu var, bilirəm, Kürdəxanada.', {}),
    ('R', 48.02, 49.80, 'Bizim də yaxın qonşumuz var da.', dict(hi=['qonşumuz'])),
    ('P', 50.56, 53.40, 'Bir dənə qonşum var...', {}),
    ('R', 53.48, 55.70, 'Bizdə də bir dənədir, bizdə OBA-dır.', dict(big=True, hi=['OBA-dır.'])),
    ('R', 55.80, 57.50, 'Yaxın qonşumuz da OBA-dır.', dict(hi=['OBA-dır.'])),
    ('R', 58.20, 60.20, 'O, bizdə də var. O, bizdə də var!', {}),
    ('R', 62.76, 64.00, 'Neçə yaşınız var, Bəhruz qardaş?', {}),
    ('P', 64.22, 65.40, '33 yaşım var.', {}),
    ('R', 65.52, 72.00, 'Bundan sonra bərk-bərk yapışın o Kürdəxanadakı qonşunuzdan, bir də bərk-bərk yapışın OBA-mızdan, tamammı?', dict(hi=['OBA-mızdan,'])),
    ('R', 72.30, 74.86, 'Şəfəq xanım telefon xəttindədir.', {}),
    ('R', 74.88, 79.44, 'Şəfəq xanım, canlı efirdəsiniz?', {}),
    ('P', 80.26, 81.02, 'Bəli, bəli.', {}),
    ('R', 81.32, 82.30, 'TikTok-a niyə abunə olmamısınız?', dict(hi=['TikTok-a'])),
    ('P', 83.06, 85.46, 'Telefonda yaddaş yoxdur. Yer yoxdur.', dict(hi=['yaddaş'])),
    ('R', 85.52, 87.82, 'Nəyisə silin də, nə var?', {}),
    ('R', 87.82, 89.28, 'Yəni, Instagramı silsən ki, TikTok...', {}),
    ('P', 90.16, 93.40, 'Yox, Instagramı silmərəm.', {}),
    ('R', 93.40, 95.96, 'Yox, alış-veriş tətbiqləri var, onları silin.', dict(hi=['alış-veriş'])),
    ('P', 95.96, 98.82, 'OBA-dan başqa heç alış-veriş tətbiqi yoxdur mənim!', dict(big=True, hi=['OBA-dan'])),
    ('R', 98.88, 100.74, 'OBA-ya onda dəyməyin, OBA qalsın.', dict(hi=['OBA', 'qalsın.'])),
    ('R', 100.80, 101.66, 'OBA-ya dəyməyin!', dict(hi=['OBA-ya'])),
    ('R', 102.06, 104.12, 'Allah sizi güldürsün, Şəfəq xanım.', {}),
    ('R', 105.20, 108.22, 'OBA-dan, OBA-dan qazanmaq şansı var.', dict(hi=['OBA-dan,', 'OBA-dan'])),
    ('R', 108.56, 110.16, 'İndi sual təqdim edirik.', {}),
    ('P', 110.52, 112.84, 'Mən sonradan əlavə bir söz deyim sizə.', {}),
    ('R', 112.84, 113.50, 'Buyurun, buyurun.', {}),
    ('P', 113.68, 116.52, '... mən OBA-ya girdim, çətirimlə.', dict(hi=['OBA-ya'])),
    ('P', 116.60, 118.38, 'Çətirim yadımdan çıxıb, qaldı OBA-da.', dict(hi=['Çətirim'])),
    ('P', 118.76, 119.98, 'Bu günlərdə götürmüşəm.', {}),
    ('P', 119.98, 122.34, 'Halal olsun OBA-nın işçilərinə!', dict(hi=['OBA-nın', 'işçilərinə!'])),
    ('R', 124.22, 125.26, 'Etibarlı qonşu!', dict(big=True, hi=['qonşu!'])),
    ('R', 125.54, 133.02, 'Vaxtilə Xəzərdə neft daşıyan bir tanker sonradan muzeyə çevrildi.', {}),
    ('R', 134.04, 137.72, 'Gəmi Bakının hansı qəsəbəsinin adını daşıyır?', dict(hi=['qəsəbəsinin'])),
    ('R', 138.00, 139.86, 'Suraxanı, qəbul eləyək?', dict(hi=['Suraxanı,'])),
    ('R', 143.44, 145.46, 'Qəbul edirik, cavab doğrudur!', dict(hi=['doğrudur!'])),
    ('R', 147.96, 150.30, 'Cavab doğrudur, sizi təbrik edirik!', dict(hi=['təbrik'])),
    ('R', 150.64, 157.72, 'Toydan canınızı qurtardıq. Biz dedik, toya gələndə o 50 manatlığı saxlayın, biz gələndə alış-veriş eləyib qabağımıza bir şey qoyasınız.', dict(hi=['50', 'manatlığı'])),
    ('R', 158.06, 163.76, 'Sizi təbrik edirik. OBA-dan 50 manatlıq kupon. Halal xoşunuz olsun!', dict(hi=['OBA-dan', '50', 'manatlıq', 'kupon.'])),
]

LAUGHS = []
def COUNTER_START(s2o): return 1e9
def FLASHES(s2o): return [s2o(53.45, ci('oba')), s2o(72.30, ci('s_intro'))]
def SHAKES(s2o): return [(s2o(55.0, ci('oba')), 8)]
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
    oba = lambda t0, t1, x=300, y=1080: lab('OBA', t0, t1, x, y, 68, bg=OBA_Y, fg=OBA_R, rot=-5, emoji='1f6d2')
    # part titles
    lab('1-Cİ SAAT · DİNLƏYİCİ BƏHRUZ', o(0.05, 'greet'), o(3.45, 'greet'), 540, 560, 34, bg=WHITE, fg=INK, rot=-2, emoji='1f4de')
    lab('MÖVZU:\nQOHUMLARLA DOST\nOLMAQ MÜMKÜNDÜR?', o(4.40, 'topic'), o(10.60, 'topic'), 540, 560, 38, bg=YEL, fg=INK, rot=-3, emoji='1f914')
    lab('UZAQ QOHUM < YAXIN QONŞU', o(31.50, 'nb1'), o(34.80, 'nb1'), 540, 760, 36, bg=YEL, fg=INK, rot=-3, emoji='1f3e1')
    em('1f6d2', o(54.00, 'oba'), o(57.90, 'oba'), 880, 420, 200, rot=8, wob=6)
    oba(o(54.60, 'oba'), o(57.90, 'oba'))
    em('1f923', o(58.00, 'obalaf'), o(62.40, 'obalaf'), 170, 430, 180, rot=-10, wob=10, wob_f=9)
    em('1f602', o(58.40, 'obalaf'), o(62.40, 'obalaf'), 170, 1200, 170, rot=10, wob=10, wob_f=8)
    em('1f6d2', o(70.00, 'grip'), o(72.20, 'grip'), 880, 420, 180, rot=10, wob=6)
    oba(o(70.20, 'grip'), o(72.20, 'grip'), 300, 1500)
    lab('3-CÜ SAAT · ŞƏFƏQ XANIM', o(72.35, 's_intro'), o(76.50, 's_intro'), 540, 560, 34, bg=WHITE, fg=INK, rot=-2, emoji='1f4de')
    em('1f4f1', o(83.06, 's_app'), o(85.46, 's_app'), 170, 1200, 150, rot=-8)
    em('1f6d2', o(96.20, 's_app'), o(101.85, 's_app'), 880, 420, 190, rot=8, wob=6)
    oba(o(96.60, 's_app'), o(101.85, 's_app'), 300, 1500)
    em('1f6d2', o(105.30, 's_luck'), o(108.30, 's_luck'), 880, 420, 160, rot=8)
    em('2602', o(114.00, 's_umb'), o(122.50, 's_umb'), 960, 330, 140, rot=8, wob=6)
    em('1f64f', o(120.00, 's_umb'), o(122.50, 's_umb'), 120, 330, 130, rot=-8, wob=6)
    oba(o(120.20, 's_umb'), o(122.50, 's_umb'), 540, 760)
    em('1f91d', o(124.20, 's_trust'), o(125.40, 's_trust'), 880, 420, 190, rot=8)
    em('1f6a2', o(126.80, 's_quiz'), o(137.85, 's_quiz'), 170, 1200, 150, rot=-6, wob=4)
    em('2753', o(134.20, 's_quiz'), o(137.85, 's_quiz'), 880, 420, 150, wob=8)
    em('2705', o(143.50, 's_ans'), o(150.45, 's_ans'), 880, 420, 170, rot=8)
    em('1f389', o(148.00, 's_ans'), o(150.45, 's_ans'), 170, 1200, 160, rot=-8, wob=8)
    em('1f39f', o(158.80, 's_win'), o(163.85, 's_win'), 880, 420, 190, rot=8, wob=6)
    lab('OBA-DAN 50 AZN KUPON', o(159.40, 's_win'), o(163.85, 's_win'), 540, 1700, 40, bg=OBA_Y, fg=OBA_R, rot=-3, emoji='1f39f')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

MUSIC_LEVEL = 0.12
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (o(52.60, 'nb2'), o(53.45, 'nb2'), 0.0),
        (o(53.45, 'oba'), o(57.90, 'oba'), 0.0),           # silence for the OBA punchline
        (o(57.90, 'obalaf'), o(62.40, 'obalaf'), 0.20),
        (o(29.15, 'nb1'), o(43.90, 'nb1'), 0.09),
        (o(110.40, 's_umb'), o(122.50, 's_umb'), 0.09),
        (o(137.95, 's_ans'), o(143.40, 's_ans'), 0.05),   # tension before the result
        (o(143.40, 's_ans'), o(150.45, 's_ans'), 0.20),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(0.05, 'greet'), 0.18), ('ding', o(4.40, 'topic'), 0.12), ('ding', o(31.50, 'nb1'), 0.12),
        ('pop', o(54.00, 'oba'), 0.18), ('badumtss', o(55.60, 'oba'), 0.22), ('pop2', o(58.40, 'obalaf'), 0.12),
        ('pop', o(70.20, 'grip'), 0.16),
        ('whoosh', o(72.35, 's_intro'), 0.18), ('pop', o(83.06, 's_app'), 0.12), ('pop', o(96.20, 's_app'), 0.18),
        ('boing', o(98.90, 's_app'), 0.14), ('pop2', o(105.30, 's_luck'), 0.12), ('pop', o(114.00, 's_umb'), 0.12),
        ('sparkle', o(120.00, 's_umb'), 0.12), ('pop2', o(124.20, 's_trust'), 0.14),
        ('tick', o(134.20, 's_quiz'), 0.16), ('riser', o(141.80, 's_ans'), 0.14), ('ding', o(143.50, 's_ans'), 0.18),
        ('sparkle', o(148.00, 's_ans'), 0.14), ('sparkle', o(158.80, 's_win'), 0.14), ('pop', o(159.40, 's_win'), 0.14),
    ]
