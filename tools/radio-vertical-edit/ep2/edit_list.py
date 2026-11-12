# Episode 2: "Qohumlarla dost olmaq mümkündür?" — caller Bəhruz. Source times in seconds.
from engine import YEL, MAG, CYA, INK, WHITE, PURP
HEADER = ''
CALLER = 'BƏHRUZ'
WHT = (255, 255, 255)
FREEZE_FX = [dict(kind='label', text='EVDƏN QOVDULAR!', t0=0.08, t1=1.25, xy=(540, 1150), size=54, bg=WHT, fg=(200, 20, 60), rot=-5, emoji='1f6aa'),
             dict(kind='emoji', code='1f4a8', t0=0.25, t1=1.25, xy=(880, 420), size=170, rot=8, wob=10, wob_f=12)]
_C = [
    ('hook',   dict(a=249.80, b=256.35, lay='stack')),
    ('greet',  dict(a=0.00,   b=3.40,   lay='call', trans='cut')),
    ('q1',     dict(a=61.45,  b=64.95,  lay='stack')),
    ('story1', dict(a=76.75,  b=84.30,  lay='soloR')),
    ('story2', dict(a=88.15,  b=91.40,  lay='soloR', trans='cut')),
    ('cont',   dict(a=92.55,  b=98.40,  lay='stack')),
    ('tesla',  dict(a=98.40,  b=102.65, lay='punchR', trans='cut')),
    ('fear',   dict(a=103.30, b=108.85, lay='call', trans='cut')),
    ('topic',  dict(a=108.90, b=115.85, lay='stack')),
    ('pct',    dict(a=131.35, b=139.75, lay='call', trans='cut')),
    ('q40',    dict(a=204.80, b=207.98, lay='stack', trans='cut')),
    ('can1',   dict(a=212.60, b=219.95, lay='call', trans='cut')),
    ('can2',   dict(a=220.10, b=226.30, lay='stack', trans='cut')),
    ('can3',   dict(a=226.30, b=233.85, lay='punchR', trans='cut')),
    ('yer',    dict(a=249.80, b=256.35, lay='stack', trans='cut')),
    ('freeze', dict(hold=1.25, at=255.95, lay='punchR', hold_zoom=True, trans='cut', fx=FREEZE_FX,
                    sfx=[('shutter', 0, 0.3), ('scratch', 0, 0.2), ('bonk', 0.35, 0.22)])),
    ('kiss1',  dict(a=395.60, b=398.80, lay='stack', trans='cut')),
    ('kiss2',  dict(a=398.80, b=409.65, lay='call')),
    ('kiss3',  dict(a=409.70, b=416.95, lay='punchR', trans='cut')),
    ('end',    dict(a=425.10, b=428.55, lay='stack', trans='cut')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

SPEAKERS = [
    (0.0, 1.5, 'R'), (1.5, 3.4, 'P'), (61.4, 65.0, 'R'), (76.7, 98.4, 'R'), (98.4, 100.35, 'R'), (100.35, 100.95, 'P'),
    (100.95, 102.65, 'R'), (103.3, 108.85, 'P'), (108.9, 115.9, 'R'), (131.3, 139.8, 'P'), (204.8, 208.0, 'R'),
    (212.6, 220.0, 'P'), (220.0, 233.9, 'R'), (243.0, 254.05, 'R'), (254.05, 255.2, 'P'), (255.2, 256.4, 'R'),
    (395.6, 398.8, 'R'), (398.8, 409.7, 'P'), (409.7, 417.0, 'R'), (425.0, 428.6, 'R'),
]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.95}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

CAPTIONS = [
    ('R', 249.84, 253.74, 'Siz qohumlara gedəndə yer vermədilər sizə, yoxsa deyirlər nə vaxt gedirsiniz?', dict(clip=ci('hook'), hi=['nə', 'vaxt', 'gedirsiniz?'])),
    ('P', 254.14, 255.12, 'Evdən qovdular.', dict(clip=ci('hook'), hi=['qovdular.'])),
    ('R', 255.28, 256.30, 'Evdən qovdular!', dict(clip=ci('hook'), hi=['qovdular!'])),
    ('R', 0.00, 1.00, 'Bəhruz bəy, salam!', {}),
    ('P', 1.70, 3.34, 'Salam, sabahınız xeyir olsun!', dict(hi=['xeyir'])),
    ('R', 61.52, 64.88, 'Neçə dəqiqədir tıxacdasınız, Bəhruz qardaş?', dict(hi=['tıxacdasınız,'])),
    ('R', 76.82, 84.22, 'O gün mən 2 saat 6 dəqiqə Xırdalandan, ekoloji postundan qara-qara evə gəlmişəm.', dict(hi=['2', 'saat', '6', 'dəqiqə'])),
    ('R', 88.18, 91.32, 'Xırdalan tərəfdə elə bil okean keçirsən.', dict(hi=['okean'])),
    ('R', 92.64, 94.60, 'Bir materikdən digər materikə keçirsən.', dict(hi=['materikə'])),
    ('R', 95.58, 98.32, 'Qitələr arasıdır! Qitələr arasıdır, başqa qitədir oranın.', dict(hi=['Qitələr'])),
    ('R', 98.52, 100.22, 'Uçan Tesla lazımdır sizə.', dict(big=True, hi=['Tesla'])),
    ('P', 100.42, 100.80, 'Hı?', {}),
    ('R', 101.10, 102.60, 'Uçan Tesla lazımdır!', dict(big=True, hi=['Tesla'])),
    ('P', 103.40, 108.76, 'Mən uçan maşınlardan qorxuram, hələ ona adapte ola bilmirəm.', dict(hi=['qorxuram,'])),
    ('R', 108.96, 115.76, 'Qardaş, siz qohumlarla bağlı nə deyə bilərsiniz? Qohumlarla dost olmaq mümkündürmü, yoxsa yox?', dict(hi=['dost'])),
    ('P', 131.38, 139.70, 'Bu, hamısına şamil deyil. Haradasa sizə deyim ki, 50-60%-inə aiddir, 40%-i mənim canım-ciyərimdir.', dict(hi=['50-60%-inə', '40%-i', 'canım-ciyərimdir.'])),
    ('R', 204.88, 207.94, 'Yox, 40%-i nə saxlamışsınız ki?', dict(hi=['40%-i'])),
    ('P', 212.70, 219.88, 'Yəni onlardan çox-çox az ünsiyyət qurduğum insanlar olub. Amma həmişə bir-birimizə can deyib, can eşitmişik.', dict(hi=['can'])),
    ('R', 220.20, 220.76, 'Can?', dict(big=True)),
    ('R', 220.84, 224.24, 'Yəni, Bəhruz... Bəhruz can!', dict(hi=['can!'])),
    ('R', 226.36, 229.60, 'Eşitmədim mən canı. Görürsən, mən sənə can deyirəm, amma can eşitmirəm.', dict(hi=['eşitmirəm.'])),
    ('R', 229.84, 233.76, 'Deməli, o 60% qohumların bəzilərinin haqqı var.', dict(hi=['haqqı'])),
    ('R', 249.84, 253.74, 'Siz qohumlara gedəndə yer vermədilər sizə, yoxsa deyirlər nə vaxt gedirsiniz?', dict(clip=ci('yer'), hi=['nə', 'vaxt', 'gedirsiniz?'])),
    ('P', 254.14, 255.12, 'Evdən qovdular.', dict(clip=ci('yer'), hi=['qovdular.'])),
    ('R', 255.28, 256.30, 'Evdən qovdular!', dict(clip=ci('yer'), hi=['qovdular!'])),
    ('R', 395.67, 398.75, 'Yox, sağollaşmamışdan əvvəl öpdün, yoxsa sağollaşdın, sonra öpdün?', dict(hi=['öpdün,', 'öpdün?'])),
    ('P', 398.85, 402.11, 'Yox, uzaqdan-uzağa öpürəm səni, dedim.', dict(hi=['uzaqdan-uzağa'])),
    ('P', 404.37, 409.57, 'Biri var şirin öpüş deyirlər, sevdiyinə. Biri var kinayəli öpüş deyirlər.', dict(hi=['şirin', 'kinayəli'])),
    ('R', 409.77, 413.19, 'Ay Allah, şirin öpüş, şirin öpüş...', dict(hi=['şirin'])),
    ('R', 413.45, 414.87, 'Yanağından elə marçıldadır ki,', dict(hi=['marçıldadır'])),
    ('R', 415.63, 416.85, 'yanağın üç gün ağrıyır!', dict(big=True, hi=['üç', 'gün'])),
    ('R', 425.19, 428.41, 'Öpüş-öpüşə qaldıq, ey, səhər-səhər!', dict(hi=['Öpüş-öpüşə'])),
]

LAUGHS = []
def COUNTER_START(s2o): return 1e9
def FLASHES(s2o): return [s2o(0.0, ci('greet')), s2o(98.40, ci('tesla')), s2o(226.30, ci('can3')), s2o(409.70, ci('kiss3'))]
def SHAKES(s2o): return [(s2o(254.20, ci('yer')), 12), (s2o(415.70, ci('kiss3')), 10), (s2o(98.55, ci('tesla')), 8)]
def _o(s2o, t, c=None): return s2o(t, ci(c) if c else None)

def GAGS(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    G = []
    def em(code, t0, t1, x, y, size=200, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='emoji', code=code, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    def lab(text, t0, t1, x, y, size=44, **k):
        if t0 is None or t1 is None: return
        G.append(dict(kind='label', text=text, t0=t0, t1=t1, xy=(x, y), size=size, **k))
    # hook
    em('1f6cf', o(250.90, 'hook'), o(253.70, 'hook'), 170, 420, 160, rot=-8)
    em('23f0', o(252.70, 'hook'), o(254.10, 'hook'), 900, 420, 150, rot=8, wob=10, wob_f=12)
    em('1f6aa', o(254.15, 'hook'), o(256.35, 'hook'), 170, 1200, 190, rot=-6, wob=8)
    em('1f4a8', o(254.40, 'hook'), o(256.35, 'hook'), 330, 1240, 150, fly=(120, 0), fly_t=0.5)
    # greeting
    lab('ƏVVƏLƏ QAYIDAQ', o(0.0, 'greet'), o(1.4, 'greet'), 540, 560, 40, bg=WHITE, fg=INK, rot=-3, emoji='23ea')
    em('2600', o(1.70), o(3.40), 960, 330, 140, rot=10, wob=8)
    # traffic
    em('1f697', o(61.60), o(64.95), 170, 1200, 170, rot=-6, wob=6)
    em('1f6a6', o(62.40), o(64.95), 900, 420, 150, rot=8)
    lab('2 SAAT 6 DƏQİQƏ', o(77.70), o(84.30), 540, 1080, 50, bg=MAG, fg=WHITE, rot=-4, emoji='23f1')
    em('1f631', o(79.50), o(84.30), 880, 420, 170, rot=8)
    em('1f30a', o(90.40), o(91.40), 880, 420, 200, rot=6, wob=10)
    em('1f6a2', o(90.60), o(91.40), 190, 420, 170, rot=-8, fly=(60, 0))
    em('1f30d', o(92.80), o(94.60), 900, 420, 160, rot=8, wob=6)
    lab('QİTƏLƏRARASI REYS', o(95.60), o(98.40), 300, 1130, 40, bg=CYA, fg=INK, rot=-4, emoji='2708')
    em('1f680', o(98.55, 'tesla'), o(102.65, 'tesla'), 870, 420, 210, rot=20, wob=8, fly=(0, -80), fly_t=1.5)
    em('1f697', o(98.70, 'tesla'), o(102.65, 'tesla'), 200, 460, 180, rot=-18, wob=10, fly=(0, -60), fly_t=1.5)
    em('2753', o(100.42, 'tesla'), o(101.10, 'tesla'), 540, 700, 180, wob=12)
    em('1f631', o(104.30), o(108.85), 960, 330, 140, rot=10, wob=10, wob_f=9)
    em('1f6f8', o(105.80), o(108.85), 120, 330, 140, rot=-12, wob=8)
    # relatives
    lab('MÖVZU:\nQOHUMLARLA DOST\nOLMAQ MÜMKÜNDÜR?', o(109.70), o(115.85), 540, 560, 40, bg=YEL, fg=INK, rot=-3, emoji='1f914')
    lab('60% ✗', o(135.20), o(139.75), 300, 760, 46, bg=(220, 30, 70), fg=WHITE, rot=-6, emoji='1f612')
    lab('40% CAN', o(137.20), o(139.75), 780, 760, 46, bg=(40, 200, 120), fg=INK, rot=5, emoji='2764')
    em('2764', o(218.80, 'can1'), o(219.95, 'can1'), 540, 760, 140, wob=10, wob_f=10)
    em('1f442', o(220.20, 'can2'), o(222.40, 'can2'), 880, 1200, 170, rot=8, wob=10)
    em('1f997', o(224.30, 'can2'), o(226.30, 'can2'), 540, 1280, 170, wob=6, wob_f=14)
    lab('...SƏSSİZLİK...', o(224.40, 'can2'), o(226.30, 'can2'), 540, 1450, 36, bg=WHITE, fg=INK, rot=-2)
    em('1f612', o(228.70, 'can3'), o(233.85, 'can3'), 880, 420, 180, rot=8)
    em('2696', o(232.40, 'can3'), o(233.85, 'can3'), 190, 420, 170, rot=-8, wob=6)
    em('1f6cf', o(250.90, 'yer'), o(253.70, 'yer'), 170, 420, 160, rot=-8)
    em('23f0', o(252.70, 'yer'), o(254.10, 'yer'), 900, 420, 150, rot=8, wob=10, wob_f=12)
    em('1f6aa', o(254.15, 'yer'), o(256.35, 'yer'), 170, 1200, 190, rot=-6, wob=8)
    # kisses
    lab('İNDİ İSƏ... ÖPÜŞLƏR', o(395.60, 'kiss1'), o(397.40, 'kiss1'), 540, 560, 40, bg=MAG, fg=WHITE, rot=-3, emoji='1f48b')
    em('1f914', o(396.80, 'kiss1'), o(398.80, 'kiss1'), 170, 1200, 160, rot=-8)
    em('1f618', o(399.00), o(402.20), 960, 330, 140, rot=10, wob=8)
    em('1f48b', o(399.40), o(402.20), 120, 330, 120, rot=-8, fly=(160, 0), fly_t=1.2)
    em('1f36c', o(405.20), o(407.80), 120, 330, 140, rot=-8, wob=8)
    em('1f60f', o(408.40), o(409.65), 960, 330, 140, rot=8, wob=8)
    em('1f60d', o(410.70, 'kiss3'), o(413.30, 'kiss3'), 880, 420, 180, rot=8, wob=8)
    em('1f4a5', o(414.20, 'kiss3'), o(415.50, 'kiss3'), 200, 460, 200, rot=-8)
    em('1f915', o(415.70, 'kiss3'), o(416.95, 'kiss3'), 880, 420, 200, rot=8, wob=10)
    lab('3 GÜN AĞRI', o(416.00, 'kiss3'), o(416.95, 'kiss3'), 300, 1050, 50, bg=WHITE, fg=(200, 20, 60), rot=-6, emoji='1f915')
    for k, (x, y) in enumerate([(160, 420), (900, 380), (300, 1200), (820, 1250), (540, 330)]):
        em('1f48b', o(425.4+k*0.35, 'end'), o(428.55, 'end'), x, y, 130, rot=(-15+k*8), wob=8, wob_f=6+k)
    lab('BƏHRUZ, UZAQDAN ÖPÜRÜK!', o(426.40, 'end'), o(428.55, 'end'), 540, 1700, 38, bg=YEL, fg=INK, rot=-3, emoji='1f618')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

MUSIC_LEVEL = 0.15
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (0, o(254.05, 'hook'), 0.0),                       # cold open dry until the punch
        (o(254.05, 'hook'), o(256.35, 'hook'), 0.20),
        (o(224.25, 'can2'), o(226.30, 'can2'), 0.0),       # awkward silence (crickets)
        (o(253.75, 'yer'), o(254.10, 'yer'), 0.0),
        (o(398.80, 'kiss2'), o(409.65, 'kiss2'), 0.11),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('pop', o(250.90, 'hook'), 0.18), ('tick', o(252.70, 'hook'), 0.26), ('bonk', o(254.15, 'hook'), 0.24), ('whoosh', o(254.40, 'hook'), 0.20),
        ('scratch', o(256.20, 'hook'), 0.18),
        ('whoosh', o(0.0, 'greet'), 0.24), ('sparkle', o(1.70), 0.14),
        ('pop', o(61.60), 0.18), ('pop2', o(62.40), 0.16),
        ('tick', o(77.70), 0.26), ('tick', o(78.30), 0.26), ('pop', o(79.50), 0.18),
        ('whoosh', o(90.40), 0.20), ('pop2', o(92.80), 0.16), ('ding', o(95.60), 0.14),
        ('riser', o(98.40, 'tesla'), 0.16), ('boing', o(100.42, 'tesla'), 0.18), ('whoosh_up', o(101.10, 'tesla'), 0.18),
        ('slide_down', o(104.30), 0.16),
        ('ding', o(109.70), 0.14), ('pop', o(135.20), 0.18), ('pop2', o(137.20), 0.18),
        ('pop', o(218.80, 'can1'), 0.16), ('pop2', o(220.20, 'can2'), 0.18), ('tick', o(224.40, 'can2'), 0.22), ('tick', o(225.10, 'can2'), 0.22), ('tick', o(225.80, 'can2'), 0.22),
        ('bonk', o(228.70, 'can3'), 0.20), ('ding', o(232.40, 'can3'), 0.14),
        ('pop', o(250.90, 'yer'), 0.18), ('tick', o(252.70, 'yer'), 0.24), ('bonk', o(254.15, 'yer'), 0.24),
        ('sparkle', o(395.60, 'kiss1'), 0.14), ('pop', o(399.00), 0.16), ('whoosh', o(399.40), 0.16),
        ('pop2', o(405.20), 0.16), ('pop', o(408.40), 0.16),
        ('pop2', o(410.70, 'kiss3'), 0.16), ('pop', o(414.20, 'kiss3'), 0.26), ('bonk', o(415.70, 'kiss3'), 0.20),
        ('sparkle', o(425.40, 'end'), 0.16), ('pop', o(425.75, 'end'), 0.12), ('pop2', o(426.10, 'end'), 0.12), ('pop', o(426.45, 'end'), 0.12),
    ]
