# The Mandelbrot solids: z starts at 0, c is the picture point; every order of the two rules is tried to a
# fixed depth (z_0 = 0, z_1 = c, ..., z_depth: 2^(depth-1) orders), with early exits.
# Run from the project root: python out/r14/turns/s03_mandel.py [N] [depth] [procs]
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from turns import *

CX, HALF = -0.7, 1.4            # the cube: x in [-2.1, 0.7], y and z in [-1.4, 1.4]


def bfs(args):
    """One chunk of c points. Returns (union_in, common_in, one_in) as bool arrays.
    A point further than 2 from the origin escapes under every order (|c| <= 2 here), so 2 is an exact bail-out."""
    pair, cx, cy, cz, depth = args
    P1, P2 = RULES[pair]
    n = len(cx)
    # one rule alone (P1), for reference and as a shortcut: bounded under P1 alone => in the union
    x, y, z = cx.copy(), cy.copy(), cz.copy()
    one = np.ones(n, bool)
    for d in range(2, depth + 1):
        a, b, c_ = P1(x, y, z)
        x, y, z = a + cx, b + cy, c_ + cz
        esc = (x * x + y * y + z * z) > 4
        one &= ~esc
        x[esc] = 3; y[esc] = 0; z[esc] = 0
    # all orders
    ci = np.arange(n)
    x, y, z = cx.copy(), cy.copy(), cz.copy()
    common = (x * x + y * y + z * z) <= 4
    union_alive = common.copy()
    keep = common
    ci, x, y, z = ci[keep], x[keep], y[keep], z[keep]
    for d in range(2, depth + 1):
        if len(ci) == 0:
            break
        a1, b1, c1 = P1(x, y, z); a2, b2, c2 = P2(x, y, z)
        nx = np.concatenate([a1 + cx[ci], a2 + cx[ci]]); ny = np.concatenate([b1 + cy[ci], b2 + cy[ci]])
        nz = np.concatenate([c1 + cz[ci], c2 + cz[ci]]); nc = np.concatenate([ci, ci])
        ok = (nx * nx + ny * ny + nz * nz) <= 4
        bad = np.zeros(n, bool); bad[nc[~ok]] = True
        common &= ~bad
        has = np.zeros(n, bool); has[nc[ok]] = True
        union_alive = has
        # keep a state when its c can still matter: for the union, c not yet proven by the one-rule shortcut;
        # for the common set, c not yet dead. A c that is dead for the common set and proven for the union is dropped.
        need = (~one) | common
        k = ok & need[nc]
        ci, x, y, z = nc[k], nx[k], ny[k], nz[k]
    union = union_alive | one
    return union, common, one


def mandel(pair, N, depth, procs):
    m = N // 2
    ax = ((np.arange(N) + 0.5) / N * 2 - 1) * HALF
    # wedge y >= 0, z >= 0, z <= y; the rest follows by the mirrors y -> -y, z -> -z and the swap of y and z
    IX, IY, IZ = np.meshgrid(np.arange(N), np.arange(m, N), np.arange(m, N), indexing='ij')
    sel = (IZ <= IY)
    ix, iy, iz = IX[sel], IY[sel], IZ[sel]
    cx, cy, cz = ax[ix] + CX, ax[iy], ax[iz]
    inb = (cx * cx + cy * cy + cz * cz) <= 4
    ix, iy, iz, cx, cy, cz = ix[inb], iy[inb], iz[inb], cx[inb], cy[inb], cz[inb]
    chunk = 3000
    jobs = [(pair, cx[i:i + chunk], cy[i:i + chunk], cz[i:i + chunk], depth) for i in range(0, len(cx), chunk)]
    import multiprocessing as mp
    with mp.Pool(procs) as pool:
        parts = pool.map(bfs, jobs, chunksize=1)
    out = {}
    for j, key in enumerate(('union', 'common', 'one')):
        flag = np.concatenate([p[j] for p in parts])
        v = np.zeros((N, N, N), bool)
        v[ix, iy, iz] = flag
        v |= np.swapaxes(v, 1, 2) if key != 'one' else False       # swap y and z (the one-rule solid has no such symmetry)
        if key == 'one':
            # the one-rule solid: computed on the wedge only; fill the mirror images in y and z, and compute the
            # other wedge (z > y) directly by symmetry of the rule in y and z separately is not available, so
            # leave it to the caller: see one_full()
            pass
        v |= v[:, ::-1, :]
        v |= v[:, :, ::-1]
        out[key] = v
    return out


def one_full(P, N, depth):
    """The Mandelbrot solid of one rule alone, on the whole cube (uses the mirrors y -> -y and z -> -z)."""
    m = N // 2
    ax = ((np.arange(N) + 0.5) / N * 2 - 1) * HALF
    IX, IY, IZ = np.meshgrid(np.arange(N), np.arange(m, N), np.arange(m, N), indexing='ij')
    cx, cy, cz = ax[IX.ravel()] + CX, ax[IY.ravel()], ax[IZ.ravel()]
    x, y, z = cx.copy(), cy.copy(), cz.copy()
    ins = (x * x + y * y + z * z) <= 4
    for d in range(2, depth + 1):
        a, b, c_ = P(x, y, z)
        x, y, z = a + cx, b + cy, c_ + cz
        esc = (x * x + y * y + z * z) > 4
        ins &= ~esc
        x[esc] = 3; y[esc] = 0; z[esc] = 0
    v = np.zeros((N, N, N), bool)
    v[IX.ravel(), IY.ravel(), IZ.ravel()] = ins
    v |= v[:, ::-1, :]; v |= v[:, :, ::-1]
    return v


def flat_mandel(N, depth):
    ax = ((np.arange(N) + 0.5) / N * 2 - 1) * HALF
    X, Y = np.meshgrid(ax + CX, ax, indexing='ij')
    c = X + 1j * Y
    z = c.copy(); ins = np.abs(z) <= 2
    for d in range(2, depth + 1):
        z = np.where(ins, z * z + c, z)
        ins &= np.abs(z) <= 2
    return ins


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 97
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    OUT = os.path.join(HERE, f'mandel-N{N}-d{depth}'); os.makedirs(OUT, exist_ok=True)
    fm = flat_mandel(N, depth)
    h = 2 * HALF / N
    rows = []; nums = {}
    for pair in ('E', 'K'):
        t0 = time.time()
        r = mandel(pair, N, depth, procs)
        r['one'] = one_full(RULES[pair][0], N, depth)
        row = []
        for key in ('one', 'union', 'common'):
            v = r[key]
            np.savez_compressed(os.path.join(OUT, f'vol-{pair}-{key}.npz'), vol=np.packbits(v), N=N)
            sl = v[:, :, N // 2]
            nums[f'{pair}|{key}'] = dict(volume=float(v.sum() * h ** 3), cut_area=float(sl.sum() * h * h), flat_area=float(fm.sum() * h * h),
                                         cut_not_flat=int((sl & ~fm).sum()), flat_not_cut=int((fm & ~sl).sum()), flat_pixels=int(fm.sum()))
            row.append(render(v, az=-60, el=22))
            if key != 'one':
                row.append(slice_img(v, None, 'z', fm))
        rows.append(row)
        print(pair, 'done in %.0f s' % (time.time() - t0), json.dumps({k: v for k, v in nums.items() if k.startswith(pair)}), flush=True)
    json.dump(nums, open(os.path.join(OUT, 'numbers.json'), 'w'), indent=1)
    sheet(rows, ['one rule alone', 'UNION: solid', 'union: cut z = 0', 'COMMON: solid', 'common: cut z = 0'],
          ['pair E\n(exact rule)', 'pair K\n(Kleinian\nsquaring)'], os.path.join(HERE, f'sheet-mandel-N{N}-d{depth}.png'),
          title=f'Mandelbrot solids, both rules at every step. Grid {N}, every order tried to depth {depth}.', cell=max(N, 257),
          note=[f'Red line in a cut = the flat Mandelbrot set at the same depth ({depth} steps). The cube shown: x from -2.1 to 0.7, y and z from -1.4 to 1.4.'])
    print('wrote sheet')
