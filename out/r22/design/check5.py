"""Loose pieces of the hinged rule: 96^3 grid, 80 steps, pieces counted with gaps of one cell bridged (bodies that
touch at one point then count as one piece) and with gaps of two cells bridged.
python out/r22/design/check5.py > out/r22/design/check5.txt"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
import sheet2 as S2
M, D = L.M, L.D
R = L.refs()
for cn in ('basilica', 'rabbit', 'siegel', 'p4', 't02'):
    c = S2.SETS[cn]
    for nm in ('oneplane', 'along', 'alonghinge'):
        r = R[nm] if nm in R else D.get(nm)
        v = L.grid(r, c, 96, 80); out = []
        for br in (0, 1, 2):
            b, n, dust = L.pieces(v, bridge=br); out.append('bridge %d: biggest %.1f %%, pieces %d, in pieces under 8 blocks %.2f %%' % (br, 100 * b, n, 100 * dust))
        print('%-9s %-11s inside %6d | %s' % (cn, nm, v.sum(), ' | '.join(out))); sys.stdout.flush()
