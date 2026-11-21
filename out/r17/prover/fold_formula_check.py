"""Prover, proposal C: the formula only. Checks by numbers that the 'one-plane rule with its steep answers folded back by a
sphere inversion' has the properties claimed for it in the report. No Julia set and no Mandelbrot solid is drawn here.

    U = P(v) / |v|^2                       (direction of the one-plane answer)
    q+ = (s, 0, 1 + s),  q- = (s, 0, -(1 + s)),   0 < s < 1
    if U . q+ > 1:  U <- q+ + (|q+|^2 - 1) (U - q+) / |U - q+|^2      (same with q-)
    F(v) = |v|^2 U
    python out/r17/prover/fold_formula_check.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import scout as S

def capfold(s):
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        X, Y, Z = S.oneplane(x, y, z)
        d = np.maximum(r2, 1e-300); U = np.stack([X / d, Y / d, Z / d])
        V = U
        for sg in (1.0, -1.0):                      # each answer is folded at most once: both caps are tested on the one-plane answer U
            q = np.array([s, 0.0, sg * (1 + s)]).reshape(3, *([1] * (U.ndim - 1)))
            inside = (U * q).sum(0) > 1
            W = U - q; k = (2 * s * s + 2 * s) / np.maximum((W * W).sum(0), 1e-300)
            V = np.where(inside, q + k * W, V)
        return r2 * V[0], r2 * V[1], r2 * V[2]
    return F

rng = np.random.default_rng(4)
for s in (0.15, 0.5, 0.8):
    F = capfold(s); P = rng.normal(size=(3, 200000))
    X, Y, Z = F(*P); ln = np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (P ** 2).sum(0)).max()
    X0, Y0, Z0 = F(P[0], P[1], 0 * P[2]); pl = max(np.abs(X0 - (P[0] ** 2 - P[1] ** 2)).max(), np.abs(Y0 - 2 * P[0] * P[1]).max(), np.abs(Z0).max())
    A = P / np.linalg.norm(P, axis=0); js = []
    for h in (1e-4, 1e-5, 1e-6):
        B = A + h * rng.normal(size=A.shape); js.append(np.linalg.norm(np.stack(F(*A)) - np.stack(F(*B)), axis=0).max())
    fa = np.stack(F(*A)); mz = np.stack(F(A[0], A[1], -A[2])); my = np.stack(F(A[0], -A[1], A[2]))
    t = np.linspace(-1.5, 1.5, 7); up = np.stack(F(0 * t, 0 * t, t)); fr = np.stack(F(0 * t, t, 0 * t))
    folded = np.mean([(np.stack(S.oneplane(*A)) * np.array([s, 0, sg * (1 + s)])[:, None]).sum(0) > 1 for sg in (1, -1)]) * 2
    print('s = %.1f: length squared to %.1e | flat plane exact to %.1e | largest jump at steps 1e-4, 1e-5, 1e-6: %.1e %.1e %.1e | mirror z %.1e, mirror y %.1e'
          % (s, ln, pl, js[0], js[1], js[2], np.abs(mz - fa * np.array([1, 1, -1])[:, None]).max(), np.abs(my - fa * np.array([1, -1, 1])[:, None]).max()))
    print('         straight up (0, 0, t) goes to (-t^2, 0, 0): error %.1e ; straight front (0, t, 0) goes to (-t^2, 0, 0): error %.1e ; share of directions that get folded: %.1f %%'
          % (np.abs(up - np.stack([-t * t, 0 * t, 0 * t])).max(), np.abs(fr - np.stack([-t * t, 0 * t, 0 * t])).max(), 100 * folded))
