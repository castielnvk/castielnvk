import cv2,json,numpy as np
F=json.load(open('../w/faces.json'))
P={'L':(90,138),'R':(1031,138)}
def box(k,t):
    # nearest detection within 1s
    best=None;bd=9
    for r in F:
        if r[k] and abs(r['t']-t)<bd: bd=abs(r['t']-t);best=r[k]
    return best
cap=cv2.VideoCapture('/workspace/castielnvk/src_dl/source.mov');fps=cap.get(5)
i=0;prev={};out=[]
bx={}
while True:
    ok=cap.grab()
    if not ok:break
    if i%4==0:
        t=i/fps;_,f=cap.retrieve();g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.int16);row={'t':t}
        for k,(ox,oy) in P.items():
            if i%60==0 or k not in bx: bx[k]=box(k,t)
            b=bx[k]
            if b is None: row[k]=0;continue
            x,y,w,h=b; mx0=ox+x+int(w*.25);mx1=ox+x+int(w*.75);my0=oy+y+int(h*.62);my1=oy+y+int(h*1.0)
            m=g[my0:my1,mx0:mx1]
            fg=g[oy+y:oy+y+int(h*.5),ox+x:ox+x+w]
            if k in prev and prev[k][0].shape==m.shape and prev[k][1].shape==fg.shape:
                row[k]=float(np.abs(m-prev[k][0]).mean()-0.5*np.abs(fg-prev[k][1]).mean())
            else: row[k]=0
            prev[k]=(m,fg)
        out.append(row)
    i+=1
json.dump(out,open('../w/mouth.json','w'))
