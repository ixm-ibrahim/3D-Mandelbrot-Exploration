"""Round 25, section "wall": the rules used to test the wall of docs/ROUND25.md section 3.

    import sys; sys.path.insert(0, 'out/r25/wall'); import wall as W

The fifth thing (the hole in W-a)
---------------------------------
W-a lists four things a rule can do off the flat picture when it treats every direction round the upright axis
alike. The list silently assumes "length squared times a map of directions". Without that there is a fifth: the
rule may send single points of the upright axis to INFINITY (as every sphere inversion does). The plainest rule of
that kind uses nothing but the unit circle, the one circle the flat square keeps in place:

    wind:  take the spheres through the unit circle (the flat plane is one of them). A point lies on exactly one;
           that sphere meets the flat plane at an angle s. Move the point, along the circle through it that
           crosses all those spheres squarely, to the sphere at the angle 3 s (three times round the unit circle).
           's3'  s -> 3 s                 (heights near the flat plane are tripled: flattened bodies)
           's3s' s -> 3 s - sin 2 s       (near the flat plane nothing moves: shapes kept there)
    rules: 'ws'  wind, then the one-plane square      'sw'  the one-plane square, then wind

    zoo:   rules that are NOT "a fixed square, then add c": z^2 + c written another way with the one-plane product
           (lengths multiply, longitudes add, Mercator latitudes add) and the plain sum of space.
           'zooA'  v * (v + c / v)            'zooB'  v^2 * (1 + c / v^2)        (both are z^2 + c on the flat plane)
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M


def P(x, y, z):
    """The one-plane square."""
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); d = r2 + z * z; f = np.where(d > 0, r2 / np.where(d > 0, d, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def wind(x, y, z, m=3, shaped=True):
    """m times round the unit circle. Profile: zeta = rho + i z (right half-plane), u = (zeta - 1)/(zeta + 1) is the
    unit disc with the unit circle of space at u = 0, the flat plane on the diameter (outside the circle u > 0,
    inside u < 0) and the upright axis on |u| = 1 (infinity at u = 1, the origin at u = -1)."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    rho = np.hypot(x, y); zeta = rho + 1j * z
    u = (zeta - 1) / (zeta + 1); R = np.abs(u); th = np.angle(u)
    s = m * th - ((m - 1) / 2.0 * np.sin(2 * th) if shaped else 0.0)
    u2 = R * np.exp(1j * s); z2 = (1 + u2) / (1 - u2)
    ok = rho > 0; rr = np.where(ok, rho, 1.0); cx = np.where(ok, x / rr, 1.0); cy = np.where(ok, y / rr, 0.0)
    flat = z == 0
    return np.where(flat, x, z2.real * cx), np.where(flat, y, z2.real * cy), np.where(flat, 0.0, z2.imag)


def ws(m=3, shaped=True):
    return lambda x, y, z: P(*wind(x, y, z, m, shaped))


def sw(m=3, shaped=True):
    return lambda x, y, z: wind(*P(x, y, z), m, shaped)


# ---------------------------------------------------------------- the one-plane product, for the zoo
def stereo(x, y, z):
    """length and the stereographic number of the direction (equator |w| = 1, upright axis w = infinity / 0)."""
    r = np.sqrt(x * x + y * y + z * z); d = r - z
    w = np.where(d > 0, (x + 1j * y) / np.where(d > 0, d, 1.0), np.inf)
    return r, w


def unstereo(r, w):
    n2 = np.abs(w) ** 2; fin = np.isfinite(n2); n2s = np.where(fin, n2, 1.0); ws_ = np.where(fin, w, 0.0)
    X = np.where(fin, 2 * ws_.real / (1 + n2s), 0.0); Y = np.where(fin, 2 * ws_.imag / (1 + n2s), 0.0); Z = np.where(fin, (n2s - 1) / (n2s + 1), 1.0)
    return r * X, r * Y, r * Z


def prod(a, b):
    ra, wa = stereo(*a); rb, wb = stereo(*b)
    return unstereo(ra * rb, wa * wb)


def inv(a):
    """the inverse for that product: a sphere inversion and a half turn about the x-axis."""
    x, y, z = a; r2 = x * x + y * y + z * z; r2 = np.where(r2 > 0, r2, np.nan)
    return x / r2, -y / r2, -z / r2


def zooA_step(x, y, z, st, k, cx, cy, cz):
    v = (x, y, z); c = (cx, cy, cz); q = prod(c, inv(v)); t = (x + q[0], y + q[1], z + q[2]); f = prod(v, t)
    flat = (z == 0) & (cz == 0)
    X = np.where(flat, x * x - y * y, f[0] - cx); Y = np.where(flat, 2 * x * y, f[1] - cy); Z = np.where(flat, 0.0, f[2] - cz)
    return X, Y, Z, st


def zooB_step(x, y, z, st, k, cx, cy, cz):
    s = P(x, y, z); c = (cx, cy, cz); q = prod(c, inv(s)); t = (1.0 + q[0], q[1], q[2]); f = prod(s, t)
    flat = (z == 0) & (cz == 0)
    X = np.where(flat, x * x - y * y, f[0] - cx); Y = np.where(flat, 2 * x * y, f[1] - cy); Z = np.where(flat, 0.0, f[2] - cz)
    return X, Y, Z, st


RULES = {
    'oneplane': lambda: M.fixed(P, 'one plane', 'the one-plane square (the baseline)'),
    'ws': lambda: M.fixed(ws(3, True), 'wind, square', 'three times round the unit circle, then the one-plane square'),
    'sw': lambda: M.fixed(sw(3, True), 'square, wind', 'the one-plane square, then three times round the unit circle'),
    'ws_plain': lambda: M.fixed(ws(3, False), 'wind (plain), square', 'the same with the plain tripling (heights tripled at the flat plane)'),
    'sw_plain': lambda: M.fixed(sw(3, False), 'square, wind (plain)', 'square, then the plain tripling'),
    'zooA': lambda: M.Rule('zoo A', 'z^2 + c written as z (z + c / z), with the one-plane product', zooA_step, init=lambda n: ()),
    'zooB': lambda: M.Rule('zoo B', 'z^2 + c written as z^2 (1 + c / z^2), with the one-plane product', zooB_step, init=lambda n: ()),
}

SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]


def best():
    return RULES['ws']()


if __name__ == '__main__':
    for key in sys.argv[1:] or ['oneplane', 'ws', 'sw', 'ws_plain', 'sw_plain', 'zooA', 'zooB']:
        r = RULES[key](); print('==', key, '|', r.label); print('   flat check', M.flat_check(r, n=20000, steps=60)); sys.stdout.flush()
