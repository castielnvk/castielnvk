"""Şamaxı zəlzələsi (1902) — no voice-over: the on-screen text is the narrator.
CHUNKS are text cards (start, end, text); words brighten at a reading pace."""
import subprocess, numpy as np
FPS = 24; W, H = 1080, 1920
OFF = 0.0
DUR = 50.0
CARDS = [
 (-0.3, 3.95, "1902-ci ildə Şamaxıdakı 5 min evdən *4 mini *dağıldı."),
 (4.05, 5.95, "*13 *fevral *1902-ci il. Saat *12:50."),
 (6.0, 8.95, "Şamaxıda güclü *zəlzələ baş verdi."),
 (9.05, 11.6, "Fəlakət Şamaxı ilə yanaşı,"),
 (11.65, 14.95, "ətrafdakı *125 *kəndə də təsir etdi."),
 (15.05, 17.4, "Tarixi *Cümə *məscidi, hamamlar,"),
 (17.45, 19.95, "məktəblər və mədrəsələr *dağıldı."),
 (20.05, 21.85, "Tarixi məlumatlara görə,"),
 (21.9, 23.95, "*2 *mindən *çox insan həlak oldu."),
 (24.05, 26.95, "*20 *minə *yaxın sakin evsiz qaldı."),
 (27.05, 30.2, "Qışın soyuğunda insanlar *çadırlara sığındı."),
 (30.3, 32.95, "Dağıntılar altında *xilasetmə işləri davam edirdi."),
 (33.05, 35.0, "Zəlzələdən *9 *gün sonra"),
 (35.05, 36.75, "*Ümmü adlı balaca qız"),
 (36.8, 38.95, "dağıntılardan *sağ *çıxarıldı."),
 (39.05, 41.9, "Bakıdan *ərzaq, *geyim və *çadırlar göndərildi."),
 (41.95, 44.95, "*Hacı *Zeynalabdin *Tağıyev də yardımın təşkilinə qoşuldu."),
 (45.05, 46.45, "Şamaxı yenidən quruldu."),
 (46.5, 47.85, "Amma bəzi insan hekayələri…"),
]
FINAL = [('kadr', 47.95), ('xaricində', 48.2), ('qaldı.', 48.5)]
CHUNKS, CHUNK_END = [], []
for a, b, txt in CARDS:
    ws = txt.split()
    CHUNKS.append([[w.lstrip('*'), max(a, 0) + .12 + i * .17 if a >= 0 else a + i * .0, w.startswith('*')] for i, w in enumerate(ws)])
    CHUNKS[-1][0][1] = a if a < 0 else CHUNKS[-1][0][1]
    CHUNK_END.append(b - .55)
CHUNKS.append([[w, t, False] for w, t in FINAL]); CHUNK_END.append(49.0)   # last entry is drawn as the ending, not as a card
SKIP_SUBS = set()
def load_audio(path, sr=48000, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, ch).copy() if ch > 1 else a.copy()
