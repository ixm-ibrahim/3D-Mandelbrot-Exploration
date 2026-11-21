"""Stack the part pictures into sheet.png and sheet-top.png.

    python out/r25/inverse/compose.py
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for tag, out in (('a', 'sheet.png'), ('top', 'sheet-top.png')):
    parts = [Image.open(os.path.join(HERE, 'part%d-%s.png' % (k, tag))) for k in (1, 2) if os.path.exists(os.path.join(HERE, 'part%d-%s.png' % (k, tag)))]
    if not parts:
        continue
    crops = [parts[0]] + [p.crop((0, 56, p.size[0], p.size[1])) for p in parts[1:]]
    W = max(c.size[0] for c in crops); H = sum(c.size[1] for c in crops)
    im = Image.new('RGB', (W, H), (12, 14, 20)); y = 0
    for c in crops:
        im.paste(c, (0, y)); y += c.size[1]
    im.save(os.path.join(HERE, out)); print('wrote', out, im.size)
