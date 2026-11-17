import numpy as np
from PIL import Image, ImageDraw
im=np.asarray(Image.open('src.png')).astype(np.float32)
bg=np.load('bg.npy')
res=np.abs(im-bg).max(-1)
S=1920/1672
out={}
regions={'logo':(595,245,1078,598,True),'araz':(755,55,915,125,False),
 'hafta':(625,665,1045,725,False),'badge':(675,735,1000,815,True),'web':(695,860,980,912,False)}
for n,(x0,y0,x1,y1,fill) in regions.items():
    p=14; X0,Y0,X1,Y1=x0-p,y0-p,x1+p,y1+p
    I2=im[Y0:Y1,X0:X1]; yy,xx=np.mgrid[Y0:Y1,X0:X1]; u=(xx-X0)/(X1-X0)*2-1; v=(yy-Y0)/(Y1-Y0)*2-1
    Bs=np.stack([u**i*v**j for i in range(3) for j in range(3-i)],-1)
    ring=np.ones(I2.shape[:2],bool); ring[p:-p,p:-p]=False
    B2=np.zeros_like(I2)
    for c in range(3):
        coef,*_=np.linalg.lstsq(Bs[ring],I2[...,c][ring],rcond=None); B2[...,c]=Bs@coef
    print(n,'ring err',np.abs(I2-B2).max(-1)[ring].mean())
    B=B2[p:-p,p:-p]
    r=np.abs(im[y0:y1,x0:x1]-B).max(-1); a=np.clip((r-14)/22,0,1)
    if fill:
        b=Image.fromarray(((a>0.5)*255).astype(np.uint8)).convert('L')
        b=Image.fromarray(np.pad(np.asarray(b),1)).copy(); ImageDraw.floodfill(b,(0,0),128)
        holes=(np.asarray(b)[1:-1,1:-1]==0); a[holes]=1
    I=im[y0:y1,x0:x1]
    fg=np.where(a[...,None]>0.02,B+(I-B)/np.maximum(a[...,None],0.02),I)
    rgba=np.dstack([np.clip(fg,0,255),a*255]).astype(np.uint8)
    img=Image.fromarray(rgba,'RGBA')
    w,h=img.size; img=img.resize((round(w*S),round(h*S)),Image.LANCZOS)
    img.save(f'L_{n}.png'); out[n]=(round(x0*S),round(y0*S))
print(out)
