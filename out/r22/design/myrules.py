"""Round 22, section 'design': the new rules. Every rule squares the length (|F(v)| = |v|^2) and is exact on the flat page.

    import sys; sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r22/design'); import mem as M, myrules as D
    D.RULES            the list;  D.get('capfold45')

Words used below. P = the one-plane square (out/me/r16/scout.py oneplane). The UPRIGHT AXIS is the z-axis, the line
through 0 square to the flat page. 'Height angle' L of a point = its angle above the flat page seen from 0
(sin L = z / |v|). A CAP is the set of directions whose height angle is more than L1 (a round cap round the upright
axis, one above and one below the page).

capfold(L1):   F(v) = P(m(v)).  m leaves every point alone whose height angle is at most L1. A point in a cap is
               MIRRORED in the rim of the cap: it keeps its length and its compass direction round the upright axis,
               and its height angle L becomes L' with  t' = e^2 / t,  t = tan((90 - L) / 2),  e = tan((90 - L1) / 2)
               (the mirror of the sphere of directions in the circle of height angle L1; it keeps shapes).
               L1 = 45 and L1 = 30 are two rules. L1 is a hand-set number.
capfold2(L1):  the same mirror done twice in a row before P (a point thrown past the other rim by the first mirror
               is mirrored back by the second). One more hand-set repeat; made to see what the second fold adds.
caphump(L1):   F(v) = P(h(v)). No crease: the height angle is changed smoothly. With M = atanh(sin L) and
               M1 = atanh(sin L1):  M' = M1 sin(M / M1)  for |M| <= pi M1, and beyond that  M' = -(M - pi M1) (north)
               so that the upright axis is sent to the opposite side as in capfold. Keeps shapes only near the page.
preturn:       F(v) = P(Rot(v)): before the one-plane square the point is swung round the x-axis from its turn phi
               to the turn  phi + 90 deg * sin(phi)^2  (for phi in 0..180; mirrored below the page). The upright
               half-page above the page is laid onto the flat page (the half with y < 0). A check of the claim
               that a swing round the x-axis which lays a second page onto the flat one must squeeze.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M
P = M.S.oneplane
TINY = 1e-300


def cap_mirror(x, y, z, eps):
    """Mirror the two caps of directions (|w| < eps, w = rho / (r + |z|)) in their rims. Length is kept."""
    r = np.sqrt(x * x + y * y + z * z); rho = np.hypot(x, y); az = np.abs(z)
    w = rho / np.maximum(r + az, TINY)
    cap = (w < eps) & (r > 0)
    e4 = eps ** 4; den = w * w + e4
    s = 2 * eps * eps * w / den                   # sine of the new angle from the upright axis
    cz = (w * w - e4) / den                       # its cosine (negative: thrown past the page to the other side)
    k = np.where(rho > 0, r * s / np.maximum(rho, TINY), 0.0)
    X = np.where(cap, x * k, x); Y = np.where(cap, y * k, y); Z = np.where(cap, np.sign(z) * r * cz, z)
    return X, Y, Z


def eps_of(L1deg):
    return float(np.tan(np.radians(90.0 - L1deg) / 2))


def capfold(L1deg, times=1):
    e = eps_of(L1deg)

    def step(x, y, z, st, k, cx, cy, cz):
        for _ in range(times):
            x, y, z = cap_mirror(x, y, z, e)
        return (*P(x, y, z), st)
    return step


def caphump(L1deg):
    M1 = float(np.arctanh(np.sin(np.radians(L1deg))))

    def step(x, y, z, st, k, cx, cy, cz):
        r = np.sqrt(x * x + y * y + z * z); rho = np.hypot(x, y)
        s = np.clip(np.where(r > 0, z / np.maximum(r, TINY), 0.0), -1 + 1e-15, 1 - 1e-15)
        m = np.arctanh(s); a = np.abs(m)
        m2 = np.where(a <= np.pi * M1, M1 * np.sin(a / M1), -(a - np.pi * M1)) * np.sign(m)
        s2 = np.tanh(m2); c2 = np.sqrt(np.clip(1 - s2 * s2, 0, 1))
        k2 = np.where(rho > 0, r * c2 / np.maximum(rho, TINY), 0.0)
        xx = np.where(rho > 0, x * k2, 0.0); yy = np.where(rho > 0, y * k2, 0.0); zz = r * s2
        zz = np.where(rho > 0, zz, -z)            # exactly on the upright axis: to the opposite side
        return (*P(xx, yy, zz), st)
    return step


def preturn_step(x, y, z, st, k, cx, cy, cz):
    phi = np.arctan2(z, y); d = (np.pi / 2) * np.sin(phi) ** 2 * np.sign(phi)
    c, s = np.cos(d), np.sin(d)
    return (*P(x, c * y - s * z, s * y + c * z), st)


_ALONG = M.bench('along').step


def meeting_turn(cx, cy):
    """The direction (in the flat page, as an angle a in -90..90 degrees, radians) of the line from 0 to the point
    where the big bodies of the flat picture meet: the fixed point  alpha = (1 - sqrt(1 - 4c)) / 2  of z -> z^2 + c."""
    c = np.asarray(cx, float) + 1j * np.asarray(cy, float)
    al = (1 - np.sqrt(1 - 4 * c)) / 2
    a = np.where(np.abs(al) > 1e-12, np.angle(al), 0.0)
    return np.where(a > np.pi / 2, a - np.pi, np.where(a <= -np.pi / 2, a + np.pi, a))


def alonghinge_step(x, y, z, st, k, cx, cy, cz):
    """'Turning plane, along' with its pages hinged on the line from 0 to the meeting point alpha(c) instead of on
    the x-axis:  F(v) = Rot_z(2a) along(Rot_z(-a) v),  a = the turn of that line (meeting_turn). For c on the x-axis
    left of 1/4 alpha is on the x-axis, a = 0, and the rule IS along. c is read through its flat-page part only."""
    a = meeting_turn(cx, cy); ca, sa = np.cos(a), np.sin(a)
    X, Y, Z, st = _ALONG(ca * x + sa * y, ca * y - sa * x, z, st, k, cx, cy, cz)
    c2, s2 = np.cos(2 * a), np.sin(2 * a)
    return c2 * X - s2 * Y, s2 * X + c2 * Y, Z, st


def none(n):
    return ()


RULES = [
    M.Rule('capfold45', 'caps above 45 degrees mirrored in their rim, then the one-plane square', capfold(45.0), none),
    M.Rule('capfold30', 'caps above 30 degrees mirrored in their rim, then the one-plane square', capfold(30.0), none),
    M.Rule('capfold45x2', 'caps above 45 degrees mirrored in their rim twice, then the one-plane square', capfold(45.0, 2), none),
    M.Rule('caphump45', 'height angle bent back smoothly (no crease), then the one-plane square', caphump(45.0), none),
    M.Rule('preturn', 'upright half-page swung onto the flat page round the x-axis, then the one-plane square', preturn_step, none),
    M.Rule('alonghinge', 'along with its pages hinged on the line from 0 to the point where the big bodies meet', alonghinge_step, none),
]
PLAIN = {'capfold45': 'Fold the top and bottom down, then square (fold at 45 degrees)',
         'capfold30': 'Fold the top and bottom down, then square (fold at 30 degrees)',
         'capfold45x2': 'Fold twice, then square',
         'caphump45': 'Bend the top and bottom down smoothly, then square',
         'preturn': 'Swing the upright page onto the flat page, then square',
         'alonghinge': 'Turning plane, along, hinged on the line to the meeting point'}


def get(name):
    return next(r for r in RULES if r.name == name)
