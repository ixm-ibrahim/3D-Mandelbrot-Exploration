import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'me', 'r15'))
import shadow_ref as R, gauge_proto as GP
rng = np.random.default_rng(5)
D = rng.normal(size=(200000, 3)); D /= np.linalg.norm(D, axis=1)[:, None]
n = 2
want = R.gauge(D[:, 0], D[:, 1], D[:, 2], n)
got = GP.gauge_newton(D, n, 16)
k = np.argsort(-np.abs(got - want))[:3]
c0, s0 = R.consts(n)
for i in k:
    X, Y, Z = D[i]
    print('d', D[i], 'want', want[i], 'got', got[i])
    zb, zt = (1 - c0) / s0, (1 + c0) / s0
    lo = max(abs(X), -Z / zb, Z / zt, 0)
    xs = np.linspace(lo, 1.74, 15)
    def G(r):
        x2 = c0 * r - s0 * Z
        return (r * r - X * X) * (r * r - x2 * x2) - (Y * (r - c0 * x2) / s0) ** 2
    print('  lo', lo, ' G:', ' '.join('%.3f:%.2e' % (x, G(x)) for x in xs))
    print('  roots', np.roots(np.polyfit(xs, G(xs), 4)))
