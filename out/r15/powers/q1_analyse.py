"""Question 1 and 5 in numbers: pieces, bodies (by shaving the solid), halves above and below the plane.
python q1_analyse.py N"""
import os, sys, json, numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
N = int(sys.argv[1])
names = ['m2', 'm3', 'm4', 'm5', 'j2', 'j3', 'j4', 'j5']
ALL = np.ones((3, 3, 3))
out = {}
for nm in names:
    f = os.path.join(HERE, 'data', 'q1-%s-%d.npz' % (nm, N))
    if not os.path.exists(f): continue
    D = np.load(f); v = D['inside']; cen = D['cen']; L = float(D['L']); n = int(D['n'])
    a = np.linspace(-L, L, N); h = a[1] - a[0]
    ax, ay, az = a + cen[0], a + cen[1], a + cen[2]
    vox = h ** 3
    r = dict(power=n, voxel=h, volume=float(v.sum() * vox))
    for k, nmx, A in ((0, 'x', ax), (1, 'y', ay), (2, 'z', az)):
        w = np.where(v.any(axis=tuple(i for i in range(3) if i != k)))[0]
        r[nmx + '_range'] = [float(A[w.min()]), float(A[w.max()])]
    up = v[:, :, az > h / 2].sum() * vox; dn = v[:, :, az < -h / 2].sum() * vox
    r['volume_above'] = float(up); r['volume_below'] = float(dn)
    # pieces as drawn (touching by a face, edge or corner counts as joined)
    lab, k = ndimage.label(v, structure=ALL)
    sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    r['pieces'] = int(k); r['largest_share'] = float(sizes[0] / v.sum()); r['pieces_over_30_voxels'] = int((sizes >= 30).sum())
    r['second_piece_share'] = float(sizes[1] / v.sum()) if k > 1 else 0.0
    # mirror in z (only meaningful when the box is centred on z = 0)
    if abs(cen[2]) < 1e-12:
        r['mirror_z_mismatch_share'] = float((v != v[:, :, ::-1]).sum() / max(1, v.sum()))
    # bodies: shave the solid by a depth d (keep points deeper than d inside), count what is left
    edt = ndimage.distance_transform_edt(v) * h
    shave = {}
    for d in (0.02, 0.03, 0.04, 0.06, 0.08, 0.1):
        core = edt > d
        lab, k = ndimage.label(core, structure=ALL)
        if k == 0: shave['%g' % d] = dict(bodies=0); continue
        cnt = np.bincount(lab.ravel())[1:]
        keep = np.where(cnt >= 8)[0]
        com = ndimage.center_of_mass(core, lab, keep + 1)
        rows = []
        for j, cm in zip(keep, com):
            p = (ax[0] + cm[0] * h, ay[0] + cm[1] * h, az[0] + cm[2] * h)
            # grown-back size: volume of the body is roughly that of the core plus a shell; report core volume
            rows.append((float(cnt[j] * vox), round(p[0], 3), round(p[1], 3), round(p[2], 3)))
        rows.sort(reverse=True)
        inplane = sum(1 for q in rows[1:] if abs(q[3]) < 0.06)
        shave['%g' % d] = dict(bodies=len(rows), round_main_in_plane=inplane, round_main_off_plane=len(rows) - 1 - inplane,
                               above=sum(1 for q in rows[1:] if q[3] >= 0.06), below=sum(1 for q in rows[1:] if q[3] <= -0.06), list=rows[:40])
    r['shave'] = shave
    out[nm] = r
    print('%s power %d N=%d voxel %.4f: volume %.4f (above the plane %.4f, below %.4f); x %s y %s z %s' % (
        nm, n, N, h, r['volume'], up, dn, np.round(r['x_range'], 3), np.round(r['y_range'], 3), np.round(r['z_range'], 3)))
    print('   pieces as drawn %d (over 30 voxels: %d), largest holds %.2f %%, second %.2f %%%s' % (
        r['pieces'], r['pieces_over_30_voxels'], 100 * r['largest_share'], 100 * r['second_piece_share'],
        '' if 'mirror_z_mismatch_share' not in r else '; mirror in z: %.3f %% of voxels differ' % (100 * r['mirror_z_mismatch_share'])))
    for d, s in shave.items():
        if s['bodies'] == 0: print('   shaved by %s: nothing left' % d); continue
        print('   shaved by %s: %d bodies; round the largest: %d in the plane, %d off it (%d above, %d below); sizes %s' % (
            d, s['bodies'], s['round_main_in_plane'], s['round_main_off_plane'], s['above'], s['below'], ['%.3g' % q[0] for q in s['list'][:14]]))
    sys.stdout.flush()
json.dump(out, open(os.path.join(HERE, 'q1-analyse-%d.json' % N), 'w'), indent=1)
