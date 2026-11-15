# Kadr Xarici — standing instructions for documentary Reels

Kadr Xarici is the user's **own** Azerbaijani media brand: short historical-mystery documentaries
about forgotten places and stories of Baku. It is **not** an Araz FM programme. The root `CLAUDE.md`
rules for Araz FM (radio clips, Araz logos, original-only music) do not apply here; the cloud notes
and general user preferences in `../MEMORY.md` still do. Reply to the user in Azerbaijani.

Read this file, then `README.md` (episode index and status), before starting a new episode.

## 1. What the user sends and what to deliver

**Input per episode:** 10–15 AI-animated vertical clips (720×1280 or 704×1280, 24 fps, 6–11 s each),
one ElevenLabs Azerbaijani voice-over MP3 (60–100 s), the full script with bracketed emotion tags,
and a long English brief. The logo is already in `template/brand/kadr_xarici_logo.png`.

**Always deliver, without being asked:**
1. One 1080×1920 MP4, H.264 + AAC stereo, at the clips' native 24 fps (say why if the brief asks for
   30), about −14 LUFS / −1.4 dBTP, burned-in subtitles. Keep the file under 100 MB so it can be
   committed (CRF 22, maxrate about 7.3–8.5 Mb/s).
2. A 1080×1920 **thumbnail** in the same style as the video (standing rule, 14 Nov 2026: "Həmişə
   hər videodan sonra bunu et. Stilistika eyni olsun").
3. An SRT file with exactly the burned-in subtitle timing.
4. `CREDITS.md`: music and SFX with URLs and licences, the caption credit line, and a timeline table.
5. An episode folder `kadr-xarici-<slug>/` containing the deliverables, `project/` (scripts and
   voice-over) and `stems/` (voice/music/SFX as m4a). Commit it, and add a short entry to
   `../MEMORY.md` and `README.md`.

Send the MP4, thumbnail, SRT and credits with SendUserFile. Never claim to have *listened*: say the
mix was measured and checked frame by frame, and ask the user to confirm it by ear.

## 2. Working rules (user corrections)

- **Never** put an "Sİ ilə canlandırma" / AI-generated label on the video ("SI ile canlandirma
  yazma", BUM, 14 Nov 2026).
- If you ask the user to choose between options, **wait for the answer** before starting. ("Bir
  dayan da. Mən başla dedim?", 14 Nov 2026.) When they say "Sənə buraxıram" or "do all of them",
  you may proceed on your own.
- Lead with the episode's **central question**, on screen from frame 0 and on the thumbnail. The user
  said the core of the tram film was "Bakıda tramvaylar niyə yox oldu?". Treat this as the default
  hook pattern.
- Music: **find existing licensed music online**. The Kadr Xarici briefs ask for this explicitly,
  unlike Araz FM, where only original music is allowed. Use only tracks whose licence you can verify
  (Kevin MacLeod / incompetech, CC BY 4.0, has worked). Say that attribution is required and give
  the caption line.
- Do not fabricate history, routes, maps, people, or "real archive" labels. If the footage cannot
  show something (no past scenes, no verified map), say so and solve it with grade, sound or
  typography. Never present 2002–03-style footage as the exact event the narration dates.
- The voice-over is fixed: never speed it up or cut words. Subtitles follow the script spelling; flag
  spoken differences (e.g. "yeniliydi"/"yenilik idi", "biriydi"/"biri idi", "səssizdi"/"səssizdir")
  instead of silently changing either.
- Make routine creative decisions yourself and take creative ownership, but report every
  compromise honestly in the final message.

## 3. House style — established in 3 delivered films (BUM, Tramvay v2, Fantaziya)

None of these has been explicitly approved or rejected yet, apart from the rules in §2. Keep the
**identity** below; vary the per-episode ideas (§4).

**Identity (keep):**
- Mood: mysterious, cinematic, historical, restrained. Documentary, not a music video or a CapCut
  template. No glitch, shake, particles or fake scratches; no flashy templates.
- **Type:** Playfair Display (Bold for years and hero words, Medium Italic for names, quotes and
  teasers) plus Inter (SemiBold/Bold) for subtitles and small tracked gold labels.
  Colours: ivory `(244,238,226)` and gold `(236,200,132)`, soft drop shadows, no boxes or pills.
- **Subtitles:** Inter SemiBold 70 px, ivory, centred at y≈1390, max width 950 px, line height 92.
  Key terms (years, names, places, the episode's keywords) in Inter Bold gold. Words brighten from
  42 % to 100 % as they are spoken, with a 12 px rise. Short natural phrases (2–5 words). A dark bottom
  gradient scrim; a top scrim that deepens while a title is up. Inter SemiBold 56 px (BUM) was felt
  to be too small for phones and was enlarged in Tramvay v2.
- **Editorial titles** (distinct from subtitles), top third, timed to the spoken word: small tracked
  gold label (e.g. "SOVET DÖVRÜ", "MƏNBƏLƏRƏ GÖRƏ") + big Playfair year or word (130–250 px) +
  italic gold or ivory line. Never reveal a fact before it is spoken.
- **Logo:** the supplied white PNG, unaltered, cropped to the artwork. Watermark 236 px wide at
  (54, 150), opacity 0.9, from frame 0; it fades as the ending starts. End card: 700 px centred on
  black, a gold hairline grows under it, and a soft synthesised low impact plays.
- **Ending (signature):** the last shot shrinks into a tilted photographic print with an ivory border
  and slides out of frame; on black, "kadr xaricində qaldı." appears word by word in Playfair Italic
  104 px, synced to the whisper, then the logo. The voice gets +1.5 dB on the whisper. Total outro
  ≤ 4 s after the last word.
- **Grade:** unify all generators. Historical: sepia/silver tone map with highlight roll-off, grain
  0.025, vignette 0.34. Modern: desaturated, cool, cinematic. Light 3–6 % push-ins, never aggressive.
  Gentle projector flicker only on early-cinema scenes.
- **Sound:** voice chain = highpass 70, −1.5 dB @220, +1.2 dB @3.5 k, deesser, 2:1 compression, RMS
  about −19 dBFS. Music is 10–14 dB under the voice, with 6.5 dB side-chain ducking and swells in
  pauses. SFX are low-passed (no harsh highs), placed per shot, about −30 to −44 dB. Synthesised sub
  "thumps" mark key reveals (years, the turning point, the logo). Master: +3.5 dB, then a limiter at
  0.84 → about −14.3 LUFS.
- **Pacing:** no slow intro; something visually interesting and the question in the first second.
  Change the picture every 2–4 s (cut or punch-in inside a long shot). Allow a meaningful pause before
  the main revelation (dip to black or a music drop of 0.3–1.5 s).

## 4. Per-episode creative toolbox (experiments — pick what serves the story)

| Technique | First used | Status |
|---|---|---|
| Hook question on frame 0 ("Bakıda tramvaylar NİYƏ YOX OLDU?", "Bura bir vaxtlar NƏ İDİ?") | Tramvay v2, Fantaziya | Requested by the user in spirit; default |
| Then/now split screen (past top, present bottom, gold divider, labels) | Tramvay v2, Fantaziya | Unreviewed |
| Animated counter (117 → 0 KM, 0 → 117 km on a gold line) | Tramvay | Unreviewed |
| Schematic route line (two dots + gold line, not a map) | Tramvay | Unreviewed; never invent geography |
| Shots shown as tilted photo prints ("köhnə fotolarda") | Tramvay | Unreviewed |
| Recurring sound motif (tram bell → one last strike → silence) | Tramvay | Unreviewed |
| Mid-video teaser line plus a 0.5 s music drop (around 40–45 s) | Tramvay v2 | Unreviewed |
| Two-world grade: warm "memory" (bloom, light breathing, water/murmur) vs cold dusty present, from the same footage | Fantaziya | Unreviewed |
| One warm flash and one sound layer per listed word, then a hard cut to silence | Fantaziya | Unreviewed |
| "Mənbələrə görə" numbered list (01, 02, 03) and a quote card | Fantaziya | Unreviewed |
| Light-leak transitions and a dip to black before the key year | BUM | Unreviewed |

New ideas are welcome. Keep the identity in §3, explain the idea in one line in the final message,
and record it in this table with its status.

## 5. Workflow (template in `template/`)

1. Make an episode working folder in the scratchpad. Copy in `template/*.py` and `template/tools/`,
   then add `src/c01..cNN.*` (in upload order), `src/vo.mp3` and `src/logo.png`
   (= `template/brand/kadr_xarici_logo.png`). Run `tools/setup.sh` once per container.
2. **Analyse:** `tools/contact_sheets.sh`, then look at every sheet. Note each clip's subject, era,
   motion, best seconds and AI defects (frozen people, deforming buildings). Use only clean seconds.
3. **Voice:** `python3 tools/transcribe.py "<names, dates, rare words>"` (faster-whisper large-v3),
   then `python3 tools/pauses.py`. Write `common.py`: `CHUNKS` as `"word@vo_time"` strings, with `*`
   for gold words; `PAUSES`; `SKIP_SUBS` for lines shown as a quote card; `OFF` (voice offset,
   0.15 s); `DUR`. Set word onsets after pauses to the pause end (whisper is early).
4. **Edit:** in `render.py` edit `SHOTS` (time, clip, source in-point, speed, zoom path, grade or `k`
   warm→cold, transition), `TITLES`, optional split screen and overlays, and the `END_*` times.
   Check with `python3 tools/stills.py qc/a.jpg=t1,t2,...` and look at every sheet before the full
   render.
5. **Full render** in the background: `nohup python3 render.py video.mp4 &`. It takes about 20 min
   for 90 s on 4 CPUs. Never start a second process writing the same file.
6. **Audio:** write `mix.py` (music research → `dl/music`; CC0 SFX from bigsoundbank:
   `https://bigsoundbank.com/UPLOAD/flac/<id>.flac` or `/UPLOAD/bwf-en/<id>.wav`; Wikimedia Commons
   rate-limits this container). Print the per-3-second voice/music/SFX table and keep music at least
   8 dB under the voice.
7. `python3 tools/srt.py Name.srt` and `python3 thumb.py`, then look at the thumbnail.
8. `tools/finalize.sh Out.mp4`: encode, decode check, `qc/final.jpg` contact sheet, loudness. Look at
   the sheet and close-up strips of the hook and the ending.
9. Package, write the credits, commit and push, update `README.md` and `../MEMORY.md`, and send the
   files.

**Thumbnail recipe** (`thumb.py`): past frame on top (0–1000 px), present below, a dark band at
y≈1010, logo 360 px above the title. Stack: gold tracked label (y≈706) + gold hairline, a huge
Playfair Bold hook (ivory) + gold Playfair Bold question, then an italic teaser. Keep all text
inside the centre square (profile-grid crop).

## 6. Licensed sources already used (avoid repeating a track unless it fits)

- BUM: "Echoes of Time v2". Tramvay: "Colorless Aura". Fantaziya: "Lightless Dawn". All are by
  Kevin MacLeod (incompetech.com), CC BY 4.0; credit required. The direct file is
  `https://incompetech.com/music/royalty-free/mp3-royaltyfree/<Title>.mp3`.
- Auditioned but not used: Dark Times, Deep Haze, Tempting Secrets, Comfortable Mystery, Long Note
  Four, Past the Edge, Dreamy Flashback, Heartbreaking, At Rest, Memory Lane, Lost Time, Time
  Passes, Sad Trio, Bittersweet.
- SFX IDs used are listed in each episode's `CREDITS.md` (projector 0065, tram 3374/3538/3539/3541,
  bell 2115, room tone 2135, footsteps 0514, water 0913/1081/1384/1386, murmur 3542/0642, wind 1714,
  whoosh 1795, and others).
