# Real CC0 SFX (freesound.org) on the 30 Nov clip (school cafeteria, grandpa eats the kid's lunch).
import numpy as np, soundfile as sf, librosa
SR=48000; D=14.125; N=int(D*SR)+SR; out=np.zeros((N,2)); F='sfxsrc/'
def ld(f,a=0,d=None,fi=.004,fo=.03):
    y,_=librosa.load(F+f,sr=SR,mono=True,offset=a,duration=d); n=len(y); e=np.ones(n); k=int(fi*SR); e[:k]=np.linspace(0,1,k); k2=min(n,int(fo*SR)); e[n-k2:]*=np.linspace(1,0,k2); y=y*e; return y/(np.abs(y).max()+1e-9)
def lvl(y): r=librosa.feature.rms(y=y,frame_length=4096,hop_length=1024)[0]; return 20*np.log10(r.max()+1e-9)
def put(y,t,db,pan=0):  # db = target peak-RMS level
    g=10**((db-lvl(y))/20); i=int(t*SR); y=y[:max(0,N-i)]; out[i:i+len(y),0]+=y*g*np.cos((pan+1)*np.pi/4); out[i:i+len(y),1]+=y*g*np.sin((pan+1)*np.pi/4)
amb=ld('school_cafeteria_ambience/537761.mp3',10,D+.2,fi=.3,fo=.5)
bite=ld('bite_sandwich/365550.mp3',2.08,.4); bite2=ld('bite_sandwich/365550.mp3',1.46,.3)
chew=ld('chewing_food/707805.mp3',.1,1.6,fo=.2); chew2=ld('chewing_food/382662.mp3',.7,1.5,fo=.2)
lid=ld('plastic_box_open/547628.mp3',.22,.35); lid2=ld('plastic_box_open/547628.mp3',3.86,.4)
gulp=ld('gulp/534336.mp3')
put(amb,0,-30)
L=121/24
for k in range(3):
    o=k*L
    put(bite if k!=1 else bite2,o+1.2,-12,.3); put(chew if k!=1 else chew2,o+1.45,-17,.3)
    put(lid if k!=2 else lid2,o+3.25,-14,-.35)
    put(gulp,o+4.4,-14,.3)
out=out[:int(D*SR)]; out/=max(1,np.abs(out).max()/.9); sf.write('aud/realsfx.wav',out,SR); print('ok')
