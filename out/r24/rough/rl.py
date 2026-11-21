"""Round 24, section "rough": the rules under test, the block grids, and the orbit tracer with its squeeze book-keeping.

    import sys; sys.path.insert(0, 'out/r24/rough'); import rl as L
    r = L.get('second')            # any name of L.MAKERS
    n = L.blocks('second', 'basilica')        # 170 x 140 x 140 blocks of side 0.02, steps each orbit stays (80 = inside)
    t = L.trace(r, P, c, cyc)      # per point: settle step, steps off the flat plane, squeeze of every step, total squeeze

Words used here.
  A rule is F(v) = |v|^2 G(direction of v) + c. One step stretches space near v by 2|v| along the ray and by |v| s1,
  |v| s2 across it (s1 >= s2: the two stretches of the direction map G at that direction). A step keeps shapes only
  where s1 = s2 = 2. squeeze of a step = (largest of 2, s1) / (smallest of 2, s2) (1 = shapes kept).
  total squeeze of a point = largest / smallest stretch of ALL its steps together up to the step where it settles
  (comes within RHO of the attracting cycle). A small ball round the landing point is the image of an ellipsoid round
  the starting point that is `total squeeze` times as long as thick.
"""
import os, sys, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in ('out/r21/lib', 'out/r23/me', 'out/r24/me'):
    sys.path.insert(0, os.path.join(ROOT, *p.split('/')))
import mem as M
import cone as C
import mfold as MF
import tri as T
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
T15 = 2.0 - np.sqrt(3.0)


def _load(modname, *parts):
    if modname not in sys.modules:
        spec = importlib.util.spec_from_file_location(modname, os.path.join(ROOT, *parts))
        mod = importlib.util.module_from_spec(spec); sys.modules[modname] = mod; spec.loader.exec_module(mod)
    return sys.modules[modname]


def _welded():
    return _load('r23_cone_best', 'out', 'r23', 'cone', 'best.py').rule()


def _welded_raw():
    """The angle-true map whose copies are the welded cones' (R_t, t = tan 15, turned by 30 degrees), no blend."""
    phi = np.pi / 6; co, si = np.cos(phi), np.sin(phi); c2, s2 = np.cos(2 * phi), np.sin(2 * phi)

    def F(x, y, z):
        r2 = x * x + y * y + z * z
        X, Y, Z = C.cone_dir(co * x + si * y, co * y - si * x, z, T15, 0.4, False)
        ok = r2 > 0
        return np.where(ok, r2 * (c2 * X - s2 * Y), 0.0), np.where(ok, r2 * (s2 * X + c2 * Y), 0.0), np.where(ok, r2 * Z, 0.0)
    return M.fixed(F, 'cones_raw', 'the angle-true map behind the welded cones, no blend')


def shear_rule(eps=0.35, top=0.8, name='shear'):
    """A CONTROL made here: no extra copies at all (every direction is still reached from exactly two), exact doubling
    on the flat plane, but a strong squeeze beside it. In Mercator coordinates (mu, lam) of the direction:
        mu' = 2 mu + eps b(mu) cos 3 lam,   lam' = 2 lam + eps b(mu) sin 3 lam,   b = sin^2(pi |mu| / top) below top, else 0
    (mu' takes the sign of z). Above Mercator latitude `top` (39 degrees for 0.8) it IS the one-plane rule."""
    def F(x, y, z):
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); rs = np.where(r > 0, r, 1.0)
        mu = np.arctanh(np.clip(np.abs(z) / rs, 0, 1 - 1e-15)); lam = np.arctan2(y, x)
        b = np.where(mu < top, np.sin(np.pi * mu / top) ** 2, 0.0)
        m2 = np.minimum(2 * mu + eps * b * np.cos(3 * lam), 60.0); l2 = 2 * lam + eps * b * np.sin(3 * lam)
        ch = 1 / np.cosh(m2); sg = np.where(z < 0, -1.0, 1.0); ok = r2 > 0
        return np.where(ok, r2 * ch * np.cos(l2), 0.0), np.where(ok, r2 * ch * np.sin(l2), 0.0), np.where(ok, r2 * np.tanh(m2) * sg, 0.0)
    return M.fixed(F, name, 'control: one plane with a squeezing zone beside the flat plane, no extra copies')


MAKERS = {
    'oneplane': lambda: M.fixed(M.S.oneplane, 'oneplane', 'one plane'),
    'second': lambda: C.cone_rule(-0.268, name='second', label='second version (dial -0.268), blended'),
    'second_raw': lambda: C.cone_rule(-0.268, blend=False, name='second_raw', label='second version with NO blend'),
    'first': lambda: C.cone_rule(0.268, name='first', label='first version (dial +0.268), blended'),
    'cones': _welded,
    'cones_raw': _welded_raw,
    'm4': lambda: MF.rule(4, -0.20),
    'm4_raw': lambda: MF.rule(4, -0.20, blend=False),
    'm6': lambda: MF.rule(6, -0.10),
    'm6_raw': lambda: MF.rule(6, -0.10, blend=False),
    'tri': lambda: T.tri_rule(),
    'shear': shear_rule,
    'shear2': lambda: shear_rule(0.45, 0.8, 'shear2'),
}
PLAIN = {'oneplane': 'One plane', 'second': 'Second version', 'second_raw': 'Second version, no blend (flat picture wrong)',
         'cones': 'Welded cones', 'cones_raw': 'Welded cones, no blend (flat picture wrong)', 'm4': 'Copy laid round twice',
         'm4_raw': 'Copy round twice, no blend (flat picture wrong)', 'm6': 'Copy laid round four times',
         'm6_raw': 'Copy round four times, no blend (flat picture wrong)', 'tri': 'Even spacing (two flat triangles)',
         'shear': 'Control: one plane with a squeezing zone and NO extra copies', 'first': 'First version'}
SETS = {'basilica': (-1.0, 0.0, 0.0), 'rabbit': M.RABBIT, 'sanmarco': (-0.75, 0.0, 0.0), 'siegel': M.SIEGEL}
SETNAME = {'basilica': 'c = -1', 'rabbit': 'rabbit', 'sanmarco': 'c = -0.75', 'siegel': 'Siegel disc'}
_made = {}


def get(name):
    if name not in _made:
        r = MAKERS[name](); r.key = name; r.plain = PLAIN.get(name, name); _made[name] = r
    return _made[name]


# ------------------------------------------------------------------ blocks (the layout of round 23's battery)
H = 0.02; VN = (170, 140, 140)
R23CACHE = os.path.join(ROOT, 'out', 'r23', 'design', 'cache')


def axes():
    return tuple((np.arange(n) + 0.5) * H - n * H / 2 for n in VN)


def blocks(name, sname, steps=80, quiet=False):
    path = os.path.join(CACHE, 'vox-%s-%s-%d.npz' % (name, sname, steps))
    if os.path.exists(path):
        return np.load(path)['n']
    rp = os.path.join(R23CACHE, 'vox-%s-%s-%d.npz' % (name, sname, steps))
    if name in ('cones',) and os.path.exists(rp):
        return np.load(rp)['n']
    r = get(name); c = SETS[sname]; xs, ys, zs = axes(); out = np.zeros(VN, np.uint8)
    for i0 in range(0, VN[0], 34):
        X, Y, Z = np.meshgrid(xs[i0:i0 + 34], ys, zs, indexing='ij')
        out[i0:i0 + 34] = M.stay(r, X, Y, Z, c[0], c[1], c[2], steps)
    np.savez_compressed(path, n=out)
    return out


def centres(idx):
    xs, ys, zs = axes()
    return np.stack([xs[idx[0]], ys[idx[1]], zs[idx[2]]], 1)


# ------------------------------------------------------------------ the direction map of a rule, and its stretches
def G(rule, d):
    """Direction map on unit vectors d (n, 3)."""
    o = rule.step(d[:, 0], d[:, 1], d[:, 2], tuple(rule.init(d.shape[0])), 1, 0.0, 0.0, 0.0)
    return np.stack([o[0], o[1], o[2]], 1)


def Fc(rule, v, c):
    o = rule.step(v[:, 0], v[:, 1], v[:, 2], tuple(rule.init(v.shape[0])), 1, c[0], c[1], c[2])
    return np.stack([o[0] + c[0], o[1] + c[1], o[2] + c[2]], 1)


def jac(rule, v, c, f0=None):
    """The 3 x 3 matrix of one step at each point (central differences)."""
    n = v.shape[0]; J = np.zeros((n, 3, 3)); h = 1e-6 * np.maximum(np.sqrt((v * v).sum(1)), 1e-3)
    for i in range(3):
        e = np.zeros((n, 3)); e[:, i] = h
        J[:, :, i] = (Fc(rule, v + e, c) - Fc(rule, v - e, c)) / (2 * h[:, None])
    return J


def sphere_table(rule, n=500):
    """Stretches of the direction map by latitude band. Returns rows (band, median squeeze, 90 % squeeze, median s1,
    median s2, smallest s2, folded share)."""
    lat = (np.arange(n) + 0.5) / n * np.pi / 2; lon = (np.arange(4 * n) + 0.5) / (4 * n) * 2 * np.pi
    LA, LO = np.meshgrid(lat, lon, indexing='ij'); la, lo = LA.ravel(), LO.ravel(); h = 1e-5

    def GG(a, b):
        return G(rule, np.stack([np.cos(a) * np.cos(b), np.cos(a) * np.sin(b), np.sin(a)], 1))
    g = GG(la, lo); a = (GG(la + h, lo) - GG(la - h, lo)) / (2 * h); b = (GG(la, lo + h) - GG(la, lo - h)) / (2 * h) / np.cos(la)[:, None]
    det = (np.cross(a, b) * g).sum(1)
    aa, bb, ab = (a * a).sum(1), (b * b).sum(1), (a * b).sum(1); tr, dd = aa + bb, np.sqrt(np.maximum((aa - bb) ** 2 + 4 * ab * ab, 0))
    s1, s2 = np.sqrt((tr + dd) / 2), np.sqrt(np.maximum((tr - dd) / 2, 0))
    sq = np.maximum(2, s1) / np.maximum(np.minimum(2, s2), 1e-9); w = np.cos(la)
    sign = np.sign(np.median(det)); rows = []
    for lo_, hi_ in ((0, 5), (5, 12), (12, 22), (22, 35), (35, 50), (50, 65), (65, 80), (80, 90)):
        m = (np.degrees(la) >= lo_) & (np.degrees(la) < hi_)
        rows.append(('%d-%d' % (lo_, hi_), float(np.median(sq[m])), float(np.percentile(sq[m], 90)), float(np.median(s1[m])), float(np.median(s2[m])),
                     float(s2[m].min()), float((w[m] * (np.sign(det[m]) != sign)).sum() / w[m].sum())))
    keep = float((w * (sq < 1.25)).sum() / w.sum())
    return rows, keep, dict(la=la, lo=lo, s1=s1, s2=s2, sq=sq, det=det, g=g)


# ------------------------------------------------------------------ the attracting cycle (where orbits settle)
def find_cycle(rule, c, n=4000, seed=1, quiet=True):
    """Limit points of inside orbits: the points that orbits settle on (clustered to 1e-3). Also the share of the
    inside seeds that end on them."""
    rng = np.random.default_rng(seed); v = rng.uniform([-1.7, -1.3, -1.3], [1.7, 1.3, 1.3], size=(n * 12, 3)); v[: n * 4, 2] *= 0.05
    ins = M.stay(rule, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 150) >= 150; v = v[ins][:n]
    for _ in range(600):
        v = Fc(rule, v, c)
    v = v[np.isfinite(v).all(1) & ((v * v).sum(1) < 36)]
    pts = []
    for k in range(24):
        v = Fc(rule, v, c)
        for p in v[:: max(1, len(v) // 400)]:
            if not any(np.abs(p - q).max() < 2e-3 for q in pts):
                pts.append(p.copy())
            if len(pts) > 60:
                break
    return np.array(pts), int(len(v))


def lookup(grid, q):
    """Value of a block grid at the points q (n, 3); False outside the grid."""
    i = [np.floor(q[:, a] / H + VN[a] / 2).astype(np.int64) for a in range(3)]
    ok = np.ones(q.shape[0], bool)
    for a in range(3):
        ok &= (i[a] >= 0) & (i[a] < VN[a])
    out = np.zeros(q.shape[0], grid.dtype); out[ok] = grid[i[0][ok], i[1][ok], i[2][ok]]
    return out


def star_lumps(ins, cyc, rmax=1.4):
    """The MAIN LUMPS: every inside block that can be seen from a point of the attracting cycle along a straight line
    that stays inside. (The body round a cycle point as seen from its middle; a body that hangs on it behind a gap or
    a waist is not in it.)"""
    star = np.zeros(VN, bool); idx = np.nonzero(ins); P = centres(idx)
    for a in np.atleast_2d(cyc):
        d = P - a; dist = np.sqrt((d * d).sum(1)); ok = dist < rmax; step = H * 0.5
        for j in range(1, int(rmax / step) + 1):
            t = j * step; m = np.nonzero(ok & (dist > t))[0]
            if m.size == 0:
                break
            q = a + d[m] * (t / dist[m])[:, None]
            ok[m[~lookup(ins, q)]] = False
        star[idx[0][ok], idx[1][ok], idx[2][ok]] = True
    return star


BANDS = (0, 12, 22, 35, 50, 65, 90.001)
RHO = 0.15; LAT0 = 12.0


def trace(rule, P, c, cyc, steps=60, rho=RHO, lat0=LAT0, keep_path=False, landed=None):
    """Follow the points P (n, 3) until each comes within rho of the cycle `cyc` (k, 3).
    Returns a dict of arrays of length n:
      settle    step at which it settled (-1: never within `steps`)
      off       steps spent more than lat0 degrees off the flat plane before settling
      total     total squeeze (largest / smallest stretch of all steps together); mid = middle / smallest stretch
      sumlog    sum of the logs of the single steps' squeezes;  band[j] = the part of sumlog from latitude band j
      worst     the largest single-step squeeze, with worst_k (step), worst_lat, worst_lon (degrees)
      s2min     the smallest tangential stretch met (0 at a branch direction)
    keep_path: also 'path' (steps, n, 3), NaN after settling."""
    n = P.shape[0]; v = P.astype(float).copy(); cyc = np.atleast_2d(cyc)
    settle = np.full(n, -1, np.int32); off = np.zeros(n, np.int32); J = np.tile(np.eye(3), (n, 1, 1)); logn = np.zeros(n)
    sumlog = np.zeros(n); band = np.zeros((n, len(BANDS) - 1)); worst = np.ones(n); worst_k = np.full(n, -1, np.int32)
    worst_lat = np.zeros(n); worst_lon = np.zeros(n); s2min = np.full(n, 9.0); path = [] if keep_path else None

    def near(u):
        if landed is not None:
            return landed(u)
        return np.sqrt(((u[:, None, :] - cyc[None]) ** 2).sum(-1)).min(1) < rho
    act = np.arange(n); s0 = near(v); settle[s0] = 0; act = act[~s0]
    for k in range(steps):
        if keep_path:
            pp = np.full((n, 3), np.nan); pp[act] = v[act]; path.append(pp)
        if act.size == 0:
            break
        u = v[act]; r = np.sqrt((u * u).sum(1)); lat = np.degrees(np.arcsin(np.clip(np.abs(u[:, 2]) / np.maximum(r, 1e-300), 0, 1)))
        lon = np.degrees(np.arctan2(u[:, 1], u[:, 0]))
        off[act] += lat > lat0
        Jk = jac(rule, u, c); sv = np.linalg.svd(Jk / r[:, None, None], compute_uv=False)
        sq = np.maximum(sv[:, 0], 1e-300) / np.maximum(sv[:, 2], 1e-12); lg = np.log(sq)
        sumlog[act] += lg; b = np.clip(np.searchsorted(BANDS, lat, side='right') - 1, 0, len(BANDS) - 2); band[act, b] += lg
        better = sq > worst[act]; a2 = act[better]; worst[a2] = sq[better]; worst_k[a2] = k; worst_lat[a2] = lat[better]; worst_lon[a2] = lon[better]
        s2min[act] = np.minimum(s2min[act], sv[:, 2])
        Jn = Jk @ J[act]; nn = np.sqrt((Jn * Jn).sum((1, 2))); nn = np.where(nn > 0, nn, 1.0); J[act] = Jn / nn[:, None, None]; logn[act] += np.log(nn)
        w = Fc(rule, u, c); v[act] = w
        bad = ~np.isfinite(w).all(1) | ((w * w).sum(1) > 36)
        done = near(np.where(bad[:, None], 99.0, w)); settle[act[done]] = k + 1
        act = act[~done & ~bad]
    sv = np.linalg.svd(J, compute_uv=False)
    out = dict(land=v.copy(), sig1=sv[:, 0] * np.exp(logn), sig3=sv[:, 2] * np.exp(logn), settle=settle, off=off, total=sv[:, 0] / np.maximum(sv[:, 2], 1e-300), mid=sv[:, 1] / np.maximum(sv[:, 2], 1e-300),
               top=sv[:, 0] / np.maximum(sv[:, 1], 1e-300), sumlog=sumlog, band=band, worst=worst, worst_k=worst_k, worst_lat=worst_lat, worst_lon=worst_lon, s2min=s2min)
    if keep_path:
        out['path'] = np.array(path)
    return out


if __name__ == '__main__':
    # python out/r24/rough/rl.py           finite / flat check / cycle of every rule
    rng = np.random.default_rng(2); n = 20000
    p = rng.normal(size=(3, n)) * rng.uniform(1e-9, 2, n); p[2, :200] = 0; p[0, 200:260] = 0; p[1, 200:260] = 0; p[:, 260] = 0
    for nm in (sys.argv[1].split(',') if len(sys.argv) > 1 else list(MAKERS)):
        r = get(nm); o = r.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(r.init(n)), 1, 0.0, 0.0, 0.0)
        fin = bool(all(np.isfinite(t).all() for t in o[:3])); err = float(np.nanmax(np.abs(np.sqrt(o[0] ** 2 + o[1] ** 2 + o[2] ** 2) - (p * p).sum(0))))
        f = M.flat_check(r, n=8000, steps=60)
        print('%-10s finite %s | length squared, largest error %.1e | flat check, differ of %d: M %d, c=-1 %d, rabbit %d, Siegel %d, strays %.1e'
              % (nm, fin, err, f['of'], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))
        for sn in ('basilica', 'rabbit'):
            cyc, k = find_cycle(r, SETS[sn]); print('     %-8s settles on %d point(s): %s   (%d seeds)' % (sn, len(cyc), ' '.join('(%.3f %.3f %.3f)' % tuple(q) for q in cyc[:8]), k))
        sys.stdout.flush()
