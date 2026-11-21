"""Is the wedge round a copy plane an exact turned copy of the wedge round the flat plane? (reasoned: yes inside the band)
Half-plane at 60 + d degrees against the half-plane at 180 + d degrees, 301 x 151 points, 60 steps, four sets."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import truth as T, rules as R
SETS = [('basilica', (-1.0, 0.0, 0.0)), ('rabbit', (-0.122561, 0.744862, 0.0)), ('siegel', (-0.390541, -0.586788, 0.0))]
x = np.linspace(-1.7, 1.7, 301); s = np.linspace(0.005, 1.7, 151); X, S = np.meshgrid(x, s)
for nm in sys.argv[1:]:
    F = R.get(nm); out = []
    for d in (4.0, 8.0, 12.0, 18.0):
        row = []
        for tag, c in SETS:
            a1 = np.radians(60 + d); a2 = np.radians(180 + d)
            m1 = T.member(F, X, S * np.cos(a1), S * np.sin(a1), c, 60) >= 60; m2 = T.member(F, X, S * np.cos(a2), S * np.sin(a2), c, 60) >= 60
            row.append('%d of %d' % (int((m1 ^ m2).sum()), int((m1 | m2).sum())))
        out.append('%g deg off the plane: %s' % (d, ', '.join(row)))
    print('%-7s points that differ (basilica, rabbit, siegel) | ' % nm + ' | '.join(out), flush=True)
