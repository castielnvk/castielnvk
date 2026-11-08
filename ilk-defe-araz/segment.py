#!/usr/bin/env python3
"""Person masks (BiRefNet_lite, MIT) for the given frames -> <frames>/<clip>_m/NNNN.png (alpha = person).
usage: python3 -I segment.py <frames_dir> '[["ai1", 12], ["ai1", 13], ...]'   (needs HF_HUB_DISABLE_XET=1)"""
import json, os, sys, time
import numpy as np, torch
from PIL import Image
from transformers import AutoModelForImageSegmentation
from torchvision import transforms

B = sys.argv[1]; need = json.loads(sys.argv[2])
m = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet_lite", trust_remote_code=True).eval()
torch.set_num_threads(os.cpu_count() or 4)
tf = transforms.Compose([transforms.Resize((768, 576)), transforms.ToTensor(),
                         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
t0 = time.time()
for i, (c, n) in enumerate(need):
    od = f"{B}/{c}_m"; os.makedirs(od, exist_ok=True); out = f"{od}/{n:04d}.png"
    if os.path.exists(out): continue
    im = Image.open(f"{B}/{c}/{n:04d}.jpg").convert("RGB")
    with torch.no_grad(): p = m(tf(im).unsqueeze(0))[-1].sigmoid()[0, 0].numpy()
    a = Image.fromarray((p * 255).astype(np.uint8)).resize(im.size, Image.BILINEAR)
    rgba = Image.new("RGBA", im.size, (255, 255, 255, 0)); rgba.putalpha(a); rgba.save(out)
    if i % 20 == 0: print(f"{i}/{len(need)} {time.time() - t0:.0f}s", flush=True)
print("masks done")
