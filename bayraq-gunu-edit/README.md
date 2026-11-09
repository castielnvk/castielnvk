# Bayraq Günü (9 Noyabr) — viral "uşaq və bayraq" Reel

Source: a viral social-media clip (TikTok id 7706007423080779028, 720×1280, 29.5 s). A child
climbs a lamp post in strong wind, trying to reach a flag that was torn loose and hangs from the
post. Credit the original author in the Instagram caption.

## Edit (31.5 s, 1080×1920, 30 fps)
| Out | Source | Text |
|---|---|---|
| 0.0–2.8 | 18.0–20.8 (flags, push-in) | Külək bayrağı dirəkdən qopardı. |
| 2.8–8.6 | 0.5–6.3 (child walks to the post) | Amma bir uşaq buna biganə qalmadı. |
| 8.6–13.6 | 11.6–16.6 (first climb) | Külək güclü idi, dirək isə hündür. |
| 13.6–19.5 | 18.4–24.3 (more attempts) | O, dəfələrlə cəhd etdi. |
| 19.5–23.0 | 24.0–25.0 at 0.5×, freeze on 24.9 (looks up) | Geri çəkilmədi. |
| 23.0–27.0 | 25.5–29.3 (climbs down, stands under the flag) | Çünki bayrağa sevgi yaşla ölçülmür. |
| 27.0–31.5 | end card on blurred last frame | 9 NOYABR · Dövlət Bayrağı Günü · MÜBARƏK! + Araz logo |

Skipped: 6.7–11.6 (wider shots with adults whose role is unclear).
The original audio is a music track, so it was dropped (copyright). Score and SFX are original
(`music.py`): D minor pads + sparse piano, heartbeat under the slow-motion, D-major resolution on
the end card, soft wind and flag flutter.

## Build
```
ffmpeg -i source.mp4 -q:v 2 -vsync 0 fr/%04d.jpg
python3 render.py fr out/video.mp4
python3 music.py out
./mix.sh out Bayraq_Gunu_9x16.mp4
```
Fonts: Playfair Display italic (fonts/, latin+latin-ext merged) and Inter Display.

Voice-over: not included, by the standing rule against generated voices. `VO_SCRIPT.md` holds
the timed script for an Araz presenter to record; mix it in with music ducked ~14 dB.
