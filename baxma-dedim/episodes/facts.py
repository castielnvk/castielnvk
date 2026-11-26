"""BAXMA DEDİM. — one "Fakt" Instagram story per episode (the user wants ONLY this slide).

    python3 facts.py 02 03      ->  <episode>/story/<NN>-fakt.svg / .png (1080×1920)

Design: the episode still, near-black, desaturated and cold, with a heavy vignette and grain.
A big red italic number glows faintly. The fact is set in small spaced capitals (caption style C),
then one quiet italic sting line, the source, and the logo. Text stays inside the story-safe zone (y 250–1650).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "shared"))
import covers as CV  # noqa: E402
import type_c as TC  # noqa: E402
from concepts import ANTON, c01  # noqa: E402
from lib import fmt, place, run, svg_doc  # noqa: E402

W, H = 1080, 1920
RED, BONE, GREY = "#D23A2E", "#E6DFD1", "#8F877A"

FACTS = {
    "02": dict(still=88 / 24 + 0.01, center=(600, 1150), zoom=1.25,
               number="2020",
               fact="Kanadada alimlər ömrünün son saatlarında olan xəstələrin beynini ölçüblər. "
                    "Huşsuz vəziyyətdə olan bəzi xəstələrin beyni səslərə reaksiya verib.",
               sting="Eşitdiklərini anlayıb-anlamadıqları isə bilinmir.",
               source="Blundon və b., Scientific Reports, 2020"),
    "03": dict(still=7.0, center=(760, 900), zoom=1.2,
               number="7,6%",
               fact="İnsanların bu qədəri ən azı bir dəfə yuxu iflici yaşayıb. "
                    "Tələbələr arasında bu rəqəm 28%-ə çatır.",
               sting="Bir çoxu otaqda kiminsə olduğunu hiss etdiyini deyir.",
               source="Sharpless & Barber, Sleep Medicine Reviews, 2011"),
}

DEFS = f'''<defs>
<radialGradient id="vig" cx="0.5" cy="0.45" r="0.75"><stop offset="0.25" stop-color="#000" stop-opacity="0.35"/>
<stop offset="0.75" stop-color="#000" stop-opacity="0.82"/><stop offset="1" stop-color="#000" stop-opacity="0.96"/></radialGradient>
<filter id="cold"><feColorMatrix type="saturate" values="0.25"/>
<feComponentTransfer><feFuncR type="linear" slope="0.62"/><feFuncG type="linear" slope="0.68"/><feFuncB type="linear" slope="0.78"/></feComponentTransfer></filter>
<filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="22" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="sh2" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur in="SourceAlpha" stdDeviation="10"/>
<feComponentTransfer><feFuncA type="linear" slope="0.9"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="2" seed="13"/>
<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.10 0"/></filter>
</defs>'''


def greedy(text, font, size, maxw, track=0.0):
    """fast word wrap (the exhaustive balanced wrap is too slow for paragraphs)."""
    lines, cur = [], ""
    for w in text.split():
        cand = (cur + " " + w).strip()
        if not cur or TC._w(font, cand, size, track) <= maxw:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def centered(font, text, size, y, color, track=0.0):
    r = run(font, text, size, track=track)
    b = r.bbox
    return run(font, text, size, track=track, x=W / 2 - (b[0] + b[2]) / 2, y=y).paths(color)


def build(num):
    ep = next(e for e in CV.EPISODES if e["num"] == num)
    F = FACTS[num]
    href = CV.still(ep, F["still"], zoom=F["zoom"], center=F["center"])
    parts = []
    # header: FAKT. (red period, like the highlight cover) and a hairline
    fk = run(ANTON, "FAKT", 46, track=0.18)
    x0 = W / 2 - (fk.width + 16) / 2
    parts.append(run(ANTON, "FAKT", 46, track=0.18, x=x0, y=330).paths(BONE))
    parts.append(run(ANTON, ".", 46, x=x0 + fk.width + 4, y=330).paths(RED))
    parts.append(f'<rect x="{W / 2 - 40}" y="362" width="80" height="2" fill="{RED}" opacity="0.8"/>')
    # the number: big red italic with a faint glow
    ns = min(300, 300 * 820 / TC._w(TC.KEY, F["number"], 300))
    parts.append(f'<g filter="url(#glow)" opacity="0.98">{centered(TC.KEY, F["number"], ns, 690, RED)}</g>')
    # the fact: small spaced capitals
    y = 690 + 135
    lines = greedy(TC.az_upper(F["fact"]), TC.SMALL, 38, 800, TC.S_TRACK)
    for ln in lines:
        parts.append(f'<g filter="url(#sh2)">{centered(TC.SMALL, ln, 38, y, BONE, TC.S_TRACK)}</g>')
        y += 62
    # the sting: quiet italic, bone
    y += 50
    words = F["sting"].split()
    best = None
    for k in range(1, len(words)):                  # two balanced lines (no orphan word)
        a_, b_ = " ".join(words[:k]), " ".join(words[k:])
        d = abs(TC._w(TC.KEY, a_, 58) - TC._w(TC.KEY, b_, 58))
        if best is None or d < best[0]:
            best = (d, [a_, b_])
    sting = best[1] if TC._w(TC.KEY, F["sting"], 58) > 860 else [F["sting"]]
    for ln in sting:
        parts.append(f'<g filter="url(#sh2)">{centered(TC.KEY, ln, 58, y + 20, BONE)}</g>')
        y += 70
    # source + logo
    ys = max(y + 60, 1440)
    parts.append(centered(TC.SMALL, TC.az_upper("Mənbə: ") + F["source"].upper(), 24, ys, GREY, 0.12))
    inner, bbox = c01("fk")["wordmark"]
    parts.append(f'<g opacity="0.9">{place(inner, bbox, W / 2, ys + 95, width=280)}</g>')
    assert ys + 160 < 1680, "fact text too long for the story-safe zone"

    body = (DEFS + f'<rect width="{W}" height="{H}" fill="#050505"/>'
            f'<image href="{href}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" filter="url(#cold)" opacity="0.55"/>'
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/>'
            f'<rect width="{W}" height="{H}" filter="url(#grain)"/>' + "".join(parts))
    out = os.path.join(HERE, ep["folder"], "story")
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, f"{num}-fakt.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg_doc(W, H, body, f"BAXMA DEDİM. {num} — Fakt"))
    jp = os.path.join(out, "jobs.json")
    with open(jp, "w") as f:
        json.dump([[p, p[:-4] + ".png", W, H, 1]], f)
    subprocess.run(["node", os.path.join(HERE, "..", "render.js"), jp], check=True)
    os.remove(jp)
    print("fakt:", p[:-4] + ".png")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        build(n)
