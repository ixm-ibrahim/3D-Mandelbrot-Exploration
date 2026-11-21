"""Crop and enlarge parts of screenshots, optionally side by side.
usage: python out/fix/shaders/crop.py out.png x0,y0,x1,y1 scale a.png [b.png ...]"""
import sys
from PIL import Image
out, box, scale = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], int(sys.argv[3])
ims = []
for p in sys.argv[4:]:
    im = Image.open(p).convert('RGB').crop(box)
    ims.append(im.resize((im.width * scale, im.height * scale), Image.NEAREST))
W = sum(i.width for i in ims) + 6 * (len(ims) - 1)
sheet = Image.new('RGB', (W, ims[0].height), (255, 0, 255))
x = 0
for i in ims:
    sheet.paste(i, (x, 0)); x += i.width + 6
sheet.save(out)
print(out, sheet.size)
