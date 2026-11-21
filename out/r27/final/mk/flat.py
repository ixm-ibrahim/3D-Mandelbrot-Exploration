"""Round 27, final: defect A2 (solid painted where there is no ball, with the neighbours at 100 %), the 2D view, and
defect M (what a saved 3D model says it was made from), on dist/r27-final.html.

A2. The framed 2D view at t = 1, depth 16 and 40 (and t = 1.4 as the control). The number the 2D view is drawn from
is read through sampleSlice at 600 x 600 points of the square the view shows. A point counts as painted when that
number is under half a point's width (inside, or the outline). For each painted point: is it inside by the recipe
(my own writing, 400 rounds, inside only when a wall is reached; "undecided" told apart), and if it is outside, is
anything inside within 2 points of it (16 probes)? Painted, outside and nothing near = solid where there is no ball;
split into "the page's depth leaves it undecided" and "the verdict is outside, the estimate reads too short".
  python out/r27/final/mk/flat.py      -> logs/flat.txt, shots/flat-t1-r16.png
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

JS = run.HEAD + """
const t = %r, rounds = %d, N = 600, K2 = 1.05, top = 2 * t;
for (const e of $('stage').children) e.style.visibility = '';
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
S.k.bt = t; S.k.bgrid = 0; S.k.bit = rounds; S.flat = true; S.cut = 0; S.cutOn = false; L.ballsFrame(); go(); await settle();
// the recipe in the flat cut (z = 0 of the picture is my = 0 of the object): 1 inside, 0 outside, 2 undecided after 400 rounds
const sure = (x, y) => { const ux = y, uz = x - K2 / 2; let d = ux * ux + uz * uz; if (!(d > 0)) d = 1e-300;
  let mx = K2 * ux / d, mz = 1 + K2 * uz / d;
  for (let i = 0; i < 400; i++) { if (mz < 0 || mz > top) return 1; mx -= Math.round(mx);
    const rb = mx * mx + mz * mz, rt = mx * mx + (mz - top) * (mz - top);
    if (rb < 1) { mx /= rb; mz /= rb; } else if (rt < 1) { mx /= rt; mz = top + (mz - top) / rt; } else return 0; }
  return 2; };
const side = S.v2.h, cx = S.v2.x, cy = S.v2.y, px = side / N;
const snap = L.takeSnapshot(), a = await L.sampleSlice(snap, cx, cy, side, 0, N); L.releaseSnapshot(snap);
if (!a) fail('sampleSlice gave nothing');
let painted = 0, insideOrUndecided = 0, nearSomething = 0, byDepth = 0, byEstimate = 0, twinDiffers = 0, realTiny = 0, realNear = 0, noBallMet = 0; const where = [];
for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
  const x = cx + side * ((i + 0.5) / N - 0.5), y = cy + side * ((j + 0.5) / N - 0.5), d = a[4 * (j * N + i) + 3];
  if ((!(d > 0)) !== L.ballsInside(x, y, 0)) twinDiffers++;
  if (!(d < 0.5 * px)) continue;
  painted++;
  if (sure(x, y) !== 0) { insideOrUndecided++; continue; }
  let near = false;
  for (const r of [1, 2]) for (let k = 0; k < 8 && !near; k++) if (sure(x + r * px * Math.cos(k * Math.PI / 4 + 0.2), y + r * px * Math.sin(k * Math.PI / 4 + 0.2)) !== 0) near = true;
  if (near) { nearSomething++; continue; }
  if (L.ballsInside(x, y, 0)) { byDepth++; continue; }
  byEstimate++;
  // My 16 probes cannot see a ball smaller than a point. The exact distance to the nearest ball the search meets
  // from here (300 rounds) can: under half a point = a real ball is that near and the outline is rightly painted.
  const met = L.ballsEstimate(x, y, 0, { t, grid: 0, rounds: 300, parts: true })[0] / px;
  if (met < 0.5) realTiny++; else if (met <= 2) realNear++; else { noBallMet++; if (where.length < 6) where.push([+x.toFixed(4), +y.toFixed(4), +(d / px).toFixed(3), +met.toFixed(1)]); }
}
for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden';
return JSON.stringify({ t, rounds, points: N * N, frame: +side.toFixed(3), painted, insideOrUndecided, nearSomething, byDepth, byEstimate, realTiny, realNear, noBallMet, shaderVsTwin: twinDiffers, where, warn: vis($('ballsWarn')) ? $('ballsWarn').textContent : '' });
"""
MODEL = run.HEAD + """
for (const e of $('stage').children) e.style.visibility = '';
S.k.bt = 1.4; S.k.bgrid = 0; S.k.bit = 16; S.flat = false; L.ballsFrame(); go(); await settle();
let saved = null; window.squaringLabSaveHook = (name, blob) => { saved = { name, blob }; };
window.squaringLabMeshTest = { cells: 48 };
$('meshStart').click(); await sleep(300);
for (let i = 0; i < 1800 && L.meshBusy(); i++) await sleep(50);
if (L.meshBusy()) fail('the model job never ended');
if ($('secMesh')) $('secMesh').open = true; await sleep(100);
if (!$('meshSave')) fail('no save button');
$('meshSave').click(); await sleep(800);
delete window.squaringLabMeshTest; delete window.squaringLabSaveHook;
if (!saved) fail('nothing reached the save hook: ' + ($('meshMsg') ? $('meshMsg').textContent : ''));
const bytes = new Uint8Array(await saved.blob.arrayBuffer()), text = new TextDecoder('latin1').decode(bytes.subarray(0, Math.min(bytes.length, 4000000)));
const lines = [...new Set([...text.matchAll(/Made from[^\\r\\n]{0,400}/g)].map(m => m[0]))];
return JSON.stringify({ M_file: saved.name, M_bytes: bytes.length, M_madeFrom: lines, M_saysT: lines.some(l => /\\bt\\s*=/.test(l)), M_pageSays: $('meshMsg') ? $('meshMsg').textContent.slice(0, 200) : '' });
"""

if __name__ == '__main__':
    steps = [run.UP]
    for t, R in ((1.0, 16), (1.0, 40), (1.4, 16)):
        st = {'js': JS % (t, R)}
        if t == 1.0 and R == 16:
            st.update(shot='out/r27/final/shots/flat-t1-r16.png', clip='#view')
        steps.append(st)
    steps.append({'js': MODEL})
    code, text, vals = run.shot(run.PAGE, steps, 'flat', '1400x950', 'dark')
    run.write('flat.log', text + 'exit %d\n' % code)
    lines = ['page %s, exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/flat.log')]
    for v in vals[1:]:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append(str(v)[:300]); continue
        if 'painted' in d:
            lines.append('A2  t = %s, depth %d: of %d points (frame %s high) painted %d; inside or undecided by the recipe at 400 rounds %d; outside with something inside within 2 points %d; SOLID WHERE THERE IS NO BALL: %d left undecided by the page\'s depth, %d where the verdict is outside and the estimate reads under half a point (of those: a real ball the search meets stands within half a point %d, within 2 points %d, NO BALL MET WITHIN 2 POINTS %d); shader verdict against the twin at all points: %d differ; first places of the last kind [x, y, estimate in points, nearest ball met in points] %s%s'
                         % (d['t'], d['rounds'], d['points'], d['frame'], d['painted'], d['insideOrUndecided'], d['nearSomething'], d['byDepth'], d['byEstimate'], d['realTiny'], d['realNear'], d['noBallMet'], d['shaderVsTwin'], d['where'], ' | ' + d['warn'] if d['warn'] else ''))
        else:
            lines.append('M   ' + json.dumps(d, ensure_ascii=False))
    out = '\n'.join(lines) + '\n'
    run.write('flat.txt', out); print(out)
    if code != 0:
        print(text[-2500:])
