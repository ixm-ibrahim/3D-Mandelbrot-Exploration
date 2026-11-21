// Round 14, rules: a second pass of numbers, for sentences the first pass left open. Runs inside the page.
const L = window.squaringLab, M = L.MATH, S = L.S, $ = id => document.getElementById(id);
const out = {};
const PI = Math.PI, rad = d => d * PI / 180, deg = r => r * 180 / PI;
const len = a => Math.hypot(a[0], a[1], a[2]), dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
let seed = 99;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const rdir = () => { const z = rnd() * 2 - 1, a = (rnd() * 2 - 1) * PI, h = Math.sqrt(1 - z * z); return [h * Math.cos(a), h * Math.sin(a), z]; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const flatM = (x, y) => { let a = 0, b = 0; for (let k = 0; k < 200; k++) { [a, b] = [a * a - b * b + x, 2 * a * b + y]; if (a * a + b * b > 4096) return false; } return true; };
const flatJ = (x, y, cx, cy) => { let a = x, b = y; for (let k = 0; k < 200; k++) { [a, b] = [a * a - b * b + cx, 2 * a * b + cy]; if (a * a + b * b > 4096) return false; } return true; };
const qmul = (p, q) => [p[0] * q[0] - p[1] * q[1] - p[2] * q[2] - p[3] * q[3], p[0] * q[1] + p[1] * q[0] + p[2] * q[3] - p[3] * q[2],
  p[0] * q[2] - p[1] * q[3] + p[2] * q[0] + p[3] * q[1], p[0] * q[3] + p[1] * q[2] - p[2] * q[1] + p[3] * q[0]];
const stay4 = (z, c, its) => { for (let k = 0; k < its; k++) { const w = qmul(z, z); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2], w[3] + c[3]]; if (Math.hypot(...z) > 64) return false; } return true; };

// 1. rotor square with a frame: is there a jump across the half-plane y = 0, x < 0 at whole powers? Points up to
// 60 degrees of latitude, a step e to each side: the gap must shrink with e if the rule is continuous there.
{
  const F = (v, n) => M.rotorframe(v, n, {}), R = {};
  for (const n of [2, 3, 4, 2.5]) {
    R['n' + n] = {};
    for (const e of [1e-4, 1e-6, 1e-8]) {
      let m = 0;
      for (let i = 0; i < 4000; i++) { const b = (rnd() - 0.5) * PI * 2 / 3, r = 0.3 + rnd(), x = -r * Math.cos(b), z = r * Math.sin(b); m = Math.max(m, dist(F([x, e, z], n), F([x, -e, z], n)) / Math.pow(r, n)); }
      R['n' + n]['step' + e] = m;
    }
  }
  out.rotorframe_gapAcrossHalfPlane = R;
  // where the directions that come out turned over lie (n = 2): share by longitude band
  const bands = [0, 0, 0, 0, 0, 0], tot = [0, 0, 0, 0, 0, 0]; let latSum = 0, cnt = 0;
  for (let i = 0; i < 60000; i++) {
    const d = rdir(), w = F(d, 2);
    const t = Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0], c = [d[1] * t[2] - d[2] * t[1], d[2] * t[0] - d[0] * t[2], d[0] * t[1] - d[1] * t[0]], lc = len(c), u = [c[0] / lc, c[1] / lc, c[2] / lc];
    const v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]], h = 1e-5, nrm = p => { const l = len(p); return [p[0] / l, p[1] / l, p[2] / l]; };
    const wu = F(nrm([d[0] + h * u[0], d[1] + h * u[1], d[2] + h * u[2]]), 2), wv = F(nrm([d[0] + h * v[0], d[1] + h * v[1], d[2] + h * v[2]]), 2);
    const A = [wu[0] - w[0], wu[1] - w[1], wu[2] - w[2]], B = [wv[0] - w[0], wv[1] - w[1], wv[2] - w[2]];
    const det = w[0] * (A[1] * B[2] - A[2] * B[1]) - w[1] * (A[0] * B[2] - A[2] * B[0]) + w[2] * (A[0] * B[1] - A[1] * B[0]);
    const k = Math.min(5, Math.floor(Math.abs(deg(Math.atan2(d[1], d[0]))) / 30)); tot[k]++;
    if (det < 0) { bands[k]++; latSum += Math.abs(deg(Math.asin(d[2]))); cnt++; }
  }
  out.rotorframe_turnedOver = { shareByLongitudeBandOf30Deg_fromXAxis: bands.map((b, i) => +(b / tot[i]).toFixed(3)), share: cnt / 60000, meanAbsLatitudeDeg: latSum / cnt };
  // the slice at z = 0 of the Mandelbrot solid against the flat set, and the plane y = 0 against it
  let d0 = 0, dy = 0, n = 0, inY = 0, inF = 0;
  for (let i = 0; i < 6000; i++) {
    const x = rnd() * 3.2 - 2.2, y = rnd() * 2.8 - 1.4, f = flatM(x, y); let z = [0, 0, 0], a = true, zz = [0, 0, 0], b = true;
    for (let k = 0; k < 200; k++) { if (a) { z = add(F(z, 2), [x, y, 0]); if (len(z) > 64) a = false; } if (b) { zz = add(F(zz, 2), [x, 0, y]); if (len(zz) > 64) b = false; } }
    if (a !== f) d0++; if (b !== f) dy++; inY += b; inF += f; n++;
  }
  out.rotorframe_slices = { points: n, sliceZ0DiffersFromFlat: d0, planeY0DiffersFromFlat: dy, planeY0Inside: inY, flatInside: inF };
}
// 2. Kleinian squaring: keeping of shapes, read robustly (the 99.9th percentile and the count of directions off by more than 1%)
{
  const R = {};
  for (const n of [2, 3, 4]) {
    const offs = [];
    for (let i = 0; i < 40000; i++) {
      const d = rdir(), w = M.kleinsq(d, n, {});
      const t = Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0], c = [d[1] * t[2] - d[2] * t[1], d[2] * t[0] - d[0] * t[2], d[0] * t[1] - d[1] * t[0]], lc = len(c), u = [c[0] / lc, c[1] / lc, c[2] / lc];
      const v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]], h = 1e-6, nrm = p => { const l = len(p); return [p[0] / l, p[1] / l, p[2] / l]; };
      const wu = M.kleinsq(nrm([d[0] + h * u[0], d[1] + h * u[1], d[2] + h * u[2]]), n, {}), wv = M.kleinsq(nrm([d[0] + h * v[0], d[1] + h * v[1], d[2] + h * v[2]]), n, {});
      const A = [wu[0] - w[0], wu[1] - w[1], wu[2] - w[2]], B = [wv[0] - w[0], wv[1] - w[1], wv[2] - w[2]], la = len(A), lb = len(B);
      offs.push(Math.max(Math.abs(la / lb - 1), Math.abs((A[0] * B[0] + A[1] * B[1] + A[2] * B[2]) / (la * lb))));
    }
    offs.sort((a, b) => a - b);
    R['n' + n] = { directions: offs.length, median: offs[offs.length >> 1], p999: offs[Math.floor(offs.length * 0.999)], offByMoreThan1Percent: offs.filter(x => x > 0.01).length };
  }
  out.kleinsq_shape = R;
  // the Julia set for c = -1 in the plane z = 0 against the flat one
  let both = 0, inS = 0, inF = 0, n = 0;
  for (let i = 0; i < 30000; i++) {
    const x = rnd() * 3.6 - 1.8, y = rnd() * 2.4 - 1.2, f = flatJ(x, y, -1, 0); let z = [x, y, 0], a = true;
    for (let k = 0; k < 200 && a; k++) { z = add(M.kleinsq(z, 2, {}), [-1, 0, 0]); if (len(z) > 64) a = false; }
    inS += a; inF += f; both += a && f; n++;
  }
  out.kleinsq_juliaBasilicaSlice = { points: n, inSlice: inS, inFlat: inF, inBoth: both };
}
// 3. Quaternions, 4D: how far the slice can move before the Mandelbrot solid is gone (plain 4D arithmetic), and a Julia slice
{
  out.quat4_emptyBeyond = [0.9, 1.0, 1.1, 1.12, 1.13, 1.2].map(w => { let n = 0; for (let i = 0; i < 200000; i++) { const x = rnd() * 2.6 - 2.1, r = rnd() * 0.6; if (stay4([0, 0, 0, 0], [x, r, 0, w], 300)) n++; } return { w, insideOf200000: n }; });
  let d = 0, inS = 0, inF = 0;
  for (let i = 0; i < 20000; i++) { const x = rnd() * 3.2 - 1.6, y = rnd() * 3.2 - 1.6, a = stay4([x, y, 0, 0], [-0.1226, 0.7449, 0, 0.3], 200), f = flatJ(x, y, -0.1226, 0.7449); inS += a; inF += f; if (a !== f) d++; }
  out.quat4_juliaRabbit_cw03_sliceZ0 = { points: 20000, inSlice: inS, inFlat: inF, differ: d };
}
// 4. the page itself: the picture's own test against plain 4D arithmetic, through sampleSlice (64 x 64 points of three level slices)
{
  const res = [];
  const pickAp = async id => { $('ap-' + id).click(); await sleep(200); };
  const cases = [
    { mode: 'm', q: { w: 0.3, tilt: 25, cw: 0 }, c: null }, { mode: 'j', q: { w: 0.1, tilt: 30, cw: 0.4 }, c: [-1, 0.15, 0.1] }, { mode: 'j', q: { w: 0, tilt: 0, cw: 0.3 }, c: [-0.1226, 0.7449, 0] },
  ];
  for (const cs of cases) {
    await pickAp('quat4'); $('mode-' + cs.mode).click(); await sleep(150);
    Object.assign(S.param.quat4, cs.q); if (cs.c) S.c = cs.c.slice();
    S.flat = false; S.cutOn = false; L.syncControls(); L.refresh(false); L.touch();
    const t0 = performance.now(); while (!L.idle() && performance.now() - t0 < 240000) await sleep(200);
    const snap = L.takeSnapshot(), N = 64, side = 3.2, its = S.iter, t = rad(cs.q.tilt), ct = Math.cos(t), st = Math.sin(t);
    let diff = 0, near = 0, tot = 0, ins = 0;
    for (const z of [0, 0.25, -0.4]) {
      const a = await L.sampleSlice(snap, 0, 0, side, z, N);
      if (!a) { res.push({ error: 'no sample' }); continue; }
      for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
        const x = (i + 0.5) / N * side - side / 2, y = (j + 0.5) / N * side - side / 2, dd = a[4 * (j * N + i) + 3];
        const E = [x * ct - cs.q.w * st, y, z, x * st + cs.q.w * ct];
        const inside = cs.mode === 'm' ? stay4([0, 0, 0, 0], E, its) : stay4(E, [cs.c[0], cs.c[1], cs.c[2], cs.q.cw], its);
        tot++; ins += inside;
        if ((dd < 0) !== inside) { diff++; if (Math.abs(dd) < 0.01) near++; }
      }
    }
    L.releaseSnapshot(snap);
    res.push({ mode: cs.mode, q: JSON.stringify(cs.q), c: cs.c ? cs.c.join(',') : '', steps: its, points: tot, inside4D: ins, pageDisagrees: diff, ofThoseWithin0p01OfTheSurface: near });
  }
  Object.assign(S.param.quat4, { w: 0, tilt: 0, cw: 0 });
  out.quat4_pageAgainst4D = res;
}
return JSON.stringify(out, null, 1);
