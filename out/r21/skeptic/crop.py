"""Cut a tall sheet into bands so that each can be looked at in full detail.
    python out/r21/skeptic/crop.py <png> <top> <row height> <rows per band>"""
import sys
from PIL import Image
p, top, rh, per = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
im = Image.open(p); W, H = im.size; k = 0; y = top
while y < H - 5:
    b = im.crop((0, y, W, min(H, y + rh * per))); out = p[:-4] + '.part%d.png' % k; b.save(out); print(out, b.size); k += 1; y += rh * per
