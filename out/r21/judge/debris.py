"""Loose debris: inside cells that are NOT joined to the main body even when every gap of up to two cells (0.045) is bridged.
python out/r21/judge/debris.py > out/r21/judge/debris.txt

Why not simply count pieces: the bodies of a Julia set meet in single points, so on any grid a clean chain of bodies
falls into several pieces. Bridging small gaps joins a chain again; what is still apart after that is loose.
(A first run bridged gaps of up to four cells, 0.09: then nothing is loose in any rule but frame.area_1_px, 16 pieces.)
Grid 160^3 on the cube -1.8..1.8 (cell 0.0226), 80 steps and 200 steps; basilica, rabbit, Siegel disc.
Reported: loose pieces (count), their share of the inside volume, and the size of the biggest loose piece (cells)."""
import os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
S = np.ones((3, 3, 3)); n = 160; xs = np.linspace(-1.8, 1.8, n)


def loose(m):
    tot = int(m.sum())
    if tot == 0:
        return '   empty'
    lab, k = ndimage.label(ndimage.binary_dilation(m, structure=S, iterations=1), structure=S)
    sz = np.bincount(lab[m]); sz[0] = 0; order = np.argsort(sz)[::-1]; rest = sz[order[1:]]; rest = rest[rest > 0]
    return '%4d loose, %5.2f%% of %7d, biggest %5d' % (rest.size, 100.0 * rest.sum() / tot, tot, int(rest[0]) if rest.size else 0)


print('%-22s | %-46s | %-46s | %-46s' % ('rule', 'basilica, 80 steps', 'rabbit, 80 steps (then 200 steps)', 'Siegel disc, 200 steps'))
for r in J.RULES:
    cells = []
    for nm, c, steps in (('basilica', (-1.0, 0.0, 0.0), (80,)), ('rabbit', M.RABBIT, (80, 200)), ('siegel', M.SIEGEL, (200,))):
        cnt = np.zeros((n, n, n), np.int32)
        for i0 in range(0, n, 40):
            X, Y, Z = np.meshgrid(xs[i0:i0 + 40], xs, xs, indexing='ij'); cnt[i0:i0 + 40] = M.stay(r, X, Y, Z, *c, max(steps))
        cells.append(' ; '.join(loose(cnt >= s) for s in steps))
    print('%-22s | %s | %s | %s' % (r.name, *cells)); sys.stdout.flush()
