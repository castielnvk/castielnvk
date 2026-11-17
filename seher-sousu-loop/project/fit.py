import numpy as np
from PIL import Image
im=np.asarray(Image.open('src.png')).astype(np.float32)
H,W,_=im.shape
yy,xx=np.mgrid[0:H,0:W]
m=np.ones((H,W),bool)
for x0,y0,x1,y1 in [(740,50,930,130),(590,240,1080,600),(620,660,1050,820),(690,855,985,915),(0,420,480,H),(1210,0,W,530)]:
    m[y0:y1,x0:x1]=False
u=xx/W*2-1; v=yy/H*2-1
def basis(u,v,d=4):
    return np.stack([u**i*v**j for i in range(d+1) for j in range(d+1-i)],-1)
B=basis(u,v)
A=B[m]; bg=np.zeros_like(im)
for c in range(3):
    coef,*_=np.linalg.lstsq(A,im[...,c][m],rcond=None); bg[...,c]=B@coef
res=np.abs(im-bg).max(-1)
print('residual on bg mean/max',res[m].mean(),np.percentile(res[m],99.5))
np.save('bg.npy',bg)
Image.fromarray(np.clip(bg,0,255).astype(np.uint8)).save('bg.png')
Image.fromarray(np.clip(res*3,0,255).astype(np.uint8)).save('diff.png')
