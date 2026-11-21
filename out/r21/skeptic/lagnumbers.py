"""Skeptic, job 2: the two library numbers for every lag, and how much of the Mandelbrot solid differs from the lathe's.
    python out/r21/skeptic/lagnumbers.py"""
import sys
import numpy as np
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

SC = {r.name: r for r in M.SCOUT}
rng = np.random.default_rng(31); n = 100000
c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
lat = M.mandel(M.bench('lathe'), c[:, 0], c[:, 1], c[:, 2], 80) >= 80
one = M.mandel(M.bench('oneplane'), c[:, 0], c[:, 1], c[:, 2], 80) >= 80
print('lathe inside %d, oneplane inside %d of %d' % (lat.sum(), one.sum(), n))
for nm in ['lag05', 'lag10', 'lag25', 'lag40', 'lag45', 'lag50', 'lag55', 'lag60', 'lag65', 'lag70', 'lag75', 'lag80', 'lag90', 'lag95', 'delay', 'first']:
    r = R.BY[nm]; f = M.flat_check(r, n=20000); s = M.spun_check(r, n=40000, steps=40); s2 = M.spun_check(r, n=40000, steps=160)
    m = M.mandel(r, c[:, 0], c[:, 1], c[:, 2], 80) >= 80
    print('%-6s flat page differs M %d, basilica %d, rabbit %d, Siegel %d of %d (strays %.0e) | turned: M differs %.2f%% at 40 steps, %.2f%% at 160; basilica %.2f%%, %.2f%% | inside %d; not in the lathe %d; lathe points missing %d'
          % (nm, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], 100 * s['mandel_differ'], 100 * s2['mandel_differ'], 100 * s['basilica_differ'], 100 * s2['basilica_differ'],
             m.sum(), (m & ~lat).sum(), (lat & ~m).sum()))
    sys.stdout.flush()
