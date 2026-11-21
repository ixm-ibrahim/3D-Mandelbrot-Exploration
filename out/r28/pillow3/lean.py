"""Round 28, pillow3, layout B ("both circles even").

The pillow has a second closed straight line: from the belt point 1/2 (direction -x) straight up to the corner a,
on along the edge to the corner 0 (direction +x), and the mirror image below. Its length is sqrt(3); doubling doubles
it too. It is the fixed line of the pillow's second mirror, so on the ball it is the upright circle through the
x-axis. Layout A (p3.py) runs through it unevenly (the corner a ends 138 degrees from +x). Layout B makes it even:
the corner a sits 120 degrees from +x, and the upright plane through the x-axis then carries the flat rule as well.

    E_B = Cap o Blend:
      Blend:  (s, f) -> ( cos(f')^2 S(s) + sin(f')^2 L(s),  f' = fan(f) )      S = the belt's clock (p3), L = the upright circle's
      Cap:    inside the cap of `cap` degrees about the corner a (and its mirror image), distances r from a are
              re-timed  r -> cap * u^(1/3) (1 + 2 u) / 3,  u = r / cap   (a cube root: the corner misses two thirds of a turn)
    L is fixed by: after the Cap, the upright circle is even. The clock of the upright circle is exact (beta functions).
    The cap's size is the one number picked by hand (it must stay clear of the flat circle: under 60 degrees).

    rule(cap_degrees) -> M.Rule       python out/r28/pillow3/lean.py   prints the self-test
"""
import os, sys
import numpy as np
from scipy.special import betainc
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import p3
M = p3.M
pi = np.pi
APEX = np.array([-0.5, 0.0, np.sqrt(3) / 2]); A120 = 2 * pi / 3


def upright_clock(s):
    """Angle from +x (even speed) of the point of the upright circle that the angle-true picture has at the angle s."""
    tn = np.tan(0.5 * np.minimum(s, pi / 2)); ct = np.tan(0.5 * (pi - np.maximum(s, pi / 2)))          # tan(s/2), cot(s/2)
    arc = np.where(s <= pi / 2, betainc(1 / 6, 1 / 3, np.clip(tn * tn, 0, 1)) / np.sqrt(3), 1 / np.sqrt(3) + betainc(1 / 3, 1 / 2, np.clip(1 - ct * ct, 0, 1)) / (2 * np.sqrt(3)))
    return 2 * pi * arc / np.sqrt(3)


def cap_f(u):
    return np.cbrt(u) * (1 + 2 * u) / 3


def cap_finv(f):
    v = np.cbrt(np.clip(f, 0, 1))
    for _ in range(40):
        v = v - (v * (1 + 2 * v ** 3) / 3 - f) / ((1 + 8 * v ** 3) / 3)
    return np.clip(v, 0, 1) ** 3


class Layout:
    def __init__(self, cap_deg=50.0):
        self.cap = np.radians(cap_deg); t = p3.TAB['t']; U = upright_clock(t ** 3)
        r = U - A120; inside = np.abs(r) < self.cap
        self.L = np.where(inside, A120 + np.sign(r) * self.cap * cap_finv(np.abs(r) / self.cap), U); self.L[0] = 0.0; self.L[-1] = pi
        self.U = U; self.S = p3.TAB['S']; self.t = t
        self.dS = np.gradient(self.S, t); self.dL = np.gradient(self.L, t)

    def _cap(self, X, Y, Z, inverse):
        sg = np.where(Z < 0, -1.0, 1.0); Za = np.abs(Z)
        cr = np.clip(X * APEX[0] + Za * APEX[2], -1, 1)
        tx, ty, tz = X - cr * APEX[0], Y, Za - cr * APEX[2]; tl = np.sqrt(tx * tx + ty * ty + tz * tz); r = np.arctan2(tl, cr)
        ins = (r < self.cap) & (tl > 0); u = np.where(ins, r / self.cap, 0.5)
        r2 = self.cap * (cap_finv(u) if inverse else cap_f(u)); tls = np.where(tl > 0, tl, 1.0); c2, s2 = np.cos(r2), np.sin(r2) / tls
        return np.where(ins, c2 * APEX[0] + s2 * tx, X), np.where(ins, s2 * ty, Y), sg * np.where(ins, c2 * APEX[2] + s2 * tz, Za)

    def fwd(self, t, f):
        f = f - 0.5 * (1 - p3.k_of_t(t)) * np.sin(2 * f); c2 = np.cos(f) ** 2
        s = c2 * np.interp(t, self.t, self.S) + (1 - c2) * np.interp(t, self.t, self.L); sn = np.sin(s)
        return self._cap(np.cos(s), sn * np.cos(f), sn * np.sin(f), False)

    def inv(self, X, Y, Z):
        X, Y, Z = self._cap(X, Y, Z, True)
        s = np.arctan2(np.sqrt(Y * Y + Z * Z), X); f = np.arctan2(Z, Y); c2 = np.cos(f) ** 2
        lo = np.zeros_like(s); hi = np.full_like(s, p3.TMAX)
        for _ in range(26):                                       # halving on a rising function (plain Newton hops to and fro at the corner a)
            t = 0.5 * (lo + hi)
            g = c2 * np.interp(t, self.t, self.S) + (1 - c2) * np.interp(t, self.t, self.L) - s
            hi = np.where(g > 0, t, hi); lo = np.where(g <= 0, t, lo)
        t = 0.5 * (lo + hi)
        for _ in range(3):                                        # polish (the function is a broken line: one step lands exactly)
            g = c2 * np.interp(t, self.t, self.S) + (1 - c2) * np.interp(t, self.t, self.L) - s
            d = c2 * np.interp(t, self.t, self.dS) + (1 - c2) * np.interp(t, self.t, self.dL)
            t = np.clip(t - g / np.maximum(d, 1e-12), lo, hi)
        return t, 0.5 * p3.kepler(2 * f, 1 - p3.k_of_t(t))

    def G(self, X, Y, Z):
        return self.fwd(*p3.R_tf(*self.inv(X, Y, Z)))

    def F(self, x, y, z):
        sh = np.shape(x); x, y, z = (np.ravel(np.asarray(v, float)) for v in (x, y, z))
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); ok = r > 0; ri = 1 / np.where(ok, r, 1.0)
        dx, dy, dz = self.G(x * ri, y * ri, z * ri); ox, oy, oz = dx * r2, dy * r2, dz * r2
        flat = z == 0
        if flat.any():
            wv = (x[flat] + 1j * y[flat]) ** 2; ox[flat], oy[flat], oz[flat] = wv.real, wv.imag, 0.0
        ox[~ok] = 0; oy[~ok] = 0; oz[~ok] = 0
        return ox.reshape(sh), oy.reshape(sh), oz.reshape(sh)


_L = {}


def layout(cap_deg=50.0):
    if cap_deg not in _L:
        _L[cap_deg] = Layout(cap_deg)
    return _L[cap_deg]


def rule(cap_deg=50.0):
    return M.fixed(layout(cap_deg).F, 'pillow3-B%g' % cap_deg, 'three-corner pillow, one corner on the flat circle, both circles even (cap %g)' % cap_deg)


if __name__ == '__main__':
    rng = np.random.default_rng(3)
    for cap in (50.0,):
        Lb = layout(cap); p = rng.normal(size=(3, 200000)); p /= np.sqrt((p * p).sum(0))
        q = np.array(Lb.fwd(*Lb.inv(*p))); print('cap %g: round trip direction -> pillow -> direction: largest error %.1e' % (cap, np.abs(q - p).max()))
        print('   the two clocks rise: belt %s, upright %s; upright clock at the corner a: %.3f degrees' % (bool((np.diff(Lb.S) > 0).all()), bool((np.diff(Lb.L) > 0).all()), np.degrees(float(upright_clock(np.array([pi / 2]))[0]))))
        a = rng.uniform(0, 2 * pi, 100000); g = np.array(Lb.G(np.cos(a), 0 * a, np.sin(a)))
        print('   upright circle against doubling: largest error %.1e, largest |y| %.1e' % (max(np.abs(g[0] - np.cos(2 * a)).max(), np.abs(g[2] - np.sin(2 * a)).max()), np.abs(g[1]).max()))
        g = np.array(Lb.G(np.cos(a), np.sin(a), 0 * a)); print('   flat circle against doubling: largest error %.1e' % max(np.abs(g[0] - np.cos(2 * a)).max(), np.abs(g[1] - np.sin(2 * a)).max()))
        for q0 in p3.pre_q(np.inf):
            t = np.cbrt(np.array([2 * np.arctan(abs(q0))])); d = np.array(Lb.fwd(t, np.array([np.angle(q0)]))).ravel()
            print('   a direction sent to -x: %.1f degrees from +x, latitude %.1f' % (np.degrees(np.arccos(np.clip(d[0], -1, 1))), np.degrees(np.arcsin(np.clip(d[2], -1, 1)))))
