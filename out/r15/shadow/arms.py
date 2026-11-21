"""Round 15B, shadow: where do the arms and spikes of the Mandelbrot solids stand? Point-by-point grid (numpy, 14 steps),
the cells of the solid that lie far from the plane z = 0: their distance from the plane y = 0."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extent as E
N = 140
out = []
for n, L in ((2, 2.0), (3, 1.4), (4, 2.1), (5, 2.1)):
    ax = (np.arange(N) + 0.5) / N * 2 * L - L
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing='ij')
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    m = E.inside(P, n); Q = P[m]
    far = np.abs(Q[:, 2]) > 0.7 * np.abs(Q[:, 2]).max()
    A = Q[far]
    out.append('power %d (grid %d^3, cell %.3f): solid z %.2f to %.2f; the %d cells further than %.2f from the plane z = 0: |y| from %.2f to %.2f (median %.2f), |x| from %.2f to %.2f (median %.2f); cells of the whole solid with |y| < one cell: %.1f %%' % (
        n, N, 2 * L / N, Q[:, 2].min(), Q[:, 2].max(), len(A), 0.7 * np.abs(Q[:, 2]).max(), np.abs(A[:, 1]).min(), np.abs(A[:, 1]).max(), np.median(np.abs(A[:, 1])),
        np.abs(A[:, 0]).min(), np.abs(A[:, 0]).max(), np.median(np.abs(A[:, 0])), 100 * (np.abs(Q[:, 1]) < 2 * L / N).mean()))
open(os.path.join(HERE, 'arms.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
