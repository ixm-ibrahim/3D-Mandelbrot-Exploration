"""Section "vahlen", round 25: the least bad rule of this corner. It is NOT a winner: read NOTES.md.

    import sys; sys.path.insert(0, 'out/r25/vahlen'); import best; r = best.rule()

rule()        'holo': square(x, y, z) = (x^2 - y^2, 2xy, 2 z |v|).  The spinor of the point, split into its two
              complex halves about the upright axis, with each half squared. The only quadratic spinor square that
              needs no phase to be chosen and is exact on the flat plane. Clean, flatter than one plane, and its buds
              sit only round the flat picture (test 4 fails).
carried()     'spin-V': the quaternion square of the spinor with the phase carried along the orbit. Exact; equal to
              the Lathe for c on the x-axis; no body at all off the flat plane for any other c that was tried.
lathe(beta)   every one-term quaternion product square: the Lathe about the flat axis at beta degrees.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V


def rule():
    return V.R_holo()


def carried(start='V'):
    return V.spin(start)


def lathe(beta=0.0):
    return V.R_lathe_b(beta)


if __name__ == '__main__':
    r = rule(); print(r.name, '|', r.label); print(V.M.flat_check(r, n=20000, steps=60))
