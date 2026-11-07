import sys,os
sys.argv=['x']
import compose as C
from engine import *
from PIL import Image
ts=[float(x) for x in os.environ['TS'].split(',')]
ims=[]
for ot in ts:
    ci,st=C.o2s(ot); c=C.clips[ci]
    r=Reader(c['at'] if 'hold' in c else st, (c['at'] if 'hold' in c else st)+0.1); p=r.next(); r.close()
    f=C.render_frame(int(round(ot*FPS)),p)
    ims.append(Image.fromarray(f).resize((540,960)))
sheet=Image.new('RGB',(540*len(ims),960))
for i,im in enumerate(ims): sheet.paste(im,(540*i,0))
sheet.save(os.environ.get('OUTP','../w/stills.jpg'),quality=88)
