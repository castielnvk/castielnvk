# Real CC0 SFX (freesound.org) on the 3 Dec clip (wedding hall: grandpa drives a kids' toy car).
import numpy as np, soundfile as sf, librosa
SR=48000; D=14.125; N=int(D*SR)+SR; out=np.zeros((N,2)); F='sfxsrc/'
def ld(f,a=0,d=None,fi=.004,fo=.03):
    y,_=librosa.load(F+f,sr=SR,mono=True,offset=a,duration=d); n=len(y); e=np.ones(n); k=int(fi*SR); e[:k]=np.linspace(0,1,k); k2=min(n,int(fo*SR)); e[n-k2:]*=np.linspace(1,0,k2); y=y*e; return y/(np.abs(y).max()+1e-9)
def lvl(y): r=librosa.feature.rms(y=y,frame_length=4096,hop_length=1024)[0]; return 20*np.log10(r.max()+1e-9)
def put(y,t,db,pan=0):
    g=10**((db-lvl(y))/20); i=int(t*SR); y=y[:max(0,N-i)]; out[i:i+len(y),0]+=y*g*np.cos((pan+1)*np.pi/4); out[i:i+len(y),1]+=y*g*np.sin((pan+1)*np.pi/4)
party=ld('party_crowd/450649.mp3',0,D+.2,fi=.3,fo=.5)
motor=ld('toy_car_motor/536339.mp3',.9,2.8,fi=.15,fo=.4)        # electric toy-car whine
horn=ld('toy_horn/564696.mp3',0,.55,fo=.08); horn2=ld('toy_horn/564697.mp3',0,.6,fo=.08)
whoa=ld('surprised_whoa/644747.mp3',.7,1.6,fo=.3)
skid=ld('tire_screech/71736.mp3',5.85,1.0,fi=.03,fo=.3); skid2=ld('tire_screech/71736.mp3',4.0,.6,fi=.03,fo=.2)
cheer=ld('crowd_cheer/651646.mp3',0,2.6,fi=.05,fo=.6); cheer2=ld('crowd_cheer/264377.mp3',9.5,2.6,fi=.2,fo=.8)
put(party,0,-33)
put(motor,0.0,-24,0); put(motor,2.6,-25,0); put(motor,7.6,-24,0); put(motor,10.3,-25,0)
put(horn,0.35,-15,0); put(whoa,2.15,-16,-.4)
put(skid,5.3,-18,.1); put(skid2,6.5,-20,-.1)
put(cheer,8.5,-21,.2); put(horn2,11.4,-15,0); put(cheer2,11.6,-24,0)
out=out[:int(D*SR)]; out/=max(1,np.abs(out).max()/.9); sf.write('aud/realsfx.wav',out,SR); print('ok')
