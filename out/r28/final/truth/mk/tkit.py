"""Round 28, truth checker of Track A: my own LIST OF BALLS for "Balls on balls" with a second sphere of radius rho.

Written from docs/ROUND28.md section 1.1 only (the recipe) and from one fact about sphere inversions: a ball that does
not hold the centre of the inversion is carried to a ball, centre o + R^2 (c - o) / (|c - o|^2 - r^2), radius
R^2 r / (|c - o|^2 - r^2). I read out/r27/measure/ballkit.py for the idea (carry the two walls about with the moves),
and wrote this one differently: no hashing (keys are compared in full), the whole numbers are taken from one list
sorted by length, every query knows that the list repeats with the grid, and for every point the recipe calls INSIDE
the very ball it lies in is worked out by walking the recipe's own moves backwards (ball_of).

Everything here is in the object's own coordinates m unless a name says "pic". top = 1 + 100 / p.

    g = Grid('square' | 'hex' | 'line')
    reps, info = build(g, top, rho, r_min)          # every ball of radius >= r_min, one for each family of slid copies
    ix = Index(reps, g, top)                        # answers "does the ball (q, e) meet a listed ball", for points anywhere
    st, chain = recipe(mx, my, mz, g, top, rho, rounds, keep=True)   # 1 inside, 0 outside, -1 undecided
    c, r, ok = ball_of(chain, g, top, rho)          # the ball each inside point lies in
"""
import time
import numpy as np
from scipy.spatial import cKDTree

K2 = 1.05
S3 = np.sqrt(3.0)
C0 = np.array([0.0, 0.0, 1.0])          # the centre of the frame inversion, in m


def top_of(p):
    return 1.0 + 100.0 / p


def share_of(top):
    return 100.0 / (top - 1.0)


# ------------------------------------------------------------------------------------------------ the whole numbers
class Grid:
    def __init__(self, name):
        assert name in ('square', 'hex', 'line')
        self.name = name
        if name == 'square':
            self.e1, self.e2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
        elif name == 'hex':
            self.e1, self.e2 = np.array([1.0, 0.0]), np.array([0.5, S3 / 2])
        else:
            self.e1, self.e2 = np.array([1.0, 0.0]), None
        # every whole number up to length 120 (line: 3000), sorted by length
        if name == 'line':
            a = np.arange(-3000, 3001); P = np.column_stack([a.astype(float), np.zeros(a.size)])
        else:
            a, b = np.meshgrid(np.arange(-142, 143), np.arange(-142, 143)); a, b = a.ravel(), b.ravel()
            P = a[:, None] * self.e1[None] + b[:, None] * self.e2[None]
        n = np.hypot(P[:, 0], P[:, 1]); o = np.argsort(n, kind='stable')
        self.P, self.N = P[o], n[o]
        self.maxlen = 120.0 if name != 'line' else 3000.0

    def upto(self, R):
        """All whole numbers of length <= R (R at most self.maxlen)."""
        if R > self.maxlen:
            raise ValueError('whole numbers asked up to %g, the list ends at %g' % (R, self.maxlen))
        return self.P[:np.searchsorted(self.N, R, side='right')]

    def nearest(self, x, y):
        """The whole number nearest to (x, y): (nx, ny)."""
        x = np.asarray(x, float); y = np.asarray(y, float)
        if self.name == 'line':
            return np.round(x), np.zeros_like(y)
        if self.name == 'square':
            return np.round(x), np.round(y)
        # honeycomb: rows y = b sqrt(3) / 2, in row b the points a + b / 2. Try the three rows about the point.
        b0 = np.round(y / (S3 / 2)); bx = np.zeros_like(x); by = np.zeros_like(y); bd = np.full(x.shape, np.inf)
        for j in (-1.0, 0.0, 1.0):
            b = b0 + j; a = np.round(x - b / 2); px = a + b / 2; py = b * S3 / 2
            d = (x - px) ** 2 + (y - py) ** 2; m = d < bd
            bx = np.where(m, px, bx); by = np.where(m, py, by); bd = np.where(m, d, bd)
        return bx, by

    def home(self, x, y):
        """One fixed copy of (x, y) among its slid copies (the same one for all of them, up to 1e-7 at the seams)."""
        x = np.asarray(x, float); y = np.asarray(y, float)
        if self.name == 'line':
            return x - np.floor(x + 0.5 + 1e-7), y
        if self.name == 'square':
            return x - np.floor(x + 0.5 + 1e-7), y - np.floor(y + 0.5 + 1e-7)
        b = y / (S3 / 2); a = x - b / 2
        fa = np.floor(a + 0.5 + 1e-7); fb = np.floor(b + 0.5 + 1e-7)
        return x - fa - fb / 2, y - fb * S3 / 2


# ------------------------------------------------------------------------------------------------ the recipe (1.1)
def frame(x, y, z):
    """Picture point -> the object's own coordinates: one sphere inversion, centre (0, 0, 1), radius^2 = 1.05."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    ux, uy, uz = y, z, x - K2 / 2
    d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    return K2 * ux / d, K2 * uy / d, 1.0 + K2 * uz / d


def unframe(mx, my, mz):
    """The object's own coordinates -> picture point (the same inversion, read backwards)."""
    vx, vy, vz = np.asarray(mx, float), np.asarray(my, float), np.asarray(mz, float) - 1.0
    d = vx * vx + vy * vy + vz * vz; d = np.where(d > 0, d, 1e-300)
    ux, uy, uz = K2 * vx / d, K2 * vy / d, K2 * vz / d
    return uz + K2 / 2, ux, uy


def recipe(mx, my, mz, grid, top, rho, rounds=200, keep=False):
    """Section 1.1, written out. Returns state (1 INSIDE, 0 OUTSIDE, -1 still undecided after `rounds` rounds).
    keep: also the moves, for ball_of: dict(nx, ny (rounds, n), inv (rounds, n) 0 none / 1 first / 2 second sphere,
    end (n) = the round at whose start the point was found beyond a wall, wall (n) = 1 below the bottom, 2 above the top)."""
    x = np.array(mx, float).ravel(); y = np.array(my, float).ravel(); z = np.array(mz, float).ravel(); n = x.size
    state = np.full(n, -1, np.int8); r2 = rho * rho
    if keep:
        NX = np.zeros((rounds, n)); NY = np.zeros((rounds, n)); INV = np.zeros((rounds, n), np.int8)
        end = np.full(n, -1, np.int32); wall = np.zeros(n, np.int8)
    live = np.arange(n)
    for k in range(rounds):
        if live.size == 0:
            break
        xl, yl, zl = x[live], y[live], z[live]
        below = zl < 0; above = zl > top; ins = below | above
        state[live[ins]] = 1
        if keep:
            end[live[ins]] = k; wall[live[below]] = 1; wall[live[above]] = 2
        live = live[~ins]; xl, yl, zl = xl[~ins], yl[~ins], zl[~ins]
        nx, ny = grid.nearest(xl, yl)
        xl = xl - nx; yl = yl - ny
        rb = xl * xl + yl * yl + zl * zl; rt = xl * xl + yl * yl + (zl - top) ** 2
        inb = rb < 1.0; itp = (~inb) & (rt < r2); out = ~(inb | itp)
        state[live[out]] = 0
        if keep:
            NX[k, live] = nx; NY[k, live] = ny; INV[k, live] = np.where(inb, 1, np.where(itp, 2, 0))
        sb = 1.0 / np.where(rb > 0, rb, 1.0); st = r2 / np.where(rt > 0, rt, 1.0)
        xn = np.where(inb, xl * sb, np.where(itp, xl * st, xl))
        yn = np.where(inb, yl * sb, np.where(itp, yl * st, yl))
        zn = np.where(inb, zl * sb, np.where(itp, top + (zl - top) * st, zl))
        x[live], y[live], z[live] = xn, yn, zn
        live = live[~out]
    if keep:
        return state, dict(nx=NX, ny=NY, inv=INV, end=end, wall=wall)
    return state


def inside_pic(x, y, z, grid, top, rho, rounds):
    """The verdict as the page gives it: INSIDE, or still undecided when the rounds run out -> True."""
    return recipe(*frame(x, y, z), grid, top, rho, rounds) != 0


def ball_of(chain, grid, top, rho):
    """For every point the recipe called INSIDE: the ball of the object's own space it lies in, found by walking the
    recipe's moves backwards from the wall it ended beyond. Returns (c (n, 3), r (n), kind (n)): kind 0 = not an inside
    point, 1 = the wall below itself, 2 = the wall above itself, 3 = a ball (c, r valid), 4 = could not be walked back."""
    NX, NY, INV, end, wall = chain['nx'], chain['ny'], chain['inv'], chain['end'], chain['wall']
    n = end.size; c = np.zeros((n, 3)); r = np.zeros(n); kind = np.zeros(n, np.int8)
    half = wall.copy()            # 1: the object is still the half-space below, 2: above, 0: a ball (or nothing)
    kind[wall == 1] = 1; kind[wall == 2] = 2
    o = [None, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, top])]; R2 = [None, 1.0, rho * rho]
    rounds = NX.shape[0]
    for k in range(rounds - 1, -1, -1):
        act = np.nonzero(end > k)[0]                       # points whose round k was done
        if act.size == 0:
            continue
        for j in (1, 2):
            a = act[INV[k, act] == j]
            if a.size == 0:
                continue
            h = half[a]
            # a half-space: the wall through the centre of this sphere stays itself; the other becomes a ball
            own = 1 if j == 1 else 2
            other = a[(h != 0) & (h != own)]
            if other.size:
                dist = top                                  # the other wall is `top` away from this centre
                rad = R2[j] / (2 * dist); sgn = 1.0 if j == 1 else -1.0   # first sphere: the top wall comes to a ball above the centre
                c[other] = o[j] + np.array([0.0, 0.0, sgn * rad]); r[other] = rad; half[other] = 0; kind[other] = 3
            b = a[h == 0]
            if b.size:
                d = c[b] - o[j]; den = (d * d).sum(1) - r[b] ** 2
                bad = ~(den > 1e-14)
                den = np.where(bad, 1.0, den)
                c[b] = o[j] + R2[j] * d / den[:, None]; r[b] = R2[j] * r[b] / den
                kind[b[bad]] = 4
        # undo the slide of round k
        c[act, 0] += NX[k, act]; c[act, 1] += NY[k, act]
    return c, r, kind


# ------------------------------------------------------------------------------------------------ the list of balls
def _uniq(c, r, tol=1e-8):
    """Rows of (c, r) that are the same to `tol` once: (indices of one of each, their keys in rising order)."""
    q = np.round(np.column_stack([c, r]) / tol).astype(np.int64)
    v = np.ascontiguousarray(q).view([('a', np.int64), ('b', np.int64), ('c', np.int64), ('d', np.int64)]).ravel()
    u, i = np.unique(v, return_index=True)
    return i, u


def _fresh(known, v):
    """known and v both in rising order: which of v are not in known, and known with them put in."""
    if len(known) == 0:
        return np.ones(len(v), bool), v.copy()
    pos = np.searchsorted(known, v)
    there = known[np.minimum(pos, len(known) - 1)] == v
    there &= pos < len(known)
    return ~there, np.insert(known, pos[~there], v[~there])


def threshold(c, r_min, grid, top, rho):
    """The smallest radius the list promises at the place c: r_min, made finer near the second sphere's centre (and its
    slid copies) like the square of the distance from it, down to r_min rho^2 inside the second sphere. (So the buds
    on the top wall are listed as finely, for their size, as those on the bottom wall. rho = 1: r_min everywhere.)"""
    c = np.asarray(c, float).reshape(-1, 3)
    nx, ny = grid.nearest(c[:, 0], c[:, 1])
    d2 = (c[:, 0] - nx) ** 2 + (c[:, 1] - ny) ** 2 + (c[:, 2] - top) ** 2
    return r_min * np.minimum(1.0, np.maximum(rho * rho, d2))


SLACK = 0.5      # the list holds everything down to SLACK * threshold, so that it is whole down to the threshold itself


def build(grid, top, rho, r_min, cap=3_000_000, verbose=False, max_levels=4000):
    """Every ball of radius >= threshold (walls left out), one for each family of slid copies: (N, 4) = centre, radius.
    A move is applied to a ball only when the ball lies outside the move's sphere (then it shrinks), so the list is
    complete when the object is one; when it is not, the list still holds real balls of the object and they overlap."""
    t0 = time.time()
    o = [np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, top])]; RR = [1.0, rho * rho]; RAD = [1.0, rho]
    low = SLACK * r_min
    c = np.array([[0.0, 0.0, 1.0 / (2 * top)], [0.0, 0.0, top - rho * rho / (2 * top)]]); r = np.array([1.0 / (2 * top), rho * rho / (2 * top)])
    keep = r >= SLACK * threshold(c, r_min, grid, top, rho); c, r = c[keep], r[keep]
    i, known = _uniq(c, r); c, r = c[i], r[i]
    all_c, all_r = [c], [r]; total = len(r); level = 1; capped = False
    while len(r) and level < max_levels:
        nc, nr = [], []
        for j in (0, 1):
            dz2 = (c[:, 2] - o[j][2]) ** 2
            # how far a whole number may lie for the image to be kept. First sphere: images further than 0.45 from every
            # centre of a second sphere have threshold >= 0.2 r_min; nearer ones come from balls within 3 of the middle line.
            # Second sphere: every image lies inside it, where the threshold is r_min rho^2.
            if j == 0:
                H2 = np.maximum(r / (0.2 * low) + r * r - dz2, 9.0) if rho < 1 else r / low + r * r - dz2
            else:
                H2 = r / low + r * r - dz2
            ok = np.nonzero(H2 > 0)[0]
            if ok.size == 0:
                continue
            reach = np.sqrt(H2[ok]) + np.hypot(c[ok, 0], c[ok, 1])
            if (reach > grid.maxlen).any():
                raise ValueError('a ball needs whole numbers past the end of my list (reach %g)' % reach.max())
            cnt = np.searchsorted(grid.N, reach, side='right')
            order = np.argsort(-cnt); ok, cnt = ok[order], cnt[order]; s = 0
            while s < ok.size:
                e = s + 1; budget = int(cnt[s])
                while e < ok.size and budget + int(cnt[e]) < 4_000_000:
                    budget += int(cnt[e]); e += 1
                ii = ok[s:e]; kk = cnt[s:e]; s = e
                own = np.repeat(ii, kk); lam = np.arange(int(kk.sum())) - np.repeat(np.cumsum(kk) - kk, kk)
                cx = c[own, 0] + grid.P[lam, 0]; cy = c[own, 1] + grid.P[lam, 1]; cz = c[own, 2] - o[j][2]; rr = r[own]
                d2 = cx * cx + cy * cy + cz * cz; den = d2 - rr * rr
                m = (den > 0) & (np.sqrt(d2) - rr >= RAD[j] - 1e-9)
                m &= RR[j] * rr >= (low * rho * rho) * np.where(den > 0, den, np.inf)      # a first, cheap cut
                if not m.any():
                    continue
                f = RR[j] / den[m]
                ic = np.column_stack([cx[m] * f, cy[m] * f, o[j][2] + cz[m] * f]); ir = rr[m] * f
                k2 = ir >= SLACK * threshold(ic, r_min, grid, top, rho)
                nc.append(ic[k2]); nr.append(ir[k2])
        if not nc:
            break
        c = np.concatenate(nc); r = np.concatenate(nr)
        if len(r) == 0:
            break
        c[:, 0], c[:, 1] = grid.home(c[:, 0], c[:, 1])
        i, v = _uniq(c, r); c, r = c[i], r[i]
        new, known = _fresh(known, v); c, r = c[new], r[new]
        all_c.append(c); all_r.append(r); total += len(r); level += 1
        if verbose:
            print('   level %d: %d new (%d in all), %.1f s' % (level, len(r), total, time.time() - t0), flush=True)
        if total > cap:
            capped = True; break
    reps = np.column_stack([np.concatenate(all_c), np.concatenate(all_r)])
    return reps, dict(levels=level, n=len(reps), capped=capped, seconds=time.time() - t0, r_min=r_min)


class Index:
    """The listed balls, sorted into classes of like size, each with a tree of centres. Knows that the list repeats
    with the grid: a query may lie anywhere."""

    def __init__(self, reps, grid, top):
        self.grid, self.top, self.reps = grid, top, reps
        r = reps[:, 3]; self.cls = []
        if len(r):
            lev = np.floor(np.log2(r.max() / r) + 1e-12).astype(int)      # 0: within a factor 2 of the largest, ...
            for L in np.unique(lev):
                ids = np.nonzero(lev == L)[0]
                self.cls.append(dict(ids=ids, c=reps[ids, :3], r=r[ids], rmax=float(r[ids].max()), tree=cKDTree(reps[ids, :3]),
                                     span=float(np.hypot(reps[ids, 0], reps[ids, 1]).max()),
                                     lo=reps[ids, :2].min(0), hi=reps[ids, :2].max(0)))

    def meets(self, q, e, tol=0.0, walls=True, deepest=False, skip=None):
        """For every ball (centre q[i], radius e[i] >= 0): does it reach more than `tol` into a listed ball (any slid
        copy), or (walls) beyond a wall? Returns hit (bool) and, with deepest, how deep the deepest reach is.
        skip: (index into reps, for every query) a listed ball that is not to count at zero slide, or -1."""
        q = np.array(q, float).reshape(-1, 3); e = np.broadcast_to(np.asarray(e, float), (len(q),)).copy()
        nx, ny = self.grid.nearest(q[:, 0], q[:, 1]); q = q.copy(); q[:, 0] -= nx; q[:, 1] -= ny
        hit = np.zeros(len(q), bool); deep = np.full(len(q), -np.inf)
        if walls:
            dw = np.maximum(e - q[:, 2], e - (self.top - q[:, 2]))            # how far beyond a wall
            hit |= dw > tol; deep = np.maximum(deep, dw)
        qh = np.hypot(q[:, 0], q[:, 1])
        for C in self.cls:
            lam = self.grid.upto(min(self.grid.maxlen, float((e + qh).max()) + C['rmax'] + C['span'] + 1e-6))
            for lx, ly in lam:
                ll = np.hypot(lx, ly)
                # only queries whose ball, slid back, can reach the box that holds this class's centres
                bx = np.maximum(np.maximum(C['lo'][0] - (q[:, 0] - lx), (q[:, 0] - lx) - C['hi'][0]), 0.0)
                by = np.maximum(np.maximum(C['lo'][1] - (q[:, 1] - ly), (q[:, 1] - ly) - C['hi'][1]), 0.0)
                sel = np.nonzero(bx * bx + by * by <= (e + C['rmax'] + 1e-9) ** 2)[0]
                if not deepest:
                    sel = sel[~hit[sel]]
                if sel.size == 0:
                    continue
                qq = q[sel] - np.array([lx, ly, 0.0])
                d1, _ = C['tree'].query(qq, k=1, distance_upper_bound=float((e[sel]).max()) + C['rmax'] + 1e-9)
                near = d1 < e[sel] + C['rmax']
                if not near.any():
                    continue
                sel, qq = sel[near], qq[near]
                lists = C['tree'].query_ball_point(qq, e[sel] + C['rmax'])
                ln = np.array([len(a) for a in lists])
                if ln.sum() == 0:
                    continue
                own = np.repeat(np.arange(sel.size), ln); idx = np.concatenate([np.asarray(a, int) for a in lists if len(a)])
                d = np.sqrt(((C['c'][idx] - qq[own]) ** 2).sum(1)); dp = e[sel][own] + C['r'][idx] - d
                if skip is not None and lx == 0 and ly == 0:
                    same = C['ids'][idx] == skip[sel][own]; dp = np.where(same, -np.inf, dp)
                best = np.full(sel.size, -np.inf); np.maximum.at(best, own, dp)
                deep[sel] = np.maximum(deep[sel], best); hit[sel] |= best > tol
        return (hit, deep) if deepest else hit

    def holds(self, P):
        """Is each point inside a listed ball or beyond a wall?"""
        return self.meets(P, 0.0, tol=0.0)

    def find(self, c, r, tol=1e-5):
        """Is the ball (c, r) one of the list (some slid copy)? The same centre and radius to `tol` of its own radius
        (and 1e-11). Returns the index into reps, or -1."""
        c = np.array(c, float).reshape(-1, 3).copy(); r = np.asarray(r, float)
        c[:, 0], c[:, 1] = self.grid.home(c[:, 0], c[:, 1])
        out = np.full(len(c), -1); lim = 1e-11 + tol * r
        for C in self.cls:
            for lx, ly in self.grid.upto(2.01):
                qq = c - np.array([lx, ly, 0.0])
                d, i = C['tree'].query(qq, k=1, distance_upper_bound=float(lim.max()) if len(lim) else 1.0)
                ok = np.isfinite(d)
                ok[ok] &= (d[ok] <= lim[ok]) & (np.abs(C['r'][i[ok]] - r[ok]) <= lim[ok])
                out[ok] = C['ids'][i[ok]]
        return out


def overlaps(reps, grid, top, tol=1e-6, n_big=None, tol_abs=1e-11):
    """Do listed balls cut into each other? Every ball against every ball no larger than itself (all slid copies) and
    against the two walls. A pair counts when the two reach into each other by more than a millionth of the smaller
    one's radius (and more than 1e-11). Returns dict(pairs, deepest, dupes, wall, worst = (i, j, depth))."""
    ix = Index(reps, grid, top); r = reps[:, 3]; order = np.argsort(-r)
    if n_big is not None:
        order = order[:n_big]
    pairs = 0; deepest = 0.0; dupes = 0; worst = None; wall = 0.0
    wall = float(np.maximum(r - reps[:, 2], r - (top - reps[:, 2])).max()) if len(r) else 0.0
    qh = np.hypot(reps[:, 0], reps[:, 1])
    for C in ix.cls:
        todo = order[r[order] >= C['r'].min() - 1e-15]           # balls at least as large as the smallest of this class
        if todo.size == 0:
            continue
        lam = grid.upto(min(grid.maxlen, float((r[todo] + qh[todo]).max()) + C['rmax'] + C['span'] + 1e-6))
        for lx, ly in lam:
            ll = np.hypot(lx, ly)
            bx = np.maximum(np.maximum(C['lo'][0] - (reps[todo, 0] - lx), (reps[todo, 0] - lx) - C['hi'][0]), 0.0)
            by = np.maximum(np.maximum(C['lo'][1] - (reps[todo, 1] - ly), (reps[todo, 1] - ly) - C['hi'][1]), 0.0)
            sel = todo[bx * bx + by * by <= (r[todo] + C['rmax'] + 1e-9) ** 2]
            for s in range(0, sel.size, 20000):
                ss = sel[s:s + 20000]
                qq = reps[ss, :3] - np.array([lx, ly, 0.0])
                d1, _ = C['tree'].query(qq, k=2, distance_upper_bound=float(r[ss].max()) + C['rmax'] + 1e-9)
                near = (d1 < (r[ss] + C['rmax'])[:, None]).any(1)
                if not near.any():
                    continue
                ss, qq = ss[near], qq[near]
                lists = C['tree'].query_ball_point(qq, r[ss] + C['rmax'])
                ln = np.array([len(a) for a in lists])
                if ln.sum() == 0:
                    continue
                own = np.repeat(np.arange(ss.size), ln); idx = np.concatenate([np.asarray(a, int) for a in lists if len(a)])
                gi = ss[own]; gj = C['ids'][idx]
                d = np.sqrt(((C['c'][idx] - qq[own]) ** 2).sum(1)); dp = r[gi] + C['r'][idx] - d
                # each pair once: against a smaller ball always; against one of the same size only one way round
                keep = (C['r'][idx] < r[gi]) | ((C['r'][idx] == r[gi]) & ((gj > gi) | ((gj == gi) & ((lx > 0) | ((lx == 0) & (ly > 0))))))
                selfsame = (gi == gj) & (lx == 0) & (ly == 0)
                # the same ball listed twice (its key fell on either side of a rounding step, or its centre lies on a
                # seam of the cell): the same to a millionth of its own size. Anything else is a pair of two balls.
                small = np.minimum(C['r'][idx], r[gi])
                dup = (~selfsame) & (d < 1e-11 + 1e-6 * small) & (np.abs(C['r'][idx] - r[gi]) < 1e-11 + 1e-6 * small)
                dupes += int(dup.sum())
                # "cut into each other": deeper than rounding can explain, measured against the smaller ball
                m = keep & ~selfsame & ~dup & (dp > np.maximum(tol_abs, tol * small))
                if m.any():
                    pairs += int(m.sum()); k = int(np.argmax(np.where(m, dp, -np.inf)))
                    if dp[k] > deepest:
                        deepest = float(dp[k]); worst = (int(gi[k]), int(gj[k]), float(lx), float(ly), float(dp[k]))
    return dict(pairs=pairs, deepest=deepest, dupes=dupes // 2, wall=wall, worst=worst)


def hulls(top, rho):
    """Section 1.3, from my own derivation: the two fixed points on the middle line and what hangs on them."""
    s = top + (1 - rho * rho) / top
    D = (top - 1 - rho) * (top - 1 + rho) / top                 # s - 2
    sq = np.sqrt(max(D * (D + 4), 0.0))
    z2 = 1 + 0.5 * (D + sq); z1 = 1 / z2
    return dict(s=s, z1=z1, z2=z2, HB=z1, HT=top - z2, zm=0.5 * (z1 + z2), d2=0.25 * D * (D + 4), reach=K2 / 2 + (K2 / (z2 - 1) if z2 > 1 else np.inf))
