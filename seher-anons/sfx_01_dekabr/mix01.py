# Real CC0 SFX (freesound.org) on the 1 Dec clip (car wash: grandpa foamed into a "snowman").
import numpy as np, soundfile as sf, librosa
SR=48000; D=14.125; N=int(D*SR)+SR; out=np.zeros((N,2)); F='sfxsrc/'
def ld(f,a=0,d=None,fi=.004,fo=.03):
    y,_=librosa.load(F+f,sr=SR,mono=True,offset=a,duration=d); n=len(y); e=np.ones(n); k=int(fi*SR); e[:k]=np.linspace(0,1,k); k2=min(n,int(fo*SR)); e[n-k2:]*=np.linspace(1,0,k2); y=y*e; return y/(np.abs(y).max()+1e-9)
def lvl(y): r=librosa.feature.rms(y=y,frame_length=4096,hop_length=1024)[0]; return 20*np.log10(r.max()+1e-9)
def put(y,t,db,pan=0):
    g=10**((db-lvl(y))/20); i=int(t*SR); y=y[:max(0,N-i)]; out[i:i+len(y),0]+=y*g*np.cos((pan+1)*np.pi/4); out[i:i+len(y),1]+=y*g*np.sin((pan+1)*np.pi/4)
spray1=ld('pressure_washer/580534.mp3',2.2,3.55,fi=.03,fo=.25); spray2=ld('pressure_washer/580534.mp3',5.8,7.4,fi=.08,fo=.4); hit=ld('pressure_washer/852533.mp3',11.0,.8,fi=.01,fo=.3)
foam=ld('foam_spray/774636.mp3',.3,2.8,fi=.05,fo=.3)
laughA=ld('men_laughing/859265.mp3',3.0,1.3,fi=.02,fo=.2); laughB=ld('men_laughing/859265.mp3',7.5,1.7,fi=.02,fo=.3); laughC=ld('men_laughing/859265.mp3',11.0,2.8,fi=.02,fo=.5)
old=ld('men_laughing/546687.mp3',10.0,1.4,fi=.02,fo=.3)
wipe1=ld('foam_spray/460541.mp3',3.5,.95,fo=.1); wipe2=ld('foam_spray/460541.mp3',.45,.95,fo=.1)
put(spray1,0.0,-15,-.3); put(hit,0.0,-17,-.3); put(foam,0.2,-22,.0)
put(laughA,0.9,-19,.35)
put(wipe1,4.15,-15,0); put(wipe2,5.1,-17,0)
put(spray2,6.72,-16,-.3); put(hit,6.72,-17,-.3); put(foam,6.9,-23,0); put(foam,10.2,-24,0)
put(laughB,7.4,-18,.35); put(old,10.6,-20,0); put(laughC,11.2,-21,.35)
out=out[:int(D*SR)]; out/=max(1,np.abs(out).max()/.9); sf.write('aud/realsfx.wav',out,SR); print('ok')
