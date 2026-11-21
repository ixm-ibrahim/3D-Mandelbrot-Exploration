"""Round 24, section "push": the library of this section.

    import sys; sys.path.insert(0, 'out/r24/push'); import plib as P

Everything here is a rule  F(v) = |v|^2 * G(direction of v), then + c  (G = "direction map": unit vector -> unit vector).

    P.DIRS[name]            the direction map G(x, y, z) -> (X, Y, Z)
    P.rule(name)            the library rule (out/r21/lib/mem.py, M.Rule)
    P.CASES                 the panel of c: name -> dict(c, a, kind, q, cycle)
    P.column(G, a, c, h)    one step of a point lifted by h above the flat point a: (new height, new flat position)
    P.law(G, case)          the predictions (law A: push * d at lifts 8 / 15 / 25; law B: the weakest one-step height gain)
    P.column_test(...)      what really happens to points straight above the meeting point
    P.neck(...)             the widest ball that can pass from one body to the next near the meeting point

Names of rules: one, v1 (first version, m = 3, t = +0.268), v2 (second version, t = -0.268), m4 (m = 4, t = -0.10),
m4b (m = 4, t = -0.20), m6 (m = 6, t = -0.10), cones (welded cones of round 23), tri (even-spacing end, kite layout).
More are added by other files of this folder (P.add).
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


def _load(modname, *parts):
    if modname not in sys.modules:
        spec = importlib.util.spec_from_file_location(modname, os.path.join(ROOT, *parts))
        mod = importlib.util.module_from_spec(spec); sys.modules[modname] = mod; spec.loader.exec_module(mod)
    return sys.modules[modname]


BEST = _load('r23_cone_best', 'out', 'r23', 'cone', 'best.py')
T15 = 2.0 - np.sqrt(3.0)


# ---------------------------------------------------------------- direction maps
def one_dir(x, y, z):
    """Plain doubling (the one-plane rule): Mercator latitude and longitude doubled."""
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
    mu = np.arctanh(np.clip(z / rs, -1 + 1e-15, 1 - 1e-15)); lam = np.arctan2(y, x); a = np.clip(2 * mu, -60.0, 60.0)
    return np.cos(2 * lam) / np.cosh(a), np.sin(2 * lam) / np.cosh(a), np.tanh(a)


def mdir(m, t, mu1=0.4, blend=True):
    return lambda x, y, z: MF.mdir(x, y, z, m, t, mu1, blend)


def turned(G, phi):
    """The pattern of G turned by phi (radians) about the upright axis: Rot(2 phi) G Rot(-phi). Doubling stays doubling."""
    co, si, c2, s2 = np.cos(phi), np.sin(phi), np.cos(2 * phi), np.sin(2 * phi)

    def H(x, y, z):
        X, Y, Z = G(co * x + si * y, co * y - si * x, z)
        return c2 * X - s2 * Y, s2 * X + c2 * Y, Z
    return H


DIRS = {}; LABEL = {}; _rules = {}


def add(name, G, label):
    DIRS[name] = G; LABEL[name] = label; _rules.pop(name, None)


add('one', one_dir, 'one plane (plain doubling)')
add('v1', mdir(3, +T15), 'first version (copy once round, dial +0.268)')
add('v2', mdir(3, -T15), 'second version (copy once round, dial -0.268)')
add('m4', mdir(4, -0.10), 'copy twice round, dial -0.10')
add('m4b', mdir(4, -0.20), 'copy twice round, dial -0.20')
add('m6', mdir(6, -0.10), 'copy four times round, dial -0.10')
add('cones', lambda x, y, z: BEST.direction(x, y, z, np.pi / 2), 'welded cones of round 23')
add('tri', lambda x, y, z: T.tri_dir(x, y, z), 'even-spacing end (two flat triangles)')
MAIN = ['one', 'v1', 'v2', 'm4', 'm6', 'cones', 'tri']


def rule_of(G, name, label=''):
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        X, Y, Z = G(x, y, z); ok = r2 > 0
        return np.where(ok, r2 * X, 0.0), np.where(ok, r2 * Y, 0.0), np.where(ok, r2 * Z, 0.0)
    return M.fixed(F, name, label or name)


def rule(name):
    if name not in _rules:
        _rules[name] = rule_of(DIRS[name], name, LABEL[name])
    return _rules[name]


def alpha(c):
    """The flat fixed point with the smaller pull: (1 - sqrt(1 - 4c)) / 2. Meeting point of the bodies when c is in a bud."""
    return (1 - np.sqrt(1 - 4 * (c + 0j))) / 2


def facing_rule(G, name, label=''):
    """A rule that LOOKS AT c: the pattern of G is turned so that its longitude 0 faces the flat fixed point alpha(c)."""
    def step(x, y, z, st, k, cx, cy, cz):
        a = alpha(cx + 1j * cy); n = np.abs(a); n = np.where(n > 0, n, 1.0); e = np.where(np.abs(a) > 0, a / n, 1.0 + 0j)
        co, si = e.real, e.imag; c2, s2 = co * co - si * si, 2 * co * si
        r2 = x * x + y * y + z * z; X, Y, Z = G(co * x + si * y, co * y - si * x, z); ok = r2 > 0
        return np.where(ok, r2 * (c2 * X - s2 * Y), 0.0), np.where(ok, r2 * (s2 * X + c2 * Y), 0.0), np.where(ok, r2 * Z, 0.0), st
    return M.Rule(name, label or name, step, init=lambda n: ())


# ---------------------------------------------------------------- the panel of c
def centre(p, q):
    """The middle of the p/q bud of the main body (Newton on 'the orbit of 0 closes after q steps')."""
    lam = (1 + 1.0 / q ** 2) * np.exp(2j * np.pi * p / q); c = lam / 2 - lam * lam / 4
    for _ in range(80):
        z = 0j; dz = 0j
        for _k in range(q):
            dz = 2 * z * dz + 1; z = z * z + c
        c = c - z / dz
    return c


def _cycle(c, q):
    """The closed orbit that the orbit of 0 settles on (q points, the one nearest 0 first: it lies in the body of 0)."""
    z = 0j
    for _ in range(30000):
        z = z * z + c
    out = []
    for _ in range(q):
        out.append(z); z = z * z + c
    out = np.array(out)
    return np.roll(out, -int(np.argmin(np.abs(out))))


def _case(name, c, kind, q=1, **kw):
    a = alpha(c); d = dict(name=name, c=complex(c), a=complex(a), kind=kind, q=q, d=float(abs(a)), lon=float(np.degrees(np.angle(a)) % 360)); d.update(kw); return d


def _airplane_root():
    """The repelling 3-cycle on the rim of the airplane's three big bodies (real; found by Newton on f^3(x) = x)."""
    c = -1.754878; f = lambda x: ((x * x + c) ** 2 + c) ** 2 + c - x
    xs = np.linspace(-2, 2, 400001); v = f(xs); r = xs[:-1][np.sign(v[:-1]) != np.sign(v[1:])]
    out = []
    for x in r:
        for _ in range(40):
            hh = 1e-7; x = x - f(x) / ((f(x + hh) - f(x - hh)) / (2 * hh))
        m = abs(8 * x * (x * x + c) * ((x * x + c) ** 2 + c))
        out.append((x, m))
    return out


def build_cases():
    cs = {}
    cs['1/2'] = _case('1/2 bud, middle (c = -1)', -1.0, 'bud', 2)
    cs['1/2root'] = _case('1/2 bud, where it joins (c = -0.75)', -0.75, 'root', 2)
    cs['1/3'] = _case('1/3 bud, middle (rabbit)', complex(M.RABBIT[0], M.RABBIT[1]), 'bud', 3)
    lam = 1.05 * np.exp(2j * np.pi / 3)
    cs['1/3near'] = _case('1/3 bud, half way to where it joins', lam / 2 - lam * lam / 4, 'bud', 3)
    cs['1/4'] = _case('1/4 bud, middle', centre(1, 4), 'bud', 4)
    cs['2/5'] = _case('2/5 bud, middle', centre(2, 5), 'bud', 5)
    cs['1/5'] = _case('1/5 bud, middle', centre(1, 5), 'bud', 5)
    cs['1/6'] = _case('1/6 bud, middle', centre(1, 6), 'bud', 6)
    cs['3/7'] = _case('3/7 bud, middle', centre(3, 7), 'bud', 7)
    lam = 0.92 * np.exp(2j * np.pi / 3)
    cs['in120'] = _case('inside the main body, toward the 1/3 bud', lam / 2 - lam * lam / 4, 'inside')
    cs['in180'] = _case('inside the main body, toward the 1/2 bud (c = -0.6)', -0.6, 'inside')
    cs['siegel'] = _case('Siegel disc', complex(M.SIEGEL[0], M.SIEGEL[1]), 'siegel')
    cs['airplane'] = _case('airplane (c = -1.7549)', -1.754878, 'airplane', 3)
    for k, v in cs.items():
        v['key'] = k
        if v['kind'] == 'bud':
            v['cycle'] = _cycle(v['c'], v['q'])
    return cs


CASES = build_cases()
BUDS = ['1/2', '1/3', '1/3near', '1/4', '2/5', '1/5', '1/6', '3/7']


# ---------------------------------------------------------------- the push, and one step of a lifted point
def push(G, lon_deg, lift_deg):
    """Image latitude / lift, for a direction at longitude lon lifted by lift degrees off the flat circle."""
    lo, la = np.radians(np.asarray(lon_deg, float)), np.radians(np.asarray(lift_deg, float))
    X, Y, Z = G(np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la) + 0 * lo)
    return np.arcsin(np.clip(Z, -1, 1)) / la


def column(G, a, c, h):
    """One step of the points a + (0, 0, h): returns (new height, new flat position as a complex number)."""
    h = np.asarray(h, float); x = a.real + 0 * h; y = a.imag + 0 * h
    r2 = x * x + y * y + h * h; X, Y, Z = G(x, y, h)
    return r2 * Z, r2 * (X + 1j * Y) + c


def gain(G, a, c, lifts_deg):
    """One-step height gain H(h) / h of the point lifted above a to the latitude lift (as seen from 0)."""
    h = abs(a) * np.tan(np.radians(np.asarray(lifts_deg, float))); H, _ = column(G, a, c, h)
    return H / h


def law(G, case, top=50.0):
    """Law A (the briefing's): push * d at lifts 8, 15, 25. Law B (this section's): the weakest one-step height gain of a
    point lifted straight above the meeting point, over lifts 1 .. top degrees, and the lift where it is weakest."""
    a, c = case['a'], case['c']; lon, d = case['lon'], case['d']
    A = [float(push(G, lon, L)) * d for L in (8.0, 15.0, 25.0)]
    lifts = np.arange(1.0, top + 0.01, 0.5); g = gain(G, a, c, lifts); i = int(np.argmin(g))
    below = lifts[g < 1.0]
    return dict(A=A, A_min=min(A), B=float(g[i]), B_at=float(lifts[i]), first_below=float(below[0]) if below.size else None, lin=2 * d)


# ---------------------------------------------------------------- what really happens
def column_test(r, case, steps=600, hmax=0.9, n=225, at=None, disc=0.0):
    """Points straight above the flat point `at` (default: the meeting point): which heights stay inside for `steps` steps.
    Returns (heights, inside flags). disc > 0: nine points in a small disc instead of one; a height counts if 5 of 9 stay."""
    a = case['a'] if at is None else at; c = case['c']; h = np.linspace(hmax / n, hmax, n)
    if disc > 0:
        off = np.concatenate([[0j], disc * np.exp(2j * np.pi * np.arange(8) / 8)])
        X = a.real + off.real[:, None] + 0 * h[None]; Y = a.imag + off.imag[:, None] + 0 * h[None]; Z = h[None] + 0 * X
        ins = (M.stay(r, X, Y, Z, c.real, c.imag, 0.0, steps) >= steps).sum(0) >= 5
    else:
        ins = M.stay(r, a.real + 0 * h, a.imag + 0 * h, h, c.real, c.imag, 0.0, steps) >= steps
    return h, ins


def column_summary(h, ins):
    """(height of the solid straight above the point = top of the first unbroken inside run from the bottom,
        total length inside, lowest height that escapes)."""
    dh = h[1] - h[0]
    first_out = int(np.argmin(ins)) if (~ins).any() else len(h)
    top = float(h[first_out - 1]) if first_out > 0 else 0.0
    return top, float(ins.sum() * dh), (float(h[first_out]) if first_out < len(h) else None)


def seeds(case, frac=0.55):
    """One flat point well inside each body that touches the meeting point: on the way from the meeting point to the
    body's own middle (the point of the closed orbit of 0 in it)."""
    a, c = case['a'], case['c']; out = []
    if case['kind'] == 'root':
        return [a + 0.2, a - 0.2]
    for zk in case['cycle']:
        for f in (frac, 0.7, 0.4, 0.85):
            s = a + f * (zk - a)
            if M.flat_stay(np.array([s.real]), np.array([s.imag]), c.real, c.imag, 2000)[0] >= 2000:
                out.append(s); break
        else:
            out.append(None)
    return out


def grid_inside(r, case, L=0.32, n=80, steps=150):
    """The inside of a box round the meeting point (half-width L, mirrored in z), as blocks."""
    a, c = case['a'], case['c']
    xs = a.real + np.linspace(-L, L, n); ys = a.imag + np.linspace(-L, L, n); nz = n // 2 + 1; zs = np.linspace(0.0, L, nz)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    ins = M.stay(r, X, Y, Z, c.real, c.imag, 0.0, steps) >= steps
    return np.concatenate([ins[:, :, :0:-1], ins], axis=2), xs, ys, zs


def neck(ins, xs, ys, zs, case, sd=None):
    """For each body other than the body of 0: the radius of the widest ball that can travel from the body of 0 into it
    without leaving the inside (0 = they do not hang together in the box), and the ball that fits at the two start points.
    Returns a list of (neck radius, body radius) and the block size."""
    from scipy import ndimage
    dx = xs[1] - xs[0]; dz = zs[1] - zs[0]
    edt = ndimage.distance_transform_edt(ins, sampling=(dx, dx, dz)); st = np.ones((3, 3, 3), bool)
    sd = sd or seeds(case); k0 = len(zs) - 1; idx = []
    for s in sd:
        if s is None:
            idx.append(None); continue
        i = int(np.clip(round((s.real - xs[0]) / dx), 1, len(xs) - 2)); j = int(np.clip(round((s.imag - ys[0]) / dx), 1, len(ys) - 2))
        sub = edt[i - 1:i + 2, j - 1:j + 2, k0]; ii, jj = np.unravel_index(int(np.argmax(sub)), sub.shape)
        idx.append((i - 1 + ii, j - 1 + jj, k0))
    out = []
    for k in range(1, len(idx)):
        if idx[0] is None or idx[k] is None:
            out.append((None, None)); continue
        body = float(min(edt[idx[0]], edt[idx[k]])); lo, hi = 0.0, body
        lab, _ = ndimage.label(ins, structure=st)
        if body <= 0 or lab[idx[0]] != lab[idx[k]]:
            out.append((0.0, body)); continue
        lo = 1e-9
        for _ in range(12):
            mid = (lo + hi) / 2; lab, _ = ndimage.label(edt >= mid, structure=st)
            if lab[idx[0]] and lab[idx[0]] == lab[idx[k]]:
                lo = mid
            else:
                hi = mid
        out.append((float(lo), body))
    return out, float(dx)


if __name__ == '__main__':
    # python out/r24/push/plib.py : the panel, and a check of every rule (finite, length squared, flat picture)
    print('the panel of c:')
    for k, v in CASES.items():
        print('   %-9s %-52s c = %+.6f %+.6fi | flat fixed point a = %+.4f %+.4fi, distance %.4f, longitude %6.1f, pull 2d = %.4f'
              % (k, v['name'], v['c'].real, v['c'].imag, v['a'].real, v['a'].imag, v['d'], v['lon'], 2 * v['d']))
    print('airplane, the 3-cycles on the x-axis (point, pull of the whole cycle):', ['%.4f (%.2f)' % t for t in _airplane_root()])
    rng = np.random.default_rng(2); n = 20000
    p = rng.normal(size=(3, n)) * rng.uniform(1e-9, 2, n); p[2, :200] = 0; p[0, 200:260] = 0; p[1, 200:260] = 0
    S = M.S
    X, Y, Z = S.oneplane(p[0], p[1], p[2]); o = rule('one').step(p[0], p[1], p[2], (), 0, 0, 0, 0)
    print('one_dir against the bench one-plane rule: largest difference %.1e' % max(np.abs(o[0] - X).max(), np.abs(o[1] - Y).max(), np.abs(o[2] - Z).max()))
    for nm in DIRS:
        r = rule(nm); o = r.step(p[0].copy(), p[1].copy(), p[2].copy(), (), 0, np.zeros(n), np.zeros(n), np.zeros(n))
        fin = bool(all(np.isfinite(t).all() for t in o[:3])); err = float(np.nanmax(np.abs(np.sqrt(o[0] ** 2 + o[1] ** 2 + o[2] ** 2) - (p * p).sum(0))))
        f = M.flat_check(r, n=8000, steps=60)
        print('%-6s finite %s | length squared, largest error %.1e | flat check, differ of %d: M %d, c=-1 %d, rabbit %d, Siegel %d, strays %.1e'
              % (nm, fin, err, f['of'], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page'])); sys.stdout.flush()
