# Project memory — notes from earlier sessions

Read this before starting new work. It records what was already made, what the user liked or
rejected, and the technical lessons. Each entry was written by the session that did the work.

## Projects

Priority order (as the user stated): 1) Sözümün Canı, 2) radio show edits, 3) Kəşf Et and other
programmes, 4) everything else.

### 1. Sözümün Canı
_(notes pending)_

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

## User preferences (across all projects)
- Use only real footage. Never fabricate archive material, reactions, voices or historical scenes,
  and never use cloned or generated voices.
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
- HDR iPhone footage: convert HLG→SDR with zscale + `tonemap=hable` (npl=100).
- Review contact sheets of design frames and transitions before delivering. They catch empty
  frames, gaps and muddy dissolves.
