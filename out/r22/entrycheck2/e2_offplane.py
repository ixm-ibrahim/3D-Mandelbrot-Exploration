"""Round 22, entrycheck second pass: the numbers the new sentences quote for a c out of the flat plane, measured again
with the library and another seed. 400,000 random start points in the box (-1.8..1.8) x (-1.4..1.4)^2, leaving = |v| >= 64.
  python out/r22/entrycheck2/e2_offplane.py -> offplane.txt
"""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

RULES = [('Along once', J.get('alongmem.c_wake1')), ('Pulled plane', J.get('sheet.evc005e70k16')), ('one plane', M.bench('oneplane'))]
a = math.radians(10)
CS = [('rabbit c turned 10 deg about the x-axis', (-0.122561, 0.744862 * math.cos(a), 0.744862 * math.sin(a))), ('c = (-1, 0, 0.3)', (-1.0, 0.0, 0.3))]
out = ['Random start points, seed 2211 (the first checker used another): how many of 400,000 stay 20 / 30 / 40 / 80 steps (leaving = |v| >= 64; the lab picture asks for 40)']
rng = np.random.default_rng(2211)
N = 400000
x = rng.uniform(-1.8, 1.8, N); y = rng.uniform(-1.4, 1.4, N); z = rng.uniform(-1.4, 1.4, N)
for cn, c in CS:
    for rn, r in RULES:
        n = M.stay(r, x, y, z, *c, 80, r2=4096.0)
        out.append('  %-42s %-13s %6d / %5d / %5d / %5d' % (cn, rn, (n >= 20).sum(), (n >= 30).sum(), (n >= 40).sum(), (n >= 80).sum()))
        print(out[-1]); sys.stdout.flush()
open(os.path.join(HERE, 'offplane.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
