"""Round 28, skeptic of Track B: the checks of the build, written again from nothing.

    PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -W ignore out/r28/skeptic/sk_checks.py A|B|plain > out/r28/skeptic/checks-A.log

Loads the explorer's rule (out/r28/pillow3/p3.py, lean.py) and nothing else of theirs. The flat truth is my own
complex orbit. The point of difference with the explorer's checks: their rule has a special case "z == 0 -> the flat
rule", so a flat check with z = 0 exactly only tests that special case. Here the flat check is ALSO run
  (a) through the general formula with the special case switched off,
  (b) a hair beside the flat plane (z = 1e-12, 1e-9, 1e-6), where the special case cannot act.
"""
import os, sys, time
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'pillow3'))
import p3, lean
M = p3.M
WHICH = sys.argv[1] if len(sys.argv) > 1 else 'A'
if WHICH == 'A':
    Gdir = lambda X, Y, Z: p3.G(X, Y, Z, True); RULE = p3.rule(True)
elif WHICH == 'plain':
    Gdir = lambda X, Y, Z: p3.G(X, Y, Z, False); RULE = p3.rule(False)
else:
    LB = lean.layout(50.0); Gdir = LB.G; RULE = lean.rule(50.0)
RABBIT = (-0.122561, 0.744862)
SETS = [('c = -1', (-1.0, 0.0)), ('rabbit', RABBIT), ('rabbit mirrored', (RABBIT[0], -RABBIT[1])), ('c = -0.75', (-0.75, 0.0)), ('c = i (no inside at all)', (0.0, 1.0))]
rng = np.random.default_rng(2028)
T0 = time.time()


def say(*a):
    print(*a); sys.stdout.flush()


def Fgen(x, y, z):
    """The rule WITHOUT its special case for z == 0: length squared times the direction map."""
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); ok = r > 0; ri = 1 / np.where(ok, r, 1.0)
    gx, gy, gz = Gdir(x * ri, y * ri, z * ri)
    return np.where(ok, gx * r2, 0.0), np.where(ok, gy * r2, 0.0), np.where(ok, gz * r2, 0.0)


def Frule(x, y, z):
    X, Y, Z, _ = RULE.step(x, y, z, (), 0, 0.0, 0.0, 0.0); return X, Y, Z


def my_stay(F, x, y, z, c, steps, r2=36.0, track=False):
    """True where the orbit never leaves the ball of radius 6. track: also the largest |z| met by orbits that stay,
    and whether anything not finite turned up."""
    x, y, z = (np.array(v, float) for v in (x, y, z)); alive = np.ones(x.shape, bool); zmax = np.zeros(x.shape); bad = 0
    for _ in range(steps):
        X, Y, Z = F(x[alive], y[alive], z[alive])
        bad += int((~np.isfinite(X) | ~np.isfinite(Y) | ~np.isfinite(Z)).sum())
        x[alive], y[alive], z[alive] = X + c[0], Y + c[1], Z
        alive &= (x * x + y * y + z * z) < r2
        if track:
            zmax = np.where(alive, np.maximum(zmax, np.abs(z)), zmax)
    return (alive, zmax, bad) if track else alive


def true_flat(zr, zi, c, steps, r2=36.0):
    """My own flat truth: the complex orbit z -> z^2 + c, the same count."""
    z = np.array(zr, float) + 1j * np.array(zi, float); cc = complex(*c); alive = np.ones(z.shape, bool)
    for _ in range(steps):
        z = np.where(alive, z * z + cc, z); alive &= (z.real ** 2 + z.imag ** 2) < r2
    return alive


def unit(v):
    return v / np.sqrt((v * v).sum(0))


say('=== skeptic checks of layout %s (%s)' % (WHICH, RULE.name))
# ------------------------------------------------------------------ 1. the flat check
n = 20000; zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); zero = np.zeros(n)
for nm, c in SETS:
    tr = true_flat(zr, zi, c, 60); tr200 = true_flat(zr, zi, c, 200)
    a_rule = my_stay(Frule, zr, zi, zero, c, 60)
    a_bench = M.stay(RULE, zr, zi, zero, c[0], c[1], 0.0, 60) >= 60
    a_gen, zmax, bad = my_stay(Fgen, zr, zi, zero, c, 60, track=True)
    say('1. %-26s inside (true flat picture, 60 steps): %5d of %d | differ: the rule as shipped %d (bench M.stay: %d) | general formula, special case off: %d, largest |z| on orbits that stay %.1e, not finite %d | (60 against 200 steps of the truth itself: %d)'
        % (nm, int(tr.sum()), n, int((a_rule != tr).sum()), int((a_bench != tr).sum()), int((a_gen != tr).sum()), float(zmax[a_gen].max()) if a_gen.any() else 0.0, bad, int((tr != tr200).sum())))
    for eps in (1e-12, 1e-9, 1e-6, 1e-3):
        a, zmax, bad = my_stay(Frule, zr, zi, np.full(n, eps), c, 60, track=True)
        b = my_stay(Frule, zr, zi, np.full(n, -eps), c, 60)
        say('      started %.0e above the flat plane: %d verdicts differ from the flat picture (below: %d); largest |z| on orbits that stay: %.1e; not finite: %d'
            % (eps, int((a != tr).sum()), int((b != tr).sum()), float(zmax[a].max()) if a.any() else 0.0, bad))
# the flat circle through the general formula, and one squaring of a flat point through the general formula
th = rng.uniform(0, 2 * np.pi, 400000); g = np.array(Gdir(np.cos(th), np.sin(th), 0 * th))
say('1. flat circle through the general formula against doubling: largest error %.1e; largest |z| of the image %.1e' % (max(np.abs(g[0] - np.cos(2 * th)).max(), np.abs(g[1] - np.sin(2 * th)).max()), np.abs(g[2]).max()))
x, y = rng.uniform(-2, 2, 400000), rng.uniform(-2, 2, 400000); X, Y, Z = Fgen(x, y, 0 * x); w = (x + 1j * y) ** 2
say('1. one squaring of 400000 flat points through the general formula against z^2: largest error %.1e; strays off the flat plane by at most %.1e' % (max(np.abs(X - w.real).max(), np.abs(Y - w.imag).max()), np.abs(Z).max()))
X, Y, Z = Frule(x, y, 0 * x); say('1. the same through the rule as shipped (special case on): error %.1e, strays %.1e' % (max(np.abs(X - w.real).max(), np.abs(Y - w.imag).max()), np.abs(Z).max()))
say('   [%.0f s]' % (time.time() - T0))

# ------------------------------------------------------------------ 2. tears, without naming the seams
# Long closed sweeps: great circles in random position and small circles round marked directions, walked in tiny
# steps. A tear of size J anywhere on the way shows as one step whose image jumps by J.
def sweep(points, label, closed=True):
    g = np.array(Gdir(*points)); d = np.sqrt(((np.roll(g, -1, 1) - g) ** 2).sum(0)); s = np.sqrt(((np.roll(points, -1, 1) - points) ** 2).sum(0))
    if not closed:
        d, s = d[:-1], s[:-1]
    fin = bool(np.isfinite(g).all()); return d.max(), (d / s).max(), fin


worst = (0.0, 0.0); allfin = True; NS = 400000 if WHICH != 'B' else 100000; NC = 60 if WHICH != 'B' else 24
for i in range(NC):
    a = unit(rng.normal(size=3)); b = rng.normal(size=3); b -= (a * b).sum() * a; b = unit(b); u = np.linspace(0, 2 * np.pi, NS, endpoint=False)
    P = a[:, None] * np.cos(u) + b[:, None] * np.sin(u); jm, st, fin = sweep(P, 'great'); worst = max(worst, (jm, st)); allfin &= fin
say('2. %d great circles in random position, %d steps each (step %.1e): largest jump of the image in one step %.1e (largest stretch %.1f); all finite: %s' % (NC, NS, 2 * np.pi / NS, worst[0], worst[1], allfin))
# the named great circles themselves are seams' neighbours: circles a hair to either side of them
h = 3e-8; res = []
for nm, nrm in (('flat circle', (0, 0, 1)), ('upright circle through the x-axis', (0, 1, 0)), ('upright circle across the x-axis', (1, 0, 0))):
    nrm = np.array(nrm, float); e1 = np.roll(nrm, 1); e2 = np.cross(nrm, e1); u = rng.uniform(0, 2 * np.pi, 200000)
    base = e1[:, None] * np.cos(u) + e2[:, None] * np.sin(u)
    ga = np.array(Gdir(*unit(base + h * nrm[:, None]))); gb = np.array(Gdir(*unit(base - h * nrm[:, None]))); d = np.sqrt(((ga - gb) ** 2).sum(0))
    res.append('%s %.1e' % (nm, d.max()))
say('2. pairs %.0e apart on either side of: %s' % (2 * h, '; '.join(res)))
# circles of every size round the x-axis (the formula swaps form on one of them; which one is not assumed)
worst = 0.0; where = 0.0; u = rng.uniform(0, 2 * np.pi, 4000 if WHICH != 'B' else 1500); NCIRC = 3599 if WHICH != 'B' else 900
for dd in np.radians(np.linspace(0.05, 179.95, NCIRC)):
    ga = np.array(Gdir(np.cos(dd - h) + 0 * u, np.sin(dd - h) * np.cos(u), np.sin(dd - h) * np.sin(u))); gb = np.array(Gdir(np.cos(dd + h) + 0 * u, np.sin(dd + h) * np.cos(u), np.sin(dd + h) * np.sin(u)))
    d = np.sqrt(((ga - gb) ** 2).sum(0)).max()
    if d > worst:
        worst, where = d, np.degrees(dd)
say('2. pairs %.0e apart across each of %d circles about the x-axis (0.05 .. 179.95 degrees, %d pairs each): images at most %.1e apart (at %.2f degrees)' % (2 * h, NCIRC, u.size, worst, where))
# half planes through the x-axis (the angle round the x-axis is cut somewhere; where is not assumed)
worst = 0.0; where = 0.0; s = np.arccos(rng.uniform(-1, 1, 4000 if WHICH != 'B' else 1500))
for ff in np.radians(np.linspace(0, 360, 720 if WHICH != 'B' else 360, endpoint=False)):
    ga = np.array(Gdir(np.cos(s), np.sin(s) * np.cos(ff - h), np.sin(s) * np.sin(ff - h))); gb = np.array(Gdir(np.cos(s), np.sin(s) * np.cos(ff + h), np.sin(s) * np.sin(ff + h)))
    d = np.sqrt(((ga - gb) ** 2).sum(0)).max()
    if d > worst:
        worst, where = d, np.degrees(ff)
say('2. pairs across each of 720 (B: 360) half planes through the x-axis: images at most %.1e apart (at %.1f degrees round the x-axis)' % (worst, where))
# small circles round marked directions: +x, -x, the two far corners, everything sent to -x, +-y, +-z, and 200 random ones
marks = [('+x', np.array([1.0, 0, 0])), ('-x', np.array([-1.0, 0, 0])), ('+y', np.array([0, 1.0, 0])), ('-y', np.array([0, -1.0, 0])), ('+z', np.array([0, 0, 1.0])), ('-z', np.array([0, 0, -1.0]))]
for sg in (1, -1):
    for a_deg in (120.0, 132.8, 132.9, 138.1, 90.0):
        a = np.radians(a_deg); marks.append(('%.1f from +x, %s' % (a_deg, 'up' if sg > 0 else 'down'), np.array([np.cos(a), 0, sg * np.sin(a)])))
# the far corner and the directions sent to -x, found by search rather than taken from the explorer's log
def find_dir_sent_to(target, guess):
    from scipy.optimize import minimize
    f = lambda v: float(((np.array(Gdir(*[np.array([t]) for t in unit(np.array(v))])).ravel() - target) ** 2).sum())
    r = minimize(f, guess, method='Nelder-Mead', options=dict(xatol=1e-13, fatol=1e-26, maxiter=4000)); return unit(r.x), r.fun


found = []
for g0 in rng.normal(size=(60, 3)):
    d, e = find_dir_sent_to(np.array([-1.0, 0, 0]), g0)
    if e < 1e-12 and not any(np.abs(d - q).max() < 1e-4 for q in found):
        found.append(d)
say('2. directions sent to -x, found by search from 60 random starts: %d' % len(found))
for d in found:
    say('      (%.5f, %.5f, %.5f): %.2f degrees from +x, %.1f round the x-axis (0 = +y, 90 = +z)' % (*d, np.degrees(np.arccos(np.clip(d[0], -1, 1))), np.degrees(np.arctan2(d[2], d[1])) % 360))
    marks.append(('sent to -x', d))
foundp = []
for g0 in rng.normal(size=(60, 3)):
    d, e = find_dir_sent_to(np.array([1.0, 0, 0]), g0)
    if e < 1e-12 and not any(np.abs(d - q).max() < 1e-4 for q in foundp):
        foundp.append(d)
say('2. directions sent to +x, found by search from 60 random starts: %d: %s' % (len(foundp), '; '.join('(%.5f, %.5f, %.5f)' % tuple(d) for d in foundp)))
for d in rng.normal(size=(200 if WHICH != 'B' else 30, 3)):
    marks.append(('random', unit(d)))
worst = 0.0; wname = ''; allfin = True
for nm, a in marks:
    b = np.cross(a, [0.3, 0.5, 0.81]); b = unit(b); c3 = np.cross(a, b); u = np.linspace(0, 2 * np.pi, 20000 if WHICH != 'B' else 6000, endpoint=False)
    for rad in (1e-1, 1e-2, 1e-3, 1e-5, 1e-7, 1e-9):
        P = unit(a[:, None] + rad * (b[:, None] * np.cos(u) + c3[:, None] * np.sin(u))); jm, st, fin = sweep(P, nm); allfin &= fin
        if jm > worst:
            worst, wname = jm, '%s, circle of radius %.0e' % (nm, rad)
say('2. small circles (radius 1e-1 .. 1e-9, 20000 (B: 6000) steps each) round %d marked and random directions: largest jump of the image in one step %.1e (%s); all finite: %s' % (len(marks), worst, wname, allfin))
# random pairs, three sizes, with the place of the largest stretch
p = unit(rng.normal(size=(3, 400000 if WHICH != 'B' else 150000))); t = rng.normal(size=p.shape); t -= (t * p).sum(0) * p; t = unit(t); g0 = np.array(Gdir(*p))
for hh in (1e-4, 1e-6, 1e-8):
    st = np.sqrt(((np.array(Gdir(*unit(p + hh * t))) - g0) ** 2).sum(0)) / hh; j = int(st.argmax())
    say('2. %d random pairs %.0e apart: stretch median %.3f, largest %.1f at %.1f degrees from +x, %.1f round the x-axis (a tear would give about %.0e)'
        % (p.shape[1], hh, np.median(st), st.max(), np.degrees(np.arccos(p[0, j])), np.degrees(np.arctan2(p[2, j], p[1, j])) % 360, 1 / hh))
say('   [%.0f s]' % (time.time() - T0))

# ------------------------------------------------------------------ 3. nothing that is not a number
N = 1000000 if WHICH != 'B' else 200000
v = unit(rng.normal(size=(3, N))) * 10.0 ** rng.uniform(-9, 1, N); X, Y, Z = Frule(*v)
fin = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z); lerr = np.abs(np.sqrt(X * X + Y * Y + Z * Z) / (v * v).sum(0) - 1).max()
say('3. %d random points, lengths 1e-9 .. 10: not finite %d; length of the image against length squared: largest relative error %.1e' % (N, int((~fin).sum()), lerr))
sp = []
for a in (0.0, 1.0, -1.0, 1e-300, -1e-300, 5e-324, 1e-17, -1e-17, 0.618, -0.618, 2.0, -0.0):
    for b in (0.0, 1.0, -1.0, 1e-300, 1e-17, -1e-17, -0.0):
        for c_ in (0.0, 1.0, -1.0, 1e-300, -1e-300, 1e-17, -1e-17, -0.0):
            sp.append((a, b, c_))
for nm, d in marks[:16] + [(None, q) for q in found]:
    for sc in (1.0, 0.5216, 1e-8):
        sp.append(tuple(sc * d))
sp = np.array(sp, float).T; X, Y, Z = Frule(*sp); fin = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z)
say('3. %d special points (zeros, signed zeros, the smallest numbers, the axes, the corners, the marked directions): not finite %d%s' % (sp.shape[1], int((~fin).sum()), '' if fin.all() else ' at ' + str(sp[:, ~fin].T[:5].tolist())))
X, Y, Z = Fgen(*sp); fin = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z); say('   the same through the general formula (special case off): not finite %d' % int((~fin).sum()))
# along real orbits (the bench drops an orbit silently when a NaN turns up: it would look like "left")
for nm, c in SETS[:2]:
    q = rng.uniform(-1.7, 1.7, size=(3, N // 2)); a, zmax, bad = my_stay(Frule, q[0], q[1], q[2], c, 40, track=True)
    say('3. %d orbits in space, %s, 40 steps: values that are not finite on the way: %d (inside: %d)' % (N // 2, nm, bad, int(a.sum())))
say('   [%.0f s]' % (time.time() - T0))

# ------------------------------------------------------------------ 4. mirrors, the half turn, how often the ball is covered
p = unit(rng.normal(size=(3, 400000 if WHICH != 'B' else 100000))); g = np.array(Gdir(*p))
a = np.array(Gdir(p[0], p[1], -p[2])); a[2] *= -1; e1 = np.abs(a - g).max()
a = np.array(Gdir(p[0], -p[1], p[2])); a[1] *= -1; e2 = np.abs(a - g).max()
a = np.array(Gdir(-p[0], -p[1], p[2])); e3 = np.sqrt(((a - g) ** 2).sum(0))
a = np.array(Gdir(p[0], p[2], -p[1])); a2 = np.stack([a[0], -a[2], a[1]]); e4 = np.sqrt(((a2 - g) ** 2).sum(0))
say('4. mirror in the flat plane: largest error %.1e; mirror in the upright plane through the x-axis: %.1e' % (e1, e2))
say('4. half turn about the upright axis (the flat rule sends z and -z to one point): the two images are apart by median %.3f, largest %.3f; share of directions where they agree to 1e-6: %.4f' % (np.median(e3), e3.max(), np.mean(e3 < 1e-6)))
say('4. quarter turn about the x-axis (a ring would be unchanged by it): the two images are apart by median %.3f, largest %.3f' % (np.median(e4), e4.max()))
# covering: my own count. Pick random targets, count the directions that are sent near each by a fine net of the ball.
n = 1200 if WHICH != 'B' else 500; lat = (np.arange(n) + 0.5) / n * np.pi - np.pi / 2; lo = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi; LA, LO = np.meshgrid(lat, lo, indexing='ij')
P = np.stack([np.cos(LA) * np.cos(LO), np.cos(LA) * np.sin(LO), np.sin(LA)]); hh = 1e-6
ea = np.stack([-np.sin(LA) * np.cos(LO), -np.sin(LA) * np.sin(LO), np.cos(LA)]); eb = np.stack([-np.sin(LO), np.cos(LO), 0 * LO])
g = np.array(Gdir(*P.reshape(3, -1))).reshape(P.shape)
ga = (np.array(Gdir(*unit(P + hh * ea).reshape(3, -1))).reshape(P.shape) - np.array(Gdir(*unit(P - hh * ea).reshape(3, -1))).reshape(P.shape)) / (2 * hh)
gb = (np.array(Gdir(*unit(P + hh * eb).reshape(3, -1))).reshape(P.shape) - np.array(Gdir(*unit(P - hh * eb).reshape(3, -1))).reshape(P.shape)) / (2 * hh)
det = (np.cross(gb, ga, axis=0) * g).sum(0); dA = np.cos(LA) * (np.pi / n) ** 2; ok = np.isfinite(det) & (np.abs(det) < 1e4)
aa, bb, ab = (ga * ga).sum(0), (gb * gb).sum(0), (ga * gb).sum(0); tr, dd = aa + bb, np.sqrt(np.maximum((aa - bb) ** 2 + 4 * ab * ab, 0)); sq = np.sqrt((tr + dd) / np.maximum(tr - dd, 1e-300))
order = np.argsort(sq[ok]); cum = np.cumsum(dA[ok][order]) / dA[ok].sum(); wq = lambda q: float(sq[ok][order][np.searchsorted(cum, q)])
ang = np.degrees(np.arccos(np.clip(P[0], -1, 1))); nearm = ok & (ang > 170)
say('4. the ball of directions is covered %.4f times (area of the image, with sign, over the area of the ball); share where the map is folded over: %.6f; net left out as not finite or wild: %.6f of the area'
    % ((det * dA)[ok].sum() / (4 * np.pi), (dA * (det < 0))[ok].sum() / dA[ok].sum(), dA[~ok].sum() / dA.sum()))
say('4. squeeze (larger over smaller stretch), by area: median %.2f, 90 %% below %.2f, 99 %% below %.2f, largest on the net %.2f; within 10 degrees of -x: median %.2f, largest %.2f' % (wq(0.5), wq(0.9), wq(0.99), float(sq[ok].max()), float(np.median(sq[nearm])), float(sq[nearm].max())))
# 5. the push off the flat plane
lon = np.linspace(0, 2 * np.pi, 3600, endpoint=False) + 0.000123
for eps in (1e-4, 1e-6, 1e-8):
    up = np.arcsin(np.clip(np.array(Gdir(np.cos(eps) * np.cos(lon), np.cos(eps) * np.sin(lon), np.sin(eps) + 0 * lon))[2], -1, 1)) / eps
    say('5. push off the flat plane, started %.0e above it, 3600 longitudes: %.4f .. %.4f (smallest at longitude %.1f, largest at %.1f)' % (eps, up.min(), up.max(), np.degrees(lon[up.argmin()]), np.degrees(lon[up.argmax()])))
# 5b. the same question AT the longitudes the explorer's list of longitudes steps over: exactly 180 (above -x) and exactly 0
for nm, lon0 in (('longitude 180 exactly (straight above the negative x-axis)', np.pi), ('longitude 0 exactly (above +x)', 0.0), ('longitude 90 exactly', np.pi / 2), ('longitude 270 exactly', 1.5 * np.pi)):
    out = []
    for eps in (1e-4, 1e-6, 1e-8):
        gz = float(np.array(Gdir(np.array([np.cos(eps) * np.cos(lon0)]), np.array([np.cos(eps) * np.sin(lon0)]), np.array([np.sin(eps)])))[2, 0]); out.append('%.0e: %+.4f' % (eps, np.arcsin(np.clip(gz, -1, 1)) / eps))
    say('5b. push at %s, by height: %s' % (nm, '; '.join(out)))
# a tiny circle round -x and round +x: which part of the half above the flat plane is sent below it
u = np.radians(np.arange(0.25, 180, 0.5))
for nm, sg in (('-x', -1.0), ('+x', 1.0)):
    for rad in (1e-3, 1e-6):
        g = np.array(Gdir(sg * np.cos(rad) + 0 * u, np.sin(rad) * np.cos(u), np.sin(rad) * np.sin(u))); below = g[2] < 0
        rng_ = ('%.1f .. %.1f degrees round the x-axis' % (np.degrees(u[below].min()), np.degrees(u[below].max()))) if below.any() else 'none'
        say('5b. circle of radius %.0e round %s, its half above the flat plane: share sent BELOW the flat plane %.3f (%s); image stays within %.2e .. %.2e of %s'
            % (rad, nm, below.mean(), rng_, np.arccos(np.clip(g[0], -1, 1)).min(), np.arccos(np.clip(g[0], -1, 1)).max(), '+x'))
# how much of the whole upper half of the ball of directions is sent below the flat plane
pp = unit(rng.normal(size=(3, 400000 if WHICH != 'B' else 100000))); pp[2] = np.abs(pp[2]); gg = np.array(Gdir(*pp)); angm = np.degrees(np.arccos(np.clip(-pp[0], -1, 1)))
say('5b. of the directions above the flat plane, the share sent below it: %.4f (within 30 degrees of -x: %.4f; farther than 60 degrees from -x: %.4f)' % ((gg[2] < 0).mean(), (gg[2] < 0)[angm < 30].mean(), (gg[2] < 0)[angm > 60].mean()))
# 6. the upright cut through the x-axis against the flat picture (my points)
xr, zz = rng.uniform(-1.8, 1.8, 20000), rng.uniform(-1.3, 1.3, 20000)
for nm, c in (SETS[0], SETS[3]):
    a = my_stay(Frule, xr, 0 * xr, zz, c, 60); b = true_flat(xr, zz, c, 60)
    say('6. upright cut through the x-axis, %s: %d of 20000 verdicts differ from the flat picture turned up (inside the flat picture: %d; inside the cut: %d)' % (nm, int((a != b).sum()), int(b.sum()), int(a.sum())))
u = rng.uniform(0, 2 * np.pi, 200000); g = np.array(Gdir(np.cos(u), 0 * u, np.sin(u)))
say('6. the upright circle through the x-axis against doubling: largest error %.2e (largest |y| %.1e)' % (max(np.abs(g[0] - np.cos(2 * u)).max(), np.abs(g[2] - np.sin(2 * u)).max()), np.abs(g[1]).max()))
say('   [%.0f s]' % (time.time() - T0))
