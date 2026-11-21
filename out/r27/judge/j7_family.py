"""Judge, check 7: the dials of the balls object (measure's "rungs" and "sideways slide"), tested another way.

Measure tested a setting by listing balls and looking for overlapping pairs. I test it by asking the recipe itself:
if a setting gives an honest object (balls that only touch), then moving a point by any of the object's own moves
(a slide by a whole number, one of the two sphere inversions) cannot change its verdict. Where balls would cut into
each other the recipe contradicts itself, and the count below is not 0.
Points: 60000 random points between floor and ceiling, in the object's own coordinates. 300 rounds."""
import sys
import numpy as np
import jlib as J

rng = np.random.default_rng(2707); n = 60000


def shift_vecs(grid):
    if grid in ('line', 'square', 'hex'):
        e = [(1.0, 0.0)] + ([(0.0, 1.0)] if grid == 'square' else []) + ([(0.5, J.S3 / 2)] if grid == 'hex' else [])
    elif grid == 'line2':
        e = [(2.0, 0.0)]
    else:
        e = [(1.0, 1.0), (1.0, -1.0)]
    return e


def test(t, grid, slide=(0.0, 0.0), rounds=300):
    top = 2 * t
    m = np.c_[rng.uniform(-2, 2, n), rng.uniform(-2, 2, n) if grid not in ('line', 'line2') else rng.uniform(-0.6, 0.6, n), rng.uniform(0.0, top, n)]
    v0 = J.balls(m[:, 0], m[:, 1], m[:, 2], t=t, grid=grid, rounds=rounds, slide=slide, raw=True)

    def lo(p):
        return p / (p * p).sum(1, keepdims=True)

    def hi(p):
        c = np.array([slide[0], slide[1], top]); d = p - c; return c + d / (d * d).sum(1, keepdims=True)
    moves = [('floor inversion', lo(m)), ('ceiling inversion', hi(m))]
    for e in shift_vecs(grid):
        s = np.array([e[0], e[1], 0.0])
        moves.append(('slide, floor inversion', lo(m + s))); moves.append(('slide, ceiling inversion', hi(m + s)))
        moves.append(('floor inv., slide, ceiling inv.', hi(lo(m) + s)))
    bad = 0; und = int((v0 == 0).sum()); tot = 0
    for nm, p in moves:
        ok = np.isfinite(p).all(1) & (np.abs(p).max(1) < 1e6)
        v1 = J.balls(p[ok, 0], p[ok, 1], p[ok, 2], t=t, grid=grid, rounds=rounds, slide=slide, raw=True)
        both = (v0[ok] != 0) & (v1 != 0); bad += int((v0[ok] != v1)[both].sum()); und += int((v1 == 0).sum()); tot += int(both.sum())
    return bad, tot, und, float((v0 == 1).mean()), float((v0 == -1).mean())


print('== the dial t (no slide). "contradictions" = verdicts that change under one of the object\'s own moves')
for grid in ('line2', 'square2', 'square'):
    for t, nm in ((2.5, ''), (1.4, 'lab'), (1.0, ''), (0.95, 'between'), (np.cos(np.pi / 8), 'rung of 8'), (0.89, 'between'), (np.cos(np.pi / 6), 'rung of 6'), (0.84, 'between'),
                  (np.cos(np.pi / 5), 'rung of 5'), (0.76, 'between'), (np.cos(np.pi / 4), 'rung of 4'), (0.6, 'between'), (0.5, 'rung of 3')):
        bad, tot, und, ins, out = test(t, grid)
        print('   %-8s t = %.4f %-10s contradictions %6d of %d; undecided %6d; inside share %.3f, outside share %.3f' % (grid, t, nm, bad, tot, und, ins, out))
    sys.stdout.flush()
print('== the sideways slide of the upper sphere, t = 1.15')
for grid, slides in (('line', [(0, 0), (0.5, 0), (0.25, 0), (0.1, 0)]), ('square', [(0, 0), (0.5, 0), (0.5, 0.5), (0.25, 0), (0.25, 0.25), (0.3, 0.1)]),
                     ('square2', [(0.3, 0), (1.0, 0), (0.37, 0.21)]), ('line2', [(0.3, 0), (0.5, 0), (1.0, 0)])):
    for s in slides:
        bad, tot, und, ins, out = test(1.15, grid, slide=s)
        print('   %-8s slide (%.2f, %.2f): contradictions %6d of %d; undecided %6d; inside share %.3f, outside share %.3f' % (grid, s[0], s[1], bad, tot, und, ins, out))
    sys.stdout.flush()
print('== the ring of three, t = 0.5: the three big bodies')
print('   floor (mz < 0), ceiling (mz > 1) and the ball of radius 0.5 about (0, 0, 0.5): the ball touches the floor at (0,0,0) and the ceiling at (0,0,1);')
print('   floor and ceiling are two flat-sided bodies that touch each other only at the far point. Three bodies, kissing two at a time.')
d = rng.normal(size=(20000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
for eps in (1e-3, 1e-6):
    pi = np.array([0, 0, 0.5]) + 0.5 * (1 - eps) * d; po = np.array([0, 0, 0.5]) + 0.5 * (1 + eps) * d
    vi = J.balls(pi[:, 0], pi[:, 1], pi[:, 2], t=0.5, grid='square2', rounds=300, raw=True); vo = J.balls(po[:, 0], po[:, 1], po[:, 2], t=0.5, grid='square2', rounds=300, raw=True)
    print('   shell at 1 -/+ %g of that ball: inside shell not inside %d of 20000; outside shell: outside %d, in a kissing ball %d, undecided %d' % (eps, int((vi != 1).sum()), int((vo == -1).sum()), int((vo == 1).sum()), int((vo == 0).sum())))
