import json,sys,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
wf=wave.open(sys.argv[1]);aud=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(np.float32)/32768
P="Radio səhər şousu. Telefonla Nihat bəy zəng edib. Qrip olmuram, əməliyyata gedirəm. Babasil əməliyyatı. Allah köməyin olsun. Qardaş, çox gülmə, əməliyyat qabağıdır. LOR həkimi, burun, nəfəs almaq. Komedixana. Azercell, Bakcell. Nənəsil."
out=[]
for a,b in [(0,27),(27,57),(56,93),(92,121),(120,145.2)]:
    segs,_=m.transcribe(aud[int(a*16000):int(b*16000)],language="az",word_timestamps=True,beam_size=5,initial_prompt=P,condition_on_previous_text=False)
    for s in segs:
        out.append({"s":s.start+a,"e":s.end+a,"t":s.text,"w":[(w.start+a,w.end+a,w.word) for w in s.words]})
        print(f"{s.start+a:7.2f}-{s.end+a:7.2f} {s.text}",flush=True)
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False)
