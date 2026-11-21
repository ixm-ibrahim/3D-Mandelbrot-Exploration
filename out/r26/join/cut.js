// "Done" for 3D, on the joined page:
// (1) the 3D module's slice at z = 0 (worked out on the graphics card, by the program the picture is drawn with)
//     against the 2D picture's own numbers (LEARN.shape.mask2), point for point, for all 21 approaches; and beside
//     it whether the page shows the sentence "cutting the 3D shape through the middle (at z = 0) gives exactly the
//     2D shape of the same step" for that approach. Shown must mean: they agree (but for points a hair from a skin).
// (2) the slice at z = 0.3 against the JavaScript twin (learnShape3d.out).
// 257 x 257 and 129 x 129 points, 16 steps, power 2.
//@
await shapeOn({ kind: 'm', space: 3, pos: 4 });
window.__v = LAB.learnShape3d.make();
if (!window.__v) fail('no 3D view');
return 'ready';
//@
const v = window.__v, SIZE = 257, rows = [], bad = [];
let worstShown = 0, leastNotShown = 1e9;
for (const a of LAB.APPROACHES) {
  await approach(a.id); S.n = 2; go(); await sleep(60);
  const cells = [];
  let shown = true;
  for (const [kind, c] of [['m', [0, 0, 0]], ['j', [-1, 0, 0]], ['j', [-0.1226, 0.7449, 0]]]) {
    L.shape.set({ kind, c, space: 3 });
    shown = shown && $('learnShapeNotice').textContent.includes('cutting the 3D shape');
    const g = v.slice(kind, c, { z: 0, half: 2, size: SIZE, maxK: 16 }), f = L.shape.mask2(kind, SIZE, 2, 16);
    if (!g) fail('no slice for ' + a.id);
    let d = 0; for (let i = 0; i < SIZE * SIZE; i++) if (g[i] !== f[i]) d++;
    cells.push(d);
  }
  const most = Math.max(...cells);
  if (shown) worstShown = Math.max(worstShown, most); else leastNotShown = Math.min(leastNotShown, most);
  if (shown && most > 12) bad.push(a.id + ' shows the sentence but ' + most + ' points differ');
  if (!shown && most <= 12) bad.push(a.id + ' keeps the flat picture (' + most + ' differ) but the sentence is not shown');
  rows.push(a.id + ': ' + cells.join(', ') + (shown ? '  (sentence shown)' : '  (sentence NOT shown)'));
}
if (bad.length) fail(bad.join('; ') + ' | ' + rows.join(' | '));
return { 'slice at z = 0 against mask2: points that differ, of 66,049 (Mandelbrot shape, Julia c = -1, Julia rabbit)': rows, mostWhereTheSentenceIsShown: worstShown, leastWhereItIsNot: leastNotShown };
//@
const v = window.__v, T3 = LAB.learnShape3d, SIZE = 129, rows = [];
let total = 0, pts = 0;
for (const id of ['mercator', 'fold', 'lathe', 'turnalong', 'alongonce', 'pulledplane', 'bulb', 'classic']) {
  await approach(id); S.n = 2; go(); await sleep(60);
  const cells = [];
  for (const [kind, c] of [['m', [0, 0, 0]], ['j', [-1, 0, 0]], ['j', [-0.1226, 0.7449, 0]]]) {
    const opt = { z: 0.3, half: 2, size: SIZE, maxK: 16 }, a = v.slice(kind, c, opt);
    let d = 0;
    for (let row = 0; row < SIZE; row++) for (let col = 0; col < SIZE; col++) { const p = v.slicePoint(row, col, opt); if (T3.out(p, kind, c, 16) !== a[row * SIZE + col]) d++; }
    cells.push(d); total += d; pts += SIZE * SIZE;
  }
  rows.push(id + ': ' + cells.join(', '));
}
await approach('mercator');
window.__v.dispose();
if (total > 60) fail('slice and out differ at ' + total + ' of ' + pts + ' points: ' + rows.join(' | '));
return { 'slice at z = 0.3 against learnShape3d.out: points that differ, of 16,641 (Mandelbrot shape, Julia c = -1, Julia rabbit)': rows, total: total + ' of ' + pts };
