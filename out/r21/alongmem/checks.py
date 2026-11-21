"""python out/r21/alongmem/checks.py
Three small checks behind statements in NOTES.md.
1. The stretch straight off the page at the rabbit's pinch point, for along about a frame turned by theta:
   measured by differences, against the formula 2 ((1 - s) |alpha| + s Re alpha), s = 1 - cos(4 theta).
2. b_keep for c on the x-axis is the one-plane Julia set re-wrapped: the point at turn phi is inside exactly when the
   point at turn sin(4 phi) / 4 (same x, same distance from the axis) is inside the one-plane set.
3. c_wake1 is 'along once, then the one-plane rule': v is inside exactly when along(v) + c is inside the one-plane set."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M

if __name__ == '__main__':
    al = np.array([T.ALPHA[0], T.ALPHA[1], 0.0]); h = 1e-6; ra = np.hypot(al[0], al[1])
    for th in (0, 2, 5, 5.2, 10, 22.5, 45):
        t = np.radians(4 * th); u = (np.array([np.cos(t)]), np.array([np.sin(t)]))
        up = R.along_u(np.array([al[0]]), np.array([al[1]]), np.array([h]), *u); dn = R.along_u(np.array([al[0]]), np.array([al[1]]), np.array([-h]), *u)
        m = (up[2][0] - dn[2][0]) / (2 * h); s = 1 - np.cos(t)
        print('frame turned %5.1f degrees: stretch off the page at the pinch point %.3f (formula %.3f)' % (th, m, 2 * ((1 - s) * ra + s * al[0])))
    rng = np.random.default_rng(8); n = 60000; v = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3))
    rho = np.hypot(v[:, 1], v[:, 2]); phi = np.arctan2(v[:, 2], v[:, 1]); d = 0.25 * np.sin(4 * phi)
    for cn, c in (('basilica', (-1.0, 0.0, 0.0)), ('San Marco', (-0.75, 0.0, 0.0))):
        a = M.stay(R.get('b_keep'), v[:, 0], v[:, 1], v[:, 2], *c, 50) >= 50
        b = M.stay(M.bench('oneplane'), v[:, 0], rho * np.cos(d), rho * np.sin(d), *c, 50) >= 50
        print('b_keep against the re-wrapped one-plane set, %s: %d verdicts of %d differ (inside %d)' % (cn, (a != b).sum(), n, a.sum()))
    M.bench('along'); import rules as RB
    for cn, c in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
        a = M.stay(R.get('c_wake1'), v[:, 0], v[:, 1], v[:, 2], *c, 50) >= 50
        w = RB.get('along')(v[:, 0], v[:, 1], v[:, 2])
        b = (M.stay(M.bench('oneplane'), w[0] + c[0], w[1] + c[1], w[2] + c[2], *c, 49) >= 49) & ((w[0] + c[0]) ** 2 + (w[1] + c[1]) ** 2 + (w[2] + c[2]) ** 2 < 36)
        print('c_wake1 against "along once, then one-plane", %s: %d verdicts of %d differ (inside %d)' % (cn, (a != b).sum(), n, a.sum()))
