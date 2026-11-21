"""A model of the lab's Kleinian view, independent of the shader, used to choose and check presets.

The group (lab notation, q = x + yi + zj):
    A: q -> mu + J(q),  J(q) = (x, -y, -z) / |q|^2        ("mu + 1/q")
    B: q -> q + 2
    C: q -> q + 2L j                                        (the third map, optional)
The solid the lab draws is the union of the "pearls": every image of the two wall half-spaces
{y < 0} and {y > my} under the group.

Three tools:

1. pearls(...)   lists the pearls directly, by applying A and A^-1 to every known pearl and its
   translates until nothing larger than `eps` is new. Spheres are kept as vectors of R^(4,1), on which
   every map above is linear, so there are no special cases for planes.
   From the list: `overlap` (do two pearls cut into each other? then the picture is dust), and the
   list itself (for framing: gaps(...) finds the empty balls between the pearls).
   The list fills in slowly near long cusps such as 1/15 (a chain is only followed while every pearl on
   the way is larger than eps), so treat distances taken from it as upper bounds.

2. kde(...)      a line-by-line port of the shader's distance estimate (GL_KLEIN in 30-shaders.js).
   The shader can only err one way about what is solid: every map it applies sends pearls to pearls, so a
   point it calls solid is solid. But its rule for choosing a map is a fitted curve, and where the curve is
   wrong it misses solid points. missed(...) measures that against the pearl list.

3. kde_exact(...)  the same search with the true distance to each pearl it meets: a proposal for the
   shader, written out as GLSL in notes/klein-kde-exact.glsl.

Run this file for a self-check on the lab's starting group.
"""
import math
import numpy as np


# ---------- spheres as vectors of R^(4,1); a point x is inside the oriented sphere v when <v, X(x)> > 0
def form(u, v):
    return (u[..., :4] * v[..., :4]).sum(-1) - u[..., 4] * v[..., 4]


def tr(v, t):
    """translate by the vector t (works on arrays of sphere vectors, t broadcastable to (..., 3))"""
    t = np.asarray(t, float)
    w = (v[..., 4] - v[..., 3])[..., None]
    x = v[..., :3]
    s = (t * x).sum(-1) + 0.5 * (t * t).sum(-1) * w[..., 0]
    out = np.empty(np.broadcast_shapes(v.shape, t.shape[:-1] + (5,)))
    out[..., :3] = x + t * w
    out[..., 3] = v[..., 3] + s
    out[..., 4] = v[..., 4] + s
    return out


def J(v):
    return v * np.array([1.0, -1.0, -1.0, -1.0, 1.0])


def wall_vectors(my):
    return np.array([[0.0, -1.0, 0.0, 0.0, 0.0],      # {y < 0}
                     [0.0, 1.0, 0.0, my, my]])        # {y > my}


def to_ball(v):
    """centre (n,3) and radius (n,) of sphere vectors that are balls"""
    w = v[..., 4] - v[..., 3]
    return v[..., :3] / w[..., None], 1.0 / w


def pearls(mu, L=1.0, three=True, eps=0.01, max_pearls=150000, rounds=200, stop_at=None):
    """Return dict(c, r, overlap, complete). c, r: the pearls (balls) with radius >= eps whose centres lie in
    the cell x in [-1, 1), z in [-L, L) (z unrestricted without the third map). overlap: the largest
    amount by which a pearl sticks out of the slab between the walls, as a fraction of its radius
    (0 for a clean group; pearls cut into each other exactly when one cuts into a wall).
    stop_at: give up as soon as the overlap exceeds this (a group that is dust has endlessly many pearls)."""
    mu = np.asarray(mu, float)
    my = mu[1]
    walls = wall_vectors(my)
    seen = set()
    cs, rs = [], []
    overlap = 0.0

    def shifts_for(rmax):
        # J shrinks a ball of radius r at distance D to r / (D^2 - r^2): translates farther than this give nothing >= eps
        reach = math.sqrt(rmax / eps + rmax * rmax) + 1.0
        kx = int(math.ceil(reach / 2.0)); ks = np.arange(-kx, kx + 1)
        if not three:
            return np.array([[2.0 * k, 0.0, 0.0] for k in ks])
        kz = int(math.ceil(reach / (2.0 * L))); ms = np.arange(-kz, kz + 1)
        sh = np.array([[2.0 * k, 0.0, 2.0 * L * m] for k in ks for m in ms])
        return sh[np.hypot(sh[:, 0], sh[:, 2]) <= reach + 2.0]

    def step(src):
        # src: (n, T, 5) sphere vectors. Returns their images under A and A^-1.
        a = tr(J(src), mu)
        b = J(tr(src, -mu))
        return np.concatenate([a.reshape(-1, 5), b.reshape(-1, 5)])

    front = step(walls[:, None, :])
    complete = True
    for _ in range(rounds):
        if len(front) == 0:
            break
        w = front[:, 4] - front[:, 3]
        # a wall again (w = 0, and it is one of the two walls)?  skip it
        is_wall = (np.abs(w) < 1e-9) & ((np.abs(front - walls[0]).max(1) < 1e-7) | (np.abs(front - walls[1]).max(1) < 1e-7))
        front = front[~is_wall]; w = w[~is_wall]
        bad = w <= 1e-9          # a half-space that is not a wall, or the outside of a ball: pearls collide
        if bad.any():
            overlap = max(overlap, 2.0)
        front = front[~bad]; w = w[~bad]
        c, r = to_ball(front)
        keep = r >= eps
        front, c, r = front[keep], c[keep], r[keep]
        if len(front) == 0:
            break
        out = np.maximum(r - c[:, 1], c[:, 1] + r - my) / r     # > 0: sticks out of the slab
        overlap = max(overlap, float(out.max()))
        if stop_at is not None and overlap > stop_at:
            complete = False
            break
        # move into the cell
        sh = np.zeros_like(c)
        sh[:, 0] = -2.0 * np.floor((c[:, 0] + 1.0) / 2.0)
        if three:
            sh[:, 2] = -2.0 * L * np.floor((c[:, 2] + L) / (2.0 * L))
        front = tr(front, sh); c = c + sh
        keys = np.round(np.concatenate([c, r[:, None]], 1) * 1e5).astype(np.int64)
        new = []
        for i, k in enumerate(map(tuple, keys)):
            if k not in seen:
                seen.add(k); new.append(i)
        if not new:
            break
        new = np.array(new)
        cs.append(c[new]); rs.append(r[new])
        if len(seen) > max_pearls:
            complete = False
            break
        # bigger pearls reach farther, so give each size class its own set of translates
        nf, nr = front[new], r[new]
        parts = []
        cls = np.floor(np.log2(nr / eps)).astype(int)
        for k in np.unique(cls):
            sel = cls == k
            sh = shifts_for(eps * 2.0 ** (k + 1))
            parts.append(step(tr(nf[sel][:, None, :], sh[None, :, :])))
        front = np.concatenate(parts)
    else:
        complete = False
    c = np.concatenate(cs) if cs else np.zeros((0, 3))
    r = np.concatenate(rs) if rs else np.zeros(0)
    return dict(c=c, r=r, overlap=overlap, complete=complete)


# ---------- the shader's estimate, ported (GL_KLEIN in src/js/30-shaders.js)
def kde(z, mu, L=1.0, three=True, iters=60):
    """z: (n, 3) points of the slab. Returns (estimate, steps). estimate <= 0 means solid."""
    z = np.array(z, float)
    mu = np.asarray(mu, float)
    a = mu[1]
    fs = np.sign(-mu[0])
    sx, sz = mu[0] / a, mu[2] / a
    n = len(z)
    DF = np.ones(n)
    best = np.minimum(z[:, 1], a - z[:, 1])
    lz = z + 1.0
    llz = z - 1.0
    live = np.ones(n, bool)
    steps = np.zeros(n)
    wrap = lambda x, per, s: (x - s) - per * np.floor((x - s) / per) + s
    for _ in range(iters):
        if not live.any():
            break
        q = z[live]
        q[:, 0] -= sx * q[:, 1]; q[:, 0] = wrap(q[:, 0], 2.0, -1.0); q[:, 0] += sx * q[:, 1]
        if three:
            q[:, 2] -= sz * q[:, 1]; q[:, 2] = wrap(q[:, 2], 2.0 * L, -L); q[:, 2] += sz * q[:, 1]
        xs = q[:, 0] - 0.5 * mu[0]
        with np.errstate(over='ignore', invalid='ignore'):
            line = a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * np.sign(xs) * (1.0 - np.exp(-(7.2 - (1.95 - a) * 15.0) * np.abs(xs)))
        up = q[:, 1] >= line
        q[up] = mu - q[up]
        iR = 1.0 / np.maximum((q * q).sum(1), 1e-20)
        q = mu + q * np.array([1.0, -1.0, -1.0]) * iR[:, None]
        z[live] = q
        DF[live] *= iR
        steps[live] += 1
        best[live] = np.minimum(best[live], np.minimum(q[:, 1], a - q[:, 1]) / np.maximum(DF[live], 1.0))
        done = ((q - llz[live]) ** 2).sum(1) < 1e-5
        idx = np.flatnonzero(live)
        llz[idx] = lz[idx]; lz[idx] = q
        live[idx[done]] = False
    return np.minimum(best, 0.3), steps


def de_display(p, k):
    """The distance estimate in the picture's own space, after the turning-out sphere. k: dict like S.k."""
    p = np.array(p, float)
    mu = np.array([k['mx'], k['my'], k['mz']])
    C = np.array([k['cx'], k['cy'], k['cz']])
    R2 = k['invR'] ** 2
    r2 = np.maximum((p * p).sum(1), 1e-12)
    r = np.sqrt(r2)
    q = C + (R2 / r2)[:, None] * p
    d = np.zeros(len(p))
    inside = (q[:, 1] < 0) | (q[:, 1] > mu[1])
    if (~inside).any():
        dd, _ = kde(q[~inside], mu, k['L'], k['three'], k['iter'])
        d[~inside] = dd
    out = r2 * d / (R2 + r * d)
    out[inside] = 0.0
    return out


def tiles(P, L, three, K=1):
    """the pearls of the cell together with their neighbours K cells away"""
    ks = np.arange(-K, K + 1)
    sh = np.array([[2.0 * k, 0.0, 2.0 * L * m] for k in ks for m in (ks if three else [0])])
    c = (P['c'][None, :, :] + sh[:, None, :]).reshape(-1, 3)
    r = np.tile(P['r'], len(sh))
    return c, r


def in_pearl(pts, c, r, chunk=4000):
    """is each point inside one of the balls (c, r)?"""
    out = np.zeros(len(pts), bool)
    for i in range(0, len(c), chunk):
        d2 = ((pts[:, None, :] - c[None, i:i + chunk, :]) ** 2).sum(-1)
        out |= (d2 < (r[None, i:i + chunk] * 0.999) ** 2).any(1)
    return out


def missed(mu, L=1.0, three=True, iters=60, n=20000, P=None, rmin=0.03, seed=3):
    """Share of the volume of the larger pearls that the shader's estimate fails to call solid."""
    mu = np.asarray(mu, float)
    if P is None:
        P = pearls(mu, L, three, eps=rmin)
    rng = np.random.default_rng(seed)
    zr = L if three else 0.6
    pts = np.column_stack([rng.uniform(-1, 1, n), rng.uniform(0, mu[1], n), rng.uniform(-zr, zr, n)])
    big = P['r'] >= rmin
    c, r = tiles(dict(c=P['c'][big], r=P['r'][big]), L, three)
    truth = in_pearl(pts, c, r)
    est, _ = kde(pts, mu, L, three, iters)
    solid = est <= 0
    miss = truth & ~solid
    return dict(share=float(miss.sum()) / max(1, int(truth.sum())), solid_truth=float(truth.mean()), solid_shader=float(solid.mean()),
                false_solid=int((solid & ~truth).sum()))


def clearance(pts, c, r, chunk=4000):
    """distance from each point to the nearest ball surface (negative inside a ball)"""
    out = np.full(len(pts), np.inf)
    for i in range(0, len(c), chunk):
        d = np.sqrt(((pts[:, None, :] - c[None, i:i + chunk, :]) ** 2).sum(-1)) - r[None, i:i + chunk]
        out = np.minimum(out, d.min(1))
    return out


def gaps(mu, L=1.0, three=True, P=None, grid=33, top=8, plane=False, min_clear=0.06, rmin=0.015, apart=0.2):
    """Centres of empty balls in one cell (local maxima of the distance to the nearest pearl or wall):
    candidates for the centre of the turning-out sphere. plane=True searches the plane z = 0 only.
    Returns [(clearance, [x, y, z])], roomiest first."""
    mu = np.asarray(mu, float)
    if P is None:
        P = pearls(mu, L, three, eps=0.01)
    big = P['r'] >= rmin      # small pearls barely move the answer and cost most of the time
    c, r = tiles(dict(c=P['c'][big], r=P['r'][big]), L, three)
    a = mu[1]
    zr = L if three else 1.0
    xs = np.linspace(-1, 1, grid, endpoint=False)
    ys = np.linspace(0, a, grid + 1)[1:-1]
    zs = np.array([0.0]) if plane else np.linspace(-zr, zr, grid, endpoint=False)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    pts = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    f = lambda q: np.minimum(clearance(q, c, r), np.minimum(q[:, 1], a - q[:, 1]))
    cl = f(pts).reshape(X.shape)
    # local maxima of the grid (periodic in x, and in z with the third map)
    peak = cl > min_clear * 0.5
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in ((0,) if plane else (-1, 0, 1)):
                if dx == dy == dz == 0:
                    continue
                sh = np.roll(cl, (dx, dz), axis=(0, 2))
                if dy:
                    sh = np.roll(sh, dy, axis=1)
                    if dy == 1: sh[0] = -1
                    else: sh[-1] = -1
                peak &= cl >= sh
    cand = np.column_stack([X[peak], Y[peak], Z[peak]])
    out = []
    h0 = 2.0 / grid
    for p in cand:
        h = h0; best = float(f(p[None])[0])
        for _ in range(8):
            d = np.array([[i, j, k] for i in (-1, 0, 1) for j in (-1, 0, 1) for k in ((0,) if plane else (-1, 0, 1))]) * h
            q = p + d
            cc = f(q)
            j = int(np.argmax(cc)); p, best = q[j], float(cc[j]); h *= 0.6
        p = p.copy(); p[0] = (p[0] + 1) % 2 - 1
        if three and not plane: p[2] = (p[2] + L) % (2 * L) - L
        if best >= min_clear and all(np.linalg.norm(p - np.array(o[1])) > apart for o in out):
            out.append((best, [round(float(v), 4) for v in p]))
    out.sort(key=lambda t: -t[0])
    keep = []
    for o in out:             # the refinement can walk two starts to the same peak
        if all(np.linalg.norm(np.array(o[1]) - np.array(k[1])) > apart for k in keep):
            keep.append(o)
    return keep[:top]


def display_extent(k, P=None):
    """Bounding box and bounding radius (about the origin) of the turned-out picture, from the pearl list."""
    mu = np.array([k['mx'], k['my'], k['mz']])
    C = np.array([k['cx'], k['cy'], k['cz']])
    R2 = k['invR'] ** 2
    if P is None:
        P = pearls(mu, k['L'], k['three'], eps=0.02)
    c, r = tiles(P, k['L'], k['three'], K=2)
    d = c - C
    den = (d * d).sum(1) - r * r
    ok = den > 1e-9
    cc = R2 * d[ok] / den[ok][:, None]
    rr = R2 * r[ok] / den[ok]
    # the two walls
    cy, a = C[1], mu[1]
    cc = np.vstack([cc, [0, -R2 / (2 * cy), 0], [0, R2 / (2 * (a - cy)), 0]])
    rr = np.concatenate([rr, [R2 / (2 * cy), R2 / (2 * (a - cy))]])
    lo = (cc - rr[:, None]).min(0); hi = (cc + rr[:, None]).max(0)
    rad = float((np.linalg.norm(cc, axis=1) + rr).max())
    return dict(lo=lo, hi=hi, radius=rad, inside_pearl=bool((~ok).any()))


if __name__ == "__main__":
    # self-checks
    w = wall_vectors(2.0)
    mu = np.array([0.0, 2.0, 0.0])
    assert np.allclose(tr(J(w[0]), mu), w[1]), "A must carry the lower wall onto the upper wall"
    v = tr(J(w[1]), mu)                 # A(upper wall): a pearl of diameter 1/my hanging from the upper wall at mu
    c, r = to_ball(v)
    assert np.allclose(c, [0, 2 - 0.25, 0]) and abs(r - 0.25) < 1e-12, (c, r)
    P = pearls(mu, 1.0, True, eps=0.02)
    print("default group: %d pearls >= 0.02 in a cell, overlap %.2e, complete %s" % (len(P['r']), P['overlap'], P['complete']))
    print("shader misses", missed(mu, 1.0, True, P=P))
    print("gaps in the plane z = 0:", gaps(mu, 1.0, True, P=P, plane=True)[:3])


# ---------- a proposal for the shader: the same search, but with the exact distance to each pearl it meets
def kde_exact(z, mu, L=1.0, three=True, iters=60):
    """Like kde(), with one more point carried along: W, the image of the point at infinity (where the two
    walls touch). The pearl met at a step is the sphere that the maps so far carry onto a wall; its radius is
    rho = |z - W|^2 / (2 D DF), D being the distance from W to that wall, and the true distance to it is
        t = E * 2 / (1 + sqrt(1 + 2 E / rho)),   E = (distance from z to the wall) / DF,
    where the shader uses E itself. E equals t (1 + t / (2 rho)): right next to the pearl, far too big away from it."""
    z = np.array(z, float)
    mu = np.asarray(mu, float)
    a = mu[1]
    fs = np.sign(-mu[0])
    sx, sz = mu[0] / a, mu[2] / a
    n = len(z)
    DF = np.ones(n)
    best = np.minimum(z[:, 1], a - z[:, 1])
    W = np.full((n, 3), 1e6)
    lz = z + 1.0
    llz = z - 1.0
    live = np.ones(n, bool)
    wrap = lambda x, per, s: (x - s) - per * np.floor((x - s) / per) + s
    flipv = np.array([1.0, -1.0, -1.0])
    for _ in range(iters):
        if not live.any():
            break
        q = z[live]; w = W[live]
        x0 = q[:, 0].copy()
        q[:, 0] -= sx * q[:, 1]; q[:, 0] = wrap(q[:, 0], 2.0, -1.0); q[:, 0] += sx * q[:, 1]
        w[:, 0] += q[:, 0] - x0
        if three:
            z0 = q[:, 2].copy()
            q[:, 2] -= sz * q[:, 1]; q[:, 2] = wrap(q[:, 2], 2.0 * L, -L); q[:, 2] += sz * q[:, 1]
            w[:, 2] += q[:, 2] - z0
        xs = q[:, 0] - 0.5 * mu[0]
        with np.errstate(over='ignore', invalid='ignore'):
            line = a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * np.sign(xs) * (1.0 - np.exp(-(7.2 - (1.95 - a) * 15.0) * np.abs(xs)))
        up = q[:, 1] >= line
        q[up] = mu - q[up]; w[up] = mu - w[up]
        iR = 1.0 / np.maximum((q * q).sum(1), 1e-20)
        q = mu + q * flipv * iR[:, None]
        w = mu + w * flipv / np.maximum((w * w).sum(1), 1e-20)[:, None]
        z[live] = q; W[live] = w
        DF[live] *= iR
        df = DF[live]
        zw2 = np.maximum(((q - w) ** 2).sum(1), 1e-30)
        cand = np.full(len(q), np.inf)
        for h, D in ((q[:, 1], w[:, 1]), (a - q[:, 1], a - w[:, 1])):
            E = h / df
            t = np.where(h > 0, E * 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * np.maximum(h, 0) * np.maximum(D, 0) / zw2)), E)
            cand = np.minimum(cand, t)
        best[live] = np.minimum(best[live], cand)
        done = ((q - llz[live]) ** 2).sum(1) < 1e-5
        idx = np.flatnonzero(live)
        llz[idx] = lz[idx]; lz[idx] = q
        live[idx[done]] = False
    return best
