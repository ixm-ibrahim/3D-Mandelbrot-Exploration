"""First look at the page: the state before and after the row, the start view, what sampleSlice hands back."""
import json, sys
import numpy as np
import drive as D
import ballslib as B

steps = [D.UP,
 {'js': D.HEAD + """
const st = () => ({ mode: S.mode, group: S.k.group, approach: S.approach, apId: L.APPROACHES[S.approach].id, flat: S.flat, n: L.APPROACHES.length, bt: S.k.bt, bgrid: S.k.bgrid, bit: S.k.bit });
const before = st();
const row = $('ap-balls');
return JSON.stringify({ before, rowThere: !!row, rowText: row ? row.textContent : null, rowParent: row ? row.parentElement.id + '/' + row.parentElement.className : null,
  keys: Object.keys(L).filter(k => /ball|BALL/.test(k)), stage: [$('stage').clientWidth, $('stage').clientHeight], q: S.q, view: S.view, v2: S.v2 });
"""},
 {'js': D.HEAD + """
L.ballsShow(); await settle();
const b = L.basis();
return JSON.stringify({ mode: S.mode, group: S.k.group, approach: S.approach, flat: S.flat, cam: L.cam, basis: b, view: S.view, v2: S.v2, q: S.q, k: S.k, cut: [S.cutOn, S.cut],
  canvas: [document.querySelector('#stage canvas').width, document.querySelector('#stage canvas').height], dpr: window.devicePixelRatio, status: $('status') ? $('status').textContent : null });
""", 'wait': 'done', 'shot': 'out/r27/checka/shots/look1-start.png'},
 {'js': D.HEAD + """
const snap = L.takeSnapshot();
const N = 8, cx = 0.31, cy = -0.12, side = 2.0, z = 0.17;
const a = await L.sampleSlice(snap, cx, cy, side, z, N);
L.releaseSnapshot(snap);
const out = [];
for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
  const x = cx + side * ((i + 0.5) / N - 0.5), y = cy + side * ((j + 0.5) / N - 0.5);
  out.push([x, y, z, a[4 * (j * N + i) + 3], L.ballsEstimate(x, y, z), L.ballsInside(x, y, z) ? 1 : 0]);
}
return JSON.stringify(out);
"""},
]
code, vals, text = D.run(D.PAGE, steps, 'look1')
print('exit', code)
for v in vals[:3]:
    print(json.dumps(v)[:3000])
pts = np.array(vals[3])
rel = np.abs(pts[:, 3] - pts[:, 4]) / np.maximum(np.abs(pts[:, 4]), 1e-9)
print('sampleSlice alpha against ballsEstimate at my guess of the sample places: largest relative difference %.2e' % rel.max())
print('sign agrees with ballsInside at %d of %d' % (((pts[:, 3] <= 0) == (pts[:, 5] > 0.5)).sum(), len(pts)))
b, f, dec, ins = B.glsl_de(pts[:, :3], 1.4, 0, 16, np.float64)
d = B.glsl_d(b, f, dec, ins)
print('my port (double) against sampleSlice alpha: largest relative difference %.2e' % (np.abs(d - pts[:, 3]) / np.maximum(np.abs(d), 1e-9)).max())
print(text[-600:])
