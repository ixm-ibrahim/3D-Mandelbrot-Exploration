"""Checker "arithmetic": my own reference for the flat game, written in Python from the definition in section 1 of
docs/ROUND26.md. Nothing here is read from the page.

  The big circle: every point no further than 2 from the centre.
  Julia shape:      z0 = p, c fixed.        Mandelbrot shape:  c = p, z0 = 0.
  A step:           the modifiers first (|x|, |y|, then flip y), then z -> z^n + c with z = x + iy.
  out(p) = the smallest k >= 0 with |z_k| > 2 (for the Mandelbrot shape k = 0 means |p| > 2);  maxK + 1 = still in.

The power: a whole power by multiplying complex numbers (a negative whole power: one over that); any other power in
polar form with the principal angle, r^n at the angle n * atan2(y, x).
"""
import numpy as np


def cpow(x, y, n):
    """(x + iy)^n for arrays x, y."""
    if float(n) == int(n) and int(n) != 0:
        m = abs(int(n))
        a, b = x.copy(), y.copy()
        for _ in range(m - 1):
            a, b = a * x - b * y, a * y + b * x
        if n > 0:
            return a, b
        d = a * a + b * b
        return a / d, -b / d
    r = np.hypot(x, y)
    th = np.arctan2(y, x) * n
    R = np.where((r == 0) & (n > 0), 0.0, np.power(r, n))
    return R * np.cos(th), R * np.sin(th)


def out_points(px, py, kind, c, n, absx=False, absy=False, flipy=False, maxK=16):
    """The step at which each point (px, py) is thrown out; maxK + 1 when it is still in after maxK steps."""
    px = np.asarray(px, dtype=np.float64); py = np.asarray(py, dtype=np.float64)
    with np.errstate(all="ignore"):
        inside = (px * px + py * py <= 4.0)
        res = np.where(inside, maxK + 1, 0).astype(np.int32)
        alive = inside.copy()
        if kind == "j":
            x, y = px.copy(), py.copy()
            cx, cy = float(c[0]), float(c[1])
        else:
            x, y = np.zeros_like(px), np.zeros_like(py)
            cx, cy = px, py
        for k in range(1, maxK + 1):
            xm = np.abs(x) if absx else x
            ym = np.abs(y) if absy else y
            if flipy:
                ym = -ym
            a, b = cpow(xm, ym, n)
            x, y = a + cx, b + cy
            gone = alive & ~(x * x + y * y <= 4.0)
            res[gone] = k
            alive &= ~gone
    return res


def grid(size, half):
    """The points of mask2 / slice: size to a side, the outer ones ON the edge of the square, row 0 at y = +half."""
    d = 2.0 * half / (size - 1)
    i = np.arange(size, dtype=np.float64)
    xs = -half + i * d
    ys = half - i * d
    return np.meshgrid(xs, ys)        # px[row, col], py[row, col]


def mask(kind, c, n, size, half, maxK=16, absx=False, absy=False, flipy=False):
    px, py = grid(size, half)
    return np.minimum(out_points(px, py, kind, c, n, absx, absy, flipy, maxK), 255).astype(np.uint8)


def explained(px, py, got, kind, c, n, absx, absy, flipy, maxK, eps=(1e-9, 1e-7)):
    """For points where the page's number `got` differs from the reference: is there a point within eps where the
    reference gives the page's number (a point within a hair of a skin, or on the cut of a power that is not whole)?"""
    px = np.asarray(px, dtype=np.float64); py = np.asarray(py, dtype=np.float64); got = np.asarray(got)
    ok = np.zeros(px.shape, dtype=bool)
    for e in eps:
        for dx in (-e, 0.0, e):
            for dy in (-e, 0.0, e):
                if dx == 0.0 and dy == 0.0:
                    continue
                ok |= (out_points(px + dx, py + dy, kind, c, n, absx, absy, flipy, maxK) == got)
    return ok
