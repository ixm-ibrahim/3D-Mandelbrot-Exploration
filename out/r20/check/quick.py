"""Round 20 check: seconds-long attacks on m_w3. python out/r20/check/quick.py"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r19', 'panel2'))
import bench as B
import rules as R

F = R.get('m_w3'); F1 = R.get('oneplane')
rng = np.random.default_rng(7)
out = {}


def rotx(v, deg):
    t = np.radians(deg); x, y, z = v
    return np.array([x, y * np.cos(t) - z * np.sin(t), y * np.sin(t) + z * np.cos(t)])


# 1. symmetries of the rule itself
v = rng.normal(size=(3, 200000))
A = np.array(F(*v))
e120 = np.abs(np.array(F(*rotx(v, 120.0))) - A).max()
e60 = np.abs(np.array(F(*rotx(v, 60.0))) - A).max()
mz = np.array(F(v[0], v[1], -v[2])); emz = np.abs(mz - A * np.array([[1], [1], [-1]])).max()
my = np.array(F(v[0], -v[1], v[2])); emy = np.abs(my - A * np.array([[1], [-1], [1]])).max()
print('rule unchanged by a 120 degree turn: max diff %.1e ; by a 60 degree turn: %.2f (should NOT be 0)' % (e120, e60))
print('mirror z -> -z commutes: %.1e ; mirror y -> -y commutes: %.1e' % (emz, emy))
out['sym'] = dict(turn120=float(e120), turn60=float(e60), mirror_z=float(emz), mirror_y=float(emy))

# 2. orbit of 0 at the nudged sets, and fans of nudges
def orbit0(Fr, c, n=3000):
    x = np.zeros(1); y = np.zeros(1); z = np.zeros(1); R2 = (B.resc(c) + 1e-9) ** 2
    for k in range(n):
        x, y, z = Fr(x, y, z); x = x + c[0]; y = y + c[1]; z = z + c[2]
        if not np.isfinite(x[0] + y[0] + z[0]) or x[0] ** 2 + y[0] ** 2 + z[0] ** 2 > R2:
            return k + 1
    return None

NEWC = dict(bas_yz=(-1.0, 0.05, 0.03), bas_zy=(-1.0, 0.03, 0.05), sm_yz=(-0.75, 0.01, 0.02), rab_up=(-0.122561, 0.744862, 0.015))
out['orbit0'] = {}
for tag, c in NEWC.items():
    r = {n: orbit0(R.get(n), c) for n in ('m_w3', 'oneplane', 'along', 'twoplane')}
    out['orbit0'][tag] = r
    print('%-7s c = %s  nudge at %.1f deg, size %.3f : orbit of 0 leaves at step %s' % (tag, c, np.degrees(np.arctan2(c[2], c[1])), np.hypot(c[1], c[2]), r))

# fan: basilica and San Marco nudged by a fixed size in every direction round the x-axis
out['fan'] = {}
for base, cx in (('basilica', -1.0), ('sanmarco', -0.75)):
    for size in (0.01, 0.0224, 0.03, 0.0583, 0.1):
        row = []
        for deg in range(0, 181, 5):
            a = np.radians(deg); c = (cx, size * np.cos(a), size * np.sin(a))
            row.append(orbit0(F, c, 1500))
        out['fan']['%s_%g' % (base, size)] = row
        print('%-9s nudge %.4f, direction 0..180 step 5 deg (step at which 0 leaves; . = stays 1500):' % (base, size))
        print('   m_w3   ', ' '.join('.' if r is None else str(r) for r in row))
        row1 = [orbit0(F1, (cx, size * np.cos(np.radians(d)), size * np.sin(np.radians(d))), 1500) for d in range(0, 181, 5)]
        print('   onepl. ', ' '.join('.' if r is None else str(r) for r in row1))
        out['fan']['%s_%g_oneplane' % (base, size)] = row1
# rabbit lifted: how far can c be lifted
for lift in (0.005, 0.01, 0.015, 0.02, 0.03, 0.05):
    c = (-0.122561, 0.744862, lift)
    print('rabbit lifted by %.3f: m_w3 %s  oneplane %s  along %s' % (lift, orbit0(F, c), orbit0(F1, c), orbit0(R.get('along'), c)))
    out['fan']['rabbit_lift_%g' % lift] = [orbit0(F, c), orbit0(F1, c)]
json.dump(out, open(os.path.join(HERE, 'quick.json'), 'w'), indent=1)
