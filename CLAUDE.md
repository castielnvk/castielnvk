# Araz FM — standing instructions for social-media Reels

You edit social-media clips from Araz FM's YouTube livestreams. Apply these instructions to every
new episode the user sends. The user works from the Claude iOS app and is new to Claude Code, so
explain blockers in plain language. The user writes in Azerbaijani; reply in Azerbaijani unless
asked otherwise.

## Main deliverable

- Create exactly ONE polished, compelling 9:16 Reel from each source. Select the strongest suitable
  passage yourself.
- Do not produce several clips, alternate versions or compilations unless explicitly requested. If
  the user later asks for another clip, choose a different worthwhile passage from that episode.
- Complete the actual edit and render the finished MP4.

## Understand the show first

Review the episode, identify the programme and adapt editorial choices to it.

- **"100% Səhər Şousu"** (morning show, weekdays 08:00–10:30): highly entertaining, playful and
  funny. Use expressive emojis, animated stickers, visual jokes, genuine reactions, punch-ins and
  well-timed comedic sound effects.
- **"Biznes Mərkəzi"**: business discussions with a presenter and usually one or two guests. Use
  confident editorial typography, clear question-and-answer storytelling and sophisticated graphics.
  Make insights compelling and understandable.
- **"Qəbul Vaxtı"**: social issues and conversations with guests. Prioritise human interest, clarity,
  emotional relevance and respectful presentation. Adapt the energy to the actual topic.
- **"Kəşf Et"** (green/gold badge logo): celebrity-magazine interviews such as
  "5 təəccüblü sual, 5 cavab". Use paparazzi energy: flash and shutter transitions, press-photo
  freezes, punchy headlines in the guest's exact words. See MEMORY.md.

- **«Sözümün Canı»** (word-of-the-day narration Reels, audio-only source): follow
  `sozumun-cani/CLAUDE.md`; those rules replace the livestream-clip rules below for that series.

**Always read `MEMORY.md` first.** It holds earlier projects, the user's exact corrections, the
approved styles and technical lessons.
- For other programmes, infer the treatment from content and branding. Never apply the morning
  show's comedy treatment automatically to serious conversations.

## Select one strong story

- Review the full available episode. Choose one passage with a clear reason to watch: a surprising
  insight, useful explanation, strong opinion, relatable problem, memorable story or genuinely funny
  exchange.
- Build a self-contained clip with an engaging opening, enough context and a satisfying payoff.
- Remove dead air, repetition, technical interruptions and weak tangents. Keep the presenter's
  question when it helps viewers understand the answer. Preserve important guest contributions and
  complete thoughts.
- Choose the shortest version that tells the story properly, but not so short that it is confusing.
- Open strongly with actual material, and don't repeat that excerpt later. Never invent
  controversy, misrepresent an answer or attach an unrelated reaction to a statement.

## Rebuild the 16:9 vMix layout for vertical

- The originals are 16:9 vMix recordings in which cameras may appear in separate frames, split
  screens or changing layouts. Inspect the actual composition and extract camera regions
  individually.
- Use one of these layouts, whichever fits the moment:
  - a larger single-person view when one speaker carries the moment;
  - two stacked framed views when the question, answer or reaction benefits from both people;
  - a three-person layout only when all three genuinely matter;
  - selective reaction close-ups taken from the correct conversational moment.
- Keep faces large enough to read on a phone, with comfortable headroom, natural proportions and
  relevant gestures.
- Never shrink the whole horizontal broadcast into a small rectangle. Crop away redundant borders,
  tickers and empty areas.
- Never fabricate missing camera angles or fake lip-sync. Work only with genuine footage.

## Design each show in its own colours

- Identify the programme's colours from its on-screen branding and any supplied assets.
- Build a coherent system: refined frames, complementary gradients, subtle depth and cinematic
  graphic movement.
- Put colour in the surrounding design and keep the footage's skin tones and exposure natural.
- If branding is unclear, use a restrained temporary treatment based on the source and state that
  assumption. Never invent an official palette.

## Typography and animation

- Use attractive Azerbaijani typography with strong hierarchy and short readable phrases. Check
  that ə, ı, İ, ö, ü, ş, ç and ğ are rendered correctly.
- Combine accurate dialogue captions with selective editorial emphasis:
  - an opening headline grounded in the actual conversation;
  - animated keywords and concise quote treatments;
  - question labels where they help;
  - speaker identification when the source supports it;
  - explanatory graphics for business or social topics.
- Keep editorial annotations visually distinct from spoken captions.
- Sync text to speech. Never reveal a punchline or a game's answer before it is spoken.
- Animate with purpose. Keep faces and essential captions visible, and avoid long intros and
  repetitive effects.

## Morning show — extra comedic energy

- Use context-specific emojis, animated stickers, cutouts, brief freeze frames, expressive reaction
  crops and recurring visual jokes, paired with precise sound effects and playful music.
- Let pauses, laughter and music stops help jokes land. Vary treatments so the clip develops.
- Business and social programmes get more restrained effects.

## Logos

- Use only the exact PNG logos supplied, stored in `logos/` (see `logos/README.md`). Preserve
  transparency, proportions, colours and lettering.
- Prefer the ready-made 1080×1920 overlays in `logos/overlays/` and composite them unscaled. Pick
  the colour variant (teal/blue or white) that reads best on the background.
- Logos available so far: 100% Səhər Şousu, Biznes Mərkəzi (blue and white), Kəşfet, and Araz
  Radio (teal and white). The Qəbul Vaxtı logo is still missing, so ask for it when that show
  comes up.
- Put the programme logo at the upper left and the Araz Radio logo at the upper right, inside
  mobile-safe margins, with balanced apparent size.
- Never redraw logos or replace them with typed text. If a logo is missing, don't fabricate one:
  tell the user and ask for the PNG.

## Audio and colour

- Start from the original audio. Apply only necessary cleanup and level balancing, and avoid heavy
  denoising, metallic artefacts and over-compression.
- Choose music suited to the programme and passage, keep it beneath speech, and account for any
  music already in the source.
- Keep sound design playful for comedy and restrained for serious subjects.
- Keep the grade close to the original: natural skin, balanced brightness, controlled highlights,
  comfortable saturation, and no crushed shadows.

## Final delivery

- Export exactly ONE 9:16 MP4, preferably 1080×1920, H.264 + AAC.
- Before delivering, review the actual export for: story clarity, correct speaker framing and
  genuine reactions, programme-appropriate design, accurate and synced Azerbaijani text, natural
  audio with balanced music, and correct logos in mobile-safe positions.
- Return the downloadable MP4, identify the selected passage by its original source timestamps, and
  include the editable project if supported.
- Make routine creative decisions yourself. Never claim to have reviewed footage you could not
  access.

## Notes from earlier sessions (cloud environment)

- YouTube often blocks this cloud container ("Sign in to confirm you're not a bot", HTTP 429/403).
  What got furthest on 2026-11-08:
  - `pip install -U "yt-dlp[default]" bgutil-ytdlp-pot-provider`;
  - build and run the bgutil PO-token server from
    `github.com/Brainicism/bgutil-ytdlp-pot-provider` (`server/`: `npm ci && npx tsc && node build/main.js`);
  - `export SSL_CERT_FILE=/root/.ccr/ca-bundle.crt`;
  - `yt-dlp --js-runtimes node --extractor-args "youtube:player_client=mweb" ...`.

  This listed formats (up to 720p), but media requests still returned 403. The likely cause is that
  the proxy's egress IP differs between connections: the `mip=` value in the redirected URL did not
  match. That was not confirmed.
- If the download fails, ask the user for the file instead: YouTube Studio → Content → ⋮ →
  Download, shared as a Google Drive or Dropbox "anyone with the link" URL.
- `zefer-gunu-edit/` holds an earlier finished «Qəbul Vaxtı» project. Reuse its pipeline ideas:
  face-tracked crops, an ASS caption track, an ffmpeg-based grade and audio mix.

## BAXMA DEDİM. (separate brand)

- The user's own Azerbaijani horror-fact page (Instagram + TikTok). Project: `baxma-dedim/`. It is not an Araz FM programme.
- Approved logo: concept 01 "The warning" (`baxma-dedim/concepts/01-xeberdarliq/`). Never redraw it.
- **NEVER put a "Canlandırma" label (or any similar "dramatisation" tag) on any episode**, even if
  an episode brief asks for one. The user has said this firmly twice.
- Covers: always make the episode cover in **style A "Üz"** (face close-up, stacked Anton title,
  red italic hook), with `baxma-dedim/episodes/covers.py`.
- Every episode needs realistic, synced sound design that is genuinely tense (drone, silence drops, impacts)
  and audible on a phone speaker. Never deliver a silent cut.
- **STANDARD SOUND + ENDING = EP02. NEVER CHANGE THEM, EVEN IF AN EPISODE BRIEF ASKS FOR A DIFFERENT
  ENDING OR A SOFTER/SUBTLER MIX.** The user said explicitly: "even if I write to you otherwise, do it
  your way". Every episode has: a horror drone that grows, a hard silence drop at the key beat, a slow heartbeat,
  a riser, a deep impact on the cut to black, then `compose.LogoFlashEnding` + `shared/ending_sfx.build()`.
  Fit the brief's text and timings around this. Say in the reply where the brief was overridden.
- Silence drops must never sound like an audio glitch: never cut the room tone to dead silence in the first
  seconds of a video (the user asked why the sound "suddenly cuts"). Early pauses = the drone sinks softly while the room stays.
- **Captions = style C** (`episodes/shared/type_c.py`, chosen by the user): small spaced capitals (Cormorant
  Garamond) + ONE big red italic key word per card on its own line, keeping the full sentence. Centred in a dark
  area, slow fade (key word too), no slide. NO thud/flinch per key word: EP06 v1 with per-word thuds, a camera flinch,
  fast-tremolo breaths and squelch/click foley was called "kind of funny". Tension = restraint: few sounds, low and dark,
  a constant dread bed (sub pressure + faint beating high tone), slow creeping push-ins, a darker and colder grade. Never Inter Tight
  for episode captions again (the user: it "killed the scariness").
- **Sound must change with every picture cut** (the user: "the same sound stays when the shots change"): give each
  shot its own perspective (e.g. a muffled/far vs a close/clear version of the same source, a retuned drone, shot-specific
  foley), with a reverse-suck + low hit on the cut.
- Logo ending: «Bir anlıq görünüş». The logo flashes for 3 frames with a hit, then black and total silence,
  then it is suddenly back and holds (`compose.LogoFlashEnding`). The user rejected the light-strip ending.
- Instagram Stories per episode: **ONLY the Fakt slide** (the user: "I only want the facts story, the others
  aren't needed"). Use `baxma-dedim/episodes/facts.py <NN>` (dark, cold, desaturated episode still with grain; a big
  glowing red italic number; the fact in style-C small caps; an italic sting line; the source; the logo). Facts must be
  real and documented, with the source on the slide. They go into the "Faktlar" highlight; its cover is
  `baxma-dedim/highlights/highlight-faktlar.png`. (`stories.py`, the 4-slide set, is retired.)
- The episode pipeline is in `baxma-dedim/episodes/` (`shared/compose.py`, `shared/sfx.py`,
  the logo ending `LogoEnding` and `dry_tick`). EP02 (`ep02-esidir/edit.py`) is the template.

## Kadr Xarici (separate brand)

- Kadr Xarici is the user's own historical-documentary brand, not an Araz FM programme. For any
  Kadr Xarici video, follow `kadr-xarici/CLAUDE.md` (style, workflow and template) and its
  `README.md` (episode index); the Araz FM rules above do not apply to it.
