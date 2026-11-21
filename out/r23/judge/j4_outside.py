"""Round 23, judge, check 4: the outside sections' claims that would be told. My points, my loop.

    python out/r23/judge/j4_outside.py

1  outside formulas against ours: share of the inside on which verdicts differ (300,000 box points, 60 steps), c = -1 and rabbit
2  flat check on c = -1 and the rabbit for the outside formulas that matter (20,000 flat points)
3  the turn law (turn the point by a about the upright axis -> the square turns by 2a): which rules obey it
4  the height factor above the rabbit's meeting point (briefing 2 (a))
5  outside2's counterexample to briefing 2 (b), typed again from its formula ("fold30")
6  one plane = "length squared, longitude doubled, Mercator latitude doubled"; the quaternion square in 3D is spun round the x-axis
7  Bristorbrot: is the upright plane y = 0 a second exact plane, also for c off the x-axis?
"""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jl as L
rng = np.random.default_rng(41); t0 = time.time()
O = L.outside1()
V = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(300000, 3))


def ins(r, c, steps=60):
    return L.stay(r, V[:, 0], V[:, 1], V[:, 2], c, steps) >= steps


print('== 1. outside formulas against ours (verdicts that differ, as a share of the larger inside)')
for a, b in (('twoplane', 'o:sym2'), ('twoplane', 'o:sym3'), ('along', 'o:eiffie'), ('oneplane', 'o:cup1'), ('oneplane', 'o:mb2')):
    for sn, c in (('c = -1', L.BAS), ('rabbit', L.RABBIT)):
        A, B = ins(L.get(a), c), ins(L.get(b), c)
        print('   %-9s against %-9s %-7s inside %.4f and %.4f of the box; differ on %.2f %% of the larger inside (%d points)'
              % (a, b, sn, A.mean(), B.mean(), 100 * (A != B).sum() / max(A.sum(), B.sum(), 1), int((A != B).sum()))); sys.stdout.flush()

print('== 2. flat check (20,000 flat points, 60 steps): verdicts that differ from the flat picture')
zr, zi = rng.uniform(-1.8, 1.8, 20000), rng.uniform(-1.3, 1.3, 20000)
for nm in ('sym2', 'sym3', 'eiffie', 'mb2', 'quat3d', 'bristor', 'scator_ix', 'hyper', 'hopfcut', 'cup1'):
    r = O.get(nm); row = []
    for sn, c in (('c = -1', L.BAS), ('rabbit', L.RABBIT), ('Siegel', L.SIEGEL)):
        a = L.stay(r, zr, zi, np.zeros(20000), c, 60) >= 60; b = L.flat_stay(zr, zi, c, 60) >= 60
        row.append('%s %d (inside: %d, flat picture %d)' % (sn, int((a != b).sum()), int(a.sum()), int(b.sum())))
    print('   %-10s %s' % (nm, ' | '.join(row))); sys.stdout.flush()

print('== 3. the turn law: largest distance between F(turned v) and F(v) turned twice as far (20,000 points, length about 1)')
p = rng.normal(size=(3, 20000)); p /= np.linalg.norm(p, axis=0)


def rotz(x, y, a):
    return np.cos(a) * x - np.sin(a) * y, np.sin(a) * x + np.cos(a) * y


def fold30(x, y, z):
    """outside2's counterexample: latitude kept up to 30 degrees, 90 - 2|L| beyond (sign kept), longitude kept; then one plane."""
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0); lat = np.arcsin(np.clip(z / rs, -1, 1)); lon = np.arctan2(y, x)
    a = np.abs(lat); l2 = np.where(a <= np.pi / 6, a, np.pi / 2 - 2 * a) * np.where(z < 0, -1.0, 1.0)
    return L.P(r * np.cos(l2) * np.cos(lon), r * np.cos(l2) * np.sin(lon), r * np.sin(l2))


FOLD30 = L.fixed(fold30, 'fold30')
for nm, F in (('one plane', L.P), ('fold30', fold30), ('cones (welded)', L.CONES), ('two planes', L.TWOPLANE), ('along', L.ALONG), ('lathe', lambda x, y, z: (x * x - y * y - z * z, 2 * x * y, 2 * x * z))):
    row = []
    for deg in (37.0, 90.0, 120.0, 180.0):
        a = np.radians(deg); x1, y1 = rotz(p[0], p[1], a); A = F(x1, y1, p[2]); B = F(p[0], p[1], p[2]); bx, by = rotz(B[0], B[1], 2 * a)
        row.append('%g deg: %.1e' % (deg, float(np.max(np.sqrt((A[0] - bx) ** 2 + (A[1] - by) ** 2 + (A[2] - B[2]) ** 2)))))
    print('   %-15s %s' % (nm, ' | '.join(row)))

print('== 4. above the rabbit\'s meeting point: height after one step, divided by the height before')
cc = complex(*L.RABBIT[:2]); al = (1 - np.sqrt(1 - 4 * cc)) / 2
for h in (0.01, 0.075, 0.15, 0.3):
    row = []
    for nm, F in (('one plane', L.P), ('two planes', L.TWOPLANE), ('along', L.ALONG), ('cones', L.CONES)):
        X, Y, Z = F(np.array([al.real]), np.array([al.imag]), np.array([h])); row.append('%s %.3f (lands at y = %.3f)' % (nm, Z[0] / h, Y[0] + cc.imag))
    print('   height %.3f: %s' % (h, ' | '.join(row)))

print('== 5. fold30: flat check, continuity, and what its 45-degree cone holds')
for sn, c in (('c = -1', L.BAS), ('rabbit', L.RABBIT)):
    a = L.stay(FOLD30, zr, zi, np.zeros(20000), c, 60) >= 60; b = L.flat_stay(zr, zi, c, 60) >= 60
    rho = np.sqrt(rng.uniform(0, 1.8 ** 2, 40000)); lon = rng.uniform(-np.pi, np.pi, 40000); s = np.sqrt(0.5)
    fl = L.flat_stay(rho * np.cos(lon), rho * np.sin(lon), c, 60) >= 60
    row = []
    for off in (0.0, 0.5, 5.0):
        la = np.radians(45.0 + off)
        k = L.stay(FOLD30, rho * np.cos(la) * np.cos(lon), rho * np.cos(la) * np.sin(lon), rho * np.sin(la), c, 60) >= 60
        row.append('%g deg off the cone: %d differ, %d of %d flat-inside points stay' % (off, int((k != fl).sum()), int((k & fl).sum()), int(fl.sum())))
    print('   %-7s flat check %d of 20000 differ | cone at 45 degrees against the flat picture of the point at the same distance and longitude: %s' % (sn, int((a != b).sum()), ' | '.join(row)))
d = rng.normal(size=(3, 100000)); d /= np.linalg.norm(d, axis=0); e = d + 1e-6 * rng.normal(size=d.shape)
A = fold30(*d); B = fold30(*e); print('   continuity: a move of the point by about 1e-6 moves its square by at most %.1e' % float(np.max(np.sqrt(sum((A[i] - B[i]) ** 2 for i in range(3))))))
inb = L.stay(FOLD30, V[:, 0], V[:, 1], V[:, 2], L.RABBIT, 60) >= 60; ino = ins(L.get('oneplane'), L.RABBIT)
print('   rabbit: inside share of the box: fold30 %.4f, one plane %.4f' % (inb.mean(), ino.mean()))

print('== 6. one plane and the quaternion square')
q = rng.normal(size=(3, 100000)) * rng.uniform(0.1, 2, 100000); r = np.linalg.norm(q, axis=0); mu = np.arctanh(q[2] / r); lon = np.arctan2(q[1], q[0])
X, Y, Z = L.P(*q); ex, ey, ez = L.unit_at(2 * mu, 2 * lon)
print('   one plane against "length squared, longitude doubled, Mercator latitude doubled": largest difference %.1e' % float(np.max(np.sqrt((X - r * r * ex) ** 2 + (Y - r * r * ey) ** 2 + (Z - r * r * ez) ** 2))))
lathe = L.fixed(lambda x, y, z: (x * x - y * y - z * z, 2 * x * y, 2 * x * z), 'lathe'); ang = rng.uniform(0, 2 * np.pi, V.shape[0])
for sn, c in (('c = -1', L.BAS), ('rabbit (c turned with the point)', None)):
    y2, z2 = np.cos(ang) * V[:, 1] - np.sin(ang) * V[:, 2], np.sin(ang) * V[:, 1] + np.cos(ang) * V[:, 2]
    if c is not None:
        a = L.stay(lathe, V[:, 0], V[:, 1], V[:, 2], c, 60) >= 60; b = L.stay(lathe, V[:, 0], y2, z2, c, 60) >= 60
        print('   quaternion square cut to 3D (the Lathe), %s: turning the start point round the x-axis changes %d of %d verdicts (inside %.4f)' % (sn, int((a != b).sum()), a.size, a.mean()))
qa = lambda x, y, z: (x * x - y * y - z * z, 2 * x * y, 2 * x * z)
x1 = q[0]; y1, z1 = L.rotx(q[1], q[2], 0.7); A = qa(x1, y1, z1); B = qa(*q); by, bz = L.rotx(B[1], B[2], 0.7)
print('   the quaternion square of a point turned round the x-axis = the square, turned by the same angle: largest difference %.1e' % float(np.max(np.abs(A[1] - by) + np.abs(A[2] - bz) + np.abs(A[0] - B[0]))))

print('== 7. Bristorbrot on the upright plane y = 0 (points (x, 0, z), c = (cr, 0, ci)): verdicts that differ from the flat picture of x + iz')
br = O.get('bristor')
for sn, c in (('c = -1', L.BAS), ('rabbit', L.RABBIT), ('Siegel', L.SIEGEL)):
    a = L.stay(br, zr, np.zeros(20000), zi, (c[0], 0.0, c[1]), 60) >= 60; b = L.flat_stay(zr, zi, c, 60) >= 60
    print('   %-7s %d of 20000' % (sn, int((a != b).sum())))
print('done %.0f s' % (time.time() - t0))
