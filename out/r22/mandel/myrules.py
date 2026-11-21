"""Round 22, section 'mandel': one control rule, made to test an explanation (it is NOT a candidate).

    import sys; sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r22/mandel'); import mem as M, myrules as R
    R.RULES[0]   'flip': the one-plane square, then mirrored in the flat page: (X, Y, Z) = (f (x^2 - y^2), f 2xy, -f 2rz)

Why: under the one-plane rule the lift of a tilted c is stretched at every step but never turned, so the lifts of all
steps add up. Mirroring after each squaring makes them alternate instead. For c in the flat page the two rules have
the same Julia sets (the mirror can be moved onto the start point), so nothing is gained for the Julia sets; the
only question asked of it is how wide the buds of its Mandelbrot solid are sideways (see extra.txt, section 2).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M


def _flip(x, y, z, st, k, cx, cy, cz):
    X, Y, Z = M.S.oneplane(x, y, z); return X, Y, -Z, st


RULES = [M.Rule('flip', 'control: the one-plane square, then mirrored in the flat page', _flip, init=lambda n: ())]


def get(name):
    return next(r for r in RULES if r.name == name)
