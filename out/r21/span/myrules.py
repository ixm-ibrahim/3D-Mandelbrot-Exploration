"""Round 21, agent "span": planes that the orbit MAKES, which need not go through the x-axis.

Two vectors from the origin span a plane. The point is squared INSIDE a plane that holds it:
    the plane's "real axis" a = the direction in the plane nearest to the positive x-axis
                              = the x-direction pressed flat into the plane, made one long
    square of v inside the plane = double the angle of v from a (inside the plane), square the length
                                 = 2 (a.v) v - |v|^2 a          (the mirror image of a in the line of v, times |v|^2)
A plane is kept as a unit normal n; n and -n are the same plane and every formula here gives the same for both.

    import sys; sys.path.insert(0, 'out/r21/span'); import myrules as R;  R.RULES, R.get('prev_page')

The carried state of every rule here is nine arrays: the normal n of the carried plane (starts as the flat page,
n = (0, 0, 1)), the point before (starts as 0 = "none"), and a carried real axis (starts as +x; only the rule
prev_axis reads it).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
P = M.S.oneplane


# ------------------------------------------------------------------ planes
def n_page(x, y, z):
    """Normal of the plane through the point (and 0) that lies nearest to the flat page: it holds the point and the
    level direction (-y, x, 0). For a point on the z-axis (every such plane is as near as any other): the x-z plane."""
    rho2 = x * x + y * y; d = np.sqrt(rho2) * np.sqrt(rho2 + z * z); ok = d > 1e-200; m = np.where(ok, d, 1.0)
    return np.where(ok, -x * z / m, 0.0), np.where(ok, -y * z / m, 1.0), np.where(ok, rho2 / m, 0.0)


def n_lathe(x, y, z):
    """Normal of the point's own sheet through the x-axis (for a point on the x-axis: the flat page)."""
    d = np.hypot(y, z); ok = d > 1e-200; m = np.where(ok, d, 1.0)
    return 0.0 * x, np.where(ok, -z / m, 0.0), np.where(ok, y / m, 1.0)


def n_made(x, y, z, wx, wy, wz, fb, tol=1e-9):
    """Normal of the plane spanned by the point and its partner w. Where the two are parallel (the sine of the angle
    between them below tol, or one of them 0) the plane is not defined and the normal fb() is used instead
    (fb is a function, called only if it is needed). Returns the normal and the mask of the places where the plane was defined."""
    a, b, c = y * wz - z * wy, z * wx - x * wz, x * wy - y * wx
    n = np.sqrt(a * a + b * b + c * c)
    ok = n > tol * np.sqrt((x * x + y * y + z * z) * (wx * wx + wy * wy + wz * wz)); ok &= n > 1e-200
    if ok.all():
        return a / n, b / n, c / n, ok
    m = np.where(ok, n, 1.0); f = fb()
    return np.where(ok, a / m, f[0]), np.where(ok, b / m, f[1]), np.where(ok, c / m, f[2]), ok


def tilt(n1, n2, n3, x, y, z):
    """Turn the plane the least that makes it hold the point: n - (n.v) v / |v|^2, made one long.
    Where the point stands square to the plane (nothing left): the plane through the point nearest the flat page."""
    r2 = x * x + y * y + z * z; t = (n1 * x + n2 * y + n3 * z) / np.maximum(r2, 1e-300)
    a, b, c = n1 - t * x, n2 - t * y, n3 - t * z
    n = np.sqrt(a * a + b * b + c * c); ok = n > 1e-9
    if ok.all():
        return a / n, b / n, c / n
    m = np.where(ok, n, 1.0); f = n_page(x, y, z)
    return np.where(ok, a / m, f[0]), np.where(ok, b / m, f[1]), np.where(ok, c / m, f[2])


def blend(n1, n2, n3, m1, m2, m3, lam):
    """Move the plane n the share lam of the way toward the plane m. A plane has no front and back, so m is first
    given the sign that makes it the nearer of its two normals. Costs a jump where the planes are square to each other."""
    s = np.where(n1 * m1 + n2 * m2 + n3 * m3 >= 0, 1.0, -1.0)
    a, b, c = (1 - lam) * n1 + lam * s * m1, (1 - lam) * n2 + lam * s * m2, (1 - lam) * n3 + lam * s * m3
    n = np.sqrt(a * a + b * b + c * c)
    return a / n, b / n, c / n


def real_axis(n1, n2, n3, o=(1.0, 0.0, 0.0), tol=1e-8):
    """The direction in the plane nearest to o (default: the positive x-axis): o pressed into the plane, one long.
    Where the plane is square to o (nothing left) the direction nearest to +y is used, and if that fails too, +z.
    o may be three arrays (a carried axis). Returns the axis and the mask of the places where it was defined."""
    d = o[0] * n1 + o[1] * n2 + o[2] * n3
    a1, a2, a3 = o[0] - d * n1, o[1] - d * n2, o[2] - d * n3; s = np.sqrt(a1 * a1 + a2 * a2 + a3 * a3); ok = s > tol
    if ok.all():
        return a1 / s, a2 / s, a3 / s, ok
    b1, b2, b3 = -n2 * n1, 1 - n2 * n2, -n2 * n3; t = np.sqrt(b1 * b1 + b2 * b2 + b3 * b3); ok2 = t > tol
    c1, c2, c3 = -n3 * n1, -n3 * n2, 1 - n3 * n3; u = np.maximum(np.sqrt(c1 * c1 + c2 * c2 + c3 * c3), 1e-300)
    s_, t_ = np.where(ok, s, 1.0), np.where(ok2, t, 1.0)
    return (np.where(ok, a1 / s_, np.where(ok2, b1 / t_, c1 / u)), np.where(ok, a2 / s_, np.where(ok2, b2 / t_, c2 / u)),
            np.where(ok, a3 / s_, np.where(ok2, b3 / t_, c3 / u)), ok)


# ------------------------------------------------------------------ the two squarings
def sq_in(x, y, z, a1, a2, a3):
    """Square the point inside the plane it spans with the real axis a: 2 (a.v) v - |v|^2 a.
    Written through the two coordinates (along a, across a) so that for a = (1, 0, 0) and z = 0 it is complex squaring
    to the last bit."""
    al = a1 * x + a2 * y + a3 * z
    b1, b2, b3 = x - al * a1, y - al * a2, z - al * a3
    be = np.sqrt(b1 * b1 + b2 * b2 + b3 * b3); m = np.where(be > 0, be, 1.0)
    b1, b2, b3 = b1 / m, b2 / m, b3 / m
    re, im = al * al - be * be, 2 * al * be
    return re * a1 + im * b1, re * a2 + im * b2, re * a3 + im * b3


def P_about(x, y, z, n1, n2, n3, a=None):
    """The one-plane rule P about the plane n (its real axis as above). The point need not lie in the plane.
    For a point IN the plane this is the same as sq_in."""
    a1, a2, a3 = (a if a is not None else real_axis(n1, n2, n3))[:3]
    b1, b2, b3 = n2 * a3 - n3 * a2, n3 * a1 - n1 * a3, n1 * a2 - n2 * a1
    A, B, C = P(x * a1 + y * a2 + z * a3, x * b1 + y * b2 + z * b3, x * n1 + y * n2 + z * n3)
    return A * a1 + B * b1 + C * n1, A * a2 + B * b2 + C * n2, A * a3 + B * b3 + C * n3


def init(n):
    o, e = np.zeros(n), np.ones(n)
    return (o.copy(), o.copy(), e.copy(), o.copy(), o.copy(), o.copy(), e.copy(), o.copy(), o.copy())


# ------------------------------------------------------------------ the family
def make(name, label, partner='c', conv='page', lam=1.0, mode='in', delay=False, first=None, axis='x'):
    """partner  what the point makes its plane with:
                 'c'        the constant c
                 'prev'     the point before it (two consecutive points of the orbit)
                 'guessP'   its own image under the one-plane rule on the flat page (a fixed rule, no memory)
                 'guessPc'  that image plus c (the guessed next point)
                 'guessN'   its own image under the one-plane rule about the CARRIED plane
                 'guessNc'  that image plus c
       conv     the plane where the made plane is not defined (the point parallel to its partner, or no partner yet):
                 'page'   the plane through the point nearest to the flat page
                 'lathe'  the point's own sheet through the x-axis
                 'keep'   the carried plane, turned the least that makes it hold the point
       lam      the share of the way the carried plane moves toward the made one before the squaring (1 = all the way)
       mode     'in'  the (moved) plane is turned the least that makes it hold the point, and the point is squared inside it
                'P'   the one-plane rule about the (moved) plane as it stands (the point need not lie in it)
       delay    True: the point is squared by P about the carried plane as it was, and the plane moves afterwards
       first    'P': the very first squaring of an orbit is the one-plane rule on the flat page
       axis     'x'  the plane's real axis is the direction in it nearest to +x
                'carry'  ... nearest to the real axis of the step before (which starts as +x)
    """
    def step(x, y, z, st, k, cx, cy, cz):
        n1, n2, n3, px, py, pz, o1, o2, o3 = st
        if first == 'P' and k == 0:
            X, Y, Z = P(x, y, z)
            return X, Y, Z, (n1, n2, n3, x, y, z, o1, o2, o3)
        if partner == 'c':
            w = (cx, cy, cz)
        elif partner == 'prev':
            w = (px, py, pz)
        elif partner in ('guessP', 'guessPc'):
            w = P(x, y, z)
        else:
            w = P_about(x, y, z, n1, n2, n3)
        if partner in ('guessPc', 'guessNc'):
            w = (w[0] + cx, w[1] + cy, w[2] + cz)
        if conv == 'page':
            fb = lambda: n_page(x, y, z)
        elif conv == 'lathe':
            fb = lambda: n_lathe(x, y, z)
        elif mode == 'P':
            fb = lambda: (n1, n2, n3)
        else:
            fb = lambda: tilt(n1, n2, n3, x, y, z)
        m1, m2, m3, _ = n_made(x, y, z, *w, fb)
        if delay:
            X, Y, Z = P_about(x, y, z, n1, n2, n3)
            q = (m1, m2, m3) if lam >= 1 else blend(n1, n2, n3, m1, m2, m3, lam)
            return X, Y, Z, (*q, x, y, z, o1, o2, o3)
        q = (m1, m2, m3) if lam >= 1 else blend(n1, n2, n3, m1, m2, m3, lam)
        if mode == 'in':
            if lam < 1:
                q = tilt(*q, x, y, z)
            a = real_axis(*q) if axis == 'x' else real_axis(*q, o=(o1, o2, o3))
            X, Y, Z = sq_in(x, y, z, a[0], a[1], a[2])
            return X, Y, Z, (*q, x, y, z, a[0], a[1], a[2])
        X, Y, Z = P_about(x, y, z, *q)
        return X, Y, Z, (*q, x, y, z, o1, o2, o3)
    return M.Rule(name, label, step, init)


def _roll(x, y, z, st, k, cx, cy, cz):
    """The carried plane is turned along with the point: by the least turn that takes the direction of the point
    before into the direction of this point (a turn inside the plane of the two consecutive points). Then the
    one-plane rule about the carried plane. Where the point before is missing, 0 or exactly opposite: the plane stays."""
    n1, n2, n3, px, py, pz, o1, o2, o3 = st
    rp = np.sqrt(px * px + py * py + pz * pz); rq = np.sqrt(x * x + y * y + z * z); ok = (rp > 1e-200) & (rq > 1e-200)
    mp, mq = np.where(ok, rp, 1.0), np.where(ok, rq, 1.0)
    p1, p2, p3, q1, q2, q3 = px / mp, py / mp, pz / mp, x / mq, y / mq, z / mq
    d = 1 + p1 * q1 + p2 * q2 + p3 * q3; ok &= d > 1e-9; d = np.where(ok, d, 1.0)
    s1, s2, s3 = p1 + q1, p2 + q2, p3 + q3
    t = (s1 * n1 + s2 * n2 + s3 * n3) / d; u = 2 * (p1 * n1 + p2 * n2 + p3 * n3)
    m1, m2, m3 = n1 - t * s1 + u * q1, n2 - t * s2 + u * q2, n3 - t * s3 + u * q3
    nn = np.sqrt(m1 * m1 + m2 * m2 + m3 * m3); nn = np.where(ok & (nn > 0.5), nn, 1.0)
    m1, m2, m3 = np.where(ok, m1 / nn, n1), np.where(ok, m2 / nn, n2), np.where(ok, m3 / nn, n3)
    X, Y, Z = P_about(x, y, z, m1, m2, m3)
    return X, Y, Z, (m1, m2, m3, x, y, z, o1, o2, o3)


RULES = [
    # --- the point and c
    make('c_lathe', 'Plane of the point and c; where undefined: the point\'s own sheet', 'c', 'lathe'),
    make('c_page', 'Plane of the point and c; where undefined: the plane through the point nearest the flat page', 'c', 'page'),
    make('c_Pfirst', 'Plane of the point and c; the first squaring is the one-plane rule on the flat page', 'c', 'page', first='P'),
    make('c_lag50', 'One-plane rule about a carried plane that moves half way to the plane of the point and c', 'c', 'keep', lam=0.5, mode='P'),
    # --- the point and the point before it
    make('prev_lathe', 'Plane of the point and the point before; first step: the point\'s own sheet', 'prev', 'lathe'),
    make('prev_page', 'Plane of the point and the point before; first step: the plane through the point nearest the flat page', 'prev', 'page'),
    make('prev_keep', 'Plane of the point and the point before; where undefined: the plane it had, tilted to hold the point', 'prev', 'keep'),
    make('prev_Pfirst', 'Plane of the point and the point before; the first squaring is the one-plane rule on the flat page', 'prev', 'page', first='P'),
    make('prev_axis', 'Plane of the point and the point before; the real axis is carried along too', 'prev', 'page', axis='carry'),
    make('prev_lag50in', 'Carried plane moves half way to the plane of the last two points, is tilted to hold the point; squared inside', 'prev', 'keep', lam=0.5),
    make('prev_lag50P', 'One-plane rule about a carried plane that moves half way to the plane of the last two points', 'prev', 'keep', lam=0.5, mode='P'),
    make('prev_lag25P', 'One-plane rule about a carried plane that moves a quarter of the way to the plane of the last two points', 'prev', 'keep', lam=0.25, mode='P'),
    make('prev_delay', 'One-plane rule about the plane of the two points BEFORE this one', 'prev', 'keep', mode='P', delay=True),
    # --- the point and its own image under a first guess
    make('guessP', 'Plane of the point and its image under the one-plane rule on the flat page (no memory)', 'guessP', 'page'),
    make('guessPc', 'Plane of the point and its guessed next point (one-plane rule on the flat page, plus c)', 'guessPc', 'page'),
    make('guessN', 'Plane of the point and its image under the one-plane rule about the carried plane', 'guessN', 'keep'),
    make('guessNc', 'Plane of the point and its guessed next point (one-plane rule about the carried plane, plus c)', 'guessNc', 'keep'),
    # --- extras: smaller lags, and the plane of two consecutive points used as the plane of a TURN
    make('c_lag10', 'One-plane rule about a carried plane that moves a tenth of the way to the plane of the point and c', 'c', 'keep', lam=0.1, mode='P'),
    make('c_lag25', 'One-plane rule about a carried plane that moves a quarter of the way to the plane of the point and c', 'c', 'keep', lam=0.25, mode='P'),
    make('prev_lag10P', 'One-plane rule about a carried plane that moves a tenth of the way to the plane of the last two points', 'prev', 'keep', lam=0.1, mode='P'),
    M.Rule('roll', 'One-plane rule about a carried plane that is turned along with the point (the turn from the last point to this one)', _roll, init),
]


def get(name):
    return next(r for r in RULES if r.name == name)
