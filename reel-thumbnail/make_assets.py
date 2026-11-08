"""Builds the two image layers for the reel cover:
 bg_flag.jpg  - photographic Azerbaijani flag (official construction, from ../zefer-gunu-edit/flag_scenes.py),
                graded dark and desaturated for a documentary look
 p1..p3.jpg   - the real photos of the people in the reel, upscaled if small and graded the same way
                (no face retouching, no generated content)
 bg_war.jpg   - optional real frame from the war footage in the reel, darkened and desaturated
Usage: python make_assets.py OUTDIR [PHOTO1.jpg[@x,y,w,h] [PHOTO2.jpg[@x,y,w,h]]] [bg=FRAME.jpg]
       @x,y,w,h crops the photo (source pixels) before grading"""
import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'zefer-gunu-edit'))
import flag_scenes as fs

def grade(img, sat=0.70, lift=0.0, gain=0.92, warm=0.0):
    """img float 0..1 RGB. Desaturate, soften contrast, slight warm/cool split, film grain."""
    l = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    img = l[..., None] + (img - l[..., None]) * sat
    img = lift + img * gain
    sh = np.clip(1 - l*2, 0, 1)[..., None]          # cool shadows, warm highlights
    hi = np.clip(l*2 - 1, 0, 1)[..., None]
    img = img + sh*np.array([-0.010, 0.004, 0.018], np.float32) + hi*np.array([0.020, 0.008, -0.012], np.float32)*(1+warm)
    rng = np.random.default_rng(7)
    img = img + rng.normal(0, 0.016, img.shape[:2]).astype(np.float32)[..., None]
    return np.clip(img, 0, 1)

def save(path, img):
    cv2.imwrite(path, cv2.cvtColor((img*255+0.5).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 94])

out = sys.argv[1]
photos = [a for a in sys.argv[2:] if not a.startswith('bg=')]
bgs = [a[3:] for a in sys.argv[2:] if a.startswith('bg=')]

def load(arg):
    path, _, box = arg.partition('@')
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32)/255
    if box:
        x, y, w, h = map(int, box.split(',')); im = im[y:y+h, x:x+w]
    return im
os.makedirs(out, exist_ok=True)

# flag: calm folds, slight tilt, emblem upper-centre, darkened
flag = fs.fullframe_flag_real(t=2.0, dur=6.0, cx=640, cy=300, flag_h_frac=0.62, rot_deg=-8,
                              push=0.0, amp=26, speed=0.6, darken=0.30, focus_y=0.30)
save(os.path.join(out, 'bg_flag.jpg'), grade(np.clip(flag, 0, 1), sat=0.62, gain=0.80))

# photos: Lanczos upscale to >=1080 px tall + gentle unsharp mask, same grade
for i, photo in enumerate(photos[:3], 1):
    im = load(photo)
    s = 1080 / min(im.shape[:2])
    if s > 1:
        im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.GaussianBlur(im, (0, 0), 1.6); im = np.clip(im + 0.45*(im - b), 0, 1)
    save(os.path.join(out, f'p{i}.jpg'), grade(im, sat=0.72, gain=0.90))

# war footage frame: cover 1080x1920, soft (phone video), dark, close to monochrome
if bgs:
    im = load(bgs[0]); s = max(1080/im.shape[1], 1920/im.shape[0])
    im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
    y0 = (im.shape[0]-1920)//2; x0 = (im.shape[1]-1080)//2; im = im[y0:y0+1920, x0:x0+1080]
    im = cv2.GaussianBlur(im, (0, 0), 1.0)
    save(os.path.join(out, 'bg_war.jpg'), grade(im, sat=0.45, gain=0.74))
