import numpy as np, math, sys, os
from PIL import Image, ImageDraw, ImageFilter
W,H=1920,1080; FPS=25; T=20.0; N=int(FPS*T); TAU=2*math.pi
w,h=960,540  # gradient is smooth: compute at half res, upscale
src=np.asarray(Image.open('fon_src.png').convert('RGB').resize((int(w*1.12),int(h*1.12)),Image.LANCZOS)).astype(np.float32)
SH,SW=src.shape[:2]
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
def sample(img,x,y):
    x=np.clip(x,0,SW-1.001); y=np.clip(y,0,SH-1.001)
    x0=x.astype(int); y0=y.astype(int); fx=(x-x0)[...,None]; fy=(y-y0)[...,None]
    a=img[y0,x0]; b=img[y0,x0+1]; c=img[y0+1,x0]; d=img[y0+1,x0+1]
    return (a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy
mx=(SW-w)/2; my=(SH-h)/2
def gradient(t):
    p=TAU*t/T
    # slow pan in a circle + gentle liquid warp (all periodic in T)
    ox=mx+mx*0.85*math.cos(p); oy=my+my*0.85*math.sin(p)
    wx=14*np.sin(TAU*yy/h*1.0+p)+8*np.sin(TAU*(xx+yy)/w*0.7-2*p)
    wy=10*np.cos(TAU*xx/w*0.8+p)+6*np.sin(TAU*(xx-yy)/w*0.9+p)
    img=sample(src,xx+ox+wx,yy+oy+wy)
    # diagonal light streaks drifting (like the light bands in the artwork)
    ang=math.radians(-22); u=(xx*math.cos(ang)+yy*math.sin(ang))
    sp=420.0; pos=(u/sp - t/T*2)%1.0
    band=np.exp(-((pos-0.5)/0.10)**2)
    band2=np.exp(-(((u/sp*0.6 + t/T)%1.0)-0.5)**2/0.03)
    light=0.10*band+0.07*band2
    glowc=np.array([255,120,255],np.float32)
    img=img+(glowc-img)*light[...,None]
    # orbiting soft glow
    gx=w*(0.62+0.18*math.cos(p)); gy=h*(0.62+0.16*math.sin(2*p))
    g=np.exp(-((xx-gx)**2+(yy-gy)**2)/(2*(w*0.22)**2))*0.12
    img=img+(np.array([255,90,230],np.float32)-img)*g[...,None]
    return img

rng=np.random.default_rng(3)
PART=[dict(x=rng.uniform(0,W),y=rng.uniform(0,H),r=rng.uniform(6,26),k=1,amp=rng.uniform(10,40),
           ph=rng.uniform(0,TAU),tw=rng.uniform(0,TAU),star=rng.random()<0.3) for _ in range(34)]
def particles(t):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for q in PART:
        y=(q['y']-(H+80)*t/T)%(H+80)-40
        x=q['x']+q['amp']*math.sin(TAU*t/T*2+q['ph'])
        tw=0.5+0.5*math.sin(TAU*t/T*4+q['tw'])
        if q['star']:
            r=4+3*tw; a=int(150*tw)
            d.polygon([(x,y-r*2),(x+r*0.3,y-r*0.3),(x+r*2,y),(x+r*0.3,y+r*0.3),(x,y+r*2),(x-r*0.3,y+r*0.3),(x-r*2,y),(x-r*0.3,y-r*0.3)],fill=(255,240,160,a))
        else:
            r=q['r']; d.ellipse([x-r,y-r,x+r,y+r],fill=(255,190,255,int(28+22*tw)))
    return im.filter(ImageFilter.GaussianBlur(1.5))

grain=[rng.normal(0,0.9,(H,W,1)).astype(np.float32) for _ in range(6)]
def frame(i):
    t=i/FPS
    g=Image.fromarray(np.clip(gradient(t),0,255).astype(np.uint8)).resize((W,H),Image.BICUBIC)
    a=np.asarray(g).astype(np.float32)+grain[i%6]
    fr=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA')
    fr.alpha_composite(particles(t))
    return fr.convert('RGB')
if __name__=='__main__':
    a,b=int(sys.argv[1]),int(sys.argv[2]); os.makedirs(sys.argv[3],exist_ok=True)
    for i in range(a,b): frame(i).save(f'{sys.argv[3]}/{i:04d}.png',compress_level=1)
