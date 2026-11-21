"""Judge, check 11: smaller claims, each asked once more with my own points.
 a. respace's flat match (true picture -> the object's flat cut): does the object, asked at the matched point, give the true verdict?
 b. way A: its own mirror image above / below and left / right? merely spun round the x-axis?
 c. the re-spacing fractions <-> halvings: is it the right function, and how hard does it squeeze the biggest bulb and the rim at a kiss?
 d. pinch's turned tree: what the turn does to the flat cut.
"""
import os, sys
import numpy as np
import jlib as J
import jcarry as JC
C = JC.C
rng = np.random.default_rng(2711)

print('== a. the flat match, 30000 random points of the box')
n = 30000; x, y = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); tru = J.truth(x, y, -1.0, 2000)
asis = J.balls(x, y, 0 * x, grid='line', rounds=40) == 1
P, kind = C.Hflat(x + 1j * y, nmax=300)
ok = np.isfinite(P.real) & np.isfinite(P.imag); m = np.zeros(n, bool)
m[ok] = J.balls(P.real[ok], P.imag[ok], 0 * P.real[ok], grid='line', rounds=60) == 1
print('   truly inside %d; the object as it stands: wrong at %d (%.1f of 100 parts of the true area)' % (int(tru.sum()), int((asis != tru).sum()), 100.0 * (asis != tru).sum() / tru.sum()))
print('   the object asked at the matched point: wrong at %d; not settled %d; matched point not a number %d' % (int((m != tru)[kind >= 0].sum()), int((kind < 0).sum()), int((~ok).sum())))

print('== b. way A, 200000 random points (my table)')
for key in ('c1', 'rabbit'):
    tab = JC.Tab(key); p = rng.uniform([-1.8, -1.3, -0.9], [1.8, 1.3, 0.9], size=(200000, 3))
    p[:, 0] = np.rint((p[:, 0] - JC.X0) / JC.STEP) * JC.STEP + JC.X0; p[:, 1] = JC.Y1 - np.rint((JC.Y1 - p[:, 1]) / JC.STEP) * JC.STEP      # on the table's own grid, so that mirrored points are grid points too
    a = tab.inside(p[:, 0], p[:, 1], p[:, 2])
    ud = tab.inside(p[:, 0], p[:, 1], -p[:, 2]); lr = tab.inside(-p[:, 0], p[:, 1], p[:, 2]); fb = tab.inside(p[:, 0], -p[:, 1], p[:, 2]); ht = tab.inside(-p[:, 0], -p[:, 1], p[:, 2])
    ang = rng.uniform(0, 2 * np.pi, len(p)); co, si = np.cos(ang), np.sin(ang)
    sp = tab.inside(p[:, 0], co * p[:, 1] - si * p[:, 2], si * p[:, 1] + co * p[:, 2])
    print('   %-6s inside %d. Verdict changes: above/below %d, left/right %d, up/down in the flat plane %d, half turn in the flat plane %d. Turned by a random angle round the x-axis: %.0f of 100 parts of the solid change'
          % (key, int(a.sum()), int((a != ud).sum()), int((a != lr).sum()), int((a != fb).sum()), int((a != ht).sum()), 100.0 * (a != sp).sum() / a.sum()))
b = J.balls(p[:, 0], p[:, 1], p[:, 2]) == 1; bs = J.balls(p[:, 0], co * p[:, 1] - si * p[:, 2], si * p[:, 1] + co * p[:, 2]) == 1
print('   for scale, the balls object itself turned by a random angle: %.0f of 100 parts change' % (100.0 * (b != bs).sum() / b.sum()))

print('== c. the re-spacing fractions <-> halvings (respace\'s qmark / Psi)')
for p_, q_, want in ((1, 2, '1/2'), (1, 3, '1/4'), (2, 3, '3/4'), (1, 4, '1/8'), (2, 5, '3/8'), (3, 5, '5/8'), (3, 4, '7/8'), (1, 5, '1/16')):
    print('   fraction %d/%d -> %.6f (should be %s = %.6f)' % (p_, q_, float(C.qmark(p_ / q_)), want, eval(want)))
deg = np.pi / 180
print('   the biggest bulb covers the ball angles 77 to 103 degrees (26 degrees); moved to the halvings it has to come from %.1f to %.1f degrees (%.1f degrees)'
      % (float(C.Psi(77 * deg)) / deg, float(C.Psi(103 * deg)) / deg, (float(C.Psi(103 * deg)) - float(C.Psi(77 * deg))) / deg))
for a_ in (20, 10, 5):
    print('   the last %d degrees of a ball\'s rim next to a kiss come from the last %.2g degrees of the true rim next to the pinch' % (a_, float(C.Psi(a_ * deg)) / deg))

print('== d. the turned tree (pinch): flat cut against the true flat picture of c = -1, my grid')
sys.path.insert(0, os.path.join(J.ROOT, 'out', 'r27', 'pinch'))
import pinchlib as PL, objs
gx, gy = J.grid_xy(900, 650); T = J.truth(gx, gy, -1.0, 400)
for tau in (0, 90, 137.5, 180):
    B = objs.get('turn%g-c1' % tau); A = PL.flat_union(B, 900, 650)
    offp = sum(1 for bb in B if abs(bb[1][2]) > 1e-9 or abs(bb[2][2]) > 1e-9)
    print('   turn %5.1f degrees: %d bodies, %d of them with a tip off the flat plane; flat cut wrong %.1f of 100 parts of the true area' % (tau, len(B), offp, 100 * J.wrong_share(A, T)))
