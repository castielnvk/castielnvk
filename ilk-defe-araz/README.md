# «İlk dəfə Araz'da» — premyera Reels şablonu (v2, premium/cinematic)

Araz Radio 103.3 FM-in eksklüziv mahnı premyeraları üçün 9:16 Reel şablonu.
Köhnə şablonu (narıncı diaqonal zolaqlar, «İLK DƏFƏ "ARAZ"DA DİNLƏ») əvəz edir.

## İstifadəçi hər dəfə nə göndərir

1. **Səs yazısı** (MP3): müğənni adını, qrupunu, mahnının adını deyir, sonra mahnı başlayır.
2. **AI videoları**: Grok ilə şəkildən çevrilmiş videolar (adətən 3 ədəd, 816×1104, 15 s).
3. **Tarix** (və saat, əgər fərqlidirsə; standart 11:00 — 12:00).

## Dizayn sistemi

- Kino işığı: qara + kəhrəba, AI kadrlarının öz isti tonu saxlanılır; incə vinyet və çox zəif dən (grain).
- Şriftlər: **Cormorant Garamond Italic** (qızılı qradiyent, adlar və mahnı adı) +
  **Inter Tight** (geniş aralıqlı böyük hərflər). Hər ikisi ə, Ə, İ, ı, ş, ğ, ö, ü, ç dəstəkləyir.
- Rənglər: fil sümüyü `#F4EDE3`, qızılı `#FBE7C2 → #E9B872 → #C98A43`, Araz narıncısı `#E86A33`
  yalnız aksent (● PREMYERA, «DİNLƏ»).
- Keçidlər: ritmə (beat) düşən sərt kəsimlər + 3 imza «işıq partlayışı» (bloom): mahnının girişi,
  başlıq anı, son kart. Başlıq anında anamorfik işıq xətti.
- Loqo: `logos/individual/araz-radio_white.png`, dəyişdirilmədən — yuxarı sağda kiçik, son kartda böyük.

## Struktur (səsdəki sözlərə sinxron)

| Səhnə | Nə vaxt | Mətn |
|---|---|---|
| `name` | müğənni adını deyəndə | «İradə» (qızılı kursiv) + «İBRAHİMOVA» |
| `group` | qrup adı | «VƏ BİZ» / «DÖNGƏ» / «qrupu» |
| `song` | mahnı adı | «YENİ MAHNIMIZ» / «Son Qərar» (söz-söz) |
| `version` | «yeni versiya, xüsusi olaraq Araz FM üçün» | 3 sətir |
| `presents` | mahnı başlayanda | «ARAZ FM TƏQDİM EDİR» |
| `titledrop` | növbəti güclü bit | «DÖNGƏ» / böyük «Son Qərar» + işıq xətti |
| `firsttime` | | «İLK DƏFƏ» / «"Araz"da» / «DİNLƏ» |
| `end` | son ~6 s | PREMYERA · TARİX · saat · ifaçı — mahnı · böyük Araz loqosu |

Hər səhnə istəyə bağlıdır: config-də olmayan səhnə çəkilmir (məs. solo müğənni üçün `group` silinir).

## Yeni epizod — addımlar

1. `episodes/<tarix>_<ifaçı>_<mahnı>/source/` qovluğuna MP3 və AI videolarını qoy.
2. Səsi transkripsiya et (faster-whisper large-v3, `language="az"`, `word_timestamps=True`)
   və bitləri ölç (librosa `beat_track`). Mətnlər heç vaxt deyilməzdən əvvəl görünmür.
3. Əvvəlki `config.json`-u köçür, dəyiş: mətnlər, söz vaxtları, `shots` (kadr seçimi, bitlərə
   düşən kəsimlər), `flashes`, `end.date` / `end.time`.
4. Önizləmə: `python3 render.py episodes/.../config.json --preview 1.9,4.5,13.5,25`
5. Tam render: `python3 render.py episodes/.../config.json` (≈2 dəqiqə, 4 paralel Chromium).
6. Yoxla: kontakt vərəq, səs sinxronu, ə/İ hərfləri, loqo.

Tələblər: `pip install playwright librosa faster-whisper`; Chromium `/opt/pw-browsers/chromium`
(və ya `CHROME=` mühit dəyişəni). Səs toxunulmur — yalnız sonda 0.4 s fade və −1 dBTP limiter.

`shots` sahələri: `start` (çıxış saniyəsi), `clip`, `src` (klipdə başlanğıc saniyə),
`z` [başlanğıc, son] miqyas (1.0 = 1920 hündürlüyə doldurur; <1 olanda kənarlar qaraya əriyir),
`cx`/`cy` fokus nöqtəsi (0–1).

## Epizodlar

| Qovluq | Mahnı | Tarix | Nəticə |
|---|---|---|---|
| `episodes/2026-11-02_donge_son-qerar` | İradə İbrahimova & Döngə — «Son Qərar» (yeni versiya) | 2 Noyabr, 11:00–12:00 | `Donge_Son_Qerar_Ilk_Defe_Araz_9x16.mp4` (28.9 s) |
