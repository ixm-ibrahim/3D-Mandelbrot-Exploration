"""A check on (W-b) of the briefing. If a rule F has a symmetry g with F(g v) = F(v), every one of its solids has the
symmetry g, for every c, so the plane g(flat plane) holds a true copy of the flat picture (turned or mirrored) for
EVERY c. "Two planes" has the mirror across the plane y = z: its upright plane should show the flat picture stood up,
for the rabbit too. python out/r25/vahlen/wb.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V
M = V.M
rng = np.random.default_rng(2); n = 40000
x, s = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); zero = np.zeros(n)
for name in ('twoplane', 'along'):
    r = M.bench(name)
    for nm, c in (('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('Siegel disc', M.SIEGEL)):
        up = M.stay(r, x, zero, s, c[0], c[1], c[2], 60) >= 60          # the point (x, 0, s) of the upright plane
        fl = M.flat_stay(x, s, c[0], c[1], 60) >= 60                    # the flat point x + i s
        fm = M.flat_stay(x, -s, c[0], c[1], 60) >= 60                   # its mirror image
        print('%-9s %-11s upright plane against the flat picture stood up: %d differ; against its mirror image: %d differ (of %d, %d inside)' % (name, nm, int((up != fl).sum()), int((up != fm).sum()), n, int(fl.sum())))
