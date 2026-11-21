"""Round 27, measure: do my tools agree with round 25's? (run first)

    python out/r27/measure/check.py        -> check.log
1. my recipe against out/r25/klein/tree.py (M.stay), three grids, three t;
2. my list of balls against the recipe (random points of the box), three grids;
3. my true flat picture against mem.flat_stay;
4. timing of a known-good case.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r25', 'klein'))
import ballkit as K
import tree as T25
M = K.M

LOG = open(os.path.join(HERE, 'check.log'), 'w')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); LOG.write(s + '\n'); LOG.flush()


rng = np.random.default_rng(11); n = 100000
P = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3))
t0 = time.time()
ref = M.stay(T25.tree('gauss'), P[:, 0], P[:, 1], P[:, 2], 0.0, 0.0, 0.0, 14) >= 14
say('timing of the known-good case (round 25 tree, 100000 points, 14 rounds): %.1f s' % (time.time() - t0))
say('1. my recipe against round 25 tree.py (100000 random points of the box, 40 rounds)')
for lat in ('line', 'gauss', 'eisen'):
    for t in (1.0, 1.4, 2.5):
        a = M.stay(T25.tree(lat, t=t), P[:, 0], P[:, 1], P[:, 2], 0.0, 0.0, 0.0, 40) >= 40
        b = K.inside_picture(P[:, 0], P[:, 1], P[:, 2], K.Grid(lat), 2 * t, 40)
        say('   %-5s t = %.1f: inside %.4f / %.4f, verdicts that differ %d, undecided by mine %d' % (lat, t, a.mean(), (b == 1).mean(), int((a != (b == 1)).sum()), int((b < 0).sum())))
say('2. my list of balls against my recipe (the same points; balls of radius >= 0.002 in the picture)')
for lat in ('line', 'gauss', 'eisen'):
    t = 1.4; g = K.Grid(lat); t1 = time.time()
    reps, info = K.build(g, K.recipe_gens(2 * t), 2 * t, rho_min=3e-4)
    B = K.picture(reps, g, 2 * t, r_min=0.002)
    b = K.inside_picture(P[:, 0], P[:, 1], P[:, 2], g, 2 * t, 40) == 1
    a = K.in_balls(P, B)
    miss = b & ~a; extra = a & ~b
    say('   %-5s: %d balls mod slides (%d levels, %.1f s), %d balls in the picture; inside by recipe %.4f, by balls %.4f; in a ball but outside by recipe: %d; inside by recipe but in no listed ball: %d'
        % (lat, info['n'], info['levels'], time.time() - t1, len(B), b.mean(), a.mean(), int(extra.sum()), int(miss.sum())))
    cnt, deep = K.overlaps(B)
    say('          balls that overlap (1500 largest against all): %d pairs, deepest %.2e' % (cnt, deep))
say('3. my true flat picture against mem.flat_stay (c = -1, 300 steps, 100000 points)')
a = M.flat_stay(P[:, 0], P[:, 1], -1.0, 0.0, 300) >= 300; b = K.julia(P[:, 0], P[:, 1], -1.0, 0.0, 300)
say('   verdicts that differ: %d' % int((a != b).sum()))
