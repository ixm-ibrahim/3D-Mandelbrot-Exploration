"""Question 1: exact cuts (z = 0 against the flat set of z^n + c, y = 0, x = const), power 4 at a second c,
and the other layout (pillow_ref through the study's fastpil) for the side-by-side of question 4.
python q1_cuts.py [procs]"""
import os, sys, time, json, numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sf
from q1_solids import CASES, S2

NP = 601
ITERS = 60


def _pts(kind, n, c, P, iters):
    x, y, z = P[:, 0].copy(), P[:, 1].copy(), P[:, 2].copy()
    if kind == 'j':
        return sf.orbit(x, y, z, c[0], c[1], c[2], n, iters)
    return sf.orbit(x, y, z, x.copy(), y.copy(), z.copy(), n, iters)


def plane(pool, kind, n, c, origin, e1, e2, half, N=NP, iters=ITERS):
    a = np.linspace(-half, half, N)
    A, B = np.meshgrid(a, a, indexing='ij')
    P = np.array(origin, float)[None, :] + A.ravel()[:, None] * np.array(e1, float)[None, :] + B.ravel()[:, None] * np.array(e2, float)[None, :]
    res = pool.starmap(_pts, [(kind, n, c, P[i], iters) for i in np.array_split(np.arange(P.shape[0]), 24)])
    return np.concatenate([r[0] for r in res]).reshape(N, N), np.concatenate([r[1] for r in res]).reshape(N, N)


def flat(kind, n, c, origin, half, N=NP, iters=ITERS, R=None):
    """The flat set of z^n + c on the same grid, same escape radius and step count."""
    R = R or sf.resc(n)
    a = np.linspace(-half, half, N)
    A, B = np.meshgrid(a + origin[0], a + origin[1], indexing='ij')
    z = A + 1j * B
    cc = z.copy() if kind == 'm' else complex(c[0], c[1])
    ins = np.ones(z.shape, bool)
    with np.errstate(over='ignore', invalid='ignore'):
        for k in range(iters + 1):
            ins &= np.abs(z) <= R
            z = np.where(ins, z ** n + cc, z)
    return ins


if __name__ == '__main__':
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    D = os.path.join(HERE, 'data'); out = {}
    with Pool(procs) as pool:
        for name, kind, n, c, cen, L in CASES:
            t0 = time.time()
            o = (cen[0], cen[1], 0.0)
            iz, dz = plane(pool, kind, n, c, o, (1, 0, 0), (0, 1, 0), L)
            fl = flat(kind, n, c, o, L)
            iy, dy = plane(pool, kind, n, c, (cen[0], 0.0, cen[2]), (1, 0, 0), (0, 0, 1), L)
            ix, dx = plane(pool, kind, n, c, (0.0, cen[1], cen[2]), (0, 1, 0), (0, 0, 1), L)
            np.savez_compressed(os.path.join(D, 'cuts-%s.npz' % name), iz=iz, dz=dz, iy=iy, dy=dy, ix=ix, dx=dx, flat=fl, cen=np.array(cen, float), L=L)
            out[name] = dict(z0_pixels_inside=int(iz.sum()), flat_pixels_inside=int(fl.sum()), pixels_that_differ=int((iz != fl).sum()),
                             y0_area=float(iy.sum() * (2 * L / (NP - 1)) ** 2), x0_area=float(ix.sum() * (2 * L / (NP - 1)) ** 2), z0_area=float(iz.sum() * (2 * L / (NP - 1)) ** 2))
            print('%s power %d: cut z = 0 against the flat set on %d x %d points: %d inside, flat %d, differ %d; areas z0 %.3f y0 %.3f x0 %.3f; %.0f s' % (
                name, n, NP, NP, iz.sum(), fl.sum(), (iz != fl).sum(), out[name]['z0_area'], out[name]['y0_area'], out[name]['x0_area'], time.time() - t0), flush=True)
        # power 4 at the other centre of a period-2 body
        t0 = time.time()
        c4 = (0.5, float(np.sqrt(0.75)), 0.0)
        axes = sf.cube_axes((0, 0, 0.45), 1.75, 193)
        ins, dth = sf.grid('j', 4, c4, axes, 30, pool)
        np.savez_compressed(os.path.join(D, 'q1-j4b-193.npz'), inside=ins, death=dth, cen=np.array((0, 0, 0.45)), L=1.75, n=4)
        print('j4b (power 4, c = (0.5, 0.866, 0)) N=193: volume %.4f, %.0f s' % (ins.sum() * (3.5 / 192) ** 3, time.time() - t0), flush=True)
        # question 4: the other layout, same c, power 2
        for nm, c in (('bas', (-1.0, 0.0, 0.0)), ('rab', (-0.12, 0.74, 0.0))):
            t0 = time.time()
            axes = sf.cube_axes((0, 0, 0), 1.75, 193)
            ins, dth = sf.grid('j', 2, c, axes, 30, pool, rule='pillow')
            np.savez_compressed(os.path.join(D, 'q4-pillow-%s-193.npz' % nm), inside=ins, death=dth, cen=np.zeros(3), L=1.75, n=2)
            zz = axes[2][np.where(ins.any(axis=(0, 1)))[0]]
            print('other layout %s N=193: volume %.4f, z %.3f to %.3f, %.0f s' % (nm, ins.sum() * (3.5 / 192) ** 3, zz.min(), zz.max(), time.time() - t0), flush=True)
        t0 = time.time()
        axes = sf.cube_axes((-0.45, 0, 0), 1.75, 193)
        ins, dth = sf.grid('m', 2, None, axes, 30, pool, rule='pillow')
        np.savez_compressed(os.path.join(D, 'q4-pillow-m2-193.npz'), inside=ins, death=dth, cen=np.array((-0.45, 0, 0)), L=1.75, n=2)
        print('other layout Mandelbrot solid N=193: volume %.4f, %.0f s' % (ins.sum() * (3.5 / 192) ** 3, time.time() - t0), flush=True)
    json.dump(out, open(os.path.join(HERE, 'q1-cuts.json'), 'w'), indent=1)
