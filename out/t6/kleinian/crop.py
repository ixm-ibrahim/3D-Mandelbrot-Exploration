"""Side-by-side crops: python out/t6/kleinian/crop.py <out.png> <x0,y0,x1,y1> <zoom> <picture>..."""
import sys
from PIL import Image, ImageDraw
out, box, zoom, paths = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3]), sys.argv[4:]
ims = [Image.open(p).convert('RGB').crop(box) for p in paths]
w, h = int(ims[0].size[0] * zoom), int(ims[0].size[1] * zoom)
sheet = Image.new('RGB', (w * len(ims), h + 16), (20, 22, 28)); d = ImageDraw.Draw(sheet)
for k, (im, p) in enumerate(zip(ims, paths)):
    sheet.paste(im.resize((w, h), Image.LANCZOS if zoom < 1 else Image.NEAREST), (k * w, 16)); d.text((k * w + 4, 2), p.split('/')[-1], fill=(230, 230, 230))
sheet.save(out); print('wrote', out, sheet.size)
