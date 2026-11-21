"""Round 25, section "wall": the rules of this section, one line each to load.

    import sys; sys.path.insert(0, 'out/r25/wall'); import best
    r = best.rule()            # the one worth looking at: evenly spaced bulbs for the CUBE, z -> z^3 + c  (not the square!)
    r = best.rule_square()     # the same construction for z^2 + c: lopsided by force (passes M.flat_check)
    r = best.rule_pole()       # "three times round the unit circle, then one plane": the fifth thing W-a had missed (z^2 + c)
    r = best.rule_zoo()        # z^2 + c written as z (z + c / z) with the one-plane product (z^2 + c, looks at c)
    best.flat_check_cube(r)    # the flat check for z^3 + c (M.flat_check tests the square and does not apply to rule())

Every rule is a rule of out/r21/lib/mem.py (M.stay, M.cut_axis, M.solid, M.julia_sheet work on it).

rule(): directions <-> a square pillow (x, y in [0, 1), (x, y) glued to (-x, -y); the flat circle is the belt y = 1/4,
x = longitude / 360); cube(x, y) = (3 x, 3 y + 1/2); length cubed. Layout and reasons: pil.py.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wall as W
import pil as PL
M = W.M


def rule(band=0.0):
    return PL.rule_pillow(3, True, band)


def rule_square():
    return PL.rule_lop(2)


def rule_pole():
    return W.RULES['ws']()


def rule_zoo():
    return W.RULES['zooA']()


CUBE_SETS = [('c = i', (0.0, 1.0, 0.0)), ('c = 0.5576 + 0.5403i', (0.5575728, 0.5403468, 0.0))]


def flat_check_cube(r=None, n=20000, steps=60, seed=3):
    """verdicts on the flat plane that differ from the true orbit of z^3 + c (must be 0)."""
    r = r or rule(); rng = np.random.default_rng(seed); out = {}
    for nm, c in CUBE_SETS + [('c = 0.3', (0.3, 0.0, 0.0)), ('c = 0.59i', (0.0, 0.59, 0.0))]:
        zr, zi = rng.uniform(-1.5, 1.5, n), rng.uniform(-1.5, 1.5, n)
        a = M.stay(r, zr, zi, np.zeros(n), c[0], c[1], 0.0, steps) >= steps; b = PL.flat_stay_n(zr, zi, c[0], c[1], steps) >= steps
        out[nm] = int((a != b).sum())
    cr, ci = rng.uniform(-1.3, 1.3, n), rng.uniform(-1.6, 1.6, n)       # the cube's own Mandelbrot set
    a = M.mandel(r, cr, ci, np.zeros(n), steps) >= steps; b = PL.flat_stay_n(cr, ci, cr, ci, steps) >= steps
    out['mandelbrot of the cube'] = int((a != b).sum()); out['of'] = n
    return out


if __name__ == '__main__':
    print('rule()         cube, flat check against z^3 + c:', flat_check_cube())
    print('rule_square()  flat check:', M.flat_check(rule_square(), n=20000, steps=60))
    print('rule_pole()    flat check:', M.flat_check(rule_pole(), n=20000, steps=60))
    print('rule_zoo()     flat check:', M.flat_check(rule_zoo(), n=20000, steps=60))
