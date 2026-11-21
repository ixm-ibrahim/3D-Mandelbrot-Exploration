"""Rule checks in seconds: length squared, flat plane exact, both mirrors, half turn about the upright axis,
jumps at gaps 1e-3 (the cliff), 1e-4, 1e-5, 1e-6 over random close pairs AND pairs straddling the flat plane.
    python out/r19/rational/check.py rule ..."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R
rng = np.random.default_rng(5)
for nm in sys.argv[1:]:
    F = R.get(nm)
    P = rng.normal(size=(200000, 3))
    f = lambda Q: np.stack(F(Q[:, 0], Q[:, 1], Q[:, 2]), 1)
    A = f(P)
    ln = np.abs(np.linalg.norm(A, axis=1) - (P ** 2).sum(1)).max()
    Pz = P.copy(); Pz[:, 2] = 0; B = f(Pz)
    fl = max(np.abs(B[:, 0] - (P[:, 0] ** 2 - P[:, 1] ** 2)).max(), np.abs(B[:, 1] - 2 * P[:, 0] * P[:, 1]).max(), np.abs(B[:, 2]).max())
    my = np.abs(f(P * [1, -1, 1]) - A * [1, -1, 1]).max(); mz = np.abs(f(P * [1, 1, -1]) - A * [1, 1, -1]).max()
    ht = np.abs(f(P * [-1, -1, 1]) - A).max()
    fin = np.isfinite(A).all()
    row = []
    for gap in (1e-3, 1e-4, 1e-5, 1e-6):
        U = rng.normal(size=(400000, 3)); U /= np.linalg.norm(U, axis=1)[:, None]
        D = rng.normal(size=(400000, 3)); D /= np.linalg.norm(D, axis=1)[:, None]
        j1 = np.linalg.norm(f(U) - f(U + gap * D), axis=1).max()
        V = U.copy(); V[:, 2] = gap / 2; V2 = V.copy(); V2[:, 2] = -gap / 2
        j2 = np.linalg.norm(f(V) - f(V2), axis=1).max()
        row.append(max(j1, j2) / gap)
    print('%-8s finite %s | length %.0e | flat plane %.0e | mirror y %.0e, mirror z %.0e | half turn about upright %.1e | '
          'largest jump / gap at 1e-3, 1e-4, 1e-5, 1e-6: %.1f %.1f %.1f %.1f' % (nm, fin, ln, fl, my, mz, ht, *row), flush=True)
