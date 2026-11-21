// Checker of round 12, maths. Pure JavaScript against window.squaringLab.MATH. Returns one JSON text.
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES, PI = Math.PI;
const out = {};
let seed = 987654321;
const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const cpow = (x, y, n) => { const r = Math.hypot(x, y), a = Math.atan2(y, x) * n, R = Math.pow(r, n); return [R * Math.cos(a), R * Math.sin(a)]; };
const byId = id => AP.find(a => a.id === id);
const defs = ap => { const p = {}; (ap.params || []).forEach(q => { if (q.key) p[q.key] = q.def; }); return p; };
const sci = x => +x.toExponential(2);
const pts2 = []; for (let i = 0; i < 2500; i++) { const r = 0.05 + 2.2 * rnd(), a = (rnd() * 2 - 1) * PI; pts2.push([r * Math.cos(a), r * Math.sin(a)]); }
const pts3 = []; for (let i = 0; i < 3000; i++) { let v; do { v = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...v) < 0.05 || Math.hypot(...v) > 1); const s = 0.1 + 2 * rnd(); pts3.push(v.map(c => c * s / Math.hypot(...v))); }
const POW = [2, 3, 5, -1, -2, 2.5];
// error of the rule on the plane through the x-axis at angle th (0: z = 0) against the complex power in that plane
// mode 1: same orientation, mode -1: mirror image (complex conjugate)
function planeErr(id, n, p, th = 0, mode = 1, ref = n) {
  let worst = 0, bad = 0, off = 0; const c = Math.cos(th), s = Math.sin(th);
  for (const [x, y] of pts2) {
    const o = M[id]([x, y * c, y * s], n, p), e = cpow(x, y, ref), Y = e[1] * mode;
    const d = Math.hypot(o[0] - e[0], o[1] - Y * c, o[2] - Y * s) / (1 + Math.hypot(e[0], e[1]));
    if (d > worst) worst = d; if (d > 1e-9) bad++;
    off = Math.max(off, Math.abs(-o[1] * s + o[2] * c));
  }
  return { worst: sci(worst), bad, off: sci(off) };
}
// ---------- 1. every entry at its starting dials: z = 0 against the flat power, and what the slice text says
out.slice0 = {};
for (const ap of AP) {
  const p = defs(ap), row = {};
  for (const n of POW) {
    const e = planeErr(ap.id, n, p), ok = e.worst < 1e-9;
    let text = ''; try { text = ap.slice(ok, p, n); } catch (err) { text = 'ERR ' + err; }
    const saysExact = /exactly/.test(text) && !/except in a wedge|does not|rounded|not the flat/.test(text);
    row[n] = { worst: e.worst, bad: e.bad, zmax: e.off, saysExact, agree: saysExact === ok, text: text.slice(0, 90) };
  }
  out.slice0[ap.id] = row;
}
// ---------- 1b. variants named in the texts
const V = out.variants = {};
V.merc_turn30 = POW.slice(0, 5).map(n => { let w = 0; for (const [x, y] of pts2) { const o = M.mercator([x, y, 0], n, { turn: 30 }), e = cpow(x, y, n), c = Math.cos(PI / 6), s = Math.sin(PI / 6); w = Math.max(w, Math.hypot(o[0] - (e[0] * c - e[1] * s), o[1] - (e[0] * s + e[1] * c), o[2]) / (1 + Math.hypot(...e))); } return sci(w); });
V.merc_lift = planeErr('mercator', 2, { lift: 0.3 });
V.fold_planes = {};
for (const k of [2, 3, 4, 5, 8]) { V.fold_planes[k] = []; for (let j = 0; j < k; j++) { const a = Math.max(...[2, 3, 5, -1, -2].map(n => planeErr('fold', n, { planes: k }, j * PI / k, 1).worst)), b = Math.max(...[2, 3, 5, -1, -2].map(n => planeErr('fold', n, { planes: k }, j * PI / k, -1).worst)); V.fold_planes[k].push(a < 1e-9 ? 'exact' : b < 1e-9 ? 'mirror' : 'NO ' + a + '/' + b); } }
V.lathe_planes = [0.3, 1, 1.5708, 2.5].map(th => Math.max(...[2, 3, 5, -1, -2].map(n => planeErr('lathe', n, { spin: 1 }, th).worst)));
V.lathe_spin3_z0 = Math.max(...[2, 3, 5, -1, -2].map(n => planeErr('lathe', n, { spin: 3 }).worst));
V.lathe_spin3_plane1 = planeErr('lathe', 2, { spin: 3 }, 1).worst;
V.softfold_planes = {};
for (const k of [2, 3, 4]) for (const mix of [0, 1, 2]) for (const blend of [0, 0.25, 0.45]) {
  const r = []; for (let j = 0; j < k; j++) { const a = Math.max(...[2, 3, 5, -1, -2].map(n => planeErr('softfold', n, { planes: k, blend, curve: 0, mix }, j * PI / k, 1).worst)), b = Math.max(...[2, 3, 5, -1, -2].map(n => planeErr('softfold', n, { planes: k, blend, curve: 0, mix }, j * PI / k, -1).worst)); r.push(a < 1e-9 ? 'exact' : b < 1e-9 ? 'mirror' : 'NO ' + a); }
  V.softfold_planes[k + 'pl mix' + mix + ' band' + blend] = r.join(',');
}
V.softfold_frac = planeErr('softfold', 2.5, { planes: 2, blend: 0.25, curve: 0, mix: 0 });
V.axisbulb_k = {};
for (let k = -7; k <= 9; k++) {
  const q = { k, wob: 0.2, reach: 45, pinch: 0 }, ws = [2, 3, 5, -1, -2];
  const z0 = Math.max(...ws.map(n => planeErr('axisbulb', n, q).worst)), y0 = Math.max(...ws.map(n => planeErr('axisbulb', n, q, PI / 2, 1).worst)), y0m = Math.max(...ws.map(n => planeErr('axisbulb', n, q, PI / 2, -1).worst));
  let text = ''; try { text = byId('axisbulb').slice(z0 < 1e-9, q, 2); } catch (e) { text = 'ERR ' + e; }
  // does an even multiplier fold the half y < 0 onto y > 0?
  let fold = 0; for (const [x, y] of pts2) { const a = M.axisbulb([x, y, 0], 2, q), b = M.axisbulb([x, -y, 0], 2, q); fold = Math.max(fold, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2])); }
  V.axisbulb_k[k] = { z0: z0 < 1e-9 ? 'exact' : 'NO ' + z0, y0: y0 < 1e-9 ? 'exact' : y0m < 1e-9 ? 'mirror' : 'NO', sameForBothHalves: fold < 1e-12, text: text.slice(0, 120) };
}
V.axisbulb_pinch = { z0: planeErr('axisbulb', 2, { k: 1, wob: 0.2, reach: 45, pinch: 2 }).worst, y0: planeErr('axisbulb', 2, { k: 1, wob: 0.2, reach: 45, pinch: 2 }, PI / 2).worst, z0k5: planeErr('axisbulb', 3, { k: 5, wob: 0.5, reach: 20, pinch: 3 }).worst };
{ let w = 0; for (const v of pts3) for (const n of [2, 3, -1, 2.5]) { const a = M.axisbulb(v, n, { k: 1, wob: 0, reach: 45, pinch: 0 }), b = M.lathe(v, n, { spin: 1 }); w = Math.max(w, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) / (1 + Math.hypot(...b))); } V.axisbulb_is_lathe = sci(w); }
V.pillow = { creased_z0: {}, creased_y0: {}, smooth_z0: {} };
for (const n of [2, 3, 4, 5, 8, -1, -2, -3]) { V.pillow.creased_z0[n] = planeErr('pillow', n, { layout: 0 }).worst; V.pillow.creased_y0[n] = Math.min(planeErr('pillow', n, { layout: 0 }, PI / 2, 1).worst, 1e9); }
V.pillow.creased_2p5_as_3 = planeErr('pillow', 2.5, { layout: 0 }, 0, 1, 3).worst;
V.pillow.creased_2p4_as_2 = planeErr('pillow', 2.4, { layout: 0 }, 0, 1, 2).worst;
for (const n of [2, 4, 8]) V.pillow.smooth_z0[n] = planeErr('pillow', n, { layout: 1 });
{ // the wobble of the smooth layout on the circle z = 0, in degrees
  let w = 0, where = 0; for (let i = 0; i < 7200; i++) { const t = (i + 0.5) / 7200 * 2 * PI - PI, o = M.pillow([Math.cos(t), Math.sin(t), 0], 2, { layout: 1 }); let d = Math.atan2(o[1], o[0]) - 2 * t; d = ((d + PI) % (2 * PI) + 2 * PI) % (2 * PI) - PI; if (Math.abs(d) > w) { w = Math.abs(d); where = t; } }
  V.pillow.smooth_wobble_deg = +(w * 180 / PI).toFixed(3); V.pillow.smooth_wobble_at_deg = +(where * 180 / PI).toFixed(2);
  // formula text: w -> (2w^3 - 1)/(w(2 - w^3)), w = (x + iy)/(1 - z)
  const cm = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]], cd = (a, b) => { const q = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / q, (a[1] * b[0] - a[0] * b[1]) / q]; };
  let fe = 0; for (const v of pts3) { const r = Math.hypot(...v), d = v.map(c => c / r); if (Math.abs(1 - d[2]) < 1e-3) continue; const ww = [d[0] / (1 - d[2]), d[1] / (1 - d[2])], w3 = cm(cm(ww, ww), ww), Lw = cd([2 * w3[0] - 1, 2 * w3[1]], cm(ww, [2 - w3[0], -w3[1]])), q = Lw[0] * Lw[0] + Lw[1] * Lw[1], e = [2 * Lw[0] / (q + 1), 2 * Lw[1] / (q + 1), (q - 1) / (q + 1)], o = M.pillow(v, 2, { layout: 1 }); fe = Math.max(fe, Math.hypot(o[0] - r * r * e[0], o[1] - r * r * e[1], o[2] - r * r * e[2]) / (r * r)); }
  V.pillow.smooth_formula_err = sci(fe);
  // the stretch at 60, 180, 300 degrees and elsewhere on the circle
  const st = deg => { const t = deg * PI / 180, h = 1e-5, a = M.pillow([Math.cos(t - h), Math.sin(t - h), 0], 2, { layout: 1 }), b = M.pillow([Math.cos(t + h), Math.sin(t + h), 0], 2, { layout: 1 }); return +(Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) / (2 * h)).toExponential(2); };
  V.pillow.smooth_stretch = { 0: st(0), 30: st(30), 60: st(60), 120: st(120), 180: st(180), 300: st(300) };
  // corners of the creased sheet: the directions that stay put under every whole power (the corner A) and the cube roots
  V.pillow.creased_roots = [0, 120, 240].map(dg => { const t = dg * PI / 180, o = M.pillow([Math.cos(t), Math.sin(t), 0], 3, { layout: 0 }); return o.map(c => +c.toFixed(6)); });
}
// ---------- 2. written formulas against MATH, on points of space
const F = out.formulas = {};
const cmp = (id, n, p, f, filter) => { let w = 0, k = 0; for (const v of pts3) { if (filter && !filter(v)) continue; const a = M[id](v, n, p), b = f(v); if (!b) continue; k++; w = Math.max(w, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) / (1 + Math.hypot(...b))); } return sci(w) + ' (' + k + ' pts)'; };
for (const n of [2, 3, 5, -1, -2, -3]) F['mercator inversions n=' + n] = cmp('mercator', n, {}, v => L.inversionPower(v, n));
F['mercator n=-1 text'] = cmp('mercator', -1, {}, ([x, y, z]) => { const q = x * x + y * y + z * z; return [x / q, -y / q, -z / q]; });
F['mercator closed 2.5'] = cmp('mercator', 2.5, {}, ([x, y, z]) => { const r = Math.hypot(x, y, z), ph = Math.atan2(y, x), lat = Math.asin(z / r), m = Math.log(Math.tan(PI / 4 + lat / 2)), R = Math.pow(r, 2.5); return [R * Math.cos(2.5 * ph) / Math.cosh(2.5 * m), R * Math.sin(2.5 * ph) / Math.cosh(2.5 * m), R * Math.tanh(2.5 * m)]; });
F['mercator after turn 20 lift 0.3, n=3'] = cmp('mercator', 3, { turn: 20, lift: 0.3 }, ([x, y, z]) => { const r = Math.hypot(x, y, z), ph = Math.atan2(y, x), lat = Math.asin(z / r), m = 3 * Math.log(Math.tan(PI / 4 + lat / 2)) + 0.3, R = r ** 3, P = 3 * ph + 20 * PI / 180; return [R * Math.cos(P) / Math.cosh(m), R * Math.sin(P) / Math.cosh(m), R * Math.tanh(m)]; });
// fold text: "the nearest of p planes through the x-axis is folded onto the xy-plane", then the one-plane rule
const myFold = ([x, y, z], k) => { const rho = Math.hypot(y, z), psi = Math.atan2(z, y); let best = 0, bd = 9; for (let j = -k; j <= k; j++) { let d = Math.abs(psi - j * PI / k); if (d < bd) { bd = d; best = j; } } const dd = psi - best * PI / k; return { x, rho, dd, best }; };
for (const k of [2, 3, 5]) F['fold = fan fold + one plane, planes ' + k + ' (|output| only up to the side)'] = cmp('fold', 2, { planes: k }, v => { const f = myFold(v, k); const cands = []; for (const sy of [1, -1]) for (const sz of [1, -1]) cands.push(M.mercator([f.x, sy * f.rho * Math.cos(f.dd), sz * f.rho * Math.sin(f.dd)], 2, {})); const a = M.fold(v, 2, { planes: k }); let b = cands[0], bd = 9e9; for (const c of cands) { const d = Math.hypot(a[0] - c[0], a[1] - c[1], a[2] - c[2]); if (d < bd) { bd = d; b = c; } } return b; });
F['lathe n=2'] = cmp('lathe', 2, { spin: 1 }, ([x, y, z]) => [x * x - y * y - z * z, 2 * x * y, 2 * x * z]);
F['lathe n=-1'] = cmp('lathe', -1, { spin: 1 }, ([x, y, z]) => { const q = x * x + y * y + z * z; return [x / q, -y / q, -z / q]; });
F['lathe n=3 general'] = cmp('lathe', 3, { spin: 1 }, ([x, y, z]) => { const r = Math.hypot(x, y, z), rho = Math.hypot(y, z), al = Math.atan2(rho, x), R = r ** 3; return [R * Math.cos(3 * al), R * Math.sin(3 * al) * y / rho, R * Math.sin(3 * al) * z / rho]; });
F['lathe spin 3: angle of (y,z) times 3, n=2'] = cmp('lathe', 2, { spin: 3 }, ([x, y, z]) => { const q = [x * x - y * y - z * z, 2 * x * y, 2 * x * z], rho = Math.hypot(q[1], q[2]), g = 3 * Math.atan2(q[2], q[1]); return [q[0], rho * Math.cos(g), rho * Math.sin(g)]; });
for (const t of [0, 15, 40, 90, 137, 180, -60]) F['tilt n=2 text, tilt ' + t] = cmp('tilt', 2, { tilt: t }, ([x, y, z]) => { const a = t * PI / 180; return [x * x - y * y - z * z * Math.cos(2 * a), 2 * x * y + z * z * Math.sin(2 * a), 2 * z * (x * Math.cos(a) - y * Math.sin(a))]; });
F['bulb n=2'] = cmp('bulb', 2, {}, ([x, y, z]) => { const r2 = x * x + y * y, k = (r2 - z * z) / r2; return [k * (x * x - y * y), k * 2 * x * y, 2 * Math.sqrt(r2) * z]; });
F['bulb n=-1'] = cmp('bulb', -1, {}, ([x, y, z]) => { const q = x * x + y * y + z * z; return [x / q, -y / q, -z / q]; });
for (const n of [2, 3, 8, -2, 2.5]) F['classic with theta (1-n)*90 = bulb, n=' + n] = cmp('classic', n, { theta: (1 - n) * 90, phi: 0 }, v => M.bulb(v, n, {}));
F['split n=2'] = cmp('split', 2, {}, ([x, y, z]) => [x * x - y * y, 2 * x * y, z * z]);
F['split n=-1'] = cmp('split', -1, {}, ([x, y, z]) => { const q = x * x + y * y + z * z; return [x / q, -y / q, z / q]; });
F['split n=3'] = cmp('split', 3, {}, ([x, y, z]) => { const e = cpow(x, y, 3); return [e[0], e[1], z ** 3]; });
F['split n=-2'] = cmp('split', -2, {}, ([x, y, z]) => { const e = cpow(x, y, 2), Z = z * z, q = e[0] * e[0] + e[1] * e[1] + Z * Z; return [e[0] / q, -e[1] / q, Z / q]; });
// axisbulb formula text
for (const q of [{ k: 1, wob: 0.2, reach: 45, pinch: 0 }, { k: 5, wob: 0, reach: 45, pinch: 0 }, { k: -3, wob: 0.4, reach: 30, pinch: 1.5 }, { k: 2, wob: 0.2, reach: 0, pinch: 0.5 }])
  for (const n of [2, 3, -1]) F['axisbulb text ' + JSON.stringify(q) + ' n=' + n] = cmp('axisbulb', n, q, ([x, y, z]) => {
    const r = Math.hypot(x, y, z), rho = Math.hypot(y, z), be = Math.atan2(rho, x), ga = Math.atan2(z, y), R = Math.pow(r, n);
    // the result of the quaternion power, then its turn g2 is changed
    const sx = R * Math.cos(n * be), sr = R * Math.sin(n * be), rr = Math.abs(sr), g2 = Math.atan2(sr * Math.sin(ga), sr * Math.cos(ga));
    const sR = Math.sin(q.reach * PI / 180), t = sR > 1e-6 ? Math.min(1, Math.max(0, (rr / R) / sR)) : 1, W = t * t * (3 - 2 * t);
    const G = q.k * g2 + q.wob * W * Math.sin(4 * g2), len = 1 + q.pinch * Math.sin(2 * g2) ** 2 * Math.sin(n * be) ** 2;
    return [len * sx, len * rr * Math.cos(G), len * rr * Math.sin(G)];
  });
// ---------- 3. the twisted quaternion square
const T = out.tilt = {};
T.z0 = {}; for (const t of [0, 15, 40, 90, 137, 180, -60]) { T.z0[t] = {}; for (const n of POW) { const e = planeErr('tilt', n, { tilt: t }); T.z0[t][n] = e.worst + (e.bad ? ' bad ' + e.bad : ''); } }
{ // where the fractional power differs: the angles of the points that differ
  const wedge = (t, n) => { let lo = 999, hi = -999, k = 0; for (const [x, y] of pts2) { const o = M.tilt([x, y, 0], n, { tilt: t }), e = cpow(x, y, n); if (Math.hypot(o[0] - e[0], o[1] - e[1], o[2]) > 1e-9) { let a = Math.atan2(y, x) * 180 / PI; if (a < 0) a += 360; lo = Math.min(lo, a); hi = Math.max(hi, a); k++; } } return { differ: k, of: pts2.length, fromDeg: +lo.toFixed(1), toDeg: +hi.toFixed(1) }; };
  T.wedge = { 't40 n2.5': wedge(40, 2.5), 't-60 n2.5': wedge(-60, 2.5), 't137 n2.5': wedge(137, 2.5), 't90 n-1.5': wedge(90, -1.5), 't180 n2.5': wedge(180, 2.5) };
}
{ let w0 = 0, w180 = 0, wm = 0, w180n = 0; for (const v of pts3) for (const n of [2, 3, 5, -1, -2]) {
    const a0 = M.tilt(v, n, { tilt: 0 }), l = M.lathe(v, n, { spin: 1 }); w0 = Math.max(w0, Math.hypot(a0[0] - l[0], a0[1] - l[1], a0[2] - l[2]) / (1 + Math.hypot(...l)));
    const a = M.tilt(v, n, { tilt: 180 }); w180 = Math.max(w180, Math.hypot(a[0] - l[0], a[1] - l[1], a[2] + l[2]) / (1 + Math.hypot(...l)));
    w180n = Math.max(w180n, Math.hypot(a[0] - l[0], a[1] - l[1], a[2] - l[2]) / (1 + Math.hypot(...l)));
    for (const t of [15, 40, 90, 137]) { const p = M.tilt(v, n, { tilt: t }), m = M.tilt([v[0], -v[1], v[2]], n, { tilt: -t }); wm = Math.max(wm, Math.hypot(p[0] - m[0], p[1] + m[1], p[2] - m[2]) / (1 + Math.hypot(...p))); }
  }
  T.tilt0_is_lathe = sci(w0); T.tilt180_is_lathe_z_mirrored = sci(w180); T.tilt180_minus_plain_lathe = sci(w180n); T.minus_tilt_is_mirror_in_y = sci(wm);
  // is it also the mirror image in z or x? (it should not be)
  let wz = 0; for (const v of pts3) { const p = M.tilt(v, 2, { tilt: 40 }), m = M.tilt([v[0], v[1], -v[2]], 2, { tilt: -40 }); wz = Math.max(wz, Math.hypot(p[0] - m[0], p[1] - m[1], p[2] + m[2])); } T.minus_tilt_mirror_in_z_differs_by = sci(wz);
}
// tilt 90: the Mandelbrot solid in the plane y = 0. c = (cx, 0, s): bounded after 2000 steps?
const esc = (id, p, c, v0, N, B = 1e6) => { let v = v0.slice(); for (let i = 0; i < N; i++) { v = M[id](v, 2, p); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; if (!(Math.hypot(...v) < B)) return i; } return -1; };
T.tilt90 = {}; for (const t of [90, -90, 40, 0]) { T.tilt90['tilt ' + t] = [2, 5, 10, 30, 100, 1000].map(s => { const inside = esc('tilt', { tilt: t }, [-s * s - 0.5, 0, s], [0, 0, 0], 3000) < 0, lo = esc('tilt', { tilt: t }, [-s * s - 2.2, 0, s], [0, 0, 0], 3000) < 0, hi = esc('tilt', { tilt: t }, [-s * s + 0.4, 0, s], [0, 0, 0], 3000) < 0; return 's=' + s + ': c=(-s^2-0.5,0,s) ' + (inside ? 'bounded' : 'escapes') + ', below band ' + (lo ? 'bounded' : 'escapes') + ', above band ' + (hi ? 'bounded' : 'escapes'); }); }
{ // band edges at tilt 90, plane y = 0: bounded exactly when -2 <= cx + s^2 <= 1/4 ?
  let wrong = 0, tot = 0; for (let i = 0; i < 4000; i++) { const s = (rnd() * 2 - 1) * 6, u = -2.6 + 3.2 * rnd(), c = [u - s * s, 0, s]; if (Math.abs(u + 2) < 0.02 || Math.abs(u - 0.25) < 0.02) continue; tot++; const b = esc('tilt', { tilt: 90 }, c, [0, 0, 0], 4000) < 0; if (b !== (u >= -2 && u <= 0.25)) wrong++; } T.tilt90_band = wrong + ' of ' + tot + ' points disagree with the band -2 <= cx + s^2 <= 1/4';
  // z stays at c's height in that plane
  let dz = 0; for (let i = 0; i < 500; i++) { const s = rnd() * 4, c = [-s * s - 0.7, 0, s]; let v = [0, 0, 0]; for (let k = 0; k < 50; k++) { v = M.tilt(v, 2, { tilt: 90 }); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; dz = Math.max(dz, Math.abs(v[2] - s), Math.abs(v[1])); } } T.tilt90_height_drift = sci(dz);
}
// 4D: q -> q * twisted(q) + c with real quaternion arithmetic, against the 3D rule
{ const qm = (a, b) => [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3], a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2], a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1], a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]];
  // (c + d i) j = c j + d k, so w = (q[2], q[3]); the twisted copy turns w by 2t
  const tw = (q, t) => { const c = Math.cos(2 * t), s = Math.sin(2 * t); return [q[0], q[1], c * q[2] - s * q[3], s * q[2] + c * q[3]]; };
  const res = {};
  for (const tdeg of [0, 15, 40, 90, 137, 180, -60]) {
    const t = tdeg * PI / 180; let stepErr = 0, kOut = 0, mism = 0, tot = 0, bnd = 0, mismC = 0, totC = 0;
    for (const v of pts3) { const q = qm([v[0], v[1], v[2], 0], tw([v[0], v[1], v[2], 0], t)), o = M.tilt(v, 2, { tilt: tdeg }); stepErr = Math.max(stepErr, Math.hypot(q[0] - o[0], q[1] - o[1], Math.hypot(q[2], q[3]) - Math.abs(o[2]))); kOut = Math.max(kOut, Math.abs(q[3])); }
    const cs = [[-1, 0], [-0.12, 0.75], [0.28, 0.01], [-0.4, 0.6], [0.3, 0.5], [-0.75, 0.1]];
    for (const c2 of cs) for (let i = 0; i < 700; i++) {
      const v0 = [(rnd() * 2 - 1) * 1.6, (rnd() * 2 - 1) * 1.3, (rnd() * 2 - 1) * 1.3]; let q = [v0[0], v0[1], v0[2], 0], v = v0.slice(), e4 = -1, e3 = -1;
      for (let k = 0; k < 300; k++) { if (e4 < 0) { q = qm(q, tw(q, t)); q[0] += c2[0]; q[1] += c2[1]; if (!(Math.hypot(...q) < 1e3)) e4 = k; } if (e3 < 0) { v = M.tilt(v, 2, { tilt: tdeg }); v[0] += c2[0]; v[1] += c2[1]; if (!(Math.hypot(...v) < 1e3)) e3 = k; } if (e3 >= 0 && e4 >= 0) break; }
      tot++; if (e3 < 0) bnd++; if ((e3 < 0) !== (e4 < 0) || (e3 >= 0 && Math.abs(e3 - e4) > 0)) mism++;
    }
    // with a c that has a height the 4D set is no longer the same thing (the page says it is its own choice)
    for (let i = 0; i < 1500; i++) { const c = [(rnd() * 2 - 1) * 1.2 - 0.3, (rnd() * 2 - 1) * 1, (rnd() * 2 - 1) * 1]; let q = [0, 0, 0, 0], v = [0, 0, 0], e4 = -1, e3 = -1; for (let k = 0; k < 300; k++) { if (e4 < 0) { q = qm(q, tw(q, t)); q[0] += c[0]; q[1] += c[1]; q[2] += c[2]; if (!(Math.hypot(...q) < 1e3)) e4 = k; } if (e3 < 0) { v = M.tilt(v, 2, { tilt: tdeg }); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; if (!(Math.hypot(...v) < 1e3)) e3 = k; } if (e3 >= 0 && e4 >= 0) break; } totC++; if ((e3 < 0) !== (e4 < 0)) mismC++; }
    res[tdeg] = { oneStep_xy_and_length_of_hidden_part: sci(stepErr), largest_k_part_after_one_step: sci(kOut), julia_points: tot, julia_bounded3D: bnd, julia_mismatch: mism, mandel_points: totC, mandel_inOut_mismatch: mismC };
  }
  T.fourD = res;
}
// the plane square to the tilted axis is crushed onto a ray (crush text), tilt 40
{ const t = 40 * PI / 180; let w = 0; for (let i = 0; i < 2000; i++) { const s = rnd() * 2 - 1, z = rnd() * 2 - 1, v = [s * Math.sin(t), s * Math.cos(t), z], o = M.tilt(v, 2, { tilt: 40 }), R = s * s + z * z; w = Math.max(w, Math.hypot(o[0] + R * Math.cos(2 * t), o[1] - R * Math.sin(2 * t), o[2])); } T.plane_square_to_axis_lands_on_one_ray = sci(w); }
// are other planes through the x-axis kept (as for the Lathe)? distance of the result from the plane of the point and the x-axis
{ let off = 0, offL = 0; for (const v of pts3) { const o = M.tilt(v, 2, { tilt: 40 }), l = M.lathe(v, 2, {}), rho = Math.hypot(v[1], v[2]), nrm = [0, -v[2] / rho, v[1] / rho]; off = Math.max(off, Math.abs(o[1] * nrm[1] + o[2] * nrm[2]) / (1 + Math.hypot(...o))); offL = Math.max(offL, Math.abs(l[1] * nrm[1] + l[2] * nrm[2]) / (1 + Math.hypot(...l))); } T.leaves_plane_of_xaxis_and_point = { tilt40: sci(off), lathe: sci(offL) };
  T.plane_y0_tilt40 = planeErr('tilt', 2, { tilt: 40 }, PI / 2).worst; T.plane_30deg_tilt40 = planeErr('tilt', 2, { tilt: 40 }, PI / 6).worst; }
// "doing that turn to v itself doubles the angle from the x-axis, and that is the quaternion square"
{ let w = 0; for (const v of pts3) { const r = Math.hypot(...v), rho = Math.hypot(v[1], v[2]), al = Math.atan2(rho, v[0]), u = [0, v[1] / rho, v[2] / rho];
    // turn v by al in the plane of the x-axis and v, and stretch by |v|
    const c = Math.cos(al), s = Math.sin(al), a = v[0], b = rho, o = [r * (c * a - s * b), r * (s * a + c * b) * u[1], r * (s * a + c * b) * u[2]], l = M.lathe(v, 2, {}); w = Math.max(w, Math.hypot(o[0] - l[0], o[1] - l[1], o[2] - l[2])); } out.turn_to_v_is_quaternion_square = sci(w); }
// ---------- 4. tried entries: more of their sentences
const TR = out.tried = {};
{ // the seam half way between two planes lands on itself (softfold), and the pinch crushes it onto the x-axis for an even power
  const seam = (q, n, k) => { let off = 0, ax = 0; const th = PI / (2 * k); for (const [x, y] of pts2) { const o = M.softfold([x, y * Math.cos(th), y * Math.sin(th)], n, q); off = Math.max(off, Math.abs(-o[1] * Math.sin(th) + o[2] * Math.cos(th)) / (1 + Math.hypot(...o))); ax = Math.max(ax, Math.hypot(o[1], o[2]) / (1e-300 + Math.hypot(...o))); } return { leavesSeamPlaneBy: sci(off), offAxisShare: sci(ax) }; };
  TR.softfold_seam = { 'blend 2pl n2': seam({ planes: 2, blend: 0.25, curve: 0, mix: 0 }, 2, 2), 'blend 2pl n3': seam({ planes: 2, blend: 0.25, curve: 0, mix: 0 }, 3, 2), 'line 3pl n2': seam({ planes: 3, blend: 0.25, curve: 0, mix: 1 }, 2, 3), 'pinch 2pl n2': seam({ planes: 2, blend: 0.25, curve: 0, mix: 2 }, 2, 2), 'pinch 3pl n4': seam({ planes: 3, blend: 0.25, curve: 0, mix: 2 }, 4, 3), 'pinch 2pl n3': seam({ planes: 2, blend: 0.25, curve: 0, mix: 2 }, 3, 2) };
  // inside a plane's own band the rule is that plane's one-plane rule
  let w = 0, cnt = 0; const k = 2, a = 0.25, wdt = PI / k; for (const v of pts3) { let psi = Math.atan2(v[2], v[1]); if (psi < 0) continue; const j = Math.floor(psi / wdt), t = psi / wdt - j; if (t > a - 0.01 && t < 1 - a + 0.01) continue; const jj = t <= a ? j : j + 1, th = jj * wdt, c = Math.cos(th), s = Math.sin(th), loc = [v[0], v[1] * c + v[2] * s, -v[1] * s + v[2] * c], m = M.mercator(loc, 2, {}), e = [m[0], m[1] * c - m[2] * s, m[1] * s + m[2] * c], o = M.softfold(v, 2, { planes: 2, blend: a, curve: 0, mix: 0 }); cnt++; w = Math.max(w, Math.hypot(o[0] - e[0], o[1] - e[1], o[2] - e[2])); }
  TR.softfold_own_band_is_one_plane_rule = sci(w) + ' (' + cnt + ' pts)';
  // share of directions that come out turned over (orientation of the map of the sphere of directions), n = 2
  const turned = q => { let neg = 0, tot = 0; const h = 1e-6; for (let i = 0; i < 40000; i++) { let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...d) > 1 || Math.hypot(...d) < 0.1); const r = Math.hypot(...d); d = d.map(c => c / r); let e1 = Math.abs(d[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0]; const dp = e1[0] * d[0] + e1[1] * d[1] + e1[2] * d[2]; e1 = e1.map((c, j) => c - dp * d[j]); const l1 = Math.hypot(...e1); e1 = e1.map(c => c / l1); const e2 = [d[1] * e1[2] - d[2] * e1[1], d[2] * e1[0] - d[0] * e1[2], d[0] * e1[1] - d[1] * e1[0]];
      const f = M.softfold(d, 2, q), f1 = M.softfold(d.map((c, j) => c + h * e1[j]), 2, q), f2 = M.softfold(d.map((c, j) => c + h * e2[j]), 2, q), a = f1.map((c, j) => c - f[j]), b = f2.map((c, j) => c - f[j]);
      const det = f[0] * (a[1] * b[2] - a[2] * b[1]) - f[1] * (a[0] * b[2] - a[2] * b[0]) + f[2] * (a[0] * b[1] - a[1] * b[0]); tot++; if (det < 0) neg++; } return +(100 * neg / tot).toFixed(1); };
  TR.softfold_turned_over_percent = { '2 planes band 0.25': turned({ planes: 2, blend: 0.25, curve: 0, mix: 0 }), '2 planes band 0': turned({ planes: 2, blend: 0, curve: 0, mix: 0 }), '2 planes band 0.45': turned({ planes: 2, blend: 0.45, curve: 0, mix: 0 }), '2 planes straight line': turned({ planes: 2, blend: 0.25, curve: 0, mix: 1 }), '3 planes': turned({ planes: 3, blend: 0.25, curve: 0, mix: 0 }), '4 planes': turned({ planes: 4, blend: 0.25, curve: 0, mix: 0 }), '3 planes band 0': turned({ planes: 3, blend: 0, curve: 0, mix: 0 }), '4 planes band 0.45': turned({ planes: 4, blend: 0.45, curve: 0, mix: 0 }), '2 planes pinch': turned({ planes: 2, blend: 0.25, curve: 0, mix: 2 }) };
}
{ // a jump: the largest |F(a) - F(b)| / |a - b| over close pairs (1e-7 apart), on the unit sphere of directions
  const jump = (id, q, n) => { let w = 0; for (let i = 0; i < 60000; i++) { let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...d) > 1 || Math.hypot(...d) < 0.2); const r = Math.hypot(...d); d = d.map(c => c / r); const e = [d[0] + 1e-7 * (rnd() - 0.5), d[1] + 1e-7 * (rnd() - 0.5), d[2] + 1e-7 * (rnd() - 0.5)], a = M[id](d, n, q), b = M[id](e, n, q); w = Math.max(w, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) / Math.hypot(d[0] - e[0], d[1] - e[1], d[2] - e[2])); } return +w.toExponential(1); };
  TR.largest_slope_over_close_pairs = {
    'softfold 2pl n2': jump('softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, 2), 'softfold 2pl n3': jump('softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, 3), 'softfold 2pl n-2': jump('softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, -2),
    'softfold 3pl n3 band 0.05': jump('softfold', { planes: 3, blend: 0.05, curve: 0, mix: 0 }, 3), 'softfold 4pl n5': jump('softfold', { planes: 4, blend: 0.25, curve: 0, mix: 0 }, 5),
    'softfold pinch 2pl n2': jump('softfold', { planes: 2, blend: 0.25, curve: 0, mix: 2 }, 2), 'softfold pinch 3pl n3': jump('softfold', { planes: 3, blend: 0.25, curve: 0, mix: 2 }, 3),
    'axisbulb start n2': jump('axisbulb', { k: 1, wob: 0.2, reach: 45, pinch: 0 }, 2), 'axisbulb k5 n2': jump('axisbulb', { k: 5, wob: 0.2, reach: 45, pinch: 0 }, 2), 'axisbulb pinch n3': jump('axisbulb', { k: 1, wob: 0.2, reach: 45, pinch: 2 }, 3),
    'pillow creased n2': jump('pillow', { layout: 0 }, 2), 'pillow creased n3': jump('pillow', { layout: 0 }, 3), 'pillow creased n-2': jump('pillow', { layout: 0 }, -2), 'pillow smooth n2': jump('pillow', { layout: 1 }, 2),
    'fold 2pl n2 (known to jump)': jump('fold', { planes: 2 }, 2), 'mercator n2 (known smooth)': jump('mercator', {}, 2), 'tilt40 n2': jump('tilt', { tilt: 40 }, 2), 'tilt40 n3': jump('tilt', { tilt: 40 }, 3) };
}
{ // axisbulb: Julia set c = -1 is the Lathe's whatever the multiplier and wobble; the pinch changes it
  const same = q => { let mm = 0, tot = 0; for (let i = 0; i < 4000; i++) { const v0 = [(rnd() * 2 - 1) * 1.7, (rnd() * 2 - 1) * 1.2, (rnd() * 2 - 1) * 1.2]; const a = esc('axisbulb', q, [-1, 0, 0], v0, 200, 1e3), b = esc('lathe', { spin: 1 }, [-1, 0, 0], v0, 200, 1e3); tot++; if ((a < 0) !== (b < 0)) mm++; } return mm + ' of ' + tot + ' differ'; };
  TR.axisbulb_julia_minus1_vs_lathe = { 'start dials': same({ k: 1, wob: 0.2, reach: 45, pinch: 0 }), 'k 5': same({ k: 5, wob: 0.2, reach: 45, pinch: 0 }), 'k -3 wob 0.8': same({ k: -3, wob: 0.8, reach: 20, pinch: 0 }), 'k 2': same({ k: 2, wob: 0, reach: 45, pinch: 0 }), 'pinch 1': same({ k: 1, wob: 0, reach: 45, pinch: 1 }) };
  // "the flat set in the plane z = 0 is then a sheet with no thickness" at a multiplier of 5 or -3: points of the flat
  // Mandelbrot set lifted a little off the plane, bounded after 3000 steps?
  const thick = (q, eps) => { let inM = 0, stay = 0; for (let i = 0; i < 60; i++) for (let j = 0; j < 40; j++) { const cx = -2 + 2.5 * (i + 0.5) / 60, cy = -1.2 + 2.4 * (j + 0.5) / 40; if (Math.abs(cy) < 0.02) continue; if (esc('lathe', {}, [cx, cy, 0], [0, 0, 0], 1500, 1e3) >= 0) continue; inM++; if (esc('axisbulb', q, [cx, cy, eps], [0, 0, 0], 3000, 1e3) < 0) stay++; } return stay + ' of ' + inM; };
  TR.axisbulb_points_of_flat_set_lifted_still_bounded = {};
  for (const k of [1, 3, 5, -3]) for (const eps of [1e-2, 1e-4, 1e-8]) TR.axisbulb_points_of_flat_set_lifted_still_bounded['k ' + k + ' lifted ' + eps] = thick({ k, wob: 0.2, reach: 45, pinch: 0 }, eps);
  TR.axisbulb_k5_examples = [[0.02, 0.03], [0.05, 0.2], [-0.05, 0.3], [-1, 0.1], [-0.5, 0.3], [0.2, 0.3]].map(([cx, cy]) => { let top = 0; for (const e of [1e-6, 1e-4, 1e-3, 0.01, 0.03, 0.1, 0.2]) if (esc('axisbulb', { k: 5, wob: 0.2, reach: 45, pinch: 0 }, [cx, cy, e], [0, 0, 0], 4000, 1e3) < 0) top = e; return 'c=(' + cx + ',' + cy + ',h): bounded up to h=' + top; });
}
return JSON.stringify(out);
