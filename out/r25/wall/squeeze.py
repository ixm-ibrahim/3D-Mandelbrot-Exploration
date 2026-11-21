"""W-f, measured directly: does the squeeze pile up from step to step, close to the surface of the solid?

Take points just outside the solid (they leave after 9 to 14 steps), off the flat plane. For k = 1, 2, 4, 6 steps of
the whole rule (square and add c) measure how a tiny ball round the point is deformed: longest over shortest axis.
A rule that keeps shapes gives 1 at every k. A rule whose squeeze piles up gives a number that grows like q^k.

    python out/r25/wall/squeeze.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
for p in (('out', 'r24', 'me'), ('out', 'r23', 'me'), ('out', 'r25', 'me')):
    sys.path.insert(0, os.path.join(ROOT, *p))
import wall as W
import pil as PL
M = W.M
import cone as C, tri as T, conefold


def steps_k(rule, v, c, k):
    x, y, z = (np.array(t, float) for t in v); n = x.size; st = tuple(rule.init(n))
    cx, cy, cz = (np.full(n, t) for t in c)
    for i in range(k):
        o = rule.step(x, y, z, st, i, cx, cy, cz); x, y, z, st = o[0] + cx, o[1] + cy, o[2] + cz, tuple(o[3])
    return np.array([x, y, z])


def measure(rule, c, n=60000, seed=7, lo=9, hi=14, ks=(1, 2, 4, 6)):
    rng = np.random.default_rng(seed); v = rng.uniform(-1.6, 1.6, size=(3, n)); v[2] = rng.uniform(0.08, 1.4, n)
    s = M.stay(rule, v[0], v[1], v[2], c[0], c[1], c[2], hi + 1); keep = (s >= lo) & (s <= hi); v = v[:, keep][:, :4000]
    out = []
    for k in ks:
        h = 1e-7; f0 = steps_k(rule, v, c, k); J = np.zeros((v.shape[1], 3, 3))
        for j in range(3):
            d = np.zeros((3, 1)); d[j] = h
            J[:, :, j] = ((steps_k(rule, v + d, c, k) - steps_k(rule, v - d, c, k)) / (2 * h)).T
        ok = np.isfinite(J).all((1, 2)) & (np.abs(J).max((1, 2)) < 1e12)
        sv = np.linalg.svd(J[ok], compute_uv=False); q = sv[:, 0] / np.maximum(sv[:, 2], 1e-300)
        out.append((k, float(np.median(q)), float(np.percentile(q, 90))))
    return v.shape[1], out


def main():
    sq = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)]
    cu = [(nm.split(' (')[0], c) for nm, c in PL.sets3()[:2]]
    jobs = [(M.fixed(W.P, 'one plane'), sq), (M.bench('twoplane'), sq), (M.bench('along'), sq), (conefold.fold_rule(30.0, name='fold at 30 (r24)'), sq),
            (C.cone_rule(-C.T15, name='cone - (r23)'), sq), (T.tri_rule(name='triangle pillow (r24)'), sq), (M.bench('pillow'), sq),
            (M.fixed(W.ws(3, True), 'wind, square'), sq),
            (PL.rule_oneplane(3), cu), (PL.rule_pillow(3), cu)]
    print('longest over shortest axis of a tiny ball after k steps, at points just outside the solid and off the flat plane')
    print('(median / 9 in 10 below)')
    for r, sets in jobs:
        for nm, c in sets:
            try:
                n, res = measure(r, c)
            except Exception as e:
                print('%-24s %-22s failed: %s' % (r.name, nm, e)); continue
            print('%-24s %-22s %5d points  ' % (r.name, nm, n) + '   '.join('k=%d: %8.3g / %8.3g' % t for t in res)); sys.stdout.flush()


if __name__ == '__main__':
    main()
