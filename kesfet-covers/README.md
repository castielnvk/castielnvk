# Kəşfet — Reel cover şablonu (A stili)

Instagram @keshfetde Reel coverləri üçün şablon. Çıxış 1080×1920 PNG-dir.

## Qovluqlar
- `cover/A_tpl.html`: cover şablonu (HTML/CSS), `_base.css` ilə.
- `cover/makeAll.js`: `pipeline/jobs.json` əsasında coverləri Playwright ilə render edir.
- `cover/*.woff2`: Archivo şrifti (variable, Expanded = `font-stretch:125%`).
- `cover/medallion.png`: yuxarıdakı qızılı "#" loqo. `logo.png` tam 3D loqodur.
- `cover/examples/`: hazır nümunələr.
- `pipeline/batch_cut.py`, `pipeline/prep_subject.py`: qonağı fondan kəsir. rembg + `birefnet-portrait` istifadə olunur, aşağı yaddaş üçün ONNX parametrləri qoyulub (arena off, mem pattern off, ORT_ENABLE_BASIC).
- `pipeline/jobs.json`: hər cover üçün məlumat (sözlər, rəng, mətn, ad).

## İstifadə
1. Qonağı kəsib `cover/subjects/<id>.png` kimi yadda saxla (şəffaf PNG).
2. `pipeline/jobs.json`-a yazı əlavə et:
   `{"n":45,"id":"<id>","pal":"green","tag":"","w1":"KONTUR SÖZ","w2":"QIZILI","w3":"SÖZ","lead":"Mətn <b>vurğu</b>","name":"Qonaq Adı","sw":"900px","edge":true}`
3. `node cover/makeAll.js 45`. Nəticə `cover/out/` qovluğuna yazılır.

Sahələr:
- `sw`: qonağın eni.
- `dy`: şaquli sürüşmə.
- `edge` / `topfade`: kənarların yumşaldılması.
- `multi`: yan pozalar (`<id>_l.png`, `<id>_r.png`).

## Üslub qaydaları
- **Düzülüş:** yuxarıda qızılı "#" medalyon. Altında 3 sətirlik söz bloku: 1-ci sətir kontur sözdür, 2-ci və 3-cü sətir böyük metal-qızılı sözlərdir. Qonaq sözlərin dərhal altından başlayır (başı söz blokunun altına düşür). Aşağıda 1–2 sətirlik krem rəngli mətn, onun altında qızılı xətlər arasında BÖYÜK HƏRFLƏRLƏ ad.
- **Rənglər (dizaynerin palitrası):**
  - `green`: sitat və müsahibə
  - `berry` (çəhrayı): premyera, yeni mahnı, "İLK DƏFƏ ARAZ'DA"
  - `peach`: giveaway (yazılar qızılı yox, krem rəngdə)
  - `aqua`: oyun və rubrikalar ("O, yoxsa BU?", "Çətin suallar", "Ürək sözləri", "Sınaq")
- **Etiketlər:** "EKSKLÜZİV" yalnız premyera və "ilk dəfə Araz'da" postlarında. "GIVEAWAY" yalnız giveaway postlarında. Sitat postlarında etiket olmur.
- **Mətn:** qızılı sözlər maksimum 2–3 söz. Ad iki dəfə yazılmır. Aşağıdakı mətn maksimum 2 sətir.
- **Grid (3:4):** Instagram profil gridi coverin ortasındakı 1080×1440 hissəni göstərir (yuxarıdan və aşağıdan 240 px kəsilir). Bütün elementlər bu sahənin içində qalır: loqo y=300-dən başlayır, ad y≈1600-də bitir.
- **Kəsim:**
  - Papaq, saç və əllərdəki əşyalar heç vaxt kəsilməməlidir.
  - Köhnə dizayndan götürülən şəkildə loqonu dairəvi örtüklə yox, yalnız loqonun öz yaşıl və qızılı pikselləri ilə silirik, ki saça toxunulmasın.
  - Köhnə yazılar kəsimə düşməməlidir.
- **Pozalar:** rəqs edilən və ifa olunan videolarda 2–3 poza istifadə olunur.
- **AI ilə keyfiyyət artırma istifadə edilmir** (istifadəçi bunu istəmədi).
