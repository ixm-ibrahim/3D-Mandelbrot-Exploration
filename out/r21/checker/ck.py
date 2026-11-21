"""Round 21, the CHECKER's own tools. Every rule here is re-coded by me from the WORDS of a report (not copied
from the reporter's file), so that 'their code' can be compared with 'their definition', verdict by verdict.

    import sys; sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker'); import mem as M, ck
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M

PI = np.pi
RABBIT = (-0.122561, 0.744862, 0.0); SIEGEL = (-0.390541, -0.586788, 0.0)


# ------------------------------------------------------------------ my own one-plane square, and P about a sheet
def P(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); f = r2 / np.maximum(r2 + z * z, 1e-300)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def sq_th(x, y, z, th):
    """P about the sheet through the x-axis at the turn th (radians): Rot_x(th) P(Rot_x(-th) v). No half-angle formula."""
    co, si = np.cos(th), np.sin(th)
    X, Y, Z = P(x, co * y + si * z, co * z - si * y)
    return X, co * Y - si * Z, si * Y + co * Z


def lathe(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def wrap90(d):
    return d - PI * np.round(d / PI)


def wrap180(t):
    return t - 2 * PI * np.round(t / (2 * PI))


def own_turn(y, z, th):
    return np.where(y * y + z * z > 0, np.arctan2(z, y), th)


def along_sq(x, y, z):
    phi = np.arctan2(z, y); psi = phi - np.sin(4 * phi) / 4
    return sq_th(x, y, z, psi)


Z1 = lambda n: (np.zeros(n),)


def R(name, step, init=Z1):
    return M.Rule(name, name, step, init)


# ------------------------------------------------------------------ rules of the reports, re-coded from their words
def fixed_sheet(deg):
    """P about a sheet that never moves, turned deg degrees from the flat page."""
    th = np.radians(deg)
    return R('fixed%g' % deg, lambda x, y, z, st, k, cx, cy, cz: (*sq_th(x, y, z, th), st), lambda n: ())


def lag(lam):
    """The scout's lag, with the sheet carried as an angle (no half-angle read-back, so no dead zone)."""
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]; d = wrap90(own_turn(y, z, th) - th)
        th = th + 0.5 * np.arctan2(lam * np.sin(2 * d), (1 - lam) + lam * np.cos(2 * d))
        return (*sq_th(x, y, z, th), (th,))
    return R('lag%g(mine)' % lam, step)


def delay():
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]
        return (*sq_th(x, y, z, th), (own_turn(y, z, th),))
    return R('delay(mine)', step)


def first_k(kk):
    """kk squarings by P about the flat page, every later one by the lathe formula."""
    def step(x, y, z, st, k, cx, cy, cz):
        return (*(P(x, y, z) if k < kk else lathe(x, y, z)), st)
    return R('first%d(mine)' % kk, step, lambda n: ())


def ease():
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]; d = wrap90(own_turn(y, z, th) - th); th = th + d - np.sin(2 * d) / 2
        return (*sq_th(x, y, z, th), (th,))
    return R('ease(mine)', step)


def vote(s):
    def step(x, y, z, st, k, cx, cy, cz):
        w1, w2 = st[0] + (y * y - z * z), st[1] + 2 * y * z
        return (*sq_th(x, y, z, 0.5 * np.arctan2(w2, w1)), (w1, w2))
    return R('vote%g(mine)' % s, step, lambda n: (np.full(n, float(s)), np.zeros(n)))


def evc(s=0.05, ease_c=0.7, ease_p=0.7, kc=16.0):
    def one(w1, w2, y, z, e, kk):
        pw = np.arctan2(w2, w1); t = wrap180(np.arctan2(2 * y * z, y * y - z * z) - pw); a = pw + t - e * np.sin(t)
        wt = kk * (y * y + z * z)
        return w1 + wt * np.cos(a), w2 + wt * np.sin(a)

    def step(x, y, z, st, k, cx, cy, cz):
        w1, w2 = one(st[0], st[1], cy, cz, ease_c, kc)
        w1, w2 = one(w1, w2, y, z, ease_p, 1.0)
        return (*sq_th(x, y, z, 0.5 * np.arctan2(w2, w1)), (w1, w2))
    return R('evc(%g,%g,%g,%g)(mine)' % (s, ease_c, ease_p, kc), step, lambda n: (np.full(n, float(s)), np.zeros(n)))


def wake(n0):
    """n0 squarings by along, every later one by P about the flat page."""
    def step(x, y, z, st, k, cx, cy, cz):
        return (*(along_sq(x, y, z) if k < n0 else P(x, y, z)), st)
    return R('wake%d(mine)' % n0, step, lambda n: ())


def keep_along():
    """b_keep: the sheet is along's sheet of the START point (the flat page if that point is on the x-axis); every
    squaring is P about that sheet."""
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]
        if k == 0:
            phi = np.arctan2(z, y); th = np.where(y * y + z * z > 0, phi - np.sin(4 * phi) / 4, 0.0)
        return (*sq_th(x, y, z, th), (th,))
    return R('keep_along(mine)', step)


# ------------------------------------------------------------------ an iteration of my own (no orbit is dropped)
def stay2(rule, x, y, z, cx, cy, cz, steps, r2=36.0):
    sh = np.shape(x)
    x, y, z, cx, cy, cz = (np.array(np.broadcast_to(np.asarray(t, float), sh)).ravel() for t in (x, y, z, cx, cy, cz))
    st = tuple(rule.init(x.size)); alive = np.ones(x.size, bool); n = np.zeros(x.size, np.int32)
    with np.errstate(all='ignore'):
        for k in range(steps):
            X, Y, Z, st = rule.step(x, y, z, st, k, cx, cy, cz); st = tuple(st)
            x, y, z = X + cx, Y + cy, Z + cz
            alive &= (x * x + y * y + z * z) < r2
            x, y, z = (np.where(alive, t, 0.0) for t in (x, y, z))        # dead orbits are parked at 0 and never counted again
            n += alive
    return n.reshape(sh)


# ------------------------------------------------------------------ measurements
def inside(rule, x, y, z, c, steps):
    """c = None: Mandelbrot verdict of the points; else the Julia set of c."""
    if c is None:
        return M.mandel(rule, x, y, z, steps) >= steps
    return M.stay(rule, x, y, z, c[0], c[1], c[2], steps) >= steps


def circle(rule, x0, rad, c, steps, n=2880, off=0.0):
    """Walk round the x-axis on the circle x = x0, radius rad: returns the list of arcs that are inside,
    as (middle in degrees from +y toward +z, width in degrees), and the inside share."""
    a = (np.arange(n) + off) * 2 * PI / n
    ins = inside(rule, np.full(n, x0), rad * np.cos(a), rad * np.sin(a), c, steps)
    if ins.all():
        return [('ring', 360.0)], 1.0
    if not ins.any():
        return [], 0.0
    i0 = int(np.argmin(ins)); r = np.roll(ins, -i0); arcs = []; j = 0
    while j < n:
        if r[j]:
            k = j
            while k < n and r[k]:
                k += 1
            mid = ((j + k - 1) / 2 + i0 + off) * 360.0 / n
            arcs.append((round(float(mid % 360), 2), round((k - j) * 360.0 / n, 2))); j = k
        else:
            j += 1
    return arcs, float(ins.mean())


def volume(rule, c, steps, n=120000, seed=11, box=((-1.8, 1.8), (-1.3, 1.3), (-1.3, 1.3))):
    rng = np.random.default_rng(seed)
    p = [rng.uniform(lo, hi, n) for lo, hi in box]
    return float(inside(rule, p[0], p[1], p[2], c, steps).mean())


def lift_loss(rule, c, lift, steps=300, n=30000, seed=7, deep=80):
    """Flat-inside points (well inside: the flat orbit stays `steps` steps AND a point is only taken if its 8
    neighbours 0.004 away are inside too), lifted `lift` off the page: how many are lost. c = None: Mandelbrot."""
    rng = np.random.default_rng(seed)
    if c is None:
        a, b = rng.uniform(-2.1, 0.7, n), rng.uniform(-1.3, 1.3, n)
        ok = np.ones(n, bool)
        for da in (-0.004, 0, 0.004):
            for db in (-0.004, 0, 0.004):
                ok &= M.flat_stay(a + da, b + db, a + da, b + db, steps) >= steps
        a, b = a[ok], b[ok]
        lost = ~(M.mandel(rule, a, b, np.full(a.size, lift), steps) >= steps)
    else:
        a, b = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
        ok = np.ones(n, bool)
        for da in (-0.004, 0, 0.004):
            for db in (-0.004, 0, 0.004):
                ok &= M.flat_stay(a + da, b + db, c[0], c[1], steps) >= steps
        a, b = a[ok], b[ok]
        lost = ~(M.stay(rule, a, b, np.full(a.size, lift), c[0], c[1], c[2], steps) >= steps)
    return int(lost.sum()), int(a.size)


def differ(r1, r2, c, steps=60, n=60000, seed=13, box=((-1.8, 1.8), (-1.3, 1.3), (-1.3, 1.3))):
    """Verdicts that differ between two rules on random points of the box (c = None: Mandelbrot, box -2.1..0.7)."""
    rng = np.random.default_rng(seed)
    if c is None:
        box = ((-2.1, 0.7), (-1.3, 1.3), (-1.3, 1.3))
    p = [rng.uniform(lo, hi, n) for lo, hi in box]
    a, b = inside(r1, *p, c, steps), inside(r2, *p, c, steps)
    return int((a != b).sum()), int(a.sum()), int(b.sum()), n


def turned(rule, deg, c, steps=40, n=40000, seed=5, mirror=None):
    """Share of verdicts that change when every test point is turned by deg degrees round the x-axis
    (mirror = 'page': z -> -z instead; 'upright': y -> -y). c = None: the Mandelbrot solid."""
    rng = np.random.default_rng(seed)
    box = ((-2.1, 0.7), (-1.3, 1.3), (-1.3, 1.3)) if c is None else ((-1.8, 1.8), (-1.2, 1.2), (-1.2, 1.2))
    p = [rng.uniform(lo, hi, n) for lo, hi in box]
    if mirror == 'page':
        q = (p[0], p[1], -p[2])
    elif mirror == 'upright':
        q = (p[0], -p[1], p[2])
    else:
        a = np.radians(deg); q = (p[0], np.cos(a) * p[1] - np.sin(a) * p[2], np.sin(a) * p[1] + np.cos(a) * p[2])
    v1, v2 = inside(rule, *p, c, steps), inside(rule, *q, c, steps)
    return float((v1 != v2).mean()), float(v1.mean())


def load(folder):
    """Another agent's myrules.py as a module (read-only use: their rules are the things under test)."""
    import importlib.util
    path = os.path.join(os.path.dirname(HERE), folder, 'myrules.py')
    spec = importlib.util.spec_from_file_location('rules_' + folder, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def byname(mod, name):
    for r in mod.RULES:
        if r.name == name:
            return r
    raise KeyError(name)
