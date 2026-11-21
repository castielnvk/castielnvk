import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S="/tmp/claude-0/-workspace-castielnvk/2c6eb8ae-60db-51e6-871f-d72b64516f5d/scratchpad/"
F=S+"fonts/"
def font(n,s): return ImageFont.truetype(F+n+".ttf",s)
def tracked(draw_img, text, fnt, cx, y, fill, track, shadow=None, glow=None):
    # measure
    w=sum(fnt.getlength(c) for c in text)+track*(len(text)-1)
    x=cx-w/2
    layer=Image.new("RGBA",draw_img.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    xx=x
    for c in text:
        d.text((xx,y),c,font=fnt,fill=fill); xx+=fnt.getlength(c)+track
    if shadow:
        sh=Image.new("RGBA",draw_img.size,(0,0,0,0)); sh.paste(shadow,(0,0),layer.split()[3])
        sh=sh.filter(ImageFilter.GaussianBlur(18)); draw_img.alpha_composite(sh)
    draw_img.alpha_composite(layer)
def frame(src,lines,out,ys,col,shadow):
    im=Image.open(src).convert("RGBA")
    for (txt,n,sz,tr),y in zip(lines,ys):
        tracked(im,txt.upper().replace("i","İ") if False else txt,font(n,sz),540,y,col,tr,shadow)
    im.convert("RGB").save(out,quality=92)
D=S+"dl/"
# Option A: tonal espresso text in sky (reference-like)
espresso=(46,22,12,235)
frame(D+"f_6.png",[("YETER Kİ SEN İSTE","ArchivoBlk",62,4),("YAPARIM HER ŞEYİ","ArchivoL",42,12)],S+"proj/A1.jpg",[470,570],espresso,None)
frame(D+"f_20.5.png",[("ESİRİN","ArchivoBlk",150,10),("OLDUM","ArchivoL",60,40)],S+"proj/A2.jpg",[420,590],espresso,None)
# Option B: warm ivory with soft shadow, lower third
ivory=(250,240,224,255); sh=Image.new("RGBA",(1080,1920),(20,8,4,170))
frame(D+"f_6.png",[("YETER Kİ SEN İSTE","ArchivoBlk",62,4),("YAPARIM HER ŞEYİ","ArchivoL",42,12)],S+"proj/B1.jpg",[1440,1540],ivory,sh)
frame(D+"f_20.5.png",[("ESİRİN","ArchivoBlk",150,10),("OLDUM","ArchivoL",60,40)],S+"proj/B2.jpg",[1380,1560],ivory,sh)
