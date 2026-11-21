"""Skeptic, job 3: can M.solid show what the cut along the flat page shows?  python out/r21/skeptic/fin.py
The eye stands on the z-axis, so the screen IS the flat page seen from above. The solid is made twice: with an odd
number of blocks in depth (one layer of blocks lies exactly on z = 0) and with an even number (no layer on z = 0,
the nearest are half a block away). Flat-cut pixels that the second solid does not cover are parts of the flat
picture that have no thickness a block can catch."""
import sys, time
import numpy as np
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

w, h, steps, hw = 281, 241, 60, 1.7; t0 = time.time()
us = np.linspace(-hw, hw, w); vs = np.linspace(hw * h / w, -hw * h / w, h); U, V = np.meshgrid(us, vs)
print('Mandelbrot solid, eye on the z-axis, %d steps. Flat-cut pixels NOT covered by the silhouette of the solid:' % steps)
for nm in ('oneplane', 'along', 'lathe', 'lag05', 'lag25', 'lag40', 'lag60', 'lag75', 'lag90', 'delay', 'first'):
    r = M.bench(nm) if nm in ('oneplane', 'along', 'lathe') else R.BY[nm]
    flat = M.mandel(r, -0.7 + U, V, np.zeros_like(U), steps) >= steps
    out = []
    for nd in (161, 160, 1600):
        if nd == 1600:                                       # only the two layers nearest the page of a 1,600-deep solid: 0.001 above and below
            z = hw / 1599.0; hit = (M.mandel(r, -0.7 + U, V, np.full_like(U, z), steps) >= steps) | (M.mandel(r, -0.7 + U, V, np.full_like(U, -z), steps) >= steps)
            # (a full solid would cover more only through blocks farther from the page; those are counted in the 160 column)
        else:
            dep, px = M.solid(r, None, w, h, nd, steps, cam=(0, 0, 1)); hit = np.isfinite(dep)
        out.append(int((flat & ~hit).sum()))
    print('  %-9s flat cut has %5d pixels | odd depth (a layer on z = 0): %4d missing | even depth 160 blocks: %4d missing | layers at z = +-0.001 alone: %4d missing   %.0f s'
          % (nm, int(flat.sum()), out[0], out[1], out[2], time.time() - t0)); sys.stdout.flush()
