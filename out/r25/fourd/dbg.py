"""Print single orbits of the spinor rule: python out/r25/fourd/dbg.py kind x y z cx cy cz [steps]"""
import sys
import numpy as np
import four as F

kind = sys.argv[1]; v = [float(t) for t in sys.argv[2:5]]; c = [float(t) for t in sys.argv[5:8]]; steps = int(sys.argv[8]) if len(sys.argv) > 8 else 14
x, y, z = (np.array([t]) for t in v)
q = F.lift_min(x, y, z) if kind == 'min' else F.lift_plane(x, y, z, np.pi / 2)
if kind.startswith('ph'):
    q = F.phase(F.lift_min(x, y, z), np.radians(float(kind[2:])) / 2)
for k in range(steps):
    h = F.hopf(q); r = np.sqrt(sum(t * t for t in h))[0]
    q0 = F.lift_min(*h); tw = 2 * np.arctan2((q0[0] * q[1] - q0[2] * q[3] + q0[3] * q[2])[0], (q0[0] * q[0] + q0[2] * q[2] + q0[3] * q[3])[0])
    print('%2d  point %9.5f %9.5f %9.5f   |v| %.4g   twist %7.1f   q %s' % (k, h[0][0], h[1][0], h[2][0], r, np.degrees(tw) % 360, ' '.join('%9.5f' % t[0] for t in q)))
    if r > 6:
        break
    q, w = F.transport(F.qsq(q), *c)
