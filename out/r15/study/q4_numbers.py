"""Question 4: other layouts, in numbers. python out/r15/study/q4_numbers.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from q3_stretch import jac, stats
np.seterr(all='ignore')
KEYS = [('E', 1.0, 2, 0.5), ('E', 0.8, 2, 0.5), ('E', 1.3, 2, 0.5), ('E', 1.0, 2, 0.35), ('E', 1.0, 2, 0.65), ('E', 1.3, 2, 0.35),
        ('J', 1.0, 2), ('J', 0.8, 2), ('J', 1.3, 2), ('J', 1.7, 2), ('bulb',), ('merc',)]
CS = (('c = -1', (-1.0, 0, 0)), ('rabbit', (-0.12, 0.74, 0.0)), ('c = (-1, 0.15, 0.1)', (-1.0, 0.15, 0.1)))

if __name__ == '__main__':
    res = {}
    rng = np.random.default_rng(11)
    d = rng.normal(size=(20000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    # near the plane: sideways stretch (should be 2 for an angle-true belt)
    th = rng.uniform(0, 2 * np.pi, 4000); e = np.stack([np.cos(th), np.sin(th), 0 * th], 1)
    print('layout | one step, no c: unit stretch 1%% / median / 99%%; shape ratio median / 99%% | 6 steps, no c: ratio median / 99%% | next to the surface, ratio median at k = 8 and k = 14 for c = -1; rabbit; c = (-1, 0.15, 0.1) | sideways stretch just above / below the plane (min..max)')
    for key in KEYS:
        r = {}
        out = jac(d, key, 6, h=1e-7)
        J1, ok = out[1]; sv = np.linalg.svd(J1, compute_uv=False)
        # the two stretches along the sphere: drop the radial one (exactly 2 at length 1)
        s1 = stats(*out[1]); s6 = stats(*out[6])
        a = d + 1e-5 * rng.normal(size=d.shape); a /= np.linalg.norm(a, axis=1)[:, None]
        fa = np.stack(vox.step(a[:, 0], a[:, 1], a[:, 2], key), 1); fd = np.stack(vox.step(d[:, 0], d[:, 1], d[:, 2], key), 1)
        st = np.linalg.norm(fa - fd, axis=1) / np.linalg.norm(a - d, axis=1)
        r['unit_stretch'] = [float(np.quantile(st, .01)), float(np.median(st)), float(np.quantile(st, .99))]
        r['k1'] = s1; r['k6'] = s6
        side = []
        for sg in (1, -1):
            u = e.copy(); u[:, 2] = sg * 1e-5; u /= np.linalg.norm(u, axis=1)[:, None]
            fu = np.stack(vox.step(u[:, 0], u[:, 1], u[:, 2], key), 1); f0 = np.stack(vox.step(e[:, 0], e[:, 1], e[:, 2] + 1e-300, key), 1)
            q = np.linalg.norm(fu - f0, axis=1) / 1e-5; side += [float(q.min()), float(q.max())]
        r['sideways'] = side
        surf = []
        for cname, c in CS:
            g = np.random.default_rng(5)
            p = g.normal(size=(300000, 3)); p *= (1.5 * g.uniform(0, 1, 300000) ** (1 / 3) / np.linalg.norm(p, axis=1))[:, None]
            dd = vox.esc(p[:, 0], p[:, 1], p[:, 2], c, key, 80)
            q = p[(dd >= 17) & (dd < 80)]
            o = jac(q, key, 14, c=c, h=1e-9)
            r[cname] = {k: stats(*o[k]) for k in (4, 8, 14)}
            surf.append('%.3g, %.3g (n=%d)' % (r[cname][8]['median'], r[cname][14]['median'], len(q)))
        res[str(key)] = r
        print('%-22s | %.2f / %.2f / %.2f; %.2f / %.1f | %.2f / %.1f | %s | %.2f..%.2f / %.2f..%.2f' % (
            key, r['unit_stretch'][0], r['unit_stretch'][1], r['unit_stretch'][2], s1['median'], s1['p99'], s6['median'], s6['p99'], ';  '.join(surf), side[0], side[1], side[2], side[3]), flush=True)
        json.dump(res, open(os.path.join(HERE, 'q4-numbers.json'), 'w'), indent=1)
