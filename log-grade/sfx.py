import numpy as np, wave, sys
sr=48000; T=24.25; N=int(sr*T); t=np.arange(N)/sr
rng=np.random.default_rng(3)
def lp(x,fc):  # one-pole x2
    a=np.exp(-2*np.pi*fc/sr); y=x.copy()
    for _ in range(2):
        z=np.empty_like(y); s=0.0
        # vectorised via lfilter-like loop in chunks
        from scipy.signal import lfilter
        y=lfilter([1-a],[1,-a],y)
    return y
from scipy.signal import lfilter, butter, sosfilt
def bp(x,lo,hi): return sosfilt(butter(2,[lo,hi],'band',fs=sr,output='sos'),x)
def lpf(x,fc): return sosfilt(butter(4,fc,'low',fs=sr,output='sos'),x)
def env(t0,a,d,shape=2):
    e=np.zeros(N); x=t-t0
    up=(x>=0)&(x<a); e[up]=(x[up]/a)**shape
    dn=(x>=a); e[dn]=np.exp(-(x[dn]-a)/d)
    return e
L=np.zeros(N); R=np.zeros(N)
# 1) dark drone: D minor-ish (D2, A2, F3) detuned, slow swell
dr=np.zeros(N)
for f,amp in [(73.42,1),(110.0,.6),(174.61,.35),(146.83,.3)]:
    for dt in (-0.25,0.25):
        dr+=amp*np.sin(2*np.pi*(f+dt)*t+rng.uniform(0,6))
dr=lpf(dr,900)*(0.6+0.4*np.sin(2*np.pi*t/9.0-1.5))
de=np.clip(t/2.5,0,1)**2*np.clip((T-t)/2.0,0,1)
dr*=de*0.05
# 2) sub boom at 0.05 and 18.0
def boom(t0,f0=48,g=0.55,d=1.4):
    x=np.clip(t-t0,0,None); ph=2*np.pi*(f0*x+ (f0*0.8)*(1-np.exp(-x*6))/6)
    b=np.sin(ph)*np.exp(-x/d)*(t>=t0)
    n=lpf(rng.standard_normal(N),300)*np.exp(-x/0.25)*(t>=t0)*0.25
    a=np.clip((t-t0)/0.008,0,1)
    return (b+n)*a*g
bm=boom(0.05,g=0.5)+boom(18.0,f0=44,g=0.6,d=1.8)
# 3) whooshes: band-noise with moving centre, stereo pan
def whoosh(tc,dur,g,rev=False,pan=0.0):
    n=rng.standard_normal(N)
    x=(t-(tc-dur/2))/dur; m=(x>=0)&(x<=1)
    e=np.zeros(N); xs=x[m]; e[m]=(np.sin(np.pi*xs)**2) if not rev else xs**3*(xs<1)
    out=np.zeros(N)
    for lo,hi in [(150,500),(300,900),(500,1600)]:
        out+=bp(n,lo,hi)
    out=lpf(out,2200)*e*g
    l=out*np.sqrt((1-pan)/2); r=out*np.sqrt((1+pan)/2)
    return l,r
for args in [(2.9,1.6,0.22,False,-0.6),(20.4,1.3,0.16,False,0.5)]:
    l,r=whoosh(*args); L+=l; R+=r
# 4) riser 16.3->18.0 : rising filtered noise + rising tone, cut at hit
rs=(t>=16.3)&(t<18.0); x=np.zeros(N); x[rs]=(t[rs]-16.3)/1.7
n=rng.standard_normal(N); riser=np.zeros(N)
for k,(lo,hi) in enumerate([(200,600),(400,1200),(800,2000)]):
    riser+=bp(n,lo,hi)*x**(2+k)
f=110+220*x**2; riser+=0.4*np.sin(2*np.pi*np.cumsum(f)/sr)*x**2
riser=lpf(riser,2500)*rs*0.18
# 5) soft reverb-ish tail for booms: simple multi-tap
def verb(s):
    o=s.copy()
    for d,g in [(0.031,.5),(0.047,.4),(0.089,.32),(0.13,.25),(0.21,.18),(0.33,.12)]:
        k=int(d*sr); o[k:]+=s[:-k]*g
    return lpf(o,3000)
mono=verb(bm)+dr+verb(riser)
L+=mono; R+=mono
# slight stereo drone width
R+=lpf(np.roll(dr,int(0.012*sr)),900)*0.3; L+=dr*0.3*0
st=np.stack([L,R],1); st/=max(1,np.abs(st).max()/0.89)
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((st*32767).astype('<i2').tobytes())
