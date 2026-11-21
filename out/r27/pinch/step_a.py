"""Way (a) and way (b): every copy of a seed under the fitted moves, in the flat plane, against the true flat picture.
    python step_a.py a      one-step moves, three fits, two seeds          -> a-c1.png, a-rabbit.png, step_a.log
    python step_a.py b      the same with the two-step and three-step moves added -> b-c1.png, b-rabbit.png, step_b.log
"""
import sys, time
import numpy as np
import pinchlib as PL, fam

which = sys.argv[1] if len(sys.argv) > 1 else 'a'
W, H = 720, 520
SMALL = (360, 260)


def shrink(img):
    from PIL import Image
    return np.asarray(Image.fromarray(img).resize(SMALL, Image.LANCZOS))


for key, c in PL.CS.items():
    al, be = PL.fixed_points(c); T = PL.true_flat(c, W, H); tiles = []
    seeds = [('ball', ('ball', 0.0 + 0j, abs(al))), ('pointed', ('spin', al, -al, 0.0 + 0j, np.radians(fam.OPEN[key])))]
    print('==== %s; true inside share of the box %.4f' % (PL.NAMES[key], T.mean()))
    sets = [(1,)] if which == 'a' else [(1,), (1, 2), (1, 2, 3)]
    kinds = ('affine', 'osc', 'pin') if which == 'a' else (('osc', 'pin') if which == 'b' else ('affine',))
    for kind in kinds:
        for ns in sets:
            moves = []
            for n in ns:
                mv, sk = PL.fitted(c, n, kind)
                for m in mv:                                             # a longer move that is only a shorter one repeated adds nothing
                    if not any(abs(m['p'] - o['p']) < 1e-7 for o in moves):
                        moves.append(m)
            for sname, seed in seeds:
                t0 = time.time()
                bodies, bad = fam.orbit(moves, seed, rmin=0.004 if len(moves) < 4 else 0.006, cap=60000)
                A = PL.flat_union(bodies, W, H); ws = PL.wrong_share(A, T); ov, nk = fam.overlap_share(bodies)
                tag = '%s fit, steps %s, %s seed' % (kind, '+'.join(str(n) for n in ns), sname)
                print('  %-38s moves %2d bodies %6d (not bounded %d)  wrong verdicts %.1f%% of the true area; inside share %.4f; overlap share %.3f (of %d largest unswallowed)  %.0f s'
                      % (tag, len(moves), len(bodies), bad, 100 * ws, A.mean(), ov, nk, time.time() - t0)); sys.stdout.flush()
                tiles.append((shrink(PL.overlay(A, T)), '%s: wrong %.0f%%, overlap %.0f%%' % (tag, 100 * ws, 100 * ov)))
    cols = 2 if which in ('a', 'baff') else 4
    PL.sheet(tiles, cols, PL.os.path.join(PL.HERE, '%s-%s.png' % (which, key)),
             title='%s, flat cut. Cream: right. Blue: true picture only. Orange: the fitted object only.' % PL.NAMES[key])
    print('wrote %s-%s.png' % (which, key))
