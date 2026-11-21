// Numeric checks for the pillow rule. api = { F(v, n), phi(ux, uy), phiInv(dx, dy, dz) }.
// Every function returns lines of text; nothing here knows which lift or layout is being checked.
function chkRng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const chkDeg = 180 / Math.PI;
function chkDir(rnd) {
  const z = 2 * rnd() - 1, p = 2 * Math.PI * rnd(), s = Math.sqrt(1 - z * z);
  return [s * Math.cos(p), s * Math.sin(p), z];
}
const chkNorm = v => { const r = Math.hypot(v[0], v[1], v[2]); return [v[0] / r, v[1] / r, v[2] / r]; };
const chkDist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const chkPct = (sorted, p) => sorted[Math.min(sorted.length - 1, Math.floor(p * sorted.length))];
const chkWhere = d => `lon ${(Math.atan2(d[1], d[0]) * chkDeg).toFixed(2)} lat ${(Math.asin(Math.max(-1, Math.min(1, d[2]))) * chkDeg).toFixed(3)}`;

// 1. the plane z = 0 against the complex power
function chkPlane(api, raw) {
  const out = [], rnd = chkRng(11);
  for (const n of [2, 3, 4, 5, 8, -1, -2, -3]) {
    let worst = 0, at = '', worstZ = 0;
    for (let i = 0; i < 500; i++) {
      let r, t;
      if (i < 300) { r = 0.05 + 1.95 * rnd(); t = 2 * Math.PI * rnd(); }
      else if (i < 460) { const base = [0, 120, 180, 240][(i - 300) % 4] / chkDeg, k = Math.floor((i - 300) / 4); r = 0.2 + 1.5 * rnd(); t = base + (k === 0 ? 0 : (k % 2 ? 1 : -1) * Math.pow(10, -1 - 8 * rnd())); }
      else { r = Math.pow(10, -6 + 5 * rnd()); t = 2 * Math.PI * rnd(); }
      const v = [r * Math.cos(t), r * Math.sin(t), 0], R = Math.pow(r, n), e = [R * Math.cos(n * t), R * Math.sin(n * t), 0];
      const f = api.F(v, n), err = chkDist(f, e) / R;
      if (err > worst) { worst = err; at = `r ${r.toExponential(2)} angle ${(t * chkDeg).toFixed(6)}`; }
      if (raw) worstZ = Math.max(worstZ, Math.abs(raw(v, n)[2]) / R);
    }
    out.push(`n = ${n}: worst relative error ${worst.toExponential(2)} (${at})` + (raw ? `; largest |z| before the snap, relative: ${worstZ.toExponential(2)}` : ''));
  }
  return out;
}

// 2. continuity: pairs of unit directions eps apart
function chkPairs(api, n, eps = 1e-5, count = 200000) {
  const rnd = chkRng(23 + n), ratios = [];
  let max = 0, at = null;
  const test = (d1, d2) => {
    const sep = chkDist(d1, d2);
    if (!(sep > 0)) return;
    const q = chkDist(api.F(d1, n), api.F(d2, n)) / sep;
    ratios.push(q);
    if (q > max) { max = q; at = d1; }
  };
  const pair = d => {
    const t = chkDir(rnd), dt = t[0] * d[0] + t[1] * d[1] + t[2] * d[2];
    const e = chkNorm([t[0] - dt * d[0], t[1] - dt * d[1], t[2] - dt * d[2]]);
    test(chkNorm([d[0] - 0.5 * eps * e[0], d[1] - 0.5 * eps * e[1], d[2] - 0.5 * eps * e[2]]), chkNorm([d[0] + 0.5 * eps * e[0], d[1] + 0.5 * eps * e[1], d[2] + 0.5 * eps * e[2]]));
  };
  for (let i = 0; i < count; i++) pair(chkDir(rnd));
  const general = ratios.length;
  for (let i = 0; i < 20000; i++) {                       // straddling the equator
    const p = 2 * Math.PI * rnd(), dp = eps * (rnd() - 0.5);
    test(chkNorm([Math.cos(p), Math.sin(p), 0.5 * eps]), chkNorm([Math.cos(p + dp), Math.sin(p + dp), -0.5 * eps]));
  }
  for (let i = 0; i < 30000; i++) {                       // straddling the meridians through the corners and through the mid-edges
    const p0 = (i % 6) * Math.PI / 3, la = Math.PI * (rnd() - 0.5), c = Math.cos(la), s = Math.sin(la), dl = eps * (rnd() - 0.5);
    test([c * Math.cos(p0 - 0.5 * eps), c * Math.sin(p0 - 0.5 * eps), s], chkNorm([Math.cos(la + dl) * Math.cos(p0 + 0.5 * eps), Math.cos(la + dl) * Math.sin(p0 + 0.5 * eps), Math.sin(la + dl)]));
  }
  const spots = [[0, 0, 1], [0, 0, -1]];
  for (let k = 0; k < 6; k++) spots.push([Math.cos(k * Math.PI / 3), Math.sin(k * Math.PI / 3), 0]);
  for (const s of spots) for (let i = 0; i < 3000; i++) {  // pairs across and beside the poles, the corners and the mid-edges
    const j = () => (rnd() - 0.5) * 2 * eps * Math.pow(10, -2 * rnd());
    test(chkNorm([s[0] + j(), s[1] + j(), s[2] + j()]), chkNorm([s[0] + j(), s[1] + j(), s[2] + j()]));
  }
  ratios.sort((a, b) => a - b);
  return [`n = ${n}: ${general} random pairs + ${ratios.length - general} special pairs, ${eps} apart: largest ratio ${max.toFixed(3)} at ${chkWhere(at)}; 99.9th percentile ${chkPct(ratios, 0.999).toFixed(3)}; median ${chkPct(ratios, 0.5).toFixed(3)}`];
}

// the small triangle of a flat point: [points up?, lA, lB, lC]
function chkTri(ux, uy) {
  const b = uy * 2 / Math.sqrt(3), a = ux + b / 2, i = Math.floor(a), j = Math.floor(b), fa = a - i, fb = b - j, up = fa >= fb;
  const k = (((i + j) % 3) + 3) % 3, w = up ? [1 - fa, fa - fb, fb] : [1 - fb, fb - fa, fa], l = [0, 0, 0];
  for (let m = 0; m < 3; m++) l[(k + m) % 3] = w[m];
  return [up, l[0], l[1], l[2]];
}
// 3. round trips
function chkRound(api) {
  const rnd = chkRng(37), out = [];
  let worst = 0, at = null, count = 0;
  const one = d => { const u = api.phiInv(d[0], d[1], d[2]), e = chkDist(api.phi(u[0], u[1]), d); count++; if (e > worst) { worst = e; at = d; } };
  for (let i = 0; i < 200000; i++) one(chkDir(rnd));
  for (let i = 0; i < 60000; i++) {                       // next to the equator, the corners, the mid-edges, the poles, the six meridians
    const t = Math.pow(10, -1 - 14 * rnd()) * (rnd() < 0.5 ? -1 : 1), s = Math.pow(10, -1 - 14 * rnd()) * (rnd() < 0.5 ? -1 : 1), k = i % 6, p0 = k * Math.PI / 3;
    const kind = Math.floor(i / 6) % 5;
    if (kind === 0) { const p = 2 * Math.PI * rnd(); one(chkNorm([Math.cos(p), Math.sin(p), t])); }
    else if (kind === 1) one(chkNorm([Math.cos(p0 + s), Math.sin(p0 + s), t]));
    else if (kind === 2) one(chkNorm([t, s, i % 2 ? 1 : -1]));
    else if (kind === 3) { const la = Math.PI * (rnd() - 0.5); one([Math.cos(la) * Math.cos(p0 + s), Math.cos(la) * Math.sin(p0 + s), Math.sin(la)]); }
    else one(chkNorm([Math.cos(p0), Math.sin(p0), i % 12 < 6 ? 0 : t]));
  }
  out.push(`Phi(PhiInv(d)) = d over ${count} directions (random, and next to the equator, corners, mid-edges, poles, meridians): worst |difference| ${worst.toExponential(2)} at ${chkWhere(at)}`);
  let wW = 0, wAt = '', flips = 0, n2 = 0;
  for (let i = 0; i < 200000; i++) {
    let ux = 16 * (rnd() - 0.5), uy = 16 * (rnd() - 0.5);
    if (i % 4 === 0) { ux = Math.round(ux) + (Math.round(uy) % 2 ? 0.5 : 0) + 1e-3 * Math.pow(10, -9 * rnd()) * (rnd() - 0.5); uy = Math.round(uy) * Math.sqrt(3) / 2 + 1e-3 * Math.pow(10, -9 * rnd()) * (rnd() - 0.5); }
    const a = chkTri(ux, uy), d = api.phi(ux, uy), u = api.phiInv(d[0], d[1], d[2]), b = chkTri(u[0], u[1]);
    const e = Math.max(Math.abs(a[1] - b[1]), Math.abs(a[2] - b[2]), Math.abs(a[3] - b[3]));
    n2++;
    if (e > wW) { wW = e; wAt = `u = (${ux.toFixed(6)}, ${uy.toFixed(6)}), weights ${a.slice(1).map(x => x.toExponential(2)).join(' ')}`; }
    if (a[0] !== b[0] && Math.min(a[1], a[2], a[3]) > 1e-7) flips++;
  }
  out.push(`PhiInv(Phi(u)) against u over ${n2} flat points (a quarter of them within 1e-3 of a lattice point): worst weight difference ${wW.toExponential(2)} (${wAt}); wrong triangle type away from an edge: ${flips}`);
  return out;
}

// 5. distortion of D = Phi o (times n) o PhiInv
function chkDistort(api, n = 2, count = 20000, h = 1e-5) {
  const rnd = chkRng(53), rows = [];
  const frame = d => {
    const a = Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0], dt = a[0] * d[0] + a[1] * d[1] + a[2] * d[2];
    const e1 = chkNorm([a[0] - dt * d[0], a[1] - dt * d[1], a[2] - dt * d[2]]);
    return [e1, [d[1] * e1[2] - d[2] * e1[1], d[2] * e1[0] - d[0] * e1[2], d[0] * e1[1] - d[1] * e1[0]]];
  };
  const D = d => api.F(d, n);
  for (let i = 0; i < count; i++) {
    const d = chkDir(rnd), [e1, e2] = frame(d), c = chkNorm(D(d)), [f1, f2] = frame(c);
    const col = e => {
      const p = chkNorm(D(chkNorm([d[0] + h * e[0], d[1] + h * e[1], d[2] + h * e[2]]))), m = chkNorm(D(chkNorm([d[0] - h * e[0], d[1] - h * e[1], d[2] - h * e[2]])));
      const g = [(p[0] - m[0]) / (2 * h), (p[1] - m[1]) / (2 * h), (p[2] - m[2]) / (2 * h)];
      return [g[0] * f1[0] + g[1] * f1[1] + g[2] * f1[2], g[0] * f2[0] + g[1] * f2[1] + g[2] * f2[2]];
    };
    const [a, b2] = col(e1), [c2, d2] = col(e2);              // J = [[a, c2], [b2, d2]]
    const fro = a * a + b2 * b2 + c2 * c2 + d2 * d2, det = Math.abs(a * d2 - b2 * c2), disc = Math.sqrt(Math.max(fro * fro / 4 - det * det, 0));
    const s1 = Math.sqrt(fro / 2 + disc) / Math.abs(n), s2 = Math.sqrt(Math.max(fro / 2 - disc, 0)) / Math.abs(n);
    rows.push({ d, ratio: s1 / Math.max(s2, 1e-12), area: s1 * s2, s1, s2 });
  }
  const by = key => rows.map(r => r[key]).sort((x, y) => x - y);
  const ra = by('ratio'), ar = by('area'), s1 = by('s1'), s2 = by('s2');
  const f = x => x.toFixed(3);
  const out = [`s1/s2: median ${f(chkPct(ra, 0.5))}, 95th ${f(chkPct(ra, 0.95))}, 99.9th ${f(chkPct(ra, 0.999))}, largest ${ra[ra.length - 1].toExponential(2)}`,
    `s1*s2: 0.1th ${f(chkPct(ar, 0.001))}, 5th ${f(chkPct(ar, 0.05))}, median ${f(chkPct(ar, 0.5))}, 95th ${f(chkPct(ar, 0.95))}, 99.9th ${f(chkPct(ar, 0.999))}, mean ${f(ar.reduce((x, y) => x + y, 0) / ar.length)}`,
    `s1: median ${f(chkPct(s1, 0.5))}, 95th ${f(chkPct(s1, 0.95))}, 99.9th ${f(chkPct(s1, 0.999))}, largest ${f(s1[s1.length - 1])};  s2: smallest ${s2[0].toExponential(2)}, 0.1th ${f(chkPct(s2, 0.001))}, 5th ${f(chkPct(s2, 0.05))}, median ${f(chkPct(s2, 0.5))}`];
  // where the worst values sit: fold the longitude into 0..60 degrees from the nearest corner, take |latitude|
  const fold = d => { let lo = ((Math.atan2(d[1], d[0]) * chkDeg) % 120 + 120) % 120; if (lo > 60) lo = 120 - lo; return [lo, Math.abs(Math.asin(d[2]) * chkDeg)]; };
  const top = (key, dir, m = 8) => rows.slice().sort((x, y) => dir * (y[key] - x[key])).slice(0, m).map(r => { const [lo, la] = fold(r.d); return `(${lo.toFixed(1)}, ${la.toFixed(1)}: ${r[key].toFixed(2)})`; }).join(' ');
  out.push('worst s1/s2 at (degrees from the nearest corner direction, |latitude|: value): ' + top('ratio', 1));
  out.push('largest s1*s2 at: ' + top('area', 1));
  out.push('smallest s1*s2 at: ' + top('area', -1));
  // a coarse map: mean s1/s2 and mean s1*s2 on a grid of folded longitude (rows of 10 degrees) and |latitude| (columns of 15 degrees)
  const grid = [...Array(6)].map(() => [...Array(6)].map(() => [0, 0, 0]));
  for (const r of rows) { const [lo, la] = fold(r.d), g = grid[Math.min(5, Math.floor(lo / 10))][Math.min(5, Math.floor(la / 15))]; g[0]++; g[1] += Math.min(r.ratio, 50); g[2] += r.area; }
  out.push('mean s1/s2 (capped at 50) by longitude from the corner (rows 0-10 ... 50-60) and |latitude| (columns 0-15 ... 75-90):');
  for (const row of grid) out.push('  ' + row.map(g => (g[0] ? (g[1] / g[0]).toFixed(2) : '  - ').padStart(6)).join(' '));
  out.push('mean s1*s2 on the same grid:');
  for (const row of grid) out.push('  ' + row.map(g => (g[0] ? (g[2] / g[0]).toFixed(2) : '  - ').padStart(6)).join(' '));
  return out;
}
