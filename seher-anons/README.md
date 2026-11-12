# 100% Səhər Şousu — "Sabahın mövzusu" comic-book announcement templates

Three style samples made on 2026-11-12 (user had not yet chosen one):
A "Komiks səhifəsi" (cream comic page, panels + freeze-frame snapshots),
B "Jurnal üz qabığı" (comic cover, purple masthead, big question block),
C "Pop-art gecə" (dark pop-art, three slanted strips, kinetic question).

How it works: `comic.html?s=A|B|C` draws one frame via `setT(t, frameIndex)`; `render.js <style>`
screenshots every frame with Playwright into `out/<style>/`, then ffmpeg joins them at 25 fps with
the source audio. Expects next to it: `fr/<style>/%04d.jpg` (footage frames, 1080 wide),
`logo.png` (the 100% Səhər overlay) and `fonts/` (`npm i @fontsource/bangers @fontsource/montserrat`;
Bangers has ə/Ə).

The samples were built from finished announcements with the old graphics baked in, so only the
clean band y 905–1525 was used. With a clean AI video, extract the full frame and adjust the
panel crops (`panel(...)` `{s, ox, oy}` values); topic text, date and stickers are plain strings.

## Second round (2026-11-12, later)

The user rejected A/B/C above ("bəyənmədim") and asked for still previews; from four full-bleed
directions (`prev.html?p=1..4`) they asked for 1, 2 and 3 as videos on a clean AI clip:
`anons.html?p=1|2|3` (1 Qrafik roman, 2 Pop-art balon, 3 Panel kəsik), rendered with
`render2.js <p> <frames>` at 24 fps. Final choice still pending.

- Clean AI clips arrive as 720×1264, ~5 s, 24 fps, silent. Scale to 1080×1920 (`scale=-2:1920,crop=1080:1920`)
  into `fr/N/`, loop to 14.1 s like the station's own anonses.
- `jingle_14s.m4a` is the standard announcement audio (identical in the 6, 11 and 12 Nov anonses).
- Check that titles don't cover the characters' heads across the whole loop; text and date are
  plain strings in `anons.html`.

## Current pipeline (approved style 1)

`python3 build.py config.json` — see MEMORY.md. Extra assets to recreate next to the scripts:
`l100.png` = `logos/individual/100-seher-sousu.png`, `larazw.png` = `logos/individual/araz-radio_white.png`,
fonts via `npm i @fontsource/bangers @fontsource/anton @fontsource/barlow-condensed` into `fonts/`.
Python: librosa, soundfile, scipy. Music from incompetech.com (CC BY 4.0, credit required).
