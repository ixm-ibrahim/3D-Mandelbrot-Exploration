// The final look, spot checks of the arithmetic on dist/r26-final.html.
//@
// (1) mask2 (the numbers the 2D picture is drawn from) against out2 (the plain way), point for point, 257 x 257
// points of the square |x|, |y| <= 2, 16 steps. At the power 2: Mandelbrot shape, Julia shape of the rabbit and of
// c = -1. Then with other rules: power 3, power 2.5 (the polar form), power 2 with |x|, power -2.
await openShape();
const SIZE = 257, N = 16, rows = [];
const cmp = (label, kind, c) => {
  if (c) L.shape.set({ kind, c, space: 2 }); else L.shape.set({ kind, space: 2 });
  const m = L.shape.mask2(kind, SIZE, 2, N);
  let differ = 0, in5m = 0, in5o = 0, firstBad = null;
  for (let r = 0; r < SIZE; r++) for (let q = 0; q < SIZE; q++) {
    const p = [-2 + q * 4 / (SIZE - 1), 2 - r * 4 / (SIZE - 1)], o = L.shape.out2(p, kind, c || null, N), v = m[r * SIZE + q];
    if (o !== v) { differ++; if (!firstBad) firstBad = { p, out2: o, mask2: v }; }
    if (v > 5) in5m++; if (o > 5) in5o++;
  }
  rows.push({ rule: label, kind, c: c || null, points: SIZE * SIZE, differ, shape5ByMask2: in5m, shape5ByOut2: in5o, firstBad });
};
const rule = async (n, absx) => { S.n = n; S.abs[0] = !!absx; refresh(); await sleep(120); };
await rule(2, false);
cmp('power 2', 'm'); cmp('power 2', 'j', [-0.1226, 0.7449, 0]); cmp('power 2', 'j', [-1, 0, 0]);
await rule(3, false); cmp('power 3', 'm'); cmp('power 3', 'j', [-0.1226, 0.7449, 0]);
await rule(2.5, false); cmp('power 2.5', 'm'); cmp('power 2.5', 'j', [-0.1226, 0.7449, 0]);
await rule(2, true); cmp('power 2 with |x|', 'm'); cmp('power 2 with |x|', 'j', [-0.1226, 0.7449, 0]);
await rule(-2, false); cmp('power -2', 'm'); cmp('power -2', 'j', [-0.1226, 0.7449, 0]);
await rule(2, false);
return { tipOfTheMandelbrotShape: { out2: L.shape.out2([-2, 0], 'm', null, 16), mask2: L.shape.mask2('m', 129, 2, 16)[64 * 129] }, rows };
//@
// (2) slice (worked out on the graphics card by the program the 3D picture is drawn with) against out (JavaScript,
// from MATH / CARRY), point for point, 129 x 129 points at the heights z = 0.3 and z = -0.7, 16 steps, for four
// approaches, the Mandelbrot shape and the Julia shape of a c off the flat plane. A point that differs is then
// asked again a hair to each side (1e-4): if out changes there, the point lies on a skin.
const T3 = LAB.learnShape3d, v = T3.make();
if (!v) fail('no 3D view');
const SIZE = 129, N = 16, rows = [];
let total = 0, pts = 0, off = 0;
for (const id of ['mercator', 'turnalong', 'pulledplane', 'bulb']) {
  const name = await approach(id); S.n = 2; refresh(); await sleep(80);
  for (const [kind, c] of [['m', [0, 0, 0]], ['j', [-0.1226, 0.7449, 0.2]]]) for (const z of [0.3, -0.7]) {
    const g = v.slice(kind, c, { z, half: 2, size: SIZE, maxK: N });
    if (!g) fail('no slice for ' + id);
    let differ = 0, notOnSkin = 0, inside = 0;
    for (let r = 0; r < SIZE; r++) for (let q = 0; q < SIZE; q++) {
      const p = [-2 + q * 4 / (SIZE - 1), 2 - r * 4 / (SIZE - 1), z], o = Math.min(255, T3.out(p, kind, kind === 'm' ? p : c, N)), gv = g[r * SIZE + q];
      if (gv > N) inside++;
      if (o === gv) continue;
      differ++;
      let skin = false;
      for (const d of [[1e-4, 0, 0], [-1e-4, 0, 0], [0, 1e-4, 0], [0, -1e-4, 0], [0, 0, 1e-4], [0, 0, -1e-4]]) { const p2 = [p[0] + d[0], p[1] + d[1], p[2] + d[2]]; if (T3.out(p2, kind, kind === 'm' ? p2 : c, N) !== o) { skin = true; break; } }
      if (!skin) notOnSkin++;
    }
    rows.push(`${id} (${name}), ${kind}, z = ${z}: ${differ} of ${SIZE * SIZE} differ, ${notOnSkin} of them not on a skin; ${inside} points still in after 16 steps`);
    total += differ; pts += SIZE * SIZE; off += notOnSkin;
  }
}
window.__v = v;
return { rows, total: total + ' of ' + pts, notOnASkin: off };
//@
// (3) the cut at z = 0 of the 3D shape against the flat picture's numbers (mask2), for the approach the page opens
// with and for two others; and whether the page shows its sentence about the cut for them.
const v = window.__v, SIZE = 257, N = 16, rows = [];
for (const id of ['mercator', 'turnalong', 'bulb']) {
  await approach(id); S.n = 2; refresh(); await sleep(80);
  for (const [kind, c] of [['m', [0, 0, 0]], ['j', [-1, 0, 0]]]) {
    L.shape.set({ kind, c, space: 3 }); await sleep(200);
    const says = $('learnShapeNotice').textContent.includes('the cut is exactly the 2D picture');
    const g = v.slice(kind, c, { z: 0, half: 2, size: SIZE, maxK: N }), f = L.shape.mask2(kind, SIZE, 2, N);
    let d = 0; for (let i = 0; i < SIZE * SIZE; i++) if (g[i] !== f[i]) d++;
    rows.push(`${id}, ${kind}: ${d} of ${SIZE * SIZE} differ; the page ${says ? 'shows' : 'does not show'} the sentence about the cut`);
  }
}
await approach('mercator'); L.shape.set({ kind: 'm', space: 2, c: [-0.4, 0.3, 0], pos: 0 });
v.dispose();
return rows;
