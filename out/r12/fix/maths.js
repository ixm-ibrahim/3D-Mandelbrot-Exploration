// Fixer of round 12: the checkers' numbers, measured again with the page's own MATH (smaller samples).
const L = window.squaringLab, M = L.MATH, PI = Math.PI, out = {};
let seed = 97531;
const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const sci = x => +x.toExponential(2);
const ball = R => { let c; do { c = [(rnd() * 2 - 1) * R, (rnd() * 2 - 1) * R, (rnd() * 2 - 1) * R]; } while (Math.hypot(...c) > R); return c; };
const pts = []; for (let i = 0; i < 2000; i++) { let v; do { v = ball(1); } while (Math.hypot(...v) < 0.05); const s = 0.1 + 2 * rnd(); pts.push(v.map(c => c * s / Math.hypot(...v))); }
// the Mandelbrot solid of an entry: z starts at 0, z -> rule(z) + c; true when it stays inside the radius for N steps
const bounded = (id, q, c, N, n = 2) => { let v = [0, 0, 0]; for (let i = 0; i < N; i++) { v = M[id](v, n, q); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; if (!(v[0] * v[0] + v[1] * v[1] + v[2] * v[2] < 1e6)) return false; } return true; };

// ---- M1: how far does the Mandelbrot solid of the twisted square reach?
out.M1_reach = {};
for (const t of [40, 90, -90]) {
  let n = 0, far = 0, high = 0, beyond2 = 0, farOut = 0;
  for (let i = 0; i < 60000; i++) { const c = ball(2.6), r = Math.hypot(...c); if (bounded('tilt', { tilt: t }, c, 200)) { n++; far = Math.max(far, r); high = Math.max(high, Math.abs(c[2])); if (r > 2) beyond2++; } }
  for (let i = 0; i < 20000; i++) { const r = 3 * Math.pow(100, rnd()); let d; do { d = ball(1); } while (Math.hypot(...d) < 0.1); const q = r / Math.hypot(...d); if (bounded('tilt', { tilt: t }, [d[0] * q, d[1] * q, d[2] * q], 60)) farOut++; }
  out.M1_reach['tilt ' + t] = { bounded_of_60000_in_ball_2p6: n, farthest: +far.toFixed(3), highest: +high.toFixed(3), bounded_beyond_radius_2: beyond2, bounded_of_20000_with_radius_3_to_300: farOut };
}
{ let w = 0; for (const t of [0, 40, 90, 180, -60]) for (const v of pts) { const o = M.tilt(v, 2, { tilt: t }); w = Math.max(w, Math.abs(Math.hypot(...o) - (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]))); } out.M1_length_is_squared_worst = sci(w); }

// ---- m1: tilt 180 against the Lathe, power by power
out.m1_tilt180 = {};
for (const n of [2, 3, 4, 5, -1, -2]) { let wm = 0, wp = 0; for (const v of pts) { const a = M.tilt(v, n, { tilt: 180 }), l = M.lathe(v, n, { spin: 1 }), s = 1 + Math.hypot(...l); wm = Math.max(wm, Math.hypot(a[0] - l[0], a[1] - l[1], a[2] + l[2]) / s); wp = Math.max(wp, Math.hypot(a[0] - l[0], a[1] - l[1], a[2] - l[2]) / s); } out.m1_tilt180['n=' + n] = { against_lathe_with_z_mirrored: sci(wm), against_plain_lathe: sci(wp) }; }

// ---- m3: does the twisted square treat other planes through the x-axis like the plane z = 0? Plane y = 0 at tilt 40, n = 2
{ let w = 0, wl = 0, off = 0; for (let i = 0; i < 2000; i++) { const a = rnd() * 3 - 1.5, b = rnd() * 3 - 1.5, o = M.tilt([a, 0, b], 2, { tilt: 40 }), l = M.lathe([a, 0, b], 2, { spin: 1 }); w = Math.max(w, Math.hypot(o[0] - (a * a - b * b), o[1], o[2] - 2 * a * b)); wl = Math.max(wl, Math.hypot(l[0] - (a * a - b * b), l[1], l[2] - 2 * a * b)); off = Math.max(off, Math.abs(o[1])); }
  let wz = 0; for (let i = 0; i < 2000; i++) { const a = rnd() * 3 - 1.5, b = rnd() * 3 - 1.5, o = M.tilt([a, b, 0], 2, { tilt: 40 }); wz = Math.max(wz, Math.hypot(o[0] - (a * a - b * b), o[1] - 2 * a * b, o[2])); }
  out.m3_planes_at_tilt40 = { plane_y0_misses_complex_square_by: +w.toFixed(3), plane_y0_result_leaves_the_plane_by: +off.toFixed(3), lathe_plane_y0_misses_by: sci(wl), plane_z0_misses_by: sci(wz) }; }

// ---- m4: Bulbs about the axis, multiplier 5: is the solid over the flat set a sheet with no thickness?
{ const flat = (cx, cy) => { let x = 0, y = 0; for (let i = 0; i < 1000; i++) { const X = x * x - y * y + cx, Y = 2 * x * y + cy; x = X; y = Y; if (!(x * x + y * y < 1e6)) return false; } return true; };
  const cs = []; for (let i = 0; i < 60; i++) for (let j = 0; j < 30; j++) { const cx = -2 + 2.5 * (i + 0.5) / 60, cy = 1.2 * (j + 0.5) / 30; if (flat(cx, cy)) cs.push([cx, cy]); }
  out.m4_axisbulb = { flat_set_grid_points: cs.length };
  for (const k of [1, 5, -3]) { const q = { k, wob: 0.2, reach: 45, pinch: 0 }; const r = {}; for (const h of [0, 1e-8, 0.01, 0.1]) r['lift ' + h] = cs.filter(c => bounded('axisbulb', q, [c[0], c[1], h], 1000)).length; out.m4_axisbulb['multiplier ' + k] = r; }
  const q5 = { k: 5, wob: 0.2, reach: 45, pinch: 0 }; out.m4_axisbulb.examples_multiplier_5 = [[0.02, 0.03], [0.2, 0.3], [-0.5, 0.3]].map(c => c.join() + ': ' + [0.01, 0.05, 0.1, 0.2].map(h => 'h ' + h + ' ' + (bounded('axisbulb', q5, [c[0], c[1], h], 1000) ? 'bounded' : 'escapes')).join(', ')); }

// ---- m5: Blended planes with the pinch: where does the seam half way between two planes land?
{ out.m5_softfold_seam = {};
  for (const [k, n] of [[2, 2], [2, 3], [3, 4], [2, 5]]) { let offAxis = 0, offPlane = 0, tot = 0; const g = PI / (2 * k);
    for (let i = 0; i < 500; i++) { const x = rnd() * 2 - 1, rho = 0.1 + rnd(), v = [x, rho * Math.cos(g), rho * Math.sin(g)], o = M.softfold(v, n, { planes: k, blend: 0.25, curve: 0, mix: 2 }), len = Math.hypot(...o); tot++;
      if (Math.hypot(o[1], o[2]) > 1e-9 * (1 + len)) offAxis++; offPlane = Math.max(offPlane, Math.abs(o[2] * Math.cos(g) - o[1] * Math.sin(g)) / (1 + len)); }
    out.m5_softfold_seam[k + ' planes, n = ' + n] = { seam_points: tot, land_off_the_x_axis: offAxis, worst_distance_from_the_seam_plane: sci(offPlane) }; } }

// ---- m6: which entries keep the flat set at z = 0 once a dial is moved?
{ const worst = (id, q, n) => { let w = 0, bad = 0; for (let i = 0; i < 2500; i++) { const a = rnd() * 3 - 1.5, b = rnd() * 3 - 1.5, o = M[id]([a, b, 0], n, q); const r = Math.hypot(a, b), p = Math.atan2(b, a) * n, R = Math.pow(r, n), e = Math.hypot(o[0] - R * Math.cos(p), o[1] - R * Math.sin(p), o[2]) / (1 + R); if (e > 1e-9) bad++; w = Math.max(w, e); } return { worst: sci(w), points_off_of_2500: bad }; };
  out.m6_slice = { pillow_creased_n2: worst('pillow', { layout: 0 }, 2), pillow_smooth_n2: worst('pillow', { layout: 1 }, 2), axisbulb_multiplier_1: worst('axisbulb', { k: 1, wob: 0.2, reach: 45, pinch: 0 }, 2), axisbulb_multiplier_2: worst('axisbulb', { k: 2, wob: 0.2, reach: 45, pinch: 0 }, 2), axisbulb_multiplier_4: worst('axisbulb', { k: 4, wob: 0.2, reach: 45, pinch: 0 }, 2), axisbulb_multiplier_5: worst('axisbulb', { k: 5, wob: 0.2, reach: 45, pinch: 0 }, 2) }; }

// ---- m8: the two hidden directions of the twisted square. q = z + w j, twisted copy = z + e^(2it) w j; is the 3D rule
// the product q * copy with w real (the height), reading back x, y and the length of the hidden part?
{ const qmul = (a, b) => [a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3], a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2], a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1], a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]];
  out.m8_hidden_pair_turned_together_by_twice_the_tilt = {};
  for (const sg of [1, -1]) for (const order of ['q times copy', 'copy times q']) { let w = 0; for (const tdeg of [15, 40, 90, -60]) { const t = sg * tdeg * PI / 180; for (const v of pts) { const q = [v[0], v[1], v[2], 0], cp = [v[0], v[1], v[2] * Math.cos(2 * t), v[2] * Math.sin(2 * t)]; const p = order === 'q times copy' ? qmul(q, cp) : qmul(cp, q), o = M.tilt(v, 2, { tilt: tdeg }); w = Math.max(w, Math.abs(p[0] - o[0]), Math.abs(p[1] - o[1]), Math.abs(Math.hypot(p[2], p[3]) - Math.abs(o[2]))); } }
    out.m8_hidden_pair_turned_together_by_twice_the_tilt[order + ', hidden pair turned by ' + (sg > 0 ? '+' : '−') + '2 x tilt'] = sci(w); } }
return JSON.stringify(out, null, 1);
