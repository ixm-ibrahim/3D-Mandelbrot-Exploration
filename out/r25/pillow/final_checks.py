"""The checks every rule of best.py must pass, and two honesty numbers (slow leak; lift).

    python out/r25/pillow/final_checks.py [names]
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
import best as B
import measure as ME
M = P.M

names = sys.argv[1].split(',') if len(sys.argv) > 1 else ['tetra', 'skew', 'skew-mirror', 'square']
rng = np.random.default_rng(9)
for nm in names:
    r = B.rule(nm); t0 = time.time()
    f = M.flat_check(r, n=20000, steps=60)
    v = rng.normal(size=(3, 200000)) * rng.uniform(0.05, 1.6, 200000); X, Y, Z, _ = r.step(v[0], v[1], v[2], (), 0, 0, 0, 0)
    fin = bool(np.isfinite(X).all() and np.isfinite(Y).all() and np.isfinite(Z).all()); le = np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (v * v).sum(0)).max()
    sp = np.array([[0, 0, 0], [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [1e-9, 0, 1], [0, 1e-9, -1], [1, 0, 1e-12], [-1, 1e-12, -1e-12]], float).T
    Xs, Ys, Zs, _ = r.step(sp[0], sp[1], sp[2], (), 0, 0, 0, 0); fin2 = bool(np.isfinite(Xs).all() and np.isfinite(Ys).all() and np.isfinite(Zs).all())
    zr, zi = rng.uniform(-1.6, 1.6, 60000), rng.uniform(-1.3, 1.3, 60000)
    lifts = []
    for c in ((-1.0, 0.0, 0.0), M.RABBIT):
        ok = M.flat_stay(zr, zi, c[0], c[1], 300) >= 300; a, b = zr[ok][:6000], zi[ok][:6000]
        lifts.append(float(min((M.stay(r, a, b, np.full(a.size, s * 1e-6), c[0], c[1], c[2], 80) >= 80).mean() for s in (1, -1))))
    vols = []
    for sk in ('m1', 'rab'):
        c = ME.SO.SETS[sk][1]
        vols.append((sk, float(ME.vox(r, c, 40).sum() * ME.HB ** 3), float(ME.vox(r, c, 100).sum() * ME.HB ** 3)))
    print('%-12s flat check (verdicts that differ, of %d): Mandelbrot %d, basilica %d, rabbit %d, Siegel %d; strays off the plane %.1e | all finite %s (special points %s), length squared to %.1e | lift test (c = -1, rabbit; up and down) %.3f %.3f | volume at 40 / 100 steps: %s   [%.0f s]'
          % (nm, f['of'], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page'], fin, fin2, le, lifts[0], lifts[1],
             '; '.join('%s %.3f / %.3f' % v for v in vols), time.time() - t0)); sys.stdout.flush()
