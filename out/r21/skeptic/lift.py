"""Skeptic: how fast does a hair's lift off the flat page grow?  python out/r21/skeptic/lift.py
One c in the flat page (inside the flat Mandelbrot set) is lifted by 1e-6 (or the height given on the command line); the height |z| of its orbit is printed
every few steps (rule.step of the library, one orbit). A sound rule: the height dies away or stays tiny."""
import sys
import numpy as np
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

SHOW = (1, 5, 10, 20, 30, 40, 60, 80, 120)
LIFT = float(sys.argv[1]) if len(sys.argv) > 1 else 1e-6


def heights(rule, c, lift=LIFT, steps=120):
    cx, cy, cz = (np.array([t]) for t in (c[0], c[1], lift)); x, y, z = cx.copy(), cy.copy(), cz.copy(); st = tuple(rule.init(1)); out = {}
    for k in range(steps):
        o = rule.step(x, y, z, st, k, cx, cy, cz); st = tuple(o[3]); x, y, z = o[0] + cx, o[1] + cy, o[2] + cz
        if not (x[0] ** 2 + y[0] ** 2 + z[0] ** 2 < 36):
            out[k + 1] = 'left'; break
        if k + 1 in SHOW:
            out[k + 1] = '%.0e' % abs(z[0])
    return ' '.join('%7s' % out.get(k, '') for k in SHOW)


for label, c in (('c = -1 + 0.1i (period-2 disc)', (-1.0, 0.1)), ('c = -0.9 + 0.2i (period-2 disc)', (-0.9, 0.2)), ('c = -0.1 + 0.3i (heart)', (-0.1, 0.3)), ('c = -0.6 + 0.2i (heart, left part)', (-0.6, 0.2)), ('c = rabbit centre', M.RABBIT[:2])):
    print(label, '  height of the orbit at steps', SHOW)
    for nm in ('oneplane', 'along', 'lathe', 'lag05', 'lag25', 'lag40', 'lag60', 'lag70', 'lag75', 'lag90', 'delay', 'first'):
        r = M.bench(nm) if nm in ('oneplane', 'along', 'lathe') else R.BY[nm]
        print('   %-9s %s' % (nm, heights(r, c)))
