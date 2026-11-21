"""Candidates for the "Turning-out sphere" entries: for a handful of groups, list roomy gaps (and a few hand-made
centres), and check each against the direct pearl list: is the centre in a gap, and does the search of the shader
(ported in model3.kde3) draw every pearl that will look big, whole?   python out/r4/kleinian/find.py"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model3 as M3
km = M3.km
GROUPS = {   # name: (mu, three, L)
    '0/1x3': ((0.0, 2.0, 0.0), True, 1.0),
    '0/1': ((0.0, 2.0, 0.0), False, 1.0),
    '1/2': ((1.0, 1.732051, 0.0), False, 1.0),
    '1/3x3': ((0.581203, 1.693897, 0.0), True, 1.0),
    '1/3': ((0.581203, 1.693897, 0.0), False, 1.0),
    '1/4': ((0.352201, 1.721433, 0.0), False, 1.0),
    '2/5': ((0.766588, 1.642139, 0.0), False, 1.0),
    '1/15': ((0.011279, 1.958591, 0.0), False, 1.0),
    'lean30': ((0.0, 1.732051, 1.0), False, 1.0),
    'lean30x3': ((0.0, 1.732051, 1.0), True, 1.0),
    'stretch': ((0.0, 2.0, 0.0), True, 2.0),
}
MANUAL = {   # centres worth trying beside the roomiest gaps: off the plane, off the middle of a gap, near where pearls touch
    '0/1': [(1, 1, 0.7), (1, 1, 1.4), (1, 0.45, 0), (0.55, 1, 0), (1, 1.62, 0), (0.42, 0.5, 0.3), (1, 0.3, 0.5)],
    '0/1x3': [(1, 1, 1), (0, 1, 1), (1, 0.5, 0), (1, 1, 0.5), (0.5, 1, 1), (1, 1.55, 1)],
    '1/2': [(-1, 0.5774, 0.6), (0, 0.5774, 0), (0, 1.1547, 0), (0, 0.5774, 0.6), (-1, 0.3, 0)],
    '1/3': [(0.2906, 0.8469, 0.5), (0.2906, 0.8469, 0)],
    '1/3x3': [(0.2906, 0.8469, 1), (0.2906, 0.8469, 0.5)],
    '1/4': [(-0.647, 1.2734, 0.5)],
    '2/5': [(1.3833, 0.8211, 0.5)],
    '1/15': [(-1, 0.4894, 0.5), (0, 0.98, 0), (-1, 1.47, 0)],
    'lean30': [(1, 0.866, 0.5), (1, 0.866, -0.5), (0, 0.866, 0.5)],
    'lean30x3': [(1, 0.866, 0.5), (0, 0.866, 1)],
    'stretch': [(1, 1, 2), (0, 1, 2), (1, 1, 1)],
}
EXIST = [(p['k']['mx'], p['k']['my'], p['k']['mz'], p['k']['three'], p['k']['cx'], p['k']['cy'], p['k']['cz']) for p in json.load(open('data/klein-presets.json', encoding='utf-8'))[:19]]
out = []
rng = np.random.default_rng(4)
for name, (mu, three, L) in GROUPS.items():
    mu = np.array(mu)
    P = km.pearls(mu, L, three, eps=0.004)
    Cc, Rr = km.tiles(P, L, three, K=2)
    cands = [tuple(c) for c in MANUAL.get(name, [])]
    for cl, c in km.gaps(mu, L, three, P=km.pearls(mu, L, three, eps=0.01), plane=not three, top=5):
        cands.append(tuple(c))
    for c in cands:
        C = np.array(c, float)
        if any(abs(e[0] - mu[0]) < 1e-6 and abs(e[1] - mu[1]) < 1e-6 and abs(e[2] - mu[2]) < 1e-6 and e[3] == three and np.linalg.norm(np.array(e[4:]) - C) < 0.12 for e in EXIST):
            continue
        d = np.linalg.norm(Cc - C, axis=1)
        clear = float(min((d - Rr).min(), C[1], mu[1] - C[1]))
        if clear < 0.04: continue
        # with invR = 1: display radius and distance of each pearl; the walls too
        den = d * d - Rr * Rr
        rad = Rr / den; dist = d / den
        ext = float(max((dist + rad).max(), 1 / C[1], 1 / (mu[1] - C[1])))
        # the pearls that will look biggest: are they whole for the shader's search?
        order = np.argsort(-rad)[:14]
        worst = 0.0
        for j in order:
            if rad[j] < 0.02 * ext: break
            dirs = rng.normal(size=(14, 3)); dirs /= np.linalg.norm(dirs, axis=1)[:, None]
            pts = Cc[j] + dirs * Rr[j] * rng.uniform(0.3, 0.95, (14, 1))
            miss = np.mean([M3.kde3(p, mu, L, three, iters=60, seq=False)[0] > 0 for p in pts])
            worst = max(worst, float(miss))
        out.append(dict(group=name, k=dict(mx=float(mu[0]), my=float(mu[1]), mz=float(mu[2]), three=three, L=L, cx=float(C[0]), cy=float(C[1]), cz=float(C[2]), invR=round(float((1.3 / ext) ** 0.5), 3)), clear=round(clear, 3), ext1=round(ext, 2), worst=round(worst, 2)))
        print("%-9s C=%-22s clear %.3f extent(R=1) %6.2f -> invR %.3f  worst share of a big pearl missed %.2f" % (name, c, clear, ext, out[-1]['k']['invR'], worst), flush=True)
json.dump(out, open('out/r4/kleinian/cands.json', 'w'), indent=1)
print(len(out), "candidates")
