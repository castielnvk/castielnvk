# Bəhruz bəy viral reel. Authored in SOURCE times (episode "Qohumlarla dost olmaq") and mapped
# onto the combined clip w8/combo.mov via w8/map.json. Strict captions: clear words only.
import json, os
from engine import YEL, MAG, CYA, INK, WHITE, PURP, WDIR
HEADER = ''
OBA_Y = (255, 205, 0)
_M = json.load(open(os.path.join(WDIR, 'map.json')))
def mp(t):
    for x in _M:
        if x['a']-0.05 <= t <= x['b']+0.05: return x['c0']+(t-x['a'])
    raise ValueError(t)
def caller_name(st): return 'BƏHRUZ BƏY'
# (name, src_a, src_b, layout, extra)
_S = [
    ('topic',  108.90, 116.70, 'stack',  dict()),
    ('heart',  116.70, 119.40, 'stack',  dict(hide='L', trans='cut')),
    ('heart2', 119.40, 125.00, 'call',   dict(hide='L')),
    ('heart3', 125.00, 127.70, 'stack',  dict(hide='L')),
    ('pct',    131.35, 139.75, 'call',   dict(hide='L', trans='cut')),
    ('rayon',  157.30, 166.90, 'call',   dict(trans='cut')),
    ('rayon2', 166.90, 175.40, 'call',   dict(hide='L')),
    ('away',   198.30, 205.00, 'call',   dict(trans='cut')),
    ('q40',    205.00, 208.40, 'stack',  dict(trans='cut')),
    ('can1',   208.40, 219.95, 'call',   dict()),
    ('can2',   220.10, 226.30, 'stack',  dict(trans='cut')),
    ('can3',   226.30, 241.20, 'punchR', dict(trans='cut')),
    ('yer',    243.10, 252.80, 'stack',  dict(trans='cut')),
    ('yer2',   252.80, 256.35, 'stack',  dict(hide='L')),
    ('nb1',    285.10, 299.70, 'call',   dict(trans='cut')),
    ('nb2',    299.70, 306.20, 'stack',  dict()),
    ('nb3',    306.20, 309.25, 'call',   dict()),
    ('oba',    309.25, 313.70, 'punchR', dict(trans='cut')),
    ('obalaf', 313.70, 318.30, 'stack',  dict(trans='cut')),
    ('age',    358.00, 368.70, 'stack',  dict(trans='cut')),
    ('grip',   368.70, 375.40, 'punchR', dict(trans='cut')),
    ('enemy',  379.70, 395.60, 'call',   dict(trans='cut')),
    ('kiss1',  395.60, 398.80, 'stack',  dict(trans='cut')),
    ('kiss2',  398.80, 409.65, 'call',   dict()),
    ('kiss3',  409.70, 417.00, 'punchR', dict(trans='cut')),
    ('kiss4',  417.00, 426.80, 'stack',  dict()),
    ('kiss5',  426.80, 428.60, 'punchR', dict(trans='cut')),
    ('hug',    428.60, 443.70, 'stack',  dict()),
]
_C = [(n, dict(a=mp(a)+0.0, b=mp(b)-0.01, lay=l, **x)) for n, a, b, l, x in _S]
# left host's hand-to-face moment inside nard2 (src ~44.1-46.0)
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

_SPK = [
    (108.9, 116.7, 'R'), (116.7, 119.0, 'R'), (119.0, 121.3, 'P'), (121.3, 122.7, 'R'), (122.7, 139.8, 'P'),
    (157.3, 175.4, 'P'), (198.3, 205.0, 'P'), (205.0, 208.4, 'R'), (208.4, 220.0, 'P'), (220.0, 241.2, 'R'),
    (243.1, 254.05, 'R'), (254.05, 255.2, 'P'), (255.2, 256.4, 'R'), (285.0, 299.7, 'P'), (299.7, 306.2, 'R'),
    (306.2, 309.25, 'P'), (309.25, 318.3, 'R'), (358.0, 362.9, 'R'), (362.9, 366.0, 'P'), (366.0, 367.4, 'R'),
    (367.4, 368.7, 'P'), (368.7, 379.7, 'R'), (379.7, 395.6, 'P'), (395.6, 398.8, 'R'), (398.8, 409.7, 'P'),
    (409.7, 417.0, 'R'), (417.0, 420.5, 'P'), (420.5, 431.7, 'R'), (431.7, 433.4, 'P'), (433.4, 443.7, 'R'),
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
    ('R', 108.96, 115.76, 'Qardaş, siz qohumlarla bağlı nə deyə bilərsiniz? İndi qohumlarla dost olmaq mümkündürmü, yoxsa yox?', dict(hi=['dost'])),
    ('R', 116.82, 118.94, 'Gəlin, birinci özünüzdən başlayaq.', {}),
    ('P', 119.06, 121.30, 'Ürəyim doludur bu məsələ ilə bağlı.', dict(hi=['Ürəyim'])),
    ('R', 121.38, 122.60, 'Danış, danış!', {}),
    ('P', 122.76, 126.40, 'Hardan necə başlayaq, necə sözə girəsən?', {}),
    ('P', 131.38, 139.70, 'Bu, hamısına şamil deyil. Haradasa sizə deyim ki, 50-60%-inə aiddir, 40%-i mənim canım-ciyərimdir.', dict(hi=['40%-i', 'canım-ciyərimdir.'])),
    ('P', 157.30, 159.40, 'Bu, bütün qohumlarıma aiddir.', {}),
    ('P', 165.10, 168.80, 'Rayondan gəlib, evimdə aylarla qalıblar.', dict(hi=['aylarla'])),
    ('P', 170.40, 175.30, 'Yerimi vermişəm, mən özüm yerdə yatmışam. Yerimi vermişəm, yerimdə yatıb.', dict(hi=['yerdə', 'yatmışam.'])),
    ('P', 198.36, 204.98, 'O dəyərləri görmədim və o dediyim 60% qohumlarımdan da uzaqlaşdım.', dict(hi=['uzaqlaşdım.'])),
    ('R', 205.00, 207.94, 'Yox, 40%-i nə saxlamışsınız ki?', dict(hi=['40%-i'])),
    ('P', 212.70, 219.88, 'Yəni onlardan çox-çox az-az ünsiyyət qurduğum insanlar olub. Amma həmişə bir-birimizə can deyib, can eşitmişik.', dict(hi=['can'])),
    ('R', 220.20, 220.76, 'Can?', dict(big=True)),
    ('R', 220.84, 224.24, 'Yəni, Bəhruz... Bəhruz can!', dict(hi=['can!'])),
    ('R', 226.44, 229.60, 'Eşitmədim mən canı. Görürsən, mən sənə can deyirəm, amma can eşitmirəm.', dict(hi=['eşitmirəm.'])),
    ('R', 229.64, 233.76, 'Deməli, o 60% qohumların bəzilərinin haqqı var.', dict(hi=['haqqı'])),
    ('R', 233.84, 240.20, 'Bəhruz can, yavaş-yavaş qohumluq əlaqələrini biz yaradırıq.', dict(hi=['qohumluq'])),
    ('R', 243.18, 249.68, 'Bəhruz, deyirsiniz ki, mən qarşılıq görmədim, onlara yerimi verdim.', dict(hi=['yerimi'])),
    ('R', 249.84, 253.74, 'Siz qohumlara gedəndə yerimi vermədilər sizə, yoxsa deyirlər nə vaxt gedirsiniz?', dict(hi=['nə', 'vaxt', 'gedirsiniz?'])),
    ('P', 254.14, 255.12, 'Evdən qovdular.', dict(hi=['qovdular.'])),
    ('R', 255.28, 256.30, 'Evdən qovdular!', dict(big=True, hi=['QOVDULAR!'])),
    ('P', 285.20, 290.60, 'Valla, bizim bir sözümüz var: uzaq qohum yaxşıdır, yoxsa yaxın qonşu?', dict(hi=['yaxın', 'qonşu?'])),
    ('P', 290.70, 293.60, 'Valla, mən Kürdəxanada yaşayıram, bir dənə qonşum var.', dict(hi=['qonşum'])),
    ('P', 293.78, 299.70, 'O 60%-də olan qohumların heç birinə dəyişmirəm o insanı. Elə gözəl insandır, elə can yandırır.', dict(hi=['dəyişmirəm'])),
    ('R', 299.76, 301.00, 'Qonşusu var, bilirəm, Kürdəxanada.', {}),
    ('R', 303.82, 305.60, 'Bizim də yaxın qonşumuz var da.', dict(hi=['qonşumuz'])),
    ('P', 306.36, 307.80, 'Bir dənə qonşum var.', {}),
    ('R', 309.28, 311.50, 'Bizdə də bir dənədir, bizdə OBA-dır.', dict(big=True, hi=['OBA-DIR.'])),
    ('R', 311.60, 313.30, 'Yaxın qonşumuz da OBA-dır.', dict(hi=['OBA-dır.'])),
    ('R', 314.00, 315.10, 'O, bizdə də var.', {}),
    ('R', 358.06, 362.10, 'İndi bununla bağlı nəsə bir tədbir görürsünüz, Bəhruz?', {}),
    ('P', 362.98, 364.40, 'Qohumluq əlaqələrini dəyişməyək.', {}),
    ('R', 366.02, 367.28, 'Neçə yaşınız var, Bəhruz qardaş?', {}),
    ('P', 367.48, 368.62, '33 yaşım var.', {}),
    ('R', 368.72, 375.20, 'Bundan sonra bərk-bərk yapışın o Kürdəxanadakı qonşunuzdan, bir də bərk-bərk yapışın OBA-mızdan, tamammı?', dict(hi=['OBA-mızdan,'])),
    ('P', 385.20, 386.82, 'Beş günlük dünyada...', {}),
    ('P', 392.02, 392.90, 'Əsas o öpməkdir.', dict(big=True, hi=['ÖPMƏKDİR.'])),
    ('R', 395.67, 398.75, 'Yox, sağollaşmamışdan əvvəl öpdün, yoxsa sağollaşdın, sonra öpdün?', dict(hi=['öpdün,', 'öpdün?'])),
    ('P', 398.85, 402.11, 'Yox, uzaqdan-uzağa öpürəm səni, dedim.', dict(hi=['uzaqdan-uzağa'])),
    ('P', 404.40, 409.57, 'Biri var şirin öpüş deyirlər, sevdiyinə. Biri var kinayəli öpüş deyirlər.', dict(hi=['şirin', 'kinayəli'])),
    ('R', 409.77, 413.19, 'Ay Allah, şirin öpüş, şirin öpüş...', dict(hi=['şirin'])),
    ('R', 413.70, 414.95, 'Yanağından elə marçıldadır ki...', dict(hi=['marçıldadır'])),
    ('R', 420.70, 422.60, 'Sağ olun, Bəhruz, biz də sizi öpürük!', dict(hi=['öpürük!'])),
    ('R', 423.48, 425.10, 'Çox sağ olun, təşəkkür edirik.', {}),
    ('P', 432.44, 433.36, 'Bir gün gələcəm, inşallah.', {}),
    ('R', 433.42, 434.90, 'Bir gün gəl, mən düşüm aşağı...', {}),
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
    def burst(code, t, c, n=6, dur=1.6, cx=540, cy=1500, size=110):
        t0 = o(t, c)
        if t0 is None: return
        import random
        r = random.Random(int(t*100))
        for i in range(n):
            side = -1 if i % 2 == 0 else 1
            x0 = 540+side*r.uniform(330, 450); y0 = 1650+r.uniform(-20, 60)
            G.append(dict(kind='float', code=code, t0=t0+i*0.12, t1=t0+i*0.12+dur, xy=(x0, y0), to=(x0+side*r.uniform(-30, 40), y0-r.uniform(900, 1300)),
                          size=int(size*r.uniform(0.8, 1.2)), rot=r.uniform(-20, 20)))
    # --- relatives ---
    lab('MÖVZU: QOHUMLARLA DOST\nOLMAQ MÜMKÜNDÜR?', o(109.70, 'topic'), o(116.60, 'topic'), 540, 1765, 54, emoji='1f914')
    lab('BƏHRUZ BƏY', o(119.20, 'heart2'), o(122.60, 'heart2'), 540, 1480, 54, emoji='1f4de')
    em('1f494', o(119.20, 'heart2'), o(125.00, 'heart2'), 950, 330, 130)
    em('1f494', o(135.20, 'pct'), o(137.20, 'pct'), 950, 330, 130)
    em('2764', o(137.30, 'pct'), o(139.75, 'pct'), 950, 330, 130)
    kin('40% = CAN', o(137.40, 'pct'), o(139.70, 'pct'), 540, 1550, 92, accent=(255, 120, 150))
    em('1f3e0', o(165.20, 'rayon'), o(166.90, 'rayon'), 950, 330, 130)
    em('1f6cf', o(170.40, 'rayon2'), o(175.40, 'rayon2'), 950, 330, 130)
    kin('YERDƏ YATMIŞAM!', o(171.60, 'rayon2'), o(175.30, 'rayon2'), 540, 1550, 86)
    em('1f622', o(202.00, 'away'), o(205.00, 'away'), 950, 330, 130)
    em('1f914', o(205.10, 'q40'), o(208.40, 'q40'), 880, 420, 160)
    em('2764', o(218.80, 'can1'), o(219.95, 'can1'), 950, 330, 130)
    kin('CAN?', o(220.20, 'can2'), o(221.60, 'can2'), 540, 1560, 120)
    em('1f442', o(220.80, 'can2'), o(224.20, 'can2'), 170, 1200, 160)
    em('1f997', o(224.30, 'can2'), o(226.30, 'can2'), 880, 1200, 160)
    lab('... SƏSSİZLİK ...', o(224.40, 'can2'), o(226.30, 'can2'), 540, 1560, 40)
    em('1f612', o(228.70, 'can3'), o(233.80, 'can3'), 880, 420, 180)
    kin('CAN EŞİTMİRƏM!', o(228.40, 'can3'), o(229.80, 'can3'), 540, 1560, 84)
    em('2696', o(232.00, 'can3'), o(233.80, 'can3'), 170, 420, 160)
    em('1f91d', o(236.00, 'can3'), o(241.20, 'can3'), 880, 420, 170)
    em('1f6cf', o(247.00, 'yer'), o(252.80, 'yer'), 170, 420, 150)
    em('23f0', o(252.00, 'yer'), o(252.80, 'yer'), 880, 420, 150)
    kin('EVDƏN QOVDULAR!', o(255.25, 'yer2'), o(256.35, 'yer2'), 540, 1560, 88, accent=(255, 110, 110))
    em('1f6aa', o(254.15, 'yer2'), o(256.35, 'yer2'), 880, 420, 190)
    burst('1f602', 255.3, 'yer2', n=5, dur=1.1)
    # --- OBA ---
    lab('UZAQ QOHUM < YAXIN QONŞU', o(287.60, 'nb1'), o(290.60, 'nb1'), 540, 1530, 40)
    em('1f3e1', o(291.20, 'nb1'), o(293.60, 'nb1'), 950, 330, 130)
    em('1f60d', o(297.40, 'nb1'), o(299.70, 'nb1'), 120, 330, 130)
    em('1f914', o(303.90, 'nb2'), o(306.20, 'nb2'), 880, 420, 160)
    em('1f6d2', o(310.20, 'oba'), o(313.70, 'oba'), 880, 420, 200)
    kin('OBA!', o(311.00, 'oba'), o(313.70, 'oba'), 540, 1560, 130, accent=OBA_Y)
    burst('1f6d2', 311.2, 'oba', n=5, dur=1.8, size=100)
    em('1f923', o(313.80, 'obalaf'), o(318.30, 'obalaf'), 170, 430, 190)
    em('1f602', o(314.30, 'obalaf'), o(318.30, 'obalaf'), 170, 1200, 180)
    burst('1f923', 314.0, 'obalaf', n=8, dur=2.2)
    em('1f382', o(367.42, 'age'), o(368.70, 'age'), 880, 420, 150)
    em('1f6d2', o(373.10, 'grip'), o(375.40, 'grip'), 880, 420, 190)
    kin('OBA-MIZDAN!', o(373.40, 'grip'), o(375.40, 'grip'), 540, 1560, 100, accent=OBA_Y)
    # --- kisses ---
    lab('İNDİ İSƏ... ÖPÜŞLƏR', o(379.90, 'enemy'), o(383.00, 'enemy'), 540, 1480, 50, accent=(255, 140, 180), emoji='1f48b')
    em('1f48b', o(386.90, 'enemy'), o(395.60, 'enemy'), 950, 330, 130)
    kin('ƏSAS O ÖPMƏKDİR!', o(392.00, 'enemy'), o(395.50, 'enemy'), 540, 1560, 80, accent=(255, 140, 180))
    burst('1f48b', 392.2, 'enemy', n=6, dur=2.0)
    em('1f914', o(396.20, 'kiss1'), o(398.80, 'kiss1'), 880, 420, 170)
    em('1f618', o(399.00, 'kiss2'), o(402.20, 'kiss2'), 950, 330, 130)
    burst('1f618', 399.6, 'kiss2', n=5, dur=1.8)
    em('1f36c', o(404.60, 'kiss2'), o(407.80, 'kiss2'), 950, 330, 130)
    em('1f60f', o(407.90, 'kiss2'), o(409.65, 'kiss2'), 120, 330, 130)
    kin('ŞİRİN ÖPÜŞ', o(405.00, 'kiss2'), o(407.20, 'kiss2'), 540, 1560, 84, accent=(255, 140, 180))
    kin('KİNAYƏLİ ÖPÜŞ', o(407.90, 'kiss2'), o(409.60, 'kiss2'), 540, 1560, 84, accent=(180, 160, 255))
    em('1f60d', o(410.40, 'kiss3'), o(413.30, 'kiss3'), 880, 420, 180)
    burst('2764', 410.6, 'kiss3', n=7, dur=2.0)
    em('1f4a5', o(413.70, 'kiss3'), o(417.00, 'kiss3'), 880, 420, 180)
    em('1f48b', o(420.80, 'kiss4'), o(426.80, 'kiss4'), 880, 420, 170)
    burst('1f48b', 421.0, 'kiss4', n=6, dur=2.0)
    kin('ÖPÜŞ-ÖPÜŞƏ QALDIQ!', o(426.90, 'kiss5'), o(428.60, 'kiss5'), 540, 1560, 80, accent=(255, 140, 180))
    burst('1f48b', 426.9, 'kiss5', n=8, dur=1.7)
    burst('1f618', 427.3, 'kiss5', n=5, dur=1.3)
    em('1f917', o(429.60, 'hug'), o(436.00, 'hug'), 880, 420, 180)
    em('1f923', o(436.00, 'hug'), o(443.70, 'hug'), 880, 420, 180)
    burst('1f917', 433.6, 'hug', n=6, dur=2.0)
    lab('BƏHRUZ BƏY, UZAQDAN ÖPÜRÜK!', o(439.00, 'hug'), o(443.70, 'hug'), 540, 1760, 46, accent=(255, 140, 180), emoji='1f618')
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

def PUNCHES(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [o(119.10, 'heart2'), o(137.40, 'pct'), o(171.60, 'rayon2'), o(220.20, 'can2'), o(228.40, 'can3'),
            o(254.15, 'yer2'), o(255.28, 'yer2'), o(309.30, 'oba'), o(311.00, 'oba'), o(313.80, 'obalaf'),
            o(373.40, 'grip'), o(392.00, 'enemy'), o(396.20, 'kiss1'), o(405.20, 'kiss2'), o(408.40, 'kiss2'),
            o(410.40, 'kiss3'), o(413.70, 'kiss3'), o(421.00, 'kiss4'), o(426.90, 'kiss5'), o(433.60, 'hug')]

MUSIC_LEVEL = 0.13
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (o(119.10, 'heart2'), o(127.70, 'heart3'), 0.09),
        (o(131.35, 'pct'), o(139.75, 'pct'), 0.09),
        (o(157.30, 'rayon'), o(175.40, 'rayon2'), 0.09),
        (o(198.30, 'away'), o(205.00, 'away'), 0.08),
        (o(208.40, 'can1'), o(219.95, 'can1'), 0.09),
        (o(224.25, 'can2'), o(226.30, 'can2'), 0.0),
        (o(254.00, 'yer2'), o(256.35, 'yer2'), 0.0),
        (o(285.10, 'nb1'), o(299.70, 'nb1'), 0.09),
        (o(308.60, 'nb3'), o(309.25, 'nb3'), 0.0),
        (o(309.25, 'oba'), o(313.70, 'oba'), 0.0),
        (o(313.70, 'obalaf'), o(318.30, 'obalaf'), 0.22),
        (o(379.70, 'enemy'), o(395.60, 'enemy'), 0.09),
        (o(398.80, 'kiss2'), o(409.65, 'kiss2'), 0.09),
        (o(409.70, 'kiss3'), o(417.00, 'kiss3'), 0.18),
        (o(426.80, 'kiss5'), o(428.60, 'kiss5'), 0.24),
        (o(428.60, 'hug'), o(443.70, 'hug'), 0.16),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(109.00, 'topic'), 0.12), ('pop', o(109.70, 'topic'), 0.10),
        ('whoosh', o(119.10, 'heart2'), 0.10), ('pop2', o(119.20, 'heart2'), 0.09), ('pop', o(135.20, 'pct'), 0.09),
        ('sparkle', o(137.40, 'pct'), 0.10), ('pop', o(165.20, 'rayon'), 0.09), ('bonk', o(171.60, 'rayon2'), 0.10),
        ('pop2', o(202.00, 'away'), 0.08), ('pop', o(205.10, 'q40'), 0.09),
        ('boing', o(220.20, 'can2'), 0.12), ('tick', o(224.40, 'can2'), 0.12), ('tick', o(225.10, 'can2'), 0.12), ('tick', o(225.80, 'can2'), 0.12),
        ('bonk', o(228.40, 'can3'), 0.11), ('ding', o(232.00, 'can3'), 0.09), ('pop', o(236.00, 'can3'), 0.08),
        ('pop', o(247.00, 'yer'), 0.08), ('tick', o(252.00, 'yer'), 0.12), ('whoosh', o(254.15, 'yer2'), 0.12), ('bonk', o(255.28, 'yer2'), 0.13),
        ('ding', o(287.60, 'nb1'), 0.09), ('pop', o(291.20, 'nb1'), 0.08), ('sparkle', o(297.40, 'nb1'), 0.08),
        ('pop2', o(303.90, 'nb2'), 0.08), ('riser', o(308.00, 'nb3'), 0.08),
        ('whoosh', o(310.20, 'oba'), 0.12), ('badumtss', o(311.00, 'oba'), 0.16), ('sparkle', o(311.20, 'oba'), 0.10),
        ('pop', o(313.90, 'obalaf'), 0.08), ('pop2', o(314.20, 'obalaf'), 0.08), ('pop', o(314.50, 'obalaf'), 0.08),
        ('pop', o(367.42, 'age'), 0.08), ('whoosh', o(373.10, 'grip'), 0.10), ('ding', o(373.40, 'grip'), 0.11),
        ('sparkle', o(379.90, 'enemy'), 0.10), ('pop', o(386.90, 'enemy'), 0.08), ('sparkle', o(392.00, 'enemy'), 0.12),
        ('pop2', o(392.20, 'enemy'), 0.08), ('pop', o(392.50, 'enemy'), 0.08),
        ('boing', o(396.20, 'kiss1'), 0.11), ('whoosh', o(399.00, 'kiss2'), 0.09), ('pop', o(399.60, 'kiss2'), 0.08), ('pop2', o(399.90, 'kiss2'), 0.08),
        ('sparkle', o(405.00, 'kiss2'), 0.10), ('slide_down', o(407.90, 'kiss2'), 0.08),
        ('whoosh', o(409.80, 'kiss3'), 0.10), ('sparkle', o(410.60, 'kiss3'), 0.11), ('bonk', o(413.80, 'kiss3'), 0.12),
        ('pop', o(421.00, 'kiss4'), 0.08), ('pop2', o(421.30, 'kiss4'), 0.08), ('sparkle', o(421.10, 'kiss4'), 0.09),
        ('whoosh', o(426.85, 'kiss5'), 0.12), ('sparkle', o(426.90, 'kiss5'), 0.13), ('pop', o(427.10, 'kiss5'), 0.09), ('pop2', o(427.40, 'kiss5'), 0.09), ('pop', o(427.70, 'kiss5'), 0.09),
        ('boing', o(429.60, 'hug'), 0.09), ('sparkle', o(433.60, 'hug'), 0.10), ('pop', o(436.00, 'hug'), 0.08), ('ding', o(439.00, 'hug'), 0.10),
    ]
