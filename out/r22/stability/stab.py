"""Round 22, section 'stability': shared tools. The step of a fixed rule looked at through a magnifying glass.

    import stab as T
    F = T.rule('along')                 # the bare square (x, y, z) -> (X, Y, Z) of a bench rule, no c
    J = T.jac(F, x, y, z)               # the 3 x 3 matrix of the step at each point (shape (..., 3, 3)); adding c changes nothing
    s, det = T.stretch(J)               # the three stretches of a tiny ball (largest first) and the sign of the handedness
    T.category(s, det)                  # 0 keeps shapes, 1 squeezes a little, 2 squeezes hard, 3 turns inside out

Everything is central differences on float64 with h = 1e-6 (error about 1e-9 of the stretch)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R

RABBIT, SIEGEL = M.RABBIT, M.SIEGEL
BAS = (-1.0, 0.0, 0.0); MARCO = (-0.75, 0.0, 0.0)
NAMES = ['oneplane', 'along', 'lathe', 'away']
PLAIN = {'oneplane': 'Sphere inversions, one plane', 'along': 'Turning plane, along', 'lathe': 'Quaternion square (Lathe)', 'away': 'Turning plane, away'}


def rule(name):
    return R.get(name)


def jac(F, x, y, z, h=1e-6):
    x, y, z = (np.asarray(t, float) for t in np.broadcast_arrays(x, y, z))
    J = np.zeros(x.shape + (3, 3))
    for j, d in enumerate(((h, 0, 0), (0, h, 0), (0, 0, h))):
        a = F(x + d[0], y + d[1], z + d[2]); b = F(x - d[0], y - d[1], z - d[2])
        for i in range(3):
            J[..., i, j] = (a[i] - b[i]) / (2 * h)
    return J


def stretch(J):
    s = np.linalg.svd(J, compute_uv=False)
    return s, np.sign(np.linalg.det(J))


def ratio(s):
    return s[..., 0] / np.maximum(s[..., 2], 1e-300)


def category(s, det, lo=1.25, hi=3.0):
    """0 keeps shapes (a tiny ball comes out a ball: longest / shortest under lo), 1 squeezes (under hi), 2 squeezes hard, 3 inside out."""
    q = ratio(s); cat = np.where(q < lo, 0, np.where(q < hi, 1, 2))
    return np.where(det < 0, 3, cat)


def orbit_jac(F, x, y, z, c, steps):
    """Follow the orbit and multiply the matrices up. Returns the list of (point, running matrix) after 1..steps steps."""
    x, y, z = (np.array(t, float) for t in np.broadcast_arrays(x, y, z))
    A = np.broadcast_to(np.eye(3), x.shape + (3, 3)).copy(); out = []
    for _ in range(steps):
        J = jac(F, x, y, z); A = J @ A
        X, Y, Z = F(x, y, z); x, y, z = X + c[0], Y + c[1], Z + c[2]
        out.append(((x.copy(), y.copy(), z.copy()), A.copy()))
    return out


def turn_from_pages(y, z):
    """Degrees between the point's page (the plane through the x-axis that holds it) and the nearest of the four pages
    at 0, 45, 90, 135 degrees; and which of them it is (0 = flat or upright, 1 = one of the two diagonal pages)."""
    phi = np.degrees(np.arctan2(z, y)) % 45.0
    d = np.minimum(phi, 45.0 - phi)
    k = np.round(np.degrees(np.arctan2(z, y)) / 45.0).astype(int) % 2
    return d, k
