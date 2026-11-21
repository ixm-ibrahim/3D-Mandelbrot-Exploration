"""Shadow, round 15B: the gauge rho, second try. The quartic is written as
    (rho - |X|)(rho - rs) K(rho) = Y^2 C(rho)^2          rs: where the seam bound sits, K > 0 and C > 0 slowly varying
and solved as the fixed point  rho = m + sqrt(d^2 + R(rho)),  R = Y^2 C^2 / K,  m, d = half sum, half difference of
|X| and rs, by Newton on  phi(rho) = rho - m - sqrt(d^2 + R(rho)).  Near a seam or a corner the two largest roots of
the quartic run together, which slows plain Newton on the quartic to a halving per step; this form does not mind."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'me', 'r15'))
import shadow_ref as R


def consts(n, dt=np.float64):
    c0, s0 = R.consts(n)
    if n == 2: c0, s0 = -0.5, np.sqrt(0.75)
    if n == 3: c0, s0 = 0.0, 1.0
    if n == 5: c0, s0 = 0.5, np.sqrt(0.75)
    return dt(c0), dt(s0)


def gauge_fp(d, n, steps, dt=np.float64, newton=True):
    c0, s0 = consts(n, dt)
    X, Y, Z = [d[:, i].astype(dt) for i in range(3)]
    aX = np.abs(X); up = Z >= 0
    rs = np.where(up, s0 * Z / (1 + c0), -s0 * Z / (1 - c0))
    m = dt(0.5) * (aX + rs); dl = dt(0.5) * (aX - rs); d2 = dl * dl
    lo = np.maximum(aX, rs)
    hi = dt(max((1 - c0) / s0, (1 + c0) / s0) * 1.0001) * np.ones_like(X)
    Y2 = Y * Y
    x = np.maximum(lo, np.sqrt(X * X + Y2 + Z * Z) * dt(1.0))       # start: the plain length, or the lower bound
    x = np.minimum(x, hi)
    tiny = dt(1e-30)
    for _ in range(steps):
        C = s0 * x + c0 * Z
        E = np.where(up, (1 - c0) * x + s0 * Z, (1 + c0) * x - s0 * Z)      # the factor that stays positive
        kE = np.where(up, 1 + c0, 1 - c0); dE = np.where(up, 1 - c0, 1 + c0)
        K = np.maximum((x + aX) * kE * E, tiny)
        Rr = Y2 * C * C / K
        sq = np.sqrt(d2 + Rr)
        if newton:
            dR = Rr * (2 * s0 / np.maximum(C, tiny) - 1 / np.maximum(x + aX, tiny) - dE / np.maximum(E, tiny))
            dphi = 1 - dR / np.maximum(2 * sq, tiny)
            phi = x - m - sq
            xn = np.where(dphi > dt(0.2), x - phi / np.where(dphi > dt(0.2), dphi, 1), m + sq)
        else:
            xn = m + sq
        x = np.minimum(np.maximum(xn, lo), hi)
    return x


if __name__ == '__main__':
    rng = np.random.default_rng(5)
    D = rng.normal(size=(200000, 3)); D /= np.linalg.norm(D, axis=1)[:, None]
    E = rng.normal(size=(100000, 3)); E[:, 1] *= 10.0 ** rng.uniform(-9, -1, 100000); E /= np.linalg.norm(E, axis=1)[:, None]
    Fz = rng.normal(size=(100000, 3)); Fz[:, 2] *= 10.0 ** rng.uniform(-9, -1, 100000); Fz /= np.linalg.norm(Fz, axis=1)[:, None]
    Cn = rng.normal(size=(100000, 3)); Cn[:, 1] *= 10.0 ** rng.uniform(-9, -1, 100000)   # beside the corner directions
    for newton in (False, True):
        print('Newton on phi' if newton else 'plain fixed point')
        for n in (2, 3, 4, 5, 7, 10):
            c0, s0 = R.consts(n)
            Cn2 = Cn.copy(); top = rng.random(len(Cn)) < 0.5
            Cn2[:, 0] = np.sign(Cn[:, 0]) * (1 + 10.0 ** rng.uniform(-9, -1, len(Cn)) * rng.normal(size=len(Cn)))
            Cn2[:, 2] = np.where(top, (1 + c0) / s0, -(1 - c0) / s0) * (1 + 10.0 ** rng.uniform(-9, -1, len(Cn)) * rng.normal(size=len(Cn)))
            Cn2 /= np.linalg.norm(Cn2, axis=1)[:, None]
            for name, P in (('anywhere', D), ('beside y = 0', E), ('beside z = 0', Fz), ('beside corners', Cn2)):
                want = R.gauge(P[:, 0], P[:, 1], P[:, 2], n)
                row = []
                for steps in (2, 3, 4, 5, 6, 8, 12):
                    e64 = np.abs(gauge_fp(P, n, steps, newton=newton) - want).max()
                    e32 = np.abs(gauge_fp(P, n, steps, np.float32, newton=newton).astype(float) - want).max()
                    row.append('%d: %.0e/%.0e' % (steps, e64, e32))
                print('n = %2d, %-14s steps: float64/float32  %s' % (n, name, ' | '.join(row)))
