"""How often the sideways part of the answer turns when the point goes once round the negative x-axis
(claim C2: 1 + 4k for rules exact on both planes), and how short the sideways part gets on the way.
    python out/r17/blends/turncount.py rule ..."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R
for nm in sys.argv[1:]:
    F = R.get(nm); out = []
    for eps in (0.2, 0.05, 0.01):
        phi = np.linspace(0, 2 * np.pi, 400001)
        X, Y, Z = F(np.full_like(phi, -1.0), eps * np.cos(phi), eps * np.sin(phi))
        ang = np.unwrap(np.arctan2(Z, Y)); s = np.hypot(Y, Z)
        out.append('circle %.2f: turns %+.2f, sideways part between %.4f and %.4f of the flat value' % (eps, (ang[-1] - ang[0]) / (2 * np.pi), s.min() / (2 * eps), s.max() / (2 * eps)))
    print('%-9s ' % nm + ' | '.join(out), flush=True)
