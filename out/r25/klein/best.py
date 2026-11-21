"""Round 25, section klein: the best object of this corner, and the one rule of the usual kind that it offers.

    import sys; sys.path.insert(0, 'out/r25/klein'); import best
    r = best.rule()                 # the pearl tree, Gaussian integers (a GROUP picture; it has no c: draw it with c = (0, 0, 0))
    r = best.rule('eisen')          # the same with Eisenstein integers (six-fold instead of four-fold)
    r = best.rule('line')           # the flat tree blown up (buds only round the flat picture)
    r = best.rule(t=1.2, k2=1.0)    # its two dials: t >= 1 (size of the attached bodies), k2 (width of the middle ball)
    r2 = best.repaired()            # the paper's rule re-spaced so that the flat cut is exact (a rule "square, add c")

    M.solid(best.rule(), (0, 0, 0), w, h, nd, 14)          # 14 rounds are enough (tree.py check)
    M.flat_check(best.repaired())                          # 0, 0, 0, 0
    M.flat_check(best.rule()) is meaningless: the tree has no c. Its flat cut is the flat TREE exactly (tree.py check),
    and the flat tree is a cousin of the basilica, not the basilica (38.6% of the area gets the wrong verdict).

The pearl tree in one line (m = the point in the group's coordinates, see tree.py for the picture frame):
    repeat: if m is below the plane mz = 0 or above the plane mz = 2t: INSIDE. Shift m by the nearest whole number of
    the lattice. If |m| < 1: m -> m / |m|^2. Else if |m - (0, 0, 2t)| < 1: the same about (0, 0, 2t). Else: OUTSIDE.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tree as T
import repair as R


def rule(lattice='gauss', t=T.T0, k2=T.K2):
    return T.tree(lattice, t=t, k2=k2)


def repaired():
    return R.RULES['kfix']()


if __name__ == '__main__':
    import numpy as np
    import mem as M
    print('repaired paper rule, flat check:', M.flat_check(repaired(), n=20000, steps=60))
    rng = np.random.default_rng(1); q = rng.uniform(-1.5, 1.5, size=(3, 100000))
    print('pearl tree (Gaussian): share of the box inside: %.4f' % (M.stay(rule(), q[0], q[1], q[2], 0.0, 0.0, 0.0, 14) >= 14).mean())
