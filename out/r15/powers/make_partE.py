"""Part E of the sheet: the Mandelbrot solids coloured by what the orbit settles on.
sand = one point (the main body), red = two points in turn (period-2 bodies), blue = three, grey = the rest of the solid.
python make_partE.py N"""
import os, sys, json, numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import viz
from viz import turns
N = int(sys.argv[1]) if len(sys.argv) > 1 else 129
TINTS = {1: (0.86, 0.78, 0.62), 2: (0.95, 0.30, 0.25), 3: (0.30, 0.55, 0.98), 0: (0.55, 0.57, 0.60)}


def render_classes(per, az, el, light=(-0.45, 0.55, 0.7), bg=(18, 20, 26)):
    """turns.render, with the colour of each picture point taken from the class of the voxel that is hit."""
    n = per.shape[0]
    occ = (per >= 0).astype(np.float32)
    u, v, w = turns._rot(az, el)
    M = np.stack([u, v, w], axis=1)
    cen = (n - 1) / 2.0
    off = np.array([cen, cen, cen]) - M @ np.array([cen] * 3)
    sm = ndimage.gaussian_filter(occ, 1.1)
    V = ndimage.affine_transform(sm, M, offset=off, output_shape=(n, n, n), order=1, mode='constant', cval=0.0)
    solid = V > 0.5
    anyhit = solid.any(axis=2)
    k0 = (n - 1) - np.argmax(solid[:, :, ::-1], axis=2); k0 = np.where(anyhit, k0, 0)
    gi, gj, gk = np.gradient(V)
    ta = lambda A, kk=None: np.take_along_axis(A, (k0 if kk is None else kk)[:, :, None], axis=2)[:, :, 0]
    nx, ny, nz = -ta(gi), -ta(gj), -ta(gk)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9; nx, ny, nz = nx / ln, ny / ln, nz / ln
    wide = ndimage.gaussian_filter(V, max(2.0, n / 60.0))
    kf = np.clip(k0 + int(max(2, n / 60.0)), 0, n - 1)
    ao = np.clip(1.25 - 1.9 * ta(wide, kf), 0.25, 1.0)
    l = np.array(light, float); l /= np.linalg.norm(l)
    diff = np.clip(nx * l[0] + ny * l[1] + nz * l[2], 0, 1)
    shade = (0.22 + 0.68 * diff + 0.10 * np.clip(nz, 0, 1)) * ao * (0.72 + 0.28 * k0 / (n - 1.0))
    # class at the hit: the class with the most weight just under the skin
    kb = np.clip(k0 - 1, 0, n - 1)
    best = np.zeros(k0.shape, np.float32); cls = np.zeros(k0.shape, np.int8)
    for c in (0, 1, 2, 3):
        ind = (per == c).astype(np.float32) if c else ((per == 0) | (per > 3)).astype(np.float32)
        W = ndimage.affine_transform(ndimage.gaussian_filter(ind, 0.8), M, offset=off, output_shape=(n, n, n), order=1, mode='constant', cval=0.0)
        s = ta(W) + ta(W, kb)
        m = s > best; best[m] = s[m]; cls[m] = c
    img = np.zeros((n, n, 3), np.float32)
    for c, t in TINTS.items():
        for ch in range(3):
            img[:, :, ch] = np.where(anyhit & (cls == c), 255 * t[ch] * shade, img[:, :, ch])
    for ch in range(3): img[:, :, ch] = np.where(anyhit, img[:, :, ch], bg[ch])
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]


def cut_classes(a, bg=(18, 20, 26)):
    img = np.zeros(a.shape + (3,), np.float32); img[:] = bg
    for c, t in TINTS.items():
        m = (a == c) if c else ((a == 0) | (a > 3))
        img[m] = [255 * x for x in t]
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]


J = json.load(open(os.path.join(HERE, 'q1-periods-%d.json' % N)))
rows, rt = [], []
for n in (2, 3, 4, 5):
    per = np.load(os.path.join(HERE, 'data', 'periods-m%d-%d.npy' % (n, N)))
    r = [render_classes(per, *viz.VIEWS[k]) for k in ('front', 'above', 'below', 'alongx', 'alongy')]
    m = N // 2
    r += [cut_classes(per[:, m, :]), cut_classes(per[m, :, :])]
    b2 = J['m%d' % n].get('period_2_bodies', [])
    rows.append(r)
    rt.append('Power %d\nred bodies (period 2)\nfound: %d\n(the flat set has\n%d of them, in the\nplane)' % (n, len(b2), n - 1))
cols = ['Seen from the front', 'From above (looking down)', 'From below (looking up)', 'Along the x-axis', 'Along the y-axis', 'Cut at y = 0 (upright)', 'Upright cut across, middle of the box']
viz.sheet(rows, cols, rt, os.path.join(HERE, 'part-E.png'), cell=250,
          title='5. Mandelbrot solids coloured by what the orbit settles on: sand = one point (main body), red = two points in turn (period 2), blue = three, grey = the rest (voxels, %d per side)' % N)
print('wrote part-E.png')
