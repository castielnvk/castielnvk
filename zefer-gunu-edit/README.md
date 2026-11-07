# Zəfər Günü — «Qəbul Vaxtı» vertical cinematic edit

A 9:16 cut (1080×1920, H.264/AAC, 30 fps) of the «Qəbul Vaxtı» (Araz FM 103.3) Victory Day segment
presented by Elnarə Sadıqova. The finished file is `Zefer_Gunu_Qebul_Vaxti_9x16.mp4`.

## Source
The supplied file is an iPhone screen recording of the 16:9 vMix programme. It is 2:02 long,
recorded at 2622×1206 with variable frame rate. The station's lower-third banner is burned in.
It contains three camera states:

| Source time | Programme picture | Used as |
|---|---|---|
| 0:00 – 0:44.39 | Elnarə close-up (the President's speech plays as audio) | face-tracked 9:16 crop with a slow push-in |
| 0:44.39 – 1:38.20 | studio wide shot with guests | tight crop on Elnarə only; guests stay out of frame |
| 1:38.20 – 2:02 | three-way split screen | Elnarə's centre panel only |

The recording contains no picture of the President. His speech is heard over Elnarə listening, so that
is how it appears in the edit. No camera angle was invented, and no speech or lip-sync was generated.

## Edit decision list (output time)
| Output | Content |
|---|---|
| 0:00 – 0:59.4 | **Protected opening**, untouched and in order: President's speech, then Elnarə listening, then her full introduction |
| 0:59.4 – 1:01.8 | Title break "ZƏFƏR GÜNÜ" over an illustrative flag scene, placed in the natural pause after "…vətən naminə döyündü." |
| 1:01.8 – 1:46.0 | Her remarks (source 0:59.4 – 1:43.63), with brief illustrative flag/dawn scenes while her voice continues |
| 1:46.0 – 2:00.4 | Source 1:46.5 – 2:00.87. The repeated phrase "vətənpərvərliyimizi nümayiş etdirərək" was trimmed |
| 2:00.4 – 2:08.8 | End card while the music rises. The source recording itself stops mid-sentence ("…ki, biz artıq…"), so the edit ends on "…qəhrəmanlıq zəfərlə yekunlaşdı." |

## Pipeline (scripts in this folder)
- `music.py`: an original score (piano, strings, cello, harp; D major, about 69 bpm). Bars are placed on the title break and the end-card arrival. It is rendered with FluidSynth and the FluidR3 GM soundfont.
- `flag_scenes.py`: procedurally rendered, clearly illustrative flag scenes. They use the official flag construction (1:2 ratio; #00B5E2 / #EF3340 / #509E2F; crescent and eight-pointed star).
- `assemble_video.py`: per-camera crops (YuNet face tracking for the close-up), a gentle grade (highlight roll-off, no crushed blacks, saturation near the source, soft bloom, fine grain) and the dissolves.
- `mix_audio.py`: the original voices with light cleanup only (high-pass, mild FFT denoise, light de-ess, small EQ). Dialogue is set to about −16 LUFS, the music level is automated with light ducking, and the transitions get subtle air swells.
- `captions.py`: the ASS caption/title track. Azerbaijani text was checked against Whisper large-v3 word timings and corrected for orthography (ə, ı, İ, ö, ü, ş, ç, ğ).
- `make_gradient.py`, `finalize.sh`: the legibility gradient and the final encode.
