import numpy as np, cv2
_VIG = {}
P = {  # per-camera: white-balance gains (R,G,B), midtone gamma, exposure
    'L': dict(wb=(1.035, 0.985, 0.955), gamma=0.76, expo=1.04),
    'R': dict(wb=(1.045, 1.000, 0.940), gamma=0.96, expo=1.00),
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
