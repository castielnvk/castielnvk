#!/usr/bin/env python3
"""Render an "İlk dəfə Araz'da" premiere Reel from an episode config.

Usage:
    python3 render.py episodes/<episode>/config.json [--preview 3.0,12.9,24] [--workers 4]

The config lists the source clips (Grok AI videos), the recording audio and every text cue.
Steps: extract frames (24 fps, upscaled to 1419x1920) -> render frames in Chromium canvas
(Playwright, parallel workers) -> encode H.264 -> mux the original recording audio (AAC).
"""
import argparse, base64, functools, http.server, json, os, shutil, subprocess, sys, threading
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sh(*a):
    subprocess.run(a, check=True)


def extract_frames(cfg, ep, build):
    fdir = build / "frames"
    for name, src in cfg["clips"].items():
        out = fdir / name
        if out.exists() and any(out.iterdir()):
            continue
        out.mkdir(parents=True, exist_ok=True)
        sh("ffmpeg", "-v", "error", "-y", "-i", str((ep / src).resolve()),
           "-vf", f"fps={cfg['fps']},scale=-2:1920:flags=lanczos,unsharp=5:5:0.4",
           "-q:v", "2", str(out / "%04d.jpg"))


SR = 48000


def _lp(x, cutoff):
    """one-pole low-pass, applied twice (12 dB/oct) — keeps effects soft, no harsh highs"""
    import numpy as np
    a = np.exp(-2 * np.pi * cutoff / SR)
    for _ in range(2):
        y = np.empty_like(x); acc = 0.0
        # vectorised IIR via lfilter if scipy exists, else python loop on short buffers
        try:
            from scipy.signal import lfilter
            y = lfilter([1 - a], [1, -a], x)
        except Exception:
            for i, v in enumerate(x):
                acc = (1 - a) * v + a * acc; y[i] = acc
        x = y
    return x


def sfx_whoosh(dur=0.7, seed=0):
    import numpy as np
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.linspace(0, 1, n)
    noise = r.standard_normal(n)
    # sweep: band moves up then down; approximate with two low-passes of varying cutoff (blockwise)
    out = np.zeros(n); blk = 512
    for i in range(0, n, blk):
        c = 300 + 2600 * np.sin(np.pi * t[min(i, n - 1)]) ** 2
        out[i:i + blk] = _lp(noise[i:i + blk], c) - _lp(noise[i:i + blk], 120)
    env = np.sin(np.pi * t) ** 2.2
    out = out * env
    return out / (np.abs(out).max() + 1e-9)


def sfx_hit(dur=0.9):
    import numpy as np
    n = int(dur * SR); t = np.arange(n) / SR
    f = 48 + 60 * np.exp(-t / 0.05)                   # pitch-dropping sub
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.28)
    click = _lp(np.random.default_rng(3).standard_normal(n) * np.exp(-t / 0.01), 1800) * 0.25
    out = body + click
    return out / (np.abs(out).max() + 1e-9)


def sfx_riser(dur=1.6):
    import numpy as np
    n = int(dur * SR); t = np.linspace(0, 1, n)
    noise = np.random.default_rng(7).standard_normal(n)
    out = np.zeros(n); blk = 512
    for i in range(0, n, blk):
        out[i:i + blk] = _lp(noise[i:i + blk], 200 + 3200 * t[min(i, n - 1)] ** 2)
    tone = np.sin(2 * np.pi * np.cumsum(110 + 220 * t ** 2) / SR) * 0.35
    out = (out / (np.abs(out).max() + 1e-9) + tone) * t ** 2.5
    out[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return out / (np.abs(out).max() + 1e-9)


def make_sfx_mix(cfg, song_path, out_path):
    import numpy as np, wave
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(song_path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    song = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    n = int((cfg["duration"] + 0.5) * SR)
    fx = np.zeros((n, 2))
    master = 10 ** (cfg.get("sfx_db", -17) / 20)
    for k, e in enumerate(cfg["sfx"]):
        typ, at, g = e["type"], e["at"], e.get("gain", 1.0)
        if typ == "whoosh":
            d = e.get("dur", 0.7); x = sfx_whoosh(d, seed=k); start = at - d / 2
            pan = np.linspace(-0.6, 0.6, len(x)) * (e.get("dir", 1))
        elif typ == "hit":
            x = sfx_hit(); start = at; pan = np.zeros(len(x))
        else:
            d = e.get("dur", 1.6); x = sfx_riser(d); start = at - d; pan = np.zeros(len(x))
        i0 = int(start * SR)
        if i0 < 0: x = x[-i0:]; pan = pan[-i0:]; i0 = 0
        m = min(len(x), n - i0)
        fx[i0:i0 + m, 0] += x[:m] * g * master * np.sqrt(0.5 * (1 - pan[:m]))
        fx[i0:i0 + m, 1] += x[:m] * g * master * np.sqrt(0.5 * (1 + pan[:m]))
    L = min(len(song), n)
    mix = song[:L] + fx[:L]
    # float WAV (no clipping here; the final true-peak limiter handles peaks)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_f32le", str(out_path)], input=mix.astype("<f4").tobytes(), check=True)


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=str(root))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def page_cfg(cfg):
    c = dict(cfg)
    c["frames"] = "frames"
    c["logo"] = "logo.png"
    return c


def render_range(url, cfg, idx, out_path=None, png_dir=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = os.environ.get("CHROME", "/opt/pw-browsers/chromium")
        b = p.chromium.launch(executable_path=exe if os.path.isfile(exe) else None)
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(url)
        pg.evaluate("c => window.init(c)", page_cfg(cfg))
        enc = None
        if out_path:
            enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(cfg["fps"]),
                                    "-c:v", "png", "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                                    "-pix_fmt", "yuv420p", str(out_path)], stdin=subprocess.PIPE)
        for i in idx:
            data = pg.evaluate("i => window.frame(i)", i)
            png = base64.b64decode(data.split(",", 1)[1])
            if enc:
                enc.stdin.write(png)
            if png_dir:
                (png_dir / f"t{i / cfg['fps']:06.2f}.png").write_bytes(png)
        if enc:
            enc.stdin.close(); enc.wait()
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--preview", help="comma-separated seconds; writes PNG stills only")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--build", help="build dir (default: <episode>/build)")
    a = ap.parse_args()

    cfgp = Path(a.config).resolve(); ep = cfgp.parent
    cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    build = Path(a.build).resolve() if a.build else ep / "build"
    build.mkdir(parents=True, exist_ok=True)
    for f in ("template.html",):
        shutil.copy(HERE / f, build / f)
    if not (build / "fonts").exists():
        os.symlink(HERE / "fonts", build / "fonts")
    shutil.copy((HERE / cfg.get("logo_file", "../logos/individual/araz-radio_white.png")).resolve(), build / "logo.png")
    extract_frames(cfg, ep, build)

    srv = serve(build)
    url = f"http://127.0.0.1:{srv.server_address[1]}/template.html"
    fps = cfg["fps"]; n = int(round(cfg["duration"] * fps))

    if a.preview:
        pdir = build / "preview"; pdir.mkdir(exist_ok=True)
        idx = [min(n - 1, int(round(float(s) * fps))) for s in a.preview.split(",")]
        render_range(url, cfg, idx, png_dir=pdir)
        print("preview ->", pdir)
        return

    chunks = [list(range(k * n // a.workers, (k + 1) * n // a.workers)) for k in range(a.workers)]
    parts = [build / f"part{k}.mp4" for k in range(a.workers)]
    ths = [threading.Thread(target=render_range, args=(url, cfg, c, parts[k])) for k, c in enumerate(chunks)]
    for t in ths: t.start()
    for t in ths: t.join()
    lst = build / "parts.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    silent = build / "video_silent.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent))

    # sound design: self-synthesised, soft, low-passed effects under the music (no samples, no copyright)
    au_src = (ep / cfg["audio"]).resolve()
    if cfg.get("sfx"):
        mixed = build / "audio_mix.wav"
        make_sfx_mix(cfg, au_src, mixed)
        au_src = mixed
    # audio: the original recording untouched, only a short tail fade and a true-peak safety limiter
    au = cfg["audio"]; fo = cfg.get("audio_fade_out", 0.4)
    af = f"afade=t=out:st={cfg['duration'] - fo:.3f}:d={fo},alimiter=limit=0.891:level=false,aresample=48000"
    out = ep / cfg["output"]
    sh("ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(au_src),
       "-t", f"{cfg['duration']:.3f}", "-map", "0:v", "-map", "1:a", "-af", af,
       "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out))
    print("done ->", out)


if __name__ == "__main__":
    main()
