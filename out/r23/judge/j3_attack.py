"""Round 23, judge, check 3: trying to make the best new rule (cones1) fail, and c = -1 against along.

    python out/r23/judge/j3_attack.py [a,b,c,d,e,f]

a  lopsidedness: share of the inside whose verdict changes under  z -> -z,  y -> -y,  the half turn (x, y) -> (-x, -y)
b  buds round the bodies of c = -1: separate arcs of inside on rings round the x-axis (round the middle body, x = 0, and
   round the body beside it, x = -1)
c  c turned out of the flat plane by 1, 3, 5, 10 degrees (c = -0.12 + 0.75i): share of a box inside at 80 steps
d  the Mandelbrot solid: share of a box inside, verdicts that differ from one plane's, share off the flat plane
e  where the extra bodies of cones1 hold on: the worked-out contact point on the cone, patches of inside on small balls
f  is the extra thing of cones1 a second copy of the flat picture on a cone? verdicts on the cone against the flat picture
"""
import os, sys, time
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jl as L
what = sys.argv[1].split(',') if len(sys.argv) > 1 else list('abcdef')
rng = np.random.default_rng(31); t0 = time.time()
NAMES = ['oneplane', 'twoplane', 'along', 'alongonce', 'cones1', 'cones2', 'cones']


def arcs(ins):
    n = ins.size
    if ins.all():
        return 1, 360.0
    if not ins.any():
        return 0, 0.0
    v = np.roll(ins, -int(np.argmin(ins))); d = np.diff(np.concatenate([[0], v.astype(int), [0]]))
    return int((d == 1).sum()), float(ins.mean() * 360)


def patches(rule, c, centre, rad, nla=160, nlo=320, steps=100):
    la = (np.arange(nla) + 0.5) / nla * np.pi - np.pi / 2; lo = (np.arange(nlo) + 0.5) / nlo * 2 * np.pi
    LA, LO = np.meshgrid(la, lo, indexing='ij')
    ins = L.stay(rule, centre[0] + rad * np.cos(LA) * np.cos(LO), centre[1] + rad * np.cos(LA) * np.sin(LO), centre[2] + rad * np.sin(LA), c, steps) >= steps
    w = np.cos(LA); share = float((ins * w).sum() / w.sum())
    wide = np.concatenate([ins, ins], axis=1); lab, k = ndi.label(wide, structure=np.ones((3, 3), bool))      # doubled in longitude: the seam is inside
    par = list(range(k + 1))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(nla):
        for j in range(nlo):
            a, b = lab[i, j], lab[i, j + nlo]
            if a and b:
                par[find(a)] = find(b)
    for row in (0, nla - 1):
        ls = np.unique(lab[row][lab[row] > 0])
        for l in ls[1:]:
            par[find(l)] = find(ls[0])
    root = np.array([find(a) for a in range(k + 1)]); lab2 = root[lab[:, :nlo]]
    area = sorted([float((w * (lab2 == r)).sum() / w.sum()) for r in np.unique(lab2[lab2 > 0])], reverse=True)
    return [a for a in area if a >= 0.003], share


if 'a' in what:
    print('== a. lopsidedness (200,000 random points of a box, 80 steps): share of the inside whose verdict changes')
    V = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(200000, 3))
    for sn, c in (('c = -1', L.BAS), ('rabbit', L.RABBIT)):
        for nm in NAMES:
            r = L.get(nm); a = L.stay(r, V[:, 0], V[:, 1], V[:, 2], c, 80) >= 80; row = []
            for tag, T in (('above <-> below', (1, 1, -1)), ('y <-> -y', (1, -1, 1)), ('half turn about the upright axis', (-1, -1, 1)), ('half turn about the x-axis', (1, -1, -1))):
                b = L.stay(r, T[0] * V[:, 0], T[1] * V[:, 1], T[2] * V[:, 2], c, 80) >= 80
                row.append('%s %.1f %%' % (tag, 100 * (a != b).sum() / max(a.sum() + b.sum(), 1) * 2 / 2))
            fl = L.flat_stay(V[:, 0], V[:, 1], c, 80) >= 80
            print('   %-7s %-10s inside %.4f | %s   [%.0f s]' % (sn, nm, a.mean(), ' | '.join(row), time.time() - t0)); sys.stdout.flush()
    print('   (the flat picture itself: c = -1 has both mirrors and the half turn; the rabbit has the half turn only)')

if 'b' in what:
    print('== b. c = -1: separate arcs of inside on rings round the x-axis (1440 points, 100 steps); "n (deg)" = arcs (degrees inside)')
    a = np.arange(1440) * 2 * np.pi / 1440
    for x0, radii in ((0.0, (0.50, 0.56, 0.62, 0.68, 0.74)), (-1.0, (0.24, 0.28, 0.32, 0.36, 0.40)), (-1.5, (0.10, 0.13, 0.16))):
        for nm in NAMES:
            r = L.get(nm); row = []
            for rad in radii:
                ins = L.stay(r, np.full(a.size, x0), rad * np.cos(a), rad * np.sin(a), L.BAS, 100) >= 100
                k, deg = arcs(ins); row.append('r %.2f: %d (%.0f)' % (rad, k, deg))
            print('   ring at x = %-4g %-10s %s' % (x0, nm, ' | '.join(row))); sys.stdout.flush()

if 'c' in what:
    print('== c. c = -0.12 + 0.75i turned out of the flat plane: share of a box inside at 80 steps (200,000 points)')
    V = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(200000, 3))
    for nm in NAMES + ['d:pillowJ']:
        r = L.get(nm); row = []
        for deg in (0, 1, 3, 5, 10):
            t = np.radians(deg); c = (-0.12, 0.75 * np.cos(t), 0.75 * np.sin(t))
            row.append('%d deg: %.4f' % (deg, (L.stay(r, V[:, 0], V[:, 1], V[:, 2], c, 80) >= 80).mean()))
        print('   %-10s %s   [%.0f s]' % (nm, ' | '.join(row), time.time() - t0)); sys.stdout.flush()

if 'd' in what:
    print('== d. the Mandelbrot solid (orbit started at c, first squaring k = 0), 300,000 points of the box -2.1..0.7, -1.3..1.3, -1.3..1.3, 60 steps')
    C = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(300000, 3)); ref = None
    for nm in ['oneplane', 'along', 'alongonce', 'cones1', 'cones2', 'cones', 'twoplane']:
        r = L.get(nm); n = C.shape[0]; st = tuple(r.init(n)); x, y, z = C[:, 0].copy(), C[:, 1].copy(), C[:, 2].copy(); alive = np.ones(n, bool)
        for k in range(60):
            with np.errstate(all='ignore'):
                o = r.step(x, y, z, st, k, C[:, 0], C[:, 1], C[:, 2])
            x, y, z = o[0] + C[:, 0], o[1] + C[:, 1], o[2] + C[:, 2]; st = tuple(o[3])
            bad = ~((x * x + y * y + z * z) < 36.0); alive &= ~bad; x[bad] = 100.0; y[bad] = 0.0; z[bad] = 0.0
        if ref is None:
            ref = alive.copy()
        far = np.abs(C[:, 2]) > 0.3
        print('   %-10s inside %.4f of the box | verdicts that differ from one plane: %d of %d | share of the solid further than 0.3 from the flat plane: %.1f %%   [%.0f s]'
              % (nm, alive.mean(), int((alive != ref).sum()), n, 100 * (alive & far).sum() / max(alive.sum(), 1), time.time() - t0)); sys.stdout.flush()

if 'e' in what:
    print('== e. cones1 on the rabbit: the contact point worked out by hand, and what small balls round it show')
    cc = complex(L.RABBIT[0], L.RABBIT[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2            # the meeting point of the flat rabbit (fixed)
    lon = np.pi / 2 - 2 * np.angle(al); rho = abs(al)
    v = (rho * 0.5 * np.cos(lon), rho * 0.5 * np.sin(lon), rho * np.sqrt(3) / 2)
    X, Y, Z = L.CONES(np.array([v[0]]), np.array([v[1]]), np.array([v[2]]))
    print('   meeting point of the flat rabbit: %.4f %+.4fi. Point on the upper cone that the first step sends there: (%.4f, %.4f, %.4f); its step lands at (%.4f, %.4f, %.2e)'
          % (al.real, al.imag, v[0], v[1], v[2], X[0] + cc.real, Y[0] + cc.imag, Z[0]))
    for tag, nm, cen in (('one plane, at the flat meeting point', 'oneplane', (al.real, al.imag, 0.0)), ('cones1, at the flat meeting point', 'cones1', (al.real, al.imag, 0.0)),
                         ('cones1, at the point on the cone', 'cones1', v), ('cones (every step), at the point on the cone', 'cones', v),
                         ('along once, at the flat meeting point', 'alongonce', (al.real, al.imag, 0.0))):
        row = []
        for rad in (0.08, 0.04, 0.02, 0.01):
            ar, sh = patches(L.get(nm), L.RABBIT, cen, rad); row.append('ball %.2f: %d patches (%s), %.0f %% of its skin inside' % (rad, len(ar), ', '.join('%.0f' % (100 * q) for q in ar[:5]), 100 * sh))
        print('   %s:\n      %s   [%.0f s]' % (tag, '\n      '.join(row), time.time() - t0)); sys.stdout.flush()

if 'f' in what:
    print('== f. cones1: is what stands on the cone (60 degrees up) the flat picture a second time, rolled up once round?')
    n = 40000; rho = np.sqrt(rng.uniform(0, 1.9 ** 2, n)); lon = rng.uniform(-np.pi, np.pi, n)
    for sn, c in (('c = -1', L.BAS), ('rabbit', L.RABBIT), ('Siegel', L.SIEGEL)):
        for nm in ('cones1', 'cones'):
            row = []
            for sgn in (1, -1):
                a = L.stay(L.get(nm), rho * 0.5 * np.cos(lon), rho * 0.5 * np.sin(lon), sgn * rho * np.sqrt(3) / 2, c, 80) >= 80
                w = rho * rho * np.exp(1j * (np.pi / 2 - lon)) + complex(c[0], c[1])          # where the first step lands, by the formula
                b = L.flat_stay(w.real, w.imag, c, 79) >= 79
                row.append('%s cone: %d of %d verdicts differ (inside %d)' % ('upper' if sgn > 0 else 'lower', int((a != b).sum()), n, int(a.sum())))
            print('   %-7s %-7s %s' % (sn, nm, ' | '.join(row))); sys.stdout.flush()
    print('   (the flat point tested is  rho^2 e^(i (90 deg - lon)) + c  for the cone point at distance rho, longitude lon: one cone point per flat point)')
