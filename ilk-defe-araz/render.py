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

    # audio: the original recording untouched, only a short tail fade and a true-peak safety limiter
    au = cfg["audio"]; fo = cfg.get("audio_fade_out", 0.4)
    af = f"afade=t=out:st={cfg['duration'] - fo:.3f}:d={fo},alimiter=limit=0.891:level=false,aresample=48000"
    out = ep / cfg["output"]
    sh("ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str((ep / au).resolve()),
       "-t", f"{cfg['duration']:.3f}", "-map", "0:v", "-map", "1:a", "-af", af,
       "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out))
    print("done ->", out)


if __name__ == "__main__":
    main()
