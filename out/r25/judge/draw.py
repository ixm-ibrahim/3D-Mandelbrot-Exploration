"""Judge, round 25: rough solids at finer blocks and more steps than the sections used, one panel per job.

    python out/r25/judge/draw.py job [job ...]      job = rule:set:tilt:eye     eye = a (front) | top (from above) | under (from behind)

Each panel: 440 x 330 pixels, 280 blocks deep, 40 steps (pearl tree: 14 rounds). Depth maps are kept in cache/.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jl, measure as MS
M = jl.M
CACHE = MS.CACHE
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'under': (0.45, 0.5, -1.0)}
W, Hh, ND, STEPS = 440, 330, 280, 40


def path(spec):
    return os.path.join(CACHE, 'd-%s.npz' % spec.replace(':', '-'))


def panel(spec, force=False):
    f = path(spec)
    if os.path.exists(f) and not force:
        d = np.load(f); return d['depth'], float(d['px'])
    name, setname, tilt, eye = spec.split(':'); r = MS.get(name); c = MS.cval(setname, float(tilt)); t0 = time.time()
    steps = 14 if name.startswith('pearl') else STEPS
    depth, px = M.solid(r, c, W, Hh, ND, steps, cam=EYES[eye])
    np.savez_compressed(f, depth=depth, px=px)
    print('%s  %.0f s, pixels hit %d' % (spec, time.time() - t0, int(np.isfinite(depth).sum()))); sys.stdout.flush()
    return depth, px


if __name__ == '__main__':
    for spec in sys.argv[1:]:
        try:
            panel(spec)
        except Exception as e:
            import traceback; traceback.print_exc(); print(spec, 'FAILED', e); sys.stdout.flush()
