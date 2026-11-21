"""A model of the Kleinian trap solid in the plane z = 0 of the strip world (before the turning-out sphere), in numpy.

  python out/r9/klein/model.py <out.png> <mx> <my> <tx> <ty> <variant> [trap] [skip] [radius] [thick]

It copies the search of kde() in src/js/30-shaders.js step by step and paints the points whose trap value is below
zero (the solid), with the walls and the edges of the copies of the pattern drawn over it. Variants:
  v8     the trap is tested at the point after each map (Version 8)
  sym    the same point, against the trap and its images under the slides by 2 and the half turn (nearest wins)
  next   Version 8 plus the map applied to the neighbours across each edge of the copy
  both   sym and next together
"""
import sys
import numpy as np
from PIL import Image

out, mx, my, tx, ty, variant = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
trap = sys.argv[7] if len(sys.argv) > 7 else 'shell'
skip = int(sys.argv[8]) if len(sys.argv) > 8 else 1
RAD = float(sys.argv[9]) if len(sys.argv) > 9 else 1.0
TW = float(sys.argv[10]) if len(sys.argv) > 10 else 0.05
ITER = 40
W, H = 1500, 700
X0, X1 = -3.2, 3.2
Y0, Y1 = -0.5, my + 0.5
H = int(W * (Y1 - Y0) / (X1 - X0))
xs, ys = np.meshgrid(np.linspace(X0, X1, W), np.linspace(Y1, Y0, H))
a = my; fs = np.sign(-mx); sx = mx / a


def trapDist(x, y):
    qx, qy = x - tx, y - ty
    if trap == 'shell': return np.abs(np.hypot(qx, qy) - RAD)
    if trap == 'point': return np.hypot(qx, qy)
    if trap == 'cross':   # the axis lines, cut down to the trap radius; in the plane z = 0 the z line is a point
        ox, oy = np.maximum(np.abs(qx) - RAD, 0), np.maximum(np.abs(qy) - RAD, 0)
        return np.sqrt(np.minimum(ox * ox + qy * qy, np.minimum(qx * qx + oy * oy, qx * qx + qy * qy)))
    raise SystemExit('trap?')


def symDist(x, y, n=1):
    d = trapDist(x, y)
    for k in range(-n, n + 1):
        if k: d = np.minimum(d, trapDist(x + 2 * k, y))
        d = np.minimum(d, trapDist(mx - x + 2 * k, my - y))
    return d


def line(x):
    xr = x - 0.5 * mx
    return a * 0.5 + fs * (2 * a - 1.95) / 4 * np.sign(xr) * (1 - np.exp(-(7.2 - (1.95 - a) * 15) * np.abs(xr)))


def reduce(x, y):
    x = x - sx * y; x = (x + 1) % 2 - 1; x = x + sx * y
    up = y >= line(x)
    return np.where(up, mx - x, x), np.where(up, my - y, y), up


def B(x, y):
    iR = 1 / np.maximum(x * x + y * y, 1e-20)
    return mx + x * iR, my - y * iR, iR


def run(variant):
    x, y = xs.copy(), ys.copy()
    DF = np.ones_like(x)
    best = np.full_like(x, 1e9)
    lvl = np.zeros_like(x)
    if skip <= 0:
        best = (symDist(x, y) if variant in ('sym', 'both') else trapDist(x, y)) - TW
    for i in range(ITER):
        dx, dy, up = reduce(x, y)
        if variant in ('next', 'both') and i + 1 >= skip:
            # the neighbours across each edge of the copy: the slides by 2 either way, and the half turn
            for nx, ny in ((dx + 2, dy), (dx - 2, dy), (mx - dx, my - dy)):
                bx, by, r = B(nx, ny)
                t = ((symDist(bx, by) if variant == 'both' else trapDist(bx, by)) - TW) / (DF * r)
                lvl = np.where(t < best, i + 1, lvl); best = np.minimum(best, t)
        x, y, iR = B(dx, dy)
        DF = DF * iR
        if i + 1 >= skip:
            t = ((symDist(x, y) if variant in ('sym', 'both') else trapDist(x, y)) - TW) / DF
            lvl = np.where(t < best, i + 1, lvl); best = np.minimum(best, t)
    return best, lvl


best, lvl = run(variant)
img = np.zeros((H, W, 3), np.uint8) + np.array([18, 20, 28], np.uint8)
pal = np.array([[255, 255, 255], [255, 120, 80], [90, 200, 255], [150, 255, 120], [255, 220, 90], [220, 130, 255], [130, 130, 130]], np.uint8)
solid = best < 0
img[solid] = pal[np.minimum(lvl[solid].astype(int), 6)]
# the walls
img[(np.abs(ys) < 0.006) | (np.abs(ys - a) < 0.006)] = [70, 90, 200]
# the edges of the copies: the sheared lines and the dividing line
xsh = xs - sx * ys
edge = (np.abs((xsh + 1) % 2) < 0.006) & (ys > 0) & (ys < a)
img[edge] = [200, 60, 60]
xw = (xsh + 1) % 2 - 1 + sx * ys
img[(np.abs(ys - line(xw)) < 0.006)] = [60, 160, 60]
Image.fromarray(img).save(out)
print('wrote', out, 'solid share %.4f' % solid.mean())
