"""Round 25, section "wall": a test of W-d. The evenly spaced rule for an ODD power, where it can sit symmetrically.

W-d says an evenly spaced pattern on a ball needs corners; the square pillow has four. Counting on the pillow
(a doughnut x, y in [0, 1) with (x, y) and (-x, -y) glued; corners at x, y in {0, 1/2}): a belt that the power-n map
keeps, with the flat rule z^n on it, and that has the same amount of pillow above and below, is the line y = 1/4,
and "n times y, plus 0 or 1/2" brings 1/4 back to 1/4 only when n is ODD. For n = 2 the only kept belts are at
y = 1/3 and 1/6: lopsided, by force. So the even-spacing idea can be tested fairly only at an odd power:

    cube(x, y) = (3 x, 3 y + 1/2)        (power 5: (5 x, 5 y))

Layout (pillow -> directions): the belt y = 1/4 is the flat circle, x = longitude / 360. The upper half pillow
1/4 <= y <= 1/2 is a band whose top edge is zipped ((x, 1/2) glued to (-x, 1/2)): it is laid on the upper half sphere
with confocal ellipses (Z = cosh(mu + i nu), nu = 2 pi x, mu = 2 pi (1/2 - y)), the two corners opened like fans
(distance from the corner made plain instead of squared, so that nothing is squeezed without bound), the outer
ellipse made the unit circle, and the disc put on the half sphere by a sphere inversion (stereographic). The four
corners come to lie at latitude +-46.6 degrees above and below the directions +x and -x, the two directions that
the flat cube keeps. Nothing is chosen except the shape of this layout.

    python out/r25/wall/pil.py check | cuts | solid <set index> <a|top>
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wall as W
M = W.M
TAU = 2 * np.pi
D0 = 0.5          # how far from a corner the fan reaches (in the ellipse picture, corners 2 apart)


def psi(Z, d0):
    """open the two corners (the foci +-1) like fans: distance d from the focus -> sqrt(d d0) inside d < d0."""
    out = np.array(Z, complex)
    for f in (1.0, -1.0):
        t = Z - f; d = np.abs(t); m = d < d0; ds = np.where(d > 0, d, 1.0)
        out = np.where(m, f + t * np.sqrt(d0 / ds), out)
    return out


def psi_inv(Zt, d0):
    out = np.array(Zt, complex)
    for f in (1.0, -1.0):
        t = Zt - f; e = np.abs(t); m = e < d0
        out = np.where(m, f + t * e / d0, out)
    return out


def make(n=3, fan=True, muc=0.0):
    """muc > 0 ('band' layout): up to the height muc above and below the flat circle the pillow is laid exactly as the
    one-plane rule lays its cylinder (Mercator), so that every direction round the flat picture is treated alike there;
    the zip and the corners are pushed into the cap above (|w| < exp(-muc))."""
    y0 = 0.25; shift = ((1 - n) / 4.0) % 1.0
    assert n % 2 == 1, 'a belt with the same amount of pillow on both sides exists only for odd powers'
    band = TAU * 0.25; mm = band - muc; rc = np.exp(-muc)
    C, S = np.cosh(mm), np.sinh(mm); TH = np.tanh(mm); d0 = min(D0, 0.8 * (C - 1)) if fan else 0.0

    def to_pillow(ux, uy, uz):
        up = uz >= 0; w = (ux + 1j * uy) / (1 + np.abs(uz)); Rw = np.abs(w); outer = Rw >= rc
        w1 = np.where(outer, 1.0, w / rc)
        Rp = np.abs(w1); th = np.angle(w1); k = 1.0 / (np.cos(th) ** 2 * TH + np.sin(th) ** 2 / TH)     # undo the belt correction
        R = k * Rp / (1 - Rp + k * Rp); w1 = R * np.exp(1j * th)
        Zt = C * w1.real + 1j * S * w1.imag
        Z = psi_inv(Zt, d0) if fan else Zt
        zeta = np.arccosh(Z); mu = np.minimum(np.abs(zeta.real), mm); nu = np.where(zeta.real >= 0, zeta.imag, -zeta.imag)
        hgt = np.where(outer, -np.log(np.maximum(Rw, 1e-300)), muc + (mm - mu)); nu = np.where(outer, np.angle(w), nu)
        return (nu / TAU) % 1.0, np.where(up, 0.25 + hgt / TAU, 0.25 - hgt / TAU)

    def from_pillow(x, y):
        up = y >= y0; hgt = np.abs(y - 0.25) * TAU; nu = x * TAU; outer = hgt <= muc
        mu = np.clip(band - hgt, 0.0, mm)
        Z = np.cosh(mu + 1j * nu)
        Zt = psi(Z, d0) if fan else Z
        X, Y = Zt.real / C, Zt.imag / S
        R = np.hypot(X, Y); th = np.arctan2(Y, X); k = 1.0 / (np.cos(th) ** 2 * TH + np.sin(th) ** 2 / TH)  # belt correction: heights beside
        Rp = R / (R + k * (1 - R))                                                                          # the flat circle exactly times n
        w = np.where(outer, np.exp(-hgt + 1j * nu), rc * Rp * np.exp(1j * th)); X, Y = w.real, w.imag; q = X * X + Y * Y
        return 2 * X / (1 + q), 2 * Y / (1 + q), np.where(up, 1.0, -1.0) * (1 - q) / (1 + q)

    def G(ux, uy, uz):
        x, y = to_pillow(ux, uy, uz)
        x2 = n * x; y2 = (n * y + shift) % 1.0
        over = y2 > 0.5; y2 = np.where(over, 1.0 - y2, y2); x2 = np.where(over, -x2, x2) % 1.0
        return from_pillow(x2, y2)

    def F(x, y, z):
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
        tiny = r < 1e-60; rs = np.where(tiny, 1.0, rs)           # a point this near 0 goes to 0 (keeps rounding out of the layout)
        gx, gy, gz = G(np.where(tiny, 1.0, x / rs), np.where(tiny, 0.0, y / rs), np.where(tiny, 0.0, z / rs)); L = np.where(tiny, 0.0, r ** n)
        flat = z == 0
        zz = (x + 1j * y) ** n
        return np.where(flat, zz.real, L * gx), np.where(flat, zz.imag, L * gy), np.where(flat, 0.0, L * gz)
    F.G = G; F.to_pillow = to_pillow; F.from_pillow = from_pillow
    return F


def make_lop(n=2, y0=1.0 / 3.0):
    """The same construction for an EVEN power. The only belts the map keeps are at y = 1/3 (or 1/6): one third of the
    pillow lies above the flat plane and two thirds below, and the map (x, y) -> (-n x, n y) that gives z^n on the belt
    swaps the two sides at every step. Lopsided by force, not by choice."""
    mu_u, mu_l = TAU * (0.5 - y0), TAU * y0; d0 = min(D0, 0.8 * (np.cosh(mu_u) - 1))

    def par(up):
        mm = np.where(up, mu_u, mu_l); return mm, np.cosh(mm), np.sinh(mm), np.tanh(mm)

    def to_pillow(ux, uy, uz):
        up = uz >= 0; mm, C, S, TH = par(up); w = (ux + 1j * uy) / (1 + np.abs(uz))
        Rp = np.abs(w); th = np.angle(w); k = 1.0 / (np.cos(th) ** 2 * TH + np.sin(th) ** 2 / TH)
        R = k * Rp / (1 - Rp + k * Rp); w = R * np.exp(1j * th)
        Z = psi_inv(C * w.real + 1j * S * w.imag, d0)
        zeta = np.arccosh(Z); mu = np.minimum(np.abs(zeta.real), mm); nu = np.where(zeta.real >= 0, zeta.imag, -zeta.imag)
        return (nu / TAU) % 1.0, np.where(up, 0.5 - mu / TAU, mu / TAU)

    def from_pillow(x, y):
        up = y >= y0; mm, C, S, TH = par(up); mu = np.where(up, 0.5 - y, y) * TAU; nu = x * TAU
        Zt = psi(np.cosh(mu + 1j * nu), d0); X, Y = Zt.real / C, Zt.imag / S
        R = np.hypot(X, Y); th = np.arctan2(Y, X); k = 1.0 / (np.cos(th) ** 2 * TH + np.sin(th) ** 2 / TH)
        Rp = R / (R + k * (1 - R)); X, Y = Rp * np.cos(th), Rp * np.sin(th); q = X * X + Y * Y
        return 2 * X / (1 + q), 2 * Y / (1 + q), np.where(up, 1.0, -1.0) * (1 - q) / (1 + q)

    def G(ux, uy, uz):
        x, y = to_pillow(ux, uy, uz)
        x2 = -n * x; y2 = (n * y) % 1.0
        over = y2 > 0.5; y2 = np.where(over, 1.0 - y2, y2); x2 = np.where(over, -x2, x2) % 1.0
        return from_pillow(x2, y2)

    def F(x, y, z):
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
        tiny = r < 1e-60; rs = np.where(tiny, 1.0, rs)           # a point this near 0 goes to 0 (keeps rounding out of the layout)
        gx, gy, gz = G(np.where(tiny, 1.0, x / rs), np.where(tiny, 0.0, y / rs), np.where(tiny, 0.0, z / rs)); L = np.where(tiny, 0.0, r ** n)
        flat = z == 0; zz = (x + 1j * y) ** n
        return np.where(flat, zz.real, L * gx), np.where(flat, zz.imag, L * gy), np.where(flat, 0.0, L * gz)
    F.G = G; F.to_pillow = to_pillow; F.from_pillow = from_pillow
    return F


def rule_lop(n=2):
    return M.fixed(make_lop(n), 'even pillow, power %d' % n, 'power %d on the square pillow: the belt can only sit at one third (lopsided by force)' % n)


def check_lop():
    F = make_lop(2); rng = np.random.default_rng(1)
    u = rng.normal(size=(3, 20000)); u /= np.linalg.norm(u, axis=0); x, y = F.to_pillow(*u); b = F.from_pillow(x, y)
    print('power 2, layout there and back: worst miss %.1e' % float(max(np.abs(p - q).max() for p, q in zip(b, u))))
    lon = rng.uniform(0, TAU, 20000)
    for h in (1e-9, 1e-6, -1e-6, 1e-3):
        g = F.G(np.cos(lon) * np.cos(h), np.sin(lon) * np.cos(h), np.sin(h) + 0 * lon)
        miss = np.angle(np.exp(1j * (np.arctan2(g[1], g[0]) - 2 * lon)))
        print('lift %+.0e: longitude is doubled to within %.1e rad; height angle multiplied by %.3f .. %.3f' % (h, float(np.abs(miss).max()), float((np.arcsin(g[2]) / h).min()), float((np.arcsin(g[2]) / h).max())))
    print('flat check', M.flat_check(rule_lop(2), n=20000, steps=60))


def oneplane_n(n=3):
    def F(x, y, z):
        r, w = W.stereo(x, y, z)
        return W.unstereo(r ** n, w ** n)
    return F


def rule_pillow(n=3, fan=True, muc=0.0):
    return M.fixed(make(n, fan, muc), 'even pillow, power %d%s' % (n, ', band %.2f' % muc if muc else ''),
                   'power %d on the square pillow, belt in the middle (evenly spaced, four corners%s%s)' % (n, '' if fan else ', corners not opened', ', one-plane band of height %.2f' % muc if muc else ''))


def rule_oneplane(n=3):
    return M.fixed(oneplane_n(n), 'one plane, power %d' % n, 'the one-plane rule for the power %d (the baseline)' % n)


def centres():
    """c of z^3 + c whose own orbit comes back to 0 after 2 and after 3 steps."""
    s = np.roots([1, 3, 3, 1, 1]); c3 = np.sqrt(s.astype(complex))
    return 1j, c3


SETS3 = [('c = i (two bodies in turn)', (0.0, 1.0, 0.0)), ('c = -0.2 + 1.1i (three bodies in turn)', None), ('c = 0.3', (0.3, 0.0, 0.0)), ('c = 0.59i', (0.0, 0.59, 0.0))]


def flat_stay_n(zr, zi, cr, ci, steps, n=3, r2=36.0):
    z = np.array(zr, float) + 1j * np.array(zi, float); c = cr + 1j * ci; k = np.zeros(z.shape, np.int32); alive = np.ones(z.shape, bool)
    for _ in range(steps):
        z = np.where(alive, z ** n + c, z); alive &= (z.real ** 2 + z.imag ** 2) < r2; k += alive
    return k


def sets3():
    _, c3 = centres(); c3 = sorted(c3, key=lambda t: -t.imag)
    # pick the period-3 centre with the largest filled set (measured on a coarse grid)
    best = None
    g = np.linspace(-1.6, 1.6, 160); A, B = np.meshgrid(g, g)
    for c in c3:
        if c.imag <= 0:
            continue
        a = float((flat_stay_n(A, B, c.real, c.imag, 60) >= 60).mean())
        if best is None or a > best[0]:
            best = (a, c)
    c = best[1]; out = list(SETS3); out[1] = ('c = %.4f %+.4fi (three bodies in turn)' % (c.real, c.imag), (float(c.real), float(c.imag), 0.0))
    return out


def check():
    F = make(3); rng = np.random.default_rng(1)
    # 1. the layout is its own inverse, and the flat circle is the belt
    u = rng.normal(size=(3, 20000)); u /= np.linalg.norm(u, axis=0)
    x, y = F.to_pillow(*u); b = F.from_pillow(x, y)
    print('layout there and back: worst miss %.1e' % float(max(np.abs(p - q).max() for p, q in zip(b, u))))
    lon = rng.uniform(0, TAU, 20000)
    for h in (1e-9, 1e-6, 1e-3):
        g = F.G(np.cos(lon) * np.cos(h), np.sin(lon) * np.cos(h), np.sin(h) + 0 * lon)
        lon2 = np.arctan2(g[1], g[0]); miss = np.angle(np.exp(1j * (lon2 - 3 * lon)))
        print('lift %.0e: longitude is tripled to within %.1e rad; height angle multiplied by %.3f .. %.3f' % (h, float(np.abs(miss).max()), float((np.arcsin(g[2]) / h).min()), float((np.arcsin(g[2]) / h).max())))
    # 2. flat check for z^3 + c
    r = rule_pillow(3); n = 20000
    for nm, c in sets3():
        zr, zi = rng.uniform(-1.5, 1.5, n), rng.uniform(-1.5, 1.5, n)
        a = M.stay(r, zr, zi, np.zeros(n), c[0], c[1], 0.0, 60) >= 60; b_ = flat_stay_n(zr, zi, c[0], c[1], 60) >= 60
        print('flat check %-40s verdicts that differ: %d of %d (inside: %d)' % (nm, int((a != b_).sum()), n, int(b_.sum())))
    # 3. even spacing: how much the direction map stretches, and how round it keeps small circles
    u = rng.normal(size=(3, 40000)); u /= np.linalg.norm(u, axis=0)
    e1 = np.cross(u.T, [0.0, 0.0, 1.0]).T; e1 /= np.linalg.norm(e1, axis=0); e2 = np.cross(u.T, e1.T).T; h = 1e-5
    g0 = np.array(F.G(*u)); ga = (np.array(F.G(*(u + h * e1))) - g0) / h; gb = (np.array(F.G(*(u + h * e2))) - g0) / h
    E, Fm, Gm = (ga * ga).sum(0), (ga * gb).sum(0), (gb * gb).sum(0); tr, det = E + Gm, E * Gm - Fm * Fm
    s1 = np.sqrt(np.maximum(tr / 2 + np.sqrt(np.maximum(tr * tr / 4 - det, 0)), 0)); s2 = np.sqrt(np.maximum(tr / 2 - np.sqrt(np.maximum(tr * tr / 4 - det, 0)), 1e-300))
    ok = np.isfinite(s1) & (s1 < 1e3)
    print('direction map (power 3 wants 3): larger stretch median %.2f (5%% .. 95%%: %.2f .. %.2f); long over short: median %.2f, 95%% below %.2f, worst %.1f'
          % (float(np.median(s1[ok])), float(np.percentile(s1[ok], 5)), float(np.percentile(s1[ok], 95)), float(np.median((s1 / s2)[ok])), float(np.percentile((s1 / s2)[ok], 95)), float((s1 / s2)[ok].max())))
    # after 4 steps: does the squeeze pile up?
    def Gk(p, k):
        for _ in range(k):
            p = np.array(F.G(*p))
        return p
    for k in (1, 2, 4):
        hh = 1e-7 if k == 4 else 1e-6
        g0 = Gk(u, k); ga = (Gk(u + hh * e1, k) - g0) / hh; gb = (Gk(u + hh * e2, k) - g0) / hh
        E, Fm, Gm = (ga * ga).sum(0), (ga * gb).sum(0), (gb * gb).sum(0); tr, det = E + Gm, E * Gm - Fm * Fm
        s1 = np.sqrt(np.maximum(tr / 2 + np.sqrt(np.maximum(tr * tr / 4 - det, 0)), 0)); s2 = np.sqrt(np.maximum(tr / 2 - np.sqrt(np.maximum(tr * tr / 4 - det, 0)), 1e-300))
        ok = np.isfinite(s1) & (s1 < 3.0 ** k * 30) & (s2 > 0)
        print('   %d steps of the direction map: long over short stretch: median %.2f, 90%% below %.2f   (one plane, same test: see below)' % (k, float(np.median((s1 / s2)[ok])), float(np.percentile((s1 / s2)[ok], 90))))
    P3 = oneplane_n(3)
    def Pk(p, k):
        for _ in range(k):
            q = np.array(P3(*p)); p = q / np.linalg.norm(q, axis=0)
        return p
    for k in (1, 2, 4):
        hh = 1e-7 if k == 4 else 1e-6
        g0 = Pk(u, k); ga = (Pk(u + hh * e1, k) - g0) / hh; gb = (Pk(u + hh * e2, k) - g0) / hh
        E, Fm, Gm = (ga * ga).sum(0), (ga * gb).sum(0), (gb * gb).sum(0)
        stretch = np.sqrt((E + Gm) / 2)
        print('   one plane, %d steps: the stretch itself ranges over 5%% .. 95%%: %.3g .. %.3g (power^steps = %d)' % (k, float(np.percentile(stretch, 5)), float(np.percentile(stretch, 95)), 3 ** k))


def cuts():
    rules = [rule_oneplane(3), rule_pillow(3), rule_pillow(3, fan=False)]
    sets = sets3(); w, h, steps, pad = 280, 280, 40, 8; f = M.font(15)
    cols = [('flat', 0.0), ('upright through the x-axis', 90.0), ('upright across (x = 0)', None)]
    W_ = pad + len(sets) * len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W_, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, (sn, c) in enumerate(sets):
            for k, (cn, ang) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                n = M.cut_across(r, 0.0, w, steps, c=c, L=1.5) if ang is None else M.cut_axis(r, ang, w, h, steps, c=c, box=(-1.5, 1.5, -1.5, 1.5))
                im.paste(Image.fromarray(M.shade(n, steps)), (x, y)); d.text((x + 4, y + 2), sn.split(' (')[0] + ', ' + cn, fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    p = os.path.join(HERE, 'cuts-pillow3.png'); im.save(p); print('wrote', p, im.size)


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if a == 'check':
        print('centres:', centres()); check()
    elif a == 'cuts':
        cuts()
    elif a == 'lop':
        check_lop()
