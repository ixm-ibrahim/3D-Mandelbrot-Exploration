// Numeric checks of the axisbulb rule, run inside the built page (python out/lab2/axisbulb/run_checks.py).
// Everything calls the page's own MATH.axisbulb (the JavaScript mirror of the shader).
const L = window.squaringLab, M = L.MATH;
const out = [], say = s => out.push(s);
let seed = 12345;
const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const gauss = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
const len = v => Math.hypot(v[0], v[1], v[2]), unit = v => { const l = len(v); return [v[0] / l, v[1] / l, v[2] / l]; };
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const rdir = () => unit([gauss(), gauss(), gauss()]);
const pct = (sorted, p) => sorted[Math.min(sorted.length - 1, Math.floor(p / 100 * sorted.length))];
const DEG = Math.PI / 180, H2 = Math.SQRT1_2;
const dirBG = (b, g) => [Math.cos(b), Math.sin(b) * Math.cos(g), Math.sin(b) * Math.sin(g)];
const VARS = [
  ['k = 5', { k: 5, wob: 0, reach: 45 }],
  ['k = -3', { k: -3, wob: 0, reach: 45 }],
  ['k = 1, A = 0.2', { k: 1, wob: 0.2, reach: 45 }],
  ['k = 1, A = 0.6', { k: 1, wob: 0.6, reach: 45 }],
  ['k = 5, A = 0.2', { k: 5, wob: 0.2, reach: 45 }],
  ['k = 1, pinch B = 1.5', { k: 1, wob: 0, reach: 45, pinch: 1.5 }],
  ['k = 9', { k: 9, wob: 0, reach: 45 }],
  ['k = -7, A = 1, reach 0, pinch B = 4', { k: -7, wob: 1, reach: 0, pinch: 4 }],
  ['k = 3', { k: 3, wob: 0, reach: 45 }],
  ['k = -1', { k: -1, wob: 0, reach: 45 }],
  ['k = 2', { k: 2, wob: 0, reach: 45 }],
  ['k = 1 (the lathe)', { k: 1, wob: 0, reach: 45 }],
];
const Fq = q => (v, n) => M.axisbulb(v, n, q);

// ---- 1. exactness on the planes through the x-axis
function cpow(x, y, n) {     // complex power by repeated multiplication (no angles involved)
  let a = 1, b = 0;
  for (let k = 0; k < Math.abs(n); k++) [a, b] = [a * x - b * y, a * y + b * x];
  if (n < 0) { const m = a * a + b * b; a = a / m; b = -b / m; }
  return [a, b];
}
const planePts = [];
for (let k = 0; k < 500; k++) {
  let th = 2 * Math.PI * rnd(), r = 0.05 + 2 * rnd();
  if (k < 160) th = [0, 90, 180, 270, 360, -90, 45, 135][k % 8] * DEG + (k < 16 ? 0 : (rnd() - 0.5) * Math.pow(10, -1 - 13 * rnd()));   // on and beside the axes
  if (k >= 160 && k < 220) r = Math.pow(10, -1 - 4 * rnd());       // near the origin (down to 1e-5; closer in, a negative power passes the lab's cap on lengths)
  planePts.push([r * Math.cos(th), r * Math.sin(th)]);
}
for (let k = 0; k < 8; k++) planePts[k] = [[1, 0], [0, 1], [-1, 0], [0, -1], [0.5, 0], [0, -0.5], [-2, 0], [0, 2]][k];   // exactly on the axes
const PLANES = [
  ['z = 0', (a, b) => [a, b, 0]], ['y = 0', (a, b) => [a, 0, b]],
  ['45° (y = z)', (a, b) => [a, b * H2, b * H2]], ['135° (y = -z)', (a, b) => [a, -b * H2, b * H2]],
];
const NS = [2, 3, 4, 5, 8, -1, -2, -3];
say('1. Exactness (500 points per plane, on and beside the axes and near the origin included): worst |F - w^n| / |w^n| per n = ' + NS.join(', ') + '; "mirror" = the same against conj(w)^n');
for (const [name, q] of VARS) {
  const F = Fq(q), rows = [];
  for (const [pn, emb] of PLANES) {
    const worst = [], worstM = [];
    for (const n of NS) {
      let e = 0, em = 0;
      for (const [a, b] of planePts) {
        const g = F(emb(a, b), n), [A, B] = cpow(a, b, n), m = Math.hypot(A, B);
        e = Math.max(e, dist(g, emb(A, B)) / m); em = Math.max(em, dist(g, emb(A, -B)) / m);
      }
      worst.push(e); worstM.push(em);
    }
    const we = Math.max(...worst), wm = Math.max(...worstM);
    rows.push(`${pn}: ${we < 1e-6 ? 'EXACT, worst per n ' + worst.map(x => x.toExponential(1)).join(' ') : wm < 1e-6 ? 'MIRROR IMAGE conj(w)^n, worst per n ' + worstM.map(x => x.toExponential(1)).join(' ') : 'neither (power ' + we.toExponential(1) + ', mirror ' + wm.toExponential(1) + ')'}`);
  }
  say(`   ${name}:\n      ` + rows.join('\n      '));
}

// ---- 2. continuity
function pairs(N, n) {
  const P = [], h = 1e-5, extra = { planes: 0, seams: 0, axis: 0, cones: 0 };
  const push = (a, b) => P.push([unit(a), unit(b)]);
  for (let k = 0; k < N; k++) { const d = rdir(), e = [gauss(), gauss(), gauss()]; push(d, [d[0] + h * e[0], d[1] + h * e[1], d[2] + h * e[2]]); }
  for (let k = 0; k < 16000; k++) {      // straddling the eight half-planes at turn j * 45° (z = 0, y = 0, both diagonals)
    const g0 = (k % 8) * 45 * DEG, b = Math.PI * rnd(), dg = 0.5 * h * rnd() / Math.max(Math.sin(b), 1e-3), db = (rnd() - 0.5) * h;
    push(dirBG(b, g0 + dg), dirBG(b + db, g0 - dg)); extra.planes++;
  }
  for (let k = 0; k < 16000; k++) {      // straddling the half-way seams at turn 22.5° + j * 45°
    const g0 = (22.5 + (k % 8) * 45) * DEG, b = Math.PI * rnd(), dg = 0.5 * h * rnd() / Math.max(Math.sin(b), 1e-3), db = (rnd() - 0.5) * h;
    push(dirBG(b, g0 + dg), dirBG(b + db, g0 - dg)); extra.seams++;
  }
  for (let k = 0; k < 12000; k++) {      // within a few h of the x-axis (both ends), on every side of it, the axis itself included
    const c = [k % 2 ? 1 : -1, 0, 0], sc = h * Math.pow(10, -3 * rnd() * (k % 3 === 0)), o1 = [0, gauss() * sc, gauss() * sc], o2 = [0, gauss() * sc, gauss() * sc];
    push([c[0], o1[1], o1[2]], k % 5 === 0 ? c : [c[0], o2[1], o2[2]]); extra.axis++;
  }
  const m = Math.abs(n);
  for (let k = 0; k < 12000; k++) {      // straddling the cones where n times the angle from the x-axis is a multiple of 180° (their images shrink to the axis)
    const b0 = (1 + k % (m - 1 || 1)) * Math.PI / m, g = 2 * Math.PI * rnd(), db = 0.5 * h * rnd(), dg = (rnd() - 0.5) * h;
    push(dirBG(b0 + db, g), dirBG(b0 - db, g + dg)); extra.cones++;
  }
  return { P, extra };
}
say('2. Continuity: pairs of unit directions about 1e-5 apart; ratio |F(d1) - F(d2)| / |d1 - d2| (a jump shows as a ratio in the tens of thousands)');
for (const n of [2, 3, -2]) {
  seed = 777 + n;
  const { P, extra } = pairs(200000, n);
  say(`   n = ${n}: 200000 random pairs plus ${JSON.stringify(extra)}`);
  const list = VARS.map(([name, q]) => [name, Fq(q)]);
  if (n === 2) list.push(['for comparison, Sphere inversions folded on 2 planes', (v, nn) => M.mercator(v, nn, { planes: 2 })]);
  for (const [name, F] of list) {
    const ratios = new Float64Array(P.length); let max = 0, at = null;
    P.forEach(([a, b], k) => {
      const q = dist(a, b); if (!(q > 1e-13)) { ratios[k] = 0; return; }
      const r = dist(F(a, n), F(b, n)) / q; ratios[k] = r;
      if (r > max) { max = r; at = a; }
    });
    const first = Array.from(ratios.subarray(0, 200000)).sort((x, y) => x - y), rest = Array.from(ratios.subarray(200000)).sort((x, y) => x - y);
    say(`      ${name}: max ${max.toFixed(2)} (at ${(Math.acos(at[0]) / DEG).toFixed(2)}° from the x-axis, turn ${(Math.atan2(at[2], at[1]) / DEG).toFixed(2)}°); random pairs: 99.9th percentile ${pct(first, 99.9).toFixed(2)}, median ${pct(first, 50).toFixed(2)}, max ${first[first.length - 1].toFixed(2)}; special pairs: max ${rest[rest.length - 1].toFixed(2)}, 99.9th ${pct(rest, 99.9).toFixed(2)}  ${max < 1000 ? 'bounded' : 'JUMP'}`);
  }
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
    const a = L.APPROACHES.find(x => x.id === 'axisbulb'), p = gl.createProgram();
    gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, HEAD + a.glsl + MAIN)); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    gl.useProgram(p); const U = name => gl.getUniformLocation(p, name);
    const run = (uA, op, n, P, Q) => {
      gl.uniform4fv(U('uA'), uA); gl.uniform1f(U('uPow'), n); gl.uniform1f(U('uN'), n); gl.uniform1i(U('uOp'), op);
      const flat = pts => { const f = new Float32Array(192); (pts || []).forEach((v, i) => f.set(v, 3 * i)); return f; };
      gl.uniform3fv(U('uP[0]'), flat(P)); gl.uniform3fv(U('uQ[0]'), flat(Q)); gl.drawArrays(gl.TRIANGLES, 0, 3);
      const o = new Float32Array(256); gl.readPixels(0, 0, 64, 1, gl.RGBA, gl.FLOAT, o);
      return P.map((_, i) => [o[4 * i], o[4 * i + 1], o[4 * i + 2]]);
    };
    const f32 = v => Array.from(new Float32Array(v));
    const edge = [[0, 0, 0], [1e-12, 0, 0], [0, 0, 1e-9], [0, 1e-25, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -2], [0, 3, 0], [50, -40, 30], [64, 0, 0], [0, 0, 64], [1e9, 2e9, -1e9], [1e18, 0, 0], [0, 1e18, 1e18], [-1e18, 1e18, 1e18], [0, 1e-30, 1e-30], [-3, 1e-20, 0]];
    say('3. GLSL against JavaScript. Per setting: 8 powers x 640 points through pw(); of every 64 points 12 have z = 0 exactly, 12 have y = 0 exactly, 12 lie within 0.01 of the plane z = 0');
    for (const [name, q] of VARS) {
      const uA = [q.k, q.wob, q.reach, q.pinch || 0], F = Fq(q);
      let worst = 0, where = '', worstSq = 0, worstMul = 0, planeZ = 0, planeY = 0, finite = true, count = 0, big = 0, cap = 0, note = '';
      for (let batch = 0; batch < 10; batch++) {
        const P = [], Q = [];
        for (let i = 0; i < 64; i++) {
          const v = [3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6, i < 36 ? 0.02 * (rnd() - 0.5) : 3.2 * (rnd() - 0.5)];
          if (i < 12) v[2] = 0; else if (i < 24) { v[2] = v[1]; v[1] = 0; }
          P.push(f32(v)); Q.push(f32([3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6]));
        }
        for (const n of NS) {
          run(uA, 0, n, P).forEach((g, i) => {
            const want = F(P[i], n), e = dist(g, want) / (1 + len(want)); count++;
            if (!g.every(Number.isFinite)) finite = false;
            if (e > 2e-3) big++;
            if (e > worst) { worst = e; where = `n=${n} v=${P[i].map(x => x.toFixed(4))}`; }
            if (i < 12) planeZ = Math.max(planeZ, Math.abs(g[2])); else if (i < 24) planeY = Math.max(planeY, Math.abs(g[1]));
          });
        }
        const two = P.map(v => F(v, 2));
        run(uA, 1, 2, P).forEach((g, i) => { worstSq = Math.max(worstSq, dist(g, two[i]) / (1 + len(two[i]))); if (i < 12) planeZ = Math.max(planeZ, Math.abs(g[2])); else if (i < 24) planeY = Math.max(planeY, Math.abs(g[1])); });
        run(uA, 2, 2, P, Q).forEach((g, i) => {
          const a = P[i], b = Q[i], w = [a[0] * b[0] - a[1] * b[1] - a[2] * b[2], a[0] * b[1] + b[0] * a[1], a[0] * b[2] + b[0] * a[2]], want = F(w, 1);   // the lathe's product, then the turn (F at n = 1 is the turn alone)
          worstMul = Math.max(worstMul, dist(g, want) / (1 + len(want))); if (!g.every(Number.isFinite)) finite = false;
        });
      }
      for (const n of [2, 3, 8, -1, -2, -3]) for (const g of run(uA, 0, n, edge)) { if (!g.every(Number.isFinite)) { finite = false; note = 'pw n=' + n + ' -> ' + g; } cap = Math.max(cap, ...g.map(Math.abs)); }
      for (const g of run(uA, 1, 2, edge)) { if (!g.every(Number.isFinite)) { finite = false; note = 'sqr -> ' + g; } }
      say(`   ${name}: worst |glsl - js| / (1 + |js|) over ${count} values = ${worst.toExponential(2)} (${where}), ${big} above 2e-3; sqr() against the JavaScript square ${worstSq.toExponential(1)}; mul(a, b) against the lathe product followed by the turn ${worstMul.toExponential(1)}; largest |z| the shader returns for a point with z = 0: ${planeZ === 0 ? 'exactly 0' : planeZ.toExponential(1)}; largest |y| for a point with y = 0: ${planeY === 0 ? 'exactly 0' : planeY.toExponential(1)}; finite at the origin, on the axes and at 1e18: ${finite ? 'yes' : 'NO ' + note} (largest component ${cap.toExponential(2)})`);
    }
  }
}

// ---- 4. distortion of the direction map at n = 2
function distortion(F, n, N) {
  const h = 2e-6, rows = [];
  for (let k = 0; k < N; k++) {
    const d = rdir(), t = unit([gauss(), gauss(), gauss()]);
    let a = [d[1] * t[2] - d[2] * t[1], d[2] * t[0] - d[0] * t[2], d[0] * t[1] - d[1] * t[0]]; a = unit(a);
    const b = [d[1] * a[2] - d[2] * a[1], d[2] * a[0] - d[0] * a[2], d[0] * a[1] - d[1] * a[0]];
    const D = (e, s) => F(unit([d[0] + s * h * e[0], d[1] + s * h * e[1], d[2] + s * h * e[2]]), n);
    const pa = D(a, 1), ma = D(a, -1), pb = D(b, 1), mb = D(b, -1);
    const Ja = [0, 1, 2].map(i => (pa[i] - ma[i]) / (2 * h)), Jb = [0, 1, 2].map(i => (pb[i] - mb[i]) / (2 * h));
    const E = Ja[0] * Ja[0] + Ja[1] * Ja[1] + Ja[2] * Ja[2], G = Jb[0] * Jb[0] + Jb[1] * Jb[1] + Jb[2] * Jb[2], Fm = Ja[0] * Jb[0] + Ja[1] * Jb[1] + Ja[2] * Jb[2];
    const tr = E + G, det = Math.max(E * G - Fm * Fm, 0), s1 = Math.sqrt((tr + Math.sqrt(Math.max(tr * tr - 4 * det, 0))) / 2) / Math.abs(n), s2 = Math.sqrt(det) / (s1 * n * n);
    rows.push({ d, s1, s2, ar: s1 / Math.max(s2, 1e-12) });
  }
  return rows;
}
say('4. Distortion of the direction map at n = 2: 20000 random directions, singular values s1 >= s2 of the derivative divided by 2 (1 and 1 would be a map that keeps shapes)');
for (const [name, q] of VARS.filter(v => !/k = (9|-7|3|-1|2)/.test(v[0])).concat([['for comparison, Sphere inversions with one plane', null]])) {
  seed = 4242;
  const F = q ? Fq(q) : (v, n) => M.mercator(v, n, { planes: 1 });
  const rows = distortion(F, 2, 20000), ar = rows.map(r => r.ar).sort((x, y) => x - y), s1 = rows.map(r => r.s1).sort((x, y) => x - y), s2 = rows.map(r => r.s2).sort((x, y) => x - y);
  const top = rows.slice().sort((x, y) => y.ar - x.ar).slice(0, 200), ang = r => Math.acos(r.d[0]) / DEG, trn = r => Math.atan2(r.d[2], r.d[1]) / DEG;
  say(`   ${name}: s1/s2 median ${pct(ar, 50).toFixed(2)}, 95th ${pct(ar, 95).toFixed(1)}, 99.9th ${pct(ar, 99.9).toFixed(0)}, max ${ar[ar.length - 1].toExponential(1)}; s1 median ${pct(s1, 50).toFixed(2)}, 99.9th ${pct(s1, 99.9).toFixed(2)}, max ${s1[s1.length - 1].toFixed(2)}; s2 median ${pct(s2, 50).toFixed(2)}, 5th percentile ${pct(s2, 5).toFixed(3)}; of the 200 worst s1/s2, ${top.filter(r => Math.abs(ang(r) - 90) < 5).length} lie within 5° of the plane x = 0 (angle 90° from the x-axis), ${top.filter(r => Math.min(ang(r), 180 - ang(r)) < 10).length} within 10° of the x-axis; the 6 worst at (angle from the x-axis, turn): ${top.slice(0, 6).map(r => `(${ang(r).toFixed(1)}°, ${trn(r).toFixed(0)}°)`).join(' ')}`);
}

// ---- 5. what the turn does to the sets (the question the pictures are for, in numbers)
{
  const esc = (F, v0, c, it) => { let v = v0; for (let i = 0; i < it; i++) { const w = F(v, 2); v = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; if (v[0] * v[0] + v[1] * v[1] + v[2] * v[2] > 16) return i; } return it; };
  const lathe = Fq({ k: 1, wob: 0 });
  seed = 99;
  const pts = []; for (let i = 0; i < 20000; i++) pts.push([3.4 * rnd() - 1.7, 3.4 * rnd() - 1.7, 3.4 * rnd() - 1.7]);
  say('5a. Julia set, c = (-1, 0, 0), 20000 random start points in a cube of side 3.4, 30 steps: how many get a different escape step from the lathe (0 = the same solid as the lathe, a body of revolution)');
  const ref = pts.map(v => esc(lathe, v, [-1, 0, 0], 30));
  for (const [name, q] of VARS.slice(0, 8)) { const F = Fq(q); let diff = 0, inside = 0; pts.forEach((v, i) => { const e = esc(F, v, [-1, 0, 0], 30); if (e !== ref[i]) diff++; if (e === 30) inside++; }); say(`      ${name}: ${diff} differ; ${inside} points inside (lathe: ${ref.filter(e => e === 30).length})`); }
  const refOff = pts.map(v => esc(lathe, v, [-1, 0.045, 0.026], 30));
  say('    the same for c = (-1, 0.045, 0.026), off the axis:');
  for (const [name, q] of VARS.slice(0, 8)) { const F = Fq(q); let diff = 0, inside = 0; pts.forEach((v, i) => { const e = esc(F, v, [-1, 0.045, 0.026], 30); if (e !== refOff[i]) diff++; if (e === 30) inside++; }); say(`      ${name}: ${diff} differ; ${inside} points inside (lathe: ${refOff.filter(e => e === 30).length})`); }

  const hs = [0, 1e-9, 1e-6, 1e-4, 0.01, 0.05, 0.1, 0.25, 0.5];
  say('5b. Mandelbrot solid, power 2, 40 steps: area of the slice at height z (grid step 0.02 over x -2.2..1, y -1.4..1.4). Heights: ' + hs.join(', '));
  const area = (F, h) => { let n = 0; for (let x = -2.2; x <= 1.0001; x += 0.02) for (let y = -1.4; y <= 1.4001; y += 0.02) if (esc(F, [0, 0, 0], [x, y, h], 40) === 40) n++; return n * 0.0004; };
  const list = VARS.slice(0, 7).map(([name, q]) => [name, Fq(q)]).concat([['k = 1 (the lathe)', lathe], ['Sphere inversions, one plane', (v, n) => M.mercator(v, n, { planes: 1 })], ['Sphere inversions folded on 2 planes', (v, n) => M.mercator(v, n, { planes: 2 })]]);
  for (const [name, F] of list) say(`      ${name}: ` + hs.map(h => area(F, h).toFixed(3)).join('  '));
  say('5c. The same solid cut by the half-plane at turn g through the x-axis (area over x -2.2..1, distance from the axis 0..1.4). Turns: 0°, 0.001°, 1°, 5°, 22.5°, 45°, 67.5°, 90°');
  const areaG = (F, g) => { let n = 0; const c = Math.cos(g * DEG), s = Math.sin(g * DEG); for (let x = -2.2; x <= 1.0001; x += 0.02) for (let t = 0.01; t <= 1.4001; t += 0.02) if (esc(F, [0, 0, 0], [x, t * c, t * s], 40) === 40) n++; return n * 0.0004; };
  for (const [name, F] of list) say(`      ${name}: ` + [0, 0.001, 1, 5, 22.5, 45, 67.5, 90].map(g => areaG(F, g).toFixed(3)).join('  '));
}
return out.join('\n');
