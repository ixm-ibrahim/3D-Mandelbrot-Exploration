"""python out/r21/alongmem/jac.py
Does 'along' fold space? The sign of the Jacobian (by central differences) of along and of the one-plane rule at
random points of the unit ball. A map with both signs folds space over itself along the surface where the sign
changes; the preimage of a connected body under such a map can come apart into pieces that float free.
Also: how far the sheet of squaring of a group A rule can stand from the point's own sheet (it is |sin(.) / 4|)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T
M = T.M


def jac_sign(F, v, h=1e-5):
    J = np.zeros((v.shape[0], 3, 3))
    for j in range(3):
        e = np.zeros(3); e[j] = h
        a = np.stack(F(*(v + e).T), 1); b = np.stack(F(*(v - e).T), 1); J[:, :, j] = (a - b) / (2 * h)
    return np.linalg.det(J)


if __name__ == '__main__':
    rng = np.random.default_rng(1); v = rng.normal(size=(400000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; v *= rng.uniform(0.2, 1.0, (400000, 1))
    M.bench('along')                                             # puts the bench registry on the path
    import rules as RB
    for nm in ('along', 'oneplane', 'lathe'):
        M.bench(nm); d = jac_sign(RB.get(nm), v); r = np.linalg.norm(v, axis=1); dn = d / (8 * r ** 3)   # a conformal square has det = (2 r)^3
        phi = np.degrees(np.arctan2(v[:, 2], v[:, 1])) % 90
        neg = dn < 0
        print('%-9s Jacobian / (2r)^3: share negative %.2f%%, smallest %.2f, largest %.2f, median %.2f' % (nm, 100 * neg.mean(), dn.min(), dn.max(), np.median(dn)))
        if neg.any():
            h, _ = np.histogram(phi[neg], bins=9, range=(0, 90)); ha, _ = np.histogram(phi, bins=9, range=(0, 90))
            print('          share negative by the turn of the point (mod 90 degrees, bins of 10): ' + ' '.join('%.0f%%' % (100 * a / max(b, 1)) for a, b in zip(h, ha)))
            ax = np.abs(v[:, 0]) / r
            h, _ = np.histogram(ax[neg], bins=5, range=(0, 1)); ha, _ = np.histogram(ax, bins=5, range=(0, 1))
            print('          share negative by |x| / r (0 = across the x-axis, 1 = on it; bins of 0.2): ' + ' '.join('%.0f%%' % (100 * a / max(b, 1)) for a, b in zip(h, ha)))
