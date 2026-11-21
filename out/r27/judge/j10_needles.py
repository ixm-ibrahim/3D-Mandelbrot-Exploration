"""Judge, check 10: where are the needles of the carried object (way A), and are they real?
For every flat grid point of my table whose column could be tall (small magnification A), find the top of the solid
above it by asking the round frame directly, list the tall columns, and re-ask respace's own function point by
point (no table) on those columns."""
import sys
import numpy as np
import jlib as J
import jcarry as JC
C = JC.C; RAD = JC.RAD

for key in ('c1', 'rabbit'):
    tab = JC.Tab(key); body = JC.BODIES[key]
    sel = tab.ok & (tab.A < 1.2); jj, ii = np.nonzero(sel)
    X = tab.X[sel].astype(float); Y = tab.Y[sel].astype(float); A = tab.A[sel].astype(float); N = tab.N[sel]
    zs = np.linspace(0.0, 1.45, 291); top = np.zeros(X.size)
    for z in zs:                                             # top of the column in the round frame
        r2 = X * X + Y * Y + z * z; ins = r2 < 1.0; cand = np.flatnonzero(~ins & (r2 < 2.3))
        if cand.size:
            v = J.balls(RAD * X[cand], RAD * Y[cand], RAD * z, rounds=14) == 1
            if v.any():
                v[v] = C.own_family(RAD * X[cand][v], RAD * Y[cand][v], np.full(int(v.sum()), RAD * z))
            ins[cand] = v
        top = np.where(ins, z, top)
    h = top / A; x = JC.X0 + ii * JC.STEP; y = JC.Y1 - jj * JC.STEP
    print('== %s: %d flat grid points with magnification below 1.2 (of %d over a body)' % (key, X.size, int(tab.ok.sum())))
    for lim in (0.6, 0.8, 1.0, 1.5, 3.0):
        print('   columns taller than %.1f: %d' % (lim, int((h > lim).sum())))
    tall = np.argsort(-h)[:12]
    al = (1 - np.sqrt(1 - 4 * body.c + 0j)) / 2
    for k in tall:
        print('   flat point (%+.3f, %+.3f): first reaches the middle body after %d steps; way out in its body %.5f; magnification %.4f; top of the column %.2f (round frame %.3f); distance to the main meeting point %.3f'
              % (x[k], y[k], N[k], np.hypot(X[k], Y[k]), A[k], h[k], top[k], abs(complex(x[k], y[k]) - al)))
    # the same columns asked point by point with respace's own function (no table), at the grid point itself and 0.0003 beside it
    hs = np.linspace(0.0, 4.0, 801); res = []
    for k in tall[:6]:
        for dx in (0.0, 3e-4):
            v = C.carried_inside(body, 'A', np.full(hs.size, x[k] + dx), np.full(hs.size, y[k]), hs, nmax=80)
            res.append('%.2f' % (hs[v].max() if v.any() else 0.0))
    print('   point by point (respace\'s function), top of the six tallest columns at the grid point / 0.0003 beside it: ' + ' '.join(res))
    # how much of the flat picture stands under a tall column?
    print('   share of the flat picture under columns taller than 0.6: %.4f of 100 parts' % (100.0 * (h > 0.6).sum() / tab.ok.sum()))
    sys.stdout.flush()
