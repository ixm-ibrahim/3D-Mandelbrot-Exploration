"""Round 28, Track A, the fixer: the SIDE SPINDLE (repair of E1), put to lists of balls before it goes into the page.

  python out/r28/fix/mk/side.py [quick]     -> out/r28/fix/logs/side.txt

No browser. The lists of balls are the truth checker's (out/r28/truth/mk/tkit.py, used as it is).

The claim. The second sphere S2 (radius rho about C = (0, 0, top)) and its copy at the next whole number (about C + n,
|n| = 1) are both centred on the top wall. Two points of the line through their centres are carried onto each other by
both inversions: C + x n and C + (1 - x) n, x = (1 - sqrt(1 - 4 rho^2)) / 2 (one point, the kiss, when rho = 1/2).
Every circle through both crosses both spheres squarely. So the spindle swept by such an arc round that line is
carried onto itself by both inversions, and the half of it under the top wall holds no ball, PROVIDED its piece
outside both spheres holds none. That piece holds none when the spindle reaches no further from the line than
   w = min(top - HB, D - rho),   D = 1 (square grid), sqrt(3) / 2 (honeycomb), 1 (a line only),
because then it stays above everything that grows on the bottom wall (nothing there is higher than HB) and clear
of every other copy of the second sphere.
In the half-plane (v = distance along the line from the middle point T = C + n / 2, q = distance from the line):
the arc is the circle about (0, a) with radius R, a = (w^2 - c2) / 2w, R = (w^2 + c2) / 2w, c2 = 1/4 - rho^2,
and a point inside has the room R - |(v, q - a)|.

What is measured, for each setting:
  1. does a listed ball (any slid copy, the walls left out) reach into that spindle, and how deep (must be <= 0);
  2. random points of the half spindle under the top wall: the recipe (300 rounds) must call none INSIDE;
  3. the same two for a spindle 3 % wider (it should fail somewhere, or the choice of w is not the largest: told only).
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(FIX), 'truth', 'mk'))
import tkit as T

LOG = os.path.join(FIX, 'logs', 'side.txt')
out = []


def say(s=''):
    print(s, flush=True); out.append(s)
    with open(LOG, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')


def side_w(gname, top, rho, HB):
    D = np.sqrt(3) / 2 if gname == 'hex' else 1.0
    return min(top - HB, D - rho)


def reach_in(B, top, c2, w):
    """B: balls (x, y, z, r) near T = (0.5, 0, top). How deep the deepest reaches into the spindle (<= 0: none does), and how many do."""
    a = (w * w - c2) / (2 * w); R = (w * w + c2) / (2 * w)
    v = B[:, 0] - 0.5; q = np.hypot(B[:, 1], B[:, 2] - top)
    deep = R - (np.hypot(v, q - a) - B[:, 3])
    return float(deep.max()), int((deep > 1e-9).sum()), a, R


def points_in(rng, n, top, c2, w):
    """n random points of the half spindle under the top wall (object's own coordinates)."""
    a = (w * w - c2) / (2 * w); R = (w * w + c2) / (2 * w)
    P = []
    vmax = R if a >= 0 else np.sqrt(c2)
    while sum(len(p) for p in P) < n:
        v = rng.uniform(-vmax, vmax, 4 * n); q = w * np.sqrt(rng.uniform(0, 1, 4 * n)); ph = rng.uniform(0, np.pi, 4 * n)
        ok = np.hypot(v, q - a) < R * (1 - 1e-9)
        P.append(np.column_stack([0.5 + v[ok], q[ok] * np.cos(ph[ok]), top - q[ok] * np.sin(ph[ok])]))
    return np.concatenate(P)[:n]


def one(gname, rho, p, r_min, rng):
    grid = T.Grid(gname); top = T.top_of(p); h = T.hulls(top, rho); t0 = time.time()
    reps, info = T.build(grid, top, rho, r_min)
    lam = grid.upto(2.5)
    B = np.concatenate([np.column_stack([reps[:, 0] + lx, reps[:, 1] + ly, reps[:, 2], reps[:, 3]]) for lx, ly in lam])
    c2 = max(0.25 - rho * rho, 0.0); w = side_w(gname, top, rho, h['HB'])
    near = np.hypot(np.hypot(B[:, 0] - 0.5, B[:, 1]), B[:, 2] - top) - B[:, 3] < 1.6
    B = B[near]
    res = []
    for f in (1.0, 1.03):
        deep, n_in, a, R = reach_in(B, top, c2, f * w)
        P = points_in(rng, 40000, top, c2, f * w)
        st = T.recipe(P[:, 0], P[:, 1], P[:, 2], grid, top, rho, 300)
        res.append((deep, n_in, int((st == 1).sum()), int((st == -1).sum()), a, R))
    ok = res[0][1] == 0 and res[0][2] == 0
    say('%-6s rho %-7.4g p %-8.2f top %-7.4f %7d balls >= %.0e | side spindle w %.4f (a %.4f, R %.4f): %d listed balls reach in (deepest %.2g), of 40000 points the recipe calls %d INSIDE, %d undecided after 300 rounds: %s'
        ' | 3 %% wider: %d reach in (deepest %.2g), %d INSIDE | %.0f s'
        % (gname, rho, p, top, info['n'], T.SLACK * r_min, w, res[0][4], res[0][5], res[0][1], max(res[0][0], 0.0), res[0][2], res[0][3], 'HOLDS' if ok else 'FAILS',
           res[1][1], max(res[1][0], 0.0), res[1][2], time.time() - t0))
    return ok, (res[1][1] > 0 or res[1][2] > 0)


if __name__ == '__main__':
    quick = len(sys.argv) > 1 and sys.argv[1] == 'quick'
    say('Round 28, the fixer: the side spindle on lists of balls (%s).' % ('quick' if quick else 'full'))
    SETS = [(0.5, 20.0), (0.5, 60.0), (0.5, 100.0), (0.5, 150.0), (0.5, 199.0), (0.5, 200.0), (0.499, 150.0), (0.495, 101.0), (0.49, 150.0), (0.49, 204.0), (0.45, 222.0),
            (0.4, 60.0), (0.4, 250.0), (1 / 3, 150.0), (1 / 3, 300.0), (0.25, 300.0), (0.25, 400.0), (0.2, 80.0), (0.125, 400.0), (0.05, 1000.0), (0.02, 400.0)]
    if quick:
        SETS = [(0.5, 60.0), (0.5, 150.0), (0.5, 200.0), (0.49, 150.0), (1 / 3, 150.0), (0.25, 400.0)]
    rng = np.random.default_rng(28)
    n = good = tight = 0
    for gname in ('square', 'hex', 'line'):
        for rho, p in SETS:
            ok, wider_fails = one(gname, rho, p, 4e-5 if gname == 'line' else (2.5e-3 if quick else 1.2e-3), rng)
            n += 1; good += ok; tight += wider_fails
        say('')
    say('%d settings. The side spindle HOLDS in %d. A spindle 3 %% wider fails in %d (where it does not, w is not the largest that would do; that is safe).' % (n, good, tight))
