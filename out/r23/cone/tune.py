"""Tune the weld so that it has no fold: on the meridian through a critical direction the two turn-rounds
(the image stops going sideways / stops going up) must fall on the same point.  python out/r23/cone/tune.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import conelib as L


def gap(bend, mua, mub, kind, muc=L.MU60):
    mu = np.linspace(1e-4, muc - 1e-4, 200001); la = 2 * np.arctan(np.exp(mu)) - np.pi / 2; h = 1e-6

    def G(lam):
        return L.weld_dir(np.cos(la) * np.cos(lam), np.cos(la) * np.sin(lam), np.sin(la), 0.0, mua, mub, bend, kind, muc)
    g0 = G(0.0); gp = G(h)
    side = gp[1] / h                                    # sideways speed of the image as the direction moves round
    up = np.gradient(np.arctan2(g0[2], g0[0]), mu)       # upward speed of the image as the direction moves up
    i1 = np.nonzero(np.sign(side[1:]) != np.sign(side[:-1]))[0]; i2 = np.nonzero(np.sign(up[1:]) != np.sign(up[:-1]))[0]
    if len(i1) == 0 or len(i2) == 0:
        return None
    return mu[i1[0]] - mu[i2[0]], mu[i1[0]], np.degrees(la[i1[0]]), np.degrees(np.arctan2(g0[2], g0[0]))[i2[0]], len(i1), len(i2)


def solve(mua, mub, kind, lo=0.3, hi=3.0, muc=L.MU60):
    a, b = lo, hi; ga, gb = gap(a, mua, mub, kind, muc), gap(b, mua, mub, kind, muc)
    if ga is None or gb is None or ga[0] * gb[0] > 0:
        return None
    for _ in range(40):
        m = 0.5 * (a + b); gm = gap(m, mua, mub, kind, muc)
        if gm[0] * ga[0] > 0:
            a, ga = m, gm
        else:
            b, gb = m, gm
    return 0.5 * (a + b), gm


if __name__ == '__main__':
    for kind in (3, 5):
        for mua, mub in ((0.0, L.MU60), (0.0, 1.1), (0.0, 0.9), (0.1, L.MU60), (0.2, L.MU60), (0.2, 1.1), (0.3, L.MU60)):
            s = solve(mua, mub, kind)
            if s is None:
                print('kind %d mua %.2f mub %.3f: no crossing' % (kind, mua, mub), gap(0.3, mua, mub, kind), gap(3.0, mua, mub, kind)); continue
            bend, gm = s
            o, _ = L.numbers(lambda x, y, z: L.weld_dir(x, y, z, 0.0, mua, mub, bend, kind), n=1000, quiet=True)
            print('kind %d mua %.2f mub %.3f: bend %.6f | critical direction at latitude %.2f, sent to latitude %.2f | folded %.6f covers %.4f ratio>2 %.3f >4 %.3f'
                  % (kind, mua, mub, bend, gm[2], gm[3], o['folded_share'], o['covers'], o['share_ratio_over_2'], o['share_ratio_over_4'])); sys.stdout.flush()
