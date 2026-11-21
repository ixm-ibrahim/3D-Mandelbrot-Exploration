"""Way (c): the bodies of the true flat picture, each replaced by a ball or by a body pointed at both ends, placed
where the true undo-moves put the meeting point, its twin and 0. Flat cuts against the true flat picture.
    python step_c.py      -> c-c1.png, c-rabbit.png, step_c.log
"""
import sys, time
import numpy as np
from PIL import Image
import pinchlib as PL, fam

W, H = 720, 520


def shrink(img):
    return np.asarray(Image.fromarray(img).resize((480, 347), Image.LANCZOS))


for key, c in PL.CS.items():
    T = PL.true_flat(c, W, H); t0 = time.time(); L = fam.true_tree(c, smin=0.005)
    sz = np.abs(L[:, 0] - L[:, 1])
    print('==== %s: %d bodies of the true picture down to size 0.005 (largest %.3f), %.0f s' % (PL.NAMES[key], L.shape[0], sz[0], time.time() - t0))
    tiles = []; res = {}
    for th in list(range(30, 91, 5)) + [fam.OPEN[key]]:
        B = fam.tree_bodies(L, 'spin', th); A = PL.flat_union(B, W, H); res[th] = (PL.wrong_share(A, T), A, B)
        print('   pointed bodies, half opening %5.1f: %5d bodies, wrong verdicts %.1f%% of the true area, inside share %.4f, %.2f times as long as wide'
              % (th, len(B), 100 * res[th][0], A.mean(), 1 / np.tan(np.radians(th) / 2))); sys.stdout.flush()
    best = min((k for k in res if k != fam.OPEN[key]), key=lambda k: res[k][0])
    for nm in ('ball', 'ballc'):
        B = fam.tree_bodies(L, nm); A = PL.flat_union(B, W, H); ws = PL.wrong_share(A, T); ov, nk = fam.overlap_share(B)
        print('   %s: wrong verdicts %.1f%% of the true area, inside share %.4f, overlap share %.3f (%d largest unswallowed)' % (nm, 100 * ws, A.mean(), ov, nk))
        if nm == 'ball':
            tiles.append((shrink(PL.overlay(A, T)), 'a ball for every body: wrong %.0f%%, overlap %.0f%%' % (100 * ws, 100 * ov)))
    for th, cap in ((fam.OPEN[key], 'pointed, true opening'), (best, 'pointed, best opening')):
        ws, A, B = res[th]; ov, nk = fam.overlap_share(B)
        print('   chosen: half opening %.1f: wrong %.1f%%, overlap share %.3f (%d largest unswallowed)' % (th, 100 * ws, ov, nk))
        tiles.append((shrink(PL.overlay(A, T)), '%s (%.0f deg): wrong %.0f%%, overlap %.0f%%' % (cap, 2 * th, 100 * ws, 100 * ov)))
    PL.sheet(tiles, 3, PL.os.path.join(PL.HERE, 'c-%s.png' % key),
             title='%s, flat cut of the tree built directly (true layout). Cream: right. Blue: true picture only. Orange: the built tree only.' % PL.NAMES[key])
    print('wrote c-%s.png' % key)
