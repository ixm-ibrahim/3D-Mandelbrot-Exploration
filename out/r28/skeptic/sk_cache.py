"""Round 28, skeptic of Track B: are the explorer's kept blocks (the ones their three user pictures are drawn from)
what the rule gives? Random blocks of each kept solid against my own verdict at the block's centre. Read only.

    PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -W ignore out/r28/skeptic/sk_cache.py > out/r28/skeptic/cache-check.log
"""
import os, sys
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, HERE)
import sk_vox
rng = np.random.default_rng(77)
for tag, layout, c, N in (('m1-0.006', 'A', (-1.0, 0.0), 300000), ('rab-0.006', 'A', sk_vox.RABBIT, 300000), ('rabm-0.006', 'A', (sk_vox.RABBIT[0], -sk_vox.RABBIT[1]), 150000), ('m1-lean50-0.006', 'B', (-1.0, 0.0), 120000)):
    d = np.load(os.path.join(ROOT, 'out', 'r28', 'pillow3', 'cache', tag + '.npz')); sh = tuple(d['shape']); th = np.unpackbits(d['ins'])[:int(np.prod(sh))].reshape(sh).astype(bool); n = int(d['n']); h = float(d['h'])
    if not bool(d['full']):
        th = np.concatenate([th[:, :, ::-1], th], 2)
    if bool(d['quarter']):
        th = np.concatenate([th[:, ::-1], th], 1)
    ax = (np.arange(-n, n) + 0.5) * h; F = sk_vox.step_fn(layout)
    # half of the sample from all blocks in the ball, half from blocks at the solid's skin (inside with an outside neighbour, or the reverse)
    i = rng.integers(0, 2 * n, size=(3, N // 2)); R = n * h; ok = (ax[i[0]] ** 2 + ax[i[1]] ** 2 + ax[i[2]] ** 2) < R * R; i = i[:, ok]
    edge = th.copy(); edge[1:] ^= th[:-1]; e = np.argwhere(edge); e = e[rng.integers(0, e.shape[0], N // 2)].T
    out = []
    for nm, idx in (('anywhere in the ball', i), ('at the skin of the solid', e)):
        mine = sk_vox.inside_pts(F, ax[idx[0]], ax[idx[1]], ax[idx[2]], c, int(d['steps'])); theirs = th[idx[0], idx[1], idx[2]]
        out.append('%s: %d of %d differ (inside: %d)' % (nm, int((mine != theirs).sum()), idx.shape[1], int(theirs.sum())))
    print('%s (%d steps, quarter computed: %s): %s' % (tag, int(d['steps']), bool(d['quarter']), '; '.join(out))); sys.stdout.flush()
