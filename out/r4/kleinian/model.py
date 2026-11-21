"""Python model of candidate Kleinian estimates, checked against the direct pearl list (notes/klein_model.py)."""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'notes'))
import klein_model as km

def kde_new(z, mu, L=1.0, three=True, iters=60, rule='leys', balls=True, cyc=True):
    """returns best (exact distance to the pearls met; <= 0 inside)."""
    z = np.array(z, float); mu = np.asarray(mu, float)
    a = mu[1]; fs = np.sign(-mu[0]); sx, sz = mu[0] / a, mu[2] / a
    n = len(z); DF = np.ones(n); W = np.full((n, 3), 1e6)
    best = np.minimum(z[:, 1], a - z[:, 1])
    lz = z + 1.0; llz = z - 1.0; live = np.ones(n, bool)
    wrap = lambda x, per, s: (x - s) - per * np.floor((x - s) / per) + s
    flipv = np.array([1.0, -1.0, -1.0]); r0 = 0.5 / a
    for _ in range(iters):
        if not live.any(): break
        q = z[live]; w = W[live]; df = DF[live]
        x0 = q[:, 0].copy(); q[:, 0] -= sx * q[:, 1]; q[:, 0] = wrap(q[:, 0], 2.0, -1.0); q[:, 0] += sx * q[:, 1]; w[:, 0] += q[:, 0] - x0
        if three:
            z0 = q[:, 2].copy(); q[:, 2] -= sz * q[:, 1]; q[:, 2] = wrap(q[:, 2], 2.0 * L, -L); q[:, 2] += sz * q[:, 1]; w[:, 2] += q[:, 2] - z0
        xs = q[:, 0] - 0.5 * mu[0]
        if rule == 'leys':
            with np.errstate(over='ignore', invalid='ignore'):
                line = a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * np.sign(xs) * (1.0 - np.exp(-(7.2 - (1.95 - a) * 15.0) * np.abs(xs)))
            up = q[:, 1] >= line
        else:   # nearer centre: the generator that stretches most
            up = ((q - mu) ** 2).sum(1) < (q * q).sum(1)
        q[up] = mu - q[up]; w[up] = mu - w[up]
        cand = np.full(len(q), np.inf)
        if balls:
            zw2 = np.maximum(((q - w) ** 2).sum(1), 1e-30)
            cs = []
            # the pearl hanging from the upper wall at mu (nearest translate), and the next translates of the one at the origin
            c = np.tile(mu - np.array([0, r0, 0]), (len(q), 1)); c[:, 0] += 2.0 * np.round((q[:, 0] - mu[0]) / 2.0)
            if three: c[:, 2] += 2.0 * L * np.round((q[:, 2] - mu[2]) / (2.0 * L))
            cs.append(c)
            c = np.zeros((len(q), 3)); c[:, 1] = r0; c[:, 0] = 2.0 * np.where(q[:, 0] >= 0, 1.0, -1.0); cs.append(c)
            if three:
                c = np.zeros((len(q), 3)); c[:, 1] = r0; c[:, 2] = 2.0 * L * np.where(q[:, 2] >= 0, 1.0, -1.0); cs.append(c)
            for c in cs:
                pz = ((q - c) ** 2).sum(1) - r0 * r0; pw = ((w - c) ** 2).sum(1) - r0 * r0
                E = pz / (2 * r0 * df)
                t = np.where(pz > 0, 2 * E / (1 + np.sqrt(1 + np.maximum(pz, 0) * np.maximum(pw, 0) / (r0 * r0 * zw2))), E)
                cand = np.minimum(cand, t)
        iR = 1.0 / np.maximum((q * q).sum(1), 1e-20)
        q = mu + q * flipv * iR[:, None]
        w = mu + w * flipv / np.maximum((w * w).sum(1), 1e-20)[:, None]
        z[live] = q; W[live] = w; DF[live] *= iR; df = DF[live]
        zw2 = np.maximum(((q - w) ** 2).sum(1), 1e-30)
        for h, D in ((q[:, 1], w[:, 1]), (a - q[:, 1], a - w[:, 1])):
            E = h / df
            t = np.where(h > 0, E * 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * np.maximum(h, 0) * np.maximum(D, 0) / zw2)), E)
            cand = np.minimum(cand, t)
        best[live] = np.minimum(best[live], cand)
        idx = np.flatnonzero(live)
        if cyc:
            done = ((q - llz[live]) ** 2).sum(1) < 1e-5
        else:
            done = np.zeros(len(q), bool)
        done |= best[live] <= 0
        llz[idx] = lz[idx]; lz[idx] = q
        live[idx[done]] = False
    return best

def study(k, eps=0.006, n=60000, iters=150, seed=5):
    mu = np.array([k['mx'], k['my'], k['mz']]); L = k['L']; three = k['three']
    t0 = time.time()
    P = km.pearls(mu, L, three, eps=eps)
    print("pearls: %d, overlap %.3g, complete %s, %.1fs" % (len(P['r']), P['overlap'], P['complete'], time.time() - t0))
    c, r = km.tiles(P, L, three, K=1)
    rng = np.random.default_rng(seed)
    zr = L if three else 0.8
    pts = np.column_stack([rng.uniform(-1, 1, n), rng.uniform(0, mu[1], n), rng.uniform(-zr, zr, n)])
    true = np.minimum(km.clearance(pts, c, r), np.minimum(pts[:, 1], mu[1] - pts[:, 1]))
    inside = true < -1e-4; out = true > 2e-3
    res = {}
    for name, kw in (('old', None), ('exact leys', dict(rule='leys', balls=False)), ('exact leys+balls', dict(rule='leys', balls=True)),
                     ('exact near', dict(rule='near', balls=False)), ('exact near+balls', dict(rule='near', balls=True))):
        if kw is None:
            est, _ = km.kde(pts, mu, L, three, iters)
        else:
            est = kde_new(pts, mu, L, three, iters, **kw)
        miss = inside & (est > 0)
        ratio = est[out] / true[out]
        print("%-18s inside missed %5d of %5d (%.2f%%) | est/true: median %.2f p90 %.2f p99 %.2f p99.9 %.2f max %.1f | share>1.25: %.2f%% >2: %.2f%% | est<0.8true: %.2f%%" % (
            name, miss.sum(), inside.sum(), 100.0 * miss.sum() / max(1, inside.sum()), np.median(ratio), np.percentile(ratio, 90), np.percentile(ratio, 99),
            np.percentile(ratio, 99.9), ratio.max(), 100 * (ratio > 1.25).mean(), 100 * (ratio > 2).mean(), 100 * (ratio < 0.8).mean()), flush=True)
        res[name] = (est, miss)
    return pts, true, res, (c, r)

if __name__ == '__main__':
    presets = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'klein-presets.json'), encoding='utf-8'))
    for i in [int(a) for a in sys.argv[1:]] or [8, 14]:
        print("== preset", i, presets[i]['name'])
        study(presets[i]['k'])
