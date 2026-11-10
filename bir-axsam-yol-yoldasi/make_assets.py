import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
W,H=1080,1920
EGG=(247,212,148); ORA=(231,105,46); DARK=(34,13,12)
F='/usr/share/fonts/opentype/inter/'
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def star(d,cx,cy,r,col):
    pts=[]
    for k in range(8):
        a=math.pi/4*k - math.pi/2; rr=r if k%2==0 else r*0.28
        pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(pts,fill=col)
# ---------- background ----------
HOR=1080
bg=Image.new('RGB',(W,H))
px=bg.load()
stops=[(0,DARK),(0.45,(92,32,20)),(0.78,ORA),(1.0,EGG)]
for y in range(HOR):
    t=y/HOR
    for i in range(len(stops)-1):
        if stops[i][0]<=t<=stops[i+1][0]:
            c=lerp(stops[i][1],stops[i+1][1],(t-stops[i][0])/(stops[i+1][0]-stops[i][0]));break
    for x in range(W): px[x,y]=c
# sun
sun=Image.new('L',(W,H),0); ImageDraw.Draw(sun).ellipse((540-330,HOR-330,540+330,HOR+330),fill=255)
glow=sun.filter(ImageFilter.GaussianBlur(90))
bg=Image.composite(Image.new('RGB',(W,H),(255,196,120)),bg,glow.point(lambda v:int(v*0.55)))
sunc=Image.new('RGB',(W,H))
sd=ImageDraw.Draw(sunc)
for y in range(HOR-330,HOR):
    t=(y-(HOR-330))/330; sd.line((0,y,W,y),fill=lerp((252,226,170),(244,150,80),t))
bg=Image.composite(sunc,bg,sun)
# sun stripes (retro cut lines)
d=ImageDraw.Draw(bg)
for i,y in enumerate(range(HOR-150,HOR,34)):
    hgt=4+i*3
    d.rectangle((0,y,W,y+hgt),fill=lerp(ORA,(214,90,40),0.5))
# ground
gr=Image.new('RGB',(W,H-HOR)); gd=ImageDraw.Draw(gr)
for y in range(H-HOR):
    gd.line((0,y,W,y),fill=lerp((70,26,18),DARK,min(1,y/500)))
bg.paste(gr,(0,HOR))
d=ImageDraw.Draw(bg)
# road in perspective
vx=540
def road_x(y,frac):  # frac -1..1 across road
    t=(y-HOR)/(H-HOR); half=20+t*720
    return vx+frac*half
poly=[(road_x(HOR,-1),HOR),(road_x(HOR,1),HOR),(road_x(H,1),H),(road_x(H,-1),H)]
d.polygon(poly,fill=(48,22,19))
for s in (-1,1):  # edge lines
    d.polygon([(road_x(HOR,s*1),HOR),(road_x(HOR,s*0.93),HOR),(road_x(H,s*0.93),H),(road_x(H,s*1),H)],fill=ORA)
# dashed centre line, perspective dashes
y=HOR+4; seg=0
while y<H:
    t=(y-HOR)/(H-HOR); L=8+t*150; g=6+t*110
    y2=min(H,y+L)
    d.polygon([(road_x(y,-0.035),y),(road_x(y,0.035),y),(road_x(y2,0.035),y2),(road_x(y2,-0.035),y2)],fill=EGG)
    y=y2+g
# horizon line
d.rectangle((0,HOR-2,W,HOR+2),fill=EGG)
# stars in the sky
random.seed(7)
for (x,y,r) in [(120,330,26),(960,420,34),(860,250,14),(180,620,16),(980,760,18),(70,880,12),(300,180,10),(760,560,10)]:
    star(d,x,y,r,EGG)
# subtle grain
noise=Image.effect_noise((W,H),18).convert('L')
bg=Image.blend(bg,Image.merge('RGB',(noise,noise,noise)),0.035)
bg.save('bg.png')
# ---------- title YOL YOLDAŞI (3D extruded like the logo) ----------
def extruded(text,size,face_top,face_bot,out=DARK,depth=16,skew=-0.18,pad=40):
    font=ImageFont.truetype(F+'InterDisplay-Black.otf',size)
    tb=ImageDraw.Draw(Image.new('L',(1,1))).textbbox((0,0),text,font=font)
    w,h=tb[2]-tb[0]+pad*2+depth,tb[3]-tb[1]+pad*2+depth
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).text((pad-tb[0],pad-tb[1]),text,font=font,fill=255)
    stroke=Image.new('L',(w,h),0); ImageDraw.Draw(stroke).text((pad-tb[0],pad-tb[1]),text,font=font,fill=255,stroke_width=10,stroke_fill=255)
    img=Image.new('RGBA',(w,h),(0,0,0,0))
    for k in range(depth,0,-1):
        sh=ImageChops.offset(stroke,k,k)
        img.paste(Image.new('RGBA',(w,h),out+(255,)),(0,0),sh)
    img.paste(Image.new('RGBA',(w,h),out+(255,)),(0,0),stroke)
    grad=Image.new('RGBA',(w,h)); gdd=ImageDraw.Draw(grad)
    for yy in range(h): gdd.line((0,yy,w,yy),fill=lerp(face_top,face_bot,yy/h)+(255,))
    img.paste(grad,(0,0),m)
    # skew
    img=img.transform((w+int(abs(skew)*h),h),Image.AFFINE,(1,skew,skew*h if skew<0 else 0,0,1,0),Image.BICUBIC)
    return img.crop(img.getbbox())
t1=extruded('YOL',230,(255,236,190),EGG)
t2=extruded('YOLDAŞI',190,(255,236,190),(244,170,96))
w=max(t1.width,t2.width); title=Image.new('RGBA',(w,t1.height+t2.height-30),(0,0,0,0))
title.alpha_composite(t1,((w-t1.width)//2-40,0)); title.alpha_composite(t2,((w-t2.width)//2,t1.height-30))
# rotate slightly like the logo
title=title.rotate(4,resample=Image.BICUBIC,expand=True); title=title.crop(title.getbbox())
title.save('title.png'); print('title',title.size)
# ---------- photo placeholder (replaceable) ----------
PW,PH=760,900
ph=Image.new('RGBA',(PW,PH),(0,0,0,0)); pd=ImageDraw.Draw(ph)
sil=(92,40,30,235)
pd.ellipse((PW/2-140,150,PW/2+140,470),fill=sil)               # head
pd.rounded_rectangle((PW/2-80,420,PW/2+80,540),40,fill=sil)    # neck
pd.pieslice((PW/2-360,500,PW/2+360,1300),180,360,fill=sil)    # shoulders
fnt=ImageFont.truetype(F+'Inter-Bold.otf',40)
for i,line in enumerate(['EKSPERTİN ŞƏKLİ','(Replace ilə dəyişin)']):
    f=fnt if i==0 else ImageFont.truetype(F+'Inter-Medium.otf',30)
    tb=pd.textbbox((0,0),line,font=f); pd.text(((PW-tb[2])/2,40+i*50),line,font=f,fill=EGG+(255,))
ph.save('photo_placeholder.png')
# ---------- sponsor logo placeholder ----------
SW,SH=420,150
sp=Image.new('RGBA',(SW,SH),(0,0,0,0)); sd=ImageDraw.Draw(sp)
sd.rounded_rectangle((3,3,SW-4,SH-4),24,outline=EGG+(255,),width=4)
for x in range(20,SW-20,28): sd.line((x,3,x+12,3),fill=(0,0,0,0),width=6); sd.line((x,SH-4,x+12,SH-4),fill=(0,0,0,0),width=6)
for i,(line,f) in enumerate([('SPONSOR LOGOSU',ImageFont.truetype(F+'Inter-Bold.otf',34)),('Toyota Bakı Mərkəzi',ImageFont.truetype(F+'Inter-Medium.otf',26))]):
    tb=sd.textbbox((0,0),line,font=f); sd.text(((SW-tb[2])/2,34+i*50),line,font=f,fill=EGG+(255,))
sp.save('sponsor_placeholder.png')
# ---------- logos ----------
lg=Image.open('../style/main_logo.png'); lg=lg.crop(lg.getbbox()); lg.thumbnail((640,640),Image.LANCZOS); lg.save('bir_axsam_logo.png'); print('logo',lg.size)
