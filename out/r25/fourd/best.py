"""Round 25, section fourd: the nearest thing this corner found. It does NOT pass the user's tests (see NOTES.md).

    import sys; sys.path.insert(0, 'out/r25/fourd'); import best
    r = best.rule()            # 'product, cone cut': a rule of out/r21/lib/mem.py (works with M.stay, M.solid, M.julia_sheet, M.flat_check)
    s = best.spinor_rule()     # the spinor rule with the least-turn start (the other new 4D rule; rings for real c, nothing for the rabbit)

rule(): the 4D rule is the product of two flat rules (the bicomplex square): a pair of flat points (u1, u2), each
follows u -> u^2 + c. The way down is not a flat cut: a 3D point with distance r from the centre, longitude L and
latitude D stands for the pair  u1 = r e^{i(L + D)},  u2 = r e^{i(L - D)}  (the two ends at the same distance from
the centre: the cut of the product by the cone over the Clifford torus |u1| = |u2|). The point is inside when both
ends stay. While the orbit runs, the library is shown the pair as the 3D point (middle of the pair, half its length).
For c off the flat plane the two ends get the pair that c itself stands for.

Flat check: 0 differ in all four sets (a flat point is the pair (u, u)).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M
import four as F


def pair_of(x, y, z):
    """The pair of flat points that a 3D point stands for: its height laid down sideways, to the left and to the right."""
    rho = np.hypot(x, y); ok = rho > 0; rr = np.where(ok, rho, 1.0); mx, my = np.where(ok, x / rr, 1.0), np.where(ok, y / rr, 0.0)
    return x - z * my, y + z * mx, x + z * my, y - z * mx


def _step(x, y, z, st, k, cx, cy, cz):
    a, b, p, q = pair_of(x, y, z) if k == 0 else st
    c1r, c1i, c2r, c2i = pair_of(np.asarray(cx, float), np.asarray(cy, float), np.asarray(cz, float))
    a, b = a * a - b * b + c1r, 2 * a * b + c1i            # each end follows the flat rule
    p, q = p * p - q * q + c2r, 2 * p * q + c2i
    big = (a * a + b * b + p * p + q * q) > 1e12            # gone: keep the numbers finite
    a, b, p, q = (np.where(big, 1e6, t) for t in (a, b, p, q))
    # what the library sees: the middle of the pair and half its length (c is added by the library, so take it off here)
    return (a + p) / 2 - cx, (b + q) / 2 - cy, np.hypot(a - p, b - q) / 2 - cz, (a, b, p, q)


def rule():
    return M.Rule('product-cone', 'two flat pictures in 4D, cut by the cone where both points are equally far from the centre', _step,
                  init=lambda n: (np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)))


def spinor_rule(kind='min'):
    return F.spinor(kind)


def inside(c, steps=30):
    """The same object as a yes / no test on arrays x, y, z (quicker than the rule: the second end is only followed where the first stayed)."""
    return F.pred_perp(c, steps)


if __name__ == '__main__':
    r = rule(); print(r.name, '|', r.label); print('flat check', M.flat_check(r, n=20000, steps=60))
    rng = np.random.default_rng(7); v = rng.uniform(-1.6, 1.6, size=(3, 200000))
    for nm, c in F.SETS:
        a = M.stay(r, v[0], v[1], v[2], c[0], c[1], c[2], 40) >= 40; b = inside(c, 40)(v[0], v[1], v[2])
        print('%-12s rule against the yes / no test: %d of %d differ; share of the box inside %.4f (one plane %.4f)' % (
            nm, int((a != b).sum()), a.size, a.mean(), (M.stay(M.bench('oneplane'), v[0], v[1], v[2], c[0], c[1], c[2], 40) >= 40).mean()))
    s = spinor_rule(); print(s.name, 'flat check', M.flat_check(s, n=20000, steps=60))
