# BAXMA DEDİM. — EP01 «Kotar sindromu»

`Baxma_Dedim_EP01_Kotar.mp4`: 1080×1920, H.264, 24 fps, 14.0 s, **no audio stream**.

## Edit (times are in the finished video)

| Time | Picture | Text |
|------|---------|------|
| 0.00–1.00 | Hold on source frame 0 (still), slow push-in | "Bəzi insanlar sağ ola-ola / öldüklərinə inanırlar." reveals at once |
| 1.00–5.17 | Source 0.0–4.17 s: he reaches, lifts the spoon, holds it over the food | line 1 stays |
| 5.17 | Spoon touches the table (source frame 100) | line 2 replaces line 1 |
| 5.17–9.00 | Source 4.17–8.0 s: untouched plate, he stares; push-in continues | "Bəziləri buna o qədər inanır ki, / yeməkdən də imtina edir." |
| 9.00–12.0 | Hard cut to near-black #0D0C0B | "Bu hal / **Kotar sindromu** adlanır." |
| 12.0–14.0 | Approved logo (concept 01, exact artwork), 0.35 s fade-in, then a hold | — |

- "Canlandırma" (a small label) stays on screen for the whole kitchen shot.
- The kitchen text is Inter Tight SemiBold 66 px, left-aligned at x 84 in the dark ceiling. It keeps clear of the lamp, the face, the spoon and the IG/TikTok interface zones.
- The grade is in `GRADE` in `edit.py`: slight contrast, deeper shadows, cooler highlights and a vignette.

## Re-render / Episode 02
`python3 edit.py` (needs Python with fonttools, brotli, numpy and Pillow, plus ffmpeg and Node Playwright).
For EP02, copy this folder and change the CONFIG block: `SOURCE`, `FREEZE`, `SPOON_TOUCH_SRC_FRAME`
(the action beat), `KITCHEN_END`, and the text in `CARDS`. The layout, typography and logo end card stay the same.
`layers/*.svg` are the editable vector text and logo layers.
