"""Follow-up to t3_first.py, part C: the points of 'first' that lie OUTSIDE the flat set spun.
Are they slow leavers, or a real part of the solid?   -> out/r21/prover/t3b_outside.txt

For 'first' the orbit after the first squaring is the lathe, so it is run here by the closed form (checked against the
library in t3_first.py, part A), with many more steps.  Also part D again with constants that are really outside the flat set.
Orbits that have left are dropped at once, so the long runs are cheap.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R

out = []


def say(t=''):
    print(t); sys.stdout.flush(); out.append(t)


def lathe_count(X, Y, Z, a, b, steps, r2=36.0):
    """Steps survived by the lathe orbit (start point counted as step 1), and the last height of those that never leave."""
    n = np.zeros(X.size, np.int64); zl = np.zeros(X.size); idx = np.arange(X.size)
    a = np.broadcast_to(np.asarray(a, float), X.shape).copy(); b = np.broadcast_to(np.asarray(b, float), X.shape).copy()
    X, Y, Z = X.copy(), Y.copy(), Z.copy()
    keep = X * X + Y * Y + Z * Z < r2; idx, X, Y, Z, a, b = idx[keep], X[keep], Y[keep], Z[keep], a[keep], b[keep]; n[idx] += 1
    for _ in range(steps - 1):
        X, Y, Z = X * X - Y * Y - Z * Z + a, 2 * X * Y + b, 2 * X * Z
        keep = X * X + Y * Y + Z * Z < r2; idx, X, Y, Z, a, b = idx[keep], X[keep], Y[keep], Z[keep], a[keep], b[keep]; n[idx] += 1
        if idx.size == 0:
            break
    zl[idx] = np.abs(Z)
    return n, zl


def flat_count(a, b, steps):
    return lathe_count(a, b, 0 * a, a, b, steps)[0]          # the lathe on the page IS the flat orbit; start point c counted as step 1... see main


def first_start(c):
    """c (n, 3) -> the first point of 'first' and c, both in the frame of c's own sheet (c0 = (a, b, 0), b >= 0)."""
    a = c[:, 0]; b = np.hypot(c[:, 1], c[:, 2]); th = np.arctan2(c[:, 2], c[:, 1])
    r = np.hypot(a, b); f = r * r / np.maximum(r * r + (b * np.sin(th)) ** 2, 1e-300)
    X = a + f * (a * a - (b * np.cos(th)) ** 2); Y = b + 2 * f * b * (a * np.cos(th) ** 2 + r * np.sin(th) ** 2); Z = f * b * (r - a) * np.sin(2 * th)
    return X, Y, Z, a, b


def main():
    t0 = time.time(); rng = np.random.default_rng(21); n = 400000; NMAX = 3000
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    X, Y, Z, a, b = first_start(c)
    nf, _ = lathe_count(X, Y, Z, a, b, NMAX)                 # squarings survived by 'first' (the first point is squaring 1)
    fx, fy = a * a - b * b + a, 2 * a * b + b                 # the flat orbit counted the same way: its first point is c^2 + c
    ng, _ = lathe_count(fx, fy, 0 * fx, a, b, NMAX)
    say("'first', %d random points of the box. Both orbits are counted in squarings survived (escape radius 6)." % n)
    for N in (60, 200, 1000, 3000):
        af, fl = nf >= N, ng >= N
        say('   N = %5d: in the solid %6d (%.3f%% of the box) | in the solid but c0 has left the flat orbit: %5d (%.4f%% of the box) | in the flat set spun but cut away: %6d'
            % (N, af.sum(), 100 * af.mean(), (af & ~fl).sum(), 100 * (af & ~fl).mean(), (fl & ~af).sum()))
    sel = ng < 60
    say('   of the %d points whose c0 leaves the flat orbit within 60 squarings: %d are still in the solid after %d; the longest stay among the rest is %d squarings'
        % (sel.sum(), (nf[sel] >= NMAX).sum(), NMAX, nf[sel][nf[sel] < NMAX].max()))
    sel2 = (ng < 3000) & (nf >= 3000)
    if sel2.any():
        say('   the %d points still in the solid at 3000 whose c0 has left: their c0 left the flat orbit after between %d and %d squarings (median %d)' % (sel2.sum(), ng[sel2].min(), ng[sel2].max(), int(np.median(ng[sel2]))))
    say('   (%.0f s)' % (time.time() - t0)); say()
    say('D again. The lathe, 400,000 random start points (|z| up to 1.2), 1500 steps, constants c in the flat page')
    v = rng.uniform([-1.8, -1.3, -1.2], [1.8, 1.3, 1.2], size=(400000, 3))
    for nm, cc in (('rabbit', M.RABBIT), ('Siegel disc', M.SIEGEL), ('c = -0.4 + 0.3i (main body)', (-0.4, 0.3)), ('c = 0.3 + 0.5i (period-4 bud)', (0.3, 0.5)),
                   ('c = 0.5 + 0.5i', (0.5, 0.5)), ('c = -0.8 + 0.4i', (-0.8, 0.4)), ('c = -0.2 + 0.9i', (-0.2, 0.9)), ('c = 0.33 + 0.07i (main body, near its edge)', (0.33, 0.07)), ('c = 0.32 + 0.02i (in the notch at the cusp)', (0.32, 0.02)), ('dendrite c = i', (0.0, 1.0))):
        fl = bool(lathe_count(np.array([cc[0]]), np.array([cc[1]]), np.array([0.0]), cc[0], cc[1], 3000)[0][0] >= 3000)
        nn, zl = lathe_count(v[:, 0], v[:, 1], v[:, 2], cc[0], cc[1], 1500); alive = nn >= 1500
        if alive.any():
            say('   %-38s c in the flat set: %-5s | stay: %6d (%.2f%%), largest height left: %.1e' % (nm, fl, alive.sum(), 100 * alive.mean(), zl[alive].max()))
        else:
            say('   %-38s c in the flat set: %-5s | stay: 0; the longest stay is %d steps' % (nm, fl, nn.max()))
    say('   (%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 't3b_outside.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
