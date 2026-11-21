"""Question 2 (detail at smaller sizes) and the rabbit's meeting point. python out/r15/study/q2_zoom.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from scipy import ndimage
D = os.path.join(HERE, 'data'); os.makedirs(D, exist_ok=True)
KEY = Fp.REF
CM1 = (-1.0, 0.0, 0.0)
RAB = (-0.12, 0.74, 0.0)
SETS = {'cm1': CM1, 'rab': RAB}
RAYS = {'cm1': (0.25, 0.6, 0.75), 'rab': (0.5, -0.3, 0.8)}
SIZES = (0.32, 0.08, 0.02)
NZ = 225


def surface_point(c, u):
    u = np.array(u, float); u /= np.linalg.norm(u)
    t = np.linspace(0, 2, 40001)
    d = vox.esc(t * u[0], t * u[1], t * u[2], c, KEY, 150)
    ins = d == 0
    first_out = int(np.argmax(~ins))          # the surface of the body that holds the origin
    return (t[first_out - 1] * u), u


def pieces_near(pool, c, p, L, N, name):
    """small box round p: share inside, and the number of pieces once a small ball round p is taken out."""
    d = vox.box(pool, KEY, tuple(p), L, N, c, 80, cache=os.path.join(D, name), trap=True)
    vol = d == 0
    a = np.linspace(-L, L, N)
    X, Y, Z = np.meshgrid(a, a, a, indexing='ij')
    R = np.sqrt(X * X + Y * Y + Z * Z)
    out = dict(share_inside=float(vol[R <= L].mean()))
    for hole in (0.15, 0.3):
        v2 = vol & (R > hole * L) & (R <= L)
        lab, k = ndimage.label(v2)
        s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
        big = s[s > 0.02 * v2.sum()]
        out['pieces_hole_%g' % hole] = dict(all=int(k), big=int(len(big)), big_shares=[float(x / v2.sum()) for x in big])
    return out


if __name__ == '__main__':
    pool = vox.make_pool()
    res = {}
    # whole rabbit at 321^3
    d = vox.box(pool, KEY, (0, 0, 0), 1.5, 321, RAB, 60, cache=os.path.join(D, 'rab-box-321.npy'), trap=True)
    vol = d == 0; h = 3.0 / 320
    lab, k = ndimage.label(vol); s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    res['rabbit'] = dict(volume=float(vol.sum() * h ** 3), pieces=int(k), sizes=[int(x) for x in s[:12]], largest_share=float(s[0] / vol.sum()))
    print('rabbit: volume %.4f, pieces %d, largest shares' % (res['rabbit']['volume'], k), [round(float(x / vol.sum()), 4) for x in s[:8]], flush=True)
    # the rabbit's meeting point of three bodies (the fixed point alpha of the flat map)
    cc = complex(RAB[0], RAB[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2
    pa = np.array([al.real, al.imag, 0.0]); res['rabbit_alpha'] = [float(al.real), float(al.imag)]
    pb = np.array([(1 - 5 ** 0.5) / 2, 0.0, 0.0])
    for nm, c, p in (('rab', RAB, pa), ('cm1', CM1, pb)):
        t = np.linspace(-1, 1, 200001)
        dd = vox.esc(p[0] + 0 * t, p[1] + 0 * t, t, c, KEY, 200)
        res[nm + '_line_z_inside_length'] = float((dd == 0).mean() * 2)
        for L in (0.1, 0.025):
            r = pieces_near(pool, c, p, L, 161, 'meet-%s-%g.npy' % (nm, L)); res['%s_meet_%g' % (nm, L)] = r
            print(nm, 'meeting point, box half-size', L, r, flush=True)
        print(nm, 'upright line through the meeting point: inside length %.5f' % res[nm + '_line_z_inside_length'], flush=True)
        # cuts through the meeting point: flat, and upright at 6 turns
        for L in (0.2, 0.02):
            dz = vox.plane(pool, KEY, tuple(p), (1, 0, 0), (0, 1, 0), L, L, 501, 501, c, 120, cache=os.path.join(D, 'meetcut-%s-flat-%g.npy' % (nm, L)))
            row = {'flat': float((dz == 0).mean())}
            for az in (0, 30, 60, 90, 120, 150):
                a = np.radians(az)
                du = vox.plane(pool, KEY, tuple(p), (np.cos(a), np.sin(a), 0), (0, 0, 1), L, L, 501, 501, c, 120, cache=os.path.join(D, 'meetcut-%s-up%d-%g.npy' % (nm, az, L)))
                row['upright_%d' % az] = float((du == 0).mean())
            res['%s_meetcut_share_%g' % (nm, L)] = row
            print(nm, 'cuts through the meeting point, half-size', L, {k_: round(v, 3) for k_, v in row.items()}, flush=True)
    json.dump(res, open(os.path.join(HERE, 'q2.json'), 'w'), indent=1)
    # zoom boxes on the surface
    for nm, c in SETS.items():
        p, u = surface_point(c, RAYS[nm])
        res[nm + '_surface_point'] = [float(v) for v in p]
        print(nm, 'surface point', p, flush=True)
        for L in SIZES:
            d = vox.box(pool, KEY, tuple(p), L, NZ, c, 90, cache=os.path.join(D, 'zoom-%s-%g.npy' % (nm, L)), trap=True)
            vol = d == 0
            lab, k = ndimage.label(vol); s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
            # roughness: surface voxels against the surface of a smoothed copy
            er = ndimage.binary_erosion(vol); surf = int((vol & ~er).sum())
            res['zoom_%s_%g' % (nm, L)] = dict(share_inside=float(vol.mean()), pieces=int(k), largest_share=float(s[0] / max(1, vol.sum())), surface_voxels=surf,
                                               surface_over_flat=float(surf / NZ ** 2))
            print('zoom', nm, L, res['zoom_%s_%g' % (nm, L)], flush=True)
    json.dump(res, open(os.path.join(HERE, 'q2.json'), 'w'), indent=1)
    pool.close()
