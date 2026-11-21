"""Julia sets for c off every kept plane: power 3 near c = i, power 2 near the rabbit. python out/r15/study/q7_offplane.py"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
from scipy import ndimage
D = os.path.join(HERE, 'data'); N = 257
CASES = [('p3-off', ('E', 1.0, 3, 0.5), (0.1, 0.95, 0.15)), ('rab-off-E', Fp.REF, (-0.12, 0.74, 0.12)), ('rab-off-J13', ('J', 1.3, 2), (-0.12, 0.74, 0.12))]
if __name__ == '__main__':
    pool = vox.make_pool(); res = {}
    for tag, key, c in CASES:
        d = vox.box(pool, key, (0, 0, 0), 1.5, N, c, 60, cache=os.path.join(D, 'off-%s-%d.npy' % (tag, N)), trap=True)
        v = d == 0; h = 3.0 / (N - 1)
        if v.sum() == 0: res[tag] = dict(c=c, volume=0.0); print(tag, c, 'empty', flush=True); continue
        lab, k = ndimage.label(v); s = np.sort(np.bincount(lab.ravel())[1:])[::-1]
        res[tag] = dict(c=c, volume=float(v.sum() * h ** 3), pieces=int(k), largest_share=float(s[0] / v.sum()), above=float(v[:, :, N // 2 + 1:].sum() * h ** 3), below=float(v[:, :, :N // 2].sum() * h ** 3))
        print(tag, res[tag], flush=True)
    json.dump(res, open(os.path.join(HERE, 'q7.json'), 'w'), indent=1)
    pool.close()
