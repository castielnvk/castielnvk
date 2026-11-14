import subprocess, numpy as np, json
FPS = 24
W, H = 1080, 1920
OFF = 0.40          # voice-over starts at this video time
DUR = 85.0

# ---------- subtitle chunks: (word, vo_time, highlight) ----------
def _c(s):
    out = []
    for tok in s.split():
        w, t = tok.rsplit('@', 1)
        hl = w.startswith('*')
        out.append([w.lstrip('*').replace('_', ' '), float(t), hl])
    return out

CHUNKS = [_c(x) for x in [
 "Bakının@0.0 məşhur@0.44 *BUM@0.98 binasında@1.36",
 "100@1.88 ildən@2.54 çox@2.92 əvvəl@3.14",
 "*kinoteatr@3.54 olduğunu@4.15 bilirdiniz?@4.5",
 "Bu@5.44 binanın@6.04 tarixi@6.38",
 "*1896–@7.06 *1898-ci@8.32",
 "illərə@10.64 gedib@10.98 çıxır.@11.24",
 "Memar@11.72 *Kazimir@12.58 *Skureviçin@13.02",
 "layihəsi@13.74 əsasında@14.18 tikilən@14.74 bina@15.2",
 "Bakının@15.5 mühüm@16.16 ticarət@16.72",
 "məkanlarından@17.2 birinə@17.9 çevrilmişdi.@18.36",
 "*1903-cü@19.48 ildə@20.72 isə@20.96",
 "*Hacı@21.32 *Zeynalabdin@21.72 *Tağıyevin@22.36",
 "mülkiyyətinə@22.92 keçərək,@23.58",
 "*Tağıyev@24.12 *pasajı@24.78 kimi@25.22",
 "tanınmağa@25.42 başladı.@25.86",
 "Amma@26.32 bu@27.22 binanın@27.52",
 "ən@27.88 maraqlı@28.34 tərəfi@28.72",
 "təkcə@29.22 ticarətlə@29.74 bağlı@30.34 deyildi.@30.68",
 "*1907-ci@31.52 ildə@32.8 burada@33.14",
 "*“Fransız@33.5 *Elektro-Bioqraf”@34.46",
 "adlı@35.58 kinoteatr@35.98 açıldı.@36.56",
 "Həmin@37.12 dövrdə@37.68 kino@38.18",
 "hələ@38.56 yenilik@38.76 idi@39.12",
 "və@39.4 insanlar@39.86 hərəkətli@40.14 görüntüləri@41.1",
 "izləmək@41.76 üçün@42.18 buraya@42.42 gəlirdilər.@42.68",
 "Sonralar@43.52 kinoteatr@44.4",
 "*“Təyyarə”@45.14 adlandırıldı.@45.72",
 "Sovet@46.7 dövründə@47.26 isə@47.82 bina@48.14",
 "*“Köhnə@48.58 *univermaq”,@49.16",
 "yəni@49.94 *BUM@50.4 kimi@50.84 məşhurlaşdı.@51.18",
 "Pasajın@52.04 diqqətçəkən@52.82",
 "xüsusiyyətlərindən@53.52 biri@54.48",
 "içəriyə@54.7 gün@55.54 işığı@55.74 buraxan@56.1",
 "tarixi@56.58 *şüşə@57.2 *damı@57.54 idi.@57.84",
 "Lakin@58.14 sonrakı@58.72 təmir@59.26 işləri@59.58 zamanı@59.92",
 "bu@60.46 dam@60.7 *asma@60.9 *tavanla@61.36 örtüldü.@61.82",
 "Bu@62.46 gün@62.72 minlərlə@62.96 insan@63.78",
 "*BUM-un@64.04 qarşısından@64.54 keçir.@65.08",
 "Amma@65.66 çoxları@66.22 bilmir@66.6 ki,@66.96",
 "burada@67.22 bir@67.64 vaxtlar@67.88",
 "Bakı@68.36 kinosunun@68.82",
 "ilk@69.26 səhifələrindən@69.66 biri@70.58 yazılıb.@70.76",
 "İllər@71.4 keçdi,@72.2",
 "bina@72.78 dəyişdi.@73.34",
 "Amma@74.02 onun@74.72 unudulmuş@74.86 hekayəsi@75.58",
 "uzun@76.28 müddət…@77.02",
 "kadr@77.64 xaricində@78.36 qaldı.@79.02",
]]
CHUNK_END = [1.88,3.54,5.14,7.06,10.5,11.58,13.74,15.5,17.2,19.06,21.32,22.92,24.12,25.42,26.32,27.88,29.22,31.24,
             33.5,35.58,36.92,38.56,39.4,41.76,43.4,45.14,46.5,48.58,49.8,51.82,53.52,54.7,56.58,58.0,60.46,62.38,
             64.04,65.56,67.16,68.36,69.26,71.3,72.72,73.88,76.28,77.64,79.48]
assert len(CHUNK_END) == len(CHUNKS)

def load_audio(path, sr=48000, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, ch).copy() if ch > 1 else a.copy()

def snap_words(vo_path):
    """Move word starts that whisper placed inside silence forward to the real onset."""
    a = load_audio(vo_path, 16000, 1)
    n = 160
    env = np.sqrt((a[:len(a)//n*n].reshape(-1, n) ** 2).mean(1))
    env = np.convolve(env, np.ones(3)/3, 'same')
    thr = 10 ** (-36 / 20)
    for ch in CHUNKS:
        for w in ch:
            i = int(w[1] * 100); j = i
            while j < len(env) - 1 and env[j] < thr and j - i < 110:
                j += 1
            if j != i: w[1] = round(j / 100 - 0.02, 2)
    # final end of speech
    k = len(env) - 1
    while env[k] < thr: k -= 1
    return k / 100
