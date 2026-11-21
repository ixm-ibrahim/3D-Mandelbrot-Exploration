"""A contact sheet: python out/r7/page/sheet.py out.png cols scale a.png b.png ..."""
import sys
from PIL import Image
out, cols, scale, files = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4:]
ims = [Image.open(f).convert('RGB') for f in files]
ims = [im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS) for im in ims]
w, h = max(i.width for i in ims), max(i.height for i in ims)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w + (cols + 1) * 6, rows * h + (rows + 1) * 6), (60, 60, 60))
for k, im in enumerate(ims):
    sheet.paste(im, (6 + (k % cols) * (w + 6), 6 + (k // cols) * (h + 6)))
sheet.save(out)
print(out, sheet.size)
