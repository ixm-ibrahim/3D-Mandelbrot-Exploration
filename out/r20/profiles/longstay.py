"""Does the nudged basilica's solid stay for many steps? Volume at 80, 300 and 1000 steps (97 points a side), bas_yz and bas_zy."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R, bench as B
for nm in sys.argv[1:]:
    F = R.get(nm); out = []
    for tag, c in (('bas_yz', (-1.0, 0.05, 0.03)), ('bas_zy', (-1.0, 0.03, 0.05))):
        vs = [float(B.volume(F, 97, L=1.7, c=c, steps=s).mean() * 3.4 ** 3) for s in (80, 300, 1000)]
        out.append('%s: %.3f, %.3f, %.3f' % (tag, *vs))
    print('%-9s volume at 80, 300, 1000 steps | ' % nm + ' | '.join(out), flush=True)
