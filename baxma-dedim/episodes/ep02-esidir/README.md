# BAXMA DEDİM. — EP02 «Bəlkə hələ eşidir»

`Baxma_Dedim_EP02.mp4`: 1080×1920, H.264 + AAC 48 kHz stereo, 24 fps, 15.0 s, −19.6 LUFS.
The source clip's audio is muted. The soundtrack mixes designed sounds (`../shared/sfx.py`) with recorded
library sounds (`../shared/sfx_library/`, Mixkit free license).

**v2 sound (tension pass):** a horror drone grows as the hand approaches. When the hand stops, the drone and
room tone cut out together for 1 s of real silence. A slow heartbeat then starts and the drone creeps back,
with a riser into the cut. At 10.0 s a deep impact lands, with low pressure under the black card. The logo ending has a reverse
swell into a flickering light strip and a low hit on BAXMA. DEDİM. arrives with the tick plus a sub-hit, and the hard cut
chops the boom off so only the tick keeps ringing.

## Edit (times are in the finished video)
| Time | Picture | Text | Sound |
|------|---------|------|-------|
| 0.00–1.20 | Hold on source frame 0: the resting hand is visible from frame one | "Yanındakı adam / sənə cavab vermir." at once | Room tone fades in |
| 1.20–4.87 | Source frames 0–88: the second hand approaches | (stays until 3.85) | Close, dry fabric rustle that follows the hand's speed |
| 4.05 | — | "Amma alimlər bir şey görüblər." | One faint, distant designed tone |
| 4.87–10.0 | **Still hold on frame 88**, the last frame with a clear gap (the source touches from ~frame 92); slow push-in and live grain | 5.85: "Ömrünün son saatlarında olan / bəzi insanların beyni / hələ də səsə reaksiya verib." | Room tone drops out for 1 s when the hand stops, then returns faintly |
| 10.0–13.0 | Hard cut to near-black | "Deyilən sözləri / anlayıb-anlamadıqlarını / bilmirik." | Silence |
| 13.0–15.0 | Logo ending: a light strip opens on BAXMA; DEDİM. appears at 13.80; hard cut to black at 14.55 | — | A dry tick at 13.80, whose tail rings past the cut |

No "Canlandırma" label (the user's standing rule).

## Files
- `edit.py` is the whole edit. The CONFIG block holds all timings, text, layout and levels.
- `stems/` holds one WAV per layer, aligned to the timeline: room tone, fabric rustle, distant tone, horror drone, heartbeat,
  riser, cut impact, black pressure, the logo reverse swell / BAXMA hit / DEDİM. sub-hit, and the logo tick,
  `logo_tick_standalone.wav` (the ending tick starting at 0, ready to reuse) and `mix.wav`.
- `layers/*.svg` are the editable vector caption layers and the logo layers.
- `covers/02-cover-A-uz.*` is the episode cover in style A.

## Reusing the ending
`compose.LogoEnding(layers_dir).frame(t)` together with `sfx.dry_tick()` placed at `ENDING["DEDIM_AT"]`
(see `edit.py`). The timings are in `compose.ENDING`.
