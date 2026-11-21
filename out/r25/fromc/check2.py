"""Round 25, fromc: three more numbers per rule.   python out/r25/fromc/check2.py [names]

(a) One step at the meeting point of c: the three stretches of the rule there (all three equal to the flat stretch
    2 |meeting point| = the step keeps shapes there and pushes a lifted point away as fast as a flat one).
(b) Lopsidedness: turn the solid half-way round the upright axis (the flat picture is the same after that turn);
    share of the inside whose verdict changes. And the mirror in the flat plane (z -> -z).
(c) Leak: inside share of a box at 30 and at 90 steps.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel', M.SIEGEL), ('1/4 bud', (0.28227139, 0.53006062, 0.0))]


def one_step(rule, p, c):
    """F(p) + c for points p (3 x n) all started fresh (first squaring)."""
    n = p.shape[1]; o = rule.step(p[0], p[1], p[2], tuple(rule.init(n)), 0, np.full(n, c[0]), np.full(n, c[1]), np.full(n, c[2]))
    return np.array([o[0] + c[0], o[1] + c[1], o[2] + c[2]])


def stretches(rule, c, h=1e-5):
    a = R.alpha(complex(c[0], c[1])); p0 = np.array([a.real, a.imag, 0.0])
    J = np.zeros((3, 3))
    for j in range(3):
        d = np.zeros(3); d[j] = h
        pts = np.array([p0 + d, p0 - d]).T
        q = one_step(rule, pts, c); J[:, j] = (q[:, 0] - q[:, 1]) / (2 * h)
    # one-sided look straight up as well (some rules have a corner there)
    up = one_step(rule, np.array([[p0[0]], [p0[1]], [h]]), c)[:, 0] - p0
    return np.linalg.svd(J, compute_uv=False), float(np.linalg.norm(up) / h), 2 * abs(a)


def lopsided(rule, c, n=150000, steps=40, seed=17):
    rng = np.random.default_rng(seed); q = rng.uniform(-1, 1, size=(3, n)) * np.array([[1.8], [1.4], [1.4]])
    a = M.stay(rule, q[0], q[1], q[2], c[0], c[1], c[2], steps) >= steps
    b = M.stay(rule, -q[0], -q[1], q[2], c[0], c[1], c[2], steps) >= steps
    m = M.stay(rule, q[0], q[1], -q[2], c[0], c[1], c[2], steps) >= steps
    s90 = M.stay(rule, q[0], q[1], q[2], c[0], c[1], c[2], 90) >= 90
    ins = max(int(a.sum()), 1)
    return ins / n, float((a != b).sum()) / ins, float((a != m).sum()) / ins, float(s90.sum()) / ins


if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else ['oneplane', 'along', 'axis_every', 'axis_once', 'm4', 'face4', 'tri', 'face_tri']
    for nm in names:
        r = R.get(nm); print('\n== %s | %s' % (r.name, r.label))
        for sn, c in SETS:
            sv, up, flat = stretches(r, c); ins, half, mir, keep = lopsided(r, c)
            print('   %-9s at the meeting point: stretches %.3f %.3f %.3f, straight up %.3f (flat stretch %.3f) | inside %.4f; changes under a half turn %.1f %%, under the mirror %.1f %%; kept from 40 to 90 steps %.1f %%'
                  % (sn, sv[0], sv[1], sv[2], up, flat, ins, 100 * half, 100 * mir, 100 * keep))
            sys.stdout.flush()
