"""python out/r21/alongmem/pieces.py name [N=201] [steps=80] [set=rabbit]
The pieces of one Julia solid on an N^3 grid (blocks touching even by a corner count as joined): for each piece
that holds more than 0.3 % of the solid its share, its middle, its box, and the gap (in blocks and in units) between
it and the biggest piece. A gap of several blocks that does not shrink when N grows is a body that floats free."""
import os, sys
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M

if __name__ == '__main__':
    nm = sys.argv[1]; opt = dict(a.split('=') for a in sys.argv[2:] if '=' in a)
    N = int(opt.get('N', 201)); steps = int(opt.get('steps', 80)); sn = opt.get('set', 'rabbit')
    c = {'rabbit': M.RABBIT, 'basilica': (-1.0, 0.0, 0.0), 'siegel': M.SIEGEL, 'sanmarco': (-0.75, 0.0, 0.0)}[sn]
    r = M.bench(nm[6:]) if nm.startswith('bench:') else R.get(nm); L = 1.75
    a = np.linspace(-L, L, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij'); h = a[1] - a[0]
    g = M.stay(r, X, Y, Z, c[0], c[1], c[2], steps) >= steps
    lab, k = ndimage.label(g, structure=np.ones((3, 3, 3))); cnt = np.bincount(lab.ravel()); cnt[0] = 0
    order = np.argsort(cnt)[::-1]; big = order[0]; tot = cnt.sum()
    dist = ndimage.distance_transform_edt(lab != big)             # distance (in blocks) of every block to the biggest piece
    print('%s, %s, N = %d, %d steps: volume %.3f, %d pieces' % (nm, sn, N, steps, g.mean() * (2 * L) ** 3, k))
    for i in order[:12]:
        if cnt[i] < 0.003 * tot:
            break
        m = lab == i; idx = np.argwhere(m); lo, hi = a[idx.min(0)], a[idx.max(0)]; mid = a[np.round(idx.mean(0)).astype(int)]
        gap = float(dist[m].min()) if i != big else 0.0
        print('  share %5.1f%%  middle (%.2f, %.2f, %.2f)  box x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f  gap to the biggest piece %.1f blocks = %.3f' % (
            100 * cnt[i] / tot, *mid, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], gap, gap * h))
