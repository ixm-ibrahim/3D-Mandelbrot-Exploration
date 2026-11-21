"""Contact sheets: python sheet.py out.png cols scale a.png b.png ..."""
import sys
from PIL import Image
out, cols, scale = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
ims = [Image.open(p).convert("RGB") for p in sys.argv[4:]]
ims = [im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS) for im in ims]
w = max(im.width for im in ims); h = max(im.height for im in ims)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (255, 0, 255))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
sheet.save(out)
print(out, sheet.size)
