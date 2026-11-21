"""Crop sheets: python out/r10/engine/crops.py <out.png> <scale> <x0,y0,x1,y1>[;...] <label/name> [<label/name> ...]
One row per crop box, one column per picture, each crop magnified <scale> times (nearest neighbour)."""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
out, scale, boxes, pics = sys.argv[1], int(sys.argv[2]), [tuple(int(v) for v in b.split(',')) for b in sys.argv[3].split(';')], sys.argv[4:]
ims = [Image.open(os.path.join(HERE, p + '.png')).convert('RGB') for p in pics]
cw = max((b[2] - b[0]) for b in boxes) * scale; rows = [(b[3] - b[1]) * scale for b in boxes]
sheet = Image.new('RGB', (len(pics) * (cw + 6), sum(rows) + 6 * len(rows) + 16), (20, 22, 28)); d = ImageDraw.Draw(sheet)
for c, (p, im) in enumerate(zip(pics, ims)):
    d.text((c * (cw + 6) + 3, 2), p[-40:], fill=(230, 230, 230)); y = 16
    for b, rh in zip(boxes, rows):
        sheet.paste(im.crop(b).resize(((b[2] - b[0]) * scale, rh), Image.NEAREST), (c * (cw + 6), y)); y += rh + 6
sheet.save(os.path.join(HERE, out)); print('wrote', out, sheet.size)
