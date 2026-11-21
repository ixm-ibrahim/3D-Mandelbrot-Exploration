"""Round 25, fromc: the numbers.   python out/r25/fromc/check.py [names,comma,separated]

For every rule: flat check (20,000 points, 60 steps), lift test (flat-inside points lifted by a millionth must stay),
all-finite test, share of a box that is inside at 30 / 90 steps for c = -1 and the rabbit.
For 'spin': how many verdicts differ from the quaternion square (lathe), for c = -1 and for the rabbit, and the spun check.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)]


def lift_test(rule, c, n=20000, steps=60, lift=1e-6, seed=7):
    rng = np.random.default_rng(seed); zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    ins = M.flat_stay(zr, zi, c[0], c[1], 200) >= 200
    zr, zi = zr[ins], zi[ins]
    st = M.stay(rule, zr, zi, np.full(zr.size, lift), c[0], c[1], c[2], steps) >= steps
    return int(st.sum()), int(zr.size)


def box_share(rule, c, steps, n=120000, seed=11):
    rng = np.random.default_rng(seed); q = rng.uniform(-1, 1, size=(3, n)) * np.array([[1.8], [1.4], [1.4]])
    return float((M.stay(rule, q[0], q[1], q[2], c[0], c[1], c[2], steps) >= steps).mean()), q


def main(names):
    for nm in names:
        t0 = time.time(); r = R.get(nm); print('\n== %s | %s' % (r.name, r.label))
        f = M.flat_check(r, n=20000, steps=60)
        print('   flat check: verdicts that differ of %d: Mandelbrot %d, c = -1 %d, rabbit %d, Siegel %d; strays off the plane %.1e'
              % (f['of'], f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['off_the_page']))
        for sn, c in SETS:
            a, b = lift_test(r, c); s30, q = box_share(r, c, 30); s90, _ = box_share(r, c, 90)
            print('   %-7s lift test %d of %d stay | inside share of the box at 30 / 90 steps: %.4f / %.4f' % (sn, a, b, s30, s90))
        rng = np.random.default_rng(4); p = rng.normal(size=(3, 20000)); zero = np.zeros(20000)
        out = r.step(p[0], p[1], p[2], tuple(r.init(20000)), 0, zero - 0.12, zero + 0.74, zero)
        print('   all finite on 20,000 random points: %s   (%.0f s)' % (bool(np.isfinite(out[0] + out[1] + out[2]).all()), time.time() - t0))
        sys.stdout.flush()
    if 'spin' in names:
        sp, la = R.get('spin'), R.get('lathe')
        for sn, c in SETS + [('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel', M.SIEGEL)]:
            rng = np.random.default_rng(21); q = rng.uniform(-1, 1, size=(3, 200000)) * np.array([[1.8], [1.4], [1.4]])
            a = M.stay(sp, q[0], q[1], q[2], c[0], c[1], c[2], 60) >= 60; b = M.stay(la, q[0], q[1], q[2], c[0], c[1], c[2], 60) >= 60
            print('   spin against the quaternion square, %-9s: %d of %d verdicts differ (inside: spin %d, quaternion square %d)' % (sn, int((a != b).sum()), a.size, int(a.sum()), int(b.sum())))
        s = M.spun_check(sp, n=40000)
        print('   spin, turned round the x-axis: Mandelbrot solid differs %.3f %%, c = -1 differs %.3f %%' % (100 * s['mandel_differ'], 100 * s['basilica_differ']))
    if any(n.endswith('m') or n.startswith('face') or n == 'm4' for n in names):
        print('\n== sideways stretch of the patterns (2 = shape-keeping with length squared)')
        for key, G in (('m = 3, t = -0.268', R.mdir(3, -0.268)), ('m = 4, t = -0.20', R.mdir(4, -0.20)), ('m = 6, t = -0.10', R.mdir(6, -0.10))):
            lats = np.array([0.0, 10, 20, 30, 40, 50, 60, 70, 80, 89])
            for lon in (0.0, 22.5, 45.0):
                s = R.stretch_of(G, lats, 0 * lats + lon)
                print('   %-18s longitude %5.1f, latitudes 0..89: %s' % (key, lon, ' '.join('%.2f' % v for v in s)))


if __name__ == '__main__':
    main(sys.argv[1].split(',') if len(sys.argv) > 1 else ['spin', 'prod', 'axis_every', 'axis_once', 'axis_cycle', 'face4', 'face4m'])
