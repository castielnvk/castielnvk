# Synthesize a playful instrumental bed + SFX library (all original, generated here)
import numpy as np, wave, sys
SR=48000
rng=np.random.default_rng(7)
def save(name,x):
    x=np.clip(x,-1,1)
    if x.ndim==1: x=np.stack([x,x],1)
    w=wave.open(name,'wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((x*32767).astype(np.int16).tobytes());w.close()
def env(n,a=0.005,d=0.2,s=0.0,r=None):
    t=np.arange(n)/SR
    e=np.minimum(1,t/max(a,1e-4))*np.exp(-t/max(d,1e-4))
    return e
def ks(freq,dur,bright=0.5,decay=0.996):
    n=int(dur*SR);p=int(SR/freq)
    buf=rng.uniform(-1,1,p)
    # lowpass initial noise for softer tone
    for _ in range(int((1-bright)*4)): buf=0.5*(buf+np.roll(buf,1))
    out=np.zeros(n)
    for i in range(n):
        out[i]=buf[i%p]
        buf[i%p]=decay*0.5*(buf[i%p]+buf[(i+1)%p])
    return out
def mf(m): return 440*2**((m-69)/12)
BPM=104; beat=60/BPM; bar=4*beat
# progression C - Am - F - G7 (bouncy), with a B section Dm-G-Em-A7? keep simple
prog=[[48,60,64,67],[45,60,64,69],[41,60,65,69],[43,59,62,65]]
bars=64
L=int(bars*bar*SR)+SR
mus=np.zeros((L,2))
def add(x,t,pan=0.0,g=1.0):
    i=int(t*SR); n=min(len(x),L-i)
    if n<=0: return
    mus[i:i+n,0]+=x[:n]*g*(1-pan)/1.0
    mus[i:i+n,1]+=x[:n]*g*(1+pan)/1.0
# cache plucks
cache={}
def pl(m,dur,bright=0.6):
    k=(m,round(dur,2),bright)
    if k not in cache: cache[k]=ks(mf(m),dur,bright)
    return cache[k]
def kick():
    n=int(0.35*SR);t=np.arange(n)/SR
    f=50+90*np.exp(-t*30);ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)
def snap():
    n=int(0.18*SR);t=np.arange(n)/SR
    x=rng.uniform(-1,1,n)
    # bandpass-ish: diff
    x=np.diff(np.concatenate([[0],x]))
    e=np.exp(-t*35)+0.6*np.exp(-np.maximum(t-0.012,0)*40)*(t>0.012)
    return x*e*0.5
def hat():
    n=int(0.05*SR);t=np.arange(n)/SR
    x=np.diff(np.concatenate([[0],rng.uniform(-1,1,n)]))
    return x*np.exp(-t*90)*0.25
K,S,H=kick(),snap(),hat()
# melody motif (staccato marimba-ish sine with fast decay) – pentatonic call/response
def mallet(m,dur=0.25):
    n=int(dur*SR);t=np.arange(n)/SR;f=mf(m)
    return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*4*f*t)*np.exp(-t*40))*np.exp(-t*10)
motifA=[(0,72),(0.75,74),(1.5,76),(2,79),(3,76),(3.5,74)]
motifB=[(0,79),(0.5,81),(1,79),(1.5,76),(2.5,74),(3,72)]
for b in range(bars):
    t0=b*bar; ch=prog[b%4]
    sec=(b//8)%3   # 0 light,1 full,2 full+melody
    # bass: root on 1, octave bounce on & of 2, fifth on 3
    r=ch[0]-12
    for (bt,m,d) in [(0,r,0.4),(1.5,r+12,0.2),(2,r+7,0.3),(3,r,0.2),(3.5,r+12,0.15)]:
        add(pl(m,0.5,0.3)*0.9,t0+bt*beat,0,0.55)
    # plucked chords offbeat (ska-ish bounce)
    for bt in [0.5,1.5,2.5,3.5]:
        for j,m in enumerate(ch[1:]):
            add(pl(m,0.3,0.7),t0+bt*beat+j*0.006,(-0.4,0,0.4)[j],0.16)
    if sec>=1:
        for bt in [0,2]: add(K,t0+bt*beat,0,0.5)
        for bt in [1,3]: add(S,t0+bt*beat,0.1,0.5)
    for k in range(8): add(H,t0+k*beat/2+ (0.02 if k%2 else 0),0.3,0.5 if k%2 else 0.3)
    if sec==2 or (b%4==3 and sec==1):
        mot=motifA if b%2==0 else motifB
        for bt,m in mot: add(mallet(m),t0+bt*beat,-0.2,0.18)
# gentle master: soft clip + normalise
mus=np.tanh(mus*1.2); mus/=np.abs(mus).max()*1.12
save('music.wav',mus)
print('music len',len(mus)/SR)
# ---- SFX ----
def tone(f0,f1,dur,shape='sin',dec=8):
    n=int(dur*SR);t=np.arange(n)/SR;f=f0*(f1/f0)**(t/dur);ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph) if shape=='sin' else np.sign(np.sin(ph))*0.5
    return x*np.exp(-t*dec)*np.minimum(1,t/0.003)
def noise(dur): return rng.uniform(-1,1,int(dur*SR))
def lp(x,a): 
    y=np.zeros_like(x);s=0
    a=np.broadcast_to(np.asarray(a,float),x.shape)
    for i in range(len(x)): s+=a[i]*(x[i]-s);y[i]=s
    return y
sfx={}
sfx['pop']=tone(900,300,0.09,dec=40)*0.9
sfx['pop2']=tone(600,1400,0.08,dec=35)*0.8
n=int(0.45*SR);t=np.arange(n)/SR
sfx['whoosh']=lp(noise(0.45),0.08)*np.sin(np.pi*t/0.45)**2*3
sfx['whoosh_up']=lp(noise(0.35),0.12)*(t[:int(0.35*SR)]/0.35)**2*np.exp(-0*t[:int(0.35*SR)])*3
sfx['boing']=(np.sin(2*np.pi*np.cumsum(180+60*np.sin(2*np.pi*14*t))/SR)*np.exp(-t*5))*0.8
sfx['ding']=(np.sin(2*np.pi*1568*t)+0.5*np.sin(2*np.pi*2350*t)+0.3*np.sin(2*np.pi*3136*t))*np.exp(-t*6)*0.5
# rimshot ba-dum-tss
bd=np.zeros(int(1.1*SR))
def put(dst,x,tt,g=1): i=int(tt*SR);m=min(len(x),len(dst)-i);dst[i:i+m]+=x[:m]*g
tom=lambda f:tone(f,f*0.7,0.25,dec=14)
put(bd,tom(220),0,0.8);put(bd,tom(160),0.16,0.8);put(bd,K,0.32,0.6)
cy=np.diff(np.concatenate([[0],noise(0.8)]))*np.exp(-np.arange(int(0.8*SR))/SR*4)*0.35
put(bd,cy,0.32)
sfx['badumtss']=bd
# record scratch
n=int(0.4*SR);t=np.arange(n)/SR
sc=noise(0.4);mod=np.abs(np.sin(2*np.pi*6*t))
sfx['scratch']=lp(sc,0.25)*mod*2.2*np.exp(-t*2)
# cartoon slide whistle down
sfx['slide_down']=tone(1800,300,0.6,dec=2)*0.5
sfx['slide_up']=tone(300,1600,0.5,dec=1.5)*0.5
# camera shutter / freeze
n=int(0.25*SR);t=np.arange(n)/SR
cl=np.zeros(n);put(cl,np.diff(np.concatenate([[0],noise(0.03)]))*np.exp(-np.arange(int(0.03*SR))/SR*150),0);put(cl,np.diff(np.concatenate([[0],noise(0.04)]))*np.exp(-np.arange(int(0.04*SR))/SR*120),0.09)
sfx['shutter']=cl*1.2
# sparkle
sp=np.zeros(int(0.7*SR))
for k,f in enumerate([2093,2637,3136,4186,3520]): put(sp,tone(f,f,0.3,dec=12)*0.3,k*0.06)
sfx['sparkle']=sp
# low "bonk"
sfx['bonk']=tone(320,120,0.2,dec=18)*0.9+lp(noise(0.2),0.3)*np.exp(-np.arange(int(0.2*SR))/SR*60)*0.6
# riser
n=int(1.2*SR);t=np.arange(n)/SR
sfx['riser']=(lp(noise(1.2),0.05+0.2*t/1.2)*2+0.2*np.sin(2*np.pi*np.cumsum(200+800*(t/1.2)**2)/SR))*(t/1.2)**2*0.7
# laugh-ish "honk" (clown horn)
n=int(0.35*SR);t=np.arange(n)/SR
hk=sum(np.sign(np.sin(2*np.pi*f*t))*a for f,a in [(370,0.4),(555,0.25),(740,0.15)])
sfx['honk']=lp(hk,0.3)*np.minimum(1,t/0.01)*np.exp(-t*3)*0.9
# tick-tock / typewriter tick
sfx['tick']=tone(2500,2000,0.03,dec=120)*0.6
# sad trombone wah-wah
st=np.zeros(int(2.2*SR))
for k,(f,d) in enumerate([(311,0.45),(294,0.45),(277,0.45),(262,0.9)]):
    n=int(d*SR);tt=np.arange(n)/SR;vib=1+0.012*np.sin(2*np.pi*6*tt)*(tt>0.2)
    x=sum(np.sin(2*np.pi*f*h*np.cumsum(vib)/SR)/h**1.2 for h in range(1,7))
    x*=np.minimum(1,tt/0.04)*np.minimum(1,(d-tt)/0.06)
    put(st,x*0.25,sum(dd for _,dd in [(311,0.45),(294,0.45),(277,0.45)][:k]))
sfx['sadtrombone']=st
for k,v in sfx.items():
    v=v/ (np.abs(v).max()+1e-9)*0.9
    save(f'sfx_{k}.wav',v)
print('sfx',list(sfx))
