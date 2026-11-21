// Fixer of round 12: the size of the Mandelbrot solid of the twisted square, tilt by tilt (for the sentence that
// replaces "has no end"). 80,000 random c in the ball of radius 2.2 for each tilt, 200 steps, the rule written out
// (it is checked against MATH.tilt first).
const L = window.squaringLab, M = L.MATH, PI = Math.PI, out = {};
let seed = 1357911;
const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const mk = tdeg => { const t = tdeg * PI / 180, c2 = Math.cos(2 * t), s2 = Math.sin(2 * t), ct = Math.cos(t), st = Math.sin(t);
  return (cx, cy, cz, N) => { let x = cx, y = cy, z = cz; for (let i = 0; i < N; i++) { const X = x * x - y * y - z * z * c2 + cx, Y = 2 * x * y + z * z * s2 + cy, Z = 2 * z * (x * ct - y * st) + cz; x = X; y = Y; z = Z; if (!(x * x + y * y + z * z < 1e6)) return false; } return true; }; };
{ let w = 0; for (const t of [40, 90, -75]) { const f = mk(t); for (let i = 0; i < 400; i++) { const c = [rnd() * 2 - 1.3, rnd() * 2 - 1, rnd() * 2 - 1]; let v = [0, 0, 0], e = true; for (let k = 0; k < 61; k++) { v = M.tilt(v, 2, { tilt: t }); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; if (!(v[0] * v[0] + v[1] * v[1] + v[2] * v[2] < 1e6)) { e = false; break; } } if (e !== f(c[0], c[1], c[2], 60)) w++; } } out.written_rule_against_MATH_mismatches_of_1200 = w; }
out.by_tilt = {};
for (const t of [0, 15, 30, 40, 60, 75, 90, 105, 120, 150, 180, -40, -90]) {
  const f = mk(t); let n = 0, far = 0, high = 0, beyond2 = 0;
  for (let i = 0; i < 80000; i++) { let c; do { c = [(rnd() * 2 - 1) * 2.2, (rnd() * 2 - 1) * 2.2, (rnd() * 2 - 1) * 2.2]; } while (Math.hypot(...c) > 2.2); if (f(c[0], c[1], c[2], 200)) { const r = Math.hypot(...c); n++; far = Math.max(far, r); high = Math.max(high, Math.abs(c[2])); if (r > 2) beyond2++; } }
  // the top of the solid, looked for more closely: 60,000 points with a height of 0.6 to 1.6
  for (let i = 0; i < 60000; i++) { const c = [rnd() * 3 - 2, rnd() * 3 - 1.5, 0.6 + rnd()]; if (f(c[0], c[1], c[2], 200)) high = Math.max(high, c[2]); }
  out.by_tilt['tilt ' + t] = 'bounded ' + n + ' of 80000, farthest from the centre ' + far.toFixed(2) + ', highest ' + high.toFixed(2) + ', beyond radius 2: ' + beyond2;
}
return JSON.stringify(out, null, 1);
