# reads rgb48le frames (graded) on stdin, adds halation, vignette, grain; writes rgb48le
import sys, numpy as np, cv2
W,H=1080,1920; n=W*H*3
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
r=np.sqrt(((xx-W/2)/(W*0.62))**2+((yy-H/2)/(H*0.62))**2)
vig=(1-0.32*np.clip(r-0.35,0,1)**1.6)[...,None].astype(np.float32)
tint=np.array([1.0,0.55,0.32],np.float32)
rng=np.random.default_rng(7)
inp=sys.stdin.buffer; out=sys.stdout.buffer
lim=int(sys.argv[1]) if len(sys.argv)>1 else 10**9; k=0
while k<lim:
    b=inp.read(n*2)
    if len(b)<n*2: break
    f=np.frombuffer(b,np.uint16).reshape(H,W,3).astype(np.float32)/65535
    L=f.max(-1)
    m=np.clip((L-0.78)/0.22,0,1)[...,None]*f
    s=cv2.resize(m,(W//4,H//4),interpolation=cv2.INTER_AREA)
    g=cv2.GaussianBlur(s,(0,0),9)+0.5*cv2.GaussianBlur(s,(0,0),24)
    g=cv2.resize(g,(W,H),interpolation=cv2.INTER_LINEAR)*tint*0.55
    f=1-(1-f)*(1-np.clip(g,0,1))   # screen
    f=f*vig
    gr=cv2.GaussianBlur(rng.standard_normal((H//2,W//2)).astype(np.float32),(0,0),0.6)
    gr=cv2.resize(gr,(W,H))[...,None]
    lum=f.mean(-1,keepdims=True)
    f=f+gr*0.018*(0.4+lum*(1-lum)*2.4)
    out.write((np.clip(f,0,1)*65535+0.5).astype(np.uint16).tobytes()); k+=1
