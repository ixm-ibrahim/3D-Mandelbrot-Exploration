"""Third model: the shipped path, and when it starts going round in a circle (the two-step test), carry on
with the nearest-centre rule until that goes round too. One point at a time in plain Python: slow but simple."""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M
km = M.km

def kde3(p, mu, L, three, iters=150, seq=True, balls=False, cap=None):
    a = mu[1]; fs = float(np.sign(-mu[0])); sx, sz = mu[0] / a, mu[2] / a
    z = np.array(p, float); W = np.array([1e6, 1e6, 1e6]); DF = 1.0
    best = min(z[1], a - z[1]); lz = z + 1; llz = z - 1; phase = 0; r0 = 0.5 / a
    wrap = lambda x, per, s: (x - s) - per * math.floor((x - s) / per) + s
    flipv = np.array([1.0, -1.0, -1.0]); n = 0
    for it in range(iters):
        if phase == 0:
            x0 = z[0]; z[0] -= sx * z[1]; z[0] = wrap(z[0], 2.0, -1.0); z[0] += sx * z[1]; W[0] += z[0] - x0
            if three:
                z0 = z[2]; z[2] -= sz * z[1]; z[2] = wrap(z[2], 2 * L, -L); z[2] += sz * z[1]; W[2] += z[2] - z0
            xs = z[0] - 0.5 * mu[0]
            line = a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * np.sign(xs) * (1.0 - math.exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))
            if z[1] >= line: z = mu - z; W = mu - W
        else:
            c0 = np.array([2.0 * round(z[0] / 2.0), 0.0, 2.0 * L * round(z[2] / (2.0 * L)) if three else 0.0])
            c1 = mu + np.array([2.0 * round((z[0] - mu[0]) / 2.0), 0.0, 2.0 * L * round((z[2] - mu[2]) / (2.0 * L)) if three else 0.0])
            if ((z - c1) ** 2).sum() < ((z - c0) ** 2).sum(): z = c1 - z; W = c1 - W
            else: z = z - c0; W = W - c0
        if balls:
            zw2 = max(((z - W) ** 2).sum(), 1e-30)
            c = mu - np.array([0, r0, 0]); c[0] += 2.0 * round((z[0] - mu[0]) / 2.0)
            if three: c[2] += 2.0 * L * round((z[2] - mu[2]) / (2.0 * L))
            pz = ((z - c) ** 2).sum() - r0 * r0; pw = ((W - c) ** 2).sum() - r0 * r0
            E = pz / (2 * r0 * DF)
            best = min(best, 2 * E / (1 + math.sqrt(1 + max(pz, 0) * max(pw, 0) / (r0 * r0 * zw2))) if pz > 0 else E)
        iR = 1.0 / max((z * z).sum(), 1e-20)
        z = mu + z * flipv * iR; W = mu + W * flipv / max((W * W).sum(), 1e-20); DF *= iR; n += 1
        zw2 = max(((z - W) ** 2).sum(), 1e-30)
        for h, D in ((z[1], W[1]), (a - z[1], a - W[1])):
            E = h / DF
            best = min(best, E * 2.0 / (1.0 + math.sqrt(1.0 + 4.0 * h * max(D, 0) / zw2)) if h > 0 else E)
        if cap is not None: best = min(best, cap / DF)
        if best <= 0: break
        if ((z - llz) ** 2).sum() < 1e-5:
            if phase == 0 and seq: phase = 1; lz = z + 1; llz = z - 1; continue
            break
        llz = lz; lz = z
    return best, n

def run(k, eps=0.004, per=6, seed=2, n_out=3000):
    mu = np.array([k['mx'], k['my'], k['mz']]); L = k['L']; three = k['three']
    P = km.pearls(mu, L, three, eps=eps)
    c, r = P['c'], P['r']
    rng = np.random.default_rng(seed)
    d = rng.normal(size=(len(r), per, 3)); d /= np.linalg.norm(d, axis=2, keepdims=True)
    rad = rng.uniform(0, 0.97, (len(r), per, 1)) ** (1 / 3)
    pts = (c[:, None, :] + d * rad * r[:, None, None]).reshape(-1, 3)
    ok = (pts[:, 1] > 0) & (pts[:, 1] < mu[1])
    C, Rr = km.tiles(P, L, three, K=1)
    zr = L if three else 0.8
    op = np.column_stack([rng.uniform(-1, 1, n_out), rng.uniform(0, mu[1], n_out), rng.uniform(-zr, zr, n_out)])
    true = np.minimum(km.clearance(op, C, Rr), np.minimum(op[:, 1], mu[1] - op[:, 1]))
    sel = true > 2e-3
    for name, kw in (('leys', dict(seq=False)), ('seq', dict(seq=True)), ('seq+ball', dict(seq=True, balls=True))):
        res = np.array([kde3(p, mu, L, three, **kw) for p in pts])
        miss = ((res[:, 0] > 0) & ok).reshape(len(r), per).mean(1)
        whole = miss > 0.9; part = (miss > 0.04) & ~whole
        line = []
        for lo, hi in ((0.004, 0.01), (0.01, 0.03), (0.03, 9)):
            s = (r >= lo) & (r < hi)
            line.append("r %.3f-%.3f: %d, %d invisible, %d cut" % (lo, hi, s.sum(), (whole & s).sum(), (part & s).sum()))
        o = np.array([kde3(p, mu, L, three, **kw) for p in op[sel]])
        ratio = o[:, 0] / true[sel]
        print("  %-8s %s | est/true p90 %.2f p99 %.2f max %.1f, >2: %.2f%%, <0.8: %.2f%% | steps mean %.1f" % (
            name, " | ".join(line), np.percentile(ratio, 90), np.percentile(ratio, 99), ratio.max(), 100 * (ratio > 2).mean(), 100 * (ratio < 0.8).mean(), o[:, 1].mean()), flush=True)

if __name__ == '__main__':
    presets = json.load(open('data/klein-presets.json', encoding='utf-8'))
    for i in [int(a) for a in sys.argv[1:]] or [8, 14, 2]:
        print("== preset", i, presets[i]['name'], flush=True)
        run(presets[i]['k'])
