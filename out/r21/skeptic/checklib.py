"""Skeptic, job 3: is the library right?  python out/r21/skeptic/checklib.py
Every check prints a number. Nothing here edits the library."""
import os, sys, math, time
import numpy as np
sys.path.insert(0, 'out/r21/lib')
import mem as M

rng = np.random.default_rng(11)
STEPS = 60
SC = {r.name: r for r in M.SCOUT}


# ------------------------------------------------------------------ independent scalar code (plain math, angles, no library)
def P_scalar(x, y, z):
    r2 = x * x + y * y + z * z; d = r2 + z * z
    if d == 0.0:
        return 0.0, 0.0, 0.0
    f = r2 / d; r = math.sqrt(r2)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * z * r


def P_about_angle(x, y, z, th):
    """Rot_x(th) P(Rot_x(-th) v), written out by hand with the angle th itself."""
    c, s = math.cos(th), math.sin(th)
    X, Y, Z = P_scalar(x, c * y + s * z, -s * y + c * z)
    return X, c * Y - s * Z, s * Y + c * Z


def slow_lag(lam, x, y, z, cx, cy, cz, steps, mode='lag'):
    """One orbit, sheet carried as an ANGLE th (starts 0 = the flat page). mode: lag / delay / first / own / fixed."""
    th = 0.0; n = 0
    for k in range(steps):
        own = math.atan2(z, y) if (y != 0.0 or z != 0.0) else None
        if mode == 'lag':
            if own is not None:
                b1 = (1 - lam) * math.cos(2 * th) + lam * math.cos(2 * own); b2 = (1 - lam) * math.sin(2 * th) + lam * math.sin(2 * own)
                if math.hypot(b1, b2) > 1e-9:
                    th = 0.5 * math.atan2(b2, b1)
            use = th
        elif mode == 'delay':
            use = th
            if own is not None:
                th = own
        elif mode == 'first':
            if k > 0 and own is not None:
                th = own
            use = th
        elif mode == 'own':
            if own is not None:
                th = own
            use = th
        else:
            use = 0.0
        X, Y, Z = P_about_angle(x, y, z, use)
        x, y, z = X + cx, Y + cy, Z + cz
        if x * x + y * y + z * z >= 36.0:
            break
        n += 1
    return n


def slow_along(x, y, z, cx, cy, cz, steps):
    n = 0
    for k in range(steps):
        phi = math.atan2(z, y); psi = phi - 0.25 * math.sin(4 * phi)
        X, Y, Z = P_about_angle(x, y, z, psi)
        x, y, z = X + cx, Y + cy, Z + cz
        if x * x + y * y + z * z >= 36.0:
            break
        n += 1
    return n


def slow_generic(rule, x, y, z, cx, cy, cz, steps):
    """One orbit at a time through rule.step itself (arrays of length 1): tests the bookkeeping of M.stay only."""
    x, y, z = np.array([x]), np.array([y]), np.array([z]); c1, c2, c3 = np.array([cx]), np.array([cy]), np.array([cz])
    st = tuple(rule.init(1)); n = 0
    for k in range(steps):
        out = rule.step(x, y, z, st, k, c1, c2, c3); st = tuple(out[3])
        x, y, z = out[0] + c1, out[1] + c2, out[2] + c3
        if not (x[0] * x[0] + y[0] * y[0] + z[0] * z[0] < 36.0):
            break
        n += 1
    return n


def report(tag, a, b, steps=STEPS):
    a, b = np.asarray(a), np.asarray(b)
    print('  %-58s counts differ %4d of %d | verdicts differ %3d | inside %d' % (tag, int((a != b).sum()), a.size, int(((a >= steps) != (b >= steps)).sum()), int((a >= steps).sum())))


print('A. M.stay against a slow loop, one orbit at a time, 1,000 random points (%d steps)' % STEPS)
N = 1000
# Julia: start points in a box, c mixed (half on the page, half anywhere), so that plenty stay
v = rng.uniform([-1.6, -1.1, -1.1], [1.6, 1.1, 1.1], size=(N, 3))
cs = np.array([(-1.0, 0, 0), M.RABBIT, M.SIEGEL, (-0.75, 0, 0), (-0.6, 0.3, 0.25), (-1.0, 0.15, 0.1)])
cJ = cs[rng.integers(0, len(cs), N)]
cM = rng.uniform([-1.9, -0.9, -0.9], [0.5, 0.9, 0.9], size=(N, 3))
for nm, mode, lam in (('fixed', 'fixed', 0), ('lag25', 'lag', 0.25), ('lag75', 'lag', 0.75), ('delay', 'delay', 0), ('first', 'first', 0), ('own', 'own', 0)):
    r = SC[nm]
    fast = M.stay(r, v[:, 0], v[:, 1], v[:, 2], cJ[:, 0], cJ[:, 1], cJ[:, 2], STEPS)
    slow = [slow_lag(lam, *v[i], *cJ[i], STEPS, mode) for i in range(N)]
    gen = [slow_generic(r, *v[i], *cJ[i], STEPS) for i in range(N)]
    report('%s Julia: stay vs my own scalar code' % nm, fast, slow); report('%s Julia: stay vs rule.step one at a time' % nm, fast, gen)
    fast = M.mandel(r, cM[:, 0], cM[:, 1], cM[:, 2], STEPS)
    slow = [slow_lag(lam, *cM[i], *cM[i], STEPS, mode) for i in range(N)]
    report('%s Mandelbrot: stay vs my own scalar code' % nm, fast, slow)
al = M.bench('along')
fast = M.stay(al, v[:, 0], v[:, 1], v[:, 2], cJ[:, 0], cJ[:, 1], cJ[:, 2], STEPS)
report('along (fixed rule) Julia: stay vs my own scalar code', fast, [slow_along(*v[i], *cJ[i], STEPS) for i in range(N)])
report('along (fixed rule) Julia: stay vs rule.step one at a time', fast, [slow_generic(al, *v[i], *cJ[i], STEPS) for i in range(N)])
fast = M.mandel(al, cM[:, 0], cM[:, 1], cM[:, 2], STEPS)
report('along (fixed rule) Mandelbrot: stay vs my own scalar code', fast, [slow_along(*cM[i], *cM[i], STEPS) for i in range(N)])

print('B. M.sq_about against rotating by hand (rotation matrices), 20,000 random points and sheets')
n = 20000; p = rng.normal(size=(n, 3)); th = rng.uniform(-np.pi, np.pi, n)       # th over the whole circle: both sides of every sheet
u1, u2 = np.cos(2 * th), np.sin(2 * th)
X, Y, Z = M.sq_about(p[:, 0], p[:, 1], p[:, 2], u1, u2)
c, s = np.cos(th), np.sin(th)
yb, zb = c * p[:, 1] + s * p[:, 2], -s * p[:, 1] + c * p[:, 2]                  # Rot_x(-th) v
X0, Y0, Z0 = M.S.oneplane(p[:, 0], yb, zb)
Xh, Yh, Zh = X0, c * Y0 - s * Z0, s * Y0 + c * Z0                               # Rot_x(th) of that
print('  one-plane rule: largest difference %.2e (sizes up to %.1f)' % (max(np.abs(X - Xh).max(), np.abs(Y - Yh).max(), np.abs(Z - Zh).max()), np.abs(Xh).max()))
print('  length is squared: largest |F| - |v|^2 = %.2e' % np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (p ** 2).sum(1)).max())
for bn in ('along', 'away', 'twoplane', 'mandelbulb', 'wind2'):
    F = M.bench(bn); Fx = lambda a, b, cc: F.step(a, b, cc, (), 0, 0, 0, 0)[:3]
    X, Y, Z = M.sq_about(p[:, 0], p[:, 1], p[:, 2], u1, u2, F=Fx)
    X0, Y0, Z0 = Fx(p[:, 0], yb, zb)
    d = max(np.abs(X - X0).max(), np.abs(Y - (c * Y0 - s * Z0)).max(), np.abs(Z - (s * Y0 + c * Z0)).max())
    print('  fixed rule %-10s about a sheet: largest difference from the by-hand turn %.2e  (0 = the side that M.half picks does not matter for it)' % (bn, d))

print('C. M.half: the angle it returns, and whether the side matters')
t = rng.uniform(-np.pi / 2, np.pi / 2, 200000); co, si = M.half(np.cos(2 * t), np.sin(2 * t))
print('  theta in (-90, 90): largest error of cos %.2e, of sin %.2e' % (np.abs(co - np.cos(t)).max(), np.abs(si - np.sin(t)).max()))
for eps in (1e-3, 1e-6, 1e-8, 1e-10):
    t = np.array([eps, -eps, np.pi / 2 - eps, -np.pi / 2 + eps]); co, si = M.half(np.cos(2 * t), np.sin(2 * t))
    print('  sheets %.0e rad from the flat page / the upright sheet: error of the returned angle %s rad' % (eps, np.array2string(np.abs(np.arctan2(si, co) - t), precision=1)))
print('  on the upright sheet itself: half(-1, +0) =', M.half(np.array([-1.0]), np.array([0.0])), ' half(-1, -1e-17) =', M.half(np.array([-1.0]), np.array([-1e-17])))


def other_side(u1, u2):
    co, si = ORIG(u1, u2); return -co, -si


ORIG = M.half
tot = 0
for r in M.SCOUT:
    a = M.stay(r, v[:, 0], v[:, 1], v[:, 2], cJ[:, 0], cJ[:, 1], cJ[:, 2], STEPS); b0 = M.mandel(r, cM[:, 0], cM[:, 1], cM[:, 2], STEPS)
    M.half = other_side                                    # in this process only: every sheet read from its other side
    a2 = M.stay(r, v[:, 0], v[:, 1], v[:, 2], cJ[:, 0], cJ[:, 1], cJ[:, 2], STEPS); b2 = M.mandel(r, cM[:, 0], cM[:, 1], cM[:, 2], STEPS)
    M.half = ORIG
    tot += int((a != a2).sum() + (b0 != b2).sum())
    print('  %-6s with every sheet read from its other side: counts that change %d (Julia) + %d (Mandelbrot) of 1,000 each' % (r.name, int((a != a2).sum()), int((b0 != b2).sum())))

print('D. The Mandelbrot convention: start at c with k = 0 (library) against start at 0 (one step more)')
n = 40000; c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3)); zero = np.zeros(n)
lathe = M.mandel(M.bench('lathe'), c[:, 0], c[:, 1], c[:, 2], STEPS) >= STEPS
for r in M.SCOUT:
    a = M.mandel(r, c[:, 0], c[:, 1], c[:, 2], STEPS) >= STEPS
    b = M.stay(r, zero, zero, zero, c[:, 0], c[:, 1], c[:, 2], STEPS + 1) >= STEPS + 1
    print('  %-6s verdicts that differ %5d of %d (inside: %d from c, %d from 0) | from 0, differs from the lathe in %d' % (r.name, int((a != b).sum()), n, int(a.sum()), int(b.sum()), int((b != lathe).sum())))

print('E. M.solid against M.cut_axis and against a plain block count')
for r in (SC['lag25'], SC['lag75'], M.bench('along')):
    w, h, nd, steps = 281, 241, 241, 30; hw = 1.7
    dep, px = M.solid(r, None, w, h, nd, steps, cam=(0, 0, 1))             # eye on the z-axis: screen right = x, up = y, depth = -z
    us = np.linspace(-hw, hw, w); vs = np.linspace(hw * h / w, -hw * h / w, h); ds = np.linspace(-hw, hw, nd)
    # (1) plain block count on the same sample points, without slabs
    first = np.full((h, w), np.inf)
    for j in range(nd - 1, -1, -1):                                        # back to front, so the front-most wins
        U, V = np.meshgrid(us, vs); ins = M.mandel(r, -0.7 + U, V, np.full_like(U, -ds[j]), steps) >= steps
        first = np.where(ins, ds[j], first)
    print('  %-6s solid vs plain block count: pixels whose depth differs %d of %d' % (r.name, int((first != dep).sum()), dep.size))
    # (2) silhouette against the cut along the flat page, same pixels
    U, V = np.meshgrid(us, vs); flat = M.mandel(r, -0.7 + U, V, np.zeros_like(U), steps) >= steps
    hit = np.isfinite(dep)
    print('         cut along the flat page inside the silhouette: %d of %d cut pixels are NOT covered' % (int((flat & ~hit).sum()), int(flat.sum())))
    # (3) the height of the solid over the x-axis against the cut along the upright sheet (cut_axis at 90 degrees)
    cut = M.cut_axis(r, 90.0, w, nd, steps, box=(-0.7 - hw, -0.7 + hw, -hw, hw)) >= steps      # rows: s from +hw (top) down
    srow = np.linspace(hw, -hw, nd); top_cut = np.where(cut.any(0), srow[np.argmax(cut, 0)], np.nan)
    mid = h // 2; top_solid = np.where(hit[mid], -dep[mid], np.nan)
    both = np.isfinite(top_cut) & np.isfinite(top_solid)
    print('         height over the x-axis, solid vs cut at 90: columns where only one has something %d, largest height difference %.4f (block %.4f)'
          % (int((np.isfinite(top_cut) != np.isfinite(top_solid)).sum()), float(np.abs(top_cut[both] - top_solid[both]).max()) if both.any() else -1, ds[1] - ds[0]))
print('done')
