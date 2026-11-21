"""Question 1, Mandelbrot solids: which part of the solid is the main body (the orbit settles on one point) and which
parts are period-2 bodies (the orbit settles on two points taken in turn), and how many of those there are,
in the plane and off it. Voxels N per side; 250 warm-up steps, then the smallest p <= 8 with |P(k+p) - P(k)| < 1e-4.
python q1_periods.py [N] [procs]"""
import os, sys, time, json, numpy as np
from multiprocessing import Pool
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sf
from q1_solids import CASES


def chunk(args):
    n, pts = args
    cx, cy, cz = pts[:, 0].copy(), pts[:, 1].copy(), pts[:, 2].copy()
    x, y, z = cx.copy(), cy.copy(), cz.copy()
    R = sf.resc(n)
    alive = np.arange(pts.shape[0])
    for k in range(250):
        fx, fy, fz, rho = sf.F(x, y, z, n, want_rho=True)
        keep = rho <= R
        alive = alive[keep]
        x, y, z = fx[keep] + cx[alive], fy[keep] + cy[alive], fz[keep] + cz[alive]
        if alive.size == 0: break
    per = np.full(pts.shape[0], -1, np.int8)             # -1 = outside
    if alive.size:
        x0, y0, z0 = x.copy(), y.copy(), z.copy()
        p_found = np.zeros(alive.size, np.int8)          # 0 = inside, no period up to 8 found
        ok = np.ones(alive.size, bool)
        for p in range(1, 9):
            fx, fy, fz, rho = sf.F(x, y, z, n, want_rho=True)
            ok &= rho <= R
            x, y, z = fx + cx[alive], fy + cy[alive], fz + cz[alive]
            d = np.sqrt((x - x0) ** 2 + (y - y0) ** 2 + (z - z0) ** 2)
            hit = (p_found == 0) & (d < 1e-4) & ok
            p_found[hit] = p
        p_found[~ok] = -1
        per[alive] = p_found
    return per


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 129
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    ALL = np.ones((3, 3, 3)); out = {}
    with Pool(procs) as pool:
        for name, kind, n, c, cen, L in CASES:
            if kind != 'm': continue
            t0 = time.time()
            ax, ay, az = sf.cube_axes(cen, L, N)
            # use the fine solid's box; only points inside a coarse pre-test are worth the long run
            X, Y, Z = np.meshgrid(ax, ay, az, indexing='ij')
            P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
            pre, _ = (np.concatenate(r) for r in zip(*pool.starmap(sf.orbit, [(P[i, 0], P[i, 1], P[i, 2], P[i, 0].copy(), P[i, 1].copy(), P[i, 2].copy(), n, 20) for i in np.array_split(np.arange(P.shape[0]), 64)])))
            idx = np.where(pre)[0]
            res = pool.map(chunk, [(n, P[i]) for i in np.array_split(idx, 64)])
            per = np.full(P.shape[0], -1, np.int8); per[idx] = np.concatenate(res)
            per = per.reshape(N, N, N)
            np.save(os.path.join(HERE, 'data', 'periods-%s-%d.npy' % (name, N)), per)
            h = ax[1] - ax[0]; vox = h ** 3
            r = dict(power=n, voxel=float(h), inside=float((per >= 0).sum() * vox))
            line = '%s power %d N=%d: inside %.3f; volume by period: ' % (name, n, N, r['inside'])
            for p in range(0, 9):
                r['period_%d_volume' % p] = float((per == p).sum() * vox)
                line += ('none found' if p == 0 else str(p)) + ' %.3f, ' % r['period_%d_volume' % p]
            print(line)
            for p in (1, 2, 3):
                lab, k = ndimage.label(per == p, structure=ALL)
                if k == 0: continue
                cnt = np.bincount(lab.ravel())[1:]
                keep = np.where(cnt >= 12)[0]
                com = ndimage.center_of_mass(per == p, lab, keep + 1)
                rows = sorted([(float(cnt[j] * vox), round(float(ax[0] + cm[0] * h), 2), round(float(ay[0] + cm[1] * h), 2), round(float(az[0] + cm[2] * h), 2)) for j, cm in zip(keep, com)], reverse=True)
                # does the body cross the plane z = 0?
                objs = ndimage.find_objects(lab)
                crosses = []
                for j in keep:
                    zs = az[objs[j][2]]
                    crosses.append(bool(zs.min() <= h and zs.max() >= -h))
                order = np.argsort([-cnt[j] for j in keep])
                rows2 = [(float(cnt[keep[o]] * vox),) + tuple(round(float(v), 2) for v in (ax[0] + com[o][0] * h, ay[0] + com[o][1] * h, az[0] + com[o][2] * h)) + (crosses[o],) for o in order]
                r['period_%d_bodies' % p] = rows2[:30]
                print('   period %d: %d bodies of 12 voxels or more; %d of them reach the plane z = 0, %d do not. Largest (volume, x, y, z, reaches the plane): %s'
                      % (p, len(rows2), sum(1 for q in rows2 if q[4]), sum(1 for q in rows2 if not q[4]), rows2[:10]))
            out[name] = r
            print('   %.0f s' % (time.time() - t0), flush=True)
    json.dump(out, open(os.path.join(HERE, 'q1-periods-%d.json' % N), 'w'), indent=1)
