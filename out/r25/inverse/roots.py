"""Round 25, section 'inverse': the 3D object built backwards, from ROOTS.

The flat Julia set is what is left when the two square roots  z -> +-sqrt(z - c)  are applied over and over.
Here: sets of 3D roots, what is left when they are applied over and over (clouds of points), and the solids they
bound.

Root sets
    P      the two roots of the one-plane square (longitude halved, Mercator latitude halved)
    Q      the two roots of the quaternion square (the flat root spun round the x-axis)
    P+Q    all four of them (a rule with two squares per point)
    zip    the four roots that shrink the ball of directions by the same amount in every direction
           ("halve and mirror" on a flat pillow), with the flat circle laid on the one closed straight line of the
           pillow on which halving is plain angle halving and which passes through no corner (the line at one third
           of the pillow's height). class Zip below. A forward rule exists: Zip.F.

Solids
    one rule       a point is inside when its orbit stays (mem.stay)
    several rules  'any' = inside when SOME choice of square at every step stays (= all the roots of all the rules,
                   applied to a big ball over and over); 'all' = inside when EVERY choice stays (= all the roots
                   applied to the outside of a big ball over and over, and the rest is the solid).
                   Worked out on a grid of blocks: grid_K.

    python out/r25/inverse/roots.py check
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

PI2 = 2 * np.pi
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]
CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}


# ---------------------------------------------------------------- the two known squares and their roots
def P(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); d = r2 + z * z; f = np.where(d > 0, r2 / np.where(d > 0, d, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def Q(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def roots_P(X, Y, Z):
    R = np.sqrt(X * X + Y * Y + Z * Z); ok = R > 0; Rs = np.where(ok, R, 1.0); r = np.sqrt(R)
    S = np.clip(Z / Rs, -1, 1); s = S / (1 + np.sqrt(1 - S * S)); cb = np.sqrt(np.clip(1 - s * s, 0, 1))
    lam = np.arctan2(Y, X) / 2
    x, y, z = r * cb * np.cos(lam), r * cb * np.sin(lam), r * s
    return [(x, y, z), (-x, -y, z)]


def roots_Q(X, Y, Z):
    rho = np.hypot(Y, Z); w = np.sqrt(X + 1j * rho); ok = rho > 0; rs = np.where(ok, rho, 1.0)
    uy, uz = np.where(ok, Y / rs, 1.0), np.where(ok, Z / rs, 0.0)
    a, b = w.real, w.imag
    return [(a, b * uy, b * uz), (-a, -b * uy, -b * uz)]


# ---------------------------------------------------------------- the zip square (even shrinking in every direction)
class Zip:
    """Directions <-> a flat pillow. The pillow is a tube: t = longitude / 360 (once round = 1), s = 0 .. b/2 across,
    and each end of the tube is pressed flat and zipped shut (t ~ -t there). Flat distances on the tube are the
    'spacing'. The square in pillow coordinates is  u -> 2 * conj(u):
        s <  b/4:   (t, s) -> (-2 t, 2 s)
        s >= b/4:   (t, s) -> ( 2 t, b - 2 s)
    Every distance on the pillow is doubled, everywhere, in every direction. The line s = b/3 goes to itself with
    t -> 2 t: that is the flat circle. The wide band (s < b/3) is the upper half of the directions, the narrow band
    the lower half (mirror=True: the other way up).
    Layout of each band on its half sphere: band -> ring r0 <= |V| <= 1 (exact, shape-keeping) -> disc by
    zeta = V + chi * r0^2 / V, chi = 0 at the flat circle (so nothing is bent there) and 1 at the zip (the inner
    circle is pressed onto a slit) -> half sphere by the stereographic view."""

    KAPPA = 0.5        # chi is 1 from the zip out to the ring radius r0^KAPPA, then falls smoothly to 0 at the flat circle

    def __init__(self, b=1.0, mirror=False):
        self.b = float(b); self.mirror = mirror
        self.r0u = np.exp(-PI2 * b / 3); self.r0l = np.exp(-PI2 * b / 6)

    def chi(self, rho, r0):
        tau = np.clip(np.log(np.maximum(rho, 1e-300)) / (self.KAPPA * np.log(r0)), 0.0, 1.0)
        return tau * tau * (3 - 2 * tau)

    def cap(self, V, r0):
        rho = np.abs(V)
        return V + r0 * r0 * self.chi(rho, r0) / V

    ITERS = 42         # halvings in the search of the layout (42 = full precision; 24 is plenty for pictures)

    def uncap(self, zeta, r0):
        """Bisection on the ring radius rho: the point zeta lies on the oval (a cos, b sin), a = rho + e chi / rho,
        b = rho - e chi / rho, and both grow with rho."""
        e = r0 * r0; xi, eta = np.abs(zeta.real), np.abs(zeta.imag)
        lo = np.broadcast_to(np.asarray(r0, float), xi.shape).copy(); hi = np.ones_like(xi)
        for _ in range(self.ITERS):
            mid = 0.5 * (lo + hi); k = e * self.chi(mid, r0) / mid; a = mid + k; bb = np.maximum(mid - k, 1e-300)
            outside = (xi / a) ** 2 + (eta / bb) ** 2 > 1.0          # zeta is outside the oval of 'mid': rho is larger
            lo = np.where(outside, mid, lo); hi = np.where(outside, hi, mid)
        rho = 0.5 * (lo + hi); k = e * self.chi(rho, r0) / rho; a = rho + k; bb = np.maximum(rho - k, 1e-300)
        co = np.clip(zeta.real / a, -1, 1); si = np.clip(zeta.imag / bb, -1, 1)
        n = np.hypot(co, si); n = np.where(n > 0, n, 1.0)
        return rho, (co + 1j * si) / n

    def to_pillow(self, x, y, z):
        up = z >= 0; zeta = (x + 1j * y) / (1 + np.abs(z)); r0 = np.where(up, self.r0u, self.r0l)
        rho, p = self.uncap(zeta, r0); d = np.log(rho) / PI2
        return np.where(up, self.b / 3 + d, self.b / 3 - d), p

    def from_pillow(self, s, p):
        up = s <= self.b / 3; r0 = np.where(up, self.r0u, self.r0l)
        rho = np.maximum(np.exp(-PI2 * np.abs(s - self.b / 3)), r0)
        zeta = self.cap(rho * p, r0); m = np.minimum(zeta.real ** 2 + zeta.imag ** 2, 1.0)
        return 2 * zeta.real / (1 + m), 2 * zeta.imag / (1 + m), np.where(up, 1.0, -1.0) * (1 - m) / (1 + m)

    def L(self, s, p):
        low = s < self.b / 4
        return np.where(low, 2 * s, self.b - 2 * s), np.where(low, np.conj(p) ** 2, p ** 2)

    def F(self, x, y, z):
        if self.mirror:
            z = -z
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); ok = r > 0; ri = 1.0 / np.where(ok, r, 1.0)
        s, p = self.to_pillow(x * ri, y * ri, z * ri); s, p = self.L(s, p); X, Y, Z = self.from_pillow(s, p)
        flat = z == 0                                                # exactly on the flat plane: plain z^2, no rounding
        X = np.where(flat, x * x - y * y, r2 * X); Y = np.where(flat, 2 * x * y, r2 * Y); Z = np.where(flat, 0.0, r2 * Z)
        return X, Y, (-Z if self.mirror else Z)

    def roots(self, X, Y, Z):
        if self.mirror:
            Z = -Z
        R = np.sqrt(X * X + Y * Y + Z * Z); ok = R > 0; Ri = 1.0 / np.where(ok, R, 1.0); r = np.sqrt(R)
        s, p = self.to_pillow(X * Ri, Y * Ri, Z * Ri); h = np.sqrt(p); out = []
        for ss, pp in ((s / 2, np.conj(h)), (s / 2, -np.conj(h)), ((self.b - s) / 2, h), ((self.b - s) / 2, -h)):
            x, y, z = self.from_pillow(ss, pp); out.append((r * x, r * y, (-r * z if self.mirror else r * z)))
        return out

    def rule(self, name=None, label=None):
        return M.fixed(self.F, name or ('zip' + ('-m' if self.mirror else '')),
                       label or 'even doubling of directions on a pillow, flat circle on the line at one third')


# ---------------------------------------------------------------- solids
def inside_rule(rule, c, steps):
    return lambda x, y, z: M.stay(rule, x, y, z, c[0], c[1], c[2], steps) >= steps


def grid_K(Fs, c, mode='any', n=224, L=1.7, steps=30, verbose=True):
    """The solid of a rule with several squares per point, on n^3 blocks of the box [-L, L]^3.
    'any': a block stays when some square of it lands on a block that stays; 'all': when every square does."""
    t0 = time.time(); ax = np.linspace(-L, L, n).astype(np.float32); h = ax[1] - ax[0]
    rstar = 0.5 * (1 + np.sqrt(1 + 4 * np.linalg.norm(c))) + 1e-6
    K = np.zeros((n, n, n), bool); idxs = [np.empty((n, n, n), np.int32) for _ in Fs]
    for i0 in range(0, n, 16):
        x, y, z = np.meshgrid(ax[i0:i0 + 16].astype(float), ax.astype(float), ax.astype(float), indexing='ij')
        K[i0:i0 + 16] = x * x + y * y + z * z < rstar * rstar
        for F, idx in zip(Fs, idxs):
            X, Y, Z = F(x, y, z); X, Y, Z = X + c[0], Y + c[1], Z + c[2]
            good = np.isfinite(X + Y + Z) & (X * X + Y * Y + Z * Z < rstar * rstar)
            i = np.rint((np.where(good, X, 0) + L) / h).astype(np.int64); j = np.rint((np.where(good, Y, 0) + L) / h).astype(np.int64)
            k = np.rint((np.where(good, Z, 0) + L) / h).astype(np.int64)
            good &= (i >= 0) & (i < n) & (j >= 0) & (j < n) & (k >= 0) & (k < n)
            idx[i0:i0 + 16] = np.where(good, (i * n + j) * n + k, -1)
    Kf = np.append(K.ravel(), False)                                  # index -1 = gone
    for it in range(steps):
        new = None
        for idx in idxs:
            v = Kf[idx.ravel()]
            new = v if new is None else ((new | v) if mode == 'any' else (new & v))
        new &= Kf[:-1]; changed = int((new != Kf[:-1]).sum()); Kf[:-1] = new
        if changed == 0:
            break
    if verbose:
        print('   grid %s n=%d: %d rounds, %.4f of the box inside, %.0f s' % (mode, n, it + 1, Kf[:-1].mean(), time.time() - t0)); sys.stdout.flush()
    return Kf, (n, L, h, rstar)


def inside_grid(Fs, c, mode, Kf, meta, pre=1):
    """Inside test from the grid, with 'pre' exact squarings in front (each one halves the size of the blocks)."""
    n, L, h, rstar = meta

    def look(x, y, z):
        good = np.isfinite(x + y + z) & (x * x + y * y + z * z < rstar * rstar)
        i = np.rint((np.where(good, x, 0) + L) / h).astype(np.int64); j = np.rint((np.where(good, y, 0) + L) / h).astype(np.int64)
        k = np.rint((np.where(good, z, 0) + L) / h).astype(np.int64)
        good &= (i >= 0) & (i < n) & (j >= 0) & (j < n) & (k >= 0) & (k < n)
        return Kf[np.where(good, (i * n + j) * n + k, -1)]

    def rec(x, y, z, d):
        if d == 0:
            return look(x, y, z)
        res = None
        for F in Fs:
            X, Y, Z = F(x, y, z); v = rec(X + c[0], Y + c[1], Z + c[2], d - 1)
            res = v if res is None else ((res | v) if mode == 'any' else (res & v))
        return res & (x * x + y * y + z * z < rstar * rstar)

    return lambda x, y, z: rec(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), pre)


def render(inside, cam, w=380, h=285, nd=200, half_w=1.75, centre=(0.0, 0.0, 0.0)):
    """The same rough picture as mem.solid, for any inside test."""
    e1, e2, e3 = M.frame(cam)
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-half_w, half_w, nd)
    U, V = np.meshgrid(us, vs); depth = np.full((h, w), np.inf)
    for k0 in range(0, nd, 8):
        dk = ds[k0:k0 + 8]
        Pt = [centre[i] + U[None] * e1[i] + V[None] * e2[i] + dk[:, None, None] * e3[i] for i in range(3)]
        ins = np.asarray(inside(Pt[0], Pt[1], Pt[2])).reshape(Pt[0].shape)
        depth = np.minimum(depth, np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf))
    return M.shade_solid(depth, us[1] - us[0])


def sheet(rows, path, sets, cam, w=380, h=285, nd=200, title=None):
    """rows: [(label, make)], make(c) -> inside test. One rough solid per row and set."""
    pad = 10; t0 = time.time(); W = pad + len(sets) * (w + pad); H = 56 + len(rows) * (h + 36)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title or 'Rough solids, eye at %s' % (cam,), fill=(240, 240, 245), font=M.font(22))
    for i, (label, make) in enumerate(rows):
        y = 56 + i * (h + 36); d.text((pad, y), label, fill=(235, 220, 170), font=M.font(17))
        for j, (sn, c) in enumerate(sets):
            x = pad + j * (w + pad)
            im.paste(Image.fromarray(render(make(c), cam, w, h, nd)), (x, y + 26)); d.text((x + 6, y + 30), sn, fill=(150, 160, 175), font=M.font(13))
            print('   %s | %s  %.0f s' % (label[:40], sn, time.time() - t0)); sys.stdout.flush()
        im.save(path)
    return path


# ---------------------------------------------------------------- clouds: the roots applied over and over to points
def cloud(rootfn, c, walkers=30000, steps=46, burn=16, seed=1):
    rng = np.random.default_rng(seed); p = rng.normal(size=(3, walkers)) * 0.7; out = []
    for k in range(steps):
        rs = rootfn(p[0] - c[0], p[1] - c[1], p[2] - c[2]); pick = rng.integers(0, len(rs), walkers)
        p = np.stack([np.choose(pick, [r[i] for r in rs]) for i in range(3)])
        if k >= burn:
            out.append(p.copy())
    return np.concatenate(out, axis=1)


def draw_cloud(pts, cam, w=380, h=285, half_w=1.75):
    e1, e2, e3 = M.frame(cam); u = pts.T @ e1; v = pts.T @ e2; dd = pts.T @ e3
    px = 2 * half_w / (w - 1); i = np.rint((half_w * h / w - v) / px).astype(int); j = np.rint((u + half_w) / px).astype(int)
    ok = (i >= 1) & (i < h - 1) & (j >= 1) & (j < w - 1); i, j, dd = i[ok], j[ok], dd[ok]
    depth = np.full((h, w), np.inf)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if abs(di) + abs(dj) < 2:
                np.minimum.at(depth, (i + di, j + dj), dd)
    hit = np.isfinite(depth); img = np.zeros((h, w, 3), np.uint8); img[...] = (14, 17, 26)
    if hit.any():
        t = np.clip((half_w - depth[hit]) / (2 * half_w), 0, 1) ** 1.3
        img[hit] = (np.outer(0.25 + 0.75 * t, [238, 226, 196])).astype(np.uint8)
    return img


# ---------------------------------------------------------------- checks
def check():
    rng = np.random.default_rng(7)
    for b in (1.0, 1.5):
        for mirror in (False, True):
            zp = Zip(b, mirror); r = zp.rule(); print('\n== zip b=%g mirror=%s' % (b, mirror))
            # the layout: there and back
            v = rng.normal(size=(3, 200000)); v /= np.linalg.norm(v, axis=0)
            s, p = zp.to_pillow(*v); w = np.array(zp.from_pillow(s, p))
            print('   layout there and back: worst error %.2e; s range %.4f .. %.4f (b/2 = %.4f)' % (np.abs(w - v).max(), s.min(), s.max(), b / 2))
            for r0, nm in ((zp.r0u, 'upper'), (zp.r0l, 'lower')):
                rho = np.linspace(r0, 1, 20001); k = r0 * r0 * zp.chi(rho, r0) / rho
                print('   %s band: inner circle of the ring %.4f, slit half-length %.4f; ovals nested: %s' % (nm, r0, 2 * r0, bool((np.diff(rho + k) > 0).all() and (np.diff(rho - k) > 0).all())))
            X, Y, Z = zp.F(*(v * rng.uniform(0.2, 1.6, 200000))); print('   all finite: %s' % bool(np.isfinite(X + Y + Z).all()))
            # roots really are roots
            w0 = rng.normal(size=(3, 50000)); bad = 0.0
            for rt in zp.roots(*w0):
                back = np.array(zp.F(*rt)); bad = max(bad, float(np.abs(back - w0).max()))
            print('   square of each of the four roots gives the point back: worst error %.2e' % bad)
            errs = np.concatenate([np.abs(np.array(zp.F(*rt)) - w0).max(0) for rt in zp.roots(*w0)]); print('      share of roots off by more than 1e-4: %.5f' % (errs > 1e-4).mean())
            print('   flat check', M.flat_check(r, n=20000, steps=60))
            # how even is the push off the flat plane? (height after one squaring over height before, over 2 r)
            lon = np.linspace(0, PI2, 721)[:-1]
            for sgn in (1, -1):
                hh = 1e-4; X, Y, Z = zp.F(np.cos(lon), np.sin(lon), sgn * hh * np.ones_like(lon)); g = np.abs(Z) / (2 * hh)
                print('   push off the flat plane, %s side: %.4f .. %.4f (1 = the one-plane push)' % ('upper' if sgn > 0 else 'lower', g.min(), g.max()))
            # spacing: how much are neighbouring directions pulled apart by one squaring?
            v = rng.normal(size=(3, 100000)); v /= np.linalg.norm(v, axis=0); e = rng.normal(size=(3, 100000)); e -= (e * v).sum(0) * v; e /= np.linalg.norm(e, axis=0)
            f = np.cross(v.T, e.T).T; h = 1e-5; A = np.array(zp.F(*v)); B = (np.array(zp.F(*(v + h * e))) - A) / h; Cc = (np.array(zp.F(*(v + h * f))) - A) / h
            G = np.stack([np.stack([(B * B).sum(0), (B * Cc).sum(0)]), np.stack([(B * Cc).sum(0), (Cc * Cc).sum(0)])]); ev = np.linalg.eigvalsh(G.transpose(2, 0, 1))
            st = np.sqrt(np.clip(ev, 1e-30, None)); q = st[:, 1] / st[:, 0]
            print('   pull-apart of directions: smaller %.2f .. larger %.2f (median %.2f, %.2f); squeeze (larger/smaller): median %.2f, 90%% below %.2f, 99%% below %.2f'
                  % (np.percentile(st[:, 0], 1), np.percentile(st[:, 1], 99), np.median(st[:, 0]), np.median(st[:, 1]), np.median(q), np.percentile(q, 90), np.percentile(q, 99)))
    # the grid solid against the plain orbit test, for the one-plane rule
    c = (-1.0, 0.0, 0.0); Kf, meta = grid_K([P], c, 'any', n=160)
    q = rng.uniform(-1.7, 1.7, size=(3, 200000)); a = inside_grid([P], c, 'any', Kf, meta, pre=1)(*q); bb = M.stay(M.fixed(P), q[0], q[1], q[2], *c, 40) >= 40
    print('\n   grid solid against orbit test (one plane, c = -1): %.3f%% of the box differ; inside %.4f vs %.4f' % (100 * (a != bb).mean(), a.mean(), bb.mean()))


if __name__ == '__main__':
    check()
