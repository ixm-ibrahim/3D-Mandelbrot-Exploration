"""Round 25, section 'torus': the rules of this corner, ready to load. NONE of them passes the user's tests.

    import sys; sys.path.insert(0, 'out/r25/torus'); import best
    r = best.rule()        # 'ring3': the only new rule of this corner that is exact on the flat plane AND has
                           # bodies off the flat picture. It FAILS: shells and crumbs, no round bodies (NOTES.md).
    b = best.book()        # exact on the flat plane, nothing at all off it (no escape, no pull to the plane)
    h = best.hopf()        # the quaternion (Hopf) doughnut object; its flat cut is NOT the flat picture

ring3 in one line: with zeta = rho + i z in the upright half-plane of the point (rho = distance from the upright
axis) and d = (zeta - 1) / (zeta + 1) = r e^(i sigma), send sigma -> 3 sigma (r and the longitude kept), go back
to x, y, z, then apply the one-plane square.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torus as T


def rule():
    return T.RULES['ring3']()


def book():
    return T.RULES['book']()


def hopf():
    return T.RULES['hopf']()


if __name__ == '__main__':
    import mem as M
    for r in (rule(), book(), hopf()):
        print(r.name, M.flat_check(r, n=20000, steps=60))
