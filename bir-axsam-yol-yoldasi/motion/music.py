# Original 15 s cue «Yol yoldaşı»: warm evening drive, 96 BPM, 6 bars. Rhodes-like FM keys, soft pad, round bass, gentle kick + soft shaker.
import numpy as np, wave
SR=48000; BPM=96; B=60/BPM; DUR=15.0; n=int(SR*DUR)
L=np.zeros(n); R=np.zeros(n)
def midi(m): return 440*2**((m-69)/12)
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*SR); j=min(n,i+len(sig)); s=sig[:j-i]*gain
    L[i:j]+=s*np.sqrt((1-pan)/2); R[i:j]+=s*np.sqrt((1+pan)/2)
def env(dur,a=0.005,d=0.3,s=0.5,r=0.4,total=None):
    total=total or dur+r; t=np.arange(int(total*SR))/SR
    e=np.where(t<a,t/a,np.where(t<a+d,1-(1-s)*(t-a)/d,s))
    rel=t>dur; e[rel]=e[rel]*np.exp(-(t[rel]-dur)/(r/4)); return t,e
def rhodes(m,dur,vel=0.6):
    t,e=env(dur,0.003,1.2,0.25,0.6); f=midi(m)
    idx=2.2*np.exp(-t*6)+0.3
    s=np.sin(2*np.pi*f*t+idx*np.sin(2*np.pi*f*t))*e
    s+=0.25*np.sin(2*np.pi*2*f*t)*np.exp(-t*3)*e   # bell partial
    s*=1+0.08*np.sin(2*np.pi*4.5*t)                # tremolo
    return s*vel
def pad(m,dur):
    t,e=env(dur,0.6,0.5,0.8,1.0); f=midi(m); s=0
    for det in (-0.08,0,0.07):
        ph=2*np.pi*f*(1+det/100)*t; s=s+ (np.sin(ph)+0.3*np.sin(2*ph)+0.12*np.sin(3*ph))
    return s*e/3
def bass(m,dur):
    t,e=env(dur,0.01,0.2,0.7,0.12); f=midi(m)
    return (np.sin(2*np.pi*f*t)+0.2*np.sin(4*np.pi*f*t))*e
def kick():
    t=np.arange(int(0.35*SR))/SR; f=48+70*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def shaker():
    t=np.arange(int(0.09*SR))/SR; x=np.random.default_rng(1).normal(0,1,len(t))
    # soft: band-limit by moving average (no harsh highs)
    k=np.ones(6)/6; x=np.convolve(x,k,'same'); x=x-np.convolve(x,np.ones(40)/40,'same')
    return x*np.exp(-t*45)
# progression (C major, evening colour): Fmaj7 | Em7 | Dm7 | G7sus4 | Fmaj7 | Cmaj9
prog=[([53,57,60,64],41),([52,55,59,62],40),([50,53,57,60],38),([55,60,62,65],43),([53,57,60,64],41),([48,55,59,62,64],36)]
for bar,(ch,bn) in enumerate(prog):
    t0=bar*4*B
    last=bar==len(prog)-1
    for k,m in enumerate(ch): add(pad(m+12,4*B if not last else 5*B),t0,pan=(k-1.5)*0.25,gain=0.05)
    # keys: syncopated comping
    hits=[0,1.5,2.5] if not last else [0]
    for h in hits:
        for k,m in enumerate(ch): add(rhodes(m+12,(1.2 if not last else 4.0)*B,0.5 if h==0 else 0.35),t0+h*B+k*0.012,pan=-0.2+0.12*k,gain=0.11)
    # bass
    pat=[(0,1.5),(1.5,1.0),(2.5,1.4)] if not last else [(0,3.5)]
    for (h,dd) in pat: add(bass(bn if h!=2.5 else bn+7,dd*B*0.9),t0+h*B,gain=0.30)
    # drums from bar 2 (soft), stop on last bar downbeat
    if bar>=1 and not last:
        for beat in (0,2): add(kick(),t0+beat*B,gain=0.42)
        for e8 in range(8): add(shaker(),t0+e8*B/2+(0.02 if e8%2 else 0),pan=0.35,gain=0.05 if e8%2 else 0.03)
    if last: add(kick(),t0,gain=0.35)
# small melodic motif in bars 3 and 5 (road call)
for bar,notes in ((2,[(0,81),(0.5,79),(1,76),(2,74)]),(4,[(0,81),(0.5,79),(1,76),(1.5,79),(2,84)])):
    for h,m in notes: add(rhodes(m,0.8*B,0.45),bar*4*B+h*B+B*2,pan=0.3,gain=0.08)
mix=np.stack([L,R],1)
# fades
fi=int(0.25*SR); mix[:fi]*=np.linspace(0,1,fi)[:,None]
fo=int(1.6*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]**1.5
# gentle tone: one-pole lowpass ~9 kHz to keep it warm
a=np.exp(-2*np.pi*9000/SR)
for c in range(2):
    y=np.zeros(n); prev=0
    x=mix[:,c]
    from scipy.signal import lfilter
    mix[:,c]=lfilter([1-a],[1,-a],x)
mix/=np.max(np.abs(mix))*1.12
w=wave.open('music_raw.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
