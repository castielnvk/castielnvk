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
