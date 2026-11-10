import sys,numpy as np,soundfile as sf,pyloudnorm as pyln,subprocess
from scipy import signal
from pedalboard import Pedalboard,HighpassFilter,LowShelfFilter,PeakFilter,HighShelfFilter,Compressor
W=sys.argv[1]; TARGET=float(sys.argv[2]); x,sr=sf.read(W+"/premaster.wav")
y=Pedalboard([HighpassFilter(25),Compressor(-18,1.5,30,250)])(x.astype(np.float32).T,sr).T.astype(np.float64)
g=TARGET-pyln.Meter(sr).integrated_loudness(y)
for i in range(5):
    z=y*10**(g/20); z=np.where(abs(z)>0.7,np.sign(z)*(0.7+0.3*np.tanh((abs(z)-0.7)/0.3)),z)  # soft clip the tallest drum peaks
    sf.write(W+"/pre.wav",z,sr,subtype="FLOAT")
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",W+"/pre.wav","-af","aresample=176400:resampler=soxr,alimiter=limit=0.87:attack=4:release=60:level=false:asc=1,aresample=44100:resampler=soxr","-c:a","pcm_f32le",W+"/lim.wav"],check=True)
    z,_=sf.read(W+"/lim.wav"); l=pyln.Meter(sr).integrated_loudness(z); print("pass",i,"gain",round(g,2),"LUFS",round(l,2))
    if abs(l-TARGET)<0.1: break
    g+=TARGET-l
e=np.sqrt(signal.sosfiltfilt(signal.butter(2,5,'lp',fs=sr,output='sos'),(z**2).mean(1)).clip(1e-14)); last=np.where(e>10**(-55/20))[0][-1]; end=min(len(z),last+int(0.5*sr)); z=z[:end]
m=int(1.5*sr); z[-m:]*=np.linspace(1,0,m)[:,None]**2; n=int(0.01*sr); z[:n]*=np.linspace(0,1,n)[:,None]
sf.write(W+"/master.wav",z,sr,subtype="PCM_24")
f,P=signal.welch(z.mean(1),sr,nperseg=8192); ed=[30,60,120,250,500,1000,2000,4000,8000,12000,16000]; print("bands",[int(round(10*np.log10(P[(f>=a)&(f<b)].sum()+1e-20))) for a,b in zip(ed,ed[1:])])
rms=np.sqrt((z**2).mean()); print("dur",round(len(z)/sr,1),"crest",round(20*np.log10(abs(z).max()/rms),1),"corr",round(np.corrcoef(z[:,0],z[:,1])[0,1],2),"mono-sum loss LU",round(pyln.Meter(sr).integrated_loudness(z)-pyln.Meter(sr).integrated_loudness(np.repeat(z.mean(1)[:,None],2,1)),1))
