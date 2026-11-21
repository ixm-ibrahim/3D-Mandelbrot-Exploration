import sys
from PIL import Image, ImageDraw
view = sys.argv[1]; ns = [int(x) for x in sys.argv[2].split(',')]; ps = [1,2,3,4]
prefix = sys.argv[3] if len(sys.argv) > 3 else 'g'
tiles = {}
for n in ns:
    for p in ps:
        im = Image.open('out/verify/p10/%s_%s_n%d_p%d.png' % (prefix, view, n, p)).convert('RGB')
        w, h = im.size
        s = min(w, h); im = im.crop(((w - s)//2, (h - s)//2, (w + s)//2, (h + s)//2)).resize((440, 440), Image.LANCZOS)
        d = ImageDraw.Draw(im); d.rectangle([0,0,110,18], fill=(0,0,0)); d.text((4,3), 'n=%d p=%d' % (n, p), fill=(255,255,0))
        tiles[(n,p)] = im
sheet = Image.new('RGB', (440*len(ps), 440*len(ns)))
for i, n in enumerate(ns):
    for j, p in enumerate(ps):
        sheet.paste(tiles[(n,p)], (440*j, 440*i))
out = 'out/verify/p10/sheet_%s_%s_n%s.png' % (prefix, view, '-'.join(map(str, ns)))
sheet.save(out); print(out, sheet.size, im.size)
