"""Round 22, entry: what are the wings in the lab's picture of the Mandelbrot solid of "Along once, then one plane"?
  python out/r22/entry/wings.py -> wings.txt
Takes stops of the lab's picture (detest.log.json, Rough) whose own orbit leaves early, and follows the line of sight
through each with the library's rule (alongmem.c_wake1), narrowing the search on the place where the orbit stays longest."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M, myrules as J
o = json.load(open(os.path.join(HERE, 'detest.log.json'), encoding='utf-8'))
rule = J.get('alongmem.c_wake1'); one = M.bench('oneplane'); rep = []
def say(t):
    rep.append(t); print(t); sys.stdout.flush()
d = o['alongonce man 0']; ro = np.array(d['pos']); STEPS = 300
P = np.array([p for p in d['picks'] if p is not None])
n = M.stay(rule, P[:, 0], P[:, 1], P[:, 2], P[:, 0], P[:, 1], P[:, 2], 29, r2=4096.0)
n1 = M.stay(one, P[:, 0], P[:, 1], P[:, 2], P[:, 0], P[:, 1], P[:, 2], 29, r2=4096.0)
say('The lab\'s picture of the Mandelbrot solid of Along once (30 iterations, Rough): %d stops; at %d of them the stop point itself leaves before step 20' % (len(P), (n < 20).sum()))
say('(the same points under the one-plane rule: %d leave before step 20).' % (n1 < 20).sum())
say('Each line below: one such stop; the line of sight through it, searched with %d steps allowed; the window is narrowed 20 times at a go round the best place.' % STEPS)
for p in P[n < 20][::8][:8]:
    rd = (p - ro) / np.linalg.norm(p - ro); lo, hi = -0.02, 0.06; out = []
    for level in range(9):
        t = np.linspace(lo, hi, 20001); Q = p[None] + t[:, None] * rd[None]
        k = M.stay(rule, Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 0], Q[:, 1], Q[:, 2], STEPS, r2=4096.0)
        out.append('%.0e: %d' % (hi - lo, k.max()) + (' (%d places stay for good)' % (k >= STEPS).sum() if (k >= STEPS).any() else ''))
        if (k >= STEPS).sum() > 2000: break
        j = np.nonzero(k >= k.max())[0]; c0 = t[j].mean(); w2 = max((hi - lo) / 20, (t[j].max() - t[j].min()) * 2)
        if w2 >= hi - lo: break
        lo, hi = c0 - w2 / 2, c0 + w2 / 2
    k1 = M.stay(one, Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 0], Q[:, 1], Q[:, 2], STEPS, r2=4096.0)
    say('  stop (%.3f, %.3f, %.3f): longest stay in a window of width ... : %s | one-plane rule in the last window: %d steps at most' % (*p, '; '.join(out), k1.max()))
open(os.path.join(HERE, 'wings.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
