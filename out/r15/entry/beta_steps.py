"""How many Newton steps does beta need, started from an upper bound? (double and float32)"""
import sys, numpy as np
sys.path.insert(0, 'out/me/r15')
import pillow_ref as R

def newton(px, py, steps, dt=np.float64):
    px = px.astype(dt); py = py.astype(dt)
    X = 4 * px * px; Y = py * py
    b = np.minimum(dt(1), px * px + Y)
    with np.errstate(divide='ignore', invalid='ignore'):
        b = np.where(X < 1, np.minimum(b, Y / (1 - X)), b)
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
den = 1 + np.abs(d[:, 2]); px, py = d[:, 0] / den, d[:, 1] / den
ref = R.solve_beta(px, py)
for dt in (np.float64, np.float32):
    for k in (2, 3, 4, 5, 6, 8, 12, 20, 40):
        b = newton(px, py, k, dt)
        e = np.abs(b - ref); eB = np.abs(np.sqrt(b) - np.sqrt(ref))
        print(dt.__name__, 'steps', k, 'beta err: max %.2e  99.9%% %.2e  median %.2e ;  B err max %.2e 99.9%% %.2e' % (e.max(), np.quantile(e, .999), np.median(e), eB.max(), np.quantile(eB, .999)))
