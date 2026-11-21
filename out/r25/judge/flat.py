"""Judge, round 25: the flat check, my own (own seed, own boxes, own true orbit, 80 steps), and each rule's speed.

    python out/r25/judge/flat.py name [name ...]
"""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jl
M = jl.M


def check(name, n=30000, steps=80, seed=2511):
    r = jl.get(name); power = 3 if name == 'cube' else 2
    rng = np.random.default_rng(seed); zero = np.zeros(n); out = []
    t0 = time.time()
    # Mandelbrot set of the power
    cr, ci = rng.uniform(-2.2, 1.0, n), rng.uniform(-1.5, 1.5, n)
    a = M.mandel(r, cr, ci, zero, steps) >= steps; b = jl.flat_true(cr, ci, cr, ci, steps, power) >= steps
    out.append(('M', int((a != b).sum()), int(b.sum())))
    sets = [('c1', jl.SETS['c1']), ('rabbit', jl.SETS['rabbit']), ('c075', jl.SETS['c075']), ('siegel', jl.SETS['siegel']),
            ('rabbit-mirror', jl.SETS['rabbit-mirror']), ('c=-0.12+0.6i', (-0.12, 0.6, 0.0)), ('c=0.28+0.53i', (0.28, 0.53, 0.0)), ('c=i', (0.0, 1.0, 0.0))]
    if power == 3:
        sets = [('c=i', jl.SETS['ci']), ('c3b', jl.SETS['c3b']), ('c=0.3', (0.3, 0, 0)), ('c=-0.2+1.08i', (-0.2, 1.08, 0)), ('c=0.59i', (0, 0.59, 0))]
    zr, zi = rng.uniform(-1.9, 1.9, n), rng.uniform(-1.5, 1.5, n)
    for nm, c in sets:
        a = M.stay(r, zr, zi, zero, c[0], c[1], 0.0, steps) >= steps; b = jl.flat_true(zr, zi, c[0], c[1], steps, power) >= steps
        out.append((nm, int((a != b).sum()), int(b.sum())))
    dt = time.time() - t0
    # does one squaring keep a flat point on the flat plane, and is it the flat square there?
    st = tuple(r.init(n)); c = jl.SETS['rabbit']
    X, Y, Z, st = r.step(zr, zi, zero, st, 0, np.full(n, c[0]), np.full(n, c[1]), zero)
    w = (zr + 1j * zi) ** power
    fin = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z)
    err = float(np.nanmax(np.hypot(X - w.real, Y - w.imag)[fin] / (1 + np.abs(w[fin])))); offp = float(np.nanmax(np.abs(Z[fin])))
    print('%-12s differ / inside of %d: %s | one step: worst error %.1e, off the plane %.1e, not finite %d | %.0f s' % (
        name, n, '  '.join('%s %d/%d' % t for t in out), err, offp, int((~fin).sum()), dt))
    sys.stdout.flush()


def speed(name, n=200000, steps=30):
    r = jl.get(name); rng = np.random.default_rng(1); v = rng.uniform(-1.6, 1.6, size=(3, n)); t0 = time.time()
    c = jl.SETS['ci'] if name == 'cube' else jl.SETS['c1']
    ins = M.stay(r, v[0], v[1], v[2], c[0], c[1], c[2], steps) >= steps
    print('%-12s speed: %d points, %d steps, %.1f s; share of the box inside %.4f' % (name, n, steps, time.time() - t0, ins.mean())); sys.stdout.flush()


if __name__ == '__main__':
    for nm in sys.argv[1:]:
        try:
            check(nm); speed(nm)
        except Exception as e:
            import traceback; traceback.print_exc(); print(nm, 'FAILED', e); sys.stdout.flush()
