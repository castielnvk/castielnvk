# Bayraq Günü (9 Noyabr) — viral "uşaq və bayraq" Reel

**Final:** `Bayraq_Gunu_9Noyabr_9x16.mp4`: 20.0 s, 1080×1920, 30 fps, H.264 + AAC, −14 LUFS.

Source: a viral social-media clip (TikTok id 7706007423080779028, 720×1280, 29.5 s). A child
climbs a lamp post in strong wind, trying to reach a flag that was torn loose and hangs from it.
Credit the original author in the Instagram caption.

## Music
The finale of the national anthem "Azərbaycan marşı" (Üzeyir Hacıbəyli), performed by the US Navy
Band: `anthem_US_Navy_Band_public_domain.mp3`, from Wikimedia Commons
("Azərbaycan marşı instrumental.ogg"). The recording is public domain as a US federal government
work, and state anthems are not objects of copyright under Azerbaijani law (No. 636-IVQD, Art. 7).
The Reel uses 109.66–129.66 s, so the final chord lands on the end card. Soft whooshes accompany
the flag wipes. The original clip's audio (a commercial song) was removed.

## Edit (cuts on the anthem's accents)
| Out | Source | Text |
|---|---|---|
| 0.00–1.85 | 18.0 (flag close-up) | Külək bayrağı dirəkdən qopardı. |
| 1.85–3.72 | 1.6 (child walks) | (same) |
| 3.72–7.33 | 3.05–6.66 | Amma bir uşaq buna biganə qalmadı. |
| 7.33–11.02 | 12.0–15.7 | Külək güclü idi, dirək isə hündür. |
| 11.02–14.79 | 20.4–24.2 | O, dəfələrlə cəhd etdi. / Geri çəkilmədi. |
| 14.79–17.28 | 24.17–24.9 at 0.4×, freeze on 24.9 | Çünki bayrağa sevgi yaşla ölçülmür. |
| 17.28–20.00 | end card | 9 NOYABR · Dövlət Bayrağı Günü · MÜBARƏK! + Araz logo |

Style (user chose option A of three): cinematic letterbox, with black bars above and below and
footage framed in a 1080×1160 window at y 280. Captions are Montserrat ExtraBold caps (50 px, tracking 4)
in the lower bar, upper-cased with the Azerbaijani i→İ rule. The small Araz logo is centred in the top bar.

Transitions: zoom-through blur (1.85, 7.33), diagonal blue–red–green flag wipes (3.72, 11.02,
17.28) and a bloom flash into the slow motion (14.79). The Araz white logo sits top centre and
returns large on the end card.

## Build
```
ffmpeg -i source.mp4 -q:v 2 -vsync 0 fr/%04d.jpg
python3 render.py fr video20.mp4
python3 audio.py anthem_US_Navy_Band_public_domain.mp3 pre.wav   # then 2-pass loudnorm −14 LUFS / −1.5 dBTP
ffmpeg -i video20.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k out.mp4
```
