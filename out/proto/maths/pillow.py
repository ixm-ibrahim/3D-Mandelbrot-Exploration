"""Referee's from-scratch implementation of the triangular 'pillow' rule.
F_n(v) = |v|^n * Phi(n * PhiInv(v/|v|)),  simplest (radial) layout.
All functions are vectorised over numpy arrays."""
import numpy as np

S3 = np.sqrt(3.0)
TP3 = 2.0 * np.pi / 3.0


# ---------- layout: weights (lA,lB,lC) <-> direction with z >= 0 ----------
def layout_fwd(lA, lB, lC):
    m = np.minimum(np.minimum(lA, lB), lC)
    s = np.clip(1.0 - 3.0 * m, 0.0, 1.0)          # 0 centre, 1 boundary
    ss = np.where(s > 1e-300, s, 1.0)
    a = 1.0 / 3 + (lA - 1.0 / 3) / ss
    b = 1.0 / 3 + (lB - 1.0 / 3) / ss
    c = 1.0 / 3 + (lC - 1.0 / 3) / ss
    # which weight is the minimum decides the edge the ray hits
    phi = np.where((lC <= lA) & (lC <= lB), TP3 * b,            # edge AB
          np.where((lA <= lB) & (lA <= lC), TP3 * (1.0 + c),    # edge BC
                   TP3 * (2.0 + a)))                            # edge CA
    th = 0.5 * np.pi * s
    st = np.sin(th)
    return st * np.cos(phi), st * np.sin(phi), np.cos(th)


def layout_inv(x, y, z):
    """z >= 0 assumed. returns weights."""
    th = np.arctan2(np.hypot(x, y), z)
    s = th / (0.5 * np.pi)
    phi = np.mod(np.arctan2(y, x), 2.0 * np.pi)
    q = phi / TP3
    k = np.clip(np.floor(q), 0, 2)
    t = q - k
    a = np.where(k == 0, 1.0 - t, np.where(k == 1, 0.0, t))
    b = np.where(k == 0, t, np.where(k == 1, 1.0 - t, 0.0))
    c = np.where(k == 0, 0.0, np.where(k == 1, t, 1.0 - t))
    lA = 1.0 / 3 + s * (a - 1.0 / 3)
    lB = 1.0 / 3 + s * (b - 1.0 / 3)
    lC = 1.0 / 3 + s * (c - 1.0 / 3)
    return lA, lB, lC


# ---------- Phi : plane -> sphere ----------
def Phi(ux, uy):
    b = uy * (2.0 / S3)
    a = ux + 0.5 * b
    i = np.floor(a)
    j = np.floor(b)
    fa = a - i
    fb = b - j
    up = fa >= fb                       # points up -> bottom face (z<=0)
    c0 = np.mod(i + j, 3.0)
    w0 = np.where(up, 1.0 - fa, 1.0 - fb)      # weight at colour c0
    w1 = np.where(up, fa - fb, fb - fa)        # weight at colour c0+1
    w2 = np.where(up, fb, fa)                  # weight at colour c0+2
    lA = np.where(c0 == 0, w0, np.where(c0 == 1, w2, w1))
    lB = np.where(c0 == 0, w1, np.where(c0 == 1, w0, w2))
    lC = np.where(c0 == 0, w2, np.where(c0 == 1, w1, w0))
    x, y, z = layout_fwd(lA, lB, lC)
    return x, y, np.where(up, -z, z)


def PhiInv(x, y, z):
    lA, lB, lC = layout_inv(x, y, np.abs(z))
    sgn = np.where(z >= 0, -1.0, 1.0)
    return lB + 0.5 * lC, sgn * (S3 / 2) * lC


def dirmap(x, y, z, n):
    """direction map of F_n (inputs must be unit vectors)."""
    ux, uy = PhiInv(x, y, z)
    return Phi(n * ux, n * uy)


def F(x, y, z, n):
    r = np.sqrt(x * x + y * y + z * z)
    rs = np.where(r > 0, r, 1.0)
    dx, dy, dz = dirmap(x / rs, y / rs, z / rs, n)
    rn = r ** n
    return rn * dx, rn * dy, rn * dz


# ---------- comparison: plain Riemann-sphere rule (poles on z axis) ----------
def riemann_dir(x, y, z, n=2):
    lon = np.arctan2(y, x)
    sz = np.clip(z, -1 + 1e-16, 1 - 1e-16)
    t = np.tanh(n * np.arctanh(sz))
    c = np.sqrt(np.maximum(0.0, 1.0 - t * t))
    return c * np.cos(n * lon), c * np.sin(n * lon), t


def rand_dirs(N, rng):
    v = rng.normal(size=(3, N))
    v /= np.linalg.norm(v, axis=0)
    return v[0], v[1], v[2]
