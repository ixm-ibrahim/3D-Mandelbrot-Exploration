"""Round 28, truth checker, section 1.4 a: IS IT AN OBJECT?

  python out/r28/truth/mk/a_object.py [quick]      -> out/r28/truth/logs/a_object.txt

For rho in {1, 0.5, 0.35, 0.2, 0.05}, p = f * 100 / rho with f from 0.05 to 1 (1 = the two spheres touch), all three
grids: my own list of balls (tkit.build), then
  1. no two listed balls cut into each other (every ball against every ball no larger, all slid copies, and the walls);
  2. at 20000 random points the recipe of section 1.1 (300 rounds) against "lies in a listed ball":
       a point the recipe calls OUTSIDE must lie in no listed ball;
       a point the recipe calls INSIDE lies in one ball, which I work out by walking the recipe backwards (tkit.ball_of);
       if that ball is at least as large as the list promises at that place it must BE in the list, to 1e-7.
     Points: 8000 in a box of the picture, 4000 anywhere between the walls, 4000 close above the bottom wall,
     4000 close to the second sphere.
Then rho = 0.7 (and a few more values the dial does not offer) with the same tool: do balls cut into each other?
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T

LOG = os.path.join(TRUTH, 'logs', 'a_object.txt')
QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'
out = []


def say(s=''):
    print(s, flush=True); out.append(s)
    with open(LOG, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')


def points(rng, grid, top, rho, p):
    h = T.hulls(top, rho)
    # 1: a box of the picture that holds the middle ball, both neighbours and a stretch beyond
    X = min(T.K2 / 2 + T.K2 * p / 100 + 0.4, 14.0); Y = min(max(T.K2 / 2, T.K2 * p / 200) + 0.25, 7.0)
    n1 = 8000
    px = rng.uniform(-X, X, n1); py = rng.uniform(-Y, Y, n1); pz = rng.uniform(-Y, Y, n1) if grid.name != 'line' else rng.uniform(-Y, Y, n1) * rng.integers(0, 2, n1)
    a = np.column_stack(T.frame(px, py, pz))
    # 2: anywhere between the walls   3: close above the bottom wall   4: close to the second sphere
    w = 0.75
    b = np.column_stack([rng.uniform(-w, w, 4000), rng.uniform(-w, w, 4000), rng.uniform(0, top, 4000)])
    c = np.column_stack([rng.uniform(-w, w, 4000), rng.uniform(-w, w, 4000), rng.uniform(0, 1.15 * h['HB'], 4000)])
    v = rng.normal(size=(4000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; v[:, 2] = -np.abs(v[:, 2])
    d = np.array([0.0, 0.0, top]) + v * (1.3 * rho * rng.uniform(0, 1, 4000) ** (1 / 3))[:, None]
    if grid.name == 'line':                      # the line grid: half of the points in the flat plane (my = 0), where the balls are widest
        for q in (b, c, d):
            q[::2, 1] *= 0.15
    return np.concatenate([a, b, c, d]), np.array([8000, 4000, 4000, 4000])


def one(gname, rho, f, r_min, rng, tag=''):
    grid = T.Grid(gname); p = f * 100.0 / rho; top = T.top_of(p); h = T.hulls(top, rho)
    t0 = time.time(); reps, info = T.build(grid, top, rho, r_min)
    ov = T.overlaps(reps, grid, top); t1 = time.time()
    ix = T.Index(reps, grid, top)
    P, parts = points(rng, grid, top, rho, p)
    st, chain = T.recipe(P[:, 0], P[:, 1], P[:, 2], grid, top, rho, 300, keep=True)
    inl = ix.holds(P)
    c, r, kind = T.ball_of(chain, grid, top, rho)
    ins = st == 1; outp = st == 0; und = st == -1
    wrong_out = int((outp & inl).sum())                       # OUTSIDE by the recipe, but in a listed ball
    isb = ins & (kind == 3)
    thr = T.threshold(c, r_min, grid, top, rho)
    must = isb & (r >= thr * (1 + 1e-6))
    found = np.full(len(P), -1); found[isb] = ix.find(c[isb], r[isb])
    missing = int((must & (found < 0)).sum())                 # its ball is large enough to be listed, and is not
    # the point must lie in its own ball
    own = np.sqrt(((P - c) ** 2).sum(1)) < r * (1 + 1e-9)
    notown = int((isb & ~own).sum())
    small = ins & ~inl                                         # INSIDE by the recipe, in no listed ball
    small_ok = int((small & isb & (r < thr * (1 + 1e-6))).sum()); small_bad = int((small & ~(isb & (r < thr * (1 + 1e-6)))).sum())
    walk = int((ins & (kind == 4)).sum())
    differ = int((ins != inl)[~und].sum())
    # the highest bud on the bottom wall and the deepest on the top wall, from the list, against the formulas
    nx, ny = grid.nearest(reps[:, 0], reps[:, 1]); topf = (reps[:, 0] - nx) ** 2 + (reps[:, 1] - ny) ** 2 + (reps[:, 2] - top) ** 2 < rho * rho
    hb = float((reps[~topf, 2] + reps[~topf, 3]).max()) if (~topf).any() else 0.0
    ht = float((top - reps[topf, 2] + reps[topf, 3]).max()) if topf.any() else 0.0
    ok = ov['pairs'] == 0 and ov['wall'] < 1e-9 and wrong_out == 0 and missing == 0 and small_bad == 0 and notown == 0 and walk == 0
    say('%s%-6s rho %-5g p %-9.4f top %-8.5f | %7d balls (>= %.1e, finer near the 2nd sphere), %3d levels | cut into each other: %d pairs (deepest %.2e), beyond a wall %.1e, twice in the list %d | '
        'points: inside %d, outside %d, undecided %d | OUTSIDE but in a listed ball: %d | INSIDE, ball large enough, not in the list: %d | INSIDE in no listed ball: %d (all below the list\'s size: %s) | '
        'verdict differs from the list at %d points | HB list %.6f formula %.6f, HT list %.6f formula %.6f | %.0f s | %s'
        % (tag, gname, rho, p, top, info['n'], T.SLACK * r_min, info['levels'], ov['pairs'], ov['deepest'], max(ov['wall'], 0.0), ov['dupes'],
           int(ins.sum()), int(outp.sum()), int(und.sum()), wrong_out, missing, small_ok + small_bad, 'yes' if small_bad == 0 else 'NO, %d are not' % small_bad,
           differ, hb, h['HB'], ht, h['HT'], time.time() - t0, 'HOLDS' if ok else 'FAILS'))
    return ok, ov


def bad_rho(gname, rho, p, r_min, rng):
    """A second sphere the dial does not offer: do the listed balls cut into each other, and how much of space lies in
    two balls at once?"""
    grid = T.Grid(gname); top = T.top_of(p)
    reps, info = T.build(grid, top, rho, r_min, cap=400_000)
    ov = T.overlaps(reps, grid, top)
    # a pair I can name: the first bud on the top wall (the image of the bottom wall) and its neighbours
    say('%-6s rho %-7g p %-8.3f top %-7.4f | %7d balls (>= %.1e) | pairs that cut into each other: %d, deepest %.4f (of a ball of radius %.4f) | %s'
        % (gname, rho, p, top, info['n'], T.SLACK * r_min, ov['pairs'], ov['deepest'], reps[ov['worst'][0], 3] if ov['worst'] else 0.0, 'OVERLAPS' if ov['pairs'] else 'no overlap found'))
    return ov


if __name__ == '__main__':
    rng = np.random.default_rng(2028_1120)
    say('Round 28, truth, 1.4 a. Lists hold every ball down to the size named (finer near the second sphere: see tkit.threshold).')
    say('')
    RHO = (1.0, 0.5, 0.35, 0.2, 0.05); F = (0.05, 0.3, 0.6, 0.9, 0.99, 1.0)
    if QUICK:
        RHO = (1.0, 0.2); F = (0.6, 0.99)
    allok = True; n = 0
    for gname in ('line', 'square', 'hex'):
        r_min = 4e-5 if gname == 'line' else (3e-3 if QUICK else 8e-4)
        for rho in RHO:
            for f in F:
                ok, _ = one(gname, rho, f, r_min, rng); allok &= ok; n += 1
        say('')
    say('ALL %d SETTINGS HOLD' % n if allok else 'SOME SETTINGS FAIL (see the lines marked FAILS)')
    say('')
    say('Second spheres the dial does not offer (between 50 and 100 % of the first):')
    for rho in (0.7, 0.6, 0.85):
        for gname in ('line', 'square', 'hex'):
            for p in (30.0, 100 / 1.8, 100.0, 0.95 * 100 / rho):
                bad_rho(gname, rho, p, 2e-4 if gname == 'line' else 8e-3, rng)
    say('')
    say('For comparison, the two ends of the gap with the same list sizes (50 and 100 %):')
    for rho in (0.5, 1.0):
        for gname in ('line', 'square', 'hex'):
            bad_rho(gname, rho, 100 / 1.8, 2e-4 if gname == 'line' else 8e-3, rng)
    say('')
    say('An aside (not offered, single values inside the gap): rho = 1 / sqrt(2) and sqrt(3) / 2')
    for rho in (np.sqrt(0.5), np.sqrt(3) / 2, 1 / np.sqrt(3)):
        for gname in ('line', 'square', 'hex'):
            bad_rho(gname, rho, 100 / 1.8, 2e-4 if gname == 'line' else 8e-3, rng)
