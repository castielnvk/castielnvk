import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
A='/workspace/castielnvk/gulay-zeynalli-kesf-et/project/assets/'
OUT='/workspace/castielnvk/gulay-zeynalli-kesf-et/highlight/'
S=4  # supersample

def bg(w,h):
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    r=np.sqrt(((xx-w/2)/(w*0.75))**2+((yy-h/2)/(h*0.55))**2)
    c0=np.array([22,104,78]);c1=np.array([5,38,29])
    t=np.clip(r,0,1)[...,None]**1.2
    img=c0*(1-t)+c1*t
    return Image.fromarray(img.astype(np.uint8)).convert('RGBA')

def gold_fill(mask):
    w,h=mask.size
    yy=np.linspace(0,1,h)[:,None,None]
    top=np.array([252,226,160]);mid=np.array([228,176,84]);bot=np.array([184,128,46])
    g=np.where(yy<0.5,top+(mid-top)*(yy/0.5),mid+(bot-mid)*((yy-0.5)/0.5))
    g=np.broadcast_to(g,(h,w,3)).astype(np.uint8)
    im=Image.fromarray(g).convert('RGBA');im.putalpha(mask);return im

def person(d,cx,cy,s,fill):
    # head
    r=0.20*s; d.ellipse([cx-r,cy-0.62*s-r,cx+r,cy-0.62*s+r],fill=fill)
    # shoulders: rounded top block
    w=0.43*s; top=cy-0.30*s; bot=cy+0.12*s
    d.rounded_rectangle([cx-w,top,cx+w,bot+0.4*s],radius=int(0.36*s),fill=fill)

def icon(size):
    W=H=size*S; m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    s=size*S*0.56; cx,cy=W/2-0.06*size*S,H*0.62
    # back person (left), then cut outline, then front person
    back=Image.new('L',(W,H),0); person(ImageDraw.Draw(back),cx-0.30*s,cy-0.04*s,s*0.82,255)
    front=Image.new('L',(W,H),0); person(ImageDraw.Draw(front),cx+0.14*s,cy+0.04*s,s,255)
    gap=front.filter(ImageFilter.MaxFilter(int(0.07*s)//2*2+1))
    m=ImageChops.lighter(ImageChops.subtract(back,gap),front)
    # clip bottom flat
    clip=Image.new('L',(W,H),0); ImageDraw.Draw(clip).rectangle([0,0,W,cy+0.30*s],fill=255)
    m=ImageChops.multiply(m,clip)
    # sparkle star top-right
    def star(x,y,R):
        pts=[]
        for k in range(8):
            ang=np.pi/2*k/2; rr=R if k%2==0 else R*0.34
            pts.append((x+rr*np.cos(ang-np.pi/2),y+rr*np.sin(ang-np.pi/2)))
        ImageDraw.Draw(m).polygon(pts,fill=255)
    star(cx+0.62*s,cy-0.92*s,0.16*s); star(cx+0.88*s,cy-0.66*s,0.10*s)
    return m.resize((size,size),Image.LANCZOS)

def make(w,h,name,text=False):
    im=bg(w,h)
    size=int(min(w,1080)*0.50)
    m=icon(size)
    g=gold_fill(m)
    sh=Image.new('RGBA',(size,size),(0,0,0,0)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(14)).point(lambda v:int(v*0.45)))
    y0=(h-size)//2-(40 if text else 0)
    im.alpha_composite(sh,((w-size)//2,y0+12)); im.alpha_composite(g,((w-size)//2,y0))
    # thin gold ring inside the highlight-circle safe area
    R=int(min(w,1080)*0.40); cx,cy=w//2,h//2
    ring=Image.new('L',(w*2,h*2),0); ImageDraw.Draw(ring).ellipse([2*(cx-R),2*(cy-R),2*(cx+R),2*(cy+R)],outline=255,width=8)
    ring=ring.resize((w,h),Image.LANCZOS)
    rg=Image.new('RGBA',(w,h),(232,184,96,0)); rg.putalpha(ring.point(lambda v:int(v*0.85)))
    im.alpha_composite(rg)
    if text:
        f=ImageFont.truetype(A+'ArchivoX-Bold.ttf',46); t='QONAQLAR'
        tr=10; tw=sum(f.getlength(c) for c in t)+tr*(len(t)-1); x=(w-tw)/2; y=y0+size+6
        d=ImageDraw.Draw(im)
        for c in t: d.text((x,y),c,font=f,fill=(250,224,160,255)); x+=f.getlength(c)+tr
    im.convert('RGB').save(OUT+name,quality=95); print(name)
make(1080,1920,'Qonaqlar_highlight_story_1080x1920.png')
make(1080,1080,'Qonaqlar_highlight_1080x1080.png')
make(1080,1920,'Qonaqlar_highlight_story_yazili_1080x1920.png',text=True)
make(1080,1080,'Qonaqlar_highlight_yazili_1080x1080.png',text=True)
