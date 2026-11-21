"""Judge, check 1: my own recipe against round 25's tree.py; how many rounds decide; flat cut of the 3D object = line object;
every body an exact ball (a few bodies measured)."""
import os, sys, time
import numpy as np
import jlib as J
sys.path.insert(0, os.path.join(J.ROOT, 'out', 'r25', 'klein'))
import tree as TR

rng = np.random.default_rng(2701); n = 200000
x, y, z = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n), rng.uniform(-1.3, 1.3, n)
names = {'line': 'line', 'square': 'gauss', 'hex': 'eisen'}
print('== my recipe against tree.py, %d random points of the box, 40 rounds' % n)
for t in (1.0, 1.4, 2.5):
    for g in ('line', 'square', 'hex'):
        mine = J.balls(x, y, z, t=t, grid=g, rounds=40)
        ref = J.M.stay(TR.tree(names[g], t=t), x, y, z, 0.0, 0.0, 0.0, 40) >= 40
        und = int((mine == 0).sum()); dif = int(((mine == 1) != ref)[mine != 0].sum())
        print('t = %.1f %-6s: inside share %.4f; undecided by mine %d; verdicts that differ among the decided %d' % (t, g, (mine == 1).mean(), und, dif))
print('== rounds needed, t = 1.4, square grid, %d points' % n)
ref = J.balls(x, y, z, rounds=80)
for r in (2, 3, 4, 6, 8, 10, 14):
    a = J.balls(x, y, z, rounds=r)
    print('   %2d rounds: undecided %d; decided but different from 80 rounds %d' % (r, int((a == 0).sum()), int(((a != ref) & (a != 0)).sum())))
print('   80 rounds: undecided %d' % int((ref == 0).sum()))
print('== flat cut of the 3D object against the line object, %d points on z = 0' % n)
for t in (1.0, 1.4, 2.5):
    ln = J.balls(x, y, 0 * x, t=t, grid='line', rounds=40)
    for g in ('square', 'hex'):
        a = J.balls(x, y, 0 * x, t=t, grid=g, rounds=40)
        both = (a != 0) & (ln != 0)
        print('   t = %.1f %-6s: differ %d (undecided in either %d)' % (t, g, int((a != ln)[both].sum()), int((~both).sum())))
print('== is every body a ball? five bodies, skin found along 4000 random lines from an inside point')
# bodies named by a point inside each: middle ball, right neighbour, top bud in the flat plane, the bulb straight toward the eye, one small bulb
k2 = 1.05; t = 1.4


def skin(p0, nlines=4000, rmax=0.6):
    d = rng.normal(size=(nlines, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    lo = np.zeros(nlines); hi = np.full(nlines, np.nan)
    # walk out until first outside
    r = np.zeros(nlines); step = 0.002; done = np.zeros(nlines, bool)
    for _ in range(int(rmax / step)):
        r2 = r + step; P = p0[None] + r2[:, None] * d
        ins = J.balls(P[:, 0], P[:, 1], P[:, 2], rounds=30) == 1
        newly = ~done & ~ins; hi[newly] = r2[newly]; lo[newly] = r[newly]; done |= newly
        r = np.where(done, r, r2)
        if done.all():
            break
    for _ in range(30):
        mid = 0.5 * (lo + hi); P = p0[None] + mid[:, None] * d
        ins = J.balls(P[:, 0], P[:, 1], P[:, 2], rounds=30) == 1
        lo = np.where(ins, mid, lo); hi = np.where(ins, hi, mid)
    return p0[None] + lo[:, None] * d


def fit_sphere(P):
    A = np.c_[2 * P, np.ones(len(P))]; b = (P * P).sum(1); s, *_ = np.linalg.lstsq(A, b, rcond=None)
    c = s[:3]; r = np.sqrt(s[3] + c @ c); res = np.linalg.norm(P - c, axis=1) - r
    return c, r, res


wn = k2 / (2 * t - 1)
starts = [('middle ball', np.array([0.1, 0.05, 0.02])), ('right neighbour', np.array([k2 / 2 + wn / 2, 0.02, 0.01])),
          ('bud on top, in the flat plane', np.array([0.0, k2 / 2 + 0.05, 0.0])), ('bulb straight toward the eye', np.array([0.0, 0.0, k2 / 2 + 0.05])),
          ('a bulb between them', np.array([0.0, (k2 / 2 + 0.03) * np.sqrt(0.5), (k2 / 2 + 0.03) * np.sqrt(0.5)]))]
for nm, p0 in starts:
    if J.balls(p0[0], p0[1], p0[2], rounds=30) != 1:
        print('   %s: start point not inside, skipped' % nm); continue
    P = skin(p0); ok = np.isfinite(P).all(1); P = P[ok]; c, r, res = fit_sphere(P)
    for _ in range(3):                                   # a line that runs through a kissing point walks on into the bud: drop those and fit again
        good = np.abs(res) < 2e-3 * r + 3 * np.median(np.abs(res)); c, r, _ = fit_sphere(P[good]); res = np.linalg.norm(P - c, axis=1) - r
    good = np.abs(res) < 2e-3 * r
    print('   %-30s centre (%.4f, %.4f, %.4f) radius %.5f; %d of %d lines end on the fitted ball to within %.1e of the radius; %d lines ran on into a bud through a kissing point'
          % (nm, c[0], c[1], c[2], r, int(good.sum()), len(P), np.abs(res[good]).max() / r, int((~good).sum())))
