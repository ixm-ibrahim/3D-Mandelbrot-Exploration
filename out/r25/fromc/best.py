"""Round 25, section "fromc": the nearest thing this corner found. It does NOT pass the user's tests (see NOTES.md).

    import sys; sys.path.insert(0, 'out/r25/fromc'); import best
    r = best.rule()            # 'twin_tri'   (a rule of out/r21/lib/mem.py: M.stay(r, x, y, z, cx, cy, cz, steps), ...)
    r = best.rule('face_tri')  # the same without the half-turn fold (lopsided)
    r = best.rule('axis_once') # "along" about the line 0 - meeting point at the first step, then one plane

twin_tri in two lines (a = the meeting point of c = (1 - sqrt(1 - 4c)) / 2, read from the flat part of c):
    u  = direction of v, turned half-way round the upright axis if it lies on the far side from a
    F(v) = |v|^2 * Rot(2 arg a) T( Rot(-arg a) u ),   then + c
T is the direction map "times 2 on two flat triangles" of out/r24/me/tri.py (even spacing, three corners on the flat
circle, laid over each direction 4 times); the turn puts one corner on the meeting point. Within 28 degrees of that
corner T is exactly the quaternion square about the line 0 - a.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R


def rule(name='twin_tri'):
    return R.get(name)
