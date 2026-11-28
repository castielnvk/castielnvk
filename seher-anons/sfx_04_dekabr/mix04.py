# Real CC0 SFX (freesound.org) on the 4 Dec clip (mall: grandpa takes selfies, the lender holds "BORC" and an empty wallet).
import numpy as np, soundfile as sf, librosa
SR=48000; D=14.125; N=int(D*SR)+SR; out=np.zeros((N,2)); F='sfxsrc/'
def ld(f,a=0,d=None,fi=.004,fo=.03):
    y,_=librosa.load(F+f,sr=SR,mono=True,offset=a,duration=d); n=len(y); e=np.ones(n); k=int(fi*SR); e[:k]=np.linspace(0,1,k); k2=min(n,int(fo*SR)); e[n-k2:]*=np.linspace(1,0,k2); y=y*e; return y/(np.abs(y).max()+1e-9)
def lvl(y): r=librosa.feature.rms(y=y,frame_length=4096,hop_length=1024)[0]; return 20*np.log10(r.max()+1e-9)
def put(y,t,db,pan=0):
    g=10**((db-lvl(y))/20); i=int(t*SR); y=y[:max(0,N-i)]; out[i:i+len(y),0]+=y*g*np.cos((pan+1)*np.pi/4); out[i:i+len(y),1]+=y*g*np.sin((pan+1)*np.pi/4)
mall=ld('mall_ambience/511421.mp3',0,D+.2,fi=.3,fo=.5)
shut=ld('phone_camera_shutter/636540.mp3',.12,.5,fo=.1); shut2=ld('phone_camera_shutter/831761.mp3',0,.6,fo=.1)
paper=ld('paper_rustle/181774.mp3',.95,1.0,fi=.02,fo=.2)
velcro=ld('velcro/536231.mp3',0,.6,fo=.1)
crick=ld('crickets/704381.mp3',0,2.5,fi=.2,fo=.6)
put(mall,0,-32)
put(paper,0.15,-20,-.4)
put(shut,0.65,-14,0); put(velcro,2.75,-17,-.4)
put(crick,4.5,-20,-.4)
put(shut2,6.6,-14,0); put(shut,10.65,-14,0); put(paper,12.55,-20,-.4); put(shut2,13.1,-15,0)
out=out[:int(D*SR)]; out/=max(1,np.abs(out).max()/.9); sf.write('aud/realsfx.wav',out,SR); print('ok')
