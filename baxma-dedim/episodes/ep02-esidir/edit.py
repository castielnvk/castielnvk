"""BAXMA DEDİM. — Episode 02 «Bəlkə hələ eşidir»: editable edit, sound design and render.

    cd baxma-dedim/episodes/ep02-esidir && python3 edit.py
    -> Baxma_Dedim_EP02.mp4 (1080×1920, H.264 + AAC, 15.0 s)
    -> stems/*.wav          (separate SFX tracks + full mix, 48 kHz / 24-bit)

Source clip audio is muted; the whole soundtrack is designed in ../shared/sfx.py.
The logo ending (light strip -> BAXMA, DEDİM. + tick, hard cut) is ../shared/compose.LogoEnding
plus sfx.dry_tick — reuse both as-is in later episodes.
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "shared"))
import compose as C  # noqa: E402
import sfx  # noqa: E402

# =============================== CONFIG ======================================
OUT = os.path.join(HERE, "Baxma_Dedim_EP02.mp4")
SOURCE = os.path.join(HERE, "source", "bedroom_gemini.mp4")     # 720×1280, 24 fps, 10 s
FPS = 24
SRC_CROP = (4, 14, 704, 1252)
GRADE = ("eq=contrast=1.04:brightness=-0.01:saturation=0.97,"
         "curves=all='0/0 0.10/0.075 0.5/0.49 1/1',vignette=angle=PI/5")

HOLD_START = 1.2          # still on frame 0 (both hands visible) while the hook reads
STOP_SRC_FRAME = 88       # last frame with a clear gap between the fingers (touching from ~92)
STOP = HOLD_START + STOP_SRC_FRAME / 24      # 4.87 s: the hand stops; still-frame hold from here
SHOT_END = 10.0           # hard cut to near-black
END_IN = 13.0             # logo ending starts (2.0 s long)
DUR = 15.0

ZOOM = (1.0, 1.06)        # slow push-in toward the gap, anchored so the dark ceiling stays dark
ANCHOR = (600, 900)

TX, TBASE, TMAXW, TMAX = 84, 300, 900, 60
CARDS = [  # bedroom captions (left, dark area above the hands); times in edit seconds
    dict(id="a", t_in=0.0, t_out=3.85, lines=["Yanındakı adam", "sənə cavab vermir."]),
    dict(id="b", t_in=4.05, t_out=5.75, lines=["Amma alimlər bir şey görüblər."]),
    dict(id="c", t_in=5.85, t_out=SHOT_END, cut_out=True,
         lines=["Ömrünün son saatlarında olan", "bəzi insanların beyni", "hələ də səsə reaksiya verib."]),
]
FINAL = dict(id="d", t_in=SHOT_END + 0.12, t_out=END_IN - 0.08, size=70, cy=930,
             lines=["Deyilən sözləri", "anlayıb-anlamadıqlarını", "bilmirik."])

# sound (edit seconds, dBFS)
SND = dict(room_db=-25, room_drop=STOP, room_gap=1.0, room_return_db=-29,
           rustle_from=HOLD_START, rustle_db=-9,
           tone_at=CARDS[1]["t_in"], tone_db=-17,
           tick_at=END_IN + C.ENDING["DEDIM_AT"], tick_db=-3)
# ============================================================================

LAYERS = os.path.join(HERE, "layers")
STEMS = os.path.join(HERE, "stems")
os.makedirs(LAYERS, exist_ok=True)
os.makedirs(STEMS, exist_ok=True)
W, H = C.W, C.H

# ---- text layers -------------------------------------------------------------------------
size = TMAX
for c in CARDS:
    for ln in c["lines"]:
        size = min(size, TMAX * TMAXW / C.seg_width([(ln, C.F_SEMI)], TMAX))
size = int(size)
lead = round(size * 1.24)
jobs = []
for c in CARDS:
    svg = os.path.join(LAYERS, f'{c["id"]}.svg')
    with open(svg, "w", encoding="utf-8") as f:
        f.write(C.text_layer_svg(c["id"], [[(ln, C.F_SEMI)] for ln in c["lines"]], size, TX, TBASE, lead))
    jobs.append([svg, svg[:-4] + ".png", W, H, 1])
fl = round(FINAL["size"] * 1.28)
fbase = FINAL["cy"] - (len(FINAL["lines"]) - 1) * fl / 2 + FINAL["size"] * 0.36
svg = os.path.join(LAYERS, "d.svg")
with open(svg, "w", encoding="utf-8") as f:
    f.write(C.text_layer_svg("d", [[(ln, C.F_SEMI)] for ln in FINAL["lines"]], FINAL["size"], 0, fbase, fl,
                             align="center", shadow=False))
jobs.append([svg, svg[:-4] + ".png", W, H, 1])
C.render_svgs(jobs, os.path.join(LAYERS, "jobs.json"))
TXT = {c["id"]: C.load_rgba(os.path.join(LAYERS, f'{c["id"]}.png')) for c in CARDS + [FINAL]}
ending = C.LogoEnding(LAYERS)


def card_alpha(c, t, d_in=0.30, d_out=0.18, rise=20):
    if t < c["t_in"] or t >= c["t_out"]:
        return 0.0, 0
    p = C.ease_out((t - c["t_in"]) / d_in)
    o = p if c.get("cut_out") else p * (1 - C.smooth((t - (c["t_out"] - d_out)) / d_out))
    return o, round(rise * (1 - p))


# ---- picture -----------------------------------------------------------------------------
src = C.Source(SOURCE, SRC_CROP, GRADE)
enc = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
     "-i", "-", "-an", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
     "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-level", "4.1",
     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", OUT + ".video.mp4"],
    stdin=subprocess.PIPE)
for n in range(round(DUR * FPS)):
    t = n / FPS
    if t < SHOT_END:
        if t < HOLD_START:
            sn = 0
        elif t < STOP:
            sn = min(STOP_SRC_FRAME, round((t - HOLD_START) * 24))
        else:
            sn = STOP_SRC_FRAME
        img = src.frame(sn)
        z = ZOOM[0] + (ZOOM[1] - ZOOM[0]) * C.smooth(t / SHOT_END)
        # anchored zoom: the anchor point stays put on screen
        cx = ANCHOR[0] + (W / 2 - ANCHOR[0]) / z
        cy = ANCHOR[1] + (H / 2 - ANCHOR[1]) / z
        frame = C.push_in(img, z, (cx, cy)).astype(np.float32) / 255.0
        frame = C.grain(frame)
        for c in CARDS:
            o, dy = card_alpha(c, t)
            frame = C.over(frame, *TXT[c["id"]], o, dy)
    elif t < END_IN:
        frame = C.ink_frame()
        o, dy = card_alpha(FINAL, t, d_in=0.35, d_out=0.12, rise=0)
        frame = C.over(frame, *TXT["d"], o)
    else:
        frame = ending.frame(t - END_IN)
    enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
enc.stdin.close()
enc.wait()
src.close()

# ---- sound: separate stems, then the mix --------------------------------------------------
SR = sfx.SR
N = int(DUR * SR)
db = lambda x: 10 ** (x / 20)  # noqa: E731


def placed(clip, at, gain_db, n=N):
    out = np.zeros((n, 2), np.float32)
    i = int(round(at * SR))
    j = min(n, i + len(clip))
    out[i:j] = clip[: j - i] * db(gain_db)
    return out


def env(points, n=N):
    t = np.arange(n) / SR
    ts, gs = zip(*points)
    return np.interp(t, ts, gs)[:, None].astype(np.float32)


S = SND
room = sfx.room_tone(DUR) * env([(0, 0), (0.25, 1), (S["room_drop"], 1), (S["room_drop"] + 0.09, 0),
                                  (S["room_drop"] + S["room_gap"], 0),
                                  (S["room_drop"] + S["room_gap"] + 0.9, db(S["room_return_db"] - S["room_db"])),
                                  (SHOT_END - 0.001, db(S["room_return_db"] - S["room_db"])), (SHOT_END, 0), (DUR, 0)])
room *= db(S["room_db"])

move = STOP - S["rustle_from"]


def intensity(x):  # hand speed: quick start, steady, slowing to a stop
    if x < 0 or x > move:
        return 0.0
    a = min(1, x / 0.18)
    return a * (1 - C.smooth((x - move * 0.45) / (move * 0.55))) * (0.85 + 0.15 * np.sin(x * 7.3))


rust = placed(sfx.fabric_rustle(move + 0.1, intensity, pan=0.3), S["rustle_from"], S["rustle_db"])
tone = placed(sfx.distant_tone(), S["tone_at"], S["tone_db"])
tick = placed(sfx.dry_tick(), S["tick_at"], S["tick_db"])

stems = dict(roomtone=room, fabric_rustle=rust, distant_tone=tone, logo_tick=tick)
for name, x in stems.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", os.path.join(STEMS, f"{name}.wav")],
                   input=x.astype(np.float32).tobytes(), check=True)
mix = sum(stems.values())
# standalone, reusable ending SFX (tick from 0)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-c:a", "pcm_s24le", os.path.join(STEMS, "logo_tick_standalone.wav")],
               input=(sfx.dry_tick() * db(S["tick_db"])).astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "alimiter=limit=0.89:attack=1:release=50:level=false", "-c:a", "pcm_s24le",
                os.path.join(STEMS, "mix.wav")], input=mix.astype(np.float32).tobytes(), check=True)

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", os.path.join(STEMS, "mix.wav"),
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-movflags", "+faststart", OUT], check=True)
os.remove(OUT + ".video.mp4")
print(f"wrote {OUT}  stop={STOP:.2f}s caption size={size}px")
