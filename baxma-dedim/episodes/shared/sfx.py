"""Designed sound effects for BAXMA DEDİM. (synthesised, no third-party samples).

Every function returns float32 stereo arrays at 48 kHz, peak-normalised to 1.0
(levels are set at mix time). Seeds keep renders repeatable.
"""
import numpy as np
from scipy import signal

SR = 48000


def _bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def _lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x, axis=0)


def _hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x, axis=0)


def _norm(x):
    return (x / (np.abs(x).max() + 1e-12)).astype(np.float32)


def _pink(n, rng):
    """1/f noise via spectral shaping."""
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    return np.fft.irfft(X / np.sqrt(f), n)


def room_tone(dur, seed=11):
    """Close, dry bedroom tone: soft pink/brown air, a hint of mains hum, slow drift."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    common = _pink(n, rng)
    ch = []
    for c in range(2):
        x = 0.75 * common + 0.25 * _pink(n, rng)          # mostly correlated = intimate, not wide
        x = _lp(_hp(x, 35), 3800)
        ch.append(x)
    x = np.stack(ch, 1)
    x /= np.abs(x).max()
    air = _lp(_hp(rng.standard_normal((n, 2)), 900), 5500)   # upper "air" so it survives phone speakers
    x = x + 0.22 * air / np.abs(air).max()
    t = np.arange(n) / SR
    hum = (0.012 * np.sin(2 * np.pi * 100 * t) + 0.006 * np.sin(2 * np.pi * 200 * t + 0.7))[:, None]
    drift = (1 + 0.08 * np.sin(2 * np.pi * 0.23 * t + 1.1) + 0.05 * np.sin(2 * np.pi * 0.61 * t))[:, None]
    return _norm((x + hum) * drift)


def fabric_rustle(dur, intensity, seed=5, pan=0.25):
    """Sleeve/sheet movement: grains of band-passed noise + a soft swish, density follows
    `intensity(t)` (0..1). Close and dry (no reverb). pan>0 = right."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.array([intensity(x) for x in t[::48]])
    env = np.interp(t, t[::48][: len(env)], env)
    out = np.zeros(n)
    # textured grains
    pos = 0.0
    while pos < dur:
        e = intensity(pos)
        rate = 8 + 140 * e
        pos += rng.exponential(1 / rate)
        if pos >= dur or e < 0.02:
            continue
        L = int(rng.uniform(0.006, 0.055) * SR)
        g = rng.standard_normal(L)
        fc = rng.uniform(900, 5200)
        g = _bp(g, fc * 0.55, min(fc * 1.7, 15000))
        a = np.exp(-np.linspace(0, rng.uniform(3, 7), L))
        a[: max(1, int(0.0015 * SR))] *= np.linspace(0, 1, max(1, int(0.0015 * SR)))
        i = int(pos * SR)
        j = min(n, i + L)
        out[i:j] += (g * a)[: j - i] * e * rng.lognormal(0, 0.45)
    # soft continuous swish of the fabric
    sw = _bp(rng.standard_normal(n), 500, 6000) * env * 0.35
    x = _hp(out + sw, 250)
    st = np.stack([x * (1 - pan) ** 0.5, x * (1 + pan) ** 0.5 * 0.98], 1)
    st[:, 1] = np.roll(st[:, 1], int(0.0004 * SR))        # tiny inter-channel offset: close, real
    return _norm(st)


def reverb_ir(length, decay, seed=2, lp=6000):
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t / decay)[:, None]
    ir = _lp(ir, lp)
    ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
    return ir / np.abs(ir).sum(0)


def distant_tone(freq=1000.0, length=0.42, tail=2.6, seed=3):
    """One faint, distant test-tone (designed; not audio from any study):
    a soft sine beep heard through a wall/corridor — mostly reverb, filtered."""
    n = int(length * SR)
    t = np.arange(n) / SR
    a = np.minimum(1, t / 0.035) * np.minimum(1, (length - t) / 0.12)
    beep = (np.sin(2 * np.pi * freq * t) + 0.06 * np.sin(2 * np.pi * 2 * freq * t)) * a
    total = n + int(tail * SR)
    dry = np.zeros((total, 2))
    dry[:n] = beep[:, None]
    ir = reverb_ir(tail, 0.55, lp=3500)
    wet = np.stack([np.convolve(dry[:, c], ir[:, c])[:total] for c in range(2)], 1)
    x = 0.18 * _lp(dry, 2500) + wet / np.abs(wet).max()
    return _norm(_lp(x, 3200))


def dry_tick(tail=1.1, seed=9):
    """A short, dry mechanical tick with a faint metallic ring that keeps decaying
    (so the tail can outlive a hard cut to black)."""
    rng = np.random.default_rng(seed)
    n = int(tail * SR)
    t = np.arange(n) / SR
    click = np.zeros(n)
    k = int(0.0025 * SR)
    click[:k] = _hp(rng.standard_normal(k), 2500) * np.exp(-np.linspace(0, 6, k))
    body = 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.018)
    ring = sum(a * np.sin(2 * np.pi * f * t + p) * np.exp(-t / d) for f, d, a, p in
               [(1870, 0.55, 0.20, 0.0), (3240, 0.38, 0.12, 1.3), (4980, 0.20, 0.07, 2.1), (7330, 0.08, 0.03, 0.4)])
    x = click * 1.0 + body + ring
    st = np.stack([x, np.roll(x, 6)], 1)
    return _norm(st)


def heartbeat(bpm=52, beats=6, seed=4):
    """Slow, close heartbeat (lub-dub). Low thump plus upper body harmonics so it still
    reads on a phone speaker."""
    period = 60 / bpm
    n = int((beats * period + 0.6) * SR)
    out = np.zeros(n)

    def thump(f0, length, amp):
        m = int(length * SR)
        t = np.arange(m) / SR
        f = f0 * (1 + 0.6 * np.exp(-t / 0.02))            # quick pitch drop
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph + 0.3)
        x *= np.exp(-t / 0.07) * np.minimum(1, t / 0.004)
        return amp * np.tanh(1.8 * x)                      # soft saturation = audible harmonics

    for k in range(beats):
        i = int(k * period * SR)
        for off, f0, amp in ((0.0, 58, 1.0), (0.27, 50, 0.72)):
            th = thump(f0, 0.32, amp)
            j = i + int(off * SR)
            out[j:j + len(th)] += th[: max(0, min(len(th), n - j))]
    out = _lp(out, 900)
    return _norm(np.stack([out, out], 1))


def sub_pressure(dur, seed=8):
    """Low, slowly breathing pressure under black: filtered rumble + 41 Hz tone with
    upper partials for small speakers."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    rum = _lp(_hp(rng.standard_normal(n), 25), 180)
    rum /= np.abs(rum).max()
    tone = np.sin(2 * np.pi * 41 * t) + 0.3 * np.sin(2 * np.pi * 82 * t) + 0.12 * np.sin(2 * np.pi * 123 * t + 1)
    x = (0.6 * rum + 0.5 * tone) * (1 + 0.25 * np.sin(2 * np.pi * 0.35 * t))
    return _norm(np.stack([x, np.roll(x, 90)], 1))


def load_file(path, start=0.0, dur=None):
    """decode any audio file to float32 stereo 48 kHz."""
    import subprocess
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-i", path, "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return _norm(a.reshape(-1, 2).copy())
