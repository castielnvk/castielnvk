import numpy as np, cv2
_VIG = {}
# Lab matching (this episode): per camera -> common target (L* mean/std, skin a/b)
MATCH = {
    'L': dict(lm=118, ls=98, tm=114, ts=94, da=-2.0, db=1.5),
    'R': dict(lm=101, ls=87, tm=114, ts=94, da=0.5, db=-4.0),
}
def _match(img, k):
    p = MATCH[k]
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
    lab[..., 0] = np.clip((lab[..., 0]-p['lm'])*(p['ts']/p['ls'])+p['tm'], 0, 255)
    db = p['db']
    if k == 'R' and lab[..., 2].mean()-128 < -2.5: db = 3.0   # cooler real-host camera: warm slightly instead
    lab[..., 1] += p['da']; lab[..., 2] += db
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
P = {  # per-camera: white-balance gains (R,G,B), midtone gamma, exposure
    'L': dict(wb=(1.0, 1.0, 1.0), gamma=0.86, expo=1.0),
    'R': dict(wb=(1.0, 1.0, 1.0), gamma=1.0, expo=1.0),
}
def _vig(h, w):
    k = (h, w)
    if k not in _VIG:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((x-w/2)/(w/2))**2 + ((y-h*0.45)/(h/2))**2)
        _VIG[k] = (1-0.10*np.clip(r-0.55, 0, 1)**1.6)[..., None]
    return _VIG[k]
def premium(img, k):
    p = P[k]
    img = _match(img, k)
    f = cv2.bilateralFilter(img, 5, 18, 5).astype(np.float32)/255.0      # tame webcam noise
    f *= np.array(p['wb'], np.float32)*p['expo']
    f = np.clip(f, 0, 1)**p['gamma']                                       # midtone lift (keeps blacks)
    # filmic S-curve: deeper blacks, soft highlight roll-off
    f = np.clip((f-0.035)/0.965, 0, 1)
    s = f*f*(3-2*f)
    f = f*0.55+s*0.45
    hi = np.clip(f-0.82, 0, None); f = f-0.55*hi*hi/0.18
    # saturation: gentle boost, but keep it natural
    lum = (f*np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    f = lum+(f-lum)*1.06
    # subtle warmth in shadows->mids (premium skin), tiny teal in deep shadows
    f[..., 0] += 0.012*(1-np.abs(lum[..., 0]-0.55)*1.6).clip(0, 1)
    f[..., 2] += 0.010*(1-lum[..., 0]*3).clip(0, 1)
    f *= _vig(*f.shape[:2])
    f = np.clip(f, 0, 1)
    out = (f*255).astype(np.uint8)
    # light unsharp for crispness
    bl = cv2.GaussianBlur(out, (0, 0), 1.2)
    return cv2.addWeighted(out, 1.35, bl, -0.35, 0)
