"""Round 27, checker A: read the shader's number de() and the twin at level pieces of points, through the lab's own
handle sampleSlice (alpha of a volume sample: gPix = 0, the estimate with nothing held up).
  sample(g, t, R, P, tag) -> pts (n x 3), alpha, twin verdict (bool), twin estimate, [twin best, twin free]
P: list of [cx, cy, side, z, N]; the points of a piece are cx + side * ((i + 0.5) / N - 0.5), same in y, at height z.
"""
import json
import numpy as np
import drive as D

JS = D.HEAD + """
const P = %s, t = %r, grid = %d, rounds = %d;
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = grid; S.k.bit = rounds; S.flat = false; go(); await settle();
if (S.k.bt !== t || S.k.bgrid !== grid || S.k.bit !== rounds) fail('the state did not take');
const snap = L.takeSnapshot(), al = [], tw = [], es = [], bs = [], fr = [], t0 = performance.now();
for (const [cx, cy, side, z, N] of P) {
  const a = await L.sampleSlice(snap, cx, cy, side, z, N);
  if (!a) fail('sampleSlice gave nothing');
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const x = cx + side * ((i + 0.5) / N - 0.5), y = cy + side * ((j + 0.5) / N - 0.5);
    al.push(+a[4 * (j * N + i) + 3].toPrecision(8));
    tw.push(L.ballsInside(x, y, z, { t, grid, rounds }) ? 1 : 0);
    const e = L.ballsEstimate(x, y, z, { t, grid, rounds, parts: true });
    bs.push(+e[0].toPrecision(8)); fr.push(+e[1].toPrecision(8));
  }
}
L.releaseSnapshot(snap);
return JSON.stringify({ al, tw: tw.join(''), bs, fr, ms: Math.round(performance.now() - t0), failed: L.R.failed || '' });
"""


def points(P):
    xs = []
    for cx, cy, side, z, N in P:
        N = int(N)
        i = (np.arange(N) + 0.5) / N - 0.5
        X, Y = np.meshgrid(cx + side * i, cy + side * i)
        xs.append(np.stack([X.ravel(), Y.ravel(), np.full(N * N, z)], 1))
    return np.concatenate(xs)


def sample(g, t, R, P, tag, page=None):
    code, vals, text = D.run(page or D.PAGE, [D.UP, {'js': JS % (json.dumps(P), t, g, R)}], tag)
    if code != 0 or len(vals) < 2:
        raise RuntimeError('%s: run failed (exit %d): %s' % (tag, code, text[-600:]))
    v = vals[1]
    pts = points(P)
    al = np.array(v['al']); tw = np.array([c == '1' for c in v['tw']])
    bs = np.array(v['bs']); fr = np.array(v['fr'])
    return pts, al, tw, np.minimum(bs, fr), bs, fr
