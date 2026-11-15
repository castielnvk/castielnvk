# python3 compose_preview.py <stills_dir> <out_dir>
import sys
from PIL import Image, ImageDraw, ImageFont
S, O = sys.argv[1], sys.argv[2]
bg = Image.open('studio_bg.jpg').convert('RGBA')
F = ImageFont.truetype('fonts/Montserrat_800ExtraBold.ttf', 44)
names = {'A': 'A — Firuzə dalğa', 'B': 'B — Xalça haşiyəsi', 'C': 'C — Kapsul', 'D': 'D — Bayraq xətti'}
for v in 'ABCD':
    full = Image.alpha_composite(bg, Image.open(f'{S}/{v}_0.png'))
    strips = [Image.alpha_composite(bg, Image.open(f'{S}/{v}_{i}.png')).crop((0, 880, 1920, 1080)) for i in (1, 2, 3)]
    sheet = Image.new('RGB', (1920, 90 + 1080 + 3 * 212), '#111')
    ImageDraw.Draw(sheet).text((40, 22), names[v], font=F, fill='white')
    sheet.paste(full.convert('RGB'), (0, 90)); y = 90 + 1080 + 12
    for s in strips: sheet.paste(s.convert('RGB'), (0, y)); y += 212
    sheet.resize((1280, sheet.height * 1280 // 1920), Image.LANCZOS).save(f'{O}/Variant_{v}.jpg', quality=90)
