# Araz FM — cinematic lower-third film (v9)

One continuous 20 s loop for the bottom 216 px of a 1920×1080 frame:
radio dial → river glint → phone glass → saz string (no wood; deep teal) → bridge → logo lockup.

## Files
- `film.js` — the whole animation. Edit the `COPY` block at the top to change any text line
  (each line is drawn as its own layer); `T` holds the scene start times, `DUR` the loop length.
- `make_textures.py` — regenerates the procedural textures (metal, water, caustics, land).
- `render_film.js` — renders frames with Playwright Chromium:
  - `node render_film.js <dir> 20 alpha`   → transparent PNG sequence (1920×1080 RGBA, 25 fps)
  - `node render_film.js <dir> 20 preview` → JPG frames composited over `studio_bg.jpg`
- `out/ArazFM_LowerThird_alpha_ProRes4444.mov` — transparent overlay for vMix (ProRes 4444, 25 fps, loops).
- `out/ArazFM_LowerThird_alpha.webm` — same with VP9 alpha (small file).
- `out/ArazFM_LowerThird_reference.mp4` — reference composite over the studio sample.

The PNG sequence (≈290 MB) is not stored in git; regenerate it with the `alpha` command above.
The logo is the supplied `logos/individual/araz-radio_white.png`, scaled down only.
