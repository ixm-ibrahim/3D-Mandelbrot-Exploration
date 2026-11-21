"""python out/r21/alongmem/leak.py name [name ...]
Volume of six Julia sets on a 97^3 grid at 30, 80, 200 and 500 steps (a slow leak or dust shows as a falling volume),
and the pieces of the solid at 80 steps on a 161^3 grid: how many pieces, the share of the biggest, and the share of
the solid that sits in pieces not joined to the biggest one."""
import os, sys
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M


def rule(name):
    return M.bench(name[6:]) if name.startswith('bench:') else R.get(name)


def stay_grid(r, c, N, steps, L=1.75):
    a = np.linspace(-L, L, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
    return M.stay(r, X, Y, Z, c[0], c[1], c[2], steps)


if __name__ == '__main__':
    for nm in sys.argv[1:]:
        r = rule(nm)
        for sn, c in M.JSETS:
            n = stay_grid(r, c, 97, 500); vols = [float((n >= s).mean() * 3.5 ** 3) for s in (30, 80, 200, 500)]
            g = stay_grid(r, c, 161, 80) >= 80
            lab, k = ndimage.label(g, structure=np.ones((3, 3, 3)))                 # blocks that touch even by a corner count as joined
            cnt = np.sort(np.bincount(lab.ravel())[1:])[::-1] if k else np.array([0])
            tot = max(int(cnt.sum()), 1)
            print('%-12s %-22s volume at 30/80/200/500 steps: %.3f %.3f %.3f %.3f | at 80 steps, 161^3: %d pieces, biggest %.1f%%, next %s%%' % (
                nm, sn, *vols, k, 100 * cnt[0] / tot, ' '.join('%.1f' % (100 * t / tot) for t in cnt[1:5])))
            sys.stdout.flush()
