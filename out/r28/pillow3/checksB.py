"""Round 28, pillow3: the short list of checks for layout B, the upright cut of both layouts, and the user's pictures.

    python out/r28/pillow3/checksB.py > out/r28/pillow3/checksB.log
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import p3, lean, look
M = p3.M
rng = np.random.default_rng(21)
SETS = [('c = -1', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2]), ('c = -0.75', (-0.75, 0.0)), ('Siegel disc', M.SIEGEL[:2])]
rB = lean.rule(50.0); LB = lean.layout(50.0); rA = p3.rule(True)
n = 20000; zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); zero = np.zeros(n)
for nm, c in SETS:
    a = M.stay(rB, zr, zi, zero, c[0], c[1], 0.0, 60) >= 60; b = M.flat_stay(zr, zi, c[0], c[1], 60) >= 60
    print('B 1. flat check %-12s %d of %d verdicts differ' % (nm, int((a != b).sum()), n))
print('B 1. bench flat_check:', M.flat_check(rB, n=20000, steps=60))
p = rng.normal(size=(3, 200000)); p /= np.sqrt((p * p).sum(0)); t = rng.normal(size=p.shape); t -= (t * p).sum(0) * p; t /= np.sqrt((t * t).sum(0))
for hh in (1e-5, 1e-7):
    q = p + hh * t; q /= np.sqrt((q * q).sum(0)); st = np.sqrt(((np.array(LB.G(*q)) - np.array(LB.G(*p))) ** 2).sum(0)) / hh
    print('B 3. 200000 random pairs %.0e apart: stretch median %.2f, 5..95 %% %.2f..%.2f, largest %.1f (a tear would show as about %.0e)' % (hh, np.median(st), np.percentile(st, 5), np.percentile(st, 95), st.max(), 1 / hh))
g = np.array(LB.G(*p)); print('B 4. all finite on 200000 directions: %s; length 1: largest error %.1e' % (bool(np.isfinite(g).all()), np.abs((g * g).sum(0) - 1).max()))
lon = np.linspace(0, 2 * np.pi, 3601)[:-1] + 1e-4; eps = 1e-5
up = np.arcsin(np.array(LB.G(np.cos(eps) * np.cos(lon), np.cos(eps) * np.sin(lon), np.sin(eps) + 0 * lon))[2]) / eps
print('B 5. push off the flat plane (should be 2): %.4f .. %.4f' % (up.min(), up.max()))
st5 = np.sqrt(((np.array(LB.G(*(lambda q: q / np.sqrt((q * q).sum(0)))(p + 1e-5 * t))) - g) ** 2).sum(0)) / 1e-5
t2 = np.cross(p.T, t.T).T; st6 = np.sqrt(((np.array(LB.G(*(lambda q: q / np.sqrt((q * q).sum(0)))(p + 1e-5 * t2))) - g) ** 2).sum(0)) / 1e-5
print('B 7. stretch along two crossed directions at 200000 places: ratio of the larger to the smaller, median %.2f, 90 %% below %.2f, 99 %% below %.2f (a lower bound of the squeeze; layout A by the same measure: see below)' % tuple(np.percentile(np.maximum(st5, st6) / np.minimum(st5, st6), (50, 90, 99))))
gA = np.array(p3.G(*p)); a5 = np.sqrt(((np.array(p3.G(*(lambda q: q / np.sqrt((q * q).sum(0)))(p + 1e-5 * t))) - gA) ** 2).sum(0)) / 1e-5
a6 = np.sqrt(((np.array(p3.G(*(lambda q: q / np.sqrt((q * q).sum(0)))(p + 1e-5 * t2))) - gA) ** 2).sum(0)) / 1e-5
print('A 7. the same measure for layout A: median %.2f, 90 %% below %.2f, 99 %% below %.2f' % tuple(np.percentile(np.maximum(a5, a6) / np.minimum(a5, a6), (50, 90, 99))))
# the upright cut through the x-axis against the flat picture (the same picture turned a quarter round the row)
xr, zz = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
for nm, r in (('A', rA), ('B', rB)):
    for sn, c in SETS[:1] + SETS[2:3]:
        a = M.stay(r, xr, zero, zz, c[0], 0.0, 0.0, 60) >= 60; b = M.flat_stay(xr, zz, c[0], 0.0, 60) >= 60
        print('%s upright cut through the x-axis, %s: %d of %d verdicts differ from the flat picture (inside the flat picture: %d)' % (nm, sn, int((a != b).sum()), n, int(b.sum())))
if len(sys.argv) > 1:
    look.sheet('m1', 0.006, os.path.join(HERE, 'user-1-row.png'), 1.75, ('above', 'edge'), title='The three-corner pillow, c = -1 (the basilica), first layout. Blocks of side 0.006.')
    look.sheet('m1-lean50', 0.006, os.path.join(HERE, 'user-2-row-B.png'), 1.75, ('above', 'edge'), title='The same rule, second layout: the two buds off the flat picture sit at the waist. Blocks of side 0.006.')
    look.sheet('rab', 0.006, os.path.join(HERE, 'user-3-rabbit.png'), 1.5, ('front', 'side'), title='The three-corner pillow, the rabbit, first layout. Blocks of side 0.006.')
