"""Pauses (>=0.25 s below -36 dBFS) in src/vo.mp3 -> paste into common.PAUSES. python3 tools/pauses.py"""
import sys; sys.path.insert(0, '.')
from common import load_audio
import numpy as np
a = load_audio('src/vo.mp3', 16000, 1); n = 160
env = np.sqrt((a[:len(a) // n * n].reshape(-1, n) ** 2).mean(1)); sil = env < 10 ** (-36 / 20)
out, i = [], 0
while i < len(sil):
    if sil[i]:
        j = i
        while j < len(sil) and sil[j]: j += 1
        if j - i >= 25: out.append((round(i / 100, 2), round(j / 100, 2)))
        i = j
    else: i += 1
print('PAUSES =', out)
