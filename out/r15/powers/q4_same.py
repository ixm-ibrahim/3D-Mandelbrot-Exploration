"""Question 4: the other layout (pillow_ref through the study's fastpil) in the SAME boxes as this layout, so the
pictures are at the same scale. Also exact cuts z = 0 / y = 0 / x = 0 of power 4 at the second c and of the rabbit."""
import os, sys, time, json, numpy as np
from multiprocessing import Pool
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sf
from q1_cuts import plane, flat
if __name__ == '__main__':
    D = os.path.join(HERE, 'data'); out = {}
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 8) as pool:
        for nm, kind, c, cen, L in (('bas', 'j', (-1.0, 0.0, 0.0), (0, 0, -0.95), 2.15), ('rab', 'j', (-0.12, 0.74, 0.0), (0, 0, -0.9), 2.0), ('m2', 'm', None, (-0.45, 0, -0.2), 1.75)):
            t0 = time.time(); N = 193
            axes = sf.cube_axes(cen, L, N)
            ins, dth = sf.grid(kind, 2, c, axes, 30, pool, rule='pillow')
            np.savez_compressed(os.path.join(D, 'q4s-pillow-%s-193.npz' % nm), inside=ins, death=dth, cen=np.array(cen, float), L=L, n=2)
            h = 2 * L / (N - 1); az = axes[2]
            lab, k = ndimage.label(ins, structure=np.ones((3, 3, 3))); sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
            zz = az[np.where(ins.any(axis=(0, 1)))[0]]
            out[nm] = dict(volume=float(ins.sum() * h ** 3), above=float(ins[:, :, az > h / 2].sum() * h ** 3), below=float(ins[:, :, az < -h / 2].sum() * h ** 3),
                           z=[float(zz.min()), float(zz.max())], pieces=int(k), largest_share=float(sizes[0] / ins.sum()))
            print('other layout %s: %s %.0f s' % (nm, out[nm], time.time() - t0), flush=True)
        for name, n, c, cen, L in (('j4b', 4, (0.5, float(np.sqrt(0.75)), 0.0), (0, 0, 0.45), 1.75), ('rab', 2, (-0.12, 0.74, 0.0), (0, 0, -0.9), 2.0)):
            o = (cen[0], cen[1], 0.0)
            iz, dz = plane(pool, 'j', n, c, o, (1, 0, 0), (0, 1, 0), L)
            fl = flat('j', n, c, o, L)
            iy, dy = plane(pool, 'j', n, c, (cen[0], 0.0, cen[2]), (1, 0, 0), (0, 0, 1), L)
            ix, dx = plane(pool, 'j', n, c, (0.0, cen[1], cen[2]), (0, 1, 0), (0, 0, 1), L)
            np.savez_compressed(os.path.join(D, 'cuts-%s.npz' % name), iz=iz, dz=dz, iy=iy, dy=dy, ix=ix, dx=dx, flat=fl, cen=np.array(cen, float), L=L)
            print('%s: cut z = 0 against the flat set: %d inside, flat %d, differ %d' % (name, iz.sum(), fl.sum(), (iz != fl).sum()), flush=True)
    json.dump(out, open(os.path.join(HERE, 'q4-same.json'), 'w'), indent=1)
