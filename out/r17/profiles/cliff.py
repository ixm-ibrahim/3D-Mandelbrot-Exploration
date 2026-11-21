"""Two rule measurements (no iteration, no solids).
1. The cliff: how far apart the rule sends two points that are a given gap apart, worst case over 400,000 pairs on the
   unit sphere straddling a diagonal plane (y = z). A smooth gentle rule: about 2 x gap. A tear: stays large as the gap shrinks.
2. Sideways stretch on the special planes: next to the plane z = 0 and next to the diagonal plane, the stretch across
   the plane divided by the stretch within it (1 = keeps angles, 0 = squashed flat, negative = turned inside out),
   against the formula  sigma = 1 - (d psi / d phi) (1 - x / r).
python out/r17/profiles/cliff.py"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screen as S
R = S.R
rng = np.random.default_rng(11)
n = 400000
th = np.arccos(rng.uniform(-1, 1, n)); x = np.cos(th); rho = np.sin(th)
print('1. the cliff: largest distance between the answers for two points a gap apart, across the diagonal plane (radius 1)')
names = ['lathe', 'along', 'away', 'p_tt1', 'p_tt4', 'p_tt16', 'p_tt64', 'p_tt256', 'p_tt1024', 'p_aw_tt256', 'twoplane']
gaps = [1e-1, 1e-2, 1e-3, 1e-4, 1e-6, 1e-9]
print('%-11s ' % 'rule' + ' '.join('gap %-7.0e' % g for g in gaps))
for nm in names:
    F = R.get(nm); row = []
    for g in gaps:
        d = g / 2 / np.maximum(rho, 1e-12)           # half the gap as an angle round the axis
        d = np.minimum(d, 0.7)
        a = np.stack(F(x, rho * np.cos(np.pi / 4 - d), rho * np.sin(np.pi / 4 - d)), 1)
        b = np.stack(F(x, rho * np.cos(np.pi / 4 + d), rho * np.sin(np.pi / 4 + d)), 1)
        row.append(np.linalg.norm(a - b, axis=1).max())
    print('%-11s ' % nm + ' '.join('%-11.3g' % v for v in row), flush=True)

print()
print('2. sideways stretch over in-plane stretch, at x / r = 0.5, 0, -0.5, -0.9 (measured | formula with the measured slope of psi)')
def sideways(F, u, phi0, h=1e-6):
    rho = np.sqrt(1 - u * u)
    def at(phi):
        return np.array(F(np.array([u]), np.array([rho * np.cos(phi)]), np.array([rho * np.sin(phi)]))).ravel()
    n_out = None
    d = (at(phi0 + h) - at(phi0 - h)) / (2 * h) / rho          # per unit length sideways
    # in-plane stretch: along the plane's own circle
    th = np.arccos(u)
    def at2(t):
        return np.array(F(np.array([np.cos(t)]), np.array([np.sin(t) * np.cos(phi0)]), np.array([np.sin(t) * np.sin(phi0)]))).ravel()
    e = (at2(th + h) - at2(th - h)) / (2 * h)
    w = at(phi0); nrm = np.cross(w, e); nrm /= np.linalg.norm(nrm)   # across the image plane
    # sign: positive if the sideways direction keeps its side (compare with the lathe at u > 0, which is +)
    side_in = np.array([0.0, -np.sin(phi0), np.cos(phi0)])
    return float(np.dot(d, nrm) / np.linalg.norm(e)), float(np.linalg.norm(d) / np.linalg.norm(e)), nrm, side_in
for nm in ['oneplane', 'lathe', 'along', 'p_cot', 'p_lin', 'p_n8', 'p_tt16']:
    F = R.get(nm); out = []
    for phi0, tag in ((0.0, 'plane z = 0'), (np.pi / 4, 'diagonal')):
        vals = []
        for u in (0.5, 0.0, -0.5, -0.9):
            s, mag, nrm, side = sideways(F, u, phi0)
            vals.append('%+.2f' % (mag * np.sign(s) * np.sign(np.dot(nrm, side)) if abs(s) > 1e-9 else 0.0))
        out.append('%s: %s' % (tag, ' '.join(vals)))
    print('%-9s %s' % (nm, ' | '.join(out)), flush=True)
