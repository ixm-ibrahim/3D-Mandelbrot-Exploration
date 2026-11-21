"""Question 3: shapes under repetition. Stretch of F^k (no c), k = 1..6, at random points: the ratio of the
largest to the smallest stretch (singular values of the derivative, plain length). The derivative of F^k is the
product of the one-step derivatives along the orbit, each by central differences (step 1e-6 of the point's length).
Four rules: this layout (closed form, power 2), the other layout (out/me/r15/pillow_ref.py), Sphere inversions
one plane (turns.E1), the Mandelbulb at power 2 (latitude and longitude doubled)."""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r15')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import sf, pillow_ref, turns


def f_shadow(P, n=2):
    a, b, c = sf.F(P[:, 0].copy(), P[:, 1].copy(), P[:, 2].copy(), n)
    return np.stack([a, b, c], 1)

def f_pillow(P):
    return pillow_ref.F(P)

def f_one(P):
    a, b, c = turns.E1(P[:, 0], P[:, 1], P[:, 2])
    return np.stack([a, b, c], 1)

def f_bulb(P):
    r = np.linalg.norm(P, axis=1)
    lat = np.arcsin(np.clip(P[:, 2] / r, -1, 1)); lon = np.arctan2(P[:, 1], P[:, 0])
    return (r * r)[:, None] * np.stack([np.cos(2 * lat) * np.cos(2 * lon), np.cos(2 * lat) * np.sin(2 * lon), np.sin(2 * lat)], 1)


def jac(f, P, h=1e-6):
    s = np.linalg.norm(P, axis=1) * h
    J = np.empty((P.shape[0], 3, 3))
    for k in range(3):
        e = np.zeros(3); e[k] = 1
        J[:, :, k] = (f(P + s[:, None] * e) - f(P - s[:, None] * e)) / (2 * s[:, None])
    return J


def study(f, P0, K=6):
    P = P0.copy(); Jt = np.tile(np.eye(3), (P.shape[0], 1, 1)); rows = []
    for k in range(1, K + 1):
        J = jac(f, P)
        Jt = J @ Jt
        P = f(P)
        ok = np.isfinite(Jt).all(axis=(1, 2))
        sv = np.linalg.svd(Jt[ok], compute_uv=False)
        ratio = sv[:, 0] / np.maximum(sv[:, 2], 1e-300)
        rows.append(dict(k=k, median=float(np.median(ratio)), p90=float(np.quantile(ratio, 0.9)), p99=float(np.quantile(ratio, 0.99)),
                         smallest_stretch_median=float(np.median(sv[:, 2])), largest_stretch_median=float(np.median(sv[:, 0])), bad=int((~ok).sum())))
    return rows


if __name__ == '__main__':
    rng = np.random.default_rng(21)
    M = 20000
    d = rng.normal(size=(M, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    # for this layout the rule keeps the surface rho = 1, not the unit sphere: start there so orbits stay of size 1
    rho = sf.gauge(d[:, 0].copy(), d[:, 1].copy(), d[:, 2].copy(), 2)
    out = {}
    for name, f, P0 in (('this layout (closed form), power 2', f_shadow, d / rho[:, None]),
                        ('the other layout (pillow_ref), power 2', f_pillow, d),
                        ('Sphere inversions, one plane', f_one, d),
                        ('Mandelbulb, power 2', f_bulb, d)):
        rows = study(f, P0)
        out[name] = rows
        print(name)
        for r in rows:
            print('   k = %d: largest / smallest stretch, median %10.3g   90 %% %10.3g   99 %% %10.3g   (median smallest stretch %.3g, largest %.3g)'
                  % (r['k'], r['median'], r['p90'], r['p99'], r['smallest_stretch_median'], r['largest_stretch_median']), flush=True)
    # powers 3, 4, 5 of this layout, for the record
    for n in (3, 4, 5):
        rho = sf.gauge(d[:, 0].copy(), d[:, 1].copy(), d[:, 2].copy(), n)
        rows = study(lambda P, n=n: f_shadow(P, n), d / rho[:, None], K=4)
        out['this layout, power %d' % n] = rows
        print('this layout, power %d' % n)
        for r in rows:
            print('   k = %d: median %10.3g   90 %% %10.3g   99 %% %10.3g' % (r['k'], r['median'], r['p90'], r['p99']), flush=True)
    json.dump(out, open(os.path.join(HERE, 'q3.json'), 'w'), indent=1)
