"""The N sweep: 'along' for the first N steps of an orbit, then one plane.   python out/r23/rabbit/nsweep.py
For c = -1: how many buds stand round each body? On circles round the x-axis at the middle of a body (x0), radius R,
1440 test points, 80 steps: the number of separate arcs that stay. Reported for every R from 0.20 to 0.90: the largest
count, and the range of R over which exactly 8 (or 4, or 2) arcs are seen.
For the rabbit: volume, bodies, patches at the meeting point (from measure.py).
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import doors as D
import measure as ME
M = D.M
NS = [0, 1, 2, 3, 5, 99]
BODIES = [('middle body (x = 0)', 0.0), ('side body (x = -1)', -1.0), ('side body (x = 1)', 1.0)]


def arcs(r, x0, R, n=1440, steps=80):
    a = (np.arange(n) + 0.5) / n * 2 * np.pi
    ins = M.stay(r, np.full(n, x0), R * np.cos(a), R * np.sin(a), -1.0, 0.0, 0.0, steps) >= steps
    if ins.all():
        return -1, 1.0                                       # the circle is wholly inside
    k = int(np.argmin(ins)); v = np.roll(ins, -k)            # start at an outside point
    edges = np.diff(v.astype(int)); starts = np.nonzero(edges == 1)[0]; ends = np.nonzero(edges == -1)[0]
    if v[-1]:
        ends = np.append(ends, n - 1)
    wide = int(((ends - starts) >= 3).sum()) if starts.size else 0
    return wide, float(ins.mean())


if __name__ == '__main__':
    out = {}
    for N in NS:
        key = 'along%d' % N; r = D.get(key); row = {}
        for nm, x0 in BODIES[:3]:
            Rs = np.arange(0.10, 0.90, 0.01); cnt = [arcs(r, x0, R)[0] for R in Rs]
            cnt = np.array(cnt); best = int(cnt.max())
            rng = {}
            for m in (2, 4, 8):
                w = Rs[cnt == m]; rng[m] = (float(w.min()), float(w.max()), int(w.size)) if w.size else None
            row[nm] = {'most': best, 'ranges': rng, 'full_until': float(Rs[cnt == -1].max()) if (cnt == -1).any() else 0.0}
        mb = ME.measure(key, 'basilica'); mr = ME.measure(key, 'rabbit')
        row['basilica'] = mb; row['rabbit'] = mr; out[key] = row
        print('N = %2d | c = -1: vol %.3f, bodies %d, off the flat plane %d (ratio med %s), thin %.3f, loose %.3f' % (N, mb['vol80'], mb['bodies'], mb['off'], ('%.2f' % mb['off_ratio_median']) if mb['off'] else '-', mb['thin'], mb['loose']))
        for nm, x0 in BODIES[:3]:
            q = row[nm]
            print('        %-28s most arcs on a circle: %d; R with 8 arcs: %s; with 4: %s; with 2: %s; solid out to R = %.2f' % (nm, q['most'], q['ranges'][8], q['ranges'][4], q['ranges'][2], q['full_until']))
        mt = mr['meet0.03']; mt6 = mr['meet0.06']
        print('        rabbit: vol %.3f (30 steps %.3f), pieces>=8 %d, loose %.3f, thin %.3f, bodies %d (biggest holds %.2f), off the flat plane %d (joined %d, loose %d, ratio med %s), over %.2f, zmax %.2f, meeting point: %d patches %.2f of the small ball (R 0.06: %d, %.2f)'
              % (mr['vol80'], mr['vol30'], mr.get('pieces8', 0), mr['loose'], mr['thin'], mr['bodies'], mr['big'], mr['off'], mr['off_joined'], mr['off_loose'], ('%.2f' % mr['off_ratio_median']) if mr['off'] else '-', mr['over'], mr['zmax'], mt['patches'], mt['share'], mt6['patches'], mt6['share']))
        sys.stdout.flush()
    json.dump(out, open(os.path.join(HERE, 'nsweep.json'), 'w'), indent=1)
