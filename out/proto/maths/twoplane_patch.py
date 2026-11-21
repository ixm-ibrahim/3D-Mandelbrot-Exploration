"""Referee's quick 'both planes exact' variant: radial layout followed by a slide along the
half circles through (0,+-1,0) so that the circle y=0 is also laid at constant speed
(face centre goes to 120 degrees in the x-z plane instead of the pole)."""
import numpy as np
import pillow as P
_f, _i = P.layout_fwd, P.layout_inv

def g(t):      return np.where(t <= np.pi / 2, (4.0 / 3) * t, (2.0 / 3) * t + np.pi / 3)
def ginv(t):   return np.where(t <= 2 * np.pi / 3, 0.75 * t, 1.5 * (t - np.pi / 3))

def slide(x, y, z, fn):
    tau = np.arctan2(z, x); c = np.hypot(x, z)
    t2 = fn(tau)
    return c * np.cos(t2), y, c * np.sin(t2)

def fwd(lA, lB, lC):
    return slide(*_f(lA, lB, lC), g)

def inv(x, y, z):
    return _i(*slide(x, y, z, ginv))

P.layout_fwd, P.layout_inv = fwd, inv
