"""Instagram Story slides for a BAXMA DEDİM. episode (1080×1920, SVG + PNG).

    python3 stories.py 01

4 slides: 1 hook (episode still) · 2 the real fact · 3 question (room left for a Poll sticker)
· 4 call to action with the approved logo (room left for a Link sticker).
Story-safe zones: nothing important above y=250 or below y=1670 (Instagram UI).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import covers as CV  # noqa: E402
from concepts import ANTON, ISERIF_I, ITIGHT5, c01, grain  # noqa: E402
from lib import BONE, INK, Font, fmt, place, run, svg_doc  # noqa: E402

W, H = 1080, 1920
SEMI = Font("inter-tight-latin-600-normal.woff2", "inter-tight-latin-ext-600-normal.woff2", name="Inter Tight SemiBold")
RED = CV.RED_HI
HOOK = CV.HOOK

STORIES = {
    "01": dict(
        hook_still=("stare", 6.5), hook_center=(560, 1250), hook_zoom=1.35,
        s1=["Qarşısında yemək var.", "Amma yemir."], s1_red="Çünki özünü ölü sanır.",
        s2_year="1880",
        s2=["1880-ci ildə fransız nevroloq", "Jül Kotar bir qadın xəstəni", "təsvir edib."],
        s2b=["Qadın beyninin və daxili", "orqanlarının olmadığına inanırdı.", "Yeməyə ehtiyacı olmadığını", "düşünürdü."],
        s3="Bunu əvvəl eşitmişdin?",
        s4=["Tam hekayə profildə."], s4_red="Amma mən sənə…",
    ),
    "02": dict(
        hook_still=("stare", 88 / 24 + 0.01), hook_center=(600, 1150), hook_zoom=1.3,
        s1=["Yanındakı adam", "sənə cavab vermir."], s1_red="Bəlkə hələ eşidir.",
        s2_year="2020",
        s2=["2020-ci ildə Kanadada alimlər", "hospisdə ömrünün son saatlarında", "olan xəstələrin beynini ölçüblər."],
        s2b=["Huşsuz vəziyyətdə olan bəzi", "xəstələrin beyni səslərə sağlam", "insanlarınkına bənzər reaksiya verib.",
             "Eşitdiklərini anlayıb-anlamadıqları", "isə bilinmir."],
        s3="Onunla danışmağa davam edərdin?",
        s4=["Tam hekayə profildə."], s4_red="Amma mən sənə…",
    ),
    "03": dict(
        hook_still=("stare", 7.0), hook_center=(700, 1000), hook_zoom=1.25,
        s1=["Oyanmısan,", "amma tərpənə bilmirsən."], s1_red="Otaqda kimsə var.",
        s2_year="7,6%",
        s2=["2011-ci ildə 35 araşdırmanın", "icmalı göstərib ki, insanların", "7,6%-i ən azı bir dəfə", "yuxu iflici yaşayıb."],
        s2b=["Tələbələr arasında", "bu rəqəm 28%-ə çatır."],
        s3="Sən heç yuxu iflici yaşamısan?",
        s4=["Tam hekayə profildə."], s4_red="Amma mən sənə…",
    ),
}


def lines_block(lines, font, size, cx, y_top, color, lead=1.25, extra=""):
    out, y = [], y_top
    for ln in lines:
        p, b = CV.text(font, ln, size, cx, y + size * 0.73, color, anchor="center", extra=extra)
        out.append(p)
        y += size * lead
    return "".join(out), y


def build(num):
    ep = next(e for e in CV.EPISODES if e["num"] == num)
    st = STORIES[num]
    out = os.path.join(HERE, ep["folder"], "story")
    os.makedirs(out, exist_ok=True)
    slides = {}

    # 1 · hook on the episode still
    key, t = st["hook_still"]
    href = CV.still(ep, t, zoom=st["hook_zoom"], center=st["hook_center"])
    a, y = lines_block(st["s1"], SEMI, 76, W / 2, 560, BONE)
    rs = min(92, CV.fit(ISERIF_I, st["s1_red"], 900))
    r, _ = CV.text(ISERIF_I, st["s1_red"], rs, W / 2, y + 70 + rs * 0.6, RED, anchor="center", extra=HOOK)
    slides["1-hook"] = (CV.image(href) + CV.shade("g", [(0, .85), (.22, .8), (.45, .55), (.62, .1), (.85, .1), (1, .7)]) +
                        CV.series_tag(num, 300) + f'<g filter="url(#tsh)">{a}</g><g filter="url(#tsh)">{r}</g>')

    # 2 · the real fact, on black
    ys = 520
    yr, _ = CV.text(ANTON, st["s2_year"], 230, W / 2, ys + 168, RED, anchor="center")
    b1, y = lines_block(st["s2"], SEMI, 56, W / 2, ys + 270, BONE)
    rule = f'<rect x="{W / 2 - 50}" y="{fmt(y + 30)}" width="100" height="3" fill="{RED}" opacity="0.85"/>'
    b2, _ = lines_block(st["s2b"], ITIGHT5, 50, W / 2, y + 90, "#CFC7B9")
    slides["2-fakt"] = (f'<rect width="{W}" height="{H}" fill="{INK}"/>' + grain("s2", 0.05) + CV.series_tag(num, 300) +
                        f'<g id="year">{yr}</g><g id="fact">{b1}</g>{rule}<g id="detail">{b2}</g>')

    # 3 · the question; lower half left empty for the Poll sticker
    href3 = CV.still(ep, ep["stills"]["stare"], zoom=1.55, center=(ep["face"][0], ep["face"][1] + 60))
    q, _ = lines_block([st["s3"]], SEMI, min(84, 84 * 900 / CV.run(SEMI, st["s3"], 84).width), W / 2, 470, BONE)
    slides["3-sorgu"] = (CV.image(href3, 0.55) + CV.shade("g", [(0, .9), (.3, .6), (.55, .75), (1, .95)]) +
                         CV.series_tag(num, 300) + f'<g filter="url(#tsh)">{q}</g>')

    # 4 · call to action: cover still, line, red correction, approved logo; room for the Link sticker
    href4 = CV.still(ep, ep["stills"]["stare"], zoom=1.55, center=(ep["face"][0], ep["face"][1] + 120))
    c, y = lines_block(st["s4"], SEMI, 70, W / 2, 400, BONE)
    rr, _ = CV.text(ISERIF_I, st["s4_red"], 84, W / 2, y + 70, RED, anchor="center", extra=HOOK)
    inner, bbox = c01("st4")["wordmark"]
    logo = place(inner, bbox, W / 2, 1450, width=620)
    slides["4-izle"] = (CV.image(href4, 0.6) + CV.shade("g", [(0, .9), (.35, .65), (.6, .7), (1, .95)]) +
                        f'<g filter="url(#tsh)">{c}{rr}</g>' + logo)

    jobs = []
    for name, body in slides.items():
        p = os.path.join(out, f"{num}-story-{name}.svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg_doc(W, H, CV.SHADOW_DEF + f'<rect width="{W}" height="{H}" fill="{INK}"/>' + body,
                            f"BAXMA DEDİM. {num} story {name}"))
        jobs.append([p, p[:-4] + ".png", W, H, 1])
    import json
    jp = os.path.join(out, "jobs.json")
    with open(jp, "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", os.path.join(HERE, "..", "render.js"), jp], check=True)
    os.remove(jp)
    print("stories:", out)


if __name__ == "__main__":
    for n in sys.argv[1:] or ["01"]:
        build(n)
