import json, os, sys, time, onnxruntime as ort
from rembg import new_session, remove
from PIL import Image, ImageFilter, ImageEnhance
o=ort.SessionOptions(); o.enable_cpu_mem_arena=False; o.enable_mem_pattern=False
o.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_BASIC; o.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
S=new_session('birefnet-portrait', sess_opts=o)
def frame(src,pick):
    p=open(f'jobs/{src}/picks.txt').read().split()[pick-1]
    return Image.open(f'jobs/{src}/frames/'+os.path.basename(p)).convert('RGB')
def cut(img, scale):
    if scale!=1: img=img.resize((int(img.width*scale),int(img.height*scale)),Image.LANCZOS)
    im=remove(img,session=S); r,g,b,a=im.split()
    a=a.point(lambda v: 0 if v<40 else min(255,int((v-40)*255/200)))
    rgb=Image.merge('RGB',(r,g,b))
    up=max(1.0,1700/rgb.height)
    if up>1.01: rgb=rgb.resize((int(rgb.width*up),int(rgb.height*up)),Image.LANCZOS); a=a.resize(rgb.size,Image.LANCZOS)
    a=a.filter(ImageFilter.GaussianBlur(0.8))
    rgb=rgb.filter(ImageFilter.UnsharpMask(radius=2.2,percent=70,threshold=2)); rgb=ImageEnhance.Contrast(rgb).enhance(1.08)
    out=rgb.convert('RGBA'); out.putalpha(a); bb=out.getbbox(); return out.crop(bb) if bb else out
jobs=json.load(open('pipeline/jobs.json'))
only=set(sys.argv[1:])
for j in jobs:
    dst=f"cover/subjects/{j['id']}.png"
    if (only and j['id'] not in only) or (not only and os.path.exists(dst)): continue
    t=time.time()
    try:
        if 'pair' in j:
            A=cut(frame(j['src'],j['pair'][0]),1); B=cut(frame(j['src'],j['pair'][1]),1)
            H=max(A.height,B.height); A=A.resize((int(A.width*H/A.height),H)); B=B.resize((int(B.width*H/B.height),H))
            ov=int(min(A.width,B.width)*0.22); W=A.width+B.width-ov
            out=Image.new('RGBA',(W,H)); out.alpha_composite(B,(A.width-ov,0)); out.alpha_composite(A,(0,0)); out.save(dst)
        else:
            img=frame(j['src'],j['pick'])
            if 'crop' in j:
                x0,y0,x1,y1=j['crop']; w,h=img.size; img=img.crop((int(x0*w),int(y0*h),int(x1*w),int(y1*h))); cut(img,2.5).save(dst)
            else: cut(img,1).save(dst)
        print(j['n'],j['id'],'ok',round(time.time()-t),'s',flush=True)
    except Exception as e: print(j['n'],j['id'],'ERR',e,flush=True)
