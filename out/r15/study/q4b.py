"""Question 4, second pass: taller Joukowski pillow, a c off every mirror plane, the rabbit's meeting point. python out/r15/study/q4b.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from scipy import ndimage
import q2_zoom as Q
D = os.path.join(HERE, 'data'); N = 257
C3 = (-1.0, 0.15, 0.1)

def info(vol, L):
    h = 2 * L / (vol.shape[0] - 1); lab, k = ndimage.label(vol); s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    return dict(volume=float(vol.sum() * h ** 3), pieces=int(k), largest_share=float(s[0] / vol.sum()))

if __name__ == '__main__':
    pool = vox.make_pool(); res = {}
    J10, J13 = ('J', 1.0, 2), ('J', 1.3, 2)
    cc = complex(Q.RAB[0], Q.RAB[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2; pa = np.array([al.real, al.imag, 0.0])
    for tag, key in (('J10', J10), ('J13', J13)):
        Q.KEY = key
        res[tag + '_rab_meet'] = Q.pieces_near(pool, Q.RAB, pa, 0.1, 161, 'lay-%s-meet-rab.npy' % tag)
        print(tag, 'rabbit meeting point', res[tag + '_rab_meet'], flush=True)
        t = np.linspace(-1, 1, 200001)
        dd = vox.esc(pa[0] + 0 * t, pa[1] + 0 * t, t, Q.RAB, key, 200)
        res[tag + '_rab_line_z'] = float((dd == 0).mean() * 2); print(tag, 'rabbit upright line through the meeting point: inside length %.5f' % res[tag + '_rab_line_z'], flush=True)
    for tag, key in (('E', Fp.REF), ('J10', J10)):
        d = vox.box(pool, key, (0, 0, 0), 1.7, N, C3, 60, cache=os.path.join(D, 'lay-%s-c3-%d.npy' % (tag, N)), trap=True)
        res[tag + '_c3'] = info(d == 0, 1.7); print(tag, 'c3', res[tag + '_c3'], flush=True)
    for nm, c, L in (('rab', Q.RAB, 1.5), ('cm1', Q.CM1, 1.7)):
        d = vox.box(pool, J13, (0, 0, 0), L, N, c, 60, cache=os.path.join(D, 'lay-J13-%s-%d.npy' % (nm, N)), trap=True)
        res['J13_' + nm] = info(d == 0, L); print('J13', nm, res['J13_' + nm], flush=True)
    Q.KEY = J13
    p, u = Q.surface_point(Q.RAB, Q.RAYS['rab'])
    for L in (0.08, 0.02):
        d = vox.box(pool, J13, tuple(p), L, 225, Q.RAB, 90, cache=os.path.join(D, 'lay-J13-zoom-rab-%g.npy' % L), trap=True)
        vol = d == 0; er = ndimage.binary_erosion(vol)
        res['J13_zoom_rab_%g' % L] = dict(share_inside=float(vol.mean()), surface_over_flat=float((vol & ~er).sum() / 225 ** 2)); print('J13 zoom rab', L, res['J13_zoom_rab_%g' % L], flush=True)
    # a deeper zoom for the two layouts on the rabbit: does the kind of detail hold four times smaller again
    for tag, key in (('E', Fp.REF), ('J10', J10)):
        Q.KEY = key
        p, u = Q.surface_point(Q.RAB, Q.RAYS['rab'])
        d = vox.box(pool, key, tuple(p), 0.005, 225, Q.RAB, 110, cache=os.path.join(D, 'deep-%s-zoom-rab-0.005.npy' % tag), trap=True)
        vol = d == 0; er = ndimage.binary_erosion(vol)
        res['%s_zoom_rab_0.005' % tag] = dict(share_inside=float(vol.mean()), surface_over_flat=float((vol & ~er).sum() / 225 ** 2)); print(tag, 'zoom rab 0.005', res['%s_zoom_rab_0.005' % tag], flush=True)
    json.dump(res, open(os.path.join(HERE, 'q4b.json'), 'w'), indent=1)
    pool.close()
