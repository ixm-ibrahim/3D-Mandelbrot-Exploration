"""Prover, three small checks by numbers of statements made in report.md (known rules only).

 (a) Why the torn two-plane rule draws a clean basilica: on the tear wall y = z the two candidate answers are mirror images
     of each other in that same wall. So when the set is symmetric in the wall (c on the x-axis) both answers agree on
     'inside or outside' and the tear cannot be seen; for c off the axis the set is not symmetric and it can.
 (b) Sideways stretch ON the flat plane for the family psi = phi - a sin(4 phi)/4 (a = 1: 'along'; a = 0: lathe):
     predicted (sideways stretch) / (in-plane stretch) = a + (1 - a) cos(theta), theta = direction in the flat plane from +x.
 (c) The complex-analysis identity behind 'no rule can keep angles on the sphere of directions and be exact on two planes':
     in the coordinate w = (y + i z)/(1 + x) the flat plane's rule is A(w) = 2w/(1 - w^2), the upright plane's is
     B(w) = 2w/(1 + w^2); they agree only at w = 0 and infinity.

    python out/r17/prover/c2_extra.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import scout as S

rng = np.random.default_rng(3)

# (a)
x, t = rng.normal(size=100000), rng.normal(size=100000)
Pz = np.stack(S.oneplane(x, t, t))                      # the flat plane's rule on the wall y = z
X2, Z2, Y2 = S.oneplane(x, t, t); Py = np.stack([X2, Y2, Z2])    # the upright plane's rule there (as in scout.twoplane)
mirror = np.stack([Pz[0], Pz[2], Pz[1]])                # mirror image of the first answer in the wall (swap y and z)
print('(a) on the wall y = z: | upright answer - mirror image of flat answer | max = %.1e   (| upright - flat | max = %.2f: the tear itself)'
      % (np.abs(Py - mirror).max(), np.abs(Py - Pz).max()))


def run(F, v, c, steps=60):
    v = v.copy(); alive = np.ones(v.shape[1], bool)
    for _ in range(steps):
        X, Y, Z = F(v[0, alive], v[1, alive], v[2, alive])
        w = np.stack([X + c[0], Y + c[1], Z + c[2]])
        v[:, alive] = w
        alive[alive] = (w * w).sum(0) <= 36
    return alive


P = rng.uniform(-1.6, 1.6, size=(3, 400000))
Q = np.stack([P[0], P[2], P[1]])                        # mirror images in the wall
for c in ((-1.0, 0, 0), (-1.0, 0.15, 0.0), (-0.122561, 0.744862, 0.0)):
    a, b = run(S.twoplane, P, c), run(S.twoplane, Q, c)
    print('    two-plane set for c = %s: points whose mirror image in the wall gets a different verdict: %.3f %% of the set' % (str(c), 100.0 * (a != b).sum() / max(a.sum(), 1)))

# (b)
print('(b) sideways / in-plane stretch on the flat plane, family psi = phi - a sin(4 phi)/4: measured against a + (1 - a) cos(theta)')
h = 1e-6
worst = 0.0
for a in (0.0, 0.3, 0.6, 1.0):
    F = S.switch(a)
    th = np.linspace(0.05, np.pi - 0.05, 9)
    xx, yy = np.cos(th), np.sin(th)
    _, _, Zp = F(xx, yy, np.full_like(th, h)); _, _, Zm = F(xx, yy, np.full_like(th, -h))
    tau = (Zp - Zm) / (2 * h) / 2.0                     # in-plane stretch is 2 r = 2
    pred = a + (1 - a) * np.cos(th)
    worst = max(worst, np.abs(tau - pred).max())
    print('    a = %.1f: ' % a + ' '.join('%+.3f' % v for v in tau))
print('    largest difference from the formula: %.1e' % worst)
print('    so a profile a(t) with a = 0 on the axis and a = 1 at right angles to it has sideways stretch -1 on the negative axis, +1 at 90 degrees,')
print('    and exactly 0 on two rays of the flat plane behind x = 0: there the rule flattens space onto the flat plane.')
for nm, af in (('a(t) = t', lambda s: s), ('a(t) = t^2', lambda s: s * s), ('a(t) = smoothstep', lambda s: s * s * (3 - 2 * s))):
    th = np.linspace(np.pi / 2, np.pi, 200001); s = np.sin(th); tau = af(s) + (1 - af(s)) * np.cos(th)
    k = np.flatnonzero(np.sign(tau[1:]) != np.sign(tau[:-1]))
    print('    %-18s sideways stretch is zero at %s degrees from the +x axis' % (nm, ', '.join('%.1f' % np.degrees(th[i]) for i in k)))

# (c)
w = (rng.normal(size=200000) + 1j * rng.normal(size=200000))
A, B = 2 * w / (1 - w * w), 2 * w / (1 + w * w)
d = np.abs(A - B) / (1 + np.abs(A)) / (1 + np.abs(B))
print('(c) A(w) - B(w) = 4 w^3 / (1 - w^4): zero only at w = 0 (and at infinity). Smallest |A - B| among 200,000 random w with 0.2 < |w| < 5: %.3f'
      % np.abs(A - B)[(np.abs(w) > 0.2) & (np.abs(w) < 5)].min())
