# Fourth of July — lyric Reel (Rahib Mirzoev)

- Final: `Rahib_Mirzoev_Fourth_of_July_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, 56.9 s).
- Fully procedural film (numpy + OpenCV + PIL → ffmpeg), no stock footage.
- `project/render.py` — picture (`python3 render.py all video.mp4`, about 10 min on 4 cores;
  `python3 render.py still 10.9,38.3 outdir` for check frames). Lyric timings are in `LYR`.
- `project/sfx.py` — synthesised sound design mixed under the untouched recording → `mix.wav`.
- `project/feat.npz` — loudness curves of the recording; they drive wind, firefly glow and dew glints.
- Mux: `ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k final.mp4`
