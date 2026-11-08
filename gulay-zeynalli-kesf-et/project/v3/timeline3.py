"""v3 — social-media paparazzi cut. src times refer to IMG_7215.MOV. Non-clip beats are snapped so every answer starts on the music grid."""
import math
FPS = 30; BPM = 124; BEAT = 60 / BPM
def q(t): return round(t * FPS) / FPS

SEGMENTS = [
    dict(kind='clip', tag='hook', parts=[(69.18, 71.6667, 1.24, 1.32)], vf=True),
    dict(kind='collage', dur=2.55),
    dict(kind='q', n=1, cat='SƏNƏTİ', text='Bu günə istedad gətirdi, yoxsa mübarizə?', sm=0.6, dur=1.6),
    dict(kind='clip', n=1, parts=[(4.92, 8.3667, 1.00, 1.07, 7.70, 1.22)]),
    dict(kind='q', n=2, cat='AİLƏ', text='Səhnədəki Gülay, yoxsa ailədəki?', sm=10.9, dur=1.5),
    dict(kind='clip', n=2, parts=[(13.62, 17.40, 1.06, 1.10, 15.42, 1.24)]),
    dict(kind='q', n=3, cat='XASİYYƏTİ', text='Haqlı olduğunuz halda üzr istəyirsiniz?', sm=31.4, dur=1.6),
    dict(kind='clip', n=3, parts=[(42.25, 42.95, 1.04, 1.06), (43.62, 49.6333, 1.08, 1.14, 46.55, 1.30)], vf_from=46.55),
    dict(kind='burst', dur=0.9),
    dict(kind='q', n=4, cat='HƏMKARLARI', text='Kiminlə münasibətiniz əvvəlki kimi deyil?', sm=50.4, dur=1.6),
    dict(kind='clip', n=4, parts=[(53.45, 55.62, 1.00, 1.05), (56.32, 57.3667, 1.18, 1.20)]),
    dict(kind='follow', text='Qəlbiniz qırılmır?', src=67.30, dur=1.2),
    dict(kind='callback', dur=1.5, quote='QƏLBİM ARTIQ\nQIRILMIR.'),
    dict(kind='q', n=5, cat='GÖZLƏNİLMƏZ ETİRAF', text='Səmimi olmayan tərifə inanmış kimi davranırsınız?', sm=73.9, dur=1.75),
    dict(kind='clip', n=5, parts=[(78.24, 78.86, 1.04, 1.06), (79.50, 82.40, 1.10, 1.22)]),
    dict(kind='end', sm=75.3, dur=2.8),
]

# word-by-word captions: chunk (src start, words); emphasis words marked with '*'
CHUNKS = [
    (69.25, 'Qəlbim artıq'), (69.95, '*qırılmır.'), (70.70, 'O, əvvəllər'), (71.40, 'idi.'),
    (5.01, 'Təbii ki,'), (5.57, '*istedad olmasa,'), (6.41, '*mübarizə də'), (7.00, 'olmaz.'), (7.73, '*İkisi də.'),
    (13.72, 'Mən *ailədəki'), (14.47, 'Gülayı sevirəm,'), (15.45, 'tamaşaçılar isə'), (16.37, '*səhnədəki Gülayı.'),
    (42.39, '*Yox.'), (43.81, '*Haqsız olsam,'), (45.03, 'səhvim olsa,'), (46.00, 'üzr istəyirəm.'),
    (46.58, '*Haqlı olduğum'), (47.55, 'halda mən'), (48.00, '*niyə üzr'), (48.45, 'istəyim ki?'), (49.23, '*Yox.'),
    (53.63, 'Hamısıyla'), (54.14, 'münasibət'), (54.72, 'çox *gözəldir.'), (56.42, 'Hamısını'), (56.80, 'çox *sevirəm.'),
    (78.36, '*Heç vaxt.'), (79.66, '*Səmimiyyət'), (80.33, 'olmayan ortamda'), (81.43, 'mən heç vaxt'), (82.05, '*olmuram.'),
]
CHUNK_END_PAD = 0.25

def build():
    items = []; t = 0.0; grid0 = None; last_clip = None
    for s in SEGMENTS:
        s = dict(s)
        if s['kind'] == 'clip':
            parts = []
            for pp in s['parts']:
                a, b, z0, z1 = pp[:4]; a, b = q(a), q(b)
                d = dict(src_in=a, src_out=b, out_in=t, out_out=t + (b - a), z0=z0, z1=z1)
                if len(pp) > 4: d['zcut'] = (q(pp[4]), pp[5])
                parts.append(d); t += b - a
            s['parts'] = parts; s['start'] = parts[0]['out_in']; s['end'] = t; last_clip = s
        else:
            s['start'] = t
            if grid0 is None: grid0 = t                        # first drop = bar 0 of the music grid
            end = t + s['dur']
            if s['kind'] != 'end':
                n = round((end - grid0) / BEAT)
                if grid0 + n * BEAT < t + s['dur'] - 0.25: n += 1
                end = grid0 + n * BEAT
            t = q(end); s['end'] = t
            if s['kind'] in ('burst', 'callback', 'collage'):
                p = last_clip['parts'][-1]; s['freeze_sf'] = int(round(p['src_out'] * FPS)) - 1; s['freeze_z'] = p['z1']
        items.append(s)
    return items, t, grid0

def caption_chunks(items):
    """returns list of (out_start, out_end, text) — chunks end at next chunk start or the clip end."""
    ev = []
    for it in items:
        if it['kind'] != 'clip': continue
        for p in it['parts']:
            cs = [(a, txt) for a, txt in CHUNKS if p['src_in'] - 0.05 <= a < p['src_out']]
            for k, (a, txt) in enumerate(cs):
                nxt = cs[k + 1][0] if k + 1 < len(cs) else p['src_out']
                ev.append((p['out_in'] + max(0, a - p['src_in']), p['out_in'] + min(nxt, p['src_out']) - p['src_in'], txt))
    ev.sort(); return ev

if __name__ == '__main__':
    items, T, g0 = build()
    for it in items: print(f"{it['kind']:8s} {str(it.get('n', it.get('tag', ''))):5s} {it['start']:6.2f}-{it['end']:6.2f}  ({it['end'] - it['start']:.2f})")
    print('TOTAL', round(T, 2), 'grid0', g0)
