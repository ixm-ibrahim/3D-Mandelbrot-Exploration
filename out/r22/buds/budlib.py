"""Round 22, section 'buds': shared tools. The orbits are the library's (out/r21/lib/mem.py); this file only
adds, for the five rules, WHICH PAGE each squaring used and how far the point was from that page.

    import budlib as B
    B.RULES['along'] ...           'lathe', 'oneplane', 'along', 'once' (alongmem.c_wake1), 'pulled' (sheet.evc005e70k16)
    t = B.trace('along', x, y, z, c, nsteps)
        t['pos'][k]   (x, y, z) after k steps (k = 0 .. nsteps); escaped orbits are nan from then on
        t['page'][k]  turn (radians, from the flat page) of the page that squaring number k used
        t['off'][k]   how far the point was from that page before squaring number k (a length)
        t['offang'][k] the same as a turn round the x-axis, folded into -90..90 degrees (radians)
    B.inside(name, x, y, z, c, steps)
    B.flat_centres(c)   centres of the buds of the flat picture, by the number of steps they need to reach the x-axis
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

P = M.S.oneplane
RULES = {'lathe': M.bench('lathe'), 'oneplane': M.bench('oneplane'), 'along': M.bench('along'),
         'once': J.get('alongmem.c_wake1'), 'pulled': J.get('sheet.evc005e70k16')}
PLAIN = {'lathe': 'Quaternion square (Lathe)', 'oneplane': 'Sphere inversions, one plane', 'along': 'Turning plane, along',
         'once': 'Along once, then one plane', 'pulled': 'Pulled plane'}
BASILICA = (-1.0, 0.0, 0.0); SANMARCO = (-0.75, 0.0, 0.0)


def fold(a):
    """A turn folded into -90..90 degrees (a page has no front and back)."""
    return (a + np.pi / 2) % np.pi - np.pi / 2


def page_used(name, y, z, st_after, k):
    """Turn (radians) of the page the point (.., y, z) was squared about, squaring number k."""
    phi = np.arctan2(z, y)
    if name == 'lathe':
        return phi
    if name == 'oneplane':
        return 0 * phi
    if name == 'along':
        return phi - np.sin(4 * phi) / 4
    if name == 'once':
        return phi - np.sin(4 * phi) / 4 if k == 0 else 0 * phi
    if name == 'pulled':
        return 0.5 * np.arctan2(st_after[1], st_after[0])
    raise KeyError(name)


def sq_at(x, y, z, th):
    c, s = np.cos(th), np.sin(th)
    X, Y, Z = P(x, c * y + s * z, c * z - s * y)
    return X, c * Y - s * Z, s * Y + c * Z


def trace(name, x, y, z, c, nsteps, rule=None, page_fn=None, r2=36.0):
    r = rule or RULES[name]
    x, y, z = (np.array(np.broadcast_to(np.asarray(t, float), np.shape(x)), float).ravel() for t in (x, y, z))
    n = x.size; cx, cy, cz = (np.full(n, float(t)) for t in c)
    st = tuple(r.init(n)); pos = [(x.copy(), y.copy(), z.copy())]; page = []; off = []; offang = []
    alive = np.ones(n, bool)
    with np.errstate(all='ignore'):
        for k in range(nsteps):
            xs, ys, zs = (np.where(alive, t, 0.5) for t in (x, y, z))          # dead orbits are parked at a harmless point
            out = r.step(xs, ys, zs, st, k, cx, cy, cz); st2 = tuple(out[3])
            pg = page_fn(ys, zs, st2, k) if page_fn else page_used(name, ys, zs, st2, k)
            phi = np.arctan2(zs, ys); rho = np.hypot(ys, zs); da = fold(phi - pg)
            page.append(np.where(alive, pg, np.nan)); offang.append(np.where(alive, da, np.nan)); off.append(np.where(alive, rho * np.abs(np.sin(da)), np.nan))
            x, y, z = out[0] + cx, out[1] + cy, out[2] + cz; st = st2
            alive = alive & (x * x + y * y + z * z < r2)
            x, y, z = (np.where(alive, t, np.nan) for t in (x, y, z))
            pos.append((x.copy(), y.copy(), z.copy()))
    return {'pos': pos, 'page': page, 'off': off, 'offang': offang}


def inside(name, x, y, z, c, steps=80, rule=None):
    return M.stay(rule or RULES[name], x, y, z, c[0], c[1], c[2], steps) >= steps


def check_pages(n=20000, seed=1):
    """Does 'the one-plane square about the page I report' reproduce the library's step? Largest difference per rule."""
    rng = np.random.default_rng(seed); out = {}
    for name, r in RULES.items():
        worst = 0.0
        for c in (BASILICA, M.RABBIT):
            v = rng.uniform(-1.5, 1.5, size=(n, 3)); x, y, z = v[:, 0], v[:, 1], v[:, 2]
            cx, cy, cz = (np.full(n, float(t)) for t in c); st = tuple(r.init(n))
            for k in range(3):
                o = r.step(x, y, z, st, k, cx, cy, cz); st2 = tuple(o[3])
                X, Y, Z = sq_at(x, y, z, page_used(name, y, z, st2, k))
                worst = max(worst, float(np.max(np.abs(X - o[0]) + np.abs(Y - o[1]) + np.abs(Z - o[2]))))
                x, y, z = np.clip(o[0] + cx, -2, 2), np.clip(o[1] + cy, -2, 2), np.clip(o[2] + cz, -2, 2); st = st2
        out[name] = worst
    return out


def flat_centres(c):
    """Centres of buds of the flat picture for a c on the x-axis with a two-cycle (basilica) or its edge (San Marco).
    g1 = the bud on top of the middle body (1 step to the x-axis); g2 = a side bud of the left body (2 steps);
    g3 = a slanted bud of the middle body (3 steps); g4 = a small bud of the right body (4 steps).
    Also the centres on the x-axis: 'small' (the small body left of the left body) and 'right'."""
    c = complex(c)
    right = np.sqrt(-c + 0j)                    # maps to 0
    small = -np.sqrt(right - c)                 # maps to 'right'
    g1 = np.sqrt(small - c + 0j)                # i * something: on top of the middle body
    if g1.imag < 0: g1 = -g1
    g2 = -np.sqrt(g1 - c)                       # on the left body, below the axis
    g2 = complex(g2.real, abs(g2.imag))
    g3 = np.sqrt(g2 - c); g3 = complex(abs(g3.real), abs(g3.imag))
    g4 = np.sqrt(g3 - c); g4 = complex(abs(g4.real), abs(g4.imag))
    return {'right': right.real, 'small': small.real, 'g1': g1, 'g2': g2, 'g3': g3, 'g4': g4}


def arcs(ins):
    """Runs of True on a closed ring: list of (centre index (float), length). A full ring gives [(0, n)]."""
    n = ins.size
    if ins.all():
        return [(0.0, n)]
    if not ins.any():
        return []
    s = int(np.argmin(ins)); r = np.roll(ins, -s); out = []; i = 0
    while i < n:
        if r[i]:
            j = i
            while j < n and r[j]:
                j += 1
            out.append((((i + j - 1) / 2.0 + s) % n, j - i)); i = j
        else:
            i += 1
    return out


if __name__ == '__main__':
    print('page check (largest difference between the library step and P about the reported page):')
    for k, v in check_pages().items():
        print('  %-9s %.2e' % (k, v))
    for c in (-1.0, -0.75):
        print('flat centres, c = %g:' % c, {k: (np.round(v, 4)) for k, v in flat_centres(c).items()})
