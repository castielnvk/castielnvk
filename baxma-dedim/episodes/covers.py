"""Instagram/TikTok cover options for every BAXMA DEDİM. episode.

    python3 covers.py            # all episodes in EPISODES
    python3 covers.py 01         # one episode

Per episode this writes  <episode>/covers/<NN>-cover-<option>.svg / .png (1080×1920)
and a comparison board  <episode>/covers/EP<NN>-covers-board.png.

Instagram shows Reel covers in the profile grid cropped to the centre 3:4 (1080×1440,
y 240–1680), so every title and key subject is kept inside that band.
The SVGs are editable: the still is one embedded <image>, all type is vector outlines.
To add an episode: add a dict to EPISODES (source, frame times, focus points, text).
"""
import base64
import io
import json
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
from concepts import ANTON, ISERIF_I, ITIGHT5  # noqa: E402
from lib import BONE, INK, RED, cap_height, fmt, run, svg_doc  # noqa: E402

W, H = 1080, 1920
GRID_TOP, GRID_BOT = 240, 1680          # Instagram profile-grid 3:4 crop
RED_HI = "#C42A20"
HOOK = ' stroke="#C42A20" stroke-width="2.6" stroke-linejoin="round"'
SHADOW_DEF = ('<defs><filter id="tsh" x="-10%" y="-40%" width="120%" height="180%">'
              '<feGaussianBlur in="SourceAlpha" stdDeviation="16"/><feComponentTransfer><feFuncA type="linear" slope="0.85"/></feComponentTransfer>'
              '<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')

EPISODES = [
    dict(
        num="01", folder="ep01-kotar",
        source="source/kitchen_gemini.mp4", crop=(4, 14, 704, 1252),
        grade=("eq=contrast=1.06:brightness=-0.012:saturation=0.93,"
               "curves=all='0/0 0.12/0.085 0.45/0.43 0.8/0.81 1/1',"
               "colorbalance=rh=-0.015:bh=0.025:bm=0.01,vignette=angle=PI/4.6"),
        # stills (source seconds) and focus points in 1080×1920 frame coordinates
        stills=dict(stare=6.5, wide=8.5, touch=4.25),
        face=(603, 1100), plate=(520, 1600),
        name="Kotar sindromu",
        title=("KOTAR", "SİNDROMU"),            # syndrome / topic name, uppercase (İ for i)
        hook="özünü ölü sanır.",                # short red "correction" line
        big="SAĞDIR.", big_sub="Amma buna inanmır.",
    ),
    dict(
        num="02", folder="ep02-esidir", styles=["A"],   # from EP02 on: style A only (user's choice)
        source="source/bedroom_gemini.mp4", crop=(4, 14, 704, 1252),
        grade=("eq=contrast=1.04:brightness=-0.01:saturation=0.97,"
               "curves=all='0/0 0.10/0.075 0.5/0.49 1/1',vignette=angle=PI/5"),
        stills=dict(stare=88 / 24 + 0.01),       # frame 88: the hand stopped, gap clearly visible
        face=(600, 1239),                         # close-up subject: the gap between the hands
        name="Bəlkə hələ eşidir",
        title=("BƏLKƏ HƏLƏ", "EŞİDİR"),
        hook="ömrünün son saatlarında.",
    ),
    dict(
        num="03", folder="ep03-yuxu-iflici", styles=["A"],
        source="source/bedroom_door_gemini.mp4", crop=(4, 14, 704, 1252),
        grade=("eq=contrast=1.05:brightness=-0.02:saturation=0.95,"
               "curves=all='0/0 0.12/0.08 0.5/0.47 1/1',vignette=angle=PI/4.8"),
        stills=dict(stare=7.0),                   # curtain settled after its one shift
        face=(820, 760),                          # close-up subject: the dark doorway
        name="Yuxu iflici",
        title=("YUXU", "İFLİCİ"),
        hook="elə bil otaqda kimsə var.",
    ),
    dict(
        num="04", folder="ep04-damdabaca", styles=["A"],
        source="source/2_roof_silhouette.mp4", crop=(4, 14, 704, 1252),
        grade="eq=contrast=1.03:brightness=-0.015:saturation=0.97,vignette=angle=PI/4.6",
        stills=dict(stare=6.0),                   # silhouette leaning over the chimney
        face=(840, 720),                          # close-up subject: the silhouette at the chimney (kept above the title)
        name="Damdabaca",
        title=("DAMDA", "BACA"),                  # "Adını ayrı-ayrı de: damda baca"
        hook="bəs sən bacaya baxardın?",
    ),
    dict(
        num="05", folder="ep05-cin-toyu", styles=["A"],
        source="source/1_old_man_staring.mp4", crop=(4, 14, 704, 1252),
        grade="eq=contrast=1.03:brightness=-0.02:saturation=0.96,vignette=angle=PI/4.6",
        stills=dict(stare=3.0),
        face=(360, 840),                          # the old man staring into the lens (face above the title)
        name="Cin toyu",
        title=("CİN", "TOYU"),
        hook="gedib baxardın?",
    ),
]


# ---------------------------------------------------------------------------
def still(ep, t, zoom=1.0, center=None, out_w=W, out_h=H):
    """graded frame at source time t, optionally zoomed around center (frame coords)."""
    src = os.path.join(HERE, ep["folder"], ep["source"])
    cx, cy, cw, ch = ep["crop"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf",
                          f"crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos,{ep['grade']},unsharp=5:5:0.35",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if zoom > 1:
        bw, bh = W / zoom, H / zoom
        x, y = center or (W / 2, H / 2)
        x0 = min(max(x - bw / 2, 0), W - bw)
        y0 = min(max(y - bh / 2, 0), H - bh)
        im = im.resize((out_w, out_h), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def image(href, opacity=1.0):
    return f'<image id="still" href="{href}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" opacity="{opacity}"/>'


def shade(pid, stops):
    """vertical darkening gradient: stops = [(offset 0..1, opacity)]."""
    s = "".join(f'<stop offset="{o}" stop-color="{INK}" stop-opacity="{a}"/>' for o, a in stops)
    return (f'<defs><linearGradient id="{pid}" x1="0" y1="0" x2="0" y2="1">{s}</linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{pid})"/>')


def text(font, s, size, x, y, fill, track=0.0, anchor="left", idp="", extra=""):
    r = run(font, s, size, track=track)
    b = r.bbox
    if anchor == "center":
        x -= (b[0] + b[2]) / 2
    elif anchor == "right":
        x -= b[2]
    r = run(font, s, size, track=track, x=x, y=y)
    return r.paths(fill, idp=idp, extra=extra), r.bbox


def fit(font, s, width, track=0.0):
    """font size so that the ink width of s equals width."""
    r = run(font, s, 100, track=track)
    return 100 * width / (r.bbox[2] - r.bbox[0])


def series_tag(num, y, x=W / 2, anchor="center", color="#B7AFA2"):
    p, _ = text(ITIGHT5, f"BAXMA DEDİM.  ·  {num}", 26, x, y, color, track=0.22, anchor=anchor)
    return f'<g id="series-tag">{p}</g>'


# ---------------------------------------------------------------------------
# Option A — "Üz" (the stare): tight on his face, title stacked under him
def opt_stare(ep):
    href = still(ep, ep["stills"]["stare"], zoom=1.55, center=(ep["face"][0], ep["face"][1] + 120))
    t1, t2 = ep["title"]
    size = min(fit(ANTON, t1, 860), fit(ANTON, t2, 860), 300)   # cap: short words must not swallow the subject
    cap = cap_height(ANTON, size)
    y2 = 1500
    y1 = y2 - cap - 0.24 * cap           # room for the İ dots of line 2
    p1, b1 = text(ANTON, t1, size, W / 2, y1, BONE, anchor="center")
    p2, b2 = text(ANTON, t2, size, W / 2, y2, BONE, anchor="center")
    hs = min(86, fit(ISERIF_I, ep["hook"], W - 2 * 84))
    hw = run(ISERIF_I, ep["hook"], hs).bbox
    right = min(max(b1[2], b2[2]) + 20, W - 70)
    right = max(right, 84 + (hw[2] - hw[0]))    # never past the left margin
    ph, _ = text(ISERIF_I, ep["hook"], hs, right, y2 + 0.30 * cap + cap_height(ISERIF_I, hs) + 22, RED_HI,
                 anchor="right", extra=HOOK)
    return (image(href) + shade("g", [(0, .55), (.18, 0), (.45, 0), (.62, .55), (.78, .9), (1, .95)]) +
            series_tag(ep["num"], 312) + f'<g id="title" filter="url(#tsh)">{p1}{p2}</g><g id="hook" filter="url(#tsh)">{ph}</g>')


# Option B — "Boşqab" (the untouched plate): spoon and plate close, title in the dark above
def opt_plate(ep):
    href = still(ep, ep["stills"]["stare"], zoom=1.9, center=(ep["plate"][0], ep["plate"][1] - 230))
    t1, t2 = ep["title"]
    size = fit(ANTON, t1 + " " + t2, 900)
    cap = cap_height(ANTON, size)
    y = 420 + cap
    p, b = text(ANTON, t1 + " " + t2, size, W / 2, y, BONE, anchor="center")
    hs = 92
    ph, _ = text(ISERIF_I, ep["hook"], hs, b[2] + 10, y + cap_height(ISERIF_I, hs) + 30, RED_HI, anchor="right", extra=HOOK)
    return (image(href) + shade("g", [(0, .95), (.16, .85), (.32, .35), (.45, 0), (.85, 0), (1, .6)]) +
            series_tag(ep["num"], 312) + f'<g id="title" filter="url(#tsh)">{p}</g><g id="hook" filter="url(#tsh)">{ph}</g>')


# Option C — "Düzəliş" (the logo's correction idea): one huge word, the red line that undoes it
def opt_correction(ep):
    href = still(ep, ep["stills"]["wide"])
    size = fit(ANTON, ep["big"], 900)
    cap = cap_height(ANTON, size)
    y = 900 + cap / 2
    p, b = text(ANTON, ep["big"], size, W / 2, y, BONE, anchor="center")
    hs = 92
    ph, _ = text(ISERIF_I, ep["big_sub"], hs, b[2] + 24, y + cap_height(ISERIF_I, hs) + 40, RED_HI, anchor="right", extra=HOOK)
    name = ep["name"]
    pn, _ = text(ITIGHT5, name, 42, W / 2, 1530, "#CFC7B9", track=0.04, anchor="center")
    return (image(href, 0.42) + shade("g", [(0, .6), (.3, .45), (.7, .45), (1, .8)]) +
            series_tag(ep["num"], 312) + f'<g id="big" filter="url(#tsh)">{p}</g><g id="hook" filter="url(#tsh)">{ph}</g><g id="name">{pn}</g>')


# Option D — "Mətbəx" (the wide, quiet room): whole kitchen, small cinematic title in the ceiling
def opt_wide(ep):
    href = still(ep, ep["stills"]["wide"], zoom=1.06, center=(540, 1060))
    t = " ".join(ep["title"])
    size = fit(ANTON, t, 820)
    cap = cap_height(ANTON, size)
    y = 372 + cap
    p, b = text(ANTON, t, size, W / 2, y, BONE, track=0.02, anchor="center")
    hs = 76
    ph, _ = text(ISERIF_I, ep["hook"], hs, W / 2, y + cap_height(ISERIF_I, hs) + 26, RED_HI, anchor="center", extra=HOOK)
    return (image(href) + shade("g", [(0, .75), (.3, .25), (.5, 0), (.85, 0), (1, .5)]) +
            series_tag(ep["num"], 300) + f'<g id="title" filter="url(#tsh)">{p}</g><g id="hook" filter="url(#tsh)">{ph}</g>')


OPTIONS = [("A", "uz", "Üz", opt_stare), ("B", "bosqab", "Boşqab", opt_plate),
           ("C", "duzelis", "Düzəliş", opt_correction), ("D", "metbex", "Mətbəx", opt_wide)]


def build(ep):
    out = os.path.join(HERE, ep["folder"], "covers")
    os.makedirs(out, exist_ok=True)
    jobs, made = [], []
    for key, slug, label, fn in [o for o in OPTIONS if o[0] in ep.get("styles", "ABCD")]:
        base = os.path.join(out, f'{ep["num"]}-cover-{key}-{slug}')
        with open(base + ".svg", "w", encoding="utf-8") as f:
            f.write(svg_doc(W, H, SHADOW_DEF + f'<rect width="{W}" height="{H}" fill="{INK}"/>' + fn(ep),
                            f'BAXMA DEDİM. {ep["num"]} cover {key}'))
        jobs.append([base + ".svg", base + ".png", W, H, 1])
        made.append((key, label, os.path.basename(base) + ".png"))
    with open(os.path.join(out, "jobs.json"), "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", os.path.join(ROOT, "render.js"), os.path.join(out, "jobs.json")], check=True)
    os.remove(os.path.join(out, "jobs.json"))

    # board: each option full 9:16, its 3:4 grid crop, and a 3-up profile grid mock
    cards = "".join(f'''<div class="opt"><h2><b>{k}</b> {lbl}</h2>
<div class="pair"><img class="full" src="{p}"><div class="gridc"><div class="crop" style="background-image:url({p})"></div><span>profil şəbəkəsi 3:4</span></div></div></div>'''
                    for k, lbl, p in made)
    html = f'''<!doctype html><meta charset="utf-8"><style>
body{{margin:0;background:#121110;color:#E8E1D3;font-family:Inter,sans-serif;width:1200px;padding:36px 40px 44px;box-sizing:border-box}}
h1{{font-size:28px;margin:0 0 6px}} p.sub{{color:#8a8275;margin:0 0 26px;font-size:14px}}
.wrap{{display:grid;grid-template-columns:1fr 1fr;gap:26px}}
.opt{{background:#1A1816;border:1px solid #2a2723;border-radius:14px;padding:16px 18px}}
h2{{margin:0 0 12px;font-size:18px;font-weight:600}} h2 b{{color:#C42A20;margin-right:6px}}
.pair{{display:flex;gap:16px;align-items:flex-start}}
.full{{width:250px;height:444px;border-radius:8px;display:block}}
.gridc{{display:flex;flex-direction:column;gap:8px;align-items:center}}
.crop{{width:240px;height:320px;background-size:240px 427px;background-position:center;border-radius:4px}}
.gridc span{{font-size:11px;color:#7a7266;letter-spacing:.04em}}
</style><h1>BAXMA DEDİM. — EP{ep["num"]} cover variantları</h1>
<p class="sub">Solda tam 9:16 cover, sağda Instagram profil şəbəkəsində görünən 3:4 kəsik.</p>
<div class="wrap">{cards}</div>'''
    hp = os.path.join(out, "board.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html)
    subprocess.run(["node", os.path.join(ROOT, "render.js"), "--board", hp,
                    os.path.join(out, f'EP{ep["num"]}-covers-board.png')], check=True)
    os.remove(hp)
    print("covers:", out)


if __name__ == "__main__":
    want = sys.argv[1:]
    for ep in EPISODES:
        if not want or ep["num"] in want:
            build(ep)
