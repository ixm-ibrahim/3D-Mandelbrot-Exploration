"""Round 19, section foldpre (prefix g_): fold the DIRECTION first, then apply the one-plane rule.

A fold is a mirror of the sphere of directions in a circle (a sphere inversion that keeps the unit sphere), used on
one side of the circle only (the 'cap'); outside the cap nothing is changed. The circle itself is not moved, so the
answers agree on both sides (a crease, no tear). The length of the point is never changed by the fold, and the
one-plane rule squares it, so |F(v)| = |v|^2.

    cap, given by its centre direction q (unit) and its angular radius a (degrees):
        apex p = q / cos(a);   inside the cap: u . p > 1;   mirror: u -> p + (|p|^2 - 1) (u - p) / |u - p|^2

Rules (all exact on the flat plane, all the same above and below it):
    g_p<L>    one cap round each pole, crease at latitude L, folded once
    g_k<L>    the same two creases used as two facing mirrors (folded again and again: a kaleidoscope in latitude)
    g_t35     four small caps leaning over +y and -y (radius 35, centre at latitude 45): creases low over the bud
              directions only, far from the long arms
    g_d48     two caps per hemisphere leaning over +y and -y, crossing at right angles over +x and -x
              (radius 48.3, centre at latitude 58.3: crease 10 degrees up over +-y, 51 degrees up over +-x)
    g_mix     fold before (g_p245) and fold after (the round-17 cap fold, s = 0.15)
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import scout as S

EPS = 1e-300


def apex(lat, lon, a):
    """Apex vector of the cap whose centre is at latitude lat (from the flat plane), longitude lon (from +x, in the
    flat plane), angular radius a. Degrees."""
    la, lo, a = np.radians(lat), np.radians(lon), np.radians(a)
    q = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return q / np.cos(a)


def mirror(U, p):
    p = p.reshape(3, *([1] * (U.ndim - 1)))
    W = U - p
    return p + ((p * p).sum() - 1.0) * W / np.maximum((W * W).sum(0), EPS)


def inside(U, p):
    return (U * p.reshape(3, *([1] * (U.ndim - 1)))).sum(0) > 1.0


def unit(x, y, z):
    x, y, z = (np.asarray(a, float) for a in (x, y, z))
    r2 = x * x + y * y + z * z
    r = np.sqrt(r2); d = np.maximum(r, EPS)
    return r2, r, np.stack([x / d, y / d, z / d])


def finish(r2, V):
    """one-plane rule on the folded direction V (unit), length r: |v|^2 D(V)."""
    X, Y, Z = S.oneplane(V[0], V[1], V[2])
    return r2 * X, r2 * Y, r2 * Z


def fold_once(groups):
    """groups: list of lists of apex vectors. Each group is a set of caps handled together: a single cap, or two caps
    whose circles cross at right angles (then a point in both is mirrored in both). Groups must not overlap."""
    def fold(U):
        V = U
        for g in groups:
            W = U
            hit = np.zeros(U.shape[1:], bool)
            for p in g:
                ins = inside(W, p)
                W = np.where(ins, mirror(W, p), W)
                hit |= ins
            V = np.where(hit, W, V)
        return V
    return fold


def prefold(fold):
    def F(x, y, z):
        r2, r, U = unit(x, y, z)
        return finish(r2, fold(U))
    return F


def polecaps(L):
    return fold_once([[apex(90, 0, 90 - L)], [apex(-90, 0, 90 - L)]])


def kaleido(L):
    """Two facing mirrors: the circles of latitude +L and -L. In the angle-true height t = ln tan(45 - lat/2) the
    two mirrors are t = -a and t = +a and the fold is a triangle wave."""
    a = -np.log(np.tan(np.radians(45 - L / 2)))
    def fold(U):
        rho = np.sqrt(U[0] ** 2 + U[1] ** 2)
        s = rho / np.maximum(1 + U[2], EPS)
        t = np.log(np.maximum(s, 1e-150))
        t2 = a - np.abs(np.mod(t + a, 4 * a) - 2 * a)
        s2 = np.exp(t2)
        z2 = (1 - s2 * s2) / (1 + s2 * s2); rho2 = 2 * s2 / (1 + s2 * s2)
        k = rho2 / np.maximum(rho, EPS)
        cx = np.where(rho > 0, U[0] * k, rho2); cy = np.where(rho > 0, U[1] * k, 0.0)
        return np.stack([cx, cy, z2])
    return fold


def leaning4(lat=45.0, a=35.0):
    return fold_once([[apex(sg * lat, lon, a)] for sg in (1, -1) for lon in (90, -90)])


def crossed(lat=58.3, a=48.3):
    # exact right angle: cos(distance between centres) = cos(a)^2, distance = 180 - 2 lat
    a = np.degrees(np.arccos(np.sqrt(max(np.cos(np.radians(180 - 2 * lat)), 0.0))))
    return fold_once([[apex(sg * lat, 90, a), apex(sg * lat, -90, a)] for sg in (1, -1)])


def postcap(s):
    """the round-17 fold of the ANSWER (m_cap): caps with centres (s, 0, +-(1 + s))."""
    def post(V):
        out = V
        for sg in (1.0, -1.0):
            q = np.array([s, 0.0, sg * (1 + s)])
            out = np.where(inside(V, q), mirror(V, q), out)
        return out
    return post


def mixed(fold, post):
    def F(x, y, z):
        r2, r, U = unit(x, y, z)
        V = fold(U)
        X, Y, Z = S.oneplane(V[0], V[1], V[2])
        W = post(np.stack([X, Y, Z]))
        return r2 * W[0], r2 * W[1], r2 * W[2]
    return F


def pleats(a1=12.0, a2=90.0, b1=27.9, b2=69.55):
    """A pleat = two creases, one inside the other, both leaning over the bud direction (+y or -y) and both on one side
    of the flat plane. Numbers are angles up the meridian from the bud direction (so a1 is the latitude of the low point
    of the outer crease, a2 = 90 means it touches the pole). Between the creases: mirrored in the outer one. Inside the
    inner one: mirrored in both (same hand again). Four pleats: above / below times +y / -y."""
    def cap(t1, t2, sg, lon):
        return apex(sg * (t1 + t2) / 2, lon, (t2 - t1) / 2)
    ps = [(cap(a1, a2, sg, lon), cap(b1, b2, sg, lon)) for sg in (1, -1) for lon in (90, -90)]
    def fold(U):
        V = U
        for pa, pb in ps:
            ina = inside(U, pa)
            W = np.where(inside(U, pb), mirror(U, pb), U)
            V = np.where(ina, mirror(W, pa), V)
        return V
    return fold


L45 = 90 - 2 * np.degrees(np.arctan(np.sqrt(np.tan(np.radians(22.5)))))     # crease whose copy of the flat plane is at 45 degrees: 24.47

FOLDS = {
    'g_p12':  (polecaps(12.0), 'Fold directions above 12 degrees down, then one plane'),
    'g_p22':  (polecaps(22.0), 'Fold directions above 22 degrees down, then one plane'),
    'g_p245': (polecaps(L45),  'Fold directions above 24.5 degrees down (copy of the flat plane at 45), then one plane'),
    'g_p30':  (polecaps(30.0), 'Fold directions above 30 degrees down, then one plane'),
    'g_p45':  (polecaps(45.0), 'Fold directions above 45 degrees down, then one plane'),
    'g_k12':  (kaleido(12.0),  'Two facing mirrors at 12 degrees up and down, then one plane'),
    'g_k245': (kaleido(L45),   'Two facing mirrors at 24.5 degrees up and down, then one plane'),
    'g_t35':  (leaning4(),     'Four small caps leaning over the bud directions, then one plane'),
    'g_d48':  (crossed(),      'Two crossed caps per side (low over the buds, high over the arms), then one plane'),
    'g_pl':   (pleats(),       'Four pleats leaning over the bud directions (no copy of the long arms), then one plane'),
    'g_pt':   (pleats(12.0, 90.0, 27.9, 90.0), 'Four pleats, both creases through the pole (a paper pleat seen from the pole), then one plane'),
    'g_pt8':  (pleats(8.0, 90.0, 19.0, 90.0), 'The same pleats, lower (outer crease 8 degrees up, inner 19), then one plane'),
}
RULES = {k: (prefold(f), lab, '') for k, (f, lab) in FOLDS.items()}
RULES['g_mix'] = (mixed(polecaps(L45), postcap(0.15)), 'Fold before (24.5 degrees) and fold after (s = 0.15)', '')
