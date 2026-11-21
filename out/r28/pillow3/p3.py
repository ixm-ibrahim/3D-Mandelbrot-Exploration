"""Round 28, Track B: the three-corner pillow with ONE corner on the flat circle ("pillow3").

The pillow: the plane of z folded by  z ~ z + 1,  z ~ z + w,  z ~ w z   (w = a third of a turn). Three corners, each
missing two thirds of a turn: 0, a = 1/2 + i / (2 sqrt 3), and conj(a). The direction map is DOUBLING, z -> 2 z.
The belt is the real axis from 0 to 1: it runs through the corner 0 (direction +x) and has the corner a on one side
and conj(a) on the other. On the belt x -> 2 x, so with longitude = 2 pi x the flat circle is doubled exactly.

Layout (pillow <-> ball of directions), in two steps:
  1. the angle-true (conformal) picture of the pillow on the ball: corner 0 at +x, the point 1/2 at -x, the corners
     a, conj(a) at the two poles, the belt on the flat circle. In the coordinate q = tan(s/2) e^(i f)  (s = angle from
     +x, f = angle round the x-axis, f = 0 toward +y, f = 90 toward +z) doubling is the rational map
         q -> 8 q / (1 - 18 q^2 - 27 q^4)                                   (derived in NOTES.md, checked in checks.py)
     In this picture the belt is NOT run through at even speed: the belt point x sits at the angle s with
         2 pi x = S(s) = pi K * integral_0^s sin(u/2)^(-2/3) du,   K = Gamma(2/3) / (sqrt(pi) Gamma(1/6)).
  2. the re-timing E, in circles about the x-axis:  (s, f) -> (S(s), f - (1 - k(s)) sin(2 f) / 2),
         k(s) = S'(s) sin(s) / sin(S(s)).
     S makes the belt even (the flat cut becomes exact). The second part keeps the layout angle-true to first order
     all along the belt, so a point just beside the flat plane is pushed off it by exactly 2 at EVERY longitude.
     At the corner k = 1/3 and the second part is round 25's paper formula  b -> 3 b - sin(6 b) / 3  with distance kept.
  fan=False leaves the second part out (k = 1): the belt is still exact, but the push beside the flat plane is uneven.

    G(X, Y, Z) = E( R( E^-1 (X, Y, Z) ) ),      F(v) = |v|^2 G(v / |v|),       rule() -> M.Rule

    python out/r28/pillow3/p3.py        prints the self-test of the tables
"""
import os, sys
from math import gamma, pi, sqrt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

KB = gamma(2 / 3) / (sqrt(pi) * gamma(1 / 6))
CS = pi * KB * 3 * 2 ** (2 / 3)
TMAX = pi ** (1 / 3)
N = 8193


def _dS(t):                                    # dS / dt, t = s^(1/3)
    u = 0.5 * t ** 3
    return CS * np.where(u > 1e-8, np.sin(u) / np.where(u > 1e-8, u, 1.0), 1.0 - u * u / 6) ** (-2 / 3)


def _build():
    t = np.linspace(0.0, TMAX, N); h = t[1] - t[0]
    gx, gw = np.polynomial.legendre.leggauss(10)
    mid = 0.5 * (t[:-1] + t[1:])
    cell = sum(w * _dS(mid + 0.5 * h * x) for x, w in zip(gx, gw)) * 0.5 * h
    Sv = np.concatenate([[0.0], np.cumsum(cell)])
    err_total = Sv[-1] - pi
    Sv *= pi / Sv[-1]                          # the total is pi (checked: the raw sum is pi to 1e-13)
    dS = _dS(t)
    # inverse table: t as a function of S on an even grid of S
    Sg = np.linspace(0.0, pi, N); tg = np.interp(Sg, Sv, t)
    for _ in range(6):
        tg = np.clip(tg - (_herm(tg, t, Sv, dS) - Sg) / _dS(tg), 0.0, TMAX)
    tg[0], tg[-1] = 0.0, TMAX
    dtg = 1.0 / _dS(tg)
    # k on the t grid
    s = t ** 3
    with np.errstate(divide='ignore', invalid='ignore'):
        k = pi * KB * np.sin(0.5 * s) ** (-2 / 3) * np.sin(s) / np.sin(Sv)
    k[0] = 1 / 3; k[-1] = 1.0
    k[1:4] = np.where(np.isfinite(k[1:4]), k[1:4], 1 / 3)
    return dict(t=t, S=Sv, dS=dS, Sg=Sg, tg=tg, dtg=dtg, k=k, err_total=err_total)


def _herm(x, xg, f, df):
    """Cubic Hermite interpolation on an even grid."""
    n = xg.size - 1; h = xg[1] - xg[0]
    u = np.clip((x - xg[0]) / h, 0.0, n); i = np.minimum(u.astype(np.int64), n - 1); s = u - i
    f0, f1, d0, d1 = f[i], f[i + 1], df[i] * h, df[i + 1] * h
    s2 = s * s; s3 = s2 * s
    return (2 * s3 - 3 * s2 + 1) * f0 + (s3 - 2 * s2 + s) * d0 + (-2 * s3 + 3 * s2) * f1 + (s3 - s2) * d1


TAB = _build()


def S_of_t(t):
    return _herm(t, TAB['t'], TAB['S'], TAB['dS'])


def t_of_S(S):
    return _herm(S, TAB['Sg'], TAB['tg'], TAB['dtg'])


def k_of_t(t):
    return np.interp(t, TAB['t'], TAB['k'])


def kepler(Mm, e):
    """psi with psi - e sin(psi) = Mm."""
    p = Mm + e * np.sin(Mm)
    for _ in range(9):
        p = p - np.clip((p - e * np.sin(p) - Mm) / (1 - e * np.cos(p)), -1.0, 1.0)
    return p


def E_inv(X, Y, Z, fan=True):
    """Direction -> (t, f) of the angle-true picture; s = t^3."""
    s = np.arctan2(np.sqrt(Y * Y + Z * Z), X); f = np.arctan2(Z, Y)
    t = t_of_S(s)
    if fan:
        f = 0.5 * kepler(2 * f, 1 - k_of_t(t))
    return t, f


def E_fwd(t, f, fan=True):
    s = S_of_t(t)
    if fan:
        f = f - 0.5 * (1 - k_of_t(t)) * np.sin(2 * f)
    sn = np.sin(s)
    return np.cos(s), sn * np.cos(f), sn * np.sin(f)


def R_tf(t, f):
    """Doubling on the pillow, in the angle-true picture: (t, f) -> (t', f')."""
    s = t ** 3; near = s <= 0.5 * pi
    m = np.where(near, np.tan(0.5 * np.minimum(s, 0.5 * pi)), np.tan(0.5 * (pi - np.maximum(s, 0.5 * pi))))   # |q| or 1 / |q|
    q = m * np.exp(1j * np.where(near, f, -f)); q2 = q * q
    num = np.where(near, 8 * q, 8 * q2 * q)
    den = np.where(near, 1 - 18 * q2 - 27 * q2 * q2, q2 * q2 - 18 * q2 - 27)
    s2 = 2 * np.arctan2(np.abs(num), np.abs(den))
    f2 = np.angle(num * np.conj(den))
    return np.cbrt(s2), f2


def G(X, Y, Z, fan=True):
    t, f = E_inv(X, Y, Z, fan)
    return E_fwd(*R_tf(t, f), fan)


def F(x, y, z, fan=True):
    sh = np.shape(x); x, y, z = (np.ravel(np.asarray(v, float)) for v in (x, y, z))
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); ok = r > 0; ri = 1 / np.where(ok, r, 1.0)
    dx, dy, dz = G(x * ri, y * ri, z * ri, fan)
    ox, oy, oz = dx * r2, dy * r2, dz * r2
    flat = z == 0
    if flat.any():                                  # on the flat plane itself: the flat rule, to the last digit
        wv = (x[flat] + 1j * y[flat]) ** 2
        ox[flat], oy[flat], oz[flat] = wv.real, wv.imag, 0.0
    ox[~ok] = 0; oy[~ok] = 0; oz[~ok] = 0
    return ox.reshape(sh), oy.reshape(sh), oz.reshape(sh)


def rule(fan=True):
    if fan:
        return M.fixed(lambda x, y, z: F(x, y, z, True), 'pillow3', 'three-corner pillow, one corner on the flat circle, even push')
    return M.fixed(lambda x, y, z: F(x, y, z, False), 'pillow3-plain', 'three-corner pillow, one corner on the flat circle, plain re-timing')


def pre_q(q):
    """The four q with R(q) = the given q (conformal coordinate, q = tan(s/2) e^(i f))."""
    if np.isinf(q):
        return np.roots([-27, 0, -18, 0, 1])
    return np.roots([-27 * q, 0, -18 * q, -8, q])


def dir_of_q(q, fan=True):
    """Direction (X, Y, Z) of the conformal coordinate q, after the re-timing."""
    s = 2 * np.arctan(np.abs(q)); f = np.angle(q)
    return np.array(E_fwd(np.cbrt(np.array([s])), np.array([f]), fan)).ravel()


if __name__ == '__main__':
    print('K = %.12f; the raw integral of S over the half belt misses pi by %.1e' % (KB, TAB['err_total']))
    t = np.random.default_rng(1).uniform(0, TMAX, 200000)
    print('round trip t -> S -> t: largest error %.1e' % np.abs(t_of_S(S_of_t(t)) - t).max())
    print('k: smallest %.6f, largest %.6f; at s = 1, 30, 90, 150, 179 degrees: %s' % (TAB['k'].min(), TAB['k'].max(), ', '.join('%.4f' % float(k_of_t(np.cbrt(np.radians(a)))) for a in (1, 30, 90, 150, 179))))
    print('S at s = 30, 60, 90, 120, 150 degrees: %s degrees' % ', '.join('%.3f' % np.degrees(float(S_of_t(np.cbrt(np.radians(a))))) for a in (30, 60, 90, 120, 150)))
