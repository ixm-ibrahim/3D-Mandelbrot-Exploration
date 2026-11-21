// Numeric checks of the pillow rule, run inside the built page (python out/proto/radial/run_checks.py).
// Everything here calls the page's own MATH.pillow; Phi and PhiInv are also rebuilt from the assignment's
// wording (Cartesian sheet, lattice coordinates (a, b), split along fa = fb) as an independent reference.
const L = window.squaringLab, F = (v, n) => L.MATH.pillow(v, n, {});
const A = L.APPROACHES.find(a => a.id === 'pillow'), lay = A.parts.layout, inv = A.parts.inverse;
const out = [], say = s => out.push(s);
let seed = 12345;
const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const gauss = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
const len = v => Math.hypot(v[0], v[1], v[2]), unit = v => { const l = len(v); return [v[0] / l, v[1] / l, v[2] / l]; };
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const rdir = () => unit([gauss(), gauss(), gauss()]);
const pct = (sorted, p) => sorted[Math.min(sorted.length - 1, Math.floor(p / 100 * sorted.length))];
const R3 = Math.sqrt(3), DEG = Math.PI / 180;

// ---- reference Phi and PhiInv, written from the task text
function phiRef(u) {
  const b = u[1] * 2 / R3, a = u[0] + u[1] / R3, i = Math.floor(a), j = Math.floor(b), fa = a - i, fb = b - j;
  const col = k => ((k % 3) + 3) % 3, w = [0, 0, 0];
  let top;
  if (fa >= fb) { w[col(i + j)] = 1 - fa; w[col(i + j + 1)] = fa - fb; w[col(i + j + 2)] = fb; top = false; }      // points up: a bottom triangle
  else { w[col(i + j)] = 1 - fb; w[col(i + j + 2)] = fa; w[col(i + j + 1)] = fb - fa; top = true; }               // points down: a top triangle
  const d = lay(w);
  return { d: [d[0], d[1], top ? d[2] : -d[2]], w, top };
}
function phiInvRef(d) {
  const l = inv(d[0], d[1], Math.abs(d[2]));
  return { u: d[2] >= 0 ? [l[1] + 0.5 * l[2], -0.5 * R3 * l[2]] : [l[1] + 0.5 * l[2], 0.5 * R3 * l[2]], w: l, top: d[2] >= 0 };
}
function Fref(v, n) { const r = len(v), q = phiInvRef([v[0] / r, v[1] / r, v[2] / r]).u, d = phiRef([n * q[0], n * q[1]]).d, R = Math.pow(r, n); return [R * d[0], R * d[1], R * d[2]]; }

// ---- 1. exactness on z = 0
function cpow(x, y, n) {     // complex power by repeated multiplication (no angles involved)
  let a = 1, b = 0;
  for (let k = 0; k < Math.abs(n); k++) [a, b] = [a * x - b * y, a * y + b * x];
  if (n < 0) { const m = a * a + b * b; a = a / m; b = -b / m; }
  return [a, b];
}
const planePts = [];
for (let k = 0; k < 500; k++) {
  let th = 2 * Math.PI * rnd(), r = 0.05 + 2 * rnd();
  if (k < 160) th = [0, 120, 180, 240, 60, 300, 360, -120][k % 8] * DEG + (k < 16 ? 0 : (rnd() - 0.5) * Math.pow(10, -1 - 13 * rnd()));   // on and beside the special angles
  if (k >= 160 && k < 220) r = Math.pow(10, -1 - 4 * rnd());                                            // near the origin (down to 1e-5: closer in, a negative power passes the cap of 1.7e18 the lab puts on every length)
  planePts.push([r * Math.cos(th), r * Math.sin(th), 0]);
}
say('1. Exactness on z = 0 (500 points; worst relative error |F - z^n| / |z^n|, and worst |F.z| / |z^n|)');
for (const n of [2, 3, 4, 5, 8, -1, -2, -3]) {
  let worst = 0, worstZ = 0, at = null;
  for (const v of planePts) {
    const g = F(v, n), [a, b] = cpow(v[0], v[1], n), m = Math.hypot(a, b), e = Math.hypot(g[0] - a, g[1] - b, g[2]) / m;
    if (e > worst) { worst = e; at = v; }
    worstZ = Math.max(worstZ, Math.abs(g[2]) / m);
  }
  say(`   n = ${n}: ${worst.toExponential(2)}  (z part ${worstZ.toExponential(1)})  ${worst < 1e-6 ? 'ok' : 'FAIL at ' + at}`);
}

// ---- 2. continuity
function pairs(N) {
  const P = [], h = 1e-5;
  const push = (a, b) => P.push([unit(a), unit(b)]);
  for (let k = 0; k < N; k++) { const d = rdir(), e = unit([gauss(), gauss(), gauss()]); push(d, [d[0] + h * e[0], d[1] + h * e[1], d[2] + h * e[2]]); }
  const extra = { equator: 0, meridians: 0, poles: 0, corners: 0, midedges: 0 };
  for (let k = 0; k < 20000; k++) {       // straddling the equator, straight across and obliquely
    const a = 2 * Math.PI * rnd(), s = (rnd() - 0.5) * h, z = h * (0.05 + 0.45 * rnd());
    push([Math.cos(a), Math.sin(a), z], [Math.cos(a + s), Math.sin(a + s), -z * rnd()]); extra.equator++;
  }
  for (let k = 0; k < 20000; k++) {       // straddling the meridians through the corner directions (and their far sides)
    const a0 = (k % 6) * 60 * DEG, lat = (rnd() - 0.5) * Math.PI, da = 0.5 * h * rnd() / Math.max(Math.cos(lat), 1e-3), dl = (rnd() - 0.5) * h;
    push([Math.cos(lat) * Math.cos(a0 + da), Math.cos(lat) * Math.sin(a0 + da), Math.sin(lat)], [Math.cos(lat + dl) * Math.cos(a0 - da), Math.cos(lat + dl) * Math.sin(a0 - da), Math.sin(lat + dl)]); extra.meridians++;
  }
  const around = (c, count, key) => {     // pairs within a few h of a special direction, on every side of it
    for (let k = 0; k < count; k++) {
      const sc = h * Math.pow(10, -3 * rnd() * (k % 2)), o1 = [gauss() * sc, gauss() * sc, gauss() * sc], o2 = [gauss() * sc, gauss() * sc, gauss() * sc];
      push([c[0] + o1[0], c[1] + o1[1], c[2] + o1[2]], k % 5 === 0 ? c : [c[0] + o2[0], c[1] + o2[1], c[2] + o2[2]]); extra[key]++;
    }
  };
  around([0, 0, 1], 5000, 'poles'); around([0, 0, -1], 5000, 'poles');
  for (const a of [0, 120, 240]) around([Math.cos(a * DEG), Math.sin(a * DEG), 0], 4000, 'corners');
  for (const a of [60, 180, 300]) around([Math.cos(a * DEG), Math.sin(a * DEG), 0], 4000, 'midedges');
  return { P, extra };
}
const { P: PAIRS, extra } = pairs(200000);
say(`2. Continuity: ${PAIRS.length} pairs of unit directions about 1e-5 apart (200000 random, plus ${JSON.stringify(extra)}); ratio |F(d1) - F(d2)| / |d1 - d2|`);
for (const n of [2, 3, -2]) {
  const ratios = new Float64Array(PAIRS.length); let max = 0, at = null, maxRef = 0;
  PAIRS.forEach(([a, b], k) => {
    const q = dist(a, b); if (!(q > 1e-12)) { ratios[k] = 0; return; }
    const r = dist(F(a, n), F(b, n)) / q; ratios[k] = r;
    if (r > max) { max = r; at = a; }
    if (k % 20 === 0) maxRef = Math.max(maxRef, dist(F(a, n), Fref(a, n)));
  });
  const first = Array.from(ratios.subarray(0, 200000)).sort((x, y) => x - y), rest = Array.from(ratios.subarray(200000)).sort((x, y) => x - y);
  say(`   n = ${n}: max ${max.toFixed(2)} (at lon ${(Math.atan2(at[1], at[0]) / DEG).toFixed(2)}°, lat ${(Math.asin(at[2]) / DEG).toFixed(2)}°), 99.9th percentile of the random pairs ${pct(first, 99.9).toFixed(2)}, median ${pct(first, 50).toFixed(2)}; special pairs: max ${rest[rest.length - 1].toFixed(2)}, 99.9th ${pct(rest, 99.9).toFixed(2)}  ${max < 1000 ? 'bounded' : 'JUMP'}; rule against the reference built from the task text: ${maxRef.toExponential(1)}`);
}

// ---- 3. round trips
{
  let e1 = 0, e2 = 0, e3 = 0, bad = 0;
  for (let k = 0; k < 20000; k++) {
    const d = k < 6 ? [[0, 0, 1], [0, 0, -1], [1, 0, 0], [-0.5, R3 / 2, 0], [-0.5, -R3 / 2, 0], [-1, 0, 0]][k] : rdir();
    const p = phiInvRef(d), q = phiRef(p.u);
    e1 = Math.max(e1, dist(q.d, d));
    const u = [12 * (rnd() - 0.5), 12 * (rnd() - 0.5)], a = phiRef(u), b = phiInvRef(a.d);
    if (a.top !== b.top) bad++;
    e2 = Math.max(e2, Math.max(Math.abs(a.w[0] - b.w[0]), Math.abs(a.w[1] - b.w[1]), Math.abs(a.w[2] - b.w[2])));
    e3 = Math.max(e3, dist(phiRef(b.u).d, a.d));
  }
  say(`3. Round trips over 20000 samples: |Phi(PhiInv(d)) - d| max ${e1.toExponential(1)}; PhiInv(Phi(u)) against u: weights differ by at most ${e2.toExponential(1)}, wrong triangle type ${bad} times; Phi of that copy against Phi(u): ${e3.toExponential(1)}  ${e1 < 1e-6 && e2 < 1e-6 && !bad ? 'ok' : 'FAIL'}`);
}

// ---- 4. shader against JavaScript
{
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 1;
  const gl = cv.getContext('webgl2');
  if (!gl || !gl.getExtension('EXT_color_buffer_float')) say('4. GLSL against JavaScript: SKIPPED, no float render target here');
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
    const pil = prog('pillow'), mer = prog('mercator'), f32 = v => Array.from(new Float32Array(v));
    let worst = 0, where = '', worstSq = 0, worstMul = 0, worstMer = 0, planeZ = 0, finite = true, count = 0, big = 0, bigList = [];
    for (let batch = 0; batch < 40; batch++) {
      const P = [], Q = [];
      for (let i = 0; i < 64; i++) { P.push(f32([3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6, i < 12 ? 0 : (i < 24 ? 0.02 : 3.2) * (rnd() - 0.5)])); Q.push(f32([3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6, 3.2 * rnd() - 1.6])); }
      for (const n of [2, 3, 4, 5, 8, -1, -2, -3]) {
        run(pil, [0, 0, 0, 0], 0, n, P).forEach((g, i) => {
          const want = F(P[i], n), e = dist(g, want) / (1 + len(want)); count++;
          if (!g.every(Number.isFinite)) finite = false;
          if (e > 2e-3) { big++; if (bigList.length < 4) bigList.push(`n=${n} v=${P[i].map(x => x.toFixed(4))} glsl=${g.map(x => x.toFixed(4))} js=${want.map(x => x.toFixed(4))}`); }
          if (e > worst) { worst = e; where = `n=${n} v=${P[i].map(x => x.toFixed(4))}`; }
          if (i < 12) planeZ = Math.max(planeZ, Math.abs(g[2]));
        });
      }
      const two = P.map(v => F(v, 2));
      run(pil, [0, 0, 0, 0], 1, 2, P).forEach((g, i) => { worstSq = Math.max(worstSq, dist(g, two[i]) / (1 + len(two[i]))); });
      const a = run(pil, [0, 0, 0, 0], 2, 2, P, Q), b = run(mer, [1, 0, 0, 0], 2, 2, P, Q);
      a.forEach((g, i) => { worstMul = Math.max(worstMul, dist(g, b[i]) / (1 + len(b[i]))); if (!g.every(Number.isFinite)) finite = false; });
    }
    const edge = [[0, 0, 0], [1e-12, 0, 0], [0, 0, 1e-9], [0, 1e-25, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -2], [0, 3, 0], [50, -40, 30], [64, 0, 0], [0, 0, 64], [1e9, 2e9, -1e9], [1e18, 0, 0], [0, 1e18, 1e18], [-1e18, 1e18, 1e18], [-0.5, R3 / 2, 0], [-0.5, -R3 / 2, 0], [0.5, R3 / 2, 0]];
    let cap = 0, note = '';
    for (const n of [2, 3, 8, -1, -2, -3]) for (const g of run(pil, [0, 0, 0, 0], 0, n, edge)) { if (!g.every(Number.isFinite)) { finite = false; note = 'pw n=' + n + ' -> ' + g; } cap = Math.max(cap, ...g.map(Math.abs)); }
    say(`4. GLSL against JavaScript, ${count} values (8 powers × 2560 points, 12 of every 64 in the plane z = 0, 12 just beside it): worst |glsl - js| / (1 + |js|) = ${worst.toExponential(2)} at ${where}; ${big} values differ by more than 2e-3${bigList.length ? ' e.g. ' + bigList.join(' | ') : ''}; sqr() against the JavaScript square ${worstSq.toExponential(1)}; mul(a, b) against the Sphere inversions shader with one plane ${worstMul.toExponential(1)}; largest |z| the shader returns for a point of the plane z = 0: ${planeZ.toExponential(1)}; finite at the origin, on the axes and at 1e18: ${finite ? 'yes' : 'NO ' + note}, largest component ${cap.toExponential(2)}`);
  }
}

// ---- 5. distortion of the direction map D = Phi o (times n) o PhiInv
function distortion(n, N) {
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
    rows.push({ d, ar: s1 / s2, pr: s1 * s2 });
  }
  return rows;
}
say('5. Distortion of D = Phi o (times n) o PhiInv, 20000 random directions, singular values s1 >= s2 of the derivative divided by |n|');
for (const n of [2, 3]) {
  const rows = distortion(n, 20000), ar = rows.map(r => r.ar).sort((x, y) => x - y), pr = rows.map(r => r.pr).sort((x, y) => x - y);
  say(`   n = ${n}: s1/s2 median ${pct(ar, 50).toFixed(3)}, 95th ${pct(ar, 95).toFixed(3)}, 99.9th ${pct(ar, 99.9).toFixed(2)}, max ${ar[ar.length - 1].toFixed(1)};  s1*s2 median ${pct(pr, 50).toFixed(3)}, 5th ${pct(pr, 5).toFixed(3)}, 95th ${pct(pr, 95).toFixed(3)}, 99.9th ${pct(pr, 99.9).toFixed(2)}, min ${pr[0].toFixed(3)}, max ${pr[pr.length - 1].toFixed(2)}`);
  if (n === 2) {
    // where the shape distortion sits: by latitude band, and by longitude folded into one 60° half sector (0° = corner meridian, 60° = mid-edge meridian)
    const fold = d => { let a = ((Math.atan2(d[1], d[0]) / DEG) % 120 + 120) % 120; return a > 60 ? 120 - a : a; };
    const med = list => { const s = list.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : NaN; };
    const lat = [0, 10, 25, 45, 65, 80, 90], lon = [0, 10, 25, 35, 50, 60];
    say('      median s1/s2 (and median s1*s2) by |latitude| band: ' + lat.slice(0, -1).map((a, i) => { const sel = rows.filter(r => { const q = Math.abs(Math.asin(r.d[2])) / DEG; return q >= a && q < lat[i + 1]; }); return `${a}–${lat[i + 1]}°: ${med(sel.map(r => r.ar)).toFixed(2)} (${med(sel.map(r => r.pr)).toFixed(2)})`; }).join(', '));
    say('      median s1/s2 by longitude from the nearest corner meridian: ' + lon.slice(0, -1).map((a, i) => { const sel = rows.filter(r => { const q = fold(r.d); return q >= a && q < lon[i + 1]; }); return `${a}–${lon[i + 1]}°: ${med(sel.map(r => r.ar)).toFixed(2)}`; }).join(', '));
    const top = rows.slice().sort((x, y) => y.ar - x.ar).slice(0, 40);
    say('      the 40 worst s1/s2 sit at (longitude from the nearest corner meridian, |latitude|): ' + top.slice(0, 12).map(r => `(${fold(r.d).toFixed(0)}°, ${(Math.abs(Math.asin(r.d[2])) / DEG).toFixed(0)}°) ${r.ar.toFixed(1)}`).join(', ') + `; of the 40, ${top.filter(r => fold(r.d) > 45).length} are within 15° of a mid-edge meridian, ${top.filter(r => fold(r.d) < 15).length} within 15° of a corner meridian, ${top.filter(r => Math.abs(Math.asin(r.d[2])) / DEG > 60).length} above 60° latitude, ${top.filter(r => Math.abs(Math.asin(r.d[2])) / DEG < 20).length} below 20°`);
    const worstPr = rows.slice().sort((x, y) => Math.abs(Math.log(y.pr)) - Math.abs(Math.log(x.pr))).slice(0, 8);
    say('      the 8 worst s1*s2 sit at: ' + worstPr.map(r => `(${fold(r.d).toFixed(0)}°, ${(Math.abs(Math.asin(r.d[2])) / DEG).toFixed(0)}°) ${r.pr.toFixed(2)}`).join(', '));
  }
}
return out.join('\n');
