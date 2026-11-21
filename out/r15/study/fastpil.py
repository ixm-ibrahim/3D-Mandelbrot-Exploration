"""Fast square-pillow rule (round 15 study). Stand-alone numpy.

Layouts (sphere <-> pillow), all with the belt on the equator and s = longitude / 360:
  LayE(h, n, a)  the orchestrator's ellipse layout, generalised:
                 pillow height h (t in [0, h/2]), power n (belt at t0 = h/(n+1)), seam half-length a
                 (p = ((a + (1-a) B^2) cos nu, B sin nu)); B(t) = sinh or sin profile with dB/dt = 2 pi at the belt.
                 LayE(1, 2, 0.5) is out/me/r15/pillow_ref.py.
  LayJ(h, n)     Joukowski layout: rho = exp(-2 pi * distance from the belt in t), zeta = rho e^{i nu},
                 p = (Re(zeta + a^2/zeta)/(1 + a^2), Im(zeta + a^2/zeta)/(1 - a^2)), a = exp(-2 pi * width).
                 Closed-form inverse (a complex square root). Angle-true up to the factor (1+a^2)/(1-a^2).
Rule: F(v) = |v|^n * dir(D(pil(v/|v|))),  D(s, t) = (-n s, n t) folded back into [0, h/2].
"""
import numpy as np

TWO_PI = 2 * np.pi


def _solve_b(w):
    from scipy.optimize import brentq
    lim = 1 / TWO_PI
    if abs(w - lim) < 1e-9:
        return 0.0, 'lin'
    if w > lim:      # b coth(b w) = 2 pi
        return brentq(lambda b: b / np.tanh(b * w) - TWO_PI, 1e-9, TWO_PI + 1), 'sinh'
    return brentq(lambda b: b / np.tan(b * w) - TWO_PI, 1e-9, (np.pi / 2 - 1e-9) / w), 'sin'


def solve_beta(px, py, a=0.5, iters=80):
    """beta in [0, 1] with px^2 / (a + (1-a) beta)^2 + py^2 / beta = 1. Newton from beta = 1 with a bracket."""
    px2 = px * px; py2 = py * py
    oa = 1 - a
    n = px2.size
    out = np.ones(n)
    idx = np.arange(n)
    b = np.ones(n); lo = np.zeros(n); hi = np.ones(n)
    for it in range(iters):
        A = a + oa * b
        A2 = A * A
        g = b * A2 - px2 * b - py2 * A2
        gp = A2 + 2 * oa * A * (b - py2) - px2
        pos = g > 0
        hi = np.where(pos, b, hi); lo = np.where(pos, lo, b)
        with np.errstate(divide='ignore', invalid='ignore'):
            nb = b - g / gp
        bad = ~((nb >= lo) & (nb <= hi))
        nb = np.where(bad, 0.5 * (lo + hi), nb)
        conv = np.abs(nb - b) <= 1e-10 * nb + 1e-300      # Newton doubles the digits: the next value is exact
        b = nb
        if it >= 3 and conv.any():
            out[idx[conv]] = b[conv]
            keep = ~conv
            if not keep.any():
                idx = idx[:0]
                break
            idx = idx[keep]; b = b[keep]; lo = lo[keep]; hi = hi[keep]; px2 = px2[keep]; py2 = py2[keep]
    if idx.size:
        out[idx] = b
    return out


class LayE:
    def __init__(self, h=1.0, n=2, a=0.5):
        self.h, self.n, self.a = float(h), int(n), float(a)
        self.t0 = self.h / (self.n + 1)
        self.wn, self.ws = self.h / 2 - self.t0, self.t0
        self.bn, self.kn = _solve_b(self.wn)
        self.bs, self.ks = _solve_b(self.ws)

    @staticmethod
    def _B(tau, b, w, kind):
        if kind == 'sinh': return np.sinh(b * tau) / np.sinh(b * w)
        if kind == 'sin': return np.sin(b * tau) / np.sin(b * w)
        return tau / w

    @staticmethod
    def _tau(B, b, w, kind):
        if kind == 'sinh': return np.arcsinh(B * np.sinh(b * w)) / b
        if kind == 'sin': return np.arcsin(np.clip(B * np.sin(b * w), -1, 1)) / b
        return B * w

    def pil(self, x, y, z):
        north = z >= 0
        den = 1 + np.abs(z)
        px, py = x / den, y / den
        a = self.a
        beta = solve_beta(px, py, a)
        B = np.sqrt(beta)
        A = a + (1 - a) * beta
        nu = np.arctan2(np.where(B > 1e-300, py / np.maximum(B, 1e-300), 0.0), px / A)
        seam = B < 1e-9
        if seam.any():
            nu[seam] = np.arccos(np.clip(px[seam] / a, -1, 1))
        s = nu / TWO_PI
        t = np.where(north, self.h / 2 - self._tau(B, self.bn, self.wn, self.kn), self._tau(B, self.bs, self.ws, self.ks))
        return s, t

    def dirn(self, s, t):
        north = t >= self.t0
        B = np.where(north, self._B(self.h / 2 - t, self.bn, self.wn, self.kn), self._B(t, self.bs, self.ws, self.ks))
        B = np.clip(B, 0, 1)
        nu = TWO_PI * s
        px, py = (self.a + (1 - self.a) * B * B) * np.cos(nu), B * np.sin(nu)
        r2 = px * px + py * py
        k = 2 / (1 + r2)
        zz = (1 - r2) / (1 + r2)
        return k * px, k * py, np.where(north, zz, -zz)


class LayJ:
    """Joukowski layout. sq = 1: the affine squeeze (uniform shape error (1+a^2)/(1-a^2), not angle-true at the
    belt on the north side)."""
    def __init__(self, h=1.0, n=2):
        self.h, self.n = float(h), int(n)
        self.t0 = self.h / (self.n + 1)
        self.wn, self.ws = self.h / 2 - self.t0, self.t0
        self.an, self.as_ = np.exp(-TWO_PI * self.wn), np.exp(-TWO_PI * self.ws)

    def pil(self, x, y, z):
        north = z >= 0
        den = 1 + np.abs(z)
        a = np.where(north, self.an, self.as_)
        a2 = a * a
        J = (x / den) * (1 + a2) + 1j * (y / den) * (1 - a2)
        w = np.sqrt(J * J - 4 * a2 + 0j)
        w = np.where((J.real * w.real + J.imag * w.imag) >= 0, w, -w)
        zeta = 0.5 * (J + w)
        rho = np.clip(np.abs(zeta), a, 1.0)
        s = np.angle(zeta) / TWO_PI
        te = -np.log(rho) / TWO_PI
        return s, np.where(north, self.t0 + te, self.t0 - te)

    def dirn(self, s, t):
        north = t >= self.t0
        a = np.where(north, self.an, self.as_)
        a2 = a * a
        rho = np.maximum(np.exp(-TWO_PI * np.abs(t - self.t0)), a)
        nu = TWO_PI * s
        cs, sn = np.cos(nu), np.sin(nu)
        px = (rho + a2 / rho) * cs / (1 + a2)
        py = (rho - a2 / rho) * sn / (1 - a2)
        r2 = px * px + py * py
        k = 2 / (1 + r2)
        zz = (1 - r2) / (1 + r2)
        return k * px, k * py, np.where(north, zz, -zz)


def Dmap(s, t, n, h):
    u = (n * t) % h
    low = u <= h / 2
    return np.where(low, -n * s, n * s), np.where(low, u, h - u)


def F(x, y, z, lay):
    """One step without c. x, y, z 1-D float arrays. Returns three arrays."""
    n = lay.n
    r2 = x * x + y * y + z * z
    r = np.sqrt(r2)
    ok = r > 0
    ri = 1 / np.where(ok, r, 1)
    s, t = lay.pil(x * ri, y * ri, z * ri)
    s2, t2 = Dmap(s, t, n, lay.h)
    dx, dy, dz = lay.dirn(s2, t2)
    rn = r2 if n == 2 else r ** n
    ox, oy, oz = dx * rn, dy * rn, dz * rn
    flat = z == 0
    if flat.any():
        w = (x[flat] + 1j * y[flat]) ** n
        ox[flat], oy[flat], oz[flat] = w.real, w.imag, 0.0
    if not ok.all():
        ox[~ok] = 0; oy[~ok] = 0; oz[~ok] = 0
    return ox, oy, oz


_LAYS = {}
def get_lay(key):
    """key = ('E', h, n, a) or ('J', h, n)."""
    key = tuple(key)
    if key not in _LAYS:
        _LAYS[key] = LayE(*key[1:]) if key[0] == 'E' else LayJ(*key[1:])
    return _LAYS[key]


REF = ('E', 1.0, 2, 0.5)

if __name__ == '__main__':
    import os, sys, time
    HERE = os.path.dirname(os.path.abspath(__file__))
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r15'))
    import pillow_ref as P
    lay = get_lay(REF)
    print('bn, bs', lay.bn, lay.bs, 'ref', P.BN, P.BS)
    rng = np.random.default_rng(7)
    sets = {}
    v = rng.normal(size=(200000, 3)); v *= (rng.uniform(0.05, 1.6, size=200000) / np.linalg.norm(v, axis=1))[:, None]
    sets['200,000 random points, length 0.05 to 1.6'] = v
    e = rng.normal(size=(50000, 3)); e[:, 2] *= 1e-6; sets['50,000 points within 1e-6 of the plane'] = e / np.linalg.norm(e, axis=1)[:, None]
    q = rng.normal(size=(50000, 3)); q[:, 2] = 0; sets['50,000 points exactly in the plane'] = q
    # near the seams: directions with stereographic p = (u, eps), |u| < 1/2
    u = rng.uniform(-0.5, 0.5, 50000); eps = rng.normal(size=50000) * 1e-4
    r2 = u * u + eps * eps
    d = np.stack([2 * u / (1 + r2), 2 * eps / (1 + r2), (1 - r2) / (1 + r2) * rng.choice([-1, 1], 50000)], 1)
    sets['50,000 directions within 1e-4 of a seam'] = d
    u = 0.5 * rng.choice([-1, 1], 50000) + rng.normal(size=50000) * 1e-3; eps = rng.normal(size=50000) * 1e-3
    r2 = u * u + eps * eps
    d = np.stack([2 * u / (1 + r2), 2 * eps / (1 + r2), (1 - r2) / (1 + r2) * rng.choice([-1, 1], 50000)], 1)
    sets['50,000 directions within 1e-3 of a corner point'] = d
    for name, v in sets.items():
        t0 = time.time(); a = P.F(v.copy()); t1 = time.time()
        bx, by, bz = F(v[:, 0].copy(), v[:, 1].copy(), v[:, 2].copy(), lay); t2 = time.time()
        err = np.abs(a - np.stack([bx, by, bz], 1)).max(axis=1)
        print('%-48s worst %.2e  99.9%% %.2e  median %.1e   ref %.2f s, fast %.2f s' % (name, err.max(), np.quantile(err, .999), np.median(err), t1 - t0, t2 - t1), flush=True)
    # round trips of both layouts
    d = rng.normal(size=(200000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    for key in (REF, ('J', 1.0, 2), ('E', 1.0, 3, 0.5), ('J', 1.0, 3), ('E', 0.8, 2, 0.5), ('E', 1.3, 2, 0.35), ('J', 0.8, 2)):
        L = get_lay(key)
        s, t = L.pil(d[:, 0], d[:, 1], d[:, 2])
        bx, by, bz = L.dirn(s, t)
        rt = np.abs(np.stack([bx, by, bz], 1) - d).max()
        th = rng.uniform(0, TWO_PI, 20000); n = L.n
        s, t = L.pil(np.cos(th), np.sin(th), 0 * th); s2, t2 = Dmap(s, t, n, L.h); gx, gy, gz = L.dirn(s2, t2)
        eq = max(np.abs(gx - np.cos(n * th)).max(), np.abs(gy - np.sin(n * th)).max(), np.abs(gz).max())
        # continuity: close pairs
        a_ = rng.normal(size=(200000, 3)); a_ /= np.linalg.norm(a_, axis=1)[:, None]
        jumps = []
        for hh in (1e-4, 1e-5):
            b_ = a_ + hh * rng.normal(size=a_.shape); b_ /= np.linalg.norm(b_, axis=1)[:, None]
            fa = np.stack(F(a_[:, 0], a_[:, 1], a_[:, 2], L), 1); fb = np.stack(F(b_[:, 0], b_[:, 1], b_[:, 2], L), 1)
            jumps.append(np.linalg.norm(fa - fb, axis=1).max())
        print(key, 'round trip %.1e, equator against angle x%d %.1e, largest jump at step 1e-4 / 1e-5: %.2e / %.2e' % (rt, n, eq, jumps[0], jumps[1]), flush=True)
