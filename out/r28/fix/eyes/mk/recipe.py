"""The eyes' own writing of the recipe of docs/ROUND28.md section 1.1, in numpy (float64). Nothing here is taken
from the builder's code: the frame is the one sphere inversion about (0, 0, 1) with k^2 = 1.05 that the round's
brief names, picture x along the chain, picture y up in the flat plane, picture z out of it.

verdict(P, top, rho, grid, rounds) -> for every picture point: 1 = a wall was reached (inside a ball),
                                      0 = OUTSIDE, 2 = still undecided when the rounds ran out.
The page counts 2 as inside ("solid at the page's depth" = verdict != 0 with rounds = the page's depth).
"""
import numpy as np

K2 = 1.05
S3H = np.sqrt(3.0) / 2.0


def slide(mx, my, grid):
    """the nearest whole number of the grid: 0 square, 1 honeycomb (points a - b/2, b sqrt(3)/2), 2 a line only"""
    if grid == 2:
        return np.round(mx), np.zeros_like(my)
    if grid == 0:
        return np.round(mx), np.round(my)
    b0 = np.round(my / S3H)
    bx = np.zeros_like(mx); by = np.zeros_like(my); bd = np.full(mx.shape, np.inf)
    # (the nearest point of a row b is the one at a = round(x + b / 2), and the nearest point of all lies within
    #  1 / sqrt(3) of (x, y), so in one of the three rows next to y: three candidates are enough. The first writing
    #  tried nine, a = round(...) - 1, 0, +1 in each row, and gave the same verdicts: logs/recipe-selfcheck.txt.)
    for db in (-1.0, 0.0, 1.0):
        b = b0 + db
        a = np.round(mx + b / 2.0)
        px = a - b / 2.0; py = b * S3H
        d = (mx - px) ** 2 + (my - py) ** 2
        take = d < bd
        bx = np.where(take, px, bx); by = np.where(take, py, by); bd = np.where(take, d, bd)
    return bx, by


def slide9(mx, my):
    """the honeycomb slide with nine candidates (the first writing), kept to check the short one against"""
    b0 = np.round(my / S3H)
    bx = np.zeros_like(mx); by = np.zeros_like(my); bd = np.full(mx.shape, np.inf)
    for db in (-1.0, 0.0, 1.0):
        b = b0 + db
        for da in (-1.0, 0.0, 1.0):
            a = np.round(mx + b / 2.0) + da
            px = a - b / 2.0; py = b * S3H
            d = (mx - px) ** 2 + (my - py) ** 2
            take = d < bd
            bx = np.where(take, px, bx); by = np.where(take, py, by); bd = np.where(take, d, bd)
    return bx, by


def to_m(P):
    """the frame: picture point -> the object's own coordinates"""
    ux = P[:, 1]; uy = P[:, 2]; uz = P[:, 0] - K2 / 2.0
    d = ux * ux + uy * uy + uz * uz
    d = np.where(d > 0, d, 1e-300)
    return K2 * ux / d, K2 * uy / d, 1.0 + K2 * uz / d


def verdict(P, top, rho, grid, rounds):
    P = np.asarray(P, dtype=np.float64).reshape(-1, 3)
    n = P.shape[0]
    out = np.full(n, 2, dtype=np.uint8)
    mx, my, mz = to_m(P)
    idx = np.arange(n)
    r2 = rho * rho
    for _ in range(int(rounds)):
        if idx.size == 0:
            break
        wall = (mz < 0) | (mz > top)
        if wall.any():
            out[idx[wall]] = 1
            keep = ~wall
            idx = idx[keep]; mx = mx[keep]; my = my[keep]; mz = mz[keep]
            if idx.size == 0:
                break
        sx, sy = slide(mx, my, grid)
        mx = mx - sx; my = my - sy
        q = mx * mx + my * my
        rb = q + mz * mz
        rt = q + (mz - top) ** 2
        a = rb < 1.0
        b = (~a) & (rt < r2)
        c = ~(a | b)
        if c.any():
            out[idx[c]] = 0
        # first sphere
        sa = np.where(a, 1.0 / np.where(rb > 0, rb, 1.0), 1.0)
        sb = np.where(b, r2 / np.where(rt > 0, rt, 1.0), 1.0)
        nmx = np.where(a, mx * sa, np.where(b, mx * sb, mx))
        nmy = np.where(a, my * sa, np.where(b, my * sb, my))
        nmz = np.where(a, mz * sa, np.where(b, top + (mz - top) * sb, mz))
        keep = a | b
        idx = idx[keep]; mx = nmx[keep]; my = nmy[keep]; mz = nmz[keep]
    return out


def solid(P, top, rho, grid, rounds):
    """what the page draws: inside, or undecided when the page's rounds run out"""
    return verdict(P, top, rho, grid, rounds) != 0


if __name__ == '__main__':
    # a small self-check on facts that follow from the brief alone: the middle ball is k^2 wide about x = 0, the
    # two neighbours k^2 / (top - 1) wide and touch it at x = +-k^2 / 2; the picture is its own mirror image.
    rng = np.random.default_rng(1)
    for rho, p in ((1.0, 55.56), (0.5, 150.0), (0.25, 300.0), (0.05, 1000.0)):
        top = 1 + 100.0 / p
        for grid in (0, 1, 2):
            n = 40000
            # points inside the middle ball
            v = rng.normal(size=(n, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; r = rng.random(n) ** (1 / 3)
            A = v * (r * 0.999 * K2 / 2)[:, None]
            # points inside the right neighbour
            R = K2 / (top - 1) / 2
            B = v * (r * 0.999 * R)[:, None] + np.array([K2 / 2 + R, 0, 0])
            # random points, and their mirror images
            C = rng.uniform(-3, 3, size=(n, 3)); C2 = C * np.array([-1.0, 1, 1])
            va = verdict(A, top, rho, grid, 300); vb = verdict(B, top, rho, grid, 300)
            vc = verdict(C, top, rho, grid, 300); vc2 = verdict(C2, top, rho, grid, 300)
            print('rho %.3f p %7.2f grid %d: middle ball all inside %s, right neighbour all inside %s, mirror image differs at %d of %d, inside %d outside %d undecided %d'
                  % (rho, p, grid, bool((va == 1).all()), bool((vb == 1).all()), int((vc != vc2).sum()), n, int((vc == 1).sum()), int((vc == 0).sum()), int((vc == 2).sum())))
