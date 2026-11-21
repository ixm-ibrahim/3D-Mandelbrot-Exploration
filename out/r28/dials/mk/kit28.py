"""Round 28, Track A, builder: the object of ROUND28.md section 1.1 in plain numpy, with the new number rho.

Nothing here is taken from the page: it is a separate writing, for checking the page against.

  recipe(x, y, z, t, rho, grid, rounds)   the recipe of section 1.1 at picture points: 1 inside, 0 outside, -1 undecided
  recipe_m(mx, my, mz, top, rho, grid, rounds)   the same in the object's own coordinates
  cell_balls(top, rho, grid, rmin)        the LIST OF BALLS of one cell: (A1, A2), the balls inside the first sphere
                                          and inside the second sphere at the whole number 0, each (N, 4) = centre, radius
  picture_balls(A1, A2, grid, rpic)       the same balls and their slid copies in picture coordinates, radius >= rpic,
                                          with the two walls (middle ball, right neighbour) first
  hulls(top, rho)                         the numbers of section 1.3: z1, z2, H_B, H_T, zm, delta^2
  estimate(x, y, z, t, rho, grid, rounds) the distance of section 1.3, written out in numpy (two numbers: best, free)

grid: 0 square, 1 honeycomb, 2 a line only.
"""
import numpy as np

K2 = 1.05
S3 = np.sqrt(3.0)


def rnd(v):
    return np.floor(np.asarray(v, float) + 0.5)          # JavaScript's Math.round


def near(grid, x, y):
    """The whole number of the grid nearest to (x, y)."""
    if grid == 2:
        return rnd(x), np.zeros_like(np.asarray(x, float))
    if grid == 0:
        return rnd(x), rnd(y)
    b0 = rnd(y / (S3 / 2)); bx = np.zeros_like(x); by = np.zeros_like(x); bd = np.full(np.shape(x), np.inf)
    for j in (-1, 0, 1):
        b = b0 + j; a = rnd(x + b / 2); px = a - b / 2; py = b * S3 / 2; d = (x - px) ** 2 + (y - py) ** 2
        m = d < bd; bx = np.where(m, px, bx); by = np.where(m, py, by); bd = np.where(m, d, bd)
    return bx, by


def to_model(x, y, z):
    ux, uy, uz = np.asarray(y, float), np.asarray(z, float), np.asarray(x, float) - K2 / 2
    d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    return K2 * ux / d, K2 * uy / d, 1 + K2 * uz / d


def recipe_m(mx, my, mz, top, rho, grid, rounds):
    mx = np.array(mx, float); my = np.array(my, float); mz = np.array(mz, float)
    state = np.full(mx.shape, -1, int)
    for _ in range(rounds):
        live = state < 0
        if not live.any():
            break
        state = np.where(live & ((mz < 0) | (mz > top)), 1, state); live = state < 0
        nx, ny = near(grid, mx, my); mx = mx - nx; my = my - ny
        rb = mx * mx + my * my + mz * mz; rt = mx * mx + my * my + (mz - top) ** 2
        inb = live & (rb < 1); itp = live & ~inb & (rt < rho * rho)
        state = np.where(live & ~inb & ~itp, 0, state)
        sb = 1 / np.where(rb > 0, rb, 1.0); st = rho * rho / np.where(rt > 0, rt, 1.0)
        mx, my, mz = (np.where(inb, mx * sb, np.where(itp, mx * st, mx)), np.where(inb, my * sb, np.where(itp, my * st, my)),
                      np.where(inb, mz * sb, np.where(itp, top + (mz - top) * st, mz)))
    return state


def recipe(x, y, z, t, rho, grid, rounds):
    return recipe_m(*to_model(x, y, z), 2 * t, rho, grid, rounds)


# ------------------------------------------------------------------ the list of balls
def lat(grid, a, b):
    if grid == 0:
        return a, b
    if grid == 1:
        return a - b / 2.0, b * S3 / 2
    return a, np.zeros_like(a)


def lat_coef(grid, x, y):
    if grid == 0:
        return rnd(x), rnd(y)
    if grid == 1:
        b = rnd(y / (S3 / 2)); return rnd(x + b / 2), b
    return rnd(x), np.zeros_like(x)


def slid_images(C, o, R2, grid, rmin, outside_only=False, chunk=2_000_000):
    """C (N, 4): balls. Every slid copy C + n (n a whole number of the grid) is carried by the sphere inversion about o
    with radius^2 R2; those of radius >= rmin are returned, as (M, 4). outside_only: only the copies that lie outside
    that sphere are carried (a copy inside it, or one the sphere cuts squarely, is left alone)."""
    out = []
    if len(C) == 0:
        return np.zeros((0, 4))
    c = C[:, :3]; r = C[:, 3]; Rs = np.sqrt(R2)
    dz = c[:, 2] - o[2]
    Rn2 = R2 * r / rmin + r * r - dz * dz                 # |c_xy + n - o_xy|^2 must be at most this
    ok = np.nonzero(Rn2 >= 0)[0]
    Rn = np.sqrt(np.maximum(Rn2, 0))
    Kk = (np.ceil(Rn * (1.16 if grid == 1 else 1.0)) + 1).astype(int)
    for kv in np.unique(Kk[ok]):
        sel = ok[Kk[ok] == kv]; off = np.arange(-kv, kv + 1)
        if grid == 2:
            da = off; db = np.zeros_like(off)
        else:
            da, db = np.meshgrid(off, off); da = da.ravel(); db = db.ravel()
        step = max(1, chunk // da.size)
        for s in range(0, sel.size, step):
            ii = sel[s:s + step]
            a0, b0 = lat_coef(grid, o[0] - c[ii, 0], o[1] - c[ii, 1])
            A = a0[:, None] + da[None]; B = b0[:, None] + db[None]
            nx, ny = lat(grid, A, B)
            dx = c[ii, 0, None] + nx - o[0]; dy = c[ii, 1, None] + ny - o[1]; dzz = np.broadcast_to(dz[ii, None], dx.shape)
            dd = dx * dx + dy * dy + dzz * dzz
            den = dd - (r[ii, None] ** 2)
            rr = R2 * r[ii, None] / np.where(den > 1e-300, den, 1e-300)
            keep = (den > 0) & (rr >= rmin)
            if outside_only:
                keep &= np.sqrt(dd) - r[ii, None] >= Rs - 1e-9
            f = R2 / den[keep]
            out.append(np.column_stack([o[0] + dx[keep] * f, o[1] + dy[keep] * f, o[2] + dzz[keep] * f, rr[keep]]))
    return np.concatenate(out) if out else np.zeros((0, 4))


def canon(B, grid):
    """Each ball slid so that its centre lies in the middle cell; the same ball met twice is kept once."""
    if len(B) == 0:
        return B
    nx, ny = near(grid, B[:, 0] + 1e-9, B[:, 1] + 1.3e-9)
    B = B.copy(); B[:, 0] -= nx; B[:, 1] -= ny
    key = np.round(B / 1e-7).astype(np.int64)
    _, idx = np.unique(key, axis=0, return_index=True)
    return B[np.sort(idx)]


def cell_balls(top, rho, grid, rmin, maxgen=400, cap=3_000_000, verbose=False):
    """The LIST OF BALLS, one for every family of slid copies, centre in the middle cell, radius >= rmin:
    (A1, A2) = the ones inside the first sphere, the ones inside the second sphere (at the whole number 0).
    A ball inside a sphere is the image, by that sphere's inversion, of a larger ball outside it (a wall, or a slid
    copy of a listed ball); so the list grows from the two walls downwards in size and cutting at rmin loses nothing."""
    o1 = np.zeros(3); o2 = np.array([0.0, 0.0, top]); R1 = 1.0; R2 = rho * rho
    F1 = np.array([[0.0, 0.0, 1 / (2 * top), 1 / (2 * top)]]); F2 = np.array([[0.0, 0.0, top - R2 / (2 * top), R2 / (2 * top)]])
    A1 = [F1]; A2 = [F2]; n = 2
    for g in range(maxgen):
        F = np.concatenate([F1, F2])
        N1 = canon(slid_images(F, o1, R1, grid, rmin, True), grid)
        N2 = canon(slid_images(F, o2, R2, grid, rmin, True), grid)
        # only the copies whose centre is in the middle cell are new members (the others are slid copies of members)
        def mine(N, o, Rr):
            if len(N) == 0:
                return N
            d = np.sqrt(((N[:, :3] - o) ** 2).sum(1)) + N[:, 3]
            return N[d <= Rr + 1e-9]
        N1 = mine(N1, o1, 1.0); N2 = mine(N2, o2, rho)
        if verbose:
            print('  generation %d: %d + %d new balls' % (g + 1, len(N1), len(N2)))
        if len(N1) + len(N2) == 0:
            break
        A1.append(N1); A2.append(N2); F1, F2 = N1, N2; n += len(N1) + len(N2)
        if n > cap:
            raise RuntimeError('more than %d balls: raise rmin' % cap)
    return canon(np.concatenate(A1), grid), canon(np.concatenate(A2), grid)


def picture_balls(A1, A2, grid, rpic, top, extra=None):
    """Every ball of the picture with radius >= rpic: the two walls first (the middle ball, the right neighbour), then
    the slid copies of the cell's balls carried by the frame inversion (centre (0, 0, 1), k^2 = 1.05)."""
    o = np.array([0.0, 0.0, 1.0])
    B = slid_images(np.concatenate([A1, A2]), o, K2, grid, rpic)
    # object's own coordinates (u-frame after inversion: u = m' - (0,0,1)) -> picture: x = u_z + k^2/2, y = u_x, z = u_y
    P = np.column_stack([B[:, 2] - 1.0 + K2 / 2, B[:, 0], B[:, 1], B[:, 3]])
    walls = np.array([[0.0, 0.0, 0.0, K2 / 2], [K2 / 2 + K2 / (2 * (top - 1)), 0.0, 0.0, K2 / (2 * (top - 1))]])
    return np.concatenate([walls, P])


# ------------------------------------------------------------------ the numbers of section 1.3
def hulls(top, rho, brief=False):
    """z1, z2: the two fixed points on the middle line. HB, HT: the hull balls. zm, d2: the spindle's mid-height and
    delta^2. w: how far the spindle reaches from the middle line at mid-height; a, R: its circle (centre (a, zm) in the
    half-plane (distance from the line, height), radius R). brief=True: w = 1/2 always, as ROUND28.md section 1.3 has it."""
    gap = max(top - 1 - rho, 0.0)
    D = gap * (top - 1 + rho) / top                        # s - 2, written so that nothing large is taken from something large
    s = 2 + D; sq = np.sqrt(D * (D + 4))
    z2 = (s + sq) / 2; z1 = 1 / z2
    HB = z1; HT = rho * rho / (top - HB)
    zm = s / 2; d2 = D * (D + 4) / 4
    w = 0.5 if brief else min(0.5, top - zm + rho)
    return dict(z1=z1, z2=z2, HB=HB, HT=HT, zm=zm, d2=d2, s=s, w=w, a=(w * w - d2) / (2 * w), R=(w * w + d2) / (2 * w))


def rests(top, rho, grid):
    h = hulls(top, rho); f = (0.5, 1 / 3.0, 0.25)[grid]
    return f * h['HB'], (f * h['HT'] if rho == 1 else rho * rho * h['HT'])


def top_ball(top, rho, grid):
    """rho < 1: everything that grows on the top wall at the whole number 0, the whole-number hull apart, lies within
    this distance of the second sphere's centre (0, 0, top): the buds touch the wall no further than
    x = (1 - sqrt(1 - 4 rho^2)) / 2 from it (x = rho^2 / (1 - x)), each is at most the rest across, and all of it is
    inside the second sphere."""
    rT = rests(top, rho, grid)[1]
    xs = 2 * rho * rho / (1 + np.sqrt(max(1 - 4 * rho * rho, 0.0)))
    return min(rho, xs + rT)


def room_m(mx, my, mz, top, rho, grid, spindle=True, brief=False):
    """Section 1.3 at a point of the middle cell that the recipe has just called OUTSIDE: the radius of a ball round it
    that is certainly free of every ball other than the two walls (in the object's own coordinates)."""
    h = hulls(top, rho); HB, HT = h['HB'], h['HT']; rb, rt = rests(top, rho, grid)
    hb = mz; ht = top - mz
    cb = np.sqrt(mx * mx + my * my + (hb - HB / 2) ** 2) - HB / 2
    ct = np.sqrt(mx * mx + my * my + (ht - HT / 2) ** 2) - HT / 2
    lo = np.hypot(my, hb) if grid == 2 else hb
    hi = np.hypot(my, ht) if grid == 2 else ht
    hiR = hi - rt
    if rho < 1 and not brief:
        hiR = np.maximum(hiR, np.sqrt(mx * mx + my * my + ht * ht) - top_ball(top, rho, grid))
    e = np.maximum(np.minimum(np.minimum(cb, ct), np.minimum(lo - rb, hiR)), 0.0)
    if spindle:
        e = np.maximum(e, spindle_room(mx, my, mz, top, rho, brief))
    return e


def spindle_room(mx, my, mz, top, rho, brief=False):
    h = hulls(top, rho, brief); d2 = h['d2']; a = h['a']; r = np.hypot(mx, my); dz = mz - h['zm']
    return (d2 + r * (2 * a - r) - dz * dz) / (h['R'] + np.hypot(r - a, dz))


def pearl(h, D, kk):
    return np.where(h > 0, 2 * h / (1 + np.sqrt(1 + kk * np.maximum(h, 0) * np.maximum(D, 0))), h)


def estimate(x, y, z, t, rho, grid, rounds, spindle=True):
    """-> (best, free, state): the true distance to the nearest ball the search met; the length certainly free of balls
    (inf where the search ended inside a ball or undecided); state 1 inside, 0 outside, -1 undecided."""
    top = 2 * t
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    u = np.stack([y, z, x - K2 / 2]); d2 = np.maximum((u * u).sum(0), 1e-300)
    DF = K2 / d2; m = np.array([0.0, 0.0, 1.0])[:, None] + DF * u; W = np.zeros_like(m); W[2] = 1.0
    best = np.full(x.shape, 1e9); free = np.full(x.shape, np.inf); state = np.full(x.shape, -1, int)
    for _ in range(rounds):
        live = state < 0
        if not live.any():
            break
        nx, ny = near(grid, m[0], m[1])
        m = np.where(live, np.stack([m[0] - nx, m[1] - ny, m[2]]), m); W = np.where(live, np.stack([W[0] - nx, W[1] - ny, W[2]]), W)
        L2 = np.maximum(((m - W) ** 2).sum(0), 1e-300); kk = 4 / L2; hb = m[2]; ht = top - m[2]
        cand = np.minimum(pearl(hb, W[2], kk), pearl(ht, top - W[2], kk)) / DF
        best = np.where(live, np.minimum(best, cand), best)
        ins = live & ((hb < 0) | (ht < 0)); state = np.where(ins, 1, state); live = state < 0
        mt = m - np.array([0.0, 0.0, top])[:, None]; Wt = W - np.array([0.0, 0.0, top])[:, None]
        rb = (m * m).sum(0); rt = (mt * mt).sum(0)
        inb = live & (rb < 1); itp = live & ~inb & (rt < rho * rho); out = live & ~inb & ~itp
        if out.any():
            e = room_m(m[0], m[1], m[2], top, rho, grid, spindle); L = np.sqrt(L2)
            free = np.where(out, e * L / ((L + e) * DF), free); state = np.where(out, 0, state)
        sb = 1 / np.maximum(rb, 1e-300); st = rho * rho / np.maximum(rt, 1e-300)
        m1 = m * sb; W1 = W / np.maximum((W * W).sum(0), 1e-300)
        m2 = np.array([0.0, 0.0, top])[:, None] + mt * st; W2 = np.array([0.0, 0.0, top])[:, None] + rho * rho * Wt / np.maximum((Wt * Wt).sum(0), 1e-300)
        m = np.where(inb, m1, np.where(itp, m2, m)); W = np.where(inb, W1, np.where(itp, W2, W))
        DF = np.where(inb, DF * sb, np.where(itp, DF * st, DF))
    return best, free, state


def reach(top, rho):
    h = hulls(top, rho)
    return np.inf if h['HB'] >= 1 else K2 / 2 + K2 * h['HB'] / (1 - h['HB'])
