// Checker of round 12, part 3: is the skin of the twisted square's Mandelbrot solid smooth up close, away from z = 0?
// Along rays from the inside point (-0.1, 0, 0): where the edge is for more and more steps, how many times a ray
// goes in and out, and how the edge moves from one ray to its neighbours a hair apart.
const PI = Math.PI, out = {};
const mk = tdeg => { const t = tdeg * PI / 180, c2 = Math.cos(2 * t), s2 = Math.sin(2 * t), ct = Math.cos(t), st = Math.sin(t);
  return (cx, cy, cz, N) => { let x = cx, y = cy, z = cz; for (let i = 0; i < N; i++) { const X = x * x - y * y - z * z * c2 + cx, Y = 2 * x * y + z * z * s2 + cy, Z = 2 * z * (x * ct - y * st) + cz; x = X; y = Y; z = Z; if (!(x * x + y * y + z * z < 1e6)) return i; } return -1; }; };
const base = [-0.1, 0, 0];
const dirOf = (el, az) => { const a = el * PI / 180, b = az * PI / 180; return { d: [Math.cos(a) * Math.cos(b), Math.cos(a) * Math.sin(b), Math.sin(a)], east: [-Math.sin(b), Math.cos(b), 0] }; };
const at = (f, d, r, N) => f(base[0] + d[0] * r, base[1] + d[1] * r, base[2] + d[2] * r, N) < 0;
const edge = (f, d, N, from = 0, st = 0.002) => { let r = from; while (r < 4 && at(f, d, r + st, N)) r += st; let lo = r, hi = r + st; for (let i = 0; i < 44; i++) { const m = 0.5 * (lo + hi); if (at(f, d, m, N)) lo = m; else hi = m; } return 0.5 * (lo + hi); };
const flips = (f, d, a, b, n, N) => { let k = 0, prev = at(f, d, a, N); for (let i = 1; i <= n; i++) { const now = at(f, d, a + (b - a) * i / n, N); if (now !== prev) k++; prev = now; } return k; };
const t0 = performance.now();
for (const [tdeg, places] of [[40, [[50, 250], [75, 20], [25, 35], [-40, 200], [25, 160], [50, 100], [35, 300], [60, 200], [15, 100], [-20, 60], [45, 0], [10, 250]]], [0, [[50, 250], [25, 160]]]]) {
  const f = mk(tdeg), o = {};
  for (const [el, az] of places) {
    if (performance.now() - t0 > 200000) { o.stopped = 'time'; break; }
    const D = dirOf(el, az), r = {};
    r.edge_by_steps = [14, 50, 200, 1000, 5000].map(N => N + ': ' + edge(f, D.d, N).toFixed(6)).join(', ');
    const e = edge(f, D.d, 5000);
    r.in_out_changes_along_ray_0p05_to_2p4 = flips(f, D.d, 0.05, 2.4, 6000, 1000);
    r.in_out_changes_within_1e3_of_edge = flips(f, D.d, e - 1e-3, e + 1e-3, 1000, 5000);
    r.in_out_changes_within_1e5_of_edge = flips(f, D.d, e - 1e-5, e + 1e-5, 1000, 20000);
    // 101 neighbouring rays, each 2e-5 of angle from the next: the edge on each (2000 steps), a straight line taken away
    for (const [hh, N] of [[1e-3, 2000], [1e-5, 6000]]) { const rs = []; for (let i = -50; i <= 50; i++) { const u = i / 50 * hh, d = [D.d[0] + u * D.east[0], D.d[1] + u * D.east[1], D.d[2] + u * D.east[2]], l = Math.hypot(...d); rs.push(edge(f, d.map(c => c / l), N, Math.max(0, e - 0.05))); }
      const a = (rs[100] - rs[0]) / 100; let dev = 0, wig = 0, prev = 0; for (let i = 0; i <= 100; i++) dev = Math.max(dev, Math.abs(rs[i] - (rs[0] + a * i))); for (let i = 1; i < 100; i++) { const s2 = rs[i + 1] - 2 * rs[i] + rs[i - 1]; if (Math.abs(s2) > 1e-13) { const sg = Math.sign(s2); if (prev && sg !== prev) wig++; prev = sg; } }
      r['101 rays across an angle of ' + (2 * hh) + ': edge moves by'] = +(Math.max(...rs) - Math.min(...rs)).toExponential(2) + ', off a straight line by ' + dev.toExponential(2) + ' (' + (dev / hh).toExponential(1) + ' of the width), bends back and forth ' + wig + ' times'; }
    o['height angle ' + el + ', round ' + az] = r;
  }
  out['tilt ' + tdeg] = o;
}
out.seconds = +((performance.now() - t0) / 1000).toFixed(1);
return JSON.stringify(out);
