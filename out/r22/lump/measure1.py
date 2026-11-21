"""Numbers on a 3D grid: bodies pressed together (walls), the height law, how fast points come down to the page.
    python out/r22/lump/measure1.py [cset] [N]    -> prints; measure1-<cset>.json"""
import sys, time, json, os
import numpy as np
import lumplib as L

cs = sys.argv[1] if len(sys.argv) > 1 else 'rabbit'; N = int(sys.argv[2]) if len(sys.argv) > 2 else 96
c = L.CSETS[cs]; fc = L.flat_cycle(c); per = len(fc) if fc else 1; STEPS = 120
g = (np.arange(N) + 0.5) / N * 3.0 - 1.5; gx = (np.arange(N) + 0.5) / N * 3.6 - 1.8
X, Y, Z = np.meshgrid(gx, g, g, indexing='ij'); cell = (3.6 / N) * (3.0 / N) ** 2
res = {}; t0 = time.time(); R = {}
for rn in ['along', 'oneplane', 'alongmem.c_wake1', 'lathe']:
    r = L.rule(rn); ro = L.route(r, X, Y, Z, c, STEPS); R[rn] = ro
    ins = ro['inside']; ph = ro['phase']; tot = int(ins.sum())
    same = diff = 0                                            # face neighbours, both inside: same body or two bodies
    for ax in range(3):
        a = [slice(None)] * 3; b = [slice(None)] * 3; a[ax] = slice(0, -1); b[ax] = slice(1, None); a, b = tuple(a), tuple(b)
        both = ins[a] & ins[b]; same += int((both & (ph[a] == ph[b])).sum()); diff += int((both & (ph[a] != ph[b])).sum())
    skin = 0                                                   # faces between an inside block and an outside block
    for ax in range(3):
        a = [slice(None)] * 3; b = [slice(None)] * 3; a[ax] = slice(0, -1); b[ax] = slice(1, None); a, b = tuple(a), tuple(b)
        skin += int((ins[a] != ins[b]).sum())
    land = ro['land'][ins]; h = np.abs(Z[ins])
    hi = h > 0.2
    d = dict(inside=tot, vol=tot * cell, by_body=[int((ins & (ph == k)).sum()) for k in range(-1, per)], walls=diff, skin=skin,
             wall_share=diff / max(diff + skin, 1), land_median=float(np.median(land)) if tot else None,
             land_hi_median=float(np.median(land[hi])) if hi.any() else None, hi=int(hi.sum()),
             land_hist=[int((land == k).sum()) for k in range(0, 13)], never_low=int((land >= STEPS).sum()))
    res[rn] = d
    print('%-18s inside %6d vol %.3f | by body (none, then cycle points) %s | faces: body against body %6d, body against outside %6d -> %.1f %% of all skin is a wall between two bodies'
          % (rn, tot, d['vol'], d['by_body'], diff, skin, 100 * d['wall_share']))
    print('    steps until the height stays under 0.02: median %s; for the %d that start higher than 0.2: median %s; histogram 0..12 %s  (%.0f s)'
          % (d['land_median'], d['hi'], d['land_hi_median'], d['land_hist'], time.time() - t0)); sys.stdout.flush()

# the height law: one squaring, at the points of along's lump higher than 0.05
ins = R['along']['inside'] & (np.abs(Z) > 0.05); x, y, z = X[ins], Y[ins], Z[ins]; n = x.size
cx, cy, cz = (np.full(n, t) for t in c); rr = np.sqrt(x * x + y * y + z * z)
print('height after one squaring / height before, at the %d points of along\'s lump higher than 0.05:' % n)
for rn in ['along', 'oneplane', 'lathe']:
    r = L.rule(rn); o = r.step(x, y, z, tuple(r.init(n)), 0, cx, cy, cz); q = np.abs(o[2] + cz) / np.abs(z)
    res['ratio_' + rn] = dict(median=float(np.median(q)), q25=float(np.quantile(q, 0.25)), q75=float(np.quantile(q, 0.75)), under1=float((q < 1).mean()))
    print('  %-9s median %.3f (quartiles %.3f, %.3f); shrinks at %.1f %% of the points | compare 2|x|: median %.3f, 2r: median %.3f'
          % (rn, np.median(q), np.quantile(q, 0.25), np.quantile(q, 0.75), 100 * (q < 1).mean(), np.median(2 * np.abs(x)), np.median(2 * rr)))
# along against one plane: the extra points
a, o = R['along']['inside'], R['oneplane']['inside']
print('along inside %d, one plane inside %d, both %d; along only %d (%.1f %% of along)' % (a.sum(), o.sum(), (a & o).sum(), (a & ~o).sum(), 100.0 * (a & ~o).sum() / max(a.sum(), 1)))
res['along_only'] = int((a & ~o).sum()); res['both'] = int((a & o).sum()); res['oneplane_only'] = int((o & ~a).sum())
for lo, hi in ((0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 0.8), (0.8, 1.5)):
    m = (np.abs(Z) >= lo) & (np.abs(Z) < hi)
    print('  height %.2f..%.2f: along %6d, one plane %6d, ratio %.2f' % (lo, hi, (a & m).sum(), (o & m).sum(), (a & m).sum() / max((o & m).sum(), 1)))
    res['band_%.2f' % lo] = [int((a & m).sum()), int((o & m).sum())]
json.dump(res, open(os.path.join(L.HERE, 'measure1-%s.json' % cs), 'w'), indent=1)
