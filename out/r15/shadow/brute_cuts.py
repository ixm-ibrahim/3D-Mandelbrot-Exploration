"""Round 15B, shadow: point-by-point cuts of the Mandelbrot solids (numpy, 64-bit, no distance estimate, 14 steps,
escape radius 64 as the page): the plane y = 0 (where the pillow's seams and corners lie) and the plane y = 0.05 beside
it, for the powers 2 to 5. Also: does it matter whether the escape test uses the plain length |v| or the gauge rho?"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extent as E, gauge_proto2 as G

N = 360
tiles, rep = [], []
for n in (2, 3, 4, 5):
    for y in (0.0, 0.05):
        xs = (np.arange(N) + 0.5) / N * 4.4 - 2.2; zs = 2.2 - (np.arange(N) + 0.5) / N * 4.4
        X, Z = np.meshgrid(xs, zs)
        P = np.stack([X.ravel(), np.full(N * N, y), Z.ravel()], 1)
        m = E.inside(P, n).reshape(N, N)
        rep.append('power %d, cut at y = %.2f (x and z from -2.2 to 2.2, %d x %d points): %.1f %% of the window is in the solid; highest point z = %.2f, lowest z = %.2f' % (
            n, y, N, N, 100 * m.mean(), Z[m].max() if m.any() else float('nan'), Z[m].min() if m.any() else float('nan')))
        im = np.zeros((N, N, 3), np.uint8); im[:] = (16, 18, 24); im[m] = (232, 223, 201)
        k = int(round((2.2 - 0) / 4.4 * N)); im[k, :, :] = np.where(m[k][:, None], im[k], (90, 90, 110))     # the line z = 0
        tiles.append((im, 'power %d, cut at y = %s' % (n, '0' if y == 0 else '0.05')))
W = 4 * (N + 8) + 8
sheet = Image.new('RGB', (W, 2 * (N + 30) + 8), (0, 0, 0)); d = ImageDraw.Draw(sheet)
for i, (im, cap) in enumerate(tiles):
    col, row = i // 2, i % 2
    sheet.paste(Image.fromarray(im), (8 + col * (N + 8), 8 + row * (N + 30)))
    d.text((12 + col * (N + 8), 8 + row * (N + 30) + N + 4), cap + ' (x to the right, z up, grey line: z = 0)', fill=(220, 220, 220))
sheet.save(os.path.join(HERE, 'brute-y-cuts.png'))

# the escape test: plain length against the gauge, on random points round the solids
rng = np.random.default_rng(7)
for n in (2, 3):
    P = rng.uniform(-2.0, 2.0, size=(300000, 3))
    a = E.inside(P, n)
    # the same with the gauge: |v| replaced by rho(v)
    z = np.zeros_like(P); alive = np.ones(len(P), bool)
    for i in range(15):
        r = np.linalg.norm(z, axis=1); ok = r > 1e-20
        rho = np.where(ok, r * G.gauge_fp(z / np.where(ok, r, 1)[:, None], n, 5), 0)
        alive &= rho <= 64
        if i == 14: break
        z = np.where(alive[:, None], E.F(z, n) + P, z)
    rep.append('power %d, 300,000 random points in a box: in the solid by the plain length %d, by the gauge %d, in one but not the other %d' % (n, a.sum(), alive.sum(), (a != alive).sum()))
open(os.path.join(HERE, 'brute_cuts.txt'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
print('\n'.join(rep))
