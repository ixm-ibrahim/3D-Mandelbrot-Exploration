"""Round 27, judge: my own tools. Written from the recipe text in docs/ROUND27.md section 1, not from tree.py.

    balls(x, y, z, t, grid, k2, rounds, slide)   verdict of the balls object at picture points: 1 inside, -1 outside, 0 undecided
    truth(x, y, c, steps)                        the true flat picture (orbit of z^2 + c never leaves)
    wrong_share(A, T)                            area(A xor T) / area(T)
    render(inside_fn, w, h, nd, cam, ...)        first inside block on each line of sight, skin refined by halving
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

S3 = np.sqrt(3.0)
RABBIT = complex(-0.12256116687665362, 0.7448617666197442)
BOX = (-1.8, 1.8, -1.3, 1.3)
EYES = {'front': (0.45, 0.5, 1.0), 'above': (0.2, 1.0, 0.35)}


def slide_grid(grid, mx, my):
    """(mx, my) minus the nearest whole number of the grid."""
    if grid == 'line':
        return mx - np.round(mx), my
    if grid == 'square':
        return mx - np.round(mx), my - np.round(my)
    if grid == 'square2':                                   # every second point of the square grid (a + b even)
        u = (mx + my) / 2; v = (mx - my) / 2; u = u - np.round(u); v = v - np.round(v)
        return u + v, u - v
    if grid == 'line2':
        return mx - 2 * np.round(mx / 2), my
    # hex: whole numbers a + b w, w = (1/2, sqrt3/2). The nearest one is a corner of the cell the point lies in.
    b = my / (S3 / 2); a = mx - b / 2; a0 = np.floor(a); b0 = np.floor(b)
    bx = mx.copy(); by = my.copy(); bd = np.full(np.shape(mx), np.inf)
    for da in (0, 1):
        for db in (0, 1):
            px = mx - (a0 + da) - (b0 + db) / 2; py = my - (b0 + db) * S3 / 2; d = px * px + py * py
            m = d < bd; bx = np.where(m, px, bx); by = np.where(m, py, by); bd = np.where(m, d, bd)
    return bx, by


def to_m(x, y, z, k2):
    """Picture point -> the object's own coordinates: one sphere inversion, centre (0, 0, 1), radius k.
    Picture x runs along the chain (the object's third axis), y up in the flat plane, z out of it."""
    ux, uy, uz = y, z, x - k2 / 2
    d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    return k2 * ux / d, k2 * uy / d, 1.0 + k2 * uz / d


def balls(x, y, z, t=1.40, grid='square', k2=1.05, rounds=14, slide=(0.0, 0.0), raw=False):
    """The recipe. Returns int8: 1 inside, -1 outside, 0 not decided after `rounds` rounds.
    slide: the upper unit sphere (and its whole numbers) moved sideways by this much."""
    sh = np.shape(x)
    mx, my, mz = (np.array(v, float).ravel() for v in (to_m(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), k2) if not raw else (x, y, z)))
    top = 2 * t; v = np.zeros(mx.size, np.int8); idx = np.arange(mx.size)
    for _ in range(rounds):
        ins = (mz < 0) | (mz > top)
        v[idx[ins]] = 1
        keep = ~ins; idx, mx, my, mz = idx[keep], mx[keep], my[keep], mz[keep]
        if idx.size == 0:
            break
        ax, ay = slide_grid(grid, mx, my)                                   # as seen from the floor
        bx, by = slide_grid(grid, mx - slide[0], my - slide[1])             # as seen from the (slid) ceiling
        r0 = ax * ax + ay * ay + mz * mz; r1 = bx * bx + by * by + (mz - top) ** 2
        lo = r0 < 1; hi = (r1 < 1) & ~lo; out = ~lo & ~hi
        v[idx[out]] = -1
        s0 = 1 / np.where(r0 > 0, r0, 1.0); s1 = 1 / np.where(r1 > 0, r1, 1.0)
        nx = np.where(lo, ax * s0, bx * s1 + slide[0]); ny = np.where(lo, ay * s0, by * s1 + slide[1])
        nz = np.where(lo, mz * s0, top + (mz - top) * s1)
        keep = ~out; idx, mx, my, mz = idx[keep], nx[keep], ny[keep], nz[keep]
        if idx.size == 0:
            break
    return v.reshape(sh)


def truth(x, y, c, steps=300):
    """The true flat picture: the orbit of z^2 + c has not left after `steps` steps."""
    c = complex(c); z = np.asarray(x, float) + 1j * np.asarray(y, float); sh = z.shape; z = z.ravel().copy()
    ins = np.ones(z.size, bool); idx = np.arange(z.size)
    for _ in range(steps):
        z = z * z + c; k = (z.real * z.real + z.imag * z.imag) < 36.0
        ins[idx[~k]] = False; idx = idx[k]; z = z[k]
        if idx.size == 0:
            break
    return ins.reshape(sh)


def grid_xy(w=900, h=650, box=BOX):
    return np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h))


def wrong_share(A, T):
    return float((A != T).sum()) / float(T.sum())


def overlay(A, T):
    """Both: cream. Only the true flat picture: blue. Only the object: orange."""
    img = np.zeros(A.shape + (3,), np.uint8); img[...] = (16, 19, 30)
    img[T & ~A] = (70, 130, 235); img[A & ~T] = (236, 140, 44); img[A & T] = (232, 224, 200)
    return img


def render(inside_fn, w, h, nd, cam, centre=(0.0, 0.0, 0.0), half_w=1.75, depth_half=None, refine=7, slab=6, log=None):
    """First inside block on each line of sight (front to back; a pixel stops at its first hit), then the skin is
    placed between the last outside block and the first inside one by halving. inside_fn(x, y, z) -> bool array."""
    e1, e2, e3 = M.frame(cam); centre = np.asarray(centre, float); dh = depth_half or half_w
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-dh, dh, nd)
    U, V = np.meshgrid(us, vs); U = U.ravel(); V = V.ravel(); dd = ds[1] - ds[0]
    depth = np.full(U.size, np.inf); live = np.arange(U.size); t0 = time.time()

    def pts(ii, d):
        return [centre[k] + U[ii] * e1[k] + V[ii] * e2[k] + d * e3[k] for k in range(3)]
    for k0 in range(0, nd, slab):
        dk = ds[k0:k0 + slab]
        if live.size == 0:
            break
        P = [centre[k] + U[live][None] * e1[k] + V[live][None] * e2[k] + dk[:, None] * e3[k] for k in range(3)]
        ins = inside_fn(P[0], P[1], P[2])
        hit = ins.any(0)
        depth[live[hit]] = dk[np.argmax(ins, 0)[hit]]
        live = live[~hit]
        if log and (k0 // slab) % 10 == 0:
            print('   %s: depth %d of %d, %d lines still open, %.0f s' % (log, k0, nd, live.size, time.time() - t0)); sys.stdout.flush()
    hit = np.flatnonzero(np.isfinite(depth))
    if refine and hit.size:
        hi = depth[hit].copy(); lo = hi - dd
        for _ in range(refine):
            mid = 0.5 * (lo + hi); P = pts(hit, mid); ins = inside_fn(P[0], P[1], P[2])
            hi = np.where(ins, mid, hi); lo = np.where(ins, lo, mid)
        depth[hit] = hi
    return depth.reshape(h, w), us[1] - us[0]


def shade(depth, px):
    return M.shade_solid(depth, px)


def font(sz):
    return M.font(sz)
