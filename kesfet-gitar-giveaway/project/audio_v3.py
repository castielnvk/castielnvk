import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR=48000; DUR=21.9; N=int(SR*DUR); rng=np.random.default_rng(7)
def filt(x,kind,f,order=2): return sosfilt(butter(order,f,kind,fs=SR,output='sos'),x)
def place(buf,x,t,g=1.0,pan=0.0):
    i=int(t*SR); 
    if i>=len(buf): return
    x=x[:len(buf)-i]; l=g*np.sqrt((1-pan)/2)*1.414; r=g*np.sqrt((1+pan)/2)*1.414
    buf[i:i+len(x),0]+=x*l; buf[i:i+len(x),1]+=x*r
def env(n,a,d): t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-np.maximum(0,t-a)/d)
# ---------- voice
v,sr=sf.read('work/voice_full.wav'); assert sr==SR
def cut(a,b):
    x=v[int(a*SR):int(b*SR)].copy(); f=int(0.012*SR); r=np.linspace(0,1,f)[:,None]; x[:f]*=r; x[-f:]*=r[::-1]; return x
voice=np.zeros((N,2)); s1=cut(0.90,17.40); s2=cut(17.40,20.10)
voice[:len(s1)]+=s1; i=int(17.30*SR); voice[i:i+len(s2)]+=s2
# ---------- music: "Funky Chunk" by Kevin MacLeod (incompetech.com), CC BY 4.0
def stab(freqs,dur=.22):
    n=int(dur*SR); t=np.arange(n)/SR; x=sum(sum(np.sin(2*np.pi*f*k*t*(1+d))/k for k in (1,2,3,4,5)) for f in freqs for d in (-.003,.003)); return filt(x,'low',2200)*env(n,.005,.07)
fk,sr2=sf.read('work/funk.wav'); assert sr2==SR
mus=np.zeros((N,2)); mus[:]=fk[:N]
t=np.arange(N)/SR
gate=np.clip((16.5-t)/0.05,0,1)+np.clip((t-17.3)/0.03,0,1)   # music stop on the freeze frame
mus*=np.clip(gate,0,1)[:,None]
# ---------- sfx (soft, low-passed)
sfx=np.zeros((N,2))
def click():
    n=int(.05*SR); x=filt(rng.standard_normal(n),'band',[1200,4200])*env(n,.0008,.006); t=np.arange(n)/SR; return x+0.6*np.sin(2*np.pi*190*t)*np.exp(-t/.012)
def shutter(): x=np.zeros(int(.2*SR)); c=click(); x[:len(c)]+=c; j=int(.075*SR); x[j:j+len(c)]+=0.8*click(); return x
def whoosh(d=.38,lo=400,hi=3200): n=int(d*SR); x=filt(rng.standard_normal(n),'band',[lo,hi]); return x*np.sin(np.pi*np.arange(n)/n)**2.5
def thump(): n=int(.5*SR); t=np.arange(n)/SR; f=38+60*np.exp(-t/.05); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.16)+0.15*filt(rng.standard_normal(n),'low',300)*np.exp(-t/.05)
def tick(f=1100): n=int(.06*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.76*t))*np.exp(-t/.012)
def flashp(): n=int(.30*SR); t=np.arange(n)/SR; return filt(rng.standard_normal(n),'band',[1500,6000])*np.exp(-t/.05)*np.minimum(1,t/.002)
place(sfx,shutter(),0.0,0.30); place(sfx,flashp(),0.02,0.16); place(sfx,thump(),0.10,0.42)
place(sfx,whoosh(.28),1.52,0.10,-0.3); place(sfx,shutter(),1.64,0.26)
place(sfx,whoosh(.30),3.98,0.11,0.3); place(sfx,flashp(),4.15,0.08)
for i,t in enumerate((5.00,5.07,5.14)): place(sfx,tick(900+i*150),t,0.035)
place(sfx,whoosh(.26),7.46,0.10,-0.3); place(sfx,shutter(),7.57,0.26)
place(sfx,whoosh(.30),9.72,0.11,0.3); place(sfx,flashp(),9.90,0.08)
place(sfx,whoosh(.24),13.27,0.10,-0.3); place(sfx,shutter(),13.37,0.26)
place(sfx,flashp(),14.85,0.05)
# freeze: flash + shutter + thump after the last word, then the stamp
place(sfx,shutter(),16.48,0.42); place(sfx,flashp(),16.50,0.26); place(sfx,thump(),16.52,0.70)
place(sfx,thump(),16.70,0.50); place(sfx,stab([329.63,415.30,493.88,659.25],.5),16.70,0.07)
place(sfx,whoosh(.2),17.12,0.10); place(sfx,shutter(),17.24,0.26)
place(sfx,whoosh(.32),19.74,0.14); place(sfx,flashp(),20.0,0.18); place(sfx,thump(),20.02,0.55)
for i in range(3): place(sfx,tick(700+i*120),20.70+i*0.1,0.05,(-.4+.4*i))
# ---------- v3: cold open ("bu gitarı sizə hədiyyə edəcəm", source 15.80-17.40) + softer sfx
D=1.6; Dn=int(D*SR)
sfx=sosfilt(butter(2,2600,'low',fs=SR,output='sos'),sfx,axis=0)*0.40
cold=np.zeros((Dn,2)); c=cut(15.80,17.40); cold[:len(c)]+=c[:Dn]
voice=np.vstack([cold,voice]); sfx=np.vstack([np.zeros((Dn,2)),sfx]); N=N+Dn
t=np.arange(N)/SR
mus=fk[:N].copy(); gate=np.clip((16.5+D-t)/0.05,0,1)+np.clip((t-17.3-D)/0.03,0,1); mus*=np.clip(gate,0,1)[:,None]
def rms_db(x): return 20*np.log10(np.sqrt((x**2).mean())+1e-9)
sp=voice[int(3.6*SR):int(16.6*SR)]; mm=mus[int(3.6*SR):int(16.6*SR)]
g=10**((rms_db(sp)-17.0-rms_db(mm))/20); mus*=g
lift=1+1.5*np.clip((t-19.85-D)/0.3,0,1); mus*=lift[:,None]
mix=voice+mus+sfx
fo=int(.7*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
print('peak',np.abs(mix).max(),'sfx peak',np.abs(sfx).max(),'dur',N/SR)
sf.write('work/mix_raw.wav',mix*0.8,SR,subtype='PCM_24'); sf.write('work/music_only.wav',mus,SR,subtype='PCM_24'); sf.write('work/sfx_only.wav',sfx,SR,subtype='PCM_24'); sf.write('work/voice_only.wav',voice,SR,subtype='PCM_24')
