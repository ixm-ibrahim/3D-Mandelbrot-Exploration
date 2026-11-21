"""Parallel escape-time grids for the square-pillow rule (and two comparison rules). Stand-alone numpy."""
import os, sys, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import fastpil as Fp

PROCS = 12
CHUNK = 60000


def step(x, y, z, key):
    if key[0] in ('E', 'J'):
        return Fp.F(x, y, z, Fp.get_lay(key))
    if key[0] == 'merc':                      # Sphere inversions, one plane (turns.E1)
        r2 = x * x + y * y + z * z; r = np.sqrt(r2)
        f = r2 / np.maximum(r2 + z * z, 1e-300)
        return f * (x * x - y * y), f * (2 * x * y), f * (2 * z * r)
    if key[0] == 'bulb':                      # Mandelbulb, power 2: longitude and latitude doubled
        r2 = x * x + y * y + z * z; r = np.sqrt(r2)
        lon = np.arctan2(y, x); lat = np.arcsin(np.clip(z / np.maximum(r, 1e-300), -1, 1))
        cl = np.cos(2 * lat)
        return r2 * cl * np.cos(2 * lon), r2 * cl * np.sin(2 * lon), r2 * np.sin(2 * lat)
    raise ValueError(key)


def esc(x, y, z, c, key, iters, mandel=False, R2=4.0, trap=False):
    """escape step per point (uint8; 0 = still inside after `iters` steps)."""
    M = x.size
    death = np.zeros(M, np.uint8)
    for a in range(0, M, CHUNK):
        xs, ys, zs = x[a:a + CHUNK].copy(), y[a:a + CHUNK].copy(), z[a:a + CHUNK].copy()
        alive = np.arange(a, a + xs.size)
        if mandel:
            cx, cy, cz = xs.copy(), ys.copy(), zs.copy()
            keep = xs * xs + ys * ys + zs * zs <= R2
            death[alive[~keep]] = 1
            alive, xs, ys, zs, cx, cy, cz = alive[keep], xs[keep], ys[keep], zs[keep], cx[keep], cy[keep], cz[keep]
        else:
            cx, cy, cz = c
        snap = None
        for k in range(iters):
            if alive.size == 0: break
            if trap and k >= 12 and k % 12 == 0:
                # shortcut for the inside: an orbit that comes back to within 1e-6 of where it was 12 steps ago
                # has settled on a cycle (periods 1, 2, 3, 4, 6, 12) and is counted as inside without further steps
                if snap is not None:
                    go = (np.abs(xs - snap[0]) + np.abs(ys - snap[1]) + np.abs(zs - snap[2])) > 1e-6
                    if not go.all():
                        alive, xs, ys, zs = alive[go], xs[go], ys[go], zs[go]
                        if mandel: cx, cy, cz = cx[go], cy[go], cz[go]
                        if alive.size == 0: break
                snap = (xs.copy(), ys.copy(), zs.copy())
            xs, ys, zs = step(xs, ys, zs, key)
            xs = xs + cx; ys = ys + cy; zs = zs + cz
            keep = xs * xs + ys * ys + zs * zs <= R2
            if not keep.all():
                death[alive[~keep]] = min(k + 1 + (1 if mandel else 0), 254)
                alive, xs, ys, zs = alive[keep], xs[keep], ys[keep], zs[keep]
                if mandel: cx, cy, cz = cx[keep], cy[keep], cz[keep]
                if snap is not None: snap = (snap[0][keep], snap[1][keep], snap[2][keep])
    return death


def _work(a):
    key, cen, e1, e2, e3, n1, n2, n3, i0, i1, c, iters, mandel, trap = a
    i = np.arange(i0, i1) - (n1 - 1) / 2.0; j = np.arange(n2) - (n2 - 1) / 2.0; k = np.arange(n3) - (n3 - 1) / 2.0
    I, J, K = np.meshgrid(i, j, k, indexing='ij')
    I, J, K = I.ravel(), J.ravel(), K.ravel()
    x = cen[0] + I * e1[0] + J * e2[0] + K * e3[0]
    y = cen[1] + I * e1[1] + J * e2[1] + K * e3[1]
    z = cen[2] + I * e1[2] + J * e2[2] + K * e3[2]
    return esc(x, y, z, c, key, iters, mandel, trap=trap).reshape(i1 - i0, n2, n3)


def grid(pool, key, cen, e1, e2, e3, n1, n2, n3, c=(0, 0, 0), iters=40, mandel=False, cache=None, trap=False):
    if cache and os.path.exists(cache):
        return np.load(cache)
    t0 = time.time()
    per = max(1, min(n1 // (PROCS * 3) + 1, max(1, 2000000 // (n2 * n3))))
    tasks = [(tuple(key), tuple(cen), tuple(e1), tuple(e2), tuple(e3), n1, n2, n3, a, min(n1, a + per), tuple(c), iters, mandel, trap)
             for a in range(0, n1, per)]
    out = np.concatenate(pool.map(_work, tasks, chunksize=1), axis=0)
    if cache: np.save(cache, out)
    print('  grid %s %dx%dx%d iters %d: %.0f s' % (os.path.basename(cache) if cache else '', n1, n2, n3, iters, time.time() - t0), flush=True)
    return out


def box(pool, key, cen, L, N, c=(0, 0, 0), iters=40, mandel=False, cache=None, trap=False):
    """cube of half-size L, N^3 points (N odd puts the planes through the centre on the grid). death[ix, iy, iz]."""
    h = 2.0 * L / (N - 1)
    return grid(pool, key, cen, (h, 0, 0), (0, h, 0), (0, 0, h), N, N, N, c, iters, mandel, cache, trap)


def plane(pool, key, cen, u, v, Lu, Lv, Nu, Nv, c=(0, 0, 0), iters=80, mandel=False, cache=None):
    """flat cut: points cen + a u + b v, a in [-Lu, Lu], b in [-Lv, Lv]. death[iu, iv]."""
    hu, hv = 2.0 * Lu / (Nu - 1), 2.0 * Lv / (Nv - 1)
    e1 = tuple(hu * np.array(u, float)); e2 = tuple(hv * np.array(v, float))
    return grid(pool, key, cen, e1, e2, (0, 0, 0), Nu, Nv, 1, c, iters, mandel, cache)[:, :, 0]


def cut_img(death, scale=14.0):
    """death[iu, iv] -> RGB, u to the right, v up. Inside light, outside shaded by escape step."""
    d = death.astype(np.float32)
    t = np.clip(d / scale, 0, 1)
    img = np.zeros(death.shape + (3,), np.float32)
    for ch, col in enumerate((70, 110, 170)): img[:, :, ch] = 18 + (col - 18) * t
    img[death == 0] = (235, 225, 200)
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]


def make_pool():
    import multiprocessing as mp
    return mp.Pool(PROCS)
