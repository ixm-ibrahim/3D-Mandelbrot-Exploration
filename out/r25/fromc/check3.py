"""Round 25, fromc: what the triangle pattern is near its corner, how big the jump on the seam of 'twin_tri' is,
and how much of a solid is loose scrap.      python out/r25/fromc/check3.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M


def ang(a, b):
    d = np.clip(a[0] * b[0] + a[1] * b[1] + a[2] * b[2], -1, 1); return np.degrees(np.arccos(d))


def near_corner():
    G = R._tri(); print('(a) the triangle pattern near its corner (the direction +x) against the quaternion square about the x-axis')
    for smax in (10, 20, 28, 31, 40, 44, 46, 60):
        rng = np.random.default_rng(1); n = 40000
        for nm, phi in (('all round', rng.uniform(0, 2 * np.pi, n)), ('in the flat plane', np.zeros(n)), ('in the upright plane', np.full(n, np.pi / 2))):
            s = np.radians(rng.uniform(0, smax, n))
            u = (np.cos(s), np.sin(s) * np.cos(phi), np.sin(s) * np.sin(phi))
            g = G(*u); l = (np.cos(2 * s), np.sin(2 * s) * np.cos(phi), np.sin(2 * s) * np.sin(phi))
            print('    within %2d degrees of the corner, %-20s: largest difference %.2e degrees' % (smax, nm, float(ang(g, l).max())))


def seam():
    G = R._tri(); print('(b) the jump on the seam of twin_tri (the upright plane through 0 square to the line 0 - meeting point)')
    for L in (0, 2, 5, 10, 20, 30, 45, 60, 75, 85, 89.9):
        la = np.radians(L); a = G(0.0 * la, np.cos(la) + 0 * la, np.sin(la) + 0 * la); b = G(0.0 * la, -np.cos(la) + 0 * la, np.sin(la) + 0 * la)
        a = [np.atleast_1d(t) for t in a]; b = [np.atleast_1d(t) for t in b]
        print('    height angle %5.1f: the two sides of the seam are sent %.1f degrees apart' % (L, float(ang(a, b)[0])))


def pieces():
    try:
        from scipy import ndimage as ndi
    except Exception as e:
        print('(c) no scipy:', e); return
    print('(c) loose scrap on a 110^3 grid (box 3.6 x 2.8 x 2.8), 40 steps: pieces are blocks joined by faces')
    n = 110; xs = np.linspace(-1.8, 1.8, n); ys = np.linspace(-1.4, 1.4, n); zs = np.linspace(-1.4, 1.4, n)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    for nm in ('oneplane', 'along', 'axis_once', 'face4', 'face_tri', 'twin_tri'):
        r = R.get(nm)
        for sn, c in (('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
            ins = np.zeros(X.shape, bool)
            for i in range(0, n, 10):
                ins[i:i + 10] = M.stay(r, X[i:i + 10], Y[i:i + 10], Z[i:i + 10], c[0], c[1], c[2], 40) >= 40
            lab, k = ndi.label(ins); tot = int(ins.sum())
            if tot == 0:
                print('    %-10s %-7s nothing inside' % (nm, sn)); continue
            sz = np.sort(np.bincount(lab.ravel())[1:])[::-1]
            small = int(sz[sz < max(8, 0.002 * tot)].sum())
            print('    %-10s %-7s inside %6d blocks in %4d pieces; the five biggest hold %5.1f %%; scrap (pieces under 0.2 %% of the whole) %5.2f %%'
                  % (nm, sn, tot, k, 100.0 * sz[:5].sum() / tot, 100.0 * small / tot))
            sys.stdout.flush()


if __name__ == '__main__':
    near_corner(); seam(); pieces()
