"""The turn. For c = -1 the true tree, with the stretch about the meeting point given a turn tau about the chain
(every body is swung round the x-axis by tau for each undo-move of that kind in its chain). For each tau:
    - the flat cut against the true flat picture (share of the true area with the wrong verdict)
    - how much of the solid lies in two bodies at once (do the swung bodies run into each other?)
    - how much of the flat cut is left off the chain's own bodies (the buds of the flat picture), and where the buds sit round the chain
    (I tried to count buds that come loose from the bud they stand on; the count was not reliable and is not kept.)
    python step_turn.py   -> step_turn.log
"""
import sys
import numpy as np
import pinchlib as PL, objs, fam

c = PL.CS['c1']; T = PL.true_flat(c)
rng = np.random.default_rng(11); n = 400000
X = rng.uniform([-1.8, -1.0, -1.0], [1.8, 1.0, 1.0], size=(n, 3))
for tau in (0.0, 30.0, 60.0, 90.0, 120.0, 137.5, 180.0):
    B = objs.swung_tree(c, tau, objs.BEST['c1'])
    A = PL.flat_union(B); ws = PL.wrong_share(A, T)
    top = B[:400]; S = [fam.samples(b) for b in top]; keep = []
    for i, b in enumerate(top):                                           # bodies swallowed by a larger one do not count as running into it
        if not any(PL.inside(top[j], S[i]).all() for j in keep):
            keep.append(i)
    cnt = np.zeros(n, np.int32)
    for i in keep:
        cen, rad = PL.bound(top[i]); near = ((X - cen) ** 2).sum(1) <= rad * rad
        if near.any():
            cnt[near] += PL.inside(top[i], X[near])
    onaxis = [b for b in B if abs(b[1][1]) + abs(b[1][2]) + abs(b[2][1]) + abs(b[2][2]) < 1e-9]
    inax = np.zeros(n, bool)
    for b in onaxis:
        inax |= PL.inside(b, X)
    offb = [i for i, b in enumerate(B) if not (abs(b[1][1]) + abs(b[1][2]) + abs(b[2][1]) + abs(b[2][2]) < 1e-9)]
    chainflat = PL.flat_union(onaxis); budarea = int((A & ~chainflat).sum()); truebud = int((T & ~chainflat).sum())
    print('turn %6.1f: bodies off the chain %d | flat cut off the chain: %d grid points inside (the true flat picture has %d there)'
          % (tau, len(offb), budarea, truebud))
    off = (cnt >= 1) & ~inax
    r = np.hypot(X[off, 1], X[off, 2]); ang = np.degrees(np.arctan2(X[off, 2], X[off, 1])) % 180.0
    hist = np.histogram(ang, bins=6, range=(0, 180))[0] / max(off.sum(), 1)
    print('turn %6.1f: flat cut wrong %.1f%% of the true area | solid: %.2f%% of it lies in two bodies at once (%d largest unswallowed bodies) | '
          'buds off the chain: %.1f%% of the solid; where they sit round the chain, in six slices of 30 degrees from the flat plane: %s'
          % (tau, 100 * ws, 100.0 * (cnt >= 2).sum() / max((cnt >= 1).sum(), 1), len(keep), 100.0 * off.sum() / max((cnt >= 1).sum(), 1), np.round(100 * hist).astype(int)))
    sys.stdout.flush()
