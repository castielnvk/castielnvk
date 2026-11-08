# «Zəfərin görünməyən qəhrəmanları»: Reels üz qabığı (1080×1920)

Reel: «Qəbul Vaxtı» (Araz FM 103.3), instagram.com/reel/DfeaCj5o5lQ.
Üz qabığında üç nəfər var: anestezioloq-reanimatoloq **Elşən Ağayev**, ortada aparıcı **Elnarə Sadıqova** və böyük tibb bacısı **Sevda Məmmədova**.

Portretlər reel-in öz kadrlarıdır, yuxarıdakı foto isə real arxiv fotosudur (`frames/`):

| Fayl | Video vaxtı | Üz qabığında |
|---|---|---|
| `elshen_agayev_0m16s.jpg` | 0:16.4 | sol portret |
| `elnare_sadiqova_0m02s.jpg` | 0:02 | orta portret (bir az hündür) |
| `sevda_memmedova_1m25s.jpg` | 1:24.6 | sağ portret |
| `qaziler_zefer_paradi_2020.jpg` | — | yuxarıdakı fon: Zəfər paradında yaralı qazilər, 10.12.2020. Mənbə: president.az, Wikimedia Commons, **CC BY 4.0**. Kredit üz qabığının üzərində yazılıb. |
| `cebhe_0m51s.jpg` | 0:51.8 | əvvəlki fon (reel-dəki cəbhə kadrı), ehtiyat üçün saxlanılıb |

Başlığın arxasında Azərbaycan bayrağı var (rəsmi konstruksiya, `../zefer-gunu-edit/flag_scenes.py`).
Rəng tonu sənədli filmdəki kimidir: solğun rənglər, tünd vinyet, incə dən. Üzlərə retuş edilməyib, heç nə generasiya olunmayıb.
Mətnlərin hamısı Instagram-ın 4:5 tor kəsiminin içindədir.

Yenidən yaratmaq üçün:
```
python3 make_assets.py build "frames/elshen_agayev_0m16s.jpg@130,190,330,760" \
  "frames/sevda_memmedova_1m25s.jpg@170,250,330,760" \
  "frames/elnare_sadiqova_0m02s.jpg@125,170,330,760" bg=frames/qaziler_zefer_paradi_2020.jpg   # p1 sol, p2 sağ, p3 orta
node render.js            # -> cover_1080x1920.jpg
```
