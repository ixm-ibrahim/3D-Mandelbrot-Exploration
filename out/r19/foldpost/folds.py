"""Round 19, section foldpost: fold the one-plane ANSWER with sphere inversions.

Every rule here is F(v) = |v|^2 D(v/|v|), D = (folds) o P, P = the one-plane map of directions
(in Mercator terms: longitude doubled, Mercator height doubled; stretch sqrt(2 cos L' (1 + cos L')) seen from the
answer latitude L', 2 on the flat circle, 0 at the poles).
A fold = reflection of a cap of ANSWER directions in its own rim circle (the restriction to the unit sphere of the
inversion in the sphere that meets the unit sphere squarely along that rim). It keeps angles, reverses handedness,
is the identity on the rim (so: a crease, no tear), and its stretch at an inside point at angle t_in from the cap
centre, whose image sits at t_out, is sin(t_out) / sin(t_in).

Kinds built here:
  one(n, alpha)                 answers inside the cap (centre n, angular radius alpha) are reflected out of it
  pleat(n1, a1, n2, a2)         answers inside cap 1 are reflected out; those that then land OUTSIDE cap 2
                                (cap 2 contains cap 1) are reflected back in its rim: a Z-fold, three layers over
                                the ring between the two rims and nothing extra elsewhere
Every cap is used together with its mirror image below the flat plane (and across y = 0 when it is off that plane).
"""
import os, sys
import numpy as np

EPS = 1e-300


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def P_dir(U):
    """One-plane map on unit directions, array (3, ...)."""
    x, y, z = U
    f = 1.0 / (1.0 + z * z)
    return np.stack([f * (x * x - y * y), f * 2 * x * y, f * 2 * z])


def reflect(U, n, alpha):
    """Reflection of unit directions U in the circle (centre n, angular radius alpha)."""
    q = (np.asarray(n, float) / np.cos(alpha)).reshape(3, *([1] * (U.ndim - 1)))
    k = np.tan(alpha) ** 2
    W = U - q
    return q + k * W / np.maximum((W * W).sum(0), EPS)


def in_cap(U, n, alpha):
    nn = np.asarray(n, float).reshape(3, *([1] * (U.ndim - 1)))
    return (U * nn).sum(0) > np.cos(alpha)


def mirrors(n):
    """The cap centre and its mirror images (z -> -z always; y -> -y when the centre is off the plane y = 0)."""
    n = unit(n); out = [n, n * np.array([1, 1, -1.0])]
    if abs(n[1]) > 1e-12:
        out += [n * np.array([1, -1, 1.0]), n * np.array([1, -1, -1.0])]
    return out


def fold_one(n, alpha):
    cs = mirrors(n)
    def fold(U):
        V = U
        for c in cs:
            V = np.where(in_cap(U, c, alpha), reflect(U, c, alpha), V)
        return V
    fold.caps = [(c, alpha) for c in cs]
    return fold


def fold_pleat(n1, a1, n2, a2):
    c1s = mirrors(n1); c2s = mirrors(n2)
    def fold(U):
        V = U
        for c1, c2 in zip(c1s, c2s):
            ins = in_cap(U, c1, a1)
            V1 = reflect(U, c1, a1)
            V2 = np.where(in_cap(V1, c2, a2), V1, reflect(V1, c2, a2))
            V = np.where(ins, V2, V)
        return V
    fold.caps = [(c, a1) for c in c1s]
    return fold


def D_of(fold):
    def D(U):
        return fold(P_dir(U))
    return D


def rule(fold):
    """Bench rule F(x, y, z) -> (X, Y, Z), |F(v)| = |v|^2."""
    def F(x, y, z):
        x, y, z = (np.asarray(a, float) for a in (x, y, z))
        r2 = x * x + y * y + z * z
        r = np.sqrt(np.maximum(r2, EPS))
        U = np.stack([x / r, y / r, z / r])
        U = np.where(r2 > 0, U, np.stack([np.ones_like(r), 0 * r, 0 * r]))
        V = fold(P_dir(U))
        n = np.sqrt((V * V).sum(0))                     # keep the length exact
        return r2 * V[0] / n, r2 * V[1] / n, r2 * V[2] / n
    F.fold = fold
    return F


# ----------------------------------------------------------------------------------------------------------------
# prediction: where a rule sends directions and how much it stretches them there (no iteration)

def sph(lat, lon):
    lat, lon = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def latlon(v):
    v = np.asarray(v, float); v = v / np.linalg.norm(v)
    return float(np.degrees(np.arcsin(np.clip(v[2], -1, 1)))), float(np.degrees(np.arctan2(v[1], v[0])))


def stretch_at(D, d, h=1e-6):
    """Two sideways stretches of the direction map at direction d, and the sign (+1 keeps handedness, -1 mirror)."""
    d = unit(d)
    a = np.cross(d, [0.3, 0.5, 0.8]); a /= np.linalg.norm(a); b = np.cross(d, a)
    def g(q):
        q = unit(q); w = D(q.reshape(3, 1))[:, 0]; return w / np.linalg.norm(w)
    w0 = g(d); da = (g(d + h * a) - g(d - h * a)) / (2 * h); db = (g(d + h * b) - g(d - h * b)) / (2 * h)
    sv = np.linalg.svd(np.stack([da, db], 1), compute_uv=False)
    return float(sv[0]), float(sv[1]), float(np.sign(np.dot(w0, np.cross(da, db))))


_GRID = None
def grid(nlat=1800, nlon=3600):
    global _GRID
    if _GRID is None:
        la = (np.arange(nlat) + 0.5) / nlat * 180 - 90; lo = (np.arange(nlon) + 0.5) / nlon * 360 - 180
        LA, LO = np.meshgrid(la, lo, indexing='ij')
        _GRID = (LA, LO, sph(LA, LO))
    return _GRID


def preimages(D, target, tol_deg=0.6):
    """All directions the rule sends to `target` (found on a 0.1 degree grid, then refined)."""
    from scipy.optimize import minimize
    LA, LO, U = grid()
    W = D(U); t = unit(target)
    dot = (W * t.reshape(3, 1, 1)).sum(0)
    sel = dot > np.cos(np.radians(tol_deg))
    pts = U[:, sel].T; found = []
    pts = list(pts[np.argsort(-dot[sel])])
    while pts:
        p = pts[0]; A = np.array(pts); near = A @ p > np.cos(np.radians(3.0))
        found.append(p); pts = [q for q, m in zip(pts, near) if not m]
    out = []
    for p in found:
        la0, lo0 = latlon(p)
        def cost(q):
            w = D(sph(q[0], q[1]).reshape(3, 1))[:, 0]
            return 1 - float(w @ t)
        r = minimize(cost, [la0, lo0], method='Nelder-Mead', options=dict(xatol=1e-9, fatol=1e-16, maxiter=600))
        d = sph(r.x[0], r.x[1])
        if r.fun < 1e-9 and not any(d @ o > np.cos(np.radians(0.3)) for o in out):
            out.append(d)
    return out


def describe(d):
    la, lo = latlon(d)
    return 'latitude %+.1f, longitude %+.1f' % (la, lo)


def predict(name, fold, targets=None, verbose=True):
    """The seconds-long screen of the brief: for each flat direction (angle from +x in the flat plane) the
    directions sent to it, their latitude and longitude, both stretches and handedness; where the crushed pole goes;
    how wide the untouched band round the flat plane is."""
    D = D_of(fold)
    LA, LO, U = grid()
    Pu = P_dir(U); W = fold(Pu)
    moved = ((W - Pu) ** 2).sum(0) > 1e-18
    lat_moved = np.abs(LA[moved])
    res = dict(name=name)
    res['band_half_width_deg'] = float(lat_moved.min()) if moved.any() else 90.0
    for lon0, tag in ((0, 'above_px'), (90, 'above_py'), (180, 'above_mx')):
        m = moved & (np.abs(((LO - lon0 + 180) % 360) - 180) < 0.06) & (LA > 0)
        res['crease_lat_' + tag] = float(LA[m].min()) if m.any() else None
    pole = D(np.array([[0.0], [0.0], [1.0]]))[:, 0]
    res['pole_goes_to'] = dict(elev=latlon(pole)[0], lon=latlon(pole)[1], vec=[float(v) for v in pole])
    res['share_of_sources_folded_pct'] = float(100 * (np.cos(np.radians(LA)) * moved).sum() / np.cos(np.radians(LA)).sum())
    res['targets'] = {}
    lines = []
    for phi in (targets if targets is not None else (180, 0, 150, 120, 90, 60, 30)):
        t = np.array([np.cos(np.radians(phi)), np.sin(np.radians(phi)), 0.0])
        ps = preimages(D, t)
        rows = []
        for d in ps:
            s1, s2, sg = stretch_at(D, d)
            la, lo = latlon(d)
            rows.append(dict(lat=la, lon=lo, stretch=s1, stretch2=s2, hand=sg))
        rows.sort(key=lambda r: (abs(r['lat']), r['lon']))
        res['targets'][phi] = rows
        up = [r for r in rows if r['lat'] > 0.05]
        flat = [r for r in rows if abs(r['lat']) <= 0.05]
        lines.append('  to flat direction %3d deg (%s): %d in the flat plane, %d above it (same below): %s' % (
            phi, {0: '+x, long arms', 180: '-x, buds'}.get(phi, 'in between'), len(flat), len(up),
            '; '.join('lat %.1f lon %+.0f stretch %.2f%s' % (r['lat'], r['lon'], r['stretch'], ' mirrored' if r['hand'] < 0 else '') for r in up) or 'none'))
    if verbose:
        print('%s' % name)
        print('  untouched band round the flat plane: %.1f deg each side at its narrowest; crease above +x %s, above +-y %s, above -x %s (degrees of source latitude)' % (
            res['band_half_width_deg'], *('%.1f' % res['crease_lat_' + t] if res['crease_lat_' + t] is not None else 'none' for t in ('above_px', 'above_py', 'above_mx'))))
        print('  the crushed pole (straight up) is sent to: elevation %+.1f, longitude %+.1f; share of directions folded %.1f %%' % (
            res['pole_goes_to']['elev'], res['pole_goes_to']['lon'], res['share_of_sources_folded_pct']))
        print('\n'.join(lines), flush=True)
    return res
