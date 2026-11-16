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
    ('greet', 0.00, 3.50, 'call', dict(hide='L')),
    ('road', 20.65, 26.85, 'call', dict(hide='L', trans='cut')),
    ('nard', 36.60, 39.40, 'punchR', dict(trans='cut')),
    ('nard2', 41.25, 47.00, 'call', dict(trans='cut', hide='L')),
    ('nard3', 51.30, 53.00, 'stack', dict(trans='cut')),
    ('q1', 61.45, 64.95, 'stack', dict(trans='cut')),
    ('tesla', 98.40, 102.65, 'punchR', dict(trans='cut')),
    ('fear', 103.30, 108.85, 'call', dict(trans='cut')),
    ('topic', 108.90, 115.20, 'stack', dict(trans='cut')),
    ('topic2', 115.20, 115.85, 'stack', dict(hide='L')),
    ('pct', 131.35, 139.75, 'call', dict(hide='L', trans='cut')),
    ('q40', 204.80, 207.98, 'stack', dict(trans='cut')),
    ('can1', 212.60, 219.95, 'call', dict(trans='cut')),
    ('can2', 220.10, 226.30, 'stack', dict(trans='cut')),
    ('can3', 226.30, 241.20, 'punchR', dict(trans='cut')),
    ('yer', 249.80, 252.80, 'stack', dict(trans='cut')),
    ('yer2', 252.80, 256.35, 'stack', dict(hide='L')),
    ('nb1', 285.10, 299.70, 'call', dict(trans='cut')),
    ('nb2', 303.80, 306.20, 'stack', dict(trans='cut')),
    ('nb3', 306.20, 309.25, 'call', dict()),
    ('oba', 309.25, 313.70, 'punchR', dict(trans='cut')),
    ('obalaf', 313.70, 318.20, 'stack', dict(trans='cut')),
    ('grip', 365.90, 375.30, 'stack', dict(trans='cut')),
    ('kiss1', 395.60, 398.80, 'stack', dict(trans='cut')),
    ('kiss2', 398.80, 409.65, 'call', dict()),
    ('kiss3', 409.70, 415.00, 'punchR', dict(trans='cut')),
    ('end', 420.55, 422.65, 'stack', dict(trans='cut')),
    ('end2', 426.80, 428.60, 'stack', dict(trans='cut')),
]
_C = [(n, dict(a=mp(a)+0.0, b=mp(b)-0.01, lay=l, **x)) for n, a, b, l, x in _S]
# left host's hand-to-face moment inside nard2 (src ~44.1-46.0)
CLIPS = [c for _, c in _C]
IDX = {n: i for i, (n, _) in enumerate(_C)}
def ci(name): return IDX[name]

_SPK = [
    (0.0, 1.5, 'R'), (1.5, 3.5, 'P'), (20.6, 26.9, 'P'), (36.5, 39.5, 'R'), (41.2, 47.1, 'P'), (51.3, 53.0, 'R'),
    (61.4, 65.0, 'R'), (98.4, 100.35, 'R'), (100.35, 100.95, 'P'), (100.95, 102.65, 'R'), (103.3, 108.85, 'P'),
    (108.9, 115.9, 'R'), (131.3, 139.8, 'P'), (204.8, 208.0, 'R'), (212.6, 220.0, 'P'), (220.0, 241.2, 'R'),
    (249.8, 254.05, 'R'), (254.05, 255.2, 'P'), (255.2, 256.4, 'R'), (285.0, 299.7, 'P'), (299.7, 306.2, 'R'),
    (306.2, 309.25, 'P'), (309.25, 318.2, 'R'), (365.9, 367.4, 'R'), (367.4, 368.68, 'P'), (368.68, 375.3, 'R'),
    (395.6, 398.8, 'R'), (398.8, 409.7, 'P'), (409.7, 428.6, 'R'),
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
    ('R', 0.00, 1.00, 'Bəhruz bəy, salam!', {}),
    ('P', 1.70, 3.34, 'Salam, sabahınız xeyir olsun!', {}),
    ('P', 20.72, 26.80, 'Elə bu dəqiqə ... gölün yolundayıq, vəziyyət bərbaddır.', dict(hi=['bərbaddır.'])),
    ('R', 36.74, 39.30, 'Maşının yük yerinə bir dənə nərd atırsınız?', dict(big=True, hi=['nərd', 'NƏRD'])),
    ('P', 41.36, 43.30, 'Məşğuliyyətim sizsiniz, gözəl insanlar.', dict(hi=['Məşğuliyyətim', 'sizsiniz,'])),
    ('P', 43.62, 46.90, 'Hər səhər bu yolu gedəndə, hər gün sizə qulaq atıram.', {}),
    ('R', 51.38, 52.90, 'Gördün, gördün?', {}),
    ('R', 61.52, 64.88, 'Neçə dəqiqədir tıxacdasınız, Bəhruz qardaş?', dict(hi=['tıxacdasınız,'])),
    ('R', 98.52, 100.22, 'Uçan Tesla lazımdır sizə.', dict(big=True, hi=['TESLA'])),
    ('P', 100.42, 100.80, 'Hı?', {}),
    ('R', 101.10, 102.60, 'Uçan Tesla lazımdır!', dict(big=True, hi=['TESLA'])),
    ('P', 106.10, 107.00, 'Mən o uçan maşınlardan qorxuram...', dict(hi=['qorxuram...'])),
    ('R', 108.96, 115.76, 'Qardaş, siz qohumlarla bağlı nə deyə bilərsiniz? İndi qohumlarla dost olmaq mümkündürmü, yoxsa yox?', dict(hi=['dost'])),
    ('P', 131.38, 139.70, 'Bu, hamısına şamil deyil. Haradasa sizə deyim ki, 50-60%-inə aiddir, 40%-i mənim canım-ciyərimdir.', dict(hi=['40%-i', 'canım-ciyərimdir.'])),
    ('R', 204.88, 207.94, 'Yox, 40%-i nə saxlamışsınız ki?', dict(hi=['40%-i'])),
    ('P', 212.70, 219.88, 'Yəni onlardan çox-çox az-az ünsiyyət qurduğum insanlar olub. Amma həmişə bir-birimizə can deyib, can eşitmişik.', dict(hi=['can'])),
    ('R', 220.20, 220.76, 'Can?', dict(big=True)),
    ('R', 220.84, 224.24, 'Yəni, Bəhruz... Bəhruz can!', dict(hi=['can!'])),
    ('R', 226.44, 229.60, 'Eşitmədim mən canı. Görürsən, mən sənə can deyirəm, amma can eşitmirəm.', dict(hi=['eşitmirəm.'])),
    ('R', 233.84, 240.20, 'Bəhruz can, yavaş-yavaş qohumluq əlaqələrini biz yaradırıq.', dict(hi=['qohumluq'])),
    ('R', 249.84, 253.74, 'Siz qohumlara gedəndə yerimi vermədilər sizə, yoxsa deyirlər nə vaxt gedirsiniz?', dict(hi=['nə', 'vaxt', 'gedirsiniz?'])),
    ('P', 254.14, 255.12, 'Evdən qovdular.', dict(hi=['qovdular.'])),
    ('R', 255.28, 256.30, 'Evdən qovdular!', dict(big=True, hi=['QOVDULAR!'])),
    ('P', 285.20, 290.60, 'Valla, bizim bir sözümüz var: uzaq qohum yaxşıdır, yoxsa yaxın qonşu?', dict(hi=['yaxın', 'qonşu?'])),
    ('P', 290.70, 293.60, 'Valla, mən Kürdəxanada yaşayıram, bir dənə qonşum var.', dict(hi=['qonşum'])),
    ('P', 293.78, 299.70, 'O 60%-də olan qohumların heç birinə dəyişmirəm o insanı. Elə gözəl insandır, elə can yandırır.', dict(hi=['dəyişmirəm'])),
    ('R', 303.82, 305.60, 'Bizim də yaxın qonşumuz var da.', dict(hi=['qonşumuz'])),
    ('P', 306.36, 307.80, 'Bir dənə qonşum var.', {}),
    ('R', 309.28, 311.50, 'Bizdə də bir dənədir, bizdə OBA-dır.', dict(big=True, hi=['OBA-DIR.'])),
    ('R', 311.60, 313.30, 'Yaxın qonşumuz da OBA-dır.', dict(hi=['OBA-dır.'])),
    ('R', 314.00, 315.10, 'O, bizdə də var.', {}),
    ('R', 365.96, 367.20, 'Neçə yaşınız var, Bəhruz qardaş?', {}),
    ('P', 367.42, 368.60, '33 yaşım var.', {}),
    ('R', 368.72, 375.20, 'Bundan sonra bərk-bərk yapışın o Kürdəxanadakı qonşunuzdan, bir də bərk-bərk yapışın OBA-mızdan, tamammı?', dict(hi=['OBA-mızdan,'])),
    ('R', 395.67, 398.75, 'Yox, sağollaşmamışdan əvvəl öpdün, yoxsa sağollaşdın, sonra öpdün?', dict(hi=['öpdün,', 'öpdün?'])),
    ('P', 398.85, 402.11, 'Yox, uzaqdan-uzağa öpürəm səni, dedim.', dict(hi=['uzaqdan-uzağa'])),
    ('P', 404.40, 409.57, 'Biri var şirin öpüş deyirlər, sevdiyinə. Biri var kinayəli öpüş deyirlər.', dict(hi=['şirin', 'kinayəli'])),
    ('R', 409.77, 413.19, 'Ay Allah, şirin öpüş, şirin öpüş...', dict(hi=['şirin'])),
    ('R', 413.70, 414.95, 'Yanağından elə marçıldadır ki...', dict(hi=['marçıldadır'])),
    ('R', 420.70, 422.60, 'Sağ olun, Bəhruz, biz də sizi öpürük!', dict(hi=['öpürük!'])),
    ('R', 426.90, 428.50, 'Öpüş-öpüşə qaldıq, səhər-səhər!', dict(big=True, hi=['ÖPÜŞ-ÖPÜŞƏ'])),
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
    lab('BƏHRUZ BƏY', o(0.05, 'greet'), o(3.45, 'greet'), 540, 1480, 54, emoji='1f4de')
    em('1f697', o(21.50, 'road'), o(26.85, 'road'), 950, 330, 130)
    em('1f6a6', o(22.50, 'road'), o(26.85, 'road'), 120, 330, 130)
    em('1f3b2', o(38.40, 'nard'), o(39.40, 'nard'), 880, 420, 190)
    em('2764', o(41.40, 'nard2'), o(43.30, 'nard2'), 950, 330, 130)
    em('1f3a7', o(44.30, 'nard2'), o(47.00, 'nard2'), 120, 330, 130)
    em('1f697', o(61.80, 'q1'), o(64.95, 'q1'), 170, 1200, 160)
    em('1f680', o(98.60, 'tesla'), o(102.65, 'tesla'), 880, 420, 190)
    em('2753', o(100.42, 'tesla'), o(101.10, 'tesla'), 170, 1200, 150)
    em('1f631', o(104.30, 'fear'), o(108.85, 'fear'), 950, 330, 130)
    lab('MÖVZU: QOHUMLARLA DOST\nOLMAQ MÜMKÜNDÜR?', o(109.70, 'topic'), o(115.85, 'topic'), 540, 1765, 54, emoji='1f914')
    em('1f494', o(135.20, 'pct'), o(137.20, 'pct'), 950, 330, 130)
    em('2764', o(137.30, 'pct'), o(139.75, 'pct'), 950, 330, 130)
    em('1f442', o(220.20, 'can2'), o(222.40, 'can2'), 170, 1200, 160)
    em('1f997', o(224.30, 'can2'), o(226.30, 'can2'), 880, 1200, 160)
    em('1f612', o(228.70, 'can3'), o(233.80, 'can3'), 880, 420, 180)
    em('1f91d', o(236.00, 'can3'), o(241.20, 'can3'), 880, 420, 170)
    em('1f6cf', o(250.90, 'yer'), o(252.80, 'yer'), 170, 420, 150)
    em('1f6aa', o(254.15, 'yer2'), o(256.35, 'yer2'), 880, 420, 190)
    lab('UZAQ QOHUM < YAXIN QONŞU', o(287.60, 'nb1'), o(290.60, 'nb1'), 540, 1530, 40)
    em('1f3e1', o(291.20, 'nb1'), o(293.60, 'nb1'), 950, 330, 130)
    em('1f60d', o(297.40, 'nb1'), o(299.70, 'nb1'), 120, 330, 130)
    em('1f914', o(303.90, 'nb2'), o(306.20, 'nb2'), 880, 420, 160)
    em('1f6d2', o(310.20, 'oba'), o(313.70, 'oba'), 880, 420, 200)
    lab('OBA', o(310.95, 'oba'), o(313.70, 'oba'), 300, 1080, 64, accent=OBA_Y, emoji='1f6d2')
    em('1f923', o(313.80, 'obalaf'), o(318.20, 'obalaf'), 170, 430, 190)
    em('1f602', o(314.30, 'obalaf'), o(318.20, 'obalaf'), 170, 1200, 180)
    em('1f382', o(367.42, 'grip'), o(368.68, 'grip'), 880, 420, 150)
    em('1f6d2', o(373.10, 'grip'), o(375.30, 'grip'), 880, 420, 190)
    lab('OBA', o(373.60, 'grip'), o(375.30, 'grip'), 300, 1500, 64, accent=OBA_Y, emoji='1f6d2')
    em('1f48b', o(395.80, 'kiss1'), o(398.80, 'kiss1'), 880, 420, 170)
    em('1f618', o(399.00, 'kiss2'), o(402.20, 'kiss2'), 950, 330, 130)
    em('1f36c', o(405.20, 'kiss2'), o(407.80, 'kiss2'), 120, 330, 130)
    em('1f60f', o(408.40, 'kiss2'), o(409.65, 'kiss2'), 950, 330, 130)
    em('1f60d', o(410.70, 'kiss3'), o(413.30, 'kiss3'), 880, 420, 180)
    em('1f4a5', o(413.70, 'kiss3'), o(415.00, 'kiss3'), 880, 420, 180)
    em('1f48b', o(426.90, 'end2'), o(428.60, 'end2'), 880, 420, 180)
    em('1f618', o(427.10, 'end2'), o(428.60, 'end2'), 170, 1200, 170)
    G.extend(GAG_EXTRA)
    return G

GAG_EXTRA = []

MUSIC_LEVEL = 0.12
def MUSIC_AUTOMATION(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        (o(224.25, 'can2'), o(226.30, 'can2'), 0.0),          # awkward silence waiting for "can"
        (o(252.70, 'yer'), o(252.80, 'yer'), 0.0),
        (o(308.60, 'nb3'), o(309.25, 'nb3'), 0.0),
        (o(309.25, 'oba'), o(313.70, 'oba'), 0.0),           # silence for the OBA punchline
        (o(313.70, 'obalaf'), o(318.20, 'obalaf'), 0.20),
        (o(285.10, 'nb1'), o(299.70, 'nb1'), 0.09),
        (o(398.80, 'kiss2'), o(409.65, 'kiss2'), 0.09),
    ]

def SFX(s2o):
    o = lambda t, c=None: _o(s2o, t, c)
    return [
        ('whoosh', o(0.05, 'greet'), 0.10), ('pop', o(38.40, 'nard'), 0.08), ('sparkle', o(98.60, 'tesla'), 0.08),
        ('pop', o(109.70, 'topic'), 0.06), ('tick', o(224.40, 'can2'), 0.10), ('tick', o(225.20, 'can2'), 0.10),
        ('pop', o(254.15, 'yer2'), 0.08), ('whoosh', o(310.20, 'oba'), 0.09), ('sparkle', o(310.95, 'oba'), 0.09),
        ('pop', o(373.60, 'grip'), 0.07), ('pop', o(395.80, 'kiss1'), 0.06), ('sparkle', o(426.90, 'end2'), 0.09),
    ]
