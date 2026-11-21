import re,sys,html,subprocess,os,urllib.parse
q=sys.argv[1]; n=int(sys.argv[2]) if len(sys.argv)>2 else 6; out=sys.argv[3]
url=f"https://freesound.org/search/?q={urllib.parse.quote_plus(q)}&f=license%3A%22Creative+Commons+0%22&s=Downloads+desc"
t=subprocess.run(['curl','-s','-m','30',url],capture_output=True,text=True).stdout
ids=re.findall(r'data-sound-id="(\d+)".{0,800}?data-mp3="([^"]+)"',t,re.S)
ttl=[html.unescape(x) for x in re.findall(r'class="bw-link--black"[^>]*title="([^"]+)"',t)]
os.makedirs(out,exist_ok=True)
for i,((sid,mp3),tt) in enumerate(zip(ids,ttl)):
    if i>=n: break
    f=f"{out}/{sid}.mp3"; subprocess.run(['curl','-s','-m','40','-o',f,mp3.replace('-lq.mp3','-hq.mp3')])
    d=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout.strip()
    print(sid,d,tt)
