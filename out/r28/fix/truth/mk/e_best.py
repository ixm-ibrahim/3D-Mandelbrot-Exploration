"""Round 28, truth checker: the first line of section 1.3 (the scale factor of the second inversion, for DF and for W).

  python out/r28/fix/truth/mk/e_best.py      -> out/r28/fix/truth/logs/e_best.txt

"best" in ballsEstimate is meant to be the TRUE distance to the nearest ball the search met. It is made from DF (the
scale factor of all the maps so far) and W (where the picture's far distance has been carried to). If the scale factor
of the second inversion were wrong, "best" would be wrong. So I work the same number out with no scale factor and no
W at all: the two walls are carried BACK through the recipe's moves, one inversion at a time, to explicit balls of the
picture (centre, radius), and the distance from the point to the nearest of them is taken. One browser run asks the
page for [best, free] at 6000 outside points a setting.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
import pagerun as R
import bc_page as B

JS = """
const J = %s, out = [];
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
for (const s of J) {
  const r = [], o = { t: s.t, grid: s.g, rounds: s.depth, rho: s.rho, parts: true };
  for (let i = 0; i < s.p.length; i += 3) { const e = L.ballsEstimate(s.p[i], s.p[i + 1], s.p[i + 2], o); r.push(e[0], e[1]); }
  out.push(r);
}
return JSON.stringify(out);
"""


def my_best(P, grid, top, rho, depth):
    """The distance from each picture point to the nearest of the balls its own search meets: both walls, carried back
    through the first j inversions of the search, j = 0, 1, ... . No DF, no W."""
    mx, my, mz = T.frame(P[:, 0], P[:, 1], P[:, 2])
    st, ch = T.recipe(mx, my, mz, grid, top, rho, depth, keep=True)
    NX, NY, INV = ch['nx'], ch['ny'], ch['inv']; n = len(P)
    J = (INV != 0).sum(0)                                            # inversions the search made (they come first, one a round)
    o = [None, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, top])]; R2 = [None, 1.0, rho * rho]
    u = np.column_stack([P[:, 1], P[:, 2], P[:, 0] - T.K2 / 2])
    best = np.full(n, np.inf)
    for j in range(0, depth + 1):
        act = np.nonzero(J >= j)[0]
        if act.size == 0:
            break
        for wall in (1, 2):
            c = np.zeros((act.size, 3)); r = np.zeros(act.size); half = np.full(act.size, wall)
            for k in range(j - 1, -1, -1):
                inv = INV[k, act]
                for s in (1, 2):
                    a = np.nonzero(inv == s)[0]
                    if a.size == 0:
                        continue
                    h = half[a]
                    oth = a[(h != 0) & (h != s)]                      # the wall that does not pass through this sphere's centre becomes a ball
                    if oth.size:
                        rad = R2[s] / (2 * top); c[oth] = o[s] + np.array([0.0, 0.0, rad if s == 1 else -rad]); r[oth] = rad; half[oth] = 0
                    b = a[h == 0]
                    if b.size:
                        d = c[b] - o[s]; den = (d * d).sum(1) - r[b] ** 2
                        c[b] = o[s] + R2[s] * d / den[:, None]; r[b] = R2[s] * r[b] / np.abs(den)
                c[:, 0] += np.where(half == 0, NX[k, act], 0.0); c[:, 1] += np.where(half == 0, NY[k, act], 0.0)
            # to the picture
            dist = np.full(act.size, np.inf)
            hL = half == 1; hU = half == 2; bl = half == 0
            if hL.any():
                dist[hL] = np.sqrt((P[act[hL]] ** 2).sum(1)) - T.K2 / 2
            if hU.any():
                rU = T.K2 / (2 * (top - 1.0)); cU = np.array([T.K2 / 2 + rU, 0.0, 0.0])
                dist[hU] = np.sqrt(((P[act[hU]] - cU) ** 2).sum(1)) - rU
            if bl.any():
                d = c[bl] - T.C0; den = (d * d).sum(1) - r[bl] ** 2
                uc = T.K2 * d / den[:, None]; rp = T.K2 * r[bl] / np.abs(den); dd = np.sqrt(((u[act[bl]] - uc) ** 2).sum(1))
                dist[bl] = np.where(den > 0, dd - rp, rp - dd)
            best[act] = np.minimum(best[act], dist)
    return best, st


if __name__ == '__main__':
    keys = ['A', 'D', 'E', 'G', 'I', 'J', 'L']
    jobs = []; meta = []
    for key in keys:
        words, rho, t, gname, depth = B.SETS[key]; rho = float(rho); t = float(t); grid = T.Grid(gname); top = 2 * t; p = 100 / (top - 1)
        rng = np.random.default_rng(77 + ord(key))
        X = float(min(T.K2 / 2 + T.K2 * p / 100 + 0.4, 12.0)); Y = float(min(max(T.K2 / 2, T.K2 * p / 200) + 0.3, 6.5))
        C = np.column_stack([rng.uniform(-X, X, 30000), rng.uniform(-Y, Y, 30000), rng.uniform(-Y, Y, 30000)])
        close = rng.random(30000) < 0.6; rad = Y * rng.random(30000) ** 2; ang = rng.uniform(0, 2 * np.pi, 30000)
        C[close, 1] = (rad * np.cos(ang))[close]; C[close, 2] = (rad * np.sin(ang))[close]
        C = B.rnd10(C); C = C[~T.inside_pic(C[:, 0], C[:, 1], C[:, 2], grid, top, rho, depth)][:6000]
        jobs.append(dict(t=t, g=B.GID[gname], depth=depth, rho=rho, p=C.ravel().tolist())); meta.append((key, words, rho, top, grid, depth, C))
    code, text, vals = R.run(R.PAGE, [JS % json.dumps(jobs)], 'e_best')
    lines = ['page %s, exit %d, %s' % (R.PAGE, code, 'no console errors' if R.clean(text) else 'CONSOLE: see logs/e_best.log')]
    got = json.loads(vals[-1])
    for (key, words, rho, top, grid, depth, C), g in zip(meta, got):
        e = np.array(g, float).reshape(-1, 2); mine, st = my_best(C, grid, top, rho, depth)
        ok = (e[:, 0] > 0) & np.isfinite(mine)
        rel = np.abs(e[ok, 0] - mine[ok]) / np.maximum(mine[ok], 1e-12)
        lines.append('%s (%s): %d outside points; the page\'s "best" against the distance to the nearest ball the search met, worked out from explicit balls: largest relative difference %.2e, more than 1e-6 apart at %d; "best" is the smaller of the page\'s two numbers at %d'
                     % (key, words, int(ok.sum()), float(rel.max()), int((rel > 1e-6).sum()), int((e[ok, 0] <= e[ok, 1]).sum())))
    out = '\n'.join(lines) + '\n'
    open(os.path.join(R.LOGS, 'e_best.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out)
