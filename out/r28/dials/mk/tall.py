"""Round 28, Track A, builder: how far the picture reaches from the middle line (for the start view and "Frame it").

  python out/r28/dials/mk/tall.py   -> out/r28/dials/logs/tall.txt

For each setting the picture's list of balls is made (kit28) and the largest of (distance of a ball's centre from the
middle line + its radius) is found, and which ball it is. Against the formula the start view uses for a smaller
second sphere: max(the neighbour's radius k^2 p / 200, the middle ball with the largest bud on its waist
k^2 / 2 + k^2 / (2 top - 1)).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kit28 as K

SET = [(1, 30), (1, 55.5556), (1, 80), (1, 90), (1, 97), (0.5, 30), (0.5, 60), (0.5, 100), (0.5, 120), (0.5, 150), (0.5, 180), (0.5, 195), (0.4, 125), (0.4, 240), (1 / 3, 150),
       (0.3, 300), (0.25, 200), (0.25, 300), (0.25, 380), (1 / 6, 300), (0.125, 400), (0.1, 500), (0.05, 1000), (0.2, 480)]
lines = ['second sphere, size, grid | reach of the chain | furthest from the middle line by the list (the ball: at x, radius) | the formula | list - formula']
worst = 0.0; n = 0
for rho, p in SET:
    for g in (0, 1):
        top = 1 + 100.0 / p
        A1, A2 = K.cell_balls(top, rho, g, 4e-3)
        B = K.picture_balls(A1, A2, g, 4e-3, top)
        ext = np.hypot(B[:, 1], B[:, 2]) + B[:, 3]; i = int(np.argmax(ext))
        f = max(K.K2 * p / 200, K.K2 / 2 + K.K2 / (2 * top - 1))
        lines.append('%.4f %8.2f %s | %7.3f | %.4f (x = %.3f, r = %.4f) | %.4f | %+.4f' % (rho, p, ('square', 'honeycomb')[g], K.reach(top, rho), ext[i], B[i, 0], B[i, 3], f, ext[i] - f))
        if rho < 1:
            worst = max(worst, abs(ext[i] - f)); n += 1
lines.append('with a smaller second sphere (%d lists): the list and the formula differ by at most %.4f. With two equal spheres the list reaches further (buds on buds), up to 1.02 at size 97; there the start view is Version 20\'s, unchanged.' % (n, worst))
text = '\n'.join(lines) + '\n'
os.makedirs(os.path.join(os.path.dirname(HERE), 'logs'), exist_ok=True)
open(os.path.join(os.path.dirname(HERE), 'logs', 'tall.txt'), 'w', encoding='utf-8', newline='\n').write(text)
print(text)
