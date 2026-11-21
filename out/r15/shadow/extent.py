"""Round 15B, shadow: how large are the Mandelbrot solids of the powers 2 to 5? A coarse numpy grid (14 steps, escape
radius 64 in the plain length, as the page), with the rule as in MATH.pillow4d (gauge by gauge_proto2.gauge_fp)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gauge_proto2 as G


def F(P, n):
    c0, s0 = G.consts(n)
    r = np.linalg.norm(P, axis=1); ok = r > 1e-20
    d = P / np.where(ok, r, 1)[:, None]
    g = G.gauge_fp(d, n, 5)
    u1 = np.clip(d[:, 0] / g, -1, 1); u2 = np.clip(c0 - s0 * d[:, 2] / g, -1, 1); wr = d[:, 1] * (s0 * g + c0 * d[:, 2]) / (g * g)
    t0, t1, p0, p1 = np.ones_like(u1), u1, np.zeros_like(u1), np.ones_like(u1)
    a0, a1, b0, b1 = np.ones_like(u2), u2, np.zeros_like(u2), np.ones_like(u2)
    for _ in range(n - 1):
        t0, t1 = t1, 2 * u1 * t1 - t0; p0, p1 = p1, 2 * u1 * p1 - p0
        a0, a1 = a1, 2 * u2 * a1 - a0; b0, b1 = b1, 2 * u2 * b1 - b0
    R = np.minimum(r * g, 1e30) ** n
    out = np.stack([R * t1, -R * s0 * wr * p1 * b1 / (1 - c0 * a1), R * (c0 - a1) / s0], 1)
    out[~ok] = 0
    return out


def inside(P, n, c=None, its=14):
    z = np.zeros_like(P) if c is None else P.copy()
    k = P if c is None else np.asarray(c, float)[None, :]
    alive = np.ones(len(P), bool)
    for i in range(its + 1):
        alive &= np.linalg.norm(z, axis=1) <= 64
        if i == its: break
        z = np.where(alive[:, None], F(z, n) + k, z)
    return alive


if __name__ == '__main__':
    N = 90
    for n in (2, 3, 4, 5):
        L = 4.0 if n == 2 else 2.5
        ax = (np.arange(N) + 0.5) / N * 2 * L - L
        X, Y, Z = np.meshgrid(ax, ax, ax, indexing='ij')
        P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
        m = inside(P, n)
        Q = P[m]
        up = Q[:, 2] > 0
        print('power %d: grid %d^3 over +-%.1f, cell %.3f: %d cells in the solid; x %.2f to %.2f, y %.2f to %.2f, z %.2f to %.2f; share of the volume above the plane %.2f; touches the box wall: %s' % (
            n, N, L, 2 * L / N, m.sum(), Q[:, 0].min(), Q[:, 0].max(), Q[:, 1].min(), Q[:, 1].max(), Q[:, 2].min(), Q[:, 2].max(), up.mean(), bool((np.abs(Q).max() > L - 2 * L / N))))
