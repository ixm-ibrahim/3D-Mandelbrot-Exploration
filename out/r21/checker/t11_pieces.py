"""t11: pieces. The inside set on a grid, split into connected pieces (blocks that touch by a face, edge or corner).
Bodies that touch in one point may come out as separate pieces, so the one-plane rule is the yardstick for 'clean'.
Also a check of M.solid against direct verdicts."""
import sys, time
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/checker')
import numpy as np
from scipy import ndimage
import mem as M, ck

sheet, am = ck.load('sheet'), ck.load('alongmem')
N = 141; steps = 80


def grid(rule, c):
    xs = np.linspace(-1.8, 1.8, N); ys = np.linspace(-1.3, 1.3, N); zs = np.linspace(-1.3, 1.3, N)
    out = np.zeros((N, N, N), bool)
    for i in range(0, N, 12):
        X, Y, Z = np.meshgrid(xs[i:i + 12], ys, zs, indexing='ij')
        out[i:i + 12] = M.stay(rule, X, Y, Z, c[0], c[1], c[2], steps) >= steps
    return out, xs, ys, zs


def report(rule, cn, c):
    t0 = time.time(); g, xs, ys, zs = grid(rule, c)
    lab, n = ndimage.label(g, structure=np.ones((3, 3, 3)))
    if n == 0:
        print('  %-14s %-9s empty' % (rule.name, cn)); return
    sizes = ndimage.sum(g, lab, range(1, n + 1)); order = np.argsort(-sizes); tot = sizes.sum()
    cen = ndimage.center_of_mass(g, lab, [int(i) + 1 for i in order[:6]])
    big = ['%.1f%% at (%.2f, %.2f, %.2f)' % (100 * sizes[i] / tot, xs[0] + ce[0] * (xs[1] - xs[0]), ys[0] + ce[1] * (ys[1] - ys[0]), zs[0] + ce[2] * (zs[1] - zs[0])) for i, ce in zip(order[:6], cen)]
    small = sizes < 0.001 * tot
    print('  %-14s %-9s %d pieces; pieces under 0.1%% of the volume: %d, holding %.2f%% of it; biggest: %s  [%.0f s]'
          % (rule.name, cn, n, int(small.sum()), 100 * sizes[small].sum() / tot, '; '.join(big), time.time() - t0)); sys.stdout.flush()


what = sys.argv[1] if len(sys.argv) > 1 else 'pieces'
if what == 'pieces':
    print('grid %d^3 in the box -1.8..1.8 x -1.3..1.3 x -1.3..1.3, %d steps' % (N, steps))
    for r in (M.bench('oneplane'), M.bench('along'), sheet.get('evc005e70k16'), am.get('c_wake1'), am.get('c_wake2'), sheet.get('ease'), sheet.get('vote4'), M.Rule('lag70', '', M.lag(0.7))):
        for cn, c in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', ck.RABBIT), ('Siegel', ck.SIEGEL)):
            report(r, cn, c)
else:
    print('M.solid against direct verdicts, eye straight at the flat page (cam = (0, 0, 1)), 120 x 90 pixels, 120 blocks deep, 40 steps')
    for r, c in ((M.SCOUT[1], (-1.0, 0.0, 0.0)), (M.bench('along'), ck.RABBIT), (sheet.get('evc005e70k16'), None)):
        w, h, nd = 120, 90, 120; hw = 1.7 if c is None else 1.75; ce = (-0.7, 0.0, 0.0) if c is None else (0.0, 0.0, 0.0)
        dep, px = M.solid(r, c, w, h, nd, 40, cam=(0.0, 0.0, 1.0))
        us = np.linspace(-hw, hw, w); vs = np.linspace(hw * h / w, -hw * h / w, h); ds = np.linspace(-hw, hw, nd)
        U, V = np.meshgrid(us, vs); D = ds[:, None, None] + 0 * U[None]
        P = (ce[0] + U[None] + 0 * D, ce[1] + V[None] + 0 * D, ce[2] - D)
        ins = (M.mandel(r, *P, 40) if c is None else M.stay(r, *P, c[0], c[1], c[2], 40)) >= 40
        mine = np.where(ins.any(0), ds[np.argmax(ins, 0)], np.inf)
        print('  %-14s %-10s pixels where the depth differs: %d of %d (hit pixels: %d)' % (r.name, 'Mandelbrot' if c is None else str(c[:2]), int((mine != dep).sum()), w * h, int(np.isfinite(dep).sum())))
