"""Writes the ASS caption/title track (output timeline). Text verified against Whisper large-v3
word timings of the original audio and corrected for Azerbaijani orthography."""
import sys

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H64000000,&H8C000000,0,0,0,0,100,100,0.5,0,1,2.4,1.5,2,64,64,370,1
Style: Speaker,Inter SemiBold,28,&H00B8E2F6,&H00FFFFFF,&H40000000,&H00000000,0,0,0,0,100,100,5,0,1,2.2,0.8,2,90,90,520,1
Style: Name,Noto Serif Display,70,&H00FFFFFF,&H00FFFFFF,&H50000000,&H00000000,0,0,0,0,100,100,1,0,1,1.6,1.2,1,96,96,560,1
Style: NameSub,Inter SemiBold,28,&H00E6EEF3,&H00FFFFFF,&H48000000,&H00000000,0,0,0,0,100,100,3,0,1,2,0.8,1,98,96,520,1
Style: Quote,Noto Serif Display,74,&H00FFFFFF,&H00FFFFFF,&H6E000000,&H00000000,0,1,0,0,100,100,0.5,0,1,2,2,8,90,90,250,1
Style: Accent,Inter Medium,30,&H00EAF4FA,&H00FFFFFF,&H78000000,&H00000000,0,0,0,0,100,100,7,0,1,1.4,0.8,8,90,90,270,1
Style: Big,Noto Serif Display,150,&H00FFFFFF,&H00FFFFFF,&H6E000000,&H00000000,0,0,0,0,100,100,4,0,1,2,2.5,8,90,90,200,1
Style: Title,Noto Serif Display,124,&H00FFFFFF,&H00FFFFFF,&H5A101010,&H00000000,1,0,0,0,100,100,10,0,1,2,3,5,60,60,0,1
Style: TitleSub,Inter Medium,32,&H00FFFFFF,&H00FFFFFF,&H5A101010,&H00000000,0,0,0,0,100,100,12,0,1,1.4,1.5,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
def add(st, en, style, text, layer=0):
    ev.append(f"Dialogue: {layer},{ts(st)},{ts(en)},{style},,0,0,0,,{text}")

FADE = r"{\fad(160,160)}"
# ---- President (audio over Elnarə listening) ----
pres = [
    (1.40, 3.30, "Yumruq göstərmişdim düşmənə."),
    (3.45, 8.20, "Demişdim ki, bu yumruq elə-belə yumruq deyil,\\Nbu dəmir yumruqdur."),
    (8.30, 11.50, "Bu dəmir yumruqla düşmənin başını əzirik"),
    (11.55, 15.05, "və eyni zamanda bu yumruq\\Nbirliyimizin rəmzi."),
    (15.10, 19.20, "Bax, bu gün Azərbaycan xalqı bu yumruq kimi\\Nbirləşir və həmişə belə olacaq."),
    (19.25, 20.95, "Bu birlik əbədi olacaq."),
    (21.10, 26.80, "Bütün Azərbaycan xalqını Zəfər Günü\\Nmünasibətilə ürəkdən təbrik edirəm."),
    (26.85, 30.20, "Eşq olsun Azərbaycan Silahlı Qüvvələrinə!"),
    (30.30, 33.40, "Qarabağ Azərbaycandır!"),
]
for st, en, tx in pres: add(st, en, "Sub", FADE + tx)
add(1.40, 8.20, "Speaker", r"{\fad(300,300)}PREZİDENT İLHAM ƏLİYEV")

# ---- Elnarə: introduction (protected opening) ----
eln_open = [
    (35.55, 39.65, "Bəli, 6 il bundan əvvəl elə\\N«Qarabağ Azərbaycandır!» deyib,"),
    (39.70, 44.00, "bütün ordu, dövlət, xalq həmrəyliyi ilə"),
    (44.05, 48.35, "biz bu yola çıxdıq —\\Nvətənin azadlığı uğrunda."),
    (48.40, 52.85, "El bir olarsa, basılmaz vətən deyib,"),
    (52.90, 59.35, "həm ön, həm arxa cəbhədə hər birimizin ürəyi\\Nelə məhz vətən naminə döyündü."),
]
for st, en, tx in eln_open: add(st, en, "Sub", FADE + tx)
# name super, kept above the subtitle zone and away from her face
add(36.2, 41.6, "Name", r"{\fad(450,400)\blur0.6}Elnarə")
add(36.4, 41.6, "NameSub", r"{\fad(500,400)}«QƏBUL VAXTI» APARICISI")

# ---- Title break (no speech) ----
add(59.70, 61.75, "Title", r"{\an5\pos(540,1440)\fad(450,350)\blur0.8\t(0,2050,\fscx104\fscy104)}ZƏFƏR GÜNÜ")

# ---- Body (OT = src + 2.4) ----
o = 2.4
body = [
    (60.00, 64.00, "Biz döyüşdə, ön cəbhədə\\Nigid oğullarımızın qəhrəmanlığı"),
    (64.02, 68.55, "hər gün yeni-yeni qalibiyyət xəbərlərini\\Nbizə eşitdirirdi."),
    (68.65, 72.20, "Arxa cəbhədə isə\\Nhər bir Azərbaycan vətəndaşı,"),
    (72.22, 75.15, "damarında Azərbaycan qanı axan\\Nhər bir insan"),
    (75.18, 79.65, "öz işində vətənpərvərliyini\\Nnümayiş etdirdi,"),
    (79.70, 81.55, "həmrəyliyini nümayiş etdirdi."),
    (81.60, 86.50, "Bəlkə də biz dekabrın 31-i hər il\\NHəmrəylik Gününü qeyd etsək də belə,"),
    (86.52, 90.90, "amma 6 il bundan əvvəl həmrəyliyin\\Nsözün əsl mənasında —"),
    (90.92, 95.45, "sözün öz hərfi yox, əsl mənasında —\\Nnə olduğunu"),
    (95.48, 99.85, "biz məhz hərəkətdə, reallıqda,\\Nhəqiqətdə"),
    (99.87, 103.63, "onu nümayiş etdirdik,\\Nhiss etdik və gördük."),
]
for st, en, tx in body: add(st + o, en + o, "Sub", FADE + tx)
add(83.0 + o, 88.6 + o, "Accent", r"{\fad(500,500)}31 DEKABR  ·  HƏMRƏYLİK GÜNÜ")

# ---- Final passage (OT = src - 0.4667) ----
o2 = -0.4667
fin = [
    (106.55, 109.78, "Və elə onun da nəticəsidir ki,"),
    (109.82, 113.70, "vətən uğrunda 44 gün davam edən,"),
    (113.75, 117.95, "torpaqlarımızın azadlığı uğrunda\\Ndavam edən"),
]
for st, en, tx in fin: add(st + o2, en + o2, "Sub", FADE + tx)
add(111.9 + o2, 115.4 + o2, "Big", r"{\fad(400,450)\blur0.6\t(0,3500,\fscx106\fscy106)}44 GÜN")
# closing line as a larger quote treatment (replaces the subtitle for this line)
add(118.0 + o2, 123.0, "Quote", r"{\fad(350,700)\blur0.5}«...qəhrəmanlıq zəfərlə\N yekunlaşdı.»")

# ---- End card ----
add(122.2, 127.6, "Title", r"{\an5\pos(540,1430)\fad(800,1100)\blur0.8\t(0,5400,\fscx105\fscy105)}ZƏFƏR GÜNÜ")
add(122.9, 127.6, "TitleSub", r"{\an5\pos(540,1560)\fad(700,1100)}8 NOYABR")
add(123.6, 127.6, "TitleSub", r"{\an5\pos(540,1690)\fs26\fad(700,1100)\alpha&H30&}«QƏBUL VAXTI»  ·  ARAZ FM 103.3")

open(sys.argv[1], "w", encoding="utf-8").write(HEAD + "\n".join(ev) + "\n")
print(len(ev), "events")
