"""Questions 5 and 6: the Mandelbrot solid (power 2), and power 3. python out/r15/study/q56.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from scipy import ndimage
from PIL import Image
D = os.path.join(HERE, 'data'); os.makedirs(D, exist_ok=True)

def flat_mandel(cx, cy, n, iters, R2=4.0):
    c = cx + 1j * cy; z = c.copy(); ins = np.abs(z) ** 2 <= R2
    with np.errstate(all='ignore'):
        for _ in range(iters):
            z = np.where(ins, z ** n + c, z); ins &= (z.real ** 2 + z.imag ** 2) <= R2
    return ins

def flat_julia(x, y, c, n, iters, R2=4.0):
    z = x + 1j * y; ins = np.ones(z.shape, bool)
    with np.errstate(all='ignore'):
        for _ in range(iters):
            z = np.where(ins, z ** n + c, z); ins &= (z.real ** 2 + z.imag ** 2) <= R2
    return ins

def describe(vol, L, cen, tag, res):
    N = vol.shape[0]; h = 2 * L / (N - 1)
    lab, k = ndimage.label(vol); s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    ax = np.linspace(-L, L, N)
    ext = {}
    for i, nm in enumerate('xyz'):
        other = tuple(j for j in range(3) if j != i)
        w = np.nonzero(vol.any(axis=other))[0]
        ext[nm] = [float(ax[w[0]] + cen[i]), float(ax[w[-1]] + cen[i])]
    up = vol[:, :, N // 2 + 1:].sum() * h ** 3; dn = vol[:, :, :N // 2].sum() * h ** 3
    res[tag] = dict(volume=float(vol.sum() * h ** 3), pieces=int(k), largest_share=float(s[0] / vol.sum()), extent=ext, volume_above_plane=float(up), volume_below_plane=float(dn))
    print(tag, res[tag], flush=True)

if __name__ == '__main__':
    pool = vox.make_pool(); res = {}
    K2, K3 = Fp.REF, ('E', 1.0, 3, 0.5)
    # ---- power 2 Mandelbrot solid
    cen, L, N = (-0.25, 0.0, 0.0), 1.85, 321
    d = vox.box(pool, K2, cen, L, N, iters=48, mandel=True, cache=os.path.join(D, 'mandel2-box-%d.npy' % N), trap=True)
    describe(d == 0, L, cen, 'mandel2', res)
    n = 1201
    dz = vox.plane(pool, K2, cen, (1, 0, 0), (0, 1, 0), L, L, n, n, iters=100, mandel=True, cache=os.path.join(D, 'mandel2-z0.npy'))
    a = np.linspace(-L, L, n); X, Y = np.meshgrid(a + cen[0], a, indexing='ij')
    fm = flat_mandel(X, Y, 2, 100)
    res['mandel2_z0_points_that_differ_from_flat'] = int(((dz == 0) != fm).sum()); res['mandel2_z0_inside'] = int((dz == 0).sum())
    print('Mandelbrot cut z = 0 against the flat set: %d of %d points differ (inside: %d)' % (((dz == 0) != fm).sum(), n * n, (dz == 0).sum()), flush=True)
    Image.fromarray(vox.cut_img(dz)).save(os.path.join(HERE, 'q5-mandel-z0.png'))
    dy = vox.plane(pool, K2, cen, (1, 0, 0), (0, 0, 1), L, L, n, n, iters=100, mandel=True, cache=os.path.join(D, 'mandel2-y0.npy'))
    Image.fromarray(vox.cut_img(dy)).save(os.path.join(HERE, 'q5-mandel-y0.png'))
    for x0 in (-1.0, -0.2):
        dx = vox.plane(pool, K2, (x0, 0, 0), (0, 1, 0), (0, 0, 1), L, L, n, n, iters=100, mandel=True, cache=os.path.join(D, 'mandel2-x%g.npy' % x0))
        Image.fromarray(vox.cut_img(dx)).save(os.path.join(HERE, 'q5-mandel-x%g.png' % x0))
        res['mandel2_x%g_area' % x0] = float((dx == 0).mean() * (2 * L) ** 2)
    json.dump(res, open(os.path.join(HERE, 'q56.json'), 'w'), indent=1)
    # ---- power 3
    cj = (0.0, 1.0, 0.0); Lj, Nj = 1.5, 257
    d = vox.box(pool, K3, (0, 0, 0), Lj, Nj, cj, 60, cache=os.path.join(D, 'p3-julia-box-%d.npy' % Nj), trap=True)
    describe(d == 0, Lj, (0, 0, 0), 'p3_julia_c=i', res)
    v = d == 0; res['p3_julia_mirror_mismatch_voxels'] = int((v != v[:, :, ::-1]).sum())
    n = 801
    dz = vox.plane(pool, K3, (0, 0, 0), (1, 0, 0), (0, 1, 0), Lj, Lj, n, n, cj, 100, cache=os.path.join(D, 'p3-julia-z0.npy'))
    a = np.linspace(-Lj, Lj, n); X, Y = np.meshgrid(a, a, indexing='ij')
    fj = flat_julia(X, Y, 1j, 3, 100)
    res['p3_julia_z0_points_that_differ_from_flat'] = int(((dz == 0) != fj).sum())
    print('power 3 Julia cut z = 0 against the flat set: %d points differ' % ((dz == 0) != fj).sum(), flush=True)
    Image.fromarray(vox.cut_img(dz)).save(os.path.join(HERE, 'q6-p3-julia-z0.png'))
    for nm, u in (('y0', (1, 0, 0)), ('x0', (0, 1, 0))):
        dd = vox.plane(pool, K3, (0, 0, 0), u, (0, 0, 1), Lj, Lj, n, n, cj, 100, cache=os.path.join(D, 'p3-julia-%s.npy' % nm))
        Image.fromarray(vox.cut_img(dd)).save(os.path.join(HERE, 'q6-p3-julia-%s.png' % nm))
    Lm, Nm = 1.5, 257
    d = vox.box(pool, K3, (0, 0, 0), Lm, Nm, iters=48, mandel=True, cache=os.path.join(D, 'p3-mandel-box-%d.npy' % Nm), trap=True)
    describe(d == 0, Lm, (0, 0, 0), 'p3_mandel', res)
    v = d == 0; res['p3_mandel_mirror_mismatch_voxels'] = int((v != v[:, :, ::-1]).sum())
    dz = vox.plane(pool, K3, (0, 0, 0), (1, 0, 0), (0, 1, 0), Lm, Lm, n, n, iters=100, mandel=True, cache=os.path.join(D, 'p3-mandel-z0.npy'))
    fm = flat_mandel(X, Y, 3, 100)
    res['p3_mandel_z0_points_that_differ_from_flat'] = int(((dz == 0) != fm).sum())
    print('power 3 Mandelbrot cut z = 0 against the flat set: %d points differ' % ((dz == 0) != fm).sum(), flush=True)
    Image.fromarray(vox.cut_img(dz)).save(os.path.join(HERE, 'q6-p3-mandel-z0.png'))
    dd = vox.plane(pool, K3, (0, 0, 0), (1, 0, 0), (0, 0, 1), Lm, Lm, n, n, iters=100, mandel=True, cache=os.path.join(D, 'p3-mandel-y0.npy'))
    Image.fromarray(vox.cut_img(dd)).save(os.path.join(HERE, 'q6-p3-mandel-y0.png'))
    json.dump(res, open(os.path.join(HERE, 'q56.json'), 'w'), indent=1)
    pool.close()
