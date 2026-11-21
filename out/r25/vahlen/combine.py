"""Stack the two parts of each sheet: sheet.png (front eye) and sheet-top.png. python out/r25/vahlen/combine.py"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for tag, out in (('a', 'sheet.png'), ('top', 'sheet-top.png')):
    parts = [os.path.join(HERE, 'part-%s-%s.png' % (tag, p)) for p in ('1', '2')]
    if not all(os.path.exists(p) for p in parts):
        print('missing a part for', out); continue
    a, b = (Image.open(p).convert('RGB') for p in parts)
    b = b.crop((0, 50, b.width, b.height))                      # drop the second title line
    im = Image.new('RGB', (max(a.width, b.width), a.height + b.height), (12, 14, 20)); im.paste(a, (0, 0)); im.paste(b, (0, a.height))
    im.save(os.path.join(HERE, out)); print('wrote', out, im.size)
