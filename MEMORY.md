# Project memory — notes from earlier sessions

Read this before starting new work. It records what was already made, what the user liked or
rejected, and the technical lessons. Each entry was written by the session that did the work.

## Projects

Priority order (as the user stated): 1) Sözümün Canı, 2) radio show edits, 3) Kəşf Et and other
programmes, 4) everything else.

### 1. Sözümün Canı — word-of-the-day Reels (Nov 2026)
- **What:** cinematic 9:16 Reels (1080×1920, about 60–72 s) for the Araz Radio 103.3 FM segment
  "Sözümün Canı". Each episode explains one Azerbaijani word. The user supplies the narrated MP3
  (a radio mix with a music bed). Make a matching 1080×1920 Reel cover JPG for each episode.
- **Episodes delivered — all archived in `sozumun-cani/` (final MP4s, covers, source MP3s,
  editable projects, separated voice/music/SFX tracks; see `sozumun-cani/README.md`):**
  1. Müjgan (eyelash = arrow, Persian origin) → `Sozumun_Cani_Mujgan_v2_9x16.mp4`
  2. Məlal (Arabic origin; sorrow and heart-weariness) → `Sozumun_Cani_Melal_9x16.mp4`
  3. Zənəxdan (chin dimple; opens with Molla Vəli Vidadi's lines) →
     `Sozumun_Cani_Zenexdan_9x16_v4.mp4`
- **Intro rule:** only the first episode (Müjgan) keeps the series intro ("Sözümün canı", the proverb
  "Qulaq gündə bir söz eşitməsə kar olar", "qulağınız bizdə olsun"). Later episodes start
  directly on that day's word. "Quote ilə başlasın" means open on the quoted poem lines.
- **Music:**
  - Remove the original background song by separating out the voice, then add new music. Never
    layer music over the old song.
  - **Original music only.** The user doesn't want copyright issues, so no stock and no
    public-domain tracks (a CC0 Chopin piece was rejected).
  - Liked: calm felt piano with warm pads (Məlal); santur-like plucks in a Hijaz mode (Müjgan).
  - Rejected: busy synth guitar strumming, glockenspiel stabs and constant beats — "Mahnı çox
    pisdir, adamın başına düşür."
- **SFX:** varied and timed to the visuals, but soft and low-passed. Harsh hissy high frequencies
  were rejected ("saçlar tökülən səs çox harsh").
- **Logo:**
  - White Araz Radio PNG, small at top centre (y ≈ 150), large on the closing card.
  - On light backgrounds, recolour the logo itself dark (keeping transparency) and fade it to white
    as the background darkens. Never put a dark pill behind it.
- **Style:**
  - Procedural editorial motion graphics in an HTML canvas (animated type plus vector
    illustration). No AI or photo imagery.
  - Each episode gets its own palette and font:
    - Müjgan: gold on indigo, Cormorant Garamond.
    - Məlal: dusk slate, silver and amber; Playfair Display + Lora; rain and reflections.
    - Zənəxdan: dawn cream paper, peach and rose-gold; Fraunces; a "smile line" motif.
  - Captions: Inter 37 px, word-by-word highlight, dark gradient scrim, last line at y 1555.
  - Mix: voice at about −14 LUFS, music about 16 dB under with gentle ducking, final −14 LUFS /
    −1.5 dBTP.
- **Open questions (not yet answered by the user):**
  - Transcript readings: "dərman atırıq" vs "atıraq"; "gündəlik qayğılar".
  - Spellings: "zənəxdan" (pronounced zənəqdan); "yumşaldan" (spoken yumuşaldan).
  - Whether to remake Məlal's music.

### 2. Radio shows (100% Səhər Şousu, Qəbul Vaxtı, Biznes Mərkəzi, Reel covers)
_(notes pending)_

### 3. Kəşf Et — Gülay Zeynallı, "5 təəccüblü sual, 5 cavab" (7–8 Nov 2026)
- **What:** a celebrity-magazine 9:16 edit of the Kəşf Et (Araz Radio 103.3 FM) segment with
  singer Gülay Zeynallı.
  - Source: one iPhone clip, `IMG_7215.MOV` (85 s, HEVC HLG HDR, 120 fps, fixed camera), delivered
    through Google Drive.
  - Brand guide: `KESFET_PROJECT.pdf`. Font Archivo Expanded. Palette Deep Green, Berry Blush,
    Forest Mint, Aqua Breeze, Golden Peach and Ivory Sand.
- **Final:** `Gulay_Zeynalli_Kesf_Et_v2.mp4` (53.5 s), with an `.srt` and a project zip, delivered by
  file card. Nothing was pushed to GitHub. One caption is uncertain: "Hamısıyla münasibət çox
  gözəldir" (possibly "münasibətim").
- **User rejected v1** (88 s, elegant green/gold, ML-denoised voice). The complaints were:
  - the processed voice sounded worse than the source (metallic, filtered, over-compressed);
  - it was boring, repetitive and not trimmed enough;
  - the opening hook was repeated later in full.
- **What the user wanted instead:** a celebrity-magazine/paparazzi energy, with flash and shutter
  transitions, freeze frames, punchy headlines and a quiet energetic instrumental.
- **Logos:** the Araz logo must be a white PNG. The user then supplied a 1080×1920 overlay: Kəşf Et
  upper left, white Araz upper right. Use it 1:1 and unmodified; only a soft shadow is allowed.
- **Cut complaint, made twice:** "istəyire- kəsilir, İSTƏYİRƏM olmalıdır, söz tam
  səslənməlidir." Never clip a word ending; the user listens closely.
- **Approved v2 style:**
  - Structure:
    - cold open "Qəlbim artıq qırılmır. O, əvvəllər idi.";
    - a flash into a tilted white-border "press photo" freeze with the title;
    - question cards "SUAL 0X / 05" (category in Archivo Expanded ExtraBold, question in Playfair
      Display italic) over blurred, green-tinted footage, with shutter transitions;
    - freeze-frame headlines in her exact words, on berry/deep-green bars.
  - Captions: Archivo SemiBold 56 px, ivory with a shadow, near the bottom.
  - Music: original 120 BPM fashion-house, about 18 dB under speech. SFX: shutter clicks, flash
    whoosh, low thump.
  - Grade: HLG→SDR with zscale and hable tonemapping. Skin stays natural.
  - Editing: the journalist's voice was removed by editing alone, and the questions appear only as
    text.

### 4. Other: Victory Day vertical film — "Bir xəbər. Minlərlə xatirə." (7 Nov 2026)
- **What:** a 35-second vertical documentary for Victory Day (8 November). It was not made for a
  radio programme. Delivered as `bir_xeber_minlerle_xatire_1080x1920.mp4` (v2, 43 MB); v1 was
  `zefer_gunu_8noyabr_1080x1920.mp4`. The user has not yet given feedback on v2.
- **Sources (real archive only):**
  - President's address, 8 Nov 2020 ("Şuşa şəhəri işğaldan azad edildi!"), from the newstube.az
    copy embedded on Trend (newstube embed 118062). It matches YouTube 8q50s0FqAp8 and the
    president.az transcript.
  - Baku celebrations, 8 Nov 2020: newstube 98340 (a 480p phone video).
  - Shusha footage from the Ministry of Defence: mod.gov.az/videos/0_58.mp4, published 9 Nov 2020.
    Label it "Noyabr, 2020", never as 8 November.
- **User rejected v1** as "footage joined together" and asked for a full creative rebuild with motion
  graphics as a central storytelling layer, expressive typography and cinematic sound.
- **v2 style:**
  - colours: ivory paper #F4EFE4 with grain, ink #161820, flag colours as accents;
  - a recurring 6 px red line (#E22634) that links the scenes;
  - type: Inter Tight only, 72 px margins, scene labels "01 — XATİRƏ … 06 — EHTİRAM";
  - music: "Dreams Become Real" by Kevin MacLeod (CC BY 4.0, which must be credited in the post);
  - mix: −14.8 LUFS, original speech untouched;
  - export: 1080×1920, 25 fps.

### 5. Other: Bayraq Günü Reel from a viral TikTok clip (9 Nov 2026), in `bayraq-gunu-edit/`
- A 20 s Reel of a child trying to reach a torn flag on a lamp post. Delivered as
  `Bayraq_Gunu_9Noyabr_9x16.mp4`; no feedback yet.
- **The user was angry that I started rendering without first agreeing the plan with them**
  ("Hazırlamadan əvvəl mənimlə məsləhətləş"). For new creative requests, propose the plan (story,
  texts, music, length) and wait for approval before rendering.
- User's choices:
  - no voice-over, on-screen texts only;
  - national music for Flag Day;
  - 20 s length (they believed shorter avoids copyright flags);
  - Araz logo top centre;
  - "more motion, cinematic, premium".
- Music: national-anthem finale, US Navy Band recording (public domain), with cuts on its accents.

## User preferences (across all projects)
- Use only real footage. Never fabricate archive material, reactions, voices or historical scenes,
  and never use cloned or generated voices.
- Agree the creative plan with the user before rendering a new project.
- Always deliver a real, verified MP4, never an HTML preview. Never claim success before checking
  the file.
- Inspect sources before editing: contact sheets, transcription and real timecodes. If a source is
  inaccessible, say exactly which one before changing the story.
- Don't stretch low-resolution footage; use intentional framed windows instead.
- Avoid these:
  - aggressive zooms or fake camera shake;
  - particles or fake scratches;
  - generic templates or rounded cards on every scene;
  - cheap synthesised beeps.
- Graphics and typography should tell the story, not just caption it.
- **Audio:** keep the original voice with only minimal level balancing. Never use heavy ML denoising
  (DeepFilterNet etc.), which the user rejected as metallic.
- **Cuts:** never clip a word or its ending. Use about 12 ms fades at cut points; longer fades eat
  syllables. Bring SFX and music swells in after the last word.
- **Editing:** keep it as short and punchy as the story allows. Don't repeat the opening hook later.
- **Logos:** use the user's supplied overlays exactly as provided.
- **Music:** prefer original, self-composed music. The user wants no copyright issues and dislikes
  busy or annoying tracks.

## Technical lessons (cloud environment)
- YouTube downloads usually fail here: bot checks, 429 errors, and 403 on media requests even with
  PO tokens. Look for another copy of the same broadcast (for example newstube.az or the
  publisher's own site), or ask the user for the file.
- New download hosts must be added to the environment's network allowlist.
- FFmpeg ignores the proxy, so download with curl or yt-dlp first and process locally. For flaky
  hosts like mod.gov.az, use `curl -C -` with retries.
- Transcription: faster-whisper. Set `HF_HUB_DISABLE_XET=1` and pass audio as a numpy array. It
  hallucinates on silence ("Altyazı M.K.", repeated lines), so check levels.
- Fonts: get TTFs from npm `@expo-google-fonts/*` or `@fontsource/*`; the npm registry is
  reachable, while Google Fonts and GitHub raw may be blocked. Merge the latin and latin-ext
  subsets with fontTools to get ə.
- Google Drive files download via `drive.usercontent.google.com/download?id=…&confirm=t`.
- Whisper word timestamps drift 0.3–0.6 s. Verify cut points with a 10–20 ms energy envelope.
  large-v3 is the best model for Azerbaijani.
- Use opencv-python-headless 4.10; 5.x lacks CascadeClassifier.
- Voice/music separation: Demucs `htdemucs_ft --two-stems=vocals --shifts 2` works well.
- For long files, transcribe in windows, because whole-file runs drop tail segments. Don't use
  initial_prompt on music-heavy parts.
- HTML-canvas rendering: Playwright Chromium, 4 parallel pages, PNG frames piped to ffmpeg
  libx264. It takes about 25 min per minute of video. Embed logos as base64 data URLs, because
  file:// images taint the canvas.
- Music downloads: Pixabay and chosic are blocked. archive.org, FMA and incompetech are reachable.
- HDR iPhone footage: convert HLG→SDR with zscale + `tonemap=hable` (npl=100).
- Review contact sheets of design frames and transitions before delivering. They catch empty
  frames, gaps and muddy dissolves.
