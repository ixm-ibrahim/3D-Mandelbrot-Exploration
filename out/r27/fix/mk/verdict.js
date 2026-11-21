// Step 2 checks. (A) The shader's verdict against the twin at 142 x 142 = 20164 points of the square -1.8..1.8 (moved by
// a random offset), for nine settings, once in the flat cut and once at a random height. The shader is read through
// sampleSlice (colour and signed distance of one level slice, from the program the picture is drawn with).
// (B) The shader's distance against the twin's (ballsEstimate). (C) The twin's distance is never longer than the true
// distance: no point of the sphere of radius 0.999 d round a point with estimate d is inside a ball; and how tight
// it is: the smallest of the radii 1.5 d, 2 d, 3 d, 5 d, 10 d at which a sample is inside.
if (typeof L.sampleSlice !== 'function') fail('no sampleSlice');
let seed = 2027;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
S.mode = 'k'; S.k.group = 1; S.flat = false; S.cutOn = false; S.colour.solid = 0; go(); await settle();
const N = 142, side = 3.6, out = { A: [], C: [] };
for (const grid of [0, 1, 2]) for (const t of [1, 1.4, 2.5]) for (const flat of [true, false]) {
  S.k.bgrid = grid; S.k.bt = t; S.k.bit = 40; go(); await sleep(30);
  const cx = 0.02 * (rnd() - 0.5), cy = 0.02 * (rnd() - 0.5), z = flat ? 0 : 1.3 * (2 * rnd() - 1) * 0.6;
  const snap = L.takeSnapshot(), a = await L.sampleSlice(snap, cx, cy, side, z, N);
  L.releaseSnapshot(snap);
  if (!a) fail('sampleSlice gave nothing for grid ' + grid + ', t ' + t);
  let diff = 0, inside = 0, worst = 0, relMax = 0, relN = 0, relSum = 0, longer = 0;
  const opts = { t, grid, rounds: 40 };
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const x = cx + side * ((i + 0.5) / N - 0.5), y = cy + side * ((j + 0.5) / N - 0.5), d = a[4 * (j * N + i) + 3];
    const vs = !(d > 0), vt = L.ballsInside(x, y, z, opts), e = L.ballsEstimate(x, y, z, opts);
    if (vt) inside++;
    if (vs !== vt) { diff++; worst = Math.max(worst, Math.abs(e)); }
    else if (e > 1e-4) { const r = Math.abs(d - e) / e; relSum += r; relN++; if (r > relMax) relMax = r; if (d > e * 1.001 + 1e-6) longer++; }
  }
  out.A.push({ grid, t, flat, z: +z.toFixed(4), points: N * N, inside, differ: diff, worstEstimateAtADifference: worst, shaderVsTwinMeanRel: relSum / Math.max(1, relN), shaderVsTwinMaxRel: relMax, shaderLongerThanTwin: longer });
  await sleep(10);
}
// (C) in JavaScript, double precision
const dirs = [];
for (let i = 0; i < 240; i++) { const u = 2 * rnd() - 1, a = 2 * Math.PI * rnd(), s = Math.sqrt(1 - u * u); dirs.push([s * Math.cos(a), s * Math.sin(a), u]); }
for (const grid of [0, 1, 2]) for (const t of [1, 1.4, 2.5]) {
  const opts = { t, grid, rounds: 60 }, fs = [1.5, 2, 3, 5, 10], hist = [0, 0, 0, 0, 0, 0];
  let n = 0, breaks = 0, worstBreak = 0, undecidedAt60 = 0;
  for (let k = 0; k < 3000; k++) {
    const p = [-1.9 + 3.8 * rnd(), -1.4 + 2.8 * rnd(), -1.4 + 2.8 * rnd()], d = L.ballsEstimate(p[0], p[1], p[2], opts);
    if (!(d > 0)) continue;
    n++;
    let bad = false;
    // (Fixer: ballsInside calls a point that is still undecided after its rounds inside. With 60 rounds that is not a
    //  ball at t = 1, where the chain is endless: such a probe is asked again with 4000 rounds, and counted apart.)
    for (const v of dirs) { const q = [p[0] + 0.999 * d * v[0], p[1] + 0.999 * d * v[1], p[2] + 0.999 * d * v[2]];
      if (!L.ballsInside(q[0], q[1], q[2], opts)) continue;
      if (L.ballsInside(q[0], q[1], q[2], { t, grid, rounds: 4000 })) { bad = true; break; }
      undecidedAt60++; }
    if (bad) { breaks++; worstBreak = Math.max(worstBreak, d); continue; }
    let at = 5;
    for (let f = 0; f < fs.length && at === 5; f++) for (const v of dirs) if (L.ballsInside(p[0] + fs[f] * d * v[0], p[1] + fs[f] * d * v[1], p[2] + fs[f] * d * v[2], opts)) { at = f; break; }
    hist[at]++;
  }
  out.C.push({ grid, t, outsidePoints: n, estimateLongerThanTrue: breaks, worstBreak, probesOnlyUndecidedAfter60Rounds: undecidedAt60, aBallWithin: { '1.5d': hist[0], '2d': hist[1], '3d': hist[2], '5d': hist[3], '10d': hist[4], 'none within 10d': hist[5] } });
}
S.k.bgrid = 0; S.k.bt = 1.4; S.k.bit = L.BALLS.rounds; go();
return JSON.stringify(out);
