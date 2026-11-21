# «Bambaşka biri» — kinetic typography lyric video (16:9, YouTube)

- `Bambaska_Biri_Lyric_Video_16x9.mp4` — final 1920×1080, 30 fps, H.264 + AAC 256k, 3:06.
- `Bambaska_Biri_thumbnail_1280x720.jpg` — YouTube thumbnail.
- `render/` — editable project: `timeline.js` (word-timed lyrics), `render.js` (Node + @napi-rs/canvas
  renderer), `fonts/`, `audio.json` (beats/energy).

Rebuild: `cd render && npm i @napi-rs/canvas && node render.js video 0 5589 out/v.mp4`, then mux the song WAV.
Stills: `node render.js still OUTDIR 47.5 92.6`.
