"""Siegel disc (c = -0.390541 - 0.586788 i): does a band give it a body (claim W6)?
1. thickness: how far straight up from the disc's centre (the resting point, 0.338 from the x-axis) the solid reaches, at 80 and 300 steps
2. the solid stays: volume at 20, 40, 60, 80 steps (129 points a side, the panel's own grid)
python siegel.py <rule> ..."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R, bench as B
c = (-0.390541, -0.586788, 0.0); cc = complex(c[0], c[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2
print('resting point', al, 'distance from the x-axis %.3f' % abs(al.imag))
p = os.path.join(HERE, 'siegel.json'); out = json.load(open(p)) if os.path.exists(p) else {}
for nm in sys.argv[1:]:
    F = R.get(nm); z = np.linspace(0, 0.6, 6001)[1:]; res = {}
    for steps in (80, 300):
        ins, _ = B.inside(F, np.full_like(z, al.real), np.full_like(z, al.imag), z, c=c, steps=steps)
        o = np.flatnonzero(~ins); res['reach_%d' % steps] = float(z[o[0] - 1]) if o.size and o[0] > 0 else (0.0 if o.size else 0.6)
        res['filled_%d' % steps] = float(ins.mean() * 0.6)
    vols = []
    for steps in (20, 40, 60, 80):
        v = B.volume(F, 129, L=1.45, c=c, steps=steps); vols.append(float(v.mean() * 2.9 ** 3))
    res['volumes'] = vols; res['stays_pct'] = 100 * vols[3] / max(vols[1], 1e-12); out[nm] = res
    print('%-9s reaches %.3f straight up from the centre at 80 steps, %.3f at 300 (total length inside on that line: %.3f, %.3f) | volume at 20, 40, 60, 80 steps: %s | stays %.0f %%' % (
        nm, res['reach_80'], res['reach_300'], res['filled_80'], res['filled_300'], ' '.join('%.3f' % v for v in vols), res['stays_pct']), flush=True)
    json.dump(out, open(p, 'w'), indent=1)
