"""Round 27, explorer "measure": the balls object as an explicit LIST OF BALLS, and the tools to draw and measure it.

Every body of the object is an exact ball. So instead of asking the recipe point by point (out/r25/klein/tree.py), this
file lists the balls: start from the two half-spaces L (mz < 0) and U (mz > top) and apply the moves of the object
(slides by whole numbers of the grid, sphere inversions) to them until the balls are smaller than a cut-off. A ball
moved by a sphere inversion is a ball again, with a centre and radius given by one line of arithmetic.

    import ballkit as K
    g = K.Grid('gauss')                               # 'line', 'gauss' (square), 'eisen' (honeycomb); period=2.0: every second whole number
    gens = K.recipe_gens(top=2.8)                     # the object: inversions in the unit spheres about (0,0,0) and (0,0,top)
    gens = K.recipe_gens(top, slide=(0.5, 0.0))       # the glued copy slid sideways
    gens = K.klein_gens(mu=(0.3, 0.0, 1.95))          # the lab's old Kleinian group: q -> mu + 1/q and back (mu = slide x, slide y, height)
    reps = K.build(g, gens, top, rho_min=2e-4)        # the balls, one for every family of slid copies: array (N, 4) = centre, radius
    B = K.picture(reps, g, top, c0=(0, 0, 1), k2=1.05, r_min=0.002)     # the balls in picture coordinates (x along the chain,
                                                      # y up in the flat plane, z out of it), L first, U second
    img = K.shade(*K.splat(B, 900, 640, 1.75))        # the solid, seen from cam (exact balls, no blocks)
    cov = K.cut(B, 900, 640, (-1.8, 1.8, -1.28, 1.28))                  # the flat cut z = 0 (coverage 0..1 per pixel)
    v = K.recipe(mx, my, mz, g, top, slide=(0, 0))    # the recipe itself, point by point: 1 inside, 0 outside, -1 undecided
    K.to_model(x, y, z, k2, c0)                       # picture point -> the object's own coordinates

Checked in check.py: the recipe here against out/r25/klein/tree.py, and the list of balls against the recipe.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

S3 = np.sqrt(3.0)
BASIS = {'line': [[1.0, 0.0]], 'gauss': [[1.0, 0.0], [0.0, 1.0]], 'eisen': [[1.0, 0.0], [-0.5, S3 / 2]]}


class Grid:
    """The whole numbers that slide: a line of them, a square grid or a honeycomb grid, in the plane mz = 0."""

    def __init__(self, name='gauss', period=1.0):
        self.name, self.period = name, period
        self.B = np.array(BASIS[name], float) * period; self.rank = len(self.B)
        if self.rank == 2:
            self.Binv = np.linalg.inv(self.B.T); self.kappa = float(np.linalg.norm(self.Binv, 2))

    def coef(self, x, y):
        if self.rank == 1:
            return (np.asarray(x) / self.period)[None]
        return self.Binv[:, 0, None] * np.ravel(x)[None] + self.Binv[:, 1, None] * np.ravel(y)[None]

    def cell(self, x, y):
        """The point slid into one fixed cell (the same copy for every slid copy of a ball)."""
        x = np.asarray(x, float); y = np.asarray(y, float)
        if self.rank == 1:
            return x - self.period * np.floor(x / self.period + 0.5 + 1e-7), y
        a = self.coef(x, y); a = np.floor(a + 0.5 + 1e-7)
        return x - (a[0] * self.B[0, 0] + a[1] * self.B[1, 0]).reshape(x.shape), y - (a[0] * self.B[0, 1] + a[1] * self.B[1, 1]).reshape(y.shape)

    def near(self, x, y):
        """The point minus the NEAREST whole number of the grid (the slide of the recipe)."""
        if self.rank == 1:
            return x - self.period * np.round(x / self.period), y
        if self.name == 'gauss':
            return x - self.period * np.round(x / self.period), y - self.period * np.round(y / self.period)
        sh = np.shape(x); a = np.round(self.coef(x, y)); bx, by = np.ravel(x).copy(), np.ravel(y).copy(); bd = np.full(bx.shape, np.inf)
        X, Y = np.ravel(x), np.ravel(y)
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                px = X - ((a[0] + da) * self.B[0, 0] + (a[1] + db) * self.B[1, 0]); py = Y - ((a[0] + da) * self.B[0, 1] + (a[1] + db) * self.B[1, 1])
                d = px * px + py * py; m = d < bd; bx = np.where(m, px, bx); by = np.where(m, py, by); bd = np.where(m, d, bd)
        return bx.reshape(sh), by.reshape(sh)

    def pairs(self, cx, cy, R, chunk=4_000_000):
        """For every i: all whole numbers n of the grid with |n - (cx[i], cy[i])| <= R[i]. Returns (i, nx, ny)."""
        cx, cy, R = (np.asarray(t, float) for t in (cx, cy, R)); ok = np.nonzero(R >= 0)[0]
        I, NX, NY = [], [], []
        if ok.size == 0:
            return np.zeros(0, int), np.zeros(0), np.zeros(0)
        if self.rank == 1:
            Kk = np.ceil(R[ok] / self.period).astype(int) + 1
        else:
            Kk = np.ceil(R[ok] * self.kappa).astype(int) + 1
        for kv in np.unique(Kk):
            sel = ok[Kk == kv]; off = np.arange(-kv, kv + 1)
            if self.rank == 1:
                per = off.size; step = max(1, chunk // per)
                for s in range(0, sel.size, step):
                    ii = sel[s:s + step]; a0 = np.round(cx[ii] / self.period)
                    nx = (a0[:, None] + off[None]) * self.period; ny = np.zeros_like(nx)
                    m = (nx - cx[ii, None]) ** 2 + cy[ii, None] ** 2 <= R[ii, None] ** 2
                    I.append(np.broadcast_to(ii[:, None], nx.shape)[m]); NX.append(nx[m]); NY.append(ny[m])
            else:
                da, db = np.meshgrid(off, off); da, db = da.ravel(), db.ravel(); per = da.size; step = max(1, chunk // per)
                for s in range(0, sel.size, step):
                    ii = sel[s:s + step]; a = np.round(self.coef(cx[ii], cy[ii]))
                    A = a[0][:, None] + da[None]; Bc = a[1][:, None] + db[None]
                    nx = A * self.B[0, 0] + Bc * self.B[1, 0]; ny = A * self.B[0, 1] + Bc * self.B[1, 1]
                    m = (nx - cx[ii, None]) ** 2 + (ny - cy[ii, None]) ** 2 <= R[ii, None] ** 2
                    I.append(np.broadcast_to(ii[:, None], nx.shape)[m]); NX.append(nx[m]); NY.append(ny[m])
        return np.concatenate(I), np.concatenate(NX), np.concatenate(NY)


class Gen:
    """One move: x -> A + Rot(inv(x) - o), inv = the inversion in the unit sphere about o; Rot = nothing, or the half
    turn about the mx-axis (my, mz -> -my, -mz) that the lab's old Kleinian group uses (q -> mu + 1/q)."""

    def __init__(self, o, A, flip=False):
        self.o = np.array(o, float); self.A = np.array(A, float); self.flip = flip

    def ball(self, c, r):
        d = c - self.o; den = (d * d).sum(1) - r * r; s = 1.0 / np.where(np.abs(den) > 1e-12, den, 1e-12); v = d * s[:, None]
        if self.flip:
            v[:, 1:] *= -1
        return self.A + v, r * np.abs(s)

    def point(self, x, y, z):
        dx, dy, dz = x - self.o[0], y - self.o[1], z - self.o[2]; s = 1.0 / np.maximum(dx * dx + dy * dy + dz * dz, 1e-300)
        f = -1.0 if self.flip else 1.0
        return self.A[0] + dx * s, self.A[1] + f * dy * s, self.A[2] + f * dz * s

    def half(self, which, top):
        """The image of L (mz < 0) or U (mz > top): 'L', 'U', or a ball (centre, radius)."""
        h = 0.0 if which == 'L' else top; side = -1.0 if which == 'L' else 1.0          # the half-space is side * (mz - h) > 0
        delta = side * (h - self.o[2])                                                 # how far o stands outside it
        f = -1.0 if self.flip else 1.0
        if abs(delta) < 1e-12:                                                          # o on its wall: a half-space again
            s2 = side * f; wall = self.A[2]
            return ('U' if s2 > 0 else 'L') if abs(wall - (top if s2 > 0 else 0.0)) < 1e-9 else None
        if delta < 0:
            return None
        return self.A + np.array([0.0, 0.0, f * side / (2 * delta)]), 1.0 / (2 * delta)


def recipe_gens(top, slide=(0.0, 0.0)):
    """The object's two inversions: unit spheres about (0, 0, 0) and about (slide, top)."""
    p = (slide[0], slide[1], top)
    return [Gen((0, 0, 0), (0, 0, 0)), Gen(p, p)]


def klein_gens(mu):
    """The lab's old Kleinian group: T(q) = mu + 1/q and its undo-move. mu = (slide x, slide y, height)."""
    return [Gen((0, 0, 0), mu, flip=True), Gen(mu, (0, 0, 0), flip=True)]


def _keys(c, r, tol=1e-8):
    q = np.round(np.column_stack([c, r]) / tol).astype(np.int64).view(np.uint64)
    k = q[:, 0] * np.uint64(0x9E3779B97F4A7C15) ^ (q[:, 1] * np.uint64(0xC2B2AE3D27D4EB4F) + np.uint64(0x165667B19E3779F9))
    k = (k ^ (k >> np.uint64(29))) * np.uint64(0xBF58476D1CE4E5B9) ^ (q[:, 2] * np.uint64(0x94D049BB133111EB))
    return (k ^ (k >> np.uint64(31))) * np.uint64(0xD6E8FEB86659FD93) ^ (q[:, 3] * np.uint64(0xFF51AFD7ED558CCD))


def build(grid, gens, top, rho_min=2e-4, cap=3_000_000, strict=True, verbose=False):
    """Every ball of the object with radius >= rho_min (in the object's own coordinates), one for each family of slid
    copies, as an array (N, 4). strict: a move is applied only to balls that lie outside its unit sphere (then balls
    only shrink, and the list is complete when the recipe is valid). Returns (reps, info)."""
    t0 = time.time(); front_c, front_r = [], []
    for g in gens:
        for which in ('L', 'U'):
            im = g.half(which, top)
            if isinstance(im, tuple):
                front_c.append(im[0]); front_r.append(im[1])
    c = np.array(front_c, float).reshape(-1, 3); r = np.array(front_r, float)
    c[:, 0], c[:, 1] = grid.cell(c[:, 0], c[:, 1])
    k = _keys(c, r); _, u = np.unique(k, return_index=True); c, r, k = c[u], r[u], k[u]
    known = np.sort(k); all_c, all_r = [c], [r]; total = len(r); level = 1; capped = False
    while len(r) and not capped:
        nc, nr = [], []
        for g in gens:
            R2 = r / rho_min + r * r - (c[:, 2] - g.o[2]) ** 2
            i, nx, ny = grid.pairs(g.o[0] - c[:, 0], g.o[1] - c[:, 1], np.where(R2 > 0, np.sqrt(np.maximum(R2, 0)), -1.0))
            if i.size == 0:
                continue
            cc = c[i].copy(); cc[:, 0] += nx; cc[:, 1] += ny; rr = r[i]
            if strict:
                d = np.sqrt(((cc - g.o) ** 2).sum(1)); m = d - rr >= 1 - 1e-9; cc, rr = cc[m], rr[m]
            ic, ir = g.ball(cc, rr); m = (ir >= rho_min) & (ir < 1e5)
            nc.append(ic[m]); nr.append(ir[m])
        if not nc:
            break
        c = np.concatenate(nc); r = np.concatenate(nr)
        c[:, 0], c[:, 1] = grid.cell(c[:, 0], c[:, 1])
        k = _keys(c, r); _, u = np.unique(k, return_index=True); c, r, k = c[u], r[u], k[u]
        new = ~np.isin(k, known); c, r, k = c[new], r[new], k[new]
        known = np.sort(np.concatenate([known, k])); all_c.append(c); all_r.append(r); total += len(r); level += 1
        if verbose:
            print('   level %d: %d new balls (%d in all), %.1f s' % (level, len(r), total, time.time() - t0)); sys.stdout.flush()
        capped = total > cap
    reps = np.column_stack([np.concatenate(all_c), np.concatenate(all_r)])
    return reps, {'levels': level, 'n': len(reps), 'capped': capped, 'seconds': time.time() - t0}


def picture(reps, grid, top, c0=(0.0, 0.0, 1.0), k2=1.05, r_min=0.002):
    """The balls in picture coordinates (one sphere inversion about c0 with radius sqrt(k2)), radius >= r_min, as (N, 4).
    Picture x = along the chain, y = up in the flat plane, z = out of the flat plane; L is centred at the origin.
    L is row 0, U is row 1."""
    c0 = np.array(c0, float); c, r = reps[:, :3], reps[:, 3]
    R2 = k2 * r / r_min + r * r - (c[:, 2] - c0[2]) ** 2
    i, nx, ny = grid.pairs(c0[0] - c[:, 0], c0[1] - c[:, 1], np.where(R2 > 0, np.sqrt(np.maximum(R2, 0)), -1.0))
    cc = c[i].copy(); cc[:, 0] += nx; cc[:, 1] += ny; rr = r[i]
    d = cc - c0; den = (d * d).sum(1) - rr * rr; ok = den > 1e-12; d, rr, den = d[ok], rr[ok], den[ok]
    s = k2 / den; u = d * s[:, None]; rp = rr * s; off = k2 / (2 * c0[2])
    m = rp >= r_min
    out = np.column_stack([u[m, 2] + off, u[m, 0], u[m, 1], rp[m]])
    rL = k2 / (2 * c0[2]); rU = k2 / (2 * (top - c0[2]))
    head = np.array([[0.0, 0.0, 0.0, rL], [rL + rU, 0.0, 0.0, rU]])
    out = out[np.argsort(-out[:, 3])]
    return np.concatenate([head, out])


def to_model(x, y, z, k2=1.05, c0=(0.0, 0.0, 1.0)):
    """Picture point -> the object's own coordinates (the same map as out/r25/klein/tree.py for c0 = (0, 0, 1))."""
    ux, uy, uz = y, z, x - k2 / (2 * c0[2]); d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    return c0[0] + k2 * ux / d, c0[1] + k2 * uy / d, c0[2] + k2 * uz / d


def recipe(mx, my, mz, grid, top, rounds=40, slide=(0.0, 0.0), klein=None):
    """The recipe, point by point, in the object's own coordinates. 1 inside, 0 outside, -1 undecided after `rounds`.
    klein = mu: the lab's old Kleinian group instead (q -> mu + 1/q when inside the unit sphere about 0, the undo-move
    when inside the unit sphere about mu)."""
    sh = np.shape(mx); x, y, z = (np.array(np.broadcast_to(np.asarray(t, float), sh)).ravel() for t in (mx, my, mz))
    out = np.full(x.size, -1, np.int8); idx = np.arange(x.size)
    if klein is not None:
        gf, gc = klein_gens(klein); px, py = klein[0], klein[1]
    else:
        gf, gc = recipe_gens(top, slide); px, py = slide
    for _ in range(rounds):
        ins = (z < 0) | (z > top); out[idx[ins]] = 1
        keep = ~ins; idx, x, y, z = idx[keep], x[keep], y[keep], z[keep]
        if idx.size == 0:
            break
        x, y = grid.near(x, y); inb = x * x + y * y + z * z < 1
        x2, y2 = grid.near(x - px, y - py); x2 += px; y2 += py
        itp = ((x2 - px) ** 2 + (y2 - py) ** 2 + (z - top) ** 2 < 1) & ~inb
        o = ~inb & ~itp; out[idx[o]] = 0
        ax, ay, az = gf.point(x, y, z); bx, by, bz = gc.point(x2, y2, z)
        x = np.where(inb, ax, bx); y = np.where(inb, ay, by); z = np.where(inb, az, bz)
        keep = ~o; idx, x, y, z = idx[keep], x[keep], y[keep], z[keep]
        if idx.size == 0:
            break
    if idx.size:
        ins = (z < 0) | (z > top); out[idx[ins]] = 1
    return out.reshape(sh)


def inside_picture(x, y, z, grid, top, rounds=40, k2=1.05, c0=(0.0, 0.0, 1.0), slide=(0.0, 0.0), klein=None):
    return recipe(*to_model(x, y, z, k2, c0), grid, top, rounds, slide, klein)


def in_balls(P, balls, r_big=0.03):
    """Is each point of P (n, 3) inside one of the balls (N, 4)? Exact (big balls one by one, small ones by a tree)."""
    from scipy.spatial import cKDTree
    P = np.asarray(P, float); ins = np.zeros(len(P), bool); big = balls[:, 3] >= r_big
    for b in balls[big]:
        ins |= ((P - b[:3]) ** 2).sum(1) < b[3] ** 2
    sm = balls[~big]
    if len(sm):
        tr = cKDTree(sm[:, :3]); todo = np.nonzero(~ins)[0]
        for s in range(0, todo.size, 20000):
            ii = todo[s:s + 20000]; nb = tr.query_ball_point(P[ii], r_big)
            for a, lst in zip(ii, nb):
                if lst:
                    q = sm[lst]; ins[a] = bool((((P[a] - q[:, :3]) ** 2).sum(1) < q[:, 3] ** 2).any())
    return ins


def overlaps(balls, n_big=1500, tol=1e-7):
    """Do balls overlap? The n_big largest are tested against all. Returns (pairs that overlap, deepest overlap)."""
    order = np.argsort(-balls[:, 3]); big = balls[order[:n_big]]; cnt = 0; deep = 0.0
    for s in range(0, len(big), 200):
        a = big[s:s + 200]; d = np.sqrt(((a[:, None, :3] - balls[None, :, :3]) ** 2).sum(2)); gap = a[:, None, 3] + balls[None, :, 3] - d
        same = d < 1e-9; gap[same] = -1; nest = d + np.minimum(a[:, None, 3], balls[None, :, 3]) < np.maximum(a[:, None, 3], balls[None, :, 3]) + tol
        m = (gap > tol); cnt += int(m.sum()); deep = max(deep, float(gap[m].max()) if m.any() else 0.0)
    return cnt // 1, deep


# ---------------------------------------------------------------- pictures from the list of balls
def splat(balls, w, h, half_w, centre=(0.0, 0.0, 0.0), cam=(0.45, 0.5, 1.0), ss=2):
    """The solid: exact balls seen from cam (the same eye as mem.solid). Returns (depth, nu, nv, pixel size) at ss times
    the size; shade() brings it down."""
    W, H = w * ss, h * ss; e1, e2, e3 = M.frame(cam); P = balls[:, :3] - np.array(centre, float)
    px = 2 * half_w / (W - 1); u = (P @ e1 + half_w) / px; v = (half_w * H / W - P @ e2) / px; d = P @ e3; r = balls[:, 3]; rp = r / px
    depth = np.full((H, W), np.inf); nu = np.zeros((H, W), np.float32); nv = np.zeros((H, W), np.float32)
    order = np.argsort(-r); small = rp[order] < 2.0; n_big = int((~small).sum())
    for a in order[:n_big]:
        j0, j1 = max(int(np.floor(u[a] - rp[a])), 0), min(int(np.ceil(u[a] + rp[a])) + 1, W)
        i0, i1 = max(int(np.floor(v[a] - rp[a])), 0), min(int(np.ceil(v[a] + rp[a])) + 1, H)
        if j0 >= j1 or i0 >= i1:
            continue
        du = (np.arange(j0, j1) - u[a])[None] / rp[a]; dv = (np.arange(i0, i1) - v[a])[:, None] / rp[a]; q = 1 - du * du - dv * dv
        m = q > 0; dd = d[a] - r[a] * np.sqrt(np.where(m, q, 0)); sub = depth[i0:i1, j0:j1]; m &= dd < sub
        sub[m] = dd[m]; nu[i0:i1, j0:j1][m] = np.broadcast_to(du, m.shape)[m]; nv[i0:i1, j0:j1][m] = np.broadcast_to(-dv, m.shape)[m]
    sm = order[n_big:]
    if sm.size:
        for oi in (-2, -1, 0, 1, 2):
            for oj in (-2, -1, 0, 1, 2):
                jj = np.round(u[sm]).astype(int) + oj; ii = np.round(v[sm]).astype(int) + oi
                du = (jj - u[sm]) / rp[sm]; dv = (ii - v[sm]) / rp[sm]; q = 1 - du * du - dv * dv
                m = (q > 0) & (jj >= 0) & (jj < W) & (ii >= 0) & (ii < H)
                if not m.any():
                    continue
                dd = d[sm][m] - r[sm][m] * np.sqrt(q[m]); lin = ii[m] * W + jj[m]
                o2 = np.argsort(dd); lin, dd, du2, dv2 = lin[o2], dd[o2], du[m][o2], dv[m][o2]
                lin, first = np.unique(lin, return_index=True); dd, du2, dv2 = dd[first], du2[first], dv2[first]
                fd = depth.ravel(); better = dd < fd[lin]; lin = lin[better]
                fd[lin] = dd[better]; nu.ravel()[lin] = du2[better]; nv.ravel()[lin] = -dv2[better]
    return depth, nu, nv, px, ss


def shade(depth, nu, nv, px, ss=2, tint=(238, 226, 196), bg=(14, 17, 26), shadow=True):
    hit = np.isfinite(depth); nd = -np.sqrt(np.clip(1 - nu * nu - nv * nv, 0, 1))
    light = np.array([-0.45, 0.6, -0.66]); light /= np.linalg.norm(light)
    lam = np.clip(nu * light[0] + nv * light[1] + nd * light[2], 0, 1)
    dm = np.where(hit, depth, 0.0); rng = float(np.ptp(dm[hit])) if hit.any() else 1.0; near = np.clip((dm[hit].max() - dm) / max(rng, 1e-9), 0, 1) if hit.any() else dm
    val = 0.16 + 0.72 * lam + 0.12 * near
    if shadow and hit.any():                                   # a soft darkening in the creases: where the surface lies deeper than its surroundings
        from scipy import ndimage
        far = dm[hit].max(); fill = np.where(hit, depth, far); blur = ndimage.uniform_filter(fill, size=int(9 * ss))
        val *= np.clip(1.0 - 2.2 * np.clip(fill - blur, 0, None) / max(rng, 1e-9), 0.55, 1.0)
    img = np.zeros(depth.shape + (3,), float); img[...] = bg
    img[hit] = np.clip(val[hit, None] * np.array(tint, float), 0, 255)
    H, W = depth.shape; img = img.reshape(H // ss, ss, W // ss, ss, 3).mean((1, 3))
    return img.astype(np.uint8)


def solid_img(balls, w, h, half_w=1.75, centre=(0.0, 0.0, 0.0), cam=(0.45, 0.5, 1.0), ss=2, tint=(238, 226, 196)):
    return shade(*splat(balls, w, h, half_w, centre, cam, ss), tint=tint)


def cut(balls, w, h, box, ang=0.0, ss=3):
    """The cut along the plane through the x-axis turned ang degrees from the flat plane (0 = the flat cut z = 0).
    Returns the share of each pixel that is inside (0..1). box = (x0, x1, y0, y1)."""
    a = np.radians(ang); cy = balls[:, 1] * np.cos(a) + balls[:, 2] * np.sin(a); cz = -balls[:, 1] * np.sin(a) + balls[:, 2] * np.cos(a)
    m = np.abs(cz) < balls[:, 3]; discs = np.column_stack([balls[m, 0], cy[m], np.sqrt(balls[m, 3] ** 2 - cz[m] ** 2)])
    return discs_cov(discs, w, h, box, ss)


def discs_cov(discs, w, h, box, ss=3):
    W, H = w * ss, h * ss; px = (box[1] - box[0]) / W; py = (box[3] - box[2]) / H
    u = (discs[:, 0] - box[0]) / px - 0.5; v = (box[3] - discs[:, 1]) / py - 0.5; rp = discs[:, 2] / px
    msk = np.zeros((H, W), bool); order = np.argsort(-rp)
    for a in order:
        if rp[a] < 0.5:
            break
        j0, j1 = max(int(np.floor(u[a] - rp[a])), 0), min(int(np.ceil(u[a] + rp[a])) + 1, W)
        i0, i1 = max(int(np.floor(v[a] - rp[a])), 0), min(int(np.ceil(v[a] + rp[a])) + 1, H)
        if j0 >= j1 or i0 >= i1:
            continue
        du = (np.arange(j0, j1) - u[a])[None]; dv = (np.arange(i0, i1) - v[a])[:, None] * (py / px)
        msk[i0:i1, j0:j1] |= du * du + dv * dv < rp[a] ** 2
    return msk.reshape(h, ss, w, ss).mean((1, 3))


# ---------------------------------------------------------------- the true flat picture
def julia(u, s, cr, ci, steps=600, r2=36.0):
    """True flat picture of z^2 + c: True where the orbit has not left after `steps`. Same test as mem.flat_stay, but
    orbits that have left are dropped, so many steps are affordable."""
    sh = np.shape(u); zr = np.array(u, float).ravel(); zi = np.array(np.broadcast_to(s, sh), float).ravel()
    ins = np.ones(zr.size, bool); idx = np.arange(zr.size)
    for k in range(steps):
        zr, zi = zr * zr - zi * zi + cr, 2 * zr * zi + ci
        keep = zr * zr + zi * zi < r2
        if not keep.all():
            ins[idx[~keep]] = False; idx, zr, zi = idx[keep], zr[keep], zi[keep]
        if idx.size == 0:
            break
    return ins.reshape(sh)


def julia_cov(cr, ci, w, h, box, steps=600, ss=3):
    W, H = w * ss, h * ss; px = (box[1] - box[0]) / W; py = (box[3] - box[2]) / H
    u, s = np.meshgrid(box[0] + (np.arange(W) + 0.5) * px, box[3] - (np.arange(H) + 0.5) * py)
    return julia(u, s, cr, ci, steps).reshape(h, ss, w, ss).mean((1, 3))


def font(sz):
    return M.font(sz)


def paint(cov, fg=(238, 228, 200), bg=(22, 28, 44)):
    c = np.clip(cov, 0, 1)[..., None]
    return (np.array(bg, float) * (1 - c) + np.array(fg, float) * c).astype(np.uint8)


def overlay(cov_obj, cov_true, edge=True):
    """Two shapes in one picture: both = pale, only the object = orange, only the true picture = blue. With the true
    picture's outline drawn in white on top."""
    a = np.clip(cov_obj, 0, 1); b = np.clip(cov_true, 0, 1); both = np.minimum(a, b); oa = a - both; ob = b - both
    img = np.zeros(a.shape + (3,), float); img[...] = (16, 19, 30)
    for wgt, col in ((both, (226, 220, 200)), (oa, (236, 138, 52)), (ob, (72, 146, 240))):
        img = img * (1 - wgt[..., None]) + np.array(col, float) * wgt[..., None]
    if edge:
        t = b > 0.5; e = t ^ (np.roll(t, 1, 0) & np.roll(t, -1, 0) & np.roll(t, 1, 1) & np.roll(t, -1, 1) & t)
        img[e & t] = (255, 255, 255)
    return img.astype(np.uint8)
