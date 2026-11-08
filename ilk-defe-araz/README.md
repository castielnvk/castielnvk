# «İlk dəfə "Araz"da dinlə» — premyera Reels şablonu (v4 — orijinala yaxın, premium motion)

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

## Dizayn (v4) — orijinal şablonun dili, premium hərəkətlə

- v2 (qızılı serif) və v3 (Big Shoulders, işıq effektləri) **rədd edildi**: «qarışıq», «şriftlər cringy».
  İstifadəçi orijinala yaxın, **stabil** şablon istəyir.
- Şrift: **Montserrat** (900 başlıqlar, 800 tarix, 600 saat) — orijinaldakı qalın həndəsi şriftə ən yaxın.
  Yazılar ağ, sol tərəfdə (x=72), orijinaldakı sıra ilə: tarix / saat / İLK DƏFƏ / “ARAZ”DA / DİNLƏ.
- Narıncı 60° «slash» paneli sol aşağıda (orijinaldakı üçbucaq), 3 qatla girir: ağ incə xətt,
  tünd narıncı kölgə zolağı, əsas narıncı (qradiyentli). Çox yavaş parallax «nəfəs».
- Keçidlər: açılışda və 2 dəfə (mahnının girişi, final) üç qatlı narıncı slash pərdə bütün ekranı
  keçir; kəsim ekran tam örtülü olanda olur. Hard cut-larda incə ağ işıq slash-ı. Hamısı əsl motion blur ilə.
- Yazılar maskanın arxasından çıxır (motion blur ilə); “ARAZ”DA slash bucağı ilə girir və bitlərdə
  üzərindən narıncı parıltı keçir.
- AI videolarının uğursuz yerləri (ghost/morf keçidlər, əyilmiş əl/obyekt) istifadə olunmur —
  kontakt vərəqlə yoxla, yalnız təmiz kəsitləri götür.
- Loqo: `logos/individual/araz-radio_white.png`, dəyişdirilmədən, aşağıda ortada (orijinal yer).

## Yeni epizod — addımlar

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
