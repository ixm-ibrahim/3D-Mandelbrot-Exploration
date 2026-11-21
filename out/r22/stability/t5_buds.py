"""t5: does the stretch of the step predict the SHAPE of a bud? python out/r22/stability/t5_buds.py > t5_buds.txt
Basilica. The bud on the middle body in the direction phi (turn round the x-axis from the flat page) is the set of points that
one step carries into the body round -1.414 on the x-axis. Its middle is the point (0, 0.6436 cos phi, 0.6436 sin phi)
whenever that point lies in the page it is squared in. Measured, point by point (200 steps): how far the solid reaches
from that middle outward / inward (away from the axis), along x, and round the axis; and the three stretches of the step there.
If the bud is the body seen through the step, its width in a direction is the body's width divided by the stretch."""
import numpy as np
import stab as T
M = T.M

C = T.BAS; RHO = float(np.sqrt(np.sqrt(2.0) - 1.0)); STEPS = 200


def reach(r, p0, d, hmax=0.4, n=4001):
    t = np.linspace(0, hmax, n)
    ins = M.stay(r, p0[0] + t * d[0], p0[1] + t * d[1], p0[2] + t * d[2], *C, STEPS) >= STEPS
    if ins.all():
        return hmax
    return t[np.argmin(ins)]


print('bud middle at distance %.4f from the x-axis (its image is %.4f on the x-axis)' % (RHO, -1 - RHO ** 2))
for nm in ('oneplane', 'along', 'away', 'lathe'):
    r = M.bench(nm); F = T.rule(nm)
    for phi in (0.0, 22.5, 45.0, 67.5, 90.0):
        a = np.radians(phi); p0 = np.array([0.0, RHO * np.cos(a), RHO * np.sin(a)])
        inside = M.stay(r, *p0, *C, STEPS) >= STEPS
        X, Y, Z = F(*(np.array([t]) for t in p0)); land = (X[0] - 1, Y[0], Z[0])
        J = T.jac(F, *p0); s, det = T.stretch(J)
        e_out = np.array([0.0, np.cos(a), np.sin(a)]); e_x = np.array([1.0, 0, 0]); e_rnd = np.array([0.0, -np.sin(a), np.cos(a)])
        st = [np.linalg.norm(J @ e) for e in (e_out, e_x, e_rnd)]
        if inside:
            w = [reach(r, p0, e) + reach(r, p0, -e) for e in (e_out, e_x, e_rnd)]
            txt = 'bud size: outward %.4f, along x %.4f, round the axis %.4f -> round-the-axis / outward = %.2f' % (w[0], w[1], w[2], w[2] / w[0])
        else:
            txt = 'NOT inside: no bud here'
        print('%-9s phi %5.1f: lands at (%.3f, %.3f, %.3f) | stretch outward %.3f, along x %.3f, round the axis %.3f (det %+d; longest/shortest %.2f) | %s'
              % (nm, phi, *land, *st, det, s[0] / s[2], txt))

# the same for the bud ON a bud and for buds on the side bodies: follow the orbit, multiply the stretches up
print('\n== second generation: points that need TWO steps to reach the axis body. Bud on the left body (round x = -1): its middle is a point whose image is a first bud middle')
print('   (found by a search on the circle x = x1, distance d from the axis; printed: where the solid has matter on that circle, as arcs of the turn phi)')
for nm in ('along', 'oneplane', 'away'):
    r = M.bench(nm)
    for (x1, d) in ((0.0, RHO), (-1.0, 0.33), (1.0, 0.33), (-1.0, 0.25), (0.0, 0.55), (0.0, 0.70)):
        ph = np.radians(np.arange(0, 360, 0.05))
        ins = M.stay(r, np.full_like(ph, x1), d * np.cos(ph), d * np.sin(ph), *C, STEPS) >= STEPS
        if ins.all() or not ins.any():
            print('%-9s circle x = %+.2f, d = %.3f: %s' % (nm, x1, d, 'all inside' if ins.all() else 'nothing inside')); continue
        k0 = int(np.argmin(ins)); ins2 = np.roll(ins, -k0); edges = np.flatnonzero(ins2[1:] != ins2[:-1]) + 1
        starts = edges[::2]; ends = edges[1::2] if len(edges) % 2 == 0 else np.append(edges[1::2], len(ins2))
        arcs = [(((s + k0) * 0.05) % 360, (e - s) * 0.05) for s, e in zip(starts, ends)]
        big = [a for a in arcs if a[1] >= 1.0]; thin = [a for a in arcs if a[1] < 1.0]
        print('%-9s circle x = %+.2f, d = %.3f: %d arcs at least 1 degree wide: %s | %d thinner than 1 degree (thinnest %.2f): at %s'
              % (nm, x1, d, len(big), ' '.join('%.1f(+%.1f)' % a for a in big[:16]), len(thin), min([a[1] for a in thin], default=0), ' '.join('%.1f' % a[0] for a in thin[:24])))
