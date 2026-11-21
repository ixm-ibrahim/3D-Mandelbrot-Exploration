"""Hunter: does the choice of cone decide whether the period-2 body under the main body touches at ONE point?
Level cut at the touching height z = -0.75, 0.2 wide: at a clean point contact nothing but the centre point may stay
bounded. For each cone (full lathe inside b1 degrees of the axis, one-plane rule beyond b2) and both versions
(string: cone round -z only; updown: both cones) print how much of the cut stays bounded and how far from the axis."""
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R
P = R.get('oneplane')
def g(t): return np.where(t > 0, np.exp(-1.0 / np.maximum(t, 1e-12)), 0.0)
def make(b1, b2, both):
    B1, B2 = np.radians(b1), np.radians(b2)
    def F(x, y, z):
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); rr = np.maximum(r, 1e-300)
        ca = (np.abs(z) if both else -z) / rr
        beta = np.arccos(np.clip(ca, -1, 1)); t = np.clip((beta - B1) / (B2 - B1), 0, 1)
        s = g(1 - t) / (g(t) + g(1 - t))
        sg = np.where(z > 0, -1.0, 1.0) if both else 1.0
        X1, Y1, Z1 = P(x, y, z); X2, Y2, Z2 = sg * 2 * z * x, sg * 2 * z * y, sg * (z * z - x * x - y * y)
        X, Y, Z = (1 - s) * X1 + s * X2, (1 - s) * Y1 + s * Y2, (1 - s) * Z1 + s * Z2
        n = np.sqrt(X * X + Y * Y + Z * Z); k = np.where(n > 0, r2 / np.maximum(n, 1e-300), 0.0)
        return X * k, Y * k, Z * k
    return F
if __name__ == '__main__':
    out = {}; a = np.linspace(-0.1, 0.1, 141); A, B = np.meshgrid(a, a); rad = np.hypot(A, B)
    for both in (False, True):
        for b1, b2 in ((30, 50), (15, 30), (45, 60), (55, 75), (65, 85)):
            F = make(b1, b2, both)
            per = K.periods(F, np.stack([A, B, np.full_like(A, -0.75)], -1), steps=3000)
            bd = per != 0
            key = '%s cone %d-%d' % ('updown' if both else 'string', b1, b2)
            out[key] = {'bounded_share': float(bd.mean()), 'period2_share': float((per == 2).mean()), 'farthest_bounded': float(rad[bd].max()) if bd.any() else 0.0,
                        'bounded_within_0.01': float(bd[rad < 0.01].mean()), 'bounded_0.01_to_0.03': float(bd[(rad >= 0.01) & (rad < 0.03)].mean()), 'bounded_0.03_to_0.06': float(bd[(rad >= 0.03) & (rad < 0.06)].mean())}
            print(key, json.dumps(out[key]), flush=True)
            Image.fromarray(K.colour_of(per)).save(os.path.join(HERE, 'hunt', 'probe-%s-%d-%d.png' % ('updown' if both else 'string', b1, b2)))
    json.dump(out, open(os.path.join(HERE, 'probe.json'), 'w'), indent=1)
