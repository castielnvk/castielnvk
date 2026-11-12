import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt
SR=48000; rng=np.random.default_rng(3); N=int(14.2*SR); out=np.zeros((N,2))
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def bp(x,lo,hi): return sosfilt(butter(2,[lo,hi],'band',fs=SR,output='sos'),x)
def put(x,t,g=1,pan=0):
    i=int(t*SR); x=x[:max(0,N-i)]; l=g*np.cos((pan+1)*np.pi/4); r=g*np.sin((pan+1)*np.pi/4)
    out[i:i+len(x),0]+=x*l; out[i:i+len(x),1]+=x*r
def whoosh(d=.35,f0=500,f1=2600,peak=.6):
    n=int(d*SR); nz=rng.standard_normal(n); t=np.arange(n)/n; y=np.zeros(n); B=1024
    for i in range(0,n,B):  # moving band-pass in blocks w/ crossfade-free approx
        fc=f0*(f1/f0)**(i/n); seg=nz[max(0,i-2048):i+B]; f=bp(seg,fc*.6,min(fc*1.6,9000)); y[i:i+B]=f[-min(B,n-i):] if len(f)>=B else f[:n-i]
    env=np.sin(np.pi*np.clip(t/(2*peak),0,.5))**2*(t<=peak)+np.cos(np.pi/2*np.clip((t-peak)/(1-peak),0,1))**2*(t>peak)
    return lp(y*env,6000)*.9
def thump(f0=110,f1=42,d=.32,click=.5):
    n=int(d*SR); t=np.arange(n)/SR; f=f1+(f0-f1)*np.exp(-t*28); y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*13)
    c=lp(rng.standard_normal(int(.012*SR)),3500)*np.linspace(1,0,int(.012*SR))**2; y[:len(c)]+=c*click; return y
def pop(f0=260,f1=620,d=.09):
    n=int(d*SR); t=np.arange(n)/SR; f=f0+(f1-f0)*(t/d)**.6; y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*38)*np.minimum(1,t/.003)
    return y+lp(rng.standard_normal(n),2500)*np.exp(-t*90)*.25
def tick(fc=1800,d=.03):
    n=int(d*SR); t=np.arange(n)/SR; return bp(rng.standard_normal(n),fc*.7,fc*1.4)*np.exp(-t*160)
def stamp():
    n=int(.12*SR); t=np.arange(n)/SR; return lp(rng.standard_normal(n),1800)*np.exp(-t*45)*1.2+np.pad(thump(150,70,.12,.2),(0,0))[:n]*.8
def wood(fc=820,d=.14):
    n=int(d*SR); t=np.arange(n)/SR; y=np.sin(2*np.pi*fc*t)*np.exp(-t*42)+.5*np.sin(2*np.pi*fc*2.4*t)*np.exp(-t*70); c=tick(2200,.01); y[:len(c)]+=c*.6; return y
def whistle(f0=1500,f1=520,d=.36):
    n=int(d*SR); t=np.arange(n)/SR; f=f0*(f1/f0)**((t/d)**1.3)*(1+.012*np.sin(2*np.pi*11*t)); y=np.sin(2*np.pi*np.cumsum(f)/SR)+.18*np.sin(4*np.pi*np.cumsum(f)/SR)
    env=np.minimum(1,t/.03)*np.minimum(1,(d-t)/.05); br=bp(rng.standard_normal(n),1500,4000)*.12; return lp((y+br)*env,4500)
def air(d=.9):
    n=int(d*SR); t=np.arange(n)/n; return bp(rng.standard_normal(n),2500,6500)*np.sin(np.pi*t)**2
def boing(d=.5,f=150):
    n=int(d*SR); t=np.arange(n)/SR; fm=f*(1+.35*np.sin(2*np.pi*9*t)*np.exp(-t*4)); y=np.sin(2*np.pi*np.cumsum(fm)/SR)+.4*np.sin(4*np.pi*np.cumsum(fm)/SR); return lp(y*np.exp(-t*7)*np.minimum(1,t/.004),2200)
B=0.594; L=121/24
# intro wipe + title
put(whoosh(.38,400,2400,.7),0.0,.55,-.2); put(thump(120,45,.3),0.02,.5)
for i in range(7): put(pop(240+i*38,520+i*60,.06),.08+i*.05,.16,-.5+i*.12)
put(thump(105,40,.34),B,.75); put(stamp(),B,.3)
put(air(.9),.3,.10)
put(stamp(),2*B,.55,-.4)
# telescope gags per loop
put(whistle(),1.24,.20,.3); put(wood(),1.62,.5,.35); put(boing(),1.63,.33,.35); put(pop(),1.62,.3,.35)
put(wood(700),L+1.62,.42,.35); put(pop(300,700),L+1.62,.3,.35); put(boing(.4,170),L+1.63,.22,.35)
put(whistle(1300,480,.33),2*L+1.26,.16,.3); put(wood(900),2*L+1.62,.42,.35); put(pop(),2*L+1.62,.3,.35)
# captions
put(whoosh(.3,700,3000,.6),4*B-.1,.40,-.4)
for k in range(2): put(tick(1700+200*k),4*B+.12+k*.1,.22,-.3)
put(whoosh(.3,600,2800,.6),5*B-.1,.40,-.2)
for k in range(2): put(tick(1900-150*k),5*B+.12+k*.1,.22,0)
put(thump(125,38,.42,.7),6*B,.95); put(pop(220,560,.11),6*B,.45); put(whoosh(.45,2600,500,.15),6*B+.02,.28)
put(tick(1500),7*B,.25,-.5); put(pop(300,520,.06),7*B+.02,.14,-.5)
# loop-cut wipes
for tl in (L,2*L): put(whoosh(.42,450,2600,.5),tl-.2,.48,0)
# title waves
for tw in (10*B,18*B):
    for i in range(7): put(pop(260+i*34,500+i*55,.05),tw+i*.045,.10,-.5+i*.12)
# end badge + final
put(whoosh(.28,800,2800,.7),21*B-.12,.34,-.3); put(pop(240,640,.1),21*B,.42,-.3); put(stamp(),21*B,.3,-.3)
put(thump(120,40,.45,.6),22*B,.8)
out=sosfiltfilt(butter(2,30,'high',fs=SR,output='sos'),out,axis=0)
out/=max(1,np.abs(out).max()/.9); sf.write('sfx.wav',out,SR); print('peak',np.abs(out).max())
