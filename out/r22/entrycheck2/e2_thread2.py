"""Round 22, entrycheck second pass: Pulled plane with a c in the plane y = 0 whose flat picture HAS an inside
(c = (-1, 0, 0.2), the flat c = -1 + 0.2i, inside the disc round -1), beside c = (-1, 0, 0.3) (flat c outside).
  python out/r22/entrycheck2/e2_thread2.py -> thread2.txt"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J
PP = J.get('sheet.evc005e70k16'); AO = J.get('alongmem.c_wake1')
rng = np.random.default_rng(5); N = 400000
x = rng.uniform(-1.8, 1.8, N); y = rng.uniform(-1.4, 1.4, N); z = rng.uniform(-1.4, 1.4, N)
out = []
for name, r in (('Pulled plane', PP), ('Along once', AO)):
    for c in ((-1.0, 0.0, 0.2), (-1.0, 0.0, 0.3), (-1.0, 0.2, 0.0)):
        n = M.stay(r, x, y, z, *c, 300, r2=4096.0)
        out.append('%-12s c = %s: of %d random points stay 40 / 80 / 300 steps: %d / %d / %d' % (name, c, N, (n >= 40).sum(), (n >= 80).sum(), (n >= 300).sum()))
        print(out[-1]); sys.stdout.flush()
open(os.path.join(HERE, 'thread2.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
