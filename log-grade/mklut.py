import numpy as np, sys
N=33; exp=float(sys.argv[2]) if len(sys.argv)>2 else 2.2
g=np.linspace(0,1,N); B,G,R=np.meshgrid(g,g,g,indexing='ij')  # cube order: R fastest
P=np.stack([R,G,B],-1).reshape(-1,3)
R0,Rt,c,b,gm,be=-0.05641088,0.01,47.28711236,0.00964052,0.08550479,0.69336945
Pt=c*(Rt-R0)**2
lin=np.where(P>=Pt,2**((P-be)/gm)-b,np.where(P>=0,np.sqrt(np.clip(P,0,None)/c)+R0,R0))
lin=np.clip(lin,0,None)
M=np.array([[1.6605,-0.5876,-0.0728],[-0.1246,1.1329,-0.0083],[-0.0182,-0.1006,1.1187]])
x=np.clip(lin@M.T,0,None)*exp
# saturation in linear, preserve highlights
Y=(x*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True)
x=Y+(x-Y)*0.92
# filmic (ACES fit)
def aces(v): return np.clip((v*(2.51*v+0.03))/(v*(2.43*v+0.59)+0.14),0,1)
y=aces(x)
d=y**(1/2.4)
L=(d*[0.2126,0.7152,0.0722]).sum(-1,keepdims=True)
sh=np.clip(1-L/0.45,0,1)**1.5; hi=np.clip((L-0.45)/0.55,0,1)**1.2
d=d+sh*np.array([-0.030,0.014,0.020])+hi*np.array([0.030,0.010,-0.032])
# gentle S contrast around 0.42
d=np.clip(d,0,1); d=d+0.10*np.sin((d-0.42)*np.pi)*d*(1-d)*2
# lift blacks slightly (filmic)
d=0.012+d*(0.985)
d=np.clip(d,0,1)
with open(sys.argv[1],'w') as f:
  f.write('TITLE "AppleLog_Cinematic"\nLUT_3D_SIZE %d\n'%N)
  for r in d: f.write('%.6f %.6f %.6f\n'%tuple(r))
