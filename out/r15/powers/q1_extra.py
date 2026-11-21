"""Extra counts: power 4 at the second c (bodies by shaving), the largest pieces of each Julia solid, and
whether the cut at x = 0 of the power-3 solids is the flat set again."""
import os, sys, json, numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data')
ALL = np.ones((3, 3, 3)); out = {}
V = np.load(os.path.join(D, 'q1-j4b-193.npz')); v = V['inside']; cen = V['cen']; L = float(V['L']); N = v.shape[0]
a = np.linspace(-L, L, N); h = a[1] - a[0]
edt = ndimage.distance_transform_edt(v) * h
lab, k = ndimage.label(v, structure=ALL); sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
print('j4b: volume %.4f, pieces %d, largest %.2f %%' % (v.sum() * h ** 3, k, 100 * sizes[0] / v.sum()))
for d in (0.03, 0.04, 0.06, 0.08, 0.1):
    core = edt > d; lab, k = ndimage.label(core, structure=ALL); cnt = np.bincount(lab.ravel())[1:]
    keep = np.where(cnt >= 8)[0]; com = ndimage.center_of_mass(core, lab, keep + 1)
    rows = sorted([(float(cnt[j] * h ** 3), round(cen[0] - L + cm[0] * h, 2), round(cen[1] - L + cm[1] * h, 2), round(cen[2] - L + cm[2] * h, 2)) for j, cm in zip(keep, com)], reverse=True)
    zs = sorted(set(round(q[3], 1) for q in rows[1:]))
    print('  shaved by %g: %d bodies besides the largest; by height z: %s' % (d, len(rows) - 1, {z: sum(1 for q in rows[1:] if round(q[3], 1) == z) for z in zs}))
    out['j4b_shave_%g' % d] = rows[:40]
for nm in ('j2', 'j3', 'j4', 'j5', 'm2', 'm3', 'm4', 'm5'):
    v = np.load(os.path.join(D, 'q1-%s-225.npz' % nm))['inside']
    lab, k = ndimage.label(v, structure=ALL); sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    out[nm + '_piece_shares'] = [float(s / v.sum()) for s in sizes[:8]]
    print('%s: the eight largest pieces hold %s %% of the solid' % (nm, ' '.join('%.2f' % (100 * s / v.sum()) for s in sizes[:8])))
for nm in ('m3', 'j3'):
    C = np.load(os.path.join(D, 'cuts-%s.npz' % nm)); ix, fl = C['ix'], C['flat']      # ix[iy, iz], fl[ix, iy]
    cands = {'x -> z': ix.T, 'x -> -z': ix.T[::-1]}
    print('%s: cut at x = 0 against the flat set (601 x 601): pixels that differ: %s' % (nm, {k: int((a != fl).sum()) for k, a in cands.items()}))
    out[nm + '_x0_vs_flat'] = {k: int((a != fl).sum()) for k, a in cands.items()}
json.dump(out, open(os.path.join(HERE, 'q1-extra.json'), 'w'), indent=1)
