# CTC forced alignment of the supplied lyrics on the Demucs vocal stem (Turkish wav2vec2 XLS-R).
import json, re, sys, numpy as np, torch, librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
NAME = 'mpoyraz/wav2vec2-xls-r-300m-cv8-turkish'
proc = Wav2Vec2Processor.from_pretrained(NAME); model = Wav2Vec2ForCTC.from_pretrained(NAME).eval()
vocab = proc.tokenizer.get_vocab()
y, _ = librosa.load(sys.argv[1], sr=16000, mono=True)
D = json.load(open(sys.argv[2]))
lines = [l for l in D['lines']]

def norm(w):
    w = w.replace('İ', 'i').replace('I', 'ı').lower()
    return re.sub(r"[^a-zçöüğış]", '', w)

def emissions(a, b):
    seg = y[int(a * 16000):int(b * 16000)]
    inp = proc(seg, sampling_rate=16000, return_tensors='pt').input_values
    with torch.no_grad():
        lg = model(inp).logits[0]
    return torch.log_softmax(lg, -1).numpy()

def viterbi(em, tokens):
    T, S = em.shape[0], len(tokens)
    # states: blank, t0, blank, t1, ... (2S+1)
    ext = [0]
    for t in tokens: ext += [t, 0]
    N = len(ext)
    NEG = -1e9
    dp = np.full((T, N), NEG); bp = np.zeros((T, N), dtype=np.int32)
    dp[0, 0] = em[0, ext[0]]; dp[0, 1] = em[0, ext[1]]
    for t in range(1, T):
        for s in range(N):
            c = [(dp[t - 1, s], s)]
            if s >= 1: c.append((dp[t - 1, s - 1], s - 1))
            if s >= 2 and ext[s] != 0 and ext[s] != ext[s - 2]: c.append((dp[t - 1, s - 2], s - 2))
            v, k = max(c)
            dp[t, s] = v + em[t, ext[s]]; bp[t, s] = k
    s = N - 1 if dp[-1, N - 1] > dp[-1, N - 2] else N - 2
    path = []
    for t in range(T - 1, -1, -1):
        path.append((t, s)); s = bp[t, s]
    path.reverse()
    return ext, path

out = []
prev_end = 0
rmsv = librosa.feature.rms(y=y, frame_length=640, hop_length=160)[0]
rdb = 20 * np.log10(rmsv + 1e-6)
def refine_start(s, e, word):
    # first word of a line can absorb earlier sound: if there is a clear energy dip before the point
    # where the word can no longer fit its syllables, the word starts at the onset after that dip
    nv = max(1, sum(ch in 'aeıioöuü' for ch in word))
    lim = e - 0.16 * nv
    i0, i1 = int(s * 100), int(lim * 100)
    if i1 - i0 < 4: return s
    med = np.median(rdb[int(lim * 100):int(e * 100) + 1])
    low = np.where(rdb[i0:i1] < med - 10)[0]
    if len(low) == 0: return s
    j = i0 + low[-1]
    while j < int(e * 100) and rdb[j] < med - 6: j += 1
    return j / 100
for i, L in enumerate(lines):
    prev = lines[i - 1] if i else None
    nxt = lines[i + 1] if i + 1 < len(lines) else None
    a = max(L['t'] - 1.2, prev_end + 0.03)
    b = (nxt['t'] + 0.25) if nxt else L['words'][-1]['t'] + 2.0
    if L.get('end'): b = min(b, L['end'] + 0.3) if nxt else b
    b = max(b, L['words'][-1]['t'] + 0.9)
    words = [norm(w['text']) for w in L['words']]
    toks, owner = [], []
    for wi, w in enumerate(words):
        if wi: toks.append(vocab['|']); owner.append(-1)
        for ch in w: toks.append(vocab[ch]); owner.append(wi)
    em = emissions(a, b)
    fr = (b - a) / em.shape[0]
    ext, path = viterbi(em, toks)
    st = [None] * len(words); en = [None] * len(words)
    for t, s in path:
        if s % 2 == 1:
            o = owner[(s - 1) // 2]
            if o >= 0:
                if st[o] is None: st[o] = a + t * fr
                en[o] = a + (t + 1) * fr
    res = [{'text': L['words'][k]['text'], 'w': L['words'][k]['t'], 's': round(st[k], 3), 'e': round(en[k], 3)} for k in range(len(words))]
    for r in res[:1]:
        r['s'] = round(refine_start(r['s'], r['e'], norm(r['text'])), 3)
    prev_end = res[-1]['e']
    out.append(res)
    print(i, ' '.join(f"{r['text']}[{r['w']:.2f}->{r['s']:.2f}-{r['e']:.2f}]" for r in res), flush=True)
json.dump(out, open(sys.argv[3], 'w'), ensure_ascii=False)
