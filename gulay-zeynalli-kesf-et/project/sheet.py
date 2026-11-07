import sys,glob
from PIL import Image
fs=sorted(glob.glob(sys.argv[1]+'/*.png'));ims=[Image.open(f).resize((270,480)) for f in fs]
S=Image.new('RGB',(270*6,480*((len(ims)+5)//6)),'white')
for k,i in enumerate(ims):S.paste(i,((k%6)*270,(k//6)*480))
S.save(sys.argv[2])
