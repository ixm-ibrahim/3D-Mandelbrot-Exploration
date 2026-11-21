"""Contact sheets of the band pictures: python tiles.py <tag> <state> <x0> <x1> <per sheet> [first] [last]"""
import sys, os, glob
from PIL import Image, ImageDraw
tag, state, x0, x1, per = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
files = sorted(glob.glob('raw/%s-%s-[0-9][0-9].png' % (tag, state)))
a = int(sys.argv[6]) if len(sys.argv) > 6 else 0
b = int(sys.argv[7]) if len(sys.argv) > 7 else len(files) - 1
files = files[a:b + 1]
for n in range(0, len(files), per):
    ims = [Image.open(f).convert('RGB') for f in files[n:n + per]]
    ims = [i.crop((x0, 0, min(x1, i.size[0]), i.size[1])) for i in ims]
    w, h = ims[0].size
    sheet = Image.new('RGB', (len(ims) * (w + 6), h + 16), (120, 0, 120))
    d = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        sheet.paste(im, (k * (w + 6), 16)); d.text((k * (w + 6) + 3, 2), os.path.basename(files[n + k]), fill=(255, 255, 255))
    out = 'sheet-%s-%s-%02d.png' % (tag, state, a + n)
    sheet.save(out); print('wrote out/t6/layout/' + out, sheet.size)
