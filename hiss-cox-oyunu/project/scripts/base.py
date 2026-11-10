"""v3 base render: original HLG source -> neutral SDR LUT (no extra grade) -> tracked fabric cleanup
-> face-tracked framing (face/shoulders, abdomen cropped out) -> Lanczos 1080x1920. Also cuts the dialog."""
import subprocess, json, os, sys, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from segs import timeline, FPS
from fx import fabric_cleanup

RAW = '../src/raw.mov'; PROXY = '../src/proxy709b.mov'
W, H = 1080, 1920
ZOOM = 1.0                               # full original frame (no zoom: keep the ARAZ wall visible)
CW, CH = int(round(W / ZOOM / 2) * 2), int(round(H / ZOOM / 2) * 2)
FACE_Y_FRAC = 0.37                       # face centre sits at 37 % of frame height
LUT = ("zscale=min=bt2020nc:rin=tv:tin=arib-std-b67:t=arib-std-b67:pin=bt2020:p=bt2020:r=full,format=gbrpf32le,"
       "lut3d=grade.cube:interp=tetrahedral,"
       "zscale=tin=bt709:t=bt709:pin=bt709:p=bt709:min=gbr:m=bt709:rin=full:r=full,format=rgb24")
tl, T = timeline()
V3 = json.load(open('v3_timeline.json')); CACHE = [c for c in V3 if not c['freeze']]
os.makedirs('parts', exist_ok=True)
casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def track(a, b):
    """face centre per output frame for src range [a,b): detect on proxy every 2nd frame, reject outliers, smooth"""
    n = round((b - a) * FPS)
    cap = cv2.VideoCapture(PROXY); cap.set(cv2.CAP_PROP_POS_MSEC, a * 1000)
    pts = []
    for i in range(n):
        ok, fr = cap.read()
        if not ok: break
        if i % 2: continue
        g = cv2.cvtColor(cv2.resize(fr, (540, 960)), cv2.COLOR_BGR2GRAY)
        f = casc.detectMultiScale(g, 1.1, 5, minSize=(60, 60))
        f = [r for r in f if 450 < (r[1] + r[3] / 2) * 2 < 950 and 300 < (r[0] + r[2] / 2) * 2 < 800]
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3]); pts.append((i, (x + w / 2) * 2, (y + h / 2) * 2))
    idx = np.arange(n)
    if not pts: return np.full(n, 600.0), np.full(n, 690.0)
    p = np.array(pts)
    fx = np.interp(idx, p[:, 0], p[:, 1]); fy = np.interp(idx, p[:, 0], p[:, 2])
    def sm(v, s=10):  # ~0.33 s gaussian, edge-padded
        k = np.exp(-0.5 * (np.arange(-3 * s, 3 * s + 1) / s) ** 2); k /= k.sum()
        return np.convolve(np.pad(v, 3 * s, mode='edge'), k, 'valid')
    return sm(fx), sm(fy)

def frame_job(img, fx, fy):
    img = fabric_cleanup(img, fx, fy)
    x0 = int(np.clip(fx - CW / 2, 0, W - CW)); y0 = int(np.clip(fy - FACE_Y_FRAC * CH, 0, H - CH))
    crop = img[y0:y0 + CH, x0:x0 + CW]
    return np.ascontiguousarray(crop)

ENC = '-c:v libx264 -crf 14 -preset medium -pix_fmt yuv420p -colorspace bt709 -color_trc bt709 -color_primaries bt709 -r 30'
meta = []; lst = []; alst = []
last = None
for i, s in enumerate(tl):
    v = f"parts/{i:02d}.mp4"; a = f"parts/{i:02d}.wav"
    if s['freeze']:
        n = round(s['odur'] * FPS)
        cv2.imwrite(f'parts/fr{i}.png', cv2.cvtColor(last, cv2.COLOR_RGB2BGR))
        subprocess.run(f'ffmpeg -loglevel error -y -loop 1 -framerate 30 -i parts/fr{i}.png -frames:v {n} -vf format=yuv420p {ENC} {v}', shell=True, check=True)
        subprocess.run(f'ffmpeg -loglevel error -y -f lavfi -i anullsrc=r=48000:cl=mono -t {s["odur"]:.4f} -c:a pcm_s16le {a}', shell=True, check=True)
        meta.append(dict(id=s['id']))
    elif any(abs(c['src_in'] - s['src_in']) < 1e-3 and abs(c['src_out'] - s['src_out']) < 1e-3 for c in CACHE):
        j = next(k for k, c in enumerate(V3) if not c['freeze'] and abs(c['src_in'] - s['src_in']) < 1e-3 and abs(c['src_out'] - s['src_out']) < 1e-3)
        subprocess.run(f'cp ../v3/parts/{j:02d}.mp4 {v} && cp ../v3/parts/{j:02d}.wav {a}', shell=True, check=True)
        raw = subprocess.run(f'ffmpeg -loglevel error -sseof -0.2 -i {v} -vf "scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24" -f rawvideo -', shell=True, capture_output=True).stdout
        last = np.frombuffer(raw[-W * H * 3:], np.uint8).reshape(H, W, 3).copy()
        meta.append(dict(id=s['id'])); print(s['id'], 'cached', flush=True)
    else:
        d = s['src_out'] - s['src_in']; n = round(d * FPS)
        fxs, fys = track(s['src_in'], s['src_out'])
        dec = subprocess.Popen(f'ffmpeg -loglevel error -ss {s["src_in"]:.3f} -i {RAW} -t {d:.4f} -map 0:v:0 -vf "fps=30,{LUT}" -frames:v {n} -f rawvideo -', shell=True, stdout=subprocess.PIPE)
        enc = subprocess.Popen(f'ffmpeg -loglevel error -y -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r 30 -i - -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" {ENC} {v}', shell=True, stdin=subprocess.PIPE)
        k = 0
        while k < n:
            buf = dec.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            fi = min(k, len(fxs) - 1)
            last = frame_job(img, fxs[fi], fys[fi]); enc.stdin.write(last.tobytes()); k += 1
        while k < n:  # pad if decoder came up short
            enc.stdin.write(last.tobytes()); k += 1
        enc.stdin.close(); enc.wait(); dec.wait()
        subprocess.run(f'ffmpeg -loglevel error -y -ss {s["src_in"]:.3f} -i {PROXY} -t {d:.4f} -map 0:a -ac 1 -af "afade=t=in:d=0.015,afade=t=out:st={d-0.02:.4f}:d=0.02" -ar 48000 -c:a pcm_s16le {a}', shell=True, check=True)
        # face position in OUTPUT coordinates (for graphics placement / punch-in origins)
        x0 = np.clip(fxs - CW / 2, 0, W - CW); y0 = np.clip(fys - FACE_Y_FRAC * CH, 0, H - CH)
        meta.append(dict(id=s['id'], ox=float(np.median((fxs - x0) * ZOOM)), oy=float(np.median((fys - y0) * ZOOM))))
        print(s['id'], 'frames', n, 'face(out)', round(meta[-1]['ox']), round(meta[-1]['oy']), flush=True)
    lst.append(f"file '{v}'"); alst.append(f"file '{a}'")
open('v.txt', 'w').write("\n".join(lst)); open('a.txt', 'w').write("\n".join(alst))
json.dump(meta, open('facemeta.json', 'w'))
json.dump(tl, open('timeline.json', 'w'), indent=1)
subprocess.run('ffmpeg -loglevel error -y -f concat -safe 0 -i v.txt -c copy base.mp4', shell=True, check=True)
subprocess.run('ffmpeg -loglevel error -y -f concat -safe 0 -i a.txt -c:a pcm_s16le dialog_raw.wav', shell=True, check=True)
print('total', T)
