"""Round 17, section "profiles" (prefix p_): the reference-plane family.

    F(v) = Rot_x(psi) P( Rot_x(-psi) v ),   P = the one-plane square,   psi = psi(phi, u)
    phi = atan2(z, y)  (which way the point lies round the x-axis),  u = x / |v|  (+1 on the positive x-axis,
    0 on the plane x = 0, -1 on the negative x-axis),  t = sqrt(1 - u^2)  (0 on the axis, 1 on the plane x = 0).

Every member:  psi = q * (phi - a(u) * g(4 phi) / 4),  g odd, 2 pi periodic, g(0) = g(pi) = 0, so psi = 0 on z = 0 and
pi / 2 on y = 0 (both planes follow complex squaring exactly), and the rule commutes with both mirrors.
q = +1: the plane turns with the point ("along" kind);  q = -1: against it ("away" kind).
The bench loads RULES from this file. Stand-alone numpy, no imports from the project.
"""
import math
import numpy as np

EPS = 1e-300


def oneplane(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); f = r2 / np.maximum(r2 + z * z, EPS)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * z * r


def about(psi_fn):
    """The one-plane square about the plane through the x-axis turned by psi_fn(phi, u)."""
    def F(x, y, z):
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r = np.sqrt(x * x + y * y + z * z)
        u = np.clip(x / np.maximum(r, EPS), -1.0, 1.0)
        phi = np.arctan2(z, y)
        psi = psi_fn(phi, u)
        c, s = np.cos(psi), np.sin(psi)
        X, Y, Z = oneplane(x, c * y + s * z, -s * y + c * z)
        return X, c * Y - s * Z, s * Y + c * Z
    return F


# ---- the shapes g (what the reference plane does as the point goes round the axis) -------------------------
def g_sin(s):                      # d psi / d phi = 1 - a cos(4 phi): the round-16 shape
    return np.sin(s)


def g_notch(m):
    """Narrow flat spots: d psi / d phi = 1 - a K(4 phi), K = (cos^(2m)(s/2) - mu) / (1 - mu). With a = 1 the slope is
    0 on the planes and at most 1 + mu / (1 - mu) between them (m = 4: 1.38, m = 8: 1.24)."""
    mu = math.comb(2 * m, m) / 4.0 ** m
    co = [2.0 * math.comb(2 * m, m - k) / 4.0 ** m / (1 - mu) / k for k in range(1, m + 1)]
    def g(s):
        out = 0.0
        for k, ck in enumerate(co, 1):
            out = out + ck * np.sin(k * s)
        return out
    return g


def g_hump(m):
    """Wide flat spots, steep crossing: d psi / d phi = sin^(2m)(2 phi) / mu (m = 1 is the round-16 shape, slope 2 at
    the crossing; m = 4: 3.7; m = 16: 7.1)."""
    mu = math.comb(2 * m, m) / 4.0 ** m
    co = [-2.0 * (-1) ** k * math.comb(2 * m, m - k) / 4.0 ** m / mu / k for k in range(1, m + 1)]
    def g(s):
        out = 0.0
        for k, ck in enumerate(co, 1):
            out = out + ck * np.sin(k * s)
        return out
    return g


def fam(g, a=None, q=1.0):
    """psi = q (phi - a(u) g(4 phi) / 4)."""
    def psi(phi, u):
        w = g(4 * phi) * 0.25
        if a is not None:
            w = w * a(u)
        return q * (phi - w)
    return about(psi)


def step_tt(kappa, q=1.0):
    """psi is the nearest plane's angle almost everywhere (as in "two planes"), crossing from one plane to the next
    in a band round each diagonal, infinitely smooth:  psi = (pi/2) (n + S(f)),  phi = (pi/2)(n + f),
    S(f) = (1 + tanh(kappa tan(pi (f - 1/2)))) / 2.  Slope at the crossing 1.57 kappa."""
    def psi(phi, u):
        w = phi / (0.5 * np.pi); n = np.floor(w); f = w - n
        S = 0.5 * (1 + np.tanh(kappa * np.tan(np.pi * (np.clip(f, 1e-12, 1 - 1e-12) - 0.5))))
        S = np.where(f <= 0, 0.0, S)
        return q * 0.5 * np.pi * (n + S)
    return about(psi)


# ---- how strongly the shape is applied, by where the point stands along the axis -----------------------------
def a_lin(u):                      # 0 on the axis (pure lathe there), 1 on the plane x = 0
    return np.sqrt(np.maximum(1 - u * u, 0.0))


def a_ss(u):
    t = np.sqrt(np.maximum(1 - u * u, 0.0)); return t * t * (3 - 2 * t)


def a_cot(u):                      # 1 for x >= 0; (r + x) / (r - x) for x < 0: lathe only at the NEGATIVE axis
    return np.minimum(1.0, (1 + u) / np.maximum(1 - u, EPS))


def a_const(v):
    return lambda u: v


def a_cotk(k):                     # the same, k times stronger before it is capped at 1
    return lambda u: np.minimum(1.0, k * (1 + u) / np.maximum(1 - u, EPS))


def rat4(a):
    """SCOUT ONLY. Direction map = a degree-4 angle-keeping map of the sphere that keeps the circle of the flat plane
    and goes round it twice:  R(w) = w^3 (1 - a w) / (w - a),  w = (x + i y) / (r + z)  (the flat plane is |w| = 1,
    the direction +z is w = 0). Length squared as always. a = 0 is the one-plane rule. On the flat plane the angle is
    NOT doubled exactly (it would need a change of angle first), so the cut at z = 0 is not the flat set."""
    def F(x, y, z):
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r2 = x * x + y * y + z * z; r = np.sqrt(r2)
        up = z >= 0                                  # work in the half where the coordinate is at most 1 in size, mirror back
        zz = np.abs(z)
        w = (x + 1j * y) / np.maximum(r + zz, EPS)
        W = w ** 3 * (1 - a * w) / np.where(np.abs(w - a) < 1e-300, 1e-300, w - a)
        m2 = W.real ** 2 + W.imag ** 2
        k = r2 / (1 + m2)
        X, Y, Z = 2 * W.real * k, 2 * W.imag * k, (1 - m2) * k
        return X, Y, np.where(up, Z, -Z)
    return F



def rat4c(a, n=1 << 17):
    """SCOUT ONLY (not a member of the reference-plane family). The same angle-keeping 4-wrap map R as rat4, seen
    through a change of angle round the z-axis, so that on the flat plane the angle is doubled exactly:
        direction map = h^-1 o R o h,   h(rho e^(i t)) = rho e^(i tau(t)),   R(e^(i tau(t))) = e^(i tau(2 t)).
    tau is found by iterating tau(t) = g^-1(tau(2 t)), g(t) = 2 t - 2 atan(a sin t / (1 - a cos t)) (R on the circle),
    on a grid of n points on [0, pi]; tau(-t) = -tau(t). tau is continuous and rising but not smooth, and this simple
    way of carrying it off the flat plane (along the meridians of the z-axis) is the crude one. z = 0 exactly in gives
    the complex square exactly."""
    grid = np.linspace(0.0, np.pi, n + 1)
    fine = np.linspace(0.0, np.pi, 4 * n + 1)
    gf = 2 * fine - 2 * np.arctan2(a * np.sin(fine), 1 - a * np.cos(fine)); gf[0] = 0.0; gf[-1] = 2 * np.pi
    tau = grid.copy(); k2 = 2 * np.arange(n + 1)
    for _ in range(120):
        ext = np.where(k2 <= n, tau[np.minimum(k2, n)], 2 * np.pi - tau[np.clip(2 * n - k2, 0, n)])
        new = np.interp(ext, gf, fine); new[0] = 0.0; new[-1] = np.pi
        if np.abs(new - tau).max() < 1e-15:
            tau = new; break
        tau = new
    def F(x, y, z):
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); zz = np.abs(z)
        rho = np.sqrt(x * x + y * y) / np.maximum(r + zz, EPS)
        t = np.arctan2(y, x)
        t1 = np.sign(t) * np.interp(np.abs(t), grid, tau)
        w = rho * (np.cos(t1) + 1j * np.sin(t1))
        d = w - a; d = np.where(np.abs(d) < 1e-150, 1e-150, d)
        W = w ** 3 * (1 - a * w) / d
        m = np.minimum(np.abs(W), 1e150); T1 = np.arctan2(W.imag, W.real)
        T = np.sign(T1) * np.interp(np.abs(T1), tau, grid)
        k = r2 / (1 + m * m)
        X, Y, Z = 2 * m * np.cos(T) * k, 2 * m * np.sin(T) * k, (1 - m * m) * k
        flat = z == 0
        X = np.where(flat, x * x - y * y, X); Y = np.where(flat, 2 * x * y, Y); Z = np.where(flat, 0.0, np.where(z > 0, Z, -Z))
        return X, Y, Z
    return F



def one_spot(q=1.0):
    """A flat spot at the flat plane only: psi = q (phi - sin(2 phi) / 2). The upright plane is still kept exactly
    (psi = 90 degrees there) but the reference plane sweeps through it at slope 2 instead of resting on it."""
    def psi(phi, u):
        return q * (phi - 0.5 * np.sin(2 * phi))
    return about(psi)



RULES = {
    # the orchestrator's first candidates: lathe at the axis, the round-16 shape on the plane x = 0
    'p_lin':    (fam(g_sin, a_lin),        'Turning plane, along; fades to the lathe at the axis (a = t)', ''),
    'p_ss':     (fam(g_sin, a_ss),         'Turning plane, along; fades to the lathe at the axis (smooth step)', ''),
    # lathe only at the negative axis, chosen so that the sideways stretch never exceeds the in-plane stretch
    'p_cot':    (fam(g_sin, a_cot),        'Turning plane, along; fades to the lathe at the negative axis only', ''),
    # gentler everywhere
    'p_half':   (fam(g_sin, a_const(0.5)), 'Turning plane, along, half strength (slope 0.5 to 1.5)', ''),
    # narrow flat spots, gentle crossing
    'p_n4':     (fam(g_notch(4)),          'Turning plane, along; narrow flat spots (slope at most 1.38)', ''),
    'p_n8':     (fam(g_notch(8)),          'Turning plane, along; narrower flat spots (slope at most 1.24)', ''),
    'p_n8c':    (fam(g_notch(8), a_cotk(4.1)), 'Turning plane, along; narrow flat spots, lathe at the negative axis', ''),
    # wide flat spots, steep crossing
    'p_h4':     (fam(g_hump(4)),           'Turning plane, along; wide flat spots (crossing slope 3.7)', ''),
    'p_h16':    (fam(g_hump(16)),          'Turning plane, along; wider flat spots (crossing slope 7.1)', ''),
    'p_tt1':    (step_tt(1.0),             'Nearest plane, crossing smoothed (slope 1.6)', ''),
    'p_tt4':    (step_tt(4.0),             'Nearest plane, crossing smoothed (slope 6.3)', ''),
    'p_tt16':   (step_tt(16.0),            'Nearest plane, crossing smoothed in a thin band (slope 25)', ''),
    # the "away" kind (plane turns against the point)
    'p_aw_n8':  (fam(g_notch(8), q=-1.0),  'Turning plane, away; narrow flat spots', ''),
    'p_aw_h4':  (fam(g_hump(4), q=-1.0),   'Turning plane, away; wide flat spots', ''),
    'p_aw_tt4': (step_tt(4.0, q=-1.0),     'Nearest plane mirrored, crossing smoothed (away kind)', ''),
    'p_tt64':   (step_tt(64.0),            'Nearest plane, crossing smoothed in a very thin band (slope 100)', ''),
    'p_tt256':  (step_tt(256.0),           'Nearest plane, crossing smoothed in a hair-thin band (slope 400)', ''),
    'p_tt1024': (step_tt(1024.0),          'Nearest plane, crossing smoothed in a band 0.1 degrees wide (slope 1600)', ''),
    'p_aw_tt16': (step_tt(16.0, q=-1.0),   'Nearest plane mirrored, crossing smoothed in a thin band (away kind)', ''),
    'p_aw_tt64': (step_tt(64.0, q=-1.0),   'Nearest plane mirrored, crossing smoothed in a very thin band (away kind)', ''),
    'p_aw_tt256': (step_tt(256.0, q=-1.0), 'Nearest plane mirrored, crossing smoothed in a hair-thin band (away kind)', ''),
    'p_tt128':  (step_tt(128.0),           'Nearest plane, crossing smoothed in a band 0.9 degrees wide (slope 200)', ''),
    'p_aw_tt1024': (step_tt(1024.0, q=-1.0), 'Nearest plane mirrored, crossing smoothed in a band 0.1 degrees wide (away kind)', ''),
    # SCOUT, NOT a member of the family and NOT exact on z = 0 (fails J1 by construction): see report.md, "best next"
    'p_x_rat25': (rat4(0.25),              'SCOUT: directions by the angle-keeping map w^3 (1 - a w) / (w - a), a = 0.25 (cut z = 0 NOT exact)', ''),
    'p_x_ratc25': (rat4c(0.25),            'SCOUT: angle-keeping 4-wrap direction map with a change of angle (exact on z = 0; crude version)', ''),
    'p_x_ratc15': (rat4c(0.15),            'SCOUT: the same, a = 0.15', ''),
    'p_m1':     (one_spot(1.0),            'Turning plane, along; a flat spot at the flat plane only', ''),
    'p_aw_m1':  (one_spot(-1.0),           'Turning plane, away; a flat spot at the flat plane only', ''),
}
