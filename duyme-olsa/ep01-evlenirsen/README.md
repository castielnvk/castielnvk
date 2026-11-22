# Düymə olsa · Ep01 — «Bəs sən nə vaxt evlənirsən?»

12-second silent 9:16 Reel. Output: `Duyme_olsa_Ep01_evlenirsen_9x16.mp4` (1080×1920, H.264, **no audio stream**).

## Layers

| Layer | Source | Notes |
|---|---|---|
| 3D tabletop | `scene/build_scene.py` → `scene/ep01.blend` | Blender 4.5 LTS / Cycles. Armudu glass, tea, saucer, jam, half-cut cake, qənd, teapot, hands, relatives, room, all modelled in code. |
| Textures | `tools/make_textures.py` → `scene/textures/` | Tablecloth (buta + 8-point stars), wall carpet, weave bump. |
| Interface + Azerbaijani text | `ui/overlay.html`, `overlay.css`, `overlay.js` | Editable HTML/CSS. Frosted glass uses real backdrop blur over the plate. |
| End card | `../logo/anim/endcard.html` | Shared brand end card (logo 02). |
| Copy + timing | `episode.json` | One place for every line of text and every beat. |

## Rebuild

```bash
./render.sh                # textures → plates → composite → MP4 (≈70 min on 4 CPU cores)
node tools/compose.js      # UI-only changes: re-composite in ~2 min, no 3D re-render
node tools/compose.js --preview 0,4,7,9.5   # stills to build/preview/
```

Requirements: Blender 4.5 (`BLENDER=/path/to/blender`), Python 3 + Pillow, Node + Playwright, ffmpeg.

## How timing works

- `episode.json → ui` holds the copy and the UI beats (seconds). Change text or timing there and
  re-run only `compose.js`.
- `episode.json → scene` holds the 3D beats (pour, hand, lift). Changing these needs a plate re-render.
- Only frames with 3D motion are rendered (`build/bg_ranges.txt`). Held stretches reuse the last
  rendered plate, and the slow camera push is a 2D scale in compositing (`composite.push`).

## Beats (as delivered)

| Time | Beat |
|---|---|
| 0.0–3.0 | Tea finishes pouring; Xala's message is readable from frame 1 and settles. |
| 3.0–3.4 | Buttons appear: «Qismət, xala» / «Xalanı səssizə al». |
| 3.95 | Tap: the primary button compresses and releases. |
| 4.4–4.9 | The card collapses into «Xala səssizə alındı.» |
| 4.85–6.55 | Relief: a hand reaches for the glass and lifts it, stopping halfway as… |
| 6.15–6.6 | …«Bizimkilər · Ana» slides in above the muted pill (which wobbles). |
| 8.4–8.8 | «Anası da razıdır.» appears; held to 11.0. |
| 11.0–12.0 | Hard cut to the Düymə olsa end card. |

## Next episodes

Copy this folder, edit `episode.json` (copy and beats), then swap the props in `scene/build_scene.py`.
The UI components (notification card, buttons, pill, group card) are reusable as they are.
