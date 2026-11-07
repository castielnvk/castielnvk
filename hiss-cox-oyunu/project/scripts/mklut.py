"""HLG (BT.2100) -> SDR BT.709 3D LUT, following the BT.2408 display-light approach:
inverse OETF -> OOTF (Lw=1000, gamma 1.2) -> BT.2020->BT.709 -> exposure (ref white) ->
hue-preserving highlight roll-off on maxRGB -> BT.1886 inverse EOTF. No creative grade."""
import numpy as np, sys
N=65; EXPO=float(sys.argv[1]); SAT=float(sys.argv[2]); KNEE=float(sys.argv[3]); TAG='_'.join(sys.argv[1:])
a,b,c=0.17883277,0.28466892,0.55991073
g=np.linspace(0,1,N); B,G,R=np.meshgrid(g,g,g,indexing='ij')  # cube order: R fastest
E=np.stack([R,G,B],-1)
lin=np.where(E<=0.5,E**2/3,(np.exp((E-c)/a)+b)/12)
Ys=lin@np.array([0.2627,0.6780,0.0593])
GM=float(sys.argv[4]) if len(sys.argv)>4 else 1.2
Fd=1000*np.power(np.maximum(Ys,1e-9),GM-1)[...,None]*lin          # display nits
M=np.array([[1.6605,-0.5876,-0.0728],[-0.1246,1.1329,-0.0083],[-0.0182,-0.1006,1.1187]])
x=(Fd@M.T)/203*EXPO                                               # ref white (203 nits) -> 1.0*EXPO
Y709=(x@np.array([0.2126,0.7152,0.0722]))[...,None]
x=Y709+SAT*(x-Y709)
x=np.maximum(x,0)
mx=x.max(-1,keepdims=True)
# soft knee: identity below KNEE, smooth compression to 1.0 above
k=KNEE; TOP=0.93; over=np.maximum(mx-k,0); comp=k+(TOP-k)*(1-np.exp(-over/(TOP-k)))
y=np.where(mx>k,x*comp/np.maximum(mx,1e-9),x)
y=np.clip(y,0,1)**(1/2.4)
with open(f'hlg2sdr_{TAG}.cube','w') as f:
  f.write(f'TITLE "HLG to SDR BT709"\nLUT_3D_SIZE {N}\n')
  for v in y.reshape(-1,3): f.write(f'{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
