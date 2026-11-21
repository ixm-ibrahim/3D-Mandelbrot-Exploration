"""c = -1: is the row of bodies fused along the x-axis? Area of the cut across the x-axis at the touching point
(x = -0.618034) as a share of the area of the cut through the middle body (x = 0), 60 steps, 300 x 300 points.
    python out/r23/rabbit/necks.py <rule keys joined by commas>
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import doors as D
M = D.M
if __name__ == '__main__':
    B = D.SETS['basilica']
    for k in sys.argv[1].split(','):
        r = D.get(k)
        a0 = (M.cut_across(r, 0.0, 300, 60, c=B, L=1.3) >= 60).mean() * 2.6 * 2.6
        a1 = (M.cut_across(r, -0.6180339887, 300, 60, c=B, L=1.3) >= 60).mean() * 2.6 * 2.6
        n = M.cut_across(r, 0.0, 300, 60, c=B, L=1.3) >= 60
        up, dn = n[:150].sum(), n[150:].sum()
        print('%-9s middle cut %.3f, cut at the touching point %.4f = %.1f %% of it; middle cut above / below the flat plane %.2f' % (k, a0, a1, 100 * a1 / max(a0, 1e-12), up / max(dn, 1))); sys.stdout.flush()
