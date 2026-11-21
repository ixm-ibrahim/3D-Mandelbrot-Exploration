"""Where does "the point and the point before" lose the orbit of 0?  python out/r21/span/rest.py -> rest.txt
The c whose verdict differs from the swept flat set are sorted by where gamma lies in the flat set:
in the heart (orbit comes to REST on one point) or elsewhere (orbit keeps going round two or more points)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M
out = []
rng = np.random.default_rng(33); n = 120000; steps = 60
c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3)); cx, cy, cz = c[:, 0], c[:, 1], c[:, 2]
for nm, nfun in (('prev_lathe', R.n_lathe), ('prev_page', R.n_page), ('prev_keep', R.n_page), ('prev_axis', R.n_page), ('c_page', R.n_page)):
    nn = nfun(cx, cy, cz); a = R.real_axis(*nn)
    g1 = a[0] * cx + a[1] * cy + a[2] * cz; g2 = np.sqrt(np.maximum(cx * cx + cy * cy + cz * cz - g1 * g1, 0.0))
    rule = M.mandel(R.get(nm), cx, cy, cz, steps) >= steps; flat = M.flat_stay(g1, g2, g1, g2, steps) >= steps
    g = g1 + 1j * g2; heart = np.abs(1 - np.sqrt(1 - 4 * g)) < 1            # gamma in the main heart-shaped body: the flat orbit comes to rest
    off = np.abs(cz) > 1e-3
    out.append('%-10s of %d c: swept flat set inside %d (heart %d, elsewhere %d). The rule throws out %d of the heart (%.1f%%) and %d of the rest (%.1f%%); lets in %d that the sweep has out'
               % (nm, n, flat.sum(), (flat & heart).sum(), (flat & ~heart).sum(), (flat & heart & ~rule).sum(), 100 * (flat & heart & ~rule).sum() / max((flat & heart).sum(), 1),
                  (flat & ~heart & ~rule).sum(), 100 * (flat & ~heart & ~rule).sum() / max((flat & ~heart).sum(), 1), (rule & ~flat).sum()))
    print(out[-1])
# the same at more steps: does the bite grow?
for st in (30, 120, 240):
    nn = R.n_page(cx[:40000], cy[:40000], cz[:40000]); a = R.real_axis(*nn)
    g1 = a[0] * cx[:40000] + a[1] * cy[:40000] + a[2] * cz[:40000]; g2 = np.sqrt(np.maximum((c[:40000] ** 2).sum(1) - g1 * g1, 0.0))
    rule = M.mandel(R.get('prev_keep'), cx[:40000], cy[:40000], cz[:40000], st) >= st; flat = M.flat_stay(g1, g2, g1, g2, st) >= st
    out.append('prev_keep at %d steps: swept flat set inside %d, rule inside %d' % (st, flat.sum(), rule.sum())); print(out[-1])
open(os.path.join(HERE, 'rest.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
