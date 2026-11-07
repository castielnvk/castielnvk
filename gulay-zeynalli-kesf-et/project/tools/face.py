import cv2,json,numpy as np
cap=cv2.VideoCapture('master.mp4')
cc=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
res=[];i=0
while True:
    ok,f=cap.read()
    if not ok:break
    if i%3==0:
        g=cv2.cvtColor(cv2.resize(f,(360,640)),cv2.COLOR_BGR2GRAY)
        fs=cc.detectMultiScale(g,1.1,5,minSize=(50,50))
        if len(fs):
            x,y,w,h=max(fs,key=lambda r:r[2]*r[3]);res.append([i,float(x+w/2)*3,float(y+h/2)*3,float(w)*3])
        else: res.append([i,None,None,None])
    i+=1
json.dump(res,open('face.json','w'))
v=[r for r in res if r[1]];a=np.array([r[1:] for r in v]);print(len(res),len(v),a.min(0),a.max(0),a.mean(0))
