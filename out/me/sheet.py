"""Contact sheet: python out/me/sheet.py <out.png> <cols> <scale> <picture> [<picture> ...]

Each tile is labelled with its file name. Paths are relative to the project root.
"""
import os, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out, cols, scale = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
paths = sys.argv[4:]
ims = [Image.open(os.path.join(ROOT, p)).convert('RGB') for p in paths]
w = int(max(i.size[0] for i in ims) * scale)
h = int(max(i.size[1] for i in ims) * scale)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * (h + 18)), (20, 22, 28))
d = ImageDraw.Draw(sheet)
for k, (im, p) in enumerate(zip(ims, paths)):
    t = im.resize((int(im.size[0] * scale), int(im.size[1] * scale)), Image.LANCZOS)
    x, y = (k % cols) * w, (k // cols) * (h + 18)
    sheet.paste(t, (x, y + 18))
    d.text((x + 4, y + 3), os.path.basename(p), fill=(230, 230, 230))
sheet.save(os.path.join(ROOT, out))
print('wrote', out, sheet.size)
