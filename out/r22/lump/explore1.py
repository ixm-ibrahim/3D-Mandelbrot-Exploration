"""First look: fates on a 3D grid.  python out/r22/lump/explore1.py [rule] [cset] [N]"""
import sys, time
import numpy as np
import lumplib as L

rn = sys.argv[1] if len(sys.argv) > 1 else 'along'; cs = sys.argv[2] if len(sys.argv) > 2 else 'rabbit'; N = int(sys.argv[3]) if len(sys.argv) > 3 else 80
r = L.rule(rn); c = L.CSETS[cs]; t0 = time.time()
print(rn, cs, 'follow vs M.stay differ:', L.check_follow(r, c))
g = (np.arange(N) + 0.5) / N * 3.0 - 1.5                       # no grid point on z = 0
gx = (np.arange(N) + 0.5) / N * 3.6 - 1.8
X, Y, Z = np.meshgrid(gx, g, g, indexing='ij')
code, ex = L.fates(r, X, Y, Z, c)
tot = (code > 0).sum()
print('inside at 80 steps and after the long run: %d (leaked in the long run: %d)  %.0f s' % (tot, ex['leaked'], time.time() - t0))
for k in range(1, 7):
    print('  %-28s %7d  %5.1f %%' % (L.FATE_NAMES[k], (code == k).sum(), 100.0 * (code == k).sum() / max(tot, 1)))
per = ex['period']; print('periods found:', {int(p): int((per == p).sum()) for p in np.unique(per)})
zm = ex['zmax']; print('zmax quantiles (0, 50, 90, 99, 100 %):', np.quantile(zm, [0, 0.5, 0.9, 0.99, 1.0]) if zm.size else None)
dc = ex['dcyc']; print('dist to flat cycle quantiles:', np.quantile(dc, [0, 0.5, 0.9, 0.99, 1.0]) if dc.size and np.isfinite(dc).all() else None)
lam = ex['lam']; ok = np.isfinite(lam)
if ok.any():
    print('neighbour drift of the %d without a cycle: quantiles' % ok.sum(), np.quantile(lam[ok], [0, 0.1, 0.5, 0.9, 1.0]))
    e = ex['end'][:, ok]; print('  their last points: x %.3f..%.3f y %.3f..%.3f |z| %.3f..%.3f' % (e[0].min(), e[0].max(), e[1].min(), e[1].max(), np.abs(e[2]).min(), np.abs(e[2]).max()))
off = (per > 0) & (zm > 1e-7)
if off.any():
    e = ex['end'][:, off]; print('off-page cycles: %d; periods' % off.sum(), {int(p): int((per[off] == p).sum()) for p in np.unique(per[off])})
    print('  sample ends:', np.round(e[:, :8].T, 4).tolist())
