"""Word timings for the ElevenLabs voice-over: python3 tools/transcribe.py "<names, dates, rare words>"
Writes words.json and prints `start end word`. Whisper starts sentences ~0.3-0.6 s early after a pause:
use tools/pauses.py and take the pause END as the onset of the next word."""
import os, sys, json, subprocess, numpy as np
os.environ["HF_HUB_DISABLE_XET"] = "1"
from faster_whisper import WhisperModel
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "src/vo.mp3", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.float32)
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="az", word_timestamps=True, vad_filter=False, initial_prompt=(sys.argv[1] if len(sys.argv) > 1 else None))
out = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words]
json.dump(out, open("words.json", "w"), ensure_ascii=False)
for w in out: print(*w)
