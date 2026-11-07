# Warm, soft, playful bed: mellow e-piano + round bass + gentle brush groove, low-passed, no clipping
import numpy as np, wave
SR=48000; rng=np.random.default_rng(3)
BPM=96; beat=60/BPM; bar=4*beat; bars=60
L=int(bars*bar*SR)+SR; out=np.zeros((L,2))
def mf(m): return 440*2**((m-69)/12)
def add(x,t,pan=0,g=1):
    i=int(t*SR); n=min(len(x),L-i)
    if n>0: out[i:i+n,0]+=x[:n]*g*(1-pan*0.5); out[i:i+n,1]+=x[:n]*g*(1+pan*0.5)
def epiano(m,dur):
    n=int(dur*SR); t=np.arange(n)/SR; f=mf(m)
    x=np.sin(2*np.pi*f*t)+0.22*np.sin(2*np.pi*2*f*t)*np.exp(-t*3)+0.05*np.sin(2*np.pi*3*f*t)*np.exp(-t*6)
    env=np.minimum(1,t/0.012)*np.exp(-t*1.6)*np.minimum(1,(dur-t)/0.08)
    return x*env*(1+0.08*np.sin(2*np.pi*4.5*t))
def bass(m,dur):
    n=int(dur*SR); t=np.arange(n)/SR; f=mf(m)
    x=np.sin(2*np.pi*f*t)+0.15*np.sin(2*np.pi*2*f*t)
    return x*np.minimum(1,t/0.01)*np.exp(-t*2.5)*np.minimum(1,(dur-t)/0.04)
def kick():
    n=int(0.3*SR); t=np.arange(n)/SR; f=45+50*np.exp(-t*25)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*10)
def brush():
    n=int(0.12*SR); t=np.arange(n)/SR; x=rng.uniform(-1,1,n)
    k=np.ones(12)/12; x=np.convolve(x,k,'same')   # dull it
    return x*np.exp(-t*30)
def mallet(m):
    n=int(0.5*SR); t=np.arange(n)/SR; f=mf(m)
    return np.sin(2*np.pi*f*t)*np.exp(-t*7)*np.minimum(1,t/0.005)
prog=[[48,55,64,71],[45,52,60,67],[41,48,57,64],[43,50,59,64]]  # Cmaj7 Am7 Fmaj7 G6-ish
K,B=kick(),brush()
mel=[[(0,76),(1,79),(1.5,81),(3,79)],[(0,76),(1.5,74),(2,72)],[(0,72),(1,74),(1.5,76),(3,77)],[(0,79),(2,74)]]
for b in range(bars):
    t0=b*bar; ch=prog[b%4]
    # e-piano: chord on 1, light re-hit on the "and" of 2 (bouncy)
    for bt,g in [(0,1.0),(1.5,0.55),(3,0.45)]:
        for j,m in enumerate(ch[1:]): add(epiano(m,1.4),t0+bt*beat+j*0.008,(-0.5,0,0.5)[j],0.10*g)
    for bt,m,d in [(0,ch[0]-12,0.9),(1.5,ch[0]-12,0.4),(2,ch[0]-5,0.9),(3.5,ch[0]-12,0.4)]:
        add(bass(m,d),t0+bt*beat,0,0.32)
    if b%16>=4:
        for bt in [0,2]: add(K,t0+bt*beat,0,0.35)
        for k in range(8): add(B,t0+k*beat/2+(0.03 if k%2 else 0),0.3,0.10 if k%2 else 0.05)
    if b%16>=8:
        for bt,m in mel[b%4]: add(mallet(m),t0+bt*beat,-0.2,0.09)
# gentle low-pass ~4.5 kHz (FFT) + small room
X=np.fft.rfft(out,axis=0); f=np.fft.rfftfreq(len(out),1/SR)
X*=(1/np.sqrt(1+(f/4500)**4))[:,None]; out=np.fft.irfft(X,n=len(out),axis=0)
ir_n=int(0.6*SR); ir=rng.normal(0,1,ir_n)*np.exp(-np.arange(ir_n)/SR*7); ir=np.convolve(ir,np.ones(20)/20,'same'); ir/=np.abs(ir).sum()/3
from numpy.fft import rfft,irfft
N=1<<int(np.ceil(np.log2(len(out)+ir_n)))
wet=np.stack([irfft(rfft(out[:,c],N)*rfft(ir,N),N)[:len(out)] for c in range(2)],1)
out=out*0.85+wet*0.15
out/=np.abs(out).max()/0.8
w=wave.open('music.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
def hf(p):
    w=wave.open(p);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,2).mean(1).astype(float)
    S=np.abs(np.fft.rfft(a[:SR*30]))**2;ff=np.fft.rfftfreq(SR*30,1/SR)
    return 10*np.log10(S[ff>5000].sum()/S.sum())
print('HF share new',round(hf('music.wav'),1),'dB  old',round(hf('music_old.wav'),1),'dB')
