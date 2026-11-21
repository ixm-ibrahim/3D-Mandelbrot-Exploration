"""python out/r21/alongmem/kick.py
How much does a sheet that does NOT hold c cost? The one-plane rule about a FIXED sheet turned by tau from the flat
page (which holds c), for the rabbit, the Siegel disc and the basilica: volume of the Julia solid at 80 steps (97^3
grid) and the share of the flat-page inside points that are still inside (20,000 flat-page points, 60 steps).
For the basilica c lies on the x-axis, in every sheet: nothing should change but the direction."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T
M = T.M


def about(tau):
    a = np.radians(2 * tau)
    return M.Rule('tau%g' % tau, '', lambda x, y, z, st, k, cx, cy, cz: (*M.sq_about(x, y, z, *st), st), init=lambda n: (np.full(n, np.cos(a)), np.full(n, np.sin(a))))


if __name__ == '__main__':
    rng = np.random.default_rng(3); n = 20000; zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    for sn, c in (('rabbit', M.RABBIT), ('Siegel disc', M.SIEGEL), ('basilica', (-1.0, 0.0, 0.0))):
        fl = M.flat_stay(zr, zi, c[0], c[1], 60) >= 60
        for tau in (0, 1, 2, 5, 10, 15, 20, 30, 45, 90):
            r = about(tau); v = T.volume(r, c, steps=80)
            keep = (M.stay(r, zr, zi, np.zeros(n), c[0], c[1], 0.0, 60) >= 60)[fl].mean()
            print('%-12s sheet turned %4g degrees from the flat page: volume %.3f, flat-page inside points kept %.1f%%' % (sn, tau, v, 100 * keep)); sys.stdout.flush()
