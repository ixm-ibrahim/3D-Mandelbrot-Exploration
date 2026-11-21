"""Rows of rough solids of ONE set for several rules, from several eye positions, at a chosen step count.

    python out/r21/sheet/closeup.py <tag> <set> <steps> name name ... [w=380] [nd=240] [half=1.75] [cx=0 cy=0 cz=0]
<set>: basilica | sanmarco | airplane | rabbit | siegel | dendrite | mandel
One row per rule, one picture per eye position.  -> close-<tag>.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M

SETS = {'basilica': (-1.0, 0.0, 0.0), 'sanmarco': (-0.75, 0.0, 0.0), 'airplane': (-1.754878, 0.0, 0.0), 'rabbit': M.RABBIT, 'siegel': M.SIEGEL, 'dendrite': (0.0, 1.0, 0.0), 'mandel': None}
CAMS = [((0.45, 0.5, 1.0), 'from the front, a little above'), ((0.0, 0.0, 1.0), 'straight at the flat page'), ((0.0, 1.0, 0.02), 'from above (down the y-axis)'), ((1.0, 0.25, 0.25), 'along the x-axis')]

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if '=' not in a]; opt = dict(a.split('=') for a in sys.argv[1:] if '=' in a)
    tag, sname, steps, names = args[0], args[1], int(args[2]), args[3:]
    w = int(opt.get('w', 380)); nd = int(opt.get('nd', 240)); h = int(w * 0.75); c = SETS[sname]
    half = float(opt.get('half', 1.7 if c is None else 1.75))
    centre = (float(opt.get('cx', -0.7 if c is None else 0.0)), float(opt.get('cy', 0.0)), float(opt.get('cz', 0.0)))
    cams = CAMS[:int(opt.get('cams', 4))]
    pad = 10; t0 = time.time(); W = pad + len(cams) * (w + pad); H = 50 + len(names) * (h + 34)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), '%s, %d steps, rough blocks (centre %s, half-width %.2f)' % (sname, steps, centre, half), fill=(240, 240, 245), font=M.font(20))
    for i, nm in enumerate(names):
        r = R.get(nm); y = 50 + i * (h + 34); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(16))
        for j, (cam, cn) in enumerate(cams):
            dep, px = M.solid(r, c, w, h, nd, steps, centre=centre, half_w=half, cam=cam); x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 24)); d.text((x + 6, y + 28), cn, fill=(150, 160, 175), font=M.font(13))
        print(nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'close-%s.png' % tag))
