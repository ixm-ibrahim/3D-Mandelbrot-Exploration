# Side by side crops, enlarged: python out/t9/flat/crops.py <out.png> <zoom> <x0> <y0> <w> <h> <picA> <picB> [...]
import sys
from PIL import Image, ImageDraw
out, zoom, x0, y0, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
pics = sys.argv[7:]
sheet = Image.new('RGB', (len(pics) * (w * zoom + 6), h * zoom + 18), (20, 22, 28))
d = ImageDraw.Draw(sheet)
for k, p in enumerate(pics):
    im = Image.open(p).convert('RGB').crop((x0, y0, x0 + w, y0 + h)).resize((w * zoom, h * zoom), Image.NEAREST)
    sheet.paste(im, (k * (w * zoom + 6), 18))
    d.text((k * (w * zoom + 6) + 4, 3), p[-40:], fill=(230, 230, 230))
sheet.save(out)
print('wrote', out, sheet.size)
