"""Share of directions folded (landing mirror-reversed) and the worst stretch ratio, for the fade of the cap into
the band, over its two radii and its pacing. 200,000 directions each; seconds."""
import os, sys, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('qr', os.path.join(HERE, 'myrules.py')); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
rng = np.random.default_rng(3); V = rng.normal(size=(200000, 3)); V /= np.linalg.norm(V, axis=1)[:, None]
a = np.cross(V, np.array([0.3, 0.5, 0.8])); a /= np.linalg.norm(a, axis=1)[:, None]; b = np.cross(V, a); h = 1e-6
def scr(F):
    def g(Q):
        Q = Q / np.linalg.norm(Q, axis=1)[:, None]; W = np.stack(F(Q[:, 0], Q[:, 1], Q[:, 2]), 1); return W / np.linalg.norm(W, axis=1)[:, None]
    W0 = g(V); da = (g(V + h * a) - g(V - h * a)) / (2 * h); db = (g(V + h * b) - g(V - h * b)) / (2 * h)
    det = np.einsum('ij,ij->i', W0, np.cross(da, db)); sv = np.linalg.svd(np.stack([da, db], 2), compute_uv=False)
    ratio = sv[:, 0] / np.maximum(sv[:, 1], 1e-12)
    return 100 * (det < 0).mean(), np.percentile(ratio, 99), 100 * (ratio < 1.25).mean(), sv[:, 0].max(), det.mean()
for d, beta in ((2, -M.B6), (2, +M.B6), (1, 0.268), (2, -0.0666)):
    n = d + 2; z = abs(beta) ** (1.0 / n)
    print('d = %d, beta = %+.4f: directions sent straight up sit at |w| = %.3f' % (d, beta, z))
    for r1 in (z * 1.03, z * 1.08, z * 1.15):
        for r0 in (0.93, 1.0):
            for pw in (0, n, 2 * n):
                f, r99, kept, smax, deg = scr(M.band(beta, d, r1, r0, pw))
                print('   cap to %.3f, band from %.2f, pacing %d: folded %.2f %%, stretch ratio 99%% %.1f, angles kept on %.0f %%, largest stretch %.1f, covers %.2f'
                      % (r1, r0, pw, f, r99, kept, smax, deg), flush=True)
