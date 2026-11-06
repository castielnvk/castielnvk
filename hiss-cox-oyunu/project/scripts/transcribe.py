import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
import wave,numpy as np
wf=wave.open(sys.argv[1]);a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(np.float32)/32768
segs,info=m.transcribe(a,language="az",word_timestamps=True,beam_size=5,vad_filter=False,condition_on_previous_text=False,
  initial_prompt="Hiss. Aygün Kazımova, Ayaz Babayev, Safura Əlizadə, Roza Zərgərli, Röya, Nigar Camal, Samra, Promete, Natavan Həbibi, Zamiq, Elza Seyidcahan, Nuran. çox")
out=[]
for s in segs:
    out.append({"s":s.start,"e":s.end,"t":s.text,"w":[(w.start,w.end,w.word,round(w.probability,2)) for w in s.words]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text}",flush=True)
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
