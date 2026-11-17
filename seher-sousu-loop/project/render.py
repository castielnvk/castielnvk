import numpy as np, math, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops
W,H=1920,1080; FPS=25; T=10.0; N=int(FPS*T); SS=2
S=1920/1672
POS={'logo': (683, 281), 'araz': (867, 63), 'hafta': (718, 764), 'badge': (775, 844), 'web': (798, 988)}
LAY={k:Image.open(f'L_{k}.png') for k in POS}
TAU=2*math.pi
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)

def background(t):
    ph=TAU*t/T
    anchors=[((0,0),(20,3,112)),((0,1080),(45,3,150)),((560,0),(80,4,178)),((1380,0),(125,4,165)),
             ((960+60*math.cos(ph),540+35*math.sin(ph)),(160,6,236)),((560+40*math.sin(ph),470),(108,5,222)),
             ((1840+50*math.sin(ph),690+60*math.cos(ph)),(228,6,172)),((1900,1080),(190,4,158)),((1260,1080),(118,4,170))]
    num=np.zeros((H,W,3),np.float32); den=np.zeros((H,W),np.float32)
    for (ax,ay),c in anchors:
        w=np.exp(-((xx-ax)**2+(yy-ay)**2)/(2*430**2))+1e-6
        num+=w[...,None]*np.array(c,np.float32); den+=w
    return num/den[...,None]

def rot(p,c,a):
    x,y=p[0]-c[0],p[1]-c[1]; ca,sa=math.cos(a),math.sin(a)
    return (c[0]+x*ca-y*sa, c[1]+x*sa+y*ca)

def ease_bump(t,t0,dur):
    u=(t-t0)/dur
    return 0.0 if u<0 or u>1 else math.sin(math.pi*u)

ALARM=(5.8,1.6)  # start, duration
def alarm_shake(t):
    u=(t-ALARM[0])/ALARM[1]
    if u<0 or u>1: return 0.0
    env=math.sin(math.pi*u)**0.6
    return env*math.sin(TAU*14*(t-ALARM[0]))

def deco_layer(t):
    """Clock + sun + sparkles drawn at SSx supersampling, returned as RGBA."""
    im=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); d=ImageDraw.Draw(im)
    s=SS
    # ---- sun (top right) ----
    sc=(1774*s,218*s); sr=281*s
    pulse=0.5+0.5*math.cos(TAU*t/T*2)
    glow=Image.new('RGBA',im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gr=sr*(1.18+0.05*pulse)
    gd.ellipse([sc[0]-gr,sc[1]-gr,sc[0]+gr,sc[1]+gr],fill=(255,120,230,int(40+25*pulse)))
    glow=glow.filter(ImageFilter.GaussianBlur(60*s))
    im.alpha_composite(glow)
    d.ellipse([sc[0]-sr,sc[1]-sr,sc[0]+sr,sc[1]+sr],fill=(255,110,235,int(58+14*pulse)))
    nr=12; spin=TAU/nr*(t/T)
    for i in range(nr):
        a=spin+TAU*i/nr
        breathe=6*s*math.sin(TAU*t/T*2+i)
        r0=sr+30*s+breathe; r1=sr+88*s+breathe; hw=34*s
        tip=(sc[0]+r1*math.cos(a),sc[1]+r1*math.sin(a))
        b1=(sc[0]+r0*math.cos(a)-hw*math.sin(a),sc[1]+r0*math.sin(a)+hw*math.cos(a))
        b2=(sc[0]+r0*math.cos(a)+hw*math.sin(a),sc[1]+r0*math.sin(a)-hw*math.cos(a))
        d.polygon([tip,b1,b2],fill=(255,120,235,62))
    # ---- alarm clock (bottom left) ----
    sh=alarm_shake(t)
    cc=(250*s,800*s); ang=math.radians(5)*sh
    jump=-10*s*abs(sh)
    C=(cc[0],cc[1]+jump)
    R_out=280*s; R_in=200*s
    def P(x,y): return rot((C[0]+x*s,C[1]+y*s),C,ang)
    # legs
    for sx in (-1,1):
        pts=[P(sx*150,215),P(sx*215,330),P(sx*120,265)]
        d.polygon(pts,fill=(150,110,255,60))
    # bells (rounded bars), vibrate during alarm
    for sx in (-1,1):
        bang=math.radians(sx*34)+sx*math.radians(6)*sh
        cx_,cy_=0+305*math.sin(bang),-305*math.cos(bang)
        L=68; th=26
        a0=(cx_-L*math.cos(bang),cy_-L*math.sin(bang)); a1=(cx_+L*math.cos(bang),cy_+L*math.sin(bang))
        p0,p1=P(*a0),P(*a1)
        d.line([p0,p1],fill=(160,120,255,85),width=int(2*th*s))
        for p in (p0,p1): d.ellipse([p[0]-th*s,p[1]-th*s,p[0]+th*s,p[1]+th*s],fill=(160,120,255,85))
    # ring + face
    d.ellipse([C[0]-R_out,C[1]-R_out,C[0]+R_out,C[1]+R_out],fill=(150,110,255,70))
    d.ellipse([C[0]-R_in,C[1]-R_in,C[0]+R_in,C[1]+R_in],fill=(28,0,120,115))
    # dots
    for k in range(12):
        if k%3==0: continue
        a=TAU*k/12; p=P(160*math.sin(a),-160*math.cos(a)); r=11*s
        d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=(150,110,255,120))
    for k in range(4):
        a=TAU*k/4; p=P(160*math.sin(a),-160*math.cos(a)); r=13*s
        d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=(170,135,255,140))
    # hands: minute = one full turn per loop, hour = gentle back-and-forth around 8
    am=TAU*(t/T)
    ah=math.radians(240)+math.radians(4)*math.sin(TAU*t/T)
    def hand(a,length,wid,col):
        tip=P(length*math.sin(a),-length*math.cos(a)); base=P(0,0)
        d.line([base,tip],fill=col,width=int(wid*s))
        r=wid*s/2; d.ellipse([tip[0]-r,tip[1]-r,tip[0]+r,tip[1]+r],fill=col)
    hand(ah,95,12,(175,140,255,170)); hand(am,140,8,(190,160,255,180))
    p=P(0,0); r=30*s; d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=(170,135,255,170))
    r=14*s; d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=(40,0,130,220))
    # ring "brrr" lines during alarm
    if sh!=0:
        u=(t-ALARM[0])/ALARM[1]; env=math.sin(math.pi*u)
        for sx in (-1,1):
            for j,off in enumerate((0,1,2)):
                a=math.radians(sx*(22+off*18)); r0=(360+((t*400+j*30)%40))
                q0=P(r0*math.sin(a),-r0*math.cos(a)); q1=P((r0+45)*math.sin(a),-(r0+45)*math.cos(a))
                d.line([q0,q1],fill=(255,245,90,int(255*env)),width=int(12*s))
    return im.resize((W,H),Image.LANCZOS)

rng=np.random.default_rng(7)
PART=[dict(x=rng.uniform(0,W),y=rng.uniform(0,H),r=rng.uniform(3,9),k=int(rng.integers(1,3)),
           amp=rng.uniform(10,40),ph=rng.uniform(0,TAU),star=rng.random()<0.35,tw=rng.uniform(0,TAU)) for _ in range(46)]
def particles(t):
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for p in PART:
        y=(p['y']-p['k']*(H+60)*t/T)%(H+60)-30
        x=p['x']+p['amp']*math.sin(TAU*t/T+p['ph'])
        tw=0.55+0.45*math.sin(TAU*t/T*3+p['tw'])
        if p['star']:
            r=p['r']*1.6*tw; a=int(210*tw)
            d.polygon([(x,y-r*2),(x+r*0.35,y-r*0.35),(x+r*2,y),(x+r*0.35,y+r*0.35),(x,y+r*2),(x-r*0.35,y+r*0.35),(x-r*2,y),(x-r*0.35,y-r*0.35)],fill=(255,240,150,a))
        else:
            r=p['r']; d.ellipse([x-r,y-r,x+r,y+r],fill=(255,200,255,int(70*tw)))
    return im.filter(ImageFilter.GaussianBlur(0.8))

def shine(layer,t,t0,dur,width=90,strength=0.75):
    u=(t-t0)/dur
    if u<0 or u>1: return layer
    w,h=layer.size
    pos=-width*2+(w+h+width*4)*u
    g=np.clip(1-np.abs((np.arange(w)[None,:]+np.arange(h)[:,None]*0.6)-pos)/width,0,1)**2
    arr=np.asarray(layer).astype(np.float32)
    add=g*strength*255*(arr[...,3]/255)
    arr[...,:3]=np.clip(arr[...,:3]+add[...,None],0,255)
    return Image.fromarray(arr.astype(np.uint8),'RGBA')

def logo_transform(t):
    base=1+0.012*math.sin(TAU*t/T*2)
    u=t-(ALARM[0]+0.15)
    pop=0.0
    if 0<=u<1.8: pop=0.07*math.exp(-3.2*u)*math.sin(TAU*1.6*u)
    sy=base+pop; sx=base+pop*0.6   # little squash & stretch
    dy=-8*math.sin(TAU*t/T)-pop*120
    tilt=1.2*math.sin(TAU*t/T)+ (6*pop/0.07*0.4 if pop else 0)*0
    return sx,sy,dy,tilt

def place(frame,layer,pos,sx=1,sy=1,dy=0,tilt=0):
    w,h=layer.size
    L=layer.resize((max(1,round(w*sx)),max(1,round(h*sy))),Image.BICUBIC) if (sx!=1 or sy!=1) else layer
    if tilt: L=L.rotate(tilt,Image.BICUBIC,expand=True)
    cx=pos[0]+w/2; cy=pos[1]+h/2+dy
    frame.alpha_composite(L,(round(cx-L.width/2),round(cy-L.height/2)))

def shadow(layer,blur=18,alpha=90,off=(0,10)):
    a=layer.split()[3].point(lambda v:v*alpha//255)
    sh=Image.new('RGBA',layer.size,(25,0,70,0)); sh.putalpha(a)
    pad=blur*3; big=Image.new('RGBA',(layer.width+2*pad,layer.height+2*pad),(0,0,0,0)); big.alpha_composite(sh,(pad,pad))
    return big.filter(ImageFilter.GaussianBlur(blur)),pad

LOGO_SH,LP=shadow(LAY['logo'],22,110,(0,14))
grain=[(rng.normal(0,2.2,(H,W,1))).astype(np.float32) for _ in range(6)]

def frame(i):
    t=i/FPS
    bg=background(t)+grain[i%6]
    fr=Image.fromarray(np.clip(bg,0,255).astype(np.uint8)).convert('RGBA')
    fr.alpha_composite(particles(t))
    fr.alpha_composite(deco_layer(t))
    # Araz logo static (official asset), soft shadow only
    fr.alpha_composite(LAY['araz'],POS['araz'])
    sx,sy,dy,tilt=logo_transform(t)
    place(fr,LOGO_SH,(POS['logo'][0]-LP,POS['logo'][1]-LP+14),sx,sy,dy,tilt)
    lg=shine(LAY['logo'],t,1.6,1.1,width=70,strength=0.35)
    place(fr,lg,POS['logo'],sx,sy,dy,tilt)
    # text block: gentle float, badge pulse + shine
    f2=3*math.sin(TAU*t/T+1.2)
    place(fr,LAY['hafta'],POS['hafta'],dy=f2)
    bp=1+0.025*ease_bump(t,3.2,0.6)+0.03*ease_bump(t,ALARM[0]+0.3,0.5)
    place(fr,shine(LAY['badge'],t,3.4,0.9,width=60,strength=0.0) ,POS['badge'],bp,bp,dy=f2)
    place(fr,LAY['web'],POS['web'],dy=f2*0.6)
    return fr.convert('RGB')

if __name__=='__main__':
    a,b=int(sys.argv[1]),int(sys.argv[2]); os.makedirs('frames',exist_ok=True)
    for i in range(a,b): frame(i).save(f'frames/{i:04d}.png',compress_level=1)
