// Round 12, tried rules: the shader code of the three new entries against their MATH mirrors.
// Runs inside the page (tools/shot.py) on a small WebGL 2 context of its own. Returns one JSON string.
// The harness (64 points per draw into a float texture) follows out/lab2/softfold/checks.js, section 3.
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES;
const cv = document.createElement('canvas'); cv.width = 64; cv.height = 1;
const gl = cv.getContext('webgl2');
if (!gl || !gl.getExtension('EXT_color_buffer_float')) return JSON.stringify({ skipped: 'no float render target here' });
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
const prog = id => { const a = AP.find(x => x.id === id), p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, HEAD + a.glsl + MAIN)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; };
const run = (p, uA, op, n, P, Q) => {
  gl.useProgram(p); const U = name => gl.getUniformLocation(p, name);
  gl.uniform4fv(U('uA'), uA); gl.uniform1f(U('uPow'), n); gl.uniform1f(U('uN'), n); gl.uniform1i(U('uOp'), op);
  const flat = pts => { const f = new Float32Array(192); (pts || []).forEach((v, i) => f.set(v, 3 * i)); return f; };
  gl.uniform3fv(U('uP[0]'), flat(P)); gl.uniform3fv(U('uQ[0]'), flat(Q)); gl.drawArrays(gl.TRIANGLES, 0, 3);
  const o = new Float32Array(256); gl.readPixels(0, 0, 64, 1, gl.RGBA, gl.FLOAT, o);
  return P.map((_, i) => [o[4 * i], o[4 * i + 1], o[4 * i + 2]]);
};
let seed = 2024;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const f32 = v => Array.from(new Float32Array(v));
// 64 points: 40 anywhere in a ball of radius up to 1.6, 12 in the plane z = 0, 6 in the plane y = 0, 6 just beside z = 0
const batch = () => {
  const P = [];
  for (let i = 0; i < 64; i++) {
    const r = 0.2 + 1.4 * rnd(), a = (rnd() * 2 - 1) * Math.PI, z = rnd() * 2 - 1, h = Math.sqrt(1 - z * z);
    let v = [r * h * Math.cos(a), r * h * Math.sin(a), r * z];
    if (i >= 40 && i < 52) v = [r * Math.cos(a), r * Math.sin(a), 0];
    else if (i >= 52 && i < 58) v = [r * Math.cos(a), 0, r * Math.sin(a)];
    else if (i >= 58) v = [r * Math.cos(a), r * Math.sin(a), (rnd() * 2 - 1) * 1e-4];
    P.push(f32(v));
  }
  return P;
};
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]), len = a => Math.hypot(a[0], a[1], a[2]);
const keys = id => (AP.find(a => a.id === id).params || []).filter(s => s.key !== undefined).map(s => s.key);
const SETS = [
  ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, [2, 3, 8, -1, -2]],
  ['softfold', { planes: 3, blend: 0.25, curve: 1, mix: 0 }, [2, 3, 8, -1, -2]],
  ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 1 }, [2, 3, 8, -1, -2]],
  ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 2 }, [2, 3, 8, -1, -2]],
  ['softfold', { planes: 4, blend: 0.1, curve: 0, mix: 2 }, [2, 3, 8, -1, -2]],
  ['axisbulb', { k: 1, wob: 0.2, reach: 45, pinch: 0 }, [2, 3, 8, -1, -2]],
  ['axisbulb', { k: 5, wob: 0, reach: 45, pinch: 0 }, [2, 3, 8, -1, -2]],
  ['axisbulb', { k: -3, wob: 0.2, reach: 45, pinch: 0 }, [2, 3, 8, -1, -2]],
  ['axisbulb', { k: 1, wob: 0, reach: 45, pinch: 1.5 }, [2, 3, 8, -1, -2]],
  ['pillow', { layout: 0 }, [2, 3, 4, 8, -1, -2]],
  ['pillow', { layout: 1 }, [2, 4, 8, 1, 3]],
];
const progs = {}, rows = [];
for (const [id, q, powers] of SETS) {
  const p = progs[id] || (progs[id] = prog(id)), uA = [0, 0, 0, 0];
  keys(id).forEach((k, i) => { uA[i] = +q[k]; });
  const row = { id, q: JSON.stringify(q), pw: {}, zleak: 0, finite: true };
  for (const n of powers) {
    const errs = [];
    for (let b = 0; b < 20; b++) {
      const P = batch(), G = run(p, uA, 0, n, P);
      G.forEach((g, i) => {
        const want = M[id](P[i], n, q);
        if (!g.every(Number.isFinite)) row.finite = false;
        errs.push(dist(g, want) / (1 + len(want)));
        if (P[i][2] === 0 && g[2] !== 0) row.zleak++;
      });
    }
    errs.sort((a, b) => a - b);
    row.pw['n' + n] = { median: errs[errs.length >> 1], p999: errs[Math.floor(errs.length * 0.999)], worst: errs[errs.length - 1], over2e3: errs.filter(e => !(e <= 2e-3)).length, points: errs.length };
  }
  // sqr against the JavaScript square, and cmap against the identity
  let sq = 0, cm = 0;
  for (let b = 0; b < 10; b++) {
    const P = batch();
    run(p, uA, 1, 2, P).forEach((g, i) => { const want = M[id](P[i], 2, q); sq = Math.max(sq, dist(g, want) / (1 + len(want))); if (P[i][2] === 0 && g[2] !== 0) row.zleak++; });
    run(p, uA, 3, 2, P).forEach((g, i) => { cm = Math.max(cm, dist(g, P[i])); });
  }
  row.sqr = sq; row.cmap = cm;
  // mul of two different points: the one-plane product for Blended planes and Pillow, the quaternion product then the turn for Bulbs
  if (id !== 'axisbulb') {
    const mer = progs.mercator || (progs.mercator = prog('mercator'));
    let mm = 0;
    for (let b = 0; b < 5; b++) { const P = batch(), Q = batch(), a = run(p, uA, 2, 2, P, Q), c = run(mer, [0, 0, 0, 0], 2, 2, P, Q); a.forEach((g, i) => { mm = Math.max(mm, dist(g, c[i])); }); }
    row.mulAgainstOnePlane = mm;
  }
  // finite at the origin, on the axes and far out
  const edge = [[0, 0, 0], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], [1e18, 0, 0], [0, 1e18, 0], [0, 0, 1e18], [-2, 0, 1e-30], [1e-20, 0, 0]].map(f32);
  for (const n of powers) for (const g of run(p, uA, 0, n, edge)) if (!g.every(Number.isFinite)) { row.finite = false; row.notFinite = 'pw n=' + n + ' -> ' + g; }
  rows.push(row);
}
return JSON.stringify({ renderer: (gl.getExtension('WEBGL_debug_renderer_info') ? gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)), rows }, null, 1);
