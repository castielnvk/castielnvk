# Araz FM — "Bakıda il dəyişdirilir." (New Year 2027 Reel, Nov 2026)

12 s, 1080×1920, 30 fps, H.264 + AAC 48 kHz, −13.6 LUFS / −1.4 dBTP.

- `Araz_FM_Yeni_Il_2027_9x16.mp4`: the final video.
- `Araz_FM_Yeni_Il_2027_cover.jpg`: the cover frame.
- `layers/`: separate graphic layers (headline, logo, "CANLI" live bug) as transparent PNGs.
- `audio_stems/`: the mix and the stems (ambience, creak, reverse beep, lock click, light-up thunks, music accent).
- `project/`: the editable source. `scene.html` is the three.js 3D scene (deterministic `renderAt(t)`);
  `render.js` renders it frame by frame in headless Chromium; `audio.py` builds the original sound design;
  `composite.py` adds the graphics and encodes.

## Timeline
| Time | Shot |
|---|---|
| 0–3 s | A low shot close to the swinging metal 6, pulling back to reveal "202" and the empty slot |
| 3–5.4 s | Wide: the second crane lowers the glowing 7, with the Flame Towers and the national flag behind |
| 5.4–6.75 s | Close: hook block, slings and taut cable |
| 6.75–8 s | The 7 settles onto the deck and locks with a metallic click at 7.85 s |
| 8–12 s | 2027 lights up, with a chase and reflections on the wet promenade. Headline at 8.55 s, logo at 9.15 s |

## Rebuild
```
npm i three@0.170.0
python3 -m http.server 8765 --bind 127.0.0.1 &
node render.js frames 1 30 all 0 1
python3 audio.py audio
python3 composite.py frames ../../logos/individual/araz-radio_white.png audio/mix.wav out.mp4 layers
```
