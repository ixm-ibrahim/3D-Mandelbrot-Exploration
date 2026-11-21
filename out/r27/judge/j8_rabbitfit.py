"""Judge, check 8: the best the balls object's flat cut can do against the true rabbit.
Free: the dial t, the size, a turn and a shift of the picture. Random starts, then a downhill search.
Measure: area(object xor true) / area(true), on 60000 random points; the best is re-measured on the 900 x 650 grid."""
import sys, time
import numpy as np
from scipy.optimize import minimize
import jlib as J

rng = np.random.default_rng(2708); n = 60000
x, y = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); T = J.truth(x, y, J.RABBIT, 600)
gx, gy = J.grid_xy(900, 650); TG = J.truth(gx, gy, J.RABBIT, 600)


def obj(p, xx, yy):
    t, k2, th, dx, dy = p; t = max(t, 1.0); k2 = max(k2, 0.05)
    co, si = np.cos(th), np.sin(th); u = co * (xx - dx) + si * (yy - dy); v = -si * (xx - dx) + co * (yy - dy)
    return J.balls(u, v, 0 * u, t=t, grid='line', k2=k2, rounds=30) == 1


def err(p):
    return J.wrong_share(obj(p, x, y), T)


t0 = time.time(); starts = []
for _ in range(600):
    p = np.array([rng.uniform(1.02, 3.0), rng.uniform(0.4, 1.6), rng.uniform(0, np.pi), rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4)])
    starts.append((err(p), p))
starts.sort(key=lambda v: v[0]); print('600 random starts: best five %s (%.0f s)' % (', '.join('%.3f' % s[0] for s in starts[:5]), time.time() - t0)); sys.stdout.flush()
best = (9e9, None)
for e0, p0 in starts[:12]:
    r = minimize(err, p0, method='Nelder-Mead', options=dict(xatol=1e-3, fatol=1e-4, maxiter=400,
                 initial_simplex=np.vstack([p0] + [p0 + d for d in np.diag([0.15, 0.1, 0.15, 0.08, 0.08])])))
    if r.fun < best[0]:
        best = (r.fun, r.x)
    print('   start %.3f -> %.3f at t = %.2f, middle ball %.2f wide, turn %.0f degrees, shift (%.2f, %.2f)  (%.0f s)'
          % (e0, r.fun, max(r.x[0], 1), r.x[1], np.degrees(r.x[2]) % 180, r.x[3], r.x[4], time.time() - t0)); sys.stdout.flush()
fine = J.wrong_share(obj(best[1], gx, gy), TG)
print('best chain of balls against the true rabbit: %.1f of 100 parts of the true area wrong (on the grid; %.1f in the search)' % (100 * fine, 100 * best[0]))
print('for scale: one plain disc fitted the same way:')
bd = (9e9, None)
for _ in range(400):
    p = np.array([rng.uniform(0.2, 0.9), rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4)])
    e = J.wrong_share((x - p[1]) ** 2 + (y - p[2]) ** 2 < p[0] ** 2, T)
    if e < bd[0]:
        bd = (e, p)
r = minimize(lambda p: J.wrong_share((x - p[1]) ** 2 + (y - p[2]) ** 2 < p[0] ** 2, T), bd[1], method='Nelder-Mead')
print('   %.1f of 100 parts wrong (radius %.2f)' % (100 * r.fun, r.x[0]))
np.save(J.os.path.join(J.HERE, 'cache', 'rabbitfit-best.npy'), best[1])
