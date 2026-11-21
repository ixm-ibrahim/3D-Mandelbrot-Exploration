"""panel2's hair number by tile width: at which scale do the fins show? Tiles are 0.1, 0.02 and 0.004 wide (x the set's scale).
The half-planes at 30 and 90 degrees (the rule's own mirror planes, always clean) are left out so that every rule is counted on the same 8 - 1 = 7 half-planes.
python hairw.py <rule>:<set> ..."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r19', 'panel2'))
import hairnum as H
p = os.path.join(HERE, 'hairw.json'); out = json.load(open(p)) if os.path.exists(p) else {}
print('%-9s %-9s | %-34s | %-34s | %-34s' % ('rule', 'set', 'tile 0.1 wide: over / thin med / film med', 'tile 0.02 wide', 'tile 0.004 wide'))
for arg in sys.argv[1:]:
    rule, tag = arg.split(':'); rows = H.score_set(rule, tag)
    if rows is None:
        print(arg, 'no tiles'); continue
    rows = [r for r in rows if r['fins'] is not None and r['angle'] not in (30.0, 90.0)]
    cells = []; out[arg] = {}
    for q in (0, 1, 2):
        rq = [r for r in rows if r['q'] == q]
        over = sum(1 for r in rq if r['fins'] > H.T_FINS or r['film_pct'] > H.T_FILM)
        mt = float(np.median([r['fins'] for r in rq])); mf = float(np.median([r['film_pct'] for r in rq]))
        cells.append('%2d of %2d / %.2f / %4.1f %%' % (over, len(rq), mt, mf)); out[arg]['q%d' % q] = dict(over=over, tiles=len(rq), thin_median=mt, film_median=mf, thin_worst=max(r['fins'] for r in rq), film_worst=max(r['film_pct'] for r in rq))
    print('%-9s %-9s | %-34s | %-34s | %-34s' % (rule, tag, *cells), flush=True)
    json.dump(out, open(p, 'w'), indent=1)
