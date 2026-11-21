"""Round 27, respace: the numbers behind the five tests and the mirror test, for the carried object.

    python tests5.py flat      flat cut against the true flat picture (20000 points), c = -1 and the rabbit
    python tests5.py mirror    mirror images and "spun round a line"
    python tests5.py blocks    pieces, needles, share of the solid off the middle ball family (c = -1, way A)
"""
import sys, time
import numpy as np
from scipy import ndimage
import carry as C
M = C.M
SETS = [('c = -1', C.BASILICA), ('rabbit', C.RABBIT)]


def flat():
    rng = np.random.default_rng(27); n = 20000
    u, s = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); z0 = np.zeros(n)
    for nm, B in SETS:
        tru = M.flat_stay(u, s, B.c.real, B.c.imag, 600) >= 600
        for way in ('A', 'B', 'C', 'F'):
            a = C.carried_inside(B, way, u, s, z0, nmax=300)
            up = C.carried_inside(B, way, u[tru], s[tru], np.full(tru.sum(), 1e-6), nmax=300)
            print('%-7s way %s: flat cut, wrong verdicts %d of %d (truly inside %d); inside points lifted by a millionth that are lost: %d'
                  % (nm, way, (a != tru).sum(), n, tru.sum(), (~up).sum()))
        sys.stdout.flush()


def mirror():
    rng = np.random.default_rng(11); n = 150000
    p = rng.uniform([-1.8, -1.3, -0.9], [1.8, 1.3, 0.9], size=(n, 3)).T
    ang = rng.uniform(0, 2 * np.pi, n); co, si = np.cos(ang), np.sin(ang)
    for nm, B in SETS:
        for way in ('A', 'B'):
            a = C.carried_inside(B, way, p[0], p[1], p[2])
            ud = C.carried_inside(B, way, p[0], p[1], -p[2])
            ht = C.carried_inside(B, way, -p[0], -p[1], p[2])
            lr = C.carried_inside(B, way, -p[0], p[1], p[2])
            fb = C.carried_inside(B, way, p[0], -p[1], p[2])
            sp = C.carried_inside(B, way, p[0], co * p[1] - si * p[2], si * p[1] + co * p[2])
            print('%-7s way %s: inside %d of %d. Differs from its mirror image: above/below %d, half turn in the flat plane %d, left/right %d, up/down in the flat plane %d. '
                  'Turned by a random angle round the x-axis: %.1f%% of the solid differs (0 = merely spun)'
                  % (nm, way, a.sum(), n, (a != ud).sum(), (a != ht).sum(), (a != lr).sum(), (a != fb).sum(), 100.0 * (a != sp).sum() / max(a.sum(), 1)))
            sys.stdout.flush()
    t = C.tree_inside(p[0], p[1], p[2]); ts = C.tree_inside(p[0], co * p[1] - si * p[2], si * p[1] + co * p[2])
    print('the balls object itself: turned by a random angle: %.1f%% of the solid differs' % (100.0 * (t != ts).sum() / t.sum()))
    one = M.bench('oneplane'); o = M.stay(one, p[0], p[1], p[2], -1.0, 0.0, 0.0, 40) >= 40
    os_ = M.stay(one, p[0], co * p[1] - si * p[2], si * p[1] + co * p[2], -1.0, 0.0, 0.0, 40) >= 40
    print('one plane, c = -1 (a spun flat picture, for scale): %.1f%% differs' % (100.0 * (o != os_).sum() / o.sum()))


def blocks():
    t0 = time.time()
    for nm, B in SETS:
        for way in ('A', 'B'):
            nx, ny, nz = 360, 260, 130
            xs, ys, zs = np.linspace(-1.8, 1.8, nx), np.linspace(-1.3, 1.3, ny), np.linspace(0.0, 1.3, nz)
            occ = np.zeros((nz, ny, nx), bool)
            for k in range(nz):
                X, Y = np.meshgrid(xs, ys); occ[k] = C.carried_inside(B, way, X, Y, np.full_like(X, zs[k]), nmax=48)
            lab, cnt = ndimage.label(occ, structure=np.ones((3, 3, 3)))
            sizes = np.bincount(lab.ravel())[1:]; big = np.sort(sizes)[::-1]
            flatlab, fc = ndimage.label(occ[0], structure=np.ones((3, 3)))
            touching = np.unique(lab[0][occ[0]]); loose = np.setdiff1d(np.arange(1, cnt + 1), touching)
            top = zs[np.flatnonzero(occ.any((1, 2))).max()]
            col = occ.sum(0) * (zs[1] - zs[0])                               # height of the solid over each flat point
            print('%-7s way %s (%d x %d x %d blocks above the flat plane): %d pieces by blocks; pieces that do not reach the flat plane: %d holding %.2f%% of the blocks; '
                  'highest inside block at %.2f; blocks above height 0.8: %.3f%% of the solid  (%.0f s)'
                  % (nm, way, nx, ny, nz, cnt, len(loose), 100.0 * sizes[loose - 1].sum() / occ.sum() if len(loose) else 0.0, top,
                     100.0 * occ[zs > 0.8].sum() / occ.sum(), time.time() - t0))
            sys.stdout.flush()


if __name__ == '__main__':
    {'flat': flat, 'mirror': mirror, 'blocks': blocks}[sys.argv[1]]()
