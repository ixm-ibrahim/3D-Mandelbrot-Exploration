// Scratch copy of the pillow maths with every lift that was tried (the app file keeps only the chosen one).
const PI = Math.PI, clamp = (x, a, b) => Math.min(Math.max(x, a), b);
const PIL_R3 = Math.sqrt(3), PIL_T = 2 * PI / 3;
let LIFT = { kind: 'quad', k: 1 }, NEWTON = 8;

// q = 1 - |H|^2  ->  [z, s] with (x, y) = s * H
function liftZ(q) {
  if (LIFT.kind === 'ortho') return [Math.sqrt(q), 1];
  if (LIFT.kind === 'equi') {
    const rho = Math.sqrt(Math.max(1 - q, 0)), om = q / (1 + rho);
    return [Math.sin(PI / 2 * om), rho > 1e-9 ? Math.cos(PI / 2 * om) / rho : PI / 2];
  }
  const k = LIFT.k, z = q * (k + (1 - k) * q);
  return [z, Math.sqrt((1 + (1 - k) * q) * (1 + z))];
}
// z  ->  [q, s] with H = s * (x, y)
function liftQ(z) {
  if (LIFT.kind === 'ortho') return [z * z, 1];
  if (LIFT.kind === 'equi') {
    const om = 2 / PI * Math.asin(z), rho = 1 - om, sn = Math.sqrt(Math.max(1 - z * z, 0));
    return [om * (1 + rho), sn > 1e-9 ? rho / sn : 2 / PI];
  }
  const k = LIFT.k, q = 2 * z / (k + Math.sqrt(k * k + 4 * (1 - k) * z));
  return [q, 1 / Math.sqrt((1 + (1 - k) * q) * (1 + z))];
}
// The layout seen from its heaviest corner, taken as A: weights w1, w2 of the next two corners -> [hx, hy, 1 - |h|^2].
// Written so that nothing cancels next to the two edges that meet at that corner.
function pilLay(w1, w2) {
  const b = PIL_T * w1, g = PIL_T * w2, sh = (b + g) / 2;
  const S = Math.sin(sh), C = Math.cos(sh), D = 2 / PIL_R3 * Math.sin(b / 2) * Math.sin(g / 2);
  return [1 - 2 * S * (S + D), 2 * C * Math.sin((b - g) / 2),
    4 * (C * C * Math.sin(b) * Math.sin(g) + S * D * (1 - 2 * S * S - S * D))];
}
function pilPhi(ux, uy) {
  const b = uy * 2 / PIL_R3, a = ux + b / 2, i = Math.floor(a), j = Math.floor(b), fa = a - i, fb = b - j;
  const up = fa >= fb, k = (((i + j) % 3) + 3) % 3;
  const w = up ? [1 - fa, fa - fb, fb] : [1 - fb, fb - fa, fa];     // weights of the colours k, k + 1, k + 2
  let m = 0; if (w[1] > w[m]) m = 1; if (w[2] > w[m]) m = 2;
  const [hx, hy, q] = pilLay(w[(m + 1) % 3], w[(m + 2) % 3]);
  const c = (k + m) % 3, [z, s] = liftZ(clamp(q, 0, 1));
  const cs = c === 0 ? 1 : -0.5, sn = c === 0 ? 0 : c === 1 ? PIL_R3 / 2 : -PIL_R3 / 2;
  return [s * (cs * hx - sn * hy), s * (sn * hx + cs * hy), up ? -z : z];
}
let lastIters = 0;
function pilPhiInv(dx, dy, dz) {
  const [q, s] = liftQ(Math.min(Math.abs(dz), 1));
  let hx = dx * s, hy = dy * s, c = 0;
  if (Math.abs(hy) > PIL_R3 * hx) {
    c = hy > 0 ? 1 : 2;
    const t = c === 1 ? PIL_R3 / 2 : -PIL_R3 / 2;
    [hx, hy] = [-0.5 * hx + t * hy, -t * hx - 0.5 * hy];
  }
  const T = (hy * hy + q) / (1 + hx);
  let p = Math.min(Math.sqrt(T / 2), 0.8);
  lastIters = 0;
  for (let it = 0; it < NEWTON; it++) {
    const ss = Math.sqrt(1 - p * p), e = hy * hy / (4 * ss * ss), cc = Math.sqrt(Math.max(1 - e, 1e-12));
    const f = 2 * p * p + 2 / PIL_R3 * p * (cc - ss) - T;
    const df = 4 * p + 2 / PIL_R3 * ((cc - ss) + p * p * (1 / ss - e / (cc * ss * ss)));
    if (!(df > 1e-300)) break;
    const step = f / df;
    p = clamp(p - step, 0, 0.8); lastIters++;
    if (Math.abs(step) < 1e-15) break;
  }
  const ss = Math.sqrt(1 - p * p), sh = Math.asin(p), th = Math.asin(clamp(hy / (2 * ss), -p, p));
  const w1 = (sh + th) / PIL_T, w2 = (sh - th) / PIL_T, w0 = 1 - w1 - w2;
  const lB = c === 0 ? w1 : c === 1 ? w0 : w2, lC = c === 0 ? w2 : c === 1 ? w1 : w0;
  return [lB + lC / 2, (dz >= 0 ? -1 : 1) * lC * PIL_R3 / 2];
}
function pilDir(d, n) { const u = pilPhiInv(d[0], d[1], d[2]); return pilPhi(n * u[0], n * u[1]); }
function pillow(v, n) {
  const k = Math.round(n), r = Math.hypot(v[0], v[1], v[2]);
  if (r < 1e-20 && k > 0) return [0, 0, 0];
  const d = r > 0 ? [v[0] / r, v[1] / r, v[2] / r] : [1, 0, 0], o = pilDir(d, k), R = Math.pow(r, k);
  return [R * o[0], R * o[1], R * o[2]];
}
