"""Fate shares on a 3D grid for every rule and c.  python out/r22/lump/explore2.py [N]  -> fates-table.txt"""
import sys, time, json, os
import numpy as np
import lumplib as L

N = int(sys.argv[1]) if len(sys.argv) > 1 else 72
RULES = ['along', 'oneplane', 'alongmem.c_wake1', 'lathe']
CS = ['rabbit', 'siegel', 't003', 't010', 't020']
g = (np.arange(N) + 0.5) / N * 3.0 - 1.5; gx = (np.arange(N) + 0.5) / N * 3.6 - 1.8
X, Y, Z = np.meshgrid(gx, g, g, indexing='ij'); cell = (3.6 / N) * (3.0 / N) ** 2
out = []; t0 = time.time()
for cs in CS:
    c = L.CSETS[cs]; fc = L.flat_cycle(c)
    print('== %s  c = %s   flat cycle: %s' % (cs, c, 'none (orbit of 0 does not settle)' if fc is None else 'period %d' % len(fc)))
    for rn in RULES:
        r = L.rule(rn)
        burn = 600 if cs == 'rabbit' else 3000
        code, ex = L.fates(r, X, Y, Z, c, burn=burn, lyap_steps=400)
        tot = int((code > 0).sum()); sh = [int((code == k).sum()) for k in range(7)]
        per = ex['period']; pers = {int(p): int((per == p).sum()) for p in np.unique(per)}
        lam = ex['lam']; ok = np.isfinite(lam)
        lq = np.round(np.quantile(lam[ok], [0, 0.5, 1.0]), 4).tolist() if ok.any() else None
        zq = np.quantile(ex['zmax'], [0.5, 0.99, 1.0]).tolist() if tot else None
        print('  %-18s inside %6d (vol %.3f) leaked %4d | flat %5.1f  page %5.1f  offcyc %5.1f  curve %5.1f  cloud %5.1f  slow %5.1f %% | periods %s | zmax med/99/max %s | drift %s | %.0f s'
              % (rn, tot, tot * cell, ex['leaked'], *[100.0 * sh[k] / max(tot, 1) for k in range(1, 7)], pers, None if zq is None else ['%.1e' % q for q in zq], lq, time.time() - t0)); sys.stdout.flush()
        out.append(dict(c=cs, rule=rn, N=N, inside=tot, vol=tot * cell, leaked=ex['leaked'], shares=sh, periods=pers, drift=lq, zmax=zq))
json.dump(out, open(os.path.join(L.HERE, 'fates-table-%d.json' % N), 'w'), indent=1)
