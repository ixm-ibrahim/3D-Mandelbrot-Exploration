"""Round 15B, powers: the pillow rule in closed form ("4D shadow"), fast. Stand-alone numpy.

Same rule as out/me/r15/shadow_ref.py; the gauge rho is found by a safeguarded Newton iteration
(bracket kept, bisection whenever a Newton step leaves it) instead of 70 bisections.
Arrays are 1-D float64 x, y, z. Whole powers n >= 2.
"""
import numpy as np, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def consts(n):
    b0 = 2 * np.pi / (n + 1)
    return float(np.cos(b0)), float(np.sin(b0))


def gauge(X, Y, Z, n, tol=4e-16, maxit=200):
    """rho >= 0: the root of (r^2 - X^2)(r^2 - x2^2) - (Y (r - c0 x2) / s0)^2, x2 = c0 r - s0 Z, above the lower bound."""
    c0, s0 = consts(n)
    aX = np.abs(X)
    lo = np.maximum(np.maximum(aX, -s0 * Z / (1 - c0)), np.maximum(s0 * Z / (1 + c0), 0.0))
    hi = 4 * (aX + np.abs(Y) + np.abs(Z)) / min(1 - abs(c0), s0) + 1e-300
    Y2 = Y * Y
    r = np.minimum(np.sqrt(lo * lo + Y2) * 1.05 + 1e-300, hi)
    out = np.empty_like(r)
    idx = np.arange(r.size)
    X2 = X * X
    for it in range(maxit):
        x2 = c0 * r - s0 * Z
        e = r - c0 * x2
        a = r * r - X2
        b = r * r - x2 * x2
        g = a * b - Y2 * e * e / (s0 * s0)
        dg = 2 * r * b + a * (2 * r - 2 * c0 * x2) - 2 * Y2 * e
        neg = g < 0
        lo = np.where(neg, r, lo)
        hi = np.where(neg, hi, r)
        with np.errstate(divide='ignore', invalid='ignore'):
            rn = r - g / dg
        bad = ~((rn > lo) & (rn < hi))
        rn = np.where(bad, 0.5 * (lo + hi), rn)
        done = (np.abs(rn - r) <= tol * rn) | (hi - lo <= tol * hi)
        if done.any():
            out[idx[done]] = rn[done]
            keep = ~done
            if not keep.any():
                break
            idx = idx[keep]; r = rn[keep]; lo = lo[keep]; hi = hi[keep]
            X2 = X2[keep]; Y2 = Y2[keep]; Z = Z[keep]
        else:
            r = rn
    else:
        out[idx] = r
    return out


def cheb(n, u):
    t0, t1 = np.ones_like(u), u
    u0, u1 = np.zeros_like(u), np.ones_like(u)
    for _ in range(n - 1):
        t0, t1 = t1, 2 * u * t1 - t0
        u0, u1 = u1, 2 * u * u1 - u0
    return t1, u1


def F(X, Y, Z, n=2, want_rho=False):
    """One step without c. Returns X', Y', Z' (and rho of the input)."""
    c0, s0 = consts(n)
    rho = gauge(X, Y, Z, n)
    ok = rho > 0
    r = np.where(ok, rho, 1.0)
    x2 = c0 * rho - s0 * Z
    w = np.where(ok, Y * (rho - c0 * x2) / (s0 * r), 0.0)
    T1, U1 = cheb(n, np.clip(X / r, -1, 1))
    T2, U2 = cheb(n, np.clip(x2 / r, -1, 1))
    rn = r ** n
    x1n, x2n, wn = rn * T1, rn * T2, -rn / r * w * U1 * U2
    den = rn - c0 * x2n
    Yn = np.where(den > 0, s0 * rn * wn / np.where(den > 0, den, 1.0), 0.0)
    Zn = -(x2n - c0 * rn) / s0
    Xn = x1n
    flat = Z == 0
    if flat.any():
        zc = (X[flat] + 1j * Y[flat]) ** n
        Xn[flat] = zc.real; Yn[flat] = zc.imag; Zn[flat] = 0.0
    if not ok.all():
        Xn[~ok] = 0; Yn[~ok] = 0; Zn[~ok] = 0
    if want_rho:
        return Xn, Yn, Zn, rho
    return Xn, Yn, Zn


# ---------------------------------------------------------------- escape radius (in rho), per power
_RESC = {}
def rho_range(n):
    rng = np.random.default_rng(11)
    d = rng.normal(size=(200000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    r = gauge(d[:, 0].copy(), d[:, 1].copy(), d[:, 2].copy(), n)
    return float(r.min()), float(r.max())


def resc(n, cmax=2.0):
    """A rho beyond which the orbit must run away: rho(F(P) + c) >= rmin (rho^n / rmax - |c|) > 1.5 rho.
    rmin, rmax = range of rho on the unit sphere (measured on 200,000 directions, widened by 5 %)."""
    if n not in _RESC:
        a, b = rho_range(n)
        a *= 0.95; b *= 1.05
        R = 1.0
        while a * (R ** n / b - cmax) <= 1.5 * R:
            R += 0.25
        _RESC[n] = max(R, 2.0)
    return _RESC[n]


# ---------------------------------------------------------------- orbits
def orbit(x, y, z, cx, cy, cz, n, iters, R=None):
    """Start points (1-D arrays) and c (scalars or arrays). Returns inside (bool), death step (int16).
    A point is out once the gauge rho of the orbit point passes R (see resc)."""
    R = R or resc(n)
    M = x.size
    alive = np.arange(M)
    death = np.zeros(M, np.int16)
    carr = isinstance(cx, np.ndarray)
    x = x.copy(); y = y.copy(); z = z.copy()
    # the start point itself
    for k in range(iters + 1):
        fx, fy, fz, rho = F(x, y, z, n, want_rho=True)
        keep = rho <= R
        if not keep.all():
            death[alive[~keep]] = k + 1
            alive = alive[keep]
            fx, fy, fz = fx[keep], fy[keep], fz[keep]
            if alive.size == 0:
                break
        if carr:
            x, y, z = fx + cx[alive], fy + cy[alive], fz + cz[alive]
        else:
            x, y, z = fx + cx, fy + cy, fz + cz
    inside = np.zeros(M, bool); inside[alive] = True
    return inside, death


def _chunk(args):
    kind, n, c, axes, iters, i0, i1, rule = args
    ax, ay, az = axes
    X, Y, Z = np.meshgrid(ax[i0:i1], ay, az, indexing='ij')
    x, y, z = X.ravel(), Y.ravel(), Z.ravel()
    if rule == 'shadow':
        if kind == 'j':
            ins, d = orbit(x, y, z, c[0], c[1], c[2], n, iters)
        else:
            ins, d = orbit(x, y, z, x.copy(), y.copy(), z.copy(), n, iters)
    else:
        ins, d = orbit_other(rule, x, y, z, c, kind, n, iters)
    sh = (i1 - i0, ay.size, az.size)
    return i0, ins.reshape(sh), d.reshape(sh)


def orbit_other(rule, x, y, z, c, kind, n, iters, R=4.0):
    """The same loop for a rule that sends plain length r to r^n: escape at plain length R."""
    if rule == 'pillow':
        sys.path.insert(0, os.path.join(ROOT, 'out', 'r15', 'study'))
        import fastpil
        lay = fastpil.get_lay(('E', 1.0, n, 0.5))
        step = lambda a, b, cc: fastpil.F(a, b, cc, lay)
    elif rule == 'oneplane':
        sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
        import turns
        step = turns.E1
    else:
        raise ValueError(rule)
    M = x.size
    alive = np.arange(M); death = np.zeros(M, np.int16)
    if kind == 'm':
        cx, cy, cz = x.copy(), y.copy(), z.copy()
    x = x.copy(); y = y.copy(); z = z.copy()
    for k in range(iters + 1):
        keep = x * x + y * y + z * z <= R * R
        if not keep.all():
            death[alive[~keep]] = k + 1
            alive = alive[keep]; x, y, z = x[keep], y[keep], z[keep]
            if alive.size == 0:
                break
        fx, fy, fz = step(x, y, z)
        if kind == 'm':
            x, y, z = fx + cx[alive], fy + cy[alive], fz + cz[alive]
        else:
            x, y, z = fx + c[0], fy + c[1], fz + c[2]
    inside = np.zeros(M, bool); inside[alive] = True
    return inside, death


def grid(kind, n, c, axes, iters, pool=None, rule='shadow', per=None):
    """Solid on the box given by three 1-D axes. kind 'j' (Julia, c a 3-tuple) or 'm' (Mandelbrot solid).
    Returns inside [nx, ny, nz] bool and death int16."""
    ax, ay, az = [np.asarray(a, float) for a in axes]
    nx = ax.size
    per = per or max(1, int(400000 // (ay.size * az.size)))
    jobs = [(kind, n, c, (ax, ay, az), iters, i, min(nx, i + per), rule) for i in range(0, nx, per)]
    ins = np.zeros((nx, ay.size, az.size), bool); dth = np.zeros((nx, ay.size, az.size), np.int16)
    it = map(_chunk, jobs) if pool is None else pool.imap_unordered(_chunk, jobs)
    for i0, a, d in it:
        ins[i0:i0 + a.shape[0]] = a; dth[i0:i0 + a.shape[0]] = d
    return ins, dth


def cube_axes(cen, L, N):
    a = np.linspace(-L, L, N)
    return a + cen[0], a + cen[1], a + cen[2]


if __name__ == '__main__':
    # checks of the fast gauge and rule against the reference (bisection)
    sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r15'))
    import shadow_ref as S
    rng = np.random.default_rng(5)
    for n in (2, 3, 4, 5):
        P = rng.normal(size=(200000, 3)) * rng.uniform(0.02, 2.5, size=(200000, 1))
        # add hard cases: near the plane Y = 0 (corners and seams), near Z = 0, on the axes
        Q = P[:40000].copy(); Q[:, 1] *= 1e-7
        Q2 = P[40000:80000].copy(); Q2[:, 2] *= 1e-7
        Q3 = P[80000:90000].copy(); Q3[:, 1] = 0
        Q4 = P[90000:100000].copy(); Q4[:, 2] = 0
        A = np.concatenate([P, Q, Q2, Q3, Q4])
        t0 = time.time(); r_ref = S.gauge(A[:, 0], A[:, 1], A[:, 2], n); t1 = time.time()
        r_new = gauge(A[:, 0].copy(), A[:, 1].copy(), A[:, 2].copy(), n); t2 = time.time()
        eg = np.abs(r_new - r_ref) / np.maximum(r_ref, 1e-300)
        f_ref = S.F(A, n)
        fx, fy, fz = F(A[:, 0].copy(), A[:, 1].copy(), A[:, 2].copy(), n)
        f_new = np.stack([fx, fy, fz], 1)
        sc = np.maximum(r_ref, 1e-300) ** n
        ef = np.linalg.norm(f_new - f_ref, axis=1) / sc
        lo, hi = rho_range(n)
        print('n = %d: gauge against bisection, worst relative %.1e (median %.1e); rule against reference, worst %.1e (99.9 %% %.1e) on %d points; '
              'time bisection %.2f s, Newton %.2f s; rho on the unit sphere %.3f to %.3f; escape rho %.2f'
              % (n, eg.max(), np.median(eg), ef.max(), np.quantile(ef, 0.999), A.shape[0], t1 - t0, t2 - t1, lo, hi, resc(n)), flush=True)
