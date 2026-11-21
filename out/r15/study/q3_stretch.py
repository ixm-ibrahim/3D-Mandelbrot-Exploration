"""Question 3: does the rule keep shapes under repetition? Stretch of F^k in three perpendicular directions.
python out/r15/study/q3_stretch.py [layout keys as python tuples ...]"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox, fastpil as Fp


def jac(pts, key, k, c=None, h=1e-6):
    """numerical derivative of (F + c)^k at pts (M, 3): returns J (M, 3, 3) and the end points; nan where an orbit leaves radius 2."""
    M = pts.shape[0]
    P = [pts]
    for i in range(3):
        e = np.zeros(3); e[i] = h
        P += [pts + e, pts - e]
    A = np.concatenate(P, 0)
    x, y, z = A[:, 0].copy(), A[:, 1].copy(), A[:, 2].copy()
    ok = np.ones(M, bool)
    out = {}
    for it in range(1, k + 1):
        x, y, z = vox.step(x, y, z, key)
        if c is not None:
            x = x + c[0]; y = y + c[1]; z = z + c[2]
            ok &= (x[:M] ** 2 + y[:M] ** 2 + z[:M] ** 2) <= 4.0
        W = np.stack([x, y, z], 1).reshape(7, M, 3)
        J = np.stack([(W[1 + 2 * i] - W[2 + 2 * i]) / (2 * h) for i in range(3)], 2)      # J[m, out, in]
        out[it] = (J.copy(), ok.copy())
    return out


def stats(J, ok):
    sv = np.linalg.svd(J[ok], compute_uv=False)
    good = np.isfinite(sv).all(axis=1) & (sv[:, 2] > 0)
    sv = sv[good]
    r = sv[:, 0] / sv[:, 2]
    return dict(n=int(len(r)), median=float(np.median(r)), p90=float(np.quantile(r, .9)), p99=float(np.quantile(r, .99)), worst=float(r.max()),
                largest_median=float(np.median(sv[:, 0])), smallest_median=float(np.median(sv[:, 2])))


if __name__ == '__main__':
    keys = [Fp.REF, ('merc',), ('bulb',)] + [eval(a) for a in sys.argv[1:]]
    rng = np.random.default_rng(11)
    d = rng.normal(size=(20000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    res = {}
    print('A. F^k without c, 20,000 random directions (length 1). ratio = largest stretch / smallest stretch')
    for key in keys:
        out = jac(d, key, 6, h=1e-7)
        res[str(key)] = {'noc': {}}
        for k in range(1, 7):
            s = stats(*out[k]); res[str(key)]['noc'][k] = s
            print('  %-22s k=%d  median %8.2f   90%% %9.2f   99%% %10.2f   worst %10.3g   (stretch / 2^k: largest %.3f smallest %.4f)' % (
                key, k, s['median'], s['p90'], s['p99'], s['worst'], s['largest_median'] / 2 ** k, s['smallest_median'] / 2 ** k), flush=True)
    for cname, c in (('c = -1', (-1.0, 0, 0)), ('rabbit', (-0.12, 0.74, 0.0))):
        print('B. (F + c)^k with %s: random points in the ball of radius 1.4, kept while the orbit stays inside radius 2' % cname)
        p = rng.normal(size=(60000, 3)); p *= (1.4 * rng.uniform(0, 1, 60000) ** (1 / 3) / np.linalg.norm(p, axis=1))[:, None]
        for key in keys:
            out = jac(p, key, 12, c=c, h=1e-8)
            res[str(key)][cname] = {}
            for k in (1, 2, 3, 4, 6, 8, 10, 12):
                J, ok = out[k]
                if ok.sum() < 200: continue
                s = stats(J, ok); res[str(key)][cname][k] = s
                print('  %-22s k=%2d  n=%5d  median %8.2f   90%% %9.2f   99%% %10.3g' % (key, k, s['n'], s['median'], s['p90'], s['p99']), flush=True)
    json.dump(res, open(os.path.join(HERE, 'q3%s.json' % ('' if len(sys.argv) == 1 else '-extra')), 'w'), indent=1)
