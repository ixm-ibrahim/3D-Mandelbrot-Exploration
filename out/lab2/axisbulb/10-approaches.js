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
// The power maps in JavaScript: MATH[id](v, n, q) with q the approach's parameter object. They mirror the
// shader code below line for line, so what the scorecard measures is what the picture shows.
// Bulbs about the x-axis: the lathe power, then the turn around the x-axis is changed.
//   turn G = k * g + A * W * sin(4g),   g the turn of the lathe result, W = smoothstep of sin(angle from the x-axis) / sin(reach)
// e^(ig) is raised to the whole power k by repeated complex multiplication and sin(4g) is the polynomial
// 4cs(c^2 - s^2), so a point with z = 0 (or y = 0, for k = 1 mod 4) comes out with z = 0 (y = 0) to the last bit.
// That matters: for |k| > 1 the turn dynamics pushes away from those planes, and a rounding leak would grow.
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
const MATH = {
  axisbulb(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const rho = Math.hypot(y, z), a = Math.atan2(rho, x) * n, R = aprPow(r, n), sa = Math.sin(a);
    const u = rho > 0 ? [y / rho, z / rho] : [1, 0];     // the direction of (y, z) by division, not by angle: exact on the planes
    return axbTurn([R * Math.cos(a), R * sa * u[0], R * sa * u[1]], q);
  },
  mercator(v, n, q = {}) {
    const planes = q.planes || 1, [x, y, z] = foldk(v, planes), r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const Z = r > 0 ? clamp(z / r, -0.999999, 0.999999) : 0;
    const m = clamp(n * Math.atanh(Z), -20, 20) + (q.lift || 0), h = 1 / Math.cosh(m);
    const R = aprPow(r, n), p = Math.atan2(y, x) * n + (planes < 2 ? aprRad(q.turn) : 0);
    return [R * h * Math.cos(p), R * h * Math.sin(p), R * Math.tanh(m)];
  },
  lathe(v, n, q = {}) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-20 && n > 0) return [0, 0, 0];
    const rho = Math.hypot(y, z), a = Math.atan2(rho, x) * n, R = aprPow(r, n), p = Math.atan2(z, y) * (q.spin || 1);
    return [R * Math.cos(a), R * Math.sin(a) * Math.cos(p), R * Math.sin(a) * Math.sin(p)];
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
const GL_MERCATOR = GL_APR + `
vec3 aprFold(vec3 v){
  float k = uA.x;
  if (k < 1.5) return v;
  float rho = length(v.yz);
  if (rho < 1e-20) return v;
  float w = PI / k, psi = atan(v.z, v.y), s = psi < 0.0 ? -1.0 : 1.0, a = abs(psi);
  float j = floor(a / w + 0.5), d = a - j * w, a2;
  if (2.0 * j < k - 0.5 || (abs(2.0 * j - k) < 0.5 && d < 0.0)) a2 = mod(j, 2.0) < 0.5 ? d : -d;
  else a2 = PI + (mod(k - j, 2.0) < 0.5 ? d : -d);
  a2 *= s;
  return vec3(v.x, rho * cos(a2), rho * sin(a2));
}
vec3 aprMmul(vec3 a, vec3 b){
  float ra = length(a), rb = length(b);
  if (ra < 1e-20 || rb < 1e-20) return vec3(0.0);
  float Za = a.z / ra, Zb = b.z / rb;
  float Z = clamp((Za + Zb) / max(1.0 + Za * Zb, 1e-6), -1.0, 1.0);
  float la = length(a.xy), lb = length(b.xy);
  vec2 u = la > 0.0 && lb > 0.0 ? cmul(a.xy / la, b.xy / lb) : vec2(1.0, 0.0);
  return min(ra * rb, APR_CAP) * vec3(sqrt(max(0.0, 1.0 - Z * Z)) * u, Z);
}
// Longitude and Mercator latitude times n, then the turn (uA.y, degrees) and the lift (uA.z). The turn
// applies with one plane only: the folds rely on the mirror symmetry y -> -y, which a turn breaks.
float aprTurn(){ return uA.x < 1.5 ? radians(uA.y) : 0.0; }
vec3 aprMpw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20 && n > 0.0) return vec3(0.0);
  float Z = r > 0.0 ? clamp(v.z / r, -0.999999, 0.999999) : 0.0;
  float m = clamp(n * atanh(Z), -20.0, 20.0) + uA.z;
  float p = at2(v.y, v.x) * n + aprTurn();
  return aprPow(r, n) * vec3(vec2(cos(p), sin(p)) / cosh(m), tanh(m));
}
vec3 aprMsq(vec3 v){
  float r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  return aprCap((r2 / (r2 + v.z * v.z)) * vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, 2.0 * sqrt(r2) * v.z));
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(aprFold(a), aprFold(b)); }
vec3 pw(vec3 a, float n){ return aprMpw(aprFold(a), n); }
vec3 sqr(vec3 a){ return aprTurn() == 0.0 && uA.z == 0.0 ? aprMsq(aprFold(a)) : aprMpw(aprFold(a), 2.0); }
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
// uA.x: turn multiplier k (whole), uA.y: wobble A, uA.z: reach of the wobble in degrees, uA.w: pinch B. mul, pw and sqr are
// the lathe's (copied from GL_LATHE), each followed by the change of turn, as the lathe does with its spin.
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
const aprMercTurn = p => ((p.planes || 1) < 2 ? aprWrap(p.turn || 0) : 0);   // the turn in effect: one plane only
const APR_INVERSION = 'At n = −1 the rule is a single sphere inversion with a flip, and inversions keep every shape.';
const APR_MIRROR = 'At n = −1 the rule is a single sphere inversion with a mirror, and inversions keep every shape.';
// n = 0 sends every point to the same place, whatever the approach
const aprNone = () => ['no', 'Everything is crushed onto one point.'];
const aprConstant = () => ['ok', 'A constant.'];
// what the turn and longitude-phase dials do to the slice at z = 0
const APR_SLICE_TURNS = ' Away from 0 the slice at z = 0 is no longer the plain 2D picture: it is that picture turned (Mandelbrot) or a different set (Julia).';

// which planes through the x-axis a turn multiplier k keeps exact (the wobble never disturbs them)
const axbExact = k => (k % 2 === 0 ? 0 : ((k % 4) + 4) % 4 === 1 ? 2 : 1);   // 0: none, 1: z = 0 only, 2: z = 0 and y = 0
const APPROACHES = [
  {
    id: 'axisbulb', name: 'Bulbs about the x-axis', glsl: GL_AXISBULB, axis: () => [1, 0, 0],
    tag: 'Multiply the angle from the x-axis by n and the turn around it by k, with an optional wobble of the turn.',
    params: [
      { type: 'dial', key: 'k', label: 'Turn multiplier k', min: -7, max: 9, step: 1, def: 1, int: true, help: 'The turn around the x-axis is multiplied by k. 1 is the lathe. Odd k keeps the plane z = 0 exact; 1, 5, 9 and −3, −7 keep the plane y = 0 exact as well. An even k folds the half y < 0 of the plane onto the half y > 0, so the slice is no longer the flat set.' },
      { type: 'dial', key: 'wob', label: 'Wobble A of the turn', min: 0, max: 1, step: 0.01, def: 0.2, lo: -1, hi: 1, help: 'Adds A·sin(4·turn) to the turn. It vanishes on the planes z = 0 and y = 0 and on the two planes at 45° between them. Above 0.25 the turn folds over itself.' },
      { type: 'dial', key: 'reach', label: 'Wobble at full strength from, degrees off the axis', min: 0, max: 90, step: 1, def: 45, when: p => p.wob !== 0, help: 'The wobble fades to nothing toward the x-axis, so the axis keeps no crease from it. 0 switches the fade off.' },
      { type: 'dial', key: 'pinch', label: 'Pinch B between the planes', min: 0, max: 4, step: 0.05, def: 0, lo: -0.9, hi: 16, help: 'Makes every result longer by the factor 1 + B·sin²(2·turn)·sin²(angle from the x-axis). The factor is 1 on the planes z = 0 and y = 0 and on the x-axis, so those stay exact. It is the one dial here that changes a Julia set whose c is on the x-axis.' },
    ],
    formula: (p, n) => 'vⁿ = |v|ⁿ · (cos nβ, sin nβ · cos G, sin nβ · sin G)   with β the angle from the x-axis, γ the turn around it, and G = '
      + (p.k === 1 ? 'γ' : `${aprNum(p.k)}·γ`) + (p.wob ? `${aprPlus(p.wob, '')}·W·sin 4γ, W fading to 0 at the x-axis` : '') + (p.pinch ? `, and the length times 1${aprPlus(p.pinch, '')}·sin² 2γ·sin² nβ` : '')
      + (aprIs(n, 2) && p.k === 1 && !p.wob && !p.pinch ? '. That is (x² − y² − z², 2xy, 2xz).' : '.'),
    about: 'A prototype. The lathe multiplies the angle from the x-axis and keeps the turn around it, which gives bodies of revolution. Here the turn is multiplied as well, by a whole number k, and can be given a wobble. With k = 5 or −3 the planes z = 0 and y = 0 both follow complex arithmetic exactly and the planes at 45° follow its mirror image. For a Julia set whose c is on the x-axis the turn never feeds back into the shape, so that set is the lathe’s body of revolution whatever the dials say.',
    roundNote: (p, n) => (aprIs(n, -1) && p.k === 1 && !p.wob && !p.pinch ? APR_INVERSION : Math.abs(p.k) > 1 ? `The squash is in the turn direction: beside the x-axis, circles around it are stretched ${aprNum(Math.abs(p.k))} times their due.` : 'The squash is in the turn direction.'),
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (p.k === 0 && !p.wob) return ['no', 'With k = 0 every turn is thrown onto the half-plane z = 0, y > 0.'];
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the x-axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane x = 0.` : '') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      const tear = aprTear(n, APR_LINE);
      if (aprIs(n, 0)) return aprConstant();
      if (p.k !== 1) return ['no', 'Continuous, with a crease along the whole x-axis, where the turn has nothing to be measured from.' + tear];
      if (p.wob || p.pinch) return ['part', 'Continuous everywhere. The wobble and the pinch fade out toward the x-axis, so the axis keeps no crease.' + tear];
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only.' + tear];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.'];
    },
    slice: (ok, p) => {
      const e = axbExact(p.k);
      if (!ok || !e) return 'The plane z = 0 does not follow complex arithmetic: an even k folds its half y < 0 onto the half y > 0.';
      if (p.k === 1 && !p.wob && !p.pinch) return 'The plane z = 0 follows complex arithmetic exactly, and so does every other plane through the x-axis.';
      return 'The plane z = 0 follows complex arithmetic exactly' + (e === 2 ? ', and so does the plane y = 0.' : '. The plane y = 0 follows its mirror image.');
    },
  },
  {
    id: 'mercator', name: 'Sphere inversions', glsl: GL_MERCATOR, axis: p => (p.planes > 1 ? [1, 0, 0] : [0, 0, 1]),
    tag: 'Add up sphere inversions, the way circle inversions add up to zⁿ in the plane.',
    params: [
      { type: 'dial', key: 'planes', label: 'Planes that carry the flat set', min: 1, max: 8, step: 1, def: 1, int: true },
      { type: 'note', text: 'The number of planes is a free choice: nothing in this rule fixes it. With p planes the solid has 2p fins around the x-axis, whatever the power is, so fins and power match only when p is half of n (4 planes for n = 8, 3 for n = 6, 2 for n = 4). Fins come in pairs, so an odd power has no exact match. No value is the correct one. Kučera’s 3D figure uses 2 planes at n = 2, the starting value here.' },
      { type: 'dial', key: 'turn', label: 'Turn, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, when: p => p.planes < 2, help: 'This approach’s version of the Mandelbulb’s longitude phase, added to the longitude each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis, and Julia sets change shape.' + APR_SLICE_TURNS },
      { type: 'note', when: p => p.planes >= 2, text: 'With one plane there is also a turn dial. The folds need the flat set’s mirror symmetry, which a turn would break.' },
      { type: 'dial', key: 'lift', label: 'Lift toward the pole', min: -2, max: 2, step: 0.01, def: 0, lo: -6, hi: 6, animate: true, help: 'This approach’s version of the Mandelbulb’s latitude phase: it pushes every direction toward one pole each time a power is taken. Press play to make the solid pulse. Away from 0 the flat set leaves the plane z = 0.' },
    ],
    formula: (p, n) => {
      let s;
      const k = Math.round(n);
      if (aprWhole(n) && n >= 2) s = `v${aprSup(k)} = |v|${aprSup(k)} · [1 + ${k}·inv(Σₖ Rₖ·inv(d − ωₖ))]   with d = v/|v| the direction of v, inv a sphere inversion, ωₖ the ${k} points spaced evenly round the unit circle, and Rₖ the turn about the z-axis that reaches the k-th of them.`;
      else if (aprIs(n, 1)) s = 'v¹ = v.';
      else if (aprIs(n, 0)) s = 'v⁰ = (1, 0, 0).';
      else if (aprIs(n, -1)) s = 'v⁻¹ = inv(v) = (x, −y, −z)/|v|²: one sphere inversion, then a flip.';
      else if (aprWhole(n)) s = `v${aprSup(k)} = inv(v${aprSup(-k)}): the sum of inversions for the power ${-k}, then one more inversion.`;
      else s = 'vⁿ = |v|ⁿ · (cos nφ / cosh nm, sin nφ / cosh nm, tanh nm)   with φ the longitude and m the latitude as a Mercator map stretches it. At whole n this is what the sum of inversions gives.';
      if (p.planes > 1) s += ` Before that, the nearest of ${p.planes} planes through the x-axis is folded onto the xy-plane.`;
      const turn = aprMercTurn(p);
      if (turn || p.lift) s += ' After it, ' + [turn ? `${aprDeg(turn)} is added to the longitude` : '', p.lift ? `${aprNum(p.lift)} is added to the latitude (measured the way a Mercator map stretches it)` : ''].filter(Boolean).join(' and ') + '.';
      return s;
    },
    about: 'In the plane, zⁿ can be built from n + 1 circle inversions: one about each of n points spaced evenly round the unit circle, the results added, then one more inversion of the sum. Swap the circles for spheres and the same recipe works in space. Cut the solid at z = 0 and the slice is exactly the ordinary 2D Mandelbrot or Julia set of the same power (the 2D view shows it). Slices at other heights are different shapes. Worked out, the recipe multiplies two angles by n: the longitude, and the latitude as a Mercator map stretches it. One plane gives the inflated sets in Václav Kučera’s paper (Bridges 2019), two planes his fully 3D figure.',
    roundNote: (p, n) => (aprIs(n, -1) ? (p.planes < 2 ? APR_INVERSION : 'At n = −1 each piece is a sphere inversion with a flip, which keeps every shape. The folds between the pieces still leave creases.')
      : 'Circles on the sphere stay circles (see the step view). The squash is between the outward direction and the sphere.'),
    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      if (p.planes >= 2) return ['part', (n > 1 ? 'Nothing but the origin is crushed.' : 'Nothing is crushed.') + ' Space is creased where the folds meet instead.' + aprPole(n)];
      const a = Math.abs(n);
      if (aprIs(a, 1)) return ['ok', n < 0 ? 'Crushes nothing: at n = −1 the rule is one sphere inversion. The origin is sent to infinity.' : 'Crushes nothing: at n = 1 every point stays where it is.'];
      if (a < 1) return ['part', 'Crushes nothing at this power, but the stretch has no limit beside the z-axis.' + aprPole(n)];
      return ['part', 'Crushes the z-axis only: a line where the plane has a point.' + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (p.planes >= 2) return ['no', 'Pieces of the one-plane rule joined by mirror folds. The folds leave creases, and a jump whose effect cancels only when c is on the x-axis.' + aprTear(n, APR_HALF)];
      if (!aprWhole(n)) return ['no', 'Smooth for whole powers only.' + aprTear(n, APR_HALF)];
      return ['part', n < 0 ? 'Smooth everywhere except the origin, which is a pole.' : 'Smooth everywhere except the origin. It needs |v|, so it is not a polynomial.'];
    },
    slice: (ok, p, n = S.n) => {
      if (p.lift) return 'With a lift the plane z = 0 lands on a cone, so no flat slice follows complex arithmetic. Set the lift to 0 to get the flat set back.';
      const turn = aprMercTurn(p);
      if (turn) return aprTurned('The plane z = 0 follows', turn, n);
      if (!ok) return 'The plane z = 0 does not follow complex arithmetic.';
      return p.planes < 2 ? 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' : `${p.planes} planes through the x-axis follow complex arithmetic exactly, z = 0 among them.`;
    },
  },
  {
    id: 'lathe', name: 'Lathe', glsl: GL_LATHE, axis: () => [1, 0, 0],
    tag: 'Multiply the angle from the x-axis. Leave the spin around it alone, or multiply that too.',
    params: [{ type: 'dial', key: 'spin', label: 'Spin multiplier (odd)', min: -7, max: 9, step: 2, def: 1, odd: true }],
    formula: (p, n) => (aprIs(n, 2) ? 'v² = (x² − y² − z², 2xy, 2xz)' : aprIs(n, -1) ? 'v⁻¹ = (x, −y, −z)/|v|²'
      : 'vⁿ = |v|ⁿ · (cos nα, sin nα · u)   with α the angle from the x-axis and u the direction of (y, z)')
      + (p.spin !== 1 ? `, then the angle of (y, z) is multiplied by ${aprNum(p.spin)}` : ''),
    about: 'With spin 1 this is the power of a quaternion (a number with three imaginary parts) with one part held at zero, and the set is the flat one turned on a lathe. Any other odd spin also twists directions around the x-axis, which breaks the rings into bulbs while the plane z = 0 stays exact.',
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
    id: 'bulb', name: 'Mandelbulb', glsl: GL_BULB, axis: () => [0, 0, 1],
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
    id: 'classic', name: 'Mandelbulb, classic', glsl: GL_CLASSIC, axis: () => [0, 0, 1],
    tag: 'Multiply the angle from the z-axis and the angle around it.',
    params: [
      { type: 'dial', key: 'theta', label: 'θ phase, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'Added to the angle from the z-axis each time a power is taken. Sweeping it makes the solid pulse from its poles.' },
      { type: 'dial', key: 'phi', label: 'φ phase, degrees', min: -180, max: 180, step: 1, def: 0, lo: -360, hi: 360, animate: true, help: 'Added to the angle around the z-axis each time a power is taken. For zⁿ + c it turns the Mandelbrot solid about the z-axis; Julia sets change shape.' },
    ],
    formula: p => `vⁿ = |v|ⁿ · (sin T cos P, sin T sin P, cos T)   with T = n·θ${aprPlus(p.theta, '°')}, P = n·φ${aprPlus(p.phi, '°')}, θ the angle from the z-axis and φ the angle around it`,
    about: 'White and Nylander’s formula as most renders use it, usually at n = 8. It is here as a rendering benchmark, and it is the one approach whose z = 0 slice is not the flat set: for even n that whole plane is thrown onto the z-axis. A θ phase of (1 − n) × 90° turns it into the Mandelbulb above.',
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
        return `No. This is the one approach here that does not keep the flat set at z = 0. Setting the θ phase to ${aprDeg(fix)} would put it back: that turns this formula into the Mandelbulb above.`;
      }
      const turn = aprWrap((p.phi || 0) + (Math.sin(T) < 0 ? 180 : 0));
      if (turn) return aprTurned('The plane z = 0 follows', turn, n);
      return p.theta ? 'With this θ phase the plane z = 0 follows complex arithmetic exactly: the formula has become the Mandelbulb above.'
        : 'At this n the plane z = 0 happens to follow complex arithmetic.';
    },
  },
  {
    id: 'split', name: 'Split', glsl: GL_SPLIT, axis: () => [0, 0, 1],
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
];
