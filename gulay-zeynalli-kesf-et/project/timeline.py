"""Edit decision list for 'Kəşf Et — Gülay Zeynallı: 5 təəccüblü sual, 5 cavab'.
All src times refer to the original IMG_7215.MOV (seconds). Output is built sequentially."""
FPS = 30
def q(t): return round(t * FPS) / FPS

# kind: 'hook','title','card','follow','answer','end'
# For answers: parts = list of (src_in, src_out, zoom_from, zoom_to)
SEGMENTS = [
    dict(kind='hook',   parts=[(43.55, 49.02, 1.16, 1.24)]),
    dict(kind='title',  src=(75.30, 78.40), dur=3.4),
    dict(kind='card',   n=1, cat='SƏNƏTİ', text='Sizi bu günə istedad gətirib, yoxsa mübarizə?', src=(0.30, 3.70), dur=3.6),
    dict(kind='answer', n=1, parts=[(4.75, 9.30, 1.00, 1.07)]),
    dict(kind='card',   n=2, cat='AİLƏ', text='Səhnədəki Gülay, yoxsa ailədəki Gülay?', src=(9.90, 13.45), dur=3.4),
    dict(kind='answer', n=2, parts=[(13.45, 17.55, 1.10, 1.14)]),
    dict(kind='follow', n=2, text='Hansından imtina etmək çətindir?', src=(17.55, 19.75), dur=2.3),
    dict(kind='answer', n=2, parts=[(19.75, 28.97, 1.00, 1.10)]),
    dict(kind='card',   n=3, cat='XASİYYƏTİ', text='Haqlı olduğunuz halda üzr istədiyiniz olur?', src=(31.00, 34.40), dur=3.6),
    dict(kind='answer', n=3, parts=[(34.40, 37.75, 1.13, 1.16), (41.90, 49.62, 1.00, 1.06)], tail=0.6),
    dict(kind='card',   n=4, cat='HƏMKARLARI', text='Hansı həmkarınızla münasibətiniz əvvəlki kimi deyil?', src=(49.95, 53.40), dur=3.8),
    dict(kind='answer', n=4, parts=[(53.40, 67.10, 1.00, 1.15)]),
    dict(kind='follow', n=4, text='Qəlbiniz qırılmır?', src=(67.10, 69.00), dur=1.9),
    dict(kind='answer', n=4, parts=[(69.00, 72.70, 1.19, 1.24, 71.95)]),
    dict(kind='card',   n=5, cat='GÖZLƏNİLMƏZ ETİRAF', text='Səmimi olmayan tərifə inanmış kimi davranırsınız?', src=(72.70, 75.30), dur=3.8),
    dict(kind='answer', n=5, parts=[(78.05, 83.30, 1.04, 1.18)], last=True),
    dict(kind='end',    src=(83.30, 83.30), dur=5.4),
]

# Spoken captions (src time ranges, verified against the audio)
CAPTIONS = [
    (5.00, 7.62, 'Təbii ki, istedad olmasa,\nmübarizə də olmaz.'),
    (7.62, 8.40, 'İkisi də.'),
    (13.70, 15.42, 'Mən ailədəki Gülayı sevirəm,'),
    (15.42, 17.45, 'tamaşaçılar isə\nsəhnədəki Gülayı.'),
    (19.95, 21.20, 'Heç birindən.'),
    (21.98, 22.95, 'Heç birindən.'),
    (23.05, 24.70, 'İkisi də gözəl,'),
    (24.80, 26.30, 'sevilməyə, sevməyə,'),
    (26.30, 28.90, 'xoşbəxt olmağa\nlayiq Gülaydır.'),
    (34.80, 37.50, 'Haqlı olduğum halda\nüzr istəmək?'),
    (42.33, 43.60, 'Yox.'),
    (43.72, 46.62, 'Haqsız olsam, səhvim olsa,\nüzr istəyirəm.'),
    (46.68, 48.98, 'Haqlı olduğum halda\nmən niyə üzr istəyim ki?'),
    (49.18, 49.62, 'Yox.'),
    (53.58, 55.95, 'Hamısıyla münasibət\nçox gözəldir.'),
    (56.38, 58.25, 'Hamısını çox sevirəm,\nçünki biz'),
    (58.38, 60.20, 'sənət insanları,'),
    (60.33, 62.80, 'hamımız eyni sahədə,'),
    (63.40, 65.58, 'eyni işdə olan insanlarıq.'),
    (65.60, 67.05, 'Ona görə hamısını\nçox sevirəm.'),
    (69.20, 70.55, 'Qəlbim artıq qırılmır.'),
    (70.60, 71.80, 'O, əvvəllər idi.'),
    (78.28, 79.40, 'Heç vaxt.'),
    (79.60, 82.50, 'Səmimiyyət olmayan ortamda\nmən heç vaxt olmuram.'),
]

# Editorial pull-quotes: shown AFTER the words are spoken (src start time), duration in s
QUOTES = [
    (7.45, 1.45, 'İstedad olmasa,\nmübarizə də olmaz.'),
    (70.45, 1.95, 'Qəlbim artıq qırılmır.'),
    (82.35, 2.40, 'Səmimiyyət olmayan ortamda\nmən heç vaxt olmuram.'),
]
TRANS = 0.0

def build():
    """Returns list of output items with absolute output times."""
    items = []; t = 0.0
    for s in SEGMENTS:
        s = dict(s)
        if s['kind'] in ('hook', 'answer'):
            parts = []
            for pp in s['parts']:
                a, b, z0, z1 = pp[:4]; aout = pp[4] if len(pp) > 4 else pp[1]
                a, b = q(a), q(b)
                parts.append(dict(src_in=a, src_out=b, a_out=aout, out_in=t, out_out=t + (b - a), z0=z0, z1=z1))
                t += b - a
            s['parts'] = parts; s['start'] = parts[0]['out_in']; s['end'] = t
        else:
            s['start'] = t; t = q(t + s['dur']); s['end'] = t
            a, b = s['src']; s['src'] = (q(a), q(b))
        items.append(s)
    return items, t

def src_to_out(items, ts):
    """map a src time into output time if it falls inside an answer/hook part (first match, skipping hook)."""
    res = []
    for it in items:
        if it['kind'] not in ('answer', 'hook'): continue
        for p in it['parts']:
            if p['src_in'] - 1e-6 <= ts <= p['src_out'] + 1e-6:
                res.append((it['kind'], p['out_in'] + ts - p['src_in']))
    return res

def caption_events(items):
    ev = []
    for it in items:
        if it['kind'] not in ('answer', 'hook'): continue
        for p in it['parts']:
            for (a, b, txt) in CAPTIONS:
                lo, hi = max(a, p['src_in']), min(b, p['src_out'])
                if hi - lo > 0.15:
                    ev.append((p['out_in'] + lo - p['src_in'], p['out_in'] + hi - p['src_in'], txt))
    return ev

def quote_events(items):
    ev = []
    for (a, d, txt) in QUOTES:
        for it in items:
            if it['kind'] != 'answer': continue
            for p in it['parts']:
                if p['src_in'] <= a <= p['src_out']:
                    ev.append((p['out_in'] + a - p['src_in'], d, txt))
    return ev

if __name__ == '__main__':
    items, T = build()
    for it in items:
        print(f"{it['kind']:7s} {it.get('n','')!s:2s} {it['start']:6.2f}-{it['end']:6.2f}")
    print('TOTAL', T)
    for e in caption_events(items): print('CAP %.2f-%.2f %s' % (e[0], e[1], e[2].replace('\n', ' / ')))
    for e in quote_events(items): print('QUOTE %.2f +%.2f %s' % e)
