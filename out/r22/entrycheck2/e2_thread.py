"""Round 22, entrycheck second pass: what is the "thin branching thread" of Pulled plane for c = (-1, 0, 0.3)?
c = (-1, 0, 0.3) lies in the plane y = 0, the second plane in which Pulled plane (nearly) shows the flat picture, and
there it is the flat c = -1 + 0.3i, which lies OUTSIDE the flat Mandelbrot set (0.3 from -1; the disc there has radius 0.25):
a c whose flat picture has no inside at all (the trap named in the briefing).
  python out/r22/entrycheck2/e2_thread.py -> thread.txt
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

PP = J.get('sheet.evc005e70k16'); AO = J.get('alongmem.c_wake1')
out = []
def say(t):
    out.append(t); print(t); sys.stdout.flush()

def flat(zr, zi, cr, ci, steps, r2=4096.0):
    z = zr + 1j * zi; c = cr + 1j * ci; n = np.zeros(z.shape, int); alive = np.ones(z.shape, bool)
    with np.errstate(all='ignore'):
        for _ in range(steps):
            z = z * z + c; alive &= (z.real ** 2 + z.imag ** 2) < r2; n += alive; z = np.where(alive, z, 0)
    return n

W, H = 720, 560
xs = -1.8 + 3.6 * (np.arange(W) + 0.5) / W; zs = -1.4 + 2.8 * (np.arange(H) + 0.5) / H
gx, gz = np.meshgrid(xs, zs)
for steps in (40, 80):
    f = flat(gx, gz, -1.0, 0.3, steps) >= steps
    p = M.stay(PP, gx, np.zeros_like(gx), gz, -1.0, 0.0, 0.3, steps, r2=4096.0) >= steps
    say('%d steps, the plane y = 0, %d x %d points: the flat picture of c = -1 + 0.3i keeps %d; Pulled plane with c = (-1, 0, 0.3) keeps %d; they differ at %d' % (steps, W, H, f.sum(), p.sum(), (f != p).sum()))
rng = np.random.default_rng(99); N = 400000
x = rng.uniform(-1.8, 1.8, N); y = rng.uniform(-1.4, 1.4, N); z = rng.uniform(-1.4, 1.4, N)
n = M.stay(PP, x, y, z, -1.0, 0.0, 0.3, 40, r2=4096.0); k = n >= 40
say('Pulled plane, c = (-1, 0, 0.3), %d random points of the box: %d stay 40 steps; their distance from the plane y = 0: median %.3f, largest %.3f; from the plane z = 0: median %.3f' % (N, k.sum(), np.median(np.abs(y[k])) if k.any() else 0, np.abs(y[k]).max() if k.any() else 0, np.median(np.abs(z[k])) if k.any() else 0))
# the same question for the rabbit's c turned 10 degrees: is its slab near the flat page or near c's own page?
a = np.radians(10); c = (-0.122561, 0.744862 * np.cos(a), 0.744862 * np.sin(a))
n = M.stay(PP, x, y, z, *c, 40, r2=4096.0); k = n >= 40
d_own = np.abs(-np.sin(a) * y + np.cos(a) * z)   # distance from c's own page (the plane through the x-axis and c)
say('Pulled plane, rabbit c turned 10 degrees: %d stay 40 steps; distance from c\'s own page: median %.3f, largest %.3f; from the flat page: median %.3f' % (k.sum(), np.median(d_own[k]) if k.any() else 0, d_own[k].max() if k.any() else 0, np.median(np.abs(z[k])) if k.any() else 0))
open(os.path.join(HERE, 'thread.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
