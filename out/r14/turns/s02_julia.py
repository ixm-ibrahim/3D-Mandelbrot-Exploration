# The Julia sets: for each pair (E, K) and each c: one rule alone, union, common. Solids, cuts, numbers.
# Run from the project root: python out/r14/turns/s02_julia.py [N] [procs]
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage
from turns import *

CS = [('c = -1', (-1.0, 0.0, 0.0)), ('c = (-1, 0.15, 0.1)', (-1.0, 0.15, 0.1)),
      ('rabbit\nc = (-0.1226, 0.7449, 0)', (-0.1226, 0.7449, 0.0)), ('c = (-0.6, 0.3, 0.3)', (-0.6, 0.3, 0.3))]


def boxdim(vol):
    """Box-counting slope of the surface between 2 and 16 voxels: 2.0 for a smooth surface."""
    N = vol.shape[0]
    out = []
    for s in (2, 4, 8, 16):
        n = (N // s) * s
        v = vol[:n, :n, :n].reshape(n // s, s, n // s, s, n // s, s)
        a = v.any(axis=(1, 3, 5)); b = v.all(axis=(1, 3, 5))
        out.append((s, int((a & ~b).sum())))
    xs = np.log([1.0 / s for s, _ in out]); ys = np.log([max(c, 1) for _, c in out])
    return float(np.polyfit(xs, ys, 1)[0]), out


def stats(vol, info, c, N, L):
    st3 = np.ones((3, 3, 3), bool)
    lab, ncomp = ndimage.label(vol, structure=st3)
    sizes = np.bincount(lab.ravel())[1:] if ncomp else np.array([0])
    big = float(sizes.max()) / max(1, int(vol.sum()))
    dim, boxes = boxdim(vol)
    s = dict(volume=info['volume'], voxels=int(vol.sum()), depth=info['depth'], converged=bool(info['converged']),
             pieces=int(ncomp), pieces_over_20_voxels=int((sizes > 20).sum()), largest_piece_share=big,
             surface_box_dim=dim, cut_area=float(vol[:, :, N // 2].sum() * info['h'] ** 2))
    if c[2] == 0:
        fj = flat_julia(c[0], c[1], N, L)
        sl = vol[:, :, N // 2]
        s.update(flat_area=float(fj.sum() * info['h'] ** 2), cut_not_flat=int((sl & ~fj).sum()), flat_not_cut=int((fj & ~sl).sum()),
                 flat_pixels=int(fj.sum()))
        # how many of the differing pixels are further than one pixel from the flat set's edge
        edge = ndimage.binary_dilation(fj, iterations=1) & ~ndimage.binary_erosion(fj, iterations=1)
        s['differ_away_from_edge'] = int(((sl ^ fj) & ~edge).sum())
    return s


def job(args):
    pair, ci, N, L, outdir = args
    name, c = CS[ci]
    P1, P2 = RULES[pair]
    fj = flat_julia(c[0], c[1], N, L) if c[2] == 0 else None
    res = {}; ims = {}
    for key, rules, mode in (('one', [P1], 'union'), ('union', [P1, P2], 'union'), ('common', [P1, P2], 'common')):
        vol, death, info = julia(c, rules, mode, N=N, L=L, verbose=False)
        res[key] = stats(vol, info, c, N, L)
        ims[key] = render(vol)
        ims[key + '_cut'] = slice_img(vol, death, 'z', fj)
        ims[key + '_cuty'] = slice_img(vol, death, 'y', None)
        np.savez_compressed(os.path.join(outdir, f'vol-{pair}-{ci}-{key}-N{N}.npz'), vol=np.packbits(vol), N=N, L=L)
    np.savez_compressed(os.path.join(outdir, f'ims-{pair}-{ci}-N{N}.npz'), **ims)
    print(pair, name.replace('\n', ' '), json.dumps({k: {q: (round(v, 4) if isinstance(v, float) else v) for q, v in r.items()} for k, r in res.items()}), flush=True)
    return pair, ci, res


if __name__ == '__main__':
    import multiprocessing as mp
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 257
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    L = 1.7
    OUT = os.path.join(HERE, f'julia-N{N}'); os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    jobs = [(pair, ci, N, L, OUT) for pair in ('E', 'K') for ci in range(len(CS))]
    with mp.Pool(procs) as pool:
        results = pool.map(job, jobs, chunksize=1)
    allres = {}
    for pair, ci, res in results:
        allres[f'{pair}|{CS[ci][0].replace(chr(10), " ")}'] = res
    json.dump(allres, open(os.path.join(OUT, 'numbers.json'), 'w'), indent=1)
    for pair in ('E', 'K'):
        rows = []
        for ci in range(len(CS)):
            d = np.load(os.path.join(OUT, f'ims-{pair}-{ci}-N{N}.npz'))
            rows.append([d['one'], d['union'], d['union_cut'], d['union_cuty'], d['common'], d['common_cut'], d['common_cuty']])
        what = 'E = the exact rule of "Sphere inversions, one plane"' if pair == 'E' else 'K = the Kleinian squaring H (three sphere inversions)'
        sheet(rows, ['one rule alone', 'UNION: solid', 'union: cut z = 0', 'union: cut y = 0', 'COMMON: solid', 'common: cut z = 0', 'common: cut y = 0'],
              [n for n, _ in CS], os.path.join(HERE, f'sheet-julia-{pair}-N{N}.png'),
              title=f'Both rules at every step, pair {pair}. {what}. Grid {N}, all orders to any depth.',
              note=['Union = bounded for some order of the two rules. Common = bounded for every order. Red line in a cut = the flat Julia set (only where c lies in that plane).',
                    'Cuts: light = in the set; blue shades = how late the point left.'])
    print('done in %.0f s' % (time.time() - t0))
