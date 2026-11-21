"""Quick screen of a rule as a map of the sphere of directions (no iteration, seconds per rule).
    python out/r17/blends/screen.py <rule> [more]
Prints: length squared, plane z = 0 and y = 0 against complex squaring, a jump test, and on 400,000 random
directions: how many times the sphere is covered (degree), the share of directions that land mirror-reversed
(folded), and the sideways stretch (the flat rule gives 2 on the unit sphere): median, 99th per cent, largest,
and the worst ratio of the two sideways stretches (1 = keeps angles)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))


def screen(name, F, n=400000, h=1e-6, seed=3):
    rng = np.random.default_rng(seed)
    P = rng.normal(size=(20000, 3))
    X, Y, Z = F(P[:, 0], P[:, 1], P[:, 2])
    ln = np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (P ** 2).sum(1)).max()
    X, Y, Z = F(P[:, 0], P[:, 1], 0 * P[:, 2])
    pz = max(np.abs(X - (P[:, 0] ** 2 - P[:, 1] ** 2)).max(), np.abs(Y - 2 * P[:, 0] * P[:, 1]).max(), np.abs(Z).max())
    X, Y, Z = F(P[:, 0], 0 * P[:, 1], P[:, 2])
    py = max(np.abs(X - (P[:, 0] ** 2 - P[:, 2] ** 2)).max(), np.abs(Z - 2 * P[:, 0] * P[:, 2]).max(), np.abs(Y).max())
    # jump test: close pairs
    jumps = []
    for st in (1e-4, 1e-5, 1e-6):
        A = rng.normal(size=(200000, 3)); A /= np.linalg.norm(A, axis=1)[:, None]
        D = rng.normal(size=(200000, 3)); D /= np.linalg.norm(D, axis=1)[:, None]
        B = A + st * D
        fa = np.stack(F(A[:, 0], A[:, 1], A[:, 2]), 1); fb = np.stack(F(B[:, 0], B[:, 1], B[:, 2]), 1)
        jumps.append(float(np.linalg.norm(fa - fb, axis=1).max()))
    # the map of directions
    V = rng.normal(size=(n, 3)); V /= np.linalg.norm(V, axis=1)[:, None]
    a = np.cross(V, np.array([0.3, 0.5, 0.8])); a /= np.linalg.norm(a, axis=1)[:, None]; b = np.cross(V, a)
    def g(Q):
        Q = Q / np.linalg.norm(Q, axis=1)[:, None]
        W = np.stack(F(Q[:, 0], Q[:, 1], Q[:, 2]), 1)
        return W / np.linalg.norm(W, axis=1)[:, None]
    W0 = g(V); da = (g(V + h * a) - g(V - h * a)) / (2 * h); db = (g(V + h * b) - g(V - h * b)) / (2 * h)
    det = np.einsum('ij,ij->i', W0, np.cross(da, db))          # signed area factor (outward normals)
    M = np.stack([da, db], 2)                                   # 3 x 2
    sv = np.linalg.svd(M, compute_uv=False)                     # two sideways stretches
    s1, s2 = sv[:, 0], sv[:, 1]
    ok = np.isfinite(det) & np.isfinite(s1)
    deg = float(det[ok].mean()); fold = float((det[ok] < 0).mean())
    ratio = s1[ok] / np.maximum(s2[ok], 1e-12)
    out = dict(length=ln, plane_z=pz, plane_y=py, jumps=jumps, degree=deg, folded_pct=100 * fold,
               stretch_median=float(np.median(s1[ok])), stretch_99=float(np.percentile(s1[ok], 99)), stretch_max=float(s1[ok].max()),
               ratio_median=float(np.median(ratio)), ratio_99=float(np.percentile(ratio, 99)),
               angles_kept_pct=float(100 * (ratio < 1.25).mean()))
    print('%-10s length %.0e | z=0 exact %.0e | y=0 exact %.0e | jumps %.0e %.0e %.0e | covers the sphere %.2f times | folded %.1f %% | '
          'stretch med %.2f, 99%% %.2f, max %.1f | stretch ratio med %.2f, 99%% %.1f | angles kept (ratio < 1.25) on %.0f %%'
          % (name, ln, pz, py, *jumps, deg, 100 * fold, out['stretch_median'], out['stretch_99'], out['stretch_max'],
             out['ratio_median'], out['ratio_99'], out['angles_kept_pct']), flush=True)
    return out


if __name__ == '__main__':
    import rules as R
    for nm in sys.argv[1:]:
        screen(nm, R.get(nm))
