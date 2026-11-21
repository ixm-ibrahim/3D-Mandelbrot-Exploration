"""Numbers for run a (the rechecks): python out/t9/solids/meas.py
For each picture of dist/v8.html and the first check's picture of the same step on dist/v6.html:
share of bright pixels (largest channel above 60), mean colour, share of bright pixels on the 3 pixel rim of the frame."""
import os, sys
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
A, T = os.path.join(ROOT, 'out/t9/solids/'), os.path.join(ROOT, 'out/t6/solids/')
PAIRS = [('a-m-skip0', 'p-m-skip0'), ('a-m-skip1', 'p-m-skip1'), ('a-m-iter4', 'p-m-iter4'), ('a-m-iter80', 'p-m-iter80'), ('a-m-thick0.01', 'p-m-thick0.01'),
         ('a-m-shell-skip0', None), ('a-m-planes-skip0', None), ('a-m-ring-skip0', None), ('a-m-point-skip0', None),
         ('a-m-point', 'm-point-s1'), ('a-m-point-thick0.3', None), ('a-m-ray', 'm-ray-s1'), ('a-m-ray-thick0.2', None),
         ('a-j-base', 'p-j-base'), ('a-j-thick0.005', 'p-j-thick0.005'), ('a-j-thick0.02', 'p-j-thick0.02'), ('a-j-skip3', 'p-j-skip3'), ('a-j-skip6', 'p-j-skip6'),
         ('a-j-radius0.2', 'p-j-radius0.2'), ('a-j-tx0.5', 'p-j-tx0.5'), ('a-j-ty0.5', 'p-j-ty0.5'), ('a-j-iter3', 'p-j-iter3'), ('a-j-iter80', 'p-j-iter80'),
         ('a-j-radius1.5', 'p-j-radius1.5'), ('a-j-radius2', 'p-j-radius2'), ('a-j-radius2-resetview', None), ('a-j1-point', 'j1-point-s1'), ('a-j3-point', 'j3-point-s1'), ('a-j3-ray', 'j3-ray-s1'),
         ('a-k-base', 'p-k-base'), ('a-k-thick0.2', 'p-k-thick0.2'), ('a-k-thick0.2-resetview', None), ('a-k-radius1.6', 'p-k-radius1.6'), ('a-k-tx0.6', 'p-k-tx0.6'),
         ('a-k-point', 'k-point-s1'), ('a-k-line', 'k-line-s1'), ('a-k-ray', 'k-ray-s1')]


def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)


def stats(im):
    b = im.max(axis=2) > 60
    rim = np.zeros(b.shape, bool); rim[:3] = rim[-3:] = True; rim[:, :3] = True; rim[:, -3:] = True
    return 100 * b.mean(), im.reshape(-1, 3).mean(axis=0), 100 * b[rim].mean()


def differ(a, b):
    return 100 * ((np.abs(a - b).max(axis=2)) > 24).mean()


for a, t in PAIRS:
    pa = A + a + '.png'
    if not os.path.exists(pa):
        print('%-26s missing' % a); continue
    ia = load(pa); s = stats(ia)
    line = '%-26s v8: bright %5.2f %%  mean %5.1f %5.1f %5.1f  rim %5.1f %%' % (a, s[0], s[1][0], s[1][1], s[1][2], s[2])
    if t and os.path.exists(T + t + '.png'):
        it = load(T + t + '.png'); u = stats(it)
        line += '   | v6 %-16s bright %5.2f %%  mean %5.1f %5.1f %5.1f  rim %5.1f %%' % (t, u[0], u[1][0], u[1][1], u[1][2], u[2])
        if it.shape == ia.shape:
            line += '  | v6 to v8 differ %5.2f %%' % differ(ia, it)
    print(line)
for x, y in (('a-j-iter3', 'a-j-iter80'), ('a-m-iter4', 'a-m-iter80'), ('a-k-point', 'a-k-line'), ('a-k-point', 'a-k-ray'), ('a-k-line', 'a-k-ray')):
    print('differ %s against %s: %.2f %% of the pixels (v8)' % (x, y, differ(load(A + x + '.png'), load(A + y + '.png'))))
for x, y in (('p-j-iter3', 'p-j-iter80'), ('p-m-iter4', 'p-m-iter80'), ('k-point-s1', 'k-line-s1'), ('k-point-s1', 'k-ray-s1'), ('k-line-s1', 'k-ray-s1')):
    print('differ %s against %s: %.2f %% of the pixels (v6)' % (x, y, differ(load(T + x + '.png'), load(T + y + '.png'))))
