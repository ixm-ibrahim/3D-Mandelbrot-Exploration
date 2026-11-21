"""Numbers behind the notes of the section "vahlen". python out/r25/vahlen/measure.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V
M = V.M
rng = np.random.default_rng(11)


def same_as_lathe():
    """For c on the x-axis the carried spinor never leaves the no-k family, so spin-V is the Lathe."""
    n = 200000; q = rng.uniform(-1, 1, size=(3, n)) * np.array([[1.8], [1.4], [1.4]])
    for nm, c in (('c = -1', (-1.0, 0.0, 0.0)), ('c = -0.75', (-0.75, 0.0, 0.0)), ('rabbit', M.RABBIT)):
        a = M.stay(V.spin('V'), q[0], q[1], q[2], c[0], c[1], c[2], 40) >= 40; b = M.stay(V.R_lathe(), q[0], q[1], q[2], c[0], c[1], c[2], 40) >= 40
        print('spin-V against the Lathe, %-9s: verdicts that differ %d of %d (inside: spin %d, lathe %d)' % (nm, int((a != b).sum()), n, int(a.sum()), int(b.sum())))


def thickness():
    """Flat points that stay, lifted off the flat plane by a height t: the share that still stays."""
    n = 200000; zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    for nm, c in (('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.12+0.6i (rabbit bulb, not the centre)', (-0.12, 0.60, 0.0)), ('Siegel disc', M.SIEGEL)):
        ins = M.flat_stay(zr, zi, c[0], c[1], 200) >= 200; x, y = zr[ins], zi[ins]
        print('%s: %d flat points inside' % (nm, x.size))
        for r in (V.R_one(), V.R_holo(), V.R_lathe(), V.spin('V'), V.spin('up')):
            row = []
            for t in (1e-8, 1e-5, 1e-3, 1e-2, 5e-2):
                row.append((M.stay(r, x, y, np.full_like(x, t), c[0], c[1], c[2], 200) >= 200).mean())
            print('   %-10s share still inside at height 1e-8, 1e-5, 1e-3, 1e-2, 5e-2: %s' % (r.name, ' '.join('%.3f' % s for s in row)))


def origin_tear():
    """Near the origin the carried phase depends on the DIRECTION the orbit comes in from, not on how near it is.
    Start at eps * d, d at latitude lat; one step; report where the NEXT square lands (it should be near c^2)."""
    c = M.RABBIT; one = np.ones(1)
    r = V.spin('V')
    print('rabbit: the point c squared is (%.3f, %.3f, 0)' % (c[0] * c[0] - c[1] * c[1], 2 * c[0] * c[1]))
    for eps in (1e-2, 1e-4, 1e-8):
        for lat in (0.0, 1.0, 10.0, 45.0):
            for lon in (20.0, 110.0):
                la, lo = np.radians(lat), np.radians(lon)
                x, y, z = eps * np.cos(la) * np.cos(lo) * one, eps * np.cos(la) * np.sin(lo) * one, eps * np.sin(la) * one
                X, Y, Z, st = r.step(x, y, z, r.init(1), 0, c[0] * one, c[1] * one, 0 * one)
                x1, y1, z1 = X + c[0], Y + c[1], Z + c[2]
                X2, Y2, Z2, st2 = r.step(x1, y1, z1, st, 1, c[0] * one, c[1] * one, 0 * one)
                print('   start %.0e from the origin, latitude %4.1f, longitude %5.1f: after c, the next square is (%.3f, %.3f, %.3f)' % (eps, lat, lon, X2[0], Y2[0], Z2[0]))


def heights():
    """How tall is the main body over its centre (c = -1)? One plane against holo."""
    t = np.linspace(0, 1.5, 3001)
    for r in (V.R_one(), V.R_holo()):
        ins = M.stay(r, 0 * t, 0 * t, t, -1.0, 0.0, 0.0, 200) >= 200
        print('%-10s c = -1: the upright axis stays up to height %.3f' % (r.name, t[ins].max()))


if __name__ == '__main__':
    same_as_lathe(); heights(); origin_tear(); thickness()
