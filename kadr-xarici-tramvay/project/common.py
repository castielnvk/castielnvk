import subprocess, numpy as np
FPS = 24; W, H = 1080, 1920
OFF = 0.15
DUR = 102.5
def _c(s):
    out = []
    for tok in s.split():
        w, t = tok.rsplit('@', 1); hl = w.startswith('*')
        out.append([w.lstrip('*').replace('_', ' '), float(t), hl])
    return out
CHUNKS = [_c(x) for x in [
 "Bir@0.02 vaxtlar@0.2 Bakıda@0.66",
 "*117@1.24 *kilometrlik@1.9",
 "tramvay@2.76 şəbəkəsi@3.24 var@3.8 idi.@3.92",
 "Bu@4.75 gün@4.95 isə@5.1 həmin@5.67",
 "tramvaylardan@6.0 küçələrdə@6.6",
 "*əsər-əlamət@7.36 qalmayıb.@8.2",
 "Bəs@9.43 Bakının@9.62 *80@10.06 *illik@10.44",
 "tramvay@10.98 tarixi@11.44",
 "necə@12.0 sona@12.42 çatdı?@12.72",
 "Hekayə@13.76 *1924-cü@14.16 il@15.72",
 "*fevralın@15.9 *8-də@16.46 başlayır.@17.04",
 "Həmin@18.18 gün@18.4 Bakıda@19.02",
 "ilk@19.3 *elektrik@19.58 *tramvayı@20.22",
 "hərəkətə@20.66 keçdi.@21.12",
 "Onun@22.1 ilk@22.3 marşrutu@22.55",
 "*Dəmiryol@23.64 *Vağzalından@24.02",
 "*Azneft@24.58 *meydanına@25.32",
 "qədər@25.82 uzanırdı.@26.12",
 "İllər@27.35 keçdikcə@27.75",
 "tramvaylar@28.34 Bakı@29.08 həyatının@29.46",
 "ayrılmaz@29.92 hissəsinə@30.64 çevrildi.@31.18",
 "İnsanlar@32.26 işə,@32.8 məktəbə,@33.3",
 "evlərinə@34.52 bu@35.0 vaqonlarla@35.16 gedirdilər.@35.72",
 "*1939-cu@36.96 ildə@38.4",
 "tramvay@39.1 şəbəkəsinin@39.4 uzunluğu@39.96",
 "artıq@40.6 *117@41.06 *kilometrə@41.74 çatmışdı.@42.32",
 "Amma@43.52 zamanla@43.9",
 "hər@44.7 şey@45.2 dəyişməyə@45.38 başladı.@45.94",
 "*1960-cı@47.11 illərdən@48.24 etibarən@48.72",
 "avtobusların,@49.7",
 "trolleybusların@50.64 və@51.54 metronun@52.02",
 "inkişafı@52.5 ilə@53.1",
 "tramvay@53.74 xətləri@54.05",
 "tədricən@54.48 azaldıldı.@55.18",
 "*1990-cı@56.48 illərdə@57.56 isə@58.04",
 "köhnəlmiş@58.76 vaqonlar@59.2 və@59.82",
 "dəyişən@60.08 nəqliyyat@60.56 sistemi@61.06",
 "tramvayların@62.03 fəaliyyətini@62.5",
 "daha@63.22 da@63.54 məhdudlaşdırdı.@63.7",
 "Nəhayət,@65.26 *2004-cü@65.82 ildə@66.9",
 "Xətai@67.36 metrosu@67.84 ilə@68.42",
 "Montin@68.64 bazarı@69.1 arasındakı@69.48",
 "*sonuncu@70.04 *xətt@70.62 də@70.9 bağlandı.@71.1",
 "Beləcə,@72.29 onilliklər@72.8 boyu@73.58",
 "Bakı@73.92 küçələrində@74.34 eşidilən@75.0",
 "*tramvay@75.46 *zəngləri@76.0 susdu.@76.46",
 "Onların@77.5 yerini@77.8 başqa@78.14",
 "nəqliyyat@78.68 vasitələri@79.08 aldı.@79.66",
 "Amma@80.53 köhnə@80.8 fotolarda,@81.34",
 "küçələrin@82.1 tarixində@82.84",
 "və@84.12 onları@84.22 xatırlayan@84.48",
 "insanların@85.12 yaddaşında@85.74",
 "tramvaylar@86.93 hələ@87.44 də@87.82 yaşayır.@88.04",
 "Bir@89.16 vaxtlar@89.35 Bakının@89.68",
 "gündəlik@90.3 həyatının@90.92",
 "ayrılmaz@91.46 hissəsi@92.22 olan@92.76",
 "bu@92.9 vaqonların@93.14 hekayəsi@93.66 isə…@94.34",
 "kadr@95.44 xaricində@95.72 qaldı.@96.44",
]]
PAUSES = [(4.21,4.75),(5.33,5.67),(8.72,9.43),(13.18,13.76),(17.71,18.18),(18.67,19.02),(21.62,22.10),(23.29,23.64),(26.73,27.35),(31.78,32.26),(34.22,34.52),(36.43,36.96),(38.80,39.10),(42.95,43.52),(46.55,47.11),(49.38,49.70),(53.40,53.74),(55.97,56.48),(58.39,58.76),(61.67,62.03),(64.66,65.26),(71.71,72.29),(77.02,77.50),(80.04,80.53),(83.76,84.12),(86.55,86.93),(88.59,89.16),(94.90,95.44),(96.84,97.14)]
CHUNK_END = []
for i, ch in enumerate(CHUNKS):
    nxt = CHUNKS[i + 1][0][1] if i + 1 < len(CHUNKS) else 96.84
    e = nxt
    for a, b in PAUSES:
        if ch[-1][1] < a < nxt + .01: e = a; break
    CHUNK_END.append(round(e, 2))
def load_audio(path, sr=48000, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, ch).copy() if ch > 1 else a.copy()
