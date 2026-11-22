"""BAXMA DEDİM. — Episode 03 «Yuxu iflici»: editable edit, sound design and render.

    cd baxma-dedim/episodes/ep03-yuxu-iflici && python3 edit.py
    -> Baxma_Dedim_EP03.mp4 (1080×1920, H.264 + AAC, 16.0 s)
    -> stems/*.wav          (one WAV per sound layer + mix)

The source clip's audio is muted. The curtain moves only once: the shot holds still on frame 18
(just before the movement), then plays in real time so the shift lands at 7.0 s.
No "Canlandırma" label (the user's standing rule).
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
OUT = os.path.join(HERE, "Baxma_Dedim_EP03.mp4")
SOURCE = os.path.join(HERE, "source", "bedroom_door_gemini.mp4")   # 720×1280, 24 fps, 10 s
FPS = 24
SRC_CROP = (4, 14, 704, 1252)
GRADE = ("eq=contrast=1.05:brightness=-0.02:saturation=0.95,"
         "curves=all='0/0 0.12/0.08 0.5/0.47 1/1',vignette=angle=PI/4.8")

HOLD_FRAME = 18           # still frame before the curtain moves (motion starts ~frame 20)
SHIFT_AT = 7.0            # the curtain's visible shift (source frame ~26) lands here
PLAY_FROM = SHIFT_AT - (26 - HOLD_FRAME) / 24          # 6.67 s: real-time playback from frame 18
SHOT_END = 13.5
END_IN = 13.5
DUR = 16.0

ZOOM = (1.0, 1.08)        # after the shift: slow push toward the doorway (anchored on it)
DOOR = (945, 840)
TOP_SHADE = 0.50          # darken the top band behind the captions (1 = no change at the top)

TX, TBASE, TMAXW, TMAX = 84, 300, 900, 66
# card: lines appear at their own beats; the whole card leaves at t_out
CARDS = [
    dict(id="c1", t_out=2.40, lines=[("Gözlərini açırsan.", 0.0)], instant=True),
    dict(id="c2", t_out=4.90, lines=[("Tərpənmək istəyirsən.", 2.50), ("Alınmır.", 3.40)]),
    dict(id="c3", t_out=6.88, lines=[("Qışqırmaq istəyirsən.", 5.00), ("Səsin çıxmır.", 5.85)]),
    dict(id="c4", t_out=10.40, lines=[("Elə bil otaqda kimsə var.", SHIFT_AT)]),
    dict(id="c5", t_out=SHOT_END, cut_out=True, lines=[("Buna yuxu iflici deyilir.", 10.50)]),
]
SILENCE_AT = CARDS[2]["lines"][1][1]       # room tone + rumble cut as "Səsin çıxmır." appears
RUSTLE_AT = SHIFT_AT + 0.20                # one soft rustle from the doorway side (right)
ROOM_BACK = 10.50                          # a trace of the room tone returns

SND = dict(room_db=-18, traffic_db=-16, rumble_db=-16, rustle_db=-4, room_back_db=-28, click_db=-6)
# logo ending (relative to END_IN): on at 0.10, one 2-frame flicker at 0.55 with the click,
# hold, fade 1.65 -> 2.40, then silence until the end
ENDING = dict(on=0.10, flick=0.55, off_frames=2, fade_at=1.65, fade_end=2.40)
# ============================================================================

LAYERS = os.path.join(HERE, "layers")
STEMS = os.path.join(HERE, "stems")
os.makedirs(LAYERS, exist_ok=True)
os.makedirs(STEMS, exist_ok=True)
W, H = C.W, C.H

# ---- text layers (one PNG per line, each with its own beat) -------------------------------
size = TMAX
for c in CARDS:
    for ln, _ in c["lines"]:
        size = min(size, TMAX * TMAXW / C.seg_width([(ln, C.F_SEMI)], TMAX))
size = int(size)
lead = round(size * 1.24)
jobs, LINES = [], []
for c in CARDS:
    for i, (ln, t_in) in enumerate(c["lines"]):
        name = f'{c["id"]}-{i + 1}'
        svg = os.path.join(LAYERS, name + ".svg")
        with open(svg, "w", encoding="utf-8") as f:
            f.write(C.text_layer_svg(name, [[(ln, C.F_SEMI)]], size, TX, TBASE + i * lead, lead))
        jobs.append([svg, svg[:-4] + ".png", W, H, 1])
        LINES.append(dict(png=svg[:-4] + ".png", t_in=t_in, card=c))
C.render_svgs(jobs, os.path.join(LAYERS, "jobs.json"))
for L in LINES:
    L["rgb"], L["a"] = C.load_rgba(L["png"])
ending = C.LogoFlickerEnding(LAYERS, **ENDING)


def line_state(L, t, d_in=0.32, d_out=0.18, rise=18):
    c = L["card"]
    if t < L["t_in"] or t >= c["t_out"]:
        return 0.0, 0
    if c.get("instant") and L["t_in"] == 0.0:
        p = 1.0                                   # already on screen at frame one
    else:
        p = C.ease_out((t - L["t_in"]) / d_in)
    o = p if c.get("cut_out") else p * (1 - C.smooth((t - (c["t_out"] - d_out)) / d_out))
    return o, round(rise * (1 - p))


ys = np.arange(H, dtype=np.float32)[:, None, None]
shade = 1 - (1 - TOP_SHADE) * (1 - np.clip(ys / 760, 0, 1)) ** 1.6

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
        sn = HOLD_FRAME if t < PLAY_FROM else HOLD_FRAME + round((t - PLAY_FROM) * 24)
        img = src.frame(sn)
        z = ZOOM[0] + (ZOOM[1] - ZOOM[0]) * C.smooth((t - SHIFT_AT) / (SHOT_END - SHIFT_AT))
        cx = DOOR[0] + (W / 2 - DOOR[0]) / z
        cy = DOOR[1] + (H / 2 - DOOR[1]) / z
        frame = C.push_in(img, z, (cx, cy)).astype(np.float32) / 255.0 * shade
        frame = C.grain(frame)
        for L in LINES:
            o, dy = line_state(L, t)
            frame = C.over(frame, L["rgb"], L["a"], o, dy)
    else:
        frame = ending.frame(t - END_IN)
    enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
enc.stdin.close()
enc.wait()
src.close()

# ---- sound --------------------------------------------------------------------------------
SR = sfx.SR
N = int(DUR * SR)
db = lambda x: 10 ** (x / 20)  # noqa: E731
LIB = os.path.join(HERE, "..", "shared", "sfx_library")
S = SND


def placed(clip, at, gain_db):
    out = np.zeros((N, 2), np.float32)
    i = int(round(at * SR))
    j = min(N, i + len(clip))
    out[i:j] = clip[: j - i] * db(gain_db)
    return out


def env(points, n=N):
    t = np.arange(n) / SR
    ts, gs = zip(*points)
    return np.interp(t, ts, gs)[:, None].astype(np.float32)


def chop(x, at, fade=0.006):
    i, k = int(at * SR), int(fade * SR)
    x[i:i + k] *= np.linspace(1, 0, k)[:, None]
    x[i + k:] = 0
    return x


# 1 · night room tone: on from frame one, cut dead at "Səsin çıxmır."
room = chop(placed(sfx.room_tone(DUR, seed=31), 0, S["room_db"]), SILENCE_AT)

# 2 · distant traffic outside: a real street ambience, far away behind glass
tr = sfx.load_file(os.path.join(LIB, "city_traffic_ambience_mixkit2708.mp3"), 3.0, SILENCE_AT + 0.5)
tr = sfx._lp(sfx._hp(tr, 70), 700, order=4)                       # through a closed window
tr = sfx._norm(tr * 0.6 + np.roll(tr, int(0.031 * SR), 0) * 0.4)    # a little distance smear
traffic = chop(placed(tr * db(env([(0, -12), (0.6, 0), (9, 0)], n=len(tr))), 0, S["traffic_db"]), SILENCE_AT)

# 3 · low rumble from "Tərpənmək istəyirsən.": barely audible, with 100–300 Hz body for phones
rl = SILENCE_AT - 2.5 + 0.1
rum = sfx.sub_pressure(rl, seed=12) + 0.35 * sfx._norm(sfx._bp(np.random.default_rng(3).standard_normal(
    (int(rl * SR), 2)), 90, 300))
rumble = chop(placed(sfx._norm(rum) * db(env([(0, -30), (1.2, -4), (rl, 0)], n=len(rum))), 2.5, S["rumble_db"]),
              SILENCE_AT)

# 4 · one soft fabric rustle from the doorway side (panned right), in the silence


def bump(x):
    return 0.0 if x < 0 or x > 0.85 else min(1, x / 0.12) * (1 - C.smooth((x - 0.25) / 0.6))


rustle = placed(sfx.fabric_rustle(0.9, bump, seed=23, pan=0.75), RUSTLE_AT, S["rustle_db"])

# 5 · a trace of the room tone comes back for the name of the condition
back = sfx.room_tone(SHOT_END - ROOM_BACK, seed=31)
room_back = chop(placed(back * db(env([(0, -40), (0.8, 0), (9, 0)], n=len(back))), ROOM_BACK, S["room_back_db"]),
                 SHOT_END)

# 6 · logo: one short, dry click on the flicker, then silence
click = placed(sfx.dry_tick(tail=0.35, ring=0.25), END_IN + ENDING["flick"], S["click_db"])

stems = dict(night_roomtone=room, distant_traffic=traffic, low_rumble=rumble, doorway_rustle=rustle,
             roomtone_trace=room_back, logo_click=click)
for name, x in stems.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", os.path.join(STEMS, f"{name}.wav")],
                   input=x.astype(np.float32).tobytes(), check=True)
mix = sum(stems.values())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "alimiter=limit=0.79:attack=0.5:release=60:level=false", "-c:a", "pcm_s24le",
                os.path.join(STEMS, "mix.wav")], input=mix.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", os.path.join(STEMS, "mix.wav"),
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-movflags", "+faststart", OUT], check=True)
os.remove(OUT + ".video.mp4")
print(f"wrote {OUT}  play_from={PLAY_FROM:.2f}s caption={size}px")
