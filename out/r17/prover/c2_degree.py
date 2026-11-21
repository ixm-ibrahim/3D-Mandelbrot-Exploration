"""Prover, claim C2: numbers that check the theorem (not bench work; known rules only, read from the scouts).

For each rule: the map it induces on the sphere of directions D(u) = F(u) / |F(u)|.
  degree      = how many times D wraps the sphere over itself, counted with sign (integral of the signed area stretch / 4 pi)
  reversed    = share of the sphere's area where D turns the surface over (signed area stretch < 0): folding
  cover       = total area of the image counted without sign / 4 pi (how many layers on average)
  W-, W+      = how many times the sideways part of the answer turns when the point goes once round the negative / positive x-axis
  speed       = fastest and slowest turning rate d(sigma)/d(phi) round the negative x-axis (1 or -1 = keeps shape; 3 = shapes stretched 3 to 1)

    python out/r17/prover/c2_degree.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import scout as S, scout2 as S2, scout3 as S3


def lathe(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def mandelbulb(x, y, z):
    p2 = x * x + y * y
    q = np.where(p2 > 0, p2, 1.0)
    k = (p2 - z * z) / q
    return k * (x * x - y * y), k * 2 * x * y, 2 * z * np.sqrt(p2)


RULES = [('oneplane', S.oneplane), ('lathe', lathe), ('twoplane (torn)', S.twoplane), ('along', S3.turning(1)), ('away', S3.turning(-1)),
         ('wind2', S2.wind(2)), ('mandelbulb n=2', mandelbulb)]


def unit(F, T, P):
    """direction of F at the direction (colatitude T from +x, azimuth P round the x-axis)."""
    x, y, z = np.cos(T), np.sin(T) * np.cos(P), np.sin(T) * np.sin(P)
    X, Y, Z = F(x, y, z)
    n = np.sqrt(X * X + Y * Y + Z * Z)
    return np.stack([X / n, Y / n, Z / n])


def degree(F, nt=1500, npz=3000, h=2e-6):
    t = (np.arange(nt) + 0.5) * np.pi / nt
    p = (np.arange(npz) + 0.5) * 2 * np.pi / npz
    T, P = np.meshgrid(t, p, indexing='ij')
    D = unit(F, T, P)
    Dt = (unit(F, T + h, P) - unit(F, T - h, P)) / (2 * h)
    Dp = (unit(F, T, P + h) - unit(F, T, P - h)) / (2 * h)
    J = np.einsum('i...,i...->...', D, np.cross(Dt, Dp, axis=0))        # signed area stretch times sin T
    cell = (np.pi / nt) * (2 * np.pi / npz)
    area = np.sin(T) * cell
    deg = J.sum() * cell / (4 * np.pi)
    cover = np.abs(J).sum() * cell / (4 * np.pi)
    rev = area[J < 0].sum() / (4 * np.pi)
    return deg, cover, rev, J, T, P


def winding(F, sign, eps=1e-3, n=40000):
    ph = np.arange(n + 1) * 2 * np.pi / n
    X, Y, Z = F(np.full_like(ph, sign * 1.0), eps * np.cos(ph), eps * np.sin(ph))
    sig = np.unwrap(np.arctan2(Z, Y))
    W = (sig[-1] - sig[0]) / (2 * np.pi)
    sp = np.gradient(sig, ph)
    return W, sp.min(), sp.max()


if __name__ == '__main__':
    print('%-16s %8s %7s %9s %7s %7s   %s' % ('rule', 'degree', 'cover', 'reversed', 'W-', 'W+', 'turning speed round the negative x-axis (min, max)'))
    keep = {}
    for name, F in RULES:
        deg, cover, rev, J, T, P = degree(F)
        Wm, lo, hi = winding(F, -1)
        Wp, _, _ = winding(F, +1)
        print('%-16s %8.3f %7.3f %8.1f%% %7.2f %7.2f   %.2f, %.2f' % (name, deg, cover, 100 * rev, Wm, Wp, lo, hi), flush=True)
        keep[name] = (J < 0)
    np.savez_compressed(os.path.join(HERE, 'c2_reversed.npz'), **{k.split()[0]: v[::3, ::3] for k, v in keep.items()})
