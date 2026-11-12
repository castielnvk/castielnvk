# Episode 2: "Qohumlarla dost olmaq mümkündür?" — caller Bəhruz. Source times in seconds.
from engine import YEL, MAG, CYA, INK, WHITE, PURP
HEADER = ''
CALLER = 'BƏHRUZ'
WHT = (255, 255, 255)
FREEZE_FX = [dict(kind='label', text='EVDƏN QOVDULAR!', t0=0.08, t1=1.25, xy=(540, 1150), size=54, bg=WHT, fg=(200, 20, 60), rot=-5, emoji='1f6aa'),
             dict(kind='emoji', code='1f4a8', t0=0.25, t1=1.25, xy=(880, 420), size=170, rot=8, wob=10, wob_f=12)]
_C = [
    ('hook',   dict(a=309.20, b=317.60, lay='stack')),
    ('greet',  dict(a=0.00,   b=6.90,   lay='call', trans='cut')),
    ('q1',     dict(a=61.45,  b=64.95,  lay='stack')),
    ('story1', dict(a=76.75,  b=84.30,  lay='soloR')),
    ('cont',   dict(a=92.55,  b=98.40,  lay='stack', trans='cut')),
    ('tesla',  dict(a=98.40,  b=102.65, lay='punchR', trans='cut')),
    ('fear',   dict(a=103.30, b=108.85, lay='call', trans='cut')),
    ('nard',   dict(a=36.60,  b=39.40,  lay='punchR', trans='cut')),
    ('nard2',  dict(a=41.25,  b=47.00,  lay='call', trans='cut')),
    ('nard3',  dict(a=51.30,  b=55.35,  lay='stack', trans='cut')),
    ('topic',  dict(a=108.90, b=115.85, lay='stack', trans='cut')),
    ('pct',    dict(a=131.35, b=139.75, lay='call', trans='cut')),
    ('q40',    dict(a=204.80, b=207.98, lay='stack', trans='cut')),
    ('can1',   dict(a=212.60, b=219.95, lay='call', trans='cut')),
    ('can2',   dict(a=220.10, b=226.30, lay='stack', trans='cut')),
    ('can3',   dict(a=226.30, b=241.20, lay='punchR', trans='cut')),
    ('yer',    dict(a=243.10, b=256.35, lay='stack', trans='cut')),
    ('freeze', dict(hold=1.25, at=255.95, lay='punchR', hold_zoom=True, trans='cut', fx=FREEZE_FX,
                    sfx=[('pop2', 0, 0.25), ('bonk', 0.35, 0.22)])),
    ('nb1',    dict(a=285.10, b=299.70, lay='call', trans='cut')),
    ('nb2',    dict(a=299.70, b=306.20, lay='stack')),
    ('nb3',    dict(a=306.20, b=309.25, lay='call', trans='cut')),
    ('oba',    dict(a=309.25, b=313.70, lay='punchR', trans='cut')),
    ('obalaf', dict(a=313.70, b=318.20, lay='stack', trans='cut')),
    ('age',    dict(a=365.90, b=368.68, lay='call', trans='cut')),
    ('grip',   dict(a=368.68, b=375.30, lay='punchR', trans='cut')),
    ('kiss1',  dict(a=395.60, b=398.80, lay='stack', trans='cut')),
    ('kiss2',  dict(a=398.80, b=409.65, lay='call')),
    ('kiss3',  dict(a=409.70, b=417.30, lay='punchR', trans='cut')),
    ('end',    dict(a=420.55, b=422.65, lay='stack', trans='cut')),
    ('end2',   dict(a=426.80, b=428.60, lay='stack', trans='cut')),
]
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

SPEAKERS = [
    (0.0, 1.5, 'R'), (1.5, 3.5, 'P'), (3.5, 6.9, 'R'), (36.5, 39.5, 'R'), (41.2, 47.1, 'P'), (51.3, 55.4, 'R'),
    (61.4, 65.0, 'R'), (76.7, 98.4, 'R'), (98.4, 100.35, 'R'), (100.35, 100.95, 'P'),
    (100.95, 102.65, 'R'), (103.3, 108.85, 'P'), (108.9, 115.9, 'R'), (131.3, 139.8, 'P'), (204.8, 208.0, 'R'),
    (212.6, 220.0, 'P'), (220.0, 241.2, 'R'), (243.0, 254.05, 'R'), (254.05, 255.2, 'P'), (255.2, 256.4, 'R'),
    (285.0, 299.7, 'P'), (299.7, 306.2, 'R'), (306.2, 309.25, 'P'), (309.25, 315.2, 'R'),
    (365.9, 367.4, 'R'), (367.4, 368.68, 'P'), (368.68, 375.3, 'R'),
    (395.6, 398.8, 'R'), (398.8, 409.7, 'P'), (409.7, 417.3, 'R'), (420.5, 428.6, 'R'),
]
SPK_GAIN = {'R': 1.0, 'L': 1.04, 'P': 0.95}
def speaker_at(st):
    for a, b, k in SPEAKERS:
        if a <= st < b: return k
    return None

CAPTIONS = [
    ('R', 309.28, 311.50, 'Bizdə də bir dənədir, bizdə OBA-dır.', dict(clip=ci('hook'), big=True, hi=['OBA-dır.'])),
    ('R', 311.60, 313.30, 'Yaxın qonşumuz da OBA-dır.', dict(clip=ci('hook'), hi=['OBA-dır.'])),
    ('R', 0.00, 1.00, 'Bəhruz bəy, salam!', {}),
    ('P', 1.78, 3.40, 'Salam, sabahınız xeyir olsun!', dict(hi=['xeyir'])),
    ('R', 3.70, 6.80, 'O qardaş, sən arada yatıb, bu enerjini necə işlədirsən?', dict(hi=['enerjini'])),
    ('R', 61.52, 64.88, 'Neçə dəqiqədir tıxacdasınız, Bəhruz qardaş?', dict(hi=['tıxacdasınız,'])),
    ('R', 76.82, 84.22, 'O gün mən 2 saat 6 dəqiqə Xırdalandan, ekoloji postundan qara-qara evə gəlmişəm.', dict(hi=['2', 'saat', '6', 'dəqiqə'])),
    ('R', 92.64, 94.60, 'Bir materikdən digər materikə keçirsən.', dict(hi=['materikə'])),
    ('R', 95.58, 98.32, 'Qitələr arasıdır! Qitələr arasıdır, başqa qitədir oranın.', dict(hi=['Qitələr'])),
    ('R', 98.52, 100.22, 'Uçan Tesla lazımdır sizə.', dict(big=True, hi=['Tesla'])),
    ('P', 100.42, 100.80, 'Hı?', {}),
    ('R', 101.10, 102.60, 'Uçan Tesla lazımdır!', dict(big=True, hi=['Tesla'])),
    ('P', 103.40, 108.76, 'Mən uçan maşınlardan qorxuram, hələ ona adaptasiya ola bilmirəm.', dict(hi=['qorxuram,'])),
    ('R', 36.74, 39.30, 'Maşının yük yerinə bir dənə nərd atırsınız?', dict(big=True, hi=['nərd'])),
    ('P', 41.36, 46.90, 'Məşğuliyyətim sizsiniz, gözəl insanlar. Hər səhər bu yolu gedəndə hər gün sizə qulaq asıram.', dict(hi=['Məşğuliyyətim', 'sizsiniz,'])),
    ('R', 51.38, 55.30, 'Gördün, gördün, Elgün? Bizə heç nərd də lazım deyil, siz varsınız!', dict(hi=['nərd'])),
    ('R', 108.96, 115.76, 'Qardaş, siz qohumlarla bağlı nə deyə bilərsiniz? Qohumlarla dost olmaq mümkündürmü, yoxsa yox?', dict(hi=['dost'])),
    ('P', 131.38, 139.70, 'Bu, hamısına şamil deyil. Haradasa sizə deyim ki, 50-60%-inə aiddir, 40%-i mənim canım-ciyərimdir.', dict(hi=['50-60%-inə', '40%-i', 'canım-ciyərimdir.'])),
    ('R', 204.88, 207.94, 'Yox, 40%-i nə saxlamışsınız ki?', dict(hi=['40%-i'])),
    ('P', 212.70, 219.88, 'Yəni onlardan çox-çox az ünsiyyət qurduğum insanlar olub. Amma həmişə bir-birimizə can deyib, can eşitmişik.', dict(hi=['can'])),
    ('R', 220.20, 220.76, 'Can?', dict(big=True)),
    ('R', 220.84, 224.24, 'Yəni, Bəhruz... Bəhruz can!', dict(hi=['can!'])),
    ('R', 226.44, 229.60, 'Eşitmədim mən canı. Görürsən, mən sənə can deyirəm, amma can eşitmirəm.', dict(hi=['eşitmirəm.'])),
    ('R', 229.64, 233.76, 'Deməli, o 60% qohumların bəzilərinin haqqı var.', dict(hi=['haqqı'])),
    ('R', 233.84, 240.20, 'Bəhruz can, yavaş-yavaş qohumluq əlaqələrini biz yaradırıq.', dict(hi=['qohumluq'])),
    ('R', 243.18, 249.68, 'Bəhruz, deyirsiniz ki, mən qarşılıq görmədim, onlara yerimi verdim, yediyimdən yedizdirdim.', dict(hi=['yerimi'])),
    ('R', 249.84, 253.74, 'Siz qohumlara gedəndə yerimi vermədilər sizə, yoxsa deyirlər nə vaxt gedirsiniz?', dict(hi=['nə', 'vaxt', 'gedirsiniz?'])),
    ('P', 254.14, 255.12, 'Evdən qovdular.', dict(hi=['qovdular.'])),
    ('R', 255.28, 256.30, 'Evdən qovdular!', dict(big=True, hi=['qovdular!'])),
    ('P', 285.20, 290.60, 'Valla, bizim bir sözümüz var: uzaq qohumdan yaxın qonşu yaxşıdır.', dict(hi=['qonşu'])),
    ('P', 290.70, 293.60, 'Mən Kürdəxanada yaşayıram, bir dənə qonşum var.', dict(hi=['Kürdəxanada'])),
    ('P', 293.78, 299.70, 'O 60%-dəki qohumların heç birinə dəyişmirəm o insanı. Elə gözəl insandır, elə can yandırır.', dict(hi=['dəyişmirəm'])),
    ('R', 299.76, 301.00, 'Qonşusu var, bilirəm, Kürdəxanada.', {}),
    ('R', 303.82, 305.60, 'Bizim də yaxın qonşumuz var da.', dict(hi=['qonşumuz'])),
    ('P', 306.36, 309.25, 'Bir dənə qonşum var...', {}),
    ('R', 309.28, 311.50, 'Bizdə də bir dənədir, bizdə OBA-dır.', dict(clip=ci('oba'), big=True, hi=['OBA-dır.'])),
    ('R', 311.60, 313.30, 'Yaxın qonşumuz da OBA-dır.', dict(clip=ci('oba'), hi=['OBA-dır.'])),
    ('R', 314.00, 316.00, 'O, bizdə də var. O, bizdə də var!', dict(hi=['var!'])),
    ('R', 365.96, 367.20, 'Neçə yaşınız var, Bəhruz qardaş?', {}),
    ('P', 367.42, 368.60, '33 yaşım var.', dict(hi=['33'])),
    ('R', 368.72, 375.20, 'Bundan sonra bərk-bərk yapışın o Kürdəxanadakı qonşunuzdan, bir də bərk-bərk yapışın OBA-mızdan, tamammı?', dict(hi=['OBA-mızdan,', 'qonşunuzdan,'])),
    ('R', 395.67, 398.75, 'Yox, sağollaşmamışdan əvvəl öpdün, yoxsa sağollaşdın, sonra öpdün?', dict(hi=['öpdün,', 'öpdün?'])),
    ('P', 398.85, 402.11, 'Yox, uzaqdan-uzağa öpürəm səni, dedim.', dict(hi=['uzaqdan-uzağa'])),
    ('P', 404.40, 409.57, 'Biri var şirin öpüş deyirlər, sevdiyinə. Biri var kinayəli öpüş deyirlər.', dict(hi=['şirin', 'kinayəli'])),
    ('R', 409.77, 413.19, 'Ay Allah, şirin öpüş, şirin öpüş...', dict(hi=['şirin'])),
    ('R', 413.70, 415.00, 'Yanağından elə marçıldadır ki,', dict(hi=['marçıldadır'])),
    ('R', 415.04, 416.90, 'yanağı üç gün ağrıyır!', dict(big=True, hi=['üç', 'gün'])),
    ('R', 420.70, 422.60, 'Sağ olun, Bəhruz, biz də sizi öpürük!', dict(hi=['öpürük!'])),
    ('R', 426.90, 428.50, 'Öpüş-öpüşə qaldıq, səhər-səhər!', dict(big=True, hi=['Öpüş-öpüşə'])),
]

LAUGHS = []
def COUNTER_START(s2o): return 1e9
def FLASHES(s2o): return [s2o(0.0, ci('greet')), s2o(98.40, ci('tesla')), s2o(36.60, ci('nard')), s2o(309.25, ci('oba')), s2o(409.70, ci('kiss3'))]
def SHAKES(s2o): return [(s2o(254.20, ci('yer')), 12), (s2o(311.0, ci('oba')), 12), (s2o(314.0, ci('obalaf')), 10), (s2o(415.10, ci('kiss3')), 10), (s2o(98.55, ci('tesla')), 8), (s2o(373.6, ci('grip')), 8)]
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
    em('1f4a5', o(414.20, 'kiss3'), o(415.10, 'kiss3'), 200, 460, 200, rot=-8)
    em('1f915', o(415.10, 'kiss3'), o(417.30, 'kiss3'), 880, 420, 200, rot=8, wob=10)
    lab('3 GÜN AĞRI', o(415.60, 'kiss3'), o(417.30, 'kiss3'), 300, 1050, 50, bg=WHITE, fg=(200, 20, 60), rot=-6, emoji='1f915')
    for k, (x, y) in enumerate([(160, 420), (900, 380), (300, 1200), (820, 1250), (540, 330)]):
        em('1f48b', o(426.9+k*0.25, 'end2'), o(428.60, 'end2'), x, y, 130, rot=(-15+k*8), wob=8, wob_f=6+k)
    lab('BƏHRUZ, UZAQDAN ÖPÜRÜK!', o(427.00, 'end2'), o(428.60, 'end2'), 540, 1700, 38, bg=YEL, fg=INK, rot=-3, emoji='1f618')
    # hook: OBA
    em('1f6d2', o(310.20, 'hook'), o(313.70, 'hook'), 880, 420, 190, rot=8, wob=8)
    em('1f923', o(314.00, 'hook'), o(317.60, 'hook'), 170, 430, 190, rot=-12, wob=12, wob_f=10)
    em('1f602', o(314.40, 'hook'), o(317.60, 'hook'), 170, 1200, 170, rot=10, wob=12, wob_f=9)
    # greeting energy
    em('26a1', o(5.30), o(6.90), 120, 330, 130, rot=-10, wob=10)
    # nərd
    em('1f3b2', o(38.60, 'nard'), o(39.40, 'nard'), 880, 420, 190, rot=12, wob=14, wob_f=11)
    em('1f697', o(37.30, 'nard'), o(39.40, 'nard'), 190, 460, 170, rot=-8)
    em('1f3a7', o(44.30), o(47.00), 960, 330, 130, rot=8, wob=6)
    em('2764', o(41.40), o(43.30), 120, 330, 120, wob=10, wob_f=9)
    em('1f3b2', o(54.30, 'nard3'), o(55.35, 'nard3'), 170, 1200, 160, rot=-10)
    em('1f6ab', o(54.40, 'nard3'), o(55.35, 'nard3'), 170, 1200, 210, rot=-10)
    # can follow-up
    em('1f91d', o(237.80, 'can3'), o(241.20, 'can3'), 190, 420, 170, rot=-6, wob=6)
    # neighbours
    lab('UZAQ QOHUM < YAXIN QONŞU', o(287.60, 'nb1'), o(290.60, 'nb1'), 540, 760, 36, bg=YEL, fg=INK, rot=-3, emoji='1f3e1')
    em('1f3e1', o(291.20, 'nb1'), o(293.60, 'nb1'), 960, 330, 130, rot=8)
    em('1f60d', o(297.40, 'nb1'), o(299.70, 'nb1'), 120, 330, 130, rot=-8, wob=8)
    em('1f914', o(303.80, 'nb2'), o(306.20, 'nb2'), 880, 420, 160, rot=8)
    em('1f6d2', o(310.20, 'oba'), o(313.70, 'oba'), 880, 420, 210, rot=8, wob=8)
    lab('OBA', o(310.95, 'oba'), o(313.70, 'oba'), 300, 1080, 70, bg=(255, 205, 0), fg=(200, 20, 60), rot=-6, emoji='1f6d2')
    em('1f923', o(313.80, 'obalaf'), o(318.20, 'obalaf'), 170, 430, 200, rot=-12, wob=12, wob_f=10)
    em('1f602', o(314.30, 'obalaf'), o(318.20, 'obalaf'), 170, 1200, 180, rot=10, wob=12, wob_f=9)
    em('1f480', o(316.00, 'obalaf'), o(318.20, 'obalaf'), 880, 420, 160, rot=8, wob=8)
    # callback
    em('1f382', o(367.42, 'age'), o(368.68, 'age'), 960, 330, 130, rot=8)
    em('1f3e1', o(369.80, 'grip'), o(371.80, 'grip'), 190, 420, 170, rot=-8)
    em('1f6d2', o(373.10, 'grip'), o(375.30, 'grip'), 880, 420, 200, rot=10, wob=10)
    lab('OBA', o(373.60, 'grip'), o(375.30, 'grip'), 300, 1080, 70, bg=(255, 205, 0), fg=(200, 20, 60), rot=-6, emoji='1f6d2')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

MUSIC_LEVEL = 0.14
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (0, o(313.70, 'hook'), 0.0),                        # cold open dry until the laugh
        (o(313.70, 'hook'), o(317.60, 'hook'), 0.20),
        (o(224.25, 'can2'), o(226.30, 'can2'), 0.0),        # awkward silence
        (o(253.75, 'yer'), o(254.10, 'yer'), 0.0),
        (o(308.60, 'nb3'), o(309.25, 'nb3'), 0.0),
        (o(309.25, 'oba'), o(313.70, 'oba'), 0.0),          # silence for the OBA punchline
        (o(313.70, 'obalaf'), o(318.20, 'obalaf'), 0.22),   # groove back with the laugh
        (o(285.10, 'nb1'), o(299.70, 'nb1'), 0.10),
        (o(398.80, 'kiss2'), o(409.65, 'kiss2'), 0.10),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('pop', o(310.20, 'hook'), 0.18), ('badumtss', o(313.40, 'hook'), 0.22), ('pop2', o(314.40, 'hook'), 0.14),
        ('whoosh', o(0.0, 'greet'), 0.22), ('sparkle', o(1.78), 0.12), ('boing', o(5.30), 0.16),
        ('pop', o(61.60), 0.16), ('pop2', o(62.40), 0.14),
        ('tick', o(77.70), 0.18), ('tick', o(78.30), 0.18), ('pop', o(79.50), 0.16),
        ('pop2', o(92.80), 0.14), ('ding', o(95.60), 0.12),
        ('riser', o(98.40, 'tesla'), 0.14), ('boing', o(100.42, 'tesla'), 0.16), ('whoosh_up', o(101.10, 'tesla'), 0.16),
        ('slide_down', o(104.30), 0.14),
        ('pop', o(37.30, 'nard'), 0.16), ('boing', o(38.60, 'nard'), 0.18), ('sparkle', o(41.40), 0.12), ('pop2', o(44.30), 0.14),
        ('bonk', o(54.40, 'nard3'), 0.18),
        ('ding', o(109.70), 0.12), ('pop', o(135.20), 0.16), ('pop2', o(137.20), 0.16),
        ('pop', o(218.80, 'can1'), 0.14), ('pop2', o(220.20, 'can2'), 0.16), ('tick', o(224.40, 'can2'), 0.16), ('tick', o(225.10, 'can2'), 0.16), ('tick', o(225.80, 'can2'), 0.16),
        ('bonk', o(228.70, 'can3'), 0.18), ('ding', o(232.40, 'can3'), 0.12), ('pop', o(237.80, 'can3'), 0.14),
        ('pop', o(250.90, 'yer'), 0.16), ('tick', o(252.70, 'yer'), 0.16), ('bonk', o(254.15, 'yer'), 0.22),
        ('ding', o(287.60, 'nb1'), 0.12), ('pop', o(291.20, 'nb1'), 0.14), ('sparkle', o(297.40, 'nb1'), 0.12),
        ('pop2', o(303.80, 'nb2'), 0.14), ('pop', o(310.20, 'oba'), 0.18), ('badumtss', o(313.40, 'oba'), 0.24),
        ('pop2', o(314.30, 'obalaf'), 0.14), ('pop', o(316.00, 'obalaf'), 0.14),
        ('pop', o(367.42, 'age'), 0.14), ('pop2', o(369.80, 'grip'), 0.14), ('boing', o(373.10, 'grip'), 0.18),
        ('sparkle', o(395.60, 'kiss1'), 0.12), ('pop', o(399.00), 0.14), ('whoosh', o(399.40), 0.14),
        ('pop2', o(405.20), 0.14), ('pop', o(408.40), 0.14),
        ('pop2', o(410.70, 'kiss3'), 0.14), ('pop', o(414.20, 'kiss3'), 0.22), ('bonk', o(415.10, 'kiss3'), 0.18),
        ('sparkle', o(426.90, 'end2'), 0.14), ('pop', o(427.15, 'end2'), 0.10), ('pop2', o(427.40, 'end2'), 0.10),
    ]
