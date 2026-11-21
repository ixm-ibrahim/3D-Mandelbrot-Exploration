"""Question 4: other layouts, in pictures (rabbit, c = -1, one zoom, Mandelbrot solid). python out/r15/study/q4_vols.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from scipy import ndimage
import q2_zoom as Q
D = os.path.join(HERE, 'data')
KEYS = {'J10': ('J', 1.0, 2), 'J08': ('J', 0.8, 2), 'E08': ('E', 0.8, 2, 0.5), 'Ea35': ('E', 1.0, 2, 0.35)}
N = 257

if __name__ == '__main__':
    pool = vox.make_pool(); res = {}
    for tag, key in KEYS.items():
        for nm, c, L in (('rab', Q.RAB, 1.5), ('cm1', Q.CM1, 1.7)):
            d = vox.box(pool, key, (0, 0, 0), L, N, c, 60, cache=os.path.join(D, 'lay-%s-%s-%d.npy' % (tag, nm, N)), trap=True)
            vol = d == 0; h = 2 * L / (N - 1)
            lab, k = ndimage.label(vol); s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
            res['%s_%s' % (tag, nm)] = dict(volume=float(vol.sum() * h ** 3), pieces=int(k), largest_share=float(s[0] / vol.sum()))
            print(tag, nm, res['%s_%s' % (tag, nm)], flush=True)
        # the meeting point of c = -1: one piece or two
        Q.KEY = key
        pb = np.array([(1 - 5 ** 0.5) / 2, 0.0, 0.0])
        r = Q.pieces_near(pool, Q.CM1, pb, 0.1, 129, 'lay-%s-meet-cm1.npy' % tag); res[tag + '_cm1_meet'] = r
        print(tag, 'c = -1 meeting point', r, flush=True)
        if tag in ('J10', 'J08'):
            for nm, c in (('rab', Q.RAB), ('cm1', Q.CM1)):
                p, u = Q.surface_point(c, Q.RAYS[nm])
                res['%s_%s_surface_point' % (tag, nm)] = [float(v) for v in p]
                for L in ((0.32, 0.08, 0.02) if tag == 'J10' else (0.08,)):
                    d = vox.box(pool, key, tuple(p), L, 225, c, 90, cache=os.path.join(D, 'lay-%s-zoom-%s-%g.npy' % (tag, nm, L)), trap=True)
                    vol = d == 0; er = ndimage.binary_erosion(vol)
                    lab, k = ndimage.label(vol)
                    res['%s_zoom_%s_%g' % (tag, nm, L)] = dict(share_inside=float(vol.mean()), pieces=int(k), surface_over_flat=float((vol & ~er).sum() / 225 ** 2))
                    print(tag, 'zoom', nm, L, res['%s_zoom_%s_%g' % (tag, nm, L)], flush=True)
        if tag == 'J10':
            cen, L = (-0.25, 0.0, 0.0), 1.85
            d = vox.box(pool, key, cen, L, N, iters=48, mandel=True, cache=os.path.join(D, 'lay-%s-mandel-%d.npy' % (tag, N)), trap=True)
            vol = d == 0; h = 2 * L / (N - 1)
            res[tag + '_mandel'] = dict(volume=float(vol.sum() * h ** 3), above=float(vol[:, :, N // 2 + 1:].sum() * h ** 3), below=float(vol[:, :, :N // 2].sum() * h ** 3))
            print(tag, 'mandel', res[tag + '_mandel'], flush=True)
            from PIL import Image
            for pl, v in (('y0', (0, 0, 1)), ('z0', (0, 1, 0))):
                dd = vox.plane(pool, key, cen, (1, 0, 0), v, L, L, 801, 801, iters=100, mandel=True, cache=os.path.join(D, 'lay-%s-mandel-%s.npy' % (tag, pl)))
                Image.fromarray(vox.cut_img(dd)).save(os.path.join(HERE, 'q4-%s-mandel-%s.png' % (tag, pl)))
            for nm, c in (('rab', Q.RAB), ('cm1', Q.CM1)):
                for pl, u, v in (('y0', (1, 0, 0), (0, 0, 1)), ('x0', (0, 1, 0), (0, 0, 1))):
                    dd = vox.plane(pool, key, (0, 0, 0), u, v, 1.75, 1.75, 801, 801, c, 100, cache=os.path.join(D, 'lay-%s-%s-%s.npy' % (tag, nm, pl)))
                    Image.fromarray(vox.cut_img(dd)).save(os.path.join(HERE, 'q4-%s-%s-%s.png' % (tag, nm, pl)))
        json.dump(res, open(os.path.join(HERE, 'q4-vols.json'), 'w'), indent=1)
    pool.close()
