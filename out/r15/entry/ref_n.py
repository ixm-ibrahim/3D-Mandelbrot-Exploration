"""Round 15, entry: the reference rule for a whole power n >= 2, written from the brief (docs/ROUND15.md) and
kept apart from the page's code: bisection for beta and for b, angles by arctan2. At n = 2 it must agree with
out/me/r15/pillow_ref.py (run this file to see).

D for the power n: (s, t) -> (-n s, n t); with u = n t mod 1: u <= 1/2 -> (-n s, u), else (n s, 1 - u).
Belt t0 = 1/(n + 1). North strip [t0, 1/2], south strip [0, t0]; B = sinh(b * distance from the seam)/sinh(b * width),
b coth(b * width) = 2 pi.
"""
import sys, os
import numpy as np
from scipy.optimize import brentq


def lay(n):
    t0 = 1.0 / (n + 1)
    wn, ws = 0.5 - t0, t0
    f = lambda w: brentq(lambda x: x / np.tanh(x) - 2 * np.pi * w, 1e-6, 40) / w
    return t0, wn, ws, f(wn), f(ws)


def solve_beta(px, py):
    lo, hi = np.zeros_like(px), np.ones_like(px)
    for _ in range(60):
        m = 0.5 * (lo + hi)
        g = m * (1 + m) ** 2 - 4 * px * px * m - py * py * (1 + m) ** 2
        lo = np.where(g < 0, m, lo); hi = np.where(g < 0, hi, m)
    return 0.5 * (lo + hi)


def pil(d, n):
    t0, wn, ws, bn, bs = lay(n)
    x, y, z = d[:, 0], d[:, 1], d[:, 2]
    north = z >= 0
    den = 1 + np.abs(z)
    px, py = x / den, y / den
    beta = solve_beta(px, py)
    B = np.sqrt(beta); A = 0.5 * (1 + beta)
    nu = np.arctan2(np.where(B > 1e-300, py / np.maximum(B, 1e-300), 0.0), px / A)
    nu = np.where(B < 1e-9, np.arccos(np.clip(2 * px, -1, 1)), nu)
    s = (nu / (2 * np.pi)) % 1.0
    t = np.where(north, 0.5 - np.arcsinh(B * np.sinh(bn * wn)) / bn, np.arcsinh(B * np.sinh(bs * ws)) / bs)
    return s, t


def dirn(s, t, n):
    t0, wn, ws, bn, bs = lay(n)
    north = t >= t0
    B = np.where(north, np.sinh(bn * (0.5 - t)) / np.sinh(bn * wn), np.sinh(bs * t) / np.sinh(bs * ws))
    B = np.clip(B, 0, 1)
    nu = 2 * np.pi * s
    px, py = 0.5 * (1 + B * B) * np.cos(nu), B * np.sin(nu)
    r2 = px * px + py * py
    zz = (1 - r2) / (1 + r2)
    k = 2 / (1 + r2)
    return np.stack([k * px, k * py, np.where(north, zz, -zz)], 1)


def D(s, t, n):
    u = (n * t) % 1.0
    low = u <= 0.5
    return np.where(low, (-n * s) % 1.0, (n * s) % 1.0), np.where(low, u, 1 - u)


def F(v, n=2):
    r = np.linalg.norm(v, axis=1)
    ok = r > 0
    d = v / np.where(ok, r, 1)[:, None]
    s, t = pil(d, n)
    s2, t2 = D(s, t, n)
    out = dirn(s2, t2, n) * (r ** n)[:, None]
    flat = v[:, 2] == 0
    zc = (v[flat, 0] + 1j * v[flat, 1]) ** n
    out[flat] = np.stack([zc.real, zc.imag, 0 * zc.real], 1)
    out[~ok] = 0
    return out


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'me', 'r15'))
    import pillow_ref as R0
    rng = np.random.default_rng(3)
    v = rng.normal(size=(200000, 3))
    print('n = 2 against pillow_ref.py, 200,000 points, worst', np.abs(F(v, 2) - R0.F(v)).max())
    for n in (2, 3, 4, 5):
        t0, wn, ws, bn, bs = lay(n)
        d = v / np.linalg.norm(v, axis=1)[:, None]
        s, t = pil(d, n)
        back = dirn(s, t, n)
        th = rng.uniform(0, 2 * np.pi, 20000); e = np.stack([np.cos(th), np.sin(th), 0 * th], 1)
        s, t = pil(e, n); s2, t2 = D(s, t, n); g = dirn(s2, t2, n)
        want = np.stack([np.cos(n * th), np.sin(n * th), 0 * th], 1)
        a = d[:100000]
        res = []
        for h in (1e-4, 1e-5):
            b = a + h * rng.normal(size=a.shape); b /= np.linalg.norm(b, axis=1)[:, None]
            fa, fb = F(a, n), F(b, n)
            st = np.linalg.norm(fa - fb, axis=1) / np.linalg.norm(a - b, axis=1)
            res.append('step %g: stretch median %.3f, 1%% %.3f, 99%% %.3f, largest %.1f, largest jump %.2e' % (h, np.median(st), np.quantile(st, .01), np.quantile(st, .99), st.max(), np.linalg.norm(fa - fb, axis=1).max()))
        print('n = %d: belt %.4f, bn %.6f, bs %.6f; round trip worst %.2e; equator against angle times n worst %.2e; %s' % (n, t0, bn, bs, np.abs(back - d).max(), np.abs(g - want).max(), '; '.join(res)))
