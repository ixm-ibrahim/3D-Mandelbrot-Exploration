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
// ---------- helpers of the rules of round 14 (their checks and pictures: out/r14/rules/)
// cos and sin of an angle in degrees, with a value that should be exactly 0 made exactly 0 (the shader does the same)
const r14CS = deg => [Math.cos(aprRad(deg)), Math.sin(aprRad(deg))].map(c => (Math.abs(c) < 1e-6 ? 0 : c));
// Rotor square: the reference axis, and a direction square to it for a point that lies on the axis itself
function rtAxis(q) {
  const lo = r14CS(q.lon), la = r14CS(q.lat === undefined ? 90 : q.lat);
  return { a: [la[0] * lo[0], la[0] * lo[1], la[1]], side: [-lo[1], lo[0], 0] };
}
// Quaternions, 4D: where the picture point P sits in 4D (real, i, j, k), for a slice at w tilted by `tilt` degrees
function q4Embed(P, q = {}) {
  const [c, s] = r14CS(q.tilt), w = q.w || 0;
  return [P[0] * c - w * s, P[1], P[2], P[0] * s + w * c];
}
// Kleinian squaring: the direction map H. m + 1 caps round the equator, centred at the longitudes
// (2k + 1)·180°/(m + 1), each of angular radius 180°/(m + 1). Inside cap k: the inversion in the sphere that
// crosses the unit sphere at right angles along the cap's rim, then the mirror y -> -y. Outside every cap: the mirror.
function kqDir(d, m) {
  const psi = PI / (m + 1), cp = Math.cos(psi);
  let th = Math.atan2(d[1], d[0]);
  if (th < 0) th += 2 * PI;
  const t = (2 * Math.min(Math.floor(th / (2 * psi)), m) + 1) * psi, a = [Math.cos(t), Math.sin(t)];
  if (!(d[0] * a[0] + d[1] * a[1] > cp)) return [d[0], -d[1], d[2]];
  const C = [a[0] / cp, a[1] / cp], e = [d[0] - C[0], d[1] - C[1], d[2]], s = Math.tan(psi) ** 2 / (e[0] * e[0] + e[1] * e[1] + e[2] * e[2]);
  return [C[0] + s * e[0], -(C[1] + s * e[1]), s * e[2]];
}
const kqCaps = n => Math.max(2, Math.floor(Math.abs(n) + 0.5));   // the whole power the caps are laid out for
// two: a direction nearer the plane y = 0 than the plane z = 0 uses the same caps laid round the circle of y = 0
function kqPower(v, n, two) {
  const r = Math.hypot(v[0], v[1], v[2]);
  if (r < 1e-20) return n > 0 ? [0, 0, 0] : [aprPow(r, n), 0, 0];
  const d = [v[0] / r, v[1] / r, v[2] / r], sw = two && Math.abs(d[2]) > Math.abs(d[1]);
  let h = kqDir(sw ? [d[0], d[2], d[1]] : d, kqCaps(n));
  if (sw) h = [h[0], h[2], h[1]];
  const R = aprPow(r, n);
  return n < 0 ? [R * h[0], -R * h[1], -R * h[2]] : [R * h[0], R * h[1], R * h[2]];
}
// ---------- helpers of the rule of round 15, Square pillow (its checks and pictures: out/r15/entry/)
// Directions are laid on a square pillowcase: s runs round the pillow (one full turn is 1), t from the south seam
// (0) to the north seam (1/2), and each seam is zipped shut. For the whole power m the belt t0 = 1/(m + 1) is the
// equator, with s the longitude. Each half sphere is laid out the same way: p = (x, y)/(1 + |z|) =
// ((1 + B²)/2 · cos 2πs, B · sin 2πs), B = 1 on the equator and B = 0 on the seam. North of the belt
// B = sinh(bn·(1/2 − t))/sinh(bn·wn), south of it B = sinh(bs·t)/sinh(bs·ws), with wn = 1/2 − t0 and ws = t0 the widths
// of the two strips and b·coth(b·width) = 2π, so that a step along t and a step along s are the same length on the belt.
// The power multiplies s and t by m (with a mirror, s -> −s) and folds the result back onto the pillow.
const SP_MAXN = 5;     // the layout is made for the whole powers 2 to SP_MAXN (b·coth(b·ws) = 2π has no answer above 5)
const SP_LAY = {};
function spLayout(m) {
  if (SP_LAY[m]) return SP_LAY[m];
  const t0 = 1 / (m + 1), b = w => {             // x·coth(x) = 2π·w for x = b·w, by halving
    let lo = 1e-9, hi = 40;
    for (let i = 0; i < 100; i++) { const x = 0.5 * (lo + hi); if (x / Math.tanh(x) < 2 * PI * w) lo = x; else hi = x; }
    return 0.5 * (lo + hi) / w;
  };
  const bn = b(0.5 - t0), bs = b(t0);
  return (SP_LAY[m] = { t0, bn, bs, hn: Math.sinh(bn * (0.5 - t0)), hs: Math.sinh(bs * t0) });
}
// beta = B² for a point p of the unit disc: the root in [0, 1] of beta·(1 + beta)² − 4px²·beta − py²·(1 + beta)² = 0.
// The left side curves upward on [0, 1], so Newton's steps from a value above the root come down onto it and never
// pass it. The start is the root of the same equation without its beta³ (never below the true root, and nearly on
// it near the seams); measured, 5 steps reach the last digit (out/r15/entry/beta_steps2.py).
function spBeta(px, py) {
  const X = 4 * px * px, Y = py * py;
  if (!(Y > 0)) return Math.max(0, 2 * Math.abs(px) - 1);
  const c = 1 - X - 2 * Y, a = 2 - Y, s = Math.sqrt(c * c + 4 * a * Y);
  let b = Math.min(1, px * px + Y, c >= 0 ? 2 * Y / (c + s) : (s - c) / (2 * a));
  for (let i = 0; i < 5; i++) {
    const q = 1 + b, g = b * q * q - X * b - Y * q * q, dg = q * (q + 2 * b - 2 * Y) - X;
    if (!(g > 0) || !(dg > 0)) break;
    b = Math.max(b - g / dg, 0);
  }
  return b;
}
// (cos, sin) of m times the angle, by multiplying: no angle is ever measured
function spTurn(c, s, m) {
  let a = c, b = s;
  for (let i = 1; i < m; i++) [a, b] = [a * c - b * s, a * s + b * c];
  return [a, b];
}
// v^n = |v|^n · dir(D(pil(v/|v|))), for the whole power m nearest to n (2 to SP_MAXN). A point with z exactly 0
// takes the complex power, so its result has z exactly 0.
function spPower(v, n) {
  const m = clamp(Math.floor(Math.abs(n) + 0.5), 2, SP_MAXN), [x, y, z] = v, r = Math.hypot(x, y, z);
  if (r < 1e-20) return n > 0 ? [0, 0, 0] : [aprPow(r, n), 0, 0];
  if (z === 0 && n === 2) return [x * x - y * y, 2 * x * y, 0];
  const R = n === 2 ? r * r : aprPow(r, n);
  let h;
  if (z === 0) { const e = spTurn(x / r, y / r, m); h = [e[0], e[1], 0]; }
  else {
    const K = spLayout(m), den = r + Math.abs(z), px = x / den, py = y / den;
    const beta = spBeta(px, py), B = Math.sqrt(beta);
    let cn = B > 0 ? 2 * px / (1 + beta) : clamp(2 * px, -1, 1), sn = B > 0 ? py / B : Math.sqrt(1 - cn * cn);
    const l = Math.hypot(cn, sn);
    cn /= l; sn /= l;
    const t = z > 0 ? 0.5 - Math.asinh(B * K.hn) / K.bn : Math.asinh(B * K.hs) / K.bs;       // where on the grid
    const yy = m * t, w = yy - Math.floor(yy), back = w > 0.5, t2 = back ? 1 - w : w;       // times m, folded back
    const e = spTurn(cn, sn, m), north = t2 >= K.t0;
    const B2 = clamp(north ? Math.sinh(K.bn * (0.5 - t2)) / K.hn : Math.sinh(K.bs * t2) / K.hs, 0, 1);
    const qx = 0.5 * (1 + B2 * B2) * e[0], qy = B2 * (back ? e[1] : -e[1]), q2 = qx * qx + qy * qy;
    h = [2 * qx / (1 + q2), 2 * qy / (1 + q2), (north ? 1 - q2 : q2 - 1) / (1 + q2)];
  }
  return n < 0 ? [R * h[0], -R * h[1], -R * h[2]] : [R * h[0], R * h[1], R * h[2]];
}
// ---------- helpers of the two rules of round 16, Turning plane (their checks and pictures: out/r16/entry/)
// The one-plane power P is taken about a reference plane through the x-axis that turns with the point:
//   F(v) = Rot(psi) P(Rot(−psi) v),   psi = q·(phi − sin(2m·phi)/(2m)),   phi = atan2(z, y),
// with Rot(a) the turn about the x-axis by the angle a, m the whole number nearest to |n| (at least 1), and
// q = 1 − m ("away": the plane turns against the point) or q = 1 ("along": it turns with the point). At n = 2
// that is m = 2 and q = −1 or +1. psi stands still (a flat spot) where phi is a multiple of 180°/m.
const tpPlanes = n => Math.max(1, Math.floor(Math.abs(n) + 0.5));
// the one-plane power with no turn and no lift; at n = 2 the closed form (the shader's aprMsq)
function tpOne(v, n) {
  if (n !== 2) return MATH.mercator(v, n, {});
  const [x, y, z] = v, r2 = x * x + y * y + z * z;
  if (r2 < 1e-30) return [0, 0, 0];
  const f = r2 / (r2 + z * z);
  return [f * (x * x - y * y), f * 2 * x * y, f * 2 * Math.sqrt(r2) * z];
}
// A point with z exactly 0 takes the one-plane power as it stands (its reference plane is z = 0), so its result has
// z exactly 0: a half turn worked out with sin(π) would leave a small z.
function tpPower(v, n, along) {
  const [x, y, z] = v;
  if (z === 0) { const w = tpOne([x, y, 0], n); return [w[0], w[1], 0]; }
  const m = tpPlanes(n), q = along ? 1 : 1 - m, phi = Math.atan2(z, y);
  const psi = q * (phi - Math.sin(2 * m * phi) / (2 * m)), c = Math.cos(psi), s = Math.sin(psi);
  const w = tpOne([x, c * y + s * z, c * z - s * y], n);
  return [w[0], c * w[1] - s * w[2], s * w[1] + c * w[2]];
}
// ---------- helper of the rule of round 20, Wind, then square (its checks and pictures: out/r20/entry/)
// The other planes through the x-axis get no arithmetic of their own. The turn a of a point round the x-axis (0 on
// the side y > 0 of the plane z = 0) is first wound, a -> g(a) = k·a − (k − 1)·sin(2k·a)/(2k), and then the one-plane
// power P is taken, with nothing turned back:   F(v) = P(x, ρ·cos g, ρ·sin g),   ρ the distance of v from the x-axis.
// k is a whole odd number: m, the whole number nearest to |n| (at least 1), or m + 1 when m is even (an even count
// would send the half y < 0 of the plane z = 0 onto the half y > 0). g has slope 1 wherever g(a) is a multiple of
// 180°: those 2k half-planes are sent into the plane z = 0 with no squeeze. cos and sin of k·a come from multiplying
// (y + iz)/ρ by itself, and sin(2k·a) = 2·sin(k·a)·cos(k·a), so no angle is ever measured.
const wsCount = n => { const m = Math.max(1, Math.floor(Math.abs(n) + 0.5)); return m % 2 ? m : m + 1; };
// A point with z exactly 0 takes the one-plane power as it stands, so its result has z exactly 0.
function wsPower(v, n) {
  const [x, y, z] = v;
  if (z === 0) { const w = tpOne([x, y, 0], n); return [w[0], w[1], 0]; }
  const k = wsCount(n), rho = Math.hypot(y, z);
  if (k === 1 || !(rho > 1e-18)) return tpOne(v, n);
  const e = spTurn(y / rho, z / rho, k), d = (k - 1) * e[0] * e[1] / k, cd = Math.cos(d), sd = Math.sin(d);
  return tpOne([x, rho * (e[0] * cd + e[1] * sd), rho * (e[1] * cd - e[0] * sd)], n);
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
  // ----- round 14
  // Quaternions, 4D: the power is the quaternion power (the Lathe with spin 1). What is new sits in the shader's
  // cmap and zmap: the picture point is a point of a 3D slice of 4D (see q4Embed and GL_QUAT4).
  quat4(v, n) { return MATH.lathe(v, n, {}); },
  // Rotor square: the angle between the reference axis and the point is multiplied, in the sheet that holds both.
  rotor(v, n, q = {}) {
    const r = Math.hypot(v[0], v[1], v[2]);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const { a, side } = rtAxis(q), x = v[0] * a[0] + v[1] * a[1] + v[2] * a[2];
    const s = [v[0] - x * a[0], v[1] - x * a[1], v[2] - x * a[2]], rho = Math.hypot(s[0], s[1], s[2]);
    const u = rho > 0 ? [s[0] / rho, s[1] / rho, s[2] / rho] : side, g = Math.atan2(rho, x) * n, R = aprPow(r, n), cg = Math.cos(g), sg = Math.sin(g);
    return [R * (cg * a[0] + sg * u[0]), R * (cg * a[1] + sg * u[1]), R * (cg * a[2] + sg * u[2])];
  },
  // Rotor square with a frame: R = (turn about z by the longitude) after (tip up by the latitude) carries the
  // x-axis onto the point's direction with no roll. v^n = |v|^n * R^n(x-axis), R^n the turn about R's own axis by
  // n times its angle. As a quaternion R = w + m, with the half angles of the latitude (1) and the longitude (2).
  rotorframe(v, n) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const hb = 0.5 * Math.atan2(z, Math.hypot(x, y)), hp = 0.5 * Math.atan2(y, x);
    const c1 = Math.cos(hb), s1 = Math.sin(hb), c2 = Math.cos(hp), s2 = Math.sin(hp);
    const w = c1 * c2, m = [s1 * s2, -s1 * c2, c1 * s2], lm = Math.hypot(m[0], m[1], m[2]);
    const h = Math.atan2(lm, w) * n, k = lm > 1e-30 ? Math.sin(h) / lm : 0;
    const a = Math.cos(h), b = k * m[0], c = k * m[1], d = k * m[2], R = aprPow(r, n);
    return [R * (a * a + b * b - c * c - d * d), 2 * R * (b * c + a * d), 2 * R * (b * d - a * c)];
  },
  // Kleinian squaring: |v|^n times the direction map H (see kqDir), with one family of caps or two.
  kleinsq(v, n) { return kqPower(v, n, false); },
  kleinsq2(v, n) { return kqPower(v, n, true); },
  // ----- round 15
  // Square pillow: both coordinates of a pillowcase grid are multiplied (see spPower).
  sqpillow(v, n) { return spPower(v, n); },
  // ----- round 16
  // Turning plane: the one-plane power about a reference plane that turns with the point (see tpPower).
  turnaway(v, n) { return tpPower(v, n, false); },
  turnalong(v, n) { return tpPower(v, n, true); },
  // ----- round 20
  // Wind, then square: the turn round the x-axis is wound a whole odd number of times, then the one-plane power (see wsPower).
  windsq(v, n) { return wsPower(v, n); },
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
// ----- round 14 (the same steps as the JavaScript above: q4Embed, rtAxis, MATH.rotorframe, kqDir, kqPower)
const GL_R14 = `
vec2 r14CS(float deg){ float a = radians(deg); vec2 cs = vec2(cos(a), sin(a)); return vec2(abs(cs.x) < 1e-6 ? 0.0 : cs.x, abs(cs.y) < 1e-6 ? 0.0 : cs.y); }`;
// Quaternions, 4D. uA.x: where the slice sits on the fourth axis. uA.y: its tilt toward that axis, degrees.
// uA.z: the fourth coordinate of c in a Julia picture. A quaternion orbit of q^n + c never leaves the flat sheet or
// the 3D space spanned by 1, the imaginary part of c and the imaginary part of its start, so three numbers hold it:
// (real part, part along Im c, part across Im c), and the step is the Lathe's. cmap gives c in those numbers, and
// zmap (the hook APR_ZMAP in the orbit code) the start of a Julia orbit. Both keep the turn about the x-axis that
// (y, z) had, so that with all three dials at 0 they change nothing: then this is the Lathe to the last bit.
const GL_QUAT4 = GL_APR + GL_R14 + `
#define APR_ZMAP 1
vec4 q4E(vec3 P){ vec2 t = r14CS(uA.y); return vec4(P.x * t.x - uA.x * t.y, P.y, P.z, P.x * t.y + uA.x * t.x); }
// the constant in 4D: in a Julia picture the page's c with the dial for its fourth part, otherwise the picture point
vec4 q4C(vec3 c){ return uJulia > 0.5 ? vec4(c, uA.z) : q4E(c); }
vec2 q4Dir(vec2 v){ float l = length(v); return l > 1e-12 ? v / l : vec2(1.0, 0.0); }
vec3 cmap(vec3 c){
  vec4 k = q4C(c);
  if (k.w == 0.0) return k.xyz;
  return vec3(k.x, length(k.yzw) * q4Dir(k.yz));
}
vec3 zmap(vec3 P, vec3 c){
  vec4 E = q4E(P), k = q4C(c);
  if (k.w == 0.0 && uA.x == 0.0 && uA.y == 0.0) return E.xyz;
  float m = length(k.yzw);
  vec3 u = m > 1e-12 ? k.yzw / m : vec3(1.0, 0.0, 0.0);
  vec2 d = q4Dir(k.yz);
  float b = dot(E.yzw, u), mu = length(E.yzw - b * u);
  return vec3(E.x, b * d + mu * vec2(-d.y, d.x));
}
vec3 mul(vec3 a, vec3 b){ return aprCap(vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float rho = length(v.yz), a = at2(rho, v.x) * n;
  vec2 u = rho > 0.0 ? v.yz / rho : vec2(1.0, 0.0);
  return aprPow(r, n) * vec3(cos(a), sin(a) * u);
}
vec3 sqr(vec3 v){ return aprCap(vec3(v.x * v.x - dot(v.yz, v.yz), 2.0 * v.x * v.yz)); }`;
// Rotor square. uA.x, uA.y: the longitude and the latitude of the reference axis, degrees.
const GL_ROTOR = GL_APR + GL_R14 + `
vec3 rtAxis(){ vec2 lo = r14CS(uA.x), la = r14CS(uA.y); return vec3(la.x * lo, la.y); }
vec3 mul(vec3 p, vec3 q){
  vec3 a = rtAxis();
  float x = dot(p, a), y = dot(q, a);
  vec3 s = p - x * a, t = q - y * a;
  return aprCap((x * y - dot(s, t)) * a + x * t + y * s);
}
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  vec3 a = rtAxis();
  float x = dot(v, a);
  vec3 s = v - x * a;
  float rho = length(s), g = at2(rho, x) * n;
  vec2 lo = r14CS(uA.x);
  vec3 u = rho > 0.0 ? s / rho : vec3(-lo.y, lo.x, 0.0);
  return aprPow(r, n) * (cos(g) * a + sin(g) * u);
}
vec3 sqr(vec3 v){
  vec3 a = rtAxis();
  float x = dot(v, a);
  vec3 s = v - x * a;
  return aprCap((x * x - dot(s, s)) * a + 2.0 * x * s);
}
vec3 cmap(vec3 c){ return c; }`;
// Rotor square with a frame. No dials. mul(a, b) = |a| * Ra(b), with Ra the turn that carries the x-axis onto a
// with no roll; sqr(v) = mul(v, v), written out.
const GL_ROTORFRAME = GL_APR + `
vec3 mul(vec3 a, vec3 b){
  float r = length(a), rho = length(a.xy);
  if (r < 1e-20) return vec3(0.0);
  vec2 cb = vec2(rho, a.z) / r, cp = rho > 0.0 ? a.xy / rho : vec2(1.0, 0.0);
  vec3 t = vec3(b.x * cb.x - b.z * cb.y, b.y, b.x * cb.y + b.z * cb.x);
  return aprCap(r * vec3(t.x * cp.x - t.y * cp.y, t.x * cp.y + t.y * cp.x, t.z));
}
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float hb = 0.5 * at2(v.z, length(v.xy)), hp = 0.5 * at2(v.y, v.x);
  float c1 = cos(hb), s1 = sin(hb), c2 = cos(hp), s2 = sin(hp);
  float w = c1 * c2;
  vec3 m = vec3(s1 * s2, -s1 * c2, c1 * s2);
  float lm = length(m), h = at2(lm, w) * n, a = cos(h);
  vec3 q = lm > 1e-30 ? (sin(h) / lm) * m : vec3(0.0);
  return aprPow(r, n) * vec3(a * a + q.x * q.x - q.y * q.y - q.z * q.z, 2.0 * (q.x * q.y + a * q.z), 2.0 * (q.x * q.z - a * q.y));
}
vec3 sqr(vec3 v){
  float r = length(v), rho = length(v.xy);
  if (rho < 1e-20) return vec3(-min(v.z * v.z, APR_CAP), 0.0, 0.0);
  float z2 = v.z * v.z;
  return aprCap(vec3(v.x * v.x - (z2 * v.x + r * v.y * v.y) / rho, v.y * (v.x * (rho + r) - z2) / rho, v.z * (rho + v.x)));
}
vec3 cmap(vec3 c){ return c; }`;
// Kleinian squaring, with one family of caps (kleinsq) or two (kleinsq2). No dials. The product of two different
// points is the one-plane product of Sphere inversions (aprMmul).
const GL_KLEINSQ_CORE = GL_APR + GL_TRIED_MERC + `
vec3 kqDir(vec3 d, float m){
  float psi = PI / (m + 1.0), cp = cos(psi), th = at2(d.y, d.x);
  if (th < 0.0) th += 2.0 * PI;
  float t = (2.0 * min(floor(th / (2.0 * psi)), m) + 1.0) * psi;
  vec2 a = vec2(cos(t), sin(t));
  if (!(dot(d.xy, a) > cp)) return vec3(d.x, -d.y, d.z);
  vec3 C = vec3(a / cp, 0.0), e = d - C;
  float tp = tan(psi);
  vec3 h = C + (tp * tp / dot(e, e)) * e;
  return vec3(h.x, -h.y, h.z);
}
vec3 kqPw(vec3 v, float n, bool two){
  float r = length(v);
  if (r < 1e-20) return n > 0.0 ? vec3(0.0) : vec3(aprPow(r, n), 0.0, 0.0);
  vec3 d = v / r;
  bool sw = two && abs(d.z) > abs(d.y);
  vec3 h = kqDir(sw ? d.xzy : d, max(2.0, floor(abs(n) + 0.5)));
  if (sw) h = h.xzy;
  if (n < 0.0) h.yz = -h.yz;
  return aprPow(r, n) * h;
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 cmap(vec3 c){ return c; }`;
const GL_KLEINSQ = GL_KLEINSQ_CORE + `
vec3 pw(vec3 a, float n){ return kqPw(a, n, false); }
vec3 sqr(vec3 a){ return kqPw(a, 2.0, false); }`;
const GL_KLEINSQ2 = GL_KLEINSQ_CORE + `
vec3 pw(vec3 a, float n){ return kqPw(a, n, true); }
vec3 sqr(vec3 a){ return kqPw(a, 2.0, true); }`;
// ----- round 15 (the same steps as the JavaScript above: spLayout, spBeta, spTurn, spPower)
// Square pillow. No dials. The product of two different points is the one-plane product of Sphere inversions (aprMmul).
// spLay gives the layout of the whole power m: K = (bn, bs, sinh(bn·wn), sinh(bs·ws)) and the belt t0.
const spGl = x => { const t = String(+x.toPrecision(10)); return /[.e]/.test(t) ? t : t + '.0'; };
const GL_SQPILLOW = GL_APR + GL_TRIED_MERC + `
const float SP_MAXN = ${spGl(SP_MAXN)};
void spLay(float m, out vec4 K, out float t0){
${Array.from({ length: SP_MAXN - 1 }, (_, i) => { const m = SP_MAXN - i, k = spLayout(m); return `  ${m > 2 ? `if (m > ${m - 0.5}) ` : ''}{ K = vec4(${[k.bn, k.bs, k.hn, k.hs].map(spGl).join(', ')}); t0 = ${spGl(k.t0)}; ${m > 2 ? 'return; ' : ''}}`; }).join('\n')}
}
float spBeta(vec2 p){
  float X = 4.0 * p.x * p.x, Y = p.y * p.y;
  if (!(Y > 0.0)) return max(0.0, 2.0 * abs(p.x) - 1.0);
  float c = 1.0 - X - 2.0 * Y, a = 2.0 - Y, s = sqrt(c * c + 4.0 * a * Y);
  float b = min(min(1.0, p.x * p.x + Y), c >= 0.0 ? 2.0 * Y / (c + s) : (s - c) / (2.0 * a));
  for (int i = 0; i < 5; i++){
    float q = 1.0 + b, g = b * q * q - X * b - Y * q * q, dg = q * (q + 2.0 * b - 2.0 * Y) - X;
    if (!(g > 0.0) || !(dg > 0.0)) break;
    b = max(b - g / dg, 0.0);
  }
  return b;
}
vec2 spTurn(vec2 u, float m){
  vec2 e = u;
  for (int i = 1; i < 8; i++){ if (float(i) > m - 0.5) break; e = cmul(e, u); }
  return e;
}
vec3 spPw(vec3 v, float n){
  float m = clamp(floor(abs(n) + 0.5), 2.0, SP_MAXN), r = length(v);
  if (r < 1e-20) return n > 0.0 ? vec3(0.0) : vec3(aprPow(r, n), 0.0, 0.0);
  if (v.z == 0.0 && n == 2.0) return aprCap(vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, 0.0));
  float R = n == 2.0 ? min(r * r, APR_CAP) : aprPow(r, n);
  vec3 h;
  if (v.z == 0.0) h = vec3(spTurn(v.xy / r, m), 0.0);
  else {
    vec4 K; float t0;
    spLay(m, K, t0);
    vec2 p = v.xy / (r + abs(v.z));
    float beta = spBeta(p), B = sqrt(beta);
    vec2 u = B > 0.0 ? vec2(2.0 * p.x / (1.0 + beta), p.y / B) : vec2(clamp(2.0 * p.x, -1.0, 1.0), 0.0);
    if (B > 0.0) u /= length(u); else u.y = sqrt(1.0 - u.x * u.x);
    float t = v.z > 0.0 ? 0.5 - asinh(B * K.z) / K.x : asinh(B * K.w) / K.y;
    float yy = m * t, w = yy - floor(yy);
    bool back = w > 0.5;
    float t2 = back ? 1.0 - w : w;
    vec2 e = spTurn(u, m);
    if (!back) e.y = -e.y;
    bool north = t2 >= t0;
    float B2 = clamp(north ? sinh(K.x * (0.5 - t2)) / K.z : sinh(K.y * t2) / K.w, 0.0, 1.0);
    vec2 q = vec2(0.5 * (1.0 + B2 * B2) * e.x, B2 * e.y);
    float q2 = dot(q, q);
    h = vec3(2.0 * q, north ? 1.0 - q2 : q2 - 1.0) / (1.0 + q2);
  }
  if (n < 0.0) h.yz = -h.yz;
  return R * h;
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return spPw(a, n); }
vec3 sqr(vec3 a){ return spPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// ----- round 16
// Turning plane, away and along (see tpPower): the one-plane power about a reference plane through the x-axis that
// turns with the point. The two differ only in tpTurn, how far the plane turns for the whole power m. No dials.
// The product of two different points is the one-plane product (aprMmul).
const glTurning = turn => GL_APR + GL_TRIED_MERC + `
float tpTurn(float m){ return ${turn}; }
vec3 tpOne(vec3 v, float n){ return n == 2.0 ? aprMsq(v) : aprMpw(v, n); }
vec3 tpPw(vec3 v, float n){
  if (v.z == 0.0){ vec3 w = tpOne(v, n); return vec3(w.xy, 0.0); }
  float m = max(1.0, floor(abs(n) + 0.5)), phi = atan(v.z, v.y);
  float psi = tpTurn(m) * (phi - sin(2.0 * m * phi) / (2.0 * m)), c = cos(psi), s = sin(psi);
  vec3 w = tpOne(vec3(v.x, c * v.y + s * v.z, c * v.z - s * v.y), n);
  return vec3(w.x, c * w.y - s * w.z, s * w.y + c * w.z);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return tpPw(a, n); }
vec3 sqr(vec3 a){ return tpPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
const GL_TURNAWAY = glTurning('1.0 - m'), GL_TURNALONG = glTurning('1.0');

// ----- round 20
// Wind, then square (see wsPower): the turn round the x-axis is wound k times, k whole and odd, with slope 1 where the
// wound turn is a multiple of 180°, and then the one-plane power is taken. No dials. The product of two different
// points is the one-plane product (aprMmul).
const GL_WINDSQ = GL_APR + GL_TRIED_MERC + `
float wsCount(float n){ float m = max(1.0, floor(abs(n) + 0.5)); return mod(m, 2.0) > 0.5 ? m : m + 1.0; }
vec3 wsOne(vec3 v, float n){ return n == 2.0 ? aprMsq(v) : aprMpw(v, n); }
vec3 wsPw(vec3 v, float n){
  if (v.z == 0.0){ vec3 w = wsOne(v, n); return vec3(w.xy, 0.0); }
  float k = wsCount(n), rho = length(v.yz);
  if (k < 1.5 || !(rho > 1e-18)) return wsOne(v, n);
  vec2 u = v.yz / rho, e = u;
  int kk = int(k + 0.5);
  for (int i = 1; i < 16; i++){ if (i >= kk) break; e = cmul(e, u); }
  float d = (k - 1.0) * e.x * e.y / k;
  return wsOne(vec3(v.x, rho * cmul(e, vec2(cos(d), -sin(d)))), n);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return wsPw(a, n); }
vec3 sqr(vec3 a){ return wsPw(a, 2.0); }
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
  { id: 'kleinian', title: 'Inversions by region (the paper’s road)' },
  { id: 'quaternion', title: 'Quaternions' },
  { id: 'pillow', title: 'Doubling on a pillow grid' },
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

// ---------- the words of the five entries of round 14 (measured in out/r14/rules/: see checks.txt there)
// R14-TEXTS-BEGIN
const q4Words = p => (!p.tilt ? `(x, y, z, ${aprNum(p.w || 0)})` : `(x·cos t − w·sin t, y, z, x·sin t + w·cos t) with w = ${aprNum(p.w || 0)} and t = ${aprDeg(p.tilt)}`);
const Q4_HELP_W = 'Slides the slice along the fourth axis, the way a cut plane slides through a solid. At 0 the slice passes through the middle of the 4D set. In a Mandelbrot picture the solid shrinks as the slice moves away from 0, and past about 1.12 either way nothing is left. Play sweeps the slice there and back.';
const Q4_HELP_TILT = 'Leans the slice out of the first three axes: the picture’s x direction is turned toward the fourth axis. At 90 or −90 it runs along the fourth axis itself, and a Mandelbrot picture is then a ball of nested shells, the same from every side.';
const Q4_HELP_CW = 'Used by Julia pictures only: the fourth part of c, after the three parts that the c dials of the page give. Away from 0 the picture is a slice of a Julia set whose c points partly out of the picture’s own three directions.';
const Q4_NOTE = 'Checked against plain quaternion multiplying in 4D: for 15 settings of these dials (Mandelbrot and Julia pictures, powers 2 and 3) and 4,096 points each, the same points stay bounded, with no exception. With the three dials at 0 the picture is that of Quaternion square (Lathe), pixel for pixel (two pictures compared). The page’s own test was checked the same way on three more settings, 12,288 points each. What the pictures show: every slice of the 4D Mandelbrot set is a solid of rings round the x-axis, smaller the further the slice sits from 0, and at a tilt of 90 it is a plain ball. The Julia sets are the classic quaternion Julia shapes, smooth sheets like pulled taffy, and the dials show other slices of them. No slice shows finer detail than the Lathe’s pictures do.';
const Q4_ABOUT = 'A quaternion is a number with four parts: one real part and three imaginary ones. Squaring and adding c works for such numbers as it does for complex numbers, so the Mandelbrot set and the Julia sets of q → q² + c are shapes in four dimensions. No picture can hold all of one. This entry shows a flat 3D slice: the picture’s y and z are two of the imaginary directions, its x is the real direction (leaned toward the fourth axis by the tilt), and the first dial says where on the fourth axis the slice sits. In a Mandelbrot picture the picture point is c and the orbit starts at 0. In a Julia picture c is the page’s c with a fourth part from the third dial, and the picture point is where the orbit starts. Where it falls short: the 4D Mandelbrot set is the flat set swept round the real axis in every imaginary direction, so a slice of it can only be rings or shells, and the fourth dimension adds no detail to it. The Learn tab shows the step in three numbers, as for the Lathe, and leaves the slice out.';
const Q4_SLICE_OFF = 'The power itself follows complex arithmetic in the plane z = 0. But with these dials the picture’s plane z = 0 is no longer the flat plane of the 4D set, so the slice at z = 0 is not the flat set (measured for the Mandelbrot solid with the slice at 0.3, and with tilts of 30° and 90°; and for the rabbit’s Julia set with c at 0.3 on the fourth axis). Set the three dials to 0 to get the flat set back.';
const RT_HELP_LON = 'Turns the reference axis round the z-axis. It changes the picture only while the latitude is not 90 or −90. With the latitude at 0, the slice at z = 0 is the flat set turned by this angle.';
const RT_HELP_LAT = 'Tips the reference axis up out of the plane z = 0. At 90 it is the z-axis, as in the recipe. At 0, with the longitude at 0 too, it is the x-axis, and the rule is then Quaternion square (Lathe) itself.';
const RT_NOTE = 'The recipe from geometric algebra: pick a reference direction, find the rotor (the turn) that carries it onto v, square the rotor, apply it to the reference direction, and scale by |v|². Measured: with the reference along the x-axis the rule is Quaternion square (Lathe) to 15 digits, and its picture is the Lathe’s, pixel for pixel. For every other axis tried (5 of them) it is the same rule turned in space, and its Mandelbrot solid is the Lathe’s solid turned the same way: 4,000 points each, no exception. So the picture brings nothing the Lathe does not have. The dials only choose where the rings lie: round the reference axis. “Quaternion square, twisted” is this rule with the reference axis turned inside the plane z = 0, followed by a turn back about the z-axis.';
const RT_ABOUT = 'A rotor is the name geometric algebra gives a turn. To square a point v, the recipe takes the turn that carries a chosen reference axis straight onto the direction of v, does that turn twice, and scales the length to |v|². The turn swings by the angle between the axis and v, inside the sheet that holds both. So the square stands at twice that angle from the axis, and the power n at n times it. Rotors are the same thing as quaternions of length 1, and that is why the recipe leads to the quaternion square and to nothing new: the solid is the one that Quaternion square (Lathe) draws, with its rings round the reference axis. With the recipe’s own choice, the z-axis, the flat set stands upright, in every plane through the z-axis, and the plane z = 0 cuts the solid across its rings: that slice is a set of circles.';
const RT_SLICE_OFF = 'No. With the reference axis out of the plane z = 0, that plane does not land on itself, and the slice at z = 0 is not the flat set (measured with the axis at latitude 30° and 90°). The flat set lies in every plane through the reference axis instead.';
const RF_TAG = 'Carry a whole frame onto the point, with no roll, and do that turn twice. The plane z = 0 is exact, but the rule tears at the z-axis and crushes half of the plane y = 0.';
const RF_NOTE = 'The recipe of Rotor square leaves one thing open: a turn that carries one axis onto the point may also roll about that axis. Here a whole frame is carried, x forward and z up, with no roll: a tip up by the latitude of the point, then a turn about the z-axis by its longitude. Doing that same turn twice gives the square. Measured at n = 2: the plane z = 0 follows complex arithmetic exactly, and so does the half of the plane y = 0 with x > 0. The other half of that plane is crushed onto the positive x-axis. Directions next to the z-axis are thrown all the way round the equator, which tears the solid along that axis, and about 13% of all directions, most of them near the poles, come out turned over, as a mirror image. A product of two different points a and b is |a| times b, turned by the turn of a.';
const RF_ABOUT = 'A different rule from the Lathe and from the Mandelbulb, though all three agree in the plane z = 0. The Mandelbulb doubles the longitude and the latitude separately. This rule applies the point’s own turn to the point, which doubles the longitude only on the equator, and the latitude only on the half of the plane y = 0 with x > 0. On average its answer points 33° away from the Lathe’s and 39° away from the Mandelbulb’s (largest: 175° for both). What the pictures show: smooth layered sheets wound like a shell, with no fine bumps. In a Julia set the crushed half of the plane y = 0 shows as a large flat wall: for c = −1 it is half a disc as wide as the whole set. The slice at z = 0 is the flat set, and the fine detail is found only where the solid meets that plane.';
const RF_ROUND = 'Exact in the plane z = 0. Away from it shapes are squashed, without limit beside the z-axis and beside the half-plane y = 0, x < 0.';
const RF_CRUSH2 = 'Crushes the half-plane y = 0, x < 0 onto the positive x-axis (measured), where the plane sends only the negative x-axis there. About 13% of directions come out turned over.';
const RF_CRUSHN = 'Measured at n = 2 only: there the half-plane y = 0, x < 0 is crushed onto the positive x-axis. Other powers were not measured.';
const RF_SMOOTH = 'Torn along the z-axis: directions next to a pole are thrown all the way round the equator (measured: they land up to 180° apart at n = 2 and 3, and 121° apart at n = 4). Across the half-plane y = 0, x < 0 there is no jump at the powers 2, 3 and 4 (measured).';
const RF_SLICE = 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set. So does the half of the plane y = 0 with x > 0. The half with x < 0 does not.';
const KQ_WOBBLE = 'measured: up to 17.6° at n = 2, 31.6° at n = 3 and 42.6° at n = 4';
const kqFormula = (n, two) => {
  const m = kqCaps(n), whole = aprWhole(n) && n >= 2;
  return `v${whole ? aprSup(m) : 'ⁿ'} = |v|${whole ? aprSup(m) : 'ⁿ'} · H(d)   with d = v/|v| the direction of v. For H, ${m + 1} round caps lie side by side round the equator, each reaching ${aprDeg(180 / (m + 1))} from its centre. A direction inside a cap is turned inside out through the sphere that stands on the rim of that cap (one sphere inversion) and then mirrored, y → −y. A direction outside every cap is only mirrored.`
    + (m === 2 ? ' The three spheres have radius √3 and centres (1, √3, 0), (−2, 0, 0) and (1, −√3, 0), as in the paper.' : '')
    + (two ? ' A direction nearer the plane y = 0 than the plane z = 0 uses the same caps laid round the circle of the plane y = 0, with the mirror z → −z.' : '')
    + (whole ? '' : ` The caps are those of the whole power ${m}; only the length follows the power ${aprNum(n)}.` + (n < 0 ? ' A negative power ends with one more inversion.' : ''));
};
const KQ_TAG = 'Tried: squaring rebuilt from sphere inversions, a different one in each region of the sphere of directions (a reading of the first construction in Kučera’s paper). Failed: its slice at z = 0 is a cousin of the flat set, not the flat set.';
const KQ_NOTE = 'A reading of the first construction in Václav Kučera’s paper (Bridges 2019). The paper leaves out the details, so this is rebuilt from its text and may differ from what its author drew. Measured: the rule has no jump anywhere on the sphere of directions, and it keeps shapes inside each cap and outside the caps. On the equator it follows the pattern of zⁿ but not its numbers: at n = 2 it agrees with angle doubling in six directions, 60° apart, and is up to 17.6° off in between. So the slice at z = 0 is a cousin of the flat set: about 80% of the flat Mandelbrot set lies inside the slice, and about an eighth of the slice lies outside the flat set (for the Julia set of c = −1: about 62%, and about an eighth). A quarter of all directions, the two patches round the poles that no cap covers, are only mirrored. A product of two different points is taken from Sphere inversions, one plane.';
const KQ_ABOUT = 'Kučera’s paper replaces squaring by sphere inversions, a different one in each region of the sphere of directions, the way a Kleinian group is built from a few inversions. This entry rebuilds its first construction: for the square, three spheres stand round the equator, each crossing the unit sphere at right angles, and a direction inside one of them is inverted in it and then mirrored. What the pictures show: the Mandelbrot solid is one lumpy body with a spike, much like the solid of Sphere inversions, one plane, but with creases. The Julia set for c = −1 is a chain of bodies along the x-axis with small buds on them. The rabbit is one angular lump, and for a c off the plane z = 0 the set falls apart into shards. The slices at z = 0 are angular cousins of the flat sets: the same bodies in the same places, with straighter edges. Where it falls short: the slice is not the flat set, and the creases along the rims of the caps show on every surface.';
const KQ_ROUND = 'Circles on the sphere of directions stay circles inside each cap, and outside the caps. Along the rims of the caps the rule is creased.';
const KQ_CRUSH = 'Nothing but the origin is crushed. The sphere of directions is folded along the rims of the caps instead: the directions outside every cap come out as a mirror image (a quarter of all directions at n = 2).';
const KQ_SMOOTH = 'No jump was found (measured at n = 2, 3 and 4), but the rule is creased along the rim of every cap: inside a cap it is one sphere inversion with a mirror, outside the caps the mirror alone. A power that is not a whole number of 2 or more uses the caps of the nearest such power, so the picture jumps between whole powers.';
const KQ_SLICE = `The plane z = 0 lands on itself, but it does not follow complex arithmetic: the angle is multiplied with a wobble (${KQ_WOBBLE}). So the slice is a cousin of the flat set, not the flat set.`;
const KQ2_TAG = 'Tried: the same caps round two circles (a reading of the second construction in Kučera’s paper, its Figure 4). Failed: the slice at z = 0 is not the flat set, the number of buds follows the number of planes and not the power, and away from the x-axis it tears into shards.';
const KQ2_NOTE = 'A reading of the second construction in the paper: the caps of the entry above round the equator, and the same caps round the circle of the plane y = 0. A direction nearer the plane z = 0 uses the first family, one nearer the plane y = 0 the second. Measured: on the seam between them, the planes y = z and y = −z, the two families send one direction to places up to 180° apart (92° on average), so the rule jumps there. The jump does no harm only in a Julia set whose c lies on the x-axis. Everywhere else, the Mandelbrot solid included, it tears the solid. The paper gives the same limit: its construction is for c on the x-axis. The planes z = 0 and y = 0 both carry the cousin of the flat set that the entry above has in the plane z = 0.';
const KQ2_ABOUT = 'The second construction of Kučera’s paper, as far as its text lets it be rebuilt: the inversions of Kleinian squaring, one plane, used twice, once round the equator and once round the circle of the plane y = 0. What the pictures show: the Julia set for c = −1 is a chain of bodies along the x-axis with buds round two circles, above and below as well as left and right. That is the look of the entry Sphere inversions, two planes, with rougher, knobbly buds. With c on the x-axis at −1.75 the bodies thin to dust along the axis. For a c off the x-axis, and for the Mandelbrot solid, the picture is a mass of shards: the tear along the seam is copied all over the surface. Where it falls short: it is whole for c on the x-axis only, and its slices are cousins of the flat sets, not the flat sets.';
const KQ2_SMOOTH = 'Jumps across the planes y = z and y = −z, where the two families of caps meet (measured at n = 2: by up to 180°). It is creased along the rim of every cap as well.';
const KQ2_SLICE = `The planes z = 0 and y = 0 both land on themselves, but neither follows complex arithmetic: the angle is multiplied with a wobble (${KQ_WOBBLE}). So both slices are cousins of the flat set, not the flat set.`;
// R14-TEXTS-END

// ---------- the words of the entry of round 15 (measured in out/r15/entry/: see checks.txt there)
// R15-TEXTS-BEGIN
const spGrid = n => clamp(Math.floor(Math.abs(n) + 0.5), 2, SP_MAXN);   // the whole power the grid is laid out for
const spOwn = n => aprWhole(n) && Math.abs(n) >= 2 && Math.abs(n) <= SP_MAXN;   // a power the grid is made for
const SP_TAG = 'Lay the directions on a square pillowcase grid and double both of its coordinates. The slice at z = 0 is the flat set and no tear was found, but at power 2 the solid is streaked and its bodies do not come apart. Power 3 looks better: buds on buds.';
const SP_NOTE = 'Measured at power 2. The plane z = 0 follows complex arithmetic exactly: the 2D view draws the same picture as for Sphere inversions, one plane, pixel for pixel (five pictures compared). No jump was found between close directions (400,000 pairs). The rule is lopsided above and below the plane z = 0, because the belt of the grid that carries that plane does not lie half way between the two seams, it is twice as far from the lower seam as from the upper one: a direction and its mirror image are sent to places 0.7 apart on average, on a sphere of radius 1. At power 3 the belt lies half way and the rule is mirror-symmetric (to 15 digits). Beside the plane z = 0 a small circle of directions stays nearly a circle. Away from it the stretch is uneven: for half of all directions at least 1.6 times as much one way as the other, and for about one in six more than 3 times. The skin of the 3D picture was compared with a plain test of the set along 567 rays per picture: for three Julia sets every place where a ray stopped lay within 0.05 of the set (about 11 pixels of the opening picture), and about 5 in 6 within 0.0125. For the Mandelbrot solid 3 of 223 lay further away than 0.05. The same test gives 0.025 at most for Sphere inversions, one plane, and more than 0.1 at 12 of 145 places for Pillow. This is not the entry Pillow under “Tried”: that one wraps a sheet of triangles and has corners in the plane z = 0, this one a square sheet with no corner and no fold in that plane. A product of two different points is taken from Sphere inversions, one plane.';
const SP_ABOUT = 'The Mandelbulb doubles two angles on a globe grid, and a globe grid is squeezed toward its poles. This entry tries another grid: a square pillowcase, a flat sheet folded double and sewn shut, which is squeezed nowhere except at its four corners. On that sheet the rule doubles both coordinates, a plain enlargement by 2. One belt of the pillow comes back to itself with its position doubled. That belt is laid on the equator, so the plane z = 0 follows complex squaring exactly, and no seam is needed. What the pictures show at power 2: the Mandelbrot solid is one lopsided rock with fins. The Julia set for c = −1 is a row of bodies with spikes, but the bodies do not come apart: cut through the point where two flat bodies touch, the solid is 24% as large as cut through its middle, and it reaches as far above and below the plane there as 0.54 (in the middle: 0.60). Sphere inversions, one plane gives 4% there. The rabbit is a group of lumps, c = i a branching coral, and c = 0.3 one smooth block. Close up, at three depths, the skin is made of streaked sheets, blades and thin slits, like combed or stirred paint. Cuts worked point by point, without the shortcuts of the 3D picture, show the same thing: the detail goes on at smaller sizes, but as thin sheets and slivers, not as smaller bodies. Where it falls short: a pillowcase is flat and a sphere is round, so laying one on the other stretches it somewhere, and the layout used here is even only beside the plane z = 0. The streaks probably come from that, which was not tested. At the powers 3, 4 and 5 the opening pictures show a blocky body with knobbly buds on its corners and rims. At power 3 one Julia set, c = (0.3, 0.5, 0), was also looked at close up in one place, at three depths: there the skin is buds with smaller buds on them, with no streaks, and cuts worked point by point show a bumpy outline with no slits. Other sets and other places at these powers were not looked at.';
const SP_ROUND = 'On the pillow grid the rule is a plain enlargement, but the grid is laid on the sphere unevenly. Beside the plane z = 0 a small circle of directions stays nearly a circle (measured at power 2: about 5% out of round within 5° of the plane). Further away it comes out as an oval.';
const SP_CRUSH2 = 'Nothing but the origin is crushed onto one point. Beside the upper pole the stretch falls to almost nothing (measured: down to 0.001 where the plane gives 2), and beside the corner points of the grid in the lower half it is largest (measured: up to 10).';
const SP_CRUSHN = 'Nothing but the origin is crushed onto one point. Where the stretch is smallest and largest was measured at power 2 only: smallest beside the upper pole, largest beside the corner points of the grid in the lower half.';
const SP_SMOOTH = 'Not one formula: the grid is laid on the upper and the lower half of the sphere by two formulas that meet on the equator, and a cubic equation is solved at every step. No jump was found: the gap between the answers for two close directions shrinks in step with their distance (measured at the powers 2 to 5).';
const SP_SMOOTH_OTHER = ' The grid exists for the whole powers 2 to 5 only. Every other power uses the grid of the nearest of them, so the picture jumps between whole powers.';
const SP_SLICE = 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set. No corner and no fold of the grid lies in that plane.';
const spSliceOther = n => `The grid exists for the whole powers 2 to 5 only. At the power ${aprNum(n)} the directions follow the power ${spGrid(n)} and only the length follows ${aprNum(n)}. So the plane z = 0 lands on itself, but it does not follow complex arithmetic.`;
const spFormula = n => {
  const m = spGrid(n), own = spOwn(n) && n > 0, k = own ? aprSup(m) : 'ⁿ';
  return `v${k} = |v|${k} · dir(D(pil(d)))   with d = v/|v| the direction of v. pil lays d on a square pillowcase grid: s runs once round the pillow from 0 to 1, and t from the lower seam (0) to the upper seam (½). D multiplies both by ${m} with a mirror, (s, t) → (−${m}s, ${m}t), and where the result passes a seam the sheet is folded back over it. dir is pil backwards. The belt t = 1/${m + 1} comes back to itself with s multiplied by ${m}, and that belt is the equator, with s the longitude.`
    + (own ? '' : ` The grid is that of the whole power ${m}; only the length follows the power ${aprNum(n)}.` + (n < 0 ? ' A negative power ends with a mirror, y → −y and z → −z.' : ''));
};
// R15-TEXTS-END

// ---------- the words of the two entries of round 16 (measured in out/r16/entry/: see checks.txt there)
// R16-TEXTS-BEGIN
const TP_ROUGH = 'The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says. Raise Iterations to 40 or more to see the bodies come apart: at 14 they are still joined by necks and look ribbed.';
const TP_TAG_AWAY = 'Square each point by the one-plane rule about a plane that turns against the point. Two planes carry the flat set and nothing tears. For c = −1 it gives separate bodies with buds in four directions, but the skin is streaks and hair, and the Mandelbrot solid is two thin crossed leaves.';
const TP_TAG_ALONG = 'Square each point by the one-plane rule about a plane that turns with the point. Four planes carry the flat set and nothing tears. For c = −1 it gives separate bodies with buds in eight directions and smaller buds on those, with thin fins and hair between the planes close up. The Mandelbrot solid is a lumpy rock with no bulbs.';
const TP_SAME = 'No jump was found: for 200,000 pairs of close points the gap between the two answers shrinks in step with their distance, at three distances (also at the powers 3 and 4). The rule gives the same answer mirrored above and below, mirrored front and back, and turned a quarter turn about the x-axis (to 15 digits), and the length of a point is squared exactly. Points with z exactly 0 get exactly the answer of Sphere inversions, one plane. The 2D view draws the same picture as for that entry except along thin edges, where it shades by looking a little to the side of the plane: of 604,262 pixels, ';
const TP_POWERS = ' The number of planes in the formula is set to the power, a choice made so that the count round the x-axis follows the power and is not free. A product of two different points is taken from Sphere inversions, one plane.';
const TP_NOTE_AWAY = TP_ROUGH + ' With “Exact” the 3D picture of this rule would be wrong: a streaked spindle of fog where the solid is a row of bodies (checked against cuts worked point by point). Measured at power 2: the planes z = 0 and y = 0 both follow complex squaring (to 15 digits). ' + TP_SAME + '748 differ for the Mandelbrot set, 35 for the rabbit and none for c = −1. At a whole power n the plane turns n − 1 times as fast, and then n planes carry the flat set (measured for the powers 2 to 5).' + TP_POWERS;
const TP_NOTE_ALONG = TP_ROUGH + ' Measured at power 2: four planes through the x-axis follow complex squaring (to 15 digits): z = 0, y = 0, y = z and y = −z. ' + TP_SAME + '68 differ for the Mandelbrot set and none for the rabbit or for c = −1. With “Exact” the 3D picture would show a thin flat sheet in the planes y = z and y = −z beside the points where two bodies touch. That sheet is not part of the solid (points on it were tested one by one). At a whole power n, 2n planes carry the flat set (measured for the powers 2 to 5).' + TP_POWERS;
const TP_ABOUT_HEAD = 'Sphere inversions, one plane has its fine detail round one plane only, and the entry with two planes tears where its two halves meet. Here every point is squared by the one-plane rule about a reference plane of its own: a flat plane through the x-axis that turns smoothly as the point goes round that axis. Beside the plane z = 0 the reference plane is z = 0, and beside the plane y = 0 it is y = 0. ';
const TP_ABOUT_AWAY = TP_ABOUT_HEAD + 'In between it turns against the point, so that half way between the two planes the point stands straight above its reference plane. What the pictures show for c = −1, with the Rough estimate: a row of separate bodies along the x-axis, each with a bud above, below, in front and behind, as in Sphere inversions, two planes. Cut across at the point where two bodies touch, with 40 steps, nothing but that point is left. A bud carries smaller buds to its sides as well as along the row (cuts worked point by point). Where it falls short: the skin is not bodies on bodies. Close up, at three depths, it is combed streaks and hair with small round bumps in between. Cuts worked point by point show thin whiskers standing off the bodies beside the planes y = z and y = −z, which thin to specks when more steps are taken. Those are the places where the point stands above its reference plane, and there the one-plane rule squeezes directions together, which is probably the cause (not tested). Away from c on the x-axis it is worse. The rabbit breaks into curved shards. A c off the plane z = 0 gives a ragged, streaked lump. The Mandelbrot solid is two thin leaves crossed along the x-axis, one in the plane z = 0 and one in the plane y = 0, with feathery shards round them and no round bulbs off those planes. Whole powers: for c on the x-axis the count round the axis follows the power, six sides at power 3 and eight buds at power 4. The Mandelbrot solid of power 3 is three thin leaves crossed.';
const TP_ABOUT_ALONG = TP_ABOUT_HEAD + 'In between it turns with the point: first it lags behind, then it catches up, so that half way between the two planes the point lies in its reference plane again. So four planes carry the flat set, 45° apart. What the pictures show for c = −1: a row of separate bodies along the x-axis, each with eight buds round it, two in each of the four planes. Cut across at the point where two bodies touch, with 40 steps, nothing but that point is left. Close up, at three depths, the bodies are ribbed like a turned chair leg, and a bud carries rings of smaller buds all round it, not only in the flat plane. Cuts worked point by point show the same smaller buds. Where it falls short: between the four planes the skin is smooth only from a distance. Cuts worked point by point at 80 steps show thin fins and tufts of hair standing on it there, and the buds have spiky crowns. The rule also folds space over along some lines, which the flat set never does. The rabbit is one swollen lump in layers, with no separate bodies. A c off the plane z = 0 gives a chain of ragged lumps. The Mandelbrot solid is one lumpy rock in layers, with horns on eight corners and the spike of the flat set, and no round bulbs on it. Its cuts at z = 0, at y = 0 and along the planes y = z and y = −z are the flat Mandelbrot set. Whole powers: the count round the x-axis follows the power, twelve horns on the Mandelbrot solid of power 3 and sixteen small buds at power 4 for c = −1, where they sit on one rim of a body shaped like a lens.';
const TP_ROUND = 'Inside each plane that carries the flat set the rule is the complex power, which keeps shapes. Between those planes, and across them, shapes are squashed.';
const TP_CRUSH_AWAY = 'Half way between the planes that carry the flat set a point stands on the pole line of its reference plane, and beside that line the one-plane rule squeezes directions together without limit (worked out from the formula, not measured).';
const TP_CRUSH_ALONG = 'Nothing but the origin is crushed onto a point, but the rule folds space over. Measured at power 2: in the planes y = z and y = −z the stretch sideways is 4x − 2|v|, where the plane itself stretches by 2|v|. It falls to nothing on the lines 60° from the x-axis and reaches three times the stretch of the plane beside the negative x-axis.';
const TP_ONE = 'At this power the reference plane does not turn, and the rule is Sphere inversions, one plane itself: it crushes the z-axis only.';
const TP_SMOOTH = 'One formula with no seam. No jump was found at the powers 2, 3 and 4. The stretch is largest beside the negative x-axis (measured at power 2: gaps up to 14 times the distance for the rule that turns away, 9 times for the one that turns along). It uses an angle and a sine, so it is not a polynomial.';
const TP_SMOOTH_OTHER = ' A power that is not a whole number takes the planes of the nearest whole number, so the picture jumps between whole powers.';
const tpCount = (n, along) => tpPlanes(n) * (along ? 2 : 1);
const tpSlice = (ok, n, along) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
  : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' + (aprWhole(n) && n >= 2 ? ` So do ${tpCount(n, along)} planes through the x-axis in all, ${aprDeg(180 / tpCount(n, along))} apart` + (tpPlanes(n) === 2 ? (along ? ': z = 0, y = 0, y = z and y = −z.' : ': z = 0 and y = 0.') : '.') : ''));
const tpFormula = (n, along) => {
  const m = tpPlanes(n), k = aprWhole(n) && n >= 2 ? aprSup(n) : 'ⁿ', wave = `φ − sin ${2 * m}φ / ${2 * m}`;
  const psi = along ? wave : m === 1 ? '0' : m === 2 ? `−(${wave})` : `−${m - 1}·(${wave})`;
  if (m === 1 && !along) return `At this power m = 1, the whole number nearest to the power, so the reference plane does not turn (ψ = 0) and the rule is the power ${aprNum(n)} of Sphere inversions, one plane itself.`;
  return `v${k} = Rot(ψ)·P(Rot(−ψ)·v)   with P the power ${aprNum(n)} of Sphere inversions, one plane, Rot(a) the turn about the x-axis by the angle a, φ the angle of v round the x-axis (0 on the side y > 0 of the plane z = 0), and ψ = ${psi}. ψ is how far the reference plane of v is turned out of the plane z = 0. It stands still where φ is a multiple of ${aprDeg(180 / m)}. The ${2 * m} in it is twice m = ${m}, the whole number nearest to the power, so it follows the power and is not a free choice`
    + (along ? '.' : `, and neither is the factor ${m === 1 ? '0' : '−' + (m - 1)} in front, which is 1 − m.`)
    + (aprWhole(n) ? '' : ` P itself is taken at the power ${aprNum(n)}; only the planes follow the whole number ${m}.`);
};
// R16-TEXTS-END

// ---------- the words of the entry of round 20 (measured in out/r20/entry/: see checks.txt there)
// R20-TEXTS-BEGIN
const WS_ROUGH = 'The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says. The other two settings draw a spindle of fog round the solid: measured on seven views of the Julia sets for c = −1, the rabbit and the Siegel disc, between 21% and 99% of the places where a ray stopped had no point of the set within 8 pixels with “Exact”, between 75% and 99% with “One neighbour”, and at most 1% with “Rough”. Rough has a fault of its own: a ray can step over a sheet that is thinner than its step, so thin parts are left out of the 3D picture. For the rabbit 58 of 254 rays that meet the set stopped at nothing. With “Ray step, share of the distance estimate” lowered to 0.4 it was 15 of 254. The pictures described here were made with Iterations at 40: at 14 the bodies are still joined by short necks.';
const WS_TAG = 'Wind each point round the x-axis three times (at power 2), then square it by the one-plane rule, and turn nothing back. Three planes then carry the flat set for every c of the flat plane, and nothing tears. For c = −1 it gives separate bodies with buds in six directions, but their skin is ragged between the planes. Off the x-axis it falls short: the rabbit’s ears are thin plates and the Siegel disc is three sheets. Its Mandelbrot solid has not been judged yet.';
const WS_NOTE = WS_ROUGH + ' Measured: a point with z exactly 0 gets exactly the answer of Sphere inversions, one plane, and the cut at z = 0 is the flat set (six Julia sets at the powers 2 to 5, 160,000 points each, tested against plain complex arithmetic: none differs). The 2D view draws the flat set, and the same picture as for Sphere inversions, one plane except along thin edges of the outline: of 604,262 pixels, 586 differ for c = −1 (all of them faintly), 4,015 for the rabbit (189 of them clearly) and 5,415 for the Siegel disc (667 clearly). At power 2 the six half-planes through the x-axis at 0°, 60°, 120°, 180°, 240° and 300° are sent into the plane z = 0 in one step (to 15 digits), and from there on a point follows complex squaring. So three planes through the x-axis, 60° apart, each show the flat set, turned about the x-axis, whether c lies on the x-axis or not: for the rabbit the cut by the plane at 120° is the flat rabbit point for point, and the cut at 60° is the flat rabbit turned over (129,600 points each, none differs). No jump was found: for 200,000 pairs of close points the gap between the two answers shrinks in step with their distance, at four distances from 0.001 down to 0.000001, at the powers 2 to 5. The rule gives the same answer mirrored above and below and mirrored front and back, the same answer for a point turned by 120° about the x-axis (to 15 digits), and the length of a point is squared exactly. So every Julia set of this rule looks the same after a third of a turn about the x-axis. A whole power n is wound n times when n is odd and n + 1 times when n is even: the powers 2 and 3 have six half-planes that land in the plane z = 0, the powers 4 and 5 have ten (measured). A product of two different points is taken from Sphere inversions, one plane.';
const WS_ABOUT = 'In Sphere inversions, two planes and in the two Turning plane entries, each plane that carries the flat set is squared inside itself. Here only the plane z = 0 is squared. Before the squaring every point is carried round the x-axis: its angle round that axis is multiplied by three, unevenly, at the angle’s own pace beside six half-planes 60° apart and five times as fast half way between them. The six half-planes land in the plane z = 0, and a point of them is from then on a point of the flat plane, where c lives. So they show the flat picture without the rule having to keep them, and that works for every c of the flat plane. What the pictures show for c = −1: a row of separate bodies along the x-axis, each with six buds round it, one in each of the six half-planes, and smaller buds on those. Cut across at the point where two bodies touch, nothing but that point is left (40 steps, a cut 0.2 wide). The bud at 60° is a body and not a plate: cut along the x-axis it is an oval 0.13 long and 0.12 across. Cut across the x-axis through the middle of the middle body, at x = 0, the outline between two buds is smooth down to a picture 0.12 wide (80 steps), but that place is special. Where it falls short for c = −1: a little to the side, at x = 0.2, the same stretch of outline is ragged, with thin needles standing off it (80 steps, a picture 0.3 wide). At x = −0.3 a dozen short thin spikes and loose specks stand round the body, and the bud at 60° has a fringe of about 200 loose specks. The 3D picture shows this as a streaked, grainy skin, bristly like a sea urchin when seen along the x-axis, where Sphere inversions, one plane is smooth. The sets for c = −0.75 and c = 0.25 are ribbed from end to end: cut across the x-axis, c = 0.25 has twelve lobes like a pumpkin and c = −0.75 six sharp ridges, with a hairy rim at x = −0.3. Where it falls short away from the x-axis: the bodies are thin there. Turn the flat rabbit 4° about the x-axis and only 52% of its points are still in the set, and at 15° only 19% (the same with 40 and with 80 steps). For c = −1 it is 91% at 4° and 91% at 30°. So the rabbit’s middle body is a body with six points, but its ears are plates lying in the three planes, with shredded rims, and the 3D picture shows a feathery mass and no separate bodies. The Siegel disc is thinner still and thins with every step: a quarter of a degree off its planes 79% of its points are in the set after 40 steps and 64% after 80. It is three sheets crossing on the x-axis, not a body. For c = i, a tree in the plane, the cuts show three flat trees and the 3D picture a thin dust. Whole powers: cut across the x-axis the outline repeats six times round the axis at the powers 2 and 3 and ten times at the powers 4 and 5 (for c = −1 at power 4: ten buds), so the count follows the power two powers at a time. The Mandelbrot solid of this rule has not been judged yet.';
const wsRound = n => (wsCount(n) === 1 ? APR_CIRCLES
  : `Inside the ${wsCount(n)} planes that carry the flat set the rule is the complex power, which keeps shapes, and the ${2 * wsCount(n)} directions that are sent to the negative x-axis, one in each of the ${2 * wsCount(n)} half-planes, are stretched exactly as the flat plane stretches (measured at the powers 2 to 5). Beside those planes a small ball stays nearly a ball, and half way between them it is squeezed flat. Measured at power 2: 7% out of round within 5° of the planes, and about five to one within 5° of half way. The squeeze grows with the power: about 12 to one at power 3 and 19 to one at power 4.`);
const wsAngles = k => Array.from({ length: Math.min(k, 3) }, (_, j) => aprDeg((j + 0.5) * 180 / k)).join(', ');
const wsCrush = n => (wsCount(n) === 1 ? 'At this power the winding changes nothing, and the rule is Sphere inversions, one plane itself: it crushes the z-axis only.'
  : `Crushes ${2 * wsCount(n)} directions: those at right angles to the x-axis, half way between the half-planes that land in the plane z = 0 (at ${wsAngles(wsCount(n))} and so on round the x-axis). The winding sends them onto the z-axis, which the one-plane rule crushes: two of the three stretches fall to under 2% of what the plane gives (measured at the powers 2 to 5). Nothing is folded over: of 400,000 directions none came out as a mirror image (measured at the powers 2, 3 and 4).`);
const WS_SMOOTH_OTHER = ' A power that is not a whole number takes the winding of the nearest whole number, so the picture jumps between whole powers. It also tears space, the way zⁿ tears the plane along the negative x-axis: here along the half-planes half way between those that land in the plane z = 0, on the side x < 0 (measured at the power 2.5).';
const wsSmooth = n => (wsCount(n) === 1 ? 'At this power the rule is Sphere inversions, one plane itself.' + (aprWhole(n) ? '' : APR_HALF)
  : `One formula with no seam. No jump was found at the powers 2 to 5. The stretch is largest beside the x-axis, half way between the half-planes that land in the plane z = 0: ${2 * wsCount(n) - 1} times that of the plane (measured at the powers 2 to 5). It uses the sine of an angle, so it is not a polynomial.` + (aprWhole(n) ? '' : WS_SMOOTH_OTHER));
const wsSlice = (ok, n) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
  : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' + (aprWhole(n) && n >= 2 ? ` The ${2 * wsCount(n)} half-planes through the x-axis at every ${aprDeg(180 / wsCount(n))} are sent into the plane z = 0 at the first step, so ${wsCount(n)} planes in all show the flat set, each turned about the x-axis.` : ''));
const wsFormula = n => {
  const k = wsCount(n), m = Math.max(1, Math.floor(Math.abs(n) + 0.5)), own = aprWhole(n) && n >= 2, sup = own ? aprSup(n) : 'ⁿ';
  if (k === 1) return `At this power the turn round the x-axis is wound once, which changes nothing, and the rule is the power ${aprNum(n)} of Sphere inversions, one plane itself.`;
  return `v${sup} = P(W(v))   with P the power ${aprNum(n)} of Sphere inversions, one plane, and W the winding: W keeps x and the distance of v from the x-axis, and changes only φ, the angle of v round the x-axis (0 on the side y > 0 of the plane z = 0), to g(φ) = ${k}φ − ${k - 1}·sin ${2 * k}φ / ${2 * k}. Nothing is turned back afterwards. g runs at the pace of φ itself wherever φ is a multiple of ${aprDeg(180 / k)}, and ${2 * k - 1} times as fast half way between. `
    + (own ? `The ${k} in it is ${m % 2 ? 'the power itself' : 'the power plus one, because the power is even'}` : `The ${k} in it comes from ${m}, the whole number nearest to the size of the power: ${m % 2 ? 'that number itself' : 'one more, because that number is even'}`)
    + '. An even count would send the half y < 0 of the plane z = 0 onto the half y > 0, and the slice at z = 0 would no longer be the flat set. So the count follows the power and is not a free choice.'
    + (aprWhole(n) ? '' : ` P itself is taken at the power ${aprNum(n)}; only the winding follows the whole number.`);
};
// R20-TEXTS-END

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
  // ----- Round 14: five rules tried at the user's request. They stand at the end of this list so that the entries
  // before them keep their places; the Approach list shows each under the heading of its group. What their texts
  // say was measured in out/r14/rules/ (checks.txt, and the contact sheets there).
  {
    id: 'quat4', name: 'Quaternions, 4D (slices)', group: 'quaternion', glsl: GL_QUAT4, axis: () => [1, 0, 0],
    tag: 'The quaternion sets live in four dimensions. The picture is a flat 3D slice through one of them, and the dials move the slice.',
    params: [
      { type: 'dial', key: 'w', label: 'Slice position on the fourth axis', min: -1.5, max: 1.5, step: 0.01, def: 0, lo: -4, hi: 4, animate: 'bounce', help: Q4_HELP_W },
      { type: 'dial', key: 'tilt', label: 'Slice tilt toward the fourth axis, degrees', min: -90, max: 90, step: 1, def: 0, lo: -360, hi: 360, animate: 'bounce', help: Q4_HELP_TILT },
      { type: 'dial', key: 'cw', label: 'The point c on the fourth axis (Julia sets)', min: -1.5, max: 1.5, step: 0.01, def: 0, lo: -4, hi: 4, animate: 'bounce', help: Q4_HELP_CW },
      { type: 'note', text: Q4_NOTE },
    ],
    formula: (p, n) => (aprIs(n, 2) ? 'q² = (a² − b² − c² − d², 2ab, 2ac, 2ad)   for a quaternion q = (a, b, c, d)'
      : 'qⁿ = |q|ⁿ · (cos nα, sin nα · u)   with α the angle of the quaternion q from the real axis and u the direction of its three imaginary parts')
      + `. The picture point (x, y, z) stands for q = ${q4Words(p)}.`,
    about: Q4_ABOUT,
    roundNote: (p, n) => (aprIs(n, -1) ? APR_INVERSION : 'The squash is in the spin direction.'),
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'In the three numbers the orbit is held in, it crushes every direction whose angle from the real axis, times n, is a multiple of 180°. In 4D the same directions are crushed.' + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only.' + aprTear(n, APR_LINE)];
      return n < 0 ? ['part', 'A polynomial divided by a power of |q|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial: plain quaternion multiplying.'];
    },
    slice: (ok, p) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : !p.w && !p.tilt && !p.cw ? 'With the three dials at 0 this is Quaternion square (Lathe): the plane z = 0 follows complex arithmetic exactly, and so does every other plane through the x-axis.'
      : Q4_SLICE_OFF),
  },
  {
    id: 'rotor', name: 'Rotor square (geometric algebra)', group: 'quaternion', glsl: GL_ROTOR, axis: p => rtAxis(p).a,
    tag: 'Find the turn that carries a reference axis onto the point, and do that turn twice. It comes out as the quaternion square about that axis.',
    params: [
      { type: 'dial', key: 'lon', label: 'Reference axis, longitude, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: RT_HELP_LON },
      { type: 'dial', key: 'lat', label: 'Reference axis, latitude, degrees', min: -90, max: 90, step: 1, def: 90, animate: 'bounce', help: RT_HELP_LAT },
      { type: 'note', text: RT_NOTE },
    ],
    formula: (p, n) => {
      const a = rtAxis(p).a.map(x => aprNum(x)).join(', ');
      return (aprIs(n, 2) ? 'v² = (p² − |s|²)·a + 2p·s   with p = a·v the part of v along the reference axis a and s = v − p·a the rest of v'
        : 'vⁿ = |v|ⁿ · (cos nα · a + sin nα · u)   with α the angle between the reference axis a and v, and u the direction of v’s part square to a') + `. Here a = (${a}).`;
    },
    about: RT_ABOUT,
    roundNote: (p, n) => (aprIs(n, -1) ? 'At n = −1 the rule is a single sphere inversion with a mirror, and inversions keep every shape.' : 'The squash is in the spin direction around the reference axis.'),
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the reference axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane through the origin at right angles to the reference axis.` : '') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only. A power that is not a whole number also tears space along the reference axis, on its negative side, the way zⁿ tears the plane along the negative x-axis.'];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.'];
    },
    slice: (ok, p, n = S.n) => {
      const lat = p.lat === undefined ? 90 : p.lat, lon = aprWrap(p.lon || 0);
      if (Math.abs(r14CS(lat)[1]) > 0) return RT_SLICE_OFF + (aprIs(Math.abs(lat), 90) ? ' With the reference along the z-axis that is every plane through the z-axis, the plane y = 0 among them.' : '');
      if (ok) return lon ? 'At this power the plane z = 0 follows complex arithmetic exactly.' : 'With the reference along the x-axis this is Quaternion square (Lathe): the plane z = 0 follows complex arithmetic exactly, and so does every other plane through the x-axis.';
      const turn = aprWrap((1 - n) * lon);
      return aprWhole(n) && turn ? aprTurned('The plane z = 0 follows', turn, n) : 'The plane z = 0 does not follow complex arithmetic.';
    },
  },
  {
    id: 'rotorframe', name: 'Rotor square with a frame', group: 'quaternion', glsl: GL_ROTORFRAME, axis: () => [0, 0, 1],
    tag: RF_TAG,
    params: [{ type: 'note', text: RF_NOTE }],
    formula: (p, n) => (aprIs(n, 2) ? 'v² = |v| · R(v)   with R the turn that carries the x-axis onto the direction of v: a tip up by the latitude of v, then a turn about the z-axis by its longitude. Written out, v² = (x² − (z²x + |v|y²)/ρ, y·(x(ρ + |v|) − z²)/ρ, z(ρ + x)) with ρ = √(x² + y²).'
      : 'vⁿ = |v|ⁿ · Rⁿ(1, 0, 0)   with R the turn that carries the x-axis onto the direction of v (a tip up by the latitude, then a turn about the z-axis by the longitude), and Rⁿ the turn about the same line by n times the angle.'),
    about: RF_ABOUT,
    roundNote: () => RF_ROUND,
    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      if (Math.abs(n) < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return aprIs(Math.abs(n), 2) ? ['no', RF_CRUSH2 + aprPole(n)] : ['part', RF_CRUSHN + aprPole(n)];
    },
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : ['no', RF_SMOOTH + aprTear(n, APR_HALF)]),
    slice: ok => (ok ? RF_SLICE : 'The plane z = 0 does not follow complex arithmetic.'),
  },
  {
    id: 'kleinsq', name: 'Kleinian squaring, one plane', group: 'tried', glsl: GL_KLEINSQ, axis: () => [0, 0, 1],
    tag: KQ_TAG,
    params: [{ type: 'note', text: KQ_NOTE }],
    formula: (p, n) => kqFormula(n, false),
    about: KQ_ABOUT,
    roundNote: () => KQ_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', KQ_CRUSH + aprPole(n)]),
    smooth: () => ['no', KQ_SMOOTH],
    slice: () => KQ_SLICE,
  },
  {
    id: 'kleinsq2', name: 'Kleinian squaring, two planes', group: 'tried', glsl: GL_KLEINSQ2, axis: () => [1, 0, 0],
    tag: KQ2_TAG,
    params: [{ type: 'note', text: KQ2_NOTE }],
    formula: (p, n) => kqFormula(n, true),
    about: KQ2_ABOUT,
    roundNote: () => KQ_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', KQ_CRUSH + aprPole(n)]),
    smooth: () => ['no', KQ2_SMOOTH],
    slice: () => KQ2_SLICE,
  },
  // ----- Round 15: one new rule, in a group of its own. It stands at the end of this list so that the entries
  // before it keep their places. What its texts say was measured in out/r15/entry/.
  {
    id: 'sqpillow', name: 'Square pillow', group: 'pillow', glsl: GL_SQPILLOW, axis: () => [0, 0, 1],
    tag: SP_TAG,
    params: [{ type: 'note', text: SP_NOTE }],
    formula: (p, n) => spFormula(n),
    about: SP_ABOUT,
    roundNote: () => SP_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', (aprIs(Math.abs(n), 2) ? SP_CRUSH2 : SP_CRUSHN) + aprPole(n)]),
    smooth: (p, n = S.n) => ['no', SP_SMOOTH + (spOwn(n) ? '' : SP_SMOOTH_OTHER)],
    slice: (ok, p, n = S.n) => (spOwn(n) && ok ? SP_SLICE : spSliceOther(n)),
  },
  // ----- Round 16: two rules built from Sphere inversions, one plane, so they stand in its group. They are at the
  // end of this list so that the entries before them keep their places. What their texts say was measured in
  // out/r16/entry/.
  {
    id: 'turnaway', name: 'Turning plane, away', group: 'inversions', glsl: GL_TURNAWAY, axis: () => [1, 0, 0], deMax: 0,
    tag: TP_TAG_AWAY,
    params: [{ type: 'note', text: TP_NOTE_AWAY }],
    formula: (p, n) => tpFormula(n, false),
    about: TP_ABOUT_AWAY,
    roundNote: () => TP_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : ['part', (tpPlanes(n) === 1 ? TP_ONE : TP_CRUSH_AWAY) + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', TP_SMOOTH + (aprWhole(n) ? '' : TP_SMOOTH_OTHER) + aprTear(n, APR_HALF)]),
    slice: (ok, p, n = S.n) => tpSlice(ok, n, false),
  },
  {
    id: 'turnalong', name: 'Turning plane, along', group: 'inversions', glsl: GL_TURNALONG, axis: () => [1, 0, 0], deMax: 0,
    tag: TP_TAG_ALONG,
    params: [{ type: 'note', text: TP_NOTE_ALONG }],
    formula: (p, n) => tpFormula(n, true),
    about: TP_ABOUT_ALONG,
    roundNote: () => TP_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : ['part', TP_CRUSH_ALONG + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', TP_SMOOTH + (aprWhole(n) ? '' : TP_SMOOTH_OTHER) + aprTear(n, APR_HALF)]),
    slice: (ok, p, n = S.n) => tpSlice(ok, n, true),
  },
  // ----- Round 20: one rule built from Sphere inversions, one plane, so it stands in its group, at the end of this
  // list so that the entries before it keep their places. What its texts say was measured in out/r20/entry/.
  {
    id: 'windsq', name: 'Wind, then square', group: 'inversions', glsl: GL_WINDSQ, axis: () => [1, 0, 0], deMax: 0,
    tag: WS_TAG,
    params: [{ type: 'note', text: WS_NOTE }],
    formula: (p, n) => wsFormula(n),
    about: WS_ABOUT,
    roundNote: (p, n = S.n) => wsRound(n),
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : ['part', wsCrush(n) + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', wsSmooth(n)]),
    slice: (ok, p, n = S.n) => wsSlice(ok, n),
  },
];
