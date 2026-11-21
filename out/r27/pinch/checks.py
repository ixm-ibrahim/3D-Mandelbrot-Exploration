"""Checks behind single sentences of the notes.  python checks.py  -> checks.log
 1. my measure on my grid gives round 25's number for the balls object (so the numbers can be compared)
 2. a spindle with half opening 90 degrees is the ball on its two tips; a flat move carries a spindle to the spindle
    on the carried landmarks; the 3D body of a spindle is round about its middle line
 3. how long and how wide the bodies are (measured on the bodies, not from the formula)
 4. the trees of way (c) against the one-plane solid, in space
 5. the flat cut of the 3D objects of way (a) and (c) is the flat object (they are unions of bodies centred on the flat plane)
"""
import sys
import numpy as np
import pinchlib as PL, fam, objs
M = PL.M
sys.path.insert(0, PL.os.path.join(PL.ROOT, 'out', 'r25', 'klein'))
import tree as KT

rng = np.random.default_rng(5)
# 1
u, s = np.meshgrid(np.linspace(-1.8, 1.8, 720), np.linspace(1.3, -1.3, 520))
T1 = PL.true_flat(PL.CS['c1']); A = M.stay(KT.tree('line'), u, s, np.zeros_like(u), 0.0, 0.0, 0.0, 40) >= 40
print('1. balls object (round 25, flat cut) against the true c = -1 picture on my grid: wrong verdicts %.1f%% of the true area (round 25: 38.6 to 39.7)' % (100 * PL.wrong_share(A, T1)))
TR = PL.true_flat(PL.CS['rabbit'])
print('   the same balls object against the true rabbit: %.1f%% (it has no c; this is only to have a number)' % (100 * PL.wrong_share(A, TR)))

# 2
X = rng.uniform(-1.5, 1.5, size=(200000, 3))
P, Q = np.array([-0.4, 0.1, 0.0]), np.array([0.7, -0.2, 0.0])
sp = PL.spindle(P, Q, (P + Q) / 2, np.pi / 2); bl = ('ball', (P + Q) / 2, np.linalg.norm(P - Q) / 2)
print('2. spindle with half opening 90 against the ball on its tips: %d of %d verdicts differ' % (int((PL.inside(sp, X) != PL.inside(bl, X)).sum()), X.shape[0]))
mv, _ = PL.fitted(PL.CS['rabbit'], 1, 'pin'); Mx = mv[1]['M']
al, be = PL.fixed_points(PL.CS['rabbit']); th = np.radians(40.0)
s0 = PL.spindle(PL.to3(al), PL.to3(-al), PL.to3(0j), th)
w = rng.uniform(-1.5, 1.5, 200000) + 1j * rng.uniform(-1.5, 1.5, 200000)
s1 = PL.spindle(PL.to3(PL.ap(Mx, al)), PL.to3(PL.ap(Mx, -al)), PL.to3(PL.ap(Mx, 0j)), th)
a0 = PL.inside(s0, np.stack([w.real, w.imag, 0 * w.real], -1)); mw = PL.ap(Mx, w)
a1 = PL.inside(s1, np.stack([mw.real, mw.imag, 0 * w.real], -1))
print('   a flat move carries the spindle on three landmarks to the spindle on the carried landmarks: %d of %d verdicts differ (%d inside)' % (int((a0 != a1).sum()), w.size, int(a0.sum())))
# round about the middle line: cut the spindle s0 by planes across the line between its tips; compare with a circle
e = (s0[2] - s0[1]); L = np.linalg.norm(e); e = e / L; n1 = np.array([-e[1], e[0], 0.0]); n2 = np.array([0.0, 0.0, 1.0]); worst = 0.0
for t in (0.2, 0.5, 0.8):
    base = s0[1] + t * L * e; rad = []
    for ang in np.linspace(0, 2 * np.pi, 24, endpoint=False):
        d = np.cos(ang) * n1 + np.sin(ang) * n2; lo, hi = 0.0, 2.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if PL.inside(s0, (base + mid * d)[None])[0]: lo = mid
            else: hi = mid
        rad.append(lo)
    worst = max(worst, (max(rad) - min(rad)) / np.mean(rad))
print('   cuts across the line between the tips are circles: largest spread of the radius %.1e' % worst)

# 3
for key in ('c1', 'rabbit'):
    for th in (fam.OPEN[key], objs.BEST[key]):
        b = PL.spindle(np.array([-0.5, 0, 0.0]), np.array([0.5, 0, 0.0]), np.zeros(3), np.radians(th)); lo, hi = 0.0, 2.0
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            if PL.inside(b, np.array([[0.0, mid, 0.0]]))[0]: lo = mid
            else: hi = mid
        print('3. %s, half opening %.1f: the body is %.3f times as long as wide (measured), %.3f by the formula' % (PL.NAMES[key], th, 1 / (2 * lo), 1 / np.tan(np.radians(th) / 2)))
    L = fam.true_tree(PL.CS[key], 0.02); P, Q, C = L[:, 0], L[:, 1], L[:, 2]
    t = (C - P) / (Q - P); bend = np.degrees(np.abs(np.angle(-(C - P) / (C - Q) * (Q - P) / (P - Q) * -1)))
    print('   %s: %d bodies longer than 0.02; the image of 0 lies off the straight line between the tips by (median, worst) %.3f, %.3f of the length' % (PL.NAMES[key], L.shape[0], np.median(np.abs(t.imag)), np.abs(t.imag).max()))

# 4 and 5
one = M.bench('oneplane')
for key in ('c1', 'rabbit'):
    c = PL.CS[key]; n = 300000
    X = rng.uniform([-1.8, -1.3, -0.9], [1.8, 1.3, 0.9], size=(n, 3))
    O = M.stay(one, X[:, 0], X[:, 1], X[:, 2], c.real, c.imag, 0.0, 60) >= 60
    for nm in ('tree', 'treetrue', 'treeball', 'pin'):
        B = objs.get('%s-%s' % (nm, key)); ins = np.zeros(n, bool)
        for b in B[:1500]:                                                # the 1500 largest bodies; the rest is far below the sampling
            cen, rad = PL.bound(b); near = ((X - cen) ** 2).sum(1) <= rad * rad
            if near.any():
                ins[near] |= PL.inside(b, X[near])
        print('4. %s, %s (%d bodies): share of the box inside %.4f (one plane %.4f); verdicts that differ from the one-plane solid: %.1f%% of the one-plane volume'
              % (PL.NAMES[key], nm, len(B), ins.mean(), O.mean(), 100.0 * (ins != O).sum() / O.sum()))
        cmax = max(max(abs(b[1][2]), abs(b[2][2]) if b[0] == 'spin' else 0.0) for b in B)
        print('5.    largest height of a landmark above the flat plane: %.1e (0 = every body is centred on the flat plane)' % cmax)
        sys.stdout.flush()
