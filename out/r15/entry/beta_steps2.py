"""Newton for beta started from the root of the quadratic part (an upper bound, exact to beta^3)."""
import sys, numpy as np
sys.path.insert(0, 'out/me/r15')
import pillow_ref as R

def newton(px, py, steps, dt=np.float64):
    px = px.astype(dt); py = py.astype(dt)
    X = 4 * px * px; Y = py * py
    c = 1 - X - 2 * Y; a = 2 - Y
    s = np.sqrt(c * c + 4 * a * Y)
    with np.errstate(divide='ignore', invalid='ignore'):
        bq = np.where(c >= 0, 2 * Y / (c + s), (s - c) / (2 * a))
    b = np.minimum(np.minimum(dt(1), px * px + Y), bq)
    for _ in range(steps):
        q = 1 + b
        g = b * q * q - X * b - Y * q * q
        dg = q * (q + 2 * b - 2 * Y) - X
        ok = (g > 0) & (dg > 0)
        with np.errstate(divide='ignore', invalid='ignore'):
            nb = np.maximum(b - g / dg, 0)
        b = np.where(ok, nb, b)
    b = np.where(Y > 0, b, np.maximum(0, 2 * np.abs(px) - 1))
    return b.astype(np.float64)

rng = np.random.default_rng(5)
d = rng.normal(size=(400000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
# add points crowded round the corners, the seams and the equator
e = d[:60000].copy(); e[:, 2] *= 1e-3; e /= np.linalg.norm(e, axis=1)[:, None]
f = np.zeros((60000, 3)); f[:, 0] = 0.8 * np.sign(rng.normal(size=60000)) + 0.02 * rng.normal(size=60000) * rng.uniform(size=60000) ** 3; f[:, 1] = 0.02 * rng.normal(size=60000) * rng.uniform(size=60000) ** 3; f[:, 2] = 0.6 * np.sign(rng.normal(size=60000)); f /= np.linalg.norm(f, axis=1)[:, None]
d = np.concatenate([d, e, f])
den = 1 + np.abs(d[:, 2]); px, py = d[:, 0] / den, d[:, 1] / den
ref = R.solve_beta(px, py)
for dt in (np.float64, np.float32):
    for k in (0, 1, 2, 3, 4, 5, 6, 8, 12):
        b = newton(px, py, k, dt)
        e = np.abs(b - ref); eB = np.abs(np.sqrt(b) - np.sqrt(ref))
        print(dt.__name__, 'steps', k, 'beta err: max %.2e  99.9%% %.2e  median %.2e ;  B err max %.2e 99.9%% %.2e' % (e.max(), np.quantile(e, .999), np.median(e), eB.max(), np.quantile(eB, .999)))
