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
    tag: 'Square a quaternion with its second factor twisted. The rings of the Lathe break up.',
    params: [
      { type: 'dial', key: 'tilt', label: 'Tilt of the axis, degrees', min: -180, max: 180, step: 1, def: 40, lo: -360, hi: 360, animate: true, help: 'At 0 this is the plain quaternion square, the Lathe, and the solid is made of rings. Away from 0 the rings break up into one body with tunnels. At 180 it is the Lathe’s mirror twin. At 90 and −90 the Mandelbrot solid has no end: it runs off along a band and the drawing radius cuts it. A minus sign gives the mirror image. The plane z = 0 is exact at every tilt.' },
      { type: 'note', text: 'A rule for all of space with no plane chosen and no seam: for whole powers it is a polynomial. Up close its skin is smooth, as with every quaternion rule. The fine detail of the flat set shows where the solid meets the plane z = 0.' },
    ],
    formula: (p, n) => (aprIs(n, 2) ? `v² = ((x + iy)² − z²·e^(−2it), 2z·(x cos t − y sin t))   with t = ${aprDeg(p.tilt)}, and the first two coordinates written as one complex number. At t = 0 it is the quaternion square (x² − y² − z², 2xy, 2xz).`
      : `vⁿ = turn(−n·t) · qⁿ(turn(t) · v)   with t = ${aprDeg(p.tilt)}, qⁿ the quaternion power and turn a turn about the z-axis.`),
    about: 'A quaternion square is q times q. Here the second factor is twisted first: quaternions have four directions, two of them outside the flat plane, and those two are turned against each other by twice the tilt. What that leaves in 3D is the Lathe rule with its angle measured from an axis tilted inside the plane z = 0, and the result turned back. In the plane z = 0 the two turns cancel, so the slice is the flat set at every tilt. A Julia set whose c lies in that plane is a true slice of the 4D set. A Mandelbrot solid needs a c with a height, and adding it as a 3D point is this page’s own choice.',
    roundNote: () => 'The squash is in the spin direction around the tilted axis.',
    crush: (p, n = S.n) => {
      const a = Math.abs(n);
      if (aprIs(n, 0)) return aprNone();
      if (a < 1 + 1e-9) return ['ok', (n < 0 ? 'Crushes nothing at this power.' : 'Crushes nothing but the origin at this power.') + aprPole(n)];
      return ['no', 'Crushes every direction whose angle from the tilted axis, times n, is a multiple of 180°.' + (aprIs(a, 2) ? ` For n = ${aprNum(n)} that is the whole plane through the origin square to the tilted axis.` : '') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (!aprWhole(n)) return ['no', 'A polynomial for whole positive powers only. A power that is not a whole number also tears space along a line, the way zⁿ tears the plane along the negative x-axis.'];
      return n < 0 ? ['part', 'A polynomial divided by a power of |v|²: smooth everywhere except the origin, which is a pole.'] : ['ok', 'A polynomial.'];
    },
    // A power that is not whole tears the plane along the negative side of the tilted axis, where the plain
    // complex power tears it along the negative x-axis. So the two differ in the wedge between those two rays.
    slice: (ok, p, n = S.n) => (ok ? 'The plane z = 0 follows complex arithmetic exactly, at every tilt.'
      : !aprWhole(n) && p.tilt ? 'For a power that is not a whole number the plane z = 0 follows complex arithmetic except in a wedge: the tear lies along the tilted axis, not along the negative x-axis. Whole powers are exact at every tilt.'
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
];

// ---- test only (out/r12/page/make_test_approaches.py): stand-ins for entries that other people may add
{
  const base = APPROACHES.find(a => a.id === 'split');
  APPROACHES.push(
    { ...base, id: 'try1', name: 'Stand-in rule one', group: 'tried', tag: 'A stand-in for a rule that was tried. It draws the Split solid.',
      params: [{ type: 'note', text: 'Tried for the test of the list. It fails at nothing: it is the Split rule under another name.' }] },
    { ...base, id: 'try2', name: 'Stand-in rule two', group: 'tried', tag: 'A second stand-in, with a long one-line description that has to wrap at phone width without pushing the page wide.' },
    { ...base, id: 'odd1', name: 'Stand-in with no heading', group: 'nowhere', tag: 'Its group has no heading, so it comes last.' },
  );
  MATH.try1 = MATH.split; MATH.try2 = MATH.split; MATH.odd1 = MATH.split;
}
