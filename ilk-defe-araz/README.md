# «İlk dəfə "Araz"da dinlə» — premyera Reels şablonu (v3, cinematic)

Araz Radio 103.3 FM-in eksklüziv mahnı premyeraları üçün 9:16 Reel şablonu.

## Qəti qaydalar (istifadəçinin sözləri ilə)

- **Mətnlər yalnız orijinal promodakı kimidir, heç nə əlavə edilmir və dəyişdirilmir:**
  `TARİX` (məs. 2 NOYABR) · `11:00 – 12:00` · `İLK DƏFƏ` · `“ARAZ”DA` · `DİNLƏ` + Araz loqosu
  aşağıda ortada. Müğənni adı, mahnı adı, «təqdim edir», «premyera» kimi öz mətnlərini YAZMA.
- Saat və yazılar hər dəfə eynidir; yalnız tarix dəyişir.
- Video **18 saniyə**dir (səs yazısının ilk 18 s-i, sonda 0.5 s fade).
- Hər AI videodan **fərqli kəsitlər** istifadə olunur, kəsimlər mahnının ritminə düşür.
- v2 (zərif qızılı serif, ad kartları, «təqdim edir») bəyənilmədi — qaytarma.

## İstifadəçi hər dəfə göndərir

1. Səs yazısı (MP3) — müğənni özünü təqdim edir, sonra mahnı başlayır.
2. Grok AI videoları (adətən 3 ədəd, 816×1104, 15 s).
3. Tarix.

## Dizayn (v3)

- Qara + kəhrəba kino işığı; köhnə şablonun narıncı diaqonal zolaqları indi **diaqonal işıq şüası**
  kimi keçid olur (mahnının girişi və ortada), finalda isti işıq partlayışı (bloom).
- Yazılar solda, kino afişası kimi: `İLK DƏFƏ` və `“ARAZ”DA` — **Big Shoulders Display 900**
  (hündür, sıx); tarix/saat/`DİNLƏ` — **Inter Tight**. Narıncı `#E86A33`: `DİNLƏ` və tarixin altındakı xətt.
- Animasiya (orijinal sıra və vaxta yaxın, ~3.8 s-dən sona qədər ekranda qalır):
  `İLK DƏFƏ` hərf-hərf yuxarı qalxır → `“ARAZ”DA` işıq kənarı ilə açılır, ağ-isti metal rəngə
  oturur, altından anamorfik işıq xətti keçir → `DİNLƏ` aralığı açılır → tarix və saat narıncı
  xəttin arxasından sürüşür. Sonra hər bitdə `“ARAZ”DA` üzərindən işıq keçir.
- Loqo: `logos/individual/araz-radio_white.png`, dəyişdirilmədən, aşağıda ortada (orijinal yer).

## Yeni epizod — addımlar

1. `episodes/<tarix>_<ifaçı>_<mahnı>/source/` qovluğuna MP3 və AI videolarını qoy.
2. Bitləri ölç (librosa `beat_track`); kəsimləri bitlərə qoy. Hər klipdən fərqli hissə seç
   (morf/ghost keçid kadrlarından qaç — kontakt vərəqlə yoxla).
3. Əvvəlki `config.json`-u köçür, dəyiş: `lockup.date`, `shots`, `flashes`, `beams`, `lockup.sweeps`.
   `lockup.time`, `l1`, `l2`, `l3` dəyişmir.
4. Önizləmə: `python3 render.py episodes/.../config.json --preview 4.1,6.5,12,17.5`
5. Tam render: `python3 render.py episodes/.../config.json` (≈1–2 dəqiqə).
6. Yoxla: kontakt vərəq, səs sinxronu, Ə/İ hərfləri, yazı ekrandan çıxmır, loqo.

Tələblər: `pip install playwright librosa`; Chromium `/opt/pw-browsers/chromium` (və ya `CHROME=`).

`shots`: `start` (çıxış saniyəsi), `clip`, `src` (klipdə başlanğıc), `z` [başlanğıc, son] miqyas
(1.0 = 1920 hündürlüyə doldurur; <1 olanda kənarlar qaraya əriyir), `cx`/`cy` fokus (0–1).

## Epizodlar

| Qovluq | Mahnı | Tarix | Nəticə |
|---|---|---|---|
| `episodes/2026-11-02_donge_son-qerar` | İradə İbrahimova & Döngə — «Son Qərar» | 2 Noyabr | `Donge_Son_Qerar_Ilk_Defe_Araz_9x16.mp4` (18 s, v3) |
