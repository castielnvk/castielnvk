import cv2,json,numpy as np,sys
cap=cv2.VideoCapture(sys.argv[1]); fps=cap.get(5)
casc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
prof=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_profileface.xml')
P={'L':(90,138,894,895),'R':(1031,138,1834,895)}
res=[];i=0;step=int(fps/4)
prevg={}
while True:
    ok=cap.grab()
    if not ok: break
    if i%step==0:
        ok,f=cap.retrieve();t=i/fps;row={'t':t}
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        for k,(x0,y0,x1,y1) in P.items():
            sub=g[y0:y1,x0:x1]
            d=list(casc.detectMultiScale(sub,1.1,5,minSize=(120,120)))
            if not len(d): d=list(prof.detectMultiScale(sub,1.1,4,minSize=(120,120)))+[(sub.shape[1]-x-w,y,w,h) for (x,y,w,h) in prof.detectMultiScale(cv2.flip(sub,1),1.1,4,minSize=(120,120))]
            row[k]=[int(v) for v in max(d,key=lambda r:r[2]*r[3])] if len(d) else None
            # motion energy in lower face/mouth region later; overall motion
            small=cv2.resize(sub,(100,94))
            row[k+'m']=float(np.abs(small.astype(int)-prevg.get(k,small).astype(int)).mean()); prevg[k]=small
        res.append(row)
    i+=1
json.dump(res,open(sys.argv[2],'w'))
print(len(res))
