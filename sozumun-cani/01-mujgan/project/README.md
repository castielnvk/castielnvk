# Sözümün Canı — «Müjgan» (editable project)

Everything in this film is drawn procedurally in code (HTML canvas), so it can be edited and re-rendered exactly.

- `film.js` — all scenes, typography, timing (scene schedule at the bottom: `SCENES`).
- `data.js` — the corrected, word-timed Azerbaijani transcript; captions and text reveals sync to it.
- `transcript_az.md` — readable timestamped transcript.
- `fonts/` — Cormorant Garamond / Cormorant SC (SIL Open Font License), full Azerbaijani coverage. Captions use Inter.
- `sfx.wav` — the added sound-design layer (mixed at −6 dB under the original audio).
- `tools/` — `render.js` (Playwright → ffmpeg), `still.js` (preview frames), `sfx.py`, `mkdata.py`.

Preview: open `index.html` in Chrome, then in the console run `render(30)` to see t = 30 s.
Render: `node tools/render.js <abs path to this folder> <out dir>`, concat the segments, then mux with the audio:
`ffmpeg -i src.mp3 -i sfx.wav -filter_complex "[1]volume=0.5[s];[0][s]amix=inputs=2:normalize=0:duration=first" ...` followed by loudnorm to −14 LUFS.

## v2 (logo + new score)
- Logo: `logo.png` / `logo.js` (ARAZ Radio 103.3 FM, unaltered), drawn in `brand()` in `film.js`.
- `audio/voice_m.wav` — narration separated from the original mix with Demucs (htdemucs_ft), 70 Hz high-pass only. Intro kept.
- `audio/music_m.wav`, `audio/sfx_m.wav` — new original score and sound design (`tools/score_mujgan.py`, uses `tools/audiolib.py`).
- Mix: voice −4.5 dB, music −10 dB with gentle side-chain ducking, sfx −4 dB, then loudnorm −14 LUFS / −1.5 dBTP.
