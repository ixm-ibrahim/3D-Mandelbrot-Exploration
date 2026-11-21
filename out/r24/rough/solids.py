"""Round 24, rough: rough solids (first inside block on each line of sight, 30 steps), cached per rule, shape and eye.

    python out/r24/rough/solids.py rule[,rule...] [sets] [eyes]      -> cache/dep-<rule>-<set>-<eye>.npz
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rl as L
M = L.M
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}
W, HH, ND, STEPS, HALF = 300, 225, 180, 30, 1.75


def depth(name, sname, eye):
    path = os.path.join(L.CACHE, 'dep-%s-%s-%s.npz' % (name, sname, eye))
    if os.path.exists(path):
        d = np.load(path); return d['depth'], float(d['px'])
    dep, px = M.solid(L.get(name), L.SETS[sname], W, HH, ND, STEPS, half_w=HALF, cam=EYES[eye])
    np.savez_compressed(path, depth=dep, px=px)
    return dep, px


def surface_points(dep, eye):
    """The point of the solid seen at each pixel (NaN where nothing is hit)."""
    e1, e2, e3 = M.frame(EYES[eye]); us = np.linspace(-HALF, HALF, W); vs = np.linspace(HALF * HH / W, -HALF * HH / W, HH)
    U, V = np.meshgrid(us, vs); hit = np.isfinite(dep); d = np.where(hit, dep, 0.0)
    P = np.stack([U * e1[i] + V * e2[i] + d * e3[i] for i in range(3)], -1)
    return P, hit


if __name__ == '__main__':
    names = sys.argv[1].split(','); sets = sys.argv[2].split(',') if len(sys.argv) > 2 else ['basilica', 'rabbit']
    eyes = sys.argv[3].split(',') if len(sys.argv) > 3 else ['a', 'top']; t0 = time.time()
    for nm in names:
        for sn in sets:
            if int((L.blocks(nm, sn) >= 80).sum()) == 0:
                print('%s %s: nothing inside, skipped' % (nm, sn)); continue
            for e in eyes:
                dep, px = depth(nm, sn, e); print('%-10s %-8s %-3s hit %d pixels  [%.0f s]' % (nm, sn, e, int(np.isfinite(dep).sum()), time.time() - t0)); sys.stdout.flush()
