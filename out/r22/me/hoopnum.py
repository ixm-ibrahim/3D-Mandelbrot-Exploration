"""Numbers for the hop-the-dots toy. Stand-alone formulas (the ones the toy will use), checked against the library.
    python out/r22/me/hoopnum.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M


def oneplane(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); den = r2 + z * z
    f = np.where(den > 0, r2 / np.where(den > 0, den, 1.0), 1.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def lathe(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def along(x, y, z):
    phi = np.arctan2(z, y); psi = phi - np.sin(4 * phi) / 4; c, s = np.cos(psi), np.sin(psi)
    y1 = y * c + z * s; z1 = -y * s + z * c
    X, Y1, Z1 = oneplane(x, y1, z1)
    return X, Y1 * c - Z1 * s, Y1 * s + Z1 * c


RULES = {'lathe': lambda k: lathe, 'oneplane': lambda k: oneplane, 'along': lambda k: along,
         'alongonce': lambda k: along if k == 0 else oneplane}


def run(name, x, y, z, c, hops, out=2.0):
    """alive[k] = number still within `out` of the centre after k hops; left[i] = hop at which dot i left (0 = never)"""
    x, y, z = x.copy(), y.copy(), z.copy(); alive = np.ones(x.shape, bool); left = np.zeros(x.shape, int); counts = []
    for k in range(hops):
        X, Y, Z = RULES[name](k)(x, y, z)
        x = np.where(alive, X + c[0], x); y = np.where(alive, Y + c[1], y); z = np.where(alive, Z + c[2], z)
        gone = alive & (x * x + y * y + z * z > out * out); left[gone] = k + 1; alive &= ~gone; counts.append(int(alive.sum()))
    return counts, left


def hoop(xc, rho, n=48):
    phi = np.arange(n) * 2 * np.pi / n
    return np.full(n, xc), rho * np.cos(phi), rho * np.sin(phi)


def main():
    # 1. the stand-alone formulas against the library, one squaring of random points
    rng = np.random.default_rng(3); p = rng.uniform(-1.2, 1.2, (3, 2000)); n = p.shape[1]; zero = np.zeros(n)
    for name, fn in (('lathe', lathe), ('oneplane', oneplane), ('along', along)):
        r = M.bench(name); X, Y, Z, _ = r.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(r.init(n)), 0, zero, zero, zero)
        a = fn(p[0], p[1], p[2]); print('formula check', name, 'largest difference %.2e' % max(np.abs(a[0] - X).max(), np.abs(a[1] - Y).max(), np.abs(a[2] - Z).max()))
    C = (-1.0, 0.0, 0.0)
    # 2. the hoop round the middle body
    print('\nhoop round the middle body (x = 0, radius 0.62), 48 dots: still here after k hops')
    for name in RULES:
        counts, left = run(name, *hoop(0.0, 0.62), C, 200)
        print('%-10s' % name, 'k=1 %d  5 %d  10 %d  20 %d  30 %d  40 %d  60 %d  80 %d  120 %d  200 %d' % tuple(counts[k - 1] for k in (1, 5, 10, 20, 30, 40, 60, 80, 120, 200)),
              ' last one leaves at hop', left.max(), ' survivors at', np.nonzero(left == 0)[0].tolist())
    # 3. other hoops: where do the rules differ most?
    for xc in (0.0, -1.0):
        print('\nhoops at x = %g: survivors of 48 after 200 hops, by radius' % xc)
        print('radius   ' + '  '.join('%-9s' % k for k in RULES))
        for rho in (0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.62, 0.65, 0.7):
            row = []
            for name in RULES:
                counts, left = run(name, *hoop(xc, rho), C, 200); row.append('%-9d' % counts[-1])
            print('%.2f     ' % rho + '  '.join(row))


if __name__ == '__main__':
    main()
