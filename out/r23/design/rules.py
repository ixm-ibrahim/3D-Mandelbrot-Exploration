"""Round 23, section "design": one loader for the six rules tested here and the four reference rules.

    import sys; sys.path.insert(0, 'out/r23/design'); import rules as R
    r = R.get('lens')            # any name in R.SIX or R.REF;  R.PLAIN[name] is a label in plain words
    python out/r23/design/rules.py            # finite / length / flat check of every rule (about a minute)

The six (each is a rule of out/r21/lib/mem.py, M.Rule; c is added by the library):
  cones     the cone section's best rule ("welded cones", out/r23/cone/best.py), every step
  pillowJ   round 15's square pillow, Joukowski layout, height 1.3 (out/r15/study/fastpil.py), every step
  lens      NEW here: outside2's construction K2, "one plane with an arc blown up" (formula below), every step
  bristor   the Bristorbrot of outside1 (out/r23/outside1/outrules.py), every step
  cones1    NEW here: the welded cones for the FIRST step of every orbit, the one-plane rule for every later step
  conesup   NEW here: the welded cones with everything they lift pushed further toward the upright axis (cones_up)
Reference: oneplane, twoplane, along (bench), alongonce (round 21's alongmem.c_wake1).
Quick looks, not among the six (NOTES.md section 6): R.get('cones2'), 'cones3', ... (the cones for the first N steps),
'pillow1' (the pillow for the first step), 'conesU1', 'conesU2' (a rule with memory), 'conesup05', 'conesup2',
'v:rt30', 'v:rt-30' (any key of out/r23/cone/variants.py after 'v:'), and R.lens(name, b=..., rho=..., gamma=..., sx=..., ext=...).
Note: this file is called rules.py as the briefing asks, and so is the bench's. It replaces M.bench by a version that
loads the bench by path; import it BEFORE anything else that calls M.bench.

The lens rule (K2 of out/r23/outside2/constructions.md, with the arc allowed to lie east-west):
    d = the one-plane direction of (x, y, |z|)                       (unit vector, d_z >= 0)
    m = (cos b, 0, sin b), e1 = (-sin b, 0, cos b), e2 = (0, 1, 0)   (b = latitude of the lens's middle, above +x)
    only where x has the sign sx (one of the two square roots):
        p = ((d.e1) + i (d.e2)) / (1 + d.m) * exp(-i gamma) / eps    (angle-true chart about m; gamma turns the arc)
        if (Re p / a)^2 + (Im p / b')^2 < 1,  a = (rho + 1/rho)/2, b' = (rho - 1/rho)/2:
            zeta = rho (Re p / a + i Im p / b');   p = (zeta + 1/zeta) / 2
        d = the direction with chart coordinate p (zeta = 0 is the direction -m)
    square = |v|^2 d, its z given the sign of z.
Outside the ellipse the rule IS the one-plane rule. The small disc |zeta| < 1 is laid once over ALL directions.
The two new stopping directions (zeta = +1, -1) are sent to the two ends of the arc, chart coordinate +-eps.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
import importlib.util
for p in ('out/r21/lib', 'out/r15/study'):
    sys.path.insert(0, os.path.join(ROOT, *p.split('/')))
import mem as M
S = M.S                                   # round 16's scout: S.oneplane, S.twoplane


def _load(modname, *parts):
    """Load another section's file under a name of its own. (This file is called rules.py, and so is the bench's;
    several folders have a myrules.py. Loading by path keeps them apart.)"""
    if modname not in sys.modules:
        spec = importlib.util.spec_from_file_location(modname, os.path.join(ROOT, *parts))
        mod = importlib.util.module_from_spec(spec); sys.modules[modname] = mod; spec.loader.exec_module(mod)
    return sys.modules[modname]


BR = _load('r16_bench_rules', 'out', 'r16', 'bench', 'rules.py')
M.bench = lambda name: M.fixed(BR.get(name), name, BR.RULES[name][1])      # the library's own bench() does 'import rules', which would find THIS file


def lens_square(b=55.0, rho=1.6, gamma=90.0, sx=1.0, ext=0.25):
    """ext = how far the ellipse reaches along the meridian (chart units; 0.25 is about 28 degrees)."""
    bb = np.radians(b); cb, sb = np.cos(bb), np.sin(bb)
    a = (rho + 1 / rho) / 2; bp = (rho - 1 / rho) / 2
    g = np.radians(gamma); rot = np.exp(-1j * g)
    eps = ext / np.hypot(a * np.cos(g), bp * np.sin(g))       # the ellipse's half-width along e1 is ext

    def F(x, y, z):
        za = np.abs(z); X, Y, Z = S.oneplane(x, y, za); r2 = x * x + y * y + z * z; ok = r2 > 0; q = np.where(ok, r2, 1.0)
        dx, dy, dz = X / q, Y / q, Z / q
        dm = dx * cb + dz * sb; d1 = -dx * sb + dz * cb
        p = (d1 + 1j * dy) / (1 + dm) * rot / eps
        ins = (x * sx > 0) & ((p.real / a) ** 2 + (p.imag / bp) ** 2 < 1)
        if ins.any():
            pi_ = p[ins]; zeta = rho * (pi_.real / a + 1j * pi_.imag / bp)
            N = zeta * zeta + 1; D = 2 * zeta
            Q = eps * N * np.conj(D) * np.conj(rot); DD = np.abs(D) ** 2; NN = eps * eps * np.abs(N) ** 2; den = DD + NN
            cm, c1, c2 = (DD - NN) / den, 2 * Q.real / den, 2 * Q.imag / den
            dx = dx.copy(); dy = dy.copy(); dz = dz.copy()
            dx[ins] = cm * cb - c1 * sb; dy[ins] = c2; dz[ins] = cm * sb + c1 * cb
        sg = np.where(z < 0, -1.0, 1.0)
        return np.where(ok, r2 * dx, 0.0), np.where(ok, r2 * dy, 0.0), np.where(ok, r2 * dz * sg, 0.0)
    return F


def lens(name='lens', **kw):
    return M.fixed(lens_square(**kw), name, 'one plane with an arc blown up (K2), %s' % (kw or 'defaults'))


def pillow_rule(key=('J', 1.3, 2), name='pillowJ', label='square pillow, Joukowski layout, height 1.3'):
    import fastpil
    lay = fastpil.get_lay(key)

    def F(x, y, z):
        sh = np.shape(x)
        X, Y, Z = fastpil.F(np.ravel(x).astype(float).copy(), np.ravel(y).astype(float).copy(), np.ravel(z).astype(float).copy(), lay)
        return X.reshape(sh), Y.reshape(sh), Z.reshape(sh)
    return M.fixed(F, name, label)


def once(first, name, label, n_first=1):
    """`first` for the first n_first squarings of every orbit, the one-plane rule for every later one."""
    one = M.bench('oneplane')

    def step(x, y, z, st, k, cx, cy, cz):
        if k < n_first:
            o = first.step(x, y, z, tuple(first.init(np.size(x))), k, cx, cy, cz); return o[0], o[1], o[2], st
        return one.step(x, y, z, st, k, cx, cy, cz)
    return M.Rule(name, label, step, init=lambda n: ())


def _cones():
    return _load('r23_cone_best', 'out', 'r23', 'cone', 'best.py').rule()


def _bristor():
    return _load('r23_outside1_outrules', 'out', 'r23', 'outside1', 'outrules.py').get('bristor')


def _alongonce():
    return _load('r21_judge_myrules', 'out', 'r21', 'judge', 'myrules.py').get('alongmem.c_wake1')


def cones_up(A=1.0, m0=0.2, m1=0.7, theta=np.pi / 2, name=None):
    """A try made here (not one of the six): the welded cones, and then every direction that the rule sends higher
    than Mercator latitude m0 is pushed further toward the upright axis: mu -> mu + A * S((|mu| - m0) / (m1 - m0)),
    S the smooth step from 0 to 1, longitude kept. Near the flat plane nothing changes, so the flat plane and the two
    cones are still exact; no fold is added. The three directions per side where the rule stops stretching are then
    sent to Mercator latitude 0.88 + A (A = 1: 72 degrees) instead of 44.9 degrees."""
    best = _load('r23_cone_best', 'out', 'r23', 'cone', 'best.py')

    def step(x, y, z, st, k, cx, cy, cz):
        r2 = x * x + y * y + z * z; X, Y, Z = best.direction(x, y, z, theta); ok = r2 > 0
        az = np.clip(np.abs(Z), 0, 1 - 1e-15); mu = np.arctanh(az)
        q = np.clip((mu - m0) / (m1 - m0), 0.0, 1.0); mu2 = mu + A * q * q * q * (10 - 15 * q + 6 * q * q)
        Z2 = np.tanh(mu2); s = np.sqrt((1 - Z2 * Z2) / np.maximum(1 - az * az, 1e-300))
        return np.where(ok, r2 * X * s, 0.0), np.where(ok, r2 * Y * s, 0.0), np.where(ok, r2 * Z2 * np.where(Z < 0, -1.0, 1.0), 0.0), st
    return M.Rule(name or 'conesup', 'welded cones, images pushed toward the upright axis (A = %g, from %g to %g)' % (A, m0, m1), step, init=lambda n: ())


def cones_used(n_uses=1, name=None, theta=np.pi / 2):
    """A try made here (not one of the six): a rule with memory. Each orbit may be squared by the welded cones from
    outside their belt (Mercator latitude above 0.2, where the cones differ from one plane) at most n_uses times, at
    whatever step that happens; every other squaring is by the one-plane rule. The orbit carries the uses it has left.
    NOT continuous: two neighbours of which only one has spent its use part company later (a tear)."""
    best = _load('r23_cone_best', 'out', 'r23', 'cone', 'best.py')

    def step(x, y, z, st, k, cx, cy, cz):
        left = st[0]; r2 = x * x + y * y + z * z; r = np.sqrt(r2); rs = np.where(r > 0, r, 1.0)
        use = (np.abs(z) / rs > np.tanh(best.MUA)) & (left > 0.5)
        X, Y, Z = S.oneplane(x, y, z)
        if use.any():
            X, Y, Z = np.array(X), np.array(Y), np.array(Z)
            dx, dy, dz = best.direction(x[use], y[use], z[use], theta)
            X[use], Y[use], Z[use] = r2[use] * dx, r2[use] * dy, r2[use] * dz
        return X, Y, Z, (left - use,)
    return M.Rule(name or 'conesU%d' % n_uses, 'welded cones, at most %d use(s) per orbit, else one plane' % n_uses, step, init=lambda n: (np.full(n, float(n_uses)),))


LENS_KW = dict(b=55.0, rho=1.6, gamma=90.0, sx=1.0, ext=0.25)          # setting A of the three tried, see NOTES.md

MAKERS = {
    'oneplane': lambda: M.bench('oneplane'),
    'twoplane': lambda: M.bench('twoplane'),
    'along': lambda: M.bench('along'),
    'alongonce': _alongonce,
    'cones': _cones,
    'pillowJ': pillow_rule,
    'lens': lambda: lens('lens', **LENS_KW),
    'bristor': _bristor,
    'cones1': lambda: once(_cones(), 'cones1', 'welded cones for the first step, then one plane'),
    'pillow1': lambda: once(pillow_rule(), 'pillow1', 'square pillow (Joukowski) for the first step, then one plane'),
    'conesU1': lambda: cones_used(1),
    'conesU2': lambda: cones_used(2),
    'conesup': lambda: cones_up(1.0, 0.2, 0.7, name='conesup'),
    'conesup05': lambda: cones_up(0.5, 0.2, 0.7, name='conesup05'),
    'conesup2': lambda: cones_up(2.0, 0.2, 1.0, name='conesup2'),
}
REF = ['oneplane', 'twoplane', 'along', 'alongonce']
SIX = ['cones', 'pillowJ', 'lens', 'bristor', 'cones1', 'conesup']
PLAIN = {
    'oneplane': 'One plane',
    'twoplane': 'Two planes',
    'along': 'Along',
    'alongonce': 'Along once, then one plane',
    'cones': 'The flat picture also rolled up into two cones',
    'pillowJ': 'Square pillow, second layout',
    'lens': 'One plane with one small patch opened up on each side',
    'bristor': 'Bristorbrot (a formula from outside)',
    'cones1': 'Rolled-up cones for the first step only, then one plane',
    'cones2': 'Rolled-up cones for the first two steps only, then one plane',
    'conesup': 'Rolled-up cones, with everything it lifts pushed further up',
    'pillow1': 'Square pillow for the first step only, then one plane',
}
SETS = {'basilica': (-1.0, 0.0, 0.0), 'sanmarco': (-0.75, 0.0, 0.0), 'rabbit': M.RABBIT, 'siegel': M.SIEGEL, 'dendrite': (0.0, 1.0, 0.0)}
SETNAME = {'basilica': 'c = -1', 'sanmarco': 'c = -0.75', 'rabbit': 'rabbit', 'siegel': 'Siegel disc', 'dendrite': 'dendrite, c = i'}
_made = {}


def _variant(key):
    """A variant of the cone section by its key in out/r23/cone/variants.py (for example 'rt30', 'weld0b2')."""
    cone = os.path.join(ROOT, 'out', 'r23', 'cone')
    if cone not in sys.path:
        sys.path.insert(0, cone)
    import variants as V
    return V.get(key)


def get(name):
    """Names of MAKERS; also 'cones<N>' / 'rt30_<N>' (that rule for the first N steps, then one plane) and 'v:<key>'
    (a variant of the cone section)."""
    if name not in _made:
        if name in MAKERS:
            r = MAKERS[name]()
        elif name.startswith('cones') and name[5:].isdigit():
            r = once(_cones(), name, 'welded cones for the first %s steps, then one plane' % name[5:], int(name[5:]))
        elif name.startswith('v:') and '_' in name and name.rsplit('_', 1)[1].isdigit():
            key, n = name[2:].rsplit('_', 1); r = once(_variant(key), name, '%s for the first %s steps, then one plane' % (key, n), int(n))
        elif name.startswith('v:'):
            r = _variant(name[2:])
        else:
            raise KeyError(name)
        r.plain = PLAIN.get(name, name); _made[name] = r
    return _made[name]


if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else REF + SIX
    rng = np.random.default_rng(2); n = 20000
    p = rng.normal(size=(3, n)) * rng.uniform(1e-9, 2, n); p[2, :200] = 0; p[0, 200:260] = 0; p[1, 200:260] = 0; p[:, 260] = 0
    for nm in names:
        r = get(nm); worst = 0.0; fin = True
        for k in (0, 1):
            o = r.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(r.init(n)), k, np.full(n, -0.12), np.full(n, 0.74), np.zeros(n))
            fin &= bool(all(np.isfinite(t).all() for t in o[:3]))
            worst = max(worst, float(np.nanmax(np.abs(np.sqrt(o[0] ** 2 + o[1] ** 2 + o[2] ** 2) - (p * p).sum(0)))))
        f = M.flat_check(r, n=8000, steps=60)
        print('%-9s finite %s | length squared, largest error %.1e | flat check, differ of %d: M %d, c=-1 %d, rabbit %d, Siegel %d, strays %.1e'
              % (nm, fin, worst, f['of'], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page'])); sys.stdout.flush()
