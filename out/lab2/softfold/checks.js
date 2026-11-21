// Numeric checks of the soft fold, run inside the built page (python out/lab2/softfold/run_checks.py).
// Everything calls the page's own MATH.softfold. A second copy of the rule, written straight from the task text
// (F_k = R_k M R_k^-1 with M = the page's one-plane Sphere inversions rule, textbook slerp), serves as a reference.
const L = window.squaringLab, PI = Math.PI, DEG = PI / 180;
const F = (v, n, q) => L.MATH.softfold(v, n, q);
const out = [], say = s => out.push(s);
let seed = 24680;
const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const gauss = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * PI * rnd());
const len = v => Math.hypot(v[0], v[1], v[2]), unit = v => { const l = len(v); return [v[0] / l, v[1] / l, v[2] / l]; };
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]), dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const rdir = () => unit([gauss(), gauss(), gauss()]);
const pct = (sorted, p) => sorted[Math.min(sorted.length - 1, Math.floor(p / 100 * sorted.length))];
const rotX = (v, a) => { const c = Math.cos(a), s = Math.sin(a); return [v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]]; };
const SETS = [
  { name: 'p=2 a=0.25 smoothstep slerp', q: { planes: 2, blend: 0.25, curve: 0, mix: 0 } },
  { name: 'p=2 a=0    smoothstep slerp', q: { planes: 2, blend: 0, curve: 0, mix: 0 } },
  { name: 'p=2 a=0.45 smoothstep slerp', q: { planes: 2, blend: 0.45, curve: 0, mix: 0 } },
  { name: 'p=2 a=0.25 smootherstep slerp', q: { planes: 2, blend: 0.25, curve: 1, mix: 0 } },
  { name: 'p=2 a=0.25 smoothstep straight', q: { planes: 2, blend: 0.25, curve: 0, mix: 1 } },
  { name: 'p=2 a=0    smoothstep straight', q: { planes: 2, blend: 0, curve: 0, mix: 1 } },
  { name: 'p=3 a=0.25 smoothstep slerp', q: { planes: 3, blend: 0.25, curve: 0, mix: 0 } },
  { name: 'p=3 a=0    smoothstep slerp', q: { planes: 3, blend: 0, curve: 0, mix: 0 } },
  { name: 'p=4 a=0.25 smoothstep slerp', q: { planes: 4, blend: 0.25, curve: 0, mix: 0 } },
  { name: 'p=2 a=0.25 smoothstep PINCH', q: { planes: 2, blend: 0.25, curve: 0, mix: 2 } },
  { name: 'p=2 a=0    smoothstep PINCH', q: { planes: 2, blend: 0, curve: 0, mix: 2 } },
  { name: 'p=2 a=0.4  smoothstep PINCH', q: { planes: 2, blend: 0.4, curve: 0, mix: 2 } },
  { name: 'p=3 a=0.25 smoothstep PINCH', q: { planes: 3, blend: 0.25, curve: 0, mix: 2 } },
];
const ONLY = window.__only; const SETS_USED = ONLY ? SETS.filter((s, i) => ONLY.includes(i)) : SETS;

// ---- the reference, from the task text
const M1 = (v, n) => L.MATH.mercator(v, n, { planes: 1 });
const Fk = (v, n, k, p) => rotX(M1(rotX(v, -k * PI / p), n), k * PI / p);
const Sref = (t, a, curve) => { const x = Math.min(1, Math.max(0, (t - a) / (1 - 2 * a))); return curve ? x * x * x * (x * (6 * x - 15) + 10) : x * x * (3 - 2 * x); };
function parts(v, n, q) {     // the two plane answers (unit), the blend weight and the place between the planes
  const p = q.planes, w = PI / p; let psi = Math.atan2(v[2], v[1]); if (psi < 0) psi += 2 * PI;
  const k = Math.min(Math.floor(psi / w), 2 * p - 1), t = psi / w - k;
  return { A: unit(Fk(v, n, k, p)), B: unit(Fk(v, n, k + 1, p)), s: Sref(t, q.blend, q.curve), t, k };
}
function Fref(v, n, q) {
  const r = len(v);
  if (q.planes < 2 || Math.hypot(v[1], v[2]) < 1e-300) return M1(v, n);
  const R = Math.pow(r, n);
  let { A, B, s } = parts(v, n, q);
  let D;
  if (q.mix === 2) {     // the pinch, from its description: the nearer plane's answer, pulled toward the seam's target
    const p = q.planes, w = PI / p; let psi = Math.atan2(v[2], v[1]); if (psi < 0) psi += 2 * PI;
    const kn = Math.round(psi / w), off = psi / w - kn, tn = Math.abs(off), pz = Sref((tn - q.blend) / (0.5 - q.blend), 0, q.curve);
    const near = unit(Fk(v, n, kn, p)), odd = Math.abs(Math.abs(n) % 2 - 1) < 1e-3, sa = (kn + (off < 0 ? -0.5 : 0.5)) * w, d = unit(v), rho = Math.hypot(d[1], d[2]), g = n < 0 ? -1 : 1;
    A = near; B = odd ? [d[0], g * rho * Math.cos(sa), g * rho * Math.sin(sa)] : [1, 0, 0]; s = pz;
  }
  if (q.mix === 1) D = unit([A[0] + s * (B[0] - A[0]), A[1] + s * (B[1] - A[1]), A[2] + s * (B[2] - A[2])]);
  else {
    const om = Math.acos(Math.max(-1, Math.min(1, dot(A, B))));
    if (om < 1e-7) D = A; else if (PI - om < 1e-3) D = s < 0.5 ? A : B;
    else { const a = Math.sin((1 - s) * om) / Math.sin(om), b = Math.sin(s * om) / Math.sin(om); D = [a * A[0] + b * B[0], a * A[1] + b * B[1], a * A[2] + b * B[2]]; }
  }
  return [R * D[0], R * D[1], R * D[2]];
}

// ---- 1. exactness on every plane
function cpow(x, y, n) {     // complex power by repeated multiplication (no angles involved)
  let a = 1, b = 0;
  for (let k = 0; k < Math.abs(n); k++) [a, b] = [a * x - b * y, a * y + b * x];
  if (n < 0) { const m = a * a + b * b; a = a / m; b = -b / m; }
  return [a, b];
}
const planePts = [];
for (let k = 0; k < 500; k++) {
  let th = 2 * PI * rnd(), r = 0.05 + 2 * rnd();
  if (k < 160) th = [0, 90, 180, 270, 45, 135, 360, -90][k % 8] * DEG + (k < 16 ? 0 : (rnd() - 0.5) * Math.pow(10, -1 - 13 * rnd()));   // on and beside the axes
  if (k >= 160 && k < 220) r = Math.pow(10, -1 - 4 * rnd());     // near the origin (down to 1e-5: closer in, a negative power passes the lab's cap of 1.7e18)
  planePts.push([r * Math.cos(th), r * Math.sin(th)]);
}
say('1. Exactness on every plane P_k (500 points per plane, on and beside the axes and near the origin; worst |F - z^n| / |z^n| over all planes, per power)');
const NS = [2, 3, 4, 5, 8, -1, -2, -3];
for (const set of SETS_USED) {
  const p = set.q.planes, cells = []; let fail = '';
  for (const n of NS) {
    let worst = 0, worst0 = 0;
    for (let k = 0; k < p; k++) for (const [x, y] of planePts) {
      const a = k * PI / p, v = k === 0 ? [x, y, 0] : [x, y * Math.cos(a), y * Math.sin(a)], g = F(v, n, set.q), [X, Y] = cpow(x, y, n), m = Math.hypot(X, Y);
      const e = dist(g, k === 0 ? [X, Y, 0] : [X, Y * Math.cos(a), Y * Math.sin(a)]) / m;
      if (e > worst) worst = e;
      if (k === 0 && e > worst0) worst0 = e;
      if (e >= 1e-6 && !fail) fail = ` FAIL n=${n} plane ${k} at (${x}, ${y})`;
    }
    cells.push(`n=${n}: ${worst.toExponential(1)} (z=0 alone ${worst0.toExponential(1)})`);
  }
  say(`   ${set.name}: ${cells.join(', ')}${fail || '  ok'}`);
}
{
  let w1 = 0;
  for (const n of NS) for (let i = 0; i < 4000; i++) { const v = [3 * rnd() - 1.5, 3 * rnd() - 1.5, 3 * rnd() - 1.5], a = F(v, n, { planes: 1 }), b = M1(v, n); w1 = Math.max(w1, dist(a, b) / (1e-30 + len(b))); }
  say(`   planes = 1 against Sphere inversions with one plane, 32000 random points, 8 powers: worst relative difference ${w1.toExponential(1)}`);
}

// ---- where the two plane answers point opposite ways (a slerp has no answer there)
function opposite(n, q) {
  const N = 500; let rows = [];
  for (let i = 0; i < N; i++) for (let j = 0; j < 2 * N; j++) {
    const th = (i + 0.5) / N * PI, ps = (j + 0.5) / N * PI, v = [Math.cos(th), Math.sin(th) * Math.cos(ps), Math.sin(th) * Math.sin(ps)], P = parts(v, n, q), c = dot(P.A, P.B);
    if (c < -0.9) rows.push({ c, v, t: P.t, s: P.s });
  }
  rows.sort((a, b) => a.c - b.c);
  const picks = [];
  for (const r of rows) { if (picks.length >= 12) break; if (picks.every(o => dist(o.v, r.v) > 0.05)) picks.push(r); }
  for (const o of picks) {     // refine by a shrinking random search
    let h = 0.004;
    for (let it = 0; it < 400; it++) {
      const v = unit([o.v[0] + h * gauss(), o.v[1] + h * gauss(), o.v[2] + h * gauss()]), P = parts(v, n, q), c = dot(P.A, P.B);
      if (c < o.c) { o.c = c; o.v = v; o.t = P.t; o.s = P.s; } else h *= 0.985;
    }
  }
  return picks;
}

// ---- 2. continuity
function pairs(q, spots) {
  const P = [], h = 1e-5, p = q.planes, w = PI / p, count = {};
  const push = (a, b, key) => { P.push([unit(a), unit(b)]); count[key] = (count[key] || 0) + 1; };
  for (let k = 0; k < 200000; k++) { const d = rdir(), e = [gauss(), gauss(), gauss()], l = len(e); push(d, [d[0] + h * e[0] / l, d[1] + h * e[1] / l, d[2] + h * e[2] / l], 'random'); }
  const at = (th, ps) => [Math.cos(th), Math.sin(th) * Math.cos(ps), Math.sin(th) * Math.sin(ps)];
  const lines = [];
  for (let k = 0; k < 2 * p; k++) { lines.push([k * w, 'planes']); lines.push([(k + 0.5) * w, 'half-way seams']); lines.push([(k + q.blend) * w, 'band edges']); lines.push([(k + 1 - q.blend) * w, 'band edges']); }
  for (const [ps, key] of lines) for (let i = 0; i < 2500; i++) {     // straddling each special half-plane, squarely and obliquely
    const th = Math.acos(1 - 2 * rnd()), dp = h * (0.05 + 0.45 * rnd()) / Math.max(Math.sin(th), 1e-3), dt = (rnd() - 0.5) * h;
    push(at(th, ps - dp), at(th + dt, ps + dp * rnd()), key);
  }
  for (let i = 0; i < 20000; i++) {     // near the x-axis, on one side of it and across it
    const sg = i % 2 ? 1 : -1, e1 = h * Math.pow(10, 3 * rnd() - 2), e2 = i % 3 ? e1 * (0.5 + rnd()) : h * rnd(), a1 = 2 * PI * rnd(), a2 = i % 4 < 2 ? a1 + (rnd() - 0.5) : 2 * PI * rnd();
    push([sg, e1 * Math.cos(a1), e1 * Math.sin(a1)], [sg, e2 * Math.cos(a2), e2 * Math.sin(a2)], 'x-axis');
  }
  for (const o of spots) for (let i = 0; i < 1500; i++) {     // around the directions where the two plane answers are most nearly opposite
    const sc = h * Math.pow(10, 5 * rnd() - 2), a = [o.v[0] + sc * gauss(), o.v[1] + sc * gauss(), o.v[2] + sc * gauss()], e = [gauss(), gauss(), gauss()], l = len(e);
    push(a, i % 4 === 0 ? o.v : [a[0] + h * e[0] / l, a[1] + h * e[1] / l, a[2] + h * e[2] / l], 'opposite spots');
  }
  return { P, count };
}
say('2. Continuity: pairs of unit directions about 1e-5 apart; ratio |F(d1) - F(d2)| / |d1 - d2|. A jump shows as a ratio in the tens of thousands.');
const spotNote = {};
for (const set of SETS_USED) {
  for (const n of [2, 3, -2]) {
    const spots = opposite(n, set.q), { P: PAIRS, count } = pairs(set.q, spots);
    const ratios = new Float64Array(PAIRS.length); let max = 0, at = null, maxRef = 0, nRef = 0;
    PAIRS.forEach(([a, b], k) => {
      const dd = dist(a, b); if (!(dd > 1e-13)) { ratios[k] = 0; return; }
      const fa = F(a, n, set.q), r = dist(fa, F(b, n, set.q)) / dd; ratios[k] = r;
      if (r > max) { max = r; at = a; }
      if (k % 10 === 0) { const e = dist(fa, Fref(a, n, set.q)); if (e > maxRef) maxRef = e; if (e > 1e-6) nRef++; }
    });
    const first = Array.from(ratios.subarray(0, 200000)).sort((x, y) => x - y), rest = Array.from(ratios.subarray(200000)).sort((x, y) => x - y);
    const pa = parts(at, n, set.q), big = rest.filter(x => x > 1000).length + first.filter(x => x > 1000).length;
    const sp = spots.slice(0, 4).map(o => `dot ${o.c.toFixed(4)} at t=${o.t.toFixed(3)} (weight ${o.s.toFixed(3)}), ${(Math.acos(o.v[0]) / DEG).toFixed(1)}° from +x`).join('; ');
    say(`   ${set.name}, n = ${n}: ${PAIRS.length} pairs (${Object.entries(count).map(([k, v]) => v + ' ' + k).join(', ')}). random pairs: max ${first[first.length - 1].toFixed(2)}, 99.9th ${pct(first, 99.9).toFixed(2)}, median ${pct(first, 50).toFixed(2)}; special pairs: max ${rest[rest.length - 1].toFixed(2)}, 99.9th ${pct(rest, 99.9).toFixed(2)}; overall max ${max.toFixed(2)} at t=${pa.t.toFixed(4)}, ${(Math.acos(at[0]) / DEG).toFixed(2)}° from +x; pairs over 1000: ${big}  ${max < 1000 ? 'BOUNDED' : 'JUMP'}. Most nearly opposite plane answers: ${sp || 'none below -0.9'}. Rule against the reference from the task text: max difference ${maxRef.toExponential(1)}, ${nRef} over 1e-6`);
  }
}

say('2b. Where the two plane answers point exactly opposite ways (a blend has no answer there; it is harmless when the weight there is 0 or 1). Listed: place t between the planes, angle from +x, for the spots with dot below -0.999; "none" when the smallest dot is above that.');
for (const p of [2, 3, 4]) {
  const cells = [];
  for (const n of [2, 3, 4, 5, 8, -1, -2, -3]) {
    const sp = opposite(n, { planes: p, blend: 0, curve: 0, mix: 0 }), hard = sp.filter(o => o.c < -0.999);
    const ts = [...new Set(hard.map(o => Math.min(o.t, 1 - o.t).toFixed(3)))].sort();
    cells.push(`n=${n}: ${hard.length ? 't = ' + ts.join(', ') + ' (' + [...new Set(hard.map(o => (Math.acos(o.v[0]) / DEG).toFixed(0) + '°'))].slice(0, 4).join(', ') + ')' : 'none (smallest dot ' + (sp.length ? sp[0].c.toFixed(3) : 'above -0.9') + ')'}`);
  }
  say(`   p = ${p}: ${cells.join('; ')}`);
}
// ---- 4. distortion of the direction map at n = 2, and the symmetries
function distortion(n, q, N) {
  const h = 2e-6, rows = [];
  for (let k = 0; k < N; k++) {
    const d = rdir(), t0 = unit([gauss(), gauss(), gauss()]);
    let a = unit([d[1] * t0[2] - d[2] * t0[1], d[2] * t0[0] - d[0] * t0[2], d[0] * t0[1] - d[1] * t0[0]]);
    const b = [d[1] * a[2] - d[2] * a[1], d[2] * a[0] - d[0] * a[2], d[0] * a[1] - d[1] * a[0]];
    const D = (e, s) => F(unit([d[0] + s * h * e[0], d[1] + s * h * e[1], d[2] + s * h * e[2]]), n, q);
    const pa = D(a, 1), ma = D(a, -1), pb = D(b, 1), mb = D(b, -1);
    const Ja = [0, 1, 2].map(i => (pa[i] - ma[i]) / (2 * h)), Jb = [0, 1, 2].map(i => (pb[i] - mb[i]) / (2 * h));
    const E = dot(Ja, Ja), G = dot(Jb, Jb), Fm = dot(Ja, Jb);
    const tr = E + G, det = Math.max(E * G - Fm * Fm, 0), s1 = Math.sqrt((tr + Math.sqrt(Math.max(tr * tr - 4 * det, 0))) / 2) / Math.abs(n), s2 = Math.sqrt(det) / (s1 * n * n);
    let t = 0;
    if (q.planes > 1) { t = parts(d, n, q).t; }
    const f0 = F(d, n, q), cr = [Ja[1] * Jb[2] - Ja[2] * Jb[1], Ja[2] * Jb[0] - Ja[0] * Jb[2], Ja[0] * Jb[1] - Ja[1] * Jb[0]];
    rows.push({ d, ar: s1 / Math.max(s2, 1e-12), s1, s2, t: Math.min(t, 1 - t), th: Math.acos(d[0]) / DEG, flip: dot(cr, f0) < 0 });
  }
  return rows;
}
say('4. Distortion of the direction map at n = 2: 20000 random directions, singular values s1 >= s2 of its derivative, divided by 2 (1 and 1 would be a shape-keeping map)');
const med = list => { const s = list.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : NaN; };
for (const set of [{ name: 'planes = 1 (the one-plane rule, for scale)', q: { planes: 1 } }, ...SETS_USED]) {
  const rows = distortion(2, set.q, 20000), ar = rows.map(r => r.ar).sort((x, y) => x - y), s1 = rows.map(r => r.s1).sort((x, y) => x - y), s2 = rows.map(r => r.s2).sort((x, y) => x - y);
  let line = `   ${set.name}: s1/s2 median ${pct(ar, 50).toFixed(3)}, 95th ${pct(ar, 95).toFixed(2)}, 99.9th ${pct(ar, 99.9).toFixed(1)}, max ${ar[ar.length - 1].toExponential(2)}; s1 median ${pct(s1, 50).toFixed(2)}, 95th ${pct(s1, 95).toFixed(2)}, 99.9th ${pct(s1, 99.9).toFixed(1)}, max ${s1[s1.length - 1].toFixed(1)}; s2 median ${pct(s2, 50).toFixed(2)}, 5th ${pct(s2, 5).toFixed(3)}, min ${s2[0].toExponential(1)}`;
  line += `; the map turns the surface over (derivative with a negative determinant) at ${(100 * rows.filter(r => r.flip).length / rows.length).toFixed(1)}% of the directions`;
  if (set.q.planes > 1) {
    const bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5];
    line += '. Median s1/s2 (and 95th) by place between two planes, 0 = on a plane, 0.5 = half way: ' + bins.slice(0, -1).map((a, i) => { const sel = rows.filter(r => r.t >= a && r.t < bins[i + 1]).map(r => r.ar).sort((x, y) => x - y); return `${a}–${bins[i + 1]}: ${pct(sel, 50).toFixed(2)} (${pct(sel, 95).toFixed(1)})`; }).join(', ');
    const top = rows.slice().sort((x, y) => y.ar - x.ar).slice(0, 40);
    line += `. The 40 worst sit at (place between planes, angle from +x): ${top.slice(0, 8).map(r => `(${r.t.toFixed(2)}, ${r.th.toFixed(0)}°) ${r.ar.toFixed(0)}`).join(', ')}; of the 40, ${top.filter(r => r.t < set.q.blend).length} are inside a plane's own band, ${top.filter(r => r.t >= set.q.blend).length} in the blend; median angle from the x-axis ${med(top.map(r => Math.min(r.th, 180 - r.th))).toFixed(0)}°`;
  }
  say(line);
}
say('   Symmetries (2000 random points each, worst |F(g v) - g F(v)| / |F(v)|):');
for (const set of SETS_USED) {
  const p = set.q.planes, cells = [];
  for (const n of [2, 3, -2]) {
    let eT = 0, eZ = 0, eY = 0;
    for (let i = 0; i < 2000; i++) {
      const v = [3 * rnd() - 1.5, 3 * rnd() - 1.5, 3 * rnd() - 1.5], f = F(v, n, set.q), m = len(f);
      eT = Math.max(eT, dist(F(rotX(v, PI / p), n, set.q), rotX(f, PI / p)) / m);
      eZ = Math.max(eZ, dist(F([v[0], v[1], -v[2]], n, set.q), [f[0], f[1], -f[2]]) / m);
      eY = Math.max(eY, dist(F([v[0], -v[1], v[2]], n, set.q), [f[0], -f[1], f[2]]) / m);
    }
    cells.push(`n=${n}: turn by 180°/${p} about x ${eT.toExponential(1)}, mirror z ${eZ.toExponential(1)}, mirror y ${eY.toExponential(1)}`);
  }
  say(`   ${set.name}: ${cells.join('; ')}`);
}

// ---- 3. shader against JavaScript
{
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 1;
  const gl = cv.getContext('webgl2');
  if (!gl || !gl.getExtension('EXT_color_buffer_float')) say('3. GLSL against JavaScript: SKIPPED, no float render target here');
  else {
    const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, 64, 1, 0, gl.RGBA, gl.FLOAT, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    const fbo = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0); gl.viewport(0, 0, 64, 1);
    const VERT = '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }';
    const HEAD = '#version 300 es\nprecision highp float;\nprecision highp int;\nuniform vec4 uA; uniform float uPow;\nout vec4 o;\nconst float PI = 3.14159265358979;\n' +
      'vec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }\nfloat at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }\n';
    const MAIN = '\nuniform vec3 uP[64], uQ[64]; uniform int uOp; uniform float uN;\nvoid main(){ int i = int(gl_FragCoord.x); vec3 v = uP[i], r;\n if (uOp == 0) r = pw(v, uN); else if (uOp == 1) r = sqr(v); else if (uOp == 2) r = mul(v, uQ[i]); else r = cmap(v);\n o = vec4(r, 1.0); }';
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('shader: ' + gl.getShaderInfoLog(s)); return s; };
    const prog = id => { const a = L.APPROACHES.find(x => x.id === id), p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, HEAD + a.glsl + MAIN)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; };
    const run = (p, uA, op, n, P, Q) => {
      gl.useProgram(p); const U = name => gl.getUniformLocation(p, name);
      gl.uniform4fv(U('uA'), uA); gl.uniform1f(U('uPow'), n); gl.uniform1f(U('uN'), n); gl.uniform1i(U('uOp'), op);
      const flat = pts => { const f = new Float32Array(192); (pts || []).forEach((v, i) => f.set(v, 3 * i)); return f; };
      gl.uniform3fv(U('uP[0]'), flat(P)); gl.uniform3fv(U('uQ[0]'), flat(Q)); gl.drawArrays(gl.TRIANGLES, 0, 3);
      const o = new Float32Array(256); gl.readPixels(0, 0, 64, 1, gl.RGBA, gl.FLOAT, o);
      return P.map((_, i) => [o[4 * i], o[4 * i + 1], o[4 * i + 2]]);
    };
    const soft = prog('softfold'), mer = prog('mercator'), f32 = v => Array.from(new Float32Array(v));
    say('3. GLSL against JavaScript (8 powers × 2560 points per setting; of every 64 points 12 lie in the plane z = 0, 6 in y = 0, 6 on the other planes or half way, 8 just beside z = 0); the error is |glsl - js| / (1 + |js|)');
    for (const set of SETS_USED) {
      const q = set.q, uA = [q.planes, q.blend, q.curve, q.mix], p = q.planes;
      let worst = 0, where = '', worstSq = 0, worstMul = 0, planeZ = 0, finite = true, count = 0, big = 0, bigList = [], errs = [], worstC = 0;
      for (let batch = 0; batch < 40; batch++) {
        const P = [], Q = [];
        for (let i = 0; i < 64; i++) {
          let v = [3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6, 3.2 * (rnd() - 0.5)];
          if (i < 12) v[2] = 0;
          else if (i < 18) v[1] = 0;
          else if (i < 24) { const a = (1 + (i % 6)) * 0.5 * PI / p, rr = v[1]; v = [v[0], rr * Math.cos(a), rr * Math.sin(a)]; }
          else if (i < 32) v[2] = 0.02 * (rnd() - 0.5);
          P.push(f32(v)); Q.push(f32([3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6]));
        }
        for (const n of NS) {
          run(soft, uA, 0, n, P).forEach((g, i) => {
            const want = F(P[i], n, q), e = dist(g, want) / (1 + len(want)); count++; errs.push(e);
            if (!g.every(Number.isFinite)) finite = false;
            if (e > 2e-3) { big++; if (bigList.length < 3) bigList.push(`n=${n} v=${P[i].map(x => x.toFixed(4))} glsl=${g.map(x => x.toFixed(4))} js=${want.map(x => x.toFixed(4))}`); }
            if (e > worst) { worst = e; where = `n=${n} v=${P[i].map(x => x.toFixed(4))}`; }
            if (i < 12) planeZ = Math.max(planeZ, Math.abs(g[2]));
          });
        }
        const two = P.map(v => F(v, 2, q));
        run(soft, uA, 1, 2, P).forEach((g, i) => { worstSq = Math.max(worstSq, dist(g, two[i]) / (1 + len(two[i]))); });
        const a = run(soft, uA, 2, 2, P, Q), b = run(mer, [1, 0, 0, 0], 2, 2, P, Q);
        a.forEach((g, i) => { worstMul = Math.max(worstMul, dist(g, b[i]) / (1 + len(b[i]))); if (!g.every(Number.isFinite)) finite = false; });
        run(soft, uA, 3, 2, P).forEach((g, i) => { worstC = Math.max(worstC, dist(g, P[i])); });
      }
      const edge = [[0, 0, 0], [1e-12, 0, 0], [0, 0, 1e-9], [0, 1e-25, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -2], [0, 3, 0], [0, -3, 0], [50, -40, 30], [64, 0, 0], [0, 0, 64], [1e9, 2e9, -1e9], [1e18, 0, 0], [0, 1e18, 1e18], [-1e18, 1e18, 1e18], [-0.618034, 0, 0.786151], [-0.618034, 0.786151, 0], [1, 1e-20, 1e-20], [-2, 0, 1e-30]];
      let cap = 0, note = '';
      for (const n of [2, 3, 8, -1, -2, -3]) for (const g of run(soft, uA, 0, n, edge)) { if (!g.every(Number.isFinite)) { finite = false; note = 'pw n=' + n + ' -> ' + g; } cap = Math.max(cap, ...g.map(Math.abs)); }
      errs.sort((x, y) => x - y);
      say(`   ${set.name}: ${count} values, worst ${worst.toExponential(2)} at ${where}; median ${pct(errs, 50).toExponential(1)}, 99.9th ${pct(errs, 99.9).toExponential(1)}; ${big} over 2e-3${bigList.length ? ' e.g. ' + bigList.join(' | ') : ''}; sqr() against the JavaScript square ${worstSq.toExponential(1)}; mul(a, b) against the Sphere inversions shader with one plane ${worstMul.toExponential(1)}; cmap(c) - c ${worstC.toExponential(1)}; largest |z| returned for a point of the plane z = 0: ${planeZ.toExponential(1)}; finite at the origin, on the axes and at 1e18: ${finite ? 'yes' : 'NO ' + note}, largest component ${cap.toExponential(2)}`);
    }
  }
}
return out.join('\n');
