"""Judge, check 2: how far is the flat cut of the balls object from the true flat pictures?
Measure: area(object xor true) / area(true), on a 900 x 650 grid of the box (-1.8..1.8, -1.3..1.3).
The dial k2 is nothing but the size of the picture, so the search over (k2, t) runs on 80000 random points."""
import sys, time
import numpy as np
import jlib as J

gx, gy = J.grid_xy(900, 650)
rng = np.random.default_rng(2703); n = 80000
x, y = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)


def obj(xx, yy, k2, t):
    return J.balls(xx, yy, 0 * xx, t=t, grid='line', k2=k2, rounds=40) == 1


cs = [(-1.0, 300), (-0.95, 400), (-0.9, 400), (-0.86, 500), (-0.84, 500), (-0.82, 500), (-0.8, 600), (-0.75, 3000), (-0.7, 600), (-0.5, 300), (-1.1, 400), (-1.25, 3000)]
if len(sys.argv) > 1:
    cs = [(float(a), 600) for a in sys.argv[1:]]
A0 = obj(gx, gy, 1.05, 1.40)
print('object at the lab setting (k2 = 1.05, t = 1.40): share of the box inside %.4f' % A0.mean())
for c, steps in cs:
    t0 = time.time(); T = J.truth(gx, gy, c, steps); Tr = J.truth(x, y, c, steps)
    lab = J.wrong_share(A0, T)
    best = (9e9, 0, 0)
    for t in np.r_[np.arange(1.02, 1.60, 0.02), np.arange(1.6, 3.01, 0.1)]:
        for k2 in np.arange(0.80, 1.61, 0.02):
            e = J.wrong_share(obj(x, y, k2, t), Tr)
            if e < best[0]:
                best = (e, k2, t)
    fine = J.wrong_share(obj(gx, gy, best[1], best[2]), T)
    print('c = %+.2f: true area share %.4f | lab setting: %.1f of 100 wrong | best over both dials: %.1f of 100 (on the grid; %.1f in the search) at middle ball %.2f wide, t = %.2f | %.0f s'
          % (c, T.mean(), 100 * lab, 100 * fine, 100 * best[0], best[1], best[2], time.time() - t0)); sys.stdout.flush()
