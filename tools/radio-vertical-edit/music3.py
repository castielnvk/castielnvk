# Cheeky, mischievous instrumental: pizzicato strings, staccato tuba-ish bass, sneaky clarinet-like lead,
# soft snaps. Swung 8ths, D minor. Everything low-passed (no harsh highs), no clipping.
import numpy as np, wave
SR=48000; rng=np.random.default_rng(11)
BPM=112; beat=60/BPM; bar=4*beat; bars=72; SW=0.62   # swing ratio
L=int(bars*bar*SR)+SR; out=np.zeros((L,2))
def mf(m): return 440*2**((m-69)/12)
def add(x,t,pan=0,g=1):
    i=int(t*SR); n=min(len(x),L-i)
    if n>0: out[i:i+n,0]+=x[:n]*g*(1-pan*0.5); out[i:i+n,1]+=x[:n]*g*(1+pan*0.5)
def sw(b):  # swung position of an 8th-note index within a beat
    return int(b)*beat + (SW*beat if (b%1)>0.01 else 0)
def pizz(m,dur=0.35):
    n=int(dur*SR);t=np.arange(n)/SR;f=mf(m)
    x=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*18)+0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*30)
    return x*np.minimum(1,t/0.003)*np.exp(-t*11)
def tuba(m,dur=0.28):
    n=int(dur*SR);t=np.arange(n)/SR;f=mf(m)*(1+0.004*np.sin(2*np.pi*5*t))
    ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)+0.5*np.sin(2*ph)+0.25*np.sin(3*ph)+0.1*np.sin(4*ph)
    return x*np.minimum(1,t/0.025)*np.minimum(1,np.maximum(0,(dur-t))/0.05)*0.8
def clar(m,dur=0.2):
    n=int(dur*SR);t=np.arange(n)/SR;f=mf(m)
    ph=2*np.pi*f*t
    x=np.sin(ph)+0.33*np.sin(3*ph)+0.15*np.sin(5*ph)+0.06*np.sin(7*ph)
    return x*np.minimum(1,t/0.015)*np.minimum(1,np.maximum(0,(dur-t))/0.04)
def snap():
    n=int(0.08*SR);t=np.arange(n)/SR;x=rng.uniform(-1,1,n)
    x=np.convolve(x,np.ones(6)/6,'same')
    return x*np.exp(-t*60)
def kick():
    n=int(0.25*SR);t=np.arange(n)/SR;f=50+60*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)
# Dm - Gm/D - A7 - Dm ; second half Bb - A7
roots=[38,38,45,38, 46,45,38,45]
chords={38:[62,65,69],46:[62,65,70],45:[61,64,67,69]}
gm=[62,67,70]
S,K=snap(),kick()
# sneaky lead (original): tiptoe chromatic motif
leadA=[(0,62),(0.5,64),(1,65),(1.5,66),(2,67),(3,69),(3.5,68)]
leadB=[(0,69),(0.5,68),(1,67),(1.5,66),(2,65),(2.5,64),(3,61)]
leadC=[(0,74),(1,72),(1.5,70),(2,69),(3,65),(3.5,66)]
for b in range(bars):
    t0=b*bar; r=roots[b%8]; ch=chords[r] if not (b%8==1) else gm
    sec=(b//8)%4
    # oom-pah bass on beats 1 & 3 (staccato), pickup on 4&
    for bt,m in [(0,r),(2,r+7 if r!=45 else r-5),(3.5,r+12 if sec>=1 else r)]:
        add(tuba(m-12+12,0.24 if bt!=3.5 else 0.14),t0+sw(bt),0,0.30)
    # pizzicato chord stabs on 2 and 4 (+ cheeky off-beat)
    for bt in ([1,3] if sec==0 else [1,2.5,3]):
        for j,m in enumerate(ch): add(pizz(m),t0+sw(bt)+j*0.006,(-0.4,0,0.4,0.2)[j],0.11)
    # soft snaps on 2 & 4
    if sec>=1:
        for bt in [1,3]: add(S,t0+sw(bt),0.2,0.12)
        add(K,t0,0,0.22); add(K,t0+sw(2),0,0.16)
    # lead in sections 1-3
    if sec>=1:
        mot=[leadA,leadB,leadA,leadC][b%4]
        for bt,m in mot: add(clar(m,0.16),t0+sw(bt),-0.15,0.075)
    # pizz counter-line tiptoe in section 3
    if sec==3:
        for k,bt in enumerate([0,0.5,1,1.5,2,2.5,3,3.5]): add(pizz(74-k%4,0.2),t0+sw(bt),0.5,0.05)
# low-pass ~5k + small room
X=np.fft.rfft(out,axis=0); f=np.fft.rfftfreq(len(out),1/SR)
X*=(1/np.sqrt(1+(f/5000)**4))[:,None]; out=np.fft.irfft(X,n=len(out),axis=0)
ir_n=int(0.5*SR); ir=rng.normal(0,1,ir_n)*np.exp(-np.arange(ir_n)/SR*9); ir=np.convolve(ir,np.ones(24)/24,'same'); ir/=np.abs(ir).sum()/3
N=1<<int(np.ceil(np.log2(len(out)+ir_n)))
wet=np.stack([np.fft.irfft(np.fft.rfft(out[:,c],N)*np.fft.rfft(ir,N),N)[:len(out)] for c in range(2)],1)
out=out*0.88+wet*0.12; out/=np.abs(out).max()/0.8
w=wave.open('music.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
S2=np.abs(np.fft.rfft(out[:SR*30,0]))**2;ff=np.fft.rfftfreq(SR*30,1/SR)
print('len',len(out)/SR,'HF>5k share',round(10*np.log10(S2[ff>5000].sum()/S2.sum()),1),'dB')
