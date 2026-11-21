"""Round 23, judge: my own small tools.

    import sys; sys.path.insert(0, 'out/r23/judge'); import jl as L

The rules that matter are typed here AGAIN from their written formulas (briefing, docstrings), not imported:
    L.MY['oneplane'], 'twoplane', 'along', 'alongonce', 'cones', 'cones1', 'cones2', 'cones3'
and python out/r23/judge/jl.py compares each with the section's own version on random points.
Other sections' rules (pillow, lens, bristor, outside formulas) are loaded through L.theirs(name).
The orbit loop (L.stay) is mine; it takes any rule with .step / .init of the library's shape.
"""
import os, sys, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

RABBIT = M.RABBIT; SIEGEL = M.SIEGEL; BAS = (-1.0, 0.0, 0.0); SANMARCO = (-0.75, 0.0, 0.0); DENDRITE = (0.0, 1.0, 0.0)
SETS = {'basilica': BAS, 'sanmarco': SANMARCO, 'rabbit': RABBIT, 'siegel': SIEGEL, 'dendrite': DENDRITE}


class Rule:
    def __init__(self, name, step, init=None):
        self.name = name; self.label = name; self.step = step; self.init = init or (lambda n: ())


# ------------------------------------------------------------------ the rules, typed again
def P(x, y, z):
    """One plane: f (x^2 - y^2, 2xy, 2rz), f = r^2 / (r^2 + z^2)."""
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); den = r2 + z * z; ok = den > 0; f = np.where(ok, r2 / np.where(ok, den, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def rotx(y, z, a):
    co, si = np.cos(a), np.sin(a); return co * y - si * z, si * y + co * z


def ALONG(x, y, z):
    """phi = atan2(z, y); psi = phi - sin(4 phi)/4; Rot_x(psi) P(Rot_x(-psi) v)."""
    phi = np.arctan2(z, y); psi = phi - np.sin(4 * phi) / 4
    y1, z1 = rotx(y, z, -psi); X, Y, Z = P(x, y1, z1); Y2, Z2 = rotx(Y, Z, psi); return X, Y2, Z2


def TWOPLANE(x, y, z):
    """The one-plane square about the flat plane or the upright plane (through the x-axis), whichever is nearer."""
    X1, Y1, Z1 = P(x, y, z); X2, Z2, Y2 = P(x, z, y); near_flat = np.abs(z) <= np.abs(y)
    return np.where(near_flat, X1, X2), np.where(near_flat, Y1, Y2), np.where(near_flat, Z1, Z2)


MU60 = float(np.log(2.0 + np.sqrt(3.0))); MUA = 0.2; MUB = MUA + (MU60 / 3 - MUA) / 0.59087


def unit_at(mu, lon):
    """Unit vector at Mercator latitude mu and longitude lon."""
    return np.cos(lon) / np.cosh(mu), np.sin(lon) / np.cosh(mu), np.tanh(mu)


def CONES(x, y, z, theta=np.pi / 2):
    """Welded cones, typed from the docstring of out/r23/cone/best.py."""
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); rs = np.where(r > 0, r, 1.0)
    mu = np.arctanh(np.clip(z / rs, -1 + 1e-15, 1 - 1e-15)); am = np.abs(mu); lam = np.arctan2(y, x)
    Ex, Ey, Ez = unit_at(np.minimum(2 * am, 60.0), 2 * lam)
    Cx, Cy, Cz = unit_at(np.clip(MU60 - am, -60.0, 60.0), theta - lam)
    q = np.clip((am - MUA) / (MUB - MUA), 0.0, 1.0); chi = q ** 3 * (10 - 15 * q + 6 * q * q)
    Gx, Gy, Gz = (1 - chi) * Ex + chi * Cx, (1 - chi) * Ey + chi * Cy, (1 - chi) * Ez + chi * Cz
    n = np.sqrt(Gx * Gx + Gy * Gy + Gz * Gz); n = np.where(n > 0, n, 1.0); sg = np.where(z < 0, -1.0, 1.0)
    return r2 * Gx / n, r2 * Gy / n, r2 * sg * Gz / n


def fixed(F, name):
    return Rule(name, lambda x, y, z, st, k, cx, cy, cz: (*F(x, y, z), st))


def first_n(F, n, name):
    """F for the first n squarings of every orbit, one plane for every later one."""
    return Rule(name, lambda x, y, z, st, k, cx, cy, cz: (*(F(x, y, z) if k < n else P(x, y, z)), st))


MY = {'oneplane': fixed(P, 'oneplane'), 'twoplane': fixed(TWOPLANE, 'twoplane'), 'along': fixed(ALONG, 'along'),
      'alongonce': first_n(ALONG, 1, 'alongonce'), 'cones': fixed(CONES, 'cones'),
      'cones1': first_n(CONES, 1, 'cones1'), 'cones2': first_n(CONES, 2, 'cones2'), 'cones3': first_n(CONES, 3, 'cones3')}


# ------------------------------------------------------------------ other sections' rules, by path
def _load(modname, *parts):
    if modname not in sys.modules:
        spec = importlib.util.spec_from_file_location(modname, os.path.join(ROOT, *parts))
        mod = importlib.util.module_from_spec(spec); sys.modules[modname] = mod; spec.loader.exec_module(mod)
    return sys.modules[modname]


def design():
    return _load('r23_design_rules', 'out', 'r23', 'design', 'rules.py')


def outside1():
    return _load('r23_outside1_outrules', 'out', 'r23', 'outside1', 'outrules.py')


def theirs(name):
    """'d:<name>' a rule of the design loader, 'o:<name>' an outside formula, 'r:<name>' a rule of the rabbit loader."""
    kind, nm = name.split(':', 1)
    if kind == 'd':
        return design().get(nm)
    if kind == 'o':
        return outside1().get(nm)
    if kind == 'r':
        sys.path.insert(0, os.path.join(ROOT, 'out', 'r23', 'rabbit'))
        design()                                              # replaces M.bench by a path loader first
        import doors as D
        return D.get(nm)
    raise KeyError(name)


def get(name):
    return MY[name] if name in MY else theirs(name)


# ------------------------------------------------------------------ my orbit loop
def stay(rule, x, y, z, c, steps, r2=36.0, chunk=400000):
    """How many steps each orbit stays inside |v| < 6 (steps = never left). Mine, not the library's."""
    sh = np.shape(x); x = np.array(x, float).ravel(); y = np.array(y, float).ravel(); z = np.array(z, float).ravel()
    out = np.zeros(x.size, np.int32)
    for i0 in range(0, x.size, chunk):
        px, py, pz = x[i0:i0 + chunk].copy(), y[i0:i0 + chunk].copy(), z[i0:i0 + chunk].copy(); n = px.size
        idx = np.arange(n); st = tuple(rule.init(n)); cnt = np.zeros(n, np.int32)
        for k in range(steps):
            cx, cy, cz = np.full(px.size, float(c[0])), np.full(px.size, float(c[1])), np.full(px.size, float(c[2]))
            with np.errstate(all='ignore'):
                o = rule.step(px, py, pz, st, k, cx, cy, cz)
            px, py, pz = o[0] + c[0], o[1] + c[1], o[2] + c[2]; st = tuple(o[3])
            keep = (px * px + py * py + pz * pz) < r2                      # a NaN fails this test: it counts as gone
            idx = idx[keep]; px, py, pz = px[keep], py[keep], pz[keep]; st = tuple(t[keep] for t in st)
            cnt[idx] += 1
            if idx.size == 0:
                break
        out[i0:i0 + chunk] = cnt
    return out.reshape(sh)


def flat_stay(zr, zi, c, steps, r2=36.0):
    z = np.array(zr, float) + 1j * np.array(zi, float); cc = complex(c[0], c[1]); n = np.zeros(z.shape, np.int32); alive = np.ones(z.shape, bool)
    for _ in range(steps):
        with np.errstate(all='ignore'):
            z = np.where(alive, z * z + cc, z)
        alive &= (z.real ** 2 + z.imag ** 2) < r2; n += alive
    return n


def blocks(rule, c, h, box, steps, slab=24):
    """Inside / outside on a grid of blocks of side h. box = (x0, x1, y0, y1, z0, z1). Returns (inside, xs, ys, zs)."""
    xs = np.arange(box[0] + h / 2, box[1], h); ys = np.arange(box[2] + h / 2, box[3], h); zs = np.arange(box[4] + h / 2, box[5], h)
    ins = np.zeros((xs.size, ys.size, zs.size), bool)
    for i0 in range(0, xs.size, slab):
        X, Y, Z = np.meshgrid(xs[i0:i0 + slab], ys, zs, indexing='ij')
        ins[i0:i0 + slab] = stay(rule, X, Y, Z, c, steps) >= steps
    return ins, xs, ys, zs


def solid(rule, c, w, h, nd, steps, half_w=1.6, cam=(0.45, 0.5, 1.0), centre=(0.0, 0.0, 0.0)):
    """Rough solid: the first block on each line of sight whose orbit never leaves (my loop; the library's eye frame)."""
    e1, e2, e3 = M.frame(cam)
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-half_w, half_w, nd)
    U, V = np.meshgrid(us, vs); depth = np.full((h, w), np.inf)
    for k0 in range(0, nd, 8):
        dk = ds[k0:k0 + 8]
        Pp = [centre[i] + U[None] * e1[i] + V[None] * e2[i] + dk[:, None, None] * e3[i] for i in range(3)]
        ins = stay(rule, Pp[0], Pp[1], Pp[2], c, steps) >= steps
        depth = np.minimum(depth, np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf))
    return depth, us[1] - us[0]


if __name__ == '__main__':
    # my typed rules against the sections' own, on random points (and special ones)
    rng = np.random.default_rng(7); n = 200000
    p = rng.normal(size=(3, n)) * rng.uniform(1e-6, 2, n); p[2, :500] = 0; p[0, 500:560] = 0; p[1, 500:560] = 0; p[:, 560] = 0
    cx, cy, cz = np.full(n, RABBIT[0]), np.full(n, RABBIT[1]), np.zeros(n)
    D = design()
    pairs = [('oneplane', M.bench('oneplane')), ('twoplane', M.bench('twoplane')), ('along', M.bench('along')),
             ('alongonce', D.get('alongonce')), ('cones', D.get('cones')), ('cones1', D.get('cones1')), ('cones2', D.get('cones2'))]
    for nm, th in pairs:
        mine = MY[nm]; worst = 0.0; fin = True
        for k in (0, 1, 2):
            a = mine.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(mine.init(n)), k, cx, cy, cz)
            b = th.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(th.init(n)), k, cx, cy, cz)
            fin &= bool(all(np.isfinite(t).all() for t in a[:3]))
            d = np.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3))); worst = max(worst, float(np.nanmax(d)))
        ln = float(np.max(np.abs(np.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) - (p * p).sum(0))))
        print('%-9s mine against theirs, steps 0 to 2, %d points: largest difference %.2e | mine finite: %s | length squared to %.1e' % (nm, n, worst, fin, ln)); sys.stdout.flush()
    # my loop against the library's
    v = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(60000, 3))
    for nm in ('along', 'cones1'):
        a = stay(MY[nm], v[:, 0], v[:, 1], v[:, 2], RABBIT, 60); b = M.stay(D.get(nm), v[:, 0], v[:, 1], v[:, 2], RABBIT[0], RABBIT[1], RABBIT[2], 60)
        print('%-9s my loop with my rule against M.stay with theirs, rabbit, 60 steps: %d of %d counts differ; inside share %.4f' % (nm, int((a != b).sum()), a.size, (a >= 60).mean()))
