"""Judge: the solids for my pictures. python jrender.py <object> <eye front|above> [w h nd]
    balls            the balls object (my recipe, square grid, t = 1.40)
    carry-c1         respace's way A for c = -1        carry-rabbit   the same for the rabbit
    lemon-c1         pinch's way (c), pointed bodies, c = -1          lemon-rabbit   the same for the rabbit
    oneplane-c1      the one-plane rule of the bench for c = -1 (for scale)
-> cache/depth-<object>-<eye>.npz"""
import os, sys, time
import numpy as np
import jlib as J

name, eye = sys.argv[1], sys.argv[2]
w, h, nd = (int(v) for v in sys.argv[3:6]) if len(sys.argv) > 5 else (800, 600, 520)
cam = J.EYES[eye]; t0 = time.time(); os.makedirs(os.path.join(J.HERE, 'cache'), exist_ok=True)
if name == 'balls':
    depth, px = J.render(lambda x, y, z: J.balls(x, y, z, rounds=14) == 1, w, h, nd, cam, depth_half=1.25, log=name + ' ' + eye)
elif name.startswith('carryx-'):                      # the same rule asked point by point (no table): respace's own function
    import jcarry as JC
    body = JC.BODIES[name[7:]]
    depth, px = J.render(lambda x, y, z: JC.C.carried_inside(body, 'A', x, y, z, nmax=80), w, h, nd, cam, depth_half=1.25, log=name + ' ' + eye)
elif name.startswith('carry-'):
    import jcarry as JC
    tab = JC.Tab(name[6:])
    depth, px = J.render(tab.inside, w, h, nd, cam, depth_half=1.25, log=name + ' ' + eye)
elif name.startswith('lemon-'):
    sys.path.insert(0, os.path.join(J.ROOT, 'out', 'r27', 'pinch'))
    import pinchlib as PL, objs
    B = objs.get('tree-' + name[6:]); depth, px = PL.solid(B, w, h, nd, cam, half_w=1.75, refine=8)
elif name == 'oneplane-c1':
    one = J.M.bench('oneplane')
    depth, px = J.render(lambda x, y, z: J.M.stay(one, x, y, z, -1.0, 0.0, 0.0, 40) >= 40, w, h, nd, cam, depth_half=1.25, log=name + ' ' + eye)
else:
    raise SystemExit('unknown object ' + name)
np.savez_compressed(os.path.join(J.HERE, 'cache', 'depth-%s-%s.npz' % (name, eye)), depth=depth, px=px)
print('%s eye %s: %d x %d x %d blocks, %d lines of sight hit, %.0f s' % (name, eye, w, h, nd, int(np.isfinite(depth).sum()), time.time() - t0))
