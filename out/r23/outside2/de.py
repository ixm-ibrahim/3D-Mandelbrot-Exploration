"""Round 23, outside2: the Douady-Earle ("conformal barycentre") extension of z^2 to space, as a rule of the library.

What it is. A point p above the flat plane (upper half-space = hyperbolic 3-space) "sees" the flat plane as a sphere of
view. Push what it sees through z -> z^2. The answer E(p) is the one point of the upper half-space from which the
pushed picture is balanced (its mean direction of view is zero). Douady and Earle (1986) for the disc; Petersen (2011,
arXiv:1102.1470) for rational maps of the sphere and hyperbolic 3-space. It is the extension that commutes with every
sphere inversion map (Moebius map) of the flat plane; no choice is made anywhere. Because z -> z + c is such a map,
E(z^2 + c) = E(z^2) + c: "square, then add c" with a fixed square. Because z^2 commutes with scalings and (doubled)
turns, E(z^2)(v) = |v|^2 (R(L) cos 2 lon, R(L) sin 2 lon, +-T(L)), L = latitude of v: two functions of one variable.
Below the flat plane the mirror image is used.

    python out/r23/outside2/de.py table     compute R(L), T(L), save de_table.npz, print against one plane
    python out/r23/outside2/de.py check     flat check, lift test, turn test, stretches
    python out/r23/outside2/de.py cuts      cuts beside one plane
    python out/r23/outside2/de.py solids    rough solids beside one plane, two eye positions

Load the rule elsewhere:  sys.path.insert(0, 'out/r23/outside2'); import de; r = de.rule()
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M
TABLE = os.path.join(HERE, 'de_table.npz')


def fib_sphere(n):
    i = np.arange(n) + 0.5; z = 1 - 2 * i / n; ph = np.pi * (1 + 5 ** 0.5) * i
    s = np.sqrt(1 - z * z); return s * np.cos(ph), s * np.sin(ph), z


def barycentre(W, w0, s0, tol=1e-13, iters=400):
    """The point (w, s) of the upper half-space from which the boundary points W (complex, equal weights) are balanced."""
    w, s = complex(w0), float(s0)
    for it in range(iters):
        eta = (W - w) / s; a2 = np.abs(eta) ** 2
        big = a2 > 1e300
        a2s = np.where(big, 1.0, a2)
        ux = np.where(big, 0.0, 2 * eta.real / (1 + a2s)); uy = np.where(big, 0.0, 2 * eta.imag / (1 + a2s)); uz = np.where(big, 1.0, (a2s - 1) / (a2s + 1))
        m = np.array([ux.mean(), uy.mean(), uz.mean()])
        if np.abs(m).max() < tol:
            break
        k = 1.5
        w += s * k * (m[0] + 1j * m[1]); s *= np.exp(k * m[2])
    return w, s, float(np.abs(m).max()), it


def table(nL=181, npts=200000):
    ax, ay, az = fib_sphere(npts)
    zeta = (ax + 1j * ay) / (1 - az)                       # the view from p: straight down = 0, straight up = infinity
    Ls = np.linspace(0, np.pi / 2, nL); R = np.zeros(nL); T = np.zeros(nL); res = np.zeros(nL)
    R[0], T[0] = 1.0, 0.0
    t0 = time.time()
    for i in range(1, nL):
        rho, t = np.cos(Ls[i]), np.sin(Ls[i])
        W = (rho + t * zeta) ** 2
        f = 1.0 / (1.0 + t * t)                           # start from the one-plane answer
        w, s, res[i], it = barycentre(W, f * rho * rho, f * 2 * t)
        R[i], T[i] = w.real, s
        if abs(w.imag) > 1e-6:
            print('   warning: not in the upright plane at L = %.1f: %.2e' % (np.degrees(Ls[i]), w.imag))
        if i % 30 == 0:
            print('   L %5.1f  R %.6f  T %.6f  (%d steps, residual %.1e, %.0f s)' % (np.degrees(Ls[i]), R[i], T[i], it, res[i], time.time() - t0)); sys.stdout.flush()
    np.savez(TABLE, L=Ls, R=R, T=T, res=res)
    return Ls, R, T


def load():
    if not os.path.exists(TABLE):
        table()
    d = np.load(TABLE); return d['L'], d['R'], d['T']


def make_F():
    Ls, R, T = load()
    from scipy.interpolate import CubicSpline
    cR, cT = CubicSpline(Ls, R), CubicSpline(Ls, T)

    def F(x, y, z):
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); rs = np.where(r > 0, r, 1.0)
        L = np.arcsin(np.clip(np.abs(z) / rs, 0, 1)); rho2 = x * x + y * y; ok = rho2 > 0; q = np.where(ok, rho2, 1.0)
        c2, s2 = np.where(ok, (x * x - y * y) / q, 1.0), np.where(ok, 2 * x * y / q, 0.0)
        Rv, Tv = cR(L), cT(L)
        return r2 * Rv * c2, r2 * Rv * s2, np.where(z == 0, 0.0, r2 * Tv * np.sign(z))
    return F


def rule():
    return M.fixed(make_F(), 'de', 'Douady-Earle (balanced view) extension of z^2')


def cmd_table():
    Ls, R, T = table()
    one_lat = np.degrees(np.arcsin(2 * np.sin(Ls) / (1 + np.sin(Ls) ** 2)))
    lat = np.degrees(np.arctan2(T, R)); ln = np.hypot(R, T)
    print('\n   latitude of v | latitude of the square: Douady-Earle, one plane | length of the square for |v| = 1: Douady-Earle (one plane: 1)')
    for i in range(0, len(Ls), 15):
        print('   %5.1f | %7.3f  %7.3f | %.5f' % (np.degrees(Ls[i]), lat[i], one_lat[i], ln[i]))
    print('   largest difference of the latitude: %.3f degrees;  length between %.4f and %.4f' % (np.abs(lat - one_lat).max(), ln.min(), ln.max()))
    print('   is the latitude of the square increasing all the way (no fold, no crushed cone)? %s' % bool((np.diff(lat) > 0).all()))


def cmd_check():
    r = rule(); one = M.bench('oneplane'); F = make_F(); rng = np.random.default_rng(2)
    print('flat check', M.flat_check(r, n=20000, steps=60))
    v = rng.normal(size=(3, 20000)); X = F(*v); print('all finite:', bool(all(np.isfinite(t).all() for t in X)))
    a = np.radians(37.0); c, s = np.cos(a), np.sin(a); c2, s2 = np.cos(2 * a), np.sin(2 * a)
    A = F(c * v[0] - s * v[1], s * v[0] + c * v[1], v[2]); B = (c2 * X[0] - s2 * X[1], s2 * X[0] + c2 * X[1], X[2])
    print('turn test (37 degrees about the upright axis): %.1e' % max(np.abs(A[i] - B[i]).max() for i in range(3)))
    # lift test: flat-inside points lifted by a millionth
    n = 20000; zr, zi = rng.uniform(-1.7, 1.7, n), rng.uniform(-1.2, 1.2, n)
    for nm, cc in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
        ins = M.flat_stay(zr, zi, cc[0], cc[1], 80) >= 80
        for rr in (r, one):
            up = M.stay(rr, zr, zi, np.full(n, 1e-6), *cc, 80) >= 80
            print('   lift test %s, %s: %d of %d flat-inside points stay when lifted by 1e-6' % (nm, rr.name, (up & ins).sum(), ins.sum()))
    # volume against one plane, and agreement point by point
    P = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(120000, 3)).T
    for nm, cc in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('San Marco', (-0.75, 0.0, 0.0))):
        a_ = M.stay(r, *P, *cc, 60) >= 60; b_ = M.stay(one, *P, *cc, 60) >= 60
        print('   %s: inside share Douady-Earle %.4f, one plane %.4f; verdicts differ on %.4f of the box; largest |z| inside: %.3f against %.3f'
              % (nm, a_.mean(), b_.mean(), (a_ != b_).mean(), np.abs(P[2][a_]).max(), np.abs(P[2][b_]).max()))
    # stretches by latitude
    h = 1e-6
    for lat in (0.0, 30.0, 60.0, 80.0, 89.0):
        L = np.radians(lat); p = np.array([np.cos(L), 0.0, np.sin(L)]); J = np.zeros((3, 3))
        for j in range(3):
            e = np.zeros(3); e[j] = h
            J[:, j] = (np.array([np.ravel(t)[0] for t in F(*[np.array([q]) for q in p + e])]) - np.array([np.ravel(t)[0] for t in F(*[np.array([q]) for q in p - e])])) / (2 * h)
        sv = np.linalg.svd(J, compute_uv=False); print('   latitude %5.1f: stretches %.3f %.3f %.3f  ratio %.1f  (det %.3f)' % (lat, sv[0], sv[1], sv[2], sv[0] / sv[2], np.linalg.det(J)))


def cmd_cuts():
    from PIL import Image, ImageDraw
    rules = [M.bench('oneplane'), rule()]
    sets = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0))]
    w, h, steps, pad = 330, 240, 60, 8
    cols = [('flat cut', 0.0), ('upright cut through the x-axis', 90.0)]
    W = pad + len(sets) * len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 22), r.name + ': ' + r.label, fill=(235, 220, 170), font=M.font(15))
        for j, (sn, c) in enumerate(sets):
            for k, (cn, ang) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                im.paste(Image.fromarray(M.shade(M.cut_axis(r, ang, w, h, steps, c=c), steps)), (x, y)); d.text((x + 4, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'de-cuts.png')); print('wrote de-cuts.png', im.size)


def cmd_solids():
    rules = [M.bench('oneplane'), rule()]
    sets = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)]
    for cam, tag in (((0.45, 0.5, 1.0), 'a'), ((0.2, 1.0, 0.35), 'top')):
        M.julia_sheet(rules, os.path.join(HERE, 'de-solids-%s.png' % tag), sets=sets, w=300, h=225, nd=170, steps=30, cam=cam, title='Rough solids, eye at %s' % (cam,))
        print('sheet', tag, 'done'); sys.stdout.flush()


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'table'
    {'table': cmd_table, 'check': cmd_check, 'cuts': cmd_cuts, 'solids': cmd_solids}[a]()
