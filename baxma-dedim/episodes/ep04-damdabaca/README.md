# BAXMA DEDİM. — EP04 «Damdabaca»

`Baxma_Dedim_EP04.mp4`: 1080×1920, H.264 + AAC 48 kHz stereo, 24 fps, 35.0 s, −19.7 LUFS.
Three Gemini clips in order, with source audio muted. No voice-over, no music, no "Canlandırma" label.

| Time | Picture | Text (one card at a time) | Sound |
|------|---------|---------------------------|-------|
| 0.0–10.0 | Clip 1: the child looks up at the ceiling vent (her chin lifts at ~3.25 s) | 0.0 "Dinməyin, damdabaca gəlib sizi aparar." · 4.8 "Naxçıvandan toplanmış folklor nümunəsində…" | Quiet indoor room tone and a growing drone. **2.95: one heavy, muffled footstep overhead**, 3.22: a short wooden creak, then the drone sinks away softly (3.9–5.6) while the room tone stays, a pause for the second step that never comes (v2: the room tone is no longer cut, which sounded like a glitch) |
| 10.0–20.0 | Clip 2: the roof; the silhouette leans over the chimney at ~4.8 s and the shot holds | 10.15 "Adını ayrı-ayrı de: ‘damda baca’." · 14.4 "Bəzi təsvirlərdə Damdabacanın…" | Faint outdoor wind; **14.8: a low, close grit scrape on the brick rim**; the drone keeps growing |
| 20.0–28.0 | Clip 3: up the chimney as the silhouette blocks more sky; a slow push-in | 20.15 "Damdabacanın adı Azərbaycan ədəbiyyatında da keçir." · 23.55 "Kamal Abdullanın bir əsərində…" | **23.5: the wind cuts**, 23.8: a drier, closer scrape inside the chimney, heartbeat from 24.6, riser into the cut |
| 28.0–31.0 | Hard cut to black | 28.35 "Bəs sən bacaya baxardın?" | A deep impact on the cut, chopped to **complete silence** at 28.75 |
| 31.0–35.0 | Standard ending «Bir anlıq görünüş» | — | The standard ending sound (`shared/ending_sfx.py`) |

The captions sit clear of the ceiling vent, the silhouette and the chimney opening, with a soft dark scrim on brighter walls.
Line breaks are balanced, so no word is left alone on the last line.
The new designed sounds are in `../shared/sfx.py`: `footstep_overhead`, `wood_creak`, `wind`, `grit_scrape(close=…)`.

Brief vs. delivery: the brief asked for 30 s. The story runs 0–31 s, plus the standard 4 s logo ending (the user's standing rule),
so the video is 35 s. Following the house style, the "complete silence" before the question opens with the standard deep impact on the cut.

Files: `edit.py` (CONFIG at the top), `stems/` (one WAV per layer plus mix), `layers/*.svg`, `covers/04-cover-A-uz.*`.
