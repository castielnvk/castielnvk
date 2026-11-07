import numpy as np, cv2
def smoothstep(e0,e1,x):
    t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
def _band(img, fx, fy, strength, LOWS, cy, rx, ry, y0o, y1o):
    """img: HxWx3 uint8 RGB (source geometry 1080x1920). fx,fy: tracked face centre.
    Reduces mid-frequency relief (5-45 px) on dark, low-saturation fabric in the chest/waist zone."""
    H,W=img.shape[:2]
    f=img.astype(np.float32)
    Y=0.2126*f[...,0]+0.7152*f[...,1]+0.0722*f[...,2]
    # region of interest (bust + upper waist), relative to the face
    y0=int(max(0,fy+y0o)); y1=int(min(H,fy+y1o)); x0=int(max(0,fx-rx-80)); x1=int(min(W,fx+rx+80))
    if y1<=y0 or x1<=x0: return img
    Yr=Y[y0:y1,x0:x1]
    low=cv2.GaussianBlur(Yr,(0,0),LOWS); hi=Yr-cv2.GaussianBlur(Yr,(0,0),1.8); mid=(Yr-low)-hi
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
    # soft elliptical zone: centre ~ fy+590, spans chest to upper waist
    d=((xx-fx)/rx)**2+((yy-(fy+cy))/ry)**2
    zone=1-smoothstep(0.55,1.0,d)
    # gate: only dark, low-saturation pixels (black fabric) — skin, mic fur, wall untouched
    rgb=f[y0:y1,x0:x1]; mx=rgb.max(-1); mn=rgb.min(-1); sat=(mx-mn)/(mx+1e-3)
    gate=(1-smoothstep(95,135,cv2.GaussianBlur(Yr,(0,0),3)))*(1-smoothstep(0.18,0.30,sat))
    gate=cv2.GaussianBlur(gate,(0,0),4)
    w=strength*zone*gate
    dY=-w*mid
    out=f.copy(); out[y0:y1,x0:x1]+=dY[...,None]
    return np.clip(out+0.5,0,255).astype(np.uint8)

def fabric_cleanup(img, fx, fy):
    img = _band(img, fx, fy, 1.0, 28, 600, 300, 250, 330, 900)    # chest: soften relief / outlines
    img = _band(img, fx, fy, 0.8, 40, 860, 330, 230, 600, 1150)   # waist: soften abdominal folds
    return img
