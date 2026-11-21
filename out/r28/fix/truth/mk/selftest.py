"""Round 28, truth checker: does my own measuring tool measure right?

  python out/r28/fix/truth/mk/selftest.py      -> out/r28/fix/truth/logs/selftest.txt

1. The test "the ball of radius E about a picture point meets no listed ball" (bc_page.over, by way of the object's own
   space and the list that repeats with the grid) and the distance found from it by halving (bc_page.true_dist),
   against brute force: every listed ball, slid by every whole number up to length 8, carried to the picture one by
   one as an explicit ball (centre, radius), and the plain distance from the point to each.
2. The recipe against the same explicit picture balls: a point is inside by the recipe exactly when it is inside one.
3. My honeycomb "nearest whole number" against brute force over 49 whole numbers.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
import bc_page as B

lines = []
def say(s):
    print(s, flush=True); lines.append(s)

rng = np.random.default_rng(5)
for gname, rho, p in (('square', 1 / 3, 150.0), ('hex', 0.2, 300.0), ('line', 0.5, 150.0), ('square', 1.0, 100 / 1.8)):
    grid = T.Grid(gname); top = T.top_of(p); r_min = 1.6e-2 if gname != 'line' else 1e-3
    reps, info = T.build(grid, top, rho, r_min); ix = T.Index(reps, grid, top)
    lam = grid.upto(8.0)
    c = (reps[:, None, :3] + np.concatenate([lam, np.zeros((len(lam), 1))], 1)[None]).reshape(-1, 3); r = np.repeat(reps[:, 3], len(lam))
    d = c - T.C0; den = (d * d).sum(1) - r * r; assert (den > 0).all()
    uc = T.K2 * d / den[:, None]; rp = T.K2 * r / den
    PB = np.column_stack([uc[:, 2] + T.K2 / 2, uc[:, 0], uc[:, 1], rp])                    # explicit balls of the picture
    rU = T.K2 / (2 * (top - 1)); PB = np.concatenate([[[0, 0, 0, T.K2 / 2], [T.K2 / 2 + rU, 0, 0, rU]], PB])
    X = T.K2 / 2 + T.K2 * p / 100 + 0.4; Y = max(T.K2 / 2, T.K2 * p / 200) + 0.3
    P = np.column_stack([rng.uniform(-X, X, 1500), rng.uniform(-Y, Y, 1500), rng.uniform(-Y, Y, 1500) * (0.2 if gname == 'line' else 1.0)])
    brute = np.full(len(P), np.inf)
    for s in range(0, len(PB), 50000):
        q = PB[s:s + 50000]
        for k in range(0, len(P), 250):
            dd = np.sqrt(((P[k:k + 250, None, :] - q[None, :, :3]) ** 2).sum(2)) - q[None, :, 3]
            brute[k:k + 250] = np.minimum(brute[k:k + 250], dd.min(1))
    kiss = np.sqrt(((P - np.array([T.K2 / 2, 0, 0])) ** 2).sum(1))
    st = T.recipe(*T.frame(P[:, 0], P[:, 1], P[:, 2]), grid, top, rho, 200)
    # 2. verdicts (away from the place where balls beyond my 12 whole numbers lie, and from balls below the list's size)
    far = kiss > 0.4
    ins_b = brute < 0
    a = int(((st == 1) & ~ins_b & far).sum()); b = int(((st == 0) & ins_b).sum())
    # 1. distances, at outside points whose nearest explicit ball is nearer than the far balls I left out could be
    o = (st == 0) & (brute > 0) & (brute < kiss - 0.2)
    td = B.true_dist(P[o], 1.5 * brute[o] + 1e-6, ix, top, it=50)
    rel = np.abs(td - brute[o]) / brute[o]
    hit_at = B.over(P[o], brute[o] * (1 + 1e-6), ix, top, shrink=0.0)[0]; free_at = ~B.over(P[o], brute[o] * (1 - 1e-6), ix, top, shrink=0.0)[0]
    say('%-6s rho %.4g p %.2f: %d listed balls -> %d explicit picture balls. Distances at %d outside points: halving against brute force, largest relative difference %.1e; '
        '"meets a ball" at 1.000001 x the brute distance: %d of %d, at 0.999999 x: %d (must be all and none). Verdicts: outside by the recipe but in an explicit ball %d; inside by the recipe, in none %d (those lie in balls below the list\'s size)'
        % (gname, rho, p, len(reps), len(PB), int(o.sum()), float(rel.max()), int(hit_at.sum()), int(o.sum()), int((~free_at).sum()), b, a))
# 3. the honeycomb's nearest whole number
g = T.Grid('hex'); q = rng.uniform(-6, 6, (200000, 2)); nx, ny = g.nearest(q[:, 0], q[:, 1])
lam = g.upto(9.0); best = np.full(len(q), np.inf); bx = np.zeros(len(q)); by = np.zeros(len(q))
for lx, ly in lam:
    d = (q[:, 0] - lx) ** 2 + (q[:, 1] - ly) ** 2; m = d < best; best = np.where(m, d, best); bx = np.where(m, lx, bx); by = np.where(m, ly, by)
say('honeycomb, nearest whole number at 200000 points against brute force: %d differ' % int(((np.abs(bx - nx) > 1e-9) | (np.abs(by - ny) > 1e-9)).sum()))
open(os.path.join(TRUTH, 'logs', 'selftest.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
