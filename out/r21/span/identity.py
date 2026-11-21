"""Three small identities, by numbers.  python out/r21/span/identity.py -> identity.txt
a. The square inside a plane (normal n) through the point = the lathe's square pressed into the plane and stretched back
   to full length: (L(v) + |v|^2 n_x n) / sqrt(1 - n_x^2),  L(v) = (x^2 - y^2 - z^2, 2xy, 2xz).
b. For c on the x-axis, "the plane of the point and c" is the lathe: verdicts compared with the bench lathe.
c. The one-plane rule about a plane that holds the point = the square inside that plane.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M
out = []
rng = np.random.default_rng(8); n = 100000
v = rng.normal(size=(3, n)); w = rng.normal(size=(3, n))
nn = R.n_made(*v, *w, lambda: R.n_page(*v))[:3]; a = R.real_axis(*nn)
S = np.stack(R.sq_in(*v, a[0], a[1], a[2])); r2 = (v * v).sum(0)
L = np.stack([v[0] ** 2 - v[1] ** 2 - v[2] ** 2, 2 * v[0] * v[1], 2 * v[0] * v[2]])
T = (L + r2 * nn[0] * np.stack(nn)) / np.sqrt(1 - nn[0] ** 2)
out.append('a. square inside a random plane through the point vs the lathe square pressed into the plane and stretched: largest difference %.1e of |v|^2 (%d points)' % ((np.linalg.norm(S - T, axis=0) / r2).max(), n))
Pn = np.stack(R.P_about(*v, *nn))
out.append('c. one-plane rule about a plane that holds the point vs the square inside the plane: largest difference %.1e of |v|^2' % ((np.linalg.norm(S - Pn, axis=0) / r2).max()))
out.append('   length of the square over |v|^2: from %.12f to %.12f' % ((np.linalg.norm(S, axis=0) / r2).min(), (np.linalg.norm(S, axis=0) / r2).max()))
p = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(60000, 3)); lathe = M.bench('lathe')
for cc in ((-1.0, 0.0, 0.0), (-0.75, 0.0, 0.0), (-1.754878, 0.0, 0.0)):
    A = M.stay(lathe, p[:, 0], p[:, 1], p[:, 2], *cc, 60) >= 60
    for nm in ('c_lathe', 'c_page', 'prev_lathe', 'prev_page'):
        B = M.stay(R.get(nm), p[:, 0], p[:, 1], p[:, 2], *cc, 60) >= 60
        out.append('b. c = %.4f on the x-axis: %-10s vs the bench lathe: %d verdicts differ of %d (lathe inside %d)' % (cc[0], nm, (A != B).sum(), A.size, A.sum()))
for s in out:
    print(s)
open(os.path.join(HERE, 'identity.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
