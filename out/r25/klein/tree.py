"""Round 25, section klein, part 2: the Kleinian basilica in 3D ("the pearl tree").

Not a rule "square, then add c". It is the picture of a GROUP of sphere inversions and whole-number shifts, the way
the paper's Figure 4 (top) is. In the group's own coordinates m = (mx, my, mz):

    the lower half of space  mz < 0   is one body (a ball seen from a point on its skin),
    the upper part           mz > 2t  is the body that touches it (at the far point),
    shifts:      m -> m + n,  n a whole number of the lattice  (the line Z, the Gaussian integers Z[i], or the
                 Eisenstein integers Z[w]) lying in the plane mz = 0,
    inversions:  in the unit sphere about (0, 0, 0)   and in the unit sphere about (0, 0, 2t).

A point is INSIDE if some chain of these moves brings it into mz < 0 or mz > 2t. The chain is found by the oldest
recipe there is (the one behind continued fractions): shift to the nearest whole number, invert if inside a unit
sphere, repeat. A point that ends between the two planes and outside both unit spheres is OUTSIDE for good.
For t >= 1 this is a discrete group (Klein-Maskit combination: two copies of the lattice group glued along the shifts),
so the recipe is exact and the bodies are exact balls that touch two at a time.

The picture frame: one sphere inversion (centre (0, 0, 1), radius k) makes every body a finite ball: the middle ball
is k^2 wide, its two big neighbours k^2 / (2t - 1), and the chain ends at x = +-(k^2 / (t + sqrt(t^2 - 1) - 1) + k^2 / 2).
k^2 = 1.05, t = 1.40 is the best fit to the true basilica (c = -1). Picture x = along the chain, picture y = up in
the flat plane, picture z = out of the flat plane.

    python out/r25/klein/tree.py check        flat cut of the 3D trees against the flat tree; against the true basilica
    python out/r25/klein/tree.py cuts         tree-cuts.png
    python out/r25/klein/tree.py solids a|top tree-solids-a.png / tree-solids-top.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

K2 = 1.05                                 # the two dials of the picture, set where the flat cut is nearest the true
T0 = 1.40                                 # basilica (tree.py check: 39.7% of the true area still gets the wrong verdict)
S3 = np.sqrt(3.0)


def nearest(lattice, mx, my):
    """The point moved by a whole number of the lattice to the cell round 0."""
    if lattice == 'line':
        return mx - np.round(mx), my
    if lattice == 'gauss':
        return mx - np.round(mx), my - np.round(my)
    b0 = np.round(my / (S3 / 2)); a0 = np.round(mx + b0 / 2)                 # eisen: try the 9 lattice points round a first guess
    bx, by, bd = mx, my, np.full(np.shape(mx), np.inf)
    for db in (-1, 0, 1):
        for da in (-1, 0, 1):
            b = b0 + db; a = a0 + da; px = mx - (a - b / 2); py = my - b * S3 / 2; d = px * px + py * py
            m = d < bd; bx = np.where(m, px, bx); by = np.where(m, py, by); bd = np.where(m, d, bd)
    return bx, by


def to_model(x, y, z, k2):
    ux, uy, uz = y, z, x - k2 / 2                                             # the picture point, seen from the inversion centre
    d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    return k2 * ux / d, k2 * uy / d, 1 + k2 * uz / d


def tree(lattice='gauss', t=T0, k2=K2, name=None, label=None):
    top = 2 * t

    def step(x, y, z, st, k, cx, cy, cz):
        mx, my, mz = to_model(x, y, z, k2) if k == 0 else (x, y, z)
        inside = (mz < 0) | (mz > top)
        mx, my = nearest(lattice, mx, my)
        rb = mx * mx + my * my + mz * mz; rt = mx * mx + my * my + (mz - top) ** 2
        inb = rb < 1; itp = (rt < 1) & ~inb; out = ~inside & ~inb & ~itp
        sb = 1 / np.where(rb > 0, rb, 1.0); stp = 1 / np.where(rt > 0, rt, 1.0)
        nx = np.where(inb, mx * sb, np.where(itp, mx * stp, mx)); ny = np.where(inb, my * sb, np.where(itp, my * stp, my))
        nz = np.where(inb, mz * sb, np.where(itp, top + (mz - top) * stp, mz))
        inside |= (nz < 0) | (nz > top)
        nx, ny = nearest(lattice, nx, ny)
        nx = np.where(inside, 0.0, np.where(out, np.nan, nx)); ny = np.where(inside, 0.0, np.where(out, np.nan, ny)); nz = np.where(inside, -1.0, np.where(out, np.nan, nz))
        return nx - cx, ny - cy, nz - cz, st                                  # the library adds c; the tree has no c
    nm = {'line': 'pearl tree, one plane', 'gauss': 'pearl tree, Gaussian integers', 'eisen': 'pearl tree, Eisenstein integers'}[lattice]
    return M.Rule(name or nm, label or '', step, init=lambda n: ())


ZERO = (0.0, 0.0, 0.0)


def flat_inside(rule, u, s, steps=40):
    return M.stay(rule, u, s, np.zeros_like(u), 0.0, 0.0, 0.0, steps) >= steps


def check():
    rng = np.random.default_rng(7); n = 200000
    u, s = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    ref = flat_inside(tree('line'), u, s)
    print('flat tree: share of the box inside %.4f' % ref.mean())
    for lat in ('gauss', 'eisen'):
        a = flat_inside(tree(lat), u, s)
        print('flat cut of the 3D tree (%s) against the flat tree: %d verdicts differ of %d' % (lat, int((a != ref).sum()), n))
    # how deep must the recipe go? share still undecided after k rounds
    zz = rng.uniform(-1.3, 1.3, n); b = M.stay(tree('gauss'), u, s, zz, 0.0, 0.0, 0.0, 80) >= 80
    for k in (4, 8, 14, 40):
        a = M.stay(tree('gauss'), u, s, zz, 0.0, 0.0, 0.0, k) >= k
        print('   3D, %2d rounds: inside %.4f (80 rounds: %.4f), %d verdicts differ' % (k, a.mean(), b.mean(), int((a != b).sum())))
    # against the true basilica
    tru = M.flat_stay(u, s, -1.0, 0.0, 300) >= 300
    print('true basilica: share of the box inside %.4f' % tru.mean())
    print('flat tree against the true basilica (k2 = %.4f, t = %.4f): wrong verdicts %.1f%% of the true area' % (K2, T0, 100.0 * (ref != tru).sum() / tru.sum()))
    from scipy import ndimage
    gu, gs = np.meshgrid(np.linspace(-1.8, 1.8, 720), np.linspace(1.3, -1.3, 520)); px = 3.6 / 719
    A = flat_inside(tree('line'), gu, gs); Bt = M.flat_stay(gu, gs, -1.0, 0.0, 300) >= 300
    print('   furthest apart: %.3f' % max((ndimage.distance_transform_edt(~A) * px)[Bt].max(), (ndimage.distance_transform_edt(~Bt) * px)[A].max()))
    best = (1e9, 0, 0)
    for k2 in np.linspace(1.0, 1.5, 11):
        for t in np.linspace(1.0, 2.0, 21):
            a = flat_inside(tree('line', t=t, k2=k2), u[:60000], s[:60000], 30); e = (a != tru[:60000]).sum() / tru[:60000].sum()
            best = min(best, (e, k2, t))
    print('best fit of the two dials: wrong verdicts %.1f%% of the true area at k2 = %.3f, t = %.3f' % (100 * best[0], best[1], best[2]))
    for t in (1.0, T0, 1.25, 1.5, 2.0):
        a = flat_inside(tree('line', t=t), u, s, 30); f = np.sqrt(t * t - 1)
        print('   t = %.3f: wrong verdicts %.1f%% of the true area; neighbour %.3f wide (true 0.654); chain ends at x = +-%.3f (true 1.618)'
              % (t, 100.0 * (a != tru).sum() / tru.sum(), K2 / (2 * t - 1), (K2 / (t + f - 1) + K2 / 2) if t > 1 else float('inf')))


def cuts():
    w, h, steps, pad = 520, 376, 40, 8
    rows = [('flat cut (z = 0)', 0.0), ('upright cut through the x-axis', 90.0), ('cut turned 45 degrees', 45.0)]
    cols = [tree('line'), tree('gauss'), tree('eisen')]
    W = pad + (len(cols) + 1) * (w + pad); H = 34 + len(rows) * (h + 8)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 6), 'Cuts through the x-axis. Left: true basilica (flat picture, and the one-plane rule off it). Then the pearl trees.', fill=(240, 240, 245), font=M.font(16))
    one = M.bench('oneplane')
    for i, (rn, ang) in enumerate(rows):
        y = 34 + i * (h + 8)
        im.paste(Image.fromarray(M.shade(M.cut_axis(one, ang, w, h, 60, c=(-1.0, 0.0, 0.0)), 60)), (pad, y)); d.text((pad + 4, y + 2), 'one plane, c = -1, ' + rn, fill=(150, 160, 175), font=M.font(13))
        for j, r in enumerate(cols):
            x = pad + (j + 1) * (w + pad)
            im.paste(Image.fromarray(M.shade(M.cut_axis(r, ang, w, h, steps, c=ZERO), steps)), (x, y)); d.text((x + 4, y + 2), r.name + ', ' + rn, fill=(150, 160, 175), font=M.font(13))
    im.save(os.path.join(HERE, 'tree-cuts.png')); print('wrote tree-cuts.png', im.size)


def solids(tag, nd=200, w=440, h=330, steps=14):
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'end': (1.0, 0.25, 0.3)}[tag]
    objs = [tree('line'), tree('gauss'), tree('eisen')]
    pad = 10; W = pad + len(objs) * (w + pad); H = 44 + h + 8
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    d.text((pad, 10), 'The pearl trees (rough blocks, eye at %s)' % (cam,), fill=(240, 240, 245), font=M.font(20))
    for j, r in enumerate(objs):
        dep, px = M.solid(r, ZERO, w, h, nd, steps, cam=cam); x = pad + j * (w + pad)
        im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, 44)); d.text((x + 6, 48), r.name, fill=(150, 160, 175), font=M.font(13))
        print('solid', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'tree-solids-%s.png' % tag)); print('wrote tree-solids-%s.png' % tag)


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if a == 'check':
        check()
    elif a == 'cuts':
        cuts()
    else:
        solids(sys.argv[2] if len(sys.argv) > 2 else 'a')
