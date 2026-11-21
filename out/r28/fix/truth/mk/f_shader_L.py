"""Round 28, truth checker: the three grid points of setting L where the shader's own number is longer than the true
distance by more than my first allowance. How much, in units of the last digit of a single-precision number there?
  python out/r28/fix/truth/mk/f_shader_L.py      -> out/r28/fix/truth/logs/f_shader_L.txt     (kept answers of the page; no browser)"""
import gzip, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
import bc_page as B
import f_shader as F
lines = []
for key in ('L', 'I', 'O'):
    raw = json.load(gzip.open(os.path.join(TRUTH, 'logs', 'raw', 'bc_%s.json.gz' % key), 'rt', encoding='utf-8')); job, page = raw['job'], raw['page']
    words, rho, t, gname, depth = B.SETS[key]; top = 2 * float(t); grid = T.Grid(gname)
    P = np.concatenate([F.grid_points(s) for s in job['slices']]); d = np.concatenate([np.array([np.nan if v is None else v for v in g['d']], float) for g in page['slices']])
    o = d > 0; P, d = P[o], d[o]
    reps, info = T.build(grid, top, float(rho), 6e-4); ix = T.Index(reps, grid, top)
    hit = B.over(P, d, ix, top)[0]
    td = B.true_dist(P[hit], d[hit], ix, top); ex = d[hit] - td
    u2 = P[hit, 1] ** 2 + P[hit, 2] ** 2 + (P[hit, 0] - T.K2 / 2) ** 2
    ulp = 1.2e-7 * np.maximum(u2 / T.K2, np.sqrt((P[hit] ** 2).sum(1)) + 1)
    first = ex > 2e-3 * td + 4e-7 * (1 + np.sqrt((P[hit] ** 2).sum(1)))
    lines.append('%s (%s): %d outside grid points, the shader\'s number above the true distance at %d; the largest excess is %.2f last-digit units (%.3g, at distance %.1f from the middle); beyond my first allowance at %d:'
                 % (key, words, len(P), int(hit.sum()), float((ex / ulp).max()), float(ex[np.argmax(ex / ulp)]), float(np.sqrt((P[hit][np.argmax(ex / ulp)] ** 2).sum())), int(first.sum())))
    for k in np.nonzero(first)[0]:
        lines.append('     at (%.4f, %.4f, %.4f): shader %.6g, true %.6g, too long by %.3g = %.2f %% = %.2f last-digit units' % (*P[hit][k], d[hit][k], td[k], ex[k], 100 * ex[k] / td[k], ex[k] / ulp[k]))
out = '\n'.join(lines) + '\n'; open(os.path.join(TRUTH, 'logs', 'f_shader_L.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out)
