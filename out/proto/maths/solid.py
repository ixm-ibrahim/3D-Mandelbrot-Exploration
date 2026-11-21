"""Claim 6: Mandelbrot solid of v -> F_2(v) + c, pillow vs plain Riemann-sphere rule.
usage: python solid.py pillow|riemann"""
import sys, json, os, time
import numpy as np
from scipy import ndimage
from PIL import Image
import pillow as P

HERE = os.path.dirname(os.path.abspath(__file__))
rule = sys.argv[1]
if rule == 'pillow2':
    import twoplane_patch
NIT, R = 30, 4.0


def step(x, y, z):
    r = np.sqrt(x * x + y * y + z * z)
    rs = np.where(r > 0, r, 1.0)
    if rule in ('pillow', 'pillow2'):
        dx, dy, dz = P.dirmap(x / rs, y / rs, z / rs, 2)
    else:
        dx, dy, dz = P.riemann_dir(x / rs, y / rs, z / rs, 2)
    r2 = r * r
    return r2 * dx, r2 * dy, r2 * dz


def inside(cx, cy, cz):
    shp = cx.shape
    cx, cy, cz = cx.ravel(), cy.ravel(), cz.ravel()
    idx = np.arange(cx.size)
    x = np.zeros(cx.size); y = np.zeros(cx.size); z = np.zeros(cx.size)
    for it in range(NIT):
        fx, fy, fz = step(x, y, z)
        x, y, z = fx + cx[idx], fy + cy[idx], fz + cz[idx]
        keep = (x * x + y * y + z * z) <= R * R
        idx, x, y, z = idx[keep], x[keep], y[keep], z[keep]
    out = np.zeros(cx.size, bool)
    out[idx] = True
    return out.reshape(shp)


res = {'rule': rule}
t0 = time.time()
N = 160
xs = -2.2 + (np.arange(N) + 0.5) * 3.0 / N
ys = -1.3 + (np.arange(N) + 0.5) * 2.6 / N
zs = -1.3 + (np.arange(N) + 0.5) * 2.6 / N
X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
M = np.zeros((N, N, N), bool)
for k in range(0, N, 16):                     # chunks to bound memory
    M[k:k + 16] = inside(X[k:k + 16], Y[k:k + 16], Z[k:k + 16])
vox = (3.0 / N) * (2.6 / N) * (2.6 / N)
res['volume'] = float(M.sum() * vox)
zz = Z[M]
res['z_extent'] = [float(zz.min() - 1.3 / N), float(zz.max() + 1.3 / N)]
yy = Y[M]
res['y_extent'] = [float(yy.min() - 1.3 / N), float(yy.max() + 1.3 / N)]
lab, nlab = ndimage.label(M, structure=np.ones((3, 3, 3)))
sizes = np.bincount(lab.ravel())[1:]
res['pieces_26'] = int(nlab)
res['largest_share'] = float(sizes.max() / sizes.sum())
res['pieces_ge_8_voxels'] = int((sizes >= 8).sum())
res['second_largest_voxels'] = int(np.sort(sizes)[-2]) if nlab > 1 else 0
res['largest_voxels'] = int(sizes.max())
# symmetry of the solid under z -> -z and y -> -y
res['asym_z'] = int((M != M[:, :, ::-1]).sum())
res['asym_y'] = int((M != M[:, ::-1, :]).sum())
# area of each horizontal layer (profile along z)
res['layer_area_by_z'] = {('%.3f' % zs[k]): float(M[:, :, k].sum() * (3.0 / N) * (2.6 / N)) for k in range(N // 2, N, 4)}
res['t_grid'] = time.time() - t0
np.save(os.path.join(HERE, 'solid_%s.npy' % rule), M)

# horizontal slices at fixed z, finer
W, H = 900, 780
sx = -2.2 + (np.arange(W) + 0.5) * 3.0 / W
sy = -1.3 + (np.arange(H) + 0.5) * 2.6 / H
SX, SY = np.meshgrid(sx, sy, indexing='ij')
res['slices'] = {}
for zc in [0.0, 0.02, 0.1, 0.25, 0.5]:
    S = inside(SX, SY, np.full_like(SX, zc))
    lab2, n2 = ndimage.label(S, structure=np.ones((3, 3)))
    sz = np.bincount(lab2.ravel())[1:] if n2 else np.array([0])
    d = {'area': float(S.sum() * (3.0 / W) * (2.6 / H)), 'pieces_8conn': int(n2),
         'largest_share': float(sz.max() / max(1, sz.sum())),
         'pieces_ge_10px': int((sz >= 10).sum()),
         'top5_px': [int(v) for v in np.sort(sz)[::-1][:5]]}
    if zc == 0.0:   # compare with the flat Mandelbrot set, same grid, same test
        c = SX + 1j * SY
        w = np.zeros_like(c); alive = np.ones(c.shape, bool)
        for it in range(NIT):
            w = np.where(alive, w * w + c, w)
            alive &= (np.abs(w) <= R)
        d['pixels_different_from_flat_mandelbrot'] = int((alive != S).sum())
        d['flat_area'] = float(alive.sum() * (3.0 / W) * (2.6 / H))
    res['slices']['%.2f' % zc] = d
    Image.fromarray((~S.T[::-1] * 255).astype(np.uint8)).save(os.path.join(HERE, 'slice_%s_z%.2f.png' % (rule, zc)))
# vertical slices y = 0 (x-z plane) and x = -0.5 (y-z plane)
sz_ = -1.3 + (np.arange(H) + 0.5) * 2.6 / H
VX, VZ = np.meshgrid(sx, sz_, indexing='ij')
S = inside(VX, np.zeros_like(VX), VZ)
Image.fromarray((~S.T[::-1] * 255).astype(np.uint8)).save(os.path.join(HERE, 'slice_%s_y0_xz.png' % rule))
lab2, n2 = ndimage.label(S, structure=np.ones((3, 3)))
szv = np.bincount(lab2.ravel())[1:]
res['xz_slice_y0'] = {'area': float(S.sum() * (3.0 / W) * (2.6 / H)), 'pieces_8conn': int(n2), 'largest_share': float(szv.max() / szv.sum())}
c = VX + 1j * VZ
w = np.zeros_like(c); alive = np.ones(c.shape, bool)
for it in range(NIT):
    w = np.where(alive, w * w + c, w)
    alive &= (np.abs(w) <= R)
res['xz_slice_y0']['pixels_different_from_flat_mandelbrot'] = int((alive != S).sum())
res['xz_slice_y0']['pixels_total_flat'] = int(alive.sum())
VY, VZ2 = np.meshgrid(sy, sz_, indexing='ij')
S = inside(np.full_like(VY, -0.5), VY, VZ2)
Image.fromarray((~S.T[::-1] * 255).astype(np.uint8)).save(os.path.join(HERE, 'slice_%s_x-0.5_yz.png' % rule))
res['t_total'] = time.time() - t0
json.dump(res, open(os.path.join(HERE, 'solid_%s.json' % rule), 'w'), indent=1)
print(json.dumps(res, indent=1))
