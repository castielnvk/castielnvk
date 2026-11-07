import numpy as np, subprocess
from timeline import build
SR=48000
def load(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-af','pan=mono|c0=0.5*c0+0.5*c1','-f','f32le','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(r,np.float32)
v=load('stem_voice.wav'); m=load('stem_music.wav'); s=load('stem_sfx.wav')
items,T=build()
db=lambda x:20*np.log10(np.sqrt((x**2).mean())+1e-9)
for it in items:
    a,b=int(it['start']*SR),int(it['end']*SR)
    print(f"{it['kind']:7s}{it.get('n','')!s:2s} voice {db(v[a:b]):6.1f}  music {db(m[a:b]):6.1f}  sfx {db(s[a:b]):6.1f}")
