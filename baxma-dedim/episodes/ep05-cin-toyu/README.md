# BAXMA DEDİM. — EP05 «Cin toyu»

`Baxma_Dedim_EP05.mp4`: 1080×1920, H.264 + AAC 48 kHz stereo, 24 fps, 33.0 s, −22 LUFS.
Source audio is muted. No narration, no music beyond the diegetic zurna, no "Canlandırma" label.
Clip 2 is the user's replacement (`source/2_hand_plate_v2.mov`).

| Time | Picture | Text (each line on its own beat) | Sound |
|------|---------|----------------------------------|-------|
| 0.0–10.0 | Clip 1: the old man leaning toward the lens | 0.0 "Cinlər onu toya çağırdılar." · 4.6 "O da hamını adam bilib süfrəyə oturdu." | A thin, distant zurna behind the guests; the crowd murmur dies away 1.0–3.8 while the zurna keeps playing; a chair creak at 0.55 (the lean); the drone starts very low |
| 10.0–20.0 | Clip 2 (real time) with a slow 1.10× push-in | 10.15 "Azərbaycan folklorunda buna ‘cin toyu’ deyilir." · 14.1 "Yolçu yeməyə əl uzadıb" · **15.5 "‘Bismillah’ dedi."** (fingers reach the rice at 16.0) | The same zurna across the cut, a wool sleeve rustle 14.7–16.15, the drone grows |
| **20.0** | **Matched hard cut** to the empty clearing; the hand lands on the same spot | — | **The zurna and everything else are killed on the cut frame**; one beat of complete silence 20.0–21.0 |
| 21.0–28.0 | Clip 3: the hand pulls back at ~22.7 | 21.05 "Bir də baxdı ki, çölün düzündə tək qalıb." · 24.6 "Gecə çöldən toy səsi gəlsə, gedib baxardın?" | Faint outdoor wind, a sleeve rustle at the pullback, heartbeat, the drone creeps back, a far-away zurna phrase in the wind (25.4–27.7), riser |
| 28.0–29.0 | Hard cut to black | — | Deep impact |
| 29.0–33.0 | Standard ending «Bir anlıq görünüş» | — | Standard ending sound |

The captions sit in a left column (max 620 px), clear of the lamp, the faces, the plate and the hand, with balanced line breaks.
The zurna is synthesised (`shared/sfx.py: zurna()`: a Shur-mode wedding phrase, nasal formants, vibrato, grace notes, trills, distance).
The crowd murmur is a real recording (Mixkit 2930), low-passed so no words come through.

Brief vs delivery: the brief asked for 30 s. The story runs 0–29 s, plus the standard 4 s logo ending, so the video is 33 s.

Files: `edit.py` (CONFIG at the top), `stems/` (one WAV per layer plus mix), `layers/*.svg`, `covers/05-cover-A-uz.*`.
