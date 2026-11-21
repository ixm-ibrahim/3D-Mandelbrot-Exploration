"""Skeptic, job 1: try to break Claim S.  python out/r21/skeptic/claimS.py [noise|attempts]
For every attempt: is the flat page exact, is the Mandelbrot solid spun, and is it the lathe's solid point for point?"""
import sys, time
import numpy as np
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

what = sys.argv[1] if len(sys.argv) > 1 else 'all'
SC = {r.name: r for r in M.SCOUT}
LATHE = M.bench('lathe')

if what in ('all', 'noise'):
    print('NOISE LEVEL of M.spun_check (two rules that ARE spun; and four that are not, for scale)')
    for r in (SC['own'], LATHE, SC['fixed'], SC['lag25'], SC['lag75'], M.bench('along')):
        for n, steps, seed in ((40000, 40, 5), (40000, 80, 5), (40000, 160, 5), (200000, 40, 6), (200000, 80, 7)):
            t0 = time.time(); s = M.spun_check(r, n=n, steps=steps, seed=seed)
            print('  %-6s n = %6d steps = %3d: Mandelbrot differs %.4f%% (%d points; inside %.2f%%) | basilica differs %.4f%% (%d points; inside %.2f%%)  %.0f s'
                  % (r.name, n, steps, 100 * s['mandel_differ'], round(s['mandel_differ'] * n), 100 * s['mandel_inside'], 100 * s['basilica_differ'], round(s['basilica_differ'] * n), 100 * s['basilica_inside'], time.time() - t0))
            sys.stdout.flush()

if what in ('all', 'attempts'):
    print('ATTEMPTS (nothing fixed off the x-axis)')
    rng = np.random.default_rng(21); n = 100000
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    lat = {st: M.mandel(LATHE, c[:, 0], c[:, 1], c[:, 2], st) >= st for st in (40, 80)}
    for r in R.ATTEMPTS:
        t0 = time.time()
        f = M.flat_check(r, n=20000)
        s40 = M.spun_check(r, n=40000, steps=40); s80 = M.spun_check(r, n=40000, steps=80)
        d = {st: int(((M.mandel(r, c[:, 0], c[:, 1], c[:, 2], st) >= st) != lat[st]).sum()) for st in (40, 80)}
        print('  %-24s flat page differs: M %d, basilica %d, rabbit %d, Siegel %d of %d (strays %.1e)' % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page']))
        print('  %-24s turned: Mandelbrot differs %.4f%% at 40 steps, %.4f%% at 80 (inside %.2f%%) | basilica differs %.4f%%, %.4f%% (inside %.2f%%)'
              % ('', 100 * s40['mandel_differ'], 100 * s80['mandel_differ'], 100 * s40['mandel_inside'], 100 * s40['basilica_differ'], 100 * s80['basilica_differ'], 100 * s40['basilica_inside']))
        print('  %-24s against the lathe\'s solid, point for point: %d of %d verdicts differ at 40 steps, %d at 80 (lathe inside: %d)   %.0f s' % ('', d[40], n, d[80], int(lat[40].sum()), time.time() - t0))
        sys.stdout.flush()
