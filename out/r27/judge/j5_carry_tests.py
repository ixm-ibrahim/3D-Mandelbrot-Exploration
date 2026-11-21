"""Judge, check 5: respace's way A (the balls object's bulbs carried onto the true flat picture), measured my way.

    python j5_carry_tests.py flat      test 1: flat cut against my true flat picture; points lifted a little
    python j5_carry_tests.py family    is respace's family test what it says? (explicit balls)
    python j5_carry_tests.py round     how round are the carried bulbs? (each bulb = one known ball of the balls object)
    python j5_carry_tests.py pieces    loose pieces by blocks; the skin at the meeting points
"""
import sys, time
import numpy as np
from scipy import ndimage
import jlib as J
import jcarry as JC
C = JC.C
K2, T0, RAD = 1.05, 1.40, JC.RAD
SETS = [('c = -1', 'c1', -1.0 + 0j), ('rabbit', 'rabbit', J.RABBIT)]


def flat():
    rng = np.random.default_rng(2705); n = 30000
    x, y = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    for nm, key, c in SETS:
        body = JC.BODIES[key]; tru = J.truth(x, y, c, 2000)
        a = C.carried_inside(body, 'A', x, y, np.zeros(n), nmax=300)
        print('%-7s way A, 30000 random points of the flat plane: truly inside %d; wrong verdicts %d (called inside but truly outside %d, truly inside but called outside %d)'
              % (nm, int(tru.sum()), int((a != tru).sum()), int((a & ~tru).sum()), int((~a & tru).sum())))
        for lift in (1e-6, 1e-3, 1e-2):
            up = C.carried_inside(body, 'A', x[tru], y[tru], np.full(int(tru.sum()), lift), nmax=300)
            print('        truly inside points lifted by %g that are no longer inside: %d of %d' % (lift, int((~up).sum()), int(tru.sum())))
        # the tables I use for everything else (flat points snapped to a 0.001 grid, 80 steps): the same test at grid points
        tab = JC.Tab(key); i = rng.integers(0, tab.w, n); j = rng.integers(0, tab.h, n)
        xn = JC.X0 + i * JC.STEP; yn = JC.Y1 - j * JC.STEP; tn = J.truth(xn, yn, c, 2000); an = tab.inside(xn, yn, 0 * xn)
        print('        my table at 30000 of its own grid points: wrong verdicts %d (truly inside but lost %d: points that need more than 80 steps to reach the middle body)'
              % (int((an != tn).sum()), int((~an & tn).sum())))
        sys.stdout.flush()


def ford(p, q, t=T0, k2=K2):
    """The ball of the balls object that kisses the middle ball at the fraction p / q (whole numbers of the square grid):
    centre and radius in picture coordinates. From the recipe: in the object's own coordinates it stands on the floor
    at p / q and is 1 / (2 t |q|^2) wide; the picture frame is one sphere inversion about (0, 0, 1)."""
    xi = p / q; r = 1.0 / (4 * t * abs(q) ** 2); c = np.array([xi.real, xi.imag, r]); O = np.array([0.0, 0.0, 1.0])
    d2 = ((c - O) ** 2).sum(); u = k2 * (c - O) / (d2 - r * r); rad = k2 * r / abs(d2 - r * r)
    return np.array([u[2] + k2 / 2, u[0], u[1]]), rad


def bulbs(nmax_norm=14):
    """First bulbs off the flat plane, upper side: (fraction, centre, radius) largest first."""
    seen = {}; R = 4
    for a in range(-R, R + 1):
        for b in range(-R, R + 1):
            for cc in range(-R, R + 1):
                for d in range(-R, R + 1):
                    p = complex(a, b); q = complex(cc, d)
                    if q == 0 or abs(p) ** 2 + abs(q) ** 2 > nmax_norm:
                        continue
                    xi = p / q; key = (round(xi.real, 9), round(xi.imag, 9)); n = abs(p) ** 2 + abs(q) ** 2
                    if key not in seen or n < seen[key][0]:
                        seen[key] = (n, p, q)
    out = []
    for (re, im), (n, p, q) in seen.items():
        if im > 1e-9:
            cen, rad = ford(p, q); out.append((complex(re, im), cen, rad, n))
    out.sort(key=lambda v: -v[2]); return out


def family():
    rng = np.random.default_rng(3)
    d = rng.normal(size=(4000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]; rr = rng.uniform(0, 1, 4000) ** (1 / 3)
    print('explicit balls of the balls object (centre and radius from my own arithmetic); 4000 random points in each:')
    tests = [('middle ball', (np.zeros(3), RAD), True)]
    for nm, p, q, want in (('left neighbour (fraction 0)', 0, 1, False), ('bud on top in the flat plane (fraction 1)', 1, 1, False), ('bulb toward the eye (fraction i)', 1j, 1, True),
                           ('bulb at 1 + i', 1 + 1j, 1, True), ('bulb at (1 + i) / 2', 1 + 1j, 2, True), ('bulb at i / 2', 1j, 2, True), ('flat bud at 1 / 2', 1, 2, False), ('bulb at (1 + 2i) / 3', 1 + 2j, 3, True)):
        tests.append((nm, ford(complex(p), complex(q)), want))
    for nm, (cen, rad), want in tests:
        P = cen + rad * 0.999 * rr[:, None] * d
        ins = J.balls(P[:, 0], P[:, 1], P[:, 2], rounds=40) == 1; fam = C.own_family(P[:, 0], P[:, 1], P[:, 2])
        print('   %-42s radius %.4f: my recipe calls inside %d of 4000; respace calls it the middle ball\'s own family: %d (should be %s)' % (nm, rad, int(ins.sum()), int(fam.sum()), 'all' if want else 'none'))
    # balls that hang on a first bulb belong with it: points just outside the bulb toward the eye that are inside the object
    cen, rad = ford(1j, 1 + 0j); P = cen + rad * 1.03 * d; ins = J.balls(P[:, 0], P[:, 1], P[:, 2], rounds=40) == 1; fam = C.own_family(P[:, 0], P[:, 1], P[:, 2])
    print('   bulbs standing on the bulb toward the eye: %d points inside, of them own family %d' % (int(ins.sum()), int((fam & ins).sum())))
    cen, rad = ford(0j, 1 + 0j); P = cen + rad * 1.03 * d; ins = J.balls(P[:, 0], P[:, 1], P[:, 2], rounds=40) == 1; fam = C.own_family(P[:, 0], P[:, 1], P[:, 2])
    far = ins & (np.linalg.norm(P, axis=1) > RAD * 1.001)
    print('   bulbs standing on the left neighbour (not in the middle ball): %d points inside, of them own family %d (should be 0)' % (int(far.sum()), int((fam & far).sum())))


def measure_bulb(tab, sel, cen, rad):
    """The carried bulb = all (flat grid point, height) whose point in the round frame lies in the ball (cen, rad),
    both in round-frame units. Returns (long / short width along its own main directions, share of the ball that has
    no place over the body, number of flat grid points under it)."""
    dX = tab.X - cen[0]; dY = tab.Y - cen[1]; m = sel & (dX * dX + dY * dY < rad * rad)
    if m.sum() < 30:
        return None
    jj, ii = np.nonzero(m); x = JC.X0 + ii * JC.STEP; y = JC.Y1 - jj * JC.STEP
    s = np.sqrt(rad * rad - dX[m].astype(float) ** 2 - dY[m].astype(float) ** 2); A = tab.A[m].astype(float)
    h1 = (cen[2] - s) / A; h2 = (cen[2] + s) / A; w = h2 - h1; W = w.sum()
    mx, my = (w * x).sum() / W, (w * y).sum() / W; mh = (0.5 * (h2 * h2 - h1 * h1)).sum() / W
    xx = x - mx; yy = y - my; m1 = 0.5 * ((h2 - mh) ** 2 - (h1 - mh) ** 2); m2 = ((h2 - mh) ** 3 - (h1 - mh) ** 3) / 3
    cov = np.array([[(w * xx * xx).sum(), (w * xx * yy).sum(), (xx * m1).sum()], [(w * xx * yy).sum(), (w * yy * yy).sum(), (yy * m1).sum()],
                    [(xx * m1).sum(), (yy * m1).sum(), m2.sum()]]) / W
    lam, vec = np.linalg.eigh(cov)
    P = np.r_[np.c_[xx, yy, h1 - mh], np.c_[xx, yy, h2 - mh]]; ext = np.ptp(P @ vec, axis=0)
    # share of the ball with no place over the body (it leans out over the rim: X^2 + Y^2 >= 1)
    rng = np.random.default_rng(1); d = rng.normal(size=(20000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    Q = np.asarray(cen) + rad * (rng.uniform(0, 1, 20000) ** (1 / 3))[:, None] * d; lost = float(((Q[:, 0] ** 2 + Q[:, 1] ** 2) >= 1).mean())
    return float(ext.max() / ext.min()), float(np.sqrt(lam.max() / lam.min())), lost, int(m.sum())


def roundness():
    B = bulbs(); print('%d first bulbs off the flat plane on the upper half of the middle ball, radius %.4f down to %.4f (picture units)' % (len(B), B[0][2], B[-1][2]))
    for nm, key, c in SETS:
        tab = JC.Tab(key); body = JC.BODIES[key]
        hosts = [('middle body', tab.ok & (tab.N == 0))]
        if key == 'c1':
            xs = JC.X0 + np.arange(tab.w) * JC.STEP
            hosts.append(('left neighbour', tab.ok & (tab.N == 1) & (xs[None, :] < 0)))
        for hn, sel in hosts:
            rows = []
            for xi, cen, rad, n in B:
                r = measure_bulb(tab, sel, cen / RAD, rad / RAD)
                if r is not None:
                    rows.append((rad, xi, n) + r)
            whole = [r for r in rows if r[5] < 0.02]; cut = [r for r in rows if r[5] >= 0.02]
            print('== %s, %s: %d bulbs measured; %d whole, %d lean out over the rim and are cut by an upright wall (2%% or more of the ball has no place)' % (nm, hn, len(rows), len(whole), len(cut)))
            for lo, hi, lab in ((0.05, 1, 'large  (radius 0.05 and up)'), (0.018, 0.05, 'medium (0.018 to 0.05)'), (0.0, 0.018, 'small  (below 0.018)')):
                g = [r for r in whole if lo <= r[0] < hi]
                if g:
                    v = np.array([r[3] for r in g]); e = np.array([r[4] for r in g])
                    print('   %-28s %3d whole bulbs: longest / shortest width: least %.2f, middle value %.2f, worst %.2f   (by spread: middle value %.2f, worst %.2f)'
                          % (lab, len(g), v.min(), np.median(v), v.max(), np.median(e), e.max()))
            for r in rows[:8]:
                print('      bulb at the fraction %+.3f%+.3fi, radius %.4f: longest / shortest width %.2f (by spread %.2f); share with no place over the body %.2f; %d flat grid points'
                      % (r[1].real, r[1].imag, r[0], r[3], r[4], r[5], r[6]))
            sys.stdout.flush()


def pieces():
    for nm, key, c in SETS:
        tab = JC.Tab(key); t0 = time.time()
        for step in (0.01, 0.005):
            xs = np.arange(-1.8, 1.8 + 1e-9, step); ys = np.arange(1.3, -1.3 - 1e-9, -step); zs = np.arange(0.0, 1.3 + 1e-9, step)
            gx, gy = np.meshgrid(xs, ys); occ = np.zeros((zs.size,) + gx.shape, bool)
            for k, z in enumerate(zs):
                occ[k] = tab.inside(gx, gy, np.full(gx.shape, z))
                if not occ[k].any() and z > 0.9:
                    break
            lab, cnt = ndimage.label(occ, structure=np.ones((3, 3, 3))); sizes = np.bincount(lab.ravel())[1:]
            touching = np.unique(lab[0][occ[0]]); loose = np.setdiff1d(np.arange(1, cnt + 1), touching)
            top = zs[np.flatnonzero(occ.any((1, 2))).max()]
            print('%-7s way A, blocks of %.3f above the flat plane: %d pieces; %d do not reach the flat plane, holding %.3f of 100 parts of the solid; biggest loose piece %d blocks; highest block %.2f (%.0f s)'
                  % (nm, step, cnt, len(loose), 100.0 * sizes[loose - 1].sum() / occ.sum() if len(loose) else 0.0, int(sizes[loose - 1].max()) if len(loose) else 0, top, time.time() - t0))
            sys.stdout.flush()
        # the skin of the middle body near the point where it meets its neighbour(s): height of the base body there
        al = (1 - np.sqrt(1 - 4 * c + 0j)) / 2; sel = tab.ok & (tab.N == 0)
        jj, ii = np.nonzero(sel); zz = (JC.X0 + ii * JC.STEP) + 1j * (JC.Y1 - jj * JC.STEP)
        b2 = tab.X[sel].astype(float) ** 2 + tab.Y[sel].astype(float) ** 2; hgt = np.sqrt(np.clip(1 - b2, 0, 1)) / tab.A[sel]
        dist = np.abs(zz - al)
        print('%-7s height of the middle body\'s skin over flat points near the meeting point (%.4f%+.4fi): its height at the middle is %.3f' % (nm, al.real, al.imag, hgt[np.argmin(np.abs(zz))]))
        for r0, r1 in ((0.1, 0.2), (0.05, 0.1), (0.02, 0.05), (0.01, 0.02), (0.005, 0.01), (0.002, 0.005), (0.0, 0.002)):
            m = (dist >= r0) & (dist < r1)
            if m.any():
                print('        %.3f to %.3f from the meeting point: %5d flat points, skin height middle value %.3f, highest %.3f' % (r0, r1, int(m.sum()), np.median(hgt[m]), hgt[m].max()))
        # along the rim in general: how high is the wall where the body ends? (flat points in the body with a neighbour that is not)
        er = ndimage.binary_erosion(sel, structure=np.ones((3, 3))); rim = sel & ~er
        hr = np.sqrt(np.clip(1 - tab.X[rim].astype(float) ** 2 - tab.Y[rim].astype(float) ** 2, 0, 1)) / tab.A[rim]
        print('%-7s the outermost flat grid points of the middle body (%d points): skin height there, middle value %.3f, one in ten above %.3f, highest %.3f' % (nm, int(rim.sum()), np.median(hr), np.quantile(hr, 0.9), hr.max()))
        sys.stdout.flush()


if __name__ == '__main__':
    {'flat': flat, 'family': family, 'round': roundness, 'pieces': pieces}[sys.argv[1]]()
