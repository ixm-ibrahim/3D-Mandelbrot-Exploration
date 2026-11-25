// Approaches: the 3D squaring rules. Each defines a product mul(a, b) and a power pw(a, n) on points of space:
// its shader text (GL_...), its JavaScript twin (MATH), what its orbit carries (CARRY) and its entry in APPROACHES.

// Powers may be negative or fractional. Every result is kept finite: a pole (the origin under a negative power)
// and a runaway orbit both stop at a length of about 1.7e18, which the renderer's 32-bit numbers can still square.
// e^42 sits just above 64^10: the escape radius raised to the largest power on the dial.
const APR_LOGCAP = 42;
const aprPow = (r, n) => Math.exp(Math.min(n * Math.log(Math.max(r, 1e-30)), APR_LOGCAP));
const aprRad = deg => (deg || 0) * PI / 180;

// Folds the angle around the x-axis so that the nearest of k planes through that axis lands on the xy-plane.
// The halves y > 0 and y < 0 stay apart, which the flat dynamics needs.
function foldk(v, k) {
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
// Sphere inversions, soft mirror. The turn a of a point round the x-axis, counted from the flat plane (0° in the
// plane z = 0, 90° in the plane y = 0), is folded by a mirror at `mirror` degrees, its corner rounded over `soft` degrees:
//   g(a) = mirror − |a − mirror|                              where |a − mirror| >= soft
//   g(a) = mirror − ((a − mirror)² / (2·soft) + soft / 2)     nearer the mirror (same value and slope where they meet)
// mirror = 90, soft = 0 is the one-plane rule; mirror = 45, soft = 0 is two planes. The signs of y and z are kept,
// as in foldk, so the rule jumps across the plane y = 0.
const smDial = (q, key, def, lo, hi) => clamp(q && q[key] !== undefined && isFinite(+q[key]) ? +q[key] : def, lo, hi);
function smTurn(a, q) {
  const b = aprRad(smDial(q, 'mirror', 45, 45, 90)), w = aprRad(smDial(q, 'soft', 0, 0, 45)), t = a - b;
  if (!(w > 0) || Math.abs(t) >= w) return b - Math.abs(t);
  return b - (t * t / (2 * w) + 0.5 * w);
}
function smFold(v, q) {
  const [x, y, z] = v, rho = Math.hypot(y, z);
  if (z === 0 || !(rho > 1e-300)) return v;          // a point of the flat plane stays exactly where it is
  const g = smTurn(Math.atan2(Math.abs(z), Math.abs(y)), q);
  return [x, (y < 0 ? -1 : 1) * rho * Math.cos(g), (z < 0 ? -1 : 1) * rho * Math.sin(g)];
}
// Soft mirrors, doubling. The soft mirror of smFold with twice as many mirrors at each step of an orbit: at step k
// they stand every 90°/2^(k−1) round the x-axis, the first at half that from the flat plane, so 2, 4, 8, ... planes
// through the x-axis are sent onto the flat plane. The soft edge keeps the same share of the gap between mirrors.
//   b = 45°/2^(k−1),  t = how far the turn a is from the nearest mirror (−b .. b),  g = b − |t|, the corner rounded
// as in smTurn. k = 1 is smFold with the mirror at 45°.
function smFoldK(v, k, soft) {
  const [x, y, z] = v, rho = Math.hypot(y, z);
  if (z === 0 || !(rho > 1e-300)) return v;          // a point of the flat plane stays exactly where it is
  const h = Math.pow(2, 1 - k), b = 0.25 * PI * h, w = aprRad(soft) * h;
  const a = Math.atan2(Math.abs(z), Math.abs(y)), t = a - 2 * b * Math.floor(a / (2 * b)) - b;
  const g = !(w > 0) || Math.abs(t) >= w ? b - Math.abs(t) : b - (t * t / (2 * w) + 0.5 * w);
  return [x, (y < 0 ? -1 : 1) * rho * Math.cos(g), (z < 0 ? -1 : 1) * rho * Math.sin(g)];
}
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
// For |k| > 1 the turn pushes away from those planes, so a rounding leak would grow.
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
// weights (lA, lB, lC) to a unit direction with z >= 0
function pbLayout(l) {
  const mn = Math.min(l[0], l[1], l[2]), e = 3 * mn, s = 1 - e;        // s: 0 at the centre, 1 on the boundary
  const k = l[2] <= l[0] && l[2] <= l[1] ? 0 : l[0] <= l[1] ? 1 : 2;   // the edge the ray from the centre meets
  const t = s > 1e-12 ? clamp((l[(k + 1) % 3] - mn) / s, 0, 1) : 0.5;  // where on that edge
  const z = Math.sin(0.5 * PI * e), rho = Math.cos(0.5 * PI * e), tau = PB_T3 * (k + t);
  return pbSlide(rho * Math.cos(tau), rho * Math.sin(tau), z);
}
// the same backwards: a unit direction with z >= 0 to weights
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
// cos and sin of an angle in degrees, with a value that should be exactly 0 made exactly 0, as in the shader
const aprCosSin = deg => [Math.cos(aprRad(deg)), Math.sin(aprRad(deg))].map(c => (Math.abs(c) < 1e-6 ? 0 : c));
// Rotor square: the reference axis, and a direction square to it for a point that lies on the axis itself
function rtAxis(q) {
  const lo = aprCosSin(q.lon), la = aprCosSin(q.lat === undefined ? 90 : q.lat);
  return { a: [la[0] * lo[0], la[0] * lo[1], la[1]], side: [-lo[1], lo[0], 0] };
}
// Quaternions, 4D: where the picture point P sits in 4D (real, i, j, k), for a slice at w tilted by `tilt` degrees
function q4Embed(P, q = {}) {
  const [c, s] = aprCosSin(q.tilt), w = q.w || 0;
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
// Square pillow. Directions are laid on a square pillowcase: s runs round the pillow (one full turn is 1), t from
// the south seam (0) to the north seam (1/2), and each seam is zipped shut. For the whole power m the belt
// t0 = 1/(m + 1) is the equator, with s the longitude. Each half sphere is laid out the same way: p = (x, y)/(1 + |z|) =
// ((1 + B²)/2 · cos 2πs, B · sin 2πs), B = 1 on the equator and B = 0 on the seam. North of the belt
// B = sinh(bn·(1/2 − t))/sinh(bn·wn), south of it B = sinh(bs·t)/sinh(bs·ws), with wn = 1/2 − t0 and ws = t0 the widths
// of the two strips and b·coth(b·width) = 2π, so that a step along t and a step along s are the same length on the belt.
// The power multiplies s and t by m (with a mirror, s -> −s) and folds the result back onto the pillow.
const SP_MAXN = 5;     // the layout exists for the whole powers 2 to SP_MAXN: b·coth(b·ws) = 2π has no answer above 5
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
// pass it. The start, the root of the same equation without its beta³, is never below the true root, and 5 steps
// reach the last digit.
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
// Turning plane. The one-plane power P is taken about a reference plane through the x-axis that turns with the point:
//   F(v) = Rot(psi) P(Rot(−psi) v),   psi = q·(phi − sin(2m·phi)/(2m)),   phi = atan2(z, y),
// with Rot(a) the turn about the x-axis by the angle a, m the whole number nearest to |n| (at least 1), and
// q = 1 − m ("away": the plane turns against the point) or q = 1 ("along": it turns with the point).
// psi stands still where phi is a multiple of 180°/m.
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
// Wind, then square. The turn a of a point round the x-axis (0 on the side y > 0 of the plane z = 0) is wound,
// a -> g(a) = k·a − (k − 1)·sin(2k·a)/(2k), and then the one-plane power P is taken, with nothing turned back:
//   F(v) = P(x, ρ·cos g, ρ·sin g),   ρ the distance of v from the x-axis.
// k is odd: m, the whole number nearest to |n| (at least 1), or m + 1 when m is even, because an even count would
// send the half y < 0 of the plane z = 0 onto the half y > 0. g has slope 1 wherever g(a) is a multiple of 180°:
// those 2k half-planes are sent into the plane z = 0 with no squeeze. cos and sin of k·a come from multiplying
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
// Four to one, two planes alike: the square only. Any other power is the one-plane power.
// The direction of a point is written as the number w = tan(α/2)·e, with α its angle from the positive x-axis and
// e = (y + iz)/ρ its place round that axis. The square has the direction
//   w -> 2w / (1 − w⁴),
// which four directions share, and which treats the plane y = 0 exactly as it treats the plane z = 0. Two changes
// come first. α is replaced by β with tan β + sin β = 2·tan α, so that in both planes the angle from the x-axis is
// doubled and both carry the complex square. And e is rotated by −q·sin 4ψ (ψ the angle of e), q = (1 − 1/K)/4,
// with K how much more the change from α to β stretches across a plane than along it: a small shape beside either
// plane then keeps its shape.
// t = tan(β/2) is the root between 0 and 1 of s·t⁴ + 2c·t − s, with s and c the sine and cosine of α. Behind the
// plane x = 0 the root is larger than 1 and its reciprocal is found, the root of s·t⁴ + 2|c|·t³ − s. Newton's steps
// start above the root and come down onto it.
const F4_STEPS = 5;
function f4Planes(v, n) {
  if (n !== 2) return tpOne(v, n);
  const [x, y, z] = v;
  if (z === 0) { const w = tpOne([x, y, 0], 2); return [w[0], w[1], 0]; }
  if (y === 0) { const w = tpOne([x, z, 0], 2); return [w[0], 0, w[1]]; }
  const rho = Math.hypot(y, z), r2 = x * x + rho * rho;
  if (r2 < 1e-30) return [0, 0, 0];
  const r = Math.sqrt(r2), s = rho / r, c = Math.abs(x) / r, back = x < 0, h = s / Math.max(2 * c, 1e-30);
  let t = Math.min(1, back ? Math.pow(h, 1 / 3) : h);
  for (let i = 0; i < F4_STEPS; i++) {
    const t2 = t * t, d = 4 * s * t2 * t + (back ? 6 * c * t2 : 2 * c);
    if (d > 1e-20) t -= (s * t2 * t2 + 2 * c * (back ? t2 * t : t) - s) / d;
  }
  const l = Math.hypot(t, 1), sg = (back ? 1 : t) / l, cg = (back ? t : 1) / l;   // the sine and cosine of β/2
  const cb = cg * cg - sg * sg, sb = 2 * sg * cg, K = 2 * (1 - cb + cb * cb) / Math.sqrt(sb * sb * (1 + cb) * (1 + cb) + 4 * cb * cb);
  const ey = y / rho, ez = z / rho, a = (1 - 1 / K) * (ey * ey - ez * ez) * ey * ez, ca = Math.cos(a), sa = Math.sin(a);
  const fy = ey * ca + ez * sa, fz = ez * ca - ey * sa, f2r = fy * fy - fz * fz, f2i = 2 * fy * fz;
  // w = N/D, both multiplied through by cos⁴(β/2), so that neither end of the x-axis needs a case of its own
  const k = 2 * sg * cg * cg * cg, s4 = sg * sg * sg * sg, Nr = k * fy, Ni = k * fz;
  const Dr = cg * cg * cg * cg - s4 * (f2r * f2r - f2i * f2i), Di = -2 * s4 * f2r * f2i;
  const n2 = Nr * Nr + Ni * Ni, d2 = Dr * Dr + Di * Di, m = r2 / (n2 + d2);
  return [m * (d2 - n2), 2 * m * (Nr * Dr + Ni * Di), 2 * m * (Ni * Dr - Nr * Di)];
}
// Four to one, caps flipped over: the square only. Any other power is the one-plane power.
// The direction (X, Y, Z) of a point is written as the number ζ = (X + iY)/(1 − Z): the circle z = 0 is |ζ| = 1,
// straight down is 0 and straight up is infinity. The square has the direction
//   ζ -> (ζ³ − a) / (ζ·(1 − a·ζ³)),   a = tan(half the size of a cap),
// which four directions share. At a = 0 it is ζ², the one-plane rule. A cap round each end of the z-axis is flipped
// over onto the far half of the sphere, and the rule is the same above and below the plane z = 0.
// As it stands it carries the circle z = 0 twice round itself, but unevenly: the direction at the angle B lands at
// 2B + 2·atan2(a·sin 3B, 1 − a·cos 3B). So a point at the angle θ is first moved to the angle B that lands at 2θ,
// and its height on a Mercator map is multiplied by dB/dθ, which keeps a small shape beside the plane in shape.
// Both changes fade with that height m as exp(−(m/F4_BAND)²).
// u = e^(iB) is a root of a·E²·u⁴ + u³ − E²·u − a, with E = e^(iθ). Newton's steps start at E.
const F4_CAP = 30, F4_CAP_MOST = 40, F4_BAND = 0.6, F4_CAP_STEPS = 6;
const f4Cap = q => Math.tan(0.5 * aprRad(clamp(q.cap === undefined ? F4_CAP : +q.cap || 0, 0, F4_CAP_MOST)));
function f4Caps(v, n, q = {}) {
  if (n !== 2) return tpOne(v, n);
  const [x, y, z] = v;
  if (z === 0) { const w = tpOne([x, y, 0], 2); return [w[0], w[1], 0]; }
  const r2 = x * x + y * y + z * z;
  if (r2 < 1e-30) return [0, 0, 0];
  const a = f4Cap(q);
  if (!(a > 0)) return tpOne(v, 2);
  const r = Math.sqrt(r2), rxy = Math.hypot(x, y), E = rxy > 0 ? [x / rxy, y / rxy] : [1, 0], E2 = ptMul(E, E);
  let u = E;
  for (let i = 0; i < F4_CAP_STEPS; i++) {
    const u2 = ptMul(u, u), u3 = ptMul(u2, u), g = ptMul(E2, u), gu = ptMul(g, u3), eu = ptMul(E2, u3);
    const p = [a * gu[0] + u3[0] - g[0] - a, a * gu[1] + u3[1] - g[1]], d = [4 * a * eu[0] + 3 * u2[0] - E2[0], 4 * a * eu[1] + 3 * u2[1] - E2[1]];
    const dd = d[0] * d[0] + d[1] * d[1];
    u = [u[0] - (p[0] * d[0] + p[1] * d[1]) / dd, u[1] - (p[1] * d[0] - p[0] * d[1]) / dd];
  }
  const lu = Math.hypot(u[0], u[1]);
  u = [u[0] / lu, u[1] / lu];
  const c3 = ptMul(ptMul(u, u), u)[0], slow = 2 / (2 + 6 * a * (c3 - a) / (1 - 2 * a * c3 + a * a));   // dB/dθ
  const dl = ptMul(u, [E[0], -E[1]]), m = Math.log((r + Math.abs(z)) / Math.max(rxy, 1e-20 * r)), w = Math.exp(-(m / F4_BAND) * (m / F4_BAND));
  const b = Math.atan2(dl[1], dl[0]) * w, T = ptMul(E, [Math.cos(b), Math.sin(b)]), rh = Math.exp(-m * (1 + (slow - 1) * w));
  // e is ζ below the plane and 1/ζ above it, so that it never leaves the unit disc
  const up = z > 0, e = [rh * T[0], (up ? -rh : rh) * T[1]], e3 = ptMul(ptMul(e, e), e);
  const A = [e3[0] - a, e3[1]], B = ptMul(e, [1 - a * e3[0], -a * e3[1]]), N = up ? B : A, D = up ? A : B;
  const n2 = N[0] * N[0] + N[1] * N[1], d2 = D[0] * D[0] + D[1] * D[1], k = r2 / (n2 + d2);
  return [2 * k * (N[0] * D[0] + N[1] * D[1]), 2 * k * (N[1] * D[0] - N[0] * D[1]), k * (n2 - d2)];
}
// Four to one, caps placed by c: the square only. Any other power is the one-plane power.
// The step of f4Caps with its number a taken from c, the constant of the orbit, and no longer real:
//   ζ -> (ζ³ − a) / (ζ·(1 − ā·ζ³)),   a = tan(cap/2)·e^(i·rot)·(c.x + i·c.y),   ā: a with its imaginary part negated.
// The length of a is the size of the caps. Its angle rotates the six pinched directions about the z-axis by a third
// of itself, and the directions they are sent to by two thirds. The length is kept at tan(F4K_CAP_MOST/2) or less:
// at 1/2 the circle z = 0 would stop going round one way.
// The circle z = 0 is doubled exactly, as in f4Caps. With ψ = 3B − (the angle of a), the angle B that lands at 2θ has
//   ψ + 3·atan2(|a|·sin ψ, 1 − |a|·cos ψ) = τ,   τ = 3θ − (the angle of a).
// The left side is odd in ψ and its slope falls from ψ = 0 to ψ = π. So for τ between 0 and π the root lies between
// τ − 3·asin|a| and τ, and Newton's steps from the lower end climb onto it and cannot pass it.
const F4K_CAP = 30, F4K_ROT = -90, F4K_CAP_MOST = 51, F4K_STEPS = 6;
const F4K_A_MOST = Math.tan(0.5 * aprRad(F4K_CAP_MOST));
// a, from the entry's dials q and the constant c
function f4kA(q, c) {
  if (!c) return [0, 0];
  const k = Math.tan(0.5 * aprRad(smDial(q, 'cap', F4K_CAP, 0, F4K_CAP_MOST))), t = aprRad(smDial(q, 'rot', F4K_ROT, -360, 360));
  const a = ptMul([k * Math.cos(t), k * Math.sin(t)], [c[0], c[1]]), l = Math.hypot(a[0], a[1]);
  return l > F4K_A_MOST ? [a[0] * F4K_A_MOST / l, a[1] * F4K_A_MOST / l] : a;
}
function f4kPower(a, v, n) {
  if (n !== 2) return tpOne(v, n);
  const [x, y, z] = v;
  if (z === 0) { const w = tpOne([x, y, 0], 2); return [w[0], w[1], 0]; }
  const r2 = x * x + y * y + z * z;
  if (r2 < 1e-30) return [0, 0, 0];
  const rho = Math.hypot(a[0], a[1]);
  if (!(rho > 0)) return tpOne(v, 2);
  const r = Math.sqrt(r2), rxy = Math.hypot(x, y), E = rxy > 0 ? [x / rxy, y / rxy] : [1, 0];
  const Et = ptMul(ptMul(ptMul(E, E), E), [a[0] / rho, -a[1] / rho]), tau = Math.atan2(Et[1], Et[0]), ta = Math.abs(tau);
  const slope = cs => 1 + 3 * rho * (cs - rho) / (1 - 2 * rho * cs + rho * rho);
  let psi = Math.max(0, ta - 3 * Math.asin(rho)), cs = Math.cos(psi);
  for (let i = 0; i < F4K_STEPS; i++) {
    psi = Math.min(psi - (psi + 3 * Math.atan2(rho * Math.sin(psi), 1 - rho * cs) - ta) / slope(cs), ta);
    cs = Math.cos(psi);
  }
  const slow = 1 / slope(cs);   // dB/dθ
  const m = Math.log((r + Math.abs(z)) / Math.max(rxy, 1e-20 * r)), w = Math.exp(-(m / F4_BAND) * (m / F4_BAND));
  const b = (tau < 0 ? ta - psi : psi - ta) / 3 * w, T = ptMul(E, [Math.cos(b), Math.sin(b)]), rh = Math.exp(-m * (1 + (slow - 1) * w));
  // e is ζ below the plane and 1/ζ above it, so that it never leaves the unit disc. Above it a and ā change places.
  const up = z > 0, e = [rh * T[0], (up ? -rh : rh) * T[1]], e3 = ptMul(ptMul(e, e), e), g = [a[0], up ? -a[1] : a[1]], ge = ptMul([g[0], -g[1]], e3);
  const A = [e3[0] - g[0], e3[1] - g[1]], B = ptMul(e, [1 - ge[0], -ge[1]]), N = up ? B : A, D = up ? A : B;
  const n2 = N[0] * N[0] + N[1] * N[1], d2 = D[0] * D[0] + D[1] * D[1], k = r2 / (n2 + d2);
  return [2 * k * (N[0] * D[0] + N[1] * D[1]), 2 * k * (N[1] * D[0] - N[0] * D[1]), k * (n2 - d2)];
}
// Rules whose orbit carries something besides its point, so that one squaring is not the whole rule. CARRY[id] has:
//   start(q)           what a fresh orbit carries (q: the entry's dials)
//   step(st, z, c, q)  what it carries once the step that starts at the orbit point z, with the constant c, has begun.
//                      Called once per step, before any power of that step is taken. A step that starts at the exact
//                      origin changes nothing (so the Mandelbrot orbit counts from its point c), and neither does one
//                      that starts at the point at infinity, which the orbit code puts at 1e9 on the x-axis.
//   pw(st, v, n)       the power n of v in that step. An equation that takes several powers in one step (z² + z³ + c)
//                      takes them all with the same st.
// The shader has the same three pieces (carStart, carStep, the entry's pw) behind the hooks of APR_CARRY.
const carOrigin = v => { const r2 = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]; return !(r2 >= 1e-30) || r2 >= 1e17; };
// Pulled plane. The orbit carries w = |w|·(cos 2θ, sin 2θ): θ is the turn of a plane through the x-axis out of the
// plane z = 0, |w| how firmly it is held. The angle is doubled because a plane has no front and back. ppPull is one
// pull by a thing at (y, z), with the weight k and the ease e. A thing on the x-axis, or a weight 0, pulls nothing.
function ppPull(w, y, z, k, e) {
  const m = Math.min(k * (y * y + z * z), 1e18);
  if (!(m > 0)) return w;
  if (z === 0 && w[1] === 0 && w[0] >= 0) return [w[0] + m, 0];   // a thing of the flat page pulling at the flat page: exactly flat
  const pw = Math.atan2(w[1], w[0]);
  let t = Math.atan2(2 * y * z, y * y - z * z) - pw;
  t -= 2 * PI * Math.floor(t / (2 * PI) + 0.5);
  const a = pw + t - e * Math.sin(t);
  return [w[0] + m * Math.cos(a), w[1] + m * Math.sin(a)];
}
// the one-plane power about the plane w
function ppPower(w, v, n) {
  const [x, y, z] = v;
  if (w[1] === 0 && w[0] >= 0) { const o = tpOne(v, n); return z === 0 ? [o[0], o[1], 0] : o; }
  const th = 0.5 * Math.atan2(w[1], w[0]), c = Math.cos(th), s = Math.sin(th);
  const o = tpOne([x, c * y + s * z, c * z - s * y], n);
  return [o[0], c * o[1] - s * o[2], s * o[1] + c * o[2]];
}
const ppDial = (q, key, def) => (q && q[key] !== undefined && isFinite(+q[key]) ? +q[key] : def);
// Many turns about the origin take the x-axis onto the direction of v: the axis may be any direction that is as far
// from the x-axis as from v, a full circle of directions. axNear is the one whose axis is nearest to the direction h,
// as { m, c, s }: the axis, and the cosine and sine of the angle. null: no turn is needed (the origin, the positive
// x-axis). With h the z-axis a point of the plane z = 0 gets the turn about the z-axis by its own angle, which is
// the flat rule.
function axNear(v, h) {
  const [x, y, z] = v, r = Math.hypot(x, y, z);
  if (!(r > 1e-20)) return null;
  const u = [x / r, y / r, z / r];
  // d: from the x-axis to the direction of v. Its x part is u[0] - 1, written so that no digits are lost near the axis.
  const d = [x > 0 ? -(y * y + z * z) / (r * (r + x)) : u[0] - 1, u[1], u[2]], d2 = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];
  if (!(d2 > 1e-24)) return null;
  const k = (h[0] * d[0] + h[1] * d[1] + h[2] * d[2]) / d2;
  let m = [h[0] - k * d[0], h[1] - k * d[1], h[2] - k * d[2]], ml = Math.hypot(m[0], m[1], m[2]);
  // h points straight from the x-axis to v, so every axis on the circle is as near: take the shortest turn
  if (!(ml > 1e-9)) { m = [0, -u[2], u[1]]; ml = Math.hypot(m[1], m[2]); }
  if (!(ml > 1e-9)) { m = [0, 0, 1]; ml = 1; }
  m = [m[0] / ml, m[1] / ml, m[2] / ml];
  const s2 = 1 - m[0] * m[0];
  return s2 > 1e-18 ? { m, c: (u[0] - m[0] * m[0]) / s2, s: (m[2] * u[1] - m[1] * u[2]) / s2 } : null;
}
// The power n of v by the turn t of axNear: v is turned n - 1 times more about the same axis, and its length is
// raised to n. A point of the plane z = 0 turned about the z-axis keeps z exactly 0.
function axPower(v, n, t) {
  const [x, y, z] = v, r = Math.hypot(x, y, z);
  if (r < 1e-20 && n > 0) return [0, 0, 0];
  const R = aprPow(r, n);
  if (!(r > 0)) return [R, 0, 0];
  const u = [x / r, y / r, z / r];
  if (!t) return [R * u[0], R * u[1], R * u[2]];
  const a = Math.atan2(t.s, t.c) * (n - 1), ca = Math.cos(a), sa = Math.sin(a), m = t.m;
  const k = (m[0] * u[0] + m[1] * u[1] + m[2] * u[2]) * (1 - ca);
  return [R * (u[0] * ca + (m[1] * u[2] - m[2] * u[1]) * sa + m[0] * k),
          R * (u[1] * ca + (m[2] * u[0] - m[0] * u[2]) * sa + m[1] * k),
          R * (u[2] * ca + (m[0] * u[1] - m[1] * u[0]) * sa + m[2] * k)];
}
// Parts. The flat power is fitted at one flat point, the centre u, by a move of the plane that keeps every shape, and
// that move is carried into space: each such move has one partner there that keeps the side z > 0. A part of space
// is moved as a whole by the move of its centre. ptPow: the power n of a flat point.
function ptPow(u, n) {
  if (n === 2) return [u[0] * u[0] - u[1] * u[1], 2 * u[0] * u[1]];
  const R = aprPow(Math.hypot(u[0], u[1]), n), a = Math.atan2(u[1], u[0]) * n;
  return [R * Math.cos(a), R * Math.sin(a)];
}
const ptMul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const ptCap = o => { const m = Math.max(Math.abs(o[0]), Math.abs(o[1]), Math.abs(o[2])), cap = 1.74e18; return m > cap ? scl(o, cap / m) : o; };   // aprCap in the shader
// what a point of the flat plane gets: the flat power itself
const ptFlat = (v, n) => { const o = ptPow(v, n); return ptCap([o[0], o[1], 0]); };
// The turn-and-scale with the value and the slope of the power at u:  z -> u^n + n·u^(n−1)·(z − u).
// Heights are scaled as lengths in the plane are.
function ptTurn(v, u, n) {
  const a = ptPow(u, n), b = n === 2 ? [2 * u[0], 2 * u[1]] : ptPow(u, n - 1).map(x => n * x), o = ptMul(b, [v[0] - u[0], v[1] - u[1]]);
  return ptCap([a[0] + o[0], a[1] + o[1], Math.hypot(b[0], b[1]) * v[2]]);
}
// The Möbius move with the value, the slope and the bend of the power at u:
//   z -> a + b·d / (1 − k·d),   d = z − u,  a = u^n,  b = n·u^(n−1),  k = (n − 1) / (2u).
// Its pole is p = (1 + s)·u with s = 2 / (n − 1). In space it is the sphere inversion about p with a mirror, then a
// turn, a scaling and a slide:  (z, h) -> ((1 − n·s)·a − g·conj(z − p) / D,  |g|·h / D),  D = |z − p|² + h²,  g = n·s²·a·u.
function ptMob(v, u, n) {
  if (Math.abs(n - 1) < 1e-6) return v;
  const s = 2 / (n - 1), a = ptPow(u, n), g = ptMul(a, u).map(x => n * s * s * x), q = [v[0] - (1 + s) * u[0], v[1] - (1 + s) * u[1]];
  const D = Math.max(q[0] * q[0] + q[1] * q[1] + v[2] * v[2], 1e-30), o = ptMul(g, [q[0], -q[1]]);
  return ptCap([(1 - n * s) * a[0] - o[0] / D, (1 - n * s) * a[1] - o[1] / D, Math.hypot(g[0], g[1]) * v[2] / D]);
}
// The doubling grid, for the whole power m (2 or more). A point is read as rho = log|v|, its longitude th and its
// elevation phi above the flat plane: near that plane the power multiplies all three by m. Layer j (1, 2, ...) is
// the band of elevations from 90°/m^j up to 90°/m^(j−1); the cones between the layers are the ones the power
// carries, step by step, onto the upright axis. In layer j the parts are boxes of side a = 90°/m^j in rho and in
// th, centred on the whole multiples of a, and the power carries those centres onto the centres of layer j − 1.
// `finer` divides a by m that many more times. Returns the flat point under the centre of the part that holds v.
function ptGrid(v, n, finer = 0) {
  const m = Math.max(2, Math.floor(Math.abs(n) + 0.5)), phi = Math.atan2(Math.abs(v[2]), Math.hypot(v[0], v[1]));
  if (phi < 2e-5) return [v[0], v[1]];          // the parts are too small to tell from points
  const a = 0.5 * PI * Math.pow(m, -Math.floor(Math.log(0.5 * PI / phi) / Math.log(m)) - 1 - finer);
  const rho = a * Math.floor(Math.log(Math.hypot(v[0], v[1], v[2])) / a + 0.5), th = a * Math.floor(Math.atan2(v[1], v[0]) / a + 0.5);
  return [Math.exp(rho) * Math.cos(th), Math.exp(rho) * Math.sin(th)];
}
const ptFiner = q => clamp(Math.round((q && +q.finer) || 0), 0, 6);
// The square grid: boxes that halve towards the flat plane. A point at the height h above or below the plane lies
// in a box of side s, the power of 2 with s <= h < 2s, and the boxes of that side stand on the whole multiples of
// s. Returns the flat point under the middle of the box, which is never the origin.
function ptSquare(v) {
  const h = Math.abs(v[2]);
  if (h < 1e-5 * (Math.hypot(v[0], v[1]) + 1e-5)) return [v[0], v[1]];
  const s = Math.pow(2, Math.floor(Math.log2(h)));
  return [s * (Math.floor(v[0] / s) + 0.5), s * (Math.floor(v[1] / s) + 0.5)];
}
// Parts of no size: every point is its own part. Its centre is where the quarter circle through the point, about
// the origin and square to the flat plane, comes down on that plane.
function ptFoot(v) {
  const r = Math.hypot(v[0], v[1]), R = Math.hypot(v[0], v[1], v[2]);
  return r > 0 ? [R * v[0] / r, R * v[1] / r] : [R, 0];
}
const CARRY = {
  // Along once, then one plane. Carried: how many steps have counted, this one included.
  alongonce: {
    start: () => 0,
    step: (st, z) => (carOrigin(z) ? st : st + 1),
    pw: (st, v, n) => (st === 1 ? tpPower(v, n, true) : tpOne(v, n)),
  },
  // Pulled plane. Carried: w. Before the powers of a step c pulls, then the orbit point.
  // usesC: the first squaring already depends on c, so the card, which shows that squaring, must follow c.
  pulledplane: {
    usesC: true,
    start: q => [ppDial(q, 'hold', 0.05), 0],
    step(st, z, c, q) {
      if (carOrigin(z)) return st;
      const e = ppDial(q, 'ease', 0.7);
      return ppPull(ppPull(st, c[1], c[2], ppDial(q, 'cpull', 16), e), z[1], z[2], 1, e);
    },
    pw: (st, v, n) => ppPower(st, v, n),
  },
  // Four to one, caps placed by c. Carried: a, which c gives at every step and nothing else changes.
  // usesC: every squaring depends on c, so the card must follow c.
  fourcapsc: {
    usesC: true,
    start: () => [0, 0],
    step: (st, z, c, q) => (c ? f4kA(q, c) : st),
    pw: (st, v, n) => f4kPower(st, v, n),
  },
  // Soft mirrors, doubling. Carried: how many steps have counted, this one included, and the two dials, which pw
  // is not handed. The mirrors double until the step named by the dial "stop" and stay as they are after it.
  mirrorsdouble: {
    start: q => ({ k: 0, soft: smDial(q, 'soft', 2, 0, 45), stop: Math.round(smDial(q, 'stop', 3, 1, 12)) }),
    step: (st, z) => (carOrigin(z) ? st : { k: st.k + 1, soft: st.soft, stop: st.stop }),
    pw: (st, v, n) => MATH.mercator(smFoldK(v, clamp(st.k, 1, st.stop), st.soft), n, {}),
  },
  // Blended mirrors, doubling. The page's own orbit takes the sharp mirrors; the picture blends (APR_BLEND).
  mirrorsblend: {
    start: q => ({ k: 0, stop: Math.round(smDial(q, 'stop', 3, 1, 12)) }),
    step: (st, z) => (carOrigin(z) ? st : { k: st.k + 1, stop: st.stop }),
    pw: (st, v, n) => MATH.mercator(smFoldK(v, clamp(st.k, 1, st.stop), 0), n, {}),
  },
  // Sphere inversions, either side. The page's own orbit is the plain one, every choice "not mirrored"; the picture
  // asks all the choices, in the shader (APR_EITHER). Carried: nothing the page needs.
  either: {
    start: () => ({ k: 0 }),
    step: (st, z) => (carOrigin(z) ? st : { k: st.k + 1 }),
    pw: (st, v, n) => MATH.mercator(v, n, {}),
  },
  // Quaternion square, axis by step. Carried: how many steps have counted, this one included, and the two dials.
  tiltstep: {
    start: q => ({ k: 0, first: ppDial(q, 'first', 0), turn: ppDial(q, 'turn', 90) }),
    step: (st, z) => (carOrigin(z) ? st : { k: st.k + 1, first: st.first, turn: st.turn }),
    pw: (st, v, n) => MATH.tilt(v, n, { tilt: st.first + (Math.max(st.k, 1) - 1) * st.turn }),
  },
  // All axes, nearest to the last one. Carried: h, the axis of the last turn (the z-axis for a fresh orbit), and
  // t, the turn of the step under way.
  lastaxis: {
    start: () => ({ h: [0, 0, 1], t: null }),
    step(st, z) {
      if (carOrigin(z)) return { h: st.h, t: null };
      const t = axNear(z, st.h);
      return { h: t ? t.m : st.h, t };
    },
    pw: (st, v, n) => axPower(v, n, st.t),
  },
  // Parts carried by the orbit. Carried: u, the flat point the moves of the orbit are fitted at. It starts under
  // the first point of the orbit and goes on by the flat rule z^n + c, with n the power of the page.
  partsorbit: {
    start: () => ({ u: null }),
    step(st, z, c) {
      if (carOrigin(z)) return st;
      if (!st.u) return { u: [z[0], z[1]] };
      const w = ptPow(st.u, S.n);
      return { u: [w[0] + c[0], w[1] + c[1]] };
    },
    pw: (st, v, n) => (v[2] === 0 ? ptFlat(v, n) : ptMob(v, st.u || [v[0], v[1]], n)),
  },
  // Custom (12-custom.js). One pass of the user's steps is the whole step of an orbit, c included, so the power
  // handed back here is that pass with c taken off again: whoever adds c to it has the whole step. Carried: c, and
  // for the names first, last, mean, count and point( ) the number of steps that have counted (n), the orbit's first point,
  // the point of the step before (last; prev is the point of this step, for the next one) and the sum of its points.
  custom: {
    start: () => ({ n: 0, first: [0, 0, 0], prev: [0, 0, 0], last: [0, 0, 0], sum: [0, 0, 0], c: [0, 0, 0], hist: [] }),
    step(st, z, c) {
      const cc = c || [0, 0, 0];
      // keptIn: what the rule's own kept values hold as this step begins, which is what the pass before left (keptOut)
      const keptIn = st.keptOut || st.keptIn;
      // cIn: c as the passes before have left it, where a step of the iterations changes c (cOut); else nothing
      const cIn = st.cOut || st.cIn;
      // cm: c as the steps taken once before the iterations make it, which is what the first pass works with
      const cm = cuCmap(cc);
      if (carOrigin(z)) return { ...st, c: cc, cm, keptIn, keptOut: undefined, cIn, cOut: undefined };
      const one = st.n === 0;
      // hist: the orbit's first points in order, for point( ) (as many as the shader keeps, CU_HIST)
      return { n: st.n + 1, first: one ? z : st.first, last: one ? z : st.prev, prev: z, sum: add(st.sum, z), c: cc, hist: st.hist.length < CU_HIST ? st.hist.concat([z]) : st.hist, keptIn, cm, cIn };
    },
    pw: (st, v, n) => sub(cuRun(v, st.cm || st.c, n, st), st.c),
  },
};
// The first squaring of a fresh orbit: all that the card, which looks at one squaring, can show. (In space the
// Learn tab follows the orbit through CARRY itself.)
const carFirst = (id, v, n, q, c) => { const R = CARRY[id]; return R.pw(R.step(R.start(q), v, c, q), v, n); };
// The power maps in JavaScript: MATH[id](v, n, q) with q the approach's parameter object. They mirror the
// shader code below line for line, so what the scorecard measures is what the picture shows.
const MATH = {
  // One plane: longitude and Mercator latitude times n, then the turn and the lift. For whole n this is the closed
  // form of n + 1 sphere inversions, added:  v^n = |v|^n * [1 + n * inv(sum_k R_k inv(d - w_k))],  d = v / |v|,
  // with w_k the n-th roots of unity on the unit circle of the xy-plane, R_k the turn about the z-axis by the
  // angle of w_k, and inv(q) = (x, -y, -z) / |q|^2. A negative n takes one more inversion.
  mercator(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const Z = r > 0 ? clamp(z / r, -0.999999, 0.999999) : 0;
    const m = clamp(n * Math.atanh(Z), -20, 20) + (q.lift || 0), h = 1 / Math.cosh(m);
    const R = aprPow(r, n), p = Math.atan2(y, x) * n + aprRad(q.turn);
    return [R * h * Math.cos(p), R * h * Math.sin(p), R * Math.tanh(m)];
  },
  // Two or more planes: the fold, then the one-plane rule. No turn: the fold relies on the mirror symmetry
  // y -> -y, which a turn breaks.
  fold(v, n, q = {}) {
    return MATH.mercator(foldk(v, Math.max(2, q.planes || 2)), n, { lift: q.lift });
  },
  softmirror(v, n, q = {}) { return MATH.mercator(smFold(v, q), n, {}); },
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
  // Quaternions, 4D: the power is the quaternion power (the Lathe with spin 1). The slice sits in the shader's
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
  kleinsq(v, n) { return kqPower(v, n, false); },
  kleinsq2(v, n) { return kqPower(v, n, true); },
  sqpillow(v, n) { return spPower(v, n); },
  turnaway(v, n) { return tpPower(v, n, false); },
  turnalong(v, n) { return tpPower(v, n, true); },
  windsq(v, n) { return wsPower(v, n); },
  fourplanes(v, n) { return f4Planes(v, n); },
  fourcaps(v, n, q = {}) { return f4Caps(v, n, q); },
  // Rules whose orbit carries something (see CARRY): each gives the first squaring of a fresh orbit. For
  // pulledplane and fourcapsc c is the constant of that orbit.
  alongonce(v, n) { return carFirst('alongonce', v, n, {}, [0, 0, 0]); },
  mirrorsdouble(v, n, q = {}) { return carFirst('mirrorsdouble', v, n, q, [0, 0, 0]); },
  // The plain choice of Sphere inversions, either side: one plane.
  either(v, n) { return MATH.mercator(v, n, {}); },
  mirrorsblend(v, n, q = {}) { return carFirst('mirrorsblend', v, n, q, [0, 0, 0]); },
  pulledplane(v, n, q = {}, c) { return carFirst('pulledplane', v, n, q, c); },
  fourcapsc(v, n, q = {}, c) { return carFirst('fourcapsc', v, n, q, c); },
  tiltstep(v, n, q = {}) { return carFirst('tiltstep', v, n, q, [0, 0, 0]); },
  // All axes, nearest to upright: of the turns that take the x-axis onto the point, the one about the axis nearest
  // to the z-axis.
  nearaxis(v, n) { return axPower(v, n, axNear(v, [0, 0, 1])); },
  lastaxis(v, n) { return carFirst('lastaxis', v, n, {}, [0, 0, 0]); },
  // Even pillow. The direction d = (X, Y, Z) is written on a square pillow grid (A, L):
  //   d = N(cos A, sin A cos L, sin L),  N = "made length 1".  L = 0 is the circle z = 0 (A is the angle there),
  //   A = 90 degrees is the circle x = 0 (L is the angle there); both are laid at an even speed. The four corners of
  //   the pillow are the directions (+-1, 0, +-1). Read back: rho^2 = 2 / (1 + sqrt(1 - 4 X^2 Z^2)), cos A = rho X,
  //   sin L = rho Z, cos L >= 0, sin A with the sign of Y. The power multiplies both A and L by n.
  //   The length is the plain power |v|^n: this entry alone is not capped (aprPow), and it leaves the origin at
  //   the origin at every power.
  evenpillow(v, n) {
    const [x, y, z] = v, r2 = x * x + y * y + z * z;
    if (!(r2 > 1e-300)) return [0, 0, 0];
    const r = Math.sqrt(r2), X = x / r, Y = y / r, Z = z / r;
    const rho = Math.sqrt(2 / (1 + Math.sqrt(Math.max(1 - 4 * X * X * Z * Z, 0))));
    const cA = clamp(rho * X, -1, 1), sL = clamp(rho * Z, -1, 1);
    const sA = (Y < 0 ? -1 : 1) * Math.sqrt(Math.max(1 - cA * cA, 0)), cL = Math.sqrt(Math.max(1 - sL * sL, 0));
    let w;
    if (n === 2) w = [2 * cA * cA - 1, 2 * sA * cA * (1 - 2 * sL * sL), 2 * sL * cL];
    else { const A = Math.atan2(sA, cA) * n, L = Math.asin(sL) * n; w = [Math.cos(A), Math.sin(A) * Math.cos(L), Math.sin(L)]; }
    const m = Math.pow(r, n) / Math.hypot(w[0], w[1], w[2]);
    return [w[0] * m, w[1] * m, w[2] * m];
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
  // A negative power is the positive power followed by one sphere inversion with a mirror (y -> -y), which is what
  // a reciprocal is in every other approach. Side by side, (1/(x + iy), 1/z) has no value on the plane z = 0 or on
  // the z-axis. This form is finite everywhere except the origin, and in the plane z = 0 it is complex z^n exactly.
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
    if (k > 1 && d[2] !== 0 && rho > 1e-15) {               // on z = 0, and on the x-axis where every plane agrees, the first plane answers
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
  // Parts (see ptGrid, ptSquare, ptFoot, ptTurn and ptMob). A point of the flat plane takes the flat power itself.
  partsturn(v, n) { return v[2] === 0 ? ptFlat(v, n) : ptTurn(v, ptGrid(v, n), n); },
  partsbend(v, n, q = {}) { return v[2] === 0 ? ptFlat(v, n) : ptMob(v, ptGrid(v, n, ptFiner(q)), n); },
  partssquare(v, n) { return v[2] === 0 ? ptFlat(v, n) : ptTurn(v, ptSquare(v), n); },
  partsorbit(v, n) { return carFirst('partsorbit', v, n, {}, [0, 0, 0]); },
  partsnone(v, n) { return v[2] === 0 ? ptFlat(v, n) : ptMob(v, ptFoot(v), n); },
  custom(v, n, q, c) { return carFirst('custom', v, n, q, c || [0, 0, 0]); },
  // Pillow: a flat sheet of triangles wrapped onto the sphere of directions, in one of two layouts.
  pillow(v, n, q = {}) { return q.layout > 0.5 ? psPower(v, n) : pbPower(v, n); },
};
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
// The one-plane rule, shared by every approach built on it. Each defines aprTurn() and aprLift() itself, because
// the dials sit in different slots of uA.
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
// uA.x: the number of planes (2 or more). uA.y: the lift. No turn (see MATH.fold).
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
// Sphere inversions, soft mirror (see smFold). uA.x: where the mirror stands, in degrees from the flat plane.
// uA.y: how many degrees to each side of the mirror the corner of the fold is rounded. No turn and no lift.
const GL_SOFTMIRROR = GL_APR + `
float aprTurn(){ return 0.0; }
float aprLift(){ return 0.0; }
float smTurn(float a){
  float b = radians(clamp(uA.x, 45.0, 90.0)), w = radians(clamp(uA.y, 0.0, 45.0)), t = a - b;
  if (!(w > 0.0) || abs(t) >= w) return b - abs(t);
  return b - (t * t / (2.0 * w) + 0.5 * w);
}
vec3 smFold(vec3 v){
  float rho = length(v.yz);
  if (v.z == 0.0 || rho < 1e-20) return v;
  float g = smTurn(atan(abs(v.z), abs(v.y)));
  return vec3(v.x, (v.y < 0.0 ? -1.0 : 1.0) * rho * cos(g), (v.z < 0.0 ? -1.0 : 1.0) * rho * sin(g));
}` + GL_MERC_CORE + `
vec3 mul(vec3 a, vec3 b){ return aprMmul(smFold(a), smFold(b)); }
vec3 pw(vec3 a, float n){ return aprMpw(smFold(a), n); }
vec3 sqr(vec3 a){ return aprMsq(smFold(a)); }
vec3 cmap(vec3 c){ return smFold(c); }`;
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
// The quaternion power measured from an axis tilted inside the plane z = 0 (see MATH.tilt). aprTilt() is the tilt.
const GL_TILT_CORE = `
vec3 aprRz(vec3 v, float a){ float c = cos(a), s = sin(a); return vec3(c * v.x - s * v.y, s * v.x + c * v.y, v.z); }
vec3 aprLmul(vec3 a, vec3 b){ return vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz); }
vec3 mul(vec3 a, vec3 b){ float t = aprTilt(); return aprCap(aprRz(aprLmul(aprRz(a, t), aprRz(b, t)), -2.0 * t)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float t = aprTilt();
  vec3 u = aprRz(v, t);
  float rho = length(u.yz), a = at2(rho, u.x) * n;
  vec2 d = rho > 0.0 ? u.yz / rho : vec2(1.0, 0.0);
  return aprRz(aprPow(r, n) * vec3(cos(a), sin(a) * d), -n * t);
}
vec3 sqr(vec3 v){
  float t = aprTilt();
  vec3 u = aprRz(v, t);
  return aprCap(aprRz(vec3(u.x * u.x - dot(u.yz, u.yz), 2.0 * u.x * u.yz), -2.0 * t));
}
vec3 cmap(vec3 c){ return c; }`;
// uA.x: the tilt in degrees.
const GL_TILT = GL_APR + `
float aprTilt(){ return radians(uA.x); }` + GL_TILT_CORE;
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
// The one-plane rule with no turn and no lift, for approaches that take their product of two different points
// (aprMmul) or their power from it.
const GL_MERC_PLAIN = `
float aprTurn(){ return 0.0; }
float aprLift(){ return 0.0; }` + GL_MERC_CORE;
// the one-plane power with no turn and no lift; at n = 2 the closed form (the twin of the JavaScript tpOne)
const GL_TP_ONE = `
vec3 tpOne(vec3 v, float n){ return n == 2.0 ? aprMsq(v) : aprMpw(v, n); }`;
// Blended planes. uA = (planes, width of each plane's own band, curve: 0 smoothstep 1 smootherstep,
// mix: 0 great circle 1 straight 2 pinch). cmap is the identity: the constant is not folded.
const GL_SOFTFOLD = GL_APR + GL_MERC_PLAIN + `
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
  // on z = 0, and on the x-axis where every plane agrees, the first plane answers
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
const GL_PILLOW = GL_APR + GL_MERC_PLAIN + `
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
// cos and sin of an angle in degrees, with a value that should be exactly 0 made exactly 0 (the twin of aprCosSin above)
const GL_COSSIN = `
vec2 aprCosSin(float deg){ float a = radians(deg); vec2 cs = vec2(cos(a), sin(a)); return vec2(abs(cs.x) < 1e-6 ? 0.0 : cs.x, abs(cs.y) < 1e-6 ? 0.0 : cs.y); }`;
// Quaternions, 4D. uA.x: where the slice sits on the fourth axis. uA.y: its tilt toward that axis, degrees.
// uA.z: the fourth coordinate of c in a Julia picture. A quaternion orbit of q^n + c never leaves the flat sheet or
// the 3D space spanned by 1, the imaginary part of c and the imaginary part of its start, so three numbers hold it:
// (real part, part along Im c, part across Im c), and the step is the Lathe's. cmap gives c in those numbers, and
// zmap (the hook APR_ZMAP in the orbit code) the start of a Julia orbit. Both keep the turn about the x-axis that
// (y, z) had, so that with all three dials at 0 they change nothing: then this is the Lathe to the last bit.
const GL_QUAT4 = GL_APR + GL_COSSIN + `
#define APR_ZMAP 1
vec4 q4E(vec3 P){ vec2 t = aprCosSin(uA.y); return vec4(P.x * t.x - uA.x * t.y, P.y, P.z, P.x * t.y + uA.x * t.x); }
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
const GL_ROTOR = GL_APR + GL_COSSIN + `
vec3 rtAxis(){ vec2 lo = aprCosSin(uA.x), la = aprCosSin(uA.y); return vec3(la.x * lo, la.y); }
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
  vec2 lo = aprCosSin(uA.x);
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
const GL_KLEINSQ_CORE = GL_APR + GL_MERC_PLAIN + `
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
// Square pillow, the same steps as spLayout, spBeta, spTurn and spPower above. No dials. The product of two
// different points is the one-plane product (aprMmul). spLay gives the layout of the whole power m:
// K = (bn, bs, sinh(bn·wn), sinh(bs·ws)) and the belt t0.
const spGl = x => { const t = String(+x.toPrecision(10)); return /[.e]/.test(t) ? t : t + '.0'; };
const GL_SQPILLOW = GL_APR + GL_MERC_PLAIN + `
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
// Turning plane, away and along (see tpPower). The two differ only in tpTurn, how far the plane turns for the
// whole power m. No dials. The product of two different points is the one-plane product (aprMmul).
// glTurningCore is the rule without mul, pw, sqr and cmap: "Along once, then one plane" uses it for one step.
const glTurningCore = turn => GL_APR + GL_MERC_PLAIN + GL_TP_ONE + `
float tpTurn(float m){ return ${turn}; }
vec3 tpPw(vec3 v, float n){
  if (v.z == 0.0){ vec3 w = tpOne(v, n); return vec3(w.xy, 0.0); }
  float m = max(1.0, floor(abs(n) + 0.5)), phi = atan(v.z, v.y);
  float psi = tpTurn(m) * (phi - sin(2.0 * m * phi) / (2.0 * m)), c = cos(psi), s = sin(psi);
  vec3 w = tpOne(vec3(v.x, c * v.y + s * v.z, c * v.z - s * v.y), n);
  return vec3(w.x, c * w.y - s * w.z, s * w.y + c * w.z);
}`;
const glTurning = turn => glTurningCore(turn) + `
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return tpPw(a, n); }
vec3 sqr(vec3 a){ return tpPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
const GL_TURNAWAY = glTurning('1.0 - m'), GL_TURNALONG = glTurning('1.0');

// Wind, then square (see wsPower). No dials. The product of two different points is the one-plane product (aprMmul).
const GL_WINDSQ = GL_APR + GL_MERC_PLAIN + GL_TP_ONE + `
float wsCount(float n){ float m = max(1.0, floor(abs(n) + 0.5)); return mod(m, 2.0) > 0.5 ? m : m + 1.0; }
vec3 wsPw(vec3 v, float n){
  if (v.z == 0.0){ vec3 w = tpOne(v, n); return vec3(w.xy, 0.0); }
  float k = wsCount(n), rho = length(v.yz);
  if (k < 1.5 || !(rho > 1e-18)) return tpOne(v, n);
  vec2 u = v.yz / rho, e = u;
  int kk = int(k + 0.5);
  for (int i = 1; i < 16; i++){ if (i >= kk) break; e = cmul(e, u); }
  float d = (k - 1.0) * e.x * e.y / k;
  return tpOne(vec3(v.x, rho * cmul(e, vec2(cos(d), -sin(d)))), n);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return wsPw(a, n); }
vec3 sqr(vec3 a){ return wsPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;

// Four to one, two planes alike (see f4Planes). No dials. The product of two different points is the one-plane
// product (aprMmul).
const GL_FOURPLANES = GL_APR + GL_MERC_PLAIN + GL_TP_ONE + `
vec3 f4pPw(vec3 v, float n){
  if (n != 2.0) return tpOne(v, n);
  if (v.z == 0.0){ vec3 w = aprMsq(vec3(v.xy, 0.0)); return vec3(w.xy, 0.0); }
  if (v.y == 0.0){ vec3 w = aprMsq(vec3(v.xz, 0.0)); return vec3(w.x, 0.0, w.y); }
  float rho = length(v.yz), r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  float r = sqrt(r2), s = rho / r, c = abs(v.x) / r, h = s / max(2.0 * c, 1e-30);
  bool back = v.x < 0.0;
  float t = min(1.0, back ? pow(h, 1.0 / 3.0) : h);
  for (int i = 0; i < ${F4_STEPS}; i++){
    float t2 = t * t, d = 4.0 * s * t2 * t + (back ? 6.0 * c * t2 : 2.0 * c);
    if (d > 1e-20) t -= (s * t2 * t2 + 2.0 * c * (back ? t2 * t : t) - s) / d;
  }
  float l = length(vec2(t, 1.0)), sg = (back ? 1.0 : t) / l, cg = (back ? t : 1.0) / l;
  float cb = cg * cg - sg * sg, sb = 2.0 * sg * cg, K = 2.0 * (1.0 - cb + cb * cb) / sqrt(sb * sb * (1.0 + cb) * (1.0 + cb) + 4.0 * cb * cb);
  vec2 e = v.yz / rho;
  float a = (1.0 - 1.0 / K) * (e.x * e.x - e.y * e.y) * e.x * e.y;
  vec2 f = cmul(e, vec2(cos(a), -sin(a))), f2 = cmul(f, f);
  float k = 2.0 * sg * cg * cg * cg, s4 = sg * sg * sg * sg;
  vec2 N = k * f, D = vec2(cg * cg * cg * cg, 0.0) - s4 * cmul(f2, f2);
  float n2 = dot(N, N), d2 = dot(D, D), m = min(r2, APR_CAP) / (n2 + d2);
  return m * vec3(d2 - n2, 2.0 * (N.x * D.x + N.y * D.y), 2.0 * (N.y * D.x - N.x * D.y));
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return f4pPw(a, n); }
vec3 sqr(vec3 a){ return f4pPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// Four to one, caps flipped over (see f4Caps). uA.x: the size of a cap, in degrees.
const GL_FOURCAPS = GL_APR + GL_MERC_PLAIN + GL_TP_ONE + `
vec2 f4Cube(vec2 a){ return cmul(cmul(a, a), a); }
vec3 f4cPw(vec3 v, float n){
  if (n != 2.0) return tpOne(v, n);
  if (v.z == 0.0){ vec3 w = aprMsq(vec3(v.xy, 0.0)); return vec3(w.xy, 0.0); }
  float r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  float a = tan(0.5 * radians(clamp(uA.x, 0.0, ${F4_CAP_MOST}.0)));
  if (!(a > 0.0)) return aprMsq(v);
  float r = sqrt(r2), rxy = length(v.xy);
  vec2 E = rxy > 0.0 ? v.xy / rxy : vec2(1.0, 0.0), E2 = cmul(E, E), u = E;
  for (int i = 0; i < ${F4_CAP_STEPS}; i++){
    vec2 u2 = cmul(u, u), u3 = cmul(u2, u), g = cmul(E2, u);
    vec2 p = a * cmul(g, u3) + u3 - g - vec2(a, 0.0), d = 4.0 * a * cmul(E2, u3) + 3.0 * u2 - E2;
    u -= vec2(dot(p, d), p.y * d.x - p.x * d.y) / dot(d, d);
  }
  u = normalize(u);
  float c3 = f4Cube(u).x, slow = 2.0 / (2.0 + 6.0 * a * (c3 - a) / (1.0 - 2.0 * a * c3 + a * a));
  vec2 dl = cmul(u, vec2(E.x, -E.y));
  float m = log((r + abs(v.z)) / max(rxy, 1e-20 * r)), w = exp(-(m / ${F4_BAND}) * (m / ${F4_BAND})), b = atan(dl.y, dl.x) * w;
  vec2 T = cmul(E, vec2(cos(b), sin(b)));
  float rh = exp(-m * (1.0 + (slow - 1.0) * w));
  bool up = v.z > 0.0;
  vec2 e = vec2(rh * T.x, (up ? -rh : rh) * T.y), e3 = f4Cube(e);
  vec2 A = e3 - vec2(a, 0.0), B = cmul(e, vec2(1.0, 0.0) - a * e3), N = up ? B : A, D = up ? A : B;
  float n2 = dot(N, N), d2 = dot(D, D), k = min(r2, APR_CAP) / (n2 + d2);
  return k * vec3(2.0 * (N.x * D.x + N.y * D.y), 2.0 * (N.y * D.x - N.x * D.y), n2 - d2);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return f4cPw(a, n); }
vec3 sqr(vec3 a){ return f4cPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;

// Rules whose orbit carries something besides its point (the same steps as CARRY above). APR_CARRY switches on four
// hooks in the orbit code (orbitDE and f in 30-shaders.js), and an approach that defines it must define what they call:
//   carStart()        before an orbit is run (and when the orbit is begun again from a pole): everything carried is
//                     made fresh, for the point itself and for each of its neighbouring orbits.
//   gCarI             set before each f(): which orbit the step belongs to, 0 the point itself, 1 to 3 its neighbours.
//                     The orbit code runs them interleaved, a step of each in turn, so each needs a slot of its own.
//   carStep(z, c)     called once in every f(), before the equation takes any power: the step that starts at z, with
//                     the constant c, changes what orbit gCarI carries. pw and sqr then read it and do not change it.
//   carFit(i, s)      after each step a neighbour is pulled back to a fixed small distance from the point (its offset
//                     is multiplied by s). What it carries is pulled back the same way; s = 0: it landed across a seam
//                     and is given what the point itself carries.
const GL_CARRY = `
#define APR_CARRY 1
int gCarI;
bool carOrigin(vec3 z){ float r2 = dot(z, z); return !(r2 >= 1e-30) || r2 >= 1e17; }`;
// Along once, then one plane. Carried: the number of steps that have counted, this one included. It is a property of
// the point's own orbit: a neighbouring orbit stands for a small push of that orbit, so it takes the same rule at
// every step and has no count of its own.
const GL_ALONGONCE = glTurningCore('1.0') + GL_CARRY + `
float gAoCount;
void carStart(){ gAoCount = 0.0; gCarI = 0; }
void carStep(vec3 z, vec3 c){ if (gCarI == 0 && !carOrigin(z)) gAoCount += 1.0; }
void carFit(int i, float s){ }
vec3 aoPw(vec3 v, float n){ if (gAoCount == 1.0) return tpPw(v, n); return tpOne(v, n); }
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return aoPw(a, n); }
vec3 sqr(vec3 a){ return aoPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// Soft mirrors, doubling (see smFoldK and CARRY.mirrorsdouble). Carried: the number of steps that have counted, this
// one included; a neighbouring orbit takes the rule of the point's own step, as in Along once, then one plane.
// uA.x: the soft edge of the first mirror, in degrees. uA.y: the step after which the mirrors stop doubling.
const GL_MIRRORSDOUBLE = GL_APR + GL_MERC_PLAIN + GL_CARRY + `
float gMdCount;
void carStart(){ gMdCount = 0.0; gCarI = 0; }
void carStep(vec3 z, vec3 c){ if (gCarI == 0 && !carOrigin(z)) gMdCount += 1.0; }
void carFit(int i, float s){ }
vec3 mdFold(vec3 v, float k){
  float rho = length(v.yz);
  if (v.z == 0.0 || rho < 1e-20) return v;
  float h = exp2(1.0 - k), b = 0.25 * PI * h, w = radians(clamp(uA.x, 0.0, 45.0)) * h;
  float a = atan(abs(v.z), abs(v.y)), t = a - 2.0 * b * floor(a / (2.0 * b)) - b;
  float g = !(w > 0.0) || abs(t) >= w ? b - abs(t) : b - (t * t / (2.0 * w) + 0.5 * w);
  return vec3(v.x, (v.y < 0.0 ? -1.0 : 1.0) * rho * cos(g), (v.z < 0.0 ? -1.0 : 1.0) * rho * sin(g));
}
float mdStep(){ return clamp(gMdCount, 1.0, clamp(floor(uA.y + 0.5), 1.0, 12.0)); }
vec3 mul(vec3 a, vec3 b){ return aprMmul(mdFold(a, mdStep()), mdFold(b, mdStep())); }
vec3 pw(vec3 a, float n){ return aprMpw(mdFold(a, mdStep()), n); }
vec3 sqr(vec3 a){ return aprMsq(mdFold(a, mdStep())); }
vec3 cmap(vec3 c){ return mdFold(c, 1.0); }`;
// Sphere inversions, either side. At each of the first steps of an orbit a point may be squared as it is, or
// mirrored first (the sharp mirror at 45 degrees round the x-axis, which moves nothing on the flat side of it).
// A point belongs to the solid if any run of such choices keeps it. APR_EITHER makes the orbit code (30-shaders.js)
// run one orbit per run of choices, gPick naming the run: choice k (0 at the first squaring) is "mirrored" when
// digit k of gPick in base 2 is 1. Carried: the number of squarings so far. uA.x: through which step there is a choice.
const GL_EITHER = GL_APR + GL_MERC_PLAIN + GL_CARRY + `
#define APR_EITHER 1
int gPick = 0;
float gEiCount;
void carStart(){ gEiCount = 0.0; gCarI = 0; }
void carStep(vec3 z, vec3 c){ if (gCarI == 0 && !carOrigin(z)) gEiCount += 1.0; }
void carFit(int i, float s){ }
float eiDepth(){ return clamp(floor(uA.x + 0.5), 0.0, 5.0); }
int eitherCount(){ return int(exp2(eiDepth()) + 0.5); }
vec3 eiFold(vec3 v){
  float k = gEiCount - 1.0;
  if (k < 0.0 || k >= eiDepth() || mod(floor(float(gPick) / exp2(k)), 2.0) < 0.5) return v;
  float rho = length(v.yz);
  if (v.z == 0.0 || rho < 1e-20) return v;
  float g = 0.25 * PI - abs(atan(abs(v.z), abs(v.y)) - 0.25 * PI);
  return vec3(v.x, (v.y < 0.0 ? -1.0 : 1.0) * rho * cos(g), (v.z < 0.0 ? -1.0 : 1.0) * rho * sin(g));
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(eiFold(a), eiFold(b)); }
vec3 pw(vec3 a, float n){ return aprMpw(eiFold(a), n); }
vec3 sqr(vec3 a){ return aprMsq(eiFold(a)); }
vec3 cmap(vec3 c){ return c; }`;
// Even pillow (see MATH.evenpillow for the grid). At the power 2 no angle is taken: the doubled grid point is
// written with squares and roots only, so the plane z = 0 is complex squaring to the last digit.
const GL_EVENPILLOW = GL_APR + GL_MERC_PLAIN + `
vec3 epPw(vec3 v, float n){
  float r2 = dot(v, v);
  if (!(r2 >= 1e-30)) return vec3(0.0);
  float r = sqrt(r2);
  vec3 d = v / r;
  float rho = sqrt(2.0 / (1.0 + sqrt(max(1.0 - 4.0 * d.x * d.x * d.z * d.z, 0.0))));
  float cA = clamp(rho * d.x, -1.0, 1.0), sL = clamp(rho * d.z, -1.0, 1.0);
  float sA = (d.y < 0.0 ? -1.0 : 1.0) * sqrt(max(1.0 - cA * cA, 0.0)), cL = sqrt(max(1.0 - sL * sL, 0.0));
  vec3 w;
  if (n == 2.0) w = vec3(2.0 * cA * cA - 1.0, 2.0 * sA * cA * (1.0 - 2.0 * sL * sL), 2.0 * sL * cL);
  else { float A = atan(sA, cA) * n, L = asin(sL) * n; w = vec3(cos(A), sin(A) * cos(L), sin(L)); }
  return pow(r, n) * normalize(w);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return epPw(a, n); }
vec3 sqr(vec3 a){ return epPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// Blended mirrors, doubling. The mirrors of Soft mirrors, doubling, kept sharp. Beside a mirror a point has two
// places it could be squared from: where the mirror puts it, and the mirror image of that. Within the blend width
// of a mirror the picture runs both orbits and cross-fades their distances, half and half on the mirror itself.
// APR_BLEND makes the orbit code (30-shaders.js) run the orbits: gPick names the run (digit k in base 2: at squaring
// k + 1 take the mirror image), gBlW is the weight of the run, gBlA1..3 say whether the first three squarings of the
// run fell within a blend width. uA.x: the blend width at the first mirror, in degrees. uA.y: where doubling stops.
const GL_MIRRORSBLEND = GL_APR + GL_MERC_PLAIN + GL_CARRY + `
#define APR_BLEND 1
int gPick = 0;
float gMbCount, gMbDone, gBlW;
bool gBlA1, gBlA2, gBlA3;
void carStart(){ gMbCount = 0.0; gMbDone = 0.0; gBlW = 1.0; gBlA1 = false; gBlA2 = false; gBlA3 = false; gCarI = 0; }
void carStep(vec3 z, vec3 c){ if (gCarI == 0 && !carOrigin(z)) gMbCount += 1.0; }
void carFit(int i, float s){ }
float mbStep(){ return clamp(gMbCount, 1.0, clamp(floor(uA.y + 0.5), 1.0, 12.0)); }
vec3 mbTurn(vec3 v, float g){
  float rho = length(v.yz);
  return vec3(v.x, (v.y < 0.0 ? -1.0 : 1.0) * rho * cos(g), (v.z < 0.0 ? -1.0 : 1.0) * rho * sin(g));
}
vec3 mbFold(vec3 v, float k, bool blend){
  if (v.z == 0.0 || length(v.yz) < 1e-20) return v;
  float h = exp2(1.0 - k), b = 0.25 * PI * h, w = radians(clamp(uA.x, 0.0, 45.0)) * h;
  float a = atan(abs(v.z), abs(v.y)), t = abs(a - 2.0 * b * floor(a / (2.0 * b)) - b);
  float g = b - t;
  if (blend && gMbCount >= 1.0 && gMbCount <= 3.0 && gMbCount > gMbDone){
    gMbDone = gMbCount;
    float lam = (w > 0.0 && t < w) ? 0.5 * (1.0 - sin(0.5 * PI * t / w)) : 0.0;
    if (gMbCount < 1.5) gBlA1 = lam > 0.0; else if (gMbCount < 2.5) gBlA2 = lam > 0.0; else gBlA3 = lam > 0.0;
    if (mod(floor(float(gPick) / exp2(gMbCount - 1.0)), 2.0) > 0.5){ g = b + t; gBlW *= lam; } else gBlW *= 1.0 - lam;
  }
  return mbTurn(v, g);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(mbFold(a, mbStep(), false), mbFold(b, mbStep(), false)); }
vec3 pw(vec3 a, float n){ return aprMpw(mbFold(a, mbStep(), true), n); }
vec3 sqr(vec3 a){ return aprMsq(mbFold(a, mbStep(), true)); }
vec3 cmap(vec3 c){ return mbFold(c, 1.0, false); }`;
// Pulled plane (see ppPull, ppPower). Carried: the 2-vector w, one for the point and one for each neighbour.
// uA.x: how firmly the flat page is held at the start. uA.y: the ease. uA.z: how many times the pull of c counts.
const GL_PULLEDPLANE = GL_APR + GL_MERC_PLAIN + GL_TP_ONE + GL_CARRY + `
vec2 gPp0, gPp1, gPp2, gPp3;
vec2 ppGet(){ return gCarI == 0 ? gPp0 : gCarI == 1 ? gPp1 : gCarI == 2 ? gPp2 : gPp3; }
void carStart(){ gPp0 = vec2(uA.x, 0.0); gPp1 = gPp0; gPp2 = gPp0; gPp3 = gPp0; gCarI = 0; }
vec2 ppPull(vec2 w, vec2 p, float k, float e){
  float m = min(k * dot(p, p), 1e18);
  if (!(m > 0.0)) return w;
  if (p.y == 0.0 && w.y == 0.0 && w.x >= 0.0) return vec2(w.x + m, 0.0);
  float a0 = at2(w.y, w.x), t = at2(2.0 * p.x * p.y, p.x * p.x - p.y * p.y) - a0;
  t -= 2.0 * PI * floor(t / (2.0 * PI) + 0.5);
  float a = a0 + t - e * sin(t);
  return w + m * vec2(cos(a), sin(a));
}
void carStep(vec3 z, vec3 c){
  if (carOrigin(z)) return;
  vec2 w = ppPull(ppPull(ppGet(), c.yz, uA.z, uA.y), z.yz, 1.0, uA.y);
  if (gCarI == 0) gPp0 = w; else if (gCarI == 1) gPp1 = w; else if (gCarI == 2) gPp2 = w; else gPp3 = w;
}
void carFit(int i, float s){
  if (i == 1) gPp1 = gPp0 + (gPp1 - gPp0) * s; else if (i == 2) gPp2 = gPp0 + (gPp2 - gPp0) * s; else if (i == 3) gPp3 = gPp0 + (gPp3 - gPp0) * s;
}
vec3 ppPw(vec3 v, float n){
  vec2 w = ppGet();
  if (w.y == 0.0 && w.x >= 0.0){ vec3 o = tpOne(v, n); return v.z == 0.0 ? vec3(o.xy, 0.0) : o; }
  float th = 0.5 * at2(w.y, w.x), c = cos(th), s = sin(th);
  vec3 o = tpOne(vec3(v.x, c * v.y + s * v.z, c * v.z - s * v.y), n);
  return vec3(o.x, c * o.y - s * o.z, s * o.y + c * o.z);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return ppPw(a, n); }
vec3 sqr(vec3 a){ return ppPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// Four to one, caps placed by c (see f4kA, f4kPower). Carried: a. Every step works it out from its own c before it
// takes a power, so the point and its neighbours need no slots of their own. uA.x: the size of a cap where |c| = 1,
// in degrees. uA.y: the rotation of c, in degrees.
const GL_FOURCAPSC = GL_APR + GL_MERC_PLAIN + GL_TP_ONE + GL_CARRY + `
vec2 gFkA;
void carStart(){ gFkA = vec2(0.0); gCarI = 0; }
void carStep(vec3 z, vec3 c){
  float t = radians(clamp(uA.y, -360.0, 360.0)), most = tan(radians(${0.5 * F4K_CAP_MOST}));
  vec2 a = tan(0.5 * radians(clamp(uA.x, 0.0, ${F4K_CAP_MOST}.0))) * cmul(vec2(cos(t), sin(t)), c.xy);
  float l = length(a);
  gFkA = l > most ? a * (most / l) : a;
}
void carFit(int i, float s){ }
vec2 f4kCube(vec2 a){ return cmul(cmul(a, a), a); }
float f4kSlope(float rho, float cs){ return 1.0 + 3.0 * rho * (cs - rho) / (1.0 - 2.0 * rho * cs + rho * rho); }
vec3 f4kPw(vec3 v, float n){
  if (n != 2.0) return tpOne(v, n);
  if (v.z == 0.0){ vec3 w = aprMsq(vec3(v.xy, 0.0)); return vec3(w.xy, 0.0); }
  float r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  vec2 a = gFkA;
  float rho = length(a);
  if (!(rho > 0.0)) return aprMsq(v);
  float r = sqrt(r2), rxy = length(v.xy);
  vec2 E = rxy > 0.0 ? v.xy / rxy : vec2(1.0, 0.0), Et = cmul(f4kCube(E), vec2(a.x, -a.y) / rho);
  float tau = atan(Et.y, Et.x), ta = abs(tau), psi = max(0.0, ta - 3.0 * asin(rho)), cs = cos(psi);
  for (int i = 0; i < ${F4K_STEPS}; i++){
    psi = min(psi - (psi + 3.0 * atan(rho * sin(psi), 1.0 - rho * cs) - ta) / f4kSlope(rho, cs), ta);
    cs = cos(psi);
  }
  float slow = 1.0 / f4kSlope(rho, cs);
  float m = log((r + abs(v.z)) / max(rxy, 1e-20 * r)), w = exp(-(m / ${F4_BAND}) * (m / ${F4_BAND})), b = (tau < 0.0 ? ta - psi : psi - ta) / 3.0 * w;
  vec2 T = cmul(E, vec2(cos(b), sin(b)));
  float rh = exp(-m * (1.0 + (slow - 1.0) * w));
  bool up = v.z > 0.0;
  vec2 e = vec2(rh * T.x, (up ? -rh : rh) * T.y), e3 = f4kCube(e), g = vec2(a.x, up ? -a.y : a.y);
  vec2 A = e3 - g, B = cmul(e, vec2(1.0, 0.0) - cmul(vec2(g.x, -g.y), e3)), N = up ? B : A, D = up ? A : B;
  float n2 = dot(N, N), d2 = dot(D, D), k = min(r2, APR_CAP) / (n2 + d2);
  return k * vec3(2.0 * (N.x * D.x + N.y * D.y), 2.0 * (N.y * D.x - N.x * D.y), n2 - d2);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return f4kPw(a, n); }
vec3 sqr(vec3 a){ return f4kPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// Quaternion square, axis by step. Carried: the number of steps that have counted, this one included; a
// neighbouring orbit takes the rule of the point's own step. uA.x: the tilt at the first step, in degrees.
// uA.y: how far the tilt moves on at each later step.
const GL_TILTSTEP = GL_APR + GL_CARRY + `
float gTsCount;
void carStart(){ gTsCount = 0.0; gCarI = 0; }
void carStep(vec3 z, vec3 c){ if (gCarI == 0 && !carOrigin(z)) gTsCount += 1.0; }
void carFit(int i, float s){ }
float aprTilt(){ return radians(mod(uA.x + (max(gTsCount, 1.0) - 1.0) * uA.y, 360.0)); }` + GL_TILT_CORE;
// The turn of axNear and the power of axPower, as in the JavaScript above. axNear returns the axis and puts the
// cosine and sine of the angle in cs; an axis of length 0 means that no turn is needed.
const GL_AXNEAR = `
vec3 axNear(vec3 v, vec3 h, out vec2 cs){
  cs = vec2(1.0, 0.0);
  float r = length(v);
  if (!(r > 1e-20)) return vec3(0.0);
  vec3 u = v / r;
  vec3 d = vec3(v.x > 0.0 ? -dot(v.yz, v.yz) / (r * (r + v.x)) : u.x - 1.0, u.yz);
  float d2 = dot(d, d);
  if (!(d2 > 1e-14)) return vec3(0.0);
  vec3 m = h - (dot(h, d) / d2) * d;
  float ml = length(m);
  if (!(ml > 1e-5)){ m = vec3(0.0, -u.z, u.y); ml = length(m); }
  if (!(ml > 1e-5)){ m = vec3(0.0, 0.0, 1.0); ml = 1.0; }
  m /= ml;
  float s2 = 1.0 - m.x * m.x;
  if (!(s2 > 1e-10)) return vec3(0.0);
  cs = vec2(u.x - m.x * m.x, m.z * u.y - m.y * u.z) / s2;
  return m;
}
vec3 axTurned(vec3 v, vec3 m, float ca, float sa){ return v * ca + cross(m, v) * sa + m * (dot(m, v) * (1.0 - ca)); }
vec3 axPw(vec3 v, vec3 m, vec2 cs, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float R = aprPow(r, n);
  if (!(r > 0.0)) return vec3(R, 0.0, 0.0);
  if (m == vec3(0.0)) return R * (v / r);
  float a = at2(cs.y, cs.x) * (n - 1.0);
  return R * axTurned(v / r, m, cos(a), sin(a));
}
// At the power 2 no angle is taken, and a point of the plane z = 0 turned about the z-axis is squared as a complex number.
vec3 axSq(vec3 v, vec3 m, vec2 cs){
  if (m == vec3(0.0)) return aprCap(length(v) * v);
  if (v.z == 0.0 && m.z == 1.0) return aprCap(vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, 0.0));
  return aprCap(length(v) * axTurned(v, m, cs.x, cs.y));
}
vec3 axLmul(vec3 a, vec3 b){ return aprCap(vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz)); }`;
const GL_NEARAXIS = GL_APR + GL_AXNEAR + `
vec3 mul(vec3 a, vec3 b){ return axLmul(a, b); }
vec3 pw(vec3 v, float n){ vec2 cs; vec3 m = axNear(v, vec3(0.0, 0.0, 1.0), cs); return axPw(v, m, cs, n); }
vec3 sqr(vec3 v){ vec2 cs; vec3 m = axNear(v, vec3(0.0, 0.0, 1.0), cs); return axSq(v, m, cs); }
vec3 cmap(vec3 c){ return c; }`;
// All axes, nearest to the last one. Carried by the point's own orbit: the axis of its last turn (the z-axis at
// the start) and the turn of the step under way. A neighbouring orbit takes the turn of the point's own step.
const GL_LASTAXIS = GL_APR + GL_AXNEAR + GL_CARRY + `
vec3 gLaH, gLaM;
vec2 gLaCs;
void carStart(){ gLaH = vec3(0.0, 0.0, 1.0); gLaM = vec3(0.0); gLaCs = vec2(1.0, 0.0); gCarI = 0; }
void carStep(vec3 z, vec3 c){
  if (gCarI != 0) return;
  gLaM = vec3(0.0); gLaCs = vec2(1.0, 0.0);
  if (carOrigin(z)) return;
  gLaM = axNear(z, gLaH, gLaCs);
  if (gLaM != vec3(0.0)) gLaH = gLaM;
}
void carFit(int i, float s){ }
vec3 mul(vec3 a, vec3 b){ return axLmul(a, b); }
vec3 pw(vec3 v, float n){ return axPw(v, gLaM, gLaCs, n); }
vec3 sqr(vec3 v){ return axSq(v, gLaM, gLaCs); }
vec3 cmap(vec3 c){ return c; }`;
// Parts: the moves and the grids of ptPow, ptTurn, ptMob, ptGrid, ptSquare and ptFoot in the JavaScript above.
const GL_PARTS = GL_APR + GL_MERC_PLAIN + `
vec2 ptPow(vec2 u, float n){
  if (n == 2.0) return cmul(u, u);
  float a = at2(u.y, u.x) * n;
  return aprPow(length(u), n) * vec2(cos(a), sin(a));
}
vec3 ptFlat(vec3 v, float n){ return aprCap(vec3(ptPow(v.xy, n), 0.0)); }
vec3 ptTurn(vec3 v, vec2 u, float n){
  vec2 b = n == 2.0 ? 2.0 * u : n * ptPow(u, n - 1.0);
  return aprCap(vec3(ptPow(u, n) + cmul(b, v.xy - u), length(b) * v.z));
}
vec3 ptMob(vec3 v, vec2 u, float n){
  if (abs(n - 1.0) < 1e-6) return v;
  float s = 2.0 / (n - 1.0);
  vec2 a = ptPow(u, n), g = n * s * s * cmul(a, u), q = v.xy - (1.0 + s) * u;
  float D = max(dot(q, q) + v.z * v.z, 1e-30);
  return aprCap(vec3((1.0 - n * s) * a - cmul(g, vec2(q.x, -q.y)) / D, length(g) * v.z / D));
}`;
const GL_PARTS_GRID = `
vec2 ptGrid(vec3 v, float n, float finer){
  float m = max(2.0, floor(abs(n) + 0.5)), phi = atan(abs(v.z), length(v.xy));
  if (phi < 2e-5) return v.xy;
  float a = 0.5 * PI * pow(m, -floor(log(0.5 * PI / phi) / log(m)) - 1.0 - finer);
  float rho = a * floor(log(length(v)) / a + 0.5), th = a * floor(at2(v.y, v.x) / a + 0.5);
  return exp(rho) * vec2(cos(th), sin(th));
}`;
// The four functions every approach defines, for a rule of parts: `move` is the GLSL expression that moves the
// point v, with the power n, when v is off the flat plane.
const glParts = move => `
vec3 ptPw(vec3 v, float n){ return v.z == 0.0 ? ptFlat(v, n) : ${move}; }
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return ptPw(a, n); }
vec3 sqr(vec3 a){ return ptPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
const GL_PARTSTURN = GL_PARTS + GL_PARTS_GRID + glParts('ptTurn(v, ptGrid(v, n, 0.0), n)');
// uA.x: how many more times the boxes are divided.
const GL_PARTSBEND = GL_PARTS + GL_PARTS_GRID + glParts('ptMob(v, ptGrid(v, n, clamp(floor(uA.x + 0.5), 0.0, 6.0)), n)');
const GL_PARTSSQUARE = GL_PARTS + `
vec2 ptSquare(vec3 v){
  float h = abs(v.z);
  if (h < 1e-5 * (length(v.xy) + 1e-5)) return v.xy;
  float s = exp2(floor(log2(h)));
  return s * (floor(v.xy / s) + 0.5);
}` + glParts('ptTurn(v, ptSquare(v), n)');
// Parts carried by the orbit (see CARRY.partsorbit). Carried by the point's own orbit: the flat point its moves are
// fitted at, and whether it has one yet.
const GL_PARTSORBIT = GL_PARTS + GL_CARRY + `
vec2 gPoU;
bool gPoOn;
void carStart(){ gPoU = vec2(0.0); gPoOn = false; gCarI = 0; }
void carStep(vec3 z, vec3 c){
  if (gCarI != 0 || carOrigin(z)) return;
  if (gPoOn) gPoU = ptPow(gPoU, uPow) + c.xy;
  else { gPoU = z.xy; gPoOn = true; }
}
void carFit(int i, float s){ }` + glParts('ptMob(v, gPoOn ? gPoU : v.xy, n)');
const GL_PARTSNONE = GL_PARTS + `
vec2 ptFoot(vec3 v){
  float r = length(v.xy), R = length(v);
  return r > 0.0 ? (R / r) * v.xy : vec2(R, 0.0);
}` + glParts('ptMob(v, ptFoot(v), n)');
// Wording helpers for the approach texts
const aprIs = (a, b) => Math.abs(a - b) < 1e-9;
const aprWhole = n => aprIs(n, Math.round(n));
const aprNum = x => String(+(+x).toFixed(2)).replace('-', '−');
const aprDeg = x => aprNum(x) + '°';
const aprSup = k => [...String(Math.round(k))].map(ch => (ch === '-' ? '⁻' : '⁰¹²³⁴⁵⁶⁷⁸⁹'[+ch])).join('');   // a whole number as a superscript
const aprWrap = deg => { const d = ((deg + 180) % 360 + 360) % 360 - 180; return aprIs(d, -180) ? 180 : d; };
const aprPlus = (x, unit) => (x ? (x < 0 ? ' − ' : ' + ') + aprNum(Math.abs(x)) + unit : '');   // "" or " + 20°"
const aprPole = n => (n < 0 ? ' The origin is sent to infinity.' : '');
// A fractional power cannot close up around the origin, here or in the plane: one of these sentences is added then.
const aprTear = (n, text) => (aprWhole(n) ? '' : text);
const APR_HALF = ' A power that is not a whole number also tears space along the half-plane y = 0, x < 0, the way zⁿ tears the plane along the negative x-axis.';
const APR_LINE = ' A power that is not a whole number also tears space along the negative x-axis, the way zⁿ tears the plane there.';
// is some value  target + 180°·k  strictly between a and b (all in degrees)?
function aprPasses(a, b, target) {
  const lo = (Math.min(a, b) - target) / 180, hi = (Math.max(a, b) - target) / 180;
  return Math.ceil(hi - 1e-9) - Math.floor(lo + 1e-9) > 1;
}
// the slice sentence for a rule that adds a turn of `deg` degrees to every power
function aprTurned(deg, n) {
  const back = aprWhole(n) && !aprIs(n, 1) ? ` For zⁿ + c that slice is the usual flat set turned by ${aprDeg(aprWrap(-deg / (n - 1)))}.` : '';
  return `The plane z = 0 follows complex arithmetic with one change: every power is also turned by ${aprDeg(deg)}.${back}`;
}
const aprMercTurn = p => aprWrap(p.turn || 0);   // the turn in effect, between −180° and 180°
const APR_INVERSION = 'At n = −1 the rule is a single sphere inversion with a flip, and inversions keep every shape.';
const APR_MIRROR = 'At n = −1 the rule is a single sphere inversion with a mirror, and inversions keep every shape.';
// the cells for n = 0, where a rule sends every point to the same place
const aprNone = () => ['no', 'Everything is crushed onto one point.'];
const aprConstant = () => ['ok', 'A constant.'];
// what the turn and longitude-phase dials do to the slice at z = 0
const APR_SLICE_TURNS = ' Away from 0 the slice at z = 0 is no longer the plain 2D picture: it is that picture turned (Mandelbrot) or a different set (Julia).';

// The headings of the Approach list, in the order they are shown. Every approach names one in `group`, and
// the list shows the approaches of a group in the order they stand in APPROACHES.
const APPROACH_GROUPS = [
  { id: 'inversions', title: 'Sphere inversions' },
  { id: 'fourone', title: 'Four points to one in one step' },
  { id: 'kleinian', title: 'Inversions by region (the road of Kučera’s paper)' },
  { id: 'quaternion', title: 'Quaternions' },
  { id: 'pillow', title: 'Doubling on a pillow grid' },
  { id: 'angles', title: 'Angle rules' },
  { id: 'other', title: 'Side by side' },
  { id: 'tried', title: 'Tried, and failed' },
  { id: 'custom', title: 'Your own' },
];
// The one-plane rule in words, shared by the entries built on it.
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
// Bulbs about the axis: which planes through the x-axis a turn multiplier k keeps exact. The wobble never disturbs them.
const axbExact = k => (k % 2 === 0 ? 0 : ((k % 4) + 4) % 4 === 1 ? 2 : 1);   // 0: none, 1: z = 0 only, 2: z = 0 and y = 0

// Texts of Quaternions 4D, Rotor square, Rotor square with a frame and Kleinian squaring
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
const KQ_TAG = 'Squaring rebuilt from sphere inversions, a different one in each region of the sphere of directions (a reading of the first construction in Kučera’s paper). Its slice at z = 0 is a cousin of the flat set, not the flat set.';
const KQ_NOTE = 'A reading of the first construction in Václav Kučera’s paper (Bridges 2019). The paper leaves out the details, so this is rebuilt from its text and may differ from what its author drew. Measured: the rule has no jump anywhere on the sphere of directions, and it keeps shapes inside each cap and outside the caps. On the equator it follows the pattern of zⁿ but not its numbers: at n = 2 it agrees with angle doubling in six directions, 60° apart, and is up to 17.6° off in between. So the slice at z = 0 is a cousin of the flat set: about 80% of the flat Mandelbrot set lies inside the slice, and about an eighth of the slice lies outside the flat set (for the Julia set of c = −1: about 62%, and about an eighth). A quarter of all directions, the two patches round the poles that no cap covers, are only mirrored. A product of two different points is taken from Sphere inversions, one plane.';
const KQ_ABOUT = 'Kučera’s paper replaces squaring by sphere inversions, a different one in each region of the sphere of directions, the way a Kleinian group is built from a few inversions. This entry rebuilds its first construction: for the square, three spheres stand round the equator, each crossing the unit sphere at right angles, and a direction inside one of them is inverted in it and then mirrored. What the pictures show: the Mandelbrot solid is one lumpy body with a spike, much like the solid of Sphere inversions, one plane, but with creases. The Julia set for c = −1 is a chain of bodies along the x-axis with small buds on them. The rabbit is one angular lump, and for a c off the plane z = 0 the set falls apart into shards. The slices at z = 0 are angular cousins of the flat sets: the same bodies in the same places, with straighter edges. Where it falls short: the slice is not the flat set, and the creases along the rims of the caps show on every surface.';
const KQ_ROUND = 'Circles on the sphere of directions stay circles inside each cap, and outside the caps. Along the rims of the caps the rule is creased.';
const KQ_CRUSH = 'Nothing but the origin is crushed. The sphere of directions is folded along the rims of the caps instead: the directions outside every cap come out as a mirror image (a quarter of all directions at n = 2).';
const KQ_SMOOTH = 'No jump was found (measured at n = 2, 3 and 4), but the rule is creased along the rim of every cap: inside a cap it is one sphere inversion with a mirror, outside the caps the mirror alone. A power that is not a whole number of 2 or more uses the caps of the nearest such power, so the picture jumps between whole powers.';
const KQ_SLICE = `The plane z = 0 lands on itself, but it does not follow complex arithmetic: the angle is multiplied with a wobble (${KQ_WOBBLE}). So the slice is a cousin of the flat set, not the flat set.`;
const KQ2_TAG = 'The same caps round two circles (a reading of the second construction in Kučera’s paper, its Figure 4). The slice at z = 0 is not the flat set, the number of buds follows the number of planes and not the power, and away from the x-axis it tears into shards.';
const KQ2_NOTE = 'A reading of the second construction in the paper: the caps of the entry above round the equator, and the same caps round the circle of the plane y = 0. A direction nearer the plane z = 0 uses the first family, one nearer the plane y = 0 the second. Measured: on the seam between them, the planes y = z and y = −z, the two families send one direction to places up to 180° apart (92° on average), so the rule jumps there. The jump does no harm only in a Julia set whose c lies on the x-axis. Everywhere else, the Mandelbrot solid included, it tears the solid. The paper gives the same limit: its construction is for c on the x-axis. The planes z = 0 and y = 0 both carry the cousin of the flat set that the entry above has in the plane z = 0.';
const KQ2_ABOUT = 'The second construction of Kučera’s paper, as far as its text lets it be rebuilt: the inversions of Kleinian squaring, one plane, used twice, once round the equator and once round the circle of the plane y = 0. What the pictures show: the Julia set for c = −1 is a chain of bodies along the x-axis with buds round two circles, above and below as well as left and right. That is the look of the entry Sphere inversions, two planes, with rougher, knobbly buds. With c on the x-axis at −1.75 the bodies thin to dust along the axis. For a c off the x-axis, and for the Mandelbrot solid, the picture is a mass of shards: the tear along the seam is copied all over the surface. Where it falls short: it is whole for c on the x-axis only, and its slices are cousins of the flat sets, not the flat sets.';
const KQ2_SMOOTH = 'Jumps across the planes y = z and y = −z, where the two families of caps meet (measured at n = 2: by up to 180°). It is creased along the rim of every cap as well.';
const KQ2_SLICE = `The planes z = 0 and y = 0 both land on themselves, but neither follows complex arithmetic: the angle is multiplied with a wobble (${KQ_WOBBLE}). So both slices are cousins of the flat set, not the flat set.`;

// Texts of Square pillow
const spGrid = n => clamp(Math.floor(Math.abs(n) + 0.5), 2, SP_MAXN);   // the whole power the grid is laid out for
const spOwn = n => aprWhole(n) && Math.abs(n) >= 2 && Math.abs(n) <= SP_MAXN;   // a power the grid is made for
const SP_TAG = 'Lay the directions on a square pillowcase grid and double both of its coordinates. The slice at z = 0 is the flat set and no tear was found, but at power 2 the solid is streaked and its bodies do not come apart. Power 3 looks better: buds on buds.';
const SP_NOTE = 'Measured at power 2. The plane z = 0 follows complex arithmetic exactly: the 2D view draws the same picture as for Sphere inversions, one plane, pixel for pixel (five pictures compared). No jump was found between close directions (400,000 pairs). The rule is lopsided above and below the plane z = 0, because the belt of the grid that carries that plane does not lie half way between the two seams, it is twice as far from the lower seam as from the upper one: a direction and its mirror image are sent to places 0.7 apart on average, on a sphere of radius 1. At power 3 the belt lies half way and the rule is mirror-symmetric (to 15 digits). Beside the plane z = 0 a small circle of directions stays nearly a circle. Away from it the stretch is uneven: for half of all directions at least 1.6 times as much one way as the other, and for about one in six more than 3 times. The skin of the 3D picture was compared with a plain test of the set along 567 rays per picture: for three Julia sets every place where a ray stopped lay within 0.05 of the set (about 11 pixels of the opening picture), and about 5 in 6 within 0.0125. For the Mandelbrot solid 3 of 223 lay further away than 0.05. The same test gives 0.025 at most for Sphere inversions, one plane, and more than 0.1 at 12 of 145 places for Pillow. This is not the entry Pillow under “Tried, and failed”: that one wraps a sheet of triangles and has corners in the plane z = 0, this one a square sheet with no corner and no fold in that plane. A product of two different points is taken from Sphere inversions, one plane.';
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

// Texts of Turning plane, away and along
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

// Texts of Wind, then square
const WS_ROUGH = 'The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says. The other two settings draw a spindle of fog round the solid: measured on seven views of the Julia sets for c = −1, the rabbit and the Siegel disc, between 21% and 99% of the places where a ray stopped had no point of the set within 8 pixels with “Exact”, between 75% and 99% with “One neighbour”, and at most 1% with “Rough”. Rough has a fault of its own: a ray can step over a sheet that is thinner than its step, so thin parts are left out of the 3D picture. For the rabbit 58 of 254 rays that meet the set stopped at nothing. With “Ray step, share of the distance estimate” lowered to 0.4 it was 15 of 254. The pictures described here were made with Iterations at 40: at 14 the bodies are still joined by short necks.';
const WS_TAG = 'Wind each point round the x-axis three times (at power 2), then square it by the one-plane rule, and turn nothing back. Three planes then carry the flat set for every c of the flat plane, and nothing tears. For c = −1 it gives separate bodies with buds in six directions, but their skin is ragged between the planes. Off the x-axis it falls short: the rabbit’s ears are thin plates and the Siegel disc is three sheets.';
const WS_NOTE = WS_ROUGH + ' Measured: a point with z exactly 0 gets exactly the answer of Sphere inversions, one plane, and the cut at z = 0 is the flat set (six Julia sets at the powers 2 to 5, 160,000 points each, tested against plain complex arithmetic: none differs). The 2D view draws the flat set, and the same picture as for Sphere inversions, one plane except along thin edges of the outline: of 604,262 pixels, 586 differ for c = −1 (all of them faintly), 4,015 for the rabbit (189 of them clearly) and 5,415 for the Siegel disc (667 clearly). At power 2 the six half-planes through the x-axis at 0°, 60°, 120°, 180°, 240° and 300° are sent into the plane z = 0 in one step (to 15 digits), and from there on a point follows complex squaring. So three planes through the x-axis, 60° apart, each show the flat set, turned about the x-axis, whether c lies on the x-axis or not: for the rabbit the cut by the plane at 120° is the flat rabbit point for point, and the cut at 60° is the flat rabbit turned over (129,600 points each, none differs). No jump was found: for 200,000 pairs of close points the gap between the two answers shrinks in step with their distance, at four distances from 0.001 down to 0.000001, at the powers 2 to 5. The rule gives the same answer mirrored above and below and mirrored front and back, the same answer for a point turned by 120° about the x-axis (to 15 digits), and the length of a point is squared exactly. So every Julia set of this rule looks the same after a third of a turn about the x-axis. A whole power n is wound n times when n is odd and n + 1 times when n is even: the powers 2 and 3 have six half-planes that land in the plane z = 0, the powers 4 and 5 have ten (measured). A product of two different points is taken from Sphere inversions, one plane.';
const WS_ABOUT = 'In Sphere inversions, two planes and in the two Turning plane entries, each plane that carries the flat set is squared inside itself. Here only the plane z = 0 is squared. Before the squaring every point is carried round the x-axis: its angle round that axis is multiplied by three, unevenly, at the angle’s own pace beside six half-planes 60° apart and five times as fast half way between them. The six half-planes land in the plane z = 0, and a point of them is from then on a point of the flat plane, where c lives. So they show the flat picture without the rule having to keep them, and that works for every c of the flat plane. What the pictures show for c = −1: a row of separate bodies along the x-axis, each with six buds round it, one in each of the six half-planes, and smaller buds on those. Cut across at the point where two bodies touch, nothing but that point is left (40 steps, a cut 0.2 wide). The bud at 60° is a body and not a plate: cut along the x-axis it is an oval 0.13 long and 0.12 across. Cut across the x-axis through the middle of the middle body, at x = 0, the outline between two buds is smooth down to a picture 0.12 wide (80 steps), but that place is special. Where it falls short for c = −1: a little to the side, at x = 0.2, the same stretch of outline is ragged, with thin needles standing off it (80 steps, a picture 0.3 wide). At x = −0.3 a dozen short thin spikes and loose specks stand round the body, and the bud at 60° has a fringe of about 200 loose specks. The 3D picture shows this as a streaked, grainy skin, bristly like a sea urchin when seen along the x-axis, where Sphere inversions, one plane is smooth. The sets for c = −0.75 and c = 0.25 are ribbed from end to end: cut across the x-axis, c = 0.25 has twelve lobes like a pumpkin and c = −0.75 six sharp ridges, with a hairy rim at x = −0.3. Where it falls short away from the x-axis: the bodies are thin there. Turn the flat rabbit 4° about the x-axis and only 52% of its points are still in the set, and at 15° only 19% (the same with 40 and with 80 steps). For c = −1 it is 91% at 4° and 91% at 30°. So the rabbit’s middle body is a body with six points, but its ears are plates lying in the three planes, with shredded rims, and the 3D picture shows a feathery mass and no separate bodies. The Siegel disc is thinner still and thins with every step: a quarter of a degree off its planes 79% of its points are in the set after 40 steps and 64% after 80. It is three sheets crossing on the x-axis, not a body. For c = i, a tree in the plane, the cuts show three flat trees and the 3D picture a thin dust. Whole powers: cut across the x-axis the outline repeats six times round the axis at the powers 2 and 3 and ten times at the powers 4 and 5 (for c = −1 at power 4: ten buds), so the count follows the power two powers at a time.';
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

// Texts of "Along once, then one plane" and "Pulled plane". crRough's `off` says what the picture shows for a c out
// of the flat plane.
const crRough = (rough, fine, off) => `The lab always draws this rule with “Distance estimate” at “Rough”, whatever that setting says. Measured on the Julia sets for c = −1, the rabbit, the Siegel disc and c = −0.75, which all lie in the flat plane, 1,728 lines of sight each, against the set worked point by point: with “Rough” no ray stopped where the set has no body, and ${rough}. ${fine} For a c out of the flat plane (the dial “c along z” away from 0) that does not hold, and the picture can show what is not there: ${off} The lab stops a ray at the places where orbits hold out longest, and Sphere inversions, one plane does the same for such a c (it stopped 244 of 1,200 rays for a c whose set is empty). The pictures described here were made with Iterations at 40.`;
const AO_ROUGH = crRough('of the lines that meet the set at most 4 of 323 were missed', 'With “Exact” up to 44% of the stops were at nothing, and with “One neighbour” up to 8%.',
  'with the rabbit’s c turned 10° about the x-axis it shows jagged shards, and with c = (−1, 0, 0.3) two flat flakes, though of 400,000 points tested each time none stayed for the 40 steps the picture asks for.');
const PP_ROUGH = crRough('of the lines that meet the set at most 1 was missed', 'With “One neighbour” up to 82% of the stops were at nothing, and with “Exact” up to 26%.',
  'with the rabbit’s c turned 10° about the x-axis it shows a smooth thin slab with buds along one edge, though of 400,000 points tested only 94 stayed for the 40 steps the picture asks for.');
const CR_SEVERAL = 'When the equation takes several powers in one step (as in z² + z³ + c), they all belong to that one step';
const CR_ONE = 'The measurements on this card look at one squaring, so for this entry they show the first squaring of an orbit only';
const CR_LEARN = ' The Learn tab follows the orbit: its first step shows a first squaring, and after “Next step” the moves are those of the squaring the orbit has come to.';
const CR_START = ' A power written into the start value (as in the start value c²) is taken before the orbit begins and does not count as a squaring';
const AO_TAG = 'The first squaring of every orbit is done by Turning plane, along, and every later one by Sphere inversions, one plane. For c = −1 the middle body keeps its buds in eight directions, and the rabbit comes apart into smooth separate bodies. But the bodies beside the middle one keep 6 buds where Turning plane, along has 16, each big bud carries 2 small buds instead of 16, two bodies of the rabbit float free, and the Mandelbrot solid is very nearly the one-plane solid, with thin wings standing off it that have no thickness.';
const AO_NOTE = AO_ROUGH + ' What an orbit carries here is a count of its squarings and nothing else, and every orbit starts its count afresh. A squaring of the exact origin does not count. So in a Mandelbrot picture, where the orbit starts at 0, the squaring done by Turning plane, along is the squaring of c. ' + CR_SEVERAL + ': in the first step each of them is taken by Turning plane, along.' + CR_START + ': it is taken by Sphere inversions, one plane. ' + CR_ONE + ', which is the squaring of Turning plane, along. Every later squaring is the one of Sphere inversions, one plane, and the card of that entry describes it.' + CR_LEARN + ' A product of two different points is taken from Sphere inversions, one plane.';
const AO_ABOUT = 'Turning plane, along squares every point about a plane of its own, at every step. That gives c = −1 its buds in eight directions, and it swells the rabbit into one lump. This entry does it once. The first squaring of an orbit is the one of Turning plane, along, and from the second squaring on the orbit follows Sphere inversions, one plane. So a point belongs to a Julia set of this entry exactly when its first step lands in the solid that Sphere inversions, one plane draws for the same c. Measured point by point, and seen in cuts: for c = −1 the middle body has eight buds round it (eight separate stretches of the set on circles round the x-axis through the buds). Close up the eight are not alike. The two in the plane y = 0 carry smaller buds on their sides, as in Turning plane, along. The two in the flat plane are bare on their sides, as in Sphere inversions, one plane. The four at 45° are plain lenses. The rabbit comes apart into smooth bodies, also off the flat plane, where Turning plane, along has one lump. Where it falls short: whatever needs a second step off the flat plane is lost. Counted on rings round the x-axis: the bodies to the left and right of the middle body of c = −1 keep 6 buds where Turning plane, along has 16, the rings further out keep 2, and each big bud of the middle body carries 2 small buds where Turning plane, along has 16. For c = −0.75 the bodies are fused into one mass. The rabbit is in three pieces: two of its bodies float free, one above and one below the rest. Each holds 7.2% of the volume and stands 0.11 away from the rest, the same on a coarse grid and on a fine one, so the gap is real. For a c out of the plane z = 0 it does no better than Sphere inversions, one plane: with the rabbit’s c turned 10° or more about the x-axis no point of the set was left. The picture does not show that emptiness. It shows jagged shards there, where no point was found that stays (the numbers are in the next paragraph), and shards are one of the things this search is trying to get rid of. The Mandelbrot solid has very nearly the body of the solid of Sphere inversions, one plane: of 2,000,000 points c tested, between 4 and 8 got a different answer. But the picture also shows thin curved wings standing off its left end, where Sphere inversions, one plane has nothing: in one picture 68 of 195 rays stopped on them. The wings are there, but they are films with no thickness. Followed along a line of sight into three of them, the orbit stays longer and longer the nearer the film (18 to 22 steps at the best of 20,000 places along a stretch 0.08 long, 39 to 57 steps when the search is narrowed to a stretch of 0.000000000003), and no place was found that stays for good. And it is not one rule: it is two rules and a count that says when to change from one to the other, which nothing in the flat rule asks for. Powers other than 2 have not been looked at for this entry.';
const AO_CARD = 'This card measures the first squaring of an orbit, which is the squaring of Turning plane, along. ';
const AO_LATER = ' Every later squaring is the one of Sphere inversions, one plane';
const aoFormula = n => 'First squaring of an orbit: ' + tpFormula(n, true) + ` Every later squaring: v${aprWhole(n) && n >= 2 ? aprSup(n) : 'ⁿ'} = P(v). The orbit carries a count of its squarings and nothing else.`;
const aoSlice = ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly in the first squaring and in every later one, so that slice is the flat set.');
const PP_TAG = 'Each orbit carries a plane through the x-axis. It starts as the flat page and is pulled toward c and toward every point of the orbit, and each point is squared by the one-plane rule about it. For c = −1 it gives round buds in four directions, and the rabbit and the Siegel disc are clean separate bodies. But the four directions fade as c leaves the x-axis, the rabbit is nearly the one-plane rabbit, thin loose flakes hover over the skin close up, and three numbers in the rule were set by hand.';
const PP_NOTE = PP_ROUGH + ' What an orbit carries here is a plane through the x-axis and a number that says how firmly it is held. Every orbit starts afresh with the flat page, held weakly. The three dials below are the three numbers of the rule that were set by hand. Nothing in the flat rule gives them, and what is written about this entry was measured with the dials where they start: 0.05, 0.7 and 16. A squaring of the exact origin pulls at nothing. So in a Mandelbrot picture, where the orbit starts at 0, the first pulls are those of the step that squares c. ' + CR_SEVERAL + ': the plane is pulled once, by c and by the point the step starts from, and every power of that step is taken about it.' + CR_START + ': it is taken about the flat page. ' + CR_ONE + ', taken with the c of the picture: in a Julia picture the c of the Julia dials, and in a Mandelbrot picture, where every point is its own c, the point that is squared. In that squaring the plane has been pulled once by c and once by the point.' + CR_LEARN + ' It takes its own c. A product of two different points is taken from Sphere inversions, one plane.';
const PP_HELP_HOLD = 'How firmly an orbit holds the flat page before anything has pulled at it. At 0 the first pull decides the plane alone. The larger the number, the longer the flat page holds, and the nearer the picture comes to Sphere inversions, one plane. Set by hand: 0.05.';
const PP_HELP_EASE = 'How a thing pulls. At 0 it pulls the plane straight toward the plane it lies in itself. At 1 a thing that lies close to the plane pulls toward the plane as it stands, and only a thing that stands square to the plane pulls toward its own. Set by hand: 0.7. Measured for the rabbit: with the third dial at 16, where it starts, 8% of the set is lost at 1. With the third dial at 1, 28% is lost at 1, and at 0.5 the bodies fuse where they meet.';
const PP_HELP_CPULL = 'c pulls at the plane before every squaring, and this is how many times its pull counts beside the pull of the point. At 0 c does not pull. A c on the x-axis never pulls, whatever this number is. Set by hand: 16. Measured for the rabbit: at 4 the bodies fuse where they meet.';
const PP_ABOUT = 'Sphere inversions, one plane squares every point about the flat page. Turning plane, along gives every point a plane of its own. Here the plane belongs to the orbit. Think of the planes through the x-axis as the pages of a book whose spine is the x-axis. Every orbit starts with the book open at the flat page, held weakly. Before each squaring two things pull at the page: first c, then the point that is about to be squared. A thing far from the x-axis pulls hard, and a thing on the x-axis does not pull at all. Each pulls toward the page it lies in itself, less directly the nearer that page is to the open one. The pulls add up and none is forgotten, so the page turns less and less as the orbit goes on. Then the point is squared by the one-plane rule about the page as it stands. Measured point by point, and seen in cuts: for c = −1 a row of separate bodies with round buds in four directions, two in the flat plane and two in the plane y = 0 (four separate stretches of the set on circles round the x-axis through the buds, 19° and 15° wide, where Turning plane, along has eight of 13°). The cut along the plane y = 0 looks like the flat picture. The rabbit and the Siegel disc are clean separate bodies in one piece, where Turning plane, along has a lump. Where it falls short: the four directions are there for c on the x-axis and close to it only. For c = −1 + 0.2i no bud is left in the plane y = 0 (the bodies still cross it), and for a c a little off the x-axis a ledge runs across the front of every body. The rabbit is nearly the rabbit of Sphere inversions, one plane (one point in eight of its inside differs), so its smaller bodies sit round the flat page only. Close up, thin loose flakes hover over the skin of c = −1 between the two rows of buds: in 336 of 720 directions tested there, and still there after 600 steps, where Sphere inversions, one plane has none. At 45° there is no bud, only a thin loose crescent. The Siegel disc loses 15% of its points between 30 and 200 steps before it settles. For a c that lies in neither of the two planes the set can vanish: with the rabbit’s c turned by 10°, 30° or 45° about the x-axis no point of it was left. The picture does not show that emptiness. For the turn by 10° it shows a smooth thin slab with buds along one edge, where next to no point stays (the numbers are in the next paragraph). A c that lies in the plane y = 0 is another matter: there the cut along that plane is the flat picture of the same c stood upright (measured for c = (−1, 0, 0.3), whose flat picture is a thin branching thread). The Mandelbrot solid shows the flat set in the plane z = 0 and, but for a few points, in the plane y = 0 (104 of 84,000 places differ), with smooth skin between the two and no buds there. Three numbers of the rule were set by hand, and they matter: see the three dials. Powers other than 2 have not been looked at for this entry.';
const PP_ROUND = 'About a plane that stands still the squaring keeps circles on the sphere as circles, as Sphere inversions, one plane does. But the plane is pulled by the very point that is squared, so two points side by side are squared about slightly different planes, and that squashes shapes (read off the rule; the numbers on this card are measured).';
const PP_CRUSH = 'Each squaring is the one-plane rule about the plane the orbit carries, and the one-plane rule crushes one line only: the line that stands square to its plane. Which line that is changes from orbit to orbit and from step to step.';
// The measurement in brackets holds for the power 2 with the first dial at 0.05, so it is shown there only. Where
// the lines lie is read off the rule and holds for every power and every setting of the dials.
const ppSmooth = (p, n) => {
  const hold = Math.max(0, ppDial(p, 'hold', 0.05)), measured = aprIs(n, 2) && aprIs(hold, 0.05);
  return 'Not one formula applied again and again: the plane a point is squared about depends on the whole orbit before it. And the plane has no direction where the pulls cancel what holds it. Beside such a place it swings by a quarter turn, so the rule jumps there. '
    + (hold > 0 ? 'In the first squaring, with c on the x-axis, that happens on two lines beside the x-axis: y = 0, z = ±' + aprNum(Math.sqrt(hold)) + ', the root of the first dial (read off the rule'
      + (measured ? '; measured with c = −1 at x = −0.8: two points 0.000000002 apart, one on either side of such a line, get answers 0.70 apart, which is as far apart as the answers are long' : '') + ').'
      : 'With the first dial at 0 nothing holds the plane before the first pull, so in the first squaring, with c on the x-axis, there is no such place off the x-axis (read off the rule); in later squarings there can be.')
    + (aprWhole(n) ? '' : APR_HALF);
};
const ppSlice = ok => (ok ? 'While c lies in the plane z = 0, neither c nor a point of that plane pulls the page out of it. So the plane z = 0 follows complex arithmetic exactly, and that slice is the flat set.'
  : 'The plane z = 0 does not follow complex arithmetic here: a c that lies out of that plane pulls the page out of it.');
const ppFormula = (p, n) => {
  const k = aprWhole(n) && n >= 2 ? aprSup(n) : 'ⁿ', hold = aprNum(ppDial(p, 'hold', 0.05)), ease = aprNum(ppDial(p, 'ease', 0.7)), cpull = aprNum(ppDial(p, 'cpull', 16));
  return `v${k} = Rot(θ)·P(Rot(−θ)·v)   with P the power ${aprNum(n)} of Sphere inversions, one plane, Rot(a) the turn about the x-axis by the angle a, and θ the turn of the plane that the orbit carries. The plane is kept as w = |w|·(cos 2θ, sin 2θ), and a fresh orbit starts with w = (${hold}, 0): the flat page, held weakly. Before each squaring w is pulled twice: by c with the weight ${cpull}, then by the point v with the weight 1. A pull by a thing with the coordinates (y, z) and the weight k: t = twice the angle of the thing round the x-axis, less 2θ, brought between −180° and 180°; a = 2θ + t − ${ease}·sin t; then w becomes w + k·(y² + z²)·(cos a, sin a). The numbers ${hold}, ${ease} and ${cpull} are the three dials. They were set by hand.`;
};

// Texts of Sphere inversions, soft mirror
const SM_NOTE = 'How it works: every point is first turned about the x-axis as if a mirror stood there, and then the one-plane rule is applied. The mirror is a half-plane through the x-axis. A point on the flat-plane side of it stays where it is. A point beyond it goes to its mirror image. With the mirror at 90° nothing lies beyond it: that is Sphere inversions, one plane. With the mirror at 45° and a sharp edge it is Sphere inversions, two planes. The mirror is what puts bodies off the flat plane, and its edge is what goes wrong. A sharp edge leaves a crease in every body the mirror cuts through. A soft edge takes the crease away and stretches whatever sits beside the mirror instead. No setting has neither.';
const SM_ABOUT = 'Sphere inversions with one plane, with two planes, and Turning plane, along, are one idea at three settings: the one-plane rule, and a mirror through the x-axis that brings points from beside the upright plane down beside the flat plane. Everything that sits off the flat plane is a mirror image. One plane has no mirror, so it has no such bodies. Two planes has a mirror with a sharp edge, so its bodies keep their shapes and carry a crease. Along has a mirror with a wide soft edge, so it has no crease and its bodies are stretched. This entry puts the place of the mirror and the softness of its edge on two dials. Like two planes it is whole only for c on the x-axis, such as the Basilica.';
const smSoft = p => +(p && p.soft) > 0;
// Texts of Soft mirrors, doubling
const MD_NOTE = 'How it works: Sphere inversions, soft mirror, with twice as many mirrors at each step. At the first squaring of an orbit two planes through the x-axis are brought onto the flat plane, as in that entry. At the second squaring four planes are, at the third eight, and so on. A point of the flat plane is never moved, so the flat picture is exact. Nothing is stretched to make the count grow: every piece is a mirror image. What an orbit carries is a count of its squarings and nothing else. A squaring of the exact origin does not count.';
const MD_ABOUT = 'In the flat picture each squaring doubles the number of places round the circle that land on one spot: 2, then 4, then 8. That doubling is what lines the edge of every body with smaller bodies at every size. Round the x-axis the soft mirror has no such doubling: two planes at every step, so the bodies stay on a few circles. This entry doubles the mirrors at each step instead. Bodies then sit between the planes as well: 4 round the middle body after one step, 8 more after two, and so on. The cost: far down, where the mirrors are many, a body is ringed by a string of small beads and comes close to the rings of the Quaternion square. The dial “Doubling stops after step” says how far down the doubling goes. Like the soft mirror it is whole only for c on the x-axis, such as the Basilica.';
const mdPlanes = p => Math.pow(2, clamp(Math.round(+p.stop || 1), 1, 12));
// Texts of Sphere inversions, either side
const EI_NOTE = 'How it works: at each of its first steps a point may be squared as it is (Sphere inversions, one plane), or mirrored first in the plane that stands at 45° round the x-axis and then squared. A point belongs to the solid if any run of such choices keeps it. So the solid is the one-plane solid with mirror images of itself added, and nothing is cut away. A point on the flat side of the mirror has no choice, so the flat picture is exact. No rounded edge is needed: a mirror image is only ever added, so the skin can dip where two pieces meet but can never stand up in a ridge.';
const EI_ABOUT = 'The other mirror entries replace what is behind the mirror with the mirror image. Where the skin crossed the mirror at a slant that left a crease, and rounding the mirror took the crease away at the price of a smeared band beside it. Here the mirror image is added to what is already there instead. Two pieces that are added to each other meet in a valley, the way a bulb meets the body it sits on, never in a ridge. The bulbs between the planes come out smeared flat all the same. A second cost is work: with a choice through step 3 the picture runs 8 orbits for every point. Like every mirror through the x-axis it is whole only when c is on the x-axis.';
// Texts of the three Four to one entries. All are written for the square; at another power they are the one-plane rule.
const F4_OTHER = 'This entry is written for the square only: at any other power it is Sphere inversions, one plane. ';
const F4_HOW_OTHER = ' Written for the square only: at any other power this entry is Sphere inversions, one plane. A product of two different points is taken from Sphere inversions, one plane.';
const f4One = () => APPROACHES.find(a => a.id === 'mercator');
const f4Else = ([state, text]) => [state, F4_OTHER + text];
const f4Slice = (ok, n, more) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' + (aprIs(n, 2) ? more : ''));
const F4P_TAG = 'One smooth step that sends four points to one and treats the upright plane y = 0 exactly as it treats the flat plane, with no fold and no mirror. For c = −1 both planes show the flat picture and every body has four buds round it. Between the planes the skin is ribbed and hairy, and for a c off the x-axis the solid comes out in shreds.';
const F4P_NOTE = 'How it works: the direction of a point is written as one complex number w, and the square of the point has the direction 2w / (1 − w⁴). That is one formula for the whole sphere of directions. Four directions share each answer, and a quarter rotation about the x-axis changes nothing, so the plane y = 0 is squared exactly as the plane z = 0 is. Two changes come first: the angle from the x-axis is changed so that it doubles exactly in both planes, and the place round the x-axis is drawn a little towards the planes, so that a small shape beside a plane keeps its shape.' + F4_HOW_OTHER;
const F4P_ABOUT = 'Sphere inversions, two planes gets its second plane from a fold, and Wind, then square from winding space round the x-axis. Here the step itself sends four points to one, the way squaring sends two points to one in the plane, and nothing is folded or wound first. The price: the directions round the negative x-axis go three times round the positive x-axis, and that uneven stretch builds up from step to step. What the pictures show for c = −1: the cut by the plane y = 0 is the flat picture, and the solid is a row of bodies along the x-axis, each with four buds. Where it falls short: between the two planes the skin is ribbed, swirled and hairy. For the rabbit, for c = i and for the Kokopelli the solid is not a body: it is shreds on a shell.';
const F4P_ROUND = 'In the planes z = 0 and y = 0 the rule is the complex square, which keeps shapes, and right beside them a small circle of directions stays a circle. Between them it comes out as an oval: for half of all directions less than 1.5 times as long as wide, for one in ten more than 4 times (measured). The longest ovals lie beside the negative x-axis, half way between the planes: five times as long as wide.';
const F4P_CRUSH = 'Nothing but the origin is sent to one point. At four directions the stretch falls to nothing, as it does at the origin of the flat plane: they stand on the diagonals between the two planes, 66° from the positive x-axis (measured). Nothing is folded over.';
const F4P_SMOOTH = 'One formula with no fold, no mirror and no seam. It is not a polynomial, and it has a corner on the negative x-axis: the directions round that axis go three times round the positive x-axis.';
const F4P_SLICE = ' The plane y = 0 follows it too. So the upright cut along the x-axis shows the flat picture as well, for the Mandelbrot solid and for every Julia set with c on the x-axis.';
const F4P_FORMULA = 'v² = |v|² · dir(2w / (1 − w⁴))   with w = tan(β/2)·e′ the direction of v written as a number. α is the angle of v from the positive x-axis and e = (y + iz)/ρ its place round that axis, ρ its distance from the axis. β is the angle with tan β + sin β = 2·tan α. e′ is e rotated by −q·sin 4ψ, with ψ the angle of e, q = (1 − 1/K)/4 and K = 2(1 − cos β + cos² β) / √(sin² β·(1 + cos β)² + 4·cos² β). dir turns a number back into a direction: its angle from the positive x-axis is 2·atan |w|, and its place round the axis is the angle of w.';
const F4C_TAG = 'One smooth step that sends four points to one: a cap round each end of the z-axis is flipped over onto the far half of the sphere of directions. The same above and below the flat plane, with no fold and no mirror. Sets like trees (c = i, the Kokopelli) become trees with branches in every direction. The set for c = −1 comes out as one lump.';
const F4C_NOTE = 'How it works: the direction of a point is written as one complex number ζ, with the flat circle at |ζ| = 1, and the square of the point has the direction (ζ³ − a) / (ζ·(1 − a·ζ³)). With a = 0 that is ζ², which is Sphere inversions, one plane. With a above 0 a cap round each end of the z-axis is flipped over onto the other half of the sphere, and four directions share each answer. The dial sets the size of the caps. One change comes first: the angle round the z-axis is changed so that it doubles exactly in the flat plane, and the height beside the plane with it, so that a small shape there keeps its shape. That change fades away from the plane.' + F4_HOW_OTHER;
const F4C_HELP = 'How far from each end of the z-axis a cap reaches. 0: no caps, and the entry is Sphere inversions, one plane. 30: the edge of a cap is half as long as the flat circle.';
const F4C_ABOUT = 'Sphere inversions, one plane sends two directions to one, and its bodies bud round the flat plane only. Here four directions go to one: the two more come from flipping a cap round each end of the z-axis over onto the far half of the sphere. The rule is the same above and below the flat plane, and nothing is folded. What the pictures show: for c = i and for the Kokopelli the flat tree becomes a tree in space, with branches in every direction. The rabbit is one bushy piece with lobes off the flat plane. Where it falls short: the set for c = −1 is one lump and not a row of bodies, and every skin is rough and spiky. Smaller caps do not cure the lump: with caps of 8° and of 17° big bodies still stand above and below its left side.';
const F4C_ROUND = 'In the plane z = 0 the rule is the complex square, which keeps shapes, and right beside the plane a small circle of directions stays a circle. Further off it comes out as an oval: with caps of 30° less than 1.5 times as long as wide for half of all directions, and more than 3 times for one in ten (measured).';
const f4cCrush = p => 'Nothing but the origin is sent to one point. At six directions the stretch falls to nothing, as it does at the origin of the flat plane: at 60°, 180° and 300° round the z-axis, the same distance above and below the flat plane' + (aprIs(+p.cap, 30) ? ' (14° with caps of 30°, measured)' : '') + '. Nothing is folded over.';
const F4C_SMOOTH = 'One formula with no fold, no mirror and no seam. It is not a polynomial.';
const f4cFormula = p => {
  const cap = clamp(+p.cap || 0, 0, F4_CAP_MOST);
  return `v² = |v|² · dir((ζ³ − a) / (ζ·(1 − a·ζ³)))   with ζ = (X + iY)/(1 − Z) the direction (X, Y, Z) of v written as a number, and a = tan(${aprDeg(cap / 2)}) = ${aprNum(Math.tan(0.5 * aprRad(cap)))}, half the size of a cap. Before that the angle θ of v round the z-axis is moved towards the angle B with 2B + 2·atan2(a·sin 3B, 1 − a·cos 3B) = 2θ, and its height m on a Mercator map is multiplied towards dB/dθ, both by the share exp(−(m/${F4_BAND})²). dir turns a number back into a direction.`;
};
const F4K_TAG = 'The step of Four to one, caps flipped over, with the size and the place of its caps taken from c: every c has its own squaring step. The Basilica is a row of bodies with one more above and one below its middle body, and the Dendrite and the Kokopelli are trees in space. A c below the x-axis does not give the mirror image of the set for the c above it but a lump, and the rotation of c was fitted by hand.';
const F4K_NOTE = 'How it works: the squaring step of Four to one, caps flipped over, whose number a set the size of the caps. Here a is taken from c: the flat part of c, rotated about the z-axis by the second dial and scaled by the first. The length of a is the size of the caps, and its angle rotates the caps’ six pinched directions about the z-axis. A c at the middle has no caps, which is Sphere inversions, one plane. No cap grows past 51°.' + F4_HOW_OTHER;
const F4K_HELP_CAP = 'How far from each end of the z-axis a cap reaches for a c at the distance 1 from the middle. The caps grow with that distance, up to 51°. 0: no caps, and the entry is Sphere inversions, one plane.';
const F4K_HELP_ROT = 'The caps are placed by c after it has been rotated about the z-axis by this angle. The pinched directions rotate by a third of it, so 360 puts them where 0 does. −90 was fitted by hand to the Basilica and the Dendrite: nothing in the flat rule gives it. At +90 a c below the x-axis gets the mirror image of what the c above it gets at −90.';
const F4K_ABOUT = 'Four to one, caps flipped over draws the trees well and the Basilica as one lump. The lump stands where one of the six pinched directions lies over a body, and those directions can be rotated about the z-axis without losing the flat picture. Here c rotates them and sets the size of the caps. What the pictures show: the Basilica and San Marco are a row of bodies along the x-axis with one more body above the middle one and one below it. The Douady rabbit is one piece with bodies in several directions, and the Dendrite and the Kokopelli are trees in space. Where it falls short: the −90° was fitted by hand to two sets. With it a c on the x-axis gets a step that is not its own mirror image, so the two extra bodies of the Basilica lean to the same side of the x-axis. A c below the x-axis does not get the mirror image of the set for the c above it: the rabbit and the Dendrite mirrored in the x-axis come out as lumps, and the Mandelbrot solid is lopsided. The Airplane is dust, and every skin is rough and striped.';
const F4K_ROUND = 'In the plane z = 0 the rule is the complex square, which keeps shapes, and right beside the plane a small circle of directions stays a circle. Further off it comes out as an oval, longer the larger the caps are, so the further c lies from the middle.';
const F4K_CRUSH = 'Nothing but the origin is sent to one point. At six directions the stretch falls to nothing, as it does at the origin of the flat plane: three round the z-axis, a third of a rotation apart, the same distance above and below the flat plane. c rotates them about the z-axis by a third of its own angle. Nothing is folded over.';
const F4K_SMOOTH = 'One formula with no fold, no mirror and no seam. It is not a polynomial, and c stands inside the squaring step as well as after it.';
const f4kFormula = p => {
  const cap = smDial(p, 'cap', F4K_CAP, 0, F4K_CAP_MOST), rot = smDial(p, 'rot', F4K_ROT, -360, 360);
  return `v² = |v|² · dir((ζ³ − a) / (ζ·(1 − ā·ζ³)))   with ζ = (X + iY)/(1 − Z) the direction (X, Y, Z) of v written as a number. a = tan(${aprDeg(cap / 2)}) · c′ = ${aprNum(Math.tan(0.5 * aprRad(cap)))} · c′, with c′ the flat part of c rotated by ${aprDeg(rot)} about the z-axis, and a no longer than ${aprNum(F4K_A_MOST)}. ā is a mirrored in the x-axis. Before that the angle θ of v round the z-axis is moved towards the angle B that the step sends to 2θ, and its height m on a Mercator map is multiplied towards dB/dθ, both by the share exp(−(m/${F4_BAND})²). dir turns a number back into a direction.`;
};
// Texts of Blended mirrors, doubling
const MB_NOTE = 'How it works: the mirrors of Soft mirrors, doubling, but kept sharp and not bent. Close to a mirror a point could be squared from two places: where the mirror puts it, or the mirror image of that place. Within the blend width the picture works out both and cross-fades between them, half and half on the mirror itself. That takes the crease away without bending anything, so nothing is smeared. A bud that sits right on a mirror does not come through whole: the cross-fade puts a smooth bubble round it. This is done at the first three steps of an orbit; later mirrors are sharp. A point of the flat plane is never moved, so the flat picture is exact.';
const MB_ABOUT = 'A sharp mirror leaves a crease where the skin crosses it at a slant. Soft mirrors, doubling takes the crease away by rounding the mirror, and the rounding smears whatever sits beside the mirror round the x-axis: the striped ovals. Here the mirror stays sharp and the two sides are cross-faded instead. The cost: a bead that sits beside a mirror, but not on it, is lower than it would be, down to half its height right at the mirror. Close to a mirror the picture runs two orbits for a point, or more where blend widths of several steps meet, so it is slower there. Like every mirror through the x-axis it is whole only when c is on the x-axis.';
// Texts of Even pillow
const EP_NOTE = 'How it works: the direction of a point is read off a square grid that is wrapped round the sphere like a pillowcase, and both grid numbers are multiplied by the power. One grid number is the angle round the circle z = 0, so the flat picture is exact. The other measures how far the direction is from that circle, and it is doubled the same way, above and below alike. There is no mirror and no rounded edge anywhere. The grid is laid at an even speed along the circle z = 0 and along the circle x = 0, and it is squeezed only at its four corners, the directions (±1, 0, ±1). A product of two different points is taken from Sphere inversions, one plane.';
const EP_ABOUT = 'Square pillow uses the same idea with a grid that is lopsided above and below the flat plane and unevenly stretched, and its picture is streaked. This grid is the same above and below and nearly even. The price at the power 2, and at every even power: along two short arcs through the directions straight up and straight down the rule jumps, and the two sides of the jump are mirror images of each other, left to right. A Julia set with c on the x-axis is its own mirror image, so there the jump does not show. For other c it shows as a tear. At the odd powers, 3 and 5, there is no jump at all and the rule is whole for every c.';
const epOdd = n => aprWhole(n) && Math.abs(Math.round(n)) % 2 === 1;
// Texts of Quaternion square, axis by step
const TS_TAG = 'Tried: the quaternion square with the axis its angle is measured from turned on at every step of an orbit, so that no direction is the one left out at every step. Failed: the rings do break up, but into one lumpy body with a swirled skin and no smaller bodies on it.';
const TS_NOTE = 'How it works: the quaternion square leaves one direction alone at every point, the spin round the axis its angle is measured from. That is what turns every shape of the flat picture into a ring. Here that axis moves on at each step of an orbit, inside the plane z = 0, so the direction left alone is a different one each time. Each step is turned back the way Quaternion square, twisted does it, which keeps the plane z = 0 exact at every step.';
const TS_ABOUT = 'The thought behind it: a ring shows where the same direction is left out step after step, so changing that direction from step to step might keep the losses from piling up. It does break the rings. But a single step of the quaternion square already crushes a whole plane flat, and a later step cannot give back what an earlier one has flattened. So the solid is smooth sheets and swirls, as in Quaternion square, twisted, and not bodies upon bodies. With the turn at 0 this is Quaternion square, twisted. With the turn at 180 the Basilica is made of rings again.';
// Texts of All axes, nearest to upright and All axes, nearest to the last one
const axFormula = n => (aprIs(n, 2) ? 'v² = |v| · T(v)' : `vⁿ = |v|ⁿ⁻¹ · Tⁿ⁻¹(v)   with n = ${aprNum(n)}`)
  + '   where T is a turn that takes the x-axis onto the direction of v. Its axis can be any direction as far from the x-axis as from v, and T is the one whose axis is nearest to a direction h.';
const NA_TAG = 'Tried: of all the turns that carry the x-axis onto a point, take the one whose axis is nearest to upright, and do it twice. Failed: thin curved sheets and splinters, with no bodies.';
const NA_NOTE = 'How it works: squaring a point of the flat picture is doing a turn twice, the turn that carries the x-axis onto the point. In space that is not one turn. Its axis may be any direction that is as far from the x-axis as from the point, and those directions make a full circle. The quaternion square takes the shortest of these turns. This entry takes the one whose axis is nearest to the z-axis, the axis that every turn of the flat picture is about. For a point of the flat plane that is the z-axis itself, so the flat picture is exact.';
const NA_ABOUT = 'Doing all of those turns at once gives a ring of answers round the point’s own direction. Their average is the point’s own direction, which is no turn at all. Keeping every one of them treats all directions round the x-axis alike, so for a c on the x-axis, the Basilica among them, it can only draw rings. So one turn has to be picked, and something has to pick it. Here it is the one direction the flat picture supplies besides the x-axis: the axis its own turns are about. The price shows on the plane y = 0. For a point there the nearest axis is the direction halfway between the x-axis and the point, the turn is a half turn, and doing it twice puts the point back on the x-axis. That whole plane is crushed onto a line, and the space beside it is pulled out into threads. Rotor square with a frame picks by a different test, the turn that moves the upright axis least, and tears at the z-axis instead. Some such flaw is certain: a turn cannot be chosen for every direction without a jump or a pinch somewhere, for the same reason that a hairy ball cannot be combed flat.';
const NA_ROUND = 'Near the flat plane and away from the plane y = 0 a tiny ball stays nearly round. Higher up it is squashed, and beside the plane y = 0 it is pulled out into a thread, more so the closer to the positive x-axis: about 200 times as long as it is wide at 20° above that axis.';
const NA_HALF = 'For a point of the plane y = 0 the turn is a half turn about the direction halfway between the x-axis and the point.';
const naCrush = n => (!aprWhole(n) ? ['part', NA_HALF + ' At this power that swings the point out of the plane.']
  : Math.abs(Math.round(n)) % 2 ? ['part', NA_HALF + ' An even number of half turns is no turn, so at an odd power such a point keeps its direction: in that plane the angle is not multiplied at all.']
  : ['no', NA_HALF + ' An odd number of half turns puts the point on the positive x-axis, so the whole plane y = 0 is crushed onto that line.']);
const NA_SMOOTH = 'One formula with no jump, but not a smooth one: beside the plane y = 0 it stretches without limit towards the positive x-axis, and on that axis it pinches.';
const LA_TAG = 'Tried: the same choice among all turns, but nearest to the axis the orbit’s last turn was about, so that an orbit keeps turning the way it was turning. Failed: sheets and splinters again, and the Dendrite falls to dust.';
const LA_NOTE = 'How it works: as in All axes, nearest to upright, a step is one of the turns that carry the x-axis onto the point, done twice. Here the turn picked is the one whose axis is nearest to the axis of the step before, and nearest to the z-axis at the first step. An orbit that starts in the flat plane turns about the z-axis at every step, so the flat picture is exact.';
const LA_ABOUT = 'The thought behind it: let the orbit itself pick the axis, with no direction chosen from outside after the start, the way a spinning top keeps its axis. The orbit then carries a memory, and two orbits that land on the same spot may go on differently. It does not help. A step still crushes a sheet of points onto a line, as in All axes, nearest to upright, only a different sheet for each orbit: the plane through the x-axis and the axis the orbit carries. The solid comes apart into more splinters, not fewer.';
const LA_SMOOTH = 'What a step does depends on the axis the orbit has picked up, so an orbit is not one formula applied again and again. Each step stretches without limit beside the sheet it crushes.';
// Parts: the wording shared by the entries whose rule moves each part of space by a move that keeps every shape
const PT_HEAD = 'A single smooth formula that squares has to stretch somewhere. Here space is cut into parts instead, and each part is moved as a whole by a move that keeps every shape. Such a move can agree with the flat rule at one flat point only, the point under the middle of the part, so the parts have to get smaller towards the flat plane, without end. ';
const PT_GRID = ' How the boxes lie: a point is read by three numbers, its distance from the middle, which way it lies round the upright axis, and how steeply it stands above the flat plane. At the power 2 the points steeper than 45° make the top layer, with eight boxes round the axis. From 22.5° to 45° is the next layer, with boxes half as wide, and so on down: each layer is half as steep as the one above it, and its boxes are half as wide. Squaring carries the point under the middle of a box onto the point under the middle of a box one layer up. At another whole power n the top layer is the points steeper than 90°/n, and layers and boxes shrink n times at each step down.';
const PT_FLAT = ' A point of the flat plane takes the flat rule itself.';
const PT_GAPS = ' After the move the parts overlap in some places and leave gaps in others.';
const PT_NEAREST = ' A power that is not a whole number takes the grid of the nearest whole number.';
const PT_STAYS = 'At n = 1 every point stays where it is.';
const ptKept = n => (n < 0 ? 'Nothing is crushed' : 'Nothing but the origin is crushed');
const ptSlice = ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'A point of the plane z = 0 takes the complex power itself, and the parts shrink to nothing towards that plane, so that slice is the flat set.');
const ptGridWords = (n, finer) => {
  const m = Math.max(2, Math.floor(Math.abs(n) + 0.5));
  return ` The parts: for a point whose elevation above the plane z = 0 lies between 90°/${m}ʲ and 90°/${m}ʲ⁻¹, take a = 90°/${m}ʲ${finer ? '⁺' + aprSup(finer) : ''} in radians. Then u has the length e^ρ and the longitude θ, with ρ and θ the whole multiples of a nearest to log|v| and to the longitude of v.`;
};
const ptTurnFormula = n => `In each part: (z, h) → (uⁿ + n·uⁿ⁻¹·(z − u), n·|u|ⁿ⁻¹·h)   with n = ${aprNum(n)}, z = x + iy the flat part of the point, h its height, and u the flat point under the middle of its part.`;
const ptMobFormula = (n, lead) => (aprIs(n, 1) ? PT_STAYS
  : `${lead}: (z, h) → ((1 − n·s)·uⁿ − g·conj(z − p) / D, |g|·h / D)   with n = ${aprNum(n)}, s = 2/(n − 1), p = (1 + s)·u, g = n·s²·uⁿ⁺¹ and D = |z − p|² + h²; z = x + iy is the flat part of the point and h its height.`);
// Parts of no size: the elevation of the cone that lands on the upright axis, in degrees, or null when there is none
const ptCone = n => (Math.abs(n) > 1 + 1e-9 ? Math.acos((n * n - 1) / (n * n + 1)) * 180 / PI : null);
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
    crush: (p, n) => {
      if (aprIs(n, 0)) return aprNone();
      const a = Math.abs(n);
      if (aprIs(a, 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion. The origin is sent to infinity.' : 'Crushes nothing: at n = 1 every point stays where it is.'];
      if (a < 1) return ['part', 'Crushes nothing at this power, but the stretch has no limit beside the z-axis.' + aprPole(n)];
      return ['part', 'Crushes the z-axis only: a line where the plane has a point.' + aprPole(n)];
    },
    smooth: (p, n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'Smooth for whole powers only.' + aprTear(n, APR_HALF)];
      return ['part', n < 0 ? 'Smooth everywhere except the origin, which is a pole.' : 'Smooth everywhere except the origin. It needs |v|, so it is not a polynomial.'];
    },
    slice: (ok, p, n) => {
      if (p.lift) return APR_LIFTED;
      const turn = aprMercTurn(p);
      if (turn) return aprTurned(turn, n);
      return !ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.';
    },
  },
  {
    // The fold sends the half y > 0 and the half y < 0 of space to opposite sides, so the rule jumps across the
    // plane y = 0 (see foldk).
    id: 'fold', name: 'Sphere inversions, two planes', group: 'inversions', glsl: GL_FOLD, axis: () => [1, 0, 0],
    tag: 'Fold space like a fan first, so that two planes carry the flat set.',
    params: [
      { type: 'dial', key: 'planes', label: 'Planes', min: 2, max: 8, step: 1, def: 2, int: true, xmax: 16, xhi: 64 },
      { type: 'note', text: 'An attempt to copy Figure 4 in Václav Kučera’s paper (Bridges 2019), with beads around two circles. It looks right for a Julia set whose c lies on the x-axis, such as the Basilica. Everywhere else, the Mandelbrot solid included, the rule jumps on the seam of its fold, which tears the solid. The count is a free choice: p planes give 2p fins around the x-axis, whatever the power is. There is no Turn dial here: with a fold a turn tears the solid into sheets.' },
      APR_LIFT,
    ],
    formula: (p, n) => aprMercFormula(n) + ` Before that, the nearest of ${p.planes} planes through the x-axis is folded onto the xy-plane.` + aprMercAfter(0, p.lift),
    about: 'The one-plane rule with a fold in front of it. Space is folded around the x-axis like a fan, until the nearest of the chosen planes lies on the xy-plane, and then the one-plane rule is applied. With two planes, the planes z = 0 and y = 0 both carry the flat set. This follows the second construction in Kučera’s paper, whose third map is the second one turned by 90° about the x-axis. The paper reports that construction for c on the x-axis only, and that is where this rule is whole too.',
    roundNote: (p, n) => (aprIs(n, -1) && !p.lift ? 'At n = −1 each piece is a sphere inversion with a flip, which keeps every shape. The folds between the pieces still leave creases.' : APR_CIRCLES),
    crush: (p, n) => (aprIs(n, 0) ? aprNone()
      : ['part', (n > 1 ? 'Nothing but the origin is crushed.' : 'Nothing is crushed.') + ' Space is creased where the folds meet instead.' + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant()
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
    crush: (p, n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the x-axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane x = 0.` : '') + aprPole(n)];
    },
    smooth: (p, n) => {
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
    params: [
      { type: 'dial', key: 'tilt', label: 'Tilt of the axis, degrees', min: -180, max: 180, step: 1, def: 40, lo: -360, hi: 360, animate: true, help: 'At 0 this is the plain quaternion square, the entry above, and the solid is made of rings. Away from 0 the rings break up into one body with tunnels. At 180 it is the mirror twin of the quaternion square for an even power, and the quaternion square itself for an odd one. At 90 and −90 the Mandelbrot solid is one fat body with spikes. It ends at every tilt: nothing further than 2 from the centre belongs to it. A tilt with a minus sign gives the mirror image of that solid, with y and −y swapped. For whole powers the plane z = 0 is exact at every tilt.' },
      { type: 'note', text: 'A rule for all of space with no seam: for whole positive powers it is built from plain multiplying and adding. One plane is built into it all the same: the plane z = 0 is exact, and at power 2 the plane y = 0 is not, unless the tilt is 0. In the close-up pictures its skin is smooth sheets and folds, with no fine bumps. The fine detail of the flat set is there where the solid meets the plane z = 0.' },
    ],
    formula: (p, n) => (aprIs(n, 2) ? `v² = ((x + iy)² − z²·e^(−2it), 2z·(x cos t − y sin t))   with t = ${aprDeg(p.tilt)}, and the first two coordinates written as one complex number. At t = 0 it is the quaternion square (x² − y² − z², 2xy, 2xz).`
      : `vⁿ = turn(−n·t) · qⁿ(turn(t) · v)   with t = ${aprDeg(p.tilt)}, qⁿ the quaternion power and turn a turn about the z-axis.`),
    about: 'Squaring multiplies a quaternion by itself. Here the second copy is twisted first: a quaternion has four directions, two of them outside the flat plane, and in the second copy those two are turned together, in their own plane, by twice the tilt. What that leaves in 3D is the quaternion square with its angle measured from an axis tilted inside the plane z = 0, and the result turned back. In the plane z = 0 the two turns cancel, so the slice is the flat set at every tilt. A Julia set whose c lies in that plane is a true slice of the 4D set. A Mandelbrot solid needs a c with a height, and adding it as a 3D point is this page’s own choice.',
    roundNote: () => 'The squash is in the spin direction around the tilted axis.',
    crush: (p, n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the tilted axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane through the origin at right angles to the tilted axis.` : '') + aprPole(n)];
    },
    smooth: (p, n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A polynomial (built from plain multiplying and adding) for whole positive powers only. A power that is not a whole number also tears space along a line, the way zⁿ tears the plane along the negative x-axis.'];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial: built from plain multiplying and adding.'];
    },
    // A power that is not whole tears the plane along the negative side of the tilted axis, where the plain
    // complex power tears it along the negative x-axis. So the two differ in the wedge between those two rays.
    slice: (ok, p, n) => (ok ? 'The plane z = 0 follows complex arithmetic exactly, at every tilt.'
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
    crush: (p, n) => {
      if (aprIs(n, 0)) return aprNone();
      if (!aprPasses((p.lat || 0) - 90 * n, (p.lat || 0) + 90 * n, 90)) return ['ok', (n < 0 ? 'Crushes nothing at these settings.' : 'Crushes nothing but the origin at these settings.') + aprPole(n)];
      return ['no', `Crushes the cones where n times the latitude${p.lat ? ', plus the phase,' : ''} reaches ±90°, ±270° and so on` + (aprIs(Math.abs(n), 2) && !p.lat ? ' (latitude ±45° here).' : '.') + aprPole(n)];
    },
    smooth: (p, n) => {
      if (aprIs(n, 0)) return aprConstant();
      const torn = Math.abs(Math.cos(n * PI / 2 + aprRad(p.lat))) > 1e-6, even = aprWhole(n / 2) && !p.lat;
      return ['no', (torn ? `Torn along the z-axis: directions next to a pole are thrown all the way around ${even ? 'the equator' : 'a circle of latitude'}.`
        : 'Has a crease along the z-axis, where the longitude has nothing to be measured from.') + aprTear(n, APR_HALF)];
    },
    slice: (ok, p, n) => {
      const lat = aprWrap(p.lat || 0), flip = aprIs(Math.abs(lat), 180), turn = aprWrap((p.lon || 0) + (flip ? 180 : 0));
      if (lat && !flip) return 'With a latitude phase the plane z = 0 lands on a cone, so no flat slice follows complex arithmetic. Set that phase to 0 to get the flat set back.';
      if (turn) return aprTurned(turn, n);
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
    about: 'White and Nylander’s formula as most renders use it, usually at n = 8. It is here as a rendering benchmark. With every dial at its starting value its z = 0 slice is not the flat set: for even n that whole plane is thrown onto the z-axis. A θ phase of (1 − n) × 90° turns it into the Mandelbulb above.',
    roundNote: (p, n) => {
      if (aprIs(n, -1) && !p.theta) return APR_MIRROR;
      const torn = Math.abs(Math.sin(aprRad(p.theta))) > 1e-6 || Math.abs(Math.sin(n * PI + aprRad(p.theta))) > 1e-6;
      return torn ? 'Beside the z-axis the stretch has no limit, and on cones around the axis directions are crushed.' : 'Stretched up to |n| times too far beside the z-axis, crushed on cones around it.';
    },
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : aprPasses(p.theta || 0, (p.theta || 0) + 180 * n, 0)
      ? ['no', `Crushes every direction whose angle from the z-axis, times n${p.theta ? ' plus the phase' : ''}, is a multiple of 180°.` + aprPole(n)]
      : ['ok', (n < 0 ? 'Crushes nothing at these settings.' : 'Crushes nothing but the origin at these settings.') + aprPole(n)]),
    smooth: (p, n) => {
      if (aprIs(n, 0)) return aprConstant();
      const torn = Math.abs(Math.sin(aprRad(p.theta))) > 1e-6 || Math.abs(Math.sin(n * PI + aprRad(p.theta))) > 1e-6;
      return ['no', (torn ? 'Torn along the z-axis: directions next to a pole are thrown all the way around a circle.'
        : 'Has a crease along the whole z-axis, where the angle around it has nothing to be measured from.') + aprTear(n, APR_HALF)];
    },
    slice: (ok, p, n) => {
      const T = n * PI / 2 + aprRad(p.theta), fix = aprWrap((1 - n) * 90);
      if (Math.abs(Math.cos(T)) > 1e-6) {
        return `No. This formula starts out without the flat set at z = 0. Setting the θ phase to ${aprDeg(fix)} would put it back: that turns this formula into the Mandelbulb above.`;
      }
      const turn = aprWrap((p.phi || 0) + (Math.sin(T) < 0 ? 180 : 0));
      if (turn) return aprTurned(turn, n);
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
    crush: (p, n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (aprIs(a, 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion with a mirror. The origin is sent to infinity.' : 'Crushes nothing: at n = 1 every point stays where it is.'];
      if (a < 1) return ['part', 'Crushes nothing at this power, but the stretch has no limit at the plane z = 0 and the z-axis.' + aprPole(n)];
      return ['no', 'Crushes the plane z = 0 and the z-axis.' + aprPole(n)];
    },
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant()
      : !aprWhole(n) ? ['no', 'A polynomial for whole positive powers only. Otherwise the complex factor is torn along the half-plane y = 0, x < 0, and below the plane the real factor keeps only the real part of zⁿ.']
      : n < 0 ? ['part', 'One polynomial divided by another: smooth everywhere except the origin, which is sent to infinity.'] : ['ok', 'A polynomial.']),
    slice: (ok, p, n) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : n < 0 ? 'The plane z = 0 follows complex arithmetic exactly. Because a negative power ends with an inversion, the slices at other heights are not copies of it.'
      : 'The plane z = 0 follows complex arithmetic exactly. So does every level slice of the prism.'),
  },
  // The next three entries are rules that failed (group 'tried'; three more end the list). Each says what it was
  // tried for and why it fails: in short in `tag` (the line under the name), in full in `about` (the paragraph
  // under the formula). How the rule works is the note above its dials.
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
    about: 'Tried for: the look of Figure 4 in Kučera’s paper, bodies with beads, without the tear of Sphere inversions, two planes. Each plane keeps the one-plane rule, and between two planes the two answers are blended smoothly, so nothing jumps. Why it fails: the pictures. The Julia set for c = −1 comes out as one swollen mass with ridges where the planes cross, not a row of bodies with beads, and the Mandelbrot solid is a mass of shards and flames. The fault sits on the seam half way between two planes. A rule with no jump can only fold space back over itself there, or, for an even power, crush the whole seam onto the x-axis, and either way the seam fills with a fat set of its own. No setting of these dials mends it. The 3D picture also draws the skin a little outside the true set in places (measured on the Mandelbrot solid: by up to 0.07), so judge the fine detail with care.',
    roundNote: p => (p.mix > 1.5 ? 'Inside each plane’s own band circles on the sphere stay circles. Toward the seam between two planes they are squashed flat.'
      : 'Inside each plane’s own band circles on the sphere stay circles. In the blend between two bands they do not.'),
    crush: (p, n) => {
      if (aprIs(n, 0)) return aprNone();
      if (p.mix > 1.5) return aprWhole(n / 2) ? ['no', 'Crushes every seam, the half-plane half way between two planes, onto the x-axis.' + aprPole(n)]
        : ['part', 'For an even power every seam, the half-plane half way between two planes, is crushed onto the x-axis. Other powers were not measured.' + aprPole(n)];
      return ['no', 'In the blend the sphere of directions is folded back over itself, and along each fold line it is crushed flat. Measured at n = 2: about 5 to 7% of directions come out turned over with 2 planes, about 30% with 3 or 4.' + aprPole(n)];
    },
    smooth: (p, n) => {
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
    crush: (p, n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (p.k === 0 && !p.wob) return ['no', 'With a multiplier of 0 every turn is thrown onto the half-plane z = 0, y > 0.'];
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the x-axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane x = 0.` : '') + aprPole(n)];
    },
    smooth: (p, n) => {
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
    crush: (p, n) => {
      if (p.layout > 0.5) return psReps(n) === 0 ? ['ok', 'Crushes nothing: below 1.5 this layout leaves every point where it is.']
        : ['part', 'Nothing but the origin is crushed onto one point. At three directions in the plane z = 0 (60°, 180° and 300°) the stretch falls to 0, where three sheets wrap around.'];
      if (Math.round(n) === 0) return aprNone();
      return ['ok', (Math.abs(Math.round(n)) < 2 ? 'Crushes nothing at this power.' : 'Nothing but the origin is crushed.') + aprPole(n)];
    },
    smooth: (p, n) => {
      if (p.layout > 0.5) return psReps(n) === 0 ? ['ok', 'Below 1.5 this layout leaves every point where it is.']
        : ['part', 'Smooth everywhere except the origin. Three directions in the plane z = 0 (60°, 180° and 300°) are spots where three sheets meet: smooth, but wrapped three times around.'];
      if (Math.round(n) === 0) return aprConstant();
      return ['no', (Math.abs(Math.round(n)) < 2 ? 'Smooth at this power.' : 'No jump was found, but the layout is creased, and every power copies the creases onto more places.')
        + aprTear(n, ' A power that is not a whole number is rounded, so the picture jumps between whole powers.')];
    },
    slice: (ok, p, n) => (p.layout > 0.5 ? (psReps(n) === 0 ? 'Below 1.5 this layout leaves every point where it is.'
        : 'The plane z = 0 lands on itself, but it does not follow complex arithmetic: the angle is doubled with a wobble of up to 60°. So the slice is not the flat set.')
      : !aprWhole(n) ? 'The power is rounded to a whole number, so the plane z = 0 follows that whole power and not this one.'
      : ok ? 'The planes z = 0 and y = 0 both follow complex arithmetic exactly. The 2D view of this page still draws the slice with a fringe: measured at n = 2, about 5 to 7% more solid than the flat set.' : 'The plane z = 0 does not follow complex arithmetic.'),
  },
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
    crush: (p, n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'In the three numbers the orbit is held in, it crushes every direction whose angle from the real axis, times n, is a multiple of 180°. In 4D the same directions are crushed.' + aprPole(n)];
    },
    smooth: (p, n) => {
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
    roundNote: (p, n) => (aprIs(n, -1) ? APR_MIRROR : 'The squash is in the spin direction around the reference axis.'),
    crush: (p, n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the reference axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane through the origin at right angles to the reference axis.` : '') + aprPole(n)];
    },
    smooth: (p, n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only. A power that is not a whole number also tears space along the reference axis, on its negative side, the way zⁿ tears the plane along the negative x-axis.'];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.'];
    },
    slice: (ok, p, n) => {
      const lat = p.lat === undefined ? 90 : p.lat, lon = aprWrap(p.lon || 0);
      if (Math.abs(aprCosSin(lat)[1]) > 0) return RT_SLICE_OFF + (aprIs(Math.abs(lat), 90) ? ' With the reference along the z-axis that is every plane through the z-axis, the plane y = 0 among them.' : '');
      if (ok) return lon ? 'At this power the plane z = 0 follows complex arithmetic exactly.' : 'With the reference along the x-axis this is Quaternion square (Lathe): the plane z = 0 follows complex arithmetic exactly, and so does every other plane through the x-axis.';
      const turn = aprWrap((1 - n) * lon);
      return aprWhole(n) && turn ? aprTurned(turn, n) : 'The plane z = 0 does not follow complex arithmetic.';
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
    crush: (p, n) => {
      if (aprIs(n, 0)) return aprNone();
      if (Math.abs(n) < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return aprIs(Math.abs(n), 2) ? ['no', RF_CRUSH2 + aprPole(n)] : ['part', RF_CRUSHN + aprPole(n)];
    },
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : ['no', RF_SMOOTH + aprTear(n, APR_HALF)]),
    slice: ok => (ok ? RF_SLICE : 'The plane z = 0 does not follow complex arithmetic.'),
  },
  {
    id: 'kleinsq', name: 'Kleinian squaring, one plane', group: 'kleinian', glsl: GL_KLEINSQ, axis: () => [0, 0, 1],
    tag: KQ_TAG,
    params: [{ type: 'note', text: KQ_NOTE }],
    formula: (p, n) => kqFormula(n, false),
    about: KQ_ABOUT,
    roundNote: () => KQ_ROUND,
    crush: (p, n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', KQ_CRUSH + aprPole(n)]),
    smooth: () => ['no', KQ_SMOOTH],
    slice: () => KQ_SLICE,
  },
  {
    id: 'kleinsq2', name: 'Kleinian squaring, two planes', group: 'kleinian', glsl: GL_KLEINSQ2, axis: () => [1, 0, 0],
    tag: KQ2_TAG,
    params: [{ type: 'note', text: KQ2_NOTE }],
    formula: (p, n) => kqFormula(n, true),
    about: KQ2_ABOUT,
    roundNote: () => KQ_ROUND,
    crush: (p, n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', KQ_CRUSH + aprPole(n)]),
    smooth: () => ['no', KQ2_SMOOTH],
    slice: () => KQ2_SLICE,
  },
  {
    id: 'sqpillow', name: 'Square pillow', group: 'pillow', glsl: GL_SQPILLOW, axis: () => [0, 0, 1],
    tag: SP_TAG,
    params: [{ type: 'note', text: SP_NOTE }],
    formula: (p, n) => spFormula(n),
    about: SP_ABOUT,
    roundNote: () => SP_ROUND,
    crush: (p, n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', (aprIs(Math.abs(n), 2) ? SP_CRUSH2 : SP_CRUSHN) + aprPole(n)]),
    smooth: (p, n) => ['no', SP_SMOOTH + (spOwn(n) ? '' : SP_SMOOTH_OTHER)],
    slice: (ok, p, n) => (spOwn(n) && ok ? SP_SLICE : spSliceOther(n)),
  },
  {
    id: 'turnaway', name: 'Turning plane, away', group: 'inversions', glsl: GL_TURNAWAY, axis: () => [1, 0, 0], deMax: 0,
    tag: TP_TAG_AWAY,
    params: [{ type: 'note', text: TP_NOTE_AWAY }],
    formula: (p, n) => tpFormula(n, false),
    about: TP_ABOUT_AWAY,
    roundNote: () => TP_ROUND,
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', (tpPlanes(n) === 1 ? TP_ONE : TP_CRUSH_AWAY) + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', TP_SMOOTH + (aprWhole(n) ? '' : TP_SMOOTH_OTHER) + aprTear(n, APR_HALF)]),
    slice: (ok, p, n) => tpSlice(ok, n, false),
  },
  {
    id: 'turnalong', name: 'Turning plane, along', group: 'inversions', glsl: GL_TURNALONG, axis: () => [1, 0, 0], deMax: 0,
    tag: TP_TAG_ALONG,
    params: [{ type: 'note', text: TP_NOTE_ALONG }],
    formula: (p, n) => tpFormula(n, true),
    about: TP_ABOUT_ALONG,
    roundNote: () => TP_ROUND,
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', TP_CRUSH_ALONG + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', TP_SMOOTH + (aprWhole(n) ? '' : TP_SMOOTH_OTHER) + aprTear(n, APR_HALF)]),
    slice: (ok, p, n) => tpSlice(ok, n, true),
  },
  {
    id: 'windsq', name: 'Wind, then square', group: 'inversions', glsl: GL_WINDSQ, axis: () => [1, 0, 0], deMax: 0,
    tag: WS_TAG,
    params: [{ type: 'note', text: WS_NOTE }],
    formula: (p, n) => wsFormula(n),
    about: WS_ABOUT,
    roundNote: (p, n) => wsRound(n),
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', wsCrush(n) + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', wsSmooth(n)]),
    slice: (ok, p, n) => wsSlice(ok, n),
  },
  {
    id: 'fourplanes', name: 'Four to one, two planes alike', group: 'fourone', glsl: GL_FOURPLANES, axis: () => [1, 0, 0], deMax: 0,
    tag: F4P_TAG,
    params: [{ type: 'note', text: F4P_NOTE }],
    formula: (p, n) => (aprIs(n, 2) ? F4P_FORMULA : F4_OTHER + aprMercFormula(n)),
    about: F4P_ABOUT,
    roundNote: (p, n) => (aprIs(n, 2) ? F4P_ROUND : f4One().roundNote({}, n)),
    crush: (p, n) => (aprIs(n, 2) ? ['part', F4P_CRUSH] : f4Else(f4One().crush({}, n))),
    smooth: (p, n) => (aprIs(n, 2) ? ['part', F4P_SMOOTH] : f4Else(f4One().smooth({}, n))),
    slice: (ok, p, n) => f4Slice(ok, n, F4P_SLICE),
  },
  {
    id: 'fourcaps', name: 'Four to one, caps flipped over', group: 'fourone', glsl: GL_FOURCAPS, axis: () => [0, 0, 1], deMax: 0,
    tag: F4C_TAG,
    params: [
      { type: 'note', text: F4C_NOTE },
      { type: 'dial', key: 'cap', label: 'Size of the two caps, degrees', min: 0, max: F4_CAP_MOST, step: 0.5, def: F4_CAP, help: F4C_HELP },
    ],
    formula: (p, n) => (aprIs(n, 2) ? f4cFormula(p) : F4_OTHER + aprMercFormula(n)),
    about: F4C_ABOUT,
    roundNote: (p, n) => (aprIs(n, 2) ? F4C_ROUND : f4One().roundNote({}, n)),
    crush: (p, n) => (aprIs(n, 2) ? ['part', f4cCrush(p)] : f4Else(f4One().crush({}, n))),
    smooth: (p, n) => (aprIs(n, 2) ? ['part', F4C_SMOOTH] : f4Else(f4One().smooth({}, n))),
    slice: (ok, p, n) => f4Slice(ok, n, ''),
  },
  // The orbit of this entry carries the number its caps come from (CARRY.fourcapsc).
  {
    id: 'fourcapsc', name: 'Four to one, caps placed by c', group: 'fourone', glsl: GL_FOURCAPSC, axis: () => [0, 0, 1], deMax: 0,
    tag: F4K_TAG,
    params: [
      { type: 'note', text: F4K_NOTE },
      { type: 'dial', key: 'cap', label: 'Size of the caps for a c at the distance 1, degrees', min: 0, max: F4K_CAP_MOST, step: 0.5, def: F4K_CAP, help: F4K_HELP_CAP },
      { type: 'dial', key: 'rot', label: 'Rotation of c before it places the caps, degrees', min: -180, max: 180, step: 1, def: F4K_ROT, help: F4K_HELP_ROT },
    ],
    formula: (p, n) => (aprIs(n, 2) ? f4kFormula(p) : F4_OTHER + aprMercFormula(n)),
    about: F4K_ABOUT,
    roundNote: (p, n) => (aprIs(n, 2) ? F4K_ROUND : f4One().roundNote({}, n)),
    crush: (p, n) => (aprIs(n, 2) ? ['part', F4K_CRUSH] : f4Else(f4One().crush({}, n))),
    smooth: (p, n) => (aprIs(n, 2) ? ['part', F4K_SMOOTH] : f4Else(f4One().smooth({}, n))),
    slice: (ok, p, n) => f4Slice(ok, n, ''),
  },
  // The orbit of the next two entries carries something besides its point (CARRY, GL_CARRY).
  {
    id: 'alongonce', name: 'Along once, then one plane', group: 'inversions', glsl: GL_ALONGONCE, axis: () => [1, 0, 0], deMax: 0,
    tag: AO_TAG,
    params: [{ type: 'note', text: AO_NOTE }],
    formula: (p, n) => aoFormula(n),
    about: AO_ABOUT,
    roundNote: (p, n) => AO_CARD + `It keeps shapes inside the ${tpCount(n, true)} planes through the x-axis in which Turning plane, along is the complex power, and squashes them between those planes and across them.` + AO_LATER + ', which keeps circles on the sphere as circles.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', AO_CARD + TP_CRUSH_ALONG + AO_LATER + ', which crushes the z-axis only.' + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', AO_CARD + TP_SMOOTH + (aprWhole(n) ? '' : TP_SMOOTH_OTHER) + aprTear(n, APR_HALF) + ' The rule changes after the first squaring, so an orbit is not one formula applied again and again.']),
    slice: ok => aoSlice(ok),
  },
  {
    id: 'pulledplane', name: 'Pulled plane', group: 'inversions', glsl: GL_PULLEDPLANE, axis: () => [1, 0, 0], deMax: 0,
    tag: PP_TAG,
    params: [
      { type: 'note', text: PP_NOTE },
      { type: 'dial', key: 'hold', label: 'Hold of the flat page at the start', min: 0, max: 1, step: 0.01, def: 0.05, xmax: 4, xhi: 100, help: PP_HELP_HOLD },
      { type: 'dial', key: 'ease', label: 'How little a thing near the page turns it', min: 0, max: 1, step: 0.01, def: 0.7, help: PP_HELP_EASE },
      { type: 'dial', key: 'cpull', label: 'Pull of c, times', min: 0, max: 64, step: 0.5, def: 16, xmax: 256, xhi: 10000, help: PP_HELP_CPULL },
    ],
    formula: (p, n) => ppFormula(p, n),
    about: PP_ABOUT,
    roundNote: () => PP_ROUND,
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', PP_CRUSH + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : ['no', ppSmooth(p, n)]),
    slice: ok => ppSlice(ok),
  },
  {
    id: 'softmirror', name: 'Sphere inversions, soft mirror', group: 'inversions', glsl: GL_SOFTMIRROR, axis: () => [1, 0, 0], deMax: 0,
    tag: 'Between one plane and two planes: the one-plane rule behind a mirror. One dial says where the mirror stands, the other how soft its edge is.',
    params: [
      { type: 'note', text: SM_NOTE },
      { type: 'dial', key: 'mirror', label: 'Mirror stands at, degrees from the flat plane', min: 45, max: 90, step: 0.5, def: 45, help: 'Counted round the x-axis from the flat plane. 90°: no mirror, so nothing sits off the flat plane (one plane). 45°: the upright plane y = 0 becomes a copy of the flat plane (two planes).' },
      { type: 'dial', key: 'soft', label: 'Soft edge, degrees', min: 0, max: 45, step: 0.5, def: 20, help: 'How far to each side of the mirror its edge is rounded. 0: a sharp edge, which leaves a crease. Larger: no crease, and a band this wide on each side of the mirror in which bodies are stretched round the x-axis.' },
    ],
    formula: (p, n) => aprMercFormula(n) + ` Before that the turn a of the point round the x-axis, counted from the flat plane, becomes ${aprDeg(p.mirror)} − |a − ${aprDeg(p.mirror)}|` + (smSoft(p) ? `, with the corner rounded over ${aprDeg(p.soft)} on each side.` : '.'),
    about: SM_ABOUT,
    roundNote: p => (smSoft(p) ? 'Away from the mirror circles on the sphere stay circles. Inside the soft edge they are squashed round the x-axis, and on the mirror itself squashed flat.' : 'Each piece keeps circles on the sphere as circles. The mirror leaves a crease between the pieces.'),
    crush: (p, n) => (aprIs(n, 0) ? aprNone()
      : ['part', (smSoft(p) ? 'On the mirror the turn round the x-axis is crushed: a thin slice of directions is spread over the whole soft band.' : 'Nothing but the origin is crushed. Space is creased on the mirror instead.') + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant()
      : ['no', (smSoft(p) ? 'No crease on the mirror, but' : 'A crease on the mirror, and') + ' across the plane y = 0 a jump, whose effect cancels only when c is on the x-axis.' + aprTear(n, APR_HALF)]),
    slice: (ok, p) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' + (aprIs(+p.mirror, 45) && +p.soft < 45 ? ' With the mirror at 45° the plane y = 0 carries the flat set as well.' : '')),
  },
  // An entry whose orbit carries something (CARRY.mirrorsdouble).
  {
    id: 'mirrorsdouble', name: 'Soft mirrors, doubling', group: 'inversions', glsl: GL_MIRRORSDOUBLE, axis: () => [1, 0, 0], deMax: 0,
    tag: 'The soft mirror with twice as many mirrors at each step: 2 planes at the first squaring, 4 at the second, 8 at the third. Bodies come to sit between the planes too.',
    params: [
      { type: 'note', text: MD_NOTE },
      { type: 'dial', key: 'soft', label: 'Soft edge, degrees', min: 0, max: 45, step: 0.5, def: 2, help: 'How far to each side of the first mirror its edge is rounded. Every later mirror is rounded by the same share of the gap between mirrors. 0: sharp edges, which leave thin crease lines. From about 4 up, a bud that sits right on a mirror is smeared into a striped oval.' },
      { type: 'dial', key: 'stop', label: 'Doubling stops after step', min: 1, max: 12, step: 1, def: 3, int: true, help: 'The mirrors double at each step up to this one and stay as they are after it. 1: two planes at every step, which is Sphere inversions, soft mirror. 3: 2, 4, then 8 planes. 12: the doubling never stops within the steps a picture takes.' },
    ],
    formula: (p, n) => aprMercFormula(n) + ` Before that, at step k of an orbit, the turn a of the point round the x-axis is folded by mirrors that stand every 90°/2ᵏ⁻¹` + (smSoft(p) ? `, each with its corner rounded over the same share of that gap (${aprDeg(p.soft)} at the first step).` : '.') + ` From step ${aprNum(clamp(Math.round(+p.stop || 1), 1, 12))} on the mirrors stay as they are: ${aprNum(mdPlanes(p))} planes through the x-axis.`,
    about: MD_ABOUT,
    roundNote: p => 'This card measures the first squaring of an orbit, which is the one of Sphere inversions, soft mirror with the mirror at 45°. ' + (smSoft(p) ? 'Away from a mirror circles on the sphere stay circles. Inside a soft edge they are squashed round the x-axis.' : 'Each piece keeps circles on the sphere as circles. The mirrors leave creases between the pieces.'),
    crush: (p, n) => (aprIs(n, 0) ? aprNone()
      : ['part', (smSoft(p) ? 'On each mirror the turn round the x-axis is crushed: a thin slice of directions is spread over the whole soft band.' : 'Nothing but the origin is crushed. Space is creased on the mirrors instead.') + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant()
      : ['no', (smSoft(p) ? 'No crease on the mirrors, but' : 'A crease on every mirror, and') + ' across the plane y = 0 a jump, whose effect cancels only when c is on the x-axis. The rule changes from step to step, so an orbit is not one formula applied again and again.' + aprTear(n, APR_HALF)]),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly at every step, so that slice is the flat set.'),
  },
  // The mirror image is added to the one-plane solid; it does not replace what is behind the mirror. The picture
  // runs one orbit per run of choices (APR_EITHER in 30-shaders.js).
  {
    id: 'either', name: 'Sphere inversions, either side', group: 'tried', glsl: GL_EITHER, axis: () => [1, 0, 0], deMax: 0,
    tag: 'Tried: the one-plane solid with its mirror images added, not swapped in. Failed: fewer bulbs, and the ones between the planes are smeared flat. A point is kept if the plain rule or the mirrored rule keeps it.',
    params: [
      { type: 'note', text: EI_NOTE },
      { type: 'dial', key: 'depth', label: 'Choice through step', min: 0, max: 5, step: 1, def: 1, int: true, help: 'For how many steps a point may be mirrored first. 0: never, which is Sphere inversions, one plane. 1: the cleanest picture. From 2 on, flat plates appear between the planes. Each step more doubles the work: 3 means 8 orbits for every point, 5 means 32.' },
    ],
    formula: (p, n) => aprMercFormula(n) + ` At each of the first ${aprNum(clamp(Math.round(+p.depth || 0), 0, 5))} steps the point may first be mirrored in the plane at 45° round the x-axis. A point is kept if any run of such choices keeps it.`,
    about: EI_ABOUT,
    roundNote: () => 'This card measures the plain choice, which is Sphere inversions, one plane: circles on the sphere stay circles. The mirrored choice is a mirror image of it, so it keeps them too.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', 'Nothing but the origin is crushed: every piece is the one-plane rule or a mirror image of it.' + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant()
      : ['no', 'The solid is several solids added together, so it is not the solid of one formula applied again and again. Where two of them meet the skin has a valley. It is whole only when c is on the x-axis.' + aprTear(n, APR_HALF)]),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, and a point on it has no choice to make, so that slice is the flat set.'),
  },
  {
    id: 'evenpillow', name: 'Even pillow', group: 'tried', glsl: GL_EVENPILLOW, axis: () => [1, 0, 0], deMax: 0,
    tag: 'Tried: read the direction off a square pillow grid and double both grid numbers, the same above and below the flat plane, with no mirror at all. Failed at the power 2: the solid is spiky, with fins. At the power 2 it is whole only for c on the x-axis; at 3 and 5 for every c.',
    params: [{ type: 'note', text: EP_NOTE }],
    formula: (p, n) => `vⁿ = |v|ⁿ · N(cos nA, sin nA · cos nL, sin nL)   with n = ${aprNum(n)}, where the direction of v is N(cos A, sin A · cos L, sin L) and N makes a vector length 1. Read back from the direction (X, Y, Z): ρ² = 2 / (1 + √(1 − 4X²Z²)), cos A = ρX, sin L = ρZ, cos L ≥ 0, and sin A has the sign of Y.`,
    about: EP_ABOUT,
    roundNote: () => 'On the circles z = 0 and x = 0 a small circle of directions stays a circle. Away from them it becomes an oval, at most about 1.4 times as long as wide before the step and the same again after it. That does not build up from step to step: many steps together stretch a shape no more than one step can.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', 'Nothing but the origin is crushed onto one point. Beside the four corners of the grid, the directions (±1, 0, ±1), the stretch is uneven.' + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant()
      : epOdd(n) ? ['part', 'One formula with no mirror and no jump at this power. The four corners of the grid are the only special directions.']
      : ['no', 'One formula with no mirror, but at an even power it jumps along two short arcs through the directions straight up and straight down. The two sides of the jump are mirror images, so it does not show when c is on the x-axis.']),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set. No corner of the grid lies in that plane.'),
  },
  // The two sides of each mirror are cross-faded in the picture (APR_BLEND in 30-shaders.js).
  {
    id: 'mirrorsblend', name: 'Blended mirrors, doubling', group: 'tried', glsl: GL_MIRRORSBLEND, axis: () => [1, 0, 0], deMax: 0,
    tag: 'Tried: keep the doubling mirrors sharp and cross-fade the two sides of each mirror. Failed: a bud that sits on a mirror gets a smooth bubble round it, and a pale band shows along the mirror.',
    params: [
      { type: 'note', text: MB_NOTE },
      { type: 'dial', key: 'soft', label: 'Blend width, degrees', min: 0, max: 45, step: 0.5, def: 6, help: 'How far to each side of the first mirror the two sides are cross-faded. Every later mirror gets the same share of the gap between mirrors. 0: no blending, plain sharp mirrors, which leave thin crease lines.' },
      { type: 'dial', key: 'stop', label: 'Doubling stops after step', min: 1, max: 12, step: 1, def: 3, int: true, help: 'The mirrors double at each step up to this one and stay as they are after it. 1: two planes at every step. 3: 2, 4, then 8 planes. 12: the doubling never stops within the steps a picture takes.' },
    ],
    formula: (p, n) => aprMercFormula(n) + ` Before that, at step k of an orbit, the turn a of the point round the x-axis is folded by sharp mirrors that stand every 90°/2ᵏ⁻¹. From step ${aprNum(clamp(Math.round(+p.stop || 1), 1, 12))} on the mirrors stay as they are: ${aprNum(mdPlanes(p))} planes through the x-axis.` + (smSoft(p) ? ` Within ${aprDeg(p.soft)} of the first mirror (the same share of the gap later) the picture cross-fades the distance to the solid between the two sides, at the first three steps.` : ''),
    about: MB_ABOUT,
    roundNote: () => 'This card measures the first squaring of an orbit with the sharp mirror: each piece keeps circles on the sphere as circles. The cross-fade is done on the finished picture, not on this step, so it bends nothing.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : ['part', 'Nothing but the origin is crushed, and nothing is smeared: space is folded on the mirrors, and the picture cross-fades the two sides of each fold.' + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant()
      : ['no', (smSoft(p) ? 'No crease on the mirrors of the first three steps: the two sides are cross-faded. That is done on the picture, so the solid is not the solid of one formula.' : 'A crease on every mirror.') + ' Across the plane y = 0 a jump, whose effect cancels only when c is on the x-axis.' + aprTear(n, APR_HALF)]),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly at every step, so that slice is the flat set.'),
  },
  // The orbit of this entry carries its count of steps (CARRY.tiltstep).
  {
    id: 'tiltstep', name: 'Quaternion square, axis by step', group: 'tried', glsl: GL_TILTSTEP, deMax: 0,
    axis: p => [Math.cos(aprRad(p.first)), -Math.sin(aprRad(p.first)), 0],
    tag: TS_TAG,
    params: [
      { type: 'note', text: TS_NOTE },
      { type: 'dial', key: 'first', label: 'Tilt of the axis at the first step, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'Where the axis that the angle is measured from points at the first step of an orbit, counted inside the plane z = 0 from the x-axis. With the dial below at 0 this entry is Quaternion square, twisted at this tilt.' },
      { type: 'dial', key: 'turn', label: 'Turn of the axis at each step, degrees', min: -180, max: 180, step: 0.5, def: 90, lo: -360, hi: 360, animate: true, help: 'How far the axis moves on, inside the plane z = 0, from one step of an orbit to the next. 0: the axis never moves, which is Quaternion square, twisted. 90: it points along x, then y, then −x, then −y, and so on. 180: it flips at every step.' },
    ],
    formula: (p, n) => `At step k of an orbit: vⁿ = turn(−n·t) · qⁿ(turn(t) · v)   with t = ${aprDeg(p.first)}${aprPlus(+p.turn || 0, '°')}·(k − 1), qⁿ the quaternion power and turn a turn about the z-axis.`,
    about: TS_ABOUT,
    roundNote: () => 'This card measures the first squaring of an orbit. The squash is in the spin direction around the tilted axis, and that direction changes from step to step.',
    crush: (p, n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'At each step it crushes every direction whose angle from that step’s axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane through the origin at right angles to the axis.` : '') + aprPole(n)];
    },
    smooth: (p, n) => {
      if (aprIs(n, 0)) return aprConstant();
      const steps = ' The rule changes from step to step, so an orbit is not one formula applied again and again.';
      if (!aprWhole(n)) return ['no', 'Each step is a polynomial (built from plain multiplying and adding) for whole positive powers only. A power that is not a whole number also tears space along a line, the way zⁿ tears the plane along the negative x-axis.' + steps];
      return ['part', (n < 0 ? 'Each step is a polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.' : 'Each step is a polynomial: built from plain multiplying and adding.') + steps];
    },
    slice: (ok, p, n) => (ok ? 'The plane z = 0 follows complex arithmetic exactly at every step, wherever the axis points.'
      : !aprWhole(n) ? 'For a power that is not a whole number the plane z = 0 follows complex arithmetic except in a wedge beside the negative x-axis, as wide as that step’s tilt. Whole powers are exact at every step.'
      : 'The plane z = 0 does not follow complex arithmetic.'),
  },
  {
    id: 'nearaxis', name: 'All axes, nearest to upright', group: 'tried', glsl: GL_NEARAXIS, axis: () => [1, 0, 0], deMax: 0,
    tag: NA_TAG,
    params: [{ type: 'note', text: NA_NOTE }],
    formula: (p, n) => axFormula(n) + ' Here h is the z-axis.',
    about: NA_ABOUT,
    roundNote: () => NA_ROUND,
    crush: (p, n) => { if (aprIs(n, 0)) return aprNone(); const [k, t] = naCrush(n); return [k, t + aprPole(n)]; },
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : ['no', NA_SMOOTH]),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly: for a point of that plane the nearest axis is the z-axis itself, and the turn is the flat one.'),
  },
  // The orbit of this entry carries the axis of its last turn (CARRY.lastaxis).
  {
    id: 'lastaxis', name: 'All axes, nearest to the last one', group: 'tried', glsl: GL_LASTAXIS, axis: () => [1, 0, 0], deMax: 0,
    tag: LA_TAG,
    params: [{ type: 'note', text: LA_NOTE }],
    formula: (p, n) => axFormula(n) + ' Here h is the axis the step before turned about, and the z-axis at the first step.',
    about: LA_ABOUT,
    roundNote: () => 'This card measures the first squaring of an orbit, which is the one of All axes, nearest to upright. ' + NA_ROUND,
    crush: (p, n) => { if (aprIs(n, 0)) return aprNone(); const [k, t] = naCrush(n); return [k, 'At the first step of an orbit: ' + t + ' At a later step the same holds for the plane through the x-axis and the axis the orbit carries.' + aprPole(n)]; },
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : ['no', LA_SMOOTH]),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly at every step: an orbit that starts in that plane turns about the z-axis and never picks up another axis.'),
  },
  {
    id: 'partsturn', name: 'Parts on a doubling grid, turn and scale', group: 'tried', glsl: GL_PARTSTURN, axis: () => [0, 0, 1], deMax: 0,
    tag: 'Tried: cut space into boxes that get smaller towards the flat plane, on a grid that squaring carries onto itself, and move each box by the turn-and-scale that fits squaring under its middle. Failed: low, faceted shells, cracked along every wall of a box, with loose shards. A twig set is lost almost entirely.',
    params: [{ type: 'note', text: 'How it works: every box has a flat point under its middle. The whole box is turned, scaled and slid by the one move of that kind that agrees with the flat rule at that point, in value and in slope.' + PT_FLAT + PT_GRID }],
    formula: (p, n) => ptTurnFormula(n) + ptGridWords(n, 0),
    about: PT_HEAD + 'This entry takes the plainest move, a turn and a scaling, on the grid that the power itself lays out. Across a wall between two boxes the two moves disagree. Close to the flat plane the gap is small beside the box. Where a box is as big as the body it cuts, the gap is a good part of the box, and the body breaks along the wall.',
    roundNote: () => 'Inside a part the move is a turn and a scaling, which keeps every shape. The measurement also takes in the jumps between parts.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : aprIs(n, 1) ? ['ok', 'Crushes nothing: ' + PT_STAYS.toLowerCase()]
      : ['part', ptKept(n) + ': every part is turned and scaled as a whole.' + PT_GAPS + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : aprIs(n, 1) ? ['ok', PT_STAYS]
      : ['no', 'Not one formula: the rule jumps across every wall between two parts. Towards the flat plane the jumps shrink faster than the parts do. They are largest in the top layers.' + aprTear(n, PT_NEAREST)]),
    slice: ptSlice,
  },
  {
    id: 'partsbend', name: 'Parts on a doubling grid, Möbius', group: 'tried', glsl: GL_PARTSBEND, axis: () => [0, 0, 1], deMax: 0,
    tag: 'Tried: the same boxes, each moved by the Möbius move that fits squaring under its middle in value, slope and bend. Failed: full, round bodies, but cracked into plates along the walls of the boxes, and a twig set is lost. Finer boxes close the cracks and leave smooth balls with nothing new off the flat plane.',
    params: [
      { type: 'note', text: 'How it works: as in Parts on a doubling grid, turn and scale, but the move of a box also has the bend of the flat rule at the point under its middle. Such a move is one sphere inversion with a turn, a scaling and a slide (a Möbius move), and it keeps every shape.' + PT_FLAT + PT_GRID },
      { type: 'dial', key: 'finer', label: 'Boxes made finer, in steps', min: 0, max: 6, step: 1, def: 0, int: true, help: 'At 0 a box is about as wide as it stands high above the flat plane, which is as large as a part may be. Each step divides the width of every box by the power once more: at the power 2 it halves it. The cracks close, and what told one direction round the upright axis from another goes with them: at 6 the picture is nearly the one of Parts of no size. Nothing in the rule fixes this number.' },
    ],
    formula: (p, n) => ptMobFormula(n, 'In each part') + (aprIs(n, 1) ? '' : ' u is the flat point under the middle of the part.' + ptGridWords(n, ptFiner(p))),
    about: PT_HEAD + 'This entry gives each box the closest move there is: it has the value, the slope and the bend of the flat rule under the middle of the box. The bodies come out full and round, and the gaps across the walls are smaller than with a turn and a scaling. But they are still there, and the body is cut into plates. Making the boxes finer closes the gaps. In the end the walls are gone, and with them everything that told directions apart: what is left is Parts of no size.',
    roundNote: () => 'Inside a part the move is one sphere inversion with a turn and a scaling, which keeps every shape. The measurement also takes in the jumps between parts.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : aprIs(n, 1) ? ['ok', 'Crushes nothing: ' + PT_STAYS.toLowerCase()]
      : ['part', 'Nothing is crushed inside a part: its move can be undone. Each move sends one point of the flat plane to infinity.' + PT_GAPS]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : aprIs(n, 1) ? ['ok', PT_STAYS]
      : ['no', 'Not one formula: the rule jumps across every wall between two parts. The jumps are smaller than with a turn and a scaling, and largest in the top layers.' + aprTear(n, PT_NEAREST)]),
    slice: ptSlice,
  },
  {
    id: 'partssquare', name: 'Parts on a square grid', group: 'tried', glsl: GL_PARTSSQUARE, axis: () => [0, 0, 1], deMax: 0,
    tag: 'Tried: boxes on a square grid that halve towards the flat plane, each moved by the turn-and-scale that fits squaring under its middle. Failed: bodies built of square blocks, like step pyramids, with shards round them. A twig set is lost almost entirely.',
    params: [{ type: 'note', text: 'How it works: a point at the height h above the flat plane lies in a square box about h wide, on a square grid like the one Balls on balls slides by. Half as high, the boxes are half as wide. The whole box is turned, scaled and slid by the one move of that kind that agrees with the flat rule, in value and in slope, at the flat point under the middle of the box.' + PT_FLAT }],
    formula: (p, n) => ptTurnFormula(n) + ' The parts: with s the power of 2 between |h|/2 and |h|, the box of a point reaches from one whole multiple of s to the next along x and along y.',
    about: PT_HEAD + 'This entry uses a grid that owes nothing to the power: plain squares. Squaring does not carry this grid onto itself, so a box lands across many boxes of the next step, and the walls show as flat faces and steps. With the Möbius move in place of the turn and the scaling this grid does worse: the picture breaks up into shards.',
    roundNote: () => 'Inside a part the move is a turn and a scaling, which keeps every shape. The measurement also takes in the jumps between parts.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : aprIs(n, 1) ? ['ok', 'Crushes nothing: ' + PT_STAYS.toLowerCase()]
      : ['part', ptKept(n) + ': every part is turned and scaled as a whole, and no box has its middle over the origin.' + PT_GAPS + aprPole(n)]),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : aprIs(n, 1) ? ['ok', PT_STAYS]
      : ['no', 'Not one formula: the rule jumps across every wall between two parts, and the power does not carry the grid onto itself.']),
    slice: ptSlice,
  },
  // The orbit of this entry carries the flat point its moves are fitted at (CARRY.partsorbit).
  {
    id: 'partsorbit', name: 'Parts carried by the orbit', group: 'tried', glsl: GL_PARTSORBIT, axis: () => [0, 0, 1], deMax: 0,
    tag: 'Tried: no grid. Every orbit keeps one part for good: the flat point its moves are fitted at starts under the orbit’s first point and goes on by the flat rule. Failed: the flat picture drawn straight up into columns with no top.',
    params: [{ type: 'note', text: 'How it works: an orbit that starts above the flat point u carries u with it, and u goes on by the flat rule: it takes the power of the page and c is added. At every step the point of the orbit is moved by the Möbius move that has the value, the slope and the bend of the flat power at the u of that step. Each of these moves keeps every shape, so a whole orbit is a chain of moves that keep every shape.' + PT_FLAT }],
    formula: (p, n) => ptMobFormula(n, 'At each step') + (aprIs(n, 1) ? '' : ' u is the flat point the orbit carries: at the first step the point under the orbit’s first point, and after each step u → uⁿ + c.'),
    about: PT_HEAD + 'Here a part is not a box. It is everything above one flat point, and an orbit keeps its part for good: its moves are fitted along the flat orbit of the point it started above. There is no wall, so there is no crack. But the picture shows what that costs: above the inside of the flat set every height stays in the solid, and above the outside every height leaves it. The solid is the flat picture drawn straight up. In the other entries of this kind the fit is taken afresh at every step, and that is what closes a body over.',
    roundNote: () => 'This card measures the first squaring of an orbit. There the points above one flat point share one Möbius move, and the points above the next flat point have another. Along one orbit every step keeps every shape.',
    crush: (p, n) => (aprIs(n, 0) ? aprNone() : aprIs(n, 1) ? ['ok', 'Crushes nothing: ' + PT_STAYS.toLowerCase()]
      : ['part', 'At the first step the points above one flat point share one Möbius move, which crushes nothing. The line that stands on the origin is the exception: its move is fitted at the origin, where the flat power has no slope, and the whole line lands on one point.']),
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : aprIs(n, 1) ? ['ok', PT_STAYS]
      : ['part', 'No wall and no jump: the move changes smoothly from one starting point to the next. But what a step does depends on the flat point the orbit carries, so an orbit is not one formula applied again and again.']),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'A point of the plane z = 0 takes the complex power itself at every step, so that slice is the flat set.'),
  },
  {
    id: 'partsnone', name: 'Parts of no size', group: 'tried', glsl: GL_PARTSNONE, axis: () => [0, 0, 1], deMax: 0,
    tag: 'Tried: shrink the parts to nothing, so that every point is moved by the Möbius move fitted under itself. Failed: it is one smooth formula again. The flat cut is exact and the bodies are full and close to balls, but there is nothing new off the flat plane.',
    params: [{ type: 'note', text: 'How it works: the flat point under a point is taken along the quarter circle about the middle that stands square to the flat plane: as far from the middle as the point itself, and the same way round the upright axis. The point is moved by the Möbius move that has the value, the slope and the bend of the flat power there. Worked out for a power above 0, that is a plain rule: the length is raised to the power, the longitude is multiplied by it, and the elevation φ above the flat plane goes to φ′ with e^(iφ′) = ((n + 1)·e^(iφ) − (n − 1)) / ((n + 1) − (n − 1)·e^(iφ)).' + PT_FLAT }],
    formula: (p, n) => ptMobFormula(n, 'For every point') + (aprIs(n, 1) ? '' : ' u has the length |v| and the longitude of v.'),
    about: 'What Parts on a doubling grid, Möbius becomes when its boxes are made finer without end. The walls are gone, and so are the cracks, but the rule is one smooth formula again, and it treats every direction round the upright axis alike. Its bodies are full and close to balls, the flat cut is exact, and the solid is whole for the Basilica, the Dendrite, the Douady rabbit, Kokopelli and the Mandelbrot set. Off the flat plane it adds nothing: the shapes of the flat picture sit along the flat plane only, as with Sphere inversions, one plane. The two rules differ in what they do higher up. One plane keeps circles on the sphere of directions round and leaves the upright axis in place. This rule flattens them, crushes one cone of directions onto the upright axis, and tears that axis open.',
    roundNote: (p, n) => (aprIs(n, -1) ? APR_MIRROR : 'On the flat plane a small circle of directions stays a circle. Higher up it is flattened.'),
    crush: (p, n) => {
      if (aprIs(n, 0)) return aprNone();
      if (aprIs(Math.abs(n), 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion. The origin is sent to infinity.' : 'Crushes nothing: ' + PT_STAYS.toLowerCase()];
      const cone = ptCone(n);
      if (cone === null) return ['part', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', `Crushes the cone of directions that stand ${aprDeg(cone)} above the flat plane onto the upright axis, and the cone as far below it likewise.` + aprPole(n)];
    },
    smooth: (p, n) => (aprIs(n, 0) ? aprConstant() : aprIs(n, 1) ? ['ok', PT_STAYS] : aprIs(n, -1) ? ['part', 'Smooth everywhere except the origin, which is a pole.']
      : ['part', 'One smooth formula, except on the upright axis: a point beside that axis lands in a direction that depends on the side it stands on, so the axis is torn open.' + aprTear(n, APR_HALF)]),
    slice: ok => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.'),
  },
  {
    // The rule the user builds from steps (12-custom.js; its panel is 82-custom-ui.js). Its shader text changes
    // with the steps, so glsl is worked out when asked for, and glslKey tells two such texts apart. whole: the
    // text of a whole step of the orbit, which takes the place of the page's equation. uniforms: what its shader
    // reads besides uA. scene: how far a point may go before it is thrown out (bail) and, while its steps are
    // being played, how many iterations the picture takes (iter; 0: as many as the page's dial says).
    id: 'custom', name: 'Custom: your own steps', group: 'custom', axis: () => [0, 0, 1],
    get glsl() { return cuProgram().glsl; }, glslKey: () => cuProgram().key, whole: 'cuRun(z, c, uPow)',
    uniforms: (gl, loc) => cuUniforms(gl, loc), scene: () => cuScene(), ball: () => cuReach(), halves: () => cuBoth(),
    start: z0 => `cuPreZ(${z0}, gCuRaw, c)`,   // the start value of a Mandelbrot orbit, after the steps taken once before the iterations
    get deMax() { return cuRough() ? 0 : undefined; },   // a rule may ask for the plain distance estimate
    tag: 'An approach you put together yourself, one step after another: lengths and angles, rotations about any axis, sphere inversions, mirrors, quaternions, matrices, adding c, and formulas of your own.',
    params: [],
    formula: () => cuWords(),
    about: 'The steps stand under the picture. One pass through them is one step of an orbit, so they take the place of the equation: c is added where the step “Add c” stands, and nowhere else. A step can be switched off, moved, or broken down: a block into the formulas it is made of, and a formula into its single operations. The bar under the picture plays the steps, iteration by iteration: the solid on show is every starting point that has not been thrown out so far, and the dots are some of those points, each drawn where the steps have carried it. The card below measures one pass with c set to 0.',
    roundNote: () => '',
    crush: () => ['part', 'Not worked out for an approach of your own. The rows above are measured from your steps.'],
    smooth: () => ['part', 'Not worked out for an approach of your own. A fold, a comparison or an axis that moves with the point can each break an approach into parts.'],
    slice: ok => (ok ? 'With these steps the plane z = 0 follows complex arithmetic, so that slice is the flat set.' : 'With these steps the plane z = 0 does not follow complex arithmetic.'),
  },
];
