import subprocess, numpy as np
FPS = 24; W, H = 1080, 1920
OFF = 0.15
DUR = 92.2
def _c(s):
    out = []
    for tok in s.split():
        w, t = tok.rsplit('@', 1); hl = w.startswith('*')
        out.append([w.lstrip('*').replace('_', ' '), float(t), hl])
    return out
CHUNKS = [_c(x) for x in [
 "Bakının@0.0 mərkəzində@0.4",
 "elə@1.18 bir@1.56 tarixi@1.66 hamam@2.22 var@2.5 ki,@2.64",
 "bir@3.49 vaxtlar@3.62 burada@3.92",
 "həm@4.08 *dəbdəbə,@4.64",
 "həm@5.32 də@5.72 şəhər@5.88 həyatının@6.18",
 "xüsusi@6.66 bir@7.28 ritmi@7.42 vardı.@7.8",
 "Bu@8.98 gün@9.12 isə@9.3 həmin@9.55 bina@9.94",
 "*tərk@10.22 *edilmiş@10.56 vəziyyətdədir.@10.9",
 "Söhbət@12.22 *“Fantaziya”@12.62 hamamından@13.46 gedir.@13.94",
 "Bu@15.03 hamam@15.2 *XIX@15.5 *əsrin@15.9 *sonlarında@16.5",
 "fəaliyyətə@17.16 başlayıb@17.68",
 "və@18.56 Bakının@18.7 ilk@19.06",
 "*Avropa@19.46 *tipli@20.14 hamamlarından@20.44",
 "biri@21.02 sayılırdı.@21.3",
 "O@22.54 dövrdə@22.7 burada@23.02",
 "sadəcə@23.18 yuyunmaq@23.92 üçün@24.36 yox,@24.58",
 "istirahət@25.39 etmək,@25.88",
 "vaxt@26.44 keçirmək,@26.84",
 "hətta@28.0 müəyyən@28.26 mənada@28.74",
 "şəhər@29.18 həyatının@29.7",
 "bir@30.18 parçası@30.38 olmaq@30.88 üçün@31.24 gəlirdilər.@31.46",
 "Mənbələrə@32.63 görə,@33.08",
 "hamamda@33.38 *fəvvarəli@34.02 *zal,@34.76",
 "*dəbdəbəli@35.61 *interyer,@36.04",
 "*müalicəvi@37.22 *vannalar@37.64",
 "və@38.16 o@38.68 dövr@38.82 üçün@39.12",
 "kifayət@39.4 qədər@40.0 qeyri-adi@40.32",
 "görünən@40.86 şərait@41.32 vardı.@41.72",
 "Yəni@42.74 “Fantaziya”@42.98",
 "adi@43.76 hamam@44.38 deyildi.@44.68",
 "Bu,@45.74 köhnə@45.92 Bakının@46.4",
 "şəhər@46.74 *mədəniyyətini@47.2 göstərən@47.84",
 "məkanlardan@48.38 biri@48.86 idi.@49.2",
 "Sonrakı@50.10 illərdə@50.44 bina@51.02",
 "fəaliyyətini@51.22 davam@51.9 etdirsə@52.26 də,@52.68",
 "zamanla@52.94 əvvəlki@53.68",
 "*şöhrətini@54.26 *itirdi.@54.86",
 "*2012-ci@55.93 ildən@56.62 sonra@56.92 isə@57.18",
 "obyekt@57.6 tamamilə@58.22",
 "*istifadəsiz@59.0 *qaldı.@59.7",
 "Bu@60.66 gün@60.72 *tarixi@60.85 *abidə@61.52 statusu@61.92",
 "daşıyan@62.48 bina@62.86",
 "*baxımsız@63.24 və@64.08",
 "*yarıuçuq@64.32 vəziyyətdədir.@64.84",
 "Bir@66.18 vaxtlar@66.3",
 "*işıq,@66.72 *su,@67.46 *səs@68.06",
 "və@68.64 *insanlarla@68.78 dolu@69.44 olan@69.8",
 "bu@69.96 məkan@70.16",
 "indi@70.54 *səssizdir.@71.18",
 "“Fantaziya”@72.5 hamamının@72.94",
 "keçmiş@73.38 *dəbdəbəsi@73.94 ilə@74.54",
 "bugünkü@74.86 *tərk@75.32 *edilmiş@75.78 görünüşü@76.14",
 "arasındakı@76.7 fərq@77.26 isə,@77.62",
 "köhnə@78.38 Bakının@78.6 ən@78.98 maraqlı,@79.44",
 "amma@80.39 az@80.6 danışılan@80.84",
 "hekayələrindən@81.38 biridir.@82.24",
 "Və@83.41 uzun@83.55 müddət…@83.9",
 "kadr@84.91 xaricində@85.16 qaldı.@85.82",
]]
SKIP_SUBS = {28, 29}
PAUSES = [(3.13,3.49),(8.24,8.98),(11.70,12.22),(14.51,15.03),(18.22,18.56),(22.05,22.54),(25.04,25.39),(27.51,28.00),(32.13,32.63),(35.36,35.61),(36.86,37.22),(42.24,42.74),(45.24,45.74),(49.64,50.10),(55.40,55.93),(60.19,60.66),(65.70,66.18),(70.70,70.97),(71.88,72.50),(77.98,78.38),(80.09,80.39),(82.73,83.41),(84.48,84.91),(86.21,86.75)]
CHUNK_END = []
for i, ch in enumerate(CHUNKS):
    nxt = CHUNKS[i + 1][0][1] if i + 1 < len(CHUNKS) else 86.21
    e = nxt
    for a, b in PAUSES:
        if ch[-1][1] < a < nxt + .01: e = a; break
    CHUNK_END.append(round(e, 2))
def load_audio(path, sr=48000, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, ch).copy() if ch > 1 else a.copy()
