import sys,numpy as np,soundfile as sf,pyloudnorm as pyln,subprocess,warnings,json
warnings.filterwarnings("ignore")
from scipy import signal
from scipy.ndimage import gaussian_filter1d
from pedalboard import Pedalboard,HighpassFilter,LowpassFilter,LowShelfFilter,PeakFilter,HighShelfFilter,Compressor,Reverb,Delay
D,W,LIB=sys.argv[1],sys.argv[2],sys.argv[3]; sys.path.insert(0,LIB); import tunelib as T
SR=44100; TUN=-0.03; AMIN={0,2,4,5,7,9,11}; CHROM=set(range(12))
L=int(84.7*SR)
def load(n):
    x,sr=sf.read(f"{D}/{n}.wav"); assert sr==SR; x=x[:L]; return np.pad(x,((0,L-len(x)),(0,0)))
def pb(x,*fx): return Pedalboard(list(fx))(x.astype(np.float32).T,SR).T.astype(np.float64)
def zp(x,sos): return signal.sosfiltfilt(sos,x,axis=0)
def bt(o,f,t): return signal.butter(o,f,t,fs=SR,output='sos')
def env(x,ms=30):
    e=(x**2).mean(1) if x.ndim>1 else x**2
    return np.sqrt(np.maximum(zp(e,bt(2,1000/ms/2,'lp')),1e-14))
def lufs(x,mask=None):
    if mask is not None: x=x[mask]
    return pyln.Meter(SR).integrated_loudness(x)
def deess(x,f0=5500,pct=85,exp=0.6,maxdb=9):
    hb=zp(x,bt(4,f0,'hp')); e=env(hb,8); act=e>10**(-60/20)
    thr=np.percentile(e[act],pct); g=np.minimum(1,(thr/np.maximum(e,1e-9))**exp); g=np.maximum(g,10**(-maxdb/20))
    print(f"   de-ess max GR {20*np.log10(g.min()):.1f} dB"); return x-hb*(1-g)[:,None]
def ride(x,rng=4.0):
    e=env(x,400); act=e>np.percentile(e[e>1e-4],25)*0.5; tgt=np.median(e[act])
    g=np.clip(20*np.log10(tgt/np.maximum(e,1e-6)),-rng,rng); g[~act]=0; g=gaussian_filter1d(g,int(0.15*SR)); return x*(10**(g/20))[:,None]
def width(x,k,hp=0):
    M=x.mean(1);S_=(x[:,0]-x[:,1])/2*k
    if hp: S_=zp(S_,bt(2,hp,'hp'))
    return np.stack([M+S_,M-S_],1)
def tune(x,name,scale,lo=75,hi=700,thr=8,minf=0):
    M=x.mean(1);S_=(x[:,0]-x[:,1])/2; snd,t,f0=T.track(M,SR,lo,hi)
    if minf: f0=np.where(f0<minf,0,f0)
    shift,rep,notes=T.plan(t,f0,TUN,scale,snap_max=0.5,thr=thr); Mo=T.apply(snd,M,SR,t,shift,lo,hi)
    big=sorted([r for r in rep if r[1]>=0.2],key=lambda r:-abs(r[3]))[:8]
    print(f" tune {name}: notes {len(notes)}, corrected {len(rep)}; biggest: "+", ".join(f"{r[0]:.1f}s {r[2]} {r[3]:+.0f}c" for r in big))
    REPORT[name]=[(round(r[0],2),round(r[1],2),r[2],round(r[3])) for r in rep]
    return np.stack([Mo+S_,Mo-S_],1)
def bands(x,lab):
    f,P=signal.welch(x.mean(1),SR,nperseg=8192); ed=[30,60,120,250,500,1000,2000,4000,8000,12000,16000]
    print(f"   {lab:10s}",[int(round(10*np.log10(P[(f>=a)&(f<b)].sum()+1e-20))) for a,b in zip(ed,ed[1:])])
REPORT={}
dr,ba,ot=load("Drums"),load("Bass"),load("Others")
v1,v2,h1,h2,ad=load("VoiceAudio"),load("VoiceAudio_2"),load("VoiceAudio_Copy"),load("VoiceAudio_Copy_Copy"),load("VoiceAudio_Copy_Copy_Copy")
print("raw bands"); [bands(x,n) for x,n in [(dr,"drums"),(ba,"bass"),(ot,"others"),(dr+ba+ot,"beat")]]
# ---------- tuning
v1=tune(v1,"verse lead",AMIN); h1=tune(h1,"hook lead",AMIN); v2=tune(v2,"verse bgv",AMIN); h2=tune(h2,"hook harmony",AMIN)
ad=tune(ad,"adlib",CHROM,thr=12,minf=150)
json.dump(REPORT,open(W+"/tuning_report.json","w"),indent=1)
# ---------- vocals
print("vocals")
v1=ride(v1); v1=pb(v1,HighpassFilter(90),PeakFilter(200,1.5,0.8),HighShelfFilter(2500,-5.0,0.6),HighShelfFilter(7000,-1.5,0.7),Compressor(-22,4,5,80)); v1=deess(v1,5000,80,0.75,10); v1=pb(v1,Compressor(-16,2,15,150))
h1=ride(h1); h1=pb(h1,HighpassFilter(100),PeakFilter(350,-1.5,1.0),HighShelfFilter(3000,-2.5,0.6),Compressor(-24,3.5,6,90)); h1=deess(h1,5500,92,0.5,6); h1=pb(h1,Compressor(-16,2,15,150))
v2=pb(v2,HighpassFilter(160),PeakFilter(350,-2,1.0),HighShelfFilter(3500,5.0,0.7),Compressor(-34,4,5,100)); v2=width(v2,1.5)
h2=pb(h2,HighpassFilter(160),PeakFilter(350,-2,1.0),HighShelfFilter(5000,4.0,0.7),Compressor(-40,4,5,100)); h2=width(h2,1.4)
ad=pb(ad,HighpassFilter(200),Compressor(-38,3,5,100))
bands(v1,"verse"); bands(h1,"hook")
# level: match leads, set backgrounds relative
lv=lufs(v1); lh=lufs(h1); h1*=10**((lv-lh)/20); print(f"   lead LUFS verse {lv:.1f} hook {lh:.1f} -> matched")
for x,off,n in [(v2,-9.0,"bgv"),(h2,-8.0,"harm"),(ad,-9.0,"adlib")]:
    g=lv+off-lufs(x); x*=10**(g/20); print(f"   {n} gain {g:+.1f} dB")
lead=v1+h1
# sends
BPM=80.75; e8=60/BPM/2
def rev(x,size,damp): 
    pre=np.pad(x,((int(0.03*SR),0),(0,0)))[:len(x)]
    return pb(pre,HighpassFilter(350),LowpassFilter(6500),Reverb(room_size=size,damping=damp,wet_level=1.0,dry_level=0.0,width=1.0))
def dly(x,time,fb=0.3):
    w=pb(x,HighpassFilter(450),LowpassFilter(3800),Delay(delay_seconds=time,feedback=fb,mix=1.0))
    w2=np.pad(w,((int(time*SR),0),(0,0)))[:len(w)]  # ping-pong feel
    return np.stack([w[:,0]*0.9+w2[:,0]*0.25,w[:,1]*0.35+w2[:,1]*0.8],1)
db=lambda d:10**(d/20)
fxsend=v1*db(0)+h1*db(-7)+v2*db(-4)+h2*db(-6)+ad*db(2)
plate=rev(fxsend,0.5,0.6)*db(-17)
echo=dly(v1*db(0)+h1*db(-8)+ad*db(4),e8)*db(-21)
# duck FX under the dry lead so it only blooms in gaps
le=env(lead,60); duck=1-0.45*np.clip((20*np.log10(le+1e-9)+45)/20,0,1); echo*=duck[:,None]; plate*=(1-0.25*(1-duck)/0.45)[:,None] if False else 1
vbus=lead+v2+h2+ad+plate+echo
vbus=pb(vbus,Compressor(-14,1.5,20,200))
# ---------- beat
print("beat")
dr=pb(dr,HighpassFilter(30),LowShelfFilter(75,1.5,0.7),PeakFilter(380,-1.5,1.0),HighShelfFilter(9000,1.5,0.7))
drc=pb(dr,Compressor(-28,6,25,90)); dr=dr*0.85+drc*0.35   # parallel punch
bm=ba.mean(1); bs=zp((ba[:,0]-ba[:,1])/2,bt(2,180,'hp'))*0.7; ba=np.stack([bm+bs,bm-bs],1)
ba=pb(ba,HighpassFilter(28),PeakFilter(250,-1.5,1.0),Compressor(-22,3,25,160)); ba=np.tanh(ba*1.6)/1.6*1.05*10**(2/20)
kick=env(zp(dr.mean(1),bt(4,110,'lp')),12); kd=1-0.22*np.clip(kick/np.percentile(kick,99.5),0,1); ba*=kd[:,None]
ot=pb(ot,HighpassFilter(110),PeakFilter(300,-1.5,1.0),HighShelfFilter(7000,1.5,0.7)); ot=width(ot,1.15,150)
# carve vocal pocket in Others (1.5-5k), keyed by lead
band=zp(ot,bt(2,[1500,5000],'bp')); g=1-0.30*np.clip((20*np.log10(le+1e-9)+45)/18,0,1); ot=ot-band*(1-g)[:,None]
beat=dr+ba+ot
# ---------- balance
both=(env(lead,400)>10**(-40/20))
mb=lambda x: 20*np.log10(np.sqrt((zp(x,bt(2,[300,3000],'bp'))[both]**2).mean()))
rawlead=load("VoiceAudio")+load("VoiceAudio_Copy"); rawbeat=load("Drums")+load("Bass")+load("Others")
print(f"   artist's rough balance (lead-beat, 300-3k): {mb(rawlead)-mb(rawbeat):+.1f} dB; LUFS diff {lufs(rawlead,both)-lufs(rawbeat,both):+.1f}")
VOX=float(sys.argv[4]); vg=mb(beat)+VOX-mb(lead); print(f"   vocal bus gain {vg:+.1f} dB -> lead-beat LUFS {lufs(lead,both)+vg-lufs(beat,both):+.1f}")
mix=beat+vbus*db(vg)
bands(mix,"premaster")
sf.write(W+"/premaster.wav",mix*db(-6),SR,subtype="FLOAT"); sf.write(W+"/acapella.wav",vbus*db(vg-6),SR,subtype="FLOAT"); sf.write(W+"/beat.wav",beat*db(-6),SR,subtype="FLOAT")
