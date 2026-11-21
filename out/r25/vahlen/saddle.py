"""Why the carried spinor leaves no body off the flat plane: at the flat rule's attracting cycle the carried phase
grows. The 4 growth factors of one trip round the cycle, in spinor space. python out/r25/vahlen/saddle.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V


def G(a, c):
    a = tuple(np.atleast_1d(np.asarray(t, float)) for t in a)
    b = V.qmul(a, a); w = V.point_of(b); o = np.ones_like(a[0])
    return np.array([t[0] for t in V.carry(b, w[:3], (c[0] * o, c[1] * o, c[2] * o))])


def cycle_factors(c, period):
    z = 0j
    for _ in range(20000):
        z = z * z + complex(c[0], c[1])
    s = np.sqrt(z); a0 = np.array([s.real, s.imag, 0.0, 0.0])

    def trip(a):
        for _ in range(period):
            a = G(a, c)
        return a
    e = 1e-6; J = np.zeros((4, 4))
    for j in range(4):
        d = np.zeros(4); d[j] = e
        J[:, j] = (trip(a0 + d) - trip(a0 - d)) / (2 * e)
    lam = np.linalg.eigvals(J)
    mult = 1.0 + 0j; w = z
    for _ in range(period):
        mult *= 2 * w; w = w * w + complex(c[0], c[1])
    return z, np.sort(np.abs(lam))[::-1], abs(mult)


if __name__ == '__main__':
    for nm, c, p in (('c = -0.12 + 0.6i (inside the rabbit bulb)', (-0.12, 0.60, 0.0), 3), ('c = -0.10 + 0.70i (inside the rabbit bulb)', (-0.10, 0.70, 0.0), 3),
                     ('c = 0.2 + 0.3i (one body, attracting fixed point)', (0.2, 0.3, 0.0), 1), ('c = -0.9 + 0.05i (near the basilica)', (-0.9, 0.05, 0.0), 2),
                     ('c = -0.9 (on the x-axis)', (-0.9, 0.0, 0.0), 2)):
        z, lam, mult = cycle_factors(c, p)
        print('%s: cycle point %.4f%+.4fi, flat pull %.3f; growth factors of one trip in spinor space: %s' % (nm, z.real, z.imag, mult, ' '.join('%.3f' % t for t in lam)))
