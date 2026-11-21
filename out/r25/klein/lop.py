"""Round 25, section klein: lopsidedness as a number. The true basilica (c = -1) is the same left and right.
For each rule: of the points of the solid, the share whose mirror image (x -> -x) is NOT in the solid.

    python out/r25/klein/lop.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M
import tree as T
import repair as R

rng = np.random.default_rng(11); n = 400000
q = rng.uniform(-1, 1, size=(3, n)) * np.array([[1.8], [1.3], [1.3]])
rows = [('one plane', M.bench('oneplane'), (-1.0, 0.0, 0.0), 30), ('two planes', M.bench('twoplane'), (-1.0, 0.0, 0.0), 30),
        ('the paper\'s rule', R.RULES['paper'](), (-1.0, 0.0, 0.0), 30), ('the paper\'s rule re-spaced', R.RULES['kfix'](), (-1.0, 0.0, 0.0), 30),
        ('pearl tree, Gaussian', T.tree('gauss'), T.ZERO, 14), ('pearl tree, Eisenstein', T.tree('eisen'), T.ZERO, 14)]
for nm, r, c, steps in rows:
    a = M.stay(r, q[0], q[1], q[2], *c, steps) >= steps; b = M.stay(r, -q[0], q[1], q[2], *c, steps) >= steps
    print('%-28s inside %.4f of the box; lopsided left-right: %.1f%% of the solid has no mirror partner' % (nm, a.mean(), 100.0 * (a & ~b).sum() / max(a.sum(), 1)))
# the flat cut only (z = 0)
for nm, r, c, steps in rows:
    a = M.stay(r, q[0], q[1], 0 * q[2], *c, steps) >= steps; b = M.stay(r, -q[0], q[1], 0 * q[2], *c, steps) >= steps
    print('flat cut  %-28s lopsided: %.1f%%' % (nm, 100.0 * (a & ~b).sum() / max(a.sum(), 1)))
