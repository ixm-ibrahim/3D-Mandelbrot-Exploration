import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M
rng = np.random.default_rng(1); n = 200000
v = rng.uniform(-0.7, 0.7, size=(n, 3))
for r in [M.bench('oneplane'), M.SCOUT[2], R.get('c_page'), R.get('prev_page'), R.get('prev_lag50P'), R.get('guessN')]:
    t0 = time.time(); k = M.stay(r, v[:, 0], v[:, 1], v[:, 2], -1.0, 0.0, 0.0, 28); print('%-12s %.2f s for %d orbits, inside %.1f%%' % (r.name, time.time() - t0, n, 100 * (k >= 28).mean()))
