import sys, os, time, numpy as np
rng = np.random.default_rng(3)
v = rng.normal(size=(1000000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
x, y, z = v[:, 0].copy(), v[:, 1].copy(), v[:, 2].copy()
den = 1 + np.abs(z); px, py = x / den, y / den
a = 0.5; oa = 0.5
px2 = px * px; py2 = py * py
for start in ('one', 'p2'):
    n = px2.size
    b = np.ones(n) if start == 'one' else np.minimum(1.0, px2 + py2)
    lo = np.zeros(n); hi = np.ones(n)
    t0 = time.time()
    for it in range(30):
        A = a + oa * b; A2 = A * A
        g = b * A2 - px2 * b - py2 * A2
        gp = A2 + 2 * oa * A * (b - py2) - px2
        pos = g > 0
        hi = np.where(pos, b, hi); lo = np.where(pos, lo, b)
        nb = b - g / gp
        bad = ~((nb >= lo) & (nb <= hi))
        nb = np.where(bad, 0.5 * (lo + hi), nb)
        conv = np.abs(nb - b) <= 3e-16 * nb + 1e-300
        b = nb
        print(start, it, 'not converged', int((~conv).sum()), 'bisected', int(bad.sum()), '%.2f s' % (time.time() - t0))
