"""Judge, check 6: the pinch explorer's objects (lists of bodies from out/r27/pinch/objs.py), measured my way.
 - flat cut against MY true flat picture on MY grid (900 x 650): wrong share of the true area
 - share of the covered flat area that lies in two or more bodies (all bodies counted, also swallowed ones)
 - does anything stand off the flat plane? every body is asked on the plane z = 0 and at mirrored points above / below
 - way (a), c = -1: is there any body off the x-axis (a bud)?
"""
import os, sys, time
import numpy as np
import jlib as J
sys.path.insert(0, os.path.join(J.ROOT, 'out', 'r27', 'pinch'))
import pinchlib as PL, objs

W, H = 900, 650
gx, gy = J.grid_xy(W, H)
TR = {'c1': J.truth(gx, gy, -1.0, 400), 'rabbit': J.truth(gx, gy, J.RABBIT, 400)}
rng = np.random.default_rng(2706)
for name in ('tree-c1', 'tree-rabbit', 'treetrue-c1', 'treetrue-rabbit', 'treeball-c1', 'treeball-rabbit', 'abest-c1', 'abest-rabbit', 'pin-c1', 'pin-rabbit'):
    t0 = time.time(); key = name.rsplit('-', 1)[1]; B = objs.get(name); T = TR[key]
    A = PL.flat_union(B, W, H); cnt = np.zeros((H, W), np.int32)
    for b in B[:1500]:
        cnt += PL.flat_union([b], W, H)
    # off the flat plane: tips and axis of every body
    zmax = 0.0; off_axis = 0
    for b in B:
        if b[0] == 'ball':
            zmax = max(zmax, abs(b[1][2])); off_axis += abs(b[1][1]) > 1e-9
        else:
            zmax = max(zmax, abs(b[1][2]), abs(b[2][2]), abs(b[3][2])); off_axis += (abs(b[1][1]) > 1e-9) or (abs(b[2][1]) > 1e-9)
    # mirror test in space: 60000 random points near the solid
    p = rng.uniform([-1.8, -1.3, 0.0], [1.8, 1.3, 0.7], size=(60000, 3)); up = np.zeros(len(p), bool); dn = np.zeros(len(p), bool)
    q = p * np.array([1, 1, -1.0])
    for b in B[:1500]:
        up |= PL.inside(b, p); dn |= PL.inside(b, q)
    print('%-16s %5d bodies | flat cut wrong: %.1f of 100 parts of the true area | in two or more bodies: %.1f of 100 parts of the covered area | '
          'tips or axes off the flat plane: %.1e | above and below differ at %d of %d inside points | bodies with a tip off the x-axis: %d | %.0f s'
          % (name, len(B), 100 * J.wrong_share(A, T), 100.0 * (cnt >= 2).sum() / max((cnt >= 1).sum(), 1), zmax, int((up != dn).sum()), int(up.sum()), off_axis, time.time() - t0))
    sys.stdout.flush()
# how long against how wide is a pointed body with a given opening (measured on the body itself)
for th in (55.2, 70.0, 39.9, 60.0):
    b = PL.spindle(np.array([-1.0, 0, 0]), np.array([1.0, 0, 0]), np.array([0.0, 0, 0]), np.radians(th))
    ys = np.linspace(0, 3, 300001); ins = PL.inside(b, np.stack([0 * ys, ys, 0 * ys], -1)); half = ys[ins].max()
    print('pointed body, opening %.0f degrees at each tip: %.2f times as long as wide' % (2 * th, 1.0 / half))
