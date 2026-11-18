# Reel 3 fon kəsiminin əl ilə düzəlişi: soldakı stul izini silir, mikrofon borusunu bərkidir.
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, sys
p = sys.argv[1]
im = Image.open(p); a = np.array(im).astype(float)
def poly(pts, blur):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m.filter(ImageFilter.GaussianBlur(blur))).astype(float) / 255
a[:,:,3] *= 1 - poly([(0,600),(300,600),(300,970),(200,1000),(60,1110),(0,1190)], 2)
tube = poly([(948,994),(1080,1020),(1080,1132),(948,1142)], 1.2)
a[:,:,3] = np.maximum(a[:,:,3], tube * 255)
# borunun yuxarısındakı / aşağısındakı divar zolağını sil
a[:,:,3] *= 1 - poly([(960,900),(1080,900),(1080,1018),(960,990)], 1.5)
a[:,:,3] *= 1 - poly([(960,1150),(1080,1140),(1080,1200),(960,1200)], 1.5) * (np.array(im)[:,:,:3].mean(2) > 170)
Image.fromarray(a.astype(np.uint8)).save(p)
