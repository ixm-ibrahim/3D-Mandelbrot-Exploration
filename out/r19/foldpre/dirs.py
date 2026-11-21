"""Seconds per rule, no iteration: the rule as a map of the sphere of directions.
    python out/r19/foldpre/dirs.py <rule> [more]
1. rule checks: length squared, flat plane exact, both mirrors, largest jump over gaps 1e-3 (the cliff), 1e-4, 1e-5,
   1e-6 between random close pairs on the unit sphere (a tear keeps the jump large as the gap shrinks; a crease does not).
2. the directions sent to -x (buds grow there) and to +x (long arms grow there): where they are (latitude from the
   flat plane, longitude from +x) and the two sideways stretches there (2 and 2 = a round body; more = needle, less = lens).
3. where the crushed directions (smaller stretch under 0.05) are sent.
4. how many times the sphere is covered, the share folded over (mirror-reversed), the largest stretch."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))


def g(F, Q):
    Q = Q / np.linalg.norm(Q, axis=1)[:, None]
    W = np.stack(F(Q[:, 0], Q[:, 1], Q[:, 2]), 1)
    return W / np.linalg.norm(W, axis=1)[:, None]


def stretches(F, V, h=1e-6):
    a = np.cross(V, np.array([0.3, 0.5, 0.8])); a /= np.linalg.norm(a, axis=1)[:, None]; b = np.cross(V, a)
    W0 = g(F, V); da = (g(F, V + h * a) - g(F, V - h * a)) / (2 * h); db = (g(F, V + h * b) - g(F, V - h * b)) / (2 * h)
    det = np.einsum('ij,ij->i', W0, np.cross(da, db))
    sv = np.linalg.svd(np.stack([da, db], 2), compute_uv=False)
    return sv[:, 0], sv[:, 1], det


def latlon(c):
    c = c / np.linalg.norm(c)
    return np.degrees(np.arcsin(np.clip(c[2], -1, 1))), np.degrees(np.arctan2(c[1], c[0]))


def groups(P, sep=8.0):
    out = []; P = list(P)
    while P:
        c = P[0]; A = np.array(P); near = A @ c > np.cos(np.radians(sep))
        out.append((A[near].mean(0), int(near.sum()))); P = [p for p, n in zip(P, near) if not n]
    return out


def refine(F, c, target, it=40):
    """Newton-free polish: walk c so that g(c) = target (small steps along the pulled-back error)."""
    c = c / np.linalg.norm(c)
    for _ in range(it):
        w = g(F, c[None])[0]; e = target - w
        if np.linalg.norm(e) < 1e-10: break
        h = 1e-6; a = np.cross(c, [0.3, 0.5, 0.8]); a /= np.linalg.norm(a); b = np.cross(c, a)
        da = (g(F, (c + h * a)[None])[0] - g(F, (c - h * a)[None])[0]) / (2 * h)
        db = (g(F, (c + h * b)[None])[0] - g(F, (c - h * b)[None])[0]) / (2 * h)
        M = np.stack([da, db], 1); sol, *_ = np.linalg.lstsq(M, e, rcond=None)
        step = sol[0] * a + sol[1] * b
        n = np.linalg.norm(step)
        if n > 0.05: step *= 0.05 / n
        c = c + step; c /= np.linalg.norm(c)
    return c


def screen(name, F, n=1500000, seed=3):
    rng = np.random.default_rng(seed)
    P = rng.normal(size=(20000, 3))
    X, Y, Z = F(P[:, 0], P[:, 1], P[:, 2])
    ln = np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (P ** 2).sum(1)).max()
    X, Y, Z = F(P[:, 0], P[:, 1], 0 * P[:, 2])
    pz = max(np.abs(X - (P[:, 0] ** 2 - P[:, 1] ** 2)).max(), np.abs(Y - 2 * P[:, 0] * P[:, 1]).max(), np.abs(Z).max())
    A0 = np.stack(F(P[:, 0], P[:, 1], P[:, 2]), 1)
    Az = np.stack(F(P[:, 0], P[:, 1], -P[:, 2]), 1) * np.array([1, 1, -1])
    Ay = np.stack(F(P[:, 0], -P[:, 1], P[:, 2]), 1) * np.array([1, -1, 1])
    mz = np.abs(A0 - Az).max(); my = np.abs(A0 - Ay).max()
    jumps = []
    for st in (1e-3, 1e-4, 1e-5, 1e-6):
        A = rng.normal(size=(400000, 3)); A /= np.linalg.norm(A, axis=1)[:, None]
        D = rng.normal(size=(400000, 3)); D /= np.linalg.norm(D, axis=1)[:, None]
        B = A + st * D
        fa = np.stack(F(A[:, 0], A[:, 1], A[:, 2]), 1); fb = np.stack(F(B[:, 0], B[:, 1], B[:, 2]), 1)
        jumps.append(float(np.linalg.norm(fa - fb, axis=1).max()))
    print(f'{name}: length squared to {ln:.0e} | flat plane exact to {pz:.0e} | mirror above/below {mz:.0e}, front/back {my:.0e}')
    print(f'   largest jump over a gap of 1e-3, 1e-4, 1e-5, 1e-6: ' + ', '.join(f'{j:.1e}' for j in jumps)
          + f'   (jump / gap: ' + ', '.join(f'{j / s:.1f}' for j, s in zip(jumps, (1e-3, 1e-4, 1e-5, 1e-6))) + ')')
    V = rng.normal(size=(n, 3)); V /= np.linalg.norm(V, axis=1)[:, None]
    W = g(F, V)
    s1, s2, det = stretches(F, V)
    ok = np.isfinite(det) & np.isfinite(s1)
    print(f'   covers the sphere {det[ok].mean():+.2f} times (signed) | folded over {100 * (det[ok] < 0).mean():.1f} % | '
          f'stretch median {np.median(s1[ok]):.2f}, 99 % {np.percentile(s1[ok], 99):.2f}, largest {s1[ok].max():.1f} | '
          f'angles kept (two stretches within 1 %) on {100 * (s1[ok] / np.maximum(s2[ok], 1e-12) < 1.01).mean():.1f} %')
    res = {}
    for tag, tgt in (('-x', np.array([-1.0, 0, 0])), ('+x', np.array([1.0, 0, 0]))):
        sel = W @ tgt > np.cos(np.radians(1.0))
        gs = [q for q in groups(V[sel][:6000]) if q[1] >= 3]
        rows = []
        for c, cnt in gs:
            c2 = refine(F, c, tgt)
            a1, a2, d = stretches(F, c2[None])
            la, lo = latlon(c2)
            rows.append((la, lo, float(a1[0]), float(a2[0]), float(np.sign(d[0])), float(np.degrees(np.arccos(np.clip(g(F, c2[None])[0] @ tgt, -1, 1))))))
        rows.sort(key=lambda r: (-round(r[0]), r[1]))
        res[tag] = rows
        print(f'   sent to {tag}: {len(rows)} directions')
        for la, lo, a1, a2, sg, err in rows:
            print(f'       latitude {la:+6.1f}, longitude {lo:+7.1f}: stretch {a1:.2f} x {a2:.2f} ({"mirror-reversed" if sg < 0 else "same hand"})'
                  + ('' if err < 0.05 else f'  [polish missed by {err:.2f} degrees]'))
    cr = ok & (s2 < 0.05)
    if cr.any():
        gs = [q for q in groups(W[cr][:6000], sep=15.0) if q[1] >= 3]
        gsrc = [q for q in groups(V[cr][:6000], sep=15.0) if q[1] >= 3]
        print(f'   crushed directions (smaller stretch under 0.05): {100 * cr.mean():.2f} % of all; they sit at '
              + ', '.join('(lat %+.0f, lon %+.0f)' % latlon(q[0]) for q in gsrc[:8]) + ' and are sent to '
              + ', '.join('(lat %+.0f, lon %+.0f)' % latlon(q[0]) for q in gs[:8]))
    else:
        print('   no crushed directions found')
    return res


if __name__ == '__main__':
    import rules as R
    for nm in sys.argv[1:]:
        screen(nm, R.get(nm)); print(flush=True)
