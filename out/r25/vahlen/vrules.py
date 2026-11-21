"""Round 25, section "vahlen": the squares that quaternion arithmetic of sphere inversions offers.

A point of space is v = x + y i + z j (no k part). Every chain of sphere inversions is v -> (a v + b)(c v + d)^-1
with quaternions a, b, c, d (Vahlen). The chains that keep 0 and infinity are the turn-and-scale maps
w -> a w a*, with a* = a with the sign of its k part flipped. Such a map sends the base point 1 to a a*.
So a point v is "the turn-and-scale that carries 1 to v", written as a quaternion a with a a* = v. a is the SPINOR
of v. It is fixed only up to a phase: a and a e^(k t) give the same v (first roll about the x-axis, then turn).

    square of v  =  what v's own turn-and-scale does to v  =  a (a a*) a*  =  (a a)(a a)*  =  the point of a squared.

Rules here (each returns the square WITHOUT c):
  lathe_b(beta)  every one-term quaternion product (v b v, v b v-bar, ...) that keeps space and is z^2 on the flat
                 plane is this: the quaternion square about an axis lying in the flat plane (beta = 0: the Lathe).
  holo           the one quadratic spinor rule that needs no phase and is exact: the two complex halves of the
                 spinor (taken about the upright axis) are squared one by one.  = (x^2 - y^2, 2xy, 2 z |v|).
  spin(start)    the quaternion square of the spinor, a -> a a, with the phase CARRIED along the orbit: after c is
                 added, the spinor is moved to the new point by the shortest turn-and-scale (no extra roll).
                 start = how the very first spinor is chosen: 'V' (no k part: shortest turn from the x-axis; the
                 choice is undefined on the negative x-axis) or 'up' (tip up by the latitude, then turn by the
                 longitude; undefined on the upright axis), plus a phase offset in degrees.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

TINY = 1e-300


# ---------------------------------------------------------------- quaternions as 4 arrays (1, i, j, k)
def qmul(p, q):
    a0, a1, a2, a3 = p; b0, b1, b2, b3 = q
    return (a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
            a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
            a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
            a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0)


def star(p):                                    # reversion: keeps 1, i, j and flips k. Space = the quaternions with p* = p
    return p[0], p[1], p[2], -p[3]


def conj(p):
    return p[0], -p[1], -p[2], -p[3]


def qsqrt(m):
    """Principal square root (the one nearest to 1). On the negative real axis: i times the root of the length."""
    m0, m1, m2, m3 = m; n = np.sqrt(m0 * m0 + m1 * m1 + m2 * m2 + m3 * m3)
    d = 2 * (n + m0); ok = d > 1e-24 * np.maximum(n, TINY); s = np.sqrt(np.where(ok, d, 1.0))
    return (np.where(ok, (m0 + n) / s, 0.0), np.where(ok, m1 / s, np.sqrt(n)), np.where(ok, m2 / s, 0.0), np.where(ok, m3 / s, 0.0))


def point_of(a):
    """The point of a spinor: a a* (its k part is 0 up to rounding)."""
    return qmul(a, star(a))


# ---------------------------------------------------------------- fixed rules
def lathe(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def oneplane(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); f = r2 / np.maximum(r2 + z * z, TINY)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * z * r


def lathe_b(beta_deg):
    """R(-2 beta) o Lathe o R(beta), R = turn about the upright axis: (z^2 - t^2 e^(-2 i beta), 2 t Re(e^(i beta) z))."""
    b = np.radians(beta_deg); cb, sb = np.cos(b), np.sin(b); c2, s2 = np.cos(2 * b), np.sin(2 * b)

    def F(x, y, z):
        t2 = z * z
        return x * x - y * y - t2 * c2, 2 * x * y + t2 * s2, 2 * z * (cb * x - sb * y)
    return F


def holo(x, y, z):
    return x * x - y * y, 2 * x * y, 2 * z * np.sqrt(x * x + y * y + z * z)


# ---------------------------------------------------------------- the carried spinor
def lift_V(x, y, z):
    return qsqrt((x, y, z, np.zeros_like(x)))


def lift_up(x, y, z):
    """sqrt(r) e^(i lon / 2) e^(j lat / 2): tip up by the latitude, then turn about the upright axis by the longitude."""
    r = np.sqrt(x * x + y * y + z * z); lon = np.arctan2(y, x); lat = np.arctan2(z, np.hypot(x, y)); s = np.sqrt(r)
    p = (np.cos(lon / 2), np.sin(lon / 2), 0 * x, 0 * x); q = (np.cos(lat / 2), 0 * x, np.sin(lat / 2), 0 * x)
    a = qmul(p, q)
    return tuple(s * t for t in a)


def roll(a, deg):
    t = np.radians(deg); return qmul(a, (np.cos(t) + 0 * a[0], 0 * a[0], 0 * a[0], np.sin(t) + 0 * a[0]))


def carry(b, w, c):
    """The spinor b sits over the point w = b b*. Move it to w + c by the shortest turn-and-scale: g b, g = sqrt((w + c) w^-1)."""
    w0, w1, w2 = w; n2 = w0 * w0 + w1 * w1 + w2 * w2; ok = n2 > TINY; d = np.where(ok, n2, 1.0)
    zero = np.zeros_like(w0)
    m = qmul((w0 + c[0], w1 + c[1], w2 + c[2], zero), (w0 / d, -w1 / d, -w2 / d, zero))
    g = qsqrt(m); a = qmul(g, b)
    fresh = lift_V(c[0] + zero, c[1] + zero, c[2] + zero)          # the orbit sat exactly on 0: nothing to carry
    return tuple(np.where(ok, t, f) for t, f in zip(a, fresh))


def spin(start='V', offset=0.0, name=None, label=None):
    lift0 = {'V': lift_V, 'up': lift_up}[start]

    def step(x, y, z, st, k, cx, cy, cz):
        a = st
        if k == 0:
            a = lift0(x, y, z)
            if offset:
                a = roll(a, offset)
        b = qmul(a, a); w = point_of(b)
        return w[0], w[1], w[2], carry(b, w[:3], (cx, cy, cz))
    nm = name or ('spin-%s%s' % (start, ('+%g' % offset) if offset else ''))
    return M.Rule(nm, label or 'the spinor is squared and its phase is carried along the orbit (first spinor: %s)' % start,
                  step, init=lambda n: tuple(np.zeros(n) for _ in range(4)))


def R_lathe(): return M.fixed(lathe, 'lathe', 'the quaternion square v v')
def R_lathe_b(b): return M.fixed(lathe_b(b), 'lathe %g' % b, 'the quaternion product square about the flat axis at %g degrees' % b)
def R_holo(): return M.fixed(holo, 'holo', 'spinor halves squared one by one: (x^2 - y^2, 2xy, 2 z |v|)')
def R_one(): return M.fixed(oneplane, 'one plane', 'the baseline: sphere inversions, one plane')


SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]
