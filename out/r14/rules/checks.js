// Round 14, rules: numbers behind the texts of the five new entries. Runs inside the page (tools/shot.py).
// Returns one JSON string. Sections: glsl (shader against MATH), quat4 (against plain 4D quaternion arithmetic),
// rotor, rotorframe, kleinsq, kleinsq2.
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES;
const out = {};
const PI = Math.PI, rad = d => d * PI / 180, deg = r => r * 180 / PI;
const len = a => Math.hypot(a[0], a[1], a[2]), dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
let seed = 20261118;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const rdir = () => { const z = rnd() * 2 - 1, a = (rnd() * 2 - 1) * PI, h = Math.sqrt(1 - z * z); return [h * Math.cos(a), h * Math.sin(a), z]; };
const rball = R => { const d = rdir(), r = R * Math.cbrt(rnd()); return [r * d[0], r * d[1], r * d[2]]; };
const f32 = v => Array.from(new Float32Array(v));
const keys = id => (AP.find(a => a.id === id).params || []).filter(s => s.key !== undefined).map(s => s.key);
const uAof = (id, q) => { const u = [0, 0, 0, 0]; keys(id).forEach((k, i) => { u[i] = +q[k]; }); return u; };
const defaults = id => { const o = {}; (AP.find(a => a.id === id).params || []).forEach(s => { if (s.key !== undefined) o[s.key] = s.def; }); return o; };

// ---------- a small GPU harness: 64 points per draw into a float texture
const cv = document.createElement('canvas'); cv.width = 64; cv.height = 1;
const gl = cv.getContext('webgl2');
const gpu = !!(gl && gl.getExtension('EXT_color_buffer_float'));
let run = null, prog = null;
if (gpu) {
  const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, 64, 1, 0, gl.RGBA, gl.FLOAT, null);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  const fbo = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0); gl.viewport(0, 0, 64, 1);
  const VERT = '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }';
  const HEAD = '#version 300 es\nprecision highp float;\nprecision highp int;\nuniform vec4 uA; uniform float uPow, uJulia; uniform vec3 uC;\nout vec4 o;\nconst float PI = 3.14159265358979;\n' +
    'vec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }\nfloat at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }\n';
  const MAIN = '\nuniform vec3 uP[64], uQ[64]; uniform int uOp; uniform float uN;\nvoid main(){ int i = int(gl_FragCoord.x); vec3 v = uP[i], r;\n if (uOp == 0) r = pw(v, uN); else if (uOp == 1) r = sqr(v); else if (uOp == 2) r = mul(v, uQ[i]); else if (uOp == 3) r = cmap(v);\n#ifdef APR_ZMAP\n else r = zmap(v, uC);\n#else\n else r = v;\n#endif\n o = vec4(r, 1.0); }';
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('shader: ' + gl.getShaderInfoLog(s)); return s; };
  const progs = {};
  prog = id => progs[id] || (progs[id] = (() => { const a = AP.find(x => x.id === id), p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, HEAD + a.glsl + MAIN)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; })());
  // o: { uA, op, n, julia, c }; P, Q: up to 64 points each
  run = (id, o, P, Q) => {
    const p = prog(id); gl.useProgram(p); const U = name => gl.getUniformLocation(p, name);
    gl.uniform4fv(U('uA'), o.uA || [0, 0, 0, 0]); gl.uniform1f(U('uPow'), o.n || 2); gl.uniform1f(U('uN'), o.n || 2); gl.uniform1i(U('uOp'), o.op || 0);
    gl.uniform1f(U('uJulia'), o.julia ? 1 : 0); gl.uniform3fv(U('uC'), o.c || [0, 0, 0]);
    const flat = pts => { const f = new Float32Array(192); (pts || []).forEach((v, i) => f.set(v, 3 * i)); return f; };
    gl.uniform3fv(U('uP[0]'), flat(P)); gl.uniform3fv(U('uQ[0]'), flat(Q)); gl.drawArrays(gl.TRIANGLES, 0, 3);
    const r = new Float32Array(256); gl.readPixels(0, 0, 64, 1, gl.RGBA, gl.FLOAT, r);
    return P.map((_, i) => [r[4 * i], r[4 * i + 1], r[4 * i + 2]]);
  };
}
const many = (id, o, P, Q) => { const r = []; for (let i = 0; i < P.length; i += 64) r.push(...run(id, o, P.slice(i, i + 64), Q ? Q.slice(i, i + 64) : null)); return r; };
// 64 points: 40 anywhere in a ball, 12 in the plane z = 0, 6 in the plane y = 0, 6 just beside z = 0
const batch = () => {
  const P = [];
  for (let i = 0; i < 64; i++) {
    const r = 0.2 + 1.4 * rnd(), a = (rnd() * 2 - 1) * PI, d = rdir();
    let v = [r * d[0], r * d[1], r * d[2]];
    if (i >= 40 && i < 52) v = [r * Math.cos(a), r * Math.sin(a), 0];
    else if (i >= 52 && i < 58) v = [r * Math.cos(a), 0, r * Math.sin(a)];
    else if (i >= 58) v = [r * Math.cos(a), r * Math.sin(a), (rnd() * 2 - 1) * 1e-4];
    P.push(f32(v));
  }
  return P;
};

// ---------- 1. the shader's pw, sqr and mul against MATH
if (gpu) {
  const SETS = [
    ['quat4', { w: 0.3, tilt: 20, cw: 0.4 }], ['rotor', { lon: 0, lat: 90 }], ['rotor', { lon: 0, lat: 0 }], ['rotor', { lon: 40, lat: 0 }], ['rotor', { lon: -130, lat: 35 }],
    ['rotorframe', {}], ['kleinsq', {}], ['kleinsq2', {}],
  ];
  out.glsl = [];
  for (const [id, q] of SETS) {
    const row = { id, q: JSON.stringify(q), finite: true, zleak: 0, pw: {} }, uA = uAof(id, q);
    for (const n of [2, 3, 4, 8, -1, -2, 2.5]) {
      const errs = [];
      for (let b = 0; b < 16; b++) {
        const P = batch(), G = run(id, { uA, op: 0, n }, P);
        G.forEach((g, i) => {
          const want = M[id](P[i], n, q);
          if (!g.every(Number.isFinite)) row.finite = false;
          errs.push(dist(g, want) / (1 + len(want)));
          if (P[i][2] === 0 && g[2] !== 0) row.zleak++;
        });
      }
      errs.sort((a, b) => a - b);
      row.pw['n' + n] = { median: errs[errs.length >> 1], p99: errs[Math.floor(errs.length * 0.99)], worst: errs[errs.length - 1], over2e3: errs.filter(e => !(e <= 2e-3)).length, points: errs.length };
    }
    let sq = 0, sqz = 0, mm = 0;
    for (let b = 0; b < 16; b++) {
      const P = batch(), G = run(id, { uA, op: 1 }, P), X = run(id, { uA, op: 2 }, P, P);
      G.forEach((g, i) => { const want = M[id](P[i], 2, q); sq = Math.max(sq, dist(g, want) / (1 + len(want))); if (P[i][2] === 0 && g[2] !== 0) sqz++; mm = Math.max(mm, dist(g, X[i]) / (1 + len(g))); });
    }
    row.sqrWorst = sq; row.sqrZleak = sqz; row.mulSelfVsSqr = mm;
    out.glsl.push(row);
  }
} else out.glsl = 'no float render target here';

// ---------- 2. quat4 against plain quaternion arithmetic in 4D
const qmul = (p, q) => [p[0] * q[0] - p[1] * q[1] - p[2] * q[2] - p[3] * q[3], p[0] * q[1] + p[1] * q[0] + p[2] * q[3] - p[3] * q[2],
  p[0] * q[2] - p[1] * q[3] + p[2] * q[0] + p[3] * q[1], p[0] * q[3] + p[1] * q[2] - p[2] * q[1] + p[3] * q[0]];
const E4 = (P, q) => { const t = rad(q.tilt), c = Math.cos(t), s = Math.sin(t); return [P[0] * c - q.w * s, P[1], P[2], P[0] * s + q.w * c]; };
// bounded for `its` steps (the picture's own test: a step outside radius 64 has escaped), plain 4D arithmetic; pow: 2 or 3
const stay4 = (z, c, its, pow) => { for (let k = 0; k < its; k++) { let w = qmul(z, z); if (pow === 3) w = qmul(w, z); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2], w[3] + c[3]]; if (Math.hypot(...z) > 64) return false; } return true; };
// the same in the three numbers the page uses, started from the shader's own cmap and zmap
const stay3 = (z, c, its, pow) => { for (let k = 0; k < its; k++) { z = add(M.quat4(z, pow, {}), c); if (len(z) > 64) return false; } return true; };
if (gpu) {
  out.quat4 = [];
  const CASES = [
    { mode: 'm', q: { w: 0, tilt: 0, cw: 0 } }, { mode: 'm', q: { w: 0.3, tilt: 0, cw: 0 } }, { mode: 'm', q: { w: -0.6, tilt: 0, cw: 0 } }, { mode: 'm', q: { w: 0, tilt: 30, cw: 0 } },
    { mode: 'm', q: { w: 0.2, tilt: 60, cw: 0 } }, { mode: 'm', q: { w: 0, tilt: 90, cw: 0 } }, { mode: 'm', q: { w: 0.25, tilt: -45, cw: 0 }, pow: 3 },
    { mode: 'j', q: { w: 0, tilt: 0, cw: 0 }, c: [-1, 0.15, 0.1] }, { mode: 'j', q: { w: 0, tilt: 0, cw: 0.5 }, c: [-0.2, 0.6, 0.2] }, { mode: 'j', q: { w: 0, tilt: 0, cw: 0.3 }, c: [-1, 0, 0] },
    { mode: 'j', q: { w: 0.15, tilt: 35, cw: 0.4 }, c: [-0.1226, 0.7449, 0] }, { mode: 'j', q: { w: -0.2, tilt: 70, cw: -0.3 }, c: [-0.8, 0.1, 0.1] }, { mode: 'j', q: { w: 0.1, tilt: 25, cw: 0.2 }, c: [0.1, 0.3, -0.2], pow: 3 },
    { mode: 'j', q: { w: 0.2, tilt: 40, cw: 0 }, c: [-1, 0, 0] }, { mode: 'j', q: { w: 0, tilt: 0, cw: 0.7 }, c: [-0.5, 0, 0] },
  ];
  for (const cs of CASES) {
    const N = 4096, P = [], pow = cs.pow || 2, its = 40, uA = uAof('quat4', cs.q), jul = cs.mode === 'j';
    for (let i = 0; i < N; i++) P.push(f32(rball(jul ? 1.7 : 2.1)));
    let diff = 0, in4 = 0, in3 = 0, same = 0;
    if (jul) {
      const cc = f32(cs.c), z0 = many('quat4', { uA, op: 4, julia: true, c: cc }, P), c3 = run('quat4', { uA, op: 3, julia: true, c: cc }, [cc])[0], c4 = [cc[0], cc[1], cc[2], Math.fround(cs.q.cw)];
      P.forEach((p, i) => { const a = stay4(E4(p, cs.q), c4, its, pow), b = stay3(z0[i], c3, its, pow); in4 += a; in3 += b; if (a !== b) diff++; if (dist(z0[i], p) === 0) same++; });
    } else {
      const c3 = many('quat4', { uA, op: 3, julia: false }, P);
      P.forEach((p, i) => { const a = stay4([0, 0, 0, 0], E4(p, cs.q), its, pow), b = stay3([0, 0, 0], c3[i], its, pow); in4 += a; in3 += b; if (a !== b) diff++; if (dist(c3[i], p) === 0) same++; });
    }
    out.quat4.push({ mode: cs.mode, q: JSON.stringify(cs.q), c: cs.c ? cs.c.join(',') : '', power: pow, points: N, steps: its, inside4D: in4, insidePage: in3, disagree: diff, mappedToItself: same });
  }
}
// what the 4D Mandelbrot slices are made of (plain 4D arithmetic, no page code): turn the picture point about the
// x-axis and see whether membership changes (a solid of revolution about the x-axis), and compare z = 0 with the flat set
{
  const flat = (x, y) => { let a = 0, b = 0; for (let k = 0; k < 200; k++) { [a, b] = [a * a - b * b + x, 2 * a * b + y]; if (a * a + b * b > 4096) return false; } return true; };
  out.quat4shape = [];
  for (const q of [{ w: 0, tilt: 0 }, { w: 0.3, tilt: 0 }, { w: 0, tilt: 30 }, { w: 0, tilt: 90 }, { w: 0.3, tilt: 90 }]) {
    let spin = 0, n = 0, sliceDiff = 0, sliceIn = 0, flatIn = 0, sph = 0;
    for (let i = 0; i < 20000; i++) {
      const p = rball(2.1), a = rnd() * 2 * PI, p2 = [p[0], p[1] * Math.cos(a) - p[2] * Math.sin(a), p[1] * Math.sin(a) + p[2] * Math.cos(a)];
      const d = rdir(), p3 = [len(p) * d[0], len(p) * d[1], len(p) * d[2]];
      const m1 = stay4([0, 0, 0, 0], E4(p, q), 200, 2);
      if (m1 !== stay4([0, 0, 0, 0], E4(p2, q), 200, 2)) spin++;
      if (m1 !== stay4([0, 0, 0, 0], E4(p3, q), 200, 2)) sph++;
      const x = rnd() * 3 - 2.2, y = rnd() * 2.6 - 1.3, s = stay4([0, 0, 0, 0], E4([x, y, 0], q), 200, 2), f = flat(x, y);
      sliceIn += s; flatIn += f; if (s !== f) sliceDiff++; n++;
    }
    out.quat4shape.push({ q: JSON.stringify(q), points: n, changedByTurnAboutX: spin, changedByAnyTurnAboutOrigin: sph, sliceZ0Inside: sliceIn, flatInside: flatIn, sliceZ0DiffersFromFlat: sliceDiff });
  }
}

// ---------- 3. rotor
{
  const R = {};
  // (a) reference along the x-axis: the Lathe itself
  let worst = 0, exact = 0, n = 0;
  for (let i = 0; i < 4000; i++) for (const pw of [2, 3, -1, 2.5]) { const v = rball(1.6), a = M.rotor(v, pw, { lon: 0, lat: 0 }), b = M.lathe(v, pw, { spin: 1 }); const e = dist(a, b) / (1 + len(b)); worst = Math.max(worst, e); if (e === 0) exact++; n++; }
  R.axisX_vs_lathe = { points: n, worst, identical: exact };
  // (b) any other axis: turn . Lathe . turn back, with T a turn that carries the x-axis onto the reference axis
  const turnTo = (lon, lat) => { const cl = Math.cos(rad(lon)), sl = Math.sin(rad(lon)), cb = Math.cos(rad(lat)), sb = Math.sin(rad(lat));
    const T = v => { const x = v[0] * cb - v[2] * sb, z = v[0] * sb + v[2] * cb; return [x * cl - v[1] * sl, x * sl + v[1] * cl, z]; };
    const Ti = v => { const x = v[0] * cl + v[1] * sl, y = -v[0] * sl + v[1] * cl; return [x * cb + v[2] * sb, y, -x * sb + v[2] * cb]; };
    return [T, Ti]; };
  R.conjugate = [];
  for (const [lon, lat] of [[0, 90], [40, 0], [-130, 35], [75, -60], [180, 0]]) {
    const [T, Ti] = turnTo(lon, lat); let w = 0;
    for (let i = 0; i < 3000; i++) for (const pw of [2, 3, -2, 2.5]) { const v = rball(1.6), a = M.rotor(v, pw, { lon, lat }), b = T(M.lathe(Ti(v), pw, { spin: 1 })); w = Math.max(w, dist(a, b) / (1 + len(b))); }
    // the sets: is a point in the rotor's Mandelbrot solid exactly when its turned-back copy is in the Lathe's?
    let diff = 0, inside = 0;
    for (let i = 0; i < 4000; i++) {
      const c = rball(2), c2 = Ti(c); let z = [0, 0, 0], z2 = [0, 0, 0], a = true, b = true;
      for (let k = 0; k < 60; k++) { if (a) { z = add(M.rotor(z, 2, { lon, lat }), c); if (len(z) > 64) a = false; } if (b) { z2 = add(M.lathe(z2, 2, { spin: 1 }), c2); if (len(z2) > 64) b = false; } }
      inside += a; if (a !== b) diff++;
    }
    R.conjugate.push({ lon, lat, worstRule: w, solidPoints: 4000, solidInside: inside, solidDisagree: diff });
  }
  // (c) the plane z = 0: where does it go, and is the slice of the Mandelbrot solid the flat set?
  const flat = (x, y) => { let a = 0, b = 0; for (let k = 0; k < 200; k++) { [a, b] = [a * a - b * b + x, 2 * a * b + y]; if (a * a + b * b > 4096) return false; } return true; };
  R.plane = [];
  for (const [lon, lat] of [[0, 0], [40, 0], [0, 90], [0, 30]]) {
    let zmax = 0, cplx = 0, turned = 0, sd = 0, sdT = 0, sIn = 0, fIn = 0;
    const tl = rad(lon), ct = Math.cos(tl), st = Math.sin(tl);
    for (let i = 0; i < 4000; i++) {
      const a = (rnd() * 2 - 1) * PI, r = 0.2 + 1.4 * rnd(), v = [r * Math.cos(a), r * Math.sin(a), 0], w = M.rotor(v, 2, { lon, lat });
      zmax = Math.max(zmax, Math.abs(w[2]) / (r * r));
      cplx = Math.max(cplx, dist(w, [r * r * Math.cos(2 * a), r * r * Math.sin(2 * a), 0]) / (r * r));
      turned = Math.max(turned, dist(w, [r * r * Math.cos(2 * a - tl), r * r * Math.sin(2 * a - tl), 0]) / (r * r));
      const x = rnd() * 4 - 2, y = rnd() * 4 - 2; let z = [0, 0, 0], inS = true;
      for (let k = 0; k < 200 && inS; k++) { z = add(M.rotor(z, 2, { lon, lat }), [x, y, 0]); if (len(z) > 64) inS = false; }
      const f = flat(x, y), fT = flat(x * ct + y * st, -x * st + y * ct);
      sIn += inS; fIn += f; if (inS !== f) sd++; if (inS !== fT) sdT++;
    }
    R.plane.push({ lon, lat, leavesPlaneBy: zmax, offComplexSquare: cplx, offSquareTurnedByMinusLon: turned, slicePoints: 4000, sliceInside: sIn, flatInside: fIn, sliceDiffersFromFlat: sd, sliceDiffersFromFlatTurnedByLon: sdT });
  }
  // (d) "Quaternion square, twisted" = this rule with the axis at longitude -tilt in the flat plane, then a turn back by n * tilt
  let tw = 0;
  for (let i = 0; i < 3000; i++) for (const pw of [2, 3]) for (const tilt of [40, -75, 120]) {
    const v = rball(1.6), a = M.tilt(v, pw, { tilt }), b = M.rotor(v, pw, { lon: -tilt, lat: 0 }), t = rad(-(pw - 1) * tilt), c = [Math.cos(t) * b[0] - Math.sin(t) * b[1], Math.sin(t) * b[0] + Math.cos(t) * b[1], b[2]];
    tw = Math.max(tw, dist(a, c) / (1 + len(a)));
  }
  R.twisted_is_rotor_then_turn_by_minus_n_minus_1_tilt = tw;
  out.rotor = R;
}

// ---------- 4. rotor square with a frame
{
  const R = {}, F = (v, n) => M.rotorframe(v, n, {});
  let pz = 0, pzLeak = 0, yPos = 0, yNeg = 0, yNegOnAxis = 0, lens = 0;
  for (let i = 0; i < 6000; i++) for (const n of [2, 3, 4]) {
    const a = (rnd() * 2 - 1) * PI, r = 0.2 + 1.4 * rnd(), v = [r * Math.cos(a), r * Math.sin(a), 0], w = F(v, n), R_ = Math.pow(r, n);
    pz = Math.max(pz, dist(w, [R_ * Math.cos(n * a), R_ * Math.sin(n * a), 0]) / R_); if (w[2] !== 0) pzLeak++;
    const b = (rnd() - 0.5) * PI, u = [r * Math.cos(b), 0, r * Math.sin(b)], wu = F(u, n);          // the half x > 0 of the plane y = 0, latitude b
    yPos = Math.max(yPos, dist(wu, [R_ * Math.cos(n * b), 0, R_ * Math.sin(n * b)]) / R_);
    const un = [-r * Math.cos(b), 0, r * Math.sin(b)], wn = F(un, n), g = PI - b;                   // the half x < 0: angle g from the x-axis inside the plane
    yNeg = Math.max(yNeg, dist(wn, [R_ * Math.cos(n * g), 0, R_ * Math.sin(n * g)]) / R_);
    if (n === 2) yNegOnAxis = Math.max(yNegOnAxis, dist(wn, [R_, 0, 0]) / R_);
    const q = rball(1.6), wq = F(q, n); lens = Math.max(lens, Math.abs(len(wq) - Math.pow(len(q), n)) / Math.pow(len(q), n));
  }
  R.planeZ0_offComplexPower = pz; R.planeZ0_leaks = pzLeak; R.halfPlaneY0_xPositive_offComplexPower = yPos; R.halfPlaneY0_xNegative_offComplexPower = yNeg;
  R.halfPlaneY0_xNegative_offPositiveXAxis_n2 = yNegOnAxis; R.lengthOff = lens;
  // the tear at the z-axis: directions 0.001 degree from the pole, all round it, at n = 2: how far apart do they land (in degrees)?
  const spread = n => { const e = rad(0.001), pts = []; for (let k = 0; k < 360; k++) { const a = rad(k), w = F([Math.sin(e) * Math.cos(a), Math.sin(e) * Math.sin(a), Math.cos(e)], n); pts.push(w); }
    let m = 0; for (const p of pts) for (const q of pts) m = Math.max(m, deg(Math.acos(Math.max(-1, Math.min(1, p[0] * q[0] + p[1] * q[1] + p[2] * q[2]))))); return m; };
  R.poleSpreadDeg = { n2: spread(2), n3: spread(3), n4: spread(4) };
  R.poleLandsAt_n2 = [0, 90, 180, 270].map(k => F([Math.sin(rad(0.001)) * Math.cos(rad(k)), Math.sin(rad(0.001)) * Math.sin(rad(k)), Math.cos(rad(0.001))], 2).map(x => +x.toFixed(4)));
  // continuity across the half-plane y = 0, x < 0 (whole powers), and the jump there at a power that is not whole
  const across = n => { let m = 0; for (let i = 0; i < 4000; i++) { const b = (rnd() - 0.5) * PI * 0.98, r = 0.3 + rnd(), e = 1e-7, x = -r * Math.cos(b), z = r * Math.sin(b); m = Math.max(m, dist(F([x, e, z], n), F([x, -e, z], n)) / Math.pow(r, n)); } return m; };
  R.jumpAcrossHalfPlaneY0xNeg = { n2: across(2), n3: across(3), n4: across(4), n2p5: across(2.5) };
  // how the rule differs from the Lathe and from the Mandelbulb (largest and mean angle between the answers, n = 2)
  let dl = 0, db = 0, sl = 0, sb = 0, cnt = 0, fold = 0;
  for (let i = 0; i < 20000; i++) {
    const d = rdir(), w = F(d, 2), l = M.lathe(d, 2, { spin: 1 }), b = M.bulb(d, 2, { lat: 0, lon: 0 });
    const ang = (p, q) => deg(Math.acos(Math.max(-1, Math.min(1, p[0] * q[0] + p[1] * q[1] + p[2] * q[2]))));
    const a1 = ang(w, l), a2 = ang(w, b); dl = Math.max(dl, a1); db = Math.max(db, a2); sl += a1; sb += a2; cnt++;
    // orientation of the map on the sphere of directions: det [w, dw/du, dw/dv] for two small steps square to d
    const u = (() => { const t = Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0], c = [d[1] * t[2] - d[2] * t[1], d[2] * t[0] - d[0] * t[2], d[0] * t[1] - d[1] * t[0]], l = len(c); return [c[0] / l, c[1] / l, c[2] / l]; })();
    const v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]], h = 1e-5;
    const nrm = p => { const l = len(p); return [p[0] / l, p[1] / l, p[2] / l]; };
    const wu = F(nrm([d[0] + h * u[0], d[1] + h * u[1], d[2] + h * u[2]]), 2), wv = F(nrm([d[0] + h * v[0], d[1] + h * v[1], d[2] + h * v[2]]), 2);
    const A = [wu[0] - w[0], wu[1] - w[1], wu[2] - w[2]], B = [wv[0] - w[0], wv[1] - w[1], wv[2] - w[2]];
    const det = w[0] * (A[1] * B[2] - A[2] * B[1]) - w[1] * (A[0] * B[2] - A[2] * B[0]) + w[2] * (A[0] * B[1] - A[1] * B[0]);
    if (det < 0) fold++;
  }
  R.vsLatheDeg = { largest: dl, mean: sl / cnt }; R.vsMandelbulbDeg = { largest: db, mean: sb / cnt }; R.directionsTurnedOver_n2 = { of: cnt, count: fold };
  out.rotorframe = R;
}

// ---------- 5. Kleinian squaring
{
  const R = {}, H = (d, n) => M.kleinsq(d, n, {}), ang = (p, q) => deg(Math.acos(Math.max(-1, Math.min(1, (p[0] * q[0] + p[1] * q[1] + p[2] * q[2]) / (len(p) * len(q))))));
  R.equator = {};
  for (const n of [2, 3, 4, 8]) {
    let worst = 0, at = 0, sum = 0, cnt = 0, zl = 0; const agree = [];
    for (let k = 0; k < 36000; k++) {
      const t = rad(k / 100), w = H([Math.cos(t), Math.sin(t), 0], n), e = ang(w, [Math.cos(n * t), Math.sin(n * t), 0]);
      if (w[2] !== 0) zl++;
      if (e > worst) { worst = e; at = k / 100; }
      sum += e; cnt++;
      if (e < 1e-6) agree.push(k / 100);
    }
    R.equator['n' + n] = { largestDiffDeg: worst, atLongitude: at, meanDiffDeg: sum / cnt, leavesPlane: zl, agreesAtLongitudes: agree.filter((x, i) => i === 0 || x - agree[i - 1] > 0.5) };
  }
  // the spheres of n = 2 as the paper gives them
  R.spheres_n2 = [0, 1, 2].map(k => { const psi = PI / 3, t = (2 * k + 1) * psi; return { centre: [Math.cos(t) / Math.cos(psi), Math.sin(t) / Math.cos(psi), 0].map(x => +x.toFixed(4)), radius: +Math.tan(psi).toFixed(4) }; });
  // continuity over the whole sphere (largest step of H between directions 1e-6 apart), length, and keeping of shapes
  const kq = (n, two) => {
    const F = (d, m) => (two ? M.kleinsq2(d, m, {}) : M.kleinsq(d, m, {}));
    let jump = 0, lenOff = 0, round = 0, flipped = 0, cnt = 0, capIn = 0;
    for (let i = 0; i < 40000; i++) {
      const d = rdir(), w = F(d, n);
      lenOff = Math.max(lenOff, Math.abs(len(w) - 1));
      const t = Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0], c = [d[1] * t[2] - d[2] * t[1], d[2] * t[0] - d[0] * t[2], d[0] * t[1] - d[1] * t[0]], lc = len(c), u = [c[0] / lc, c[1] / lc, c[2] / lc];
      const v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]], h = 1e-6;
      const nrm = p => { const l = len(p); return [p[0] / l, p[1] / l, p[2] / l]; };
      const wu = F(nrm([d[0] + h * u[0], d[1] + h * u[1], d[2] + h * u[2]]), n), wv = F(nrm([d[0] + h * v[0], d[1] + h * v[1], d[2] + h * v[2]]), n);
      const A = [wu[0] - w[0], wu[1] - w[1], wu[2] - w[2]], B = [wv[0] - w[0], wv[1] - w[1], wv[2] - w[2]], la = len(A), lb = len(B);
      jump = Math.max(jump, la / h, lb / h);
      if (la / h < 50 && lb / h < 50) { round = Math.max(round, Math.abs(la / lb - 1), Math.abs((A[0] * B[0] + A[1] * B[1] + A[2] * B[2]) / (la * lb))); }
      const det = w[0] * (A[1] * B[2] - A[2] * B[1]) - w[1] * (A[0] * B[2] - A[2] * B[0]) + w[2] * (A[0] * B[1] - A[1] * B[0]);
      if (det < 0) flipped++; cnt++;
      if (dist(w, [d[0], -d[1], d[2]]) > 1e-9 && dist(w, [d[0], d[1], -d[2]]) > 1e-9) capIn++;
    }
    return { directions: cnt, largestStretch: jump, lengthOff: lenOff, shapeOff: round, mirroredShare: flipped / cnt, insideSomeCapShare: capIn / cnt };
  };
  R.sphere = { n2: kq(2, false), n3: kq(3, false), n4: kq(4, false) };
  R.sphereTwoPlanes = { n2: kq(2, true) };
  // two planes: the jump across the planes |y| = |z| (largest angle between the two families' answers there), n = 2
  let j = 0, js = 0, jc = 0, yz = 0, y0 = 0;
  for (let i = 0; i < 20000; i++) {
    const a = (rnd() * 2 - 1) * PI, b = rnd() * PI, s = rnd() < 0.5 ? 1 : -1, d = [Math.cos(b), Math.sin(b) * Math.SQRT1_2, s * Math.sin(b) * Math.SQRT1_2];
    const one = M.kleinsq(d, 2, {}), sw = M.kleinsq([d[0], d[2], d[1]], 2, {}), two = [sw[0], sw[2], sw[1]], e = ang(one, two);
    j = Math.max(j, e); js += e; jc++;
    // the plane y = 0 under the two-planes rule: does it follow the one-plane rule's equator pattern (z in place of y)?
    const p = [Math.cos(a), 0, Math.sin(a)], w2 = M.kleinsq2(p, 2, {}), w1 = M.kleinsq([p[0], p[2], 0], 2, {});
    y0 = Math.max(y0, dist(w2, [w1[0], 0, w1[1]]));
    const p0 = [Math.cos(a), Math.sin(a), 0], v2 = M.kleinsq2(p0, 2, {}), v1 = M.kleinsq(p0, 2, {});
    yz = Math.max(yz, dist(v2, v1));
  }
  R.twoPlanes = { jumpAcrossSeamDeg: { largest: j, mean: js / jc }, planeZ0_sameAsOnePlane: yz, planeY0_sameAsOnePlaneWithYZSwapped: y0 };
  // the slice at z = 0 of the Mandelbrot solid against the flat set (n = 2), and the Julia set for c = -1 on the x-axis
  const flat = (x, y) => { let a = 0, b = 0; for (let k = 0; k < 200; k++) { [a, b] = [a * a - b * b + x, 2 * a * b + y]; if (a * a + b * b > 4096) return false; } return true; };
  let sIn = 0, fIn = 0, both = 0, n = 0;
  for (let i = 0; i < 40000; i++) {
    const x = rnd() * 3.2 - 2.2, y = rnd() * 2.8 - 1.4; let z = [0, 0, 0], inS = true;
    for (let k = 0; k < 200 && inS; k++) { z = add(M.kleinsq(z, 2, {}), [x, y, 0]); if (len(z) > 64) inS = false; }
    const f = flat(x, y); sIn += inS; fIn += f; both += inS && f; n++;
  }
  R.sliceZ0_mandelbrot = { points: n, inSlice: sIn, inFlat: fIn, inBoth: both, areaSlice: sIn / n * 3.2 * 2.8, areaFlat: fIn / n * 3.2 * 2.8 };
  // on the x-axis the rule is x -> x^2 exactly (both directions of the axis are fixed points or go to +x)?
  R.xAxis = [1, -1, 0.5, -0.7].map(x => M.kleinsq([x, 0, 0], 2, {}).map(v => +v.toFixed(6)));
  out.kleinsq = R;
}
return JSON.stringify(out, null, 1);
