"""Round 27, checker A: my own tools for the balls-on-balls object. Nothing here is taken from the builder.

  recipe_inside(x, y, z, t, grid, rounds)   the recipe of docs/ROUND27.md section 1, written from that text (numpy)
  tree_inside(x, y, z, t, grid, rounds)     out/r25/klein/tree.py, called as it is (through the bench library)
  enum_cell(t, grid, rho)                   BRUTE FORCE, no recipe: every ball of the object by walking the group
                                            (slides by whole numbers, the two sphere inversions) from the two walls,
                                            one copy per cell of the grid, down to radius rho in the object's own space
  picture_balls(cell, t, grid, rmin)        the same balls in picture coordinates, down to radius rmin
  NearBalls(balls)                          true distance from points to the nearest ball surface (exact, k-d trees)
  glsl_de(p, t, grid, rounds, dtype)        GL_BALLS de() of out/r27/entry/overlay/js/32-balls.js ported line by line
                                            (TRAP_SOLIDS 0, no landing length); returns best, free, decided, inside
grid: 0 square, 1 honeycomb, 2 a line only.
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))))   # (fixer: one folder deeper)
K2 = 1.05
S3 = np.sqrt(3.0)
GRIDNAME = {0: 'square', 1: 'hex', 2: 'line'}
TREENAME = {0: 'gauss', 1: 'eisen', 2: 'line'}
BOX = (1.8, 1.3, 1.3)


# ------------------------------------------------------------------ the recipe, from the text of ROUND27.md
def slide(grid, mx, my):
    """(mx, my) minus the nearest whole number of the grid."""
    if grid == 2:
        return mx - np.round(mx), my
    if grid == 0:
        return mx - np.round(mx), my - np.round(my)
    # honeycomb: whole numbers a + b w, w a sixth of a turn = (1/2, sqrt3/2). Try all near candidates.
    b0 = np.round(my / (S3 / 2))
    bx, by, bd = mx, my, np.full(np.shape(mx), np.inf)
    for db in (-1, 0, 1):
        b = b0 + db
        a0 = np.round(mx - b / 2)
        for da in (-1, 0, 1):
            a = a0 + da
            px = mx - (a + b / 2); py = my - b * S3 / 2; d = px * px + py * py
            m = d < bd
            bx = np.where(m, px, bx); by = np.where(m, py, by); bd = np.where(m, d, bd)
    return bx, by


def to_m(x, y, z):
    ux, uy, uz = y, z, x - K2 / 2
    d = ux * ux + uy * uy + uz * uz
    d = np.where(d > 0, d, 1e-300)
    return K2 * ux / d, K2 * uy / d, 1 + K2 * uz / d


def recipe_inside(x, y, z, t, grid, rounds, want_rounds=False):
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    mx, my, mz = to_m(x, y, z)
    top = 2 * t
    res = np.ones(x.shape, bool)          # undecided when the rounds run out counts as inside
    used = np.full(x.shape, rounds, np.int32)
    live = np.ones(x.shape, bool)
    for i in range(rounds):
        ins = live & ((mz < 0) | (mz > top))
        used[ins] = i; live &= ~ins
        mx, my = slide(grid, mx, my)
        rb = mx * mx + my * my + mz * mz
        rt = mx * mx + my * my + (mz - top) ** 2
        inb = rb < 1; itp = (rt < 1) & ~inb
        out = live & ~inb & ~itp
        res[out] = False; used[out] = i; live &= ~out
        sb = 1 / np.where(rb > 0, rb, 1.0); st = 1 / np.where(rt > 0, rt, 1.0)
        mx = np.where(inb, mx * sb, np.where(itp, mx * st, mx))
        my = np.where(inb, my * sb, np.where(itp, my * st, my))
        mz = np.where(inb, mz * sb, np.where(itp, top + (mz - top) * st, mz))
        if not live.any():
            break
    if want_rounds:
        return res, used, live
    return res



def recipe_state(x, y, z, t, grid, rounds):
    """The recipe again, dropping the points that are decided as it goes (fast for many points and many rounds).
    Returns 0 outside, 1 inside (a wall was reached), 2 undecided after the rounds."""
    x, y, z = (np.asarray(v, float).ravel() for v in (x, y, z))
    mx, my, mz = to_m(x, y, z)
    top = 2 * t
    state = np.full(x.size, 2, np.int8)
    idx = np.arange(x.size)
    for i in range(rounds):
        ins = (mz < 0) | (mz > top)
        state[idx[ins]] = 1
        keep = ~ins
        idx, mx, my, mz = idx[keep], mx[keep], my[keep], mz[keep]
        if not idx.size:
            break
        mx, my = slide(grid, mx, my)
        rb = mx * mx + my * my + mz * mz
        rt = mx * mx + my * my + (mz - top) ** 2
        inb = rb < 1; itp = (rt < 1) & ~inb
        out = ~inb & ~itp
        state[idx[out]] = 0
        sb = 1 / np.where(rb > 0, rb, 1.0); st = 1 / np.where(rt > 0, rt, 1.0)
        mx = np.where(inb, mx * sb, mx * st); my = np.where(inb, my * sb, my * st)
        mz = np.where(inb, mz * sb, top + (mz - top) * st)
        keep = ~out
        idx, mx, my, mz = idx[keep], mx[keep], my[keep], mz[keep]
        if not idx.size:
            break
    return state


_tree = None


def tree_inside(x, y, z, t, grid, rounds):
    global _tree
    if _tree is None:
        sys.path.insert(0, os.path.join(ROOT, 'out', 'r25', 'klein'))
        import tree as _t
        _tree = _t
    rule = _tree.tree(TREENAME[grid], t=t, k2=K2)
    return _tree.M.stay(rule, np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), 0.0, 0.0, 0.0, rounds) >= rounds


# ------------------------------------------------------------------ brute force: walk the group from the two walls
def grid_points(grid, rmax):
    """Whole numbers of the grid with |n| <= rmax, sorted by |n|. Returns (n x 2 array, lengths)."""
    R = int(np.ceil(rmax)) + 2
    if grid == 2:
        a = np.arange(-R, R + 1); pts = np.stack([a.astype(float), np.zeros(a.size)], 1)
    elif grid == 0:
        a, b = np.meshgrid(np.arange(-R, R + 1), np.arange(-R, R + 1)); pts = np.stack([a.ravel().astype(float), b.ravel().astype(float)], 1)
    else:
        a, b = np.meshgrid(np.arange(-2 * R, 2 * R + 1), np.arange(-2 * R, 2 * R + 1))
        a = a.ravel().astype(float); b = b.ravel().astype(float)
        pts = np.stack([a + b / 2, b * S3 / 2], 1)
    ln = np.hypot(pts[:, 0], pts[:, 1])
    keep = ln <= rmax + 1e-9
    pts, ln = pts[keep], ln[keep]
    o = np.argsort(ln, kind='stable')
    return pts[o], ln[o]


SCALE = 1e6 * 0.7310585786


def cell_key(grid, c):
    """Reduce centres modulo the grid and give an integer key. Returns (reduced centres, keys)."""
    c = c.copy()
    if grid == 2:
        c[:, 0] -= np.round(c[:, 0]); fa = c[:, 0]; fb = c[:, 1]
        ka = np.round(fa * SCALE).astype(np.int64); kb = np.round(fb * SCALE).astype(np.int64)
        wrap = np.int64(round(0.5 * SCALE))
        ka = np.where(np.abs(np.abs(fa) - 0.5) < 2e-7, -wrap, ka)
    elif grid == 0:
        c[:, 0] -= np.round(c[:, 0]); c[:, 1] -= np.round(c[:, 1]); fa = c[:, 0]; fb = c[:, 1]
        wrap = np.int64(round(0.5 * SCALE))
        ka = np.where(np.abs(np.abs(fa) - 0.5) < 2e-7, -wrap, np.round(fa * SCALE).astype(np.int64))
        kb = np.where(np.abs(np.abs(fb) - 0.5) < 2e-7, -wrap, np.round(fb * SCALE).astype(np.int64))
    else:
        b = c[:, 1] / (S3 / 2); a = c[:, 0] - b / 2          # c = a (1, 0) + b (1/2, sqrt3/2)
        fa = a - np.round(a); fb = b - np.round(b)
        c[:, 0] = fa + fb / 2; c[:, 1] = fb * S3 / 2
        wrap = np.int64(round(0.5 * SCALE))
        ka = np.where(np.abs(np.abs(fa) - 0.5) < 2e-7, -wrap, np.round(fa * SCALE).astype(np.int64))
        kb = np.where(np.abs(np.abs(fb) - 0.5) < 2e-7, -wrap, np.round(fb * SCALE).astype(np.int64))
    kz = np.round(c[:, 2] * SCALE).astype(np.int64)
    # fields: ka 21 bits, kb 21 bits, kz 22 bits (kz up to 5e6 * 0.73 = 3.7e6 < 2^22)
    key =((ka + (1 << 20)) << 43) | ((kb + (1 << 20)) << 22) | (kz & ((1 << 22) - 1))
    return c, key


def enum_cell(t, grid, rho, max_levels=400, verbose=False):
    """Every ball with radius >= rho (object's own space), one copy per cell of the grid. Brute force over the group:
    start from the images of the two walls, then again and again: slide a ball by every whole number that can matter,
    turn it inside out in each of the two unit spheres, keep what is new and not smaller than rho.
    Returns dict(c (n x 3), r (n), lev (n))."""
    top = 2 * t
    seeds_c = np.array([[0.0, 0.0, 1 / (4 * t)], [0.0, 0.0, top - 1 / (4 * t)]])
    seeds_r = np.array([1 / (4 * t), 1 / (4 * t)])
    C, key = cell_key(grid, seeds_c)
    seen = set(key.tolist())
    allc, allr, alll = [C], [seeds_r], [np.ones(2, np.int32)]
    fc, fr = C, seeds_r
    for lev in range(2, max_levels):
        reach = np.sqrt(fr / rho + fr * fr) + 1.3
        pts, ln = grid_points(grid, reach.max())
        newc, newr = [], []
        order = np.argsort(-reach); fc, fr, reach = fc[order], fr[order], reach[order]
        negreach = -reach
        for j in range(pts.shape[0]):
            k = np.searchsorted(negreach, -ln[j], side='right')    # spheres whose reach >= |n|
            if k == 0:
                break
            cc = fc[:k].copy(); cc[:, 0] += pts[j, 0]; cc[:, 1] += pts[j, 1]; rr = fr[:k]
            for oz in (0.0, top):
                d = cc.copy(); d[:, 2] -= oz
                P = (d * d).sum(1) - rr * rr
                ok = P > 1e-9
                rn = np.where(ok, rr / np.where(ok, P, 1.0), 0.0)
                ok &= rn >= rho
                if ok.any():
                    cn = d[ok] / P[ok, None]; cn[:, 2] += oz
                    newc.append(cn); newr.append(rn[ok])
        if not newc:
            break
        nc = np.concatenate(newc); nr = np.concatenate(newr)
        nc, nk = cell_key(grid, nc)
        _, first = np.unique(nk, return_index=True)
        nc, nr, nk = nc[first], nr[first], nk[first]
        fresh = np.array([k not in seen for k in nk.tolist()], bool)
        if not fresh.any():
            break
        nc, nr, nk = nc[fresh], nr[fresh], nk[fresh]
        seen.update(nk.tolist())
        allc.append(nc); allr.append(nr); alll.append(np.full(nr.size, lev, np.int32))
        fc, fr = nc, nr
        if verbose:
            print('   level %d: %d new balls (smallest %.2e)' % (lev, nr.size, nr.min())); sys.stdout.flush()
    return dict(c=np.concatenate(allc), r=np.concatenate(allr), lev=np.concatenate(alll), t=t, grid=grid, rho=rho)


def column_ball(n, t):
    """All balls of the cell slid by the whole number n (|n| >= 3) land, in the picture, inside this ball:
    centre and radius. (|x / |x|^2 - y / |y|^2| = |x - y| / (|x| |y|), with y the foot of the column.)"""
    ln = float(np.hypot(n[0], n[1]))
    cen = np.array([K2 / 2, K2 * n[0] / ln ** 2, K2 * n[1] / ln ** 2])
    rad = K2 * np.hypot(0.9, 2 * t - 0.8) / ((ln - 0.9) * ln)
    return cen, rad


def picture_balls(cell, rmin, with_walls=True, keep=None, per_n=None):
    """The balls of the picture with radius >= rmin: centres (n x 3, picture x y z), radii, level (walls: 0).
    keep(C, R) -> mask, if given, says which balls are wanted (a region of the picture).
    per_n(n, |n|) -> None (no ball slid by this whole number is wanted) or the smallest radius wanted among them
    (>= rmin); it only saves work, keep() decides."""
    t, grid = cell['t'], cell['grid']
    c, r, lev = cell['c'], cell['r'], cell['lev']
    order = np.argsort(-r); c, r, lev = c[order], r[order], lev[order]
    nmax = np.sqrt(K2 * r[0] / rmin + 0.07) + 0.9
    negr = -r
    pts, ln = grid_points(grid, nmax)
    oc, orr, ol = [], [], []
    for j in range(pts.shape[0]):
        rm = rmin
        if per_n is not None and ln[j] >= 3:
            rm = per_n(pts[j], ln[j])
            if rm is None:
                continue
            rm = max(rm, rmin)
        # a ball slid by n has P = |c + n - F|^2 - r^2 >= (|n| - 0.9)^2 - 0.07, and its picture radius is k^2 r / P
        thr = rm * max((ln[j] - 0.9) ** 2 - 0.07, 0.0) / K2 if ln[j] > 0.9 else 0.0
        k = np.searchsorted(negr, -thr, side='right')
        if k == 0:
            continue
        d = c[:k].copy(); d[:, 0] += pts[j, 0]; d[:, 1] += pts[j, 1]; d[:, 2] -= 1.0
        P = (d * d).sum(1) - r[:k] ** 2
        rp = K2 * r[:k] / P
        ok = (P > 0) & (rp >= rm)
        if ok.any():
            u = K2 * d[ok] / P[ok, None]
            cc = np.stack([u[:, 2] + K2 / 2, u[:, 0], u[:, 1]], 1); rr = rp[ok]; ll = lev[:k][ok]
            if keep is not None:
                m = keep(cc, rr)
                cc, rr, ll = cc[m], rr[m], ll[m]
            if rr.size:
                oc.append(cc); orr.append(rr); ol.append(ll)
    C = np.concatenate(oc) if oc else np.zeros((0, 3)); Rr = np.concatenate(orr) if orr else np.zeros(0)
    L = np.concatenate(ol) if ol else np.zeros(0, np.int32)
    if with_walls:
        wr = K2 / (2 * (2 * t - 1))
        wc = np.array([[0.0, 0.0, 0.0], [K2 / 2 + wr, 0.0, 0.0]]); wrr = np.array([K2 / 2, wr])
        m = keep(wc, wrr) if keep is not None else np.ones(2, bool)
        C = np.concatenate([wc[m], C]); Rr = np.concatenate([wrr[m], Rr]); L = np.concatenate([np.zeros(int(m.sum()), np.int32), L])
    return C, Rr, L


def keep_box(bx=2.3, by=1.8, bz=1.8):
    return lambda C, R: (np.abs(C[:, 0]) - R <= bx) & (np.abs(C[:, 1]) - R <= by) & (np.abs(C[:, 2]) - R <= bz)


def keep_near(focus, rad):
    f = np.asarray(focus, float)
    return lambda C, R: np.sqrt(((C - f) ** 2).sum(1)) - R <= rad


class NearBalls:
    """Exact signed distance from points to the nearest ball surface of a list (negative inside a ball)."""

    def __init__(self, C, R):
        from scipy.spatial import cKDTree
        self.C, self.R = C, R
        lr = np.log2(R)
        self.bins = []
        lo = np.floor(lr.min()); hi = np.floor(lr.max())
        for b in np.arange(lo, hi + 1):
            idx = np.nonzero(np.floor(lr) == b)[0]
            if idx.size:
                self.bins.append((idx, cKDTree(C[idx]), R[idx].max()))

    def dist(self, P, want_index=False):
        P = np.asarray(P, float)
        best = np.full(P.shape[0], np.inf); bi = np.full(P.shape[0], -1, np.int64)
        # first pass: nearest centre in every size class gives an upper bound
        for idx, tree, rmax in self.bins:
            dc, j = tree.query(P, k=min(4, idx.size))
            if dc.ndim == 1:
                dc, j = dc[:, None], j[:, None]
            dd = dc - self.R[idx][j]
            a = dd.argmin(1); v = dd[np.arange(P.shape[0]), a]
            m = v < best; best[m] = v[m]; bi[m] = idx[j[np.arange(P.shape[0]), a]][m]
        # second pass: anything nearer than the bound has its centre within bound + radius
        for idx, tree, rmax in self.bins:
            rad = np.maximum(best, 0) + rmax + 1e-12
            lists = tree.query_ball_point(P, rad)
            for i, l in enumerate(lists):
                if len(l) > 4:
                    l = np.asarray(l); g = idx[l]
                    dd = np.sqrt(((self.C[g] - P[i]) ** 2).sum(1)) - self.R[g]
                    a = dd.argmin()
                    if dd[a] < best[i]:
                        best[i] = dd[a]; bi[i] = g[a]
        return (best, bi) if want_index else best


# ------------------------------------------------------------------ GL_BALLS de(), ported line by line
def glsl_de(p, t, grid, rounds, dtype=np.float32):
    """p: n x 3 picture points. The lines of de() in GL_BALLS, with TRAP_SOLIDS 0 and land = 0 (a plain distance
    query). Returns best, free, decided, inside (the shader's d is:
        !decided ? -1e-7 : inside ? best : min(best, max(free, 2.0 * uDetail * gPix)) )."""
    f = dtype
    p = np.asarray(p, f)
    n = p.shape[0]
    uBT = f(t); BK2 = f(K2)
    top = f(2.0) * uBT
    H = uBT - np.sqrt(np.maximum(uBT * uBT - f(1.0), f(0.0)), dtype=f)
    rest = f(0.5) * H if grid == 0 else (H / f(3.0) if grid == 1 else f(0.25) * H)

    def kpearl(h, D, kk):
        with np.errstate(invalid='ignore', divide='ignore'):
            v = f(2.0) * h / (f(1.0) + np.sqrt(f(1.0) + kk * h * np.maximum(D, f(0.0)), dtype=f))
        return np.where(h > 0, v, h).astype(f)

    def bnear(qx, qy):
        if grid == 2:
            return np.floor(qx + f(0.5)), np.zeros_like(qy)
        if grid == 0:
            return np.floor(qx + f(0.5)), np.floor(qy + f(0.5))
        c = f(0.8660254038)
        b0 = np.floor(qy / c + f(0.5)); bd = np.full(qx.shape, f(1e30), f)
        bx = np.zeros_like(qx); by = np.zeros_like(qy)
        for j in (-1, 0, 1):
            b = b0 + f(j); a = np.floor(qx + f(0.5) * b + f(0.5))
            sx = a - f(0.5) * b; sy = c * b
            wx = qx - sx; wy = qy - sy
            d = wx * wx + wy * wy
            m = d < bd
            bd = np.where(m, d, bd); bx = np.where(m, sx, bx); by = np.where(m, sy, by)
        return bx.astype(f), by.astype(f)

    u = np.stack([p[:, 1], p[:, 2], p[:, 0] - f(0.5) * BK2], 1).astype(f)
    DF = (BK2 / np.maximum((u * u).sum(1, dtype=f), f(1e-20))).astype(f)
    best = np.full(n, f(1e9), f); free = np.zeros(n, f)
    z = (np.array([0, 0, 1], f) + DF[:, None] * u).astype(f)
    W = np.tile(np.array([0, 0, 1], f), (n, 1))
    inside = np.zeros(n, bool); decided = np.zeros(n, bool)
    live = np.ones(n, bool)
    for i in range(rounds):
        nx, ny = bnear(z[:, 0], z[:, 1])
        z2 = z.copy(); W2 = W.copy()
        z2[:, 0] -= nx; z2[:, 1] -= ny; W2[:, 0] -= nx; W2[:, 1] -= ny
        zw = z2 - W2
        L2 = np.maximum((zw * zw).sum(1, dtype=f), f(1e-30)); kk = f(4.0) / L2
        hb = z2[:, 2]; ht = top - z2[:, 2]
        cand = (np.minimum(kpearl(hb, W2[:, 2], kk), kpearl(ht, top - W2[:, 2], kk)) / DF).astype(f)
        best = np.where(live, np.minimum(best, cand), best)
        wall = live & ((hb < 0) | (ht < 0))
        inside |= wall; decided |= wall; live &= ~wall
        zt = z2.copy(); zt[:, 2] -= top
        rb = (z2 * z2).sum(1, dtype=f); rt = (zt * zt).sum(1, dtype=f)
        A = live & (rb < 1.0)
        B = live & ~A & (rt < 1.0)
        Cc = live & ~A & ~B
        # A
        s = (f(1.0) / np.maximum(rb, f(1e-20))).astype(f)
        zA = z2 * s[:, None]; WA = W2 / np.maximum((W2 * W2).sum(1, dtype=f), f(1e-20))[:, None]
        # B
        sB = (f(1.0) / np.maximum(rt, f(1e-20))).astype(f)
        Wt = W2.copy(); Wt[:, 2] -= top
        zB = zt * sB[:, None]; zB[:, 2] += top
        WB = Wt / np.maximum((Wt * Wt).sum(1, dtype=f), f(1e-20))[:, None]; WB[:, 2] += top
        # C: OUTSIDE, for good
        if Cc.any():
            cb = np.sqrt(z2[:, 0] ** 2 + z2[:, 1] ** 2 + (hb - f(0.5) * H) ** 2, dtype=f) - f(0.5) * H
            ct = np.sqrt(z2[:, 0] ** 2 + z2[:, 1] ** 2 + (ht - f(0.5) * H) ** 2, dtype=f) - f(0.5) * H
            if grid == 2:
                lo = np.sqrt(z2[:, 1] ** 2 + hb ** 2, dtype=f); hi = np.sqrt(z2[:, 1] ** 2 + ht ** 2, dtype=f)
            else:
                lo, hi = hb, ht
            e = np.maximum(np.minimum(np.minimum(cb, ct), np.minimum(lo, hi) - rest), f(0.0)).astype(f)
            L = np.sqrt(L2, dtype=f)
            fr = (e * L / ((L + e) * DF)).astype(f)
            free = np.where(Cc, fr, free)
            decided |= Cc; live &= ~Cc
        z = np.where(A[:, None], zA, np.where(B[:, None], zB, np.where(live[:, None], z2, z))).astype(f)
        W = np.where(A[:, None], WA, np.where(B[:, None], WB, np.where(live[:, None], W2, W))).astype(f)
        DF = np.where(A, DF * s, np.where(B, DF * sB, DF)).astype(f)
        if not live.any():
            break
    return best, free, decided, inside


def glsl_d(best, free, decided, inside, hold=0.0):
    """The number de() returns. hold = 2.0 * uDetail * gPix (0 in the 2D view and for a 3D model)."""
    return np.where(~decided, -1e-7, np.where(inside, best, np.minimum(best, np.maximum(free, hold))))
