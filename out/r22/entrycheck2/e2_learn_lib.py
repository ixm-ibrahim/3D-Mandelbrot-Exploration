"""Round 22, entrycheck second pass: the orbit the Learn tab shows after "Next step" (taken off the page by
e2_defects.js, step 5) against the LIBRARY's rule, stepped here one squaring at a time (power 2 runs only).
  python out/r22/entrycheck2/e2_learn_lib.py -> learn-lib.txt
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

SHEET = sys.modules['rules_sheet']
v = json.load(open(os.path.join(HERE, 'defects.log.json'), encoding='utf-8'))
o = json.loads(v[4])
out = []
for r in o['runs']:
    if r['n'] != 2:
        continue
    if r['id'] == 'alongonce':
        rule = J.get('alongmem.c_wake1')
    elif r['dials']:
        d = r['dials']; st_m, ini_m = SHEET.evc(d['hold'], ease_c=d['ease'], ease=d['ease'], kc=float(d['cpull'])); rule = M.Rule('moved', 'evc moved', st_m, ini_m)
    else:
        rule = J.get('sheet.evc005e70k16')
    orb = np.array(r['orbit'], float); c = np.array(r['c'], float)
    z = orb[0].copy(); st = rule.init(1); k = 0; worst = 0.0; lib = [z.copy()]
    for i in range(1, len(orb)):
        if not z.any():           # a squaring of the exact origin counts for nothing (the library starts the orbit of 0 at c with k = 0)
            z = c.copy()
        else:
            X, Y, Z, st = rule.step(np.array([z[0]]), np.array([z[1]]), np.array([z[2]]), st, k, np.array([c[0]]), np.array([c[1]]), np.array([c[2]]))
            z = np.array([X[0], Y[0], Z[0]]) + c; k += 1
        lib.append(z.copy()); worst = max(worst, float(np.abs(z - orb[i]).max()))
    out.append('%-12s start %s, c %s, dials %s: %d steps; Learn against the library: largest difference %.1e; second point Learn %s, library %s' % (
        r['id'], r['z0'], r['c'], r['dials'], len(orb) - 1, worst, np.round(orb[2], 3).tolist(), np.round(lib[2], 3).tolist()))
    print(out[-1])
open(os.path.join(HERE, 'learn-lib.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
