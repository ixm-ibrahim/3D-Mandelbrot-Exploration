"""One row of pictures per rule: the basilica (c = -1) or any Julia set, rough voxels plus point-by-point cuts.
    python out/r17/blends/look.py <out name> <N> <cx,cy,cz> rule1 rule2 ...
Uses the bench's own iteration and renderer (imports only, nothing in the bench is changed)."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R, bench as B
from scipy import ndimage
turns = R.turns
font = R.S.font


def row(name, c, N, steps=60):
    F = R.get(name); c = tuple(float(v) for v in c)
    kw = dict(c=np.array(c), steps=steps)
    if c == (-1.0, 0.0, 0.0):
        kw['trap'] = B.trap_radius(F)
    t0 = time.time()
    vol = B.volume(F, N, **kw); h = 3.5 / (N - 1)
    lab, n = ndimage.label(vol, structure=B.FULL); sz = np.bincount(lab.ravel())[1:]
    big = 100 * sz.max() / max(vol.sum(), 1) if n else 0.0
    tiles = [turns.render(vol, az=-60, el=22), turns.render(vol, az=-60, el=75), turns.render(vol, az=0, el=0), turns.render(vol, az=-90, el=0)]
    for pl, at, L in (('z', 0.0, 1.75), ('y', 0.0, 1.75), ('x', 0.0, 1.2), ('x', -0.618034, 1.2)):
        i2, d2 = B.cut(F, pl, at, L=L, n=401, **kw); tiles.append(B.cut_img(i2, d2))
    line = 'volume %.2f, biggest piece %.2f %%, %d pieces' % (vol.sum() * h ** 3, big, n)
    print('%-10s c = %s  %s  (%.0f s)' % (name, c, line, time.time() - t0), flush=True)
    return tiles, line


if __name__ == '__main__':
    out, N = sys.argv[1], int(sys.argv[2]); c = [float(v) for v in sys.argv[3].split(',')]
    names = sys.argv[4:]
    COLS = ['Front', 'From above', 'Along the x-axis', 'From the side (along y)', 'Cut z = 0 (flat plane)', 'Cut y = 0 (upright)', 'Cut x = 0', 'Cut x = -0.618']
    W = 250
    sheet = Image.new('RGB', (10 + W * len(COLS), 40 + (W + 26) * len(names)), (12, 14, 20)); dr = ImageDraw.Draw(sheet)
    for k, t in enumerate(COLS):
        dr.text((14 + k * W, 6), t, fill=(200, 205, 215), font=font(14))
    for r, nm in enumerate(names):
        tiles, line = row(nm, c, N)
        y0 = 30 + r * (W + 26)
        dr.text((12, y0), '%s (%s), c = (%g, %g, %g): %s' % (R.RULES[nm][1], nm, c[0], c[1], c[2], line), fill=(235, 235, 235), font=font(15))
        for k, im in enumerate(tiles):
            sheet.paste(Image.fromarray(im).resize((W - 6, W - 6), Image.LANCZOS), (10 + k * W, y0 + 22))
    p = os.path.join(HERE, out); sheet.save(p); print('wrote', p)
