"""The film on the necks, in seconds: basilica, the upright line through the touching point (-0.618034, 0, z), |z| < 0.2.
    python out/r19/foldpre/neckline.py <rule> [more]
Prints the length of that line that is still inside after 60 and 300 steps, on the upright plane itself (y = 0) and on
lines moved sideways by y = 0.001, 0.003, 0.01. One plane gives 0 everywhere. A film in the upright plane gives 0.4 at
y = 0 and falls to 0 a hair's breadth to the side; a real body gives a length that does not care about y."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import truth as T
import rules as R
X0 = -0.6180339887498949
z = np.linspace(-0.2, 0.2, 4001)
for nm in sys.argv[1:]:
    F = R.get(nm); out = []
    for steps in (60, 300):
        row = []
        for y in (0.0, 0.001, 0.003, 0.01):
            n = T.member(F, np.full_like(z, X0), np.full_like(z, y), z, (-1.0, 0.0, 0.0), steps)
            row.append(0.4 * float((n >= steps).mean()))
        out.append('%d steps: ' % steps + ', '.join('%.3f' % v for v in row))
    print('%-9s length inside at y = 0, 0.001, 0.003, 0.01 | ' % nm + ' | '.join(out), flush=True)
