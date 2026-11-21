"""Round 20 prover: shared pieces. Nothing here is registered with the bench (no myrules.py): these rules exist only
to test statements W1..W6 about 'wind, then square'.

    F(v) = P_n(T(v)),  T: (x, rho, a) -> (x, rho, g(a)),  a = turn round the x-axis from the half y > 0 of the flat plane
    P_n = the one-plane power n: on the sphere of directions w -> w^n in the stereographic coordinate
          w = (x + i y) / (r - z); length r -> r^n.  n = 2 is S.oneplane of out/me/r16/scout.py (checked in exact.py).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r19', 'me'))
import scout as S                      # S.oneplane
import myrules as M19                  # M19.wind(k, profile) : the orchestrator's rule code, used as it stands

SETS = {'basilica': (-1.0, 0.0, 0.0), 'rabbit': (-0.122561, 0.744862, 0.0),
        'dendrite': (0.0, 1.0, 0.0), 'siegel': (-0.390541, -0.586788, 0.0)}


def Pn(n):
    """One-plane power n (whole n >= 1)."""
    def P(x, y, z):
        x, y, z = (np.asarray(t, float) for t in (x, y, z))
        r2 = x * x + y * y + z * z; r = np.sqrt(r2)
        s = np.where(r > 0, z / np.maximum(r, 1e-300), 0.0)
        A = (1 + s) ** n; B = (1 - s) ** n
        s2 = (A - B) / (A + B)                           # sine of the new latitude
        h2 = 2 * (1 - s * s) ** (n / 2.0) / (A + B)      # cosine of the new latitude
        lon = np.arctan2(y, x)
        R = r ** n
        return R * h2 * np.cos(n * lon), R * h2 * np.sin(n * lon), R * s2
    return P


# ---- angle profiles g(a) (a in radians, any real; all are continuous) -------------------------------------------
def g_sin(k):
    return lambda a: k * a - (k - 1) * np.sin(2 * k * a) / (2 * k)

def dg_sin(k):
    return lambda a: k - (k - 1) * np.cos(2 * k * a)

def g_lin(k):
    return lambda a: k * a

def g_flat(k):
    c = (k - 1) / 1.5
    return lambda a: k * a - c * (2 * np.sin(2 * k * a) / (2 * k) - 0.5 * np.sin(4 * k * a) / (4 * k))

def g_band(k, wdeg):
    """g(a) = a exactly within w of the flat plane, slope exactly 1 within w of every copy plane, C1 ramps between."""
    w = np.radians(wdeg); per = np.pi / k; L = per - 2 * w; Rz = np.pi - 2 * w
    def g(a):
        a = np.asarray(a, float)
        j = np.round(a / per)                    # nearest copy plane
        d = a - j * per                          # in [-per/2, per/2]
        sgn = np.sign(d); ad = np.abs(d)
        u = np.clip((ad - w) / L, 0.0, 0.5)      # half of the ramp belongs to this copy plane
        Sm = 3 * u * u - 2 * u ** 3
        up = np.where(ad <= w, ad, w + u * L + (Rz - L) * Sm)
        return j * np.pi + sgn * up
    return g

def g_lop2():
    """k = 2 WITHOUT the up/down mirror: once round above the flat plane (g = a), three half turns below."""
    def g(a):
        a = np.mod(np.asarray(a, float), 2 * np.pi)
        return np.where(a <= np.pi, a, np.pi + 3 * (a - np.pi))
    return g

def g_fold2():
    """Two planes with ONE fold a side, mirror-symmetric: 0..90 deg -> 0..180, 90..135 -> 180..270, 135..180 -> 270..180."""
    def g(a):
        a = np.asarray(a, float)
        b = np.mod(a + np.pi, 2 * np.pi) - np.pi            # (-pi, pi]
        ab = np.abs(b); h = np.pi / 2
        up = np.where(ab <= h, 2 * ab, np.where(ab <= 0.75 * np.pi, np.pi + 2 * (ab - h), 1.5 * np.pi - 2 * (ab - 0.75 * np.pi)))
        return np.sign(b) * up
    return g


def wind(g, P=S.oneplane):
    def F(x, y, z):
        x, y, z = (np.asarray(t, float) for t in (x, y, z))
        rho = np.hypot(y, z); a = np.arctan2(z, y); ga = g(a)
        return P(x, rho * np.cos(ga), rho * np.sin(ga))
    return F


def member(F, x, y, z, c, steps, r2=36.0):
    n = np.zeros(np.shape(x), np.int32); alive = np.ones(np.shape(x), bool)
    x, y, z = (np.array(t, float) for t in (x, y, z))
    for _ in range(steps):
        X, Y, Z = F(x, y, z)
        x = np.where(alive, X + c[0], x); y = np.where(alive, Y + c[1], y); z = np.where(alive, Z + c[2], z)
        alive &= (x * x + y * y + z * z) < r2
        n += alive
        if not alive.any():
            break
    return n


def flat_member(xr, yi, c, steps, r2=36.0):
    zc = xr + 1j * yi; cc = complex(c[0], c[1]); n = np.zeros(zc.shape, np.int32); alive = np.ones(zc.shape, bool)
    for _ in range(steps):
        zc = np.where(alive, zc * zc + cc, zc); alive &= (zc.real ** 2 + zc.imag ** 2) < r2; n += alive
    return n


def shade(n, steps):
    inside = n >= steps
    t = np.clip(n / steps, 0, 1) ** 0.6
    img = np.zeros(n.shape + (3,), np.uint8)
    img[..., 0] = (20 + 40 * t).astype(np.uint8); img[..., 1] = (26 + 70 * t).astype(np.uint8); img[..., 2] = (40 + 150 * t).astype(np.uint8)
    img[inside] = (236, 228, 200)
    return img


def rotx(deg, x, y, z):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a)
    return x, c * y - s * z, s * y + c * z
