// Check 3: LEARN.shape.mask2 (the arithmetic the picture is drawn from) against LEARN.shape.out2 (the plain way,
// through learnFlatRule), point for point. Both kinds, power 2 and 3, and some more settings for good measure.
//@
await shapeOn({ kind: 'both', space: 2, pos: 0 });
const N = 16, size = 401, half = 2, rows = [];
// the place of a sample, exactly as mask2 lays them out: the outer ones on the edge of the square, row 0 at the top
const at = (i, j, centres) => { const d = centres ? 2 * half / size : 2 * half / (size - 1), h0 = centres ? half - d / 2 : half; return [-h0 + i * d, h0 - j * d]; };
const run = (label, kind, c, centres) => {
  L.shape.set({ c });
  const t0 = performance.now(), m = L.shape.mask2(kind, size, half, N, centres ? { centres: true } : undefined), t1 = performance.now();
  let diff = 0, inBall = 0, left = 0, worst = 0; const hist = new Array(N + 2).fill(0), where = [];
  for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) {
    const p = at(i, j, centres), o = L.shape.out2(p, kind, c, N), v = m[j * size + i];
    hist[v]++; if (v > 0) inBall++; if (v > N) left++;
    if (o !== v) { diff++; worst = Math.max(worst, Math.abs(o - v)); if (where.length < 4) where.push([p[0], p[1], 'mask ' + v, 'out2 ' + o]); }
  }
  const t2 = performance.now();
  rows.push({ what: label, differ: diff + ' of ' + size * size, inTheBigCircle: inBall, leftAfter16: left, worst, where, maskMs: +(t1 - t0).toFixed(1), out2Ms: +(t2 - t1).toFixed(0) });
  return m;
};
const RAB = [-0.1226, 0.7449, 0], BAS = [-1, 0, 0];
const settings = [
  ['power 2', () => { S.n = 2; S.abs = [0, 0, 0]; S.flip = [0, 0]; }],
  ['power 3', () => { S.n = 3; }],
  ['power 2.5 (polar form)', () => { S.n = 2.5; }],
  ['power -2', () => { S.n = -2; }],
  ['power 2, |x| and flip y', () => { S.n = 2; S.abs = [1, 0, 0]; S.flip = [1, 0]; }],
  ['power 2, |y|', () => { S.abs = [0, 1, 0]; S.flip = [0, 0]; }],
];
for (const [name, put] of settings) {
  put(); go(); await sleep(50);
  run(name + ', Mandelbrot shape', 'm', RAB, false);
  run(name + ', Julia shape, c = -1', 'j', BAS, false);
  run(name + ', Julia shape, the rabbit', 'j', RAB, false);
}
S.n = 2; S.abs = [0, 0, 0]; S.flip = [0, 0]; go(); await sleep(50);
run('power 2, Mandelbrot shape, samples at the centres of cells', 'm', RAB, true);
run('power 2, Julia shape (rabbit), samples at the centres of cells', 'j', RAB, true);
// the corners of the contract: 0 outside the big circle, N + 1 when still in, row 0 at the top (y = +half)
const m = L.shape.mask2('m', 5, 2, 16), j0 = L.shape.mask2('j', 5, 2, 16);
const want = { cornerIsOutside: m[0] === 0, centreStaysIn: m[12] === 17, topMiddleIsY2: L.shape.out2([0, 2], 'm', RAB, 16) === m[2], leftMiddle: L.shape.out2([-2, 0], 'm', RAB, 16) === m[10], capped: Math.max(...L.shape.mask2('m', 9, 2, 300)) <= 255 };
// asymmetry check of the rows: the rabbit's c has y > 0, so the Mandelbrot mask is the same top and bottom but the Julia one is not mirrored that way
return { rows, want, mMiddleColumn: [m[2], m[7], m[12], m[17], m[22]], jMiddleColumn: [j0[2], j0[7], j0[12], j0[17], j0[22]], outs: [[0, 1], [0, -1], [0.3, 0.9], [0.3, -0.9]].map(p => L.shape.out2(p, 'j', RAB, 16)) };
//@
// the picture's own numbers at a whole step: what is filled on the canvas is exactly shape k
// (read back from the canvas: a pixel well inside the body is brass, a pixel outside shape k is not)
const s = L.shape.set({ kind: 'm', pos: 5, c: [-0.1226, 0.7449, 0] });
const cv = $('learnShapeCanvas'), g = cv.getContext('2d'), P = s.panes[0], sc = 0.21 * Math.min(P.w, P.h), cx = P.x + P.w / 2, cy = P.y + P.h / 2;
const dpr = cv.width / cv.clientWidth, img = g.getImageData(0, 0, cv.width, cv.height).data;
const pix = (x, y) => { const X = Math.round((cx + x * sc) * dpr), Y = Math.round((cy - y * sc) * dpr), o = 4 * (Y * cv.width + X); return [img[o], img[o + 1], img[o + 2], img[o + 3]]; };
// a grid of points not close to any skin: |out - 5| tells whether it is in shape 5; compare with the colour found
let ok = 0, bad = 0, skipped = 0; const badList = [];
for (let i = 0; i < 60; i++) for (let j = 0; j < 60; j++) {
  const x = -1.95 + 3.9 * i / 59 + 0.013, y = -1.95 + 3.9 * j / 59 + 0.007;
  if (Math.hypot(x, y) > 1.97) continue;
  // skip points within two CSS pixels of a change of the number (an outline, an axis or a figure may lie there)
  const o = L.shape.out2([x, y], 'm', null, 16), near = [[2, 0], [-2, 0], [0, 2], [0, -2], [2, 2], [-2, -2], [2, -2], [-2, 2]].some(d => L.shape.out2([x + d[0] / sc, y + d[1] / sc], 'm', null, 16) !== o);
  if (near) { skipped++; continue; }
  const p = pix(x, y), brass = p[3] > 200 && p[0] > 180 && p[1] > 140 && p[2] < 130, inShape = o > 5;
  // (outside the shape the pixel may hold an axis, a mark or a figure, never the body colour)
  if (brass === inShape) ok++; else { bad++; if (badList.length < 5) badList.push([x.toFixed(3), y.toFixed(3), o, p]); }
}
return { step: 5, pointsChecked: ok + bad, agree: ok, disagree: bad, skippedNearASkin: skipped, badList };
