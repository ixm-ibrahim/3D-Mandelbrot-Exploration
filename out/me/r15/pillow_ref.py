"""Reference for the 'square pillow with a belt' rule (my first cut, 2026-11-18).

Directions live on a square pillowcase: s in R/Z (round the pillow), t in [0, 1/2] (from the south seam to the
north seam), each seam zipped shut: (s, 0) ~ (-s, 0), (s, 1/2) ~ (-s, 1/2).
Direction map D: t <= 1/4: (s, t) -> (-2s, 2t);  t > 1/4: (s, t) -> (2s, 1 - 2t).   (double both, then mirror)
The belt t = 1/3 comes back to itself with s -> 2s: that belt is the equator, s = longitude / 360 degrees.
Rule: F(v) = |v|^2 * dir(D(pil(v / |v|))).

Layout (sphere <-> pillow), the same formula on both halves:
  north (z >= 0): p = (x, y) / (1 + z),  south: p = (x, y) / (1 - z),  |p| <= 1
  p = ((1 + B^2) / 2 * cos(nu), B * sin(nu)),  nu = 2 pi s,  B in [0, 1]  (B = 1 the equator, B = 0 the seam)
  north: B = sinh(bn * (1/2 - t)) / sinh(bn / 6),  south: B = sinh(bs * t) / sinh(bs / 3)
  with bn, bs chosen so that dB/dt = 2 pi at the equator (angle-true there).
"""
import numpy as np
from scipy.optimize import brentq

LN = brentq(lambda l: l / np.tanh(l) - np.pi / 3, 1e-3, 3)        # bn / 6
LS = brentq(lambda l: l / np.tanh(l) - 2 * np.pi / 3, 1e-3, 5)    # bs / 3
BN, BS = 6 * LN, 3 * LS

def solve_beta(px, py):
    """beta = B^2 in [0, 1] with 4 px^2 / (1 + beta)^2 + py^2 / beta = 1 (bisection, vectorised)."""
    lo, hi = np.zeros_like(px), np.ones_like(px)
    for _ in range(60):
        m = 0.5 * (lo + hi)
        g = m * (1 + m) ** 2 - 4 * px * px * m - py * py * (1 + m) ** 2    # < 0 below the root
        lo = np.where(g < 0, m, lo); hi = np.where(g < 0, hi, m)
    return 0.5 * (lo + hi)

def pil(d):
    """unit directions (N, 3) -> (s, t)."""
    x, y, z = d[:, 0], d[:, 1], d[:, 2]
    north = z >= 0
    den = 1 + np.abs(z)
    px, py = x / den, y / den
    beta = solve_beta(px, py)
    B = np.sqrt(beta)
    A = 0.5 * (1 + beta)
    nu = np.arctan2(np.where(B > 1e-300, py / np.maximum(B, 1e-300), 0.0), px / A)
    # on the seam itself (B = 0) sin(nu) is not fixed by py; take nu = acos(2 px) there
    seam = B < 1e-9
    nu = np.where(seam, np.arccos(np.clip(2 * px, -1, 1)), nu)
    s = (nu / (2 * np.pi)) % 1.0
    t = np.where(north, 0.5 - np.arcsinh(B * np.sinh(LN)) / BN, np.arcsinh(B * np.sinh(LS)) / BS)
    return s, t

def dirn(s, t):
    """(s, t) -> unit directions (N, 3); t in [0, 1/2]."""
    north = t >= 1 / 3
    B = np.where(north, np.sinh(BN * (0.5 - t)) / np.sinh(LN), np.sinh(BS * t) / np.sinh(LS))
    B = np.clip(B, 0, 1)
    nu = 2 * np.pi * s
    px, py = 0.5 * (1 + B * B) * np.cos(nu), B * np.sin(nu)
    r2 = px * px + py * py
    zz = (1 - r2) / (1 + r2)
    k = 2 / (1 + r2)
    return np.stack([k * px, k * py, np.where(north, zz, -zz)], 1)

def D(s, t):
    low = t <= 0.25
    return np.where(low, (-2 * s) % 1.0, (2 * s) % 1.0), np.where(low, 2 * t, 1 - 2 * t)

def F(v):
    r = np.linalg.norm(v, axis=1)
    ok = r > 0
    d = v / np.where(ok, r, 1)[:, None]
    s, t = pil(d)
    s2, t2 = D(s, t)
    out = dirn(s2, t2) * (r * r)[:, None]
    flat = v[:, 2] == 0                      # the flat plane: exact complex square, z stays exactly 0
    out[flat] = np.stack([v[flat, 0] ** 2 - v[flat, 1] ** 2, 2 * v[flat, 0] * v[flat, 1], 0 * v[flat, 0]], 1)
    out[~ok] = 0
    return out

if __name__ == '__main__':
    rng = np.random.default_rng(1)
    d = rng.normal(size=(200000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    s, t = pil(d)
    back = dirn(s, t)
    print('LN, LS, bn, bs', LN, LS, BN, BS)
    print('round trip sphere -> pillow -> sphere, worst', np.abs(back - d).max())
    # the plane without the special case: equator points through the general formula
    th = rng.uniform(0, 2 * np.pi, 20000); e = np.stack([np.cos(th), np.sin(th), 0 * th], 1)
    s, t = pil(e); s2, t2 = D(s, t); g = dirn(s2, t2)
    want = np.stack([np.cos(2 * th), np.sin(2 * th), 0 * th], 1)
    print('equator through the general formula against angle doubling, worst', np.abs(g - want).max(), ' t on the equator', t.min(), t.max())
    # continuity: close pairs of directions must land close (largest stretch), 400,000 pairs
    a = rng.normal(size=(400000, 3)); a /= np.linalg.norm(a, axis=1)[:, None]
    for h in (1e-4, 1e-5):
        b = a + h * rng.normal(size=a.shape); b /= np.linalg.norm(b, axis=1)[:, None]
        fa, fb = F(a), F(b)
        st = np.linalg.norm(fa - fb, axis=1) / np.linalg.norm(a - b, axis=1)
        print('step', h, ': stretch median %.3f, 1%% %.3f, 99%% %.3f, largest %.1f, largest jump %.2e' % (np.median(st), np.quantile(st, .01), np.quantile(st, .99), st.max(), np.linalg.norm(fa - fb, axis=1).max()))
    # near the plane: sideways stretch against in-plane stretch (should both be 2 for unit vectors)
    th = rng.uniform(0, 2 * np.pi, 20000); e = np.stack([np.cos(th), np.sin(th), 0 * th], 1)
    up = e.copy(); up[:, 2] = 1e-5; up /= np.linalg.norm(up, axis=1)[:, None]
    dn = e.copy(); dn[:, 2] = -1e-5; dn /= np.linalg.norm(dn, axis=1)[:, None]
    fu, fd, f0 = F(up), F(dn), F(e)
    print('sideways stretch just above the plane: %.4f to %.4f, below: %.4f to %.4f; image z sign above %s below %s' % (
        (np.linalg.norm(fu - f0, axis=1) / 1e-5).min(), (np.linalg.norm(fu - f0, axis=1) / 1e-5).max(),
        (np.linalg.norm(fd - f0, axis=1) / 1e-5).min(), (np.linalg.norm(fd - f0, axis=1) / 1e-5).max(), np.sign(fu[:, 2]).mean(), np.sign(fd[:, 2]).mean()))
