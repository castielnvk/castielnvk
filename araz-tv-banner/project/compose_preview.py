# python3 compose_preview.py <stills_dir> <out_dir>  -> 16:9 previews (1920x1080)
import sys
from PIL import Image
S, O = sys.argv[1], sys.argv[2]
bg = Image.open('studio_bg.jpg').convert('RGBA')
for v in 'ABCD':
    frames = [Image.alpha_composite(bg, Image.open(f'{S}/{v}_{i}.png')).convert('RGB') for i in range(4)]
    frames[0].save(f'{O}/Variant_{v}.jpg', quality=92)
    grid = Image.new('RGB', (1920, 1080), '#000')
    for i, f in enumerate(frames):
        grid.paste(f.resize((958, 538), Image.LANCZOS), ((i % 2) * 962, (i // 2) * 542))
    grid.save(f'{O}/Variant_{v}_4yazi.jpg', quality=92)
