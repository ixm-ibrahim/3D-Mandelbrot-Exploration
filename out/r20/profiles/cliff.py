"""The cliff half way between the planes (the round-17 measure, at this family's own mid plane): two points on the unit
sphere a given gap apart, one each side of the half-plane at 30 degrees (k = 3) or 18 degrees (k = 5); the largest
distance between their answers. A gentle rule gives about 2 x gap; a tear stays large as the gap shrinks.
Also: the six bud directions (x = 0, on the planes) must be sent to -x, and the stretch there (all directions) must be 2."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R
rng = np.random.default_rng(11); n = 200000
th = np.arccos(rng.uniform(-1, 1, n)); x = np.cos(th); rho = np.sin(th)
gaps = [1e-1, 3e-2, 1e-2, 1e-3, 1e-6]
print('%-9s ' % 'rule' + ' '.join('gap %-8.0e' % g for g in gaps) + '  largest answer distance / gap at the three smallest;   bud direction at 60 deg (k=3) or 36 deg (k=5): sent to, stretch along x / round the axis')
for nm in sys.argv[1:]:
    F = R.get(nm); k = 5 if nm in ('m_w5', 'w_5b05') else 3; mid = np.pi / (2 * k); row = []
    for g in gaps:
        d = np.minimum(g / 2 / np.maximum(rho, 1e-12), mid)
        a = np.stack(F(x, rho * np.cos(mid - d), rho * np.sin(mid - d)), 1); b = np.stack(F(x, rho * np.cos(mid + d), rho * np.sin(mid + d)), 1)
        row.append(np.linalg.norm(a - b, axis=1).max())
    a0 = np.pi / k; v = np.array([0.0, np.cos(a0), np.sin(a0)]); h = 1e-6
    f = lambda p: np.array(F(*[np.array([t]) for t in p])).ravel()
    sx = np.linalg.norm(f(v + [h, 0, 0]) - f(v - [h, 0, 0])) / (2 * h)
    e = np.array([0.0, -np.sin(a0), np.cos(a0)]); sa = np.linalg.norm(f(v + h * e) - f(v - h * e)) / (2 * h)
    print('%-9s ' % nm + ' '.join('%-12.3g' % q for q in row) + '  %5.1f %5.1f %5.1f' % tuple(row[i] / gaps[i] for i in (2, 3, 4)) + '   (%.3f, %.3f, %.3f)  %.3f / %.3f' % (*f(v), sx, sa))
