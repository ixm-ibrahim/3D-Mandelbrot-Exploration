"""Judge, round 25: two small probes.

    python out/r25/judge/probe.py tri3     round 24's two-triangle pattern with the power 3 (nobody built it): flat check against z^3 + c
    python out/r25/judge/probe.py zipfix   the zip rule with its NaN on the upright axis removed: is the c = -1 solid there after all?
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jl, measure as MS
M = jl.M


def tri3():
    r = MS.get('tri3'); rng = np.random.default_rng(2511); n = 30000; zero = np.zeros(n); out = []
    cr, ci = rng.uniform(-1.3, 1.3, n), rng.uniform(-1.6, 1.6, n)
    a = M.mandel(r, cr, ci, zero, 80) >= 80; b = jl.flat_true(cr, ci, cr, ci, 80, 3) >= 80; out.append(('M', int((a != b).sum()), int(b.sum())))
    zr, zi = rng.uniform(-1.5, 1.5, n), rng.uniform(-1.5, 1.5, n)
    for nm, c in (('c=i', jl.SETS['ci']), ('c3b', jl.SETS['c3b']), ('c=0.3', (0.3, 0, 0)), ('c=-0.2+1.08i', (-0.2, 1.08, 0))):
        a = M.stay(r, zr, zi, zero, c[0], c[1], 0.0, 80) >= 80; b = jl.flat_true(zr, zi, c[0], c[1], 80, 3) >= 80; out.append((nm, int((a != b).sum()), int(b.sum())))
    print('tri3 flat check against z^3 + c, differ / inside of %d: %s' % (n, '  '.join('%s %d/%d' % t for t in out)))
    X, Y, Z, _ = r.step(zr, zi, zero, (), 0, zero, zero, zero); w = (zr + 1j * zi) ** 3
    print('one step on the flat plane: worst error %.1e, off the plane %.1e, not finite %d' % (np.nanmax(np.hypot(X - w.real, Y - w.imag) / (1 + np.abs(w))), np.nanmax(np.abs(Z)), int((~np.isfinite(X)).sum())))
    # lifted flat inside points
    for nm in ('ci', 'c3b'):
        c = jl.SETS[nm]; ins = jl.flat_true(zr, zi, c[0], c[1], 200, 3) >= 200
        print('tri3 %s: flat inside points lifted by 1e-6 / 1e-3 / 0.02 that stay 80 steps: %s' % (nm, ' / '.join('%.3f' % (M.stay(r, zr[ins], zi[ins], np.full(ins.sum(), h), c[0], c[1], 0.0, 80) >= 80).mean() for h in (1e-6, 1e-3, 0.02))))


def zipfix():
    rng = np.random.default_rng(3); n = 300000; v = rng.uniform([-1.8, -1.5, -1.5], [1.8, 1.5, 1.5], size=(n, 3))
    for nm in ('zip1', 'zip1fix', 'oneplane'):
        r = MS.get(nm)
        for sn in ('c1', 'rabbit'):
            c = jl.SETS[sn]; cnt = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 150)
            print('%-9s %-7s share of the box still there after 20 / 40 / 60 / 150 steps: %s' % (nm, sn, ' / '.join('%.4f' % (cnt >= s).mean() for s in (20, 40, 60, 150))))


if __name__ == '__main__':
    {'tri3': tri3, 'zipfix': zipfix}[sys.argv[1]]()
