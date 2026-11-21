"""t3: the flat picture's cycles, seen from off the page. python out/r22/stability/t3_cycles.py > t3_cycles.txt
For each c and each rule: at every point of the attracting cycle and at the two fixed points, put a test point a small
step eps away (in the page, two directions; straight off the page) and take one full turn of the cycle. Printed: the
distance afterwards divided by eps (under 1 = pulled toward the cycle, over 1 = pushed away), for eps = 1e-3 and 1e-5.
For a cycle that passes through 0 the pull is 'as the square': the number then falls with eps and the column K = distance / eps^2
is the fair comparison."""
import numpy as np
import stab as T

SETS = [('basilica c=-1', T.BAS, 2), ('San Marco c=-0.75', T.MARCO, 1), ('rabbit', T.RABBIT, 3), ('Siegel', T.SIEGEL, 1),
        ('c=-1+0.1i', (-1.0, 0.1, 0.0), 2), ('c=-1+0.2i', (-1.0, 0.2, 0.0), 2)]


def flat_cycle(c, p):
    z = 0j; cc = complex(c[0], c[1])
    for _ in range(20000):
        z = z * z + cc
    pts = [z]
    for _ in range(p - 1):
        pts.append(pts[-1] ** 2 + cc)
    return pts


def turn(F, v, c, p):
    x, y, z = (np.array(t, float) for t in v)
    for _ in range(p):
        X, Y, Z = F(x, y, z); x, y, z = X + c[0], Y + c[1], Z + c[2]
    return x, y, z


for label, c, p in SETS:
    cc = complex(c[0], c[1]); cyc = flat_cycle(c, p)
    lam = np.prod([2 * z for z in cyc])
    disc = np.sqrt(1 - 4 * cc + 0j); fixed = [(1 - disc) / 2, (1 + disc) / 2]
    print('\n== %s: cycle of %d: %s, flat multiplier |lambda| = %.4f; fixed points %s (|2z| = %.3f, %.3f)'
          % (label, p, ' -> '.join('%.4f%+.4fi' % (z.real, z.imag) for z in cyc), abs(lam), ', '.join('%.4f%+.4fi' % (z.real, z.imag) for z in fixed), *(abs(2 * z) for z in fixed)))
    spots = [('cycle point %d' % i, z, p) for i, z in enumerate(cyc)] + [('fixed point alpha (pinch)', fixed[0], 1), ('fixed point beta (tip)', fixed[1], 1)]
    for nm in T.NAMES:
        F = T.rule(nm)
        for sl, z0, per in spots:
            v0 = np.array([z0.real, z0.imag, 0.0])
            row = []
            for eps in (1e-3, 1e-5):
                dirs = {'in page, along x': (1, 0, 0), 'in page, along y': (0, 1, 0), 'off the page': (0, 0, 1)}
                base = np.array(turn(F, v0, c, per))
                for dl, dvec in dirs.items():
                    w = np.array(turn(F, v0 + eps * np.array(dvec), c, per))
                    dist = np.linalg.norm(w - base); offz = abs(w[2] - base[2])
                    row.append((eps, dl, dist / eps, dist / eps ** 2, offz / eps))
            txt = ' | '.join('eps %.0e %s: x%.4f (K %.3g)' % (e, dl[:11], a, k) for e, dl, a, k, o in row if dl != 'in page, along x')
            print('  %-9s %-26s %s' % (nm, sl, txt))

# the upright and the diagonal pages for c on the x-axis: are they kept, and do they pull or push sideways (round the axis)?
print('\n== c on the x-axis: a point just beside each page (0.5 degree round the axis), basilica, 1 to 6 steps: degrees from that page afterwards')
rng = np.random.default_rng(2)
for nm in ('along', 'away', 'oneplane'):
    F = T.rule(nm)
    for page in (0.0, 45.0, 90.0):
        # start points: inside points of the flat picture, put on the page, then turned 0.5 degree off it
        zr, zi = rng.uniform(-1.6, 1.6, 40000), rng.uniform(0.02, 1.0, 40000)
        ok = T.M.flat_stay(zr, zi, -1.0, 0.0, 200) >= 200; zr, zi = zr[ok], zi[ok]
        a = np.radians(page + 0.5); x, y, z = zr.copy(), zi * np.cos(a), zi * np.sin(a)
        line = []
        for k in range(6):
            X, Y, Z = F(x, y, z); x, y, z = X - 1.0, Y, Z
            rho = np.hypot(y, z); far = rho > 1e-3
            dev = (np.degrees(np.arctan2(z, y)) - page + 90) % 180 - 90
            line.append('%.2f/%.2f/%.1f' % (np.median(np.abs(dev[far])), np.percentile(np.abs(dev[far]), 90), np.abs(dev[far]).max()))
        print('  %-9s page %4.1f (%5d flat-inside starts): median/90th/max turn away after 1..6 steps: %s' % (nm, page, ok.sum(), '  '.join(line)))
