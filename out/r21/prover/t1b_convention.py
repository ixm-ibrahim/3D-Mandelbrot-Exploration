"""How much can a convention at undefined points matter?  (NOTES.md, part 1, S4)

    python out/r21/prover/t1b_convention.py  ->  out/r21/prover/t1b_convention.txt

The point's own sheet is undefined ON the x-axis.  A convention with a tolerance: "within the distance tau of the
x-axis the point has no sheet of its own; use the flat page there".  tau = 0 is the convention at the undefined
points only.  Two recipes get this convention:
   own_tol:    every point squared about its own sheet (the lathe), or about the flat page when it has none.
   delay_tol:  every point squared about the sheet of the last earlier point that had one; while there is none yet,
               about its own sheet, and if it has none either, about the flat page.
The share of test points whose verdict changes when c is turned round the x-axis measures how far from spun the solid is.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R


def own_tol(tau):
    def f(x, y, z, st, k, cx, cy, cz):
        o1, o2, has = R.own_sheet(y, z); far = np.hypot(y, z) > tau
        return (*M.sq_about(x, y, z, np.where(far, o1, 1.0), np.where(far, o2, 0.0)), st)
    return f


def delay_tol(tau):
    def f(x, y, z, st, k, cx, cy, cz):
        u1, u2, d = st; o1, o2, has = R.own_sheet(y, z); far = np.hypot(y, z) > tau
        o1, o2 = np.where(far, o1, 1.0), np.where(far, o2, 0.0)                    # no sheet of its own: the flat page
        a1, a2 = np.where(d > 0, u1, o1), np.where(d > 0, u2, o2)
        X, Y, Z = M.sq_about(x, y, z, a1, a2)
        return X, Y, Z, (np.where(far, o1, u1), np.where(far, o2, u2), np.maximum(d, far))
    return f


def main():
    np.seterr(all='ignore'); out = []
    def say(t):
        print(t); out.append(t)
    say('share of 60,000 test points whose verdict changes when c is turned by a random angle round the x-axis (40 steps)')
    say('%-8s %12s %12s' % ('tau', 'own_tol', 'delay_tol'))
    for tau in (0.3, 0.1, 0.03, 0.01, 0.001, 0.0):
        a = M.spun_check(M.Rule('a', '', own_tol(tau)), n=60000)['mandel_differ']
        b = M.spun_check(M.Rule('b', '', delay_tol(tau), R.NOSHEET), n=60000)['mandel_differ']
        say('%-8g %11.3f%% %11.3f%%' % (tau, 100 * a, 100 * b))
    say("(delay at tau = 0 is 'delay_cov': what is left there is rounding on a knife edge, see t2_knife.txt, not the convention)")
    open(os.path.join(HERE, 't1b_convention.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
