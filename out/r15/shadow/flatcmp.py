"""Round 15B, shadow: the page's 2D view of the cut at z = 0, Pillow from 4D against Sphere inversions, one plane
(whose cut is the flat set), same page, same settings, pixel by pixel. And the flat Mandelbrot set of z^n + c itself,
worked in numpy at the centre of every pixel with the page's 14 steps and escape radius 64, against the page's inside
colour. (After out/r15/entry/flatcmp.py.)"""
import os
import numpy as np
from PIL import Image
D = 'out/r15/shadow/'
INK = np.array([232, 223, 201])
ins = lambda im: (np.abs(im - INK).max(axis=2) < 14)
pairs = [('p4-n%d-cut' % n, 'ref-n%d-cut' % n) for n in (2, 3, 4, 5)] + [('p4-j-%s-cut' % t, 'ref-j-%s-cut' % t) for t in ('basilica', 'rabbit', 'c03')]
for pa, pb in pairs:
    if not (os.path.exists(D + pa + '.png') and os.path.exists(D + pb + '.png')):
        print(pa, 'missing'); continue
    a = np.asarray(Image.open(D + pa + '.png').convert('RGB')).astype(int)
    b = np.asarray(Image.open(D + pb + '.png').convert('RGB')).astype(int)
    d = np.abs(a - b).max(axis=2)
    ia, ib = ins(a), ins(b)
    print('%-18s %dx%d: pixels that differ by more than 8 levels: %d (%.3f %%), by more than 40: %d; inside colour: pillow from 4D %d, one plane %d, in one but not the other: %d' % (
        pa, a.shape[1], a.shape[0], int((d > 8).sum()), 100.0 * (d > 8).mean(), int((d > 40).sum()), int(ia.sum()), int(ib.sum()), int((ia != ib).sum())))
for n, cx in ((2, -0.5), (3, 0.0), (4, 0.0), (5, 0.0)):
    p = D + 'p4-n%d-cut.png' % n
    if not os.path.exists(p):
        continue
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    H, W = a.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    c = (cx + (xs + 0.5 - W / 2) * 3.2 / H) + 1j * ((H / 2 - ys - 0.5) * 3.2 / H)
    z = np.zeros_like(c); alive = np.ones(c.shape, bool)
    for k in range(15):
        alive &= np.abs(z) <= 64
        z = np.where(alive, z ** n + c, z)
    ui = np.zeros((H, W), bool); ui[:, 735:] = True; ui[640:, :] = True; ui[:60, :80] = True      # the page's own controls lie over these parts
    ok = ~ui
    i2 = ins(a)
    print('power %d: flat set of z^%d + c (numpy, 14 steps, radius 64) against the inside colour of the page\'s cut, away from the controls: set %d pixels, picture %d, in one but not the other %d (%.2f %% of the set)' % (
        n, n, int((alive & ok).sum()), int((i2 & ok).sum()), int(((alive != i2) & ok).sum()), 100.0 * ((alive != i2) & ok).sum() / max(1, (alive & ok).sum())))
