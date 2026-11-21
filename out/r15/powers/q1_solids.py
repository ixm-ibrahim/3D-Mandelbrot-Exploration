"""Question 1: the solids for powers 2..5 (Mandelbrot solid and the Julia set at the centre of a period-2 body).
python out/r15/powers/q1_solids.py N [procs]   -> data/q1-<name>-N.npz (inside, death, box)"""
import os, sys, time, json, numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sf

S2 = float(np.sqrt(0.5))
# name, kind, n, c, centre, half-size
CASES = [
    ('m2', 'm', 2, None, (-0.45, 0, -0.2), 1.75),
    ('m3', 'm', 3, None, (0, 0, 0), 1.45),
    ('m4', 'm', 4, None, (0, 0, 0.4), 1.6),
    ('m5', 'm', 5, None, (0, 0, 0.45), 1.6),
    ('j2', 'j', 2, (-1.0, 0.0, 0.0), (0, 0, -0.95), 2.15),
    ('j3', 'j', 3, (0.0, 1.0, 0.0), (0, 0, 0), 1.6),
    ('j4', 'j', 4, (-1.0, 0.0, 0.0), (0, 0, 0.45), 1.75),
    ('j5', 'j', 5, (S2, S2, 0.0), (0, 0, 0.6), 1.9),
]

if __name__ == '__main__':
    N = int(sys.argv[1]); procs = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    iters = 30
    with Pool(procs) as pool:
        for name, kind, n, c, cen, L in CASES:
            if only and name not in only: continue
            t0 = time.time()
            axes = sf.cube_axes(cen, L, N)
            ins, dth = sf.grid(kind, n, c, axes, iters, pool)
            np.savez_compressed(os.path.join(HERE, 'data', 'q1-%s-%d.npz' % (name, N)), inside=ins, death=dth, cen=np.array(cen, float), L=L, n=n)
            vox = (2 * L / (N - 1)) ** 3
            zz = axes[2][np.where(ins.any(axis=(0, 1)))[0]]
            print('%s N=%d power %d: volume %.4f, z from %.3f to %.3f, %.0f s' % (name, N, n, ins.sum() * vox, zz.min() if zz.size else 0, zz.max() if zz.size else 0, time.time() - t0), flush=True)
