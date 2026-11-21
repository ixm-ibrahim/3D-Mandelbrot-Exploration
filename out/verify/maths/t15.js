// Point 15: negative powers. (a) every approach on z = 0 against complex z^n. (b) the Mandelbrot iteration the
// shader runs for "z^n + c" started at 0, emulated with MATH, against a plain complex escape-count grid.
const out = { parity: [], fails: [], compiled: {}, grid: [] };
const pts = planePoints(31);
const CASES = [['mercator', { planes: 1 }], ['mercator', { planes: 2 }], ['mercator', { planes: 3 }], ['mercator', { planes: 8 }], ['lathe', { spin: 1 }], ['lathe', { spin: 3 }], ['lathe', { spin: -7 }], ['bulb', {}], ['split', {}], ['classic', {}]];
for (const [id, q] of CASES) {
  const cells = [];
  for (const n of [-1, -2, -3, -4, -8, -0.5, -2.5]) {
    let worst = 0, bad = 0, capped = 0, worstZ = 0;
    for (const [x, y] of pts) {
      const r = Math.hypot(x, y); if (n * Math.log(r) > 41.9) { capped++; continue; }
      const got = M[id]([x, y, 0], n, q), ref = cpow([x, y], n), m = Math.hypot(ref[0], ref[1]);
      const e = Math.hypot(got[0] - ref[0], got[1] - ref[1], got[2]) / m;
      worst = Math.max(worst, e); worstZ = Math.max(worstZ, Math.abs(got[2]) / m); if (!(e <= 1e-5)) bad++;
    }
    cells.push(`n=${n}: ${sci(worst)}${bad ? ' (' + bad + ' over 1e-5)' : ''}${capped ? ' [' + capped + ' capped pts skipped]' : ''}`);
    if (bad && id !== 'classic') out.fails.push(`${id} ${JSON.stringify(q)} n=${n}: ${bad} points over 1e-5`);
  }
  out.parity.push(`${id} ${JSON.stringify(q)}: ` + cells.join(' | '));
}
// what the shader is given
out.compiled.eq = L.compileFormula('z^n + c', true, false); out.compiled.eqN2 = L.compileFormula('z^n + c', true, true); out.compiled.z0 = L.compileFormula('0', false, false);
out.compiled.presetNeg = L.PRESETS.filter(p => /-|⁻/.test(p.eq)).map(p => `${p.name}: eq ${p.eq} -> ${L.compileFormula(p.eq, true, false)}; z0 ${p.z0} -> ${L.compileFormula(p.z0, false, false)}`);
out.compiled.allPresetsCompile = L.PRESETS.map(p => { try { L.compileFormula(p.eq, true, false); L.compileFormula(p.eq, true, true); L.compileFormula(p.z0, false, false); return 'ok'; } catch (e) { return p.name + ': ' + e.message; } }).join(',');
out.iterDefault = L.S.iter;
// the shader's orbit (orbitDE in 30-shaders.js), main orbit only: returns [escaped, steps taken]
function pageOrbit(id, q, n, c, iter, bail = 64) {
  let v = [0, 0, 0], r = 0, it = 0;
  for (let k = 0; k <= iter; k++) {
    if (r > bail) return [1, it];
    if (k === iter) break;
    let w = M[id](v, n, q); w = [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
    let w2 = w[0] * w[0] + w[1] * w[1] + w[2] * w[2]; const wild = !(w2 < 1e36);
    if (k === 0) { const big = 1e3 * (bail + Math.hypot(...c)); if (r < 1e-3 && (wild || w2 > big * big)) { v = [1e9, 0, 0]; r = 0; continue; } }
    if (wild) { w = [1e18, 0, 0]; w2 = 1e36; }
    v = w; r = Math.sqrt(w2); it++;
  }
  return [0, it];
}
// plain complex numbers: 0 -> infinity -> c, then z^n + c; escaped once |z| > bail; at most iter - 1 steps after the pole
function refOrbit(n, c, iter, bail = 64) {
  let z = [c[0], c[1]], it = 1;
  for (;;) {
    if (Math.hypot(z[0], z[1]) > bail) return [1, it];
    if (it >= iter - 1) return [0, it];
    const p = cpow(z, n); z = [p[0] + c[0], p[1] + c[1]]; it++;
    if (!(z[0] * z[0] + z[1] * z[1] < 1e36)) z = [1e18, 0];
  }
}
const G = 161, H = 2.4;
for (const n of [-2, -3]) for (const [id, q] of CASES.filter(c => c[0] !== 'classic')) {
  let diffFlag = 0, diffIt = 0, esc = 0;
  for (let j = 0; j < G; j++) for (let i = 0; i < G; i++) {
    const c = [-H + 2 * H * i / (G - 1) + 0.00137, -H + 2 * H * j / (G - 1) + 0.00071, 0];
    const a = pageOrbit(id, q, n, c, 14), b = refOrbit(n, c, 14);
    if (a[0] !== b[0]) diffFlag++; else if (a[1] !== b[1]) diffIt++; if (b[0]) esc++;
  }
  out.grid.push(`n=${n} ${id} ${JSON.stringify(q)}: ${G}x${G} grid over ±${H}: escaped-or-not differs at ${diffFlag} points, step count differs at ${diffIt}; ${esc} points escape in the reference`);
}
// the shape of the reference picture: how far out the escaping region reaches in each direction
out.shape = [];
for (const n of [-2, -3]) for (const [iter, bail] of [[14, 64], [14, 2], [60, 64], [200, 8]]) {
  const N = 720, R = []; let area = 0;
  for (let i = 0; i < N; i++) { const a = 2 * PI * i / N; let hit = 0; for (let r = 2.4; r > 0.01; r -= 0.01) if (refOrbit(n, [r * Math.cos(a), r * Math.sin(a)], iter, bail)[0]) { hit = r; break; } R.push(hit); }
  const lo = Math.min(...R), hi = Math.max(...R), mid = (lo + hi) / 2; let humps = 0;
  for (let i = 0; i < N; i++) if (R[i] > mid && !(R[(i + N - 1) % N] > mid)) humps++;
  for (let j = 0; j < 121; j++) for (let i = 0; i < 121; i++) if (refOrbit(n, [-2.4 + 4.8 * i / 120 + 0.0013, -2.4 + 4.8 * j / 120 + 0.0007], iter, bail)[0]) area++;
  out.shape.push(`n=${n} steps=${iter} escape radius=${bail}: reach of the escaping region ${lo.toFixed(2)}..${hi.toFixed(2)}, ${humps} arms; it fills ${(100 * area / 14641).toFixed(1)}% of the ±2.4 square`);
}
return out;
