"""The spinor rule: what one squaring does to a small twist of the quaternion about its point.

Claim (worked out by hand): a quaternion above the point v, twisted by a small angle t away from the least-turn
quaternion, has after one squaring the twist  t (1 + |v| / x)  (x = the point's x-coordinate), whatever c is
(adding c moves every quaternion above a point by the same left factor, so it keeps twist DIFFERENCES).
Here: the claim against numbers, and the growth of a small twist along flat orbits of the four standard sets.

    python out/r25/fourd/twist.py
"""
import sys
import numpy as np
import four as F
M = F.M


def twist_of(q):
    """Twice the fibre angle between q and the least-turn quaternion above the same point (radians, -pi..pi)."""
    h = F.hopf(q); q0 = F.lift_min(*h)
    re = q0[0] * q[0] + q0[1] * q[1] + q0[2] * q[2] + q0[3] * q[3]
    im = q0[0] * q[1] - q0[1] * q[0] - q0[2] * q[3] + q0[3] * q[2]          # the i-part of conj(q0) q
    return (2 * np.arctan2(im, re) + np.pi) % (2 * np.pi) - np.pi          # q and -q are the same frame


rng = np.random.default_rng(2); n = 100000
v = rng.normal(size=(3, n)); t = 1e-6
q = F.phase(F.lift_min(*v), t / 2); c = rng.normal(size=(3, n))
p, w = F.transport(F.qsq(q), *c)
got = twist_of(F.qsq(q)) / t; want = 1 + np.sqrt((v * v).sum(0)) / v[0]
ok = np.abs(v[0]) > 0.05 * np.sqrt((v * v).sum(0))
print('one squaring: twist multiplier against 1 + |v|/x: worst difference %.1e on %d points (median size of the multiplier %.2f)' % (np.abs(got - want)[ok].max(), int(ok.sum()), np.median(np.abs(want))))
# adding c keeps twist differences: compare two quaternions above one point before and after the transport
qa = F.qsq(F.phase(F.lift_min(*v), 0.3)); qb = F.phase(qa, 0.2)
pa, _ = F.transport(qa, *c); pb, _ = F.transport(qb, *c)
d = F.qmul((pa[0], -pa[1], -pa[2], -pa[3]), pb); n2 = pa[0] ** 2 + pa[1] ** 2 + pa[2] ** 2 + pa[3] ** 2
print('adding c: the twist between two quaternions above one point stays 0.2 * 2: worst error %.1e' % np.abs(2 * np.arctan2(d[1] / n2, d[0] / n2) - 0.4).max())

# growth of a small twist along flat orbits: sum of log|1 + |z|/Re z| per step, over points of the flat picture's inside
for nm, c in F.SETS + [('c = 0', (0.0, 0.0, 0.0)), ('c = -0.5', (-0.5, 0.0, 0.0)), ('c = 0.25i', (0.0, 0.25, 0.0)), ('c = -0.12+0.6i', (-0.12, 0.6, 0.0))]:
    zr, zi = rng.uniform(-1.8, 1.8, 40000), rng.uniform(-1.3, 1.3, 40000)
    ins = F.in_flat(zr, zi, c, 200); z = (zr + 1j * zi)[ins]; cc = c[0] + 1j * c[1]
    for _ in range(100):
        z = z * z + cc
    s = np.zeros(z.size); N = 300
    for _ in range(N):
        s += np.log(np.maximum(np.abs(1 + np.abs(z) / np.where(z.real == 0, 1e-300, z.real)), 1e-300)); z = z * z + cc
    s /= N
    print('%-14s inside points %5d: growth of a small twist per step: median factor %.3g  (share of orbits where it grows: %.2f)' % (nm, z.size, np.exp(np.median(s)), (s > 0).mean()))
sys.stdout.flush()

# the same, measured on the rule itself: start flat points with a twist of 1e-9 and see whether they still stay
for nm, c in F.SETS:
    zr, zi = rng.uniform(-1.8, 1.8, 40000), rng.uniform(-1.3, 1.3, 40000); ins = F.in_flat(zr, zi, c, 60); zr, zi = zr[ins], zi[ins]; o = np.zeros(zr.size)
    out = []
    for tw in (1e-9, 1e-3, 0.3):
        r = F.spinor('phase', th=tw / 2); out.append(float((M.stay(r, zr, zi, o, c[0], c[1], 0.0, 60) >= 60).mean()))
    print('%-12s flat inside points started with a twist of 1e-9, 1e-3, 0.3: share that still stays %.3f, %.3f, %.3f' % (nm, *out))
