"""Check of the one-line form of the known rules on the sphere of directions.
w = (y + i z) / (r + x)  (0 at the +x direction, infinity at -x, the flat plane is the real line).
Claim: direction of F(v) is  w' = 2 w / (1 - mu |w|^2)  with
   lathe mu = 1;  one plane mu = e^(2 i phi);  other plane mu = -e^(2 i phi);
   along mu = e^(i sin(4 phi) / 2);  away mu = e^(i (4 phi - sin(4 phi) / 2)),   phi = arg w."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, HERE)
import rules as R, myrules as M
rng = np.random.default_rng(5); V = rng.normal(size=(200000, 3)); V /= np.linalg.norm(V, axis=1)[:, None]
V = V[(V[:, 0] > -0.999)]
x, y, z = V.T; w = (y + 1j * z) / (1 + x); phi = np.angle(w); t2 = np.abs(w) ** 2
MU = {'lathe': np.ones_like(phi), 'oneplane': np.exp(2j * phi), 'P2 (other plane)': -np.exp(2j * phi),
      'along': np.exp(0.5j * np.sin(4 * phi)), 'away': np.exp(1j * (4 * phi - 0.5 * np.sin(4 * phi)))}
for nm, mu in MU.items():
    F = M.P2 if nm.startswith('P2') else R.get(nm)
    X, Y, Z = F(x, y, z); n = np.sqrt(X * X + Y * Y + Z * Z); X, Y, Z = X / n, Y / n, Z / n
    wp = 2 * w / (1 - mu * t2)                       # predicted
    a2 = np.abs(wp) ** 2
    Xp, Yp, Zp = (1 - a2) / (1 + a2), 2 * wp.real / (1 + a2), 2 * wp.imag / (1 + a2)
    err = np.sqrt((X - Xp) ** 2 + (Y - Yp) ** 2 + (Z - Zp) ** 2)
    print('%-18s largest difference between the rule and the one-line form on %d directions: %.1e' % (nm, len(x), np.nanmax(err)))
