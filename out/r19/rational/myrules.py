"""Round 19, section "rational" (prefix q_): smooth angle-keeping surplus.

The sphere of directions in the coordinate of a hemisphere:  w = (x + i y) / (r + |z|)
    |w| = 1 on the flat plane, w = 0 straight up (or straight down for the lower half; the rule is mirrored).
The one-plane rule is  w -> w^2.  The rules here use, on a cap round the upright axis, an angle-keeping map of the
WHOLE sphere that covers it 4 times (d = 1) or 6 times (d = 2) and keeps the flat circle:

    R(w) = (w^n - beta) / ( w^d (1 - beta w^n) ),   n = d + 2,   beta real

(for d = 1 this is the round-17 "pole rule" eta^2 + lam / eta made mirror-symmetric; for d = 2 it is a function of
w^2, so the rule gives the same answer for v and for v turned half a turn about the upright axis, as squaring does).
R is NOT the doubling on the flat circle. Round 17 mended that by a change of angle carried along meridians. Here it
is mended by a band: the rule IS the one-plane rule for |w| >= rho0 (a band round the flat plane), IS R for
|w| <= rho1 (the cap), and in between

    G = w^2 * exp( kappa(|w|) * Log( R(w) / w^2 ) ),   kappa = 1 at rho1 falling smoothly (quintic) to 0 at rho0,

which has no tear and no crease (two derivatives agree at both ends) but does not keep angles in that ring.
Answer:  r^2 * ( 2 Re G, 2 Im G, sign(z) (1 - |G|^2) ) / (1 + |G|^2).

q_c*: the round-17 way kept for comparison (R everywhere, change of angle tau on the flat circle with
R(e^(i tau(t))) = e^(i tau(2t)), faded out with height instead of carried up the meridians).
"""
import numpy as np

EPS = 1e-300


def band(beta, d, rho1, rho0, pw=0):
    """pw = 0: the fade kappa runs evenly in log |w| (first try; folds 1.5 % of directions for the stretch-2 size).
    pw = n: it runs evenly in |w|^n, so that it changes slowly where R / w^2 is far from 1 (next to the cap) and
    fast where it is near 1 (next to the band)."""
    n = d + 2
    l1, l0 = np.log(rho1), np.log(rho0)
    p1, p0 = rho1 ** max(pw, 1), rho0 ** max(pw, 1)

    def F(x, y, z):
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r2 = x * x + y * y + z * z
        dead = ~(r2 > 1e-200)                         # the origin (and underflow next to it): the answer is 0
        r = np.sqrt(np.where(dead, 1.0, r2)); az = np.abs(z)
        w = np.where(dead, 1.0, x + 1j * y) / (r + np.where(dead, 0.0, az))
        m = np.abs(w)
        tiny = m < 1e-20                              # on the upright axis: the answer is the opposite pole
        ws = np.where(tiny, 1.0, w)
        wn = ws ** n
        cap = m <= rho1
        Rv = (wn - beta) / (ws ** d * (1.0 - beta * wn))
        if pw:
            u = np.clip((m ** pw - p1) / (p0 - p1), 0.0, 1.0)
        else:
            u = np.clip((np.log(np.maximum(m, 1e-30)) - l1) / (l0 - l1), 0.0, 1.0)
        kap = 1.0 - u * u * u * (10.0 - 15.0 * u + 6.0 * u * u)
        wn2 = np.where(cap, 1.0, wn)                  # outside the cap |beta / w^n| < 1: the principal Log is continuous
        L = np.log((1.0 - beta / wn2) / (1.0 - beta * wn2))
        G = np.where(cap, Rv, ws * ws * np.exp(kap * L))
        g2 = G.real * G.real + G.imag * G.imag
        k = r2 / (1.0 + g2)
        sg = np.where(z < 0, -1.0, 1.0)
        X = np.where(tiny, 0.0, 2 * k * G.real); Y = np.where(tiny, 0.0, 2 * k * G.imag)
        Z = np.where(tiny, -sg * r2, sg * k * (1.0 - g2))
        flat = z == 0
        X = np.where(flat, x * x - y * y, X); Y = np.where(flat, 2 * x * y, Y); Z = np.where(flat, 0.0, Z)
        return np.where(dead, 0.0, X), np.where(dead, 0.0, Y), np.where(dead, 0.0, Z)
    return F


def angle_table(beta, d, n=1 << 18):
    """tau on [0, 2 pi] with g(tau(t)) = tau(2 t) mod 2 pi, g = the angle map of R on the flat circle."""
    nn = d + 2
    fine = np.linspace(0.0, 2 * np.pi, 8 * n + 1)
    gf = 2 * fine + 2 * np.arctan2(beta * np.sin(nn * fine), 1 - beta * np.cos(nn * fine))   # rising iff R' > 0 on the circle
    grid = np.linspace(0.0, 2 * np.pi, n + 1)
    tau = grid.copy()
    for _ in range(400):
        t2 = np.mod(2 * grid, 2 * np.pi); t2[-1] = 2 * np.pi; wrap = (2 * grid >= 2 * np.pi) & (grid < 2 * np.pi)
        target = np.interp(t2, grid, tau) + np.where(wrap, 2 * np.pi, 0.0)
        target[-1] = 4 * np.pi
        new = np.interp(target, gf, fine); new[0] = 0.0; new[-1] = 2 * np.pi
        dlt = np.abs(new - tau).max(); tau = new
        if dlt < 1e-14:
            break
    return grid, tau, gf, fine


def faded(beta, d, rho1, rho0, n=1 << 16):
    """R everywhere, the flat circle mended by the change of angle tau, faded out with height:
    direction map = h^-1 o R o h,  h(rho e^(i t)) = rho e^(i (t + kappa(rho) (tau(t) - t))),  kappa = 1 on the flat
    plane, 0 for rho <= rho1. h^-1 by bisection on the table."""
    nn = d + 2
    tab = []                                          # built on first use, so that loading this file costs nothing
    l1, l0 = np.log(rho1), np.log(rho0)

    def kappa(m):
        u = np.clip((np.log(np.maximum(m, 1e-30)) - l1) / (l0 - l1), 0.0, 1.0)
        return u * u * u * (10.0 - 15.0 * u + 6.0 * u * u)

    def F(x, y, z):
        if not tab:
            tab.extend(angle_table(beta, d, n)[:2])
        grid, tau = tab
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r2 = x * x + y * y + z * z
        dead = ~(r2 > 1e-200)
        r = np.sqrt(np.where(dead, 1.0, r2)); az = np.abs(z)
        w = np.where(dead, 1.0, x + 1j * y) / (r + np.where(dead, 0.0, az))
        m = np.abs(w); tiny = m < 1e-20
        t = np.mod(np.arctan2(w.imag, w.real), 2 * np.pi)
        k1 = kappa(m)
        t1 = t + k1 * (np.interp(t, grid, tau) - t)
        ws = np.where(tiny, 1.0, m * np.exp(1j * t1))
        wn = ws ** nn
        W = (wn - beta) / (ws ** d * (1.0 - beta * wn))
        M = np.abs(W); T1 = np.mod(np.arctan2(W.imag, W.real), 2 * np.pi)
        Mi = np.where(M > 1, 1.0 / np.maximum(M, 1e-300), M)            # the mirror height of the answer
        k2 = kappa(Mi)
        lo = np.zeros_like(T1); hi = np.full_like(T1, 2 * np.pi)
        for _ in range(36):                                             # solve s + k2 (tau(s) - s) = T1
            mid = 0.5 * (lo + hi)
            v = mid + k2 * (np.interp(mid, grid, tau) - mid)
            up = v < T1
            lo = np.where(up, mid, lo); hi = np.where(up, hi, mid)
        T = 0.5 * (lo + hi)
        g2 = M * M
        k = r2 / (1.0 + g2)
        sg = np.where(z < 0, -1.0, 1.0)
        X = np.where(tiny, 0.0, 2 * k * M * np.cos(T)); Y = np.where(tiny, 0.0, 2 * k * M * np.sin(T))
        Z = np.where(tiny, -sg * r2, sg * k * (1.0 - g2))
        flat = z == 0
        X = np.where(flat, x * x - y * y, X); Y = np.where(flat, 2 * x * y, Y); Z = np.where(flat, 0.0, Z)
        return np.where(dead, 0.0, X), np.where(dead, 0.0, Y), np.where(dead, 0.0, Z)
    return F


# beta for d = 2 fixed by the principle "the extra bud and arm directions arrive with stretch exactly 2" (predict.py):
B6 = 0.134614
RULES = {
    # the fade: cap to 1.08 x the radius where the directions sent straight up sit, pacing |w|^n (foldscan.py: no fold)
    'q_6m':  (band(-B6, 2, 0.654, 1.00, 4),     'Six-fold rational cap, stretch 2 at the extra buds and arms (buds in the plane x = 0, arms in the upright plane y = 0, 43 degrees from upright); fades into the one-plane rule at the flat plane', ''),
    'q_6mb': (band(-B6, 2, 0.654, 0.93, 8),     'The same with a true one-plane band (4 degrees each side of the flat plane)', ''),
    'q_6p':  (band(+B6, 2, 0.654, 1.00, 4),     'Six-fold rational cap, other sign (extra buds in the upright plane y = 0, arms in the plane x = 0, stretch 4)', ''),
    'q_6h':  (band(-0.0666, 2, 0.549, 1.00, 4), 'Six-fold rational cap, six buds evenly round the x-axis (30 degrees from upright, stretch 3.4)', ''),
    'q_4p':  (band(+0.268, 1, 0.696, 1.00, 6),  'Four-fold rational cap, beta = +0.268 (extra bud forward, extra arm backward; stretch 2.5 and 1.4)', ''),
    'q_4m':  (band(-0.268, 1, 0.696, 1.00, 6),  'Four-fold rational cap, beta = -0.268 (extra bud backward, extra arm forward)', ''),
    # the round-17 way, for comparison: R everywhere, the flat circle mended by a change of angle that fades out with height
    'q_c6':  (faded(+0.03, 2, 0.50, 1.00),      'Six-fold rational map everywhere (beta = +0.03), flat circle mended by a change of angle that fades with height', ''),
    'q_c4':  (faded(+0.05, 1, 0.45, 1.00),      'Four-fold rational map everywhere (beta = +0.05), flat circle mended by a change of angle that fades with height', ''),
    # smaller surplus (the stretch at the extra directions is then well above 2)
    'q_6p6': (band(+0.0666, 2, 0.549, 1.00, 4), 'Six-fold rational cap, beta = +0.0666 (extra directions 30 degrees from upright, stretch about 4.3)', ''),
    'q_6p3': (band(+0.03, 2, 0.45, 1.00, 4),    'Six-fold rational cap, beta = +0.03 (extra directions 19 degrees from upright, stretch 6.4)', ''),
    'q_6m3': (band(-0.03, 2, 0.45, 1.00, 4),    'Six-fold rational cap, beta = -0.03 (extra directions 20 degrees from upright, stretch 5.5)', ''),
    'q_4s':  (band(+0.10, 1, 0.50, 1.00, 6),    'Four-fold rational cap, beta = +0.10 (extra directions 11 degrees from upright, stretch about 5)', ''),
}
