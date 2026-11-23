"""BAXMA DEDİM. — Episode 03 «Yuxu iflici»: editable edit, sound design and render.

    cd baxma-dedim/episodes/ep03-yuxu-iflici && python3 edit.py
    -> Baxma_Dedim_EP03.mp4 (1080×1920, H.264 + AAC, 16.0 s)
    -> stems/*.wav          (one WAV per sound layer + mix)

Sound and ending follow EP02 (the user's standard): tension drone, silence drop, heartbeat,
impact on the cut, and the «Bir anlıq görünüş» logo ending from shared/ending_sfx.py.
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
SHIFT_AT = 5.0            # the curtain's visible shift (source frame ~26) lands here
PLAY_FROM = SHIFT_AT - (26 - HOLD_FRAME) / 24          # 6.67 s: real-time playback from frame 18
SHOT_END = 14.0          # (source runs out at 14.4 s; the last frame would simply hold)
END_IN = 17.0             # black card with the last fact, then the standard ending
DUR = END_IN + C.FLASH["LENGTH"]   # 21.0 s

ZOOM = (1.0, 1.08)        # after the shift: slow push toward the doorway (anchored on it)
DOOR = (945, 840)
TOP_SHADE = 0.50          # darken the top band behind the captions (1 = no change at the top)

TX, TBASE, TMAXW, TMAX = 84, 300, 900, 66
# card: lines appear at their own beats; the whole card leaves at t_out
CARDS = [
    dict(id="c1", t_out=3.35, instant=True,
         lines=[("Oyanmısan,", 0.0), ("amma tərpənə bilmirsən.", 0.90)]),
    dict(id="c2", t_out=7.70, lines=[("Səsin çıxmır.", 3.50), ("Elə bil otaqda kimsə var.", SHIFT_AT)]),
    dict(id="c3", t_out=10.10, lines=[("Buna yuxu iflici deyilir.", 7.80)]),
    dict(id="c4", t_out=SHOT_END, cut_out=True,
         lines=[("Yuxu iflicində beyin ayılır,", 10.20), ("amma əzələlər bir müddət", 11.00),
                ("hərəkətsiz qalır.", 11.00)]),
]
# last fact on the black card after the cut (centred, like EP02)
FINAL = dict(t_in=SHOT_END + 0.20, t_out=END_IN - 0.08, size=70, cy=930,
             lines=["Bu hal bir neçə dəqiqəyə", "qədər çəkə bilər."])
SILENCE_AT = CARDS[1]["lines"][0][1]       # room tone + rumble cut as "Səsin çıxmır." appears
RUSTLE_AT = SHIFT_AT + 0.20                # one soft rustle from the doorway side (right)
ROOM_BACK = 7.80                           # a trace of the room tone returns
CREEP_AT = SHIFT_AT + 1.10                 # drone creeps back after the rustle
HEART_AT = 6.70                            # slow heartbeat while we stare at the doorway

SND = dict(room_db=-18, traffic_db=-16, rumble_db=-16, rustle_db=-4, room_back_db=-28)
# logo ending (relative to END_IN): on at 0.10, one 2-frame flicker at 0.55 with the click,
# hold, fade 1.65 -> 2.40, then silence until the end
# Standard ending «Bir anlıq görünüş» (EP02, approved; never changed per episode, whatever the brief says)
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
fl = round(FINAL["size"] * 1.28)
fsvg = os.path.join(LAYERS, "final.svg")
with open(fsvg, "w", encoding="utf-8") as f:
    f.write(C.text_layer_svg("final", [[(ln, C.F_SEMI)] for ln in FINAL["lines"]], FINAL["size"], 0,
                             FINAL["cy"] - (len(FINAL["lines"]) - 1) * fl / 2 + FINAL["size"] * 0.36, fl,
                             align="center", shadow=False))
jobs.append([fsvg, fsvg[:-4] + ".png", W, H, 1])
C.render_svgs(jobs, os.path.join(LAYERS, "jobs.json"))
FINAL_L = C.load_rgba(fsvg[:-4] + ".png")
for L in LINES:
    L["rgb"], L["a"] = C.load_rgba(L["png"])
ending = C.LogoFlashEnding(LAYERS)


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
     "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "12M", "-bufsize", "24M",
     "-profile:v", "high", "-level", "4.1",
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
    elif t < END_IN:
        frame = C.ink_frame()
        if FINAL["t_in"] <= t < FINAL["t_out"]:
            o = C.ease_out((t - FINAL["t_in"]) / 0.35) * (1 - C.smooth((t - (FINAL["t_out"] - 0.12)) / 0.12))
            frame = C.over(frame, *FINAL_L, o)
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

# 6 · EP02-style tension: horror drone grows with the room, dies with it at "Səsin çıxmır.",
#     creeps back after the rustle with a slow heartbeat and a riser into the cut
dr = sfx.load_file(os.path.join(LIB, "horror_drone_mixkit1775.mp3"))
drone = np.zeros((N, 2), np.float32)
k1 = int(SILENCE_AT * SR) + 4800
drone[:k1] = dr[:k1]
k0 = int(CREEP_AT * SR)
seg = dr[int(0.8 * SR):][: int(SHOT_END * SR) - k0]
drone[k0:k0 + len(seg)] = seg
drone *= db(env([(0, -70), (1.0, -15), (SILENCE_AT - 0.05, -5), (SILENCE_AT + 0.02, -120), (CREEP_AT, -120),
                 (CREEP_AT + 0.02, -26), (SHOT_END - 0.01, -3), (SHOT_END, -120), (DUR, -120)])[..., 0:1])
heart = chop(placed(sfx.heartbeat(bpm=52, beats=6), HEART_AT, -19), SHOT_END)
rs = sfx.load_file(os.path.join(LIB, "terror_riser_mixkit2630.mp3"), 1.2, 1.8)
riser = chop(placed(rs * db(env([(0, -30), (1.75, 0), (1.8, 0)], n=len(rs))), SHOT_END - 1.8, -10), SHOT_END)
im = sfx.load_file(os.path.join(LIB, "deep_impact_mixkit1687.mp3"))
impact = placed(im * db(env([(0, 0), (1.0, -3), (END_IN - SHOT_END - 0.45, -30), (END_IN - SHOT_END - 0.05, -90),
                             (9, -90)], n=len(im))), SHOT_END, -4)
pressure = placed(sfx.sub_pressure(2.6) * db(env([(0, -40), (0.8, 0), (1.9, 0), (2.6, -60)], n=int(2.6 * SR))),
                  SHOT_END + 0.4, -22)
import ending_sfx  # noqa: E402
end_stems = ending_sfx.build(END_IN, DUR)

stems = dict(night_roomtone=room, distant_traffic=traffic, low_rumble=rumble, doorway_rustle=rustle,
             roomtone_trace=room_back, horror_drone=drone, heartbeat=heart, riser=riser, cut_impact=impact, black_pressure=pressure,
             **end_stems)
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
