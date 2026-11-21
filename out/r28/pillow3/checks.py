"""Round 28, pillow3: the checks of the build.   python out/r28/pillow3/checks.py > out/r28/pillow3/checks.log"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import p3
M = p3.M
rng = np.random.default_rng(11)
SETS = [('c = -1', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2]), ('c = -0.75', (-0.75, 0.0)), ('Siegel disc', M.SIEGEL[:2])]


def unit(v):
    return v / np.sqrt((v * v).sum(0))


def sph(lon, lat):
    return np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)


for fan in (True, False):
    r = p3.rule(fan); print('=== %s' % r.name)
    # 1. flat check, four sets
    n = 20000; zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); zero = np.zeros(n)
    for nm, c in SETS:
        a = M.stay(r, zr, zi, zero, c[0], c[1], 0.0, 60) >= 60; b = M.flat_stay(zr, zi, c[0], c[1], 60) >= 60
        print('1. flat check %-12s %d of %d verdicts differ (inside: %d)' % (nm, int((a != b).sum()), n, int(b.sum())))
    fc = M.flat_check(r, n=20000, steps=60); print('1. bench flat_check:', fc)
    # 2. the belt through the general formula (not the special case z == 0)
    th = rng.uniform(0, 2 * np.pi, 200000); g = p3.G(np.cos(th), np.sin(th), 0 * th, fan)
    print('2. belt by the general formula against doubling: largest error %.1e, largest |z| %.1e' % (max(np.abs(g[0] - np.cos(2 * th)).max(), np.abs(g[1] - np.sin(2 * th)).max()), np.abs(g[2]).max()))
    for eps in (1e-6, 1e-9, 1e-12):
        g = np.array(p3.G(*sph(th, np.full_like(th, eps)), fan)); d = np.array(sph(2 * th, np.full_like(th, 2 * eps)))
        print('   a hair (%.0e) above the belt: image against (doubled longitude, doubled height): largest gap %.1e' % (eps, np.sqrt(((g - d) ** 2).sum(0)).max()))
    # 3. tears: pairs of directions 2e-7 apart, on either side of each line where the formula changes branch
    h = 1e-7; m = 40000; u = rng.uniform(0, 2 * np.pi, m)

    def pair(p_minus, p_plus, name):
        a = np.array(p3.G(*unit(np.array(p_minus)), fan)); b = np.array(p3.G(*unit(np.array(p_plus)), fan))
        d = np.sqrt(((a - b) ** 2).sum(0)); print('3. across %-58s images at most %.1e apart (median %.1e)' % (name, d.max(), np.median(d)))
    pair(sph(u, -h + 0 * u), sph(u, h + 0 * u), 'the flat circle:')
    pair((np.cos(u), -h + 0 * u, np.sin(u)), (np.cos(u), h + 0 * u, np.sin(u)), 'the upright circle through the x-axis:')
    sw = float(p3.S_of_t(np.cbrt(np.array([np.pi / 2])))[0])
    for dd, nm in ((sw, 'the circle %.1f degrees from +x (the formula swaps form):' % np.degrees(sw)), (np.pi / 2, 'the circle 90 degrees from +x:')):
        pair((np.cos(dd - h) + 0 * u, np.sin(dd - h) * np.cos(u), np.sin(dd - h) * np.sin(u)), (np.cos(dd + h) + 0 * u, np.sin(dd + h) * np.cos(u), np.sin(dd + h) * np.sin(u)), nm)
    for sg, nm in ((1.0, '+x'), (-1.0, '-x')):
        pair((sg + 0 * u, h * np.cos(u), h * np.sin(u)), (sg + 0 * u, -h * np.cos(u), -h * np.sin(u)), 'the direction %s (opposite sides, 2e-7 apart):' % nm)
    p = unit(rng.normal(size=(3, 400000))); t = rng.normal(size=p.shape); t -= (t * p).sum(0) * p; t = unit(t)
    for hh in (1e-5, 1e-7):
        st = np.sqrt(((np.array(p3.G(*unit(p + hh * t), fan)) - np.array(p3.G(*p, fan))) ** 2).sum(0)) / hh
        print('3. 400000 random pairs %.0e apart: stretch median %.3f, 5..95 %% %.3f..%.3f, largest %.1f (a tear would show as about %.0e)' % (hh, np.median(st), np.percentile(st, 5), np.percentile(st, 95), st.max(), 1 / hh))
    # 4. no NaN, length squared
    v = rng.normal(size=(3, 200000)) * rng.uniform(0, 2.5, 200000); X, Y, Z, _ = r.step(v[0], v[1], v[2], (), 0, 0, 0, 0)
    sp = np.array([[0, 0, 0], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], [1e-300, 0, 0], [-1, 1e-17, 1e-17], [1, 0, 1e-300], [-1, 0, 1e-300], [0, 1e-200, 1], [-0.618, 0, 1e-9]], float).T
    Xs, Ys, Zs, _ = r.step(sp[0], sp[1], sp[2], (), 0, 0, 0, 0)
    print('4. all finite on 200000 random points: %s; on %d special points: %s; length squared: largest error %.1e'
          % (bool(np.isfinite(X).all() & np.isfinite(Y).all() & np.isfinite(Z).all()), sp.shape[1], bool(np.isfinite(Xs).all() & np.isfinite(Ys).all() & np.isfinite(Zs).all()), np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (v * v).sum(0)).max()))
    # 5. the push off the flat plane, by longitude
    lon = np.linspace(0, 2 * np.pi, 7201)[:-1] + 1e-4; eps = 1e-6
    up = np.arcsin(np.array(p3.G(*sph(lon, eps + 0 * lon), fan))[2]) / eps
    print('5. push off the flat plane (should be 2): smallest %.4f at longitude %.1f, largest %.4f at longitude %.1f; share of longitudes within 1 %% of 2: %.3f'
          % (up.min(), np.degrees(lon[up.argmin()]), up.max(), np.degrees(lon[up.argmax()]), np.mean(np.abs(up - 2) < 0.02)))
    sh = np.array(p3.G(*sph(lon, eps + 0 * lon), fan)); dl = np.angle(np.exp(1j * (np.arctan2(sh[1], sh[0]) - 2 * lon))) / eps
    print('   lean along the belt per unit of height (should be 0): largest %.2e' % np.abs(dl).max())
    # 6. the two mirrors
    a = np.array(p3.G(p[0], p[1], -p[2], fan)); b = np.array(p3.G(*p, fan)); b[2] *= -1; e1 = np.abs(a - b).max()
    a = np.array(p3.G(p[0], -p[1], p[2], fan)); b = np.array(p3.G(*p, fan)); b[1] *= -1; e2 = np.abs(a - b).max()
    a = np.array(p3.G(-p[0], -p[1], p[2], fan)); b = np.array(p3.G(*p, fan)); e3 = np.sqrt(((a - b) ** 2).sum(0))
    print('6. mirror in the flat plane: largest error %.1e; mirror in the upright plane through the x-axis: %.1e; half turn about the upright axis (four-corner pillows undo it): median gap of the images %.2f (not a symmetry)' % (e1, e2, np.median(e3)))
    # 7. how often the ball is covered, and the squeeze
    n = 1400; lat = (np.arange(n) + 0.5) / n * np.pi - np.pi / 2; lo = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi; LA, LO = np.meshgrid(lat, lo, indexing='ij'); hh = 1e-6

    def GG(la, lo_):
        return np.stack(p3.G(*sph(lo_, la), fan), -1)
    g = GG(LA, LO); a = (GG(LA + hh, LO) - GG(LA - hh, LO)) / (2 * hh); b = (GG(LA, LO + hh) - GG(LA, LO - hh)) / (2 * hh) / np.cos(LA)[..., None]
    det = (np.cross(b, a) * g).sum(-1); dA = np.cos(LA) * (np.pi / n) ** 2
    aa, bb, ab = (a * a).sum(-1), (b * b).sum(-1), (a * b).sum(-1); tr, dd = aa + bb, np.sqrt(np.maximum((aa - bb) ** 2 + 4 * ab * ab, 0))
    s1, s2 = np.sqrt((tr + dd) / 2), np.sqrt(np.maximum((tr - dd) / 2, 1e-300)); sq = s1 / s2; okk = np.isfinite(det) & (np.abs(det) < 1e4)
    wq = lambda q: float(np.sort(sq[okk])[np.searchsorted(np.cumsum(dA[okk][np.argsort(sq[okk])]) / dA[okk].sum(), q)])
    print('7. the ball is covered %.3f times; share folded over %.5f; squeeze (larger over smaller stretch) by area: median %.2f, 90 %% below %.2f, 99 %% below %.2f; larger stretch median %.2f, smaller %.2f'
          % ((det * dA)[okk].sum() / (4 * np.pi), (dA * (det < 0))[okk].sum() / dA[okk].sum(), wq(0.5), wq(0.9), wq(0.99), np.median(s1[okk]), np.median(s2[okk])))
    ang = np.degrees(np.arccos(np.clip(np.cos(LA) * np.cos(LO), -1, 1)))               # angle from +x
    for lo_, hi_ in ((0, 10), (10, 30), (30, 60), (60, 90), (90, 120), (120, 150), (150, 170), (170, 180)):
        mk = okk & (ang >= lo_) & (ang < hi_)
        print('   %3d..%3d degrees from +x: squeeze median %.2f, largest %.2f; stretch across the circles about the x-axis (median) %.2f' % (lo_, hi_, np.median(sq[mk]), sq[mk].max(), np.median(s1[mk])))
    # 8. where the first directions go: everything sent to +x and to -x
    for nm, q0 in (('+x', 0.0), ('-x', np.inf)):
        out = []
        for q in ([0.0, np.inf] if q0 == 0.0 else p3.pre_q(np.inf)):
            d = np.array([-1.0, 0.0, 0.0]) if np.isinf(q) else p3.dir_of_q(complex(q), fan)
            gd = np.array(p3.G(np.array([d[0]]), np.array([d[1]]), np.array([d[2]]), fan)).ravel()
            out.append('longitude %.1f latitude %.1f (angle from +x %.1f; its image is (%.3f, %.3f, %.3f))' % (np.degrees(np.arctan2(d[1], d[0])) % 360, np.degrees(np.arcsin(np.clip(d[2], -1, 1))), np.degrees(np.arccos(np.clip(d[0], -1, 1))), *gd))
        print('8. directions sent to %s:\n      %s' % (nm, '\n      '.join(out)))
    ap = p3.dir_of_q(1j, fan); print('   the corner off the belt sits at latitude %.1f, %.1f degrees from +x' % (np.degrees(np.arcsin(ap[2])), np.degrees(np.arccos(ap[0]))))
