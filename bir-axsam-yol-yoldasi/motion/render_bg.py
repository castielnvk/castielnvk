# 15 s animated background for «Yol yoldaşı» (1080x1920, 30 fps) -> raw frames to stdout
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W,H=1080,1920; FPS=30; DUR=15.0; N=int(FPS*DUR)
EGG=np.array([247,212,148]); ORA=np.array([231,105,46]); DARK=np.array([34,13,12])
HOR=1080
def lerp(a,b,t): return a+(b-a)*t
# --- static sky gradient ---
ys=np.arange(HOR)/HOR
stops=[(0,DARK),(0.45,np.array([92,32,20])),(0.78,ORA),(1.0,EGG)]
sky=np.zeros((HOR,3))
for i in range(len(stops)-1):
    a,ca=stops[i]; b,cb=stops[i+1]; m=(ys>=a)&(ys<=b)
    sky[m]=ca+(cb-ca)*((ys[m]-a)/(b-a))[:,None]
sky=np.repeat(sky[:,None,:],W,axis=1)
# --- ground ---
gy=np.arange(H-HOR)
ground=np.array([70,26,18])+(DARK-np.array([70,26,18]))*np.minimum(1,gy/500)[:,None]
ground=np.repeat(ground[:,None,:],W,axis=1)
base=np.concatenate([sky,ground]).astype(np.float32)
XX,YY=np.meshgrid(np.arange(W),np.arange(H))
def ease(t): return 1-(1-min(max(t,0),1))**3
vx=540
def road_x(y,frac):
    t=(y-HOR)/(H-HOR); return vx+frac*(20+t*720)
# road layer (static) as RGBA
road=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(road)
d.polygon([(road_x(HOR,-1),HOR),(road_x(HOR,1),HOR),(road_x(H,1),H),(road_x(H,-1),H)],fill=(48,22,19,255))
for s in (-1,1):
    d.polygon([(road_x(HOR,s),HOR),(road_x(HOR,s*.93),HOR),(road_x(H,s*.93),H),(road_x(H,s),H)],fill=(231,105,46,255))
d.rectangle((0,HOR-2,W,HOR+2),fill=(247,212,148,255))
def star(d,cx,cy,r,col):
    pts=[]
    for k in range(8):
        a=math.pi/4*k-math.pi/2; rr=r if k%2==0 else r*.28
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col)
STARS=[(120,330,26,0.0),(960,420,34,1.3),(860,250,14,2.1),(180,620,16,0.7),(980,760,18,3.0),(70,880,12,1.9),(300,180,10,2.6),(760,560,10,0.4),(560,200,8,1.1),(420,760,9,2.4)]
rng=np.random.default_rng(3)
grains=[rng.normal(0,1,(H//2,W//2)).astype(np.float32) for _ in range(6)]
# road position helper: z in [0,1) along road (0 horizon -> 1 bottom), perspective
def z_to_y(z): return HOR+(H-HOR)*z**2.2
out=sys.stdout.buffer
for f in range(N):
    t=f/FPS
    img=base.copy()
    # sun: rises from below horizon in first 2.5 s, then breathes
    rise=ease(t/2.5)
    scy=HOR+260*(1-rise)
    breath=0.5+0.5*math.sin(2*math.pi*t/5.0)
    R=330
    dist=np.sqrt((XX[:HOR]-540)**2+(YY[:HOR]-scy)**2)
    glow=np.clip(1-(dist-R)/(260+40*breath),0,1)**2*(0.45+0.12*breath)*rise
    img[:HOR]=img[:HOR]+(np.array([255,196,120])-img[:HOR])*glow[...,None]
    inside=dist<=R
    sunrow=np.clip((YY[:HOR]-(scy-R))/R,0,1)
    suncol=np.array([252,226,170])+(np.array([244,150,80])-np.array([252,226,170]))*sunrow[...,None]
    img[:HOR][inside]=suncol[inside]
    # retro stripes scrolling down through the sun
    ph=(t*22)%34
    for i in range(6):
        y0=int(HOR-170+i*34+ph); hgt=int(3+((y0-(HOR-170))/34)*3)
        if HOR-170<=y0<HOR:
            y1=min(HOR,y0+hgt); band=img[y0:y1]
            m=inside[y0:y1]; band[m]=np.array([222,96,42]); img[y0:y1]=band
    # fade in from dark
    fin=ease(t/1.0)
    frame=Image.fromarray(np.clip(img*(0.25+0.75*fin),0,255).astype(np.uint8))
    frame.paste(road,(0,0),road)
    dd=ImageDraw.Draw(frame,'RGBA')
    # moving dashed centre line (dashes flow toward the viewer)
    speed=0.18
    for k in range(14):
        z0=((k/14)+t*speed)%1.0; z1=z0+0.035
        if z1>1: continue
        y0,y1=z_to_y(z0),z_to_y(z1)
        dd.polygon([(road_x(y0,-.035),y0),(road_x(y0,.035),y0),(road_x(y1,.035),y1),(road_x(y1,-.035),y1)],fill=(247,212,148,255))
    # passing roadside marker posts on both edges
    for k in range(6):
        z=((k/6)+t*speed)%1.0
        y=z_to_y(z); s=4+z*26
        for side in (-1,1):
            x=road_x(y,side*1.12)
            dd.rectangle((x-s*.25,y-s*2.2,x+s*.25,y),fill=(247,212,148,int(200*min(1,z*3))))
            dd.rectangle((x-s*.25,y-s*2.2,x+s*.25,y-s*1.7),fill=(231,105,46,int(230*min(1,z*3))))
    # twinkling stars
    for (x,y,r,p) in STARS:
        a=0.55+0.45*math.sin(2*math.pi*(t/2.4)+p*2.0)
        rr=r*(0.85+0.25*a)
        star(dd,x,y,rr,(247,212,148,int(255*a*fin)))
    # warm light sweep across the sky (very soft)
    arr=np.asarray(frame).astype(np.float32)
    g=grains[f%6]; g=np.repeat(np.repeat(g,2,0),2,1)[...,None]
    arr+=g*4.0
    out.write(np.clip(arr,0,255).astype(np.uint8).tobytes())
