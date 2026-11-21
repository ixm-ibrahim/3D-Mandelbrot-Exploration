"""Checks of the reasoned claims, by numbers.
python out/r21/span/theory.py   -> prints, and writes out/r21/span/theory.txt

1. SWEEP. If the orbit of 0 never leaves its first plane and is squared inside it, the Mandelbrot solid is
       { c : |c| * exp(i * theta(c)) is in the flat Mandelbrot set },   theta(c) = angle between c and the real axis of its first plane.
   Checked for the first planes: own sheet (theta = angle from +x), the plane nearest the flat page (tan theta = |y| r / (x rho)),
   the plane of c and P(c) (computed).
2. JULIA of "the point and c": the orbit of v never leaves the plane of v and c; inside it, it is the flat orbit of
   z0 = (v.a, v.b) under z^2 + gamma, gamma = (c.a, c.b), a = the plane's real axis. Checked for the rabbit and the Siegel disc.
3. How firmly does "the point and the point before" keep its plane? The orbit of 0 is started in its plane and pushed
   1e-9 out of it at the second point; the growth of the push is measured.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M
out = []


def say(s):
    print(s); sys.stdout.flush(); out.append(s)


def theta_axis(nfun, cx, cy, cz):
    n = nfun(cx, cy, cz); a = R.real_axis(*n)
    al = a[0] * cx + a[1] * cy + a[2] * cz; r = np.sqrt(cx * cx + cy * cy + cz * cz)
    return al, np.sqrt(np.maximum(r * r - al * al, 0.0))          # gamma = al + i * (the part of c across the real axis)


def n_cP(x, y, z):
    w = R.P(x, y, z); return R.n_made(x, y, z, *w, lambda: R.n_page(x, y, z))[:3]


rng = np.random.default_rng(21); n = 40000; steps = 60
c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3)); cx, cy, cz = c[:, 0], c[:, 1], c[:, 2]
say('1. SWEEP: verdicts that differ between the rule and the swept flat set, of %d random c, %d steps' % (n, steps))
for nm, nfun in (('c_lathe', R.n_lathe), ('prev_lathe', R.n_lathe), ('c_page', R.n_page), ('prev_page', R.n_page), ('prev_keep', R.n_page),
                 ('prev_axis', R.n_page), ('prev_lag50in', R.n_page), ('guessN', n_cP), ('guessNc', n_cP)):
    try:
        r = R.get(nm)
    except StopIteration:
        continue
    g1, g2 = theta_axis(nfun, cx, cy, cz)
    a = M.mandel(r, cx, cy, cz, steps) >= steps; b = M.flat_stay(g1, g2, g1, g2, steps) >= steps
    say('   %-13s differ %5d (rule inside %d, swept flat set inside %d; rule in and sweep out %d, rule out and sweep in %d)' % (nm, (a != b).sum(), a.sum(), b.sum(), (a & ~b).sum(), (~a & b).sum()))

say('2. JULIA of the point and c: verdicts that differ from the flat Julia set of gamma drawn in the plane of the point and c')
v = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3)); x, y, z = v[:, 0], v[:, 1], v[:, 2]
for sn, cc in (('rabbit', M.RABBIT), ('Siegel disc', M.SIEGEL), ('c = (-0.6, 0.3, 0.4), off the page', (-0.6, 0.3, 0.4))):
    C = [np.full(n, t) for t in cc]
    nn = R.n_made(x, y, z, *C, lambda: R.n_page(x, y, z))[:3]; a = R.real_axis(*nn)
    b = (nn[1] * a[2] - nn[2] * a[1], nn[2] * a[0] - nn[0] * a[2], nn[0] * a[1] - nn[1] * a[0])
    z0 = (x * a[0] + y * a[1] + z * a[2], x * b[0] + y * b[1] + z * b[2]); g = (C[0] * a[0] + C[1] * a[1] + C[2] * a[2], C[0] * b[0] + C[1] * b[1] + C[2] * b[2])
    A = M.stay(R.get('c_page'), x, y, z, *cc, steps) >= steps; B = M.flat_stay(z0[0], z0[1], g[0], g[1], steps) >= steps
    arg = np.degrees(np.arctan2(np.abs(g[1]), g[0]))
    say('   %-36s differ %d of %d (inside %d). gamma: |gamma| = %.4f, its angle runs from %.1f to %.1f degrees over the planes' % (sn, (A != B).sum(), n, A.sum(), np.hypot(g[0], g[1]).mean(), arg.min(), arg.max()))

say('3. the point and the point before: a push of 1e-9 out of the plane, given to the second point of the orbit of 0')
m = 20000; c = rng.uniform([-2.0, -1.2, -1.2], [0.6, 1.2, 1.2], size=(m, 3)); cx, cy, cz = c[:, 0], c[:, 1], c[:, 2]
for nm in ('prev_page', 'prev_keep', 'c_page', 'prev_lag50in'):
    try:
        r = R.get(nm)
    except StopIteration:
        continue
    res = {}
    for push in (0.0, 1e-9):
        x, y, z = cx.copy(), cy.copy(), cz.copy(); st = tuple(r.init(m)); alive = np.ones(m, bool); worst = np.zeros(m); hist = []
        for k in range(40):
            X, Y, Z, st = r.step(x, y, z, st, k, cx, cy, cz); st = tuple(st); x, y, z = X + cx, Y + cy, Z + cz
            if k == 0:
                a, b, d = cy * z - cz * y, cz * x - cx * z, cx * y - cy * x; q = np.sqrt(a * a + b * b + d * d); good = q > 1e-6; q = np.where(good, q, 1.0); nr = (a / q, b / q, d / q)
                x, y, z = x + push * nr[0], y + push * nr[1], z + push * nr[2]
            alive &= (x * x + y * y + z * z) < 9.0
            x, y, z = np.where(alive, x, 0.3), np.where(alive, y, 0.2), np.where(alive, z, 0.1)
            dist = np.abs(x * nr[0] + y * nr[1] + z * nr[2]); worst = np.where(alive & good, np.maximum(worst, dist), worst)
            if k in (4, 9, 19, 39):
                hist.append((k + 1, float(np.median(worst[alive & good])), float((worst[alive & good] > 1e-3).mean())))
        res[push] = hist
    for push in (0.0, 1e-9):
        say('   %-13s push %.0e: ' % (nm, push) + '; '.join('after %d steps median off-plane %.1e, share above 1e-3: %.1f%%' % (k, md, 100 * sh) for k, md, sh in res[push]))

with open(os.path.join(HERE, 'theory.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out) + '\n')
