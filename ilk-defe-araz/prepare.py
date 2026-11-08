#!/usr/bin/env python3
"""Auto-prepare an «İlk dəfə "Araz"da» episode.

    python3 prepare.py episodes/<episode> --date "9 NOYABR" [--base episodes/2026-11-02_donge_son-qerar/config.json]

Expects <episode>/source/ with ONE recording (.mp3/.wav/.m4a) and the Grok AI videos (.mp4).
Does, automatically:
  1. extracts frames (24 fps, 1419x1920);
  2. beat grid + song entry (the drop) from the recording; snaps all anchors to beats;
  3. scans every AI frame: sharpness, faces (count/size/position), ghost/morph detection
     (frames that look like a blend of their neighbours), and marks bad frames;
  4. picks the best clean segments per slot, using different parts of each clip;
  5. builds the member split-screen from the three faces of the cleanest group frame;
  6. writes <episode>/config.json (texts, style, date) + a contact sheet of the chosen shots;
  7. runs person segmentation (BiRefNet_lite) only for the shots that have text behind people.
Review the contact sheet, then: python3 render.py <episode>/config.json
"""
import argparse, copy, glob, json, os, subprocess, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
FPS = 24


def sh(*a):
    subprocess.run(a, check=True)


# ---------------------------------------------------------------- audio
def analyse_audio(path, duration):
    import librosa
    y, sr = librosa.load(path, sr=22050, duration=duration)
    env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, bt = librosa.beat.beat_track(y=y, sr=sr, start_bpm=100)
    beats = librosa.frames_to_time(bt, sr=sr)
    # song entry: the biggest sustained rise of low-frequency energy after the spoken intro
    # song entry = where speech pauses stop: speech has frequent RMS dips, the full mix doesn't
    rms = librosa.feature.rms(y=y, hop_length=512)[0]; db = 20 * np.log10(rms + 1e-9)
    t = librosa.frames_to_time(np.arange(len(db)), sr=sr, hop_length=512)
    win = int(1.5 * sr / 512)
    dips = np.array([np.mean(db[i:i + win] < np.median(db) - 9) for i in range(len(db))])
    cand = [i for i in range(len(db)) if 4.5 < t[i] < 12 and dips[i] < .02]
    drop = float(t[cand[0]]) if cand else 7.8
    snap = lambda x: float(beats[np.argmin(np.abs(beats - x))])
    strength = env[bt]
    return dict(tempo=float(np.atleast_1d(tempo)[0]), beats=[float(b) for b in beats], drop=snap(drop),
                strong=[round(float(b), 2) for b, s in zip(beats, strength) if s >= np.median(strength)], snap=snap)


# ---------------------------------------------------------------- video scan
def scan_clip(fdir):
    import cv2
    cc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    files = sorted(glob.glob(f"{fdir}/*.jpg"))
    small, faces, sharp = [], [], []
    for f in files:
        im = cv2.imread(f); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        s = cv2.resize(g, (355, 480)).astype(np.float32); small.append(s)
        sharp.append(cv2.Laplacian(s, cv2.CV_32F).var())
        fs = cc.detectMultiScale(cv2.resize(g, (710, 960)), 1.08, 5, minSize=(26, 26))
        faces.append([((x + w / 2) / 710, (y + h / 2) / 960, w / 710) for x, y, w, h in fs])
    n = len(files); small = np.array(small); sharp = np.array(sharp)
    # AI morphs/dissolves blur the frame relative to its neighbours: edge energy vs. its ±1 s maximum
    rel = np.array([sharp[i] / np.max(sharp[max(0, i - 24):i + 25]) for i in range(n)])
    rel = np.convolve(rel, np.ones(3) / 3, 'same')
    nf = np.array([len(x) for x in faces])
    bad = (rel < .55) | (sharp < .4 * np.median(sharp))
    bad = np.convolve(bad.astype(float), np.ones(13), 'same') > 0     # pad by ±6 frames
    ghost = 1 - rel
    return dict(n=n, faces=faces, nfaces=nf, sharp=sharp, ghost=ghost, bad=bad)


def clean_runs(scan, need):
    """all start frames with `need` consecutive clean frames"""
    ok = ~scan["bad"]; starts = []
    for i in range(0, scan["n"] - need):
        if ok[i:i + need].all(): starts.append(i)
    return starts


# ---------------------------------------------------------------- plan
SLOTS = [  # role, needs faces, depth (text behind people)
    ("intro", 1, True), ("words", 3, False), ("settle", 2, False), ("drop", 1, True),
    ("drop2", 3, True), ("depth1", 2, True), ("depth2", 1, True), ("finale", 3, True)]


def choose(scans, slots_t, used):
    shots = []
    for (role, nf, depth), (t0, t1) in zip(SLOTS, slots_t):
        need = int((t1 - t0) * FPS) + 2
        best = None
        for clip, sc in scans.items():
            for st in clean_runs(sc, need)[::3]:
                seg = range(st, st + need)
                if any(abs(st - u) < need + 6 for c2, u in used if c2 == clip):   # different part of each clip
                    continue
                fcount = np.median(sc["nfaces"][st:st + need])
                size = np.mean([max([f[2] for f in sc["faces"][k]] or [0]) for k in seg])
                score = -abs(fcount - nf) * 3 + size * 2 + np.mean(sc["sharp"][st:st + need]) / np.median(sc["sharp"]) \
                        - 0.3 * sum(1 for c2, _ in used if c2 == clip) \
                        + (2 * fcount if role in ("finale", "drop2", "words") else 0)    # group poses where the group matters
                if best is None or score > best[0]: best = (score, clip, st)
        if best is None:      # relax: least-bad segment
            for clip, sc in scans.items():
                for st in range(0, sc["n"] - need, 3):
                    sc_ = -sc["bad"][st:st + need].mean()
                    if best is None or sc_ > best[0]: best = (sc_, clip, st)
        _, clip, st = best; used.append((clip, st))
        fs = scans[clip]["faces"][st + need // 2]
        cy = np.mean([f[1] for f in fs]) if fs else .4
        shots.append(dict(start=round(t0, 2), clip=clip, src=round(st / FPS, 2), z=[1.0, 1.05] if nf < 3 else [0.96, 1.0],
                          cx=.5, cy=round(float(np.clip(cy - .05, .3, .5)), 2), depth=depth, role=role))
    return shots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode"); ap.add_argument("--date", required=True)
    ap.add_argument("--time", default="11:00 – 12:00")
    ap.add_argument("--base", default=str(HERE / "episodes/2026-11-02_donge_son-qerar/config.json"))
    ap.add_argument("--build"); ap.add_argument("--no-seg", action="store_true")
    ap.add_argument("--words", type=float, help="time the artist says «ilk dəfə» (kinetic words start here)")
    ap.add_argument("--drop", type=float, help="song entry, if auto-detection is wrong")
    ap.add_argument("--duration", type=float, help="video length (default 18 s, capped by the recording)")
    a = ap.parse_args()
    ep = Path(a.episode).resolve(); src = ep / "source"
    audio = next(f for f in sorted(src.iterdir()) if f.suffix.lower() in (".mp3", ".wav", ".m4a"))
    clips = sorted(f for f in src.iterdir() if f.suffix.lower() == ".mp4")
    base = json.loads(Path(a.base).read_text(encoding="utf-8"))
    cfg = copy.deepcopy(base)
    cfg["audio"] = f"source/{audio.name}"
    cfg["clips"] = {f"ai{i + 1}": f"source/{c.name}" for i, c in enumerate(clips)}
    cfg["lockup"]["date"] = a.date.upper(); cfg["lockup"]["time"] = a.time
    cfg["output"] = f"{ep.name}_9x16.mp4"
    build = Path(a.build) if a.build else ep / "build"
    sys.path.insert(0, str(HERE)); import render
    render.extract_frames(cfg, ep, build)

    import librosa
    alen = librosa.get_duration(path=str(audio))
    cfg["duration"] = round(min(a.duration or 18.0, alen - 0.05), 2)
    au = analyse_audio(str(audio), cfg["duration"]); snap = au["snap"]
    B = au["beats"]; beat = float(np.median(np.diff(B)))
    bar = beat * 4
    words = a.words if a.words else snap(3.85); A = dict(words=words, words2=snap(words + beat), words3=snap(words + 2 * beat), settle=snap(words + 3 * beat))
    split_in = snap(words - 2 * beat)
    drop = a.drop if a.drop else au["drop"]
    if drop < A["settle"] + beat * .9:                  # the song can't enter before the lockup settles
        drop = min(b for b in B if b >= A["settle"] + beat * .9)
    finale = snap(drop + 3 * bar)
    cuts = [0, words, A["settle"], drop, snap(drop + .5 * bar), snap(drop + bar), snap(drop + 2 * bar), finale, cfg["duration"]]
    print(f"tempo {au['tempo']:.1f}  drop {drop:.2f}  anchors {A}")

    scans = {k: scan_clip(build / "frames" / k) for k in cfg["clips"]}
    for k, s in scans.items(): print(k, "bad frames:", int(s["bad"].sum()), "/", s["n"])
    shots = choose(scans, list(zip(cuts[:-1], cuts[1:])), [])

    # member split: three faces of the cleanest group frame, left → right
    grp = [(k, i) for k, s in scans.items() for i in range(s["n"]) if s["nfaces"][i] == 3 and not s["bad"][i]]
    if grp:
        def gscore(ki):                      # three similar, large faces at the same height
            fs = scans[ki[0]]["faces"][ki[1]]; ys = [f[1] for f in fs]; ws = [f[2] for f in fs]
            return min(ws) - 2 * (max(ys) - min(ys)) - (max(ws) - min(ws))
        k, i = max(grp, key=gscore)
        fs = sorted(scans[k]["faces"][i])
        cfg["split"] = dict(in_=None)
        cfg["split"] = {"in": split_in, "stagger": round(beat / 2, 2), "out": words, "p": base["split"]["p"],
                        "members": [{"clip": k, "src": round(i / FPS, 2), "z": round(0.21 / f[2], 2), "cx": round(f[0], 3), "cy": round(f[1], 3),
                                     "fx": fx, "fy": 680} for f, fx in zip(fs, (180, 540, 900))]}
    else:
        cfg.pop("split", None)                                     # solo artist: no split-screen

    cfg["anchors"] = A
    cfg["shots"] = shots
    cfg["panel"]["in"] = A["settle"]
    cfg["wipes"] = [{"at": drop, "dur": .42}, {"at": finale, "dur": .42}]
    cfg["beats"] = [b for b in au["strong"] if b > A["settle"] + .5]
    for s in shots:
        s.pop("trans", None)
        if s["role"] in ("drop2", "depth2"): s["trans"] = {"type": "push", "dur": .35}
        if s["role"] == "depth1": s["trans"] = {"type": "whip", "dur": .2, "dir": -1}
    # rows follow the anchors
    R = base["rows"]; shift = {0: 0, 3: drop - 7.83, 5: (drop + bar) - 10.43, 6: (drop + 2 * bar) - 12.93, 7: finale - 15.44}
    rows = []
    for i, r in enumerate(R):
        r = dict(r); d = shift[[0, 0, 0, 3, 3, 5, 6, 7][i]]
        r["in"] = round(r["in"] + d, 2)
        if "out" in r: r["out"] = round(r["out"] + d, 2)
        rows.append(r)
    cfg["rows"] = rows
    cfg["shine"] = [round(drop + bar - .0, 2), round(drop + 2 * bar, 2), round(finale + .35, 2)]
    sfx = []
    for e in base["sfx"]:
        e = dict(e); t = e["at"]
        e["at"] = round(t if t < 7 else (t - 7.83 + drop if t < 15 else t - 15.44 + finale), 2); sfx.append(e)
    cfg["sfx"] = sfx
    (ep / "config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    # contact sheet of the chosen shots (first / middle / last frame of each)
    sheet = ep / "auto_shots.jpg"; inputs = []
    for s in shots:
        for f in (0, .5, .95):
            n = int(s["src"] * FPS) + 1 + int(f * 24)
            inputs.append(str(build / "frames" / s["clip"] / f"{min(n, 361):04d}.jpg"))
    lst = build / "sheet.txt"; lst.write_text("".join(f"file '{p}'\n" for p in inputs))
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", "scale=240:-1,tile=6x4", "-frames:v", "1", str(sheet))
    print("config ->", ep / "config.json", "\ncontact sheet ->", sheet)

    if not a.no_seg:
        need = sorted({(s["clip"], n) for s, nx in zip(shots, cuts[1:]) if s["depth"]
                       for n in range(max(1, int(s["src"] * FPS) - 1), min(362, int((s["src"] + nx - s["start"]) * FPS) + 4))})
        sh(sys.executable, "-I", str(HERE / "segment.py"), str(build / "frames"), json.dumps(need))


if __name__ == "__main__":
    main()
