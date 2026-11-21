"""Round 24, section "push": the PREDICTIONS of the push law, for every rule and every c of the panel.

    python out/r24/push/law.py [rule,rule,...]       -> the tables on the screen, cache/law.json

Law A (briefing 2 (c)): push * d at lifts 8, 15, 25 degrees; above 1 at all three = bodies kept apart.
Law B (mine): the weakest one-step height gain H(h)/h of a point straight above the meeting point, lifts 1 .. 50.
Also, per rule: the push all round (lift 15), and the weakest gain / d all round (so that gain = that * d).
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import plib as P


def strength(G, lons, top=50.0):
    """For each longitude: min over lifts 1..top of (one-step height gain) / d, with d = 0.53 (it hardly depends on d)."""
    lifts = np.arange(1.0, top + 0.01, 0.5); out = []
    for lo in lons:
        a = 0.53 * np.exp(1j * np.radians(lo)); g = P.gain(G, a, 0j, lifts) / 0.53; i = int(np.argmin(g)); out.append((float(g[i]), float(lifts[i])))
    return out


def main(names):
    res = {}
    lons = np.arange(0, 360, 15.0)
    for nm in names:
        G = P.DIRS[nm]; res[nm] = {}
        p15 = P.push(G, lons, 15.0); st = strength(G, lons)
        print('\n== %s: %s' % (nm, P.LABEL[nm]))
        print('   longitude                  ' + ' '.join('%5.0f' % l for l in lons))
        print('   push at lift 8             ' + ' '.join('%5.2f' % v for v in P.push(G, lons, 8.0)))
        print('   push at lift 15            ' + ' '.join('%5.2f' % v for v in p15))
        print('   push at lift 25            ' + ' '.join('%5.2f' % v for v in P.push(G, lons, 25.0)))
        print('   weakest gain / d, lifts<50 ' + ' '.join('%5.2f' % v[0] for v in st))
        print('   ... at lift                ' + ' '.join('%5.0f' % v[1] for v in st))
        res[nm]['pattern'] = dict(lon=lons.tolist(), push8=P.push(G, lons, 8.0).tolist(), push15=p15.tolist(), push25=P.push(G, lons, 25.0).tolist(), weakest=[v[0] for v in st], weakest_at=[v[1] for v in st])
        for key, cs in P.CASES.items():
            L = P.law(G, cs); res[nm][key] = L
            print('   %-9s d %.3f lon %5.1f | law A: push*d at 8/15/25 = %.2f %.2f %.2f | law B: weakest gain %.2f at lift %.0f%s'
                  % (key, cs['d'], cs['lon'], L['A'][0], L['A'][1], L['A'][2], L['B'], L['B_at'], '' if L['first_below'] is None else ' (below 1 from lift %.0f)' % L['first_below']))
    return res


if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else ['one', 'v1', 'v2', 'm4', 'm4b', 'm6', 'cones', 'tri']
    res = main(names)
    fn = os.path.join(HERE, 'cache', 'law.json'); old = json.load(open(fn)) if os.path.exists(fn) else {}
    old.update(res); json.dump(old, open(fn, 'w'), indent=1)
