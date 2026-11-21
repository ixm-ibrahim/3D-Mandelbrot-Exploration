import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model3 as M3
km = M3.km
presets = json.load(open('data/klein-presets.json', encoding='utf-8'))
k = presets[int(sys.argv[1])]['k']
mu = np.array([k['mx'], k['my'], k['mz']]); L = k['L']; three = k['three']
P = km.pearls(mu, L, three, eps=0.004)
C, Rr = km.tiles(P, L, three, K=1)
rng = np.random.default_rng(1)
n = 4000
zr = L if three else 0.8
pts = np.column_stack([rng.uniform(-1, 1, n), rng.uniform(0.02, mu[1] - 0.02, n), rng.uniform(-zr, zr, n)])
true = km.clearance(pts, C, Rr)
for name, kw in (('leys', dict(seq=False)), ('seq', dict(seq=True))):
    est = np.array([M3.kde3(p, mu, L, three, **kw)[0] for p in pts])
    fs = (est <= 0) & (true > 0.004)
    ms = (est > 0) & (true < -0.002)
    print(name, "solid share %.3f, true solid share %.3f, false solid %d, missed %d" % ((est <= 0).mean(), (true < 0).mean(), fs.sum(), ms.sum()))
    if fs.any():
        i = np.flatnonzero(fs)[:5]
        for j in i: print("   false solid at", np.round(pts[j], 3), "clearance %.3f" % true[j], "est %.4f" % est[j])
