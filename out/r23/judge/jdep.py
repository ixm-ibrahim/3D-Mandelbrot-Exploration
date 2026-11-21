"""Round 23, judge: rough solids for the user's pictures (my loop, my typed rules).

    python out/r23/judge/jdep.py <rule,rule,...> <set,set,...> <eye,eye>      compute the depth maps that are missing (cache/)

Every solid: 340 x 255 x 220 blocks, 60 steps, picture 3.2 wide, centre 0.
Eyes: 'a' = (0.45, 0.5, 1.0) from the front, a little to the right and above; 'top' = (0.2, 1.0, 0.35) from above.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jl as L
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}
DW, DH, DN, DSTEPS, DHALF = 340, 255, 220, 60, 1.6


def dep(name, sname, eye, compute=True):
    path = os.path.join(CACHE, 'dep-%s-%s-%s.npz' % (name.replace(':', '-'), sname, eye))
    if os.path.exists(path):
        d = np.load(path); return d['depth'], float(d['px'])
    if not compute:
        return None
    t0 = time.time(); r = L.get(name)
    depth, px = L.solid(r, L.SETS[sname], DW, DH, DN, DSTEPS, half_w=DHALF, cam=EYES[eye])
    np.savez_compressed(path, depth=depth, px=px)
    print('dep %-12s %-9s eye %-3s %.0f s, %.1f %% of the picture covered' % (name, sname, eye, time.time() - t0, 100 * np.isfinite(depth).mean())); sys.stdout.flush()
    return depth, px


if __name__ == '__main__':
    names = sys.argv[1].split(','); sets = sys.argv[2].split(','); eyes = sys.argv[3].split(','); t0 = time.time()
    for nm in names:
        for s in sets:
            for e in eyes:
                dep(nm, s, e)
    print('done %.0f s' % (time.time() - t0))
