# BAXMA DEDİM. — logo concepts 01–06

Six logo directions for the BAXMA DEDİM. Instagram/TikTok page.

**Selected: 01 — The warning** (2026-11-22). Its avatar was then reworked to read at 48 px: a larger red "D." with a matching stroke, dropped below and past the B.
The other five directions are kept for reference.

- `BAXMA-DEDIM-board-01-06.png` is the comparison board: wordmark, 48 px avatar and 9:16 end card for each concept.
- `concepts/NN-slug/` holds each concept's files:
  - `NN-wordmark.svg` / `NN-wordmark-transparent.png` (1600 px wide source, 3200 px PNG)
  - `NN-avatar.svg` / `NN-avatar-512.png` / `NN-avatar-48.png` (circle avatar mark)
  - `NN-endcard-9x16.svg` / `NN-endcard-1080x1920.png`
- The SVGs are editable vectors. Each letter is its own named path, and layers have ids such as
  `c04-rec-dot`, `c05-redaction-bar` and `c02-door-gap`. Text is outlined, so no fonts are needed to open them.
- Palette: near-black `#0D0C0B`, bone `#E8E1D3`, red `#B3241C`, ash `#7A7266`, door light `#FFF1CF`.
- Fonts (SIL OFL, in `fonts/`): Anton, Instrument Serif Italic, Oswald, Inter Tight, Archivo Black,
  Space Mono, DM Serif Display.
- The end-card caption "Abunə ol — növbəti daha pisdir." is placeholder copy.

| # | Concept | Wordmark background |
|---|---------|---------------------|
| 01 | The warning: big BAXMA with a small red DEDİM. correction | dark |
| 02 | The door gap: a strip of light between the words | dark |
| 03 | The second look: the İ casts its shadow the wrong way | bone (light) |
| 04 | The red dot: the period is a REC light in a viewfinder | dark |
| 05 | The redaction: a bar almost hides DEDİM. | bone (light) |
| 06 | The peephole: the name seen through a door-viewer lens | dark (self-contained emblem) |

Rebuild: `pip install fonttools brotli` and Node with Playwright/Chromium, then `python3 build.py`.
