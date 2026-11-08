# «Zəfərin görünməyən qəhrəmanları»: Reels üz qabığı (1080×1920)

Reel: «Qəbul Vaxtı» (Araz FM 103.3), instagram.com/reel/DfeaCj5o5lQ.
Üz qabığında verilişin qonaqları var: anestezioloq-reanimatoloq **Elşən Ağayev** və böyük tibb bacısı **Sevda Məmmədova**.

Bütün görüntülər reel-in öz kadrlarıdır (`frames/`):

| Fayl | Video vaxtı | Üz qabığında |
|---|---|---|
| `elshen_agayev_0m19s.jpg` | 0:19.6 | sol portret |
| `sevda_memmedova_1m20s.jpg` | 1:20.3 | sağ portret |
| `cebhe_0m51s.jpg` | 0:51.8 | yuxarıdakı fon: cəbhədən real kadr |

Başlığın arxasında Azərbaycan bayrağı var (rəsmi konstruksiya, `../zefer-gunu-edit/flag_scenes.py`).
Rəng tonu sənədli filmdəki kimidir: solğun rənglər, tünd vinyet, incə dən. Üzlərə retuş edilməyib, heç nə generasiya olunmayıb.
Mətnlərin hamısı Instagram-ın 4:5 tor kəsiminin içindədir.

Yenidən yaratmaq üçün:
```
python3 make_assets.py build "frames/elshen_agayev_0m19s.jpg@30,170,500,700" \
  "frames/sevda_memmedova_1m20s.jpg@50,200,500,700" bg=frames/cebhe_0m51s.jpg
node render.js            # -> cover_1080x1920.jpg
```
