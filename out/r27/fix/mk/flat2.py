"""Round 27, fixer: defect A2, the 2D view with the neighbours at 100 (t = 1). How much of the framed 2D view does the
page paint as inside (the number the 2D view is drawn from reads under half a pixel there) although the recipe with
300 rounds calls the point outside and nothing is inside within 2 pixels of it?

The number is read through sampleSlice at 600 x 600 points of the square the 2D view shows (its height, centred as
the view is), so one point stands for about one pixel of a 600-pixel-high picture.
  python out/r27/fix/mk/flat2.py <page> <tag>   -> logs/flat2-<tag>.txt, shots/flat2-<tag>-r16.png
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

JS = run.HEAD + """
const t = %r, g = %d, rounds = %d, N = 600, K2 = 1.05, top = 2 * t;
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = true; S.cut = 0; S.cutOn = false; L.ballsFrame(); go(); await settle();
const sure = (x, y) => { const ux = y, uy = 0, uz = x - K2 / 2; let d = ux * ux + uz * uz; if (!(d > 0)) d = 1e-300;
  let mx = K2 * ux / d, my = 0, mz = 1 + K2 * uz / d;
  for (let i = 0; i < 300; i++) { if (mz < 0 || mz > top) return 1; mx -= Math.round(mx);
    const rb = mx * mx + mz * mz, rt = mx * mx + (mz - top) * (mz - top);
    if (rb < 1) { const s = 1 / rb; mx *= s; mz *= s; } else if (rt < 1) { const s = 1 / rt; mx *= s; mz = top + (mz - top) * s; } else return 0; }
  return 2; };
const side = S.v2.h, cx = S.v2.x, cy = S.v2.y, px = side / N;
const snap = L.takeSnapshot(), a = await L.sampleSlice(snap, cx, cy, side, 0, N); L.releaseSnapshot(snap);
let painted = 0, wrong = 0, wrongDepth = 0, inside = 0;
for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
  const x = cx + side * ((i + 0.5) / N - 0.5), y = cy + side * ((j + 0.5) / N - 0.5), d = a[4 * (j * N + i) + 3];
  if (!(d < 0.5 * px)) continue;
  painted++;
  if (sure(x, y) !== 0) { inside++; continue; }
  let nearSolid = false;
  for (const r of [1, 2]) for (let k = 0; k < 8 && !nearSolid; k++) if (sure(x + r * px * Math.cos(k * Math.PI / 4), y + r * px * Math.sin(k * Math.PI / 4)) !== 0) nearSolid = true;
  if (nearSolid) continue;
  // (the flat cut is the same for the three grids: the page's own verdict here, with the page's rounds)
  if (L.ballsInside(x, y, 0)) wrongDepth++; else wrong++;
}
return JSON.stringify({ t, grid: g, rounds, points: N * N, frameHeight: +side.toFixed(3), painted, trulyInsideOrUndecidedAt300: inside, paintedInOpenBecauseTheDepthLeavesItUndecided: wrongDepth, paintedInOpenWithTheVerdictOutside: wrong });
"""

if __name__ == '__main__':
    page, tag = sys.argv[1], sys.argv[2]
    steps = [run.UP]
    for t, g, R in ((1.0, 0, 16), (1.0, 0, 40), (1.0, 0, 200), (1.4, 0, 16)):
        st = {'js': JS % (t, g, R), 'timeout': 600}
        if t == 1.0 and R == 16:
            st.update(shot='out/r27/fix/shots/flat2-%s-r16.png' % tag, clip='#view')
        steps.append(st)
    code, text, vals = run.shot(page, steps, 'flat2-' + tag, '1400x950', 'dark')
    lines = ['page %s, exit %d, %s' % (page, code, 'no console errors' if 'no console errors' in text else 'SEE THE LOG')]
    for v in vals[1:]:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append(str(v)[:300]); continue
        lines.append('t = %s, depth %3d: of %d points (frame %s high) the page paints %d as inside or outline; of those %d are inside by the recipe with 300 rounds; with nothing inside within 2 px: %d that the depth leaves undecided, %d that the verdict calls outside (the estimate reads under half a pixel there)'
                     % (d['t'], d['rounds'], d['points'], d['frameHeight'], d['painted'], d['trulyInsideOrUndecidedAt300'], d['paintedInOpenBecauseTheDepthLeavesItUndecided'], d['paintedInOpenWithTheVerdictOutside']))
    out = '\n'.join(lines) + '\n'
    run.write('flat2-%s.txt' % tag, out); print(out)
    if code != 0:
        print(text[-2000:])
