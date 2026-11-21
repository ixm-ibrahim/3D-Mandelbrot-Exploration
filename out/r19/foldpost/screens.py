"""Seconds-long screens for the foldpost rules (no iteration): rule checks (length, flat plane, jumps at gaps
1e-4, 1e-5, 1e-6 and 1e-3, both mirrors), the direction screen of round 17 (wraps, share folded, largest stretch)
and this section's own table (which directions go to -x and +x, with what stretch; where the pole goes).
    python out/r19/foldpost/screens.py [rule ...]"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r17', 'blends')); sys.path.insert(0, HERE)
import folds as FO, myrules as M
import screen as SC

names = sys.argv[1:] or list(M.FOLDS)
out = {}
for nm in names:
    fold, lab = M.FOLDS[nm]; F = M.RULES[nm][0]
    print('=== %s: %s' % (nm, lab))
    rng = np.random.default_rng(5)
    A = rng.normal(size=(300000, 3)); A /= np.linalg.norm(A, axis=1)[:, None]
    D = rng.normal(size=(300000, 3)); D /= np.linalg.norm(D, axis=1)[:, None]
    jl = []
    for st in (1e-3, 1e-4, 1e-5, 1e-6):
        B = A + st * D
        fa = np.stack(F(A[:, 0], A[:, 1], A[:, 2]), 1); fb = np.stack(F(B[:, 0], B[:, 1], B[:, 2]), 1)
        jl.append(float(np.linalg.norm(fa - fb, axis=1).max() / st))
    P = rng.normal(size=(100000, 3))
    f1 = np.stack(F(P[:, 0], P[:, 1], P[:, 2]), 1)
    mz = np.abs(np.stack(F(P[:, 0], P[:, 1], -P[:, 2]), 1) * [1, 1, -1] - f1).max()
    my = np.abs(np.stack(F(P[:, 0], -P[:, 1], P[:, 2]), 1) * [1, -1, 1] - f1).max()
    print('  largest (distance between answers) / gap at gaps 1e-3, 1e-4, 1e-5, 1e-6: %.1f %.1f %.1f %.1f (a tear would grow like 1/gap); mirror z %.0e, mirror y %.0e' % (*jl, mz, my))
    s = SC.screen(nm, F)
    p = FO.predict(nm, fold)
    out[nm] = dict(label=lab, jump_ratio=jl, mirror_z=float(mz), mirror_y=float(my), screen=s, predict=p)
    json.dump(out, open(os.path.join(HERE, 'screens.json'), 'w'), indent=1, default=float)
