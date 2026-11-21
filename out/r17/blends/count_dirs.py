"""Which directions does a rule send to the -x direction (where buds grow: in the flat picture these are +-y) and
which to the +x direction (where the long arms are: in the flat picture +-x)?  3,000,000 random directions; those
whose answer lies within 1.5 degrees of the target are grouped (groups further apart than 12 degrees).
    python out/r17/blends/count_dirs.py rule ..."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R
rng = np.random.default_rng(11); V = rng.normal(size=(3000000, 3)); V /= np.linalg.norm(V, axis=1)[:, None]

def groups(P):
    out = []
    P = list(P)
    while P:
        c = P[0]; A = np.array(P); d = A @ c
        near = d > np.cos(np.radians(12.0)); out.append((A[near].mean(0), int(near.sum()))); P = [p for p, n in zip(P, near) if not n]
    return out

def name(c):
    c = c / np.linalg.norm(c)
    lon = np.degrees(np.arctan2(c[2], c[1])); col = np.degrees(np.arccos(np.clip(c[0], -1, 1)))
    return '(%.0f from +x, %.0f round)' % (col, lon)

for nm in sys.argv[1:]:
    F = R.get(nm); X, Y, Z = F(V[:, 0], V[:, 1], V[:, 2]); n = np.sqrt(X * X + Y * Y + Z * Z); X = X / n
    line = '%-9s' % nm
    for tag, sel in (('to -x', X < -np.cos(np.radians(1.5))), ('to +x', X > np.cos(np.radians(1.5)))):
        g = groups(V[sel][:4000])
        g = [q for q in g if q[1] >= 3]
        line += '  %s: %d groups %s' % (tag, len(g), ' '.join(name(q[0]) for q in g[:10]))
    print(line, flush=True)
