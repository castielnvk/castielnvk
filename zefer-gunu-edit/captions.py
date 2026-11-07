"""Writes the ASS caption/title track (output timeline) for the 'Zəfər Günü' edit.

Text checked against Whisper large-v3 word timings of the original audio and corrected for
Azerbaijani orthography (ə, ı, İ, ö, ü, ş, ç, ğ). Cues are kept to <= 2 short lines for mobile.
Cinematic treatment: every caption is drawn twice - a soft blurred dark halo (layer 0) under crisp
bold text (layer 1) - with a gentle rise-in, and a warm gold accent on a few key words."""
import re, sys

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

GOLD = r"{\c&H7FD2F4&}"          # #F4D27F (BGR in ASS)
WHITE = r"{\c&HFFFFFF&}"

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter,58,&H00FFFFFF,&H00FFFFFF,&H50000000,&H00000000,1,0,0,0,100,100,0.3,0,1,2.2,0,2,40,40,0,1
Style: Halo,Inter,58,&HFF000000,&HFF000000,&H58000000,&H00000000,1,0,0,0,100,100,0.3,0,1,16,0,2,40,40,0,1
Style: Speaker,Inter SemiBold,32,&H0098D9F6,&H00FFFFFF,&H40000000,&H00000000,0,0,0,0,100,100,6,0,1,2.4,0,2,40,40,0,1
Style: Name,Noto Serif Display,92,&H00FFFFFF,&H00FFFFFF,&H48000000,&H00000000,0,0,0,0,100,100,1.5,0,1,2.2,0,7,0,0,0,1
Style: NameSub,Inter SemiBold,34,&H007FD2F4,&H00FFFFFF,&H40000000,&H00000000,0,0,0,0,100,100,5,0,1,2.2,0,7,0,0,0,1
Style: Quote,Noto Serif Display,96,&H00FFFFFF,&H00FFFFFF,&H48000000,&H00000000,0,1,0,0,100,100,0.5,0,1,2.4,0,8,60,60,0,1
Style: Accent,Inter SemiBold,38,&H00FFFFFF,&H00FFFFFF,&H40000000,&H00000000,0,0,0,0,100,100,8,0,1,2.4,0,8,40,40,0,1
Style: Big,Noto Serif Display,230,&H00FFFFFF,&H00FFFFFF,&H40000000,&H00000000,1,0,0,0,100,100,6,0,1,2.4,0,8,40,40,0,1
Style: Title,Noto Serif Display,150,&H00FFFFFF,&H00FFFFFF,&H40101010,&H00000000,1,0,0,0,100,100,8,0,1,2.4,0,5,30,30,0,1
Style: TitleSub,Inter SemiBold,40,&H00FFFFFF,&H00FFFFFF,&H40101010,&H00000000,0,0,0,0,100,100,14,0,1,2,0,5,30,30,0,1
Style: Rule,Inter,10,&H007FD2F4,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
def add(st, en, style, text, layer=0):
    ev.append(f"Dialogue: {layer},{ts(st)},{ts(en)},{style},,0,0,0,,{text}")

KEYS = ["Zəfər Günü", "Qarabağ Azərbaycandır!", "«Qarabağ Azərbaycandır!»", "dəmir yumruq", "birliyimizin",
        "əbədi", "həmrəyliyi", "vətən naminə", "igid oğullarımızın", "həmrəyliyini", "Həmrəylik Gününü",
        "əsl mənasında", "44 gün", "zəfərlə"]
def accent(text):
    for k in sorted(KEYS, key=len, reverse=True):
        if k in text:
            text = text.replace(k, GOLD + k + WHITE, 1); break       # one accent per cue at most
    return text

def halo(st, en, style, text, layer):
    add(st, en, style, text, layer + 1)
    add(st, en, style, re.sub(r"\\blur[0-9.]+", "", text).replace("}", r"\blur16\1a&HFF&\3c&H000000&\3a&H90&\bord12}", 1), layer)
SUB_Y = 1590                       # baseline of the subtitle block (mobile-safe, below faces)
def sub(st, en, text):
    a = r"{\an2\move(540,%d,540,%d,0,260)\fad(200,160)" % (SUB_Y + 14, SUB_Y)
    plain = re.sub(r"\{[^}]*\}", "", text)
    add(st, en, "Halo", a + r"\blur14}" + plain, 0)
    add(st, en, "Sub", a + r"\blur0.6}" + accent(text), 1)

# ---- President (audio over Elnarə listening) ----
pres = [
    (1.40, 3.30, "Yumruq göstərmişdim düşmənə."),
    (3.45, 6.75, "Demişdim ki, bu yumruq\\Nelə-belə yumruq deyil,"),
    (6.80, 8.25, "bu dəmir yumruqdur."),
    (8.30, 11.50, "Bu dəmir yumruqla\\Ndüşmənin başını əzirik"),
    (11.55, 15.05, "və eyni zamanda bu yumruq\\Nbirliyimizin rəmzi."),
    (15.10, 17.50, "Bax, bu gün Azərbaycan xalqı\\Nbu yumruq kimi birləşir"),
    (17.55, 19.20, "və həmişə belə olacaq."),
    (19.25, 20.95, "Bu birlik əbədi olacaq."),
    (21.10, 24.40, "Bütün Azərbaycan xalqını\\NZəfər Günü münasibətilə"),
    (24.45, 26.80, "ürəkdən təbrik edirəm."),
    (26.85, 30.20, "Eşq olsun Azərbaycan\\NSilahlı Qüvvələrinə!"),
    (30.30, 33.40, "Qarabağ Azərbaycandır!"),
]
for c in pres: sub(*c)
spk = r"{\an2\pos(540,1372)\fad(400,400)\blur0.5}PREZİDENT  İLHAM  ƏLİYEV"
halo(1.40, 8.25, "Speaker", spk, 2)
add(1.40, 8.25, "Rule", r"{\an7\pos(470,1388)\fad(400,400)\t(0,600,\fscx100)\fscx0\p1}m 0 0 l 140 0 140 3 0 3{\p0}", 2)

# ---- Elnarə: introduction (protected opening) ----
eln_open = [
    (35.55, 39.65, "Bəli, 6 il bundan əvvəl elə\\N«Qarabağ Azərbaycandır!» deyib,"),
    (39.70, 44.00, "bütün ordu, dövlət,\\Nxalq həmrəyliyi ilə"),
    (44.05, 46.40, "biz bu yola çıxdıq —"),
    (46.45, 48.35, "vətənin azadlığı uğrunda."),
    (48.40, 52.85, "El bir olarsa, basılmaz\\Nvətən deyib,"),
    (52.90, 55.35, "həm ön, həm arxa cəbhədə"),
    (55.38, 59.35, "hər birimizin ürəyi elə məhz\\Nvətən naminə döyündü."),
]
for c in eln_open: sub(*c)
# name super: lower-left, just above the subtitle zone, with a soft halo for legibility
add(36.1, 42.0, "Rule", r"{\an7\pos(72,1196)\fad(300,400)\t(0,700,\fscx100)\fscx0\p1}m 0 0 l 110 0 110 4 0 4{\p0}", 4)
halo(36.3, 42.0, "Name", r"{\an7\move(60,1214,72,1214,0,900)\fad(500,450)\blur0.6}Elnarə Sadıqova", 2)
halo(36.6, 42.0, "NameSub", r"{\an7\pos(76,1328)\fad(600,450)\blur0.4}«QƏBUL VAXTI» APARICISI", 2)

# ---- Title break (no speech) ----
add(59.65, 61.80, "Title", r"{\an5\pos(540,1440)\fad(450,350)\blur0.8\fsp2\t(0,2100,\fsp14)}ZƏFƏR GÜNÜ", 2)
add(59.65, 61.80, "Title", r"{\an5\pos(540,1440)\fad(450,350)\blur18\1a&HFF&\3c&H3FA6E8&\3a&H90&\bord10\fsp2\t(0,2100,\fsp14)}ZƏFƏR GÜNÜ", 1)
add(59.90, 61.80, "Rule", r"{\an7\pos(400,1532)\fad(400,350)\t(0,800,\fscx100)\fscx0\p1}m 0 0 l 280 0 280 3 0 3{\p0}", 2)

# ---- Body (OT = src + 2.4) ----
o = 2.4
body = [
    (60.00, 64.00, "Biz döyüşdə, ön cəbhədə\\Nigid oğullarımızın qəhrəmanlığı"),
    (64.02, 66.85, "hər gün yeni-yeni\\Nqalibiyyət xəbərlərini"),
    (66.90, 68.55, "bizə eşitdirirdi."),
    (68.65, 72.20, "Arxa cəbhədə isə\\Nhər bir Azərbaycan vətəndaşı,"),
    (72.22, 75.15, "damarında Azərbaycan qanı axan\\Nhər bir insan"),
    (75.18, 79.65, "öz işində vətənpərvərliyini\\Nnümayiş etdirdi,"),
    (79.70, 81.55, "həmrəyliyini nümayiş etdirdi."),
    (81.60, 84.50, "Bəlkə də biz dekabrın 31-i"),
    (84.52, 86.50, "hər il Həmrəylik Gününü\\Nqeyd etsək də belə,"),
    (86.52, 88.25, "amma 6 il bundan əvvəl"),
    (88.30, 90.90, "həmrəyliyin\\Nsözün əsl mənasında —"),
    (90.92, 93.35, "sözün öz hərfi yox,"),
    (93.40, 95.45, "əsl mənasında —\\Nnə olduğunu"),
    (95.48, 99.85, "biz məhz hərəkətdə,\\Nreallıqda, həqiqətdə"),
    (99.87, 103.63, "onu nümayiş etdirdik,\\Nhiss etdik və gördük."),
]
for st, en, tx in body: sub(st + o, en + o, tx)
halo(83.0 + o, 88.6 + o, "Accent", r"{\an8\pos(540,230)\fad(500,500)\blur0.5\fs64\fsp10}31 DEKABR", 2)
halo(83.2 + o, 88.6 + o, "Accent", r"{\an8\pos(540,318)\fad(600,500)\blur0.5\c&H7FD2F4&\fs42}HƏMRƏYLİK GÜNÜ", 2)

# ---- Final passage (OT = src - 0.4667) ----
o2 = -0.4667
fin = [
    (106.55, 109.78, "Və elə onun da nəticəsidir ki,"),
    (109.82, 113.70, "vətən uğrunda\\N44 gün davam edən,"),
    (113.75, 117.95, "torpaqlarımızın azadlığı\\Nuğrunda davam edən"),
]
for st, en, tx in fin: sub(st + o2, en + o2, tx)
big = r"{\an8\pos(540,150)\fad(400,450)\blur0.6\t(0,3500,\fscx106\fscy106)}44 GÜN"
add(111.9 + o2, 115.4 + o2, "Big", big, 2)
add(111.9 + o2, 115.4 + o2, "Big", big.replace(r"\blur0.6", r"\blur20\1a&HFF&\3c&H000000&\3a&HA0&\bord14"), 1)
# closing line as a larger quote treatment (replaces the subtitle for this line)
q = r"{\an8\pos(540,190)\fad(350,700)\blur0.5}«...qəhrəmanlıq" + GOLD + r" zəfərlə" + WHITE + r"\Nyekunlaşdı.»"
add(118.0 + o2, 123.0, "Quote", q, 2)
add(118.0 + o2, 123.0, "Quote", re.sub(r"\{\\c[^}]*\}", "", q).replace(r"\blur0.5", r"\blur18\1a&HFF&\3c&H000000&\3a&HA0&\bord12"), 1)

# ---- End card ----
add(122.2, 127.6, "Title", r"{\an5\pos(540,1420)\fad(800,1100)\blur0.8\fsp4\t(0,5400,\fsp12)}ZƏFƏR GÜNÜ", 2)
add(122.2, 127.6, "Title", r"{\an5\pos(540,1420)\fad(800,1100)\blur18\1a&HFF&\3c&H3FA6E8&\3a&H90&\bord10\fsp4\t(0,5400,\fsp12)}ZƏFƏR GÜNÜ", 1)
add(122.6, 127.6, "Rule", r"{\an7\pos(400,1512)\fad(600,1100)\t(0,900,\fscx100)\fscx0\p1}m 0 0 l 280 0 280 3 0 3{\p0}", 2)
add(122.9, 127.6, "TitleSub", r"{\an5\pos(540,1572)\fad(700,1100)}8 NOYABR", 2)
add(123.6, 127.6, "TitleSub", r"{\an5\pos(540,1700)\fs30\fad(700,1100)\alpha&H20&}«QƏBUL VAXTI»  ·  ARAZ FM 103.3", 2)

open(sys.argv[1], "w", encoding="utf-8").write(HEAD + "\n".join(ev) + "\n")
print(len(ev), "events")
