"""Skeptic: is the flat page a slice WITH THICKNESS, or an infinitely thin exact slice?  python out/r21/skeptic/thin.py
M.flat_check tests z = 0 exactly. In floating point z = 0 stays 0 for ever, so a rule whose flat orbits are unstable
to the smallest push off the page still passes. Here every flat test point is lifted by a tiny height eps and the
verdicts are compared with the flat ones. A sound rule: the count falls to (almost) nothing as eps falls."""
import sys, time
import numpy as np
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

SC = {r.name: r for r in M.SCOUT}
rules = [M.bench('oneplane'), M.bench('along'), M.bench('lathe')] + R.LAGS + [SC['delay'], SC['first']]
EPS = (1e-12, 1e-9, 1e-6, 1e-3)
rng = np.random.default_rng(8); n = 20000
cr, ci = rng.uniform(-2.1, 0.7, n), rng.uniform(-1.3, 1.3, n)
zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
for steps in (80, 300):
    print('steps = %d; %d test points each; counts of verdicts that differ from the flat verdict when lifted by eps = %s' % (steps, n, ', '.join('%.0e' % e for e in EPS)))
    fm = M.flat_stay(cr, ci, cr, ci, steps) >= steps
    fj = {nm: M.flat_stay(zr, zi, c[0], c[1], steps) >= steps for nm, c in (('basilica', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2]), ('Siegel', M.SIEGEL[:2]))}
    print('  flat inside: Mandelbrot %d, basilica %d, rabbit %d, Siegel %d' % (fm.sum(), fj['basilica'].sum(), fj['rabbit'].sum(), fj['Siegel'].sum()))
    for r in rules:
        t0 = time.time(); line = '  %-9s' % r.name
        line += ' Mandelbrot ' + ' '.join('%5d' % int(((M.mandel(r, cr, ci, np.full(n, e), steps) >= steps) != fm).sum()) for e in EPS)
        for nm, c in (('basilica', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2]), ('Siegel', M.SIEGEL[:2])):
            line += ' | %s ' % nm + ' '.join('%5d' % int(((M.stay(r, zr, zi, np.full(n, e), c[0], c[1], 0.0, steps) >= steps) != fj[nm]).sum()) for e in EPS)
        print(line + '   %.0f s' % (time.time() - t0)); sys.stdout.flush()
