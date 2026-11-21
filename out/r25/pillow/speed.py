"""The angle-true layout: accuracy (round trip pillow -> direction -> pillow -> direction) and time."""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P

rng = np.random.default_rng(3); d = rng.normal(size=(3, 400000)); d /= np.sqrt((d * d).sum(0))
for rho, H in ((0.25, 0.968), (0.5, 0.866), (0.0, 1.0)):
    t0 = time.time(); pl = P.Pillow(rho, H, 'JA'); tb = time.time() - t0
    t0 = time.time(); x, y = pl.to_flat(*d); t1 = time.time() - t0
    rt = np.abs(np.stack(pl.from_flat(x, y)) - d).max(0)
    # the other way round: pillow points -> direction -> pillow point
    xx = rng.uniform(0, 1, 400000); yy = rng.uniform(0, H / 2, 400000); x2, y2 = pl.to_flat(*pl.from_flat(xx, yy))
    ey = np.abs(y2 - yy)
    print('rho %.2f H %.3f: tables %.1f s; direction round trip worst %.1e, 99.99 %% %.1e, 99.9 %% %.1e, median %.1e; height on the pillow worst %.1e, 99.9 %% %.1e; %.2f s per 400,000'
          % (rho, H, tb, rt.max(), np.quantile(rt, 0.9999), np.quantile(rt, 0.999), np.median(rt), ey.max(), np.quantile(ey, 0.999), t1))
    plJ = P.Pillow(rho, H, 'J'); t0 = time.time(); plJ.to_flat(*d); print('   plain layout: %.2f s' % (time.time() - t0))
