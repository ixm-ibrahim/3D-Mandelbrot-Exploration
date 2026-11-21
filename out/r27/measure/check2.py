"""Round 27, measure: three small facts re-measured that the notes rely on.  -> check2.log

1. The flat cut (z = 0) of the 3D object is the 'line' object (round 25 measured it; here again with my recipe).
2. How many rounds of the recipe decide every point (t = 1.4, square grid).
3. Which t goes with which c in the best fits (from fit-table.npz and fit2.json).
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K

log = open(os.path.join(HERE, 'check2.log'), 'w')


def say(s):
    print(s); log.write(s + '\n'); log.flush()


rng = np.random.default_rng(3); n = 200000
u, s = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
for t in (1.0, 1.4, 2.5):
    ref = K.inside_picture(u, s, 0 * u, K.Grid('line'), 2 * t, 60)
    for lat in ('gauss', 'eisen'):
        a = K.inside_picture(u, s, 0 * u, K.Grid(lat), 2 * t, 60)
        say('1. flat cut of the 3D object (%s, t = %.1f) against the line object: %d verdicts differ of %d (undecided %d)' % (lat, t, int((a != ref).sum()), n, int((a < 0).sum() + (ref < 0).sum())))
P = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(n, 3)); g = K.Grid('gauss')
ref = K.inside_picture(P[:, 0], P[:, 1], P[:, 2], g, 2.8, 80)
for k in (2, 3, 4, 6, 8):
    a = K.inside_picture(P[:, 0], P[:, 1], P[:, 2], g, 2.8, k)
    say('2. %d rounds: undecided %d of %d; decided differently from 80 rounds: %d' % (k, int((a < 0).sum()), n, int(((a >= 0) & (a != ref)).sum())))
z = np.load(os.path.join(HERE, 'fit-table.npz')); f2 = json.load(open(os.path.join(HERE, 'fit2.json')))
say('3. best setting for each c (share wrong, width of the middle ball, t)')
for ci, c in enumerate(z['cs']):
    e = z['err'][ci]; a, b = np.unravel_index(np.argmin(e), e.shape); r = f2.get('%.3f' % c)
    say('   c = %+.2f: %5.1f%%  k2 = %.2f  t = %.2f%s' % (c, 100 * e[a, b], z['k2s'][b], z['ts'][a], ('   | finer search: %.1f%%  k2 = %.2f  t = %.2f' % (100 * r[0], r[1], r[2])) if r else ''))
