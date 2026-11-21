"""Round 23, section outside1: the fractal community's power-2 "3D Mandelbrot" formulas, as rules of the library.

    import sys; sys.path.insert(0, 'out/r23/outside1'); import outrules as O
    r = O.get('eiffie')            # a rule of out/r21/lib/mem.py (M.Rule); O.NAMES lists them; O.F[name] is the plain F(x, y, z)

Every formula is typed from a quoted source (see formulas.md); nothing here is from memory.
Our axes: the flat plane is z = 0, x is the real line. Where a formula's own best plane is another one it is turned
(the *_t rules), and formulas.md says how.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

EPS = 1e-300


def _bulb_r2(x, y, z):
    """The square used inside msltoe's and eiffie's formulas: Mandelbulb power 2 with zr = 1 - z^2 / (x^2 + y^2 + z^2)."""
    x2, y2, z2 = x * x, y * y, z * z
    zr = 1.0 - z2 / np.maximum(x2 + y2 + z2, EPS)
    return (x2 - y2) * zr, 2 * x * y * zr, 2 * z * np.sqrt(x2 + y2)


def mb2(x, y, z):
    """Mandelbulber 'Classic Mandelbulb Power 2' (White / Nylander), fractal_mandelbulb_power2.cpp."""
    x2, y2, z2 = x * x, y * y, z * z; p2 = x2 + y2; ok = p2 > 0; q = np.where(ok, p2, 1.0)
    t = 1.0 - z2 / q
    return np.where(ok, (x2 - y2) * t, -z2), np.where(ok, 2 * x * y * t, 0.0), -2 * z * np.sqrt(p2)


def quat3d(x, y, z):
    """Mandelbulber 'Quaternion3D' with its default multiplier (1, 2, 2): the quaternion square, cut at w = 0."""
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def bristor(x, y, z):
    """Bristorbrot (Doug Bristor), fractal_bristorbrot.cpp."""
    return x * x - y * y - z * z, y * (2 * x - z), z * (2 * x + y)


def sym2(x, y, z):
    """Msltoe Sym2 Mod (scale 1, offset 0), fractal_msltoe_sym2_mod.cpp."""
    sw = np.abs(y) < np.abs(z); y, z = np.where(sw, z, y), np.where(sw, y, z)
    x = np.where(y > z, -x, x)
    return _bulb_r2(x, y, z)


def sym3(x, y, z):
    """Msltoe Sym3 Mod (scale0 = 0, scale 1, offset 0), fractal_msltoe_sym3_mod.cpp."""
    sw = np.abs(y) < np.abs(z); y, z = np.where(sw, z, y), np.where(sw, y, z)
    fl = y > z; x = np.where(fl, -x, x); z = np.where(fl, -z, z)
    return _bulb_r2(x, y, z)


def sym4(x, y, z):
    """Msltoe Sym4 Mod (all multipliers 1), fractal_msltoe_sym4_mod.cpp: sort so that |x| >= |y| >= |z|, give y and z
    the sign of x, then the quaternion square."""
    s = np.abs(x) < np.abs(z); x, z = np.where(s, z, x), np.where(s, x, z)
    s = np.abs(x) < np.abs(y); x, y = np.where(s, y, x), np.where(s, x, y)
    s = np.abs(y) < np.abs(z); y, z = np.where(s, z, y), np.where(s, y, z)
    z = np.where(x * z < 0, -z, z); y = np.where(x * y < 0, -y, y)
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def eiffie(x, y, z):
    """Eiffie's version of msltoe's symmetric bulb (scale 1, offset 0), fractal_eiffie_msltoe.cpp:
    the turn round the x-axis is folded into a wedge 22.5 degrees wide, then the same square as Sym2."""
    psi = np.abs(np.fmod(np.arctan2(z, y) + np.pi + np.pi / 8, np.pi / 4) - np.pi / 8)
    rho = np.sqrt(y * y + z * z)
    return _bulb_r2(x, np.cos(psi) * rho, np.sin(psi) * rho)


def benesi(x, y, z, cx=-1.0):
    """Benesi power 2, fractal_benesi.cpp (offsets 0). The first coordinate changes sign where c.x >= 0 and x >= rho."""
    r1 = y * y + z * z; tp = np.sqrt(r1)
    X = np.where((cx < 0) | (x < tp), x * x - r1, -x * x + r1)
    k = -2.0 * np.abs(x) / np.maximum(tp, EPS)
    return X, k * (y * y - z * z), k * 2 * y * z


def quickdudley(x, y, z):
    return x * x - 2 * y * z, z * z + 2 * x * y, y * y + 2 * x * z


def lkmitch(x, y, z):
    return x * x - 2 * y * z, z * z + 2 * x * y, y * y - 2 * x * z


def makin3d2(x, y, z):
    return x * x + 2 * y * z, -y * y - 2 * x * z, -z * z + 2 * x * y


def xeno(x, y, z):
    """Xenodreambuie, power 2, both angle offsets 0, fractal_xenodreambuie.cpp (its own axes)."""
    r2 = x * x + y * y + z * z; r = np.sqrt(r2)
    th = 2 * np.arctan2(y, x); ph = np.arccos(np.clip(z / np.maximum(r, EPS), -1, 1))
    ph = np.where(np.abs(ph) > 0.5 * np.pi, np.sign(ph) * np.pi - ph, ph) * 2
    s = np.sin(ph)
    return r2 * np.cos(th) * s, r2 * np.sin(th) * s, r2 * np.cos(ph)


def xeno_t(x, y, z):
    """The same, turned so that its plane y = 0 (real axis = its z) is our plane z = 0 (real axis = x)."""
    X, Y, Z = xeno(y, z, x)
    return Z, X, Y


def mandelcup(shape, scale):
    """Mandelcup (pupukuusikko), mandelcup.cl, with the three 'stereographic' switches on and the others off."""
    def F(x, y, z):
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); rr = np.maximum(r, EPS)
        zz = z / rr + shape
        with np.errstate(all='ignore'):
            a, b = x / rr / zz, y / rr / zz
            p, q = a * a - b * b, 2 * a * b
            t = scale * (1 + shape * shape); p, q = p * t, q * t
            m1 = p * p + q * q - 1; m2 = 1 / (m1 + 2)
            pole = zz == 0                      # the direction that the projection sends to infinity: its image is the +z pole
            return np.where(pole, 0.0, r2 * p * 2 * m2), np.where(pole, 0.0, r2 * q * 2 * m2), np.where(pole, r2, r2 * m1 * m2)
    return F


cup0 = mandelcup(0.0, 1.0)          # the parameter names' own neutral values: Shape = 0, Scale = 1
cup1 = mandelcup(1.0, 0.5)          # Shape = 1, Scale = 1/2: a true stereographic projection, w -> w^2


def mandelnest(x, y, z):
    """Mandelnest (Jeannot), mandelnest.cl, power 2, shift 0: cos(2 acos(u)) = 2 u^2 - 1 on each coordinate, then normalised."""
    r2 = np.maximum(x * x + y * y + z * z, EPS)
    a, b, c = 2 * x * x / r2 - 1, 2 * y * y / r2 - 1, 2 * z * z / r2 - 1
    n = np.maximum(np.sqrt(a * a + b * b + c * c), EPS)
    return r2 * a / n, r2 * b / n, r2 * c / n


def scator_ix(x, y, z):
    """Imaginary scator algebra, 'ix' (Fernandez-Guasti), scator_power2_imaginary.cl. Infinite on the plane x = 0."""
    with np.errstate(all='ignore'):
        # the source has the guard "+ 1e-030f" on x^2 commented out; it is switched on here, because the flat orbit of
        # c = -1 runs into the origin (x = 0 exactly after rounding) and 0 / 0 would lose the flat picture itself
        x2, y2, z2 = x * x + 1e-30, y * y, z * z
        return x2 - y2 - z2 + (y2 * z2) / x2, 2 * x * y * (1 - z2 / x2), 2 * x * z * (1 - y2 / x2)


def hopfcut(x, y, z):
    """The 3D cut (fourth coordinate 0) of the degree-2 Hopfbrot as MathWorld defines it (Knill 2023):
    v = r U(t1, t2, phi) -> r^2 U(2 t1, 2 t2, 2 phi). In the cut t2 is 0 or 180 degrees, so this is the
    Mandelbulb power 2 (plus sign) applied to (x, y, |z|)."""
    z = np.abs(z); x2, y2, z2 = x * x, y * y, z * z; p2 = x2 + y2; ok = p2 > 0; q = np.where(ok, p2, 1.0)
    t = 1.0 - z2 / q
    return np.where(ok, (x2 - y2) * t, -z2), np.where(ok, 2 * x * y * t, 0.0), 2 * z * np.sqrt(p2)


def _hyper_step(x, y, z, st, k, cx, cy, cz):
    """Mandelbulber 'Hypercomplex' (4D, commutative), started with w = 0; w is carried, nothing is added to it."""
    w = st[0]
    return (x * x - y * y - z * z - w * w, 2 * x * y - 2 * w * z, 2 * x * z - 2 * y * w, (2 * x * w - 2 * y * z,))


# ------------------------------------------------------------------ turning a formula so that its best plane is z = 0
def best_plane(F, tries=4000, seed=1):
    """Look for a plane through 0 that F keeps and on which F is complex squaring up to a turn and a size.
    Returns (Ft, info): Ft is F turned and resized so that this plane is z = 0 with exact squaring (if residual ~ 0)."""
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed)
    ang = np.linspace(0, 2 * np.pi, 97)[:-1]

    def basis(n):
        n = n / np.linalg.norm(n); a = np.cross(n, [0.31, 0.52, 0.79]); a /= np.linalg.norm(a); return n, a, np.cross(n, a)

    def fit(n):
        n, a, b = basis(np.asarray(n, float))
        V = np.cos(ang)[:, None] * a + np.sin(ang)[:, None] * b
        W = np.stack(F(V[:, 0], V[:, 1], V[:, 2]), 1)
        u = np.cos(ang) + 1j * np.sin(ang)
        g = (W @ a) + 1j * (W @ b); kap = (g * np.conj(u * u)).mean()         # least squares for g = kappa u^2
        res = np.sqrt((np.abs(W @ n) ** 2).mean() + (np.abs(g - kap * u * u) ** 2).mean())
        return res, kap, (n, a, b)

    N = rng.normal(size=(tries, 3)); sc = np.array([fit(n)[0] for n in N]); best = None
    for i in np.argsort(sc)[:6]:
        o = minimize(lambda n: fit(n)[0], N[i], method='Nelder-Mead', options=dict(xatol=1e-13, fatol=1e-15, maxiter=4000))
        r = fit(o.x)
        if best is None or r[0] < best[0]:
            best = r
    res, kap, (n, a, b) = best
    th = np.angle(kap); k = abs(kap)
    e1 = np.cos(-th) * a + np.sin(-th) * b; e2 = np.cross(n, e1)             # w = kappa u: turn the in-plane axes by -arg kappa
    Rm = np.stack([e1, e2, n])                                               # rows: our x, y, z in the formula's own frame

    def Ft(x, y, z):
        P = [Rm[0, i] * x + Rm[1, i] * y + Rm[2, i] * z for i in range(3)]
        W = F(P[0] / k, P[1] / k, P[2] / k)
        return tuple(k * (Rm[j, 0] * W[0] + Rm[j, 1] * W[1] + Rm[j, 2] * W[2]) for j in range(3))
    return Ft, dict(residual=float(res), normal=[float(t) for t in n], size=float(k), turn_deg=float(np.degrees(th)))


_BP = {}


def turned(name, F):
    if name not in _BP:
        _BP[name] = best_plane(F)
    return _BP[name]


# name -> (F or None, label, source key in formulas.md)
F = {
    'mb2': mb2, 'quat3d': quat3d, 'bristor': bristor, 'sym2': sym2, 'sym3': sym3, 'sym4': sym4, 'eiffie': eiffie,
    'benesi': benesi, 'quickdudley': quickdudley, 'lkmitch': lkmitch, 'makin3d2': makin3d2, 'xeno_t': xeno_t,
    'cup0': cup0, 'cup1': cup1, 'mandelnest': mandelnest, 'scator_ix': scator_ix, 'hopfcut': hopfcut,
}
LABEL = {
    'mb2': 'Mandelbulb, power 2 (White / Nylander)', 'quat3d': 'Quaternion square, 3D cut', 'bristor': 'Bristorbrot',
    'sym2': 'Msltoe Sym2 (square chosen by location)', 'sym3': 'Msltoe Sym3', 'sym4': 'Msltoe Sym4 (largest coordinate is the real one)',
    'eiffie': 'Eiffie / Msltoe (eight folded wedges)', 'benesi': 'Benesi power 2', 'quickdudley': 'Quick Dudley',
    'lkmitch': 'Lkmitch', 'makin3d2': 'Makin 3D-2', 'xeno_t': 'Xenodreambuie power 2 (turned)', 'cup0': 'Mandelcup, Shape 0',
    'cup1': 'Mandelcup, Shape 1, Scale 1/2', 'mandelnest': 'Mandelnest, power 2', 'scator_ix': 'Scator "ix" (imaginary scator square)',
    'hyper': 'Hypercomplex (4D commutative), cut w = 0', 'hopfcut': 'Hopfbrot, degree 2, 3D cut',
    'quickdudley_t': 'Quick Dudley, turned to its best plane', 'lkmitch_t': 'Lkmitch, turned to its best plane',
    'makin3d2_t': 'Makin 3D-2, turned to its best plane',
}
NAMES = ['mb2', 'quat3d', 'bristor', 'sym2', 'sym3', 'sym4', 'eiffie', 'benesi', 'scator_ix', 'hyper', 'quickdudley', 'lkmitch',
         'makin3d2', 'xeno_t', 'cup0', 'cup1', 'mandelnest', 'hopfcut']


def plain(name):
    """The plain F(x, y, z) of a rule (Benesi with c.x < 0; the turned polynomial ones through best_plane)."""
    if name.endswith('_t') and name[:-2] in F:
        return turned(name[:-2], F[name[:-2]])[0]
    return F[name]


def get(name):
    if name == 'hyper':
        return M.Rule('hyper', LABEL['hyper'], _hyper_step, init=lambda n: (np.zeros(n),))
    if name == 'benesi':
        return M.Rule('benesi', LABEL['benesi'], lambda x, y, z, st, k, cx, cy, cz: (*benesi(x, y, z, cx), st), init=lambda n: ())
    f = plain(name)

    def step(x, y, z, st, k, cx, cy, cz, f=f):
        with np.errstate(all='ignore'):
            return (*f(x, y, z), st)
    return M.Rule(name, LABEL[name], step, init=lambda n: ())


if __name__ == '__main__':
    rng = np.random.default_rng(1); P = rng.normal(size=(20000, 3))
    for nm in NAMES:
        if nm == 'hyper':
            continue
        f = plain(nm)
        with np.errstate(all='ignore'):
            X, Y, Z = f(P[:, 0], P[:, 1], P[:, 2])
            ln = np.sqrt(X * X + Y * Y + Z * Z) / (P ** 2).sum(1)
            X0, Y0, Z0 = f(P[:, 0], P[:, 1], 0 * P[:, 2])
        pl = np.nanmax(np.abs(np.stack([X0 - (P[:, 0] ** 2 - P[:, 1] ** 2), Y0 - 2 * P[:, 0] * P[:, 1], Z0])))
        fin = np.isfinite(X + Y + Z).mean()
        extra = ''
        if nm in ('quickdudley', 'lkmitch', 'makin3d2', 'bristor'):
            extra = ' | best plane: %s' % (turned(nm, F[nm])[1],)
        print('%-14s finite %.4f | length / r^2 between %.3f and %.3f | z = 0 against complex squaring %.1e%s'
              % (nm, fin, np.nanmin(ln), np.nanmax(ln), pl, extra), flush=True)
