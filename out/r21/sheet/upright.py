"""Is the cut along the UPRIGHT sheet (turn 90 degrees) the flat picture? Counts verdicts that differ from the flat orbit.

    python out/r21/sheet/upright.py name ...
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M

n, steps = 20000, 60; rng = np.random.default_rng(21); zero = np.zeros(n)
cr, ci = rng.uniform(-2.1, 0.7, n), rng.uniform(-1.3, 1.3, n); fm = M.flat_stay(cr, ci, cr, ci, steps) >= steps
zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); fb = M.flat_stay(zr, zi, -1.0, 0.0, steps) >= steps
print('%d places in the upright sheet, %d steps; flat-inside: Mandelbrot %d, basilica %d; RULES holds %d rules' % (n, steps, fm.sum(), fb.sum(), len(R.RULES)))
for nm in sys.argv[1:]:
    r = R.get(nm)
    m = M.mandel(r, cr, zero, ci, steps) >= steps; b = M.stay(r, zr, zero, zi, -1.0, 0.0, 0.0, steps) >= steps
    print('%-13s upright cut differs from the flat picture: Mandelbrot %d (of them %d flat-inside but lost, %d flat-outside but kept), basilica %d'
          % (nm, (m != fm).sum(), (fm & ~m).sum(), (~fm & m).sum(), (b != fb).sum()))
