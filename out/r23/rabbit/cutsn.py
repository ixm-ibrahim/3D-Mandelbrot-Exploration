"""Cuts for the N sweep (cuts-n.png) and a finer count of the buds round the side body of c = -1.
    python out/r23/rabbit/cutsn.py
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import doors as D
import explore as E
import nsweep as NSW
M = D.M
NS = [0, 1, 2, 3, 5, 99]

if __name__ == '__main__':
    B, R = D.SETS['basilica'], D.SETS['rabbit']; cd = np.array([R[0], R[1], 0.0]); cd /= np.linalg.norm(cd)
    rows = [('c = -1, cut across the x-axis at x = 0 (the middle body)', B, (0, 0, 0), (0, 1, 0), (0, 0, 1), 1.0),
            ('c = -1, cut across the x-axis at x = -1 (the side body), closer', B, (-1, 0, 0), (0, 1, 0), (0, 0, 1), 0.5),
            ('rabbit, cut lifted to z = 0.15', R, (0, 0, 0.15), (1, 0, 0), (0, 1, 0), 1.6),
            ('rabbit, upright cut through 0 and c', R, (0, 0, 0), tuple(cd), (0, 0, 1), 1.6)]
    w = h = 260; pad = 6; steps = 80
    W = pad + len(NS) * (w + pad); H = 26 + len(rows) * (h + 22)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    for j, N in enumerate(NS):
        d.text((pad + j * (w + pad), 4), 'N = %s' % ('every step' if N == 99 else N), fill=(235, 220, 170), font=M.font(15))
    for i, (nm, c, o, e1, e2, half) in enumerate(rows):
        y = 26 + i * (h + 22); d.text((pad, y), nm, fill=(150, 160, 175), font=M.font(13))
        for j, N in enumerate(NS):
            n = E.plane_cut(D.get('along%d' % N), c, o, e1, e2, w, h, half, steps)
            im.paste(Image.fromarray(M.shade(n, steps)), (pad + j * (w + pad), y + 18))
    p = os.path.join(HERE, 'cuts-n.png'); im.save(p); print('wrote', p, im.size)
    # finer ring count round the side bodies
    for N in NS:
        r = D.get('along%d' % N); line = 'N = %2d' % N
        for nm, x0, lo, hi in (('x = -1', -1.0, 0.20, 0.45), ('x = 1', 1.0, 0.20, 0.45)):
            Rs = np.arange(lo, hi, 0.0025); cnt = np.array([NSW.arcs(r, x0, R_)[0] for R_ in Rs])
            w8 = Rs[cnt == 8]; w2 = Rs[cnt == 2]; w4 = Rs[cnt == 4]
            line += ' | %s: 8 arcs on %d radii%s, 4 on %d, 2 on %d, most %d' % (nm, w8.size, (' (R %.3f..%.3f)' % (w8.min(), w8.max())) if w8.size else '', w4.size, w2.size, cnt.max())
        print(line); sys.stdout.flush()
