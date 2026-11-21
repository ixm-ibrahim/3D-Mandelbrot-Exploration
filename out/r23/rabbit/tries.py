"""Round 23, section "rabbit": the attempts to do better for the rabbit INSIDE each door (at most two per door).

Loaded through doors.get(<key>):

  pillow door
    'pilT45', 'pilT90'  the square pillow (Joukowski layout, height 1.3) with a layout that is NOT mirror-symmetric:
                        before the pillow is read off, the direction is turned about the upright axis by an angle that
                        is 0 on the flat plane (with slope 0) and 45 / 90 degrees from latitude 40 on. Read-off and
                        put-back layouts differ, so no upright plane is kept.
    'pilJA'             the Joukowski layout (height 1.3) with the belt made angle-true: the two half-widths of the
                        nested ellipses run on two different clocks, so that next to the belt the layout is the
                        identity to first order.  A(te) = (rA + a^2/rA)/(1 + a^2), B(te) = (rB - a^2/rB)/(1 - a^2),
                        rA = exp(-2 pi (q te + (1 - q) te^2/w)), rB = exp(-2 pi (te/q + (1 - 1/q) te^2/w)),
                        q = (1 + a^2)/(1 - a^2), te = distance from the belt, w = width of that half.
    'pilJA1'            the same at height 1.0.
  hinge doors
    'alongY'            'along' with the y-axis as hinge (pages = planes through the y-axis).
    'alongC'            'along' with the UNIT CIRCLE of the flat plane as hinge: pages = the spheres through that
                        circle (the flat plane and the unit sphere are two of them, at right angles); the turn about
                        the circle by psi is, in each upright plane through the z-axis with w = rho + i z,
                        u = (w - 1)/(w + 1) -> e^(i psi) u.  sigma = arg u is the page of the point;
                        psi = sigma - sin(4 sigma)/4;  F = Turn(psi) P Turn(-psi), P the one-plane square.
    'twoC'              'two planes' with the same hinge: the one-plane square about the flat plane or about the unit
                        sphere, whichever page is nearer (sigma within 45 degrees of 0 / 180, or of 90 / -90).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import doors as D
M, fastpil = D.M, D.fastpil
TWO_PI = 2 * np.pi
import scout as S                                        # out/me/r16/scout.py (put on the path by mem.py): S.oneplane


# ---------------------------------------------------------------- pillow door
def twisted_pillow(key, deg, lat1=40.0, name='pilT', label=''):
    lay = fastpil.get_lay(key); d0 = np.radians(deg); l1 = np.radians(lat1)

    def F(x, y, z):
        sh = np.shape(x); x, y, z = (np.ravel(t).astype(float) for t in (x, y, z))
        r = np.sqrt(x * x + y * y + z * z); lat = np.arcsin(np.clip(z / np.where(r > 0, r, 1.0), -1, 1))
        q = np.clip(np.abs(lat) / l1, 0, 1); d = d0 * q * q * (3 - 2 * q)
        co, si = np.cos(d), np.sin(d)
        X, Y, Z = fastpil.F(co * x + si * y, co * y - si * x, z.copy(), lay)          # the direction turned back by d, then the pillow
        return X.reshape(sh), Y.reshape(sh), Z.reshape(sh)
    return M.fixed(F, name, label or 'pillow %s read off through a twist of %g degrees' % (key, deg))


class LayJA:
    """Joukowski layout with an angle-true belt (see the module text). Same interface as fastpil.LayJ."""
    def __init__(self, h=1.3, n=2):
        self.h, self.n = float(h), int(n); self.t0 = self.h / (self.n + 1)
        self.wn, self.ws = self.h / 2 - self.t0, self.t0
        self.an, self.as_ = np.exp(-TWO_PI * self.wn), np.exp(-TWO_PI * self.ws)

    @staticmethod
    def _AB(te, a, w):
        a2 = a * a; q = (1 + a2) / (1 - a2)
        rA = np.exp(-TWO_PI * (q * te + (1 - q) * te * te / w)); rB = np.exp(-TWO_PI * (te / q + (1 - 1 / q) * te * te / w))
        return (rA + a2 / rA) / (1 + a2), (rB - a2 / rB) / (1 - a2)

    def pil(self, x, y, z):
        north = z >= 0; den = 1 + np.abs(z); px, py = x / den, y / den
        a = np.where(north, self.an, self.as_); w = np.where(north, self.wn, self.ws)
        lo = np.zeros_like(px); hi = w.copy()
        for _ in range(34):
            mid = 0.5 * (lo + hi); A, B = self._AB(mid, a, w)
            with np.errstate(divide='ignore', invalid='ignore'):
                g = (px / A) ** 2 + np.where(B > 0, (py / np.where(B > 0, B, 1.0)) ** 2, np.where(py != 0, np.inf, 0.0)) - 1
            up = g > 0
            hi = np.where(up, mid, hi); lo = np.where(up, lo, mid)
        te = 0.5 * (lo + hi); A, B = self._AB(te, a, w)
        nu = np.arctan2(np.where(B > 1e-300, py / np.maximum(B, 1e-300), 0.0), px / A)
        seam = B < 1e-9
        if seam.any():
            nu = np.where(seam, np.arccos(np.clip(px / A, -1, 1)) * np.where(py < 0, -1.0, 1.0), nu)
        return nu / TWO_PI, np.where(north, self.t0 + te, self.t0 - te)

    def dirn(self, s, t):
        north = t >= self.t0
        a = np.where(north, self.an, self.as_); w = np.where(north, self.wn, self.ws)
        te = np.clip(np.abs(t - self.t0), 0, w); A, B = self._AB(te, a, w); B = np.maximum(B, 0.0)
        nu = TWO_PI * s; px, py = A * np.cos(nu), B * np.sin(nu)
        r2 = px * px + py * py; k = 2 / (1 + r2); zz = (1 - r2) / (1 + r2)
        return k * px, k * py, np.where(north, zz, -zz)


def pillow_lay(lay, name, label):
    def F(x, y, z):
        sh = np.shape(x)
        X, Y, Z = fastpil.F(np.ravel(x).astype(float).copy(), np.ravel(y).astype(float).copy(), np.ravel(z).astype(float).copy(), lay)
        return X.reshape(sh), Y.reshape(sh), Z.reshape(sh)
    return M.fixed(F, name, label)


# ---------------------------------------------------------------- hinge doors
def along_y(x, y, z):
    """'along' with the y-axis as hinge. The page angle is taken between -90 and 90 degrees (the flat plane must be page 0)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        phi = np.where(x != 0, np.arctan(z / np.where(x != 0, x, 1.0)), np.where(z == 0, 0.0, np.sign(z) * np.pi / 2))
    psi = phi - 0.25 * np.sin(4 * phi); c, s = np.cos(psi), np.sin(psi)
    xx, zz = c * x + s * z, -s * x + c * z
    X, Y, Z = S.oneplane(xx, y, zz)
    return c * X - s * Z, Y, s * X + c * Z


def _turn_circle(x, y, z, e):
    """The turn about the unit circle of the flat plane; e = exp(i psi). Returns the point and a flag 'sent to infinity'."""
    rho = np.hypot(x, y); ok = rho > 0; rs = np.where(ok, rho, 1.0); ca, sa = np.where(ok, x / rs, 1.0), np.where(ok, y / rs, 0.0)
    w = rho + 1j * z; u = (w - 1) / (w + 1) * e
    d = 1 - u; far = np.abs(d) < 1e-150
    w2 = (1 + u) / np.where(far, 1.0, d)
    return w2.real * ca, w2.real * sa, w2.imag, far


def _page_circle(x, y, z):
    rho = np.hypot(x, y); w = rho + 1j * z
    return np.angle((w - 1) / (w + 1))                       # 0 / 180: the flat plane; 90 / -90: the unit sphere


def _circle_rule(psi_of):
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        big = r2 > 1e12; xs, ys, zs = (np.where(big, 0.0, t) for t in (x, y, z))
        sig = _page_circle(xs, ys, zs); sig = np.where(np.isfinite(sig), sig, 0.0)
        psi = psi_of(sig); e = np.exp(1j * psi)
        x1, y1, z1, far = _turn_circle(xs, ys, zs, np.conj(e))
        X, Y, Z = S.oneplane(np.where(far, 0.0, x1), np.where(far, 0.0, y1), np.where(far, 0.0, z1))
        X2, Y2, Z2, far2 = _turn_circle(X, Y, Z, e)
        with np.errstate(divide='ignore', invalid='ignore'):
            ct = np.where(np.abs(np.sin(psi / 2)) > 1e-150, np.cos(psi / 2) / np.where(np.abs(np.sin(psi / 2)) > 1e-150, np.sin(psi / 2), 1.0), 1e9)
        X2 = np.where(far, 0.0, X2); Y2 = np.where(far, 0.0, Y2); Z2 = np.where(far, ct, Z2)       # the page's own far point
        X2 = np.where(far2, 1e9, X2)
        P = S.oneplane(x, y, z)                                                                      # far out the rule is the one-plane rule
        return np.where(big, P[0], X2), np.where(big, P[1], Y2), np.where(big, P[2], Z2)
    return F


along_c = _circle_rule(lambda s: s - 0.25 * np.sin(4 * s))
two_c = _circle_rule(lambda s: np.where(np.abs(np.sin(s)) <= np.sqrt(0.5), 0.0, np.pi / 2))


D.TRIES.update({
    'pilT45': (lambda: twisted_pillow(('J', 1.3, 2), 45.0, name='pilT45'), 'Square pillow, lopsided layout (45)'),
    'pilT90': (lambda: twisted_pillow(('J', 1.3, 2), 90.0, name='pilT90'), 'Square pillow, lopsided layout (90)'),
    'pilJA':  (lambda: pillow_lay(LayJA(1.3, 2), 'pilJA', 'square pillow, Joukowski layout with an angle-true belt, height 1.3'), 'Square pillow, second layout made shape-true at the flat plane'),
    'pilJA1': (lambda: pillow_lay(LayJA(1.0, 2), 'pilJA1', 'square pillow, Joukowski layout with an angle-true belt, height 1.0'), 'Square pillow, second layout made shape-true (square)'),
    'alongY': (lambda: M.fixed(along_y, 'alongY', 'along with the y-axis as hinge'), 'Along, swinging about the y-axis'),
    'alongC': (lambda: M.fixed(along_c, 'alongC', 'along with the unit circle as hinge'), 'Along, swinging about the unit circle'),
    'twoC':   (lambda: M.fixed(two_c, 'twoC', 'two pages through the unit circle: the flat plane and the unit sphere, nearest'), 'Flat plane and unit ball, the nearer one'),
})


def layout_numbers(lay, name):
    """Round trip, exact doubling on the equator, jump, and the two stretches right beside the flat plane."""
    rng = np.random.default_rng(4); d = rng.normal(size=(100000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    s, t = lay.pil(d[:, 0], d[:, 1], d[:, 2]); b = np.stack(lay.dirn(s, t), 1); rt = np.abs(b - d).max()
    th = rng.uniform(0, TWO_PI, 20000); s, t = lay.pil(np.cos(th), np.sin(th), 0 * th); s2, t2 = fastpil.Dmap(s, t, lay.n, lay.h); g = lay.dirn(s2, t2)
    eq = max(np.abs(g[0] - np.cos(2 * th)).max(), np.abs(g[1] - np.sin(2 * th)).max(), np.abs(g[2]).max())
    a_ = rng.normal(size=(100000, 3)); a_ /= np.linalg.norm(a_, axis=1)[:, None]; b_ = a_ + 1e-5 * rng.normal(size=a_.shape); b_ /= np.linalg.norm(b_, axis=1)[:, None]
    fa = np.stack(fastpil.F(a_[:, 0].copy(), a_[:, 1].copy(), a_[:, 2].copy(), lay), 1); fb = np.stack(fastpil.F(b_[:, 0].copy(), b_[:, 1].copy(), b_[:, 2].copy(), lay), 1)
    jump = np.linalg.norm(fa - fb, axis=1).max()
    # sideways stretch beside the plane: lift unit directions by eps and compare the height of the image
    out = []
    for eps in (1e-4, -1e-4):
        th = np.linspace(0, TWO_PI, 720, endpoint=False); v = np.stack([np.cos(th), np.sin(th), np.full_like(th, eps)], 1); v /= np.linalg.norm(v, axis=1)[:, None]
        f = fastpil.F(v[:, 0].copy(), v[:, 1].copy(), v[:, 2].copy(), lay); st = np.abs(f[2] / v[:, 2])
        out.append((float(st.min()), float(st.max())))
    print('%-8s round trip %.1e | equator against doubling %.1e | largest jump at step 1e-5: %.1e | sideways stretch beside the plane: above %.3f..%.3f, below %.3f..%.3f (2 = shape-true)'
          % (name, rt, eq, jump, out[0][0], out[0][1], out[1][0], out[1][1]))


if __name__ == '__main__':
    layout_numbers(fastpil.get_lay(fastpil.REF), 'E ref'); layout_numbers(fastpil.get_lay(('J', 1.3, 2)), 'J 1.3'); layout_numbers(fastpil.get_lay(('J', 1.0, 2)), 'J 1.0')
    layout_numbers(LayJA(1.3, 2), 'JA 1.3'); layout_numbers(LayJA(1.0, 2), 'JA 1.0')
    rng = np.random.default_rng(1)
    # hinge tries: do the pages agree on the hinge? jump of the rule across the hinge and across the plane x = 0
    for nm, F in (('along (x-axis)', D.get('along').step), ('alongY', D.get('alongY').step), ('alongC', D.get('alongC').step), ('twoC', D.get('twoC').step)):
        p = rng.uniform(-1.3, 1.3, size=(3, 200000)); q = p + 1e-6 * rng.normal(size=p.shape)
        a = np.stack(F(p[0], p[1], p[2], (), 0, 0, 0, 0)[:3]); b = np.stack(F(q[0], q[1], q[2], (), 0, 0, 0, 0)[:3]); dj = np.linalg.norm(a - b, axis=0)
        print('%-15s random close pairs (1e-6 apart): largest move %.2e, pairs moved more than 1e-3: %d of %d' % (nm, np.nanmax(dj), int((dj > 1e-3).sum()), dj.size))
    t = rng.uniform(-1.2, 1.2, 4000); e = 1e-7
    for nm, key, mk in (('alongY across its hinge (the y-axis)', 'alongY', lambda s: ((s * e, t, e), (s * e, t, -e))),
                        ('alongY across the plane x = 0 at height 0.5', 'alongY', lambda s: ((e, t, 0.5 + 0 * t), (-e, t, 0.5 + 0 * t))),
                        ('along across its hinge (the x-axis)', 'along', lambda s: ((t, e + 0 * t, e), (t, -e + 0 * t, -e)))):
        F = D.get(key).step; A, B = mk(1.0)
        A = [np.broadcast_to(np.asarray(v, float), t.shape).copy() for v in A]; B = [np.broadcast_to(np.asarray(v, float), t.shape).copy() for v in B]
        a = np.stack(F(*A, (), 0, 0, 0, 0)[:3]); b = np.stack(F(*B, (), 0, 0, 0, 0)[:3]); dj = np.linalg.norm(a - b, axis=0)
        print('%-45s jump: median %.3f, largest %.3f (2 y^2 would be up to %.3f)' % (nm, np.median(dj), dj.max(), 2 * 1.44))
