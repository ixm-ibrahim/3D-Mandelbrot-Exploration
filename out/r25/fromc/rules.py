"""Round 25, section "fromc": rules in which the flat picture does the choosing (they look at c, or the orbit
carries something along).

    import sys; sys.path.insert(0, 'out/r25/fromc'); import rules as R
    R.get('spin')         the orbit carries a quaternion that is turned by the turns the point makes
    R.get('prod')         the flat rule written from its two fixed-point arrows, multiplied the sphere-inversion way
    R.get('axis_every')   "along" about the line from 0 to the meeting point of c, at every step (round 22's alonghinge)
    R.get('axis_once')    the same at the first step only, then one plane
    R.get('axis_cycle')   the same once per round trip of c's cycle (when the orbit is in the body that holds 0)
    R.get('face4')        the copy-twice-round pattern (m = 4, t = -0.2) turned by c to face the meeting point
    R.get('face4m')       the same, and the length follows the sideways stretch instead of being squared
    R.get('m4m')          not turned by c, length follows the sideways stretch
    (more names in NAMES)

Axes: flat plane z = 0, x the real axis, z upright. Every rule returns the "square" WITHOUT c (the library adds c).
All rules read c through its flat part (cx, cy) only; cz is just added like any constant.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in ('out/r21/lib', 'out/r24/me'):
    sys.path.insert(0, os.path.join(ROOT, *p.split('/')))
import mem as M
import mfold as MF


# ------------------------------------------------------------------ small tools
def oneplane(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); d = r2 + z * z; f = np.where(d > 0, r2 / np.where(d > 0, d, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def lathe(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def along(x, y, z):
    phi = np.arctan2(z, y); psi = phi - 0.25 * np.sin(4 * phi); c, s = np.cos(psi), np.sin(psi)
    X, Y, Z = oneplane(x, c * y + s * z, -s * y + c * z)
    return X, c * Y - s * Z, s * Y + c * Z


def alpha(c):
    """The flat fixed point where the big bodies meet: (1 - sqrt(1 - 4c)) / 2."""
    return (1 - np.sqrt(1 - 4 * (c + 0j))) / 2


def qmul(a, b):
    a0, a1, a2, a3 = a; b0, b1, b2, b3 = b
    return (a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3, a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
            a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1, a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0)


# ------------------------------------------------------------------ 1. the carried quaternion
def spin_step(x, y, z, st, k, cx, cy, cz):
    """A point of space is v = Q i Q* (Q a quaternion; x, y, z are the i, j, k parts; the flat plane is i, j).
    Squaring: Q -> Q^2 (the turn that Q is, done twice). Adding c: the quaternion is turned by the shortest turn
    that takes the old direction to the new one and stretched to the new length. The first lift is the shortest turn
    from the x-axis to the point (its square is -v i, which has no bad direction)."""
    zero = 0 * x
    if k == 0:
        S = (x, zero, -z, y)                                   # Q0^2 = -v i
    else:
        S = qmul(st, st)
    Si = qmul(S, (zero, 1 + zero, zero, zero))
    _, X, Y, Z = qmul(Si, (S[0], -S[1], -S[2], -S[3]))          # v_s = S i S*
    nx, ny, nz = X + cx, Y + cy, Z + cz
    n = np.sqrt(nx * nx + ny * ny + nz * nz); ns = np.where(n > 0, n, 1.0)
    u = (zero, nx / ns, ny / ns, nz / ns)
    uSi = qmul(u, Si)
    A = tuple(S[i] - uSi[i] for i in range(4))                  # the part of S that lies over the new direction
    na = np.sqrt(sum(t * t for t in A)); ref = np.sqrt(sum(t * t for t in S))
    bad = na < 1e-9 * np.maximum(ref, 1e-300)
    if bad.any():                                               # new direction exactly opposite: take the flat choice
        kS = qmul((zero, zero, zero, 1 + zero), S)
        A = tuple(np.where(bad, kS[i], A[i]) for i in range(4)); na = np.where(bad, ref, na)
    na = np.where(na > 0, na, 1.0); f = np.sqrt(n) / na
    return X, Y, Z, tuple(f * t for t in A)


def _four(n):
    return (np.ones(n), np.zeros(n), np.zeros(n), np.zeros(n))


# ------------------------------------------------------------------ 2. the fixed-point product
def sph_product(ax, ay, az, bx, by, bz):
    """The sphere-inversion (one-plane) product of two arrows: lengths multiply, turns round the upright axis add,
    Mercator heights add. On the flat plane it is the complex product."""
    ra = np.sqrt(ax * ax + ay * ay + az * az); rb = np.sqrt(bx * bx + by * by + bz * bz)
    ras = np.where(ra > 0, ra, 1.0); rbs = np.where(rb > 0, rb, 1.0)
    mu = np.arctanh(np.clip(az / ras, -1 + 1e-15, 1 - 1e-15)) + np.arctanh(np.clip(bz / rbs, -1 + 1e-15, 1 - 1e-15))
    mu = np.clip(mu, -60.0, 60.0)
    pa = ax + 1j * ay; pb = bx + 1j * by; pr = pa * pb; m = np.abs(pr); e = np.where(m > 0, pr / np.where(m > 0, m, 1.0), 1.0 + 0j)
    L = ra * rb
    return L * e.real / np.cosh(mu), L * e.imag / np.cosh(mu), L * np.tanh(mu)


def prod_step(x, y, z, st, k, cx, cy, cz):
    """z^2 + c = a + (z - a)(z + a) with a the meeting point of c. In space: a + (v - a) * (v + a), * = sph_product."""
    a = alpha(cx + 1j * cy); a2 = a * a
    X, Y, Z = sph_product(x - a.real, y - a.imag, z, x + a.real, y + a.imag, z)
    return X + a2.real, Y + a2.imag, Z, st                      # a - c = a^2, and the library adds c


# ------------------------------------------------------------------ 3. "along" about the body's own axis
def meeting_turn(cx, cy):
    al = alpha(np.asarray(cx, float) + 1j * np.asarray(cy, float))
    a = np.where(np.abs(al) > 1e-12, np.angle(al), 0.0)
    return np.where(a > np.pi / 2, a - np.pi, np.where(a <= -np.pi / 2, a + np.pi, a))


def axis_along(x, y, z, cx, cy):
    a = meeting_turn(cx, cy); ca, sa = np.cos(a), np.sin(a)
    X, Y, Z = along(ca * x + sa * y, ca * y - sa * x, z)
    c2, s2 = np.cos(2 * a), np.sin(2 * a)
    return c2 * X - s2 * Y, s2 * X + c2 * Y, Z


def axis_every_step(x, y, z, st, k, cx, cy, cz):
    return (*axis_along(x, y, z, cx, cy), st)


def axis_once_step(x, y, z, st, k, cx, cy, cz):
    return (*(axis_along(x, y, z, cx, cy) if k == 0 else oneplane(x, y, z)), st)


_CYC = {}


def cycle_of(c):
    """Period and points of the cycle that the flat orbit of 0 settles on (the point nearest 0 first). (0, None) if none."""
    key = (round(c.real, 12), round(c.imag, 12))
    if key not in _CYC:
        zz = 0j; out = (0, None)
        for _ in range(20000):
            zz = zz * zz + c
            if abs(zz) > 1e6:
                break
        if abs(zz) < 1e6:
            w = zz
            for p in range(1, 65):
                w = w * w + c
                if abs(w - zz) < 1e-7:
                    pts = [zz]
                    for _ in range(p - 1):
                        pts.append(pts[-1] ** 2 + c)
                    pts = np.array(pts); out = (p, np.roll(pts, -int(np.argmin(np.abs(pts))))); break
        _CYC[key] = out
    return _CYC[key]


def axis_cycle_step(x, y, z, st, k, cx, cy, cz):
    """The turning-plane step about the body's own axis is taken only when the orbit is in the body that holds 0:
    once per round trip of the cycle. Which steps those are is read off the flat orbit of the start point's shadow."""
    c0 = complex(np.ravel(cx)[0], np.ravel(cy)[0]) if np.size(cx) else 0j
    same = np.size(cx) > 0 and np.all(cx == np.ravel(cx)[0]) and np.all(cy == np.ravel(cy)[0])
    p, cyc = cycle_of(c0) if same else (1, None)
    if p <= 1:
        return (*axis_along(x, y, z, cx, cy), st)
    if k == 0:
        zz = x + 1j * y; rec = zz.copy(); alive = np.ones(zz.shape, bool); N = p * int(np.ceil(48.0 / p))
        for n in range(1, N + 1):
            zz = np.where(alive, zz * zz + c0, zz); alive &= np.abs(zz) < 4.0
            if n % p == 0:
                rec = np.where(alive, zz, rec)
        j = np.argmin(np.abs(rec[:, None] - cyc[None, :]), axis=1).astype(float)   # the body class of the start
        st = (j,)
    j = st[0]
    turn = np.mod(k + j, p) < 0.5
    X1, Y1, Z1 = axis_along(x, y, z, cx, cy); X2, Y2, Z2 = oneplane(x, y, z)
    return np.where(turn, X1, X2), np.where(turn, Y1, Y2), np.where(turn, Z1, Z2), st


# ------------------------------------------------------------------ 4. patterns turned by c; length from the stretch
def pattern_rule(G, name, label, face=False, matched=False, cap=8.0, twin=False):
    """F(v) = L(v) * G_c(direction). face: the pattern of G is turned so that its longitude 0 faces the meeting point
    of c (G_c = Rot(2a) G Rot(-a)). matched: L = |v| ** max(2, s) with s the sideways stretch of G_c at that direction
    (the square root of its area stretch), so that a body is carried outward as fast as it is spread sideways."""
    def step(x, y, z, st, k, cx, cy, cz):
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); rs = np.where(r > 0, r, 1.0)
        ux, uy, uz = x / rs, y / rs, z / rs
        if face:
            a = alpha(cx + 1j * cy); n = np.abs(a); e = np.where(n > 0, a / np.where(n > 0, n, 1.0), 1.0 + 0j)
            co, si = e.real, e.imag
        else:
            co, si = 1.0, 0.0
        c2, s2 = co * co - si * si, 2 * co * si
        if twin:                                                   # z and -z have the same square: use the half of space
            sg = np.where(co * ux + si * uy < 0, -1.0, 1.0)        # that holds the meeting point (a half turn about the
            ux, uy = sg * ux, sg * uy                              # upright axis brings the other half onto it)

        def Gt(ax, ay, az):
            X, Y, Z = G(co * ax + si * ay, co * ay - si * ax, az)
            return c2 * X - s2 * Y, s2 * X + c2 * Y, Z
        X, Y, Z = Gt(ux, uy, uz)
        if matched:
            h = np.hypot(ux, uy); ok = h > 1e-9; hs = np.where(ok, h, 1.0)
            e1 = (np.where(ok, -uy / hs, 1.0), np.where(ok, ux / hs, 0.0), 0.0 * ux)
            e2 = (uy * e1[2] - uz * e1[1], uz * e1[0] - ux * e1[2], ux * e1[1] - uy * e1[0])
            eps = 2e-4
            A = Gt(ux + eps * e1[0], uy + eps * e1[1], uz + eps * e1[2]); B = Gt(ux + eps * e2[0], uy + eps * e2[1], uz + eps * e2[2])
            d1 = [(A[i] - (X, Y, Z)[i]) / eps for i in range(3)]; d2 = [(B[i] - (X, Y, Z)[i]) / eps for i in range(3)]
            cr = (d1[1] * d2[2] - d1[2] * d2[1], d1[2] * d2[0] - d1[0] * d2[2], d1[0] * d2[1] - d1[1] * d2[0])
            s = np.sqrt(np.sqrt(cr[0] ** 2 + cr[1] ** 2 + cr[2] ** 2))
            ex = 2.0 + np.clip(np.where(np.isfinite(s), s, 2.0) - 2.0 - 0.02, 0.0, cap - 2.0)   # exactly 2 beside the flat plane
            L = np.where(r > 0, rs ** ex, 0.0)
        else:
            L = r2
        ok0 = r > 0                                                # a point that has fallen onto 0 exactly stays a number
        return np.where(ok0, L * X, 0.0), np.where(ok0, L * Y, 0.0), np.where(ok0, L * Z, 0.0), st
    return M.Rule(name, label, step, init=lambda n: ())


def mdir(m, t, mu1=0.4):
    return lambda x, y, z: MF.mdir(x, y, z, m, t, mu1, True)


def stretch_of(G, lat_deg, lon_deg):
    """Sideways stretch (square root of the area stretch) of a direction map at given directions, in degrees."""
    la, lo = np.radians(np.asarray(lat_deg, float)), np.radians(np.asarray(lon_deg, float))
    ux, uy, uz = np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)
    e1 = (-np.sin(lo), np.cos(lo), 0 * lo); e2 = (-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la))
    eps = 2e-4; G0 = G(ux, uy, uz)
    A = G(ux + eps * e1[0], uy + eps * e1[1], uz + eps * e1[2]); B = G(ux + eps * e2[0], uy + eps * e2[1], uz + eps * e2[2])
    d1 = [(A[i] - G0[i]) / eps for i in range(3)]; d2 = [(B[i] - G0[i]) / eps for i in range(3)]
    cr = (d1[1] * d2[2] - d1[2] * d2[1], d1[2] * d2[0] - d1[0] * d2[2], d1[0] * d2[1] - d1[1] * d2[0])
    return np.sqrt(np.sqrt(cr[0] ** 2 + cr[1] ** 2 + cr[2] ** 2))


_MAKE = {
    'oneplane': lambda: M.fixed(oneplane, 'oneplane', 'sphere inversions, one plane (for comparison)'),
    'along': lambda: M.fixed(along, 'along', 'turning plane, along (for comparison)'),
    'lathe': lambda: M.fixed(lathe, 'lathe', 'the quaternion square (for comparison)'),
    'spin': lambda: M.Rule('spin', 'the orbit carries a quaternion, turned as the point is turned', spin_step, _four),
    'prod': lambda: M.Rule('prod', 'arrows from the meeting point and from its twin, multiplied the sphere-inversion way', prod_step, lambda n: ()),
    'axis_every': lambda: M.Rule('axis_every', '"along" about the line from 0 to the meeting point, at every step', axis_every_step, lambda n: ()),
    'axis_once': lambda: M.Rule('axis_once', '"along" about the line from 0 to the meeting point at the first step, then one plane', axis_once_step, lambda n: ()),
    'axis_cycle': lambda: M.Rule('axis_cycle', '"along" about that line once per round trip of the cycle, one plane in between', axis_cycle_step, lambda n: (np.zeros(n),)),
    'm4': lambda: pattern_rule(mdir(4, -0.20), 'm4', 'copy twice round (m = 4, t = -0.2), not turned, length squared'),
    'face4': lambda: pattern_rule(mdir(4, -0.20), 'face4', 'copy twice round, turned by c to face the meeting point, length squared', face=True),
    'm4m': lambda: pattern_rule(mdir(4, -0.20), 'm4m', 'copy twice round, not turned, length follows the sideways stretch', matched=True),
    'face4m': lambda: pattern_rule(mdir(4, -0.20), 'face4m', 'copy twice round, turned by c, length follows the sideways stretch', face=True, matched=True),
    'face3': lambda: pattern_rule(mdir(3, -0.268), 'face3', 'copy once round (m = 3), turned by c to face the meeting point, length squared', face=True),
    'face3m': lambda: pattern_rule(mdir(3, -0.268), 'face3m', 'copy once round (m = 3), turned by c, length follows the sideways stretch', face=True, matched=True),
    'face6': lambda: pattern_rule(mdir(6, -0.10), 'face6', 'copy four times round (m = 6), turned by c, length squared', face=True),
    'face6m': lambda: pattern_rule(mdir(6, -0.10), 'face6m', 'copy four times round (m = 6), turned by c, length follows the sideways stretch', face=True, matched=True),
}


def _tri():
    import tri as T                                              # out/r24/me/tri.py: two flat triangles, even spacing
    return lambda x, y, z: T.tri_dir(x, y, z)


_MAKE['tri'] = lambda: pattern_rule(_tri(), 'tri', 'even spacing on two flat triangles (three corners on the flat circle), not turned')
_MAKE['face_tri'] = lambda: pattern_rule(_tri(), 'face_tri', 'even spacing on two flat triangles, one corner turned by c onto the meeting point', face=True)
_MAKE['twin_tri'] = lambda: pattern_rule(_tri(), 'twin_tri', 'even spacing on two flat triangles, a corner on the meeting point AND on its twin (space folded by a half turn first)', face=True, twin=True)
NAMES = list(_MAKE)


def get(name):
    return _MAKE[name]()
