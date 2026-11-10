import numpy as np, parselmouth
from parselmouth.praat import call
from scipy.ndimage import gaussian_filter1d
NAMES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def track(M,sr,lo=75,hi=700):
    snd=parselmouth.Sound(M,sr); p=snd.to_pitch_ac(time_step=0.01,pitch_floor=lo,pitch_ceiling=hi)
    return snd,p.xs(),p.selected_array['frequency']
def notes_of(f0,tun,minlen=10):
    midi=np.where(f0>0,69+12*np.log2(np.maximum(f0,1)/440)-tun,np.nan); notes=[];cur=[]
    for i,m in enumerate(midi):
        if np.isnan(m) or (cur and abs(m-np.median(midi[cur[-15:]]))>0.7):
            if len(cur)>=minlen: notes.append(cur)
            cur=[] if np.isnan(m) else [i]
        else: cur.append(i)
    if len(cur)>=minlen: notes.append(cur)
    out=[]
    for n in notes:
        seg=midi[n]; k=max(1,len(seg)//8); out.append((n,float(np.median(seg[k:-k])),float(np.std(seg[k:-k]))))
    return midi,out
def plan(t,f0,tun,scale,snap_max=0.75,thr=8,long_s=0.25,s_long=0.9,s_short=0.6):
    midi,notes=notes_of(f0,tun); shift=np.zeros(len(f0)); rep=[]
    for n,c,sd in notes:
        cands=[x for x in range(int(c)-2,int(c)+4) if x%12 in scale]; tg=min(cands,key=lambda x:abs(x-c))
        if abs(tg-c)>snap_max: continue
        dev=(c-tg)*100
        if abs(dev)>thr:
            st=s_long if len(n)*0.01>=long_s else s_short
            shift[n]=-dev*st/100; rep.append((t[n[0]],len(n)*0.01,NAMES[tg%12],dev))
    return shift,rep,notes
def apply(snd,M,sr,t,shift,lo=75,hi=700):
    sm=gaussian_filter1d(shift,3)
    man=call(snd,"To Manipulation",0.01,lo,hi); pt=call(man,"Extract pitch tier")
    n=call(pt,"Get number of points"); pts=[(call(pt,"Get time from index",i),call(pt,"Get value at index",i)) for i in range(1,n+1)]
    call(pt,"Remove points between",0,snd.duration)
    for tt,ff in pts: call(pt,"Add point",tt,ff*2**(np.interp(tt,t,sm)/12))
    call([pt,man],"Replace pitch tier"); out=call(man,"Get resynthesis (overlap-add)").values[0]
    out=out[:len(M)]; out=np.pad(out,(0,len(M)-len(out)))
    act=np.interp(np.arange(len(M))/sr,t,(gaussian_filter1d((abs(shift)>0).astype(float),4)>0.02).astype(float)); act=gaussian_filter1d(act,int(0.01*sr))
    return M*(1-act)+out*act
