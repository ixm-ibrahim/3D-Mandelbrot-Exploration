"""Round 23, section "rabbit": every rule in one loader, the test shapes off the x-axis, and cached blocks / depth maps.

    import sys; sys.path.insert(0, 'out/r23/rabbit'); import doors as D
    r = D.get('along')            # any key of D.RULES, D.TRIES, or 'alongN' with a number N (0 = one plane, 99 = along)
    D.SETS['rabbit']              # the constant c of each test shape

    python out/r23/rabbit/doors.py time                       speed and NaN test of every rule
    python out/r23/rabbit/doors.py vox  <rules> <sets>        blocks (how long each orbit stays), cached in cache/
    python out/r23/rabbit/doors.py dep  <rules> <sets> [eye]  depth maps for rough solids, cached in cache/
    (<rules>, <sets>: names joined by commas, or 'all')

Nothing here iterates by itself: every orbit goes through M.stay of out/r21/lib/mem.py.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in ('out/r21/lib', 'out/r21/judge', 'out/r23/me', 'out/r15/study'):
    sys.path.insert(0, os.path.join(ROOT, *p.split('/')))
import mem as M
import myrules as J
import cone as CONE
import fastpil
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)

T10 = np.radians(10.0)
SETS = {
    'rabbit': M.RABBIT,
    'siegel': M.SIEGEL,
    'dendrite': (0.0, 1.0, 0.0),
    'tilt': (-0.12, 0.75 * np.cos(T10), 0.75 * np.sin(T10)),      # c = -0.12 + 0.75i turned 10 degrees out of the flat plane
    'basilica': (-1.0, 0.0, 0.0),
    'sanmarco': (-0.75, 0.0, 0.0),
}
SETNAME = {'rabbit': 'rabbit', 'siegel': 'Siegel disc', 'dendrite': 'dendrite, c = i', 'tilt': 'c = -0.12 + 0.75i, turned 10 degrees out of the flat picture',
           'basilica': 'c = -1', 'sanmarco': 'c = -0.75'}
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'side': (1.0, 0.35, 0.25)}


def pillow_rule(key, name, label):
    lay = fastpil.get_lay(key)

    def F(x, y, z):
        sh = np.shape(x)
        X, Y, Z = fastpil.F(np.ravel(x).astype(float).copy(), np.ravel(y).astype(float).copy(), np.ravel(z).astype(float).copy(), lay)
        return X.reshape(sh), Y.reshape(sh), Z.reshape(sh)
    return M.fixed(F, name, label)


_ALONG = M.bench('along'); _ONE = M.bench('oneplane')


def along_n(N):
    """The first N squarings of an orbit by 'along', every later one by the one-plane rule. N = 0: one plane. N >= steps: along."""
    fa, fo = _ALONG.step, _ONE.step

    def step(x, y, z, st, k, cx, cy, cz):
        return fa(x, y, z, st, k, cx, cy, cz) if k < N else fo(x, y, z, st, k, cx, cy, cz)
    return M.Rule('along%d' % N, 'along for the first %d steps, then one plane' % N, step, init=lambda n: ())


def _wrap(r, name, plain):
    q = M.Rule(name, r.label, r.step, r.init); q.plain = plain; return q


# key -> (maker, plain label for a picture)
RULES = {
    'oneplane':  (lambda: M.bench('oneplane'), 'One plane'),
    'twoplane':  (lambda: M.bench('twoplane'), 'Two planes'),
    'along':     (lambda: M.bench('along'), 'Along'),
    'alongonce': (lambda: J.get('alongmem.c_wake1'), 'Along once, then one plane'),
    'pulled':    (lambda: J.get('sheet.evc005e70k16'), 'Pulled plane'),
    'pillow':    (lambda: pillow_rule(fastpil.REF, 'pillow', 'square pillow, reference layout E(1, 2, 0.5)'), 'Square pillow'),
    'pillowJ':   (lambda: pillow_rule(('J', 1.3, 2), 'pillowJ', 'square pillow, Joukowski layout, height 1.3'), 'Square pillow, second layout'),
    'pillowJ1':  (lambda: pillow_rule(('J', 1.0, 2), 'pillowJ1', 'square pillow, Joukowski layout, height 1.0'), 'Square pillow, second layout (square)'),
    'mandelbulb': (lambda: M.bench('mandelbulb'), 'Mandelbulb, power 2'),
    'b_pcd':     (lambda: M.bench('b_pcd'), 'One plane with the top and bottom sent back in'),
    'conep':     (lambda: CONE.RULES['conep'](), 'Rolled-up copy, opening to the right'),
    'conem':     (lambda: CONE.RULES['conem'](), 'Rolled-up copy, opening to the left'),
}
ORDER = ['oneplane', 'twoplane', 'along', 'alongonce', 'pulled', 'pillow', 'pillowJ', 'mandelbulb', 'b_pcd', 'conep', 'conem']
TRIES = {}          # filled by tries.py (the attempts to do better inside each door)
_made = {}


def get(key):
    if key not in _made:
        if key in RULES:
            r = RULES[key][0](); r.plain = RULES[key][1]
        elif key.startswith('along') and key[5:].isdigit():
            r = along_n(int(key[5:])); r.plain = r.label
        else:
            if not TRIES:
                import tries                                   # registers its rules in TRIES
                TRIES.update(tries.D.TRIES)                    # (when this file runs as a script, 'doors' is a second copy)
            r = TRIES[key][0](); r.plain = TRIES[key][1]
        _made[key] = r
    return _made[key]


# ---------------------------------------------------------------- cached blocks and depth maps
VH = 0.02; VN = (170, 140, 140)                                  # block size and count: x in -1.7..1.7, y and z in -1.4..1.4


def vox_axes():
    return tuple((np.arange(n) + 0.5) * VH - n * VH / 2 for n in VN)


def vox(key, sname, steps=80, quiet=False):
    """How long (up to `steps`) the orbit of each block centre stays. The plane z = 0 lies BETWEEN two layers of blocks."""
    path = os.path.join(CACHE, 'vox-%s-%s-%d.npz' % (key, sname, steps))
    if os.path.exists(path):
        return np.load(path)['n']
    r = get(key); c = SETS[sname]; xs, ys, zs = vox_axes(); out = np.zeros(VN, np.uint8); t0 = time.time()
    for i0 in range(0, VN[0], 34):
        X, Y, Z = np.meshgrid(xs[i0:i0 + 34], ys, zs, indexing='ij')
        out[i0:i0 + 34] = M.stay(r, X, Y, Z, c[0], c[1], c[2], steps)
    np.savez_compressed(path, n=out)
    if not quiet:
        print('vox %-10s %-9s inside at 30: %.4f  at %d: %.4f   %.0f s' % (key, sname, (out >= 30).mean() * 3.4 * 2.8 * 2.8, steps, (out >= steps).mean() * 3.4 * 2.8 * 2.8, time.time() - t0)); sys.stdout.flush()
    return out


DW, DH, DN, DSTEPS, DHALF = 280, 210, 180, 40, 1.6


def dep(key, sname, eye='a', quiet=False, centre=None, half_w=None, tag=''):
    path = os.path.join(CACHE, 'dep-%s-%s-%s%s.npz' % (key, sname, eye, tag))
    if os.path.exists(path):
        d = np.load(path); return d['depth'], float(d['px'])
    r = get(key); c = SETS[sname]; t0 = time.time()
    depth, px = M.solid(r, c, DW, DH, DN, DSTEPS, centre=centre, half_w=half_w or DHALF, cam=EYES[eye])
    np.savez_compressed(path, depth=depth, px=px)
    if not quiet:
        print('dep %-10s %-9s eye %-4s %.0f s' % (key, sname, eye, time.time() - t0)); sys.stdout.flush()
    return depth, px


def speed():
    rng = np.random.default_rng(2); n = 200000
    p = rng.uniform(-1.5, 1.5, size=(3, n))
    edge = np.array([[0, 0, 0], [0, 0, 1], [0, 0, -1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [1e-9, 0, 1], [0, 1e-9, -1], [1e-200, 0, 0], [0, 0, 1e-200],
                     [0.3, 0.3, 0], [0.3, 0, 0.3], [0, 0.3, 0.3], [0.3, 0.3, 1e-12], [-0.5, 0, 1e-9], [0.5, 0, 0.5], [-0.5, 0, 0.5], [0.5, 0, -0.5]], float).T
    keys = list(RULES) + (sys.argv[2].split(',') if len(sys.argv) > 2 else [])
    for key in keys:
        r = get(key); t0 = time.time()
        X, Y, Z, st = r.step(p[0].copy(), p[1].copy(), p[2].copy(), tuple(r.init(n)), 0, np.full(n, -0.12), np.full(n, 0.74), np.zeros(n))
        dt = time.time() - t0
        bad = int((~np.isfinite(X + Y + Z)).sum()); ln = float(np.nanmax(np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (p * p).sum(0))))
        m = edge.shape[1]
        with np.errstate(all='ignore'):
            EX, EY, EZ, _ = r.step(edge[0].copy(), edge[1].copy(), edge[2].copy(), tuple(r.init(m)), 0, np.full(m, -0.12), np.full(m, 0.74), np.zeros(m))
        eb = np.nonzero(~np.isfinite(EX + EY + EZ))[0]
        print('%-10s %.2f s per 200,000 points | not finite: %d of %d random, %d of %d special points %s | length squared to %.1e'
              % (key, dt, bad, n, eb.size, m, [tuple(edge[:, i]) for i in eb][:4], ln)); sys.stdout.flush()


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'time'
    if a == 'time':
        speed()
    else:
        keys = ORDER if sys.argv[2] == 'all' else sys.argv[2].split(',')
        sets = ['rabbit', 'siegel', 'dendrite', 'tilt'] if sys.argv[3] == 'all' else sys.argv[3].split(',')
        t0 = time.time()
        for k in keys:
            for s in sets:
                if a == 'vox':
                    vox(k, s)
                else:
                    dep(k, s, sys.argv[4] if len(sys.argv) > 4 else 'a')
        print('done %.0f s' % (time.time() - t0))
