# Project memory — notes from earlier sessions

Read this before starting new work. It records what was already made, what the user liked or
rejected, and the technical lessons. Each entry was written by the session that did the work.

## Projects

### Victory Day vertical film — "Bir xəbər. Minlərlə xatirə." (7 Nov 2026)
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

## Technical lessons (cloud environment)
- YouTube downloads usually fail here: bot checks, 429 errors, and 403 on media requests even with
  PO tokens. Look for another copy of the same broadcast (for example newstube.az or the
  publisher's own site), or ask the user for the file.
- New download hosts must be added to the environment's network allowlist.
- FFmpeg ignores the proxy, so download with curl or yt-dlp first and process locally. For flaky
  hosts like mod.gov.az, use `curl -C -` with retries.
- Transcription: faster-whisper. Set `HF_HUB_DISABLE_XET=1` and pass audio as a numpy array. It
  hallucinates on silence ("Altyazı M.K.", repeated lines), so check levels.
- Fonts: get TTFs from npm `@expo-google-fonts/*`; the npm registry is reachable.
- Review contact sheets of design frames and transitions before delivering. They catch empty
  frames, gaps and muddy dissolves.
