// ---------- approaches. Each one defines a product mul(a, b) and a power pw(a, n) on points of space;
// every one except "classic" collapses to complex arithmetic in the plane z = 0.
//
// Powers may be negative or fractional. Every result is kept finite: a pole (the origin under a negative
// power) and a runaway orbit both stop at a length of about 1.7e18, which the renderer's 32-bit numbers
// can still square. e^42 sits just above 64^10: the escape radius raised to the largest power on the dial.
const APR_LOGCAP = 42;
const aprPow = (r, n) => Math.exp(Math.min(n * Math.log(Math.max(r, 1e-30)), APR_LOGCAP));
const aprRad = deg => (deg || 0) * PI / 180;

// Fold the spin angle around the x-axis so the nearest of k planes through that axis lands on the
// xy-plane (keeping the y > 0 and y < 0 halves apart, which the flat dynamics needs).
function foldk(v, k) {
  if (k < 1.5) return v;
  const [x, y, z] = v, rho = Math.hypot(y, z);
  if (rho < 1e-300) return v;
  const w = PI / k, psi = Math.atan2(z, y), s = psi < 0 ? -1 : 1, a = Math.abs(psi);
  const j = Math.floor(a / w + 0.5), d = a - j * w;
  let a2;
  if (2 * j < k || (2 * j === k && d < 0)) a2 = j % 2 === 0 ? d : -d;
  else a2 = PI + ((k - j) % 2 === 0 ? d : -d);
  a2 *= s;
  return [x, rho * Math.cos(a2), rho * Math.sin(a2)];
}
// ---------- helpers of the three rules that were tried and failed (group 'tried'; ported from out/lab2/)
// Blended planes. sfDir: the direction of the one-plane power of the unit direction d.
const sfDir = (d, n) => {
  if (n === 2) { const q = 1 + d[2] * d[2]; return [(d[0] * d[0] - d[1] * d[1]) / q, 2 * d[0] * d[1] / q, 2 * d[2] / q]; }
  const Z = clamp(d[2], -0.999999, 0.999999), m = clamp(n * Math.atanh(Z), -20, 20), p = Math.atan2(d[1], d[0]) * n, h = 1 / Math.cosh(m);
  return [h * Math.cos(p), h * Math.sin(p), Math.tanh(m)];
};
// sfStep: the blend weight. t in [0, 1] is how far the half-plane of the point has turned from one plane to the
// next; the weight stays 0 for the first `a` of the way, 1 for the last `a`, and rises smoothly in between.
const sfStep = (t, a, curve) => {
  const q = clamp((t - a) / (1 - 2 * a), 0, 1);
  return curve > 0.5 ? q * q * q * (q * (6 * q - 15) + 10) : q * q * (3 - 2 * q);
};
// Bulbs about the axis: the quaternion power, then the turn around the x-axis is changed.
//   turn G = k * g + A * W * sin(4g),   g the turn of the result, W = smoothstep of sin(angle from the x-axis) / sin(reach)
// e^(ig) is raised to the whole power k by repeated complex multiplication and sin(4g) is the polynomial
// 4cs(c^2 - s^2), so a point with z = 0 (or y = 0, for k = 1 mod 4) comes out with z = 0 (y = 0) to the last bit.
// That matters: for |k| > 1 the turn pushes away from those planes, and a rounding leak would grow.
function axbTurn(w, q) {
  const k = Math.round(q.k === undefined ? 1 : q.k), A = q.wob || 0, B = q.pinch || 0;
  if (k === 1 && A === 0 && B === 0) return w;
  const rho = Math.hypot(w[1], w[2]);
  if (!(rho > 0)) return w;
  const c = w[1] / rho, s = w[2] / rho;
  let a = 1, b = 0;
  for (let i = 0; i < Math.abs(k); i++) [a, b] = [a * c - b * s, a * s + b * c];
  if (k < 0) b = -b;
  const r = Math.hypot(w[0], rho), s2 = 2 * c * s;       // s2 = sin(2 * turn): zero on the planes z = 0 and y = 0
  if (A !== 0) {
    const sr = Math.sin(aprRad(q.reach));
    const t = sr > 1e-6 ? clamp(rho / (r * sr), 0, 1) : 1, ang = A * t * t * (3 - 2 * t) * 2 * s2 * (c * c - s * s);
    const ca = Math.cos(ang), sa = Math.sin(ang);
    [a, b] = [a * ca - b * sa, a * sa + b * ca];
  }
  // the pinch: between the two planes the result is made longer, by 1 + B sin^2(2 turn) sin^2(angle from the x-axis)
  if (B === 0) return [w[0], rho * a, rho * b];
  const g = 1 + B * s2 * s2 * (rho / r) * (rho / r), o = [g * w[0], g * rho * a, g * rho * b];
  const m = Math.max(Math.abs(o[0]), Math.abs(o[1]), Math.abs(o[2])), cap = 1.74e18;      // aprCap in the shader
  return m > cap ? scl(o, cap / m) : o;
}
// Pillow, smooth layout. Direction map w -> (2w^3 - 1) / (w (2 - w^3)), w = (x + iy)/(1 - z), worked in the chart
// of the lower half sphere, w = (x + iy)/(1 + |z|), |w| <= 1. The map commutes with the mirror z -> -z, so the
// upper half is the mirror image. N/D is kept as a pair, so nothing is ever divided by 0.
function psDir(d) {
  const s = 1 + Math.abs(d[2]), wx = d[0] / s, wy = d[1] / s;
  const ax = wx * wx - wy * wy, ay = 2 * wx * wy, cx = ax * wx - ay * wy, cy = ax * wy + ay * wx;   // w^3
  const Nx = 2 * cx - 1, Ny = 2 * cy, ex = 2 - cx, ey = -cy, Dx = wx * ex - wy * ey, Dy = wx * ey + wy * ex;
  const nn = Nx * Nx + Ny * Ny, dd = Dx * Dx + Dy * Dy, q = nn + dd;
  const Z = d[2] === 0 ? 0 : (d[2] > 0 ? dd - nn : nn - dd) / q;
  return [2 * (Nx * Dx + Ny * Dy) / q, 2 * (Ny * Dx - Nx * Dy) / q, Z];
}
const psReps = n => (n < 1.5 ? 0 : n < 3 ? 1 : n < 6 ? 2 : 3);   // the map is applied 1, 2 or 3 times: powers 2, 4, 8
function psPower(v, n) {
  const k = psReps(n), r = Math.hypot(v[0], v[1], v[2]);
  if (k === 0) return [v[0], v[1], v[2]];
  if (r < 1e-20) return [0, 0, 0];
  let d = [v[0] / r, v[1] / r, v[2] / r];
  for (let j = 0; j < k; j++) d = psDir(d);
  const R = aprPow(r, 2 ** k);
  return [R * d[0], R * d[1], R * d[2]];
}
// Pillow, creased layout: the flat triangle laid along rays from its centre (polar angle in step with the distance
// from the centre), then slid along the half circles through (0, +-1, 0) so that the centre sits at 120 degrees in
// the x-z plane. That lays the circle y = 0 at constant speed too, so both z = 0 and y = 0 are exact.
const PB_T3 = 2 * PI / 3, PB_S3 = Math.sqrt(3);
function pbSlide(x, y, z) {
  const c = Math.hypot(x, z);
  if (c < 1e-300) return [x, y, z];
  if (x >= 0) { const a = (4 / 3) * Math.atan2(z, x); return [c * Math.cos(a), y, c * Math.sin(a)]; }
  const b = (2 / 3) * Math.atan2(z, -x); return [-c * Math.cos(b), y, c * Math.sin(b)];
}
function pbUnslide(x, y, z) {
  const c = Math.hypot(x, z);
  if (c < 1e-300) return [x, y, z];
  if (z + PB_S3 * x >= 0) { const a = 0.75 * Math.atan2(z, x); return [c * Math.cos(a), y, c * Math.sin(a)]; }
  const b = 1.5 * Math.atan2(z, -x); return [-c * Math.cos(b), y, c * Math.sin(b)];
}
// weights (lA, lB, lC) -> unit direction with z >= 0
function pbLayout(l) {
  const mn = Math.min(l[0], l[1], l[2]), e = 3 * mn, s = 1 - e;        // s: 0 at the centre, 1 on the boundary
  const k = l[2] <= l[0] && l[2] <= l[1] ? 0 : l[0] <= l[1] ? 1 : 2;   // the edge the ray from the centre meets
  const t = s > 1e-12 ? clamp((l[(k + 1) % 3] - mn) / s, 0, 1) : 0.5;  // where on that edge
  const z = Math.sin(0.5 * PI * e), rho = Math.cos(0.5 * PI * e), tau = PB_T3 * (k + t);
  return pbSlide(rho * Math.cos(tau), rho * Math.sin(tau), z);
}
// the same backwards: a unit direction with z >= 0 -> weights
function pbInverse(x0, y0, z0) {
  let [x, y, z] = pbUnslide(x0, y0, z0);
  z = clamp(z, 0, 1);
  const e = Math.atan2(z, Math.hypot(x, y)) * 2 / PI;
  let a = (x === 0 && y === 0 ? 0 : Math.atan2(y, x)) / PB_T3;
  if (a < 0) a += 3;
  const k = Math.min(Math.floor(a), 2), t = a - k, l = [e / 3, e / 3, e / 3];
  l[k] += (1 - e) * (1 - t); l[(k + 1) % 3] += (1 - e) * t;
  return l;
}
// v^n = |v|^n * Phi(n * PhiInv(v/|v|)), n rounded to a whole number; the sheet is held in three coordinates
// (XA, XB, XC): the weights of the triangle with the corner A at the origin, continued over the whole sheet.
function pbPower(v, n) {
  const m = Math.round(n), [x, y, z] = v, r = Math.hypot(x, y, z);
  if (m === 0) return [1, 0, 0];
  if (r < 1e-20) return m > 0 ? [0, 0, 0] : [aprPow(r, m), 0, 0];
  const l = pbInverse(x / r, y / r, Math.abs(z) / r);
  const X = z >= 0 ? l : [l[0] + l[2], l[1] + l[2], -l[2]];           // below the equator: the mirror image in the edge AB
  const Y = [m * X[0] - (m - 1), m * X[1], m * X[2]];                 // times m about the corner A
  const i = Y.map(Math.floor), f = Y.map((c, j) => c - i[j]);
  const sum = f[0] + f[1] + f[2], flip = sum > 1.5 && sum < 2.5;
  const k = (((i[1] - i[2]) % 3) + 3) % 3, g = sum < 0.5 || sum >= 2.5 ? [1, 0, 0] : flip ? [1 - f[0], 1 - f[2], 1 - f[1]] : f, wt = [0, 0, 0];
  for (let j = 0; j < 3; j++) wt[(k + j) % 3] = g[j];
  const d = pbLayout(wt), R = aprPow(r, m);
  return [R * d[0], R * d[1], z === 0 ? 0 : flip ? -R * d[2] : R * d[2]];
}
// The power maps in JavaScript: MATH[id](v, n, q) with q the approach's parameter object. They mirror the
// shader code below line for line, so what the scorecard measures is what the picture shows.
const MATH = {
  // one plane: the rule itself
  mercator(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const Z = r > 0 ? clamp(z / r, -0.999999, 0.999999) : 0;
    const m = clamp(n * Math.atanh(Z), -20, 20) + (q.lift || 0), h = 1 / Math.cosh(m);
    const R = aprPow(r, n), p = Math.atan2(y, x) * n + aprRad(q.turn);
    return [R * h * Math.cos(p), R * h * Math.sin(p), R * Math.tanh(m)];
  },
  // two or more planes (the earlier version): the fold, then the one-plane rule. No turn: the fold relies on
  // the mirror symmetry y -> -y, which a turn breaks.
  fold(v, n, q = {}) {
    return MATH.mercator(foldk(v, Math.max(2, q.planes || 2)), n, { lift: q.lift });
  },
  lathe(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const rho = Math.hypot(y, z), a = Math.atan2(rho, x) * n, R = aprPow(r, n), p = Math.atan2(z, y) * (q.spin || 1);
    return [R * Math.cos(a), R * Math.sin(a) * Math.cos(p), R * Math.sin(a) * Math.sin(p)];
  },
  // The twisted quaternion square: the quaternion power measured from an axis tilted inside the plane z = 0.
  // With A the turn by the tilt about the z-axis and L the quaternion power: v^n = A^(-n) L^n A (v).
  // In the plane z = 0 a turn is multiplication by e^(i tilt), so (e^(it) z)^n e^(-int) = z^n at every tilt.
  tilt(v, n, q = {}) {
    const t = aprRad(q.tilt), rz = (p, a) => [Math.cos(a) * p[0] - Math.sin(a) * p[1], Math.sin(a) * p[0] + Math.cos(a) * p[1], p[2]];
    return rz(MATH.lathe(rz(v, t), n, {}), -n * t);
  },
  bulb(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const b = Math.atan2(z, Math.hypot(x, y)) * n + aprRad(q.lat), p = Math.atan2(y, x) * n + aprRad(q.lon), R = aprPow(r, n);
    return [R * Math.cos(b) * Math.cos(p), R * Math.cos(b) * Math.sin(p), R * Math.sin(b)];
  },
  classic(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const t = Math.atan2(Math.hypot(x, y), z) * n + aprRad(q.theta), p = Math.atan2(y, x) * n + aprRad(q.phi), R = aprPow(r, n);
    return [R * Math.sin(t) * Math.cos(p), R * Math.sin(t) * Math.sin(p), R * Math.cos(t)];
  },
  // A negative power is the positive power followed by one sphere inversion with a mirror (y -> -y), which
  // is what a reciprocal is in every other approach. Taken side by side, (1/(x + iy), 1/z) has no value on
  // the plane z = 0 or on the z-axis, so everything near them would be thrown to infinity. This form is
  // finite everywhere except the origin, and in the plane z = 0 it is still complex z^n exactly.
  split(v, n) {
    if (n < 0) {
      const u = MATH.split(v, -n), L = len(u), most = Math.exp(APR_LOGCAP);
      if (!(L * most > 1)) return [most, 0, 0];
      return [u[0] / L / L, -u[1] / L / L, u[2] / L / L];
    }
    const [x, y, z] = v, rho = Math.hypot(x, y), az = Math.abs(z), p = Math.atan2(y, x) * n;
    const R = rho < 1e-20 && n > 0 ? 0 : aprPow(rho, n);
    return [R * Math.cos(p), R * Math.sin(p), az > 0 ? aprPow(az, n) * (z < 0 ? Math.cos(PI * n) : 1) : 0];
  },
  // ----- tried, and kept for the record
  // Blended planes: the one-plane rule is kept exactly on each of p planes through the x-axis, and between two
  // neighbouring planes the two answers are blended along the great circle between their directions.
  softfold(v, n, q = {}) {
    const k = Math.round(q.planes === undefined ? 2 : q.planes), r = Math.hypot(v[0], v[1], v[2]);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const R = aprPow(r, n);
    let d = r > 0 ? [v[0] / r, v[1] / r, v[2] / r] : [1, 0, 0], fl = 1;
    // the half turn about the x-axis commutes with the rule: work in the half z > 0 (or z = 0, y >= 0)
    if (k > 1 && (d[2] < 0 || (d[2] === 0 && d[1] < 0))) { d = [d[0], -d[1], -d[2]]; fl = -1; }
    let s = 0, ct = 1, st = 0, cw = 1, sw = 0, cj = 1, sj = 0, pa = d, D, pz = 0, sd = 1;
    const pinch = q.mix > 1.5;
    const rho = Math.hypot(d[1], d[2]);
    if (k > 1 && d[2] !== 0 && rho > 1e-15) {               // on z = 0, and on the x-axis where every plane agrees, the first plane's rule is the answer
      const w = PI / k, u = Math.atan2(d[2], d[1]) / w, j = Math.min(Math.floor(u), k - 1), t = u - j;
      const a = clamp(q.blend || 0, 0, 0.49);
      s = sfStep(t, a, q.curve || 0);
      if (pinch) {                                          // only the nearer plane answers; pz is how far it is pulled to the seam's target
        pz = sfStep((Math.min(t, 1 - t) - a) / (0.5 - a), 0, q.curve || 0);
        s = t < 0.5 ? 0 : 1; sd = t < 0.5 ? 1 : -1;
      }
      ct = Math.cos(t * w); st = Math.sin(t * w); cw = Math.cos(w); sw = Math.sin(w);
      pa = [d[0], rho * ct, rho * st];                      // the point as plane j sees it
      cj = (d[1] * ct + d[2] * st) / rho; sj = (d[2] * ct - d[1] * st) / rho;   // the turn that puts plane j back
    }
    let A = [0, 0, 0], B = [0, 0, 0];
    if (s < 1) A = sfDir(pa, n);
    if (s > 0) {                                            // the same point as plane j + 1 sees it, and its answer turned back by one step
      const b = sfDir([d[0], rho * (ct * cw + st * sw), rho * (st * cw - ct * sw)], n);
      B = [b[0], b[1] * cw - b[2] * sw, b[1] * sw + b[2] * cw];
    }
    if (pinch) {
      // The seam half way between two planes is a mirror of the rule, so it can only land on itself. An even power
      // sends it to the x-axis (the one place the two plane answers can meet without the map folding over at
      // n = 2); an odd power keeps its angle from the x-axis.
      if (s > 0.5) A = B;
      const odd = Math.abs(Math.abs(n) % 2 - 1) < 1e-3, h = 0.5 * PI / k, g = n < 0 ? -1 : 1;
      const ch = Math.cos(h), sh = Math.sin(h);
      // the seam's direction as plane j sees it: half a step on for the first plane, half a step back from the second
      B = odd ? [d[0], g * rho * (sd > 0 ? ch : cw * ch + sw * sh), g * rho * (sd > 0 ? sh : sw * ch - cw * sh)] : [1, 0, 0];
      s = pz;
    }
    if (s <= 0) D = A;
    else if (s >= 1) D = B;
    else if (q.mix > 0.5 && !pinch) {                       // straight blend, renormalised
      const m = [A[0] + s * (B[0] - A[0]), A[1] + s * (B[1] - A[1]), A[2] + s * (B[2] - A[2])], lm = Math.hypot(m[0], m[1], m[2]);
      D = lm < 1e-3 ? (s < 0.5 ? A : B) : [m[0] / lm, m[1] / lm, m[2] / lm];
    } else {                                                // along the great circle from A to B
      const c = clamp(A[0] * B[0] + A[1] * B[1] + A[2] * B[2], -1, 1), e = [B[0] - c * A[0], B[1] - c * A[1], B[2] - c * A[2]], le = Math.hypot(e[0], e[1], e[2]);
      if (c < 0 && le < 1e-3) D = s < 0.5 ? A : B;          // opposite directions: no one great circle joins them, take the nearer plane's
      else { const om = Math.atan2(le, c) * s, g = Math.sin(om) / Math.max(le, 1e-30), cs = Math.cos(om); D = [cs * A[0] + g * e[0], cs * A[1] + g * e[1], cs * A[2] + g * e[2]]; }
    }
    return [R * D[0], R * fl * (D[1] * cj - D[2] * sj), R * fl * (D[1] * sj + D[2] * cj)];
  },
  // Bulbs about the axis: the quaternion power, then the turn around the x-axis is changed (see axbTurn).
  axisbulb(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const rho = Math.hypot(y, z), a = Math.atan2(rho, x) * n, R = aprPow(r, n), sa = Math.sin(a);
    const u = rho > 0 ? [y / rho, z / rho] : [1, 0];     // the direction of (y, z) by division, not by angle: exact on the planes
    return axbTurn([R * Math.cos(a), R * sa * u[0], R * sa * u[1]], q);
  },
  // Pillow: a flat sheet of triangles wrapped onto the sphere of directions, in one of two layouts.
  pillow(v, n, q = {}) { return q.layout > 0.5 ? psPower(v, n) : pbPower(v, n); },
};
// The sphere-inversion power written out literally: n + 1 inversions, added (see notes/inversions.md).
//   v^n = |v|^n * [ 1 + n * inv( sum_k R_k inv(d - w_k) ) ],   d = v / |v|
// with w_k the n-th roots of unity on the unit circle of the xy-plane, R_k the turn about the z-axis by the
// angle of w_k, and inv(q) = (x, -y, -z) / |q|^2. Whole n only; a negative n takes one more inversion.
// The lab draws with the closed form (MATH.mercator, one plane). This is kept so the two can be compared.
function inversionPower(v, n) {
  const inv = q => { const r2 = Math.max(dot(q, q), 1e-300); return [q[0] / r2, -q[1] / r2, -q[2] / r2]; };
  const m = Math.abs(Math.round(n)), r = len(v);
  if (m === 0) return [1, 0, 0];
  const d = scl(v, 1 / r);
  let s = [0, 0, 0];
  for (let k = 0; k < m; k++) {
    const t = 2 * PI * k / m, cs = Math.cos(t), sn = Math.sin(t), q = inv(sub(d, [cs, sn, 0]));
    s = add(s, [cs * q[0] - sn * q[1], sn * q[0] + cs * q[1], q[2]]);
  }
  const out = add([1, 0, 0], scl(inv(s), m));
  return scl(n < 0 ? inv(out) : out, Math.pow(r, n));
}

// Shader side. Shared by every approach: finite powers, and helpers the formula compiler relies on.
const GL_APR = `
const float APR_LOGCAP = 42.0, APR_CAP = 1.74e18;
float aprPow(float r, float n){ return exp(min(n * log(max(r, 1e-30)), APR_LOGCAP)); }
vec3 aprCap(vec3 v){ float m = max(abs(v.x), max(abs(v.y), abs(v.z))); return m > APR_CAP ? v * (APR_CAP / m) : v; }
float aprDiv(float a, float b){ return a / (abs(b) < 1e-6 ? (b < 0.0 ? -1e-6 : 1e-6) : b); }
float aprSPow(float a, float b){
  if (abs(a) < 1e-30 && b > 0.0) return 0.0;
  return aprPow(abs(a), b) * (a < 0.0 ? cos(PI * b) : 1.0);
}`;
// The one-plane rule, shared by "Sphere inversions, one plane" and "Sphere inversions, two planes".
// aprTurn() and aprLift() are defined by each of the two, because their dials sit in different slots of uA.
const GL_MERC_CORE = `
vec3 aprMmul(vec3 a, vec3 b){
  float ra = length(a), rb = length(b);
  if (ra < 1e-20 || rb < 1e-20) return vec3(0.0);
  float Za = a.z / ra, Zb = b.z / rb;
  float Z = clamp((Za + Zb) / max(1.0 + Za * Zb, 1e-6), -1.0, 1.0);
  float la = length(a.xy), lb = length(b.xy);
  vec2 u = la > 0.0 && lb > 0.0 ? cmul(a.xy / la, b.xy / lb) : vec2(1.0, 0.0);
  return min(ra * rb, APR_CAP) * vec3(sqrt(max(0.0, 1.0 - Z * Z)) * u, Z);
}
// Longitude and Mercator latitude times n, then the turn and the lift.
vec3 aprMpw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float Z = r > 0.0 ? clamp(v.z / r, -0.999999, 0.999999) : 0.0;
  float m = clamp(n * atanh(Z), -20.0, 20.0) + aprLift();
  float p = at2(v.y, v.x) * n + aprTurn();
  return aprPow(r, n) * vec3(vec2(cos(p), sin(p)) / cosh(m), tanh(m));
}
vec3 aprMsq(vec3 v){
  float r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  return aprCap((r2 / (r2 + v.z * v.z)) * vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, 2.0 * sqrt(r2) * v.z));
}`;
// uA.x: the turn in degrees. uA.y: the lift.
const GL_MERCATOR = GL_APR + `
float aprTurn(){ return radians(uA.x); }
float aprLift(){ return uA.y; }` + GL_MERC_CORE + `
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return aprMpw(a, n); }
vec3 sqr(vec3 a){ return uA.x == 0.0 && uA.y == 0.0 ? aprMsq(a) : aprMpw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// uA.x: the number of planes (2 or more). uA.y: the lift. No turn: the folds rely on the mirror symmetry
// y -> -y, which a turn breaks.
const GL_FOLD = GL_APR + `
float aprTurn(){ return 0.0; }
float aprLift(){ return uA.y; }
vec3 aprFold(vec3 v){
  float k = max(uA.x, 2.0);
  float rho = length(v.yz);
  if (rho < 1e-20) return v;
  float w = PI / k, psi = atan(v.z, v.y), s = psi < 0.0 ? -1.0 : 1.0, a = abs(psi);
  float j = floor(a / w + 0.5), d = a - j * w, a2;
  if (2.0 * j < k - 0.5 || (abs(2.0 * j - k) < 0.5 && d < 0.0)) a2 = mod(j, 2.0) < 0.5 ? d : -d;
  else a2 = PI + (mod(k - j, 2.0) < 0.5 ? d : -d);
  a2 *= s;
  return vec3(v.x, rho * cos(a2), rho * sin(a2));
}` + GL_MERC_CORE + `
vec3 mul(vec3 a, vec3 b){ return aprMmul(aprFold(a), aprFold(b)); }
vec3 pw(vec3 a, float n){ return aprMpw(aprFold(a), n); }
vec3 sqr(vec3 a){ return uA.y == 0.0 ? aprMsq(aprFold(a)) : aprMpw(aprFold(a), 2.0); }
vec3 cmap(vec3 c){ return aprFold(c); }`;
const GL_LATHE = GL_APR + `
vec3 aprSpin(vec3 v){
  if (uA.x == 1.0) return v;
  float rho = length(v.yz);
  if (rho < 1e-20) return v;
  float p = atan(v.z, v.y) * uA.x;
  return vec3(v.x, rho * cos(p), rho * sin(p));
}
vec3 mul(vec3 a, vec3 b){ return aprSpin(aprCap(vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz))); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float rho = length(v.yz), a = at2(rho, v.x) * n;
  vec2 u = rho > 0.0 ? v.yz / rho : vec2(1.0, 0.0);
  return aprSpin(aprPow(r, n) * vec3(cos(a), sin(a) * u));
}
vec3 sqr(vec3 v){ return aprSpin(aprCap(vec3(v.x * v.x - dot(v.yz, v.yz), 2.0 * v.x * v.yz))); }
vec3 cmap(vec3 c){ return c; }`;
// uA.x: the tilt in degrees. The quaternion power, measured from an axis turned by the tilt inside the plane
// z = 0, and the result turned back (see MATH.tilt).
const GL_TILT = GL_APR + `
vec3 aprRz(vec3 v, float a){ float c = cos(a), s = sin(a); return vec3(c * v.x - s * v.y, s * v.x + c * v.y, v.z); }
vec3 aprLmul(vec3 a, vec3 b){ return vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz); }
vec3 mul(vec3 a, vec3 b){ float t = radians(uA.x); return aprCap(aprRz(aprLmul(aprRz(a, t), aprRz(b, t)), -2.0 * t)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float t = radians(uA.x);
  vec3 u = aprRz(v, t);
  float rho = length(u.yz), a = at2(rho, u.x) * n;
  vec2 d = rho > 0.0 ? u.yz / rho : vec2(1.0, 0.0);
  return aprRz(aprPow(r, n) * vec3(cos(a), sin(a) * d), -n * t);
}
vec3 sqr(vec3 v){
  float t = radians(uA.x);
  vec3 u = aprRz(v, t);
  return aprCap(aprRz(vec3(u.x * u.x - dot(u.yz, u.yz), 2.0 * u.x * u.yz), -2.0 * t));
}
vec3 cmap(vec3 c){ return c; }`;
// uA.x, uA.y: phases in degrees, added to the latitude and the longitude after they are multiplied
const GL_BULB = GL_APR + `
vec3 aprSph(float r, float be, float ph){ float cb = cos(be); return r * vec3(cb * cos(ph), cb * sin(ph), sin(be)); }
vec3 mul(vec3 a, vec3 b){ return aprSph(min(length(a) * length(b), APR_CAP), at2(a.z, length(a.xy)) + at2(b.z, length(b.xy)), at2(a.y, a.x) + at2(b.y, b.x)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  return aprSph(aprPow(r, n), at2(v.z, length(v.xy)) * n + radians(uA.x), at2(v.y, v.x) * n + radians(uA.y));
}
vec3 sqr(vec3 v){
  if (uA.x != 0.0 || uA.y != 0.0) return pw(v, 2.0);
  float rho2 = dot(v.xy, v.xy), z2 = v.z * v.z;
  if (rho2 <= 0.0) return vec3(-min(z2, APR_CAP), 0.0, 0.0);
  float k = (rho2 - z2) / rho2;
  return aprCap(vec3(k * (v.x * v.x - v.y * v.y), k * 2.0 * v.x * v.y, 2.0 * sqrt(rho2) * v.z));
}
vec3 cmap(vec3 c){ return c; }`;
// uA.x, uA.y: phases in degrees, added to the angle from the z-axis and the angle around it
const GL_CLASSIC = GL_APR + `
vec3 aprSph(float r, float th, float ph){ float st = sin(th); return r * vec3(st * cos(ph), st * sin(ph), cos(th)); }
vec3 mul(vec3 a, vec3 b){ return aprSph(min(length(a) * length(b), APR_CAP), at2(length(a.xy), a.z) + at2(length(b.xy), b.z), at2(a.y, a.x) + at2(b.y, b.x)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  return aprSph(aprPow(r, n), at2(length(v.xy), v.z) * n + radians(uA.x), at2(v.y, v.x) * n + radians(uA.y));
}
vec3 sqr(vec3 v){ return pw(v, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
const GL_SPLIT = GL_APR + `
vec3 mul(vec3 a, vec3 b){ return aprCap(vec3(cmul(a.xy, b.xy), a.z * b.z)); }
// n < 0: the power -n, then one sphere inversion with a mirror (see MATH.split)
vec3 pw(vec3 v, float n){
  float m = abs(n), rho = length(v.xy), p = at2(v.y, v.x) * m, az = abs(v.z);
  float zs = az > 0.0 ? aprPow(az, m) * (v.z < 0.0 ? cos(PI * m) : 1.0) : 0.0;
  vec3 u = vec3((rho < 1e-20 && m > 0.0 ? 0.0 : aprPow(rho, m)) * vec2(cos(p), sin(p)), zs);
  if (n >= 0.0) return u;
  float L = length(u);
  if (!(L * APR_CAP > 1.0)) return vec3(APR_CAP, 0.0, 0.0);
  return (u / L) * vec3(1.0, -1.0, 1.0) / L;
}
vec3 sqr(vec3 v){ return aprCap(vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, v.z * v.z)); }
vec3 cmap(vec3 c){ return c; }`;
// ----- tried, and kept for the record (ported from out/lab2/, where each has its notes and its checks)
// The product of two different points in "Blended planes" and "Pillow" is the one-plane product (aprMmul).
const GL_TRIED_MERC = `
float aprTurn(){ return 0.0; }
float aprLift(){ return 0.0; }` + GL_MERC_CORE;
// Blended planes. uA = (planes, width of each plane's own band, curve: 0 smoothstep 1 smootherstep,
// mix: 0 great circle 1 straight 2 pinch). cmap is the identity: the constant is not folded.
const GL_SOFTFOLD = GL_APR + GL_TRIED_MERC + `
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
// the direction of the one-plane power of the unit direction d
vec3 sfDir(vec3 d, float n){
  if (n == 2.0) return vec3(d.x * d.x - d.y * d.y, 2.0 * d.x * d.y, 2.0 * d.z) / (1.0 + d.z * d.z);
  float Z = clamp(d.z, -0.999999, 0.999999), m = clamp(n * atanh(Z), -20.0, 20.0), p = at2(d.y, d.x) * n;
  return vec3(vec2(cos(p), sin(p)) / cosh(m), tanh(m));
}
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float R = aprPow(r, n), k = floor(uA.x + 0.5), fl = 1.0;
  vec3 d = r > 0.0 ? v / r : vec3(1.0, 0.0, 0.0);
  // the half turn about the x-axis commutes with the rule: work in the half z > 0 (or z = 0, y >= 0)
  if (k > 1.5 && (d.z < 0.0 || (d.z == 0.0 && d.y < 0.0))){ d.yz = -d.yz; fl = -1.0; }
  float s = 0.0, ct = 1.0, st = 0.0, cw = 1.0, sw = 0.0, cj = 1.0, sj = 0.0, rho = length(d.yz), pz = 0.0, sd = 1.0;
  bool pinch = uA.w > 1.5;
  vec3 pa = d, A = vec3(0.0), B = vec3(0.0), D;
  // on z = 0, and on the x-axis where every plane agrees, the first plane's rule is the answer
  if (k > 1.5 && d.z != 0.0 && rho > 1e-15){
    float w = PI / k, u = atan(d.z, d.y) / w, j = min(floor(u), k - 1.0), t = u - j;
    float a = clamp(uA.y, 0.0, 0.49), q = clamp((t - a) / (1.0 - 2.0 * a), 0.0, 1.0);
    s = uA.z > 0.5 ? q * q * q * (q * (6.0 * q - 15.0) + 10.0) : q * q * (3.0 - 2.0 * q);
    if (pinch){
      q = clamp((min(t, 1.0 - t) - a) / (0.5 - a), 0.0, 1.0);
      pz = uA.z > 0.5 ? q * q * q * (q * (6.0 * q - 15.0) + 10.0) : q * q * (3.0 - 2.0 * q);
      s = t < 0.5 ? 0.0 : 1.0; sd = t < 0.5 ? 1.0 : -1.0;
    }
    ct = cos(t * w); st = sin(t * w); cw = cos(w); sw = sin(w);
    pa = vec3(d.x, rho * ct, rho * st);
    cj = (d.y * ct + d.z * st) / rho; sj = (d.z * ct - d.y * st) / rho;
  }
  if (s < 1.0) A = sfDir(pa, n);
  if (s > 0.0){
    B = sfDir(vec3(d.x, rho * (ct * cw + st * sw), rho * (st * cw - ct * sw)), n);
    B = vec3(B.x, B.y * cw - B.z * sw, B.y * sw + B.z * cw);
  }
  if (pinch){
    // only the nearer plane answers, and it is pulled to where the seam has to land: the x-axis for an even
    // power, the seam's own direction for an odd one (see MATH.softfold)
    if (s > 0.5) A = B;
    bool odd = abs(mod(abs(n), 2.0) - 1.0) < 1e-3;
    float h = 0.5 * PI / k, g = n < 0.0 ? -1.0 : 1.0, ch = cos(h), sh = sin(h);
    B = odd ? vec3(d.x, g * rho * (sd > 0.0 ? ch : cw * ch + sw * sh), g * rho * (sd > 0.0 ? sh : sw * ch - cw * sh)) : vec3(1.0, 0.0, 0.0);
    s = pz;
  }
  if (s <= 0.0) D = A;
  else if (s >= 1.0) D = B;
  else if (uA.w > 0.5 && !pinch){
    vec3 m = mix(A, B, s); float lm = length(m);
    if (lm < 1e-3) D = s < 0.5 ? A : B; else D = m / lm;
  } else {
    float c = clamp(dot(A, B), -1.0, 1.0); vec3 e = B - c * A; float le = length(e);
    if (c < 0.0 && le < 1e-3) D = s < 0.5 ? A : B;
    else { float om = atan(le, c) * s; D = cos(om) * A + (sin(om) / max(le, 1e-30)) * e; }
  }
  return R * vec3(D.x, fl * (D.y * cj - D.z * sj), fl * (D.y * sj + D.z * cj));
}
vec3 sqr(vec3 v){ return pw(v, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// Bulbs about the axis. uA.x: turn multiplier k (whole), uA.y: wobble A, uA.z: reach of the wobble in degrees,
// uA.w: pinch B. mul, pw and sqr are the quaternion ones (as in GL_LATHE), each followed by the change of turn.
const GL_AXISBULB = GL_APR + `
vec3 axbTurn(vec3 w){
  float k = uA.x, A = uA.y, B = uA.w;
  if (k == 1.0 && A == 0.0 && B == 0.0) return w;
  float rho = length(w.yz);
  if (!(rho > 0.0)) return w;
  vec2 u = w.yz / rho, e = vec2(1.0, 0.0);
  int m = int(abs(k) + 0.5);
  for (int i = 0; i < 16; i++){ if (i >= m) break; e = cmul(e, u); }
  if (k < 0.0) e.y = -e.y;
  float r = length(w), s2 = 2.0 * u.x * u.y;
  if (A != 0.0){
    float sr = sin(radians(uA.z)), t = sr > 1e-6 ? clamp(rho / (r * sr), 0.0, 1.0) : 1.0;
    float ang = A * t * t * (3.0 - 2.0 * t) * 2.0 * s2 * (u.x * u.x - u.y * u.y);
    e = cmul(e, vec2(cos(ang), sin(ang)));
  }
  if (B == 0.0) return vec3(w.x, rho * e);
  return aprCap((1.0 + B * s2 * s2 * (rho / r) * (rho / r)) * vec3(w.x, rho * e));
}
vec3 mul(vec3 a, vec3 b){ return axbTurn(aprCap(vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz))); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float rho = length(v.yz), a = at2(rho, v.x) * n;
  vec2 u = rho > 0.0 ? v.yz / rho : vec2(1.0, 0.0);
  return axbTurn(aprPow(r, n) * vec3(cos(a), sin(a) * u));
}
vec3 sqr(vec3 v){ return axbTurn(aprCap(vec3(v.x * v.x - dot(v.yz, v.yz), 2.0 * v.x * v.yz))); }
vec3 cmap(vec3 c){ return c; }`;
// Pillow. uA.x: the layout. 0: creased, the planes z = 0 and y = 0 exact (pb...). 1: smooth and angle-true, the
// plane z = 0 kept but not exact (ps...). The same steps as psDir, pbLayout, pbInverse, psPower and pbPower.
const GL_PILLOW = GL_APR + GL_TRIED_MERC + `
vec3 psDir(vec3 d){
  float s = 1.0 + abs(d.z);
  vec2 w = d.xy / s, w3 = cmul(cmul(w, w), w);
  vec2 N = 2.0 * w3 - vec2(1.0, 0.0), D = cmul(w, vec2(2.0, 0.0) - w3);
  float nn = dot(N, N), dd = dot(D, D), q = nn + dd;
  float Z = d.z == 0.0 ? 0.0 : (d.z > 0.0 ? dd - nn : nn - dd) / q;
  return vec3(2.0 * vec2(dot(N, D), N.y * D.x - N.x * D.y) / q, Z);
}
vec3 psPw(vec3 v, float n){
  if (n < 1.5) return v;
  float r = length(v);
  if (r < 1e-20) return vec3(0.0);
  vec3 d = psDir(v / r);
  float m = 2.0;
  if (n >= 3.0) { d = psDir(d); m = 4.0; }
  if (n >= 6.0) { d = psDir(d); m = 8.0; }
  return aprPow(r, m) * d;
}
vec3 psSq(vec3 v){
  float r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  return aprCap(r2 * psDir(v * inversesqrt(r2)));
}
const float PB_T3 = 2.0943951024;
vec3 pbSlide(vec3 p){
  float c = length(p.xz);
  if (c < 1e-12) return p;
  if (p.x >= 0.0) { float a = (4.0 / 3.0) * atan(p.z, p.x); return vec3(c * cos(a), p.y, c * sin(a)); }
  float b = (2.0 / 3.0) * atan(p.z, -p.x);
  return vec3(-c * cos(b), p.y, c * sin(b));
}
vec3 pbUnslide(vec3 p){
  float c = length(p.xz);
  if (c < 1e-12) return p;
  if (p.z + 1.7320508 * p.x >= 0.0) { float a = 0.75 * atan(p.z, p.x); return vec3(c * cos(a), p.y, c * sin(a)); }
  float b = 1.5 * atan(p.z, -p.x);
  return vec3(-c * cos(b), p.y, c * sin(b));
}
vec3 pbLay(vec3 l){
  float mn = min(l.x, min(l.y, l.z)), e = 3.0 * mn, s = 1.0 - e;
  float k = l.z <= l.x && l.z <= l.y ? 0.0 : l.x <= l.y ? 1.0 : 2.0;
  float nx = k < 0.5 ? l.y : k < 1.5 ? l.z : l.x;
  float t = s > 1e-6 ? clamp((nx - mn) / s, 0.0, 1.0) : 0.5;
  float z = sin(0.5 * PI * e), rho = cos(0.5 * PI * e), tau = PB_T3 * (k + t);
  return pbSlide(vec3(rho * cos(tau), rho * sin(tau), z));
}
vec3 pbInv(vec3 d0){
  vec3 d = pbUnslide(d0);
  float e = at2(clamp(d.z, 0.0, 1.0), length(d.xy)) * 2.0 / PI;
  float a = at2(d.y, d.x) / PB_T3;
  if (a < 0.0) a += 3.0;
  float k = min(floor(a), 2.0), t = a - k;
  vec3 m = k < 0.5 ? vec3(1.0 - t, t, 0.0) : k < 1.5 ? vec3(0.0, 1.0 - t, t) : vec3(t, 0.0, 1.0 - t);
  return vec3(e / 3.0) + (1.0 - e) * m;
}
vec3 pbPw(vec3 v, float n){
  float m = floor(n + 0.5), r = length(v);
  if (m == 0.0) return vec3(1.0, 0.0, 0.0);
  if (r < 1e-20) return m > 0.0 ? vec3(0.0) : vec3(aprPow(r, m), 0.0, 0.0);
  vec3 d = v / r, l = pbInv(vec3(d.xy, abs(d.z)));
  vec3 X = d.z >= 0.0 ? l : vec3(l.x + l.z, l.y + l.z, -l.z);
  X = vec3(m * X.x - (m - 1.0), m * X.y, m * X.z);
  vec3 i = floor(X), f = X - i;
  float sum = f.x + f.y + f.z;
  bool flip = sum > 1.5 && sum < 2.5;
  float k = mod(i.y - i.z + 0.5, 3.0);
  vec3 g = sum < 0.5 || sum >= 2.5 ? vec3(1.0, 0.0, 0.0) : flip ? vec3(1.0) - f.xzy : f;
  vec3 o = pbLay(k < 1.0 ? g : k < 2.0 ? g.zxy : g.yzx);
  if (flip) o.z = -o.z;
  if (v.z == 0.0) o.z = 0.0;
  return (m == 2.0 ? min(r * r, APR_CAP) : aprPow(r, m)) * o;
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return uA.x > 0.5 ? psPw(a, n) : pbPw(a, n); }
vec3 sqr(vec3 a){ return uA.x > 0.5 ? psSq(a) : pbPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;

// ---------- wording helpers for the approach texts
const aprIs = (a, b) => Math.abs(a - b) < 1e-9;
const aprWhole = n => aprIs(n, Math.round(n));
const aprNum = x => String(+(+x).toFixed(2)).replace('-', '−');
const aprDeg = x => aprNum(x) + '°';
const aprSup = k => [...String(Math.round(k))].map(ch => (ch === '-' ? '⁻' : '⁰¹²³⁴⁵⁶⁷⁸⁹'[+ch])).join('');   // a whole number as a superscript
const aprWrap = deg => { const d = ((deg + 180) % 360 + 360) % 360 - 180; return aprIs(d, -180) ? 180 : d; };
const aprPlus = (x, unit) => (x ? (x < 0 ? ' − ' : ' + ') + aprNum(Math.abs(x)) + unit : '');   // "" or " + 20°"
const aprPole = n => (n < 0 ? ' The origin is sent to infinity.' : '');
// a fractional power cannot close up around the origin, here or in the plane: add one of these sentences then
const aprTear = (n, text) => (aprWhole(n) ? '' : text);
const APR_HALF = ' A power that is not a whole number also tears space along the half-plane y = 0, x < 0, the way zⁿ tears the plane along the negative x-axis.';
const APR_LINE = ' A power that is not a whole number also tears space along the negative x-axis, the way zⁿ tears the plane there.';
// is some value  target + 180°·k  strictly between a and b (all in degrees)?
function aprPasses(a, b, target) {
  const lo = (Math.min(a, b) - target) / 180, hi = (Math.max(a, b) - target) / 180;
  return Math.ceil(hi - 1e-9) - Math.floor(lo + 1e-9) > 1;
}
// the slice sentence for a rule that adds a turn of `deg` degrees to every power
function aprTurned(subject, deg, n) {
  const back = aprWhole(n) && !aprIs(n, 1) ? ` For zⁿ + c that slice is the usual flat set turned by ${aprDeg(aprWrap(-deg / (n - 1)))}.` : '';
  return `${subject} complex arithmetic with one change: every power is also turned by ${aprDeg(deg)}.${back}`;
}
const aprMercTurn = p => aprWrap(p.turn || 0);   // the turn in effect, between −180° and 180°
const APR_INVERSION = 'At n = −1 the rule is a single sphere inversion with a flip, and inversions keep every shape.';
const APR_MIRROR = 'At n = −1 the rule is a single sphere inversion with a mirror, and inversions keep every shape.';
// n = 0 sends every point to the same place, whatever the approach
const aprNone = () => ['no', 'Everything is crushed onto one point.'];
const aprConstant = () => ['ok', 'A constant.'];
// what the turn and longitude-phase dials do to the slice at z = 0
const APR_SLICE_TURNS = ' Away from 0 the slice at z = 0 is no longer the plain 2D picture: it is that picture turned (Mandelbrot) or a different set (Julia).';

// The headings of the Approach list, in the order they are shown. Every approach names one in `group`, and
// the list shows the approaches of a group in the order they stand in APPROACHES.
const APPROACH_GROUPS = [
  { id: 'inversions', title: 'Sphere inversions' },
  { id: 'quaternion', title: 'Quaternions' },
  { id: 'angles', title: 'Angle rules' },
  { id: 'other', title: 'Side by side' },
  { id: 'tried', title: 'Tried, and kept for the record' },
];
// The one-plane rule in words, shared by the two Sphere inversions entries.
function aprMercFormula(n) {
  const k = Math.round(n);
  if (aprWhole(n) && n >= 2) return `v${aprSup(k)} = |v|${aprSup(k)} · [1 + ${k}·inv(Σₖ Rₖ·inv(d − ωₖ))]   with d = v/|v| the direction of v, inv a sphere inversion, ωₖ the ${k} points spaced evenly round the unit circle, and Rₖ the turn about the z-axis that reaches the k-th of them.`;
  if (aprIs(n, 1)) return 'v¹ = v.';
  if (aprIs(n, 0)) return 'v⁰ = (1, 0, 0).';
  if (aprIs(n, -1)) return 'v⁻¹ = inv(v) = (x, −y, −z)/|v|²: one sphere inversion, then a flip.';
  if (aprWhole(n)) return `v${aprSup(k)} = inv(v${aprSup(-k)}): the sum of inversions for the power ${-k}, then one more inversion.`;
  return 'vⁿ = |v|ⁿ · (cos nφ / cosh nm, sin nφ / cosh nm, tanh nm)   with φ the longitude and m the latitude as a Mercator map stretches it. At whole n this is what the sum of inversions gives.';
}
const aprMercAfter = (turn, lift) => (turn || lift ? ' After it, ' + [turn ? `${aprDeg(turn)} is added to the longitude` : '', lift ? `${aprNum(lift)} is added to the latitude (measured the way a Mercator map stretches it)` : ''].filter(Boolean).join(' and ') + '.' : '');
const APR_LIFT = { type: 'dial', key: 'lift', label: 'Lift toward the pole', min: -2, max: 2, step: 0.01, def: 0, lo: -6, hi: 6, xmin: -6, xmax: 6, xlo: -20, xhi: 20, animate: 'bounce', help: 'The nearest thing this approach has to the Mandelbulb’s latitude phase: it pushes every direction toward one pole each time a power is taken. It is an offset where the phase is an angle, so play sweeps it to one end and back. Away from 0 the flat set leaves the plane z = 0.' };
const APR_LIFTED = 'With a lift the plane z = 0 lands on a cone, so no flat slice follows complex arithmetic. Set the lift to 0 to get the flat set back.';
const APR_CIRCLES = 'Circles on the sphere stay circles (see the step view). The squash is between the outward direction and the sphere.';
// Bulbs about the axis: which planes through the x-axis a turn multiplier k keeps exact (the wobble never disturbs them)
const axbExact = k => (k % 2 === 0 ? 0 : ((k % 4) + 4) % 4 === 1 ? 2 : 1);   // 0: none, 1: z = 0 only, 2: z = 0 and y = 0

const APPROACHES = [
  {
    id: 'mercator', name: 'Sphere inversions, one plane', group: 'inversions', glsl: GL_MERCATOR, axis: () => [0, 0, 1],
    tag: 'Add up sphere inversions, the way circle inversions add up to zⁿ in the plane.',
    params: [
      { type: 'note', text: 'For whole powers this rule is smooth and has no seam, so nothing tears the solid. The fine detail lies around the plane z = 0 only: these are the “inflated” sets in Václav Kučera’s paper (Bridges 2019, Figure 3). The look of Figure 4, with beads around two circles, belongs to the next entry, Sphere inversions, two planes.' },
      { type: 'dial', key: 'turn', label: 'Turn, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'This approach’s version of the Mandelbulb’s longitude phase, added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },
      // Lift is an offset where a phase is an angle: its two ends give different solids, so its sweep runs there and back.
      APR_LIFT,
    ],
    formula: (p, n) => aprMercFormula(n) + aprMercAfter(aprMercTurn(p), p.lift),
    about: 'In the plane, zⁿ can be built from n + 1 circle inversions: one about each of n points spaced evenly round the unit circle, the results added, then one more inversion of the sum. Swap the circles for spheres and the same recipe works in space, once a plane is chosen for the n points to lie in. Worked out, it multiplies two angles by n: the longitude, and the latitude as a Mercator map stretches it. Cut the solid at z = 0 and the slice is exactly the ordinary 2D Mandelbrot or Julia set of the same power (the 2D view shows it).',
    // a lift stretches the sphere of directions, so at n = −1 the rule is a plain inversion only while the lift is 0
    roundNote: (p, n) => (aprIs(n, -1) && !p.lift ? APR_INVERSION : APR_CIRCLES),
    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      const a = Math.abs(n);
      if (aprIs(a, 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion. The origin is sent to infinity.' : 'Crushes nothing: at n = 1 every point stays where it is.'];
      if (a < 1) return ['part', 'Crushes nothing at this power, but the stretch has no limit beside the z-axis.' + aprPole(n)];
      return ['part', 'Crushes the z-axis only: a line where the plane has a point.' + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'Smooth for whole powers only.' + aprTear(n, APR_HALF)];
      return ['part', n < 0 ? 'Smooth everywhere except the origin, which is a pole.' : 'Smooth everywhere except the origin. It needs |v|, so it is not a polynomial.'];
    },
    slice: (ok, p, n = S.n) => {
      if (p.lift) return APR_LIFTED;
      const turn = aprMercTurn(p);
      if (turn) return aprTurned('The plane z = 0 follows', turn, n);
      return !ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.';
    },
  },
  {
    // The earlier version of Sphere inversions, an approach of its own so that the two can be told apart. The fold
    // sends the half y > 0 and the half y < 0 of space to opposite sides, so the rule jumps across the plane
    // y = 0 (see foldk).
    id: 'fold', name: 'Sphere inversions, two planes', group: 'inversions', glsl: GL_FOLD, axis: () => [1, 0, 0],
    tag: 'The earlier version. Fold space like a fan first, so that two planes carry the flat set.',
    params: [
      { type: 'dial', key: 'planes', label: 'Planes', min: 2, max: 8, step: 1, def: 2, int: true, xmax: 16, xhi: 64 },
      { type: 'note', text: 'An attempt to copy Figure 4 in Václav Kučera’s paper (Bridges 2019), with beads around two circles. It looks right for a Julia set whose c lies on the x-axis, such as the Basilica. Everywhere else, the Mandelbrot solid included, the rule jumps on the seam of its fold, which tears the solid. The count is a free choice: p planes give 2p fins around the x-axis, whatever the power is. There is no Turn dial here: with a fold a turn tears the solid into sheets.' },
      APR_LIFT,
    ],
    formula: (p, n) => aprMercFormula(n) + ` Before that, the nearest of ${p.planes} planes through the x-axis is folded onto the xy-plane.` + aprMercAfter(0, p.lift),
    about: 'The one-plane rule with a fold in front of it. Space is folded around the x-axis like a fan, until the nearest of the chosen planes lies on the xy-plane, and then the one-plane rule is applied. With two planes, the planes z = 0 and y = 0 both carry the flat set. This follows the second construction in Kučera’s paper, whose third map is the second one turned by 90° about the x-axis. The paper reports that construction for c on the x-axis only, and that is where this rule is whole too.',
    roundNote: (p, n) => (aprIs(n, -1) && !p.lift ? 'At n = −1 each piece is a sphere inversion with a flip, which keeps every shape. The folds between the pieces still leave creases.' : APR_CIRCLES),
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone()
      : ['part', (n > 1 ? 'Nothing but the origin is crushed.' : 'Nothing is crushed.') + ' Space is creased where the folds meet instead.' + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant()
      : ['no', 'Pieces of the one-plane rule joined by mirror folds. The folds leave creases, and across the plane y = 0 a jump, whose effect cancels only when c is on the x-axis.' + aprTear(n, APR_HALF)]),
    slice: (ok, p) => (p.lift ? APR_LIFTED : !ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : `${p.planes} planes through the x-axis follow complex arithmetic exactly, z = 0 among them.`),
  },
  {
    id: 'lathe', name: 'Quaternion square (Lathe)', group: 'quaternion', glsl: GL_LATHE, axis: () => [1, 0, 0],
    tag: 'Square a quaternion: multiply the angle from the x-axis, and leave the spin around it alone. Sphere inversions with no plane chosen give this same rule.',
    params: [{ type: 'dial', key: 'spin', label: 'Spin multiplier (odd)', min: -7, max: 9, step: 2, def: 1, odd: true, xmin: -31, xmax: 33, xlo: -99, xhi: 99 }],
    formula: (p, n) => (aprIs(n, 2) ? 'v² = (x² − y² − z², 2xy, 2xz)' : aprIs(n, -1) ? 'v⁻¹ = (x, −y, −z)/|v|²'
      : 'vⁿ = |v|ⁿ · (cos nα, sin nα · u)   with α the angle from the x-axis and u the direction of (y, z)')
      + (p.spin !== 1 ? `, then the angle of (y, z) is multiplied by ${aprNum(p.spin)}` : ''),
    about: 'With spin 1 this is the power of a quaternion (a number with three imaginary parts) with one part held at zero, and the set is the flat one turned on a lathe. It is also what the sum of sphere inversions gives when no plane is chosen: for the square, the two centres are the points 1 and −1 on the x-axis, and they need no plane. So this is the one rule of its kind that treats every direction around the x-axis alike. Any other odd spin also twists directions around the x-axis, which breaks the rings into bulbs while the plane z = 0 stays exact.',
    roundNote: (p, n) => (aprIs(n, -1) && p.spin === 1 ? APR_INVERSION : 'The squash is in the spin direction.'),
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the x-axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane x = 0.` : '') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      const tear = aprTear(n, APR_LINE);
      if (aprIs(n, 0)) return aprConstant();
      if (p.spin !== 1) return ['no', 'Has a crease along the whole x-axis, where the spin has nothing to be measured from.' + tear];
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only.' + tear];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.'];
    },
    slice: (ok, p) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly' + (p.spin === 1 ? ', and so does every other plane through the x-axis.' : '.')),
  },
  {
    // F = A^(-n) L^n A, with A the turn by the tilt about the z-axis and L the quaternion power. In 4D it is
    // q times a twisted copy of q: for q = z + w j the copy is z + e^(2i tilt) w j, and
    // q . copy = z^2 - e^(-2i tilt) |w|^2 + (...) w j. A tilt of 180 is the Lathe with z mirrored (its twin).
    id: 'tilt', name: 'Quaternion square, twisted', group: 'quaternion', glsl: GL_TILT,
    axis: p => [Math.cos(aprRad(p.tilt)), -Math.sin(aprRad(p.tilt)), 0],
    tag: 'Square a quaternion, with the second copy twisted first. The rings of the quaternion square break up.',
    // What the help and the note say was measured in out/r12/check-maths/ and again in out/r12/fix/ (sweep.log,
    // after-maths.log): the Mandelbrot solid ends inside radius 2 at every tilt (the rule squares lengths); a tilt
    // of 180 is the mirror twin for even powers and the plain quaternion square for odd ones; away from tilt 0 the
    // plane y = 0 does not follow complex arithmetic.
    params: [
      { type: 'dial', key: 'tilt', label: 'Tilt of the axis, degrees', min: -180, max: 180, step: 1, def: 40, lo: -360, hi: 360, animate: true, help: 'At 0 this is the plain quaternion square, the entry above, and the solid is made of rings. Away from 0 the rings break up into one body with tunnels. At 180 it is the mirror twin of the quaternion square for an even power, and the quaternion square itself for an odd one. At 90 and −90 the Mandelbrot solid is one fat body with spikes. It ends at every tilt: nothing further than 2 from the centre belongs to it. A tilt with a minus sign gives the mirror image of that solid, with y and −y swapped. For whole powers the plane z = 0 is exact at every tilt.' },
      { type: 'note', text: 'A rule for all of space with no seam: for whole positive powers it is built from plain multiplying and adding. One plane is built into it all the same: the plane z = 0 is exact, and at power 2 the plane y = 0 is not, unless the tilt is 0. In the close-up pictures its skin is smooth sheets and folds, with no fine bumps. The fine detail of the flat set is there where the solid meets the plane z = 0.' },
    ],
    formula: (p, n) => (aprIs(n, 2) ? `v² = ((x + iy)² − z²·e^(−2it), 2z·(x cos t − y sin t))   with t = ${aprDeg(p.tilt)}, and the first two coordinates written as one complex number. At t = 0 it is the quaternion square (x² − y² − z², 2xy, 2xz).`
      : `vⁿ = turn(−n·t) · qⁿ(turn(t) · v)   with t = ${aprDeg(p.tilt)}, qⁿ the quaternion power and turn a turn about the z-axis.`),
    about: 'Squaring multiplies a quaternion by itself. Here the second copy is twisted first: a quaternion has four directions, two of them outside the flat plane, and in the second copy those two are turned together, in their own plane, by twice the tilt. What that leaves in 3D is the quaternion square with its angle measured from an axis tilted inside the plane z = 0, and the result turned back. In the plane z = 0 the two turns cancel, so the slice is the flat set at every tilt. A Julia set whose c lies in that plane is a true slice of the 4D set. A Mandelbrot solid needs a c with a height, and adding it as a 3D point is this page’s own choice.',
    roundNote: () => 'The squash is in the spin direction around the tilted axis.',
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the tilted axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane through the origin at right angles to the tilted axis.` : '') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A polynomial (built from plain multiplying and adding) for whole positive powers only. A power that is not a whole number also tears space along a line, the way zⁿ tears the plane along the negative x-axis.'];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial: built from plain multiplying and adding.'];
    },
    // A power that is not whole tears the plane along the negative side of the tilted axis, where the plain
    // complex power tears it along the negative x-axis. So the two differ in the wedge between those two rays.
    slice: (ok, p, n = S.n) => (ok ? 'The plane z = 0 follows complex arithmetic exactly, at every tilt.'
      : !aprWhole(n) && p.tilt ? 'For a power that is not a whole number the plane z = 0 follows complex arithmetic except in a wedge as wide as the tilt, beside the negative x-axis: the tear lies along the tilted axis, not along the negative x-axis. Whole powers are exact at every tilt.'
      : 'The plane z = 0 does not follow complex arithmetic.'),
  },
  {
    id: 'bulb', name: 'Mandelbulb', group: 'angles', glsl: GL_BULB, axis: () => [0, 0, 1],
    tag: 'Multiply the latitude and the longitude.',
    params: [
      { type: 'dial', key: 'lat', label: 'Latitude phase, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'Added to the latitude each time a power is taken. Away from 0 the flat set leaves the plane z = 0.' },
      { type: 'dial', key: 'lon', label: 'Longitude phase, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'Added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },
    ],
    formula: (p, n) => (aprIs(n, 2) && !p.lat && !p.lon ? 'v² = ((ρ² − z²)(x² − y²)/ρ², (ρ² − z²)·2xy/ρ², 2ρz)   with ρ = √(x² + y²)'
      : aprIs(n, -1) && !p.lat && !p.lon ? 'v⁻¹ = (x, −y, −z)/|v|²'
      : `vⁿ = |v|ⁿ · (cos B cos L, cos B sin L, sin B)   with B = n·latitude${aprPlus(p.lat, '°')} and L = n·longitude${aprPlus(p.lon, '°')}`),
    about: 'The Mandelbulb with its up-down angle counted from the equator. That is the version that keeps the flat set in the plane z = 0. The two phases are added to the angles at every power; sweeping the latitude phase makes the solid pulse from its poles.',
    roundNote: (p, n) => {
      if (aprIs(n, -1) && !p.lat) return APR_INVERSION;
      const torn = Math.abs(Math.cos(n * PI / 2 + aprRad(p.lat))) > 1e-6;
      return (Math.abs(Math.sin(aprRad(p.lat))) > 1e-6 ? 'With a latitude phase even the equator is squashed, and ' : 'Exact on the equator, but ')
        + (torn ? 'the stretch grows without limit toward the z-axis.' : 'beside the z-axis the stretch along the circles of latitude is |n| times too large.');
    },
    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      if (!aprPasses((p.lat || 0) - 90 * n, (p.lat || 0) + 90 * n, 90)) return ['ok', (n < 0 ? 'Crushes nothing at these settings.' : 'Crushes nothing but the origin at these settings.') + aprPole(n)];
      return ['no', `Crushes the cones where n times the latitude${p.lat ? ', plus the phase,' : ''} reaches ±90°, ±270° and so on` + (aprIs(Math.abs(n), 2) && !p.lat ? ' (latitude ±45° here).' : '.') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      const torn = Math.abs(Math.cos(n * PI / 2 + aprRad(p.lat))) > 1e-6, even = aprWhole(n / 2) && !p.lat;
      return ['no', (torn ? `Torn along the z-axis: directions next to a pole are thrown all the way around ${even ? 'the equator' : 'a circle of latitude'}.`
        : 'Has a crease along the z-axis, where the longitude has nothing to be measured from.') + aprTear(n, APR_HALF)];
    },
    slice: (ok, p, n = S.n) => {
      const lat = aprWrap(p.lat || 0), flip = aprIs(Math.abs(lat), 180), turn = aprWrap((p.lon || 0) + (flip ? 180 : 0));
      if (lat && !flip) return 'With a latitude phase the plane z = 0 lands on a cone, so no flat slice follows complex arithmetic. Set that phase to 0 to get the flat set back.';
      if (turn) return aprTurned('The plane z = 0 follows', turn, n);
      return ok ? 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' : 'The plane z = 0 does not follow complex arithmetic.';
    },
  },
  {
    id: 'classic', name: 'Mandelbulb, classic', group: 'angles', glsl: GL_CLASSIC, axis: () => [0, 0, 1],
    tag: 'Multiply the angle from the z-axis and the angle around it.',
    params: [
      { type: 'dial', key: 'theta', label: 'θ phase, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'Added to the angle from the z-axis each time a power is taken. Sweeping it makes the solid pulse from its poles.' },
      { type: 'dial', key: 'phi', label: 'φ phase, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'Added to the angle around the z-axis each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis; Julia sets change shape.' },
    ],
    formula: p => `vⁿ = |v|ⁿ · (sin T cos P, sin T sin P, cos T)   with T = n·θ${aprPlus(p.theta, '°')}, P = n·φ${aprPlus(p.phi, '°')}, θ the angle from the z-axis and φ the angle around it`,
    about: 'White and Nylander’s formula as most renders use it, usually at n = 8. It is here as a rendering benchmark, and with every dial at its starting value it is the one approach whose z = 0 slice is not the flat set: for even n that whole plane is thrown onto the z-axis. A θ phase of (1 − n) × 90° turns it into the Mandelbulb above.',
    roundNote: (p, n) => {
      if (aprIs(n, -1) && !p.theta) return 'At n = −1 the rule is a single sphere inversion with a mirror, and inversions keep every shape.';
      const torn = Math.abs(Math.sin(aprRad(p.theta))) > 1e-6 || Math.abs(Math.sin(n * PI + aprRad(p.theta))) > 1e-6;
      return torn ? 'Beside the z-axis the stretch has no limit, and on cones around the axis directions are crushed.' : 'Stretched up to |n| times too far beside the z-axis, crushed on cones around it.';
    },
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : aprPasses(p.theta || 0, (p.theta || 0) + 180 * n, 0)
      ? ['no', `Crushes every direction whose angle from the z-axis, times n${p.theta ? ' plus the phase' : ''}, is a multiple of 180°.` + aprPole(n)]
      : ['ok', (n < 0 ? 'Crushes nothing at these settings.' : 'Crushes nothing but the origin at these settings.') + aprPole(n)]),
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      const torn = Math.abs(Math.sin(aprRad(p.theta))) > 1e-6 || Math.abs(Math.sin(n * PI + aprRad(p.theta))) > 1e-6;
      return ['no', (torn ? 'Torn along the z-axis: directions next to a pole are thrown all the way around a circle.'
        : 'Has a crease along the whole z-axis, where the angle around it has nothing to be measured from.') + aprTear(n, APR_HALF)];
    },
    slice: (ok, p, n = S.n) => {
      const T = n * PI / 2 + aprRad(p.theta), fix = aprWrap((1 - n) * 90);
      if (Math.abs(Math.cos(T)) > 1e-6) {
        return `No. This is the one approach here that starts out without the flat set at z = 0. Setting the θ phase to ${aprDeg(fix)} would put it back: that turns this formula into the Mandelbulb above.`;
      }
      const turn = aprWrap((p.phi || 0) + (Math.sin(T) < 0 ? 180 : 0));
      if (turn) return aprTurned('The plane z = 0 follows', turn, n);
      return p.theta ? 'With this θ phase the plane z = 0 follows complex arithmetic exactly: the formula has become the Mandelbulb above.'
        : 'At this n the plane z = 0 happens to follow complex arithmetic.';
    },
  },
  {
    id: 'split', name: 'Split', group: 'other', glsl: GL_SPLIT, axis: () => [0, 0, 1],
    tag: 'Treat x + iy as a complex number and z as a real number, each on its own.',
    formula: (p, n) => {
      if (aprIs(n, 2)) return 'v² = (x² − y², 2xy, z²)';
      if (aprIs(n, -1)) return 'v⁻¹ = (x, −y, z)/|v|²: one sphere inversion with a mirror';
      if (n >= 0) return 'vⁿ = ((x + iy)ⁿ, zⁿ): the complex power and the real power, side by side';
      const whole = aprWhole(n), m = whole ? aprSup(-n) : 'ᵐ';
      return `v${whole ? aprSup(n) : 'ⁿ'} = (X, −Y, Z)/(X² + Y² + Z²)   with X + iY = (x + iy)${m} and Z = z${m}` + (whole ? '' : `, m = ${aprNum(-n)}`) + ': the two powers side by side, then one sphere inversion with a mirror';
    },
    about: 'Space treated as a complex number x + iy and an ordinary number z side by side, each multiplied on its own. Two points that are not 0 can multiply to 0 this way, and the set is the flat one extruded into a prism. A negative power is the positive power followed by one sphere inversion, as in the other approaches. Dividing by z on its own is not possible on the plane z = 0, where z is 0.',
    roundNote: (p, n) => (aprIs(n, -1) ? APR_MIRROR : 'Each factor keeps shapes on its own. Together they do not.'),
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (aprIs(a, 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion with a mirror. The origin is sent to infinity.' : 'Crushes nothing: at n = 1 every point stays where it is.'];
      if (a < 1) return ['part', 'Crushes nothing at this power, but the stretch has no limit at the plane z = 0 and the z-axis.' + aprPole(n)];
      return ['no', 'Crushes the plane z = 0 and the z-axis.' + aprPole(n)];
    },
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant()
      : !aprWhole(n) ? ['no', 'A polynomial for whole positive powers only. Otherwise the complex factor is torn along the half-plane y = 0, x < 0, and below the plane the real factor keeps only the real part of zⁿ.']
      : n < 0 ? ['part', 'One polynomial divided by another: smooth everywhere except the origin, which is sent to infinity.'] : ['ok', 'A polynomial.']),
    slice: (ok, p, n = S.n) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : n < 0 ? 'The plane z = 0 follows complex arithmetic exactly. Because a negative power ends with an inversion, the slices at other heights are not copies of it.'
      : 'The plane z = 0 follows complex arithmetic exactly. So does every level slice of the prism.'),
  },
  // ----- Tried, and kept for the record. Three rules that were built to get the look of Figure 4 (bodies with
  // beads) without the tear of the two-planes rule, and failed. Each says what it was tried for and why it fails
  // in the two places the list shows first: in short in `tag` (the line under the name, shown for every entry),
  // and in full in `about` (the paragraph under the formula). How the rule works is the note above its dials.
  // Their prototypes, numbers and pictures are in out/lab2/<softfold|axisbulb|pillow2>/; this round's checks in out/r12/tried/.
  {
    id: 'softfold', name: 'Blended planes', group: 'tried', glsl: GL_SOFTFOLD, axis: () => [1, 0, 0],
    tag: 'Tried: several planes joined by a smooth blend instead of a fold, to get beads without a tear. Failed: one swollen mass, no beads.',
    params: [
      { type: 'note', text: 'How it works: The one-plane rule of Sphere inversions is built on each of the chosen planes through the x-axis, so each of those planes carries the flat set. Between two neighbouring planes the two answers are blended: the result moves smoothly from one to the other, and the constant c is used as it is, with no fold. The seam half way between two planes is a mirror of the rule, so the rule can only send the seam into itself, and that is where the blend goes wrong: it either folds back over ground the plane’s own rule has already covered, or, with the pinch and an even power, crushes the whole seam onto the x-axis. A product of two different points is taken from Sphere inversions, one plane.' },
      { type: 'dial', key: 'planes', label: 'Planes', min: 2, max: 4, step: 1, def: 2, int: true },
      { type: 'dial', key: 'blend', label: 'Each plane’s own band', min: 0, max: 0.45, step: 0.01, def: 0.25, lo: 0, hi: 0.49, help: 'How much of the way to the next plane the rule stays the plane’s own, before the blend starts. At 0 the blend fills the whole gap. Near 0.5 the blend is squeezed into a thin sheet half way, and the solid turns to dust.' },
      { type: 'select', key: 'curve', label: 'Blend curve', def: 0, options: [[0, 'Gentle start and end'], [1, 'Gentler start and end']] },
      { type: 'select', key: 'mix', label: 'Between two planes', def: 0, options: [[0, 'Blend along a great circle'], [1, 'Blend along a straight line'], [2, 'No blend: pinch the seams']], help: 'How the two plane answers are joined. A great circle is the shortest way round the sphere of directions from one answer to the other. The pinch does not blend: the nearer plane answers alone, and for an even power each seam half way between two planes is pulled onto the x-axis. For an odd power the seam lands on itself.' },
    ],
    formula: (p, n) => (p.mix > 1.5
      ? `vⁿ = |v|ⁿ · pull(Fₖ(d), T, S(t))   with d the direction of v, Fₖ the one-plane rule built on the nearer of ${p.planes} planes through the x-axis, T the direction the seam has to land on (the x-axis for an even power), t how far the half-plane holding v has turned toward the seam, and S a weight that is 0 for the first ${aprNum(p.blend)} of the way to the next plane and rises smoothly to 1 on the seam.`
      : `vⁿ = |v|ⁿ · blend(Fₖ(d), Fₖ₊₁(d), S(t))   with d the direction of v, Fₖ the one-plane rule built on the k-th of ${p.planes} planes through the x-axis, t how far the half-plane holding v has turned from plane k to plane k + 1, and S a weight that stays at 0 for the first ${aprNum(p.blend)} of the way, rises smoothly, and stays at 1 for the last ${aprNum(p.blend)}.`),
    about: 'Tried for: the look of Figure 4, bodies with beads, without the tear of Sphere inversions, two planes. Each plane keeps the one-plane rule, and between two planes the two answers are blended smoothly, so nothing jumps. Why it fails: the pictures. The Julia set for c = −1 comes out as one swollen mass with ridges where the planes cross, not a row of bodies with beads, and the Mandelbrot solid is a mass of shards and flames. The fault sits on the seam half way between two planes. A rule with no jump can only fold space back over itself there, or, for an even power, crush the whole seam onto the x-axis, and either way the seam fills with a fat set of its own. No setting of these dials mends it. The 3D picture also draws the skin a little outside the true set in places (measured on the Mandelbrot solid: by up to 0.07), so judge the fine detail with care.',
    roundNote: p => (p.mix > 1.5 ? 'Inside each plane’s own band circles on the sphere stay circles. Toward the seam between two planes they are squashed flat.'
      : 'Inside each plane’s own band circles on the sphere stay circles. In the blend between two bands they do not.'),
    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      if (p.mix > 1.5) return aprWhole(n / 2) ? ['no', 'Crushes every seam, the half-plane half way between two planes, onto the x-axis.' + aprPole(n)]
        : ['part', 'For an even power every seam, the half-plane half way between two planes, is crushed onto the x-axis. Other powers were not measured.' + aprPole(n)];
      return ['no', 'In the blend the sphere of directions is folded back over itself, and along each fold line it is crushed flat. Measured at n = 2: about 5 to 7% of directions come out turned over with 2 planes, about 30% with 3 or 4.' + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A power that is not a whole number tears the plane z = 0 along the negative x-axis, as zⁿ does. Away from the planes such powers were not tested.'];
      if (p.mix > 1.5) return ['part', 'No jump was found with the pinch (measured with 2 and 3 planes at n = 2, 3 and −2), but toward each seam the rule is squeezed flat.'];
      if (p.planes > 2) return ['no', 'With 3 or 4 planes single rays of directions can be torn, where the two plane answers point exactly opposite ways. That was found at n = 3 with 3 planes and a narrow band, and at n = 5 with 4 planes.'];
      return ['part', 'No jump with 2 planes (measured at n = 2, 3 and −2). The blend between the planes is steep, and it folds over itself.'];
    },
    slice: (ok, p) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : `${p.planes} planes through the x-axis follow complex arithmetic exactly, z = 0 among them. The trouble is between the planes.`),
  },
  {
    id: 'axisbulb', name: 'Bulbs about the axis', group: 'tried', glsl: GL_AXISBULB, axis: () => [1, 0, 0],
    tag: 'Tried: change the turn around the x-axis, to break the rings of the quaternion square into beads. Failed: the rings stay rings.',
    params: [
      { type: 'note', text: 'How it works: The quaternion square multiplies the angle from the x-axis and keeps the turn around it, which gives bodies that are round about the x-axis, like work turned on a lathe. Here the turn is changed as well: multiplied by a whole number, or given a wobble. With a multiplier of 5 or −3 the planes z = 0 and y = 0 both follow complex arithmetic exactly. With the multiplier at 1, no wobble and no pinch, this is the Quaternion square (Lathe) itself. When c is on the x-axis, adding c changes x only, so whether a point escapes depends on its length and its angle from the x-axis and never on its turn. That is why the rings stay rings.' },
      { type: 'dial', key: 'k', label: 'Turn multiplier', min: -7, max: 9, step: 1, def: 1, int: true, help: 'The turn around the x-axis is multiplied by this whole number. 1 leaves the turn alone, as the quaternion square does. An odd number keeps the plane z = 0 exact, and 1, 5, 9, −3 and −7 keep the plane y = 0 exact as well. An even number folds the half y < 0 of the plane z = 0 onto the half y > 0, so the slice is no longer the flat set.' },
      { type: 'dial', key: 'wob', label: 'Wobble of the turn', min: 0, max: 1, step: 0.01, def: 0.2, lo: -1, hi: 1, help: 'Makes the turn run ahead and fall behind by turns, four times on the way round the x-axis, by up to this number as an angle (0.2 is about 11°). The planes z = 0 and y = 0 and the two planes at 45° between them are left where they are. Above 0.25 the turn folds over itself.' },
      { type: 'dial', key: 'reach', label: 'Wobble at full strength from, degrees off the axis', min: 0, max: 90, step: 1, def: 45, when: p => p.wob !== 0, help: 'The wobble fades to nothing toward the x-axis, so the axis keeps no crease from it. 0 switches the fade off.' },
      { type: 'dial', key: 'pinch', label: 'Pinch between the planes', min: 0, max: 4, step: 0.05, def: 0, lo: -0.9, hi: 16, help: 'Makes the result longer between the planes z = 0 and y = 0, most of all half way between them and far from the x-axis. On those two planes and on the x-axis nothing is changed, so those stay exact. The formula line above shows the factor.' },
    ],
    formula: (p, n) => 'vⁿ = |v|ⁿ · (cos nβ, sin nβ · cos G, sin nβ · sin G)   with β the angle from the x-axis, γ the turn around it, and G = '
      + (p.k === 1 ? 'γ' : `${aprNum(p.k)}·γ`) + (p.wob ? `${aprPlus(p.wob, '')}·W·sin 4γ, W fading to 0 at the x-axis` : '') + (p.pinch ? `, and the length times 1${aprPlus(p.pinch, '')}·sin² 2γ·sin² nβ` : '')
      + (aprIs(n, 2) && p.k === 1 && !p.wob && !p.pinch ? '. That is (x² − y² − z², 2xy, 2xz).' : '.'),
    about: 'Tried for: beads in place of the rings of the Quaternion square (Lathe), by also changing the turn around the x-axis. Why it fails: for a Julia set whose c lies on the x-axis, such as c = −1, the turn never feeds back into the shape. So that set stays the same body, round about the x-axis, rings and all, whatever the multiplier and the wobble are. On the Mandelbrot solid a small wobble only opens some rings into ribbons. A multiplier of 5 or −3 gives flames and whiskers, and over part of the flat set in the plane z = 0 the solid then thins to a sheet with no thickness: over about half of the flat Mandelbrot set at a multiplier of 5, and about a third at −3. The pinch is the one dial that changes the c = −1 set, and it gives fins, not beads.',
    roundNote: (p, n) => (aprIs(n, -1) && p.k === 1 && !p.wob && !p.pinch ? APR_INVERSION : Math.abs(p.k) > 1 ? `The squash is in the turn direction: beside the x-axis, circles around it are stretched ${aprNum(Math.abs(p.k))} times their due.` : 'The squash is in the turn direction.'),
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (p.k === 0 && !p.wob) return ['no', 'With a multiplier of 0 every turn is thrown onto the half-plane z = 0, y > 0.'];
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the x-axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane x = 0.` : '') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      const tear = aprTear(n, APR_LINE);
      if (aprIs(n, 0)) return aprConstant();
      if (p.k !== 1) return ['no', 'No jump, but a crease along the whole x-axis, where the turn has nothing to be measured from.' + tear];
      if (p.wob || p.pinch) return ['part', 'No jump anywhere. The wobble fades out toward the x-axis and the pinch is 0 there, so the axis keeps no crease.' + tear];
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only.' + tear];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.'];
    },
    slice: (ok, p) => {
      const e = axbExact(p.k);
      if (!ok || !e) return 'The plane z = 0 does not follow complex arithmetic' + (e ? '.' : ': an even multiplier folds its half y < 0 onto the half y > 0.');
      if (p.k === 1 && !p.wob && !p.pinch) return 'The plane z = 0 follows complex arithmetic exactly, and so does every other plane through the x-axis.';
      return 'The plane z = 0 follows complex arithmetic exactly' + (e === 2 ? ', and so does the plane y = 0.' : '. The plane y = 0 follows its mirror image.')
        + (Math.abs(p.k) > 1 ? ' But over part of the flat set a point just off the plane is pushed away from it at every step, so there the solid is a sheet with no thickness (measured on the flat Mandelbrot set: about half of it at a multiplier of 5 or 3, about a third at −3). The 2D view of this page draws it with a hairy fringe: measured at a multiplier of 5, 28% more solid than the flat Mandelbrot set.' : '');
    },
  },
  {
    id: 'pillow', name: 'Pillow', group: 'tried', glsl: GL_PILLOW, axis: () => [0, 0, 1],
    tag: 'Tried: wrap a flat sheet of triangles around the sphere like a pillow, so that no seam is needed. Failed: one lump, or fibres.',
    params: [
      { type: 'note', text: 'How it works: A sheet tiled with equilateral triangles wraps onto the sphere of directions as a flat pillow: two triangles sewn along their edges, with the corners at three points of the plane z = 0, a third of a turn apart on the circle of directions. Multiplying the sheet by n is the power. The creased layout lays each triangle along the rays from its centre and slides the centre so that the circles z = 0 and y = 0 are both laid at an even speed, which makes both planes exact. The smooth layout keeps the angle between any two crossing lines as it was, and then doubling the sheet becomes a single formula with no triangles, creases or seams, but in the plane z = 0 the angle is doubled with a wobble, so the slice is not the flat set. A pillow has to wrap three sheets around three directions of the plane z = 0, one of them the negative x-axis, where the bodies of the flat sets touch. A product of two different points is taken from Sphere inversions, one plane.' },
      { type: 'select', key: 'layout', label: 'Layout of the sheet', def: 0, options: [[0, 'Creased, both planes exact'], [1, 'Smooth, slice not exact']], help: 'The creased layout works for whole powers (others are rounded). The smooth layout exists for the powers 2, 4 and 8 only.' },
    ],
    formula: (p, n) => {
      if (p.layout > 0.5) {
        const k = psReps(n), note = aprIs(n, 2 ** k) ? '' : ` The power ${aprNum(n)} is replaced by ${2 ** k}: this layout exists for the powers 2, 4 and 8 only.`;
        if (k === 0) return 'v¹ = v.' + note;
        return `v${aprSup(2 ** k)} = |v|${aprSup(2 ** k)} · L(d)   with d = v/|v|, w = (x + iy)/(1 − z) the direction d written as one complex number, and L the map w → (2w³ − 1)/(w(2 − w³))${k > 1 ? `, applied ${k} times` : ''}.` + note;
      }
      const k = Math.round(n), whole = aprWhole(n) ? '' : ` The power ${aprNum(n)} is rounded to ${aprNum(k)}: the sheet can only be multiplied by a whole number.`;
      if (k === 1) return 'v¹ = v.' + whole;
      if (k === 0) return 'v⁰ = (1, 0, 0).' + whole;
      return `v${aprSup(k)} = |v|${aprSup(k)} · Φ(${aprNum(k)} · Φ⁻¹(d))   with d = v/|v| and Φ the wrapping of the flat sheet onto the sphere.` + whole;
    },
    about: 'Tried for: a rule with no seam to jump across. A flat sheet tiled with triangles wraps around the sphere of directions as a pillow, and multiplying the sheet is the power. Why it fails: the Julia set for c = −1 is one lump, not a row of bodies. Laid smoothly, the pillow gives a smooth egg, and its slice at z = 0 is not the flat set. Laid so that the planes z = 0 and y = 0 are both exact, the bodies get waists that never close, and the creases of the layout are copied all over the surface as fibres and dust. A smooth pillow gives a rock and a creased one gives fibres, and no layout was found that escapes both. The 3D picture also draws the skin a little outside the true set in places (measured for the creased layout on the Julia set for c = −1: by up to 0.3), so judge the fine detail with care.',
    roundNote: p => (p.layout > 0.5 ? 'Circles on the sphere of directions stay circles, except at the three directions half way between the corners, where three sheets are folded together.'
      : 'Shapes are not kept: a small circle of directions comes out as an oval or a rounded triangle.'),
    crush: (p, n = S.n) => {
      if (p.layout > 0.5) return psReps(n) === 0 ? ['ok', 'Crushes nothing: below 1.5 this layout leaves every point where it is.']
        : ['part', 'Nothing but the origin is crushed onto one point. At three directions in the plane z = 0 (60°, 180° and 300°) the stretch falls to 0, where three sheets wrap around.'];
      if (Math.round(n) === 0) return aprNone();
      return ['ok', (Math.abs(Math.round(n)) < 2 ? 'Crushes nothing at this power.' : 'Nothing but the origin is crushed.') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (p.layout > 0.5) return psReps(n) === 0 ? ['ok', 'Below 1.5 this layout leaves every point where it is.']
        : ['part', 'Smooth everywhere except the origin. Three directions in the plane z = 0 (60°, 180° and 300°) are spots where three sheets meet: smooth, but wrapped three times around.'];
      if (Math.round(n) === 0) return aprConstant();
      return ['no', (Math.abs(Math.round(n)) < 2 ? 'Smooth at this power.' : 'No jump was found, but the layout is creased, and every power copies the creases onto more places.')
        + aprTear(n, ' A power that is not a whole number is rounded, so the picture jumps between whole powers.')];
    },
    slice: (ok, p, n = S.n) => (p.layout > 0.5 ? (psReps(n) === 0 ? 'Below 1.5 this layout leaves every point where it is.'
        : 'The plane z = 0 lands on itself, but it does not follow complex arithmetic: the angle is doubled with a wobble of up to 60°. So the slice is not the flat set.')
      : !aprWhole(n) ? 'The power is rounded to a whole number, so the plane z = 0 follows that whole power and not this one.'
      : ok ? 'The planes z = 0 and y = 0 both follow complex arithmetic exactly. The 2D view of this page still draws the slice with a fringe: measured at n = 2, about 5 to 7% more solid than the flat set.' : 'The plane z = 0 does not follow complex arithmetic.'),
  },
];
