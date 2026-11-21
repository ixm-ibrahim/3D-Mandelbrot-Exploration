// Checker of round 12, maths, part 2: tilt 180 per power, how far the Mandelbrot solid of the twisted square
// reaches (tilt 90), the two-planes entry with its folded c, and how rough the skin is at small scales.
const L = window.squaringLab, M = L.MATH, PI = Math.PI, out = {};
let seed = 24681357;
const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const sci = x => +x.toExponential(2);
const pts3 = []; for (let i = 0; i < 2000; i++) { let v; do { v = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...v) < 0.05 || Math.hypot(...v) > 1); const s = 0.1 + 2 * rnd(); pts3.push(v.map(c => c * s / Math.hypot(...v))); }
// ---- tilt 180 against the Lathe, power by power
out.tilt180 = {};
for (const n of [2, 3, 4, 5, 8, -1, -2, 2.5]) { let wm = 0, wp = 0; for (const v of pts3) { const a = M.tilt(v, n, { tilt: 180 }), l = M.lathe(v, n, { spin: 1 }), s = 1 + Math.hypot(...l); wm = Math.max(wm, Math.hypot(a[0] - l[0], a[1] - l[1], a[2] + l[2]) / s); wp = Math.max(wp, Math.hypot(a[0] - l[0], a[1] - l[1], a[2] - l[2]) / s); } out.tilt180['n=' + n] = { against_lathe_with_z_mirrored: sci(wm), against_plain_lathe: sci(wp) }; }
// ---- |F(v)| = |v|^2 at every tilt
{ let w = 0; for (const t of [0, 15, 40, 90, 137, 180, -60]) for (const v of pts3) { const o = M.tilt(v, 2, { tilt: t }); w = Math.max(w, Math.abs(Math.hypot(...o) - (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]))); } out.length_is_squared_worst = sci(w); }
// ---- the Mandelbrot solid of the twisted square: the rule written out (checked against MATH.tilt in check1)
const mk = tdeg => { const t = tdeg * PI / 180, c2 = Math.cos(2 * t), s2 = Math.sin(2 * t), ct = Math.cos(t), st = Math.sin(t);
  return (cx, cy, cz, N, B2 = 1e6) => { let x = cx, y = cy, z = cz; for (let i = 0; i < N; i++) { const X = x * x - y * y - z * z * c2 + cx, Y = 2 * x * y + z * z * s2 + cy, Z = 2 * z * (x * ct - y * st) + cz; x = X; y = Y; z = Z; if (!(x * x + y * y + z * z < B2)) return i; } return -1; }; };
{ let w = 0; const f = mk(40); for (let i = 0; i < 300; i++) { const c = [rnd() * 2 - 1.3, rnd() * 2 - 1, rnd() * 2 - 1]; let v = c.slice(), e = -1; for (let k = 0; k < 60; k++) { v = M.tilt(v, 2, { tilt: 40 }); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; if (!(v[0] * v[0] + v[1] * v[1] + v[2] * v[2] < 1e6)) { e = k; break; } } if (e !== f(c[0], c[1], c[2], 60)) w++; } out.my_loop_against_MATH_mismatches = w; }
out.reach = {};
for (const t of [0, 40, 90, -90, 137]) {
  const f = mk(t); let far = 0, farAt = null, zmax = 0, zAt = null, n = 0, beyond2 = 0, shell = [0, 0, 0, 0];
  for (let i = 0; i < 260000; i++) { let c; do { c = [(rnd() * 2 - 1) * 2.6, (rnd() * 2 - 1) * 2.6, (rnd() * 2 - 1) * 2.6]; } while (Math.hypot(...c) > 2.6); const r = Math.hypot(...c); if (f(c[0], c[1], c[2], 300) < 0) { n++; if (r > far) { far = r; farAt = c; } if (Math.abs(c[2]) > zmax) { zmax = Math.abs(c[2]); zAt = c; } if (r > 2) beyond2++; shell[Math.min(3, Math.floor(r / 0.5))]++; } }
  // and far out, where a solid with no end would have to be: 120,000 points with 3 < |c| < 300, and the plane y = 0 on a grid
  let farOut = 0; for (let i = 0; i < 120000; i++) { const r = 3 * Math.pow(100, rnd()); let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...d) > 1 || Math.hypot(...d) < 0.1); const q = r / Math.hypot(...d); if (f(d[0] * q, d[1] * q, d[2] * q, 60) < 0) farOut++; }
  let gridMaxS = 0, gridIn = 0, band = 0, mine = 0, tot = 0; for (let i = 0; i < 700; i++) for (let j = 0; j < 300; j++) { const cx = -30 + 31 * (i + 0.5) / 700, s = 6 * (j + 0.5) / 300, b = f(cx, 0, s, 400) < 0; tot++; if (b) { gridIn++; gridMaxS = Math.max(gridMaxS, s); } const K = s * s + cx; if (b !== (K >= -2 && K <= 0.25)) band++; const reg = ((cx + 1) * (cx + 1) + s * s <= 1) || (cx >= -0.5 && s * s <= 0.25 - cx); if (b !== reg) mine++; }
  out.reach['tilt ' + t] = { bounded_of_260000_in_ball_2p6: n, farthest: +far.toFixed(3), farthestAt: farAt && farAt.map(c => +c.toFixed(2)), highest_z: +zmax.toFixed(3), highestAt: zAt && zAt.map(c => +c.toFixed(2)), bounded_beyond_radius_2: beyond2, by_shell_0p5: shell, bounded_of_120000_with_radius_3_to_300: farOut,
    plane_y0_grid: { points: tot, bounded: gridIn, highest_s: +gridMaxS.toFixed(2), disagree_with_band_between_parabolas: band, disagree_with_disc_plus_cap: mine } };
}
// ---- the two-planes entry: its c is folded too (cmap). Is the slice y = 0 of the Mandelbrot solid the flat set, and of the Julia set c = -1?
const foldk = (v, k) => { const [x, y, z] = v, rho = Math.hypot(y, z); if (rho < 1e-300) return v; const w = PI / k, psi = Math.atan2(z, y), s = psi < 0 ? -1 : 1, a = Math.abs(psi), j = Math.floor(a / w + 0.5), d = a - j * w; let a2; if (2 * j < k || (2 * j === k && d < 0)) a2 = j % 2 === 0 ? d : -d; else a2 = PI + ((k - j) % 2 === 0 ? d : -d); a2 *= s; return [x, rho * Math.cos(a2), rho * Math.sin(a2)]; };
{ let w = 0; for (const v of pts3) for (const k of [2, 3, 5]) { const a = M.fold(v, 2, { planes: k }), b = M.mercator(foldk(v, k), 2, {}); w = Math.max(w, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2])); } out.my_fold_is_the_page_fold = sci(w); }
const flatIn = (cx, cy, x0, y0, N) => { let x = x0, y = y0; for (let i = 0; i < N; i++) { const X = x * x - y * y + cx, Y = 2 * x * y + cy; x = X; y = Y; if (!(x * x + y * y < 1e6)) return false; } return true; };
out.fold_planes_carry_flat_set = {};
for (const k of [2, 3, 4]) for (let j = 0; j < k; j++) {
  const th = j * PI / k, c = Math.cos(th), s = Math.sin(th); let mm = 0, mj = 0, tot = 0, inn = 0;
  for (let i = 0; i < 3000; i++) { const a = rnd() * 2.6 - 2, b = rnd() * 2.4 - 1.2, C = foldk([a, b * c, b * s], k); let v = [0, 0, 0], e = true; for (let q = 0; q < 300; q++) { v = M.fold(v, 2, { planes: k }); v = [v[0] + C[0], v[1] + C[1], v[2] + C[2]]; if (!(Math.hypot(...v) < 1e3)) { e = false; break; } } const fl = flatIn(a, b, 0, 0, 300); tot++; if (fl) inn++; if (fl !== e) mm++;
    const p0 = [rnd() * 3.4 - 1.7, rnd() * 2 - 1]; v = [p0[0], p0[1] * c, p0[1] * s]; e = true; for (let q = 0; q < 300; q++) { v = M.fold(v, 2, { planes: k }); v = [v[0] - 1, v[1], v[2]]; if (!(Math.hypot(...v) < 1e3)) { e = false; break; } } if (flatIn(-1, 0, p0[0], p0[1], 300) !== e) mj++; }
  out.fold_planes_carry_flat_set[k + ' planes, plane at ' + Math.round(th * 180 / PI) + ' deg'] = 'Mandelbrot: ' + mm + ' of ' + tot + ' differ from the flat set (' + inn + ' inside); Julia c=-1: ' + mj + ' differ';
}
// ---- how rough is the skin? The edge of the solid along a ray from an inside point, read on 33 neighbouring rays
// that span an angle of 2h; what is left after the best cubic curve is taken away, divided by h. A smooth skin: falls
// fast as h shrinks. A fractal edge: does not fall.
const rough = (inside, base, d0, e1, N) => {
  const edge = d => { let lo = 0, hi = 4; // inside at 0, outside at 4: find a crossing by bisection, after a coarse walk outward
    let r = 0; const st = 0.02; while (r < 4 && inside(base[0] + d[0] * (r + st), base[1] + d[1] * (r + st), base[2] + d[2] * (r + st), N) < 0) r += st; lo = r; hi = r + st;
    for (let i = 0; i < 46; i++) { const m = 0.5 * (lo + hi); if (inside(base[0] + d[0] * m, base[1] + d[1] * m, base[2] + d[2] * m, N) < 0) lo = m; else hi = m; } return 0.5 * (lo + hi); };
  const res = {};
  for (const h of [3e-2, 3e-3, 3e-4, 3e-5]) { const us = [], rs = []; for (let i = 0; i < 33; i++) { const u = (i / 16 - 1), d = [d0[0] + u * h * e1[0], d0[1] + u * h * e1[1], d0[2] + u * h * e1[2]], l = Math.hypot(...d); us.push(u); rs.push(edge(d.map(c => c / l))); }
    // least squares cubic in u (normal equations, 4 x 4)
    const A = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], b = [0, 0, 0, 0]; for (let i = 0; i < 33; i++) { const p = [1, us[i], us[i] ** 2, us[i] ** 3]; for (let a = 0; a < 4; a++) { b[a] += p[a] * rs[i]; for (let c = 0; c < 4; c++) A[a][c] += p[a] * p[c]; } }
    for (let i = 0; i < 4; i++) { let piv = i; for (let r = i + 1; r < 4; r++) if (Math.abs(A[r][i]) > Math.abs(A[piv][i])) piv = r; [A[i], A[piv]] = [A[piv], A[i]]; [b[i], b[piv]] = [b[piv], b[i]]; for (let r = i + 1; r < 4; r++) { const f = A[r][i] / A[i][i]; for (let c = i; c < 4; c++) A[r][c] -= f * A[i][c]; b[r] -= f * b[i]; } }
    const co = [0, 0, 0, 0]; for (let i = 3; i >= 0; i--) { let s = b[i]; for (let c = i + 1; c < 4; c++) s -= A[i][c] * co[c]; co[i] = s / A[i][i]; }
    let ss = 0; for (let i = 0; i < 33; i++) { const f = co[0] + co[1] * us[i] + co[2] * us[i] ** 2 + co[3] * us[i] ** 3; ss += (rs[i] - f) ** 2; }
    res['h=' + h] = +(Math.sqrt(ss / 33) / h).toExponential(1); res.edge = +rs[16].toFixed(4); }
  return res;
};
const dirOf = (el, az) => { const a = el * PI / 180, b = az * PI / 180; return { d: [Math.cos(a) * Math.cos(b), Math.cos(a) * Math.sin(b), Math.sin(a)], east: [-Math.sin(b), Math.cos(b), 0], north: [-Math.sin(a) * Math.cos(b), -Math.sin(a) * Math.sin(b), Math.cos(a)] }; };
out.rough = {};
const t0 = performance.now();
for (const [name, tdeg, base] of [['twisted 40, Mandelbrot solid', 40, [-0.1, 0, 0]], ['Lathe (tilt 0), Mandelbrot solid', 0, [-0.1, 0, 0]], ['twisted -60, Mandelbrot solid', -60, [-0.1, 0, 0]]]) {
  const f = mk(tdeg), o = {};
  for (const [el, az] of [[0, 35], [0, 160], [25, 35], [25, 160], [50, 100], [50, 250], [75, 20], [-40, 200]]) {
    if (performance.now() - t0 > 150000) { o['stopped'] = 'time'; break; }
    const D = dirOf(el, az); o['height angle ' + el + ', round ' + az + ': along east'] = rough(f, base, D.d, D.east, 600); o['height angle ' + el + ', round ' + az + ': along north'] = rough(f, base, D.d, D.north, 600);
  }
  out.rough[name] = o;
}
// the same with more steps, to see that the numbers do not hang on the step count (one place)
{ const D = dirOf(25, 35); out.rough['twisted 40, height angle 25, round 35, east, 3000 steps'] = rough(mk(40), [-0.1, 0, 0], D.d, D.east, 3000); const D2 = dirOf(50, 100); out.rough['twisted 40, height angle 50, round 100, north, 3000 steps'] = rough(mk(40), [-0.1, 0, 0], D2.d, D2.north, 3000); }
out.rough_seconds = +((performance.now() - t0) / 1000).toFixed(1);
return JSON.stringify(out);
