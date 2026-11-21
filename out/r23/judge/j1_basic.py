"""Round 23, judge, check 1: flat check, lift test, slow leak, dendrite. My loop, my points.

    python out/r23/judge/j1_basic.py [rule,rule,...]

flat check: 20,000 random points of the flat plane; verdicts (stays 60 steps) against the complex orbit, for the Mandelbrot
            set (orbit started at c, first squaring has k = 0) and the Julia sets of c = -1, c = -0.75, rabbit, Siegel disc.
lift test:  flat-inside points (complex orbit, 300 steps) lifted by a millionth; share that stays 150 steps.
leak:       share of a random box (-1.8..1.8, -1.4..1.4, -1.4..1.4; 120,000 points) inside after 30 / 80 / 200 steps.
"""
import sys, time
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import jl as L

names = sys.argv[1].split(',') if len(sys.argv) > 1 else ['oneplane', 'twoplane', 'along', 'alongonce', 'cones', 'cones1', 'cones2', 'd:pillowJ', 'd:lens', 'd:bristor']
rng = np.random.default_rng(23); n = 20000
cr, ci = rng.uniform(-2.1, 0.7, n), rng.uniform(-1.3, 1.3, n)
zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
V = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(120000, 3))
JS = [('c = -1', L.BAS), ('c = -0.75', L.SANMARCO), ('rabbit', L.RABBIT), ('Siegel', L.SIEGEL)]
t0 = time.time()
for nm in names:
    r = L.get(nm); row = []
    # Mandelbrot: one orbit per c, each with its own c -> do it through per-point c
    class PerC:
        pass
    st = tuple(r.init(n)); x, y, z = cr.copy(), ci.copy(), np.zeros(n); alive = np.ones(n, bool); cz = np.zeros(n)
    for k in range(60):
        with np.errstate(all='ignore'):
            o = r.step(x, y, z, st, k, cr, ci, cz)
        x, y, z = o[0] + cr, o[1] + ci, o[2]; st = tuple(o[3])
        bad = ~((x * x + y * y + z * z) < 36.0); alive &= ~bad; x[bad] = 100.0; y[bad] = 0.0; z[bad] = 0.0
    fm = L.flat_stay(cr, ci, (0.0, 0.0), 0) if False else None
    zc = cr + 1j * ci; w = zc.copy(); al = np.ones(n, bool)
    for k in range(60):
        with np.errstate(all='ignore'):
            w = np.where(al, w * w + zc, w)
        al &= (w.real ** 2 + w.imag ** 2) < 36.0
    row.append('M %d' % int((alive != al).sum()))
    for sn, c in JS:
        a = L.stay(r, zr, zi, np.zeros(n), c, 60) >= 60; b = L.flat_stay(zr, zi, c, 60) >= 60
        row.append('%s %d' % (sn, int((a != b).sum())))
    print('%-10s flat check, verdicts that differ of %d: %s' % (nm, n, ', '.join(row))); sys.stdout.flush()
    lift = []; leak = []
    for sn, c in JS:
        ok = L.flat_stay(zr, zi, c, 300) >= 300
        s = L.stay(r, zr[ok], zi[ok], np.full(int(ok.sum()), 1e-6), c, 150) >= 150
        lift.append('%s %d of %d' % (sn, int(s.sum()), int(ok.sum())))
        m = L.stay(r, V[:, 0], V[:, 1], V[:, 2], c, 200)
        leak.append('%s %.4f / %.4f / %.4f' % (sn, (m >= 30).mean(), (m >= 80).mean(), (m >= 200).mean()))
    m = L.stay(r, V[:, 0], V[:, 1], V[:, 2], L.DENDRITE, 80)
    print('           lift test, stay: %s' % '; '.join(lift))
    print('           share of the box inside after 30 / 80 / 200 steps: %s' % '; '.join(leak))
    print('           dendrite c = i: inside after 30 steps %d, after 80 steps %d of %d   [%.0f s]' % (int((m >= 30).sum()), int((m >= 80).sum()), V.shape[0], time.time() - t0)); sys.stdout.flush()
