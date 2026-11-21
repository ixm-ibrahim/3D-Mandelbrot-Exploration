"""Round 28, skeptic of Track B: numbers taken from random points in space, with no grid and no mirror assumed.

    PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -W ignore out/r28/skeptic/sk_sample.py > out/r28/skeptic/sample.log

1. the rabbit against its mirror image          2. the half turn about the upright axis (left against right)
3. does the solid hold when the orbit is followed longer (40 / 100 / 200 steps)
4. the meeting place of the middle body and its neighbours: is it one point?
5. my blocks against the explorer's kept blocks (c = -1, first build), if mine exist
"""
import os, sys, time
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, HERE)
import sk_vox
rng = np.random.default_rng(404); T0 = time.time()
RAB = sk_vox.RABBIT; FA = sk_vox.step_fn('A'); FB = sk_vox.step_fn('B')


def say(*a):
    print(*a); sys.stdout.flush()


def ball_pts(n, R):
    p = rng.normal(size=(3, n)); p /= np.sqrt((p * p).sum(0)); return p * R * rng.uniform(0, 1, n) ** (1 / 3)


ins = sk_vox.inside_pts
# 1. the rabbit against its mirror image
p = ball_pts(300000, 1.51); a = ins(FA, p[0], p[1], p[2], RAB, 40); b = ins(FA, p[0], -p[1], p[2], (RAB[0], -RAB[1]), 40)
say('1. rabbit against the mirror image of the solid of the mirrored c, 300000 random points: %d verdicts differ (inside: %d)' % (int((a != b).sum()), int(a.sum())))
# 2. the half turn
c = ins(FA, -p[0], -p[1], p[2], RAB, 40)
say('2. rabbit, first build: half turn about the upright axis: inside %d, inside after the turn %d, verdicts that differ %d = %.1f %% of the inside (the explorer\'s way of counting); share of the solid outside its turned copy %.1f %%'
    % (int(a.sum()), int(c.sum()), int((a != c).sum()), 100 * (a != c).sum() / a.sum(), 100 * (a & ~c).sum() / a.sum()))
c = ins(FA, p[0], p[1], -p[2], RAB, 40); say('   rabbit, mirror in the flat plane (above against below): %d verdicts differ' % int((a != c).sum()))
for nm, F, N in (('first build', FA, 600000), ('second build', FB, 250000)):
    p = ball_pts(N, 1.63); a = ins(F, p[0], p[1], p[2], (-1.0, 0.0), 40); c = ins(F, -p[0], -p[1], p[2], (-1.0, 0.0), 40); m = ins(F, p[0], p[1], -p[2], (-1.0, 0.0), 40); my = ins(F, p[0], -p[1], p[2], (-1.0, 0.0), 40)
    say('2. c = -1, %s, %d random points: inside %d (volume %.4f); half turn about the upright axis: %d verdicts differ = %.1f %% of the inside (+- %.1f); outside its turned copy %.1f %%; mirror in the flat plane: %d differ; mirror in the upright plane through the x-axis: %d differ'
        % (nm, N, int(a.sum()), a.mean() * 4 / 3 * np.pi * 1.63 ** 3, int((a != c).sum()), 100 * (a != c).sum() / a.sum(), 100 * np.sqrt((a != c).sum()) / a.sum(), 100 * (a & ~c).sum() / a.sum(), int((a != m).sum()), int((a != my).sum())))
    say('   [%.0f s]' % (time.time() - T0))
# 3. longer orbits
for nm, F, cc, R, N in (('c = -1, first build', FA, (-1.0, 0.0), 1.63, 600000), ('rabbit, first build', FA, RAB, 1.51, 600000), ('c = -1, second build', FB, (-1.0, 0.0), 1.63, 200000)):
    p = ball_pts(N, R); a40 = ins(F, p[0], p[1], p[2], cc, 40); q = p[:, a40]; a100 = ins(F, q[0], q[1], q[2], cc, 100); a200 = ins(F, q[0], q[1], q[2], cc, 200); a20 = ins(F, p[0], p[1], p[2], cc, 20)
    say('3. %s, %d random points: inside after 20 steps %d, 40 steps %d, 100 steps %d, 200 steps %d: the solid loses %.2f %% of its volume from 40 to 100 steps and %.2f %% from 40 to 200'
        % (nm, N, int(a20.sum()), int(a40.sum()), int(a100.sum()), int(a200.sum()), 100 * (1 - a100.sum() / a40.sum()), 100 * (1 - a200.sum() / a40.sum())))
    say('   [%.0f s]' % (time.time() - T0))
# 4. the meeting places on the row, c = -1: a small disc across the row at the meeting point, at three sizes
al = 0.5 * (1 - np.sqrt(5))                                               # -0.618...: where the middle body meets its left neighbour
for nm, F in (('first build', FA), ('second build', FB)):
    for x0, lab in ((al, 'left meeting point x = -0.618034'), (-al, 'right meeting point x = +0.618034')):
        out = []
        for rad in (0.05, 0.005, 0.0005, 0.00005):
            g = (np.arange(120) + 0.5) / 120 * 2 * rad - rad; Y, Z = np.meshgrid(g, g); ok = Y * Y + Z * Z < rad * rad
            v = ins(F, np.full(ok.sum(), x0), Y[ok], Z[ok], (-1.0, 0.0), 80); out.append('radius %.0e: %.3f' % (rad, v.mean()))
        say('4. %s, disc across the row at the %s, share of the disc that is inside (80 steps): %s' % (nm, lab, '; '.join(out)))
        # along the row, a thin tube round it: where is the tube free of the solid?
        xs = np.linspace(x0 - 0.02, x0 + 0.02, 81); out = []
        for rad in (0.002,):
            u = rng.uniform(0, 2 * np.pi, 300)
            fr = [ins(F, np.full(300, x), rad * np.cos(u), rad * np.sin(u), (-1.0, 0.0), 80).mean() for x in xs]
            fr = np.array(fr); say('   ring of radius %.3f round the row, share inside, x from %.3f to %.3f in steps of 0.0005: lowest %.2f at x = %.4f; share above 0.99 at both ends: %s'
                                    % (rad, xs[0], xs[-1], fr.min(), xs[fr.argmin()], bool(fr[0] > 0.99 and fr[-1] > 0.99)))
    say('   [%.0f s]' % (time.time() - T0))
# 5. my blocks against the explorer's kept blocks
try:
    mine, xs, ys, zs = sk_vox.load('A-m1', 0.006)
    d = np.load(os.path.join(ROOT, 'out', 'r28', 'pillow3', 'cache', 'm1-0.006.npz')); sh = tuple(d['shape']); th = np.unpackbits(d['ins'])[:int(np.prod(sh))].reshape(sh).astype(bool)
    if not bool(d['full']):
        th = np.concatenate([th[:, :, ::-1], th], 2)
    if bool(d['quarter']):
        th = np.concatenate([th[:, ::-1], th], 1)
    say('5. c = -1, first build, blocks of side 0.006: mine (every block computed) %s with %d inside; the explorer\'s (a quarter computed, the rest mirrored) %s with %d inside; blocks that differ: %s'
        % (mine.shape, int(mine.sum()), th.shape, int(th.sum()), int((mine != th).sum()) if mine.shape == th.shape else 'shapes differ'))
except Exception as e:
    say('5. not done:', repr(e))
