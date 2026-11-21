"""Contact sheets: python out/lab2/axisbulb/sheet.py <folder> <out.png> name1 name2 ...   (top row default colours, bottom row plain-)"""
import sys, os
from PIL import Image, ImageDraw
folder, out, names = sys.argv[1], sys.argv[2], sys.argv[3:]
W, H = 432, 352
sheet = Image.new('RGB', (W * len(names), H * 2), (20, 20, 20))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    for j, pre in enumerate(['', 'plain-']):
        p = os.path.join(folder, pre + n + '.png')
        if os.path.exists(p):
            sheet.paste(Image.open(p).convert('RGB').resize((W, H), Image.LANCZOS), (i * W, j * H))
        d.text((i * W + 6, j * H + H - 14), pre + n, fill=(255, 255, 255))
sheet.save(out)
print('wrote', out)
