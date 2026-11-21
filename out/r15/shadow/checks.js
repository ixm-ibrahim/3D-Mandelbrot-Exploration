// Round 15B, shadow: numbers for Pillow from 4D (adapted from out/r15/entry/checks.js). Runs inside the page (tools/shot.py). Returns one JSON string.
// Sections: math (points and MATH.pillow4d results, compared with out/me/r15/shadow_ref.py by compare.py),
// flat (the plane z = 0), glsl (the shader's pw, sqr and mul against MATH).
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES;
const POW = (typeof window.__p4Pow === 'number') ? window.__p4Pow : 2;
const out = { pow: POW };
const PI = Math.PI;
let seed = 20261118;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const rdir = () => { const z = rnd() * 2 - 1, a = (rnd() * 2 - 1) * PI, h = Math.sqrt(1 - z * z); return [h * Math.cos(a), h * Math.sin(a), z]; };
const f32 = v => Array.from(new Float32Array(v));

// ---------- 1. 20,000 points anywhere in a ball, and 6,000 crowded where the layout is delicate
const P = [];
for (let i = 0; i < 20000; i++) { const d = rdir(), r = 0.05 + 1.55 * Math.cbrt(rnd()); P.push([r * d[0], r * d[1], r * d[2]]); }
const Q = [];
for (let i = 0; i < 6000; i++) {
  const k = i % 6, r = 0.3 + 1.2 * rnd(), a = (rnd() * 2 - 1) * PI, e = Math.pow(10, -1 - 7 * rnd()) * (rnd() < 0.5 ? -1 : 1);
  let d;
  if (k === 0) d = [Math.cos(a), Math.sin(a), e];                                  // beside the plane z = 0
  else if (k === 1) d = [Math.cos(a) * 0.5, e, Math.sin(a)];                      // beside the plane y = 0 (the seams lie in it)
  else if (k === 2 || k === 3) {                                                   // beside a corner direction (+-1, 0, zt) or (+-1, 0, -zb)
    const b0 = 2 * PI / (POW + 1), top = rnd() < 0.5, zc = top ? (1 + Math.cos(b0)) / Math.sin(b0) : -(1 - Math.cos(b0)) / Math.sin(b0);
    d = [(k === 2 ? 1 : -1) * (1 + e), 1e-3 * (rnd() - 0.5) * Math.abs(e) * 100, zc * (1 + Math.pow(10, -1 - 7 * rnd()) * (rnd() - 0.5))];
  }
  else if (k === 4) d = [e, 1e-3 * (rnd() - 0.5), rnd() < 0.5 ? -1 : 1];           // beside a pole
  else d = rdir();
  const l = Math.hypot(d[0], d[1], d[2]);
  Q.push([r * d[0] / l, r * d[1] / l, r * d[2] / l]);
}
out.math = { P, F: P.map(v => M.pillow4d(v, POW, {})), Q, G: Q.map(v => M.pillow4d(v, POW, {})) };

// ---------- 2. the plane z = 0: the result must have z exactly 0 and be the complex power
{
  let worst = 0, zbad = 0;
  for (let i = 0; i < 4000; i++) {
    const r = 0.05 + 1.6 * rnd(), a = (rnd() * 2 - 1) * PI, v = [r * Math.cos(a), r * Math.sin(a), 0], g = M.pillow4d(v, POW, {});
    const R = Math.pow(r, POW), w = [R * Math.cos(POW * a), R * Math.sin(POW * a)];
    if (!Object.is(g[2], 0) && g[2] !== 0) zbad++;
    worst = Math.max(worst, Math.hypot(g[0] - w[0], g[1] - w[1]) / R);
  }
  out.flat = { points: 4000, zNotZero: zbad, worstRelative: worst };
}

// ---------- 3. the shader against MATH (the harness of round 14: 64 points per draw into a float texture)
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
  for (const [name, pts] of [['ball', A], ['delicate', A2]]) {
    const g = many('pillow4d', { op: 0, n: POW }, pts), e = g.map((x, i) => rel(x, M.pillow4d(pts[i], POW, {})));
    out.glsl['pw ' + name] = Object.assign(stats(e), { finite: g.every(x => x.every(Number.isFinite)) });
    if (POW === 2) {
      const g2 = many('pillow4d', { op: 1, n: 2 }, pts), e2 = g2.map((x, i) => rel(x, M.pillow4d(pts[i], 2, {})));
      out.glsl['sqr ' + name] = Object.assign(stats(e2), { finite: g2.every(x => x.every(Number.isFinite)) });
      // where the largest differences sit
      const worst = e2.map((x, i) => [x, i]).sort((a, b) => b[0] - a[0]).slice(0, 5).map(([x, i]) => ({ err: x, v: pts[i], dir: pts[i].map(c => c / Math.hypot(...pts[i])), gl: g2[i], js: M.pillow4d(pts[i], 2, {}) }));
      out.glsl['sqr ' + name + ' worst'] = worst;
    }
  }
  // the plane z = 0 in the shader: z out exactly 0, and the complex power
  {
    const F = []; for (let i = 0; i < 1024; i++) { const r = 0.05 + 1.6 * rnd(), a = (rnd() * 2 - 1) * PI; F.push(f32([r * Math.cos(a), r * Math.sin(a), 0])); }
    const g = many('pillow4d', { op: POW === 2 ? 1 : 0, n: POW }, F);
    let zbad = 0, worst = 0;
    g.forEach((x, i) => { if (x[2] !== 0) zbad++; const v = F[i], r = Math.hypot(v[0], v[1]), a = Math.atan2(v[1], v[0]), R = Math.pow(r, POW); worst = Math.max(worst, Math.hypot(x[0] - R * Math.cos(POW * a), x[1] - R * Math.sin(POW * a)) / R); });
    out.glsl.flat = { points: 1024, zNotZero: zbad, worstRelative: worst };
  }
  // mul of two different points against the one-plane product of Sphere inversions
  {
    const B = A.slice(64, 64 + 1024), C = A.slice(2048, 2048 + 1024);
    const g = many('pillow4d', { op: 2 }, B, C), w = many('mercator', { op: 2 }, B, C);
    out.glsl.mul = { points: 1024, worstAgainstOnePlane: Math.max(...g.map((x, i) => rel(x, w[i]))) };
  }
}
return JSON.stringify(out);
