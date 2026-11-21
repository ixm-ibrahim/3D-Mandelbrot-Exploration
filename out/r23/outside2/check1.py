"""Round 23, section outside2: numbers behind verdicts.md.

    python out/r23/outside2/check1.py

A. The lab's one-plane rule against the published formula of Cabrera, Makienko, Sienra (2015), section 4.1.
B. Section 2 (a): the height factor above the rabbit's meeting point, one plane against along.
C. Section 2 (b): turn-about-the-upright-axis test for the rules; a hinge-free, tear-free rule WITH copies of the
   flat picture off the flat plane (a fold), as a counterexample to the statement as it is written.
D. Section 2 (c): the three stretches of a rule |v|^2 G(direction); the branch directions of R_t.
E. How far the one-plane rule is from keeping shapes near the upright axis (it is not quasiregular).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r23', 'me'))
import mem as M
import cone as C

rng = np.random.default_rng(11)


def F_of(rule):
    return lambda x, y, z: rule.step(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), tuple(rule.init(np.size(x))), 0, 0.0, 0.0, 0.0)[:3]


def rotz(a, x, y, z):
    c, s = np.cos(a), np.sin(a); return c * x - s * y, s * x + c * y, z


def equivariance(F, a_deg, n=20000):
    """largest |F(R_a v) - R_2a F(v)| over random points, R_a = turn by a about the upright (z) axis"""
    v = rng.normal(size=(3, n)); a = np.radians(a_deg)
    A = F(*rotz(a, *v)); B = rotz(2 * a, *F(*v))
    return float(max(np.abs(A[i] - B[i]).max() for i in range(3)))


def jac(F, v, h=1e-6):
    """3x3 derivative by central differences at the points v (3, n). Returns (n, 3, 3)."""
    n = v.shape[1]; J = np.zeros((n, 3, 3))
    for j in range(3):
        e = np.zeros((3, 1)); e[j] = h
        a = np.stack(F(*(v + e))); b = np.stack(F(*(v - e)))
        J[:, :, j] = ((a - b) / (2 * h)).T
    return J


def main():
    one = M.bench('oneplane'); along = M.bench('along'); two = M.bench('twoplane'); lathe = M.bench('lathe')
    Fo, Fa, Ft, Fl = F_of(one), F_of(along), F_of(two), F_of(lathe)

    print('== A. one plane against the published "product extension" of z^2 (Cabrera-Makienko-Sienra 2015, sec. 4.1)')
    v = rng.normal(size=(3, 200000)); x, y, z = v; p2 = x * x + y * y + z * z; p = np.sqrt(p2)
    Q = (p2 * (x * x - y * y) / (p2 + z * z), p2 * 2 * x * y / (p2 + z * z), p2 * 2 * z * p / (p2 + z * z))
    P = Fo(x, y, z)
    print('   largest difference over 200,000 random points: %.2e' % max(np.abs(Q[i] - P[i]).max() for i in range(3)))
    # their product: lengths multiply, longitudes add, Mercator latitudes add.  Check: v * v = one plane
    mu = np.arctanh(np.clip(z / p, -1 + 1e-15, 1 - 1e-15)); lon = np.arctan2(y, x)
    r2, mu2, lon2 = p2, 2 * mu, 2 * lon
    S = (r2 * np.cos(lon2) / np.cosh(mu2), r2 * np.sin(lon2) / np.cosh(mu2), r2 * np.tanh(mu2))
    print('   "lengths multiply, longitudes add, Mercator latitudes add", v * v against one plane: %.2e' % max(np.abs(S[i] - P[i]).max() for i in range(3)))

    print('\n== B. section 2 (a): height factor one step above the rabbit\'s meeting point')
    c = complex(M.RABBIT[0], M.RABBIT[1]); al = (1 - np.sqrt(1 - 4 * c)) / 2
    print('   meeting point alpha = %.4f %+.4f i   (check alpha^2 + c - alpha = %.1e)' % (al.real, al.imag, abs(al * al + c - al)))
    for h in (0.01, 0.075, 0.15):
        row = []
        for nm, F in (('one plane', Fo), ('along', Fa), ('two planes', Ft)):
            X, Y, Z = F(np.array([al.real]), np.array([al.imag]), np.array([h]))
            row.append('%s %.3f' % (nm, Z[0] / h))
        print('   height %.3f: image height / height:  %s' % (h, ',  '.join(row)))
    # where does the image lie relative to the x-axis (sign of y), for along's tilted plane argument
    X, Y, Z = Fa(np.array([al.real]), np.array([al.imag]), np.array([0.075]))
    print('   along: start (x %.3f, y %.3f, z 0.075) -> square (x %.3f, y %.3f, z %.3f): the y sign flips: %s' % (al.real, al.imag, X[0], Y[0], Z[0], Y[0] * al.imag < 0))

    print('\n== C. section 2 (b): is the rule hinge-free?  largest |F(R_a v) - R_2a F(v)|, R_a a turn about the upright axis')
    conep = C.RULES['conep'](); Fc = F_of(conep); coneraw = C.RULES['coneraw'](); Fr = F_of(coneraw)
    for nm, F in (('one plane', Fo), ('lathe', Fl), ('two planes', Ft), ('along', Fa), ('cone+ (blended)', Fc), ('cone raw R_t', Fr)):
        print('   %-18s' % nm + '  '.join('a=%g: %.1e' % (a, equivariance(F, a)) for a in (37.0, 90.0, 120.0, 180.0)))

    # the counterexample: latitude L -> L up to 30 degrees, 90 - 2L beyond (so the pole goes to the opposite pole); then one plane.
    def fold_pre(x, y, z):
        r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
        L = np.arcsin(np.clip(z / rs, -1, 1)); a = np.abs(L); L0 = np.radians(30.0)
        L2 = np.sign(L) * np.where(a <= L0, a, np.pi / 2 - 2 * a)
        rho = np.hypot(x, y); ok = rho > 0; cx = np.where(ok, x / np.where(ok, rho, 1), 1.0); cy = np.where(ok, y / np.where(ok, rho, 1), 0.0)
        return r * np.cos(L2) * cx, r * np.cos(L2) * cy, r * np.sin(L2)

    def Ffold(x, y, z):
        return Fo(*fold_pre(x, y, z))
    fold = M.fixed(Ffold, 'fold30', 'latitude folded back at 30 degrees, then one plane (hinge-free, tear-free)')
    print('   %-18s' % 'fold30' + '  '.join('a=%g: %.1e' % (a, equivariance(Ffold, a)) for a in (37.0, 90.0, 120.0, 180.0)))
    # tear-free? largest jump between close pairs of directions, everywhere and next to the poles
    a_ = rng.normal(size=(3, 200000)); a_ /= np.linalg.norm(a_, axis=0)
    for tag, pts in (('anywhere', a_), ('within 0.5 degrees of the upright axis', np.stack([a_[0] * 0.008, a_[1] * 0.008, np.sign(a_[2])]) / np.linalg.norm(np.stack([a_[0] * 0.008, a_[1] * 0.008, np.sign(a_[2])]), axis=0))):
        b_ = pts + 1e-6 * rng.normal(size=pts.shape); b_ /= np.linalg.norm(b_, axis=0)
        d = np.linalg.norm(np.stack(Ffold(*pts)) - np.stack(Ffold(*b_)), axis=0)
        print('   fold30: largest move of the square when the direction moves 1e-6, %s: %.1e' % (tag, d.max()))
    f = M.flat_check(fold, n=20000, steps=60)
    print('   fold30 flat check:', f)
    # the 45-degree cone carries the flat picture: lift flat-inside points onto the cone, for the RABBIT
    n = 40000; zr, zi = rng.uniform(-1.6, 1.6, n), rng.uniform(-1.3, 1.3, n)
    ins = M.flat_stay(zr, zi, M.RABBIT[0], M.RABBIT[1], 80) >= 80
    rr = np.hypot(zr, zi); k = np.cos(np.radians(45.0))
    on = M.stay(fold, zr * k, zi * k, rr * np.sin(np.radians(45.0)), *M.RABBIT, 80) >= 80
    print('   fold30, rabbit: points on the 45-degree cone, verdict against the flat picture drawn on the cone: %d of %d differ (inside: %d)' % ((on != ins).sum(), n, ins.sum()))
    for dl in (0.5, 2.0, 5.0):
        for sgn in (+1, -1):
            La = np.radians(45.0 + sgn * dl)
            o2 = M.stay(fold, zr * np.cos(La), zi * np.cos(La), rr * np.sin(La), *M.RABBIT, 80) >= 80
            print('   fold30, rabbit: the same points moved to latitude %.1f: %d of the %d inside ones stay' % (45 + sgn * dl, (o2 & ins).sum(), ins.sum()))
    # winding and stretch on that cone
    th = np.linspace(0, 2 * np.pi, 2001); G = Ffold(k * np.cos(th), k * np.sin(th), np.full_like(th, np.sin(np.radians(45.0))))
    lon = np.unwrap(np.arctan2(G[1], G[0])); print('   fold30: the 45-degree cone goes %.2f times round the flat plane; stretch along the circle %.3f (2 would keep shapes)' % ((lon[-1] - lon[0]) / (2 * np.pi), 2 / k))

    print('\n== D. section 2 (c): the three stretches of |v|^2 G(direction) at random points (derivative by differences)')
    v = rng.normal(size=(3, 4000)); v *= rng.uniform(0.3, 1.5, 4000) / np.linalg.norm(v, axis=0)
    for nm, F in (('one plane', Fo), ('cone raw R_t', Fr)):
        J = jac(F, v); r = np.linalg.norm(v, axis=0); u = v / r
        sv = np.linalg.svd(J, compute_uv=False)
        radial = np.linalg.norm(np.einsum('nij,jn->ni', J, u), axis=1)          # stretch along the ray
        print('   %-14s stretch along the ray / (2|v|): %.6f..%.6f;  the other two stretches equal each other to %.1e (angle-true on the sphere of directions)'
              % (nm, (radial / (2 * r)).min(), (radial / (2 * r)).max(), np.abs(np.sort(sv, axis=1)[:, 0] / np.sort(sv, axis=1)[:, 1] - 1).max() if nm == 'one plane' else np.nan))
        lat = np.degrees(np.arcsin(u[2])); srt = np.sort(sv / r[:, None], axis=1)
        for lo, hi in ((0, 2), (28, 32), (58, 62), (85, 90)):
            m = (np.abs(lat) >= lo) & (np.abs(lat) < hi)
            if m.any():
                print('      latitude %2d..%2d: the three stretches / |v|: %.3f..%.3f, %.3f..%.3f, %.3f..%.3f' % (lo, hi, srt[m, 0].min(), srt[m, 0].max(), srt[m, 1].min(), srt[m, 1].max(), srt[m, 2].min(), srt[m, 2].max()))
    t = C.T15
    w3 = np.roots([t, -(2 - 4 * t * t), t])
    print('   R_t branch directions: w^3 = %s -> |w| = %s -> latitude %s degrees, three on each side (Riemann-Hurwitz: 2*4-2 = 6 in all)'
          % (np.round(w3, 4), np.round(np.abs(w3) ** (1 / 3), 4), np.round(np.degrees(2 * np.arctan(np.abs(w3) ** (1 / 3)) - np.pi / 2), 2)))
    for w3v in w3:
        for kk in range(3):
            w = abs(w3v) ** (1 / 3) * np.exp(2j * np.pi * kk / 3 + (0 if w3v > 0 else 1j * np.pi / 3))
            R = (w ** 3 + t) / (w * (1 + t * w ** 3))
            print('      branch direction lat %6.2f lon %7.2f -> lat %6.2f lon %7.2f' % (np.degrees(2 * np.arctan(abs(w)) - np.pi / 2), np.degrees(np.angle(w)), np.degrees(2 * np.arctan(abs(R)) - np.pi / 2), np.degrees(np.angle(R))))

    print('\n== E. one plane near the upright axis: largest stretch / smallest stretch')
    for lat in (0.0, 30.0, 60.0, 80.0, 89.0, 89.9):
        L = np.radians(lat); pts = np.array([[np.cos(L)], [0.0], [np.sin(L)]]) * 0.9
        sv = np.linalg.svd(jac(Fo, pts, 1e-7), compute_uv=False)[0]
        print('   latitude %5.1f: stretches %.4f %.4f %.4f  ratio %.1f' % (lat, sv[0], sv[1], sv[2], sv[0] / sv[2]))


if __name__ == '__main__':
    main()
