// Round 20, entry: numbers for "Wind, then square" (windsq). Runs inside the page (tools/shot.py). Returns one JSON string.
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES;
const out = {};
const PI = Math.PI, ID = 'windsq';
let seed = 20261119;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const rdir = () => { const z = rnd() * 2 - 1, a = (rnd() * 2 - 1) * PI, h = Math.sqrt(1 - z * z); return [h * Math.cos(a), h * Math.sin(a), z]; };
const f32 = v => Array.from(new Float32Array(v));
const rotx = (v, a) => [v[0], Math.cos(a) * v[1] - Math.sin(a) * v[2], Math.sin(a) * v[1] + Math.cos(a) * v[2]];
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const kOf = n => { const m = Math.max(1, Math.floor(Math.abs(n) + 0.5)); return m % 2 ? m : m + 1; };
const me = AP.find(a => a.id === ID);
out.entry = { place: AP.indexOf(me), of: AP.length, ids: AP.map(a => a.id).join(' '), name: me.name, group: me.group, deMax: me.deMax === undefined ? 'none' : me.deMax };

// ---------- 1. points: 20,000 anywhere in a ball; 7,000 crowded where the rule is delicate
const P = [];
for (let i = 0; i < 20000; i++) { const d = rdir(), r = 0.05 + 1.55 * Math.cbrt(rnd()); P.push([r * d[0], r * d[1], r * d[2]]); }
const Q = [];
for (let i = 0; i < 7000; i++) {
  const k = i % 7, r = 0.3 + 1.2 * rnd(), a = (rnd() * 2 - 1) * PI, e = Math.pow(10, -1 - 7 * rnd()) * (rnd() < 0.5 ? -1 : 1);
  const pl = deg => { const t = deg * PI / 180 + e; return [Math.cos(a), Math.sin(a) * Math.cos(t), Math.sin(a) * Math.sin(t)]; };   // beside the plane at deg degrees
  let d;
  if (k === 0) d = pl(0);
  else if (k === 1) d = pl(60);
  else if (k === 2) d = pl(120);
  else if (k === 3) d = pl(30);
  else if (k === 4) d = pl(90);
  else if (k === 5) d = [rnd() < 0.5 ? -1 : 1, e * Math.cos(a), e * Math.sin(a)];             // beside the x-axis
  else d = [e * Math.cos(a), e * Math.sin(a), rnd() < 0.5 ? -1 : 1];                          // beside the z-axis
  const l = Math.hypot(d[0], d[1], d[2]);
  Q.push([r * d[0] / l, r * d[1] / l, r * d[2] / l]);
}
out.math = { P: P.slice(0, 6000), Q, F: {}, G: {} };
for (const n of [2, 3, 4, 5]) { out.math.F[n] = P.slice(0, 6000).map(v => M[ID](v, n, {})); out.math.G[n] = Q.map(v => M[ID](v, n, {})); }

// ---------- 2. half-planes through the x-axis: is a point of the half-plane at the angle a sent INTO the plane z = 0,
// onto the complex power of x + i·rho (or of x − i·rho)? Angles in steps of 180/(4k) degrees.
out.half = {};
for (const n of [2, 3, 4, 5]) {
  const k = kOf(n), rows = [];
  for (let j = 0; j < 8 * k; j++) {
    const a = j * PI / (4 * k);
    let wp = 0, wm = 0;
    for (let i = 0; i < 500; i++) {
      const r = 0.05 + 1.5 * rnd(), t = rnd() * PI, x = r * Math.cos(t), rho = r * Math.sin(t);
      const g = M[ID]([x, rho * Math.cos(a), rho * Math.sin(a)], n, {}), R = Math.pow(r, n), X = R * Math.cos(n * t), Y = R * Math.sin(n * t);
      wp = Math.max(wp, dist(g, [X, Y, 0]) / R); wm = Math.max(wm, dist(g, [X, -Y, 0]) / R);
    }
    rows.push([+(j * 180 / (4 * k)).toFixed(2), wp, wm]);
  }
  out.half['n=' + n + ' k=' + k] = rows;
}
// the plane z = 0: z out must be exactly 0, and x, y those of Sphere inversions, one plane
out.flat = {};
for (const n of [2, 3, 4, 5, -2, 2.5, 1, 0.5]) {
  let zbad = 0, worst = 0;
  for (let i = 0; i < 4000; i++) {
    const r = 0.05 + 1.6 * rnd(), a = (rnd() * 2 - 1) * PI, v = [r * Math.cos(a), r * Math.sin(a), 0], g = M[ID](v, n, {}), w = M.mercator(v, n, {});
    if (g[2] !== 0) zbad++;
    worst = Math.max(worst, Math.hypot(g[0] - w[0], g[1] - w[1]) / Math.pow(r, n));
  }
  out.flat['n=' + n] = { points: 4000, zNotZero: zbad, worstAgainstOnePlane: worst };
}
// power 1 and powers that round to 1: the rule is the one-plane rule itself
{ let w = 0; for (let i = 0; i < 4000; i++) for (const n of [1, 0.7, 1.3, -1]) w = Math.max(w, dist(M[ID](P[i], n, {}), M.mercator(P[i], n, {})) / Math.pow(Math.hypot(...P[i]), n)); out.kOne = { points: 4000, powers: [1, 0.7, 1.3, -1], worstAgainstOnePlane: w }; }

// ---------- 3. the jump test: pairs of points a step apart; the largest gap between their answers
out.jump = {};
for (const n of [2, 3, 4, 5]) {
  const row = {};
  for (const h of [1e-3, 1e-4, 1e-5, 1e-6]) {
    let worst = 0, at = null;
    for (let i = 0; i < 200000; i++) {
      let a;
      if (i % 4 === 0) { const d = rdir(), r = 0.2 + 1.3 * rnd(); a = [r * d[0], r * d[1], r * d[2]]; }
      else a = Q[(i * 7 + (i >> 2)) % Q.length].slice();
      const e = rdir(), b = [a[0] + h * e[0], a[1] + h * e[1], a[2] + h * e[2]];
      const g = dist(M[ID](a, n, {}), M[ID](b, n, {}));
      if (g > worst) { worst = g; at = a; }
    }
    row['step ' + h] = { largest: worst, ratio: worst / h, at };
  }
  out.jump['n=' + n] = row;
}

// ---------- 4. symmetries
out.sym = {};
for (const n of [2, 3, 4, 5]) {
  const k = kOf(n);
  let mz = 0, my = 0, turnK = 0, turn2K = 0, len = 0;
  for (let i = 0; i < 4000; i++) {
    const v = P[i], F = M[ID](v, n, {}), R = Math.pow(Math.hypot(...v), n);
    const a = M[ID]([v[0], v[1], -v[2]], n, {}); mz = Math.max(mz, dist(a, [F[0], F[1], -F[2]]) / R);
    const b = M[ID]([v[0], -v[1], v[2]], n, {}); my = Math.max(my, dist(b, [F[0], -F[1], F[2]]) / R);
    const c = M[ID](rotx(v, 2 * PI / k), n, {}); turnK = Math.max(turnK, dist(c, F) / R);                       // a turn by 360/k leaves the answer as it is
    const d = M[ID](rotx(v, PI / k), n, {}); turn2K = Math.max(turn2K, dist(d, [F[0], -F[1], -F[2]]) / R);       // a turn by 180/k: the answer turned half a turn about the x-axis
    len = Math.max(len, Math.abs(Math.hypot(...F) / R - 1));
  }
  out.sym['n=' + n + ' k=' + k] = { mirrorZ: mz, mirrorY: my, sameAfterTurnBy360overK: turnK, afterTurnBy180overK_answerHalfTurned: turn2K, lengthOff: len };
}

// ---------- 5. the Learn tab's plan for the entry (must not throw)
try {
  const v = [0.3, 0.4, 0.5], pl = L.learnPlan ? L.learnPlan({ id: ID, v, n: 2, space: 3 }) : null;
  let chk = '';
  if (pl && typeof pl.check === 'function') { try { chk = ', its own check: ' + JSON.stringify(pl.check(v)).slice(0, 300); } catch (e) { chk = ', its own check THROWS: ' + e.message; } }
  let end = '';
  if (pl && typeof pl.run === 'function') { try { const r = pl.run(v); const last = Array.isArray(r) ? r[r.length - 1] : r; end = ', run ends at ' + JSON.stringify(last && (last.to || last.v || last)).slice(0, 200); } catch (e) { end = ', run THROWS: ' + e.message; } }
  out.learn = pl ? 'plan for ' + pl.id + ' with ' + (pl.moves ? pl.moves.length : '?') + ' moves' + chk + end + '; MATH gives ' + JSON.stringify(M[ID](v, 2, {})) : 'no learnPlan on window.squaringLab';
} catch (e) { out.learn = 'THROWS: ' + e.message; }

// ---------- 6. the shader against MATH (64 points per draw into a float texture)
const cv = document.createElement('canvas'); cv.width = 64; cv.height = 1;
const gl = cv.getContext('webgl2');
const gpu = !!(gl && gl.getExtension('EXT_color_buffer_float'));
out.gpu = gpu;
if (gpu) {
  const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, 64, 1, 0, gl.RGBA, gl.FLOAT, null);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  const fbo = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0); gl.viewport(0, 0, 64, 1);
  const VERT = '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }';
  const HEAD = '#version 300 es\nprecision highp float;\nprecision highp int;\nuniform vec4 uA; uniform float uPow, uJulia; uniform vec3 uC;\nout vec4 o;\nconst float PI = 3.14159265358979;\n' +
    'vec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }\nfloat at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }\n';
  const MAIN = '\nuniform vec3 uP[64], uQ[64]; uniform int uOp; uniform float uN;\nvoid main(){ int i = int(gl_FragCoord.x); vec3 v = uP[i], r;\n if (uOp == 0) r = pw(v, uN); else if (uOp == 1) r = sqr(v); else if (uOp == 2) r = mul(v, uQ[i]); else r = cmap(v);\n o = vec4(r, 1.0); }';
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('shader: ' + gl.getShaderInfoLog(s)); return s; };
  const progs = {};
  const prog = id => progs[id] || (progs[id] = (() => { const a = AP.find(x => x.id === id), p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, HEAD + a.glsl + MAIN)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; })());
  const run = (id, o, A, B) => {
    const p = prog(id); gl.useProgram(p); const U = name => gl.getUniformLocation(p, name);
    gl.uniform4fv(U('uA'), [0, 0, 0, 0]); gl.uniform1f(U('uPow'), o.n || 2); gl.uniform1f(U('uN'), o.n || 2); gl.uniform1i(U('uOp'), o.op || 0);
    gl.uniform1f(U('uJulia'), 0); gl.uniform3fv(U('uC'), [0, 0, 0]);
    const flat = pts => { const f = new Float32Array(192); (pts || []).forEach((v, i) => f.set(v, 3 * i)); return f; };
    gl.uniform3fv(U('uP[0]'), flat(A)); gl.uniform3fv(U('uQ[0]'), flat(B)); gl.drawArrays(gl.TRIANGLES, 0, 3);
    const r = new Float32Array(256); gl.readPixels(0, 0, 64, 1, gl.RGBA, gl.FLOAT, r);
    return A.map((_, i) => [r[4 * i], r[4 * i + 1], r[4 * i + 2]]);
  };
  const many = (id, o, A, B) => { const r = []; for (let i = 0; i < A.length; i += 64) r.push(...run(id, o, A.slice(i, i + 64), B ? B.slice(i, i + 64) : null)); return r; };
  const quant = (e, q) => { const s = e.slice().sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(q * s.length))]; };
  const rel = (g, w) => Math.hypot(g[0] - w[0], g[1] - w[1], g[2] - w[2]) / Math.max(Math.hypot(w[0], w[1], w[2]), 1e-30);
  const stats = e => ({ points: e.length, median: quant(e, 0.5), q99: quant(e, 0.99), q999: quant(e, 0.999), max: e.reduce((a, b) => Math.max(a, b), 0), over1e3: e.filter(x => x > 1e-3).length, over1e2: e.filter(x => x > 1e-2).length });
  const A = P.slice(0, 8192).map(f32), A2 = Q.map(f32);
  out.glsl = {};
  for (const [name, pts] of [['ball', A], ['delicate', A2]]) {
    const g2 = many(ID, { op: 1, n: 2 }, pts), e2 = g2.map((x, i) => rel(x, M[ID](pts[i], 2, {})));
    out.glsl['sqr ' + name] = Object.assign(stats(e2), { finite: g2.every(x => x.every(Number.isFinite)) });
    for (const n of [2, 3, 4, 5, -2]) {
      const g = many(ID, { op: 0, n }, pts), e = g.map((x, i) => rel(x, M[ID](pts[i], n, {})));
      out.glsl['pw n=' + n + ' ' + name] = Object.assign(stats(e), { finite: g.every(x => x.every(Number.isFinite)) });
    }
  }
  for (const n of [2, 3, 4, 5]) {
    const F = []; for (let i = 0; i < 1024; i++) { const r = 0.05 + 1.6 * rnd(), a = (rnd() * 2 - 1) * PI; F.push(f32([r * Math.cos(a), r * Math.sin(a), 0])); }
    const g = many(ID, { op: n === 2 ? 1 : 0, n }, F);
    let zbad = 0, worst = 0;
    g.forEach((x, i) => { if (x[2] !== 0) zbad++; const v = F[i], r = Math.hypot(v[0], v[1]), a = Math.atan2(v[1], v[0]), R = Math.pow(r, n); worst = Math.max(worst, Math.hypot(x[0] - R * Math.cos(n * a), x[1] - R * Math.sin(n * a)) / R); });
    out.glsl['flat n=' + n] = { points: 1024, zNotZero: zbad, worstRelative: worst };
  }
  // the half-planes at 60, 120, ... degrees in the shader (power 2): how far from the plane z = 0 does the answer land?
  {
    const H = []; for (let i = 0; i < 1024; i++) { const r = 0.05 + 1.5 * rnd(), t = rnd() * PI, a = (1 + (i % 5)) * PI / 3; H.push(f32([r * Math.cos(t), r * Math.sin(t) * Math.cos(a), r * Math.sin(t) * Math.sin(a)])); }
    const g = many(ID, { op: 1, n: 2 }, H);
    out.glsl['copy planes n=2'] = { points: 1024, worstZoverLength: g.reduce((w, x, i) => Math.max(w, Math.abs(x[2]) / Math.pow(Math.hypot(...H[i]), 2)), 0) };
  }
  {
    const B = A.slice(64, 64 + 1024), C = A.slice(2048, 2048 + 1024);
    const g = many(ID, { op: 2 }, B, C), w = many('mercator', { op: 2 }, B, C);
    out.glsl.mul = { points: 1024, worstAgainstOnePlane: g.reduce((m, x, i) => Math.max(m, rel(x, w[i])), 0) };
  }
}
return JSON.stringify(out);
