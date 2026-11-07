# Kəşf Et — Gülay Zeynallı: «5 təəccüblü sual, 5 cavab»

Vertical (9:16) entertainment-magazine edit of the Kəşf Et / Araz Radio 103.3 FM interview.

| Deliverable | File |
|---|---|
| Finished video, 1080×1920, 30 fps, H.264 High + AAC 256 kbps 48 kHz, 88.3 s, −14 LUFS / −1.4 dBTP | `export/Gulay_Zeynalli_Kesf_Et_5_sual_5_cavab.mp4` |
| Azerbaijani subtitles (same text as burned-in captions) | `export/Gulay_Zeynalli_Kesf_Et_az.srt` |
| Editable project (timeline, renderer, mix, original score) | `project/` |

## v2 — tight paparazzi cut (current)

`export/Gulay_Zeynalli_Kesf_Et_v2.mp4`: 52.6 s, 1080×1920, H.264 High + AAC 256 kbps, −16 LUFS.

* **Audio**: the original camera audio with gain only (a per-answer level match within ±4 dB, then +21 dB overall). It has no denoising, EQ or compression. A fast peak limiter touches transients only: 0 dB of gain reduction on the median speech frame and ≤0.7 dB on 90% of frames. The export correlates 0.985 with the source audio.
* **Tighter structure**: cold open “Haqlı olduğum halda mən niyə üzr istəyim ki?” → title press photo → 5 cards. The hook isn't repeated; question 3 continues with “Yox, haqsız olsam, səhvim olsa, üzr istəyirəm.” Cut from v1:
  * the repeated “Heç birindən”;
  * the musing pause in answer 3;
  * the “sənət insanları…” explanation in answer 4.
* **Paparazzi treatment**: camera-flash and shutter transitions, freeze-frame press photos with slam-in headlines (her exact words), berry/green highlight bars from the brand palette, punch-in close-ups, and an original 120 BPM fashion-house score mixed about 18 dB under her voice.
* **Logos**: the supplied transparent PNG overlay (`project/assets/kesfet_araz_overlay.png`) is composited 1:1: Kəşf Et upper left, Araz Radio upper right, plus a soft shadow only.
* **Rebuild**: `cd project && python3 v2/music2.py 56 && python3 v2/mix2.py`. Then apply `volume=21dB,alimiter=limit=0.80:attack=1:release=40` to the mix and run `python3 v2/render2.py`, which needs `master.mp4` from the v1 steps.

## v1 structure (output timecodes)

| Time | Section | Source (IMG_7215.MOV) |
|---|---|---|
| 0:00–0:05 | **Hook**: “Haqsız olsam, səhvim olsa, üzr istəyirəm. Haqlı olduğum halda mən niyə üzr istəyim ki?” | 43.55–49.02 |
| 0:05–0:09 | Title: GÜLAY ZEYNALLI — *5 təəccüblü sual, 5 cavab* | footage only |
| 0:09–0:17 | 01/05 SƏNƏTİ — *Sizi bu günə istedad gətirib, yoxsa mübarizə?* | answer 4.75–9.30 |
| 0:17–0:36 | 02/05 AİLƏ — *Səhnədəki Gülay, yoxsa ailədəki Gülay?* + follow-up *Hansından imtina etmək çətindir?* | 13.45–17.55, 19.75–28.97 |
| 0:36–0:51 | 03/05 XASİYYƏTİ — *Haqlı olduğunuz halda üzr istədiyiniz olur?* (full answer; hook returns in context) | 34.40–37.75, 41.90–49.62 |
| 0:51–1:14 | 04/05 HƏMKARLARI — *Hansı həmkarınızla münasibətiniz əvvəlki kimi deyil?* + follow-up *Qəlbiniz qırılmır?* | 53.40–67.10, 69.00–72.70 |
| 1:14–1:23 | 05/05 GÖZLƏNİLMƏZ ETİRAF — *Səmimi olmayan tərifə inanmış kimi davranırsınız?* | 78.05–83.30 |
| 1:23–1:28 | Closing quote → ivory brand end card (Kəşf Et + Araz Radio) | |

Question cards are shortened from what the journalist actually asked, not from the longer reference wording.

## Editorial / audio notes

* **Journalist voice**: removed by editing alone. Every question and interjection sits in its own gap with no overlap with Gülay's speech, so none of her words were cut. A re-transcription of the exported audio contains only her words.
* Also removed:
  * a loud off-camera voice at source 72.2–73.5 (her lips are closed there);
  * a quiet murmur at 39.5–41.6 (journalist level; it doesn't match her mic level);
  * the closing “Təşəkkür edirəm” at 83.4+, which isn't clearly hers.
* **Audio repair**: the source was very quiet (−35.5 LUFS). Repairs applied:
  * 50/100 Hz mains-hum notches and an 85 Hz high-pass;
  * DeepFilterNet3 speech enhancement with a 24 dB attenuation cap, so a little natural room air remains. The studio murmur dropped from about 15 dB to about 30 dB below her voice;
  * EQ: −2.5 dB at 220 Hz, +3.5 dB presence, light air;
  * de-esser and two-stage gentle compression;
  * edit points crossfaded over 25 ms.
* **Limitation**: the phone mic captured little above about 5 kHz, so EQ adds clarity but the voice can't have full studio brightness. Some room reverb remains, because removing it harder made the voice sound processed.
* **Music**: original instrumental, synthesised in `music.py` (100 BPM: Rhodes-style FM keys, pad, soft bass, brushed percussion, bell motif). It contains no samples or third-party audio, so it's rights-free.
  * The music sits about 18 dB under speech during answers and rises to about speech level on question cards.
  * Drums drop out for the reflective answers (04 follow-up, 05).
  * Transition sounds are restrained: soft whooshes, quiet risers, two typing ticks, one low impact on the title.
* **Caption checks**: subtitles were checked against several independent transcriptions and lip movement. One wording is uncertain: “Hamısıyla münasibət çox gözəldir” might be “…münasibətim…”.

## Rebuild

Requires ffmpeg, Python 3 (numpy, pillow, opencv-python-headless 4.10), and Rust for the denoiser.

```bash
# 1. graded SDR master from the iPhone HLG source (natural skin, no orange cast)
ffmpeg -i IMG_7215.MOV -map 0:v -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=gbrp,eq=gamma=1.10:saturation=0.90:contrast=1.03,colorbalance=rs=-0.03:rm=-0.05:bm=0.02:rh=-0.02,tmix=frames=2,fps=30,format=yuv420p" -c:v libx264 -crf 9 -an master.mp4
# 2. denoise (tools/dfcli, DeepFilterNet3 via the deep-filter-rt crate) then the voice chain in mix.py header
# 3. python3 music.py 92 && python3 mix.py      -> mix_raw.wav (then volume=5.3dB + alimiter 0.73 -> -14 LUFS)
# 4. MASTER=master.mp4 python3 render.py         -> video_only.mp4, then mux with the mastered mix
```

All editorial decisions (cuts, zoom/reframing per segment, question text, captions, pull quotes) live in `project/timeline.py`.

Fonts: Archivo Expanded (the brand-guide typeface) and Playfair Display, both under the SIL Open Font License. Logos are the original artwork from the supplied brand PDF and were not redrawn. The Araz Radio logo is shown in white as a transparent PNG (`export/Araz_Radio_logo_white.png`, made from the original vector logo's own shape) with a soft shadow, and on a deep-green badge on the ivory end card.
