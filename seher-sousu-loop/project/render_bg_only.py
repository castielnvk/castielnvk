# Same v2 animation as render.py, without logos and texts.
import sys, os, numpy as np
from PIL import Image
import render as R
def frame(i):
    t=i/R.FPS
    bg=R.background(t)+R.grain[i%6]
    fr=Image.fromarray(np.clip(bg,0,255).astype(np.uint8)).convert('RGBA')
    fr.alpha_composite(R.sunburst(t))
    fr.alpha_composite(R.particles(t))
    fr.alpha_composite(R.deco_layer(t))
    return fr.convert('RGB')
if __name__=='__main__':
    a,b,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]; os.makedirs(out,exist_ok=True)
    for i in range(a,b): frame(i).save(f'{out}/{i:04d}.png',compress_level=1)
