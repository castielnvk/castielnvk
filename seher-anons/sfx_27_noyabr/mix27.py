# Real CC0 SFX (freesound.org) placed on the 27 Nov clip's events, replacing synth gag sounds.
import numpy as np, soundfile as sf, librosa, json
SR=48000; D=14.125; N=int(D*SR)+SR; out=np.zeros((N,2))
def ld(f,a=0,d=None,fi=.004,fo=.03):
    y,_=librosa.load(f,sr=SR,mono=True,offset=a,duration=d); n=len(y)
    e=np.ones(n); k=int(fi*SR); e[:k]=np.linspace(0,1,k); k2=min(n,int(fo*SR)); e[n-k2:]*=np.linspace(1,0,k2)
    y=y*e; return y/ (np.abs(y).max()+1e-9)
def put(y,t,g,pan=0):
    i=int(t*SR); y=y[:max(0,N-i)]; out[i:i+len(y),0]+=y*g*np.cos((pan+1)*np.pi/4); out[i:i+len(y),1]+=y*g*np.sin((pan+1)*np.pi/4)
F='sfxsrc/'
whoosh=ld(F+'throw_whoosh/684459.mp3',.55,.6); swoosh=ld(F+'throw_whoosh/419341.mp3')
up=ld(F+'slide_whistle_up/517633.mp3',1.55,.95,fo=.08)      # rising tail of whistle 1
down=ld(F+'slide_whistle_up/517633.mp3',3.6,.72,fo=.06)     # falling whistle 2
splat=ld(F+'splat/719131.mp3'); splat2=ld(F+'splat/248255.mp3',1.38,.5); squish=ld(F+'squish_wet/515621.mp3')
pan1=ld(F+'pan_drop/267486.mp3'); pan2=ld(F+'pan_drop/267485.mp3')
rattle=ld(F+'pot_lid_drop/737401.mp3',0.0,1.15,fo=.25); rattle2=ld(F+'pot_lid_drop/737401.mp3',3.1,1.4,fo=.3)
gasp=ld(F+'crowd_gasp/264376.mp3',0,1.6,fo=.4); gasp2=ld(F+'crowd_gasp/763876.mp3',0,1.8,fo=.4)
wah=ld(F+'sad_trombone/175409.mp3',0.2,4.6,fo=.6)
L=121/24
for k,(pv,rt,gs,sp) in enumerate([(pan1,rattle,gasp,splat2),(pan2,rattle2,gasp2,squish),(pan1,rattle,None,splat2)]):
    o=k*L
    put(whoosh if k!=1 else swoosh, o+0.0, 2.6, -.2)       # tray flick / cake launch
    put(up, o+0.08, .16, .1)                               # cake rising
    put(down, o+0.55, .16, .15)                             # cake falling (cut by splat)
    put(splat, o+1.22, 2.0, .1); put(sp, o+1.25, 1.4, .1)   # cake on head
    if gs is not None: put(gs, o+1.4, .33, 0)
    put(pv, o+2.2, .6, -.35); put(rt, o+2.28, 1.05, -.35)  # tray hits floor + rattles
# wah-wah only on the last loop, after the last splat, under the end badge
put(wah, 2*L+2.7, .62, 0)
# duck the falling whistle where splat hits (fade 40ms before splat)
out=out[:int(D*SR)]
out/=max(1,np.abs(out).max()/.9); sf.write('aud/realsfx.wav',out,SR)
print('ok')
