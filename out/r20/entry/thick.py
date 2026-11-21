"""Round 20, entry: two plain measurements on the Julia sets of the rule (numpy, out/r20/entry/rule.py, which the
checks compare with the page's MATH.windsq to 1e-14).
1. How thick are the bodies round the x-axis? Take every point of the flat set (a grid in the plane z = 0), turn it
   about the x-axis by a small angle, and ask whether it is still in the set. Points nearer the x-axis than 0.1 are
   left out (a turn hardly moves them).
2. The count round the axis: the outline of the cut across the x-axis, by direction; which number of repeats per
   turn is strongest (from the brute-*-x0.png cuts).
python out/r20/entry/thick.py -> thick.txt"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rule

out = []
def say(s=''):
    print(s); out.append(s); sys.stdout.flush()

def inside(F, x, y, z, c, its):
    x, y, z = (np.array(t, float) for t in (x, y, z)); ok = np.ones(x.shape, bool)
    for _ in range(its):
        r2 = x * x + y * y + z * z; ok &= r2 <= 4096
        X, Y, Z = F(np.where(ok, x, 0), np.where(ok, y, 0), np.where(ok, z, 0))
        x, y, z = X + c[0], Y + c[1], Z + c[2]
    return ok & (x * x + y * y + z * z <= 4096)

SETS = [('basilica', [-1, 0, 0]), ('San Marco', [-0.75, 0, 0]), ('rabbit', [-0.122561, 0.744862, 0]), ('Siegel disc', [-0.390541, -0.586788, 0])]
ANG = [0.25, 0.5, 1, 2, 4, 8, 15, 30]
F = rule.wn(2)
N = 500
g = (np.arange(N) + 0.5) / N * 3.6 - 1.8
X, Y = np.meshgrid(g, g)
say('1. Turn the flat set about the x-axis by an angle: what share of its points (further than 0.1 from the x-axis) is still in the set?')
say('   %-12s %6s  %s' % ('set', 'steps', '  '.join('%5g deg' % a for a in ANG)))
for nm, c in SETS:
    for its in (40, 80):
        flat = inside(F, X, Y, 0 * X, c, its) & (np.abs(Y) > 0.1)
        x, y = X[flat], Y[flat]
        row = []
        for a in ANG:
            t = np.radians(a)
            row.append(100.0 * inside(F, x, y * np.cos(t), y * np.sin(t), c, its).mean())
        say('   %-12s %6d  %s   (%d points)' % (nm, its, '  '.join('%7.1f %%' % v for v in row), len(x)))
say()
say('2. The cut across the x-axis at x = 0: the outline by direction, and the strongest number of repeats per turn')
for f, nm in (('brute-n2-cm1-x0.png', 'power 2, c = -1'), ('brute-n3-c03-x0.png', 'power 3, c = 0.3'), ('brute-n4-cm1-x0.png', 'power 4, c = -1'), ('brute-n5-c03-x0.png', 'power 5, c = 0.3'),
              ('brute-n3-ci-x0.png', 'power 3, c = i'), ('brute-n4-c03p03i-x0.png', 'power 4, c = 0.3 + 0.3i'), ('brute-rab-x0.png', 'power 2, rabbit'), ('brute-sie-x0.png', 'power 2, Siegel disc')):
    p = os.path.join(HERE, f)
    if not os.path.exists(p):
        continue
    im = np.asarray(Image.open(p).convert('RGB')).astype(int)
    ins = (np.abs(im - np.array([236, 226, 200])).sum(axis=2) < 12)
    n = ins.shape[0]; yy, xx = np.mgrid[0:n, 0:n]; dx = xx - (n - 1) / 2; dy = (n - 1) / 2 - yy
    r = np.hypot(dx, dy); th = np.degrees(np.arctan2(dy, dx)) % 360
    prof = np.zeros(360); np.maximum.at(prof, np.floor(th[ins]).astype(int) % 360, r[ins])
    sp = np.abs(np.fft.rfft(prof - prof.mean()))
    top = np.argsort(sp[1:25])[::-1][:3] + 1
    say('   %-24s strongest repeats per turn: %s (strengths %s)' % (nm, ', '.join(str(int(t)) for t in top), ', '.join('%.0f' % sp[t] for t in top)))
open(os.path.join(HERE, 'thick.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
