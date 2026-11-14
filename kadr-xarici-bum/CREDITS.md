# BUM — «kadr xaricində qaldı» (Kadr Xarici, 14 Nov 2026)

Final: `BUM_Kadr_Xarici_9x16.mp4` — 1080×1920, 24 fps (all source clips are 24 fps), H.264 + AAC stereo,
85.0 s, −14.3 LUFS / −1.4 dBTP. Subtitles burned in; separate `BUM_Kadr_Xarici.srt`.

## Music
- **"Echoes of Time v2" — Kevin MacLeod (incompetech.com)**, track section 0:09–1:34.
  - Source: https://incompetech.com/music/royalty-free/mp3-royaltyfree/Echoes%20of%20Time%20v2.mp3
  - Licence: Creative Commons Attribution 4.0 (https://creativecommons.org/licenses/by/4.0/).
    Commercial/monetised use on Instagram, TikTok and YouTube is allowed. **Attribution is required**
    in the post caption/description:
    `Music: "Echoes of Time v2" by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0`

## Sound effects — BigSoundBank.com (Joseph Sardin), CC0, no attribution required
| Sound | Used for | Page |
|---|---|---|
| 35mm cinema projector 1 | hook, 1907 cinema scenes, "ghost" cinema | https://bigsoundbank.com/35mm-cinema-projector-1-s0065.html |
| Footsteps of horses, rue Christine | 1890s street | https://bigsoundbank.com/footsteps-of-horses-rue-christine-s0979.html |
| Small pedestrian street | 1890s street air | https://bigsoundbank.com/small-pedestrian-street-s0527.html |
| Covered market 1 | passage crowd, glass-roof hall | https://bigsoundbank.com/covered-market-1-s3346.html |
| Covered market 3 | Soviet department store | https://bigsoundbank.com/covered-market-3-s3348.html |
| Intermission at the Palace Theater | cinema entrance and audience | https://bigsoundbank.com/intermission-at-the-palace-theater-s0642.html |
| Wind from inside 1 | glass-roof hall air | https://bigsoundbank.com/wind-from-inside-1-s1714.html |
| Small shopping arcade in London | modern interior (muffled) | https://bigsoundbank.com/small-shopping-arcade-in-london-s0646.html |
| Pedestrian place | today's street | https://bigsoundbank.com/pedestrian-place-s0526.html |
| Whoosh 3 | transitions (slowed, low-passed) | https://bigsoundbank.com/whoosh-3-s1795.html |

The four low sub impacts (0:02, 0:32, 1:01, 1:21) and the short swell before "1907" are synthesised
in `project/mix.py` — no third-party material.

## Timeline (video time; voice-over starts at 0.40 s)
| Time | Source clip | Narration |
|---|---|---|
| 0.00–2.25 | modern BUM exterior (0.0–2.25) | Bakının məşhur BUM binasında |
| 2.25–6.15 | cinema hall, tight on projector beam | 100 ildən çox əvvəl kinoteatr… |
| 6.15–12.4 | old building exterior | 1896–1898 |
| 12.4–19.85 | old street | Memar Kazimir Skureviç… ticarət |
| 19.85–24.7 | Tağıyev portrait | 1903, Hacı Zeynalabdin Tağıyev |
| 24.7–32.0 | passage interior (wide, then punch-in) | Tağıyev pasajı… təkcə ticarətlə bağlı deyildi |
| 32.0–37.7 | cinema entrance (70 % speed, hand-cranked feel) | 1907, «Fransız Elektro-Bioqraf» |
| 37.7–44.15 | cinema hall, wide | kino hələ yenilik idi… |
| 44.15–47.25 | cinema entrance, door | «Təyyarə» |
| 47.25–52.65 | Soviet department store | Köhnə univermaq, BUM |
| 52.65–61.2 | glass roof tilt-up | tarixi şüşə damı |
| 61.2–63.05 | suspended ceiling (top-down wipe) | asma tavanla örtüldü |
| 63.05–66.3 | modern BUM exterior | Bu gün minlərlə insan… |
| 66.3–72.1 | modern corridor → dissolve into cinema hall | burada bir vaxtlar… |
| 72.1–74.8 | old exterior / Soviet store / modern exterior | İllər keçdi, bina dəyişdi |
| 74.8–78.7 | modern exterior becomes a photograph and slides out of frame | unudulmuş hekayəsi uzun müddət… |
| 78.5–81.0 | black, serif title | kadr xaricində qaldı. |
| 81.05–85.0 | logo reveal | — |

Rebuild: put the ten clips as `src/c01.mp4 … c10.mp4` (upload order), `src/vo.mp3`, `src/logo.png`,
Playfair Display TTFs under `fonts/package/`, sounds under `dl/`, then `python3 mix.py` and
`python3 render.py video.mp4`, and mux with ffmpeg.
