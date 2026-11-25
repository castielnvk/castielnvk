"""BAXMA DEDİM. — Episode 06 «Qayışbaldır»: editable edit, sound design and render.

    cd baxma-dedim/episodes/ep06-qayisbaldir && python3 edit.py
    -> Baxma_Dedim_EP06.mp4 (1080×1920, H.264 + AAC) and stems/*.wav

Three POV clips in order, real speed, original low light (source audio muted). The viewer is the
traveller holding the phone, so every sound moves closer with each cut:
  shot 1  the stream is clear and open; the tug and the traveller's inhale are close
  shot 2  the stream is muffled on the cut; one uneven breath right at the mic (his face, right side)
  shot 3  the jolt (fabric strain + boot on wet stone + phone thump) is the loudest moment; the stream
          dies as the light swings away; 0.5 s of silence when the light returns; one shaky breath
Captions are style C. Standard tension and the «Bir anlıq görünüş» ending. No "Canlandırma" label.
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "shared"))
import compose as C  # noqa: E402
import ending_sfx  # noqa: E402
import sfx  # noqa: E402
import type_c  # noqa: E402

# =============================== CONFIG ======================================
OUT = os.path.join(HERE, "Baxma_Dedim_EP06.mp4")
FPS = 24
GRADE = ("eq=contrast=1.06:brightness=-0.035:saturation=0.82,curves=all='0/0 0.15/0.09 0.5/0.45 1/0.97',"
         "colorbalance=bs=0.03:bm=0.015,vignette=angle=PI/3.6")   # v2: darker, colder, heavier vignette
BUILD = os.path.join(HERE, "build")
SRC = ["1_old_man_grabs_hand.mp4", "2_on_your_back.mp4", "3_grip_tightens.mp4"]
CROPS = [(4, 14, 704, 1252), (0, 14, 704, 1252), (0, 14, 704, 1252)]

# shots: (working file, start, end) — real speed, no zoom (handheld POV)
SHOTS = [("build/1.mp4", 0.0, 10.0), ("build/2.mp4", 10.0, 20.0), ("build/3.mp4", 20.0, 30.0)]
CUT = 30.0
END_IN = 31.0
DUR = END_IN + C.FLASH["LENGTH"]                       # 35.0 s

# action beats (edit seconds, from per-frame motion analysis of the clips)
PULL = 0.58          # clip 1 frame 14: the old man pulls the hand
BREATH_AT = 12.70    # clip 2: his face is at the shoulder, closest to the lens
JOLT = 21.875        # clip 3 frame 45: the legs jerk inward
LIGHT_AWAY = 22.05   # clip 3 frame 50: the flashlight swings away
LIGHT_BACK = 24.50   # clip 3 frame 108: the light is back on the locked legs
SHAKY_AT = LIGHT_BACK + 0.5

# style C cards: elements ("s"|"k", text, t_in); layout per shot: (cx, cy, maxw)
LAYOUT = {0: (540, 1010, 880), 1: (205, 560, 350), 2: (540, 410, 880)}
CARDS = [
    dict(t_out=2.85, instant=True, el=[("s", "Qoca", 0.0), ("k", "kömək", 0.0), ("s", "istədi.", 0.0)]),
    dict(t_out=9.85, el=[("s", "Yolçu əlini uzadan kimi qoca ondan", 3.10), ("k", "yapışdı.", 3.80)]),
    dict(t_out=14.60, el=[("s", "Yolçu başını çevirəndə qoca artıq onun", 10.20), ("k", "belində", 10.95),
                          ("s", "idi.", 10.95)]),
    dict(t_out=20.0, cut_out=True, el=[("s", "Rəvayətə görə, o, dərə kənarında özünü", 14.80),
                                       ("k", "köməksiz", 15.60), ("s", "göstərərmiş.", 15.60)]),
    dict(t_out=24.30, el=[("s", "O, qayışa bənzəyən ayaqları ilə yolçunun belinə", 20.15), ("k", "sarılarmış.", JOLT)]),
    dict(t_out=CUT, cut_out=True, el=[("s", "Ona", SHAKY_AT + 0.15), ("k", "Qayışbaldır", SHAKY_AT + 0.75),
                                      ("s", "deyirdilər.", SHAKY_AT + 0.75)]),
]
KEY_HITS = sorted({e[2] for c in CARDS for e in c["el"] if e[0] == "k" and e[2] > 0})
NO_THUD = {JOLT}                                         # the jolt is its own hit
# ============================================================================

LAYERS = os.path.join(HERE, "layers")
STEMS = os.path.join(HERE, "stems")
for d in (LAYERS, STEMS, BUILD):
    os.makedirs(d, exist_ok=True)
W, H = C.W, C.H

# working copies: first video stream only (clips 2/3 carry a cover-art stream), 24 fps, cropped to 9:16
for i, (f, crop) in enumerate(zip(SRC, CROPS)):
    x, y, w, h = crop
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "source", f), "-map", "0:v:0", "-an",
                    "-vf", f"fps=24,crop={w}:{h}:{x}:{y}", "-c:v", "libx264", "-crf", "10", "-preset", "fast",
                    os.path.join(BUILD, f"{i + 1}.mp4")], check=True)


def shot_index(t):
    for i, s in enumerate(SHOTS):
        if s[1] <= t < s[2]:
            return i
    return None


# ---- caption layers (style C) ------------------------------------------------------------------
jobs, LINES = [], []
for ci, c in enumerate(CARDS):
    cx, cy, maxw = LAYOUT[shot_index(c["el"][0][2])]
    els, js = type_c.build_card(f"c{ci + 1}", c["el"], cy, LAYERS, cx=cx, maxw=maxw)
    jobs += js
    for e in els:
        e["card"], e["cx"], e["maxw"] = c, cx, maxw
        LINES.append(e)
C.render_svgs(jobs, os.path.join(LAYERS, "jobs.json"))
ys = np.arange(H, dtype=np.float32)[:, None, None]
xs = np.arange(W, dtype=np.float32)[None, :, None]
for L in LINES:
    L["rgb"], L["a"] = C.load_rgba(L["png"])
    y0, y1 = L["band"]
    dy = np.maximum(np.maximum(y0 - ys, ys - y1), 0)
    dx = np.maximum(np.abs(xs - L["cx"]) - L["maxw"] / 2, 0)
    L["scrim"] = 1 - 0.45 * np.exp(-(dy / 110) ** 2) * np.exp(-(dx / 140) ** 2)
ending = C.LogoFlashEnding(LAYERS)


def line_state(L, t, d_out=0.25):
    c = L["card"]
    if t < L["t_in"] or t >= c["t_out"]:
        return 0.0
    d_in = 0.9 if L["kind"] == "k" else 0.8     # v2: everything fades in slowly; nothing snaps
    p = 1.0 if c.get("instant") and L["t_in"] == 0.0 else C.smooth((t - L["t_in"]) / d_in)
    return p if c.get("cut_out") else p * (1 - C.smooth((t - (c["t_out"] - d_out)) / d_out))


CREEP = {0: (1.00, 1.12, (560, 640)), 1: (1.00, 1.10, (700, 620)), 2: (1.00, 1.06, (540, 1100))}  # slow push-ins


def flinch(t):  # v2: unused (the flinch read as comedy)
    z = 1.0
    for k in KEY_HITS:
        if 0 <= t - k < 1.2:
            z += 0.035 * (1 - np.exp(-(t - k) / 0.03)) * np.exp(-(t - k) / 0.35)
    return z


# ---- picture -----------------------------------------------------------------------------
sources = {}
enc = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
     "-i", "-", "-an", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
     "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "12M", "-bufsize", "24M",
     "-profile:v", "high", "-level", "4.1",
     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", OUT + ".video.mp4"],
    stdin=subprocess.PIPE)
for n in range(round(DUR * FPS)):
    t = n / FPS
    si = shot_index(t)
    if si is not None:
        name, t0, _ = SHOTS[si]
        if name not in sources:
            sources[name] = C.Source(os.path.join(HERE, name), (0, 0, 704 if si else 704, 1252), GRADE)
        img = sources[name].frame(round((t - t0) * 24))
        z0_, z1_, anc = CREEP[si]
        z = z0_ + (z1_ - z0_) * C.smooth((t - t0) / 10.0)
        cen = (anc[0] + (W / 2 - anc[0]) / z, anc[1] + (H / 2 - anc[1]) / z)
        frame = C.push_in(img, z, cen).astype(np.float32) / 255.0
        act = [(L, line_state(L, t)) for L in LINES]
        for L, o in act:
            if o > 0:
                frame = frame * (1 - (1 - L["scrim"]) * o)
        frame = C.grain(frame)
        for L, o in act:
            frame = C.over(frame, L["rgb"], L["a"], o)
    elif t < END_IN:
        frame = C.ink_frame()
    else:
        frame = ending.frame(t - END_IN)
    enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
enc.stdin.close()
enc.wait()
for v in sources.values():
    v.close()

# ---- sound --------------------------------------------------------------------------------
SR = sfx.SR
N = int(DUR * SR)
db = lambda x: 10 ** (x / 20)  # noqa: E731
LIB = os.path.join(HERE, "..", "shared", "sfx_library")


def lib(name, start=0.0, dur=None):
    return sfx.load_file(os.path.join(LIB, name), start, dur)


def placed(clip, at, gain_db):
    out = np.zeros((N, 2), np.float32)
    i = int(round(at * SR))
    j = min(N, i + len(clip))
    if j > i:
        out[i:j] = clip[: j - i] * db(gain_db)
    return out


def env(points, n=N):
    t = np.arange(n) / SR
    ts, gs = zip(*points)
    return np.interp(t, ts, gs)[:, None].astype(np.float32)


def chop(x, at, fade=0.004):
    i, k = int(at * SR), int(fade * SR)
    x[i:i + k] *= np.linspace(1, 0, k)[:, None][: len(x[i:i + k])]
    x[i + k:] = 0
    return x


def level(x, w=1.0):
    pw = np.convolve((x ** 2).mean(1), np.ones(int(w * SR)) / int(w * SR), mode="same")
    return sfx._norm(x / (np.sqrt(pw + 1e-9)[:, None] ** 0.8))


# 1 · the stream: a real water recording (birds removed by the low-pass), open in shot 1,
#     muffled on the 10.0 cut (we are now under his weight), dead as the light swings away
wa = lib("water_flowing_mixkit2473.mp3", 5.0, 26.0)
ws = lib("water_splash_mixkit1214.mp3", 2.0, 26.0)
stream_open = level(sfx._lp(sfx._hp(wa, 90), 2400, order=4) + 0.45 * sfx._lp(sfx._hp(ws, 300), 5000, order=2))
stream_muf = sfx._norm(sfx._lp(stream_open, 520, order=4))
stream = np.zeros((N, 2), np.float32)
k10, k20 = int(10 * SR), int(20 * SR)
m = min(len(stream_open), int(LIGHT_AWAY * SR) + SR)
stream[:k10] = stream_open[:k10] * db(-11)
stream[k10:m] = stream_muf[k10:m] * db(-14)
stream *= db(env([(0, -6), (0.3, 0), (PULL, -4), (PULL + 0.6, -4), (PULL + 1.6, 0), (10.0, 0),
                  (20.0, 0), (20.01, -4), (LIGHT_AWAY, -4), (LIGHT_AWAY + 0.22, -90), (DUR, -90)]))

# 2 · the pull: a short dry fabric tug + the traveller's sharp inhale behind the phone
tug = sfx.fabric_rustle(0.30, lambda x: 0 if x > 0.28 else min(1, x / 0.01) * np.exp(-x / 0.06), seed=91, pan=0.1)
inh = lib("breath_inhale_mixkit965.mp3")[: int(0.45 * SR)]
inh = sfx._lp(sfx._hp(inh, 180), 2600, order=2) * np.linspace(0.3, 1, len(inh))[:, None] ** 0.5
pull = placed(tug, PULL - 0.01, -14) + placed(inh * np.minimum(1, np.linspace(1, 0, len(inh)) * 6)[:, None], PULL + 0.05, -17)

# 3 · his breath right beside the mic: uneven, dry, from the right (his face is on the right)
br = lib("breath_gasping_mixkit1969.mp3")
br = sfx._lp(sfx._hp(br, 90), 1800, order=4)
br = np.stack([np.interp(np.arange(int(len(br) / 0.78)) * 0.78, np.arange(len(br)), br[:, c]) for c in range(2)], 1)
br = np.concatenate([br[: int(0.7 * SR)], np.zeros((int(0.25 * SR), 2)), br[int(0.7 * SR):]])   # slow, low; a catch
br = np.stack([br[:, 0] * 0.55, br[:, 1]], 1)                                             # from the right, close
breath = placed(sfx._norm(br), BREATH_AT, -15)

# 4 · the jolt (loudest moment): fabric strain + muddy boot scraping wet stone + one blunt phone thump
strain = sfx.fabric_rustle(0.45, lambda x: 0 if x > 0.42 else min(1, x / 0.015) * (1 - x / 0.42), seed=93, pan=0.0)
mud = lib("mud_steps_mixkit1187.mp3")
pk = int(np.argmax(np.abs(mud[int(1 * SR):int(6 * SR)]).mean(1))) + int(1 * SR)
squelch = mud[pk - int(0.05 * SR): pk + int(0.5 * SR)]
scrape = sfx.grit_scrape(0.5, seed=95, close=True)
im = lib("deep_impact_mixkit1687.mp3")
thump = sfx._lp(im[: int(0.35 * SR)], 500) * np.linspace(1, 0, int(0.35 * SR))[:, None] ** 1.5
click = sfx.dry_tick(tail=0.12, ring=0.0)
sub = sfx._lp(im[: int(1.6 * SR)], 120, order=4)
jolt = (placed(strain, JOLT - 0.02, -8) + placed(sfx._lp(sfx._norm(squelch), 900), JOLT, -14)
        + placed(sfx._lp(scrape, 1600), JOLT + 0.03, -12) + placed(sfx._norm(sub), JOLT, 0)
        + placed(thump, JOLT + 0.01, -3))
jolt = jolt / (np.abs(jolt).max() + 1e-9) * db(-2.0)     # v2: a heavy low blow, not a slapstick crunch
handling = placed(sfx.fabric_rustle(LIGHT_BACK - LIGHT_AWAY - 0.1,
                                    lambda x: 0.55 * np.exp(-x / 0.7), seed=97, pan=-0.2), LIGHT_AWAY, -20)

# 5 · after 0.5 s of silence: one shaky breath (the traveller)
sb = lib("breath_slow_mixkit2233.mp3")[: int(1.9 * SR)]
sb = sfx._lp(sfx._hp(sb, 140), 1500, order=4)
shaky = placed(sfx.shaky(sb, rate=4.2, depth=0.35), SHAKY_AT, -19)        # v2: a slow, held, trembling breath

# 6 · standard tension: drone (retuned per shot), heartbeat, riser, cut accents, key-word thuds, impact
dr = lib("horror_drone_mixkit1775.mp3")
body = dr[int(0.5 * SR):int(7.0 * SR)]
xf = int(0.6 * SR)
loop = body.copy()
while len(loop) < N:
    ramp = np.linspace(0, 1, xf)[:, None]
    loop = np.concatenate([loop[:-xf], loop[-xf:] * (1 - ramp) + body[:xf] * ramp, body[xf:]])
drone = level(loop[:N].copy(), 0.5) * 0.25
low = np.stack([np.interp(np.arange(N) * 0.84, np.arange(N), drone[:, c]) for c in range(2)], 1)
lower = np.stack([np.interp(np.arange(N) * 0.70, np.arange(N), drone[:, c]) for c in range(2)], 1)
drone[k10:k20] = sfx._lp(low, 800)[k10:k20] * 1.3
drone[k20:] = sfx._lp(lower, 600)[k20:] * 1.5
drone *= db(env([(0, -60), (2.0, -30), (10.0, -24), (10.01, -18), (20.0, -12), (JOLT - 0.01, -10),
                 (JOLT, -90), (SHAKY_AT + 1.2, -90), (SHAKY_AT + 2.4, -20), (CUT - 0.01, -6), (CUT, -120),
                 (DUR, -120)]))
heart = np.zeros((N, 2), np.float32)
beat = sfx.heartbeat(bpm=60, beats=1)
tb = 14.2
while tb < 20.0:                                      # under his face on your back, speeding up
    heart += placed(beat, tb, -19 + 4 * (tb - 14.2) / 5.8)
    tb += 1.0 - 0.4 * (tb - 14.2) / 5.8
heart += placed(sfx.heartbeat(bpm=72, beats=3), SHAKY_AT + 2.1, -16)
heart = chop(heart, CUT)
rs = lib("terror_riser_mixkit2630.mp3", 1.2, 1.8)
riser = chop(placed(rs * db(env([(0, -30), (1.75, 0), (1.8, 0)], n=len(rs))), CUT - 1.8, -11), CUT)
sk = im[: int(0.7 * SR)][::-1] * db(env([(0, -40), (0.55, -6), (0.7, 0)], n=int(0.7 * SR)))
cut_acc = sum(placed(sfx._lp(sk, 900), c - 0.7, -13) + placed(sfx._lp(im[: int(0.9 * SR)], 400), c, -9)
              for c in (10.0, 20.0))
thud = sfx._lp(im[: int(0.7 * SR)], 280) * np.linspace(1, 0, int(0.7 * SR))[:, None] ** 2
key_thuds = np.zeros((N, 2), np.float32)                 # v2: no thud per word (read as comedy)
impact = placed(im * db(env([(0, 0), (0.5, -2), (END_IN - CUT - 0.1, -30), (END_IN - CUT + 0.6, -90), (9, -90)],
                            n=len(im))), CUT, -10)
end_stems = {k: v * db(-6) for k, v in ending_sfx.build(END_IN, DUR).items()}   # same ending, kept under the jolt

tt = np.arange(N) / SR
pressure = sfx.sub_pressure(DUR, seed=101) * db(env([(0, -40), (3.0, -22), (10.0, -18), (20.0, -12), (JOLT - 0.01, -10),
                                                    (JOLT, -90), (SHAKY_AT + 0.8, -90), (SHAKY_AT + 3, -14),
                                                    (CUT - 0.01, -8), (CUT, -120), (DUR, -120)]))
ring = (np.sin(2 * np.pi * 2963 * tt) + np.sin(2 * np.pi * 2971 * tt))[:, None] * np.array([[1.0, 0.8]])
ring = ring.astype(np.float32) * db(env([(0, -90), (8.0, -90), (12.0, -46), (20.0, -38), (JOLT - 0.01, -34),
                                          (JOLT, -90), (SHAKY_AT + 1.5, -90), (CUT - 0.5, -36), (CUT, -120), (DUR, -120)]))
stems = dict(dread_pressure=pressure, dread_ring=ring, stream=stream, pull_tug_inhale=pull, breath_at_mic=breath, jolt=jolt, phone_handling=handling,
             shaky_breath=shaky, horror_drone=drone, heartbeat=heart, riser=riser, cut_accents=cut_acc,
             key_thuds=key_thuds, cut_impact=impact, **end_stems)
for name, x in stems.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", os.path.join(STEMS, f"{name}.wav")],
                   input=x.astype(np.float32).tobytes(), check=True)
mix = sum(stems.values())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "alimiter=limit=0.79:attack=0.3:release=80:level=false", "-c:a", "pcm_s24le",
                os.path.join(STEMS, "mix.wav")], input=mix.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", os.path.join(STEMS, "mix.wav"),
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-movflags", "+faststart", OUT], check=True)
os.remove(OUT + ".video.mp4")
print(f"wrote {OUT}  dur={DUR}s")
