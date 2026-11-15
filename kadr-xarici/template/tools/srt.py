"""Write the SRT from common.CHUNKS (same timing as the burned-in subtitles). python3 tools/srt.py Name.srt"""
import sys; sys.path.insert(0, '.')
from common import CHUNKS, CHUNK_END, OFF
def ts(t):
    ms = int(round(t * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
out = []
for i, ch in enumerate(CHUNKS):
    a = ch[0][1] + OFF; b = CHUNK_END[i] + OFF + .12
    if i + 1 < len(CHUNKS): b = min(b, CHUNKS[i + 1][0][1] + OFF - .02)
    out.append(f"{len(out)+1}\n{ts(a)} --> {ts(b)}\n{' '.join(w for w, _, _ in ch)}\n")
open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(out))
