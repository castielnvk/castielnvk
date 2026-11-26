# Original outro sound: soft clock ticks while the hours run, one low bell at midnight.
import numpy as np, wave, os
SR=48000; DUR=5.5; t=np.arange(int(SR*DUR))/SR; a=np.zeros_like(t)
def env(t0,dec): x=t-t0; return np.where(x>=0,np.exp(-np.clip(x,0,None)/dec),0)
# ticks accelerate with the counting, then stop
times=[]; x=.25
while x<2.0: times.append(x); x+=0.16*(1-0.6*(x-.25)/1.75)
for i,t0 in enumerate(times):
    f=2400 if i%2 else 1900
    a+=0.10*np.sin(2*np.pi*f*t)*env(t0,.008)
    a+=0.05*np.random.default_rng(i).standard_normal(len(t))*env(t0,.003)
# bell at the midnight reset
for f,g,d in ((196,.30,1.9),(392,.16,1.4),(588,.07,1.0),(784,.05,.7),(1176,.02,.45)):
    a+=g*np.sin(2*np.pi*f*t)*env(2.05,d)
# soft rising pad under the wordmark
pad=np.where(t>3.3,np.clip((t-3.3)/.6,0,1),0)*np.clip((DUR-t)/.8,0,1)
for f,g in ((261.6,.05),(392,.035),(523.3,.02)): a+=g*pad*np.sin(2*np.pi*f*t)
a=np.tanh(a*1.2)*.8; a*=np.clip((DUR-t)/.25,0,1)
s=(np.stack([a,a],1)*32767).astype('<i2')
with wave.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_outro.wav'),'wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(s.tobytes())
