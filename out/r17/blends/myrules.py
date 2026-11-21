"""Round 17, section "blends" (prefix b_): rules that are not a turned one-plane rule.
Every rule: F(x, y, z) -> (X, Y, Z) on numpy arrays, no c added, |F(v)| = |v|^2, exact complex squaring on z = 0.

Two kinds:
  b_avg, b_avg4, b_slerp, b_avgl   the brief's starting points: the two one-plane answers P1 (about z = 0) and
                                   P2 (about y = 0) blended, brought back to length |v|^2.
  b_pole*, b_pol2*                 my own: the one-plane rule with the top and bottom of the sphere of directions
                                   re-injected (a pole term), see report.md. In the flat coordinate of a hemisphere,
                                   eta = (x + i y) / (r + |z|)  (|eta| = 1 on the flat plane, 0 on the z-axis):
                                       one plane:   G = eta^2
                                       pole rule:   G = eta^2 + lam (1 - |eta|^2)^p / eta^d
                                   and the answer is r^2 * (2 Re G, 2 Im G, sign(z) (1 - |G|^2)) / (1 + |G|^2).
"""
import numpy as np

EPS = 1e-300


def P1(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); f = r2 / np.maximum(r2 + z * z, EPS)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * z * r


def P2(x, y, z):
    X, Z, Y = P1(x, z, y)
    return X, Y, Z


def _norm(X, Y, Z, r2):
    n = np.sqrt(X * X + Y * Y + Z * Z); ok = n > 0
    k = np.where(ok, r2 / np.where(ok, n, 1.0), 0.0)
    return k * X, k * Y, k * Z


def avg(power):
    """(a) weighted average of P1 and P2, weights |y|^p / (|y|^p + |z|^p) and |z|^p / (...), back to length r^2."""
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        a, b = np.abs(y) ** power, np.abs(z) ** power; s = a + b; ok = s > 0
        w1 = np.where(ok, a / np.where(ok, s, 1.0), 1.0); w2 = 1.0 - w1
        X1, Y1, Z1 = P1(x, y, z); X2, Y2, Z2 = P2(x, y, z)
        return _norm(w1 * X1 + w2 * X2, w1 * Y1 + w2 * Y2, w1 * Z1 + w2 * Z2, r2)
    return F


def slerp(x, y, z):
    """(b) turn on the sphere of directions from P1's answer to P2's answer, by the share z^2 / (y^2 + z^2)."""
    r2 = x * x + y * y + z * z
    s = y * y + z * z; ok = s > 0
    t = np.where(ok, z * z / np.where(ok, s, 1.0), 0.0)
    X1, Y1, Z1 = P1(x, y, z); X2, Y2, Z2 = P2(x, y, z)
    q = np.maximum(r2 * r2, EPS)
    dot = np.clip((X1 * X2 + Y1 * Y2 + Z1 * Z2) / q, -1.0, 1.0); om = np.arccos(dot); so = np.sin(om)
    small = so < 1e-9
    sos = np.where(small, 1.0, so)
    a = np.where(small, 1.0 - t, np.sin((1.0 - t) * om) / sos); b = np.where(small, t, np.sin(t * om) / sos)
    return _norm(a * X1 + b * X2, a * Y1 + b * Y2, a * Z1 + b * Z2, r2)


def avgl(x, y, z):
    """(a) with the lathe mixed in near the x-axis: lathe share = sin^2(2 phi) * (x^2 / r^2)^2."""
    r2 = x * x + y * y + z * z
    s = y * y + z * z; ok = s > 0; sd = np.where(ok, s, 1.0)
    w2 = np.where(ok, z * z / sd, 0.0); w1 = 1.0 - w2
    wl = np.where(ok, 4 * y * y * z * z / (sd * sd), 0.0) * (x * x / np.maximum(r2, EPS)) ** 2
    X1, Y1, Z1 = P1(x, y, z); X2, Y2, Z2 = P2(x, y, z)
    XL, YL, ZL = x * x - y * y - z * z, 2 * x * y, 2 * x * z
    u = 1.0 - wl
    return _norm(u * (w1 * X1 + w2 * X2) + wl * XL, u * (w1 * Y1 + w2 * Y2) + wl * YL, u * (w1 * Z1 + w2 * Z2) + wl * ZL, r2)


def pole(lam, d=1, p=2):
    """One-plane rule with a pole term: G = eta^2 + lam (1 - |eta|^2)^p / eta^d on each hemisphere."""
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        dead = ~(r2 > 1e-200)                        # the origin (and underflow next to it): the answer is 0
        r = np.sqrt(np.where(dead, 1.0, r2)); az = np.abs(z)
        e = np.where(dead, 1.0, x + 1j * y) / (r + np.where(dead, 0.0, az))   # |e| <= 1, = 1 on the flat plane, 0 on the z-axis
        m2 = np.minimum(e.real * e.real + e.imag * e.imag, 1.0)
        tiny = m2 < 1e-40                            # on the z-axis: the answer is the opposite pole
        es = np.where(tiny, 1.0, e)
        G = e * e + lam * (1.0 - m2) ** p / es ** d
        g2 = G.real * G.real + G.imag * G.imag
        k = r2 / (1.0 + g2)
        sg = np.where(z < 0, -1.0, 1.0)
        X = np.where(tiny, 0.0, 2 * k * G.real); Y = np.where(tiny, 0.0, 2 * k * G.imag)
        Z = np.where(tiny, -sg * r2, sg * k * (1.0 - g2))
        return np.where(dead, 0.0, X), np.where(dead, 0.0, Y), np.where(dead, 0.0, Z)
    return F


def polec(lam, d=1, s1=0.2, s2=1.0):
    """The pole rule with a cut-off that is flat near the pole: G = eta^2 + lam * chi(|eta|^2) / eta^d,
    chi = 1 for |eta|^2 <= s1, falls smoothly (quintic step) to 0 at |eta|^2 = s2, 0 beyond.
    So the rule IS the one-plane rule (keeps angles) for |eta|^2 >= s2 and is free of the cut-off near the pole."""
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        dead = ~(r2 > 1e-200)
        r = np.sqrt(np.where(dead, 1.0, r2)); az = np.abs(z)
        e = np.where(dead, 1.0, x + 1j * y) / (r + np.where(dead, 0.0, az))
        m2 = np.minimum(e.real * e.real + e.imag * e.imag, 1.0)
        tiny = m2 < 1e-40
        es = np.where(tiny, 1.0, e)
        u = np.clip((m2 - s1) / (s2 - s1), 0.0, 1.0)
        chi = 1.0 - u * u * u * (10.0 - 15.0 * u + 6.0 * u * u)
        G = e * e + lam * chi / es ** d
        g2 = G.real * G.real + G.imag * G.imag
        k = r2 / (1.0 + g2)
        sg = np.where(z < 0, -1.0, 1.0)
        X = np.where(tiny, 0.0, 2 * k * G.real); Y = np.where(tiny, 0.0, 2 * k * G.imag)
        Z = np.where(tiny, -sg * r2, sg * k * (1.0 - g2))
        return np.where(dead, 0.0, X), np.where(dead, 0.0, Y), np.where(dead, 0.0, Z)
    return F


RULES = {
    'b_avg':    (avg(2),            'Blend: average of the two one-plane answers (weights y^2, z^2)', ''),
    'b_avg4':   (avg(4),            'Blend: average of the two one-plane answers (weights y^4, z^4)', ''),
    'b_avg16':  (avg(16),           'Blend: average of the two one-plane answers (weights y^16, z^16)', ''),
    'b_slerp':  (slerp,             'Blend: great-circle turn from the one answer to the other', ''),
    'b_avgl':   (avgl,              'Blend: average, lathe mixed in near the x-axis', ''),
    'b_pole':   (pole(-4.0 / 27.0), 'One plane with a pole term, odd, lam = -4/27', ''),
    'b_polep':  (pole(+4.0 / 27.0), 'One plane with a pole term, odd, lam = +4/27', ''),
    'b_poleh':  (pole(-0.5),        'One plane with a pole term, odd, lam = -1/2', ''),
    'b_pol2':   (pole(-1.0 / 16.0, d=2), 'One plane with an even pole term, lam = -1/16', ''),
    'b_pol2p':  (pole(+1.0 / 16.0, d=2), 'One plane with an even pole term, lam = +1/16', ''),
    'b_pca':    (polec(-0.02, 1, 0.16), 'Pole rule, flat cut-off, lam = -0.02', ''),
    'b_pcb':    (polec(-0.05, 1, 0.20), 'Pole rule, flat cut-off, lam = -0.05', ''),
    'b_pcc':    (polec(-0.10, 1, 0.25), 'Pole rule, flat cut-off, lam = -0.10', ''),
    'b_pcd':    (polec(-4.0 / 27.0, 1, 0.30), 'Pole rule, flat cut-off, lam = -4/27', ''),
    'b_pce':    (polec(-0.01, 2, 0.20), 'Even pole rule, flat cut-off, lam = -0.01', ''),
    'b_pcf':    (polec(+0.05, 1, 0.20), 'Pole rule, flat cut-off, lam = +0.05', ''),
    'b_pch':    (polec(-1.0 / 16.0, 2, 0.36), 'Even pole rule, flat cut-off, lam = -1/16', ''),
    'b_pci':    (polec(+1.0 / 16.0, 2, 0.36), 'Even pole rule, flat cut-off, lam = +1/16', ''),
    'b_pcg':    (polec(-0.05, 1, 0.20, 0.6), 'Pole rule, flat cut-off ending at 0.6, lam = -0.05', ''),
}
