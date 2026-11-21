"""The eyes: where are the 2D 'ghost' pixels of a view (painted inside, but well outside by my recipe)?
  python out/r28/eyes/mk/ghosts2d.py <tag> <view>   -> prints clusters, saves marks/<tag>-<view>-zoom.png"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import recipe, walk
tag, name = sys.argv[1:3]
m, dep, met, img = walk.load(tag, name)
top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
H, W = img.shape[:2]; w, h = m['w'], m['h']; s = m['v2']['h'] / h
xs = m['v2']['x'] + (np.arange(W) + 0.5 - w / 2) * s; ys = m['v2']['y'] + (h / 2 - (np.arange(H) + 0.5)) * s
X, Y = np.meshgrid(xs, ys)
P = np.stack([X.ravel(), Y.ravel(), np.zeros(X.size)], axis=1)
so = (recipe.verdict(P, top, rho, grid, rounds) != 0).reshape(H, W)
cx = int(round((0 - m['v2']['x']) / s + w / 2 - 0.5)); cy = int(round(h / 2 - 0.5 - (0 - m['v2']['y']) / s))
ref = img[cy, cx]
print('inside colour', ref, 'pixel size', s)
d = np.abs(img - ref).max(axis=2)
cream = d <= 10
g = cream & ~so
ys_, xs_ = np.nonzero(g)
print('painted inside but not solid at the pixel centre:', g.sum())
# distance of each such pixel to the nearest solid pixel (in pixels), by growing the solid mask
grown = so.copy(); dist = np.full(so.shape, 99)
dist[so] = 0
for k in range(1, 8):
    e = grown.copy(); e[1:, :] |= grown[:-1, :]; e[:-1, :] |= grown[1:, :]; e[:, 1:] |= grown[:, :-1]; e[:, :-1] |= grown[:, 1:]
    dist[e & ~grown] = k; grown = e
for k in range(1, 8):
    print('  %d px (city blocks) from the nearest solid pixel centre: %d' % (k, int((g & (dist == k)).sum())))
print('  further: %d' % int((g & (dist == 99)).sum()))
# sub-pixel truth: a pixel painted inside whose centre is not solid: how much of the pixel is solid (8 x 8 points)?
if len(ys_):
    far = np.nonzero(g & (dist >= 2))
    sub = (np.arange(8) + 0.5) / 8 - 0.5
    worst = []
    for y, x in list(zip(*far))[:400]:
        QX, QY = np.meshgrid(xs[x] + sub * s, ys[y] + sub * s)
        f = (recipe.verdict(np.stack([QX.ravel(), QY.ravel(), np.zeros(64)], axis=1), top, rho, grid, rounds) != 0).mean()
        f3 = 0.0
        QX, QY = np.meshgrid(xs[x] + np.linspace(-1.5, 1.5, 24) * s, ys[y] + np.linspace(-1.5, 1.5, 24) * s)
        f3 = (recipe.verdict(np.stack([QX.ravel(), QY.ravel(), np.zeros(QX.size)], axis=1), top, rho, grid, rounds) != 0).mean()
        worst.append((f, f3, x, y, tuple(img[y, x])))
    worst.sort()
    print('  of the first %d such pixels 2 or more from a solid centre: solid share of the pixel itself (8 x 8 points), of its 3 x 3 pixels, x, y, colour' % len(worst))
    for wv in worst[:12]:
        print('   ', wv)
    print('   ...'); 
    for wv in worst[-4:]:
        print('   ', wv)
    y, x = far[0][0], far[1][0]
    x0, y0 = max(0, x - 40), max(0, y - 40)
    crop = Image.fromarray(img[y0:y0 + 80, x0:x0 + 80].astype(np.uint8)).resize((640, 640), Image.NEAREST)
    crop.save(os.path.join(walk.EYES, 'marks', '%s-%s-zoom.png' % (tag, name)))
    print('zoom about pixel', x, y)
