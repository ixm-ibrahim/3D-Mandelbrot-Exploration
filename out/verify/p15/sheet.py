import os, sys
from PIL import Image, ImageDraw
import numpy as np
OUT = 'out/verify/p15'
APS = ['mercator', 'lathe', 'bulb', 'classic', 'split']
NEG = ['-1', '-2', '-3', '-4', '-8', '-2.5']
POS = ['0', '0.5', '1', '1.5']
def tag(n): return n.replace('-', 'm').replace('.', 'p')
def stats(im):
    a = np.asarray(im.convert('RGB')).astype(int)
    h, w, _ = a.shape
    # background: the colour of a pixel in an empty stage corner area
    core = a[70:h-110, 90:w-150]
    bg = np.median(core.reshape(-1, 3), axis=0)
    diff = (np.abs(a - bg).sum(axis=2) > 40)
    c = diff[70:h-110, 90:w-150]
    frac = c.mean()
    ys, xs = np.nonzero(c)
    edge = {
      'L': diff[120:h-120, 0:5].mean(), 'T': diff[0:5, 120:w-140].mean(),
      'B': diff[h-5:h, 360:w-200].mean(), 'R': diff[200:h-260, w-5:w].mean(),
    }
    return frac, edge, tuple(int(x) for x in bg)
rows = []
for kind in ('2d', '3d'):
    for mode in ('m', 'j'):
        for name, ns in (('neg', NEG), ('pos', POS)):
            cw, ch = 300, 244
            sheet = Image.new('RGB', (cw * len(ns) + 70, ch * len(APS) + 22), (30, 30, 30))
            dr = ImageDraw.Draw(sheet)
            for j, n in enumerate(ns):
                dr.text((70 + j * cw + 120, 4), 'n = ' + n, fill=(255, 255, 255))
            for i, ap in enumerate(APS):
                dr.text((4, 22 + i * ch + 100), ap, fill=(255, 255, 255))
                for j, n in enumerate(ns):
                    p = '%s/%s-%s-%s-n%s.png' % (OUT, kind, ap, mode, tag(n))
                    if not os.path.exists(p):
                        continue
                    im = Image.open(p)
                    frac, edge, bg = stats(im)
                    rows.append((kind, mode, ap, n, round(float(frac), 4), {k: round(float(v), 2) for k, v in edge.items()}, im.size))
                    sheet.paste(im.resize((cw - 4, ch - 4)), (70 + j * cw, 22 + i * ch))
            sheet.save('%s/sheet-%s-%s-%s.png' % (OUT, kind, mode, name))
with open(OUT + '/stats.txt', 'w') as f:
    for r in rows:
        f.write(repr(r) + '\n')
print(len(rows), 'pictures')
for r in rows:
    print(r[0], r[1], r[2].ljust(8), r[3].rjust(5), 'fill %.3f' % r[4], r[5])
