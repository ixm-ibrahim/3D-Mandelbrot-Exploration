"""Second model: one estimate with a switchable rule for choosing the map, checked pearl by pearl.
rule: 'leys' (sheared cell + fitted curve, as shipped), 'near' (nearest centre of the lattices {2m} and {mu + 2m}),
'hyb' (leys while its step stretches, otherwise the nearest centre)."""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M
km = M.km

def kde2(z, mu, L=1.0, three=True, iters=60, rule='hyb', balls=True, ret_steps=False):
    z = np.array(z, float); mu = np.asarray(mu, float)
    a = mu[1]; fs = np.sign(-mu[0]); sx, sz = mu[0] / a, mu[2] / a
    n = len(z); DF = np.ones(n); W = np.full((n, 3), 1e6)
    best = np.minimum(z[:, 1], a - z[:, 1])
    lz = z + 1.0; llz = z - 1.0; live = np.ones(n, bool); steps = np.zeros(n)
    wrap = lambda x, per, s: (x - s) - per * np.floor((x - s) / per) + s
    flipv = np.array([1.0, -1.0, -1.0]); r0 = 0.5 / a
    for _ in range(iters):
        if not live.any(): break
        q = z[live].copy(); w = W[live].copy(); df = DF[live]
        m = len(q)
        # nearest centres of the two lattices
        c0 = np.zeros((m, 3)); c0[:, 0] = 2.0 * np.round(q[:, 0] / 2.0)
        c1 = np.tile(mu, (m, 1)); c1[:, 0] += 2.0 * np.round((q[:, 0] - mu[0]) / 2.0)
        if three:
            c0[:, 2] = 2.0 * L * np.round(q[:, 2] / (2.0 * L)); c1[:, 2] += 2.0 * L * np.round((q[:, 2] - mu[2]) / (2.0 * L))
        d0 = ((q - c0) ** 2).sum(1); d1 = ((q - c1) ** 2).sum(1)
        upN = d1 < d0
        qN = np.where(upN[:, None], c1 - q, q - c0); wN = np.where(upN[:, None], c1 - w, w - c0)
        if rule != 'near':
            qL = q.copy(); wL = w.copy()
            x0 = qL[:, 0].copy(); qL[:, 0] -= sx * qL[:, 1]; qL[:, 0] = wrap(qL[:, 0], 2.0, -1.0); qL[:, 0] += sx * qL[:, 1]; wL[:, 0] += qL[:, 0] - x0
            if three:
                z0 = qL[:, 2].copy(); qL[:, 2] -= sz * qL[:, 1]; qL[:, 2] = wrap(qL[:, 2], 2.0 * L, -L); qL[:, 2] += sz * qL[:, 1]; wL[:, 2] += qL[:, 2] - z0
            xs = qL[:, 0] - 0.5 * mu[0]
            with np.errstate(over='ignore', invalid='ignore'):
                line = a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * np.sign(xs) * (1.0 - np.exp(-(7.2 - (1.95 - a) * 15.0) * np.abs(xs)))
            up = qL[:, 1] >= line
            qL[up] = mu - qL[up]; wL[up] = mu - wL[up]
            if rule == 'leys': q, w = qL, wL
            else:
                useL = (qL * qL).sum(1) < 1.0
                q = np.where(useL[:, None], qL, qN); w = np.where(useL[:, None], wL, wN)
        else:
            q, w = qN, wN
        cand = np.full(m, np.inf)
        if balls:
            zw2 = np.maximum(((q - w) ** 2).sum(1), 1e-30)
            cs = []
            c = np.tile(mu - np.array([0, r0, 0]), (m, 1)); c[:, 0] += 2.0 * np.round((q[:, 0] - mu[0]) / 2.0)
            if three: c[:, 2] += 2.0 * L * np.round((q[:, 2] - mu[2]) / (2.0 * L))
            cs.append(c)
            c = np.zeros((m, 3)); c[:, 1] = r0; c[:, 0] = 2.0 * np.where(q[:, 0] >= 0, 1.0, -1.0); cs.append(c)
            if three:
                c = np.zeros((m, 3)); c[:, 1] = r0; c[:, 2] = 2.0 * L * np.where(q[:, 2] >= 0, 1.0, -1.0); cs.append(c)
            for c in cs:
                pz = ((q - c) ** 2).sum(1) - r0 * r0; pw = ((w - c) ** 2).sum(1) - r0 * r0
                E = pz / (2 * r0 * df)
                t = np.where(pz > 0, 2 * E / (1 + np.sqrt(1 + np.maximum(pz, 0) * np.maximum(pw, 0) / (r0 * r0 * zw2))), E)
                cand = np.minimum(cand, t)
        iR = 1.0 / np.maximum((q * q).sum(1), 1e-20)
        q = mu + q * flipv * iR[:, None]
        w = mu + w * flipv / np.maximum((w * w).sum(1), 1e-20)[:, None]
        z[live] = q; W[live] = w; DF[live] *= iR; df = DF[live]; steps[live] += 1
        zw2 = np.maximum(((q - w) ** 2).sum(1), 1e-30)
        for h, D in ((q[:, 1], w[:, 1]), (a - q[:, 1], a - w[:, 1])):
            E = h / df
            t = np.where(h > 0, E * 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * np.maximum(h, 0) * np.maximum(D, 0) / zw2)), E)
            cand = np.minimum(cand, t)
        best[live] = np.minimum(best[live], cand)
        idx = np.flatnonzero(live)
        done = (((q - llz[live]) ** 2).sum(1) < 1e-5) | (best[live] <= 0)
        llz[idx] = lz[idx]; lz[idx] = q
        live[idx[done]] = False
    return (best, steps) if ret_steps else best

def per_pearl(k, eps=0.004, iters=150, per=24, seed=2, rules=('leys', 'near', 'hyb'), verbose=True):
    mu = np.array([k['mx'], k['my'], k['mz']]); L = k['L']; three = k['three']
    P = km.pearls(mu, L, three, eps=eps)
    c, r = P['c'], P['r']
    rng = np.random.default_rng(seed)
    d = rng.normal(size=(len(r), per, 3)); d /= np.linalg.norm(d, axis=2, keepdims=True)
    rad = rng.uniform(0, 0.97, (len(r), per, 1)) ** (1 / 3)
    pts = (c[:, None, :] + d * rad * r[:, None, None]).reshape(-1, 3)
    ok = (pts[:, 1] > 0) & (pts[:, 1] < mu[1])
    out = {}
    for rule in rules:
        est = kde2(pts, mu, L, three, iters, rule=rule, balls=True)
        miss = ((est > 0) & ok).reshape(len(r), per)
        frac = miss.mean(1)
        whole = (frac > 0.9); part = (frac > 0.04) & ~whole
        line = []
        for lo, hi in ((0.004, 0.01), (0.01, 0.03), (0.03, 0.1), (0.1, 9)):
            sel = (r >= lo) & (r < hi)
            line.append("r %.3f-%.3f: %d pearls, %d invisible, %d cut" % (lo, hi, sel.sum(), (whole & sel).sum(), (part & sel).sum()))
        if verbose: print("  %-5s %s" % (rule, " | ".join(line)), flush=True)
        out[rule] = (int(whole.sum()), int(part.sum()), frac)
    return P, out

if __name__ == '__main__':
    presets = json.load(open('data/klein-presets.json', encoding='utf-8'))
    for i in [int(a) for a in sys.argv[1:]] or range(len(presets)):
        print("== preset", i, presets[i]['name'], flush=True)
        per_pearl(presets[i]['k'])
