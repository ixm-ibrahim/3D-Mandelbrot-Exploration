"""Shadow, round 15B: the gauge rho by safeguarded Newton, tried in numpy (float64 and float32) against the
reference's bisection (out/me/r15/shadow_ref.py). Picks the number of steps for MATH.pillow4d and the shader."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'me', 'r15'))
import shadow_ref as R


def gauge_newton(d, n, steps, dt=np.float64):
    """rho of unit directions d (N x 3): Newton from the top of the bracket, bisection when a step leaves it."""
    c0, s0 = [dt(v) for v in R.consts(n)]
    if n == 3:
        c0, s0 = dt(0), dt(1)
    X, Y, Z = [d[:, i].astype(dt) for i in range(3)]
    zb, zt = (1 - c0) / s0, (1 + c0) / s0
    a = np.maximum(np.maximum(np.abs(X), -Z / zb), np.maximum(Z / zt, dt(0)))
    b = np.full_like(X, max(zb, zt) * dt(1.0001))
    x = b.copy()
    Y2 = Y * Y
    for _ in range(steps):
        A = (1 - c0) * x + s0 * Z; B = (1 + c0) * x - s0 * Z; C = s0 * x + c0 * Z; q = x * x - X * X
        g = q * A * B - Y2 * C * C
        dg = 2 * x * A * B + q * ((1 - c0) * B + (1 + c0) * A) - 2 * s0 * Y2 * C
        pos = g > 0
        b = np.where(pos, x, b); a = np.where(pos, a, x)
        with np.errstate(divide='ignore', invalid='ignore'):
            xn = x - g / dg
        bad = ~(dg > 0) | ~(xn >= a) | ~(xn <= b)
        xn = np.where(bad, dt(0.5) * (a + b), xn)
        x = np.where(g == 0, x, xn)
    return x


if __name__ == '__main__':
    rng = np.random.default_rng(5)
    D = rng.normal(size=(200000, 3)); D /= np.linalg.norm(D, axis=1)[:, None]
    # delicate directions: beside the plane y = 0 (both seams lie in it), the corners, the plane z = 0
    E = rng.normal(size=(100000, 3)); E[:, 1] *= 10.0 ** rng.uniform(-9, -1, 100000); E /= np.linalg.norm(E, axis=1)[:, None]
    for n in (2, 3, 4, 5, 7, 10):
        for name, P in (('anywhere', D), ('beside y = 0', E)):
            want = R.gauge(P[:, 0], P[:, 1], P[:, 2], n)
            row = []
            for steps in (6, 8, 10, 12, 16, 24):
                e64 = np.abs(gauge_newton(P, n, steps) - want).max()
                e32 = np.abs(gauge_newton(P, n, steps, np.float32).astype(float) - want).max()
                row.append('%d: %.1e / %.1e' % (steps, e64, e32))
            print('n = %2d, %-12s rho %.3f to %.3f | steps: float64 / float32 error  %s' % (n, name, want.min(), want.max(), ' | '.join(row)))
