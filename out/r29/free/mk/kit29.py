"""Round 29, Track A, builder: the reference and the prototype, in numpy (no page).

  recipe(P, t, rho, grid, rounds)        the plain recipe of docs/ROUND29.md section 1, written here from that text:
                                         True where a picture point is INSIDE
  chain(P, t, rho, grid, rounds)         the recipe with what the distance needs carried along (best, m, W, DF)
  free_room(ch, t, rho, grid, parts)     the length that is certainly free, as GL_BALLS_FREE is to work it out
  estimate(P, ...)                       min(best, free), the prototype of the program's distance
  flat_truth(...) / box_truth(...)       the recipe alone on a fine grid and the true distance from it (a distance
                                         transform of the grid)
"""
import numpy as np
from scipy import ndimage

K2 = 1.05
ITN = 1.0
S3 = np.sqrt(3.0)


def t_of(p):
    return 1.4 if abs(p - 100 / 1.8) < 0.06 else 0.5 * (100.0 / p + 1)


def nearest(grid, x, y):
    if grid == 2:
        return np.round(x), np.zeros_like(y)
    if grid == 0:
        return np.round(x), np.round(y)
    b0 = np.round(y / (S3 / 2))
    best_x = np.zeros_like(x); best_y = np.zeros_like(y); bd = np.full(x.shape, np.inf)
    for j in (-1, 0, 1):
        b = b0 + j; a = np.round(x + b / 2); px = a - b / 2; py = b * S3 / 2
        d = (x - px) ** 2 + (y - py) ** 2
        k = d < bd
        bd = np.where(k, d, bd); best_x = np.where(k, px, best_x); best_y = np.where(k, py, best_y)
    return best_x, best_y


def to_m(P):
    P = np.asarray(P, float)
    u = np.stack([P[:, 1], P[:, 2], P[:, 0] - K2 / 2], 1)
    d = np.maximum((u * u).sum(1), 1e-300)
    DF = K2 / d
    m = u * DF[:, None]; m[:, 2] += 1
    return m, DF


def recipe_m(m, top, rho, grid, rounds):
    """The plain recipe from a point of the object's own space. Returns INSIDE (bool)."""
    m = np.array(m, float)
    n = len(m); inside = np.zeros(n, bool); live = np.ones(n, bool)
    for _ in range(rounds):
        if not live.any():
            break
        idx = np.nonzero(live)[0]
        q = m[idx]
        wall = (q[:, 2] < 0) | (q[:, 2] > top)
        inside[idx[wall]] = True; live[idx[wall]] = False
        idx = idx[~wall]; q = q[~wall]
        sx, sy = nearest(grid, q[:, 0], q[:, 1])
        q[:, 0] -= sx; q[:, 1] -= sy
        rb = (q * q).sum(1)
        qt = q.copy(); qt[:, 2] -= top
        rt = (qt * qt).sum(1)
        a = rb < 1
        b = (~a) & (rt < rho * rho)
        out = ~(a | b)
        q[a] = q[a] / np.maximum(rb[a], 1e-300)[:, None]
        qb = qt[b] * (rho * rho / np.maximum(rt[b], 1e-300))[:, None]; qb[:, 2] += top
        q[b] = qb
        m[idx] = q
        live[idx[out]] = False
    inside[live] = True          # undecided when the rounds run out
    return inside


def recipe(P, t, rho, grid, rounds):
    m, _ = to_m(P)
    return recipe_m(m, 2 * t, rho, grid, rounds)


def kpearl(h, D, kk):
    return np.where(h > 0, 2 * h / (1 + np.sqrt(1 + kk * np.maximum(h, 0) * np.maximum(D, 0))), h)


def chain(P, t, rho, grid, rounds):
    """The recipe with the distance's numbers carried along, as the shader does it.
    Returns dict: state (0 undecided, 1 inside, 2 outside), best, m, W, DF (as they stand when the recipe ends)."""
    top = 2 * t
    m, DF = to_m(P)
    n = len(m)
    W = np.zeros((n, 3)); W[:, 2] = 1
    best = np.full(n, 1e9); state = np.zeros(n, int); live = np.ones(n, bool); it = np.zeros(n, int)
    for rnd in range(rounds):
        if not live.any():
            break
        idx = np.nonzero(live)[0]
        it[idx] = rnd
        q = m[idx]; w = W[idx]; df = DF[idx]
        sx, sy = nearest(grid, q[:, 0], q[:, 1])
        q[:, 0] -= sx; q[:, 1] -= sy; w[:, 0] -= sx; w[:, 1] -= sy
        L2 = np.maximum(((q - w) ** 2).sum(1), 1e-300); kk = 4 / L2
        hb = q[:, 2]; ht = top - q[:, 2]
        cand = np.minimum(kpearl(hb, w[:, 2], kk), kpearl(ht, top - w[:, 2], kk)) / df
        best[idx] = np.minimum(best[idx], cand)
        wall = (hb < 0) | (ht < 0)
        rb = (q * q).sum(1)
        qt = q.copy(); qt[:, 2] -= top
        rt = (qt * qt).sum(1)
        a = (~wall) & (rb < 1)
        b = (~wall) & (~a) & (rt < rho * rho)
        out = ~(wall | a | b)
        s = 1 / np.maximum(rb[a], 1e-300)
        q[a] = q[a] * s[:, None]; w[a] = w[a] / np.maximum((w[a] ** 2).sum(1), 1e-300)[:, None]; df[a] = df[a] * s
        s = rho * rho / np.maximum(rt[b], 1e-300)
        qb = qt[b] * s[:, None]; qb[:, 2] += top
        wt = w[b].copy(); wt[:, 2] -= top
        wb = wt * (rho * rho / np.maximum((wt ** 2).sum(1), 1e-300))[:, None]; wb[:, 2] += top
        q[b] = qb; w[b] = wb; df[b] = df[b] * s
        m[idx] = q; W[idx] = w; DF[idx] = df
        state[idx[wall]] = 1; state[idx[out]] = 2
        live[idx[wall | out]] = False
    return dict(state=state, best=best, m=m, W=W, DF=DF, it=it)


# ---------------------------------------------------------------------------------------------------------------
# The length that is certainly free (the prototype of GL_BALLS_FREE's "free"). m, W, DF: the end frame of points
# the recipe called OUTSIDE.

def neighbours(grid):
    if grid == 2:
        return [(1.0, 0.0), (-1.0, 0.0)], []
    if grid == 0:
        return [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)], [(1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0)]
    h = S3 / 2
    return [(1.0, 0.0), (-1.0, 0.0), (0.5, h), (-0.5, h), (0.5, -h), (-0.5, -h)], []


def cell_dist(q, n, grid):
    """A length that is no longer than the distance from q to the cell of the whole number n."""
    dx = q[:, 0] - n[0]; dy = q[:, 1] - n[1]
    if grid == 2:
        return np.maximum(np.abs(dx) - 0.5, 0)
    if grid == 0:
        return np.hypot(np.maximum(np.abs(dx) - 0.5, 0), np.maximum(np.abs(dy) - 0.5, 0))
    h = S3 / 2
    return np.maximum(np.maximum(np.abs(dx), np.maximum(np.abs(0.5 * dx + h * dy), np.abs(0.5 * dx - h * dy))) - 0.5, 0)


def carry(e, m, W, DF):
    L = np.sqrt(np.maximum(((m - W) ** 2).sum(1), 1e-300))
    e = np.maximum(e, 0)
    return e * L / ((L + e) * DF)


def lean(m, grid):
    al = np.abs(m[:, 0]); ac = m[:, 1].copy()
    if grid == 0:
        k = np.abs(m[:, 1]) > al
        al = np.where(k, np.abs(m[:, 1]), al); ac = np.where(k, m[:, 0], ac)
    if grid == 1:
        h = S3 / 2
        d1 = np.abs(0.5 * m[:, 0] + h * m[:, 1]); d2 = np.abs(0.5 * m[:, 0] - h * m[:, 1])
        k = d1 > al
        al = np.where(k, d1, al); ac = np.where(k, 0.5 * m[:, 1] - h * m[:, 0], ac)
        k = d2 > al
        al = np.where(k, d2, al); ac = np.where(k, 0.5 * m[:, 1] + h * m[:, 0], ac)
    return al, ac


def free_apart(m, W, DF, top, rho, grid, parts=None):
    """The two spheres apart or touching, any rho: the hulls of GL_BALLS_RHO (docs/ROUND29.md T4)."""
    parts = parts or {}
    rr = rho * rho
    sD = max(top - 1 - rho, 0.0) * (top - 1 + rho) / top; sQ = np.sqrt(sD * (sD + 4))
    HB = 1 / (1 + 0.5 * (sD + sQ)); HT = rr / (top - HB); zm = 1 + 0.5 * sD; d2 = 0.25 * sD * (sD + 4)
    restB = 0.5 * HB if grid == 0 else HB / 3 if grid == 1 else 0.25 * HB; restT = rr * HT
    rT = min(rho, 2 * rr / (1 + np.sqrt(max(1 - 4 * rr, 0.0))) + restT)
    sw = min(0.5, top - zm + rho); sa = (sw * sw - d2) / (2 * sw); sR = (sw * sw + d2) / (2 * sw)
    hb = m[:, 2]; ht = top - m[:, 2]
    rt = np.sqrt(m[:, 0] ** 2 + m[:, 1] ** 2 + ht ** 2)
    cb = np.sqrt(m[:, 0] ** 2 + m[:, 1] ** 2 + (hb - 0.5 * HB) ** 2) - 0.5 * HB
    ct = np.sqrt(m[:, 0] ** 2 + m[:, 1] ** 2 + (ht - 0.5 * HT) ** 2) - 0.5 * HT
    lo = np.hypot(m[:, 1], hb) if grid == 2 else hb
    hi = np.hypot(m[:, 1], ht) if grid == 2 else ht
    e = np.maximum(np.minimum(np.minimum(cb, ct), np.minimum(lo - restB, np.maximum(hi - restT, rt - rT))), 0)
    q = np.hypot(m[:, 0], m[:, 1]); dz = m[:, 2] - zm
    if d2 < 3 and not parts.get('nospindle'):
        e = np.maximum(e, (d2 + q * (2 * sa - q) - dz * dz) / (sR + np.hypot(q - sa, dz)))
    if not parts.get('noside'):
        e = np.maximum(e, side_room(m, top, rho, grid, HB))
    return carry(e, m, W, DF)


def side_numbers(top, rho, grid, HB=None):
    """The side spindle (rho <= 1/2) or the side ring (rho > 1/2) between the second sphere and its copy at the
    next whole number: (c2, a, R, clip) or None. HB: the hull height while the two spheres are apart; None where
    they cut (then the first sphere itself is kept clear)."""
    rr = rho * rho; c2 = 0.25 - rr
    K = top * top - 1 + rr; disc = K * K + 4 * (top * top - 1) * c2
    if disc < 0:
        return None
    wA = (K + np.sqrt(disc)) / (2 * (top + 1))            # clear of the first sphere and of its copy
    lim = np.inf if grid == 2 else 0.5 if grid == 0 else 0.5 / S3   # how far across the two cells reach
    if c2 >= 0:
        w = min(wA, lim, (S3 / 2 if grid == 1 else 1.0) - rho)
        if HB is not None:
            w = min(top - HB, (S3 / 2 if grid == 1 else 1.0) - rho)   # Version 21's spindle, as it was
        clip = np.inf
    else:
        w = wA
        q0s = -c2
        if not w * w > q0s * 1.0000001:
            return None
        clip = lim * q0s / (w * w)
    if not w > 0:
        return None
    return c2, (w * w - c2) / (2 * w), (w * w + c2) / (2 * w), clip


def side_room(m, top, rho, grid, HB=None):
    sn = side_numbers(top, rho, grid, HB)
    if sn is None:
        return np.full(len(m), -1.0)
    c2, a, R, clip = sn
    al, ac = lean(m, grid)
    ht = top - m[:, 2]
    v = al - 0.5; q = np.hypot(ac, ht)
    room = (c2 - v * v + q * (2 * a - q)) / (R + np.hypot(v, q - a))
    if np.isfinite(clip):
        room = np.minimum(room, clip - np.abs(ac))
    return room


def free_cut(m, W, DF, top, rho, grid, parts=None, left=None):
    """The two spheres cut into each other. Returns (free, extra) where extra is the true distance to the two first
    buds behind the mirrors (they are balls of the picture that the recipe's own chain does not meet)."""
    parts = parts or {}
    rr = rho * rho
    C = np.array([0.0, 0.0, top])
    near, diag = neighbours(grid)
    cells = [(0.0, 0.0)] + near + diag
    n = len(m)
    # ---- looking through the first sphere (T2)
    r2 = np.maximum((m * m).sum(1), 1e-300)
    mA = m / r2[:, None]; WA = W / np.maximum((W * W).sum(1), 1e-300)[:, None]; DFA = DF / r2
    LA2 = np.maximum(((mA - WA) ** 2).sum(1), 1e-300)
    budA = kpearl(top - mA[:, 2], top - WA[:, 2], 4 / LA2) / DFA
    eA = np.full(n, 0.5)
    for c in cells:                                   # the second sphere and its copies, each in its own cell
        d = np.sqrt((mA[:, 0] - c[0]) ** 2 + (mA[:, 1] - c[1]) ** 2 + (mA[:, 2] - top) ** 2) - rho
        eA = np.minimum(eA, np.maximum(d, cell_dist(mA, c, grid)))
    for c in diag:                                    # copies of the first sphere that are not next to it
        d = np.sqrt((mA[:, 0] - c[0]) ** 2 + (mA[:, 1] - c[1]) ** 2 + mA[:, 2] ** 2) - 1
        eA = np.minimum(eA, np.maximum(d, cell_dist(mA, c, grid)))
    eA = np.maximum(eA, 1 - np.sqrt((mA * mA).sum(1)))
    roomA = carry(eA, mA, WA, DFA)
    # ---- looking through the second sphere
    mt = m - C; d2 = np.maximum((mt * mt).sum(1), 1e-300); s = rr / d2
    mB = mt * s[:, None] + C
    Wt = W - C; WB = Wt * (rr / np.maximum((Wt * Wt).sum(1), 1e-300))[:, None] + C
    DFB = DF * s
    LB2 = np.maximum(((mB - WB) ** 2).sum(1), 1e-300)
    budB = kpearl(mB[:, 2], WB[:, 2], 4 / LB2) / DFB
    eB = np.full(n, 0.5)
    for c in cells:                                   # the first sphere and its copies
        d = np.sqrt((mB[:, 0] - c[0]) ** 2 + (mB[:, 1] - c[1]) ** 2 + mB[:, 2] ** 2) - 1
        eB = np.minimum(eB, np.maximum(d, cell_dist(mB, c, grid)))
    for c in near + diag:                             # the other copies of the second sphere
        d = np.sqrt((mB[:, 0] - c[0]) ** 2 + (mB[:, 1] - c[1]) ** 2 + (mB[:, 2] - top) ** 2) - rho
        eB = np.minimum(eB, np.maximum(d, cell_dist(mB, c, grid)))
    eB = np.maximum(eB, rho - np.sqrt(((mB - C) ** 2).sum(1)))
    roomB = carry(eB, mB, WB, DFB)
    if parts.get('t1'):
        roomA = carry(np.sqrt(r2) - 1, m, W, DF); roomB = carry(np.sqrt(d2) - rho, m, W, DF)
        budA = np.full(n, 1e9); budB = np.full(n, 1e9)
    t1 = np.minimum(carry(np.sqrt(r2) - 1, m, W, DF), carry(np.sqrt(d2) - rho, m, W, DF))
    free = np.minimum(roomA, roomB)
    whole = np.full(n, -1.0)
    zm = (top * top + 1 - rr) / (2 * top); dd = zm * zm - 1
    # ---- the ring round the circle where the two spheres cross (T3)
    w = min(0.5, top - zm + rho)
    if not parts.get('noring'):
        if w * w + dd > 0:
            a = (w * w - dd) / (2 * w); R = (w * w + dd) / (2 * w)
            q = np.hypot(m[:, 0], m[:, 1]); dz = m[:, 2] - zm
            ring = (dd + q * (2 * a - q) - dz * dz) / (R + np.hypot(q - a, dz))
            whole = np.maximum(whole, ring)
    # ---- the ring (or the spindle) between the second sphere and its copy at the next whole number
    side = side_room(m, top, rho, grid, None) if not parts.get('noside') else np.full(n, -1.0)
    # ---- balls that every move of the recipe carries onto themselves (they cross both spheres squarely, and the
    #      walls of the cell they reach are mirrors through their centres): nothing inside can lie in one
    if not parts.get('noballs'):
        whole = np.maximum(whole, own_balls(m, top, rho, grid))
    whole = carry(whole, m, W, DF); side = carry(side, m, W, DF)
    # ---- the depth of the search: a point that is still undecided when the rounds run out counts as inside, and
    #      such points lie in the rooms above, some rounds away. `left`: rounds the search had left when it ended.
    if left is not None and not parts.get('nodepth'):
        cdepth = parts.get('cdepth', 100) / 100.0
        q0 = np.sqrt(max(-dd, 0.0)); v = 0.5 if q0 < 0.5 else (np.sqrt(0.5) if grid == 0 else 1 / S3 if grid == 1 else q0 + 0.25)
        kap = np.sqrt(max(v - q0, 1e-9) / (v + q0)); rhoT = np.log((1 + kap) / (1 - kap))
        # the fan round the circle where the two spheres cross: so many rounds apart, at no distance at all
        fan = np.pi / max(np.pi - np.arccos(np.clip((1 + rr - top * top) / (2 * rho), -1, 1)), 1e-6) - 1e-3 if parts.get('fan', 1) else 1.0
        # (while only the far half of that fan is undecided, the ring itself still holds as far as the circle)
        if not parts.get('noring') and w * w + dd > 0 and not parts.get('nohalf'):
            half = carry(np.minimum(ring, np.hypot(q - q0, dz)), m, W, DF)
        else:
            half = np.full(n, -1.0)
        whole = np.where(left >= fan, whole * (1 - np.exp(-cdepth * rhoT * np.maximum(left - fan, 0))), np.where(left >= 0.5 * fan + 1, half, -1.0))
        sm = parts.get('sidemode', 1)
        if rr > 0.25:
            fs = np.pi / max(np.pi - np.arccos(np.clip((2 * rr - 1) / (2 * rr), -1, 1)), 1e-6) - 1e-3
            side = side * (1 - np.exp(-cdepth * rhoT * np.maximum(left - fs, 0)))
        elif sm == 1:
            side = side * np.maximum(left - 1, 0) / (left + parts.get('itn', 8))
        elif sm == 2:
            side = side * (1 - np.exp(-cdepth * rhoT * np.maximum(left - 1, 0)))
        free = np.where(left < 1, t1, free)
    free = np.maximum(free, np.maximum(whole, side))
    return free, np.minimum(budA, budB)


def own_balls(m, top, rho, grid):
    """Room inside the balls that cross both spheres squarely (centre at the height zm, radius^2 = (distance of the
    centre from the middle line)^2 + d2) and are centred on a wall of the cell or on one of its upright edges."""
    rr = rho * rho
    zm = (top * top + 1 - rr) / (2 * top); d2 = zm * zm - 1
    hmin = min(zm, top - zm)                      # the ball has to stay between the two walls
    al, ac = lean(m, grid)
    dz = m[:, 2] - zm
    room = np.full(len(m), -1.0)
    # centred on the wall the point leans towards, as far along the wall as the cell lets it
    if grid == 0:
        ylim = -d2                                # |y| + r <= 1/2
    elif grid == 1:
        ylim = 2 * (np.sqrt(max(-d2, 0.0)) - S3 / 4) if d2 < 0 else -1.0   # r <= (sqrt 3 / 2)(1 / (2 sqrt 3) - |y|)
    else:
        ylim = np.inf
    if rr - 0.25 > 1e-5:
        ylim = min(ylim, np.sqrt(rr - 0.25))
    else:
        ylim = -1.0
    if ylim >= 0:
        yc = np.clip(ac, -ylim, ylim)
        r2 = 0.25 + yc * yc + d2
        ok = r2 > 0
        r = np.sqrt(np.maximum(r2, 0))
        room = np.where(ok, r - np.sqrt((al - 0.5) ** 2 + (ac - yc) ** 2 + dz * dz), room)
    # centred on the upright edge of the cell nearest to the point
    if grid != 2:
        if grid == 0:
            ex = 0.5 * np.sign(m[:, 0] + 1e-30); ey = 0.5 * np.sign(m[:, 1] + 1e-30); v2 = 0.5; far = 1.0
        else:
            ang = np.arctan2(m[:, 1], m[:, 0]); k = np.floor(ang / (np.pi / 3)); a0 = (k + 0.5) * (np.pi / 3)
            ex = np.cos(a0) / S3; ey = np.sin(a0) / S3; v2 = 1.0 / 3; far = 0.5
        r2 = v2 + d2
        if r2 > 0 and np.sqrt(r2) <= min(hmin, far):
            r = np.sqrt(r2)
            room = np.maximum(room, r - np.sqrt((m[:, 0] - ex) ** 2 + (m[:, 1] - ey) ** 2 + dz * dz))
    return room


def estimate(P, t, rho, grid, rounds, parts=None):
    """The prototype of the program's distance at picture points P. Returns (d, best, free, state)."""
    top = 2 * t
    ch = chain(P, t, rho, grid, rounds)
    st = ch['state']; best = ch['best'].copy()
    free = np.zeros(len(best))
    o = st == 2
    if o.any():
        if top - 1 - rho >= -1e-9:
            free[o] = free_apart(ch['m'][o], ch['W'][o], ch['DF'][o], top, rho, grid, parts)
        else:
            f, extra = free_cut(ch['m'][o], ch['W'][o], ch['DF'][o], top, rho, grid, parts, rounds - 1 - ch['it'][o])
            free[o] = f; best[o] = np.minimum(best[o], np.where(rounds - 1 - ch['it'][o] >= 1, extra, 1e9) if not (parts or {}).get('nodepth') else extra)
    d = np.where(st == 0, -1e-7, np.where(st == 1, best, np.minimum(best, free)))
    return d, best, free, st


# ---------------------------------------------------------------------------------------------------------------
# The reference: the recipe alone on a fine grid, and the true distance from it.

def flat_truth(t, rho, grid, rounds, cx, cy, half_w, half_h, nx, z=0.0):
    """Flat cut z: returns xs, ys, inside (ny, nx), dist (true distance of every outside point to the nearest inside
    point OF THE CUT, in picture units), step."""
    step = 2 * half_w / nx
    ny = int(round(2 * half_h / step))
    xs = cx - half_w + (np.arange(nx) + 0.5) * step
    ys = cy + half_h - (np.arange(ny) + 0.5) * step
    X, Y = np.meshgrid(xs, ys)
    P = np.stack([X.ravel(), Y.ravel(), np.full(X.size, z)], 1)
    ins = recipe(P, t, rho, grid, rounds).reshape(X.shape)
    dist = ndimage.distance_transform_edt(~ins) * step if ins.any() else np.full(X.shape, np.inf)
    return xs, ys, ins, dist, step, P


def box_truth(t, rho, grid, rounds, centre, half, n):
    """A box in space: inside (n, n, n) and the true distance of every outside point to the nearest inside point
    of the box."""
    step = 2 * half / n
    ax = [(c - half) + (np.arange(n) + 0.5) * step for c in centre]
    X, Y, Z = np.meshgrid(ax[0], ax[1], ax[2], indexing='ij')
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    ins = np.zeros(len(P), bool)
    for i in range(0, len(P), 2000000):
        ins[i:i + 2000000] = recipe(P[i:i + 2000000], t, rho, grid, rounds)
    ins = ins.reshape(X.shape)
    dist = ndimage.distance_transform_edt(~ins) * step if ins.any() else np.full(X.shape, np.inf)
    return P, ins, dist, step


PANEL_NEW = [('X1', 120, 100, 0, 16), ('X2', 130, 100, 0, 16), ('X3', 150, 100, 2, 16), ('X4', 150, 100, 1, 16),
             ('X5', 200, 100, 2, 16), ('X6', 150, 75, 0, 16), ('X7', 300, 50, 0, 16), ('X8', 400, 100, 0, 16),
             ('X9', 105, 100, 0, 16), ('X9d', 105, 100, 0, 60), ('Y1', 80, 75, 0, 16), ('Y2', 60, 60, 1, 16),
             ('Y3', 100, 90, 0, 16), ('Y4', 55.56, 99, 0, 16), ('Y5', 133.33, 75, 0, 16), ('Y6', 120, 51, 2, 16),
             ('Y7', 30, 75, 0, 16)]
PANEL_OLD = [('O1', 55.56, 100, 0, 16), ('O2', 100, 100, 0, 16), ('O3', 20, 100, 0, 16), ('O4', 150, 100 / 3, 0, 16),
             ('O5', 300, 100 / 6, 0, 16), ('O6', 200, 50, 0, 16), ('O7', 400, 12.5, 1, 16), ('O8', 1000, 5, 0, 16),
             ('O9', 60, 40, 1, 16), ('O10', 80, 50, 2, 16)]
