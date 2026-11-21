"""Round 23 outside1: is an outside formula the same solid as one of ours?   python out/r23/outside1/compare.py
For pairs of rules: the share of the inside volume on which the two verdicts differ (c = -1 and the rabbit),
and for the three chosen formulas the inside share at 30 against 80 steps (leaks)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M, outrules as O

rng = np.random.default_rng(21); V = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(400000, 3))


def ins(rule, c, steps=40):
    with np.errstate(all='ignore'):
        return M.stay(rule, V[:, 0], V[:, 1], V[:, 2], c[0], c[1], c[2], steps) >= steps


def R(nm):
    return M.bench(nm) if nm in ('oneplane', 'twoplane', 'along') else O.get(nm)


for a, b in (('twoplane', 'sym2'), ('twoplane', 'sym3'), ('along', 'eiffie'), ('oneplane', 'cup1'), ('mb2', 'hopfcut'), ('twoplane', 'hyper'), ('quat3d', 'xeno_t'), ('quat3d', 'benesi')):
    for sn, c in (('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
        A, B = ins(R(a), c), ins(R(b), c)
        print('%-9s against %-8s %-7s inside %.4f and %.4f of the box; verdicts differ on %.4f of the box = %.1f %% of the larger inside'
              % (a, b, sn, A.mean(), B.mean(), (A != B).mean(), 100 * (A != B).mean() / max(A.mean(), B.mean(), 1e-12)), flush=True)
for nm in ('along', 'twoplane', 'sym2', 'eiffie', 'hyper', 'bristor', 'mb2', 'scator_ix'):
    for sn, c in (('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
        a30, a80 = ins(R(nm), c, 30).mean(), ins(R(nm), c, 80).mean()
        print('%-9s %-7s inside at 30 steps %.4f, at 80 steps %.4f (kept %.1f %%)' % (nm, sn, a30, a80, 100 * a80 / max(a30, 1e-12)), flush=True)
