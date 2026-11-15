# Sözümün Canı — permanent editing rules

Word-of-the-day Reels for the Araz Radio 103.3 FM segment «Sözümün Canı». Each episode explains
one Azerbaijani word: its meaning and origin as narrated. Reply to the user in Azerbaijani. These
rules override the livestream-clip rules in the root `CLAUDE.md` for this series. Read
`../MEMORY.md` §1 for history.

**Template:** start every new episode by copying `03-zenexdan/project/`, the newest project with all
fixes. Reuse its engine, captions, branding, render tools and cover; replace the scenes, palette,
font and score.

## Deliverables (every episode, without being asked)
1. One 9:16 MP4: 1080×1920, 30 fps, H.264 + AAC, named `Sozumun_Cani_<Word>_9x16.mp4`.
2. A matching 1080×1920 Reel cover JPG.
3. An Instagram caption (format below).
4. The editable project and the transcript (`transcript_az.md`).
5. Archive everything in `sozumun-cani/NN-<word>/`, with the same layout as the existing episodes.

## Source and story
- The source is the user's narrated radio MP3. It has a music bed throughout, which must be removed.
- **Intro rule:**
  - Only the first episode (Müjgan) keeps the series intro: "Sözümün canı" + the proverb
    "Qulaq gündə bir söz eşitməsə kar olar" + "Sözümün canı odur ki, qulağınız bizdə olsun"
    (≈ 0–12.5 s of the source).
  - Every later episode starts **directly on the day's word**.
  - If the narration opens with a poem or quote, start on the quote. "Quote ilə başlasın" =
    open on the quoted lines.
  - Example trims: Məlal T0 = 12.78 s, Zənəxdan T0 = 12.5 s.
- **What to keep:**
  - Keep everything from T0 onward in order, including "Söz yerinə düşdü. Gələn sözlərə qədər."
    and the closing "Sözümün canı".
  - Never shorten substantive narration without asking.
- **Facts:**
  - The narration is the only factual source. Don't invent etymology, translations, history or
    quotes.
  - Don't add facts the narration doesn't contain. For example, don't show "مژگان" or any origin
    script unless it is spoken.

## Transcript (accuracy first)
- Use faster-whisper large-v3 (int8, `language='az'`, `word_timestamps=True`), passing audio as a
  float32 numpy array decoded by ffmpeg.
- Transcribe in windows of about 10–12 s, because whole-file runs drop the tail. Re-check unclear
  parts on the separated vocal stem.
- Use `initial_prompt` only on clean speech; on music it hallucinates the prompt words.
- Correct ASR errors by sense and keep a list of uncertain readings to report to the user.
- Build `data.js` (`LINES` = `[{s, e, text, w: [[word, t], …]}]`) on the edited timeline
  (source time − T0), aligning corrected words to whisper word times (see `tools/mkdata.py`).
- Spelling:
  - Use standard written Azerbaijani even when the pronunciation differs (zənəxdan, yumşaldan),
    and tell the user.
  - Preserve ə ı İ ö ü ş ç ğ. Write uppercase Azerbaijani literally (MƏLAL, ŞAİRANƏ) instead of
    calling `toUpperCase`.

## Visual language
- **Medium:**
  - Procedural editorial motion graphics in an HTML canvas: expressive typography plus vector
    illustration.
  - No AI images, stock or photos.
  - No waveform visualiser and no static background with captions.
- **One concept per word**, derived from the narration. Recurring motifs from the episodes so far:
  - Müjgan: lash → arrow → bow.
  - Məlal: rain, still water, reflection.
  - Zənəxdan: one fine "smile line".
- **Story structure:**
  - Each narrated idea (meaning, origin, example, modern contrast, conclusion) gets its own
    scene.
  - Scenes connect through shared elements: a word lifting out of a verse, a target becoming a
    ring light, a knot untying into a smile.
- **Openings and endings:**
  - The opening must move from frame 0, for example rain gathering into letters or a quotation
    mark drawing itself.
  - The ending brings the word back as a resolution, with the letters landing on a line or
    surface.
- **Palette and font:**
  - Each episode gets a NEW palette and a NEW display font, never repeated.
  - Used so far: Cormorant Garamond (gold/indigo), Playfair Display + Lora (slate/silver/amber),
    Fraunces (dawn cream/peach/rose-gold).
  - Check fonts with fontTools for all of `əƏıİöÖüÜşŞçÇğĞ` before use. DM Serif Display FAILS
    this check.
- **Comfort:** avoid harsh brightness and crushed blacks. Light "paper" scenes are allowed in warm
  cream (#ebdfcc), not white.
- **Timing:**
  - Text must never appear before it is spoken. Use `said(t, wordTime)`, which ramps over
    ≈ 0.35 s starting 0.06 s before the word.
  - Words reveal with blur→sharp and a small upward drift.
- **Transitions:** scene crossfades of 0.3–0.5 s, or hard cuts with a shared element. Avoid empty
  transition frames.
- **Finish:** film grain (soft-light, α 0.22) and a radial vignette over every frame (`finish()`
  in `common.js`).

## Layout (1080×1920)
- **Top branding:**
  - The Araz Radio logo sits top centre at y = 150, 180–200 px wide.
  - Below it, "SÖZÜMÜN CANI" in Inter 500, 22 px, letter-spacing 8.
  - It appears ≈ 0.5–2 s in, not as a logo animation, and fades out before the end card.
- **Logo colour:**
  - Use the exact supplied PNG (`shared/araz_logo_supplied_1080.png`), embedded as a base64
    data URL (`logo.js`).
  - **On light backgrounds, recolour the logo itself to dark ink (#2a1d1a) with canvas
    `source-in`, keeping its transparency, and crossfade it to white as the background darkens.**
  - **Never** put a dark pill or box behind it.
- **End card (≈ last 3 s):**
  - The logo, 360–400 px wide, at y ≈ 330–600.
  - "SÖZÜMÜN CANI" in the episode font (≈ 52 px, letter-spacing 14), with a per-letter reveal
    synced to the spoken closing "Sözümün canı".
  - The word stays visible below.
- **Captions:**
  - Inter 400, 37 px, max width 820, line height 54, last line at y = 1555, centred.
  - Words reveal as spoken; the current word is highlighted in the accent colour.
  - A dark gradient scrim sits under the captions.
  - No caption where hero typography already shows the full line (verses, the reveal, the
    "Söz yerinə düşdü" outro).
  - Hold the first caption until a light paper scene ends.
- **Safe zones:**
  - Hero text between y ≈ 300 and 1400, and nothing important at x > 950 below y 1100 (Reels
    buttons).
  - No stray marks near letters: a dimple beside the final "N" read as an apostrophe.

## Audio
- **Separation:** Demucs `htdemucs_ft --two-stems=vocals --shifts 2 --overlap 0.5`.
  - Check levels: music must be ≈ −30 dB under speech, and vocal-stem gaps ≈ −50 to −64 dB.
  - Compare the separated voice with the original word by word via whisper.
  - If separation damages speech, stop and ask for a voice-only recording.
- **Voice:**
  - The stem, trimmed at T0, with only `highpass=f=70` and a 30 ms fade-in.
  - No denoising and no other processing.
  - A slightly softened "f" may appear; mention it.
- **Music:**
  - **ORIGINAL ONLY**, synthesised in Python (`shared/audiolib.py`). No stock, no public-domain
    recordings, no copyright questions: the user rejected a CC0 Chopin piece.
  - Approved: calm felt `piano()` plus warm `pad()`, slow arpeggios (step ≥ 0.45 s, velocity
    0.22–0.34), reverb 3.4–4.2 s, wet 0.36–0.42. Müjgan also used santur-like Karplus–Strong
    plucks in a D-Hijaz mode.
  - Follow the story: thin out or drop out for silence and tension, warm up on resolutions, and
    end on a soft final chord.
  - **Rejected:** busy guitar strumming, glockenspiel stabs, constant beats or pulses, trembling
    clusters. In the user's words: "Mahnı çox pisdir, adamın başına düşür."
- **SFX:**
  - Varied, one meaningful sound per visual event (ripples, ink, creaks, letter landings).
  - Soft and low-passed, gain 0.12–0.25 per event, light reverb (1.8–2.2 s, wet 0.22).
  - **No hissy high-frequency noise:** "silk" = bpf 600–2600 Hz + lpf 2200 Hz.
  - No cheap beeps.
- **Mix** (`ffmpeg -filter_complex`):
  - Set the voice to ≈ −14 LUFS (stem ≈ −9.4 LUFS → −4.6 dB), the music to ≈ −30 LUFS and the
    SFX to ≈ −29 to −30 LUFS.
  - Duck the music with `sidechaincompress=threshold=0.04:ratio=2.5:attack=120:release=700`.
  - Combine with `amix=inputs=3:normalize=0`.
  - Then run two-pass `loudnorm=I=-14:TP=-1.5:LRA=11:linear=true` at 48 kHz.
  - Targets: −13.9 LUFS, peak ≈ −3.5 dBFS.

## Render and encode (`project/tools/`)
- **Frames:**
  - Run `node tools/render.js <abs project dir> <out dir> <duration>`: 4 Chromium pages, PNG
    frames → libx264 crf 16 segments, then concat.
  - It takes ≈ 25 min per minute of video.
  - Await `document.fonts.load` for every face and `window.LOGO_READY` before rendering.
- **Fixes:** use `render_range.js <dir> <out> <startFrame> <endFrame>` and splice with ffmpeg
  `trim`/`concat`. Don't re-render the whole film.
- **Previews:** `still.js <dir> t1,t2,… <out>`. Check contact sheets every 2 s before the full
  render.
- **Final encode:** `libx264 -preset slow -crf 20 -maxrate 12M -bufsize 24M -profile:v high
  -level 4.2 -pix_fmt yuv420p -movflags +faststart`, AAC 256k 48 kHz.

## Verify the export (before delivering)
- **Old music gone:** correlation of the final audio with the Demucs music stem ≈ 0.02.
- **Voice intact:** correlation with the voice stem ≈ 0.99.
- **Narration:** re-transcribe the export in windows. It must start at the right word, contain
  every line and keep the original order.
- **Frames:** contact sheet every 2 s, plus the first and last frames. Look for overlaps, empty
  frames, clipped glyphs (e.g. a J's descender) and the logo position.

## Cover (Reel thumbnail)
- `project/cover.js` defines `window.cover()`. Render it with
  `node shared/tools/shoot_cover.js <abs project dir> x <out dir> <Name>` and save as JPG q95.
- **Layout:**
  - The logo, 230 px wide, at y = 345.
  - Under it, "SÖZÜMÜN CANI".
  - The big word in the episode's motif, e.g. ZƏNƏXDAN on its smile curve.
  - ONE short subtitle line quoted from the narration.
- Keep all key content inside the profile-grid crop (centre 1080×1350, y ≈ 285–1635).

## Instagram caption (approved format)
- **Don't repeat the narration.** The video already carries the captions; the post should create
  curiosity.
- **Structure:**
  1. Opening line.
  2. "Bu günün sözü: <Word>."
  3. One teaser built from narrated facts, ending in "Cavab videoda."
  4. "Qulağınız bizdə olsun."
  5. "🎙️ Araz Radio 103.3 FM".
  6. Hashtags.
- **Opening line:**
  - The first episode opens with «Qulaq gündə bir söz eşitməsə, kar olar.» and one line about
    the series.
  - The series line says "hər epizodda bir sözün mənasını və mənşəyini danışırıq". **Not
    "hekayəsini"**: the series doesn't tell stories.
  - When an episode has a quote, it opens with that quote.
- **Hashtags:** #SözümünCanı #ArazRadio #ArazFM #<Word> #AzərbaycanDili #SözünMənası.
- Don't invent the station's Instagram handle or airtime.
- **Approved examples:**
  - Məlal: "Bu günün sözü: Məlal. Ərəb dilindən gələn bu söz kədəri bildirir. Bəs niyə o,
    boşluq deyil, əslində doluluqdur? Cavab videoda."
  - Zənəxdan: opens «Xırda tellər zənəxdana düşübdü.» — Molla Vəli Vidadi, then "Hər gün
    üzünüzdə görünən bu incə cizginin adını bilirdinizmi? Cavab videoda."

## Working with the user
- Batch feedback rounds and make routine creative decisions yourself.
- When a request is ambiguous ("quote ilə başlasın"), state your interpretation and offer the
  alternative.
- Deliver the latest version clearly named (v2, v3…) and say which earlier files it replaces.
- Usage budget: do one episode per session and avoid unnecessary full re-renders.
