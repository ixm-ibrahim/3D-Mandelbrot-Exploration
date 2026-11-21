"""Round 20 check, extras: (1) how big a nudge the basilica's resting cycle survives, by direction of the nudge;
(2) where the basilica's loose voxel pieces sit; (3) panel2's hair number on the FLAT rabbit and Siegel disc (control)."""
import os, sys, json
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r19', 'panel2'))
import wide as Wd
import hairnum as H
B = Wd.B; R = Wd.R
out = {}
what = sys.argv[1:] or ['nudge', 'loose', 'flat']

def settles(F, c, n=4000):
    x = np.zeros(1); y = np.zeros(1); z = np.zeros(1); R2 = B.resc(c) ** 2; tr = []
    for k in range(n):
        x, y, z = F(x, y, z); x = x + c[0]; y = y + c[1]; z = z + c[2]
        if x[0] ** 2 + y[0] ** 2 + z[0] ** 2 > R2:
            return 'L'
        if k >= n - 400:
            tr.append((x[0], y[0], z[0]))
    tr = np.array(tr)
    for p in (1, 2, 3, 4, 6, 8, 12, 16):
        if np.abs(tr[p:] - tr[:-p]).max() < 1e-6:
            return str(p) if p < 10 else 'c'
    return '~'

if 'nudge' in what:
    print('Does the orbit of 0 settle on a cycle? digit = length of the cycle, c = a longer cycle, ~ = never settles (churns), L = leaves.')
    for base, cx in (('basilica', -1.0), ('sanmarco_side -0.9', -0.9)):
        for rule in ('m_w3', 'along', 'oneplane'):
            F = R.get(rule)
            print('%s, rule %s; columns = direction of the nudge 0, 5, ... 90 degrees from the flat plane' % (base, rule))
            for size in (0.005, 0.01, 0.02, 0.03, 0.04, 0.058, 0.08):
                row = [settles(F, (cx, size * np.cos(np.radians(d)), size * np.sin(np.radians(d)))) for d in range(0, 91, 5)]
                out['nudge|%s|%s|%g' % (base, rule, size)] = row
                print('   nudge %.3f: %s' % (size, ' '.join(row)), flush=True)
    json.dump(out, open(os.path.join(HERE, 'extra.json'), 'w'), indent=1)

if 'loose' in what:
    F = R.get('m_w3'); N = 385; L = 1.7
    vol = B.volume(F, N, L=L, c=(-1.0, 0.0, 0.0), steps=40)
    lab, k = ndimage.label(vol); sz = np.bincount(lab.ravel()); sz[0] = 0; big = int(np.argmax(sz))
    idx = [i for i in range(1, k + 1) if i != big]
    com = np.array(ndimage.center_of_mass(vol, lab, idx)); a = np.linspace(-L, L, N); h = a[1] - a[0]
    xyz = -L + com * h; ang = np.degrees(np.arctan2(xyz[:, 2], xyz[:, 1])) % 60.0; d = np.minimum(ang, 60 - ang); rho = np.hypot(xyz[:, 1], xyz[:, 2]); w = sz[idx] * h ** 3
    tot = w.sum()
    print('basilica, m_w3, %d a side: %d loose pieces, loose volume %.4f (%.2f %% of the solid)' % (N, len(idx), tot, 100 * tot / (vol.sum() * h ** 3)))
    for lo, hi in ((0, 3), (3, 10), (10, 20), (20, 30.01)):
        m = (d >= lo) & (d < hi)
        print('   %2d to %2d degrees from the nearest of the six planes: %5d pieces, %.1f %% of the loose volume, biggest %.6f, median distance from the axis %.2f' % (lo, hi, m.sum(), 100 * w[m].sum() / tot, w[m].max() if m.any() else 0, np.median(rho[m]) if m.any() else 0))
    out['loose'] = dict(pieces=len(idx), volume=float(tot))
    # the same for the one-plane rule
    vol1 = B.volume(R.get('oneplane'), N, L=L, c=(-1.0, 0.0, 0.0), steps=40); lab1, k1 = ndimage.label(vol1); s1 = np.bincount(lab1.ravel())[1:]
    print('   one plane, same grid: %d loose pieces, loose volume %.4f' % (k1 - 1, (s1.sum() - s1.max()) * h ** 3))

if 'flat' in what:
    # panel2's hair number on flat sets it was not calibrated on: one plane cut at 0 degrees
    for tag in ('rabbit', 'siegel', 'basilica'):
        F = R.get('oneplane'); c, L, _ = Wd.SETS[tag]; scale = Wd.thick_of(tag) / 0.47
        xs = np.linspace(-L, L, 401); ss = np.linspace(0.0, L, 201)[1:]; X, Sg = np.meshgrid(xs, ss, indexing='ij')
        ins, _ = B.inside(F, X, Sg, 0 * Sg, c=c, steps=80); lab, k = ndimage.label(ins); big = lab == (1 + int(np.argmax(np.bincount(lab.ravel())[1:])))
        d = ndimage.distance_transform_edt(np.pad(big, ((1, 1), (0, 1)))[1:-1, :-1]); i, j = np.unravel_index(int(np.argmax(d)), d.shape); dmax = float(d[i, j] * (xs[1] - xs[0])); s0 = float(ss[j])
        res = []
        for off in Wd.FLAT_OFFS:
            x0 = float(xs[i] + off * dmax); s = np.linspace(s0, 1.3 * L, 20001); i1, _ = B.inside(F, np.full_like(s, x0), s, 0 * s, c=c, steps=80); o = np.flatnonzero(~i1)
            if not o.size or o[0] == 0:
                continue
            e = float(s[o[0]])
            for q, hw0 in enumerate(Wd.WID):
                hw = hw0 * scale; x, sg = np.meshgrid(np.linspace(x0 - hw, x0 + hw, Wd.CW), np.linspace(e + 0.7 * hw, e - 0.7 * hw, Wd.CH))
                it, _ = B.inside(F, x, sg, 0 * sg, c=c, steps=80); sc = H.score(it)
                if sc['fins'] is not None:
                    res.append((sc['fins'], sc['film_pct']))
        over = sum(1 for f_, l_ in res if f_ > H.T_FINS or l_ > H.T_FILM)
        print('flat %s (one plane cut at 0 degrees): %d tiles, worst thin %.2f, worst film %.1f %%, %d over a line' % (tag, len(res), max(r[0] for r in res), max(r[1] for r in res), over), flush=True)
        out['flat|' + tag] = dict(tiles=len(res), thin=max(r[0] for r in res), film=max(r[1] for r in res), over=over)
    json.dump(out, open(os.path.join(HERE, 'extra.json'), 'w'), indent=1)
