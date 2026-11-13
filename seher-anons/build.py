#!/usr/bin/env python3
"""Build one 'Sabahın mövzusu' announcement. Usage: build.py config.json
config: {name, video, date, l1, l2, big, music, music_from (s, approx), st:[[word,colour,time,x,y,sound]], bq (beat period hint, optional)}"""
import json,sys,os,subprocess as sp,shutil,warnings,numpy as np,librosa,soundfile as sf
from scipy.signal import butter,sosfilt,sosfiltfilt
warnings.filterwarnings('ignore')
cfg=json.load(open(sys.argv[1])); D=14.125; SR=48000
run=lambda c:sp.run(c,shell=True,check=True)
# 1. footage frames
shutil.rmtree('fr/N',ignore_errors=True); os.makedirs('fr/N')
run(f"ffmpeg -v error -y -i '{cfg['video']}' -map 0:v:0 -vf 'fps=24,scale=-2:1920:flags=lanczos,crop=1080:1920' -q:v 2 fr/N/%04d.jpg")
n=len(os.listdir('fr/N'))
# 2. beat grid of the music from onset strength
y,sr=librosa.load(cfg['music'],sr=22050,mono=True,offset=max(0,cfg.get('music_from',0)-1),duration=20); o0=max(0,cfg.get('music_from',0)-1)
H=64; oe=librosa.onset.onset_strength(y=y,sr=sr,hop_length=H); tt=o0+librosa.frames_to_time(np.arange(len(oe)),sr=sr,hop_length=H)
tempo=float(np.atleast_1d(librosa.beat.beat_track(y=y,sr=sr)[0])[0]); B0=cfg.get('bq') or 60/tempo
best=None
for B in np.arange(B0*.97,B0*1.03,B0*.0008):
    for ph in np.arange(0,B,.004):
        g=np.arange(o0+ph,o0+19,B); s=np.interp(g,tt,oe).mean()
        if best is None or s>best[0]: best=(s,B,ph)
_,B,ph=best; g=np.arange(o0+ph,o0+19,B); acc=np.interp(g,tt,oe)
i0=next(i for i in range(len(g)) if g[i]>=cfg.get('music_from',0)-.05 and acc[i]>.6*acc.max())
t0=g[i0]-.015; print('beat',round(B,4),'bpm',round(60/B,1),'music start',round(t0,3),'accents',np.round(acc[i0:i0+12],1))
beat=lambda t:round(t/B)*B
tg={'m':.55,'tag':1.1,'c1':2.45,'c2':3.0,'c3':3.55,'ft':4.15,'w1':6.0,'w2':10.9,'bd':12.5,'end':13.1}; ev={}; last=0
for k,v in tg.items():
    b=beat(v)
    if k in('m','tag','c1','c2','c3','ft','end') and b<=last+.2: b=last+B*max(1,round(.45/B))
    ev[k]=float(b); last=b if k not in('w1','w2') else last
if cfg.get('gap') and cfg['gap'][1] is None: cfg['gap'][1]=ev['bd']-.3
cfg.update(B=float(B),ev=ev,n=n); json.dump(cfg,open('cfg_run.json','w'),ensure_ascii=False); print(ev)
# 3. sfx
rng=np.random.default_rng(3); N=int((D+.1)*SR); out=np.zeros((N,2))
lp=lambda x,f:sosfilt(butter(2,f,'low',fs=SR,output='sos'),x); bp=lambda x,lo,hi:sosfilt(butter(2,[lo,hi],'band',fs=SR,output='sos'),x)
def put(x,t,g=1,pan=0):
    i=int(max(0,t)*SR); x=x[:max(0,N-i)]; out[i:i+len(x),0]+=x*g*np.cos((pan+1)*np.pi/4); out[i:i+len(x),1]+=x*g*np.sin((pan+1)*np.pi/4)
def whoosh(d=.35,f0=500,f1=2600,peak=.6):
    n=int(d*SR); nz=rng.standard_normal(n); t=np.arange(n)/n; yv=np.zeros(n); K=1024
    for i in range(0,n,K):
        fc=f0*(f1/f0)**(i/n); f=bp(nz[max(0,i-2048):i+K],fc*.6,min(fc*1.6,9000)); m=min(K,n-i); yv[i:i+m]=f[-m:]
    env=np.where(t<=peak,np.sin(np.pi*np.clip(t/(2*peak),0,.5))**2,np.cos(np.pi/2*np.clip((t-peak)/(1-peak),0,1))**2); return lp(yv*env,6000)*.9
def thump(f0=110,f1=42,d=.32,click=.5):
    n=int(d*SR); t=np.arange(n)/SR; f=f1+(f0-f1)*np.exp(-t*28); yv=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*13); c=lp(rng.standard_normal(576),3500)*np.linspace(1,0,576)**2; yv[:576]+=c*click; return yv
def pop(f0=260,f1=620,d=.09):
    n=int(d*SR); t=np.arange(n)/SR; f=f0+(f1-f0)*(t/d)**.6; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*38)*np.minimum(1,t/.003)+lp(rng.standard_normal(n),2500)*np.exp(-t*90)*.25
def tick(fc=1800,d=.03):
    n=int(d*SR); t=np.arange(n)/SR; return bp(rng.standard_normal(n),fc*.7,fc*1.4)*np.exp(-t*160)
def stamp():
    n=int(.12*SR); t=np.arange(n)/SR; return lp(rng.standard_normal(n),1800)*np.exp(-t*45)*1.2+thump(150,70,.12,.2)[:n]*.8
def wood(fc=820,d=.14):
    n=int(d*SR); t=np.arange(n)/SR; yv=np.sin(2*np.pi*fc*t)*np.exp(-t*42)+.5*np.sin(2*np.pi*fc*2.4*t)*np.exp(-t*70); c=tick(2200,.01); yv[:len(c)]+=c*.6; return yv
def whistle(f0=1500,f1=520,d=.36):
    n=int(d*SR); t=np.arange(n)/SR; f=f0*(f1/f0)**((t/d)**1.3)*(1+.012*np.sin(2*np.pi*11*t)); p=np.cumsum(f)/SR; yv=np.sin(2*np.pi*p)+.18*np.sin(4*np.pi*p)
    return lp((yv+bp(rng.standard_normal(n),1500,4000)*.12)*np.minimum(1,t/.03)*np.minimum(1,(d-t)/.05),4500)
def air(d=.9):
    n=int(d*SR); t=np.arange(n)/n; return bp(rng.standard_normal(n),2500,6500)*np.sin(np.pi*t)**2
def boing(d=.5,f=150):
    n=int(d*SR); t=np.arange(n)/SR; fm=f*(1+.35*np.sin(2*np.pi*9*t)*np.exp(-t*4)); p=np.cumsum(fm)/SR; return lp((np.sin(2*np.pi*p)+.4*np.sin(4*np.pi*p))*np.exp(-t*7)*np.minimum(1,t/.004),2200)
L=n/24; E=ev
put(whoosh(.38,400,2400,.7),0,.55,-.2); put(thump(120,45,.3),.02,.5)
for i in range(7): put(pop(240+i*38,520+i*60,.06),.08+i*.05,.16,-.5+i*.12)
put(thump(105,40,.34),E['m'],.75); put(stamp(),E['m'],.3); put(air(.9),.3,.10); put(stamp(),E['tag'],.55,-.4)
for w,c,t,x,yy,snd in cfg['st']:
    pan=(x+155-540)/700
    if snd=='bonk': put(whistle(),t-.38,.2,pan); put(wood(),t,.5,pan); put(boing(),t+.01,.33,pan); put(pop(),t,.3,pan)
    elif snd=='grump': put(boing(.55,95),t,.5,pan); put(thump(140,60,.2,.3),t,.45,pan); put(pop(200,150,.1),t,.3,pan)
    elif snd=='ask': put(whistle(520,1250,.3),t-.3,.2,pan); put(pop(300,760,.09),t,.4,pan); put(wood(980),t,.3,pan)
    elif snd=='cold':
        put(air(.5),t-.1,.35,pan); put(pop(520,900,.07),t,.3,pan)
        for k in range(6): put(tick(2600+150*(k%2),.02),t+.08+k*.055,.22,pan)
    elif snd=='hot':
        nn=int(.45*SR); tt_=np.arange(nn)/SR; put(bp(rng.standard_normal(nn),2500,6500)*np.exp(-tt_*7)*(1+.5*np.sin(2*np.pi*23*tt_)),t,.3,pan); put(pop(240,520,.1),t,.35,pan); put(thump(130,60,.2,.2),t,.4,pan)
    elif snd=='sneeze':
        put(whoosh(.22,3000,700,.2),t,.6,pan); put(thump(140,50,.25,.5),t+.02,.6,pan); put(boing(.45,180),t+.05,.3,pan)
    elif snd=='shh': put(air(.55),t-.05,.55,pan); put(pop(300,420,.06),t,.2,pan)
    elif snd=='cash':
        put(pop(280,700,.09),t,.35,pan); put(wood(900),t,.3,pan)
        for k in range(9): put(tick(1400+rng.integers(0,900),.035),t+.15+k*.07,.2,pan+rng.uniform(-.3,.3))
    elif snd=='crack':
        put(whistle(1300,420,.34),t-.36,.2,pan)
        for k in range(4): put(wood(1100+rng.integers(0,500),.07),t+k*.06,.45,pan)
        put(thump(130,45,.3,.6),t+.02,.6,pan)
    else: put(wood(700),t,.45,pan); put(pop(300,700),t,.3,pan)
put(whoosh(.3,700,3000,.6),E['c1']-.1,.4,-.4); [put(tick(1700+200*k),E['c1']+.12+k*.1,.22,-.3) for k in range(2)]
put(whoosh(.3,600,2800,.6),E['c2']-.1,.4,-.2); [put(tick(1900-150*k),E['c2']+.12+k*.1,.22,0) for k in range(2)]
put(thump(125,38,.42,.7),E['c3'],.95); put(pop(220,560,.11),E['c3'],.45); put(whoosh(.45,2600,500,.15),E['c3']+.02,.28)
put(tick(1500),E['ft'],.25,-.5); put(pop(300,520,.06),E['ft']+.02,.14,-.5)
for tl in np.arange(L,D-.3,L) if n<339 else []: put(whoosh(.42,450,2600,.5),tl-.2,.48,0)
for tw in (E['w1'],E['w2']):
    for i in range(7): put(pop(260+i*34,500+i*55,.05),tw+i*.045,.10,-.5+i*.12)
if cfg.get('gap'): put(whoosh(.35,2600,600,.3),cfg['gap'][0]-.05,.45,-.4); put(whoosh(.35,600,2600,.6),cfg['gap'][1]-.1,.45,-.4)
put(whoosh(.28,800,2800,.7),E['bd']-.12,.34,-.3); put(pop(240,640,.1),E['bd'],.42,-.3); put(stamp(),E['bd'],.3,-.3); put(thump(120,40,.45,.6),E['end'],.8)
out=sosfiltfilt(butter(2,30,'high',fs=SR,output='sos'),out,axis=0); out/=max(1,np.abs(out).max()/.9); os.makedirs('aud',exist_ok=True); sf.write('aud/sfx.wav',out,SR)
# 4. music cut + mix to -14 LUFS
def lufs(f): 
    r=sp.run(f"ffmpeg -hide_banner -i {f} -af ebur128 -f null -",shell=True,capture_output=True,text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])
run(f"ffmpeg -v error -y -ss {t0:.3f} -t {D} -i '{cfg['music']}' -af 'afade=t=in:d=0.008,afade=t=out:st={D-.75}:d=0.75' -ar 48000 aud/mus.wav")
if cfg.get('tapestop'):
    m,_=sf.read('aud/mus.wav'); ts=cfg['tapestop']; d=.75; i0=int(ts*SR); nn=int(d*SR); tau=np.arange(nn)/SR
    pos=i0+(tau-tau**2/(2*d))*SR; seg=np.stack([np.interp(pos,np.arange(len(m)),m[:,c]) for c in range(m.shape[1])],1)*(1-(tau/d)**3)[:,None]
    m[i0:i0+nn]=seg; m[i0+nn:]=0; sf.write('aud/mus.wav',m,SR)
mg=-17-lufs('aud/mus.wav')
run(f"ffmpeg -v error -y -i aud/mus.wav -i aud/sfx.wav -filter_complex '[0:a]volume={mg:.2f}dB[m];[1:a]volume=1.25[s];[m][s]amix=inputs=2:normalize=0[a]' -map '[a]' aud/mix_pre.wav")
run(f"ffmpeg -v error -y -i aud/mix_pre.wav -af 'volume={-14-lufs('aud/mix_pre.wav'):.2f}dB,alimiter=limit=0.84:level=false' aud/mix.wav"); print('final LUFS',lufs('aud/mix.wav'))
# 5. render + encode
if len(sys.argv)>2: os.environ['CFG']='cfg_run.json'; run(f"node render2.js 1 339 {sys.argv[2]}"); sys.exit()
shutil.rmtree('out/N1',ignore_errors=True); os.environ['CFG']='cfg_run.json'; run("node render2.js 1 339")
run(f"ffmpeg -v error -y -framerate 24 -i out/N1/%04d.jpg -i aud/mix.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 224k -shortest -movflags +faststart {cfg['name']}.mp4"); print('done',cfg['name'])
