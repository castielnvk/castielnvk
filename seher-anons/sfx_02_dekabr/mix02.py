# Real CC0 SFX (freesound.org) on the 2 Dec clip (gym: grandpa tries a sit-up, gives up, falls asleep).
import numpy as np, soundfile as sf, librosa
SR=48000; D=14.125; N=int(D*SR)+SR; out=np.zeros((N,2)); F='sfxsrc/'
def ld(f,a=0,d=None,fi=.004,fo=.03):
    y,_=librosa.load(F+f,sr=SR,mono=True,offset=a,duration=d); n=len(y); e=np.ones(n); k=int(fi*SR); e[:k]=np.linspace(0,1,k); k2=min(n,int(fo*SR)); e[n-k2:]*=np.linspace(1,0,k2); y=y*e; return y/(np.abs(y).max()+1e-9)
def lvl(y): r=librosa.feature.rms(y=y,frame_length=4096,hop_length=1024)[0]; return 20*np.log10(r.max()+1e-9)
def put(y,t,db,pan=0):
    g=10**((db-lvl(y))/20); i=int(t*SR); y=y[:max(0,N-i)]; out[i:i+len(y),0]+=y*g*np.cos((pan+1)*np.pi/4); out[i:i+len(y),1]+=y*g*np.sin((pan+1)*np.pi/4)
amb=ld('gym_ambience/370967.mp3',5,D+.2,fi=.3,fo=.5)
g1=ld('effort_grunt_man/680135.mp3',0,.3,fo=.08); g2=ld('effort_grunt_man/680135.mp3',.7,.35,fo=.08); g3=ld('effort_grunt_man/680135.mp3',2.68,.45,fo=.1)
sigh=ld('sigh/277043.mp3',.95,1.5,fo=.2)
s1=ld('snoring/432996.mp3',.2,1.7,fo=.15); s2=ld('snoring/432996.mp3',4.7,1.9,fo=.2); s3=ld('snoring/432996.mp3',10.45,1.75,fo=.2)
ch1=ld('chuckle_man/720133.mp3',0,2.1,fo=.2); ch2=ld('chuckle_man/823548.mp3',2.95,.6,fo=.1)
clank=ld('weights_clank/607167.mp3',4.7,.35,fo=.1)
put(amb,0,-32)
put(clank,0.6,-22,.4); put(g1,1.35,-15,-.3); put(g2,2.05,-14,-.3); put(g3,2.8,-12,-.3)
put(sigh,4.05,-14,-.3)
put(s1,5.6,-16,-.3); put(s2,8.0,-15,-.3); put(s3,10.6,-14,-.3)
put(ch1,6.4,-20,.4); put(clank,9.4,-24,.4); put(ch2,12.1,-19,.4)
out=out[:int(D*SR)]; out/=max(1,np.abs(out).max()/.9); sf.write('aud/realsfx.wav',out,SR); print('ok')
