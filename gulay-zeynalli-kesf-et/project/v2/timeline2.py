"""v2 — tight paparazzi cut. All src times refer to IMG_7215.MOV (seconds)."""
FPS = 30
def q(t): return round(t * FPS) / FPS

# clip parts: (src_in, src_out, z0, z1[, zcut_src, zcut_z])  — zcut = hard punch-in at a src time inside the part (video only)
SEGMENTS = [
    dict(kind='clip', tag='hook', parts=[(46.5333, 48.95, 1.20, 1.27)]),
    dict(kind='title', dur=2.3, flash=True),                                   # freeze of previous frame as press photo
    dict(kind='card', n=1, cat='SƏNƏTİ', text='Bu günə istedad gətirdi,\nyoxsa mübarizə?', src=(1.00, 3.20), dur=2.3),
    dict(kind='clip', n=1, parts=[(4.92, 8.95, 1.00, 1.08)]),
    dict(kind='card', n=2, cat='AİLƏ', text='Səhnədəki Gülay,\nyoxsa ailədəki?', src=(10.90, 12.90), dur=2.1),
    dict(kind='clip', n=2, parts=[(13.62, 17.40, 1.06, 1.12)]),
    dict(kind='follow', text='Hansından imtina\netmək çətindir?', src=(17.55, 19.05), dur=1.5),
    dict(kind='clip', n=2, parts=[(19.90, 20.62, 1.00, 1.02), (22.95, 28.9667, 1.06, 1.10, 26.20, 1.30)]),
    dict(kind='card', n=3, cat='XASİYYƏTİ', text='Haqlı olduğunuz halda\nüzr istəyirsiniz?', src=(31.10, 33.40), dur=2.3),
    dict(kind='clip', n=3, parts=[(42.25, 42.95, 1.04, 1.06), (43.62, 46.5333, 1.14, 1.20)]),
    dict(kind='freeze', dur=1.15, quote='HAQSIZ OLSAM,\nÜZR İSTƏYİRƏM.'),
    dict(kind='card', n=4, cat='HƏMKARLARI', text='Kiminlə münasibətiniz\nəvvəlki kimi deyil?', src=(50.00, 52.40), dur=2.4),
    dict(kind='clip', n=4, parts=[(53.45, 55.62, 1.00, 1.05), (56.32, 57.3667, 1.12, 1.14)]),
    dict(kind='follow', text='Qəlbiniz qırılmır?', src=(67.30, 68.70), dur=1.4),
    dict(kind='clip', n=4, parts=[(69.18, 71.66, 1.22, 1.30)]),
    dict(kind='freeze', dur=1.25, quote='QƏLBİM ARTIQ\nQIRILMIR.'),
    dict(kind='card', n=5, cat='GÖZLƏNİLMƏZ ETİRAF', text='Səmimi olmayan tərifə\ninanmış kimi davranırsınız?', src=(72.70, 75.20), dur=2.5),
    dict(kind='clip', n=5, parts=[(78.24, 78.86, 1.04, 1.06), (79.50, 82.40, 1.12, 1.22)]),
    dict(kind='freeze', dur=1.3, quote='SƏMİMİYYƏT OLMAYAN\nORTAMDA MƏN HEÇ VAXT\nOLMURAM.', last=True),
    dict(kind='end', dur=2.4),
]

CAPTIONS = [
    (46.53, 48.95, 'Haqlı olduğum halda\nmən niyə üzr istəyim ki?'),
    (4.98, 7.62, 'Təbii ki, istedad olmasa,\nmübarizə də olmaz.'),
    (7.62, 8.40, 'İkisi də.'),
    (13.62, 15.42, 'Mən ailədəki Gülayı sevirəm,'),
    (15.42, 17.40, 'tamaşaçılar isə\nsəhnədəki Gülayı.'),
    (19.90, 20.62, 'Heç birindən.'),
    (22.95, 24.75, 'İkisi də gözəl,'),
    (24.80, 26.20, 'sevilməyə, sevməyə,'),
    (26.20, 28.95, 'xoşbəxt olmağa\nlayiq Gülaydır.'),
    (42.25, 42.95, 'Yox.'),
    (43.62, 46.5333, 'Haqsız olsam, səhvim olsa,\nüzr istəyirəm.'),
    (53.45, 55.62, 'Hamısıyla münasibət\nçox gözəldir.'),
    (56.32, 57.3667, 'Hamısını çox sevirəm.'),
    (69.18, 70.55, 'Qəlbim artıq qırılmır.'),
    (70.55, 71.66, 'O, əvvəllər idi.'),
    (78.24, 78.86, 'Heç vaxt.'),
    (79.50, 82.40, 'Səmimiyyət olmayan ortamda\nmən heç vaxt olmuram.'),
]
# live quote headline over footage (src start, dur, text)
LIVE_QUOTES = [(7.70, 1.25, 'İSTEDAD OLMASA,\nMÜBARİZƏ DƏ OLMAZ.')]

def build():
    items = []; t = 0.0; last_clip = None
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
            s['start'] = t; t = q(t + s['dur']); s['end'] = t
            if 'src' in s: s['src'] = (q(s['src'][0]), q(s['src'][1]))
            if s['kind'] in ('title', 'freeze', 'end'):
                p = last_clip['parts'][-1]; s['freeze_sf'] = int(round(p['src_out'] * FPS)) - 1; s['freeze_z'] = p['z1']
        items.append(s)
    return items, t

def caption_events(items):
    ev = []
    for it in items:
        if it['kind'] != 'clip': continue
        for p in it['parts']:
            for (a, b, txt) in CAPTIONS:
                lo, hi = max(a, p['src_in']), min(b, p['src_out'])
                if hi - lo > 0.15: ev.append((p['out_in'] + lo - p['src_in'], p['out_in'] + hi - p['src_in'], txt))
    ev.sort(); return ev

def live_quote_events(items):
    ev = []
    for (a, d, txt) in LIVE_QUOTES:
        for it in items:
            if it['kind'] != 'clip': continue
            for p in it['parts']:
                if p['src_in'] <= a <= p['src_out']: ev.append((p['out_in'] + a - p['src_in'], d, txt))
    return ev

if __name__ == '__main__':
    items, T = build()
    for it in items: print(f"{it['kind']:7s} {it.get('n', it.get('tag', ''))!s:5s} {it['start']:6.2f}-{it['end']:6.2f}")
    print('TOTAL', T)
