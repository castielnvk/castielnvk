# Melay — «Bambaşka biri» — kinetic typography lyric video (16:9, YouTube)

- `Melay_Bambaska_Biri_Lyric_Video_v2.mp4` — final 1920×1080, 30 fps, H.264 + AAC 256k, 3:06.
- `Melay_Bambaska_Biri_thumbnail_1280x720.jpg` — YouTube thumbnail.
- `align/` — forced alignment of the lyrics on the vocal stem (`align.py`, result `aligned.json`,
  `plot.py` spectrogram check). Words are shown only from their sung onset.
- `render/` — editable project: `timeline.js` (lyrics, fx per line, backing lines), `render.js`
  (Node + @napi-rs/canvas renderer), `fonts/`, `audio.json` (beats/energy).

Rebuild: `cd render && npm i @napi-rs/canvas && node render.js video 0 5589 out/v.mp4`, then mux the song WAV.
v1 (first version, whisper timing, simpler design) is in git history.
