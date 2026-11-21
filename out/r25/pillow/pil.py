"""Round 25, section "pillow": EVERY four-corner pillow with a smooth belt, as one family.

The pillow is the plane of z = x + i y folded by   z ~ z + 1,  z ~ z + tau,  z ~ -z,   tau = rho + i H.
Its four corners are 0, 1/2, tau/2, (1 + tau)/2. The direction map is the mirror doubling  z -> 2 conj(z)
(the only kind that gives angle DOUBLING, not minus doubling, on a belt: see NOTES.md). It respects the folding
only for rho = 0, 1/2, 1/4, 3/4. The belt is the line y = H/3; on it the longitude is s = x + rho and s -> 2 s.

    rho = 0     the two seams lie one above the other          (round 15's square pillow is rho = 0, H = 1)
    rho = 1/2   the two seams are crossed (a tetrahedron; H = sqrt(3)/2 is the regular one)
    rho = 1/4   the top seam is turned 135 degrees against the bottom one (3/4: the mirror image)

In the fundamental strip 0 <= y <= H/2 the map is
    y <= H/4 :  (x, y) -> (-2 x, 2 y)
    y >= H/4 :  (x, y) -> (2 x + rho, H - 2 y)

Layout (direction <-> pillow), "J": each side of the belt is a cylinder closed by a folded seam = an ellipse by the
Joukowski map, and the ellipse is squeezed to the round half sphere (stereographic from its pole). This is the layout
with the least squeeze that still has exact, even doubling on the belt. "JA": the same with the belt made angle-true
(round 23's two clocks).
    lower half (y < H/3):  seam y = 0,   corners at longitude rho, rho + 1/2
    upper half (y > H/3):  seam y = H/2, corners at longitude 3 rho / 2, 3 rho / 2 + 1/2

    python out/r25/pillow/pil.py check
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

TWO_PI = 2 * np.pi


class Pillow:
    def __init__(self, rho=0.0, H=1.0, kind='J'):
        self.rho, self.H, self.kind = float(rho), float(H), kind
        self.y0 = self.H / 3
        self.wn, self.ws = self.H / 6, self.H / 3                       # widths of the upper and the lower side
        self.an, self.as_ = np.exp(-TWO_PI * self.wn), np.exp(-TWO_PI * self.ws)
        self.rotn, self.rots = np.exp(1j * TWO_PI * 1.5 * self.rho), np.exp(1j * TWO_PI * self.rho)
        if kind == 'JA':
            self.tabn, self.tabs = self._table(self.an, self.wn), self._table(self.as_, self.ws)

    NT = 769

    def _table(self, a, w):
        """te on a grid of (|px|, |py|) in the seam's own frame, by bisection."""
        u = np.linspace(0, 1, self.NT); U, V = np.meshgrid(u, u, indexing='ij'); U2, V2 = U * U, V * V
        lo = np.zeros_like(U); hi = np.full_like(U, w)
        for _ in range(44):
            mid = 0.5 * (lo + hi); A, B = self._AB(mid, a, w)
            up = (B * B * U2 + A * A * V2 - A * A * B * B) > 0
            hi = np.where(up, mid, hi); lo = np.where(up, lo, mid)
        return 0.5 * (lo + hi)

    # ---- half-widths of the nested ellipses at the distance te from the belt
    def _AB(self, te, a, w):
        a2 = a * a
        if self.kind == 'J':
            r = np.exp(-TWO_PI * te)
            return (r + a2 / r) / (1 + a2), (r - a2 / r) / (1 - a2)
        q = (1 + a2) / (1 - a2)
        rA = np.exp(-TWO_PI * (q * te + (1 - q) * te * te / w)); rB = np.exp(-TWO_PI * (te / q + (1 - 1 / q) * te * te / w))
        return (rA + a2 / rA) / (1 + a2), (rB - a2 / rB) / (1 - a2)

    def to_flat(self, X, Y, Z):
        """Unit direction -> (x, y) on the pillow, 0 <= y <= H/2."""
        north = Z >= 0
        p = (X + 1j * Y) / (1 + np.abs(Z))
        a = np.where(north, self.an, self.as_); w = np.where(north, self.wn, self.ws)
        q = p * np.where(north, np.conj(self.rotn), np.conj(self.rots))
        if self.kind == 'J':
            a2 = a * a
            J = q.real * (1 + a2) + 1j * q.imag * (1 - a2)
            sq = np.sqrt(J * J - 4 * a2 + 0j)
            sq = np.where((J.real * sq.real + J.imag * sq.imag) >= 0, sq, -sq)
            zeta = 0.5 * (J + sq)
            r = np.clip(np.abs(zeta), a, 1.0)
            nu = np.angle(zeta); te = -np.log(r) / TWO_PI
        else:
            px, py = q.real, q.imag; px2, py2 = px * px, py * py
            a2 = a * a; qq = (1 + a2) / (1 - a2)
            # first guess from a table (built once by bisection), then polished
            n1 = self.NT - 1; fu = np.clip(np.abs(px), 0, 1) * n1; fv = np.clip(np.abs(py), 0, 1) * n1
            iu = np.minimum(fu.astype(np.int64), n1 - 1); iv = np.minimum(fv.astype(np.int64), n1 - 1); du = fu - iu; dv = fv - iv
            te = np.empty_like(px)
            for flag, tab in ((True, self.tabn), (False, self.tabs)):
                m = north == flag
                if m.any():
                    i, j, d1, d2 = iu[m], iv[m], du[m], dv[m]
                    te[m] = (tab[i, j] * (1 - d1) * (1 - d2) + tab[i + 1, j] * d1 * (1 - d2) + tab[i, j + 1] * (1 - d1) * d2 + tab[i + 1, j + 1] * d1 * d2)
            te = np.clip(te, 0.0, w)
            c1 = 1 / qq; c2 = (1 - 1 / qq) / w
            for it in range(3):
                sA = qq * te + (1 - qq) * te * te / w; sB = te / qq + (1 - 1 / qq) * te * te / w
                rA = np.exp(-TWO_PI * sA); rB = np.exp(-TWO_PI * sB)
                A = (rA + a2 / rA) / (1 + a2); B = (rB - a2 / rB) / (1 - a2)
                dA = -TWO_PI * (qq + 2 * (1 - qq) * te / w) * (rA - a2 / rA) / (1 + a2)
                dB = -TWO_PI * (1 / qq + 2 * (1 - 1 / qq) * te / w) * (rB + a2 / rB) / (1 - a2)
                A2, B2 = A * A, B * B
                g = B2 * px2 + A2 * py2 - A2 * B2
                dg = 2 * B * dB * (px2 - A2) + 2 * A * dA * (py2 - B2)
                with np.errstate(divide='ignore', invalid='ignore'):
                    nt = te - g / dg
                # close to the seam: B straight from the ellipse equation with the A we have, then te from B (closed form)
                Bs = np.abs(py) / np.sqrt(np.maximum(1 - px2 / A2, 1e-30)); Bs = np.minimum(Bs, 1.0)
                rs = 0.5 * (Bs * (1 - a2) + np.sqrt(Bs * Bs * (1 - a2) ** 2 + 4 * a2)); ss = -np.log(rs) / TWO_PI
                ts = (-c1 + np.sqrt(np.maximum(c1 * c1 + 4 * c2 * ss, 0))) / (2 * c2)
                near = (B < 0.25) & (px2 < 0.8 * A2)
                ok = np.isfinite(nt) & (np.abs(nt - te) < 0.05 * w)
                new = np.clip(np.where(near, ts, np.where(ok, nt, te)), 0.0, w); delta = np.abs(new - te); te = new
            hard = ~(delta < 1e-11)
            if hard.any():                                    # the few the polish did not settle: plain bisection
                hx2, hy2, ha, hw = px2[hard], py2[hard], a[hard], w[hard]; lo = np.zeros_like(hx2); hi = hw.copy()
                for _ in range(46):
                    mid = 0.5 * (lo + hi); A, B = self._AB(mid, ha, hw)
                    up = (B * B * hx2 + A * A * hy2 - A * A * B * B) > 0
                    hi = np.where(up, mid, hi); lo = np.where(up, lo, mid)
                te[hard] = 0.5 * (lo + hi)
            A, B = self._AB(te, a, w)
            co = np.clip(px / A, -1.0, 1.0)
            # close to the seam B is tiny and py / B is not to be trusted: there the angle is read from px / A alone
            nu = np.where(B > 0.25, np.arctan2(py / np.maximum(B, 1e-300), px / A), np.arccos(co) * np.where(py < 0, -1.0, 1.0))
        x = nu / TWO_PI + np.where(north, self.rho / 2, 0.0)
        y = np.where(north, self.y0 + te, self.y0 - te)
        return x, y

    def from_flat(self, x, y):
        """(x, y) on the pillow, 0 <= y <= H/2 -> unit direction."""
        north = y >= self.y0
        a = np.where(north, self.an, self.as_); w = np.where(north, self.wn, self.ws)
        te = np.minimum(np.abs(y - self.y0), w)
        nu = TWO_PI * (x - np.where(north, self.rho / 2, 0.0))
        A, B = self._AB(te, a, w)
        p = (A * np.cos(nu) + 1j * B * np.sin(nu)) * np.where(north, self.rotn, self.rots)
        r2 = p.real * p.real + p.imag * p.imag
        k = 2 / (1 + r2); zz = (1 - r2) / (1 + r2)
        return k * p.real, k * p.imag, np.where(north, zz, -zz)

    def D(self, x, y):
        low = y <= self.H / 4
        return np.where(low, -2 * x, 2 * x + self.rho), np.where(low, 2 * y, self.H - 2 * y)

    def G(self, X, Y, Z):
        x, y = self.to_flat(X, Y, Z)
        return self.from_flat(*self.D(x, y))

    def F(self, x, y, z):
        sh = np.shape(x); x, y, z = (np.ravel(np.asarray(t, float)) for t in (x, y, z))
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); ok = r > 0; ri = 1 / np.where(ok, r, 1.0)
        dx, dy, dz = self.G(x * ri, y * ri, z * ri)
        ox, oy, oz = dx * r2, dy * r2, dz * r2
        flat = z == 0
        if flat.any():
            wv = (x[flat] + 1j * y[flat]) ** 2
            ox[flat], oy[flat], oz[flat] = wv.real, wv.imag, 0.0
        ox[~ok] = 0; oy[~ok] = 0; oz[~ok] = 0
        return ox.reshape(sh), oy.reshape(sh), oz.reshape(sh)


_P = {}


def pillow(rho=0.0, H=1.0, kind='J'):
    key = (float(rho), float(H), kind)
    if key not in _P:
        _P[key] = Pillow(*key)
    return _P[key]


def rule(rho=0.5, H=np.sqrt(3) / 2, kind='J', name=None, label=None):
    P = pillow(rho, H, kind)
    return M.fixed(P.F, name or 'pillow rho=%g H=%.3f %s' % (rho, H, kind), label or 'four-corner pillow, seams turned %g degrees, height %.3f' % (540 * rho % 180, H))


def mirror(r, name=None, label=None):
    """The same rule turned upside down (z -> -z before and after)."""
    def step(x, y, z, st, k, cx, cy, cz):
        X, Y, Z, st = r.step(x, y, -z, st, k, cx, cy, cz)
        return X, Y, -Z, st
    return M.Rule(name or r.name + ' flipped', label or r.label, step, init=r.init)


def check(rho, H, kind='J', n=200000, seed=7, flat=True):
    P = pillow(rho, H, kind); rng = np.random.default_rng(seed)
    d = rng.normal(size=(3, n)); d /= np.sqrt((d * d).sum(0))
    x, y = P.to_flat(*d); b = np.stack(P.from_flat(x, y)); rt = np.abs(b - d).max()
    th = rng.uniform(0, TWO_PI, 20000); g = P.G(np.cos(th), np.sin(th), 0 * th)
    eq = max(np.abs(g[0] - np.cos(2 * th)).max(), np.abs(g[1] - np.sin(2 * th)).max(), np.abs(g[2]).max())
    jumps = []
    for hh in (1e-4, 1e-5):
        e = d + hh * rng.normal(size=d.shape); e /= np.sqrt((e * e).sum(0))
        jumps.append(np.sqrt(((np.stack(P.G(*d)) - np.stack(P.G(*e))) ** 2).sum(0)).max())
    # sideways stretch right beside the belt, and the lift direction
    eps = 1e-5; up = P.G(np.cos(th) * np.cos(eps), np.sin(th) * np.cos(eps), np.full_like(th, np.sin(eps)))
    dn = P.G(np.cos(th) * np.cos(eps), np.sin(th) * np.cos(eps), np.full_like(th, -np.sin(eps)))
    su, sd = -np.arcsin(up[2]) / eps, np.arcsin(dn[2]) / eps
    out = dict(rho=rho, H=H, kind=kind, round_trip=rt, belt=eq, jump4=jumps[0], jump5=jumps[1], side_up=(su.min(), su.max()), side_dn=(sd.min(), sd.max()),
               corners_low_lat=float(np.degrees(np.arcsin(-(1 - (2 * P.as_ / (1 + P.as_ ** 2)) ** 2) / (1 + (2 * P.as_ / (1 + P.as_ ** 2)) ** 2)))),
               corners_up_lat=float(np.degrees(np.arcsin((1 - (2 * P.an / (1 + P.an ** 2)) ** 2) / (1 + (2 * P.an / (1 + P.an ** 2)) ** 2)))),
               squeeze_up=(1 + P.an ** 2) / (1 - P.an ** 2), squeeze_low=(1 + P.as_ ** 2) / (1 - P.as_ ** 2))
    if flat:
        out['flat'] = M.flat_check(rule(rho, H, kind), n=20000, steps=60)
    return out


if __name__ == '__main__':
    for rho, H in ((0.0, 1.0), (0.5, 0.5), (0.5, np.sqrt(3) / 2), (0.25, 1.0), (0.75, 1.0)):
        for kind in ('J', 'JA'):
            c = check(rho, H, kind, flat=(kind == 'J'))
            print('rho %.2f H %.3f %s: round trip %.1e, belt against doubling %.1e, largest jump at 1e-4 / 1e-5: %.1e / %.1e, sideways stretch beside the belt up %.3f..%.3f (flipped), down %.3f..%.3f; corners at latitude %.1f (low) %.1f (up); squeeze low %.3f up %.3f'
                  % (rho, H, kind, c['round_trip'], c['belt'], c['jump4'], c['jump5'], *c['side_up'], *c['side_dn'], c['corners_low_lat'], c['corners_up_lat'], c['squeeze_low'], c['squeeze_up']))
            if 'flat' in c:
                print('     flat check', c['flat'])
            sys.stdout.flush()
