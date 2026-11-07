import sys,wave,numpy as np
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
w=wave.open(sys.argv[1]);A=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
for rng in sys.argv[2:]:
    s,e=map(float,rng.split('-'));a=A[int(s*16000):int(e*16000)];a=a*min(30.0,0.6/np.abs(a).max())
    for temp in (0.0,):
        segs,_=m.transcribe(a,language="az",word_timestamps=True,beam_size=5,vad_filter=False,condition_on_previous_text=False,no_speech_threshold=0.9,log_prob_threshold=-3,initial_prompt=None)
        print("==",rng)
        for sg in segs:
            print(f"  [{sg.start+s:6.2f}-{sg.end+s:6.2f}] {sg.text}")
            print("     "+" ".join(f"{w.word.strip()}@{w.start+s:.2f}" for w in sg.words))
