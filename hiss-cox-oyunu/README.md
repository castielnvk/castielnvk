# Hiss — «… çox ?» söz oyunu (sosial media montajı)

- `Hiss_cox_oyunu_v4.mp4`: final montaj (v4). 1080×1920, 30 fps, H.264 High + AAC 192 kbps, 89.1 san, −14 LUFS. Rəng orijinal HLG-dən çevrilib (`scripts/mklut.py`, `grade.cube`); parça təmizləmə `scripts/fx.py`.
- `Hiss_cox_oyunu.az.srt`: Azərbaycan dilində altyazılar və cavab yazıları (hazır videoda onsuz da var; bu fayl ayrıca istifadə üçündür).
- `project/hyperframes/`: redaktə edilə bilən HyperFrames kompozisiyası. Kartlar, altyazılar, cavab ştampları və zoom-lar burada qurulub. Video kəsimi `base.mp4` faylındadır.
  Yenidən render: `npx hyperframes@0.9.19 render project/hyperframes -q delivery --sdr`
- `project/scripts/`: kəsim siyahısı (`segs.py`), HDR→SDR kəsim (`base.py`), qrafika generatoru (`gen.py` + `template.html`), səs miksi (`audio.py`).
- `project/audio-stems/`: dialoq, musiqi və effektlər ayrı-ayrı (FLAC).

Musiqi: "Wallpaper", Kevin MacLeod (incompetech.com).
Licensed under Creative Commons: By Attribution 4.0 — http://creativecommons.org/licenses/by/4.0/
(Paylaşanda bu krediti post mətninə əlavə edin.)
Səs effektləri kodla sintez olunub.
