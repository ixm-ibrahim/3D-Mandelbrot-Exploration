# does the settle shortcut change the answer? one flat cut with and without it
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp
if __name__ == '__main__':
    pool = vox.make_pool()
    for nm, c in (('c=-1', (-1.0, 0, 0)), ('rabbit', (-0.12, 0.74, 0.0)), ('c=(-1,0.15,0.1)', (-1, 0.15, 0.1))):
        for pl, u, v, cen in (('x=0.1', (0, 1, 0), (0, 0, 1), (0.1, 0, 0)), ('z=0.2', (1, 0, 0), (0, 1, 0), (0, 0, 0.2))):
            h = 2.0 * 1.6 / 600
            a = vox.grid(pool, Fp.REF, cen, tuple(h * np.array(u)), tuple(h * np.array(v)), (0, 0, 0), 601, 601, 1, c, 80)
            b = vox.grid(pool, Fp.REF, cen, tuple(h * np.array(u)), tuple(h * np.array(v)), (0, 0, 0), 601, 601, 1, c, 80, trap=True)
            print(nm, pl, 'inside without shortcut', int((a == 0).sum()), 'with', int((b == 0).sum()), 'points that differ', int(((a == 0) != (b == 0)).sum()), flush=True)
    pool.close()
