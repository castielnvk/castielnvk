# OBA compilation v3: Bəhruz bəy call + Şəfəq xanım call (full context, strict captions).
# Times are on the combined source w5/combo.mov (see w5/map.json).
# Caption rule: only clearly heard words, exactly as spoken; unclear speech gets NO caption.
from engine import YEL, MAG, CYA, INK, WHITE, PURP
HEADER = ''
OBA_Y = (255, 205, 0)
def caller_name(st): return 'BƏHRUZ BƏY' if st < 72.3 else 'ŞƏFƏQ XANIM'
_C = [
    # --- Bəhruz bəy ---
    ('greet',  dict(a=0.00,  b=3.50,  lay='call', hide='L')),
    ('topic',  dict(a=3.50,  b=10.60, lay='stack')),
    ('heart',  dict(a=10.70, b=13.30, lay='call', hide='L')),
    ('pct',    dict(a=14.50, b=23.05, lay='call', hide='L')),
    ('nb1',    dict(a=29.15, b=43.90, lay='call')),
    ('nb2',    dict(a=47.80, b=53.45, lay='stack')),
    ('oba',    dict(a=53.45, b=57.90, lay='punchR', trans='cut')),
    ('obalaf', dict(a=57.90, b=62.40, lay='stack', trans='cut')),
    ('age',    dict(a=62.60, b=65.45, lay='call', trans='cut')),
    ('grip',   dict(a=65.45, b=72.20, lay='stack')),
    # --- Şəfəq xanım ---
    ('s_intro',dict(a=72.30, b=81.30, lay='stack', trans='cut')),
    ('s_date', dict(a=81.30, b=85.42, lay='stack')),
    ('s_insta',dict(a=89.10, b=94.70, lay='stack', trans='cut')),
    ('s_abune',dict(a=104.60, b=108.90, lay='stack', trans='cut')),
    ('s_sub',  dict(a=109.45, b=113.90, lay='call', trans='cut')),
    ('s_app',  dict(a=113.90, b=122.30, lay='stack')),
    ('s_app2', dict(a=126.10, b=134.45, lay='stack', trans='cut')),
    ('s_luck', dict(a=137.60, b=143.10, lay='stack', trans='cut')),
    ('s_umb',  dict(a=143.10, b=154.45, lay='call', hide='L')),
    ('s_trust',dict(a=156.70, b=158.00, lay='punchR', trans='cut', hide='L')),
    ('s_quiz0',dict(a=158.00, b=160.95, lay='stack', trans='cut')),
    ('s_quiz', dict(a=162.95, b=174.95, lay='stack', trans='cut')),
    ('s_ans',  dict(a=175.00, b=177.20, lay='stack', trans='cut')),
    ('s_ans1', dict(a=180.55, b=186.30, lay='stack', trans='cut')),
    ('s_ans2', dict(a=186.30, b=187.55, lay='stack', hide='L')),
    ('s_toy',  dict(a=192.60, b=198.95, lay='stack', trans='cut')),
    ('s_win',  dict(a=199.00, b=205.00, lay='stack', trans='cut')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

SPEAKERS = [
    (0.0, 1.5, 'R'), (1.5, 3.5, 'P'), (3.5, 10.6, 'R'), (10.7, 13.3, 'P'), (14.5, 23.1, 'P'),
    (29.1, 43.95, 'P'), (43.95, 50.5, 'R'), (50.5, 53.45, 'P'), (53.45, 60.3, 'R'),
    (62.6, 64.2, 'R'), (64.2, 65.45, 'P'), (65.45, 72.2, 'R'),
    (72.3, 80.2, 'R'), (80.2, 81.3, 'P'), (81.3, 84.3, 'R'), (84.3, 87.0, 'P'),
    (89.1, 93.5, 'R'), (93.5, 94.7, 'P'), (104.6, 108.9, 'R'), (108.9, 113.9, 'P'),
    (113.9, 115.05, 'R'), (115.05, 118.1, 'P'), (118.1, 122.3, 'R'),
    (126.1, 128.8, 'R'), (128.8, 131.5, 'P'), (131.5, 134.5, 'R'),
    (137.6, 143.1, 'R'), (143.1, 145.4, 'P'), (145.4, 146.25, 'R'), (146.25, 154.5, 'P'), (154.5, 162.0, 'R'),
    (162.9, 177.3, 'R'), (177.3, 180.5, 'P'), (180.5, 205.0, 'R'),
]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.95}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

CAPTIONS = [
    ('R', 0.00, 1.00, 'Bəhruz bəy, salam!', {}),
    ('P', 1.70, 3.34, 'Salam, sabahınız xeyir olsun!', {}),
    ('R', 3.66, 10.46, 'Qardaş, siz qohumlarla bağlı nə deyə bilərsiniz? İndi qohumlarla dost olmaq mümkündürmü, yoxsa yox?', dict(hi=['dost'])),
    ('P', 10.82, 13.12, 'Ürəyim doludur bu məsələ ilə bağlı.', dict(hi=['Ürəyim'])),
    ('P', 14.58, 22.90, 'Bu, hamısına şamil deyil. Sizə deyim ki, 50-60%-inə aiddir, 40%-i mənim canım-ciyərimdir.', dict(hi=['40%-i', 'canım-ciyərimdir.'])),
    ('P', 29.40, 34.80, 'Valla, bizim bir sözümüz var: uzaq qohum yaxşıdır, yoxsa yaxın qonşu?', dict(hi=['yaxın', 'qonşu?'])),
    ('P', 34.90, 37.80, 'Valla, mən Kürdəxanada yaşayıram, bir dənə qonşum var.', dict(hi=['qonşum'])),
    ('P', 37.98, 43.90, 'O 60%-də olan qohumların heç birinə dəyişmirəm o insanı. Elə gözəl insandır, elə can yandırır.', dict(hi=['dəyişmirəm'])),
    ('R', 48.02, 49.80, 'Bizim də yaxın qonşumuz var da.', dict(hi=['qonşumuz'])),
    ('P', 50.56, 52.00, 'Bir dənə qonşum var.', {}),
    ('R', 53.48, 55.70, 'Bizdə də bir dənədir, bizdə OBA-dır.', dict(big=True, hi=['OBA-dır.'])),
    ('R', 55.80, 57.50, 'Yaxın qonşumuz da OBA-dır.', dict(hi=['OBA-dır.'])),
    ('R', 58.20, 59.40, 'O, bizdə də var.', {}),
    ('R', 62.76, 64.00, 'Neçə yaşınız var, Bəhruz qardaş?', {}),
    ('P', 64.22, 65.40, '33 yaşım var.', {}),
    ('R', 65.52, 72.00, 'Bundan sonra bərk-bərk yapışın o Kürdəxanadakı qonşunuzdan, bir də bərk-bərk yapışın OBA-mızdan, tamammı?', dict(hi=['OBA-mızdan,'])),
    # Şəfəq xanım
    ('R', 72.84, 75.20, 'Şəfəq xanım telefon xəttindədir.', {}),
    ('R', 75.68, 79.90, 'Şəfəq xanım, canlı dəvətnamə?', dict(hi=['dəvətnamə?'])),
    ('P', 80.34, 81.20, 'Bəli, bəli.', {}),
    ('R', 81.42, 83.95, 'Aprelin 29-u, düzdürmü? Cümə axşamı?', dict(hi=['29-u,'])),
    ('P', 84.40, 85.35, 'İnşallah, inşallah.', {}),
    ('R', 89.10, 93.30, 'Şəfəq xanım, siz Instagram səhifəsi işlədirsiniz?', dict(hi=['Instagram'])),
    ('P', 93.60, 94.60, 'Bəli, bəli, bəli.', {}),
    ('R', 104.64, 107.70, 'Bizim Araz FM-in Instagram səhifəsinə abunə oldunuzmu?', dict(hi=['abunə'])),
    ('P', 109.56, 113.85, 'Sentyabrın 9-dan mən sizin bütün səhifələrə TikTokdan başqa abunə olmuşam.', dict(hi=['TikTokdan', 'başqa'])),
    ('R', 113.96, 115.05, 'TikTok-a niyə olmamısınız?', dict(hi=['TikTok-a'])),
    ('P', 115.12, 118.05, 'Telefonda yaddaş yoxdur. Yer yoxdur.', dict(hi=['yaddaş'])),
    ('R', 118.16, 120.40, 'Yer yoxdur? Nəyisə silin də, nə var?', {}),
    ('R', 120.86, 122.20, 'Instagramı silsən ki, TikTok...', {}),
    ('R', 126.18, 128.50, 'Alış-veriş tətbiqləri var, onları silin də.', dict(hi=['Alış-veriş'])),
    ('P', 128.88, 131.50, 'OBA-dan başqa heç alış-veriş tətbiqi yoxdur mənim.', dict(big=True, hi=['OBA-dan'])),
    ('R', 132.58, 133.40, 'OBA-ya dəyməyin.', dict(hi=['OBA-ya'])),
    ('R', 133.48, 134.40, 'OBA-ya dəyməyin!', dict(hi=['OBA-ya'])),
    ('R', 137.78, 140.95, 'OBA-dan, OBA-dan qazanmaq şansı var.', dict(hi=['OBA-dan,', 'OBA-dan'])),
    ('R', 141.70, 142.95, 'İndi sual təqdim edirik.', {}),
    ('P', 143.18, 145.05, 'Mən sonradan əlavə bir söz deyim.', {}),
    ('R', 145.48, 146.20, 'Buyurun, buyurun.', {}),
    ('P', 147.70, 149.10, 'Mən OBA-ya girdim çətirimlə.', dict(hi=['OBA-ya'])),
    ('P', 149.22, 151.10, 'Çətirim yadımdan çıxıb, qaldı OBA-da.', dict(hi=['Çətirim'])),
    ('P', 152.64, 154.35, 'Halal olsun OBA-nın işçilərinə.', dict(hi=['OBA-nın', 'işçilərinə.'])),
    ('R', 156.88, 157.95, 'Etibarlı qonşu!', dict(big=True, hi=['qonşu!'])),
    ('R', 158.00, 160.90, 'İndi sual verəcəyik sizə. Sualı təqdim edirik, diqqətli olun.', dict(hi=['sual'])),
    ('R', 163.06, 169.95, 'Vaxtilə Xəzərdə neft daşıyan bir tanker sonradan muzeyə çevrildi.', {}),
    ('R', 170.28, 174.90, 'Gəmi Bakının hansı qəsəbəsinin adını daşıyır?', dict(hi=['qəsəbəsinin'])),
    ('R', 175.00, 177.10, 'Suraxanı, qəbul edək?', dict(hi=['Suraxanı,'])),
    ('R', 180.68, 182.60, 'Qəbul edirik, cavab doğrudur.', dict(hi=['doğrudur.'])),
    ('R', 185.58, 187.45, 'Cavab doğrudur, sizi təbrik edirik.', dict(hi=['təbrik'])),
    ('R', 192.72, 198.90, 'Yox, toydan canınızı qurtardıq. Biz dedik, toya gələndə o 50 manatlığı saxlayıb, biz gələndə alış-veriş eləyib qabağımıza bir şey qoyasınız.', dict(hi=['50', 'manatlığı'])),
    ('R', 199.00, 204.90, 'Sizi təbrik edirik. OBA-dan 50 manatlıq kupon. Halal xoşunuz olsun.', dict(hi=['OBA-dan', '50', 'manatlıq', 'kupon.'])),
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
    oba = lambda t0, t1, x=300, y=1500: lab('OBA', t0, t1, x, y, 64, accent=OBA_Y, emoji='1f6d2')
    # names + topic (topic text is the show's own on-screen title)
    lab('BƏHRUZ BƏY', o(0.05, 'greet'), o(3.45, 'greet'), 540, 790, 54, emoji='1f4de')
    lab('MÖVZU: QOHUMLARLA DOST\nOLMAQ MÜMKÜNDÜR?', o(4.40, 'topic'), o(10.60, 'topic'), 540, 1765, 54, emoji='1f914')
    lab('ŞƏFƏQ XANIM', o(72.35, 's_intro'), o(76.50, 's_intro'), 540, 1745, 54, emoji='1f4de')
    # OBA moments
    em('1f6d2', o(54.00, 'oba'), o(57.90, 'oba'), 880, 420, 190)
    oba(o(54.60, 'oba'), o(57.90, 'oba'), 300, 1080)
    em('1f923', o(58.00, 'obalaf'), o(62.40, 'obalaf'), 170, 430, 180)
    em('1f602', o(58.40, 'obalaf'), o(62.40, 'obalaf'), 170, 1200, 170)
    em('1f6d2', o(70.00, 'grip'), o(72.20, 'grip'), 880, 420, 180)
    oba(o(70.20, 'grip'), o(72.20, 'grip'))
    em('1f4f1', o(115.12, 's_app'), o(118.05, 's_app'), 170, 1200, 150)
    em('1f6d2', o(129.00, 's_app2'), o(134.45, 's_app2'), 880, 420, 190)
    oba(o(129.40, 's_app2'), o(134.45, 's_app2'))
    em('1f6d2', o(137.90, 's_luck'), o(141.00, 's_luck'), 880, 420, 160)
    em('2602', o(147.80, 's_umb'), o(154.45, 's_umb'), 950, 330, 140)
    oba(o(152.80, 's_umb'), o(154.45, 's_umb'), 540, 790)
    em('1f91d', o(156.90, 's_trust'), o(158.00, 's_trust'), 880, 420, 190)
    em('2753', o(170.40, 's_quiz'), o(174.95, 's_quiz'), 880, 420, 150)
    em('2705', o(180.80, 's_ans1'), o(186.30, 's_ans1'), 900, 360, 170)
    em('1f39f', o(200.50, 's_win'), o(205.00, 's_win'), 880, 420, 190)
    lab('OBA-DAN 50 MANATLIQ KUPON', o(201.00, 's_win'), o(205.00, 's_win'), 540, 1750, 50, accent=OBA_Y, emoji='1f39f')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

MUSIC_LEVEL = 0.12
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (o(52.60, 'nb2'), o(53.45, 'nb2'), 0.0),
        (o(53.45, 'oba'), o(57.90, 'oba'), 0.0),            # silence for the OBA punchline
        (o(57.90, 'obalaf'), o(62.40, 'obalaf'), 0.20),
        (o(29.15, 'nb1'), o(43.90, 'nb1'), 0.09),
        (o(143.10, 's_umb'), o(154.45, 's_umb'), 0.09),
        (o(175.00, 's_ans'), o(177.20, 's_ans'), 0.05),
        (o(180.55, 's_ans1'), o(186.30, 's_ans1'), 0.20),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(0.05, 'greet'), 0.12), ('pop', o(4.40, 'topic'), 0.07),
        ('whoosh', o(54.40, 'oba'), 0.10), ('sparkle', o(54.70, 'oba'), 0.09), ('pop', o(70.20, 'grip'), 0.08),
        ('whoosh', o(72.35, 's_intro'), 0.12), ('sparkle', o(129.40, 's_app2'), 0.09), ('pop', o(137.90, 's_luck'), 0.06),
        ('sparkle', o(152.80, 's_umb'), 0.09), ('pop', o(156.90, 's_trust'), 0.06),
        ('ding', o(180.80, 's_ans1'), 0.12), ('sparkle', o(201.00, 's_win'), 0.10),
    ]
