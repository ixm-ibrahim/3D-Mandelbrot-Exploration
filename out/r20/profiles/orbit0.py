"""The panel's first question for a c off the planes: does the orbit of 0 stay bounded (3,000 steps)? One orbit per rule and c.
Also a lift scan: c = (-1, 0, h) and c = (-1, h, h): the largest h (step 0.005, up to 0.2) for which the orbit of 0 stays."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R, bench as B
CS = dict(bas_yz=(-1.0, 0.05, 0.03), bas_zy=(-1.0, 0.03, 0.05), sm_yz=(-0.75, 0.01, 0.02), rab_up=(-0.122561, 0.744862, 0.015))
def leaves(F, c, n=3000):
    v = np.zeros(3); R2 = (B.resc(c) + 1e-9) ** 2
    for k in range(n):
        X, Y, Z = F(np.array([v[0]]), np.array([v[1]]), np.array([v[2]])); v = np.array([X[0] + c[0], Y[0] + c[1], Z[0] + c[2]])
        if v @ v > R2 or not np.all(np.isfinite(v)):
            return k + 1
    return 0
for nm in sys.argv[1:]:
    F = R.get(nm); cells = []
    for tag, c in CS.items():
        k = leaves(F, c); cells.append('%s: %s' % (tag, 'stays' if k == 0 else 'leaves at step %d' % k))
    def scan(make):
        best = 0.0
        for h in np.arange(0.005, 0.2001, 0.005):
            if leaves(F, make(h), 600) == 0:
                best = h
            else:
                break
        return best
    print('%-9s %s | basilica lifted straight up, largest lift that stays: %.3f; lifted along y and z together: %.3f' % (nm, ', '.join(cells), scan(lambda h: (-1.0, 0.0, h)), scan(lambda h: (-1.0, h, h))), flush=True)
