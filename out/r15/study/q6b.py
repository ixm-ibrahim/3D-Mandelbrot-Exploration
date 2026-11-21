"""Power 3 with both layouts: Julia set c = i close up, Mandelbrot solid, stretch numbers. python out/r15/study/q6b.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from scipy import ndimage
from PIL import Image
import q2_zoom as Q
from q3_stretch import jac, stats
np.seterr(all='ignore')
D = os.path.join(HERE, 'data'); N = 257
CI = (0.0, 1.0, 0.0)
KEYS = {'E3': ('E', 1.0, 3, 0.5), 'J3': ('J', 1.0, 3)}

if __name__ == '__main__':
    pool = vox.make_pool(); res = {}
    rng = np.random.default_rng(11)
    dd = rng.normal(size=(20000, 3)); dd /= np.linalg.norm(dd, axis=1)[:, None]
    for tag, key in KEYS.items():
        out = jac(dd, key, 4, h=1e-7)
        s1, s4 = stats(*out[1]), stats(*out[4])
        g = np.random.default_rng(5)
        p = g.normal(size=(300000, 3)); p *= (1.4 * g.uniform(0, 1, 300000) ** (1 / 3) / np.linalg.norm(p, axis=1))[:, None]
        e = vox.esc(p[:, 0], p[:, 1], p[:, 2], CI, key, 60)
        q = p[(e >= 12) & (e < 60)]
        o = jac(q, key, 9, c=CI, h=1e-9)
        r = {k: stats(*o[k]) for k in (3, 6, 9)}
        res[tag + '_numbers'] = dict(k1=s1, k4=s4, surface=r, n=int(len(q)))
        print(tag, 'no c: shape ratio median / 99%%: 1 step %.2f / %.1f, 4 steps %.2f / %.1f;  next to the surface of c = i (n=%d): median at 3, 6, 9 steps: %.3g, %.3g, %.3g' % (
            s1['median'], s1['p99'], s4['median'], s4['p99'], len(q), r[3]['median'], r[6]['median'], r[9]['median']), flush=True)
        if tag == 'J3':
            d = vox.box(pool, key, (0, 0, 0), 1.5, N, CI, 60, cache=os.path.join(D, 'J3-julia-box-%d.npy' % N), trap=True)
            v = d == 0; lab, k = ndimage.label(v); s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
            res['J3_julia'] = dict(volume=float(v.sum() * (3.0 / 256) ** 3), pieces=int(k), largest_share=float(s[0] / v.sum()), mirror_mismatch=int((v != v[:, :, ::-1]).sum()))
            print('J3 julia', res['J3_julia'], flush=True)
            d = vox.box(pool, key, (0, 0, 0), 1.5, N, iters=48, mandel=True, cache=os.path.join(D, 'J3-mandel-box-%d.npy' % N), trap=True)
            v = d == 0; res['J3_mandel'] = dict(volume=float(v.sum() * (3.0 / 256) ** 3)); print('J3 mandel', res['J3_mandel'], flush=True)
            for pl, vv in (('y0', (0, 0, 1)), ('z0', (0, 1, 0))):
                e2 = vox.plane(pool, key, (0, 0, 0), (1, 0, 0), vv, 1.5, 1.5, 801, 801, iters=100, mandel=True, cache=os.path.join(D, 'J3-mandel-%s.npy' % pl))
                Image.fromarray(vox.cut_img(e2)).save(os.path.join(HERE, 'q6-J3-mandel-%s.png' % pl))
        Q.KEY = key
        p0, u = Q.surface_point(CI, (0.5, -0.3, 0.8))
        res[tag + '_surface_point'] = [float(x) for x in p0]
        for L in (0.32, 0.08, 0.02):
            d = vox.box(pool, key, tuple(p0), L, 225, CI, 80, cache=os.path.join(D, '%s-zoom-%g.npy' % (tag, L)), trap=True)
            v = d == 0; er = ndimage.binary_erosion(v)
            res['%s_zoom_%g' % (tag, L)] = dict(share_inside=float(v.mean()), surface_over_flat=float((v & ~er).sum() / 225 ** 2)); print(tag, 'zoom', L, res['%s_zoom_%g' % (tag, L)], flush=True)
        json.dump(res, open(os.path.join(HERE, 'q6b.json'), 'w'), indent=1)
    pool.close()
