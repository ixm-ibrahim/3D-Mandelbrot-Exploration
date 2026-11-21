const L = window.squaringLab, M = L.MATH, PI = Math.PI;
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
// complex helpers, written independently of the page
const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const cinv = a => { const d = a[0] * a[0] + a[1] * a[1]; return [a[0] / d, -a[1] / d]; };
// z^n: repeated multiplication for whole n (reciprocal for negative), principal branch otherwise
function cpow(z, n) {
  if (Number.isInteger(n)) { let o = [1, 0]; for (let k = 0; k < Math.abs(n); k++) o = cmul(o, z); return n < 0 ? cinv(o) : o; }
  const r = Math.hypot(z[0], z[1]), a = Math.atan2(z[1], z[0]), R = Math.pow(r, n); return [R * Math.cos(n * a), R * Math.sin(n * a)];
}
const sci = x => (x === 0 ? '0' : x.toExponential(2));
function planePoints(seed) {
  const rnd = rng(seed), pts = [];
  for (let i = 0; i < 100; i++) { const r = Math.exp(Math.log(0.05) + rnd() * Math.log(60)), a = (rnd() * 2 - 1) * PI; pts.push([r * Math.cos(a), r * Math.sin(a), 'generic']); }
  for (let i = 0; i < 50; i++) { const r = Math.pow(10, -6 + 4 * rnd()), a = (rnd() * 2 - 1) * PI; pts.push([r * Math.cos(a), r * Math.sin(a), 'origin']); }
  for (let i = 0; i < 46; i++) { const r = 0.1 + 2.5 * rnd(), e = Math.pow(10, -9 + 7 * rnd()) * (i % 2 ? 1 : -1); pts.push([-r, r * e, 'negx']); }
  pts.push([-1.3, 0, 'negx'], [-0.4, 0, 'negx'], [-2, 1e-300, 'negx'], [-2, -1e-300, 'negx']);
  return pts;
}
