import subprocess,json,os
from segs import *
tl,T=timeline(); print("total",round(T,2))
json.dump(tl,open('timeline.json','w'),indent=1)
SRC='../src/proxy709b.mov'; os.makedirs('parts',exist_ok=True)
GRADE="eq=saturation=0.72:contrast=0.98,colorbalance=rm=-0.025:gm=0.005:bm=0.01,unsharp=5:5:0.25"
lst=[];alst=[]
for i,s in enumerate(tl):
  v=f"parts/{i:02d}.mp4"; a=f"parts/{i:02d}.wav"
  if s["freeze"]:
    n=round(s["odur"]*FPS)
    subprocess.run(f'ffmpeg -loglevel error -y -ss {s["src"]:.3f} -i {SRC} -frames:v 1 -vf "{GRADE}" parts/fr{i}.png',shell=True,check=True)
    subprocess.run(f'ffmpeg -loglevel error -y -loop 1 -framerate 30 -i parts/fr{i}.png -frames:v {n} -c:v libx264 -crf 14 -preset medium -pix_fmt yuv420p -colorspace bt709 -color_trc bt709 -color_primaries bt709 -r 30 {v}',shell=True,check=True)
    subprocess.run(f'ffmpeg -loglevel error -y -f lavfi -i anullsrc=r=48000:cl=mono -t {s["odur"]:.4f} -c:a pcm_s16le {a}',shell=True,check=True)
  else:
    d=s["src_out"]-s["src_in"]; n=round(d*FPS)
    subprocess.run(f'ffmpeg -loglevel error -y -ss {s["src_in"]:.3f} -i {SRC} -t {d:.4f} -map 0:v -vf "{GRADE}" -frames:v {n} -c:v libx264 -crf 14 -preset medium -pix_fmt yuv420p -colorspace bt709 -color_trc bt709 -color_primaries bt709 -r 30 {v}',shell=True,check=True)
    subprocess.run(f'ffmpeg -loglevel error -y -ss {s["src_in"]:.3f} -i {SRC} -t {d:.4f} -map 0:a -ac 1 -af "afade=t=in:d=0.015,afade=t=out:st={d-0.02:.4f}:d=0.02" -ar 48000 -c:a pcm_s16le {a}',shell=True,check=True)
  lst.append(f"file '{v}'"); alst.append(f"file '{a}'")
open('v.txt','w').write("\n".join(lst)); open('a.txt','w').write("\n".join(alst))
subprocess.run('ffmpeg -loglevel error -y -f concat -safe 0 -i v.txt -c copy base.mp4',shell=True,check=True)
subprocess.run('ffmpeg -loglevel error -y -f concat -safe 0 -i a.txt -c:a pcm_s16le dialog_raw.wav',shell=True,check=True)
