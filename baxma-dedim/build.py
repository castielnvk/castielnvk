"""Build all six BAXMA DEDİM. concepts: SVG sources, PNG renders and the comparison board.

    python3 build.py        # needs: fonttools brotli, node + playwright (Chromium)
"""
import html
import json
import os
import subprocess

from concepts import CONCEPTS
from lib import fmt, svg_doc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "concepts")
jobs = []  # (svg_path, png_path, w, h, scale)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


meta = []
for num, slug, title, fn, why in CONCEPTS:
    c = fn()
    d = os.path.join(OUT, f"{num}-{slug}")
    inner, (x0, y0, x1, y1) = c["wordmark"]
    W, H = x1 - x0, y1 - y0
    s = 1600 / W  # normalise wordmark artboards to 1600 px wide
    wm = svg_doc(1600, H * s, f'<g transform="scale({s:.5f}) translate({fmt(-x0)} {fmt(-y0)})">\n{inner}\n</g>',
                 f"BAXMA DEDİM. — {num} {title} (wordmark)")
    write(f"{d}/{num}-wordmark.svg", wm)
    write(f"{d}/{num}-avatar.svg", svg_doc(512, 512, c["avatar"], f"BAXMA DEDİM. — {num} avatar"))
    write(f"{d}/{num}-endcard-9x16.svg", svg_doc(1080, 1920, c["endcard"], f"BAXMA DEDİM. — {num} end card"))
    jobs += [
        (f"{d}/{num}-wordmark.svg", f"{d}/{num}-wordmark-transparent.png", 1600, round(H * s), 2),
        (f"{d}/{num}-avatar.svg", f"{d}/{num}-avatar-512.png", 512, 512, 1),
        (f"{d}/{num}-avatar.svg", f"{d}/{num}-avatar-48.png", 512, 512, 48 / 512),
        (f"{d}/{num}-endcard-9x16.svg", f"{d}/{num}-endcard-1080x1920.png", 1080, 1920, 1),
    ]
    meta.append(dict(num=num, slug=slug, title=title, why=why, panel=c["panel"], fonts=c["fonts"],
                     dir=f"{num}-{slug}"))

write(os.path.join(HERE, "build", "jobs.json"), json.dumps(jobs))
subprocess.run(["node", os.path.join(HERE, "render.js"), os.path.join(HERE, "build", "jobs.json")], check=True)

# ---- comparison board -------------------------------------------------------
cards = []
for m in meta:
    p = f"concepts/{m['dir']}/{m['num']}"
    cards.append(f'''
<section class="card">
  <header><span class="num">{m["num"]}</span><h2>{html.escape(m["title"])}</h2><span class="font">{html.escape(m["fonts"])}</span></header>
  <div class="wm" style="background:{m["panel"]}"><img src="{p}-wordmark-transparent.png"></div>
  <div class="row">
    <img class="ec" src="{p}-endcard-1080x1920.png">
    <div class="side">
      <div class="avs">
        <figure><img class="a48" src="{p}-avatar-512.png"><figcaption>48 px</figcaption></figure>
        <figure><img class="a160" src="{p}-avatar-512.png"><figcaption>avatar mark</figcaption></figure>
      </div>
      <p>{html.escape(m["why"])}</p>
    </div>
  </div>
</section>''')

board = f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{background:#121110;color:#E8E1D3;font-family:"Inter Display","Inter",sans-serif;width:1200px;padding:44px 40px 48px}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:28px;border-bottom:1px solid #2c2925;padding-bottom:18px}}
.top h1{{font-size:30px;font-weight:800;letter-spacing:.01em}} .top h1 em{{color:#B3241C;font-style:normal}}
.top div{{font-size:13px;color:#8a8275;text-align:right;line-height:1.5}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:26px}}
.card{{background:#1A1816;border:1px solid #2a2723;border-radius:14px;overflow:hidden}}
header{{display:flex;align-items:baseline;gap:12px;padding:14px 18px}}
.num{{font-weight:800;color:#B3241C;font-size:22px;font-variant-numeric:tabular-nums}}
h2{{font-size:19px;font-weight:700}} .font{{margin-left:auto;font-size:11.5px;color:#7a7266;letter-spacing:.04em}}
.wm{{height:250px;display:flex;align-items:center;justify-content:center;padding:26px 34px}}
.wm img{{max-width:100%;max-height:100%}}
.row{{display:flex;gap:18px;padding:18px}}
.ec{{width:162px;height:288px;border-radius:8px;border:1px solid #2f2c28;flex:none}}
.side{{display:flex;flex-direction:column;gap:16px}}
.avs{{display:flex;align-items:flex-end;gap:22px}}
figure{{display:flex;flex-direction:column;align-items:center;gap:7px}}
figcaption{{font-size:11px;color:#7a7266;letter-spacing:.05em}}
.a48{{width:48px;height:48px}} .a160{{width:132px;height:132px}}
.side p{{font-size:14.5px;line-height:1.5;color:#cfc8ba}}
</style></head><body>
<div class="top"><h1>BAXMA DEDİM<em>.</em> — six logo directions</h1>
<div>wordmark · 48 px avatar · 9:16 end card<br>near-black #0D0C0B · bone #E8E1D3 · red #B3241C</div></div>
<div class="grid">{"".join(cards)}</div></body></html>'''
write(os.path.join(HERE, "board.html"), board)
subprocess.run(["node", os.path.join(HERE, "render.js"), "--board", os.path.join(HERE, "board.html"),
                os.path.join(HERE, "BAXMA-DEDIM-board-01-06.png")], check=True)
print("done")
