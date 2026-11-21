"""Do bodies of the rabbit float free?   python out/r21/judge/floating.py > out/r21/judge/floating.txt

The rabbit on two grids (160^3 and 240^3 on the cube -1.5..1.5, 80 steps). Pieces touch by face, edge or corner.
For every piece that holds 0.5 % of the volume or more: its share, its middle, and its GAP = the shortest distance to
any OTHER piece of that size (specks are not counted as neighbours). Bodies that meet in a point show a gap of one or
two cells that shrinks with the cell; a gap that stays the same on both grids is a body that floats free.
Also: how many big pieces are left when every gap of up to two cells is bridged (the grid is 'closed' by one cell)."""
import os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
S = np.ones((3, 3, 3))
for nm in ('along', 'oneplane', 'sheet.evc005e70k16', 'alongmem.c_wake1', 'alongmem.c_wake2'):
    r = J.get(nm)
    for n in (160, 240):
        xs = np.linspace(-1.5, 1.5, n); cell = xs[1] - xs[0]; m = np.zeros((n, n, n), bool)
        for i0 in range(0, n, 40):                                        # in slabs, to keep the memory down
            X, Y, Z = np.meshgrid(xs[i0:i0 + 40], xs, xs, indexing='ij'); m[i0:i0 + 40] = M.stay(r, X, Y, Z, *M.RABBIT, 80) >= 80
        lab, k = ndimage.label(m, structure=S); sz = np.bincount(lab.ravel()); sz[0] = 0; tot = int(m.sum())
        big = [i for i in np.argsort(sz)[::-1] if sz[i] >= 0.005 * tot]
        lab2, k2 = ndimage.label(ndimage.binary_dilation(m, structure=S), structure=S); sz2 = np.bincount(lab2.ravel()); sz2[0] = 0
        big2 = int((sz2 >= 0.005 * sz2.sum()).sum())
        print('%-20s grid %d^3 (cell %.4f): inside %d, %d pieces, %d of them hold 0.5 %% or more; after bridging gaps of two cells: %d big pieces'
              % (nm, n, cell, tot, k, len(big), big2))
        if len(big) > 1:
            bigmask = np.isin(lab, big)
            for i in big:
                d = ndimage.distance_transform_edt(~(bigmask & (lab != i)), sampling=cell); gap = float(d[lab == i].min())
                idx = np.argwhere(lab == i).mean(0); cm = [xs[0] + cell * t for t in idx]
                print('      piece of %5.1f%%: gap to the nearest other big piece %.3f (%.1f cells), middle at (%.2f, %.2f, %.2f)' % (100.0 * sz[i] / tot, gap, gap / cell, *cm))
        sys.stdout.flush()
