import os, sys, json, subprocess, numpy as np
os.environ["HF_HUB_DISABLE_XET"] = "1"
from faster_whisper import WhisperModel
f = sys.argv[1]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.float32)
# energy envelope, 50 ms
h = 800
env = [float(np.sqrt((a[i:i + h] ** 2).mean())) for i in range(0, len(a) - h, h)]
json.dump(env, open("env.json", "w"))
m = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "medium.en", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="en", word_timestamps=True, vad_filter=False,
                       initial_prompt="The evil it spread like a fever ahead. It was night when you died, my firefly. Tillamook burn. Fourth of July.")
out = []
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words:
        out.append((round(w.start, 2), round(w.end, 2), w.word))
        print(f"   {w.start:.2f} {w.end:.2f} {w.word}")
json.dump(out, open("words.json", "w"))
