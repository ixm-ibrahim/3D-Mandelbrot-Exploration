# Check of the pull-back machinery against the plain definition: at random points, try every order of the two
# rules to depth D by direct iteration (float64, no grid), and compare with what the grid says at the same depth.
# Run from the project root: python out/r14/turns/s04_check.py
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from turns import *


def brute(P1, P2, c, pts, depth):
    """For each point: (union, common) = some / every order of length `depth` keeps the orbit within Resc."""
    R2 = resc(c) ** 2
    n = len(pts)
    ci = np.arange(n); x, y, z = pts[:, 0].copy(), pts[:, 1].copy(), pts[:, 2].copy()
    ok0 = (x * x + y * y + z * z) <= R2
    common = ok0.copy(); has = ok0.copy()
    ci, x, y, z = ci[ok0], x[ok0], y[ok0], z[ok0]
    for d in range(depth):
        a1, b1, c1 = P1(x, y, z); a2, b2, c2 = P2(x, y, z)
        nx = np.concatenate([a1, a2]) + c[0]; ny = np.concatenate([b1, b2]) + c[1]; nz = np.concatenate([c1, c2]) + c[2]
        nc = np.concatenate([ci, ci])
        ok = (nx * nx + ny * ny + nz * nz) <= R2
        bad = np.zeros(n, bool); bad[nc[~ok]] = True; common &= ~bad
        has = np.zeros(n, bool); has[nc[ok]] = True
        ci, x, y, z = nc[ok], nx[ok], ny[ok], nz[ok]
    return has, common


if __name__ == '__main__':
    N, L, D = 193, 1.7, 9
    rng = np.random.default_rng(7)
    out = {}
    for pair in ('E', 'K'):
        P1, P2 = RULES[pair]
        for c in ((-1.0, 0.0, 0.0), (-1.0, 0.15, 0.1)):
            h = 2 * L / N
            # random voxel centres inside the ball (the grid's own sample points), plus the depth it reports
            idx = rng.integers(0, N, size=(6000, 3))
            pts = ((idx + 0.5) / N * 2 - 1) * L
            bu, bc = brute(P1, P2, c, pts, D)
            for mode, ref in (('union', bu), ('common', bc)):
                vol, death, info = julia(c, [P1, P2], mode, N=N, L=L, max_depth=D, verbose=False)
                got = vol[idx[:, 0], idx[:, 1], idx[:, 2]]
                differ = got != ref
                # is a differing voxel next to the surface of the grid's set? (then it is a resolution matter)
                from scipy import ndimage
                edge = ndimage.binary_dilation(vol, iterations=2) & ~ndimage.binary_erosion(vol, iterations=2)
                far = differ & ~edge[idx[:, 0], idx[:, 1], idx[:, 2]]
                key = f'{pair} c={c} {mode} depth {D}'
                out[key] = dict(points=len(pts), inside_by_direct=int(ref.sum()), inside_by_grid=int(got.sum()),
                                differ=int(differ.sum()), differ_further_than_2_voxels_from_surface=int(far.sum()))
                print(key, out[key], flush=True)
    json.dump(out, open(os.path.join(HERE, 'check-pullback.json'), 'w'), indent=1)
