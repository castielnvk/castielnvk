# «İlk dəfə "Araz"da dinlə» — premyera Reels şablonu (v5 — motion design, Araz teal)

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

## Diza## Dizayn (v5) — motion design, Araz rəngi

- Rədd edilənlər: v2 (qızılı serif, uydurma mətnlər), v3 (Big Shoulders, «cringy»), v4 (orijinalın
  diaqonal qutusunun kopyası, «motion design 0»).
- **Rəng:** Araz Radio teal **#095d6a** (+ onun açıq/tünd çalarları; parlaq aksent #3FC1CF). Narıncı yoxdur.
- **Şrift:** Montserrat 900/800/600, ağ.
- **Lockup:** «kino çərçivəsi» (`lockupStyle: "frame"`) — videonun ətrafında öz-özünə çəkilən teal
  çərçivə + yazıların solunda teal xətt. Orijinalın diaqonal qutusu istifadə olunmur.
  Alternativlər şablonda var: `glass` (şüşə kart), `chips` (pill + xətt), `slash` (köhnə).
- **Hərəkət xoreoqrafiyası** (anchors-a bağlı, hər epizodda eyni):
  1. açılış: üç qatlı teal slash pərdə; böyük yazı zolaqları müğənninin **arxasında** axır (dərinlik maskası);
  2. «və biz … qrupu» anında ekran 3 diaqonal hissəyə bölünür, hər birində bir üzv (split);
  3. kinetik sözlər bitlərlə: İLK DƏFƏ (teal blok) → “ARAZ”DA (echo) → DİNLƏ (parlaq teal);
  4. sözlər uçub lockup-a düzülür (FLIP), tarix hərf-hərf, saat rəqəmləri sayğac kimi fırlanır;
  5. mahnının girişində teal pərdə + zərbə; insanların arxasında nəhəng yazı zolaqları;
  6. keçidlər: **siluet keçidi** (yeni kadrın insanları əvvəl görünür), **whip** (istiqamətli, motion blur);
  7. finalda yenə pərdə, qrup pozası, yazı zolağı başların üstündə; “ARAZ”DA üzərində parıltı.
- **Ritm:** güclü bitlərdə çərçivə və yazılar 1–2% «nəfəs alır» (`beats`).
- **Qreyd:** kölgələrdə yüngül teal (`grade.amount`), dəri təbii qalır.
- **Səs dizaynı:** öz sintez etdiyim whoosh / sub-zərbə / riser (heç bir sample yox), low-pass,
  musiqidən ~17 dB aşağı (`sfx`, `sfx_db`). Mahnının özü toxunulmur.
- **Dərinlik maskaları:** BiRefNet_lite (MIT) — `segment.py`; yalnız arxasında yazı olan kadrlar üçün.

## Sürət qeydləri

- Fayllar gələn kimi maskaları arxa planda başlat: `SEG_RES=512x384 python3 -I segment.py …` (~2 s/kadr, 768x576-da ~3.5 s).
- AI materialı videodan qısadırsa, `shots[].speed` (məs. 0.75) ilə slow-motion — kəsitlər təkrarlanmasın.
- `render.py` hər hissənin kadr sayını yoxlayır; yarımçıq video yazmır.

## Avtomatlaşdırma (`prepare.py`)

`python3 prepare.py episodes/<qovluq> --date "9 NOYABR"` — bitlər və mahnı girişini tapır, bütün
anchor-ları bitə bağlayır, AI kadrlarını skan edir (morf/ghost/bulanıq kadrları işarələyir), hər slot
üçün təmiz və fərqli kəsit seçir, split üçün 3 sifəti tapır, `config.json` + `auto_shots.jpg`
(kontakt vərəq) yazır və maskaları hesablayır. Kontakt vərəqə bax → `python3 render.py …`.

 epizod — addımlar

1. `episodes/<tarix>_<ifaçı>_<mahnı>/source/` qovluğuna MP3 və AI videolarını qoy.
2. Bitləri ölç (librosa `beat_track`); kəsimləri bitlərə qoy. Hər klipdən fərqli hissə seç
   (morf/ghost keçid kadrlarından qaç — kontakt vərəqlə yoxla).
3. Əvvəlki `config.json`-u köçür, dəyiş: `lockup.date`, `shots`, `wipes`, `lockup.style.l2.shine`, `glints`.
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
| `episodes/2026-11-02_donge_son-qerar` | İradə İbrahimova & Döngə — «Son Qərar» | 2 Noyabr | `Donge_Son_Qerar_Ilk_Defe_Araz_9x16.mp4` (18 s, v4) |
| `episodes/2026-11-11_benay_indi-bax` | Benay — «İndi bax» | 11 Noyabr | `Benay_Indi_Bax_Ilk_Defe_Araz_9x16.mp4` (16 s, v5; solo, ağ fon → teal yazı zolaqları) |
| `episodes/2026-11-13_ayan_o-tek` | Ayan — «O tək» | 13 Noyabr | `Ayan_O_Tek_Ilk_Defe_Araz_9x16.mp4` (18 s, v5; cəmi 15 s AI material → speed ramp 0.62–0.92×) |
