"""Dialog cleanup + music bed with ducking/automation + synthesized SFX -> mix.wav"""
import numpy as np, subprocess, json, wave
SR = 48000
G = json.load(open('gfx.json')); TL = {s['id']: s for s in json.load(open('timeline.json'))}
T = G['T']; N = int(round(T * SR))
rng = np.random.default_rng(7)

def load(path, ch=1, extra=""):
    raw = subprocess.run(f'ffmpeg -loglevel error -i "{path}" {extra} -f f32le -ac {ch} -ar {SR} -', shell=True, capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    return a.reshape(-1, ch) if ch > 1 else a

# ---------- dialog: rumble cut, mild denoise (keeps laughter), leveling, gentle compression
dlg = load('dialog_raw.wav', 1, '-af "highpass=f=85,lowpass=f=15000,afftdn=nr=8:nf=-42:tn=1,dynaudnorm=f=250:g=13:p=0.9:m=8:s=12,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2"')
dlg = np.pad(dlg, (0, max(0, N - len(dlg))))[:N]

# ---------- speech mask -> music ducking envelope
hop = SR // 100
fr = dlg[:len(dlg) // hop * hop].reshape(-1, hop)
db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
speech = db > (np.percentile(db, 95) - 24)
k = 30  # dilate 300 ms each side
sp = np.convolve(speech.astype(float), np.ones(2 * k + 1), 'same') > 0
gdb = np.where(sp, -17.0, -9.0)
def seg_t(i): return TL[i]['ostart']
def seg_e(i): return TL[i]['ostart'] + TL[i]['odur']
t = np.arange(len(gdb)) / 100
gdb[t < 0.45] = -6.0                                   # punchy start under the title
gdb[(t >= seg_t('FZ')) & (t < seg_e('FZ'))] = -13      # freeze-frame beat
gdb[t >= seg_t('FE') + 0.1] = -5.0                     # outro swell
# smooth: fast attack (duck down), slower release
sm = np.empty_like(gdb); cur = gdb[0]
for i, g in enumerate(gdb):
    a = 0.35 if g < cur else 0.06
    if g <= -79: a = 1.0
    if i and gdb[i - 1] <= -79 and g > -79: cur = g  # music re-enters hard on the cut back
    cur += (g - cur) * a; sm[i] = cur
env = np.repeat(10 ** (sm / 20), hop)
env = np.pad(env, (0, N - len(env)), 'edge')[:N]

# ---------- music: Hep Cats (Kevin MacLeod, CC BY 4.0)
mus = load('../music/Hep_Cats.mp3', 2, '-af "loudnorm=I=-16:TP=-2:LRA=11"')
off = int(0.0 * SR)
mus = mus[off:off + N]
if len(mus) < N: mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
fo = int(1.4 * SR); mus[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
mus *= env[:, None]

# ---------- SFX synthesis
def adsr(n, a=0.002, r=None):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    return e
def bp_noise(n, f0, f1, q=3):
    """noise with a time-varying resonant band (simple biquad, coefficients per block)"""
    x = rng.standard_normal(n); y = np.zeros(n); b = 256
    z1 = z2 = 0.0
    for s in range(0, n, b):
        f = f0 + (f1 - f0) * s / n; w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q)
        b0, a0, a1, a2 = al, 1 + al, -2 * np.cos(w), 1 - al
        for i in range(s, min(n, s + b)):
            v = (b0 * x[i] - b0 * (x[i - 2] if i > 1 else 0) - a1 * z1 - a2 * z2) / a0
            z2, z1 = z1, v; y[i] = v
    return y / (np.abs(y).max() + 1e-9)
def whoosh(d=0.32):
    n = int(d * SR); x = bp_noise(n, 400, 3800, 2.2); e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * e * 0.5
def tick(f=1650):
    n = int(0.07 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 70) + 0.4 * rng.standard_normal(n) * np.exp(-tt * 400)) * 0.5
def stamp():
    n = int(0.36 * SR); tt = np.arange(n) / SR
    f = 95 * np.exp(-tt * 9) + 45; ph = 2 * np.pi * np.cumsum(f) / SR
    thump = np.sin(ph) * np.exp(-tt * 11)
    clack = rng.standard_normal(n) * np.exp(-tt * 160)
    snap = np.sin(2 * np.pi * 2300 * tt) * np.exp(-tt * 90)
    return (0.9 * thump + 0.35 * clack + 0.18 * snap) * 0.75
def ding(f):
    n = int(0.7 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt + 1.2 * np.exp(-tt * 6) * np.sin(2 * np.pi * 3.5 * f * tt)) * np.exp(-tt * 5.5) * 0.32
def swipe():
    n = int(0.2 * SR); return bp_noise(n, 2500, 900, 4) * np.sin(np.linspace(0, np.pi, n)) * 0.3
def tapestop():
    n = int(0.42 * SR); tt = np.arange(n) / SR; f = 520 * (1 - tt / tt[-1]) ** 2 + 45
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.4 * np.sign(np.sin(ph))) * np.exp(-tt * 3)
    return x * 0.3
def riser(d=1.0):
    n = int(d * SR); tt = np.arange(n) / SR
    x = bp_noise(n, 300, 5000, 3) * 0.6 + 0.25 * np.sin(2 * np.pi * (220 * tt + 300 * tt ** 2 / d))
    return x * (tt / d) ** 2 * 0.35

sfx = np.zeros(N)
def put(sig, at, gain_db=0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    j = min(N, i + len(sig)); sfx[max(i, 0):j] += sig[max(0, -i):j - i] * 10 ** (gain_db / 20)

put(whoosh(0.4), 0.0, -4)
for c in G['cards']:
    if c['i'] > 1: put(whoosh(), c['t_in'] - 0.08, -7)
    put(tick(), c['t_letter'] - 0.04, -6)
for r in G['revs']:
    if r['style'] == 'tease': continue           # silence sells the whisper
    put(stamp(), r['a'] - 0.01, -3)
    if r.get('pulse'): put(tick(1400), r['pulse'], -9)
    if r['style'] == 'combo': put(ding([784, 988, 1175][r['n'] - 1]), r['a'] + 0.02, -6)
    if r.get('strike'): put(swipe(), r['a'] + 0.42, -4)
F = G['extras']['freeze']; put(tapestop(), F['a'], -3); put(tick(1200), F['a'] + 0.3, -6)
LA = G['extras']['later']
for k in range(3): put(tick(2600 if k % 2 == 0 else 2000), LA['a'] + 0.04 + 0.22 * k, -9)
final = [r for r in G['revs'] if r['style'] == 'rainbow'][0]
put(riser(0.9), final['a'] - 0.9, -10)
put(ding(1568), final['a'] + 0.05, -9)
E = G['extras']['end']; put(stamp(), E['a'] + 0.35, -6)

# ---------- mix
mix = mus * 1.0 + (dlg[:, None] + sfx[:, None] * 0.9)
pk = np.abs(mix).max(); mix = mix / max(pk, 1e-9) * 0.89
with wave.open('mix_pre.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes())
# stems for the editable project
for name, arr in [('stem_dialog.wav', dlg), ('stem_sfx.wav', sfx * 0.9)]:
    with wave.open(name, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(arr / max(pk, 1e-9) * 0.89, -1, 1) * 32767).astype('<i2').tobytes())
with wave.open('stem_music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mus / max(pk, 1e-9) * 0.89, -1, 1) * 32767).astype('<i2').tobytes())
r=subprocess.run('ffmpeg -hide_banner -i mix_pre.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null -',shell=True,capture_output=True,text=True).stderr
j=json.loads(r[r.rfind('{'):r.rfind('}')+1])
af=f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(f'ffmpeg -loglevel error -y -i mix_pre.wav -af {af} -ar 48000 mix.wav', shell=True, check=True)
print("done", T)
