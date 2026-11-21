"""Skeptic, job 3: the dead zone of M.half.  python out/r21/skeptic/halfzone.py
M.half takes cos and sin of the sheet's turn from the doubled-angle vector by square roots of (1 +- u1) / 2. For a
sheet turned less than about 5e-9 radians from the flat page (or from the upright sheet) 1 - u1 rounds to 0, and
the sheet is read as the flat page itself. Effect: a point lifted by less than about 1e-8 of its distance from the
x-axis is handled by every lag rule exactly as by the one-plane rule, so a test with a very small lift sees nothing."""
import sys
import numpy as np
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

for t in (1e-6, 1e-7, 3e-8, 1e-8, 7e-9, 5e-9, 3e-9, 1e-9, 1e-12):
    co, si = M.half(np.array([np.cos(2 * t)]), np.array([np.sin(2 * t)]))
    co2, si2 = M.half(np.array([np.cos(np.pi - 2 * t)]), np.array([np.sin(np.pi - 2 * t)]))
    print('sheet turned %.0e rad from the flat page: M.half gives the turn %.3e | %.0e short of the upright sheet: M.half gives %.3e short' % (t, np.arctan2(si[0], co[0]), t, np.pi / 2 - np.arctan2(si2[0], co2[0])))
print('the consequence, lag25 at c = (-0.9, 0.2, lift), a point of the period-2 disc of the flat set, 400 steps:')
for lift in (0.0, 1e-13, 1e-11, 1e-9, 1e-8, 1e-7, 1e-6, 1e-4):
    a = int(M.mandel(R.BY['lag25'], np.array([-0.9]), np.array([0.2]), np.array([lift]), 400)[0])
    b = int(M.mandel(M.bench('oneplane'), np.array([-0.9]), np.array([0.2]), np.array([lift]), 400)[0])
    print('   lift %.0e: lag25 stays %3d steps, the one-plane rule stays %3d steps' % (lift, a, b))
