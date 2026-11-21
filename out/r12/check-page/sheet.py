# Contact sheet of pictures:  python out/r12/check-page/sheet.py out.png cols scale file1 file2 ...
import sys, os
from PIL import Image, ImageDraw
out, cols, scale = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
files = sys.argv[4:]
ims = []
for f in files:
    im = Image.open(f).convert('RGB')
    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width, 12], fill=(0, 0, 0))
    d.text((3, 1), os.path.basename(f), fill=(255, 255, 0))
    ims.append(im)
w = max(i.width for i in ims)
rows = [ims[k:k + cols] for k in range(0, len(ims), cols)]
hs = [max(i.height for i in r) for r in rows]
sheet = Image.new('RGB', (w * cols, sum(hs)), (30, 30, 30))
y = 0
for r, h in zip(rows, hs):
    for k, im in enumerate(r):
        sheet.paste(im, (k * w, y))
    y += h
sheet.save(out)
print(out, sheet.size)
