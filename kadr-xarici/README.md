# Kadr Xarici — documentary Reels archive

Style and workflow rules: `CLAUDE.md` (this folder). Reusable pipeline: `template/`.
The episode folders sit at the repository root and are kept exactly as delivered.

| # | Episode | Folder | Final video | Length | Status |
|---|---|---|---|---|---|
| 1 | BUM / Tağıyev pasajı — the forgotten 1907 cinema | `../kadr-xarici-bum/` | `BUM_Kadr_Xarici_9x16.mp4` | 85.0 s | Delivered. "Sİ ilə canlandırma" label removed on request. Thumbnail added afterwards. No other feedback. |
| 2 | Bakının yoxa çıxan tramvayları (1924–2004) | `../kadr-xarici-tramvay/` | `Tramvay_Kadr_Xarici_v2_9x16.mp4` | 101.3 s | v1 (102.5 s, quiet opening) → user asked for "more engaging" → v2 with the question hook, split screen, 117 → 0 counter, punch-ins, mid-hook and 70 px subtitles. v2 awaits feedback; v1 survives only in git history. |
| 3 | «Fantaziya» hamamı — abandoned bathhouse | `../kadr-xarici-fantaziya/` | `Fantaziya_Kadr_Xarici_9x16.mp4` | 92.2 s | Delivered, awaits feedback. No past-scene clips were supplied; the past is evoked by grade and sound only. |
| 4 | Şamaxı zəlzələsi, 1902 — no voice-over, text as narrator | `../kadr-xarici-samaxi-1902/` | `Samaxi_1902_Kadr_Xarici_v2_9x16.mp4` | 50.0 s exactly | Ending = logo only (user correction). v1 music "Dark Walk" rejected ("Mahnı uyğun deyil"); user wanted "çox intense dark" and supplied their own track (TikTok, @the_phonkface, licence unverified) → v2. Awaits feedback. |

Each episode folder contains the MP4, thumbnail, SRT, `CREDITS.md` (music, SFX, licences, timeline),
`project/` (`render.py`, `common.py`, `mix.py`, `thumb.py`, voice-over MP3) and `stems/`.
Source clips and downloaded music and SFX are **not** stored; they are listed in `CREDITS.md` and
must be uploaded or downloaded again to re-render.

## `template/`

| File | Purpose |
|---|---|
| `render.py` | Frame renderer (OpenCV + PIL → ffmpeg). Copied from Fantaziya, the most complete version: warm/cold `k` grade with bloom, bloom/dissolve/cut transitions, split screen, titles, word-highlight subtitles, photo-slide ending, logo watermark and end card. Edit `SHOTS`, `SPLIT_*`, `END_*` and `TITLES` per episode. |
| `common.py` | Subtitle data: `CHUNKS`, `PAUSES`, `SKIP_SUBS`, `OFF`, `DUR`. Replace per episode. |
| `mix.py` | Voice chain, music bed with side-chain ducking, SFX placement helpers (`place`, `seg`, `lp`, `hp`, `thump`). Replace the cue list per episode. |
| `thumb.py` | Past/present thumbnail with the hook title. |
| `tools/` | `setup.sh`, `contact_sheets.sh`, `transcribe.py`, `pauses.py`, `stills.py`, `srt.py`, `finalize.sh`. |
| `brand/kadr_xarici_logo.png` | The user's original logo upload (960×960 white on transparent), unaltered. |

For the BUM-style sepia/silver grades (`sepia`, `sepia_soft`, `silver`, `soviet`, `ninety`, `today`,
light leaks, projector flicker, km counter, route line), see `../kadr-xarici-bum/project/render.py`
and `../kadr-xarici-tramvay/project/render.py`; their `grade()` function contains every preset.
