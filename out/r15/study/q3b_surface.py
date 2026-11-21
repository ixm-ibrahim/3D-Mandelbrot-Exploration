"""Question 3, the part that matters for the pictures: stretch of (F + c)^k at points right next to the surface.
Points: random in the ball of radius 1.5, kept when they stay inside radius 2 for at least 16 steps and leave
before step 80 (so they sit just outside the solid). python out/r15/study/q3b_surface.py [extra layout keys]"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from q3_stretch import jac, stats
np.seterr(all='ignore')

if __name__ == '__main__':
    keys = [Fp.REF, ('merc',), ('bulb',)] + [eval(a) for a in sys.argv[1:]]
    res = {}
    for cname, c in (('c = -1', (-1.0, 0, 0)), ('rabbit', (-0.12, 0.74, 0.0)), ('c = (-1, 0.15, 0.1)', (-1.0, 0.15, 0.1))):
        print('(F + c)^k, %s, points next to the surface' % cname, flush=True)
        for key in keys:
            rng = np.random.default_rng(5)
            p = rng.normal(size=(500000, 3)); p *= (1.5 * rng.uniform(0, 1, 500000) ** (1 / 3) / np.linalg.norm(p, axis=1))[:, None]
            d = vox.esc(p[:, 0], p[:, 1], p[:, 2], c, key, 80)
            sel = (d >= 17) & (d < 80)
            q = p[sel]
            out = jac(q, key, 14, c=c, h=1e-9)
            res.setdefault(str(key), {})[cname] = {}
            line = []
            for k in (1, 2, 4, 6, 8, 10, 12, 14):
                J, ok = out[k]
                s = stats(J, ok); res[str(key)][cname][k] = s
                line.append('k=%d: %.3g / %.3g' % (k, s['median'], s['p90']))
            print('  %-22s n=%5d  median / 90%%:  ' % (key, len(q)) + ';  '.join(line), flush=True)
    json.dump(res, open(os.path.join(HERE, 'q3b%s.json' % ('' if len(sys.argv) == 1 else '-extra')), 'w'), indent=1)
