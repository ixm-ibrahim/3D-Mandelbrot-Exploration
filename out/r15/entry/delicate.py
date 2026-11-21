"""Round 15, entry: who is right beside the seams? The 6,000 crowded points of checks.js: the page's MATH.sqpillow
against pillow_ref.py as it stands (its halving for beta stops after 60 steps, about 1e-18, which is coarse where
beta itself is 1e-16, next to the plane y = 0), and against pillow_ref.py with the halving run to the last bit
(1,100 steps; nothing else changed). Reads out/r15/entry/checks-raw.json (written by run.py checks).
"""
import json, sys
import numpy as np
sys.path.insert(0, 'out/me/r15')
import pillow_ref as R0


def solve_beta_full(px, py):
    lo, hi = np.zeros_like(px), np.ones_like(px)
    for _ in range(1100):
        m = 0.5 * (lo + hi)
        g = m * (1 + m) ** 2 - 4 * px * px * m - py * py * (1 + m) ** 2
        lo = np.where(g < 0, m, lo); hi = np.where(g < 0, hi, m)
    return 0.5 * (lo + hi)


o = json.load(open('out/r15/entry/checks-raw.json', encoding='utf-8'))
for tag, a, b in (('20,000 points in a ball', 'P', 'F'), ('6,000 crowded points', 'Q', 'G')):
    Q = np.array(o['math'][a], float); G = np.array(o['math'][b], float)
    keep = R0.solve_beta
    W0 = R0.F(Q)
    R0.solve_beta = solve_beta_full
    W1 = R0.F(Q)
    R0.solve_beta = keep
    e0 = np.linalg.norm(G - W0, axis=1); e1 = np.linalg.norm(G - W1, axis=1)
    print(tag)
    print('  page against pillow_ref.py as it stands:           largest %.3e, 99.9 %% %.3e, median %.3e, over 1e-9: %d' % (e0.max(), np.quantile(e0, .999), np.median(e0), int((e0 > 1e-9).sum())))
    print('  page against pillow_ref.py, halving to the last bit: largest %.3e, 99.9 %% %.3e, median %.3e, over 1e-9: %d' % (e1.max(), np.quantile(e1, .999), np.median(e1), int((e1 > 1e-9).sum())))
    for i in np.argsort(-e1)[:4]:
        d = Q[i] / np.linalg.norm(Q[i])
        print('    worst: direction %s  page %s  reference %s  off %.2e' % (d.tolist(), G[i].tolist(), W1[i].tolist(), e1[i]))
