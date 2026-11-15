"""Preview stills: python3 tools/stills.py qc/a.jpg=0,2.5,6 qc/b.jpg=10,14 (times in seconds)."""
import sys; sys.path.insert(0, ".")
import sys, numpy as np, cv2
from PIL import Image
import render
from render import render as R, FPS
for spec in sys.argv[1:]:
    out, ts = spec.split('=')
    ims = [cv2.resize((np.clip(R(float(t), int(float(t) * FPS)),0,1) * 255).astype(np.uint8), (360, 640), interpolation=cv2.INTER_AREA) for t in ts.split(',')]
    Image.fromarray(np.hstack(ims)).save(out, quality=88)
