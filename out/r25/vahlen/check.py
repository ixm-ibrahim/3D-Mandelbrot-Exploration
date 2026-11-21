"""Numbers for the section "vahlen". python out/r25/vahlen/check.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V
M = V.M
rng = np.random.default_rng(7)


def algebra():
    n = 20000; p = rng.normal(size=(3, n)); zero = np.zeros(n)
    # 1. the carried spinor: a a* = v, (ga)(ga)* = v + c, flat points keep phase 0
    for nm, lift in (('V', V.lift_V), ('up', V.lift_up)):
        a = lift(*p); w = V.point_of(a)
        print('lift %-2s: |a a* - v| max %.1e, k part %.1e' % (nm, max(np.abs(w[i] - p[i]).max() for i in range(3)), np.abs(w[3]).max()))
    a = V.roll(V.lift_V(*p), 37.0); w = V.point_of(a)
    print('rolled spinor gives the same point: %.1e' % max(np.abs(w[i] - p[i]).max() for i in range(3)))
    c = rng.normal(size=(3, n)); b = V.qmul(a, a); wb = V.point_of(b); a2 = V.carry(b, wb[:3], c); w2 = V.point_of(a2)
    print('carry lands on w + c: %.1e' % max(np.abs(w2[i] - wb[i] - c[i]).max() for i in range(3)))
    # the carry is the shortest turn: the turn axis is square to both w and w + c  (check: g w g* stays in their plane)
    # 2. one-term quaternion products: v b v and v b vbar with the constants forced by "z^2 on the flat plane"
    for beta in (0.0, 30.0, 90.0, 135.0):
        bq = (np.cos(np.radians(beta)), np.sin(np.radians(beta)), 0.0, 0.0)           # b = e^(i beta)
        lam = (np.cos(np.radians(beta / 2)), np.sin(np.radians(beta / 2)), 0.0, 0.0)  # lambda = e^(i beta / 2)
        v = (p[0], p[1], p[2], zero); one = lambda q: tuple(np.full(n, t) for t in q)
        t = V.qmul(V.qmul(V.qmul(V.qmul(one(lam), one(V.conj(bq))), v), one(bq)), V.qmul(v, one(V.conj(lam))))
        F = V.lathe_b(beta)(*p)
        print('beta %5.1f: e^(ib/2) e^(-ib) v e^(ib) v e^(-ib/2) minus lathe_b: %.1e, k part %.1e' % (beta, max(np.abs(t[i] - F[i]).max() for i in range(3)), np.abs(t[3]).max()))
    # 3. every quadratic rule is even, so on the ball of directions it turns half of them inside out
    for nm, F in (('lathe', V.lathe), ('lathe 90', V.lathe_b(90)), ('holo', V.holo), ('one plane', V.oneplane)):
        e = 1e-5; q = p / np.linalg.norm(p, axis=0)
        f0 = np.array(F(*q)); J = np.zeros((3, 3, n))
        for j in range(3):
            d = np.zeros((3, 1)); d[j] = e
            J[:, j] = (np.array(F(*(q + d))) - np.array(F(*(q - d)))) / (2 * e)
        det = np.linalg.det(np.moveaxis(J, 2, 0)); sv = np.linalg.svd(np.moveaxis(J, 2, 0), compute_uv=False)
        print('%-9s share of directions turned inside out: %.3f ; squeeze (largest / smallest stretch) median %.2f, 90%% %.1f' % (nm, (det < 0).mean(), np.median(sv[:, 0] / sv[:, 2]), np.quantile(sv[:, 0] / sv[:, 2], 0.9)))


def flat():
    rules = [V.R_lathe_b(90), V.R_holo(), V.spin('V'), V.spin('up'), V.spin('V', 20.0)]
    for r in rules:
        print('%-12s flat check %s' % (r.name, M.flat_check(r, n=20000, steps=60)))
        q = rng.uniform(-1, 1, size=(3, 20000)) * np.array([[1.8], [1.4], [1.4]])
        for nm, c in V.SETS[:2]:
            n30 = M.stay(r, q[0], q[1], q[2], c[0], c[1], c[2], 30) >= 30; o = M.stay(V.R_one(), q[0], q[1], q[2], c[0], c[1], c[2], 30) >= 30
            print('      %-8s share of the box inside after 30 steps: %.4f (one plane %.4f)' % (nm, n30.mean(), o.mean()))


if __name__ == '__main__':
    algebra(); flat()
