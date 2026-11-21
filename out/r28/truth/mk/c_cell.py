"""Round 28, truth checker, 1.4 c (first half), a second pass: the "certainly free" length, everywhere in a cell.

  python out/r28/truth/mk/c_cell.py [keys ...]     -> out/r28/truth/logs/c_cell.txt

"free" depends on the place m where the recipe ends OUTSIDE: a point of the middle cell, between the walls, outside
both spheres. So here the test points FILL that region evenly (in the object's own coordinates), are slid by a whole
number and carried to the picture. For such a point the search makes no inversion: its "best" is the distance to the
two walls only, and everything else rests on the hulls of section 1.3. Three sets of 20000 outside points a setting:
  cell : anywhere in the cell between the walls;
  low  : in the lowest part, up to 1.3 HB above the bottom wall (hull ball, rest, cell corners);
  high : in the highest part, down to 1.5 max(HT, rho) below the top wall (hull ball, rest, bare wall, the foot of
         the second sphere).
The test is the one of bc_page.py: the ball of radius ballsEstimate about the point must meet no ball of my list.
One browser run for all settings (only ballsEstimate is asked).
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
import pagerun as R
import bc_page as B

JS = """
const J = %s, out = [];
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
for (const s of J) {
  const res = {}, o = { t: s.t, grid: s.g, rounds: s.depth, rho: s.rho, parts: true };
  for (const name of Object.keys(s.est)) {
    const p = s.est[name], r = [];
    for (let i = 0; i < p.length; i += 3) { const e = L.ballsEstimate(p[i], p[i + 1], p[i + 2], o); r.push(e[0], e[1]); }
    res[name] = r;
  }
  out.push(res);
}
return JSON.stringify(out);
"""
N = 20000

if __name__ == '__main__':
    keys = sys.argv[1:] or ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'L', 'M', 'O']
    jobs = []; meta = []
    for key in keys:
        words, rho, t, gname, depth = B.SETS[key]; rho = float(rho); t = float(t); grid = T.Grid(gname); top = 2 * t; h = T.hulls(top, rho)
        rng = np.random.default_rng(4242 + ord(key)); n = 6 * N; est = {}
        xy = lambda: rng.uniform(-0.6, 0.6, (n, 2)) * (np.array([1.0, 1.0]) if gname != 'line' else np.array([1.0, 0.6]))
        zs = dict(cell=rng.uniform(0, top, n), low=rng.uniform(0, min(1.3 * h['HB'], top), n), high=top - rng.uniform(0, min(1.5 * max(h['HT'], rho), top), n))
        for name, z in zs.items():
            M = np.column_stack([xy(), z])
            if gname == 'line':
                M[::2, 1] *= 0.1                                   # half of them close to the flat plane, where the balls are
            C = B.rnd10(B.slid_to_picture(rng, grid, M)); C = C[np.sqrt((C * C).sum(1)) < 60.0]
            C = C[~T.inside_pic(C[:, 0], C[:, 1], C[:, 2], grid, top, rho, depth)][:N]
            est[name] = C
        jobs.append(dict(t=t, g=B.GID[gname], depth=depth, rho=rho, est={k: v.ravel().tolist() for k, v in est.items()})); meta.append((key, words, rho, top, grid, gname, est))
    t0 = time.time()
    code, text, vals = R.run(R.PAGE, [JS % json.dumps(jobs)], 'c_cell')
    lines = ['page %s, exit %d, %s, %.0f s in the browser' % (R.PAGE, code, 'no console errors' if R.clean(text) else 'CONSOLE: see logs/c_cell.log', time.time() - t0)]
    got = json.loads(vals[-1]); total = [0, 0]
    for (key, words, rho, top, grid, gname, est), g in zip(meta, got):
        reps, info = T.build(grid, top, rho, 2e-5 if gname == 'line' else 6e-4); ix = T.Index(reps, grid, top)
        lines.append('=== %s: %s (my list: %d balls)' % (key, words, info['n']))
        for name in ('cell', 'low', 'high'):
            P = est[name]; e = np.array(g[name], float).reshape(-1, 2); E = np.minimum(e[:, 0], e[:, 1]); o = E > 0
            Pn, En = P[o], E[o]
            hit = B.over(Pn, En, ix, top)[0]; loose = ~B.over(Pn, 2 * En, ix, top)[0]
            # how many of these points end at once (no inversion): "best" is then the walls alone
            m = np.column_stack(T.frame(Pn[:, 0], Pn[:, 1], Pn[:, 2])); nx, ny = grid.nearest(m[:, 0], m[:, 1])
            at_once = (((m[:, 0] - nx) ** 2 + (m[:, 1] - ny) ** 2 + m[:, 2] ** 2 >= 1) & ((m[:, 0] - nx) ** 2 + (m[:, 1] - ny) ** 2 + (m[:, 2] - top) ** 2 >= rho * rho))
            lines.append('    %-4s: %d outside points (%d of them end at once, with no inversion); estimate longer than the true distance to the nearest listed ball at %d; "free" is the smaller number at %d; twice the estimate would still be free at %d'
                         % (name, len(Pn), int(at_once.sum()), int(hit.sum()), int((e[o, 1] < e[o, 0]).sum()), int(loose.sum())))
            total[0] += len(Pn); total[1] += int(hit.sum())
            if hit.any():
                td = B.true_dist(Pn[hit], En[hit], ix, top); ex = En[hit] - td
                for j in np.argsort(-ex)[:6]:
                    mm = m[hit][j]; a, b = grid.nearest(mm[0], mm[1])
                    lines.append('         too long at picture (%.8f, %.8f, %.8f): estimate %.6g (best %.6g, free %.6g), true %.6g, too long by %.3g; in the cell: (%.5f, %.5f, %.5f)'
                                 % (*Pn[hit][j], En[hit][j], e[o][hit][j, 0], e[o][hit][j, 1], td[j], ex[j], mm[0] - a, mm[1] - b, mm[2]))
        print('\n'.join(lines[-4:]), flush=True)
    lines.append('TOTAL: %d outside points, estimate longer than the true distance to the nearest listed ball at %d' % tuple(total))
    out = '\n'.join(lines) + '\n'
    open(os.path.join(R.LOGS, 'c_cell.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out[-3000:])
