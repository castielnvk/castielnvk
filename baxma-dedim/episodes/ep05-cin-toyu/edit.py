"""BAXMA DEDİM. — Episode 05 «Cin toyu»: editable edit, sound design and render.

    cd baxma-dedim/episodes/ep05-cin-toyu && python3 edit.py
    -> Baxma_Dedim_EP05.mp4 (1080×1920, H.264 + AAC)
    -> stems/*.wav          (one WAV per sound layer + mix)

Three Gemini clips (old man staring -> hand over the plov -> empty clearing). Source audio muted.
Clip 2 is the user's replacement clip (source/2_hand_plate_v2.mov, 1080×1920 HEVC 30 fps), converted to
24 fps and played in real time. The fingers come down to the rice at ~6.0 s (edit 16.0 s); "‘Bismillah’ dedi."
appears 0.5 s before. A slow 1.10× push-in (top-anchored) puts its last hand position on the spot where clip 3's hand
starts, so the hard cut at 20.0 s is a matched cut. Standard sound and ending (EP02). No "Canlandırma" label.
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

# =============================== CONFIG ======================================
OUT = os.path.join(HERE, "Baxma_Dedim_EP05.mp4")
FPS = 24
SRC_CROP = (4, 14, 704, 1252)
GRADE = "eq=contrast=1.03:brightness=-0.02:saturation=0.96,vignette=angle=PI/4.6"   # natural and dark
BUILD = os.path.join(HERE, "build")

CONTACT = 16.0                                     # fingers reach the rice (clip 2 ~6.0 s)

# shots: (file, start, end, source offset s, zoom from, zoom to, centre from, centre to, caption base, crop)
SHOTS = [
    ("1_old_man_staring.mp4", 0.0, 10.0, 0.0, 1.00, 1.10, (540, 960), (430, 860), 300, SRC_CROP),  # push into his stare
    ("build/2_hand_plate_24.mp4", 10.0, 20.0, 0.0, 1.00, 1.10, (540, 960), (589, 873), 300, (0, 0, 1080, 1920)),
    ("3_empty_clearing.mp4", 20.0, 28.0, 0.0, 1.00, 1.04, (540, 960), (420, 900), 300, SRC_CROP),
]
CUT = 28.0
END_IN = 29.0
DUR = END_IN + C.FLASH["LENGTH"]                   # 33.0 s

# Caption style C (../shared/type_c.py): small spaced capitals + one big red italic key word per card.
# Elements in reading order: ("s"|"k", text, t_in). cy = vertical centre of the card per shot.
CARD_CY = {0: 290, 1: 470, 2: 470}           # shot index -> card centre (dark areas above faces/table/hand)
CARDS = [
    dict(t_out=4.40, instant=True, el=[("k", "Cinlər", 0.0), ("s", "onu toya çağırdılar.", 0.0)]),
    dict(t_out=9.85, el=[("s", "O da hamını", 4.60), ("k", "adam", 5.10), ("s", "bilib süfrəyə oturdu.", 5.10)]),
    dict(t_out=13.90, el=[("s", "Azərbaycan folklorunda buna", 10.15), ("k", "‘cin toyu’", 10.75),
                          ("s", "deyilir.", 10.75)]),
    dict(t_out=20.0, cut_out=True, el=[("s", "Yolçu yeməyə əl uzadıb", 14.10), ("k", "‘Bismillah’", CONTACT - 0.50),
                                       ("s", "dedi.", CONTACT - 0.50)]),
    dict(t_out=24.40, el=[("s", "Bir də baxdı ki, çölün düzündə", 21.05), ("k", "tək", 21.75), ("s", "qalıb.", 21.75)]),
    dict(t_out=CUT, cut_out=True, el=[("s", "Gecə çöldən toy səsi gəlsə, gedib", 24.60), ("k", "baxardın?", 25.50)]),
]
KEY_HITS = sorted({e[2] for c in CARDS for e in c["el"] if e[0] == "k" and e[2] > 0})

# sound beats (edit seconds)
LEAN_CREAK_AT = 0.55       # the man leans in (clip 1 motion peaks 0.25–1.5 s)
MURMUR_FADE = (1.0, 3.8)   # crowd murmur dies away as he leans closer; the zurna keeps playing
SLEEVE_REACH = (14.7, CONTACT + 0.15)
SILENCE = (20.0, 21.0)     # zurna killed on the cut frame; one beat of complete silence
PULLBACK_AT = 22.70        # clip 3 hand pulls back (~2.7 s)
GHOST_ZURNA = (25.4, 27.7)  # a far-away phrase under the question, almost not there
SND = dict(zurna=-13, murmur=-22, creak=-15, sleeve=-8, wind=-21, pull_sleeve=-10, ghost=-22)
# intensity (v2)
ZURNA_REC = os.path.join(HERE, "source", "zurna_recording_user.wav")   # the user's zurna (real performance)
ZURNA_WARP = (17.6, 20.0)  # the wedding goes wrong: the zurna slows and sags like tape before it is killed
HEART_S2 = (12.0, 20.0)    # heartbeat under the reach, speeding up (1.05 s -> 0.6 s between beats)
GLIMPSE_AT = CONTACT - 0.50  # with "‘Bismillah’": 2 frames of the empty clearing + a muffled hit
GLIMPSE_FRAMES = 2
LAMP_FLICKER = [(18.55, 18.62, 0.62), (18.95, 19.0, 0.8), (19.30, 19.42, 0.5), (19.62, 19.67, 0.75),
                (19.80, 19.88, 0.55)]     # (start, end, brightness): the wedding light stutters before it vanishes
# ============================================================================

LAYERS = os.path.join(HERE, "layers")
STEMS = os.path.join(HERE, "stems")
for d in (LAYERS, STEMS, BUILD):
    os.makedirs(d, exist_ok=True)
W, H = C.W, C.H

# ---- clip 2 (replacement, 30 fps HEVC) -> 24 fps working copy -------------------------------------
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "source", "2_hand_plate_v2.mov"), "-an",
                "-vf", "fps=24", "-c:v", "libx264", "-crf", "10", "-preset", "fast",
                os.path.join(BUILD, "2_hand_plate_24.mp4")], check=True)


def wrap(text, size, maxw, font=C.F_SEMI):
    from itertools import combinations
    words = text.split()
    wid = lambda ws: C.seg_width([(" ".join(ws), font)], size)  # noqa: E731
    for k in range(1, len(words) + 1):
        best = None
        for cuts in combinations(range(1, len(words)), k - 1):
            parts = [words[a:b] for a, b in zip((0,) + cuts, cuts + (len(words),))]
            ws = [wid(p) for p in parts]
            if max(ws) <= maxw and (best is None or max(ws) - min(ws) < best[0]):
                best = (max(ws) - min(ws), [" ".join(p) for p in parts])
        if best:
            return best[1]
    return [text]


def shot_at(t):
    for s in SHOTS:
        if s[1] <= t < s[2]:
            return s
    return None


# ---- text layers (style C) -------------------------------------------------------------------
import type_c  # noqa: E402
jobs, LINES = [], []
for ci, c in enumerate(CARDS):
    shot = SHOTS.index(shot_at(c["el"][0][2]))
    els, js = type_c.build_card(f"c{ci + 1}", c["el"], CARD_CY[shot], LAYERS)
    jobs += js
    for e in els:
        e["card"] = c
        LINES.append(e)
C.render_svgs(jobs, os.path.join(LAYERS, "jobs.json"))
ys = np.arange(H, dtype=np.float32)[:, None, None]
for L in LINES:
    L["rgb"], L["a"] = C.load_rgba(L["png"])
    y0, y1 = L["band"]
    d = np.maximum(np.maximum(y0 - ys, ys - y1), 0)
    L["scrim"] = 1 - 0.42 * np.exp(-(d / 110) ** 2)
ending = C.LogoFlashEnding(LAYERS)


def line_state(L, t, d_out=0.25):
    """slow fade, no slide; key words come in faster (they land with the thud)."""
    c = L["card"]
    if t < L["t_in"] or t >= c["t_out"]:
        return 0.0, 0
    d_in = 0.18 if L["kind"] == "k" else 0.7
    p = 1.0 if c.get("instant") and L["t_in"] == 0.0 else C.smooth((t - L["t_in"]) / d_in)
    o = p if c.get("cut_out") else p * (1 - C.smooth((t - (c["t_out"] - d_out)) / d_out))
    return o, 0


def flinch(t):
    """camera flinch on each key word: a quick 3.5 % punch-in that settles."""
    z = 1.0
    for k in KEY_HITS:
        if 0 <= t - k < 1.2:
            z += 0.035 * (1 - np.exp(-(t - k) / 0.03)) * np.exp(-(t - k) / 0.35)
    return z


# ---- picture -----------------------------------------------------------------------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H * 0.55) / (H * 0.62)), 0, 1.4) ** 2.2)[..., None]
_g = C.Source(os.path.join(HERE, "source", "3_empty_clearing.mp4"), SRC_CROP, GRADE)
GLIMPSE = _g.frame(150).astype(np.float32) / 255.0 * 0.85      # the clearing, no hand: what is really there
_g.close()
del yy, xx
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
    s = shot_at(t)
    if s:
        name, t0, t1, ss, z0, z1, c0, c1, _, crop = s
        if name not in sources:
            path = os.path.join(HERE, name) if name.startswith("build/") else os.path.join(HERE, "source", name)
            sources[name] = C.Source(path, crop, GRADE)
        img = sources[name].frame(round((ss + t - t0) * 24))
        p = C.smooth((t - t0) / (t1 - t0))
        z = (z0 + (z1 - z0) * p) * flinch(t)
        cen = (c0[0] + (c1[0] - c0[0]) * p, c0[1] + (c1[1] - c0[1]) * p)
        frame = C.push_in(img, z, cen).astype(np.float32) / 255.0
        if t0 == 10.0:                                           # the table shot closes in
            frame = frame * (1 - 0.42 * C.smooth((t - 10.0) / 10.0) * VIG)
            for a, b, v in LAMP_FLICKER:
                if a <= t < b:
                    frame = frame * v
            if GLIMPSE_AT <= t < GLIMPSE_AT + GLIMPSE_FRAMES / 24:
                frame = C.grain(GLIMPSE.copy())
                enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
                continue
        active = [(L, *line_state(L, t)) for L in LINES]
        for L, o, dy in active:
            if o > 0:
                frame = frame * (1 - (1 - L["scrim"]) * o)
        frame = C.grain(frame)
        for L, o, dy in active:
            frame = C.over(frame, L["rgb"], L["a"], o, dy)
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


def chop(x, at, fade=0.004):
    i, k = int(at * SR), int(fade * SR)
    x[i:i + k] *= np.linspace(1, 0, k)[:, None][: len(x[i:i + k])]
    x[i + k:] = 0
    return x


CUT_SHOT = SILENCE[0]
# 1 · the wedding: a thin, distant zurna through both table shots, killed on the cut frame
zr = sfx.load_file(ZURNA_REC)
need = int((CUT_SHOT + 1.0) * SR)
xf = int(1.0 * SR)
while len(zr) < need:                                    # extend with a crossfaded repeat of the middle
    tail = sfx.load_file(ZURNA_REC, 6.0)
    ramp = np.linspace(0, 1, xf)[:, None]
    zr = np.concatenate([zr[:-xf], zr[-xf:] * (1 - ramp) + tail[:xf] * ramp, tail[xf:]])
zr = zr[:need]
zr = sfx._lp(sfx._hp(zr, 140), 1300, order=4)           # muffled: behind the guests, through bodies and cloth
w_ = int(1.0 * SR)                                       # even out the level (the opening has no drum)
pw_ = np.convolve((zr ** 2).mean(1), np.ones(w_) / w_, mode="same")
zr = zr / (np.sqrt(pw_ + 1e-9)[:, None] ** 0.75)
mono = zr.mean(1, keepdims=True)
zr = 0.7 * mono + 0.3 * zr                               # narrow, far
ir = sfx.reverb_ir(1.8, 0.42, seed=73, lp=1400)
wet = np.stack([np.convolve(zr[:, c], ir[:, c])[:need] for c in range(2)], 1)
zr = sfx._norm(0.65 * zr / np.abs(zr).max() + 0.55 * wet / np.abs(wet).max())
tt = np.arange(need) / SR                                # tape sag: playback rate 1.0 -> 0.84
w0, w1 = ZURNA_WARP
rate = 1 - 0.16 * np.clip((tt - w0) / (w1 - w0), 0, 1) ** 1.6
pos = np.cumsum(rate) - rate[0]
zr = np.stack([np.interp(pos, np.arange(need), zr[:, c]) for c in range(2)], 1).astype(np.float32)
# shot 2 is AT the table: same performance, closer and clearer; the switch happens on the 10.0 cut frame
zc = sfx.load_file(ZURNA_REC)
while len(zc) < need:
    zc = np.concatenate([zc, sfx.load_file(ZURNA_REC, 6.0)])
zc = sfx._lp(sfx._hp(zc[:need], 120), 3200, order=2)
pwc = np.convolve((zc ** 2).mean(1), np.ones(w_) / w_, mode="same")
zc = sfx._norm(zc / (np.sqrt(pwc + 1e-9)[:, None] ** 0.75))
zc = np.stack([np.interp(pos, np.arange(need), zc[:, c]) for c in range(2)], 1).astype(np.float32)
k10 = int(10.0 * SR)
zr[k10:] = zc[k10:] * 0.75                                # hard perspective change on the cut
zur = placed(zr, 0, S["zurna"]) * db(env([(0, -8), (0.5, 0), (9.6, 0), (9.98, -12), (10.0, 2), (w0, 2),
                                          (CUT_SHOT - 0.01, 4)]))
g0, g1 = int(GLIMPSE_AT * SR), int((GLIMPSE_AT + GLIMPSE_FRAMES / 24) * SR)
zur[g0:g1] *= 0.02                                       # the wedding drops out for the 2-frame glimpse
zur = chop(zur, CUT_SHOT)
# 2 · crowd murmur (real recording, far and indistinct), dies away as the man leans in
cr = sfx.load_file(os.path.join(LIB, "crowd_talking_mixkit2930.mp3"), 5.0, 6.0)
cr = sfx._lp(sfx._hp(cr, 150), 2200, order=4)
murmur = placed(sfx._norm(cr) * db(env([(0, 0), (MURMUR_FADE[0], 0), (MURMUR_FADE[1], -60), (6, -90)], n=len(cr))),
                0, S["murmur"])
# 3 · soft chair creak as he leans
creak = placed(sfx.wood_creak(0.75, seed=63, f0=40), LEAN_CREAK_AT, S["creak"])


# 4 · wool sleeve rustle as the hand comes down to the food
def reach(x):
    d = SLEEVE_REACH[1] - SLEEVE_REACH[0]
    return 0.0 if x < 0 or x > d else min(1, x / 0.4) * (0.55 + 0.45 * np.sin(np.pi * x / d)) * \
        (1 - C.smooth((x - d + 0.5) / 0.5))


sleeve = placed(sfx.fabric_rustle(SLEEVE_REACH[1] - SLEEVE_REACH[0] + 0.1, reach, seed=65, pan=0.35),
                SLEEVE_REACH[0], S["sleeve"])
sleeve = chop(sleeve, CUT_SHOT)
# 5 · after one beat of complete silence: faint outdoor wind, and the sleeve as the hand pulls back
wind = placed(sfx.wind(CUT - SILENCE[1] + 0.2, seed=67), SILENCE[1], S["wind"])
wind = chop(wind * db(env([(0, -120), (SILENCE[1], -40), (SILENCE[1] + 1.2, 0), (CUT, 0)])), CUT)


def pull(x):
    return 0.0 if x < 0 or x > 1.0 else min(1, x / 0.08) * (1 - C.smooth((x - 0.35) / 0.65))


pull_sleeve = placed(sfx.fabric_rustle(1.05, pull, seed=69, pan=0.4), PULLBACK_AT, S["pull_sleeve"])
# 6 · the question: a far-away zurna phrase in the wind, almost not there
gz = sfx.load_file(ZURNA_REC, 9.0, GHOST_ZURNA[1] - GHOST_ZURNA[0])   # the same wedding, very far away
gz = sfx._lp(sfx._hp(gz, 200), 650, order=4)
gir = sfx.reverb_ir(2.8, 0.9, seed=75, lp=900)
gz = sfx._norm(np.stack([np.convolve(gz[:, c], gir[:, c])[:len(gz)] for c in range(2)], 1))
ghost = chop(placed(gz * db(env([(0, -40), (0.9, 0), (1.6, 0), (GHOST_ZURNA[1] - GHOST_ZURNA[0], -40)], n=len(gz))),
                    GHOST_ZURNA[0], S["ghost"]), CUT)
# 7 · standard tension: drone grows under the wedding, dies with the zurna, creeps back; heartbeat; riser; impact
dr = sfx.load_file(os.path.join(LIB, "horror_drone_mixkit1775.mp3"))
body = dr[int(0.5 * SR):int(7.0 * SR)]
xf = int(0.6 * SR)
loop = body.copy()
while len(loop) < N:
    ramp = np.linspace(0, 1, xf)[:, None]
    loop = np.concatenate([loop[:-xf], loop[-xf:] * (1 - ramp) + body[:xf] * ramp, body[xf:]])
drone = loop[:N].copy()
w = int(0.5 * SR)
pw = np.convolve((drone ** 2).mean(1), np.ones(w) / w, mode="same")
drone = (drone / np.sqrt(pw + 1e-8)[:, None] * 0.12).astype(np.float32)
lowd = np.stack([np.interp(np.arange(N) * 0.82, np.arange(N), drone[:, c]) for c in range(2)], 1)
drone[int(10.0 * SR):int(CUT_SHOT * SR)] = sfx._lp(lowd, 700)[int(10.0 * SR):int(CUT_SHOT * SR)] * 1.4
drone *= db(env([(0, -60), (3.0, -24), (10.0, -18), (CUT_SHOT - 0.01, -5), (CUT_SHOT, -120), (SILENCE[1], -120),
                 (SILENCE[1] + 1.5, -26), (CUT - 0.01, -6), (CUT, -120), (DUR, -120)]))
heart = chop(placed(sfx.heartbeat(bpm=54, beats=5), 22.2, -18), CUT)
beat = sfx.heartbeat(bpm=60, beats=1)                    # under the reach: the heart speeds up
heart2 = np.zeros((N, 2), np.float32)
tb = HEART_S2[0]
while tb < HEART_S2[1]:
    heart2 += placed(beat, tb, -17 + 5 * (tb - HEART_S2[0]) / (HEART_S2[1] - HEART_S2[0]))
    tb += 1.05 - 0.45 * (tb - HEART_S2[0]) / (HEART_S2[1] - HEART_S2[0])
heart2 = chop(heart2, CUT_SHOT)
im0 = sfx.load_file(os.path.join(LIB, "deep_impact_mixkit1687.mp3"))
hit = im0[: int(0.5 * SR)] * np.linspace(1, 0, int(0.5 * SR))[:, None] ** 2
glimpse_hit = placed(sfx._lp(hit, 600), GLIMPSE_AT, -6)  # muffled thump under the glimpse
rs = sfx.load_file(os.path.join(LIB, "terror_riser_mixkit2630.mp3"), 1.2, 1.8)
riser = chop(placed(rs * db(env([(0, -30), (1.75, 0), (1.8, 0)], n=len(rs))), CUT - 1.8, -11), CUT)
im = sfx.load_file(os.path.join(LIB, "deep_impact_mixkit1687.mp3"))
impact = placed(im * db(env([(0, 0), (0.5, -2), (END_IN - CUT - 0.1, -30), (END_IN - CUT + 0.6, -90), (9, -90)],
                            n=len(im))), CUT, -4)
end_stems = ending_sfx.build(END_IN, DUR)

# cut accent at 10.0: reverse suck into a low hit
sk = im0[: int(0.7 * SR)][::-1] * db(env([(0, -40), (0.55, -6), (0.7, 0)], n=int(0.7 * SR)))
cut_accent = placed(sfx._lp(sk, 900), 10.0 - 0.7, -12) + placed(sfx._lp(im0[: int(0.9 * SR)], 400), 10.0, -9)
# key words land with a muffled thud (Bismillah already has the glimpse hit)
thud = sfx._lp(im0[: int(0.7 * SR)], 280) * np.linspace(1, 0, int(0.7 * SR))[:, None] ** 2
key_thuds = sum(placed(thud, k, -10) for k in KEY_HITS if abs(k - GLIMPSE_AT) > 0.05)
# table foley in shot 2: a spoon on a plate somewhere down the table, then the hand in the rice
cl = sfx.load_file(os.path.join(LIB, "metal_clink_mixkit2836.mp3"))
sc = sfx.load_file(os.path.join(LIB, "cutlery_scrape_mixkit3158.mp3"), 0.17, 0.35)
table = placed(sfx._lp(cl, 2500), 11.3, -27) + placed(sfx._lp(cl[::-1].copy()[::-1], 1800), 13.2, -31) + \
    placed(sc, CONTACT - 0.05, -18)
table = chop(table, CUT_SHOT)
stems = dict(cut_accent=cut_accent, key_thuds=key_thuds, table_foley=table, zurna=zur, heartbeat_reach=heart2, glimpse_hit=glimpse_hit, crowd_murmur=murmur, chair_creak=creak, sleeve_reach=sleeve, outdoor_wind=wind,
             sleeve_pullback=pull_sleeve, ghost_zurna=ghost, horror_drone=drone, heartbeat=heart, riser=riser,
             cut_impact=impact, **end_stems)
for name, x in stems.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", os.path.join(STEMS, f"{name}.wav")],
                   input=x.astype(np.float32).tobytes(), check=True)
mix = sum(stems.values())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "alimiter=limit=0.82:attack=0.5:release=60:level=false", "-c:a", "pcm_s24le",
                os.path.join(STEMS, "mix.wav")], input=mix.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", os.path.join(STEMS, "mix.wav"),
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-movflags", "+faststart", OUT], check=True)
os.remove(OUT + ".video.mp4")
print(f"wrote {OUT}  contact={CONTACT:.2f}s dur={DUR}s")
