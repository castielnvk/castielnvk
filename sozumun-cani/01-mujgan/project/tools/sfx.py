import numpy as np, wave
SR=44100; D=71.9; n=int(SR*D); L=np.zeros(n); R=np.zeros(n); rng=np.random.default_rng(1)
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); s=0.
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
def put(t,sig,g=1.0,pan=0.0):
    i=int(t*SR); m=min(len(sig),n-i); L[i:i+m]+=sig[:m]*g*(1-pan)**.5; R[i:i+m]+=sig[:m]*g*(1+pan)**.5
def whoosh(d=0.6,bright=0.25):
    m=int(d*SR); x=rng.standard_normal(m); env=np.sin(np.linspace(0,np.pi,m))**2
    a=np.linspace(0.02,bright,m)*env+0.01; y=np.empty(m); s=0
    for i in range(m): s+=a[i]*(x[i]-s); y[i]=s
    return y*env/np.max(np.abs(y)+1e-9)
def thud(f=70,d=0.5):
    t=np.arange(int(d*SR))/SR; return np.sin(2*np.pi*f*t*(1+0.6*np.exp(-t*30)))*np.exp(-t*9)
def tick(d=0.08):
    t=np.arange(int(d*SR))/SR; return (np.sin(2*np.pi*2400*t)*0.5+rng.standard_normal(len(t))*0.3)*np.exp(-t*90)
def shimmer(d=2.0,base=880):
    t=np.arange(int(d*SR))/SR; y=sum(np.sin(2*np.pi*base*k*t+k)*np.exp(-t*(1.5+k)) /k for k in (1,1.5,2,3)); return y*np.minimum(1,t*40)/2
def twang(d=0.7):
    t=np.arange(int(d*SR))/SR; return (np.sin(2*np.pi*98*t)+0.4*np.sin(2*np.pi*196*t))*np.exp(-t*7)
put(14.25,shimmer(2.2,660),0.05); put(15.75,whoosh(0.9,0.12),0.05,-0.3)
for k in range(5): put(23.80+k*0.07,whoosh(0.45,0.3),0.035,(k-2)/3)
put(24.40,thud(65,0.4),0.06)
put(30.84,twang(),0.06); put(30.86,whoosh(0.45,0.35),0.06); put(31.27,thud(80,0.35),0.10); put(31.27,tick(0.05),0.05)
for k in range(10): put(35.2+k*0.24,tick(0.05),0.012)
put(42.25,lp(rng.standard_normal(int(1.5*SR)),0.01)*np.exp(-np.arange(int(1.5*SR))/SR*2.5),1.6)
put(47.35,whoosh(1.0,0.2),0.05)
put(56.25,whoosh(0.8,0.2),0.05,-0.5)
put(60.08,whoosh(0.8,0.25),0.05,-0.4); put(60.85,thud(55,0.5),0.10); put(61.45,thud(55,0.4),0.06)
for i in range(6): put(63.42+i*0.21+0.52,tick(0.06),0.035,(i-2.5)/4); put(63.42+i*0.21+0.52,thud(110,0.15),0.03)
put(68.45,shimmer(2.5,520),0.045)
st=np.stack([L,R],1); st=np.clip(st,-1,1)
w=wave.open('sfx.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes()); w.close()
print('peak dBFS',20*np.log10(np.abs(st).max()))
