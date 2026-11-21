"""Round 27, explorer "respace": carrying the balls object over to the true flat picture.

The pieces (all point by point, nothing drawn by hand):

  qmark / qinv        the re-spacing "fractions <-> halvings" (Minkowski's question mark and its inverse)
  Omega / Psi         the same as a re-spacing of the angle round a body, measured from the point where the body
                      hangs on its parent: true angle psi (0..pi)  ->  angle on the round ball omega (0..pi)
  Body(c, p)          the body of the true flat picture that holds 0, for a c whose orbit of 0 comes back after p steps
                      (c = -1: p = 2, the rabbit: p = 3).  bott(z) = the body's own natural coordinate b (|b| < 1) in
                      which "p steps of z^2 + c" is plain squaring, and its derivative.
  enter(body, z0, N)  for each flat point: the first step n at which its orbit is in that body (-1: never), the point
                      there, and how much the n steps have magnified.
  carried(way)        the 3D verdict of the carried object.  For p = (z0, h):
                          run z^2 + c on the flat part and multiply the hidden part h by the same factor 2|z| each step,
                          until the flat part is in the body of 0 for the first time;
                          go to the body's natural coordinate, hidden part again times the same factor: (b, hh);
                          way 'A': nothing more.  way 'B': re-space the angle from the hanging point, spun round the
                          body's axis.  way 'C': re-space the angle in the flat plane only (straight columns).
                          Then ask the balls object (round 25, tree.py) at R * (-b, hh).
  Hflat               the point-to-point match of the two FLAT pictures (true -> balls object's flat cut).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r25', 'klein'))
import mem as M
import tree as TR

K2, T0 = TR.K2, TR.T0; RAD = K2 / 2
RABBIT_C = complex(-0.12256116687665362, 0.7448617666197442)
ZERO = (0.0, 0.0, 0.0)
OWN_ONLY = True          # each true body is given the middle ball's own family only (see own_family)
FIT_CAP = True           # lift 'fit': a column is followed only up to the top of its fitted arc


# ------------------------------------------------------------------ fractions <-> halvings
def qinv(y, nbits=50):
    """Inverse of Minkowski's question mark on [0, 1] (halvings -> fractions)."""
    y = np.clip(np.array(y, float), 0.0, 1.0)
    a = np.ones_like(y); b = np.zeros_like(y); c = np.zeros_like(y); d = np.ones_like(y)
    for _ in range(nbits):
        lo = y < 0.5
        a, b, c, d = np.where(lo, a + b, b), np.where(lo, b, a + b), np.where(lo, c + d, d), np.where(lo, d, c + d)
        y = np.where(lo, 2 * y, 2 - 2 * y)
    return (a * y + b) / (c * y + d)                      # the tail is closed with ?^-1(y) ~ y


def qmark(x, nsteps=64):
    """Minkowski's question mark on [0, 1] (fractions -> halvings)."""
    x = np.clip(np.array(x, float), 0.0, 1.0); off = np.zeros_like(x); sc = np.ones_like(x)
    for _ in range(nsteps):
        lo = x <= 0.5
        off = np.where(lo, off, off + sc); sc = np.where(lo, sc / 2, -sc / 2)
        x = np.where(lo, x / np.maximum(1 - x, 1e-300), (1 - x) / np.maximum(x, 1e-300))
        x = np.clip(x, 0.0, 1.0)
    return off + sc * x


def Omega(psi):
    """True angle from the hanging point (0..pi) -> angle on the round ball (0..pi). Odd and 2pi-periodic by hand."""
    th = np.clip(np.asarray(psi, float) / (2 * np.pi), 0.0, 0.5)
    return np.where(th <= 0.25, 2 * np.arctan(qinv(4 * th)), np.pi - 2 * np.arctan(qinv(2 - 4 * th)))


def Psi(om):
    """Angle on the round ball (0..pi) -> true angle (0..pi): the inverse of Omega."""
    om = np.clip(np.asarray(om, float), 0.0, np.pi)
    return np.where(om <= np.pi / 2, (np.pi / 2) * qmark(np.tan(np.minimum(om, np.pi / 2) / 2)),
                    np.pi - (np.pi / 2) * qmark(np.tan((np.pi - np.maximum(om, np.pi / 2)) / 2)))


def signed(fn, ang):
    """Apply a map of 0..pi to a signed angle in (-pi, pi]."""
    return np.sign(ang) * fn(np.abs(ang))


# ------------------------------------------------------------------ the body of 0 and its natural coordinate
class Body:
    def __init__(self, c, p):
        self.c = complex(c); self.p = int(p)
        z = 0j; a = 1.0 + 0j
        for _ in range(1, self.p):
            z = z * z + self.c; a *= 2 * z
        self.a = a                                             # p steps near 0:  z -> a z^2
        self.alpha = (1 - np.sqrt(1 - 4 * self.c + 0j)) / 2    # where the body of 0 hangs on its neighbours
        self.al2 = abs(self.alpha) ** 2

    def strip(self, z):
        """The coordinate across the band that holds the body of 0: |u| < 1 between the two hanging points."""
        return (z.real * self.alpha.real + z.imag * self.alpha.imag) / self.al2

    def g(self, z):
        d = np.ones_like(z)
        for _ in range(self.p):
            d = d * 2 * z; z = z * z + self.c
        return z, d

    def bott(self, z, kmax=70):
        """b = natural coordinate of the body of 0 (b(p steps) = b^2), and db/dz. Only for z in that body."""
        z = np.asarray(z, complex); zk = z.copy(); zkp = np.ones_like(z); L = np.zeros_like(z); D = np.zeros_like(z); w = 0.5
        with np.errstate(all='ignore'):
            for _ in range(kmax):
                gz, gd = self.g(zk)
                ok = (np.abs(zk) > 1e-3) & np.isfinite(gz) & (np.abs(gz) > 0)
                if not ok.any():
                    break
                zs = np.where(ok, zk, 1.0); gs = np.where(ok, gz, self.a)
                L = L + np.where(ok, w * np.log(gs / (self.a * zs * zs)), 0)
                D = D + np.where(ok, w * (gd / gs - 2 / zs) * zkp, 0)
                zkp = np.where(ok, gd * zkp, 0); zk = np.where(ok, gz, 0); w /= 2
            e = np.exp(L)
        return self.a * z * e, self.a * e * (1 + z * D)

    def unbott(self, b, rounds=14):
        """z in the body of 0 with bott(z) = b (|b| < 1): Newton, walking out from the middle."""
        b = np.asarray(b, complex); z = b * 0.05 / self.a
        for t in np.linspace(0.05, 1.0, rounds):
            for _ in range(4 if t < 1 else 8):
                v, dv = self.bott(z)
                z = z - (v - b * t) / np.where(np.abs(dv) > 1e-12, dv, 1.0)
        return z


def enter(body, z0, nmax=60, tail=0.35, jets=False):
    """First step n at which the flat orbit of z0 is in the body of 0 (-1 = never within nmax), the point z_n,
    and the magnification |d z_n / d z_0|. alive = the orbit has not left after nmax steps."""
    z0 = np.asarray(z0, complex).ravel(); N = nmax; p = body.p; c = body.c
    z = z0.copy(); alive = np.ones(z.size, bool); band = np.zeros((N + 1, z.size), bool); last = []
    with np.errstate(all='ignore'):
        for k in range(N + 1):
            band[k] = alive & (np.abs(body.strip(z)) < 1.0)
            if k > N - p:
                last.append(alive & (np.abs(z) < tail))
            if k < N:
                z = np.where(alive, z * z + c, 4.0); alive &= np.abs(z) < 4.0
    flag = np.zeros((N + 1, z.size), bool)
    for j, k in enumerate(range(N - p + 1, N + 1)):
        flag[k] = band[k] & last[j]
    for k in range(N - p, -1, -1):
        flag[k] = band[k] & flag[k + p]
    has = flag.any(0); n = np.where(has, np.argmax(flag, 0), -1)
    z = z0.copy(); d1 = np.ones(z.size, complex); d2 = np.zeros(z.size, complex)
    for k in range(int(n.max()) if has.any() else 0):
        m = k < n
        d2 = np.where(m, 2 * d1 * d1 + 2 * z * d2, d2); d1 = np.where(m, 2 * z * d1, d1); z = np.where(m, z * z + c, z)
    if jets:
        return n, z, d1, d2                                    # first and second derivative of the n steps
    return n, z, np.abs(d1), alive


BASILICA = Body(-1.0, 2)
RABBIT = Body(RABBIT_C, 3)
_TREES = {}


def tree_rule(grid='gauss'):
    if grid not in _TREES:
        _TREES[grid] = TR.tree(grid)
    return _TREES[grid]


def tree_inside(x, y, z, grid='gauss', rounds=14):
    """The balls object's own verdict (round 25, tree.py) at picture points."""
    return M.stay(tree_rule(grid), x, y, z, 0.0, 0.0, 0.0, rounds) >= rounds


def own_family(x, y, z, t=T0, k2=K2, rounds=24):
    """Of the balls object: is the picture point in the MIDDLE ball's own family, that is in the middle ball or in a
    ball that hangs on it through a chain that starts OFF the flat plane? (The balls that hang on the middle ball in
    the flat plane, and all that hangs on those, belong to other bodies of the flat picture.)
    Every ball that hangs on the middle ball at the fraction p/q lies, with all that hangs on it, in the ball that
    touches there and is 1 / (t |q|^2) wide in the object's own coordinates; those do not overlap. The loop finds p/q."""
    sh = np.shape(x); mx, my, mz = (np.array(v, float).ravel() for v in TR.to_model(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), k2))
    n = mx.size; a = np.ones(n, complex); b = np.zeros(n, complex); c = np.zeros(n, complex); d = np.ones(n, complex)
    odd = np.zeros(n, bool); live = mz > 0; found = np.zeros(n, bool)
    for _ in range(rounds):
        hit = live & (mz > t); found |= hit; live &= ~hit
        if not live.any():
            break
        nx, ny = np.round(mx), np.round(my); sft = nx + 1j * np.where(odd, -ny, ny)
        b = np.where(live, a * sft + b, b); d = np.where(live, c * sft + d, d)
        mx = np.where(live, mx - nx, mx); my = np.where(live, my - ny, my)
        r2 = mx * mx + my * my + mz * mz; inv = live & (r2 < 1); stop = live & ~inv & (mz <= t); live &= ~stop
        s = 1 / np.where(inv & (r2 > 0), r2, 1.0)
        mx, my, mz = np.where(inv, mx * s, mx), np.where(inv, my * s, my), np.where(inv, mz * s, mz)
        a, b = np.where(inv, b, a), np.where(inv, a, b); c, d = np.where(inv, d, c), np.where(inv, c, d); odd ^= inv
    off = found & (np.abs((a * np.conj(c)).imag) > 0.5)
    mz0 = TR.to_model(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), k2)[2]
    return (off | (np.ravel(mz0) < 0)).reshape(sh)


# ------------------------------------------------------------------ the three ways off the flat plane
def respace(way, X, Y, Z):
    """Master frame (unit ball, hanging point at (-1, 0, 0)), true spacing -> the round ball's spacing."""
    if way == 'A':
        return X, Y, Z
    if way == 'B':                                            # spun round the body's axis (the x-axis of the frame)
        rho = np.hypot(Y, Z); r = np.sqrt(X * X + rho * rho)
        psi = np.arctan2(rho, -X); om = Omega(psi); s = np.where(rho > 1e-300, r * np.sin(om) / np.where(rho > 1e-300, rho, 1.0), 0.0)
        return -r * np.cos(om), Y * s, Z * s
    if way == 'C':                                            # the angle in the flat plane only; heights untouched
        r = np.hypot(X, Y); psi = np.arctan2(Y, -X); om = signed(Omega, psi)
        return -r * np.cos(om), r * np.sin(om), Z
    raise ValueError(way)


def unrespace(way, X, Y, Z):
    """The inverse of respace (round ball's spacing -> true spacing)."""
    if way == 'A':
        return X, Y, Z
    if way == 'B':
        rho = np.hypot(Y, Z); r = np.sqrt(X * X + rho * rho)
        om = np.arctan2(rho, -X); psi = Psi(om); s = np.where(rho > 1e-300, r * np.sin(psi) / np.where(rho > 1e-300, rho, 1.0), 0.0)
        return -r * np.cos(psi), Y * s, Z * s
    r = np.hypot(X, Y); om = np.arctan2(Y, -X); psi = signed(Psi, om)
    return -r * np.cos(psi), r * np.sin(psi), Z


def master(body, x, y, z, nmax=60, lift='same'):
    """(X, Y, Z, ok): the point in the master frame of the body it stands over (ok = it stands over a body).
    lift = 'same': the hidden direction is multiplied by the same factor as the flat directions (straight columns).
    lift = 'fit' : at every flat point the body's natural coordinate is replaced by the sphere inversion that fits
                   it best there (same value, same factor, same bend), and that inversion is used off the plane."""
    sh = np.shape(x); z0 = (np.asarray(x, float) + 1j * np.asarray(y, float)).ravel(); h = np.asarray(z, float).ravel()
    X = np.zeros(z0.size); Y = np.zeros(z0.size); Z = np.zeros(z0.size); ok = np.zeros(z0.size, bool)
    cand = (np.abs(z0) < 2.1) & (np.abs(h) < 1.6)
    if cand.any():
        n, zn, d1, d2 = enter(body, z0[cand], nmax, jets=True)
        good = n >= 0; zg = zn[good]; hg = h[np.flatnonzero(cand)[good]]; idx = np.flatnonzero(cand)[good]
        b, db = body.bott(zg); A = db * d1[good]
        if lift == 'same':
            bb = b; hh = np.abs(A) * hg
        else:
            e = 1e-5; _bp, dp = body.bott(zg + e); _bm, dm = body.bott(zg - e)
            with np.errstate(all='ignore'):
                B = (dp - dm) / (2 * e) / (2 * db) * d1[good] + d2[good] / (2 * d1[good])     # half of (second / first derivative)
                B = np.where(np.isfinite(B), B, 0.0); q = 1 + np.abs(B) ** 2 * hg * hg
                bb = b - A * np.conj(B) * hg * hg / q; hh = np.abs(A) * hg / q
                if FIT_CAP:                                    # past the top of its arc the fitted column comes down again: stop there
                    over = np.abs(B) * np.abs(hg) > 1.0; hh = np.where(over, 50.0, hh)
                if lift == 'fit2':                             # where the fitted inversion is inside-out (it sends the far end of
                    with np.errstate(all='ignore'):            # the column INTO the ball) fall back on the straight column
                        back = np.abs(b - A / np.where(np.abs(B) > 1e-12, B, 1e-12)) < 1.0
                    bb = np.where(back, b, bb); hh = np.where(back, np.abs(A) * hg, hh)
        X[idx] = -bb.real; Y[idx] = -bb.imag; Z[idx] = hh; ok[idx] = True
    return X.reshape(sh), Y.reshape(sh), Z.reshape(sh), ok.reshape(sh)


def carried_inside(body, way, x, y, z, grid='gauss', nmax=60, rounds=14):
    lift = 'fit' if way.startswith('F') else ('fit2' if way == 'G' else 'same'); way = {'F': 'A', 'FB': 'B', 'G': 'A'}.get(way, way)
    X, Y, Z, ok = master(body, x, y, z, nmax, lift)
    out = np.zeros(np.shape(X), bool)
    ok &= (X * X + Y * Y + Z * Z) < 9.0
    if ok.any():
        Xr, Yr, Zr = respace(way, X[ok], Y[ok], Z[ok])
        ins = tree_inside(RAD * Xr, RAD * Yr, RAD * Zr, grid, rounds)
        if OWN_ONLY and ins.any():
            ins[ins] = own_family(RAD * Xr[ins], RAD * Yr[ins], RAD * Zr[ins])
        out[ok] = ins
    return out


def carried(body, way, grid='gauss', nmax=60, rounds=14, name=None):
    """The carried object as a rule of the bench library (draw it with c = ZERO and 2 steps)."""
    def step(x, y, z, st, k, cx, cy, cz):
        if k > 0:
            return x, y, z, st
        ins = carried_inside(body, way, x, y, z, grid, nmax, rounds)
        return np.where(ins, 0.0, 100.0), np.zeros_like(x), np.zeros_like(x), st
    return M.Rule(name or 'carried %s' % way, '', step, init=lambda n: ())


# ------------------------------------------------------------------ the flat match (true picture -> the object's flat cut)
def _mob(m, w):
    return (m[0] * w + m[1]) / (m[2] * w + m[3])


def _mul(m, g):
    return (m[0] * g[0] + m[1] * g[2], m[0] * g[1] + m[1] * g[3], m[2] * g[0] + m[3] * g[2], m[2] * g[1] + m[3] * g[3])


def model_of(P, k2=K2):
    """Picture point (complex, flat plane) -> the object's own coordinate w = mx + i mz."""
    return 1j + 1j * k2 / (P - k2 / 2)


def picture_of(w, k2=K2):
    return k2 / 2 + 1j * k2 / (w - 1j)


def Hflat(z0, nmax=200, t=T0, far=4.0):
    """The flat match for c = -1. Returns (P, kind): P = the matched point of the object's flat cut (picture frame),
    kind = 1 inside a body (matched through the body's natural coordinate and the re-spacing fractions <-> halvings),
    0 = outside (sent on by the same moves until far away: outside goes to outside, nothing more is claimed),
    -1 = not settled within nmax steps (a hair along a rim)."""
    body = BASILICA; al = body.alpha.real                      # -0.618
    z0 = np.asarray(z0, complex).ravel(); npt = z0.size; N = nmax
    orb = np.empty((N + 3, npt), complex); z = z0.copy(); alive = np.ones(npt, bool)
    with np.errstate(all='ignore'):
        for k in range(N + 3):
            orb[k] = z; z = np.where(alive, z * z - 1.0, 4.0 + 0j); alive &= np.abs(z) < 1e6
    n, zn, d, _ = enter(body, z0, N)
    one = np.ones(npt, complex); zero = np.zeros(npt, complex)
    G = (one.copy(), zero.copy(), zero.copy(), one.copy())
    N1 = (-1.0, 0.0, 2j * t, 1.0); SN1 = (-2j * t, -1.0, -1.0, 0.0)          # S N1 with S(w) = -1/w
    Ai = (1.0, 0.0, 1.0, 1.0); Bi = (1.0, -1.0, 1.0, 0.0); Api = (1.0, 0.0, -1.0, 1.0); Bpi = (-1.0, -1.0, 1.0, 0.0)
    pos = np.zeros(npt, int); done = np.zeros(npt, bool); kind = np.full(npt, -1); W = np.zeros(npt, complex)
    ar = np.arange(npt)
    for _ in range(N + 1):
        act = ~done & (pos <= N)
        if not act.any():
            break
        zc = orb[np.minimum(pos, N + 2), ar]
        inb = act & (n >= 0) & (pos == n)                      # arrived in the body of 0
        farp = act & ~inb & (np.abs(zc) > far)
        left = act & ~inb & ~farp & (zc.real < al); right = act & ~inb & ~farp & (zc.real > -al)
        mid = act & ~inb & ~farp & ~left & ~right
        z2 = orb[np.minimum(pos + 2, N + 2), ar]
        limb = mid & (z2.real > -al)                           # the bud straight above / below
        up = zc.imag > 0; lf = zc.real < 0
        sel = [(left, N1, 1), (right, SN1, 1), (mid & (limb | lf) & up, Ai, 2), (mid & ~limb & ~lf & up, Bi, 2),
               (mid & (limb | lf) & ~up, Api, 2), (mid & ~limb & ~lf & ~up, Bpi, 2)]
        for msk, g, adv in sel:
            if msk.any():
                Gn = _mul(G, g)
                G = tuple(np.where(msk, Gn[i], G[i]) for i in range(4))
                pos = np.where(msk, pos + adv, pos)
        if inb.any():
            b, _db = body.bott(np.where(inb, zc, 0.0))
            r = np.abs(b); om = signed(Omega, np.arctan2(-b.imag, b.real))      # angle from the hanging point, up positive
            P = RAD * r * (-np.cos(om) + 1j * np.sin(om))
            W = np.where(inb, _mob(G, model_of(np.where(inb, P, 0.0))), W); kind = np.where(inb, 1, kind); done |= inb
        if farp.any():
            W = np.where(farp, _mob(G, model_of(np.where(farp, zc, 10.0))), W); kind = np.where(farp, 0, kind); done |= farp
    with np.errstate(all='ignore'):
        P = picture_of(W)
    return P, kind


def flat_tree_inside(P, rounds=40):
    return M.stay(tree_rule('line'), P.real, P.imag, np.zeros(P.shape), 0.0, 0.0, 0.0, rounds) >= rounds
