"""Round 22, section 'mandel': helpers to follow the orbit of c (the Mandelbrot solid).

    import sys; sys.path.insert(0, 'out/r22/mandel'); import mlib as L
    L.RULES['along'], ['oneplane'], ['wake'] (alongmem.c_wake1), ['evc'] (sheet.evc005e70k16), ['lathe']
    L.trace(key, cx, cy, cz, steps) -> pts (steps + 1, n, 3), page (steps, n), n_stay (n)

The rules are the library's own (out/r21/lib/mem.py and out/r21/judge/myrules.py). trace() repeats the loop of
M.stay with the same rule.step, keeps every point, and also says which page (plane through the x-axis) each
squaring was taken about. check() proves that the page it reports reproduces rule.step.
The orbit of c is started at the point c with k = 0, as M.mandel does (the squaring of 0 counts for nothing).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

RULES = {'along': M.bench('along'), 'oneplane': M.bench('oneplane'), 'wake': J.get('alongmem.c_wake1'),
         'evc': J.get('sheet.evc005e70k16'), 'lathe': M.bench('lathe')}
LAB = {'along': 'Turning plane, along', 'oneplane': 'Sphere inversions, one plane', 'wake': 'Along once, then one plane',
       'evc': 'Pulled plane', 'lathe': 'Quaternion square (Lathe)'}
P = M.S.oneplane
DEG = 180 / np.pi


def psi_along(y, z):
    phi = np.arctan2(z, y); return phi - 0.25 * np.sin(4 * phi)


def about(x, y, z, th):
    """The one-plane square about the page through the x-axis at the turn th (radians)."""
    c, s = np.cos(th), np.sin(th)
    X, Y, Z = P(x, c * y + s * z, c * z - s * y)
    return X, c * Y - s * Z, s * Y + c * Z


def page_used(key, x, y, z, k, st_new):
    """The turn (radians) of the page the squaring number k of the point (x, y, z) was taken about."""
    if key == 'oneplane':
        return np.zeros_like(x)
    if key == 'along':
        return psi_along(y, z)
    if key == 'wake':
        return psi_along(y, z) if k == 0 else np.zeros_like(x)
    if key == 'evc':
        return 0.5 * np.arctan2(st_new[1], st_new[0])
    if key == 'lathe':
        return np.arctan2(z, y)
    raise KeyError(key)


def fold(a):
    """A difference of two page turns, brought into -90..90 degrees (a page has no front and back). Radians in and out."""
    return (a + np.pi / 2) % np.pi - np.pi / 2


def trace(key, cx, cy, cz, steps, start=None, r2=36.0):
    """Orbit of c (or of the start points 'start' = (x, y, z) with the constant c). Escaped orbits are nan from then on."""
    rule = RULES[key]
    cx, cy, cz = (np.atleast_1d(np.asarray(t, float)).copy() for t in (cx, cy, cz)); n = cx.size
    x, y, z = (cx.copy(), cy.copy(), cz.copy()) if start is None else (np.broadcast_to(np.asarray(t, float), (n,)).copy() for t in start)
    st = tuple(rule.init(n)); pts = np.full((steps + 1, n, 3), np.nan); page = np.full((steps, n), np.nan)
    pts[0] = np.stack([x, y, z], 1); alive = np.ones(n, bool); nstay = np.zeros(n, np.int32)
    for k in range(steps):
        with np.errstate(all='ignore'):
            out = rule.step(x, y, z, st, k, cx, cy, cz)
        X, Y, Z, st = out[0], out[1], out[2], tuple(out[3])
        pg = page_used(key, x, y, z, k, st)
        x, y, z = X + cx, Y + cy, Z + cz
        alive &= (x * x + y * y + z * z) < r2
        x, y, z = (np.where(alive, t, np.nan) for t in (x, y, z))
        page[k] = np.where(np.isfinite(pts[k, :, 0]), pg, np.nan); pts[k + 1] = np.stack([x, y, z], 1); nstay += alive
    return pts, page, nstay


def check(n=4000, seed=1):
    """The page that page_used reports reproduces rule.step (largest difference), for random points and constants."""
    rng = np.random.default_rng(seed); v = rng.uniform(-1.5, 1.5, (n, 3)); c = rng.uniform(-1, 1, (n, 3)); out = {}
    for key in ('along', 'oneplane', 'wake', 'evc'):
        rule = RULES[key]; worst = 0.0
        for k in (0, 1, 2):
            st = tuple(rule.init(n))
            if key == 'evc' and k:
                st = (rng.uniform(-1, 1, n), rng.uniform(-1, 1, n))
            X, Y, Z, st2 = rule.step(v[:, 0], v[:, 1], v[:, 2], st, k, c[:, 0], c[:, 1], c[:, 2])
            A = about(v[:, 0], v[:, 1], v[:, 2], page_used(key, v[:, 0], v[:, 1], v[:, 2], k, tuple(st2)))
            worst = max(worst, float(np.max(np.abs(np.stack(A) - np.stack([X, Y, Z])))))
        out[key] = worst
    return out


def fate(pts, nstay, steps, pmax=64, tol=1e-7, loose=1e-3):
    """Where each orbit ends up. Returns period (0 = no cycle found; -1 = it left), kind text per orbit:
    'out', 'cycle' (settled on a cycle of that period), 'near' (within 1e-3 of repeating), 'cloud' (bounded, never repeats)."""
    n = pts.shape[1]; per = np.zeros(n, np.int32); kind = np.empty(n, object)
    last = pts[-(2 * pmax + 1):]                                  # (2 pmax + 1, n, 3)
    for i in range(n):
        if nstay[i] < steps:
            per[i] = -1; kind[i] = 'out'; continue
        a = last[:, i, :]; kind[i] = 'cloud'
        for tl, nm in ((tol, 'cycle'), (loose, 'near')):
            for p in range(1, pmax + 1):
                if np.max(np.abs(a[p:] - a[:-p])) < tl:
                    per[i] = p; kind[i] = nm; break
            if per[i]:
                break
    return per, kind


def arcs(inside):
    """Separate inside stretches on a closed circle of places: list of (centre index, width in places)."""
    n = inside.size
    if inside.all():
        return [(0.0, n)]
    if not inside.any():
        return []
    s = int(np.argmin(inside)); a = np.roll(inside, -s); out = []; i = 0
    while i < n:
        if a[i]:
            j = i
            while j < n and a[j]:
                j += 1
            out.append((((i + j - 1) / 2.0 + s) % n, j - i)); i = j
        else:
            i += 1
    return out


def ring(x0, rho, n):
    phi = np.arange(n) * 2 * np.pi / n
    return np.full(n, float(x0)), rho * np.cos(phi), rho * np.sin(phi), phi


if __name__ == '__main__':
    print('page_used against rule.step, largest difference:', check())
    for key in RULES:
        x, y, z, phi = ring(-0.1226, 0.7449, 360)
        _, _, ns = trace(key, x, y, z, 100)
        ref = M.mandel(RULES[key], x, y, z, 100)
        print('%-9s trace against M.mandel: %d of 360 counts differ' % (key, int((ns != ref).sum())))
