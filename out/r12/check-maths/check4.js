// Checker of round 12, part 4: does a rule jump? Along 300 arcs on the sphere of directions (20,000 steps each) the
// largest step of the rule is found and its interval is halved 40 times. A jump keeps its size; a steep but
// unbroken stretch shrinks to nothing. "Sphere inversions, two planes" is known to jump: it is the test of the test.
const L = window.squaringLab, M = L.MATH, PI = Math.PI, out = {};
let seed = 5551212; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const unit = () => { let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...d) > 1 || Math.hypot(...d) < 0.2); const r = Math.hypot(...d); return d.map(c => c / r); };
const arcs = []; for (let i = 0; i < 80; i++) { const a = unit(); let b = unit(); const dp = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; b = b.map((c, j) => c - dp * a[j]); const l = Math.hypot(...b); arcs.push([a, b.map(c => c / l)]); }
const dist = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
const jump = (id, q, n) => { let worst = 0, at = null, count = 0;
  for (const [a, b] of arcs) { const P = t => [a[0] * Math.cos(t) + b[0] * Math.sin(t), a[1] * Math.cos(t) + b[1] * Math.sin(t), a[2] * Math.cos(t) + b[2] * Math.sin(t)], F = t => M[id](P(t), n, q);
    const K = 5000, st = 2 * PI / K; let prev = F(0), big = [];
    for (let i = 1; i <= K; i++) { const now = F(i * st), d = dist(now, prev); if (d > 0.02) big.push([d, i]); prev = now; }
    big.sort((x, y) => y[0] - x[0]);
    for (const [d0, i] of big.slice(0, 6)) { let lo = (i - 1) * st, hi = i * st, flo = F(lo), fhi = F(hi); for (let k = 0; k < 40; k++) { const m = 0.5 * (lo + hi), fm = F(m); if (dist(flo, fm) >= dist(fm, fhi)) { hi = m; fhi = fm; } else { lo = m; flo = fm; } } const d = dist(flo, fhi); if (d > 1e-3) count++; if (d > worst) { worst = d; at = P(lo).map(c => +c.toFixed(4)); } } }
  return worst > 1e-3 ? 'JUMP of ' + worst.toFixed(3) + ' (' + count + ' places on 80 arcs), for example at direction ' + JSON.stringify(at) : 'no jump (largest left after halving: ' + worst.toExponential(1) + ')'; };
const T = [
  ['fold', { planes: 2 }, 2], ['mercator', {}, 2], ['mercator', {}, 3], ['tilt', { tilt: 40 }, 2], ['tilt', { tilt: 40 }, 3], ['tilt', { tilt: 40 }, -2], ['tilt', { tilt: 40 }, 2.5],
  ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, 2], ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, 3], ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, -2], ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }, 5], ['softfold', { planes: 2, blend: 0, curve: 0, mix: 0 }, 2], ['softfold', { planes: 2, blend: 0.45, curve: 1, mix: 1 }, 2],
  ['softfold', { planes: 3, blend: 0.25, curve: 0, mix: 0 }, 2], ['softfold', { planes: 3, blend: 0.05, curve: 0, mix: 0 }, 3], ['softfold', { planes: 4, blend: 0.25, curve: 0, mix: 0 }, 5], ['softfold', { planes: 4, blend: 0.25, curve: 0, mix: 0 }, 2],
  ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 2 }, 2], ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 2 }, 3], ['softfold', { planes: 2, blend: 0.25, curve: 0, mix: 2 }, -2], ['softfold', { planes: 3, blend: 0.25, curve: 0, mix: 2 }, 2], ['softfold', { planes: 3, blend: 0.25, curve: 0, mix: 2 }, 3], ['softfold', { planes: 4, blend: 0.25, curve: 0, mix: 2 }, 5],
  ['axisbulb', { k: 1, wob: 0.2, reach: 45, pinch: 0 }, 2], ['axisbulb', { k: 5, wob: 0.2, reach: 45, pinch: 0 }, 2], ['axisbulb', { k: -3, wob: 0.6, reach: 20, pinch: 0 }, 3], ['axisbulb', { k: 2, wob: 0, reach: 45, pinch: 0 }, 2], ['axisbulb', { k: 1, wob: 0.5, reach: 0, pinch: 2 }, 2], ['axisbulb', { k: 1, wob: 0.2, reach: 45, pinch: 0 }, 2.5],
  ['pillow', { layout: 0 }, 2], ['pillow', { layout: 0 }, 3], ['pillow', { layout: 0 }, 5], ['pillow', { layout: 0 }, -1], ['pillow', { layout: 0 }, -2], ['pillow', { layout: 1 }, 2], ['pillow', { layout: 1 }, 8],
];
const t0 = performance.now();
for (const [id, q, n] of T) { if (performance.now() - t0 > 60000) { out.stopped = 'time'; break; } out[id + ' ' + JSON.stringify(q) + ' n=' + n] = jump(id, q, n); }
out.seconds = +((performance.now() - t0) / 1000).toFixed(1);
return JSON.stringify(out);
