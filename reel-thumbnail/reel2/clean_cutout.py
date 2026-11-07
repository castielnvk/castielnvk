# Videokadrın fon kəsiminin əl ilə düzəlişi: stulu silir, sağ qulaqlıq yastığını bərpa edir.
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, sys
p = sys.argv[1]
im = Image.open(p); a = np.array(im).astype(float)
def poly(pts, blur):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m.filter(ImageFilter.GaussianBlur(blur))).astype(float) / 255
chair = poly([(0,380),(350,380),(350,862),(305,880),(240,905),(198,962),(184,1022),(0,1062)], 2)
a[:,:,3] *= (1 - chair); a[:380,:,3] = 0
reg = a[:1150,:420,3]; reg[reg < 170] = 0
pad = poly([(848,705),(868,686),(885,676),(898,680),(906,690),(908,760),(905,830),(895,866),(880,876),(850,880),(805,884),(800,860),(825,790)], 1.2)
a[:,:,3] = np.maximum(a[:,:,3], pad * 255)
Image.fromarray(a.astype(np.uint8)).save(p)
