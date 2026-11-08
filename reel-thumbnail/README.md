# «Zəfərin görünməyən qəhrəmanları» — Reels üz qabığı (1080×1920)

Reel: «Qəbul Vaxtı» (Araz FM 103.3). Qonaqlar: anestezioloq-reanimatoloq **Elşən Ağayev** və böyük tibb bacısı **Sevda Məmmədova**.

Üslub: sənədli film tonu (desaturasiya, tünd vinyet, incə dən), arxa fonda Azərbaycan bayrağı
(rəsmi konstruksiya, `../zefer-gunu-edit/flag_scenes.py`), iki portret arxiv çapı kimi yan-yana.
Başlıq və mətnlər Instagram-ın 4:5 tor kəsiminin içində yerləşir.

`cover_1080x1920.jpg` hələlik **boş foto yerləri** ilə hazırdır. Real fotolar gələndə:

```
python3 make_assets.py build elshen_agayev.jpg sevda_memmedova.jpg   # p1 = sol, p2 = sağ
node render.js                                                       # -> cover_1080x1920.jpg
```

Fotolar yalnız böyüdülür (Lanczos) və rəng qreydi alır; üzə retuş edilmir, heç nə generasiya olunmur.
Kadrda üzün yeri `cover.html`-də `.p img { object-position }` ilə tənzimlənir.
