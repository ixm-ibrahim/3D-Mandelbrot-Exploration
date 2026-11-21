"""Reference for the pillow rule in closed form ("the 4D shadow"), whole powers n >= 2. Mine, 2026-11-18.

In 4D, as two complex numbers (z1, z2) of the SAME length rho:  z1 = rho e^{i a},  z2 = rho e^{i b}.
Rule in 4D:  (z1, z2) -> (conj(z1)^n, z2^n)          (turn both circles n times as far, one of them backwards)
A 3D point stands for the pair (z1, z2) together with its mirror pair (conj z1, conj z2). Three numbers survive
that folding:  x1 = Re z1,  x2 = Re z2,  w = Im z1 * Im z2 / rho,   with  w^2 rho^2 = (rho^2 - x1^2)(rho^2 - x2^2).
In those numbers the rule is polynomial (Chebyshev T and U):
    x1' = rho^n T_n(x1/rho),  x2' = rho^n T_n(x2/rho),  w' = -rho^(n-1) w U_{n-1}(x1/rho) U_{n-1}(x2/rho),  rho' = rho^n
The belt b0 = 2 pi / (n + 1) (x2 = c0 rho, c0 = cos b0) comes back to itself with a -> n a. Lab coordinates put
that belt on the plane Z = 0, angle-true there:
    X = x1,   Y = s0 rho w / (rho - c0 x2),   Z = -(x2 - c0 rho) / s0          (s0 = sin b0)
Going back needs rho: the root of  Y^2 (rho - c0 x2)^2 / s0^2 = (rho^2 - X^2)(rho^2 - x2^2),  x2 = c0 rho - s0 Z.
"""
import numpy as np

def cheb(n, u):
    """T_n(u), U_{n-1}(u) for |u| <= 1 by the recurrence (polynomials, no angles)."""
    t0, t1 = np.ones_like(u), u
    u0, u1 = np.zeros_like(u), np.ones_like(u)      # U_{-1} = 0, U_0 = 1
    for _ in range(n - 1):
        t0, t1 = t1, 2 * u * t1 - t0
        u0, u1 = u1, 2 * u * u1 - u0
    return t1, u1                                    # T_n, U_{n-1}

def consts(n):
    b0 = 2 * np.pi / (n + 1)
    return np.cos(b0), np.sin(b0)

def gauge(X, Y, Z, n):
    """rho for lab points (vectorised bisection on the one root above the lower bound)."""
    c0, s0 = consts(n)
    def G(r):
        x2 = c0 * r - s0 * Z
        return (r * r - X * X) * (r * r - x2 * x2) - (Y * (r - c0 * x2) / s0) ** 2
    # x2 must lie in [-rho, rho]:  rho (1 - c0) >= -s0 Z  and  rho (1 + c0) >= s0 Z
    lo = np.maximum.reduce([np.abs(X), -s0 * Z / (1 - c0), s0 * Z / (1 + c0), np.zeros_like(X)])
    hi = 4 * (np.abs(X) + np.abs(Y) + np.abs(Z)) / min(1 - abs(c0), s0) + 1e-300
    for _ in range(70):
        m = 0.5 * (lo + hi)
        g = G(m) < 0
        lo = np.where(g, m, lo); hi = np.where(g, hi, m)
    return 0.5 * (lo + hi)

def to_shadow(P, n):
    c0, s0 = consts(n)
    X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
    rho = gauge(X, Y, Z, n)
    x2 = c0 * rho - s0 * Z
    w = np.where(rho > 0, Y * (rho - c0 * x2) / (s0 * np.where(rho > 0, rho, 1)), 0.0)
    return X, x2, w, rho

def from_shadow(x1, x2, w, rho, n):
    c0, s0 = consts(n)
    den = rho - c0 * x2
    Y = np.where(den > 0, s0 * rho * w / np.where(den > 0, den, 1), 0.0)
    return np.stack([x1, Y, -(x2 - c0 * rho) / s0], 1)

def F(P, n=2):
    x1, x2, w, rho = to_shadow(P, n)
    ok = rho > 0
    r = np.where(ok, rho, 1)
    Tn1, Un1 = cheb(n, np.clip(x1 / r, -1, 1))
    Tn2, Un2 = cheb(n, np.clip(x2 / r, -1, 1))
    rn = r ** n
    out = from_shadow(rn * Tn1, rn * Tn2, -rn / r * w * Un1 * Un2, rn, n)
    flat = P[:, 2] == 0                      # the flat plane: exact complex power, Z stays exactly 0
    if flat.any():
        zc = (P[flat, 0] + 1j * P[flat, 1]) ** n
        out[flat] = np.stack([zc.real, zc.imag, 0 * zc.real], 1)
    out[~ok] = 0
    return out

if __name__ == '__main__':
    rng = np.random.default_rng(3)
    for n in (2, 3, 4, 5):
        c0, s0 = consts(n)
        # 1. the rule against plain angles on the two circles
        a = rng.uniform(0, 2 * np.pi, 100000); b = rng.uniform(0, np.pi, 100000); rho = rng.uniform(0.2, 1.8, 100000)
        P = from_shadow(rho * np.cos(a), rho * np.cos(b), rho * np.sin(a) * np.sin(b), rho, n)
        x1, x2, w, r = to_shadow(P, n)
        back = np.abs(np.stack([x1 - rho * np.cos(a), x2 - rho * np.cos(b), w - rho * np.sin(a) * np.sin(b), r - rho], 1)).max()
        a2, b2, r2 = -n * a, n * b, rho ** n
        want = from_shadow(r2 * np.cos(a2), r2 * np.cos(b2), r2 * np.sin(a2) * np.sin(b2), r2, n)
        got = F(P, n)
        e1 = (np.linalg.norm(got - want, axis=1) / r2).max()
        # 2. the plane through the general formulas (no special case): tiny Z replaced by the belt itself
        th = rng.uniform(0, 2 * np.pi, 20000); rr = rng.uniform(0.2, 1.8, 20000)
        Q = np.stack([rr * np.cos(th), rr * np.sin(th), 0 * th], 1)
        x1, x2, w, r = to_shadow(Q, n)
        Tn1, Un1 = cheb(n, np.clip(x1 / r, -1, 1)); Tn2, Un2 = cheb(n, np.clip(x2 / r, -1, 1))
        g = from_shadow(r ** n * Tn1, r ** n * Tn2, -r ** (n - 1) * w * Un1 * Un2, r ** n, n)
        zc = (Q[:, 0] + 1j * Q[:, 1]) ** n
        e2 = (np.abs(np.stack([g[:, 0] - zc.real, g[:, 1] - zc.imag, g[:, 2]], 1)).max(axis=1) / rr ** n).max()
        # 3. no jump: close pairs
        A = rng.normal(size=(300000, 3)); A /= np.linalg.norm(A, axis=1)[:, None]
        jumps = []
        for h in (1e-4, 1e-5):
            B = A + h * rng.normal(size=A.shape)
            jumps.append(np.linalg.norm(F(A, n) - F(B, n), axis=1).max())
        # 4. sideways stretch next to the plane (unit circle): should be n, with the side flipped
        E = np.stack([np.cos(th), np.sin(th), 0 * th], 1); U = E.copy(); U[:, 2] = 1e-6
        d = F(U, n) - F(E, n)
        side = np.linalg.norm(d, axis=1) / 1e-6
        # 5. how far the gauge is from the plain length
        r1 = gauge(A[:, 0], A[:, 1], A[:, 2], n)
        print('n = %d: back to the two angles %.1e | rule against angles %.1e | plane against z^n %.1e | largest jump at step 1e-4, 1e-5: %.1e, %.1e | sideways stretch at the plane %.4f to %.4f (want %d), image side %+.0f | rho on the unit sphere %.3f to %.3f'
              % (n, back, e1, e2, jumps[0], jumps[1], side.min(), side.max(), n, np.sign(d[:, 2]).mean(), r1.min(), r1.max()))
