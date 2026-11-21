"""One piece? Voxels, 257 a side, no gap allowed (26 neighbours) and with a one-voxel gap allowed (closing by one voxel).
python pieces.py <set> <steps,steps,...> <rule> ..."""
import os, sys, json
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R, bench as B
SETS = dict(rabbit=((-0.122561, 0.744862, 0.0), 1.4), dendrite=((0.0, 1.0, 0.0), 1.5), siegel=((-0.390541, -0.586788, 0.0), 1.45), basilica=((-1.0, 0.0, 0.0), 1.7), bas_yz=((-1.0, 0.05, 0.03), 1.7), rab_up=((-0.122561, 0.744862, 0.015), 1.4), bas_zy=((-1.0, 0.03, 0.05), 1.7), sm_yz=((-0.75, 0.01, 0.02), 1.6), sanmarco=((-0.75, 0.0, 0.0), 1.6))
tag = sys.argv[1]; steps = [int(s) for s in sys.argv[2].split(',')]; c, L = SETS[tag]; FULL = np.ones((3, 3, 3), bool)
p = os.path.join(HERE, 'pieces.json'); out = json.load(open(p)) if os.path.exists(p) else {}
for nm in sys.argv[3:]:
    F = R.get(nm); cells = []
    for s in steps:
        v = B.volume(F, 257, L=L, c=c, steps=s)
        lab, k = ndimage.label(v, FULL); sz = np.bincount(lab.ravel())[1:]
        v2 = ndimage.binary_dilation(v, FULL); lab2, k2 = ndimage.label(v2, FULL); sz2 = np.bincount(lab2[v])[1:]
        vol = float(v.mean() * (2 * L) ** 3); th = float(ndimage.distance_transform_edt(v).max() * 2 * L / 256)
        cells.append(dict(steps=s, volume=vol, pieces=int(k), biggest_pct=float(100 * sz.max() / max(v.sum(), 1)) if k else 0.0, biggest_gap_pct=float(100 * sz2.max() / max(v.sum(), 1)) if k else 0.0, thickest=th))
    out['%s:%s' % (nm, tag)] = cells
    print('%-9s %-8s ' % (nm, tag) + ' | '.join('%d steps: vol %.3f, thickest %.3f, %d pieces, biggest %.1f %% (%.2f %% with a one-voxel gap)' % (q['steps'], q['volume'], q['thickest'], q['pieces'], q['biggest_pct'], q['biggest_gap_pct']) for q in cells), flush=True)
    json.dump(out, open(p, 'w'), indent=1)
