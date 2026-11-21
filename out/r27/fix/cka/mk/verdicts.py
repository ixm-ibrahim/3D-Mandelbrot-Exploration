"""Round 27, checker A, bullet 1: the shader's verdict against the twin's against out/r25/klein/tree.py.

For each of the nine settings (three grids x t = 1, 1.4, 2.5) and each depth asked for:
  flat cut:  10 level pieces at z = 0, 45 x 45 points each, every piece with its own random centre and width
  in space: 100 level pieces at random heights in the box, 15 x 15 points each, random centre and width
  (20250 and 22500 points; the points of a piece form a square grid, the pieces are random)
The shader is read through the lab's own handle sampleSlice (alpha = the number de() returns; inside when <= 0).
The twin is window.squaringLab.ballsInside with the same t, grid and rounds. tree.py is called as it is (steps =
rounds). A fourth opinion is my own writing of the recipe from the text of ROUND27.md.
  python verdicts.py [depths, default 16]  -> ../logs/verdicts.json, ../logs/verdicts.txt
"""
import json, os, sys, time
import numpy as np
import drive as D
import ballslib as B

depths = [int(a) for a in sys.argv[1].split(',')] if len(sys.argv) > 1 else [16]
only = sys.argv[2] if len(sys.argv) > 2 else ''
rng = np.random.default_rng(2027)
SETS = [(g, t) for g in (0, 1, 2) for t in (1.0, 1.4, 2.5)]


def pieces(flat):
    out = []
    n = 10 if flat else 100; N = 45 if flat else 15
    for _ in range(n):
        side = rng.uniform(2.6, 3.6)
        out.append([float(rng.uniform(-0.5, 0.5)), float(rng.uniform(-0.35, 0.35)), float(side), 0.0 if flat else float(rng.uniform(-1.3, 1.3)), N])
    return out


JS = D.HEAD + """
const P = %s, t = %r, grid = %d, rounds = %d;
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = grid; S.k.bit = rounds; S.flat = false; go(); await settle();
if (S.k.bt !== t || S.k.bgrid !== grid || S.k.bit !== rounds) fail('the state did not take');
const snap = L.takeSnapshot(), al = [], tw = [], es = [], t0 = performance.now();
for (const [cx, cy, side, z, N] of P) {
  const a = await L.sampleSlice(snap, cx, cy, side, z, N);
  if (!a) fail('sampleSlice gave nothing');
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const x = cx + side * ((i + 0.5) / N - 0.5), y = cy + side * ((j + 0.5) / N - 0.5);
    al.push(+a[4 * (j * N + i) + 3].toPrecision(8));
    tw.push(L.ballsInside(x, y, z, { t, grid, rounds }) ? 1 : 0);
    es.push(+L.ballsEstimate(x, y, z, { t, grid, rounds }).toPrecision(8));
  }
}
L.releaseSnapshot(snap);
return JSON.stringify({ al, tw: tw.join(''), es, ms: Math.round(performance.now() - t0), failed: L.R.failed || '' });
"""


def points(P):
    xs = []
    for cx, cy, side, z, N in P:
        i = (np.arange(N) + 0.5) / N - 0.5
        X, Y = np.meshgrid(cx + side * i, cy + side * i)      # rows = j (y), columns = i (x)
        xs.append(np.stack([X.ravel(), Y.ravel(), np.full(N * N, z)], 1))
    return np.concatenate(xs)


res = []
lines = []
for R in depths:
    for g, t in SETS:
        if only and only != '%d-%g' % (g, t):
            continue
        for flat in (True, False):
            P = pieces(flat)
            tag = 'verd-g%d-t%g-r%d-%s' % (g, t, R, 'flat' if flat else 'space')
            t0 = time.time()
            code, vals, text = D.run(D.PAGE, [D.UP, {'js': JS % (json.dumps(P), t, g, R)}], tag)
            if code != 0 or len(vals) < 2:
                lines.append('%s: RUN FAILED (exit %d): %s' % (tag, code, text[-400:])); print(lines[-1]); continue
            v = vals[1]
            pts = points(P)
            al = np.array(v['al']); sh = al <= 0
            tw = np.array([c == '1' for c in v['tw']])
            es = np.array(v['es'])
            tr = B.tree_inside(pts[:, 0], pts[:, 1], pts[:, 2], t, g, R)
            me = B.recipe_inside(pts[:, 0], pts[:, 1], pts[:, 2], t, g, R)
            ref80 = B.recipe_inside(pts[:, 0], pts[:, 1], pts[:, 2], t, g, 80)
            inbox = (np.abs(pts[:, 0]) <= 1.8) & (np.abs(pts[:, 1]) <= 1.3)
            d = dict(tag=tag, grid=g, t=t, rounds=R, flat=flat, n=int(len(pts)), in_box=int(inbox.sum()), inside_twin=int(tw.sum()),
                     shader_vs_twin=int((sh != tw).sum()), twin_vs_tree=int((tw != tr).sum()), shader_vs_tree=int((sh != tr).sum()),
                     twin_vs_mine=int((tw != me).sum()), depth_vs_80=int((tw != ref80).sum()), ms=v['ms'], failed=v['failed'])
            bad = np.nonzero(sh != tw)[0]
            d['shader_vs_twin_where'] = [dict(p=[float(c) for c in pts[i]], alpha=float(al[i]), twin_est=float(es[i]), twin=bool(tw[i])) for i in bad[:60]]
            d['shader_vs_twin_largest_abs_est'] = float(np.abs(es[bad]).max()) if bad.size else 0.0
            d['shader_vs_twin_largest_abs_alpha'] = float(np.abs(al[bad]).max()) if bad.size else 0.0
            dd = np.nonzero(tw != ref80)[0]
            d['depth_vs_80_where'] = [[float(c) for c in pts[i]] for i in dd[:40]]
            # the shader's distance against the twin's distance (same formula, single against double precision)
            both = (al > 0) & (es > 0)
            rel = (al[both] - es[both]) / es[both]
            d['dist_rel_mean_abs'] = float(np.abs(rel).mean()) if both.any() else 0.0
            d['dist_rel_max_longer'] = float(rel.max()) if both.any() else 0.0
            d['dist_rel_max_shorter'] = float(-rel.min()) if both.any() else 0.0
            res.append(d)
            np.save(os.path.join(D.LOGS, tag + '-pts.npy'), np.column_stack([pts, al, tw, es]))
            lines.append('%-28s points %5d  inside %5d | shader/twin differ %3d (largest twin distance there %.1e) | twin/tree.py differ %d | shader/tree.py %3d | twin/my recipe %d | this depth/80 rounds %d | shader distance vs twin: mean %.1e, longest +%.1e | %d ms'
                         % (tag, d['n'], d['inside_twin'], d['shader_vs_twin'], d['shader_vs_twin_largest_abs_est'], d['twin_vs_tree'], d['shader_vs_tree'], d['twin_vs_mine'], d['depth_vs_80'], d['dist_rel_mean_abs'], d['dist_rel_max_longer'], d['ms']))
            print(lines[-1]); sys.stdout.flush()
suffix = '-'.join(str(r) for r in depths) + (('-' + only) if only else '')
with open(os.path.join(D.LOGS, 'verdicts-%s.json' % suffix), 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=1)
with open(os.path.join(D.LOGS, 'verdicts-%s.txt' % suffix), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
