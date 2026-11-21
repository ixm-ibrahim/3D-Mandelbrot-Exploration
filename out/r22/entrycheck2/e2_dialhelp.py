"""Round 22, entrycheck second pass: the help text of Pulled plane's second dial says "Measured for the rabbit in
round 21: at 1 a third of the set is lost, at 0.5 the bodies fuse where they meet". Round 21's row for that
(out/r21/judge/dials.txt, 'evc005' against 'evc005e70') has the weight of c at 1, not at the lab's 16. Here: both.
  python out/r22/entrycheck2/e2_dialhelp.py -> dialhelp.txt"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J
SHEET = sys.modules['rules_sheet']
def evc(s, e, kc):
    st, ini = SHEET.evc(s, ease_c=e, ease=e, kc=kc); return M.Rule('v', 'v', st, ini)
rng = np.random.default_rng(77); N = 300000
x = rng.uniform(-1.8, 1.8, N); y = rng.uniform(-1.4, 1.4, N); z = rng.uniform(-1.4, 1.4, N)
out = []
for kc in (16.0, 1.0):
    row = {}
    for e in (0.7, 1.0, 0.85, 0.5):
        n = M.stay(evc(0.05, e, kc), x, y, z, *M.RABBIT, 200, r2=4096.0); row[e] = ((n >= 30).sum(), (n >= 80).sum(), (n >= 200).sum())
    b = row[0.7]
    for e in (0.7, 1.0, 0.85, 0.5):
        r = row[e]
        out.append('rabbit, third dial (weight of c) %g, second dial %.2f: stay 30 / 80 / 200 steps %d / %d / %d; at 200 steps %.0f %% of what the second dial at 0.7 keeps' % (kc, e, r[0], r[1], r[2], 100.0 * r[2] / b[2]))
        print(out[-1]); sys.stdout.flush()
open(os.path.join(HERE, 'dialhelp.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
