"""Cut out a guest from a frame with BiRefNet-portrait (low-memory ONNX settings), clean and upscale it.
usage: python prep_subject.py frame.png out.png"""
import sys, onnxruntime as ort
from rembg import new_session, remove
from PIL import Image, ImageFilter, ImageEnhance
o=ort.SessionOptions()
o.enable_cpu_mem_arena=False          # default arena keeps every buffer -> >16 GB, OOM
o.enable_mem_pattern=False
o.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_BASIC  # avoid extra weight copies
o.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
s=new_session('birefnet-portrait', sess_opts=o)
im=remove(Image.open(sys.argv[1]).convert('RGB'),session=s)
r,g,b,a=im.split()
a=a.point(lambda v: 0 if v<40 else min(255,int((v-40)*255/200)))
rgb=Image.merge('RGB',(r,g,b)); W,H=rgb.size
rgb=rgb.resize((int(W*1.6),int(H*1.6)),Image.LANCZOS)
a=a.resize(rgb.size,Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
rgb=rgb.filter(ImageFilter.UnsharpMask(radius=2.2,percent=70,threshold=2))
rgb=ImageEnhance.Contrast(rgb).enhance(1.08)
out=rgb.convert('RGBA'); out.putalpha(a); out=out.crop(out.getbbox()); out.save(sys.argv[2]); print(out.size)
