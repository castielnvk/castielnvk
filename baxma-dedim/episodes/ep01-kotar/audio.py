"""EP01 sound design: real recorded SFX placed against the picture timeline.

Sources: the Gemini clip's own room tone, plus Mixkit sound effects (Mixkit Sound Effects
Free License: free for commercial and personal use, no attribution required) in sfx/.
All times are in edit seconds. Levels are dBFS, measured as peak (pk) or RMS (rms).
"""
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
SFX = os.path.join(HERE, "sfx")


def load(path, start=0.0, dur=None, stereo=True):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-i", path, "-vn", "-ac", "2" if stereo else "1", "-ar", str(SR), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).copy() if stereo else a.copy()


def db(x):
    return 10 ** (x / 20)


def to_peak(a, target):
    return a * (db(target) / (np.abs(a).max() + 1e-9))


def to_rms(a, target):
    return a * (db(target) / (np.sqrt((a ** 2).mean()) + 1e-9))


def fade(a, fin=0.0, fout=0.0):
    a = a.copy()
    n = len(a)
    if fin:
        k = min(n, int(fin * SR))
        a[:k] *= np.linspace(0, 1, k)[:, None] ** 2
    if fout:
        k = min(n, int(fout * SR))
        a[n - k:] *= np.linspace(1, 0, k)[:, None] ** 2
    return a


def ramp(n, points):
    """gain envelope (linear) from [(t, dB), ...] relative to the clip start."""
    t = np.arange(n) / SR
    ts, gs = zip(*points)
    return db(np.interp(t, ts, gs))[:, None]


def room_ir(length=0.45, seed=3):
    """small hard kitchen: short decaying noise impulse response (tiles, table)."""
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t / 0.075)[:, None]
    ir[:int(0.004 * SR)] = 0
    return ir / np.abs(ir).sum(axis=0) * 6


def reverb(a, wet_db=-14):
    ir = room_ir()
    out = np.zeros((len(a) + len(ir) - 1, 2), np.float32)
    for c in range(2):
        out[:, c] = np.convolve(a[:, c], ir[:, c])
    out[:len(a)] += 0  # dry added below
    res = out * db(wet_db)
    res[:len(a)] += a
    return res


def build(out_wav, T):
    n = int(T["DUR"] * SR)
    mix = np.zeros((n, 2), np.float32)
    cut = int(T["KITCHEN_END"] * SR)

    def put(a, at, until=None):
        i = int(round(at * SR))
        j = min(n, i + len(a))
        if until is not None:
            j = min(j, int(until * SR))
        if j > i:
            mix[i:j] += a[: j - i]

    FREEZE, TOUCH, END = T["FREEZE"], T["TOUCH"], T["KITCHEN_END"]

    # 1 · Room tone from the Gemini clip itself (its own clinks at 4.6–5.5 s are out of sync -> skipped)
    src = os.path.join(HERE, "source", "kitchen_gemini.mp4")
    bed = np.concatenate([load(src, 6.0, 1.0), load(src, 0.05, 4.5), load(src, 5.6, 4.3)])
    bed = to_rms(bed, -40)
    put(fade(bed[: cut], 0.0, 0.0), 0.0, until=END)

    # 2 · Refrigerator hum, low and constant (a real Baku kitchen at night)
    fr = load(os.path.join(SFX, "refrigerator_hum_mixkit3013.mp3"), 1.0, 10.0)
    fr = to_rms(fr, -39)
    put(fade(fr, 0.4, 0.0), 0.0, until=END)

    # 3 · Wall clock: one tick per second (file ticks at 1.0, 2.0, …). Stops at the spoon touch.
    ck = load(os.path.join(SFX, "wall_clock_tick_mixkit988.mp3"))
    ck = to_peak(ck, -19)
    ck = reverb(ck, -16)
    first_tick = 0.30                         # ticks at 0.30, 1.30, … 4.30 s
    last = TOUCH - 0.05                       # no tick after the spoon lands: time stops
    put(ck[int((1.0 - first_tick) * SR):], 0.0, until=last)

    # 4 · Spoon lifted off the table (source frame 25 -> edit 2.04 s): one soft cutlery scrape
    sc = load(os.path.join(SFX, "cutlery_scrape_mixkit3158.mp3"), 0.17, 0.30)
    sc = reverb(fade(to_peak(sc, -27), 0.01, 0.12), -15)
    put(sc, FREEZE + 25 / 24 - 0.05)

    # 5 · Spoon set down on the table: metallic double clink, synced to the touch frame
    cl = load(os.path.join(SFX, "metal_clink_mixkit2836.mp3"))
    cl = reverb(fade(to_peak(cl, -8), 0.0, 0.25), -12)
    put(cl, TOUCH - 0.01)

    # 6 · Low horror drone: creeps in under the kitchen, swells after the touch, cut hard at black
    dr = load(os.path.join(SFX, "horror_drone_mixkit1775.mp3"))
    dr = np.concatenate([dr, dr[::-1]])[: int(END * SR)]
    dr = to_rms(dr, -30) * ramp(len(dr), [(0, -30), (TOUCH - 0.3, -12), (TOUCH + 0.8, -2), (END, 4)])
    put(dr, 0.0, until=END)

    # 7 · Riser into the cut (peak of the sweep lands on the cut)
    rs = load(os.path.join(SFX, "terror_riser_mixkit2630.mp3"), 1.2, 1.8)
    rs = to_peak(rs, -13) * ramp(len(rs), [(0, -30), (1.7, 0), (1.8, 0)])
    put(rs, END - 1.8, until=END)

    # 8 · Cut to black: everything stops on one deep impact; its tail carries the reveal line
    im = load(os.path.join(SFX, "deep_impact_mixkit1687.mp3"))
    im = to_peak(im, -4) * ramp(len(im), [(0, 0), (2.4, -6), (2.95, -40)])
    put(im, END)

    # 8b · A faint low drone under the reveal and logo so black never goes digitally dead
    tl = load(os.path.join(SFX, "horror_drone_mixkit1775.mp3"), 2.0, T["DUR"] - END)
    tl = to_rms(tl, -44) * ramp(len(tl), [(0, -30), (1.2, 0), (T["DUR"] - END - 0.6, 0), (T["DUR"] - END, -40)])
    put(tl, END)

    # 9 · Logo: one low tonal hit, short tail into silence
    lg = load(os.path.join(SFX, "logo_hit_mixkit833.mp3"))
    lg = reverb(to_peak(lg, -9), -10)
    put(lg, T["LOGO_IN"] - 0.10)

    # master: tail fade, gentle limiting
    mix[-int(0.25 * SR):] *= np.linspace(1, 0, int(0.25 * SR))[:, None]
    raw = out_wav + ".raw.f32"
    mix.astype(np.float32).tofile(raw)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
                    "-af", "volume=4.5dB,highpass=f=28,alimiter=limit=0.84:attack=2:release=60:level=false",
                    "-c:a", "pcm_s24le", out_wav], check=True)
    os.remove(raw)
