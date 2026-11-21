"""Round 28, the fixer: can the test of mk/side.py fail at all? The side spindle made 1.1, 1.2, 1.5 and 2 times as wide.

  python out/r28/fix/mk/side_wider.py     -> out/r28/fix/logs/side-wider.txt      (no browser)
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(FIX), 'truth', 'mk'))
import tkit as T
import side

side.LOG = os.path.join(FIX, 'logs', 'side-wider.txt'); side.out[:] = []
rng = np.random.default_rng(1)
for gname, rho, p in (('square', 0.5, 150.0), ('hex', 0.5, 150.0), ('line', 0.5, 150.0), ('square', 0.5, 200.0), ('hex', 0.4, 250.0), ('square', 0.25, 400.0), ('line', 0.25, 400.0)):
    grid = T.Grid(gname); top = T.top_of(p); h = T.hulls(top, rho)
    reps, info = T.build(grid, top, rho, 4e-5 if gname == 'line' else 2e-3)
    B = np.concatenate([np.column_stack([reps[:, 0] + lx, reps[:, 1] + ly, reps[:, 2], reps[:, 3]]) for lx, ly in grid.upto(2.5)])
    c2 = max(0.25 - rho * rho, 0.0); w = side.side_w(gname, top, rho, h['HB'])
    for f in (1.0, 1.1, 1.2, 1.5, 2.0):
        deep, n_in, a, R = side.reach_in(B, top, c2, f * w)
        P = side.points_in(rng, 20000, top, c2, f * w)
        st = T.recipe(P[:, 0], P[:, 1], P[:, 2], grid, top, rho, 300)
        side.say('%-6s second sphere %.3f, size %.0f (top - HB %.4f), w %.4f x %.1f: the deepest listed ball reaches %+.5f into the spindle (%d balls in), the recipe calls %d of 20000 points of it INSIDE'
                 % (gname, rho, p, top - h['HB'], w, f, deep, n_in, int((st == 1).sum())))
