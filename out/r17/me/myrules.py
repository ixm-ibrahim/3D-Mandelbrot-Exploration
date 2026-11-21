"""Orchestrator's own trial rules (prefix m_). Loaded by the bench's registry hook.
m_cap<s>: the prover's proposal C. The one-plane answer, with answers that point too steeply up or down folded back
by a sphere inversion (the paper's own tool) that carries straight-up to straight-back. Each piece keeps angles on
the sphere of directions; the pieces meet along a crease (no tear). Flat plane exact."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import scout as S


def capfold(s, tilt=None):
    """tilt None: cap centres (s, 0, +-(1 + s)) (straight up goes to straight back)."""
    def F(x, y, z):
        x, y, z = (np.asarray(a, float) for a in (x, y, z))
        r2 = x * x + y * y + z * z
        X, Y, Z = S.oneplane(x, y, z)
        d = np.maximum(r2, 1e-300); U = np.stack([X / d, Y / d, Z / d])
        V = U
        for sg in (1.0, -1.0):
            q = np.array([s, 0.0, sg * (1 + s)]).reshape(3, *([1] * (U.ndim - 1)))
            inside = (U * q).sum(0) > 1
            W = U - q; k = (2 * s * s + 2 * s) / np.maximum((W * W).sum(0), 1e-300)
            V = np.where(inside, q + k * W, V)
        return r2 * V[0], r2 * V[1], r2 * V[2]
    return F


RULES = {
    'm_cap15': (capfold(0.15), 'One plane, steep answers folded back (s = 0.15)', ''),
    'm_cap30': (capfold(0.30), 'One plane, steep answers folded back (s = 0.30)', ''),
    'm_cap50': (capfold(0.50), 'One plane, steep answers folded back (s = 0.50)', ''),
    'm_cap80': (capfold(0.80), 'One plane, steep answers folded back (s = 0.80)', ''),
}
