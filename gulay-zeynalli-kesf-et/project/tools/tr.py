import sys,json
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device="cpu",compute_type="int8",cpu_threads=4)
import wave,numpy as np
w=wave.open(sys.argv[2]);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
a=a*min(20.0,0.5/np.abs(a).max())
segs,info=m.transcribe(a,language="az",word_timestamps=True,beam_size=5,vad_filter=False,condition_on_previous_text=False)
out=[]
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}",flush=True)
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[[w.start,w.end,w.word,w.probability] for w in s.words]})
json.dump(out,open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
