"""python out/r21/frame/extra.py <tag> name1 name2 ...   The basilica (c = -1) at 60 steps: seen from a second eye position
(almost along the x-axis), from above the pole of the flat page, and one close-up of the top of the main body."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
import myrules as R
np.seterr(all='ignore')
tag = sys.argv[1]; names = sys.argv[2:]
rs = [M.bench(n[1:]) if n.startswith('@') else R.BY[n] for n in names]
C = (-1.0, 0.0, 0.0); w, h, nd, steps = 300, 225, 170, 60
VIEWS = [('eye almost on the x-axis (1, 0.3, 0.45)', dict(cam=(1.0, 0.3, 0.45))),
         ('eye above the flat page, a little to the side (0.25, 0.3, 1)', dict(cam=(0.25, 0.3, 1.0))),
         ('close-up: the main body, top right, half-width 0.6', dict(cam=(0.45, 0.5, 1.0), centre=(0.25, 0.35, 0.35), half_w=0.6))]
pad = 10; W = pad + len(VIEWS) * (w + pad); H = 50 + len(rs) * (h + 46)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'The basilica, c = -1, rough blocks at %d steps: other eye positions and a close-up' % steps, fill=(240, 240, 245), font=M.font(20))
t0 = time.time()
for i, r in enumerate(rs):
    y = 50 + i * (h + 46); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(15))
    for j, (lab, kw) in enumerate(VIEWS):
        dep, px = M.solid(r, C, w, h, nd, steps, **kw); x = pad + j * (w + pad)
        d.text((x, y + 20), lab, fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 36))
    print(r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
p = os.path.join(HERE, 'extra-%s.png' % tag); im.save(p); print('wrote', p)
