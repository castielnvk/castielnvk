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
# ---------- music (original, synthesised): 116.36 BPM house bed in E minor
BEAT=16.5/32; mus=np.zeros((N,2))
def kick(): n=int(.30*SR); t=np.arange(n)/SR; f=45+75*np.exp(-t/0.035); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.11)
def hat(): n=int(.06*SR); return filt(filt(rng.standard_normal(n),'high',6000),'low',11000)*env(n,.001,.014)
def clap(): n=int(.16*SR); x=filt(rng.standard_normal(n),'band',[900,2600]); e=env(n,.001,.05); e[:int(.012*SR)]*=np.abs(np.sin(np.arange(int(.012*SR))/SR*2*np.pi*120)); return x*e
def note(f,dur,cut=900):
    n=int(dur*SR); t=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*k*t)/k for k in range(1,9)); return filt(x,'low',cut)*env(n,.004,dur/3)
def stab(freqs,dur=.22):
    n=int(dur*SR); t=np.arange(n)/SR; x=sum(sum(np.sin(2*np.pi*f*k*t*(1+d))/k for k in (1,2,3,4,5)) for f in freqs for d in (-.003,.003)); return filt(x,'low',2200)*env(n,.005,.07)
E2,G2,A2,B2,D3=82.41,98.0,110.0,123.47,146.83
Em9=[164.81,196.0,246.94,293.66,369.99]; Cmaj7=[130.81,164.81,196.0,246.94,293.66]; Am7=[110.0,130.81,164.81,196.0,261.63]; Bm7=[123.47,146.83,185.0,220.0,293.66]
chords=[Em9,Em9,Cmaj7,Cmaj7,Am7,Am7,Bm7,Bm7]; roots=[E2,E2,65.41*2,65.41*2,A2,A2,B2,B2]
K,Hh,Cl=kick(),hat(),clap()
def active(t): return (t<16.5-0.01) or (17.3<=t<20.0-0.01)
nb=int(DUR/BEAT)+1
for b in range(nb):
    t=b*BEAT; bar=(b//4)%8
    if not active(t): continue
    full = t>=1.9   # sparse intro under the greeting, full groove after first cut
    place(mus,K,t,0.9)
    place(mus,Hh,t+BEAT/2,0.22,0.2)
    if full:
        place(mus,Hh,t+BEAT/4,0.08,-0.3); place(mus,Hh,t+3*BEAT/4,0.10,-0.2)
        if b%2==1: place(mus,Cl,t,0.30)
        r=roots[bar]; place(mus,note(r,BEAT*.45),t+BEAT/2,0.42); 
        if b%4==3: place(mus,note(r*1.5,BEAT*.3),t+3*BEAT/4,0.30)
        if b%4 in (0,2): place(mus,stab(chords[bar]),t+BEAT*.75,0.050,0.25)
        if b%4==1: place(mus,stab(chords[bar]),t+BEAT*.5,0.045,-0.25)
# warm pad swell on end card
def pad(freqs,dur):
    n=int(dur*SR); t=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*t*(1+d)) for f in freqs for d in (-.004,0,.004)); e=np.minimum(1,t/0.08)*np.exp(-t/0.9); return filt(x,'low',1800)*e
place(mus,pad(Em9,1.9),20.0,0.035); place(mus,K,20.0,1.0)
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
# ---------- mix
def rms_db(x): return 20*np.log10(np.sqrt((x**2).mean())+1e-9)
sp=voice[int(2*SR):int(15*SR)]; mm=mus[int(2*SR):int(15*SR)]
g=10**((rms_db(sp)-17.5-rms_db(mm))/20); mus*=g
# lift the bed on the end card, where there is no speech
t=np.arange(N)/SR; lift=1+1.2*np.clip((t-19.85)/0.3,0,1); mus*=lift[:,None]
mix=voice+mus+sfx
fo=int(.5*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
print('voice rms',rms_db(sp),'music rms',rms_db(mus[int(2*SR):int(15*SR)]),'peak',np.abs(mix).max())
sf.write('work/mix_raw.wav',mix*0.8,SR,subtype='PCM_24'); sf.write('work/music_only.wav',mus,SR,subtype='PCM_24'); sf.write('work/sfx_only.wav',sfx,SR,subtype='PCM_24'); sf.write('work/voice_only.wav',voice,SR,subtype='PCM_24')
