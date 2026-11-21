// Round 16, entry: numbers for the two Turning plane rules. Runs inside the page (tools/shot.py). Returns one JSON string.
// Sections: math (points and MATH results at power 2, compared with out/me/r16/scout3.py by run.py), planes (which
// planes through the x-axis follow the complex power), jump (close pairs), sym (mirrors and turns), glsl (shader against MATH).
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES;
const out = {};
const PI = Math.PI;
let seed = 20261118;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const rdir = () => { const z = rnd() * 2 - 1, a = (rnd() * 2 - 1) * PI, h = Math.sqrt(1 - z * z); return [h * Math.cos(a), h * Math.sin(a), z]; };
const f32 = v => Array.from(new Float32Array(v));
const IDS = ['turnaway', 'turnalong'];
const rotx = (v, a) => [v[0], Math.cos(a) * v[1] - Math.sin(a) * v[2], Math.sin(a) * v[1] + Math.cos(a) * v[2]];
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

// ---------- 1. power 2: 20,000 points anywhere in a ball, and 6,000 crowded where the rule is delicate
const P = [];
for (let i = 0; i < 20000; i++) { const d = rdir(), r = 0.05 + 1.55 * Math.cbrt(rnd()); P.push([r * d[0], r * d[1], r * d[2]]); }
const Q = [];
for (let i = 0; i < 6000; i++) {
  const k = i % 6, r = 0.3 + 1.2 * rnd(), a = (rnd() * 2 - 1) * PI, e = Math.pow(10, -1 - 7 * rnd()) * (rnd() < 0.5 ? -1 : 1);
  let d;
  if (k === 0) d = [Math.cos(a), Math.sin(a), e];                                  // beside the plane z = 0
  else if (k === 1) d = [Math.cos(a), e, Math.sin(a)];                             // beside the plane y = 0
  else if (k === 2) d = [Math.cos(a), Math.sin(a) * (0.7071 + e), Math.sin(a) * 0.7071];      // beside the plane y = z
  else if (k === 3) d = [Math.cos(a), Math.sin(a) * (0.7071 + e), -Math.sin(a) * 0.7071];     // beside the plane y = -z
  else if (k === 4) d = [rnd() < 0.5 ? -1 : 1, e * Math.cos(a), e * Math.sin(a)];             // beside the x-axis
  else d = [e * Math.cos(a), e * Math.sin(a), rnd() < 0.5 ? -1 : 1];                          // beside the z-axis
  const l = Math.hypot(d[0], d[1], d[2]);
  Q.push([r * d[0] / l, r * d[1] / l, r * d[2] / l]);
}
out.math = { P, Q };
for (const id of IDS) out.math[id] = { F: P.map(v => M[id](v, 2, {})), G: Q.map(v => M[id](v, 2, {})) };

// ---------- 2. planes through the x-axis: does the plane at the angle a follow the complex power? (powers 2 to 5)
// a point (x, rho) of the plane sits at (x, rho cos a, rho sin a); the complex power of x + i rho is laid back the same way
out.planes = {};
for (const id of IDS) for (const n of [2, 3, 4, 5]) {
  const rows = [];
  for (let k = 0; k < 4 * n; k++) {
    const a = k * PI / (4 * n);
    let worst = 0;
    for (let i = 0; i < 500; i++) {
      const r = 0.05 + 1.5 * rnd(), t = (rnd() * 2 - 1) * PI, x = r * Math.cos(t), rho = r * Math.sin(t);
      const g = M[id]([x, rho * Math.cos(a), rho * Math.sin(a)], n, {}), R = Math.pow(r, n), X = R * Math.cos(n * t), Y = R * Math.sin(n * t);
      worst = Math.max(worst, dist(g, [X, Y * Math.cos(a), Y * Math.sin(a)]) / R);
    }
    rows.push([+(k * 180 / (4 * n)).toFixed(2), worst]);
  }
  out.planes[id + ' n=' + n] = rows;
}
// the plane z = 0: z out must be exactly 0
out.flat = {};
for (const id of IDS) for (const n of [2, 3, 4, 5, -2, 2.5]) {
  let zbad = 0, worst = 0;
  for (let i = 0; i < 4000; i++) {
    const r = 0.05 + 1.6 * rnd(), a = (rnd() * 2 - 1) * PI, v = [r * Math.cos(a), r * Math.sin(a), 0], g = M[id](v, n, {}), w = M.mercator(v, n, {});
    if (g[2] !== 0) zbad++;
    worst = Math.max(worst, Math.hypot(g[0] - w[0], g[1] - w[1]) / Math.pow(r, n));
  }
  out.flat[id + ' n=' + n] = { points: 4000, zNotZero: zbad, worstAgainstOnePlane: worst };
}

// ---------- 3. the jump test: pairs of points a step apart; the largest gap between their answers
out.jump = {};
for (const id of IDS) for (const n of [2, 3, 4]) {
  const row = {};
  for (const h of [1e-4, 1e-5, 1e-6]) {
    let worst = 0, at = null;
    for (let i = 0; i < 200000; i++) {
      let a;
      const k = i % 4;
      if (k === 0) { const d = rdir(), r = 0.2 + 1.3 * rnd(); a = [r * d[0], r * d[1], r * d[2]]; }
      else { a = Q[(i * 7 + (i >> 2)) % Q.length].slice(); }
      const e = rdir(), b = [a[0] + h * e[0], a[1] + h * e[1], a[2] + h * e[2]];
      const g = dist(M[id](a, n, {}), M[id](b, n, {}));
      if (g > worst) { worst = g; at = a; }
    }
    row['step ' + h] = { largest: worst, at };
  }
  out.jump[id + ' n=' + n] = row;
}

// ---------- 4. symmetries: both mirrors, the half turn, and the turn by 180/m degrees about the x-axis
out.sym = {};
for (const id of IDS) for (const n of [2, 3, 4]) {
  const m = Math.max(1, Math.floor(Math.abs(n) + 0.5));
  let mz = 0, my = 0, half = 0, turn = 0, len = 0;
  for (let i = 0; i < 4000; i++) {
    const v = P[i], F = M[id](v, n, {}), R = Math.pow(Math.hypot(...v), n);
    const a = M[id]([v[0], v[1], -v[2]], n, {}); mz = Math.max(mz, dist(a, [F[0], F[1], -F[2]]) / R);
    const b = M[id]([v[0], -v[1], v[2]], n, {}); my = Math.max(my, dist(b, [F[0], -F[1], F[2]]) / R);
    const c = M[id](rotx(v, PI), n, {}); half = Math.max(half, dist(c, rotx(F, PI)) / R);
    const d = M[id](rotx(v, PI / m), n, {}); turn = Math.max(turn, dist(d, rotx(F, PI / m)) / R);
    len = Math.max(len, Math.abs(Math.hypot(...F) / R - 1));
  }
  out.sym[id + ' n=' + n] = { mirrorZ: mz, mirrorY: my, halfTurn: half, turnBy180overM: turn, m, lengthOff: len };
}

// ---------- 5. the shader against MATH (the harness of round 14: 64 points per draw into a float texture)
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
  const stats = e => ({ points: e.length, median: quant(e, 0.5), q99: quant(e, 0.99), q999: quant(e, 0.999), max: Math.max(...e), over1e3: e.filter(x => x > 1e-3).length, over1e2: e.filter(x => x > 1e-2).length });
  const A = P.slice(0, 8192).map(f32), A2 = Q.map(f32);
  out.glsl = {};
  for (const id of IDS) {
    for (const [name, pts] of [['ball', A], ['delicate', A2]]) {
      const g2 = many(id, { op: 1, n: 2 }, pts), e2 = g2.map((x, i) => rel(x, M[id](pts[i], 2, {})));
      out.glsl[id + ' sqr ' + name] = Object.assign(stats(e2), { finite: g2.every(x => x.every(Number.isFinite)) });
      for (const n of [2, 3, 4, -2]) {
        const g = many(id, { op: 0, n }, pts), e = g.map((x, i) => rel(x, M[id](pts[i], n, {})));
        out.glsl[id + ' pw n=' + n + ' ' + name] = Object.assign(stats(e), { finite: g.every(x => x.every(Number.isFinite)) });
      }
    }
    // the plane z = 0 in the shader: z out exactly 0, and the complex power
    for (const n of [2, 3]) {
      const F = []; for (let i = 0; i < 1024; i++) { const r = 0.05 + 1.6 * rnd(), a = (rnd() * 2 - 1) * PI; F.push(f32([r * Math.cos(a), r * Math.sin(a), 0])); }
      const g = many(id, { op: n === 2 ? 1 : 0, n }, F);
      let zbad = 0, worst = 0;
      g.forEach((x, i) => { if (x[2] !== 0) zbad++; const v = F[i], r = Math.hypot(v[0], v[1]), a = Math.atan2(v[1], v[0]), R = Math.pow(r, n); worst = Math.max(worst, Math.hypot(x[0] - R * Math.cos(n * a), x[1] - R * Math.sin(n * a)) / R); });
      out.glsl[id + ' flat n=' + n] = { points: 1024, zNotZero: zbad, worstRelative: worst };
    }
    // mul of two different points against the one-plane product of Sphere inversions
    {
      const B = A.slice(64, 64 + 1024), C = A.slice(2048, 2048 + 1024);
      const g = many(id, { op: 2 }, B, C), w = many('mercator', { op: 2 }, B, C);
      out.glsl[id + ' mul'] = { points: 1024, worstAgainstOnePlane: Math.max(...g.map((x, i) => rel(x, w[i]))) };
    }
  }
}
return JSON.stringify(out);
