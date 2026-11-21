"""Why the Mandelbrot solid of "Turning plane, along" (a KNOWN rule, solid drawn in round 16) grows a fused lump:
the resting point for c in one of its exact planes, and the three stretch factors there.
In an exact mirror plane the rule is complex squaring, so for c = w - w^2 (w = r e^(i theta) in that plane) the resting
point is w, two factors are the pair 2w, conj(2w) (size 2r), and the third is real: the sideways stretch.
Claim (from the rule, see cliff.py part 2):  third factor = 2 r (1 - psi' (1 - cos theta)), psi' = slope of the
reference plane at that plane: 0 on z = 0 and y = 0 (third = +2r), 2 on the diagonals of "along" (third = 2r (2 cos theta - 1)).
No solid is drawn here. python out/r17/profiles/sideways.py"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen as S
R = S.R
F = R.get('along')
print('rule "along": c = w - w^2 with w = r e^(i theta) placed in the plane; resting point error; sizes of the three factors (measured) | predicted pair, third')
for tag, az, slope in (('flat plane z = 0', 0.0, 0.0), ('diagonal plane', np.pi / 4, 2.0)):
    for th_deg in (60, 90, 120, 150):
        for r in (0.2, 0.4):
            th = np.radians(th_deg); w = r * np.exp(1j * th); c2 = w - w * w
            v = np.array([[w.real, w.imag * np.cos(az), w.imag * np.sin(az)]]); c = np.array([c2.real, c2.imag * np.cos(az), c2.imag * np.sin(az)])
            err = np.abs(np.array(F(*v.T)).ravel() + c - v.ravel()).max()
            ev = np.linalg.eigvals(S.jac(F, v)[0]); ev = ev[np.argsort(-np.abs(ev.imag))]
            third = ev[np.argmin(np.abs(ev.imag))].real; pair = np.abs(ev[0])
            pred3 = 2 * r * (1 - slope * (1 - np.cos(th)))
            print('%-17s theta %3d r %.1f  c = (%+.3f, %+.3f in the plane)  error %.0e   pair %.3f third %+.3f | %.3f %+.3f  %s' % (
                tag, th_deg, r, c2.real, c2.imag, err, pair, third, 2 * r, pred3, 'RESTING POINT REPELS SIDEWAYS although c is inside the flat main body' if abs(third) > 1 and 2 * r < 1 else ''))
print()
print('where the resting point stops attracting, as r on the ray at angle theta (flat main body: r = 0.5 everywhere):')
for th_deg in (60, 90, 120, 150, 170):
    th = np.radians(th_deg); print('  theta %3d: flat plane 0.500 | diagonal plane of "along" %.3f' % (th_deg, 0.5 / max(1.0, abs(2 * np.cos(th) - 1))))
