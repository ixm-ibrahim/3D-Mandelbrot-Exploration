"""Judge, check 9: where do the buds sit on the middle body? Fractions (balls object) against halvings (true c = -1).

Balls object: walk round the middle ball in the flat plane just outside its rim, note every stretch that is inside
(a bud), and compare the place of each bud with the place my arithmetic gives for the fraction p / q.
True picture: a bud is attached where the middle body touches another body. The way round the middle body is
measured in the body's own natural coordinate (one full turn = 1, starting where it meets the left neighbour); two
steps of the rule double it. The attach points are read off my table of that coordinate."""
import numpy as np
from math import gcd
import jlib as J
import jcarry as JC
from j5_carry_tests import ford

K2 = 1.05; RAD = K2 / 2
print('== balls object, quarter of the rim from the left meeting point (0) to the bud on top (1)')
n = 400000; ang = np.pi - (np.arange(n) + 0.5) / n * (np.pi / 2)          # from the left meeting point over the top
found = {}
for lift in (1.004, 1.0015):
    r = RAD * lift; ins = J.balls(r * np.cos(ang), r * np.sin(ang), 0 * ang, grid='line', rounds=60) == 1
    edges = np.flatnonzero(np.diff(ins.astype(int)) != 0); runs = []
    st = 0 if ins[0] else None
    for e in edges:
        if st is None:
            st = e + 1
        else:
            runs.append((st, e)); st = None
    found[lift] = [(0.5 * (a + b) / n, (b - a + 1) / n) for a, b in runs]
runs = found[1.004]
fr = sorted({(p, q) for q in range(1, 9) for p in range(0, q + 1) if gcd(p, q) == 1}, key=lambda v: v[0] / v[1])
print('   buds met at 1.004 of the radius: %d; at 1.0015 of the radius: %d' % (len(runs), len(found[1.0015])))
worst = 0.0
for p, q in fr:
    cen, rad = ford(complex(p), complex(q)); place = (np.pi - np.arctan2(cen[1], cen[0])) / (np.pi / 2)
    if rad < 0.004 * RAD * 1.2 or not (0.01 < place < 0.99):
        continue
    near = min(runs, key=lambda v: abs(v[0] - place)); worst = max(worst, abs(near[0] - place))
    if q <= 5:
        print('   fraction %d/%d: my arithmetic puts the bud at %.4f of the way, %.4f wide; the walk meets a bud at %.4f' % (p, q, place, 2 * rad, near[0]))
print('   all fractions with bottom number up to 8 that are big enough to be met: a bud is met within %.4f of the way of each' % worst)
big = sorted(runs, key=lambda v: -v[1])[:7]
print('   the seven widest buds met on the walk sit at: ' + ', '.join('%.3f' % v[0] for v in sorted(big)))

print('== true flat picture of c = -1: where other bodies are attached to the middle body')
tab = JC.Tab('c1'); mid = tab.ok & (tab.N == 0); oth = tab.ok & (tab.N > 0)
from scipy import ndimage
touch = mid & ndimage.binary_dilation(oth, structure=np.ones((5, 5)))
lab, cnt = ndimage.label(ndimage.binary_dilation(touch, structure=np.ones((3, 3)))); rows = []
osz = ndimage.label(oth, structure=np.ones((3, 3)))
for k in range(1, cnt + 1):
    m = touch & (lab == k)
    if m.sum() < 2:
        continue
    X = tab.X[m].astype(float); Y = tab.Y[m].astype(float); r = np.hypot(X, Y); i = np.argmax(r)
    turn = (np.arctan2(-Y[i], -X[i]) / (2 * np.pi)) % 1.0             # b = -(X + iY); the left meeting point is b = 1
    jj, ii = np.nonzero(m); nb = osz[0][max(jj.min() - 3, 0):jj.max() + 4, max(ii.min() - 3, 0):ii.max() + 4]
    ids = np.unique(nb[nb > 0]); size = max((int((osz[0] == t).sum()) for t in ids[:3]), default=0) if len(ids) else 0
    rows.append((size, turn, JC.X0 + ii[i] * JC.STEP, JC.Y1 - jj[i] * JC.STEP, r[i]))
rows.sort(reverse=True)
print('   the 14 biggest attached bodies: way round the middle body where each is attached, and the nearest halving')
for size, turn, x, y, r in rows[:14]:
    best = min(((abs(turn - j / d), j, d) for d in (1, 2, 4, 8, 16, 32, 64) for j in range(d + 1) if gcd(j, d) == 1 or j == 0), key=lambda v: (round(v[0], 3), v[2]))
    print('      attached at (%+.3f, %+.3f): %.4f of a full turn; nearest halving %d/%d (off by %.4f); attached body %d grid points' % (x, y, turn, best[1], best[2], best[0], size))
