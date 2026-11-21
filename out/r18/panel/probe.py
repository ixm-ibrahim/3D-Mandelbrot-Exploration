import os, sys, time
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B, rules as R
print('stage1 passers:', [n for n in R.RULES if B.passed_stage1(n)])
print('all rules:', list(R.RULES))
SETS = dict(basilica=(-1, 0), sanmarco=(-0.75, 0), airplane=(-1.754878, 0), cauliflower=(0.25, 0), rabbit=(-0.122561, 0.744862), dendrite=(0, 1), siegel=(-0.390541, -0.586788))
for tag, c in SETS.items():
    for steps in (8, 12, 16, 20, 30, 40, 60):
        L = 2.0; n = 1601
        f = B.flat_set(L=L, n=n, c=(c[0], c[1], 0), steps=steps)
        h = 2 * L / (n - 1)
        d = ndimage.distance_transform_edt(f) * h
        ii = np.argwhere(f)
        ext = (ii.min(0) * h - L, ii.max(0) * h - L)
        lab, k = ndimage.label(f)
        print('%-11s steps %2d  thickest %.4f  area %.4f  x %.2f..%.2f y %.2f..%.2f  pieces %d' % (tag, steps, d.max(), f.sum() * h * h, ext[0][0], ext[1][0], ext[0][1], ext[1][1], k), flush=True)
# timing
for nm in ('oneplane', 'along', 'twoplane', 'lathe', 'away'):
    t = time.time(); v = B.volume(R.get(nm), 161, L=1.7, c=(-0.122561, 0.744862, 0.0), steps=40); print(nm, 'rabbit 161^3 40 steps: %.1f s' % (time.time() - t), 'volume %.3f' % (v.sum() * (3.4 / 160) ** 3), flush=True)
