"""BAXMA DEDİM. — Episode 04 «Damdabaca»: editable edit, sound design and render.

    cd baxma-dedim/episodes/ep04-damdabaca && python3 edit.py
    -> Baxma_Dedim_EP04.mp4 (1080×1920, H.264 + AAC)
    -> stems/*.wav          (one WAV per sound layer + mix)

Three Gemini clips in order (child looks up -> roof silhouette -> up the chimney). Source audio muted.
Sound follows the standard (EP02): growing drone, hard silence drops, heartbeat, riser, deep impact on
the cut to black, then the «Bir anlıq görünüş» ending. No "Canlandırma" label.
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
OUT = os.path.join(HERE, "Baxma_Dedim_EP04.mp4")
FPS = 24
SRC_CROP = (4, 14, 704, 1252)
GRADE = "eq=contrast=1.03:brightness=-0.015:saturation=0.97,vignette=angle=PI/4.6"   # natural low light

# shots: (file, edit start, edit end, source start, zoom from, zoom to, zoom anchor, caption base y)
SHOTS = [
    ("1_child_looks_up.mp4", 0.0, 10.0, 0.0, 1.00, 1.03, (560, 900), 520),
    ("2_roof_silhouette.mp4", 10.0, 20.0, 0.0, 1.00, 1.00, (540, 960), 300),
    ("3_up_the_chimney.mp4", 20.0, 28.0, 0.0, 1.00, 1.05, (560, 1000), 270),
]
CUT = 28.0                 # hard cut to black (deep impact), then complete silence
END_IN = 31.0              # standard ending
DUR = END_IN + C.FLASH["LENGTH"]          # 35.0 s

TX, TSIZE, TMAXW = 84, 58, 900
CARDS = [  # one card at a time; times in edit seconds
    dict(t_in=0.0, t_out=4.60, instant=True, text="Dinməyin, damdabaca gəlib sizi aparar."),
    dict(t_in=4.80, t_out=9.88,
         text="Naxçıvandan toplanmış folklor nümunəsində böyüklərin uşaqları bu sözlərlə qorxutduğu yazılıb."),
    dict(t_in=10.15, t_out=14.20, text="Adını ayrı-ayrı de: ‘damda baca’."),
    dict(t_in=14.40, t_out=19.88,
         text="Bəzi təsvirlərdə Damdabacanın gecələr bacadan evə endiyi deyilir."),
    dict(t_in=20.15, t_out=23.40, text="Damdabacanın adı Azərbaycan ədəbiyyatında da keçir."),
    dict(t_in=23.55, t_out=CUT, cut_out=True,
         text="Kamal Abdullanın bir əsərində Əsgər ağa nənəsinin onu Damdabaca ilə qorxutduğunu xatırlayır."),
]
QUESTION = dict(t_in=CUT + 0.35, t_out=END_IN - 0.08, size=74, cy=930, text="Bəs sən bacaya baxardın?")

# sound beats (edit seconds)
FOOTSTEP_AT = 2.95         # just before the chin lifts (source frame ~78 = 3.25 s)
CREAK_AT = 3.22
LISTEN = (3.9, 5.6)        # everything drops away: the second step never comes
ROOF_SCRAPE_AT = 14.80     # silhouette leans over the chimney (clip 2 ~4.8 s)
WIND_CUT = 23.50           # silhouette blocks more of the sky (clip 3 ~3.5 s)
CHIMNEY_SCRAPE_AT = 23.80
HEART_AT = 24.60
SILENCE_FROM = CUT + 0.75  # impact chopped -> complete silence under the question
SND = dict(room=-19, step=-2, creak=-13, wind=-20, roof_scrape=-5, chimney_scrape=1)
# ============================================================================

LAYERS = os.path.join(HERE, "layers")
STEMS = os.path.join(HERE, "stems")
os.makedirs(LAYERS, exist_ok=True)
os.makedirs(STEMS, exist_ok=True)
W, H = C.W, C.H


def wrap(text, size, maxw, font=C.F_SEMI):
    """fewest lines that fit maxw, then the most even break (no lonely last word)."""
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


# ---- text layers -------------------------------------------------------------------------
lead = round(TSIZE * 1.24)
jobs = []
for i, c in enumerate(CARDS):
    base = shot_at(c["t_in"])[7]
    c["lines"] = wrap(c["text"], TSIZE, TMAXW)
    c["band"] = (base - TSIZE, base + (len(c["lines"]) - 1) * lead + 0.3 * TSIZE)
    svg = os.path.join(LAYERS, f"card{i + 1}.svg")
    with open(svg, "w", encoding="utf-8") as f:
        f.write(C.text_layer_svg(f"card{i + 1}", [[(ln, C.F_SEMI)] for ln in c["lines"]], TSIZE, TX, base, lead))
    jobs.append([svg, svg[:-4] + ".png", W, H, 1])
    c["png"] = svg[:-4] + ".png"
qlines = wrap(QUESTION["text"], QUESTION["size"], 860)
ql = round(QUESTION["size"] * 1.28)
qsvg = os.path.join(LAYERS, "question.svg")
with open(qsvg, "w", encoding="utf-8") as f:
    f.write(C.text_layer_svg("question", [[(ln, C.F_SEMI)] for ln in qlines], QUESTION["size"], 0,
                             QUESTION["cy"] - (len(qlines) - 1) * ql / 2 + QUESTION["size"] * 0.36, ql,
                             align="center", shadow=False))
jobs.append([qsvg, qsvg[:-4] + ".png", W, H, 1])
C.render_svgs(jobs, os.path.join(LAYERS, "jobs.json"))
for c in CARDS:
    c["rgb"], c["a"] = C.load_rgba(c["png"])
Q = C.load_rgba(qsvg[:-4] + ".png")
ending = C.LogoFlashEnding(LAYERS)

ys = np.arange(H, dtype=np.float32)[:, None, None]


def scrim(band, k=0.48, soft=130):
    """soft dark band behind a caption so it reads on brighter walls/boards."""
    y0, y1 = band
    d = np.maximum(np.maximum(y0 - ys, ys - y1), 0)
    return 1 - k * np.exp(-(d / soft) ** 2)


for c in CARDS:
    c["scrim"] = scrim(c["band"])


def card_state(c, t, d_in=0.32, d_out=0.18, rise=18):
    if t < c["t_in"] or t >= c["t_out"]:
        return 0.0, 0
    p = 1.0 if c.get("instant") and c["t_in"] == 0.0 else C.ease_out((t - c["t_in"]) / d_in)
    o = p if c.get("cut_out") else p * (1 - C.smooth((t - (c["t_out"] - d_out)) / d_out))
    return o, round(rise * (1 - p))


# ---- picture -----------------------------------------------------------------------------
sources = {s[0]: None for s in SHOTS}
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
        name, t0, t1, ss, z0, z1, anc, _ = s
        if sources[name] is None:
            sources[name] = C.Source(os.path.join(HERE, "source", name), SRC_CROP, GRADE)
        img = sources[name].frame(round((ss + t - t0) * 24))
        z = z0 + (z1 - z0) * C.smooth((t - t0) / (t1 - t0))
        cx = anc[0] + (W / 2 - anc[0]) / z
        cy = anc[1] + (H / 2 - anc[1]) / z
        frame = C.push_in(img, z, (cx, cy)).astype(np.float32) / 255.0
        for c in CARDS:
            o, dy = card_state(c, t)
            if o > 0:
                frame = frame * (1 - (1 - c["scrim"]) * o)
        frame = C.grain(frame)
        for c in CARDS:
            o, dy = card_state(c, t)
            frame = C.over(frame, c["rgb"], c["a"], o, dy)
    elif t < END_IN:
        frame = C.ink_frame()
        if QUESTION["t_in"] <= t < QUESTION["t_out"]:
            o = C.ease_out((t - QUESTION["t_in"]) / 0.4) * (1 - C.smooth((t - (QUESTION["t_out"] - 0.12)) / 0.12))
            frame = C.over(frame, *Q, o)
    else:
        frame = ending.frame(t - END_IN)
    enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
enc.stdin.close()
enc.wait()
for v in sources.values():
    if v:
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


def chop(x, at, fade=0.006):
    i, k = int(at * SR), int(fade * SR)
    x[i:i + k] *= np.linspace(1, 0, k)[:, None][: len(x[i:i + k])]
    x[i + k:] = 0
    return x


L0, L1 = LISTEN
# 1 · indoor room tone (child's room): drops out after the creak, the listening pause, returns faintly
room = placed(sfx.room_tone(20.0, seed=51), 0, S["room"])
room *= db(env([(0, 0), (L0 - 0.05, 0), (L0 + 0.06, -90), (L1, -90), (L1 + 0.6, -6), (9.98, -6), (10.0, -120),
                (DUR, -120)]))
# 2 · footstep overhead + wooden creak
step = placed(sfx.footstep_overhead(), FOOTSTEP_AT, S["step"])
creak = placed(sfx.wood_creak(0.55, f0=52), CREAK_AT, S["creak"])
# 3 · outdoor wind from the roof cut, cut dead when the silhouette blocks the sky
wind = placed(sfx.wind(WIND_CUT - 10.0 + 0.1, seed=53), 10.0, S["wind"])
wind = chop(wind * db(env([(0, -120), (10.0, -120), (10.01, -3), (10.6, 0), (DUR, 0)])), WIND_CUT)
# 4 · grit scrape on the roof rim (low, close) and a drier, closer one inside the chimney
roof_scrape = placed(sfx.grit_scrape(0.42, seed=57), ROOF_SCRAPE_AT, S["roof_scrape"])
chim_scrape = placed(sfx.grit_scrape(0.55, seed=59, close=True), CHIMNEY_SCRAPE_AT, S["chimney_scrape"])
# 5 · standard tension: drone grows, dies in the listening pause, creeps back; heartbeat; riser; impact
dr = sfx.load_file(os.path.join(LIB, "horror_drone_mixkit1775.mp3"))
body = dr[int(0.5 * SR):int(7.0 * SR)]                      # steady part of the drone file
xf = int(0.6 * SR)
loop = body.copy()
while len(loop) < N:                                         # seamless crossfaded loop
    ramp = np.linspace(0, 1, xf)[:, None]
    loop = np.concatenate([loop[:-xf], loop[-xf:] * (1 - ramp) + body[:xf] * ramp, body[xf:]])
drone = loop[:N].copy()
w = int(0.5 * SR)                                            # flatten the file's own swells so the
pw = np.convolve((drone ** 2).mean(1), np.ones(w) / w, mode="same")  # envelope below sets the growth
drone = (drone / np.sqrt(pw + 1e-8)[:, None] * 0.12).astype(np.float32)
drone *= db(env([(0, -60), (2.8, -22), (L0 - 0.05, -14), (L0 + 0.04, -120), (L1, -120), (L1 + 0.05, -30),
                 (10.0, -20), (20.0, -12), (WIND_CUT, -9), (CUT - 0.01, -3), (CUT, -120), (DUR, -120)]))
heart = chop(placed(sfx.heartbeat(bpm=54, beats=4), HEART_AT, -18), CUT)
rs = sfx.load_file(os.path.join(LIB, "terror_riser_mixkit2630.mp3"), 1.2, 1.8)
riser = chop(placed(rs * db(env([(0, -30), (1.75, 0), (1.8, 0)], n=len(rs))), CUT - 1.8, -10), CUT)
im = sfx.load_file(os.path.join(LIB, "deep_impact_mixkit1687.mp3"))
impact = chop(placed(im, CUT, -4) * db(env([(0, 0), (CUT, 0), (SILENCE_FROM - 0.35, -8), (SILENCE_FROM, -40)])),
              SILENCE_FROM)
end_stems = ending_sfx.build(END_IN, DUR)

stems = dict(room_tone=room, footstep_overhead=step, wood_creak=creak, outdoor_wind=wind, roof_grit_scrape=roof_scrape,
             chimney_grit_scrape=chim_scrape, horror_drone=drone, heartbeat=heart, riser=riser, cut_impact=impact,
             **end_stems)
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
print(f"wrote {OUT}  dur={DUR}s")
