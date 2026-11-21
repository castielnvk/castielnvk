import json, sys, numpy as np, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
y, sr = librosa.load('../src/sep/htdemucs_ft/song/vocals.wav', sr=16000)
A = json.load(open('aligned.json'))
a0, a1, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
seg = y[int(a0*sr):int(a1*sr)]
S = librosa.amplitude_to_db(np.abs(librosa.stft(seg, n_fft=1024, hop_length=160)), ref=np.max)
rms = librosa.feature.rms(y=seg, frame_length=640, hop_length=160)[0]
fig, ax = plt.subplots(2, 1, figsize=(26, 7), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
ax[0].imshow(S[:200], origin='lower', aspect='auto', extent=[a0, a1, 0, 5000], cmap='magma', vmin=-60)
t = a0 + np.arange(len(rms)) * 0.01
ax[1].plot(t, 20*np.log10(rms+1e-6)); ax[1].set_ylim(-60, -5)
for line in A:
    for w in line:
        if a0 <= w['s'] <= a1:
            ax[0].axvline(w['s'], color='cyan', lw=1); ax[0].text(w['s'], 4600, w['text'], color='cyan', fontsize=10, rotation=0)
            ax[1].axvline(w['s'], color='cyan', lw=1)
        if a0 <= w['w'] <= a1:
            ax[0].axvline(w['w'], color='lime', lw=0.8, ls='--'); ax[0].text(w['w'], 300, w['text'], color='lime', fontsize=8)
ax[1].set_xticks(np.arange(np.ceil(a0), a1, 0.5)); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(out, dpi=70)
