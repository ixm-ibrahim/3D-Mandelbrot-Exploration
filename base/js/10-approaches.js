// ---------- approaches. Each one defines a product mul(a, b) and a power pw(a, n) on points of space;
// every one except "classic" collapses to complex arithmetic in the plane z = 0.

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
const MATH = {
  mercator(v, n, q) {
    const [x, y, z] = foldk(v, q.planes), r = Math.hypot(x, y, z);
    if (r < 1e-300) return [0, 0, 0];
    const Z = clamp(z / r, -0.999999, 0.999999), Zn = Math.tanh(clamp(n * Math.atanh(Z), -20, 20));
    const h = Math.sqrt(Math.max(0, 1 - Zn * Zn)), R = Math.pow(r, n), p = Math.atan2(y, x) * n;
    return [R * h * Math.cos(p), R * h * Math.sin(p), R * Zn];
  },
  lathe(v, n, q) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-300) return [0, 0, 0];
    const rho = Math.hypot(y, z), a = Math.atan2(rho, x) * n, R = Math.pow(r, n), p = Math.atan2(z, y) * q.spin;
    return [R * Math.cos(a), R * Math.sin(a) * Math.cos(p), R * Math.sin(a) * Math.sin(p)];
  },
  bulb(v, n) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-300) return [0, 0, 0];
    const b = Math.atan2(z, Math.hypot(x, y)) * n, p = Math.atan2(y, x) * n, R = Math.pow(r, n);
    return [R * Math.cos(b) * Math.cos(p), R * Math.cos(b) * Math.sin(p), R * Math.sin(b)];
  },
  classic(v, n) {
    const [x, y, z] = v, r = Math.hypot(x, y, z);
    if (r < 1e-300) return [0, 0, 0];
    const t = Math.atan2(Math.hypot(x, y), z) * n, p = Math.atan2(y, x) * n, R = Math.pow(r, n);
    return [R * Math.sin(t) * Math.cos(p), R * Math.sin(t) * Math.sin(p), R * Math.cos(t)];
  },
  split(v, n) {
    const [x, y, z] = v, rho = Math.hypot(x, y), R = Math.pow(rho, n), p = Math.atan2(y, x) * n;
    return [R * Math.cos(p), R * Math.sin(p), Math.pow(Math.abs(z), n) * (z < 0 ? Math.cos(PI * n) : 1)];
  },
};

const GL_MERCATOR = `
vec3 foldk(vec3 v){
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
vec3 mmul(vec3 a, vec3 b){
  float ra = length(a), rb = length(b);
  if (ra < 1e-20 || rb < 1e-20) return vec3(0.0);
  float Za = a.z / ra, Zb = b.z / rb;
  float Z = clamp((Za + Zb) / max(1.0 + Za * Zb, 1e-6), -1.0, 1.0);
  float la = length(a.xy), lb = length(b.xy);
  vec2 u = la > 0.0 && lb > 0.0 ? cmul(a.xy, b.xy) / (la * lb) : vec2(1.0, 0.0);
  return ra * rb * vec3(sqrt(max(0.0, 1.0 - Z * Z)) * u, Z);
}
vec3 mpw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20) return vec3(0.0);
  float Z = clamp(v.z / r, -0.999999, 0.999999);
  float Zn = tanh(clamp(n * atanh(Z), -20.0, 20.0));
  float p = at2(v.y, v.x) * n;
  return pow(r, n) * vec3(sqrt(max(0.0, 1.0 - Zn * Zn)) * vec2(cos(p), sin(p)), Zn);
}
vec3 msq(vec3 v){
  float r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  return (r2 / (r2 + v.z * v.z)) * vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, 2.0 * sqrt(r2) * v.z);
}
vec3 mul(vec3 a, vec3 b){ return mmul(foldk(a), foldk(b)); }
vec3 pw(vec3 a, float n){ return mpw(foldk(a), n); }
vec3 sqr(vec3 a){ return msq(foldk(a)); }
vec3 cmap(vec3 c){ return foldk(c); }`;
const GL_LATHE = `
vec3 spin(vec3 v){
  if (uA.x == 1.0) return v;
  float rho = length(v.yz);
  if (rho < 1e-20) return v;
  float p = atan(v.z, v.y) * uA.x;
  return vec3(v.x, rho * cos(p), rho * sin(p));
}
vec3 mul(vec3 a, vec3 b){ return spin(vec3(a.x * b.x - dot(a.yz, b.yz), a.x * b.yz + b.x * a.yz)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20) return vec3(0.0);
  float rho = length(v.yz), a = atan(rho, v.x) * n;
  vec2 u = rho > 0.0 ? v.yz / rho : vec2(0.0);
  return spin(pow(r, n) * vec3(cos(a), sin(a) * u));
}
vec3 sqr(vec3 v){ return spin(vec3(v.x * v.x - dot(v.yz, v.yz), 2.0 * v.x * v.yz)); }
vec3 cmap(vec3 c){ return c; }`;
const GL_BULB = `
vec3 sph(float r, float be, float ph){ float cb = cos(be); return r * vec3(cb * cos(ph), cb * sin(ph), sin(be)); }
vec3 mul(vec3 a, vec3 b){ return sph(length(a) * length(b), at2(a.z, length(a.xy)) + at2(b.z, length(b.xy)), at2(a.y, a.x) + at2(b.y, b.x)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20) return vec3(0.0);
  return sph(pow(r, n), at2(v.z, length(v.xy)) * n, at2(v.y, v.x) * n);
}
vec3 sqr(vec3 v){
  float rho2 = dot(v.xy, v.xy), z2 = v.z * v.z;
  if (rho2 <= 0.0) return vec3(-z2, 0.0, 0.0);
  float k = (rho2 - z2) / rho2;
  return vec3(k * (v.x * v.x - v.y * v.y), k * 2.0 * v.x * v.y, 2.0 * sqrt(rho2) * v.z);
}
vec3 cmap(vec3 c){ return c; }`;
const GL_CLASSIC = `
vec3 sph(float r, float th, float ph){ float st = sin(th); return r * vec3(st * cos(ph), st * sin(ph), cos(th)); }
vec3 mul(vec3 a, vec3 b){ return sph(length(a) * length(b), at2(length(a.xy), a.z) + at2(length(b.xy), b.z), at2(a.y, a.x) + at2(b.y, b.x)); }
vec3 pw(vec3 v, float n){
  float r = length(v);
  if (r < 1e-20) return vec3(0.0);
  return sph(pow(r, n), at2(length(v.xy), v.z) * n, at2(v.y, v.x) * n);
}
vec3 sqr(vec3 v){ return pw(v, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
const GL_SPLIT = `
vec3 mul(vec3 a, vec3 b){ return vec3(cmul(a.xy, b.xy), a.z * b.z); }
vec3 pw(vec3 v, float n){
  float rho = length(v.xy), p = at2(v.y, v.x) * n, az = abs(v.z);
  float zs = az > 0.0 ? pow(az, n) * (v.z < 0.0 ? cos(PI * n) : 1.0) : 0.0;
  return vec3((rho > 0.0 ? pow(rho, n) : 0.0) * vec2(cos(p), sin(p)), zs);
}
vec3 sqr(vec3 v){ return vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, v.z * v.z); }
vec3 cmap(vec3 c){ return c; }`;

const APPROACHES = [
  {
    id: 'mercator', name: 'Mercator', glsl: GL_MERCATOR, axis: p => (p.planes > 1 ? [1, 0, 0] : [0, 0, 1]),
    tag: 'Multiply the longitude, and the latitude as a Mercator chart measures it.',
    params: [{ type: 'dial', key: 'planes', label: 'Planes that carry the flat set', min: 1, max: 6, step: 1, def: 2, int: true }],
    formula: p => 'z² = r²/(r² + z²) · (x² − y², 2xy, 2rz)' + (p.planes > 1 ? `, after folding the nearest of ${p.planes} planes through the x-axis onto the xy-plane` : ''),
    about: 'The approach that reproduces the Julia sets in Václav Kučera’s paper (Bridges 2019), rebuilt by eye because the paper leaves its construction out. One plane gives his inflated sets. Two planes give his truly 3D figure: show the Julia set at c = (−1, 0, 0) and look straight down.',
    roundNote: 'Circles on the sphere stay circles (see the step view). The squash is between the outward direction and the sphere.',
    crush: p => (p.planes < 2 ? ['part', 'Crushes the z-axis only: a line where the plane has a point.'] : ['part', 'Nothing but the origin is crushed. Space is creased where the folds meet instead.']),
    smooth: p => (p.planes < 2 ? ['part', 'Smooth everywhere except the origin. It needs |v|, so it is not a polynomial.'] : ['no', 'Pieces of the one-plane rule joined by mirror folds. The folds leave creases, and a jump whose effect cancels only when c is on the x-axis.']),
    slice: (ok, p) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : p.planes < 2 ? 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' : `${p.planes} planes through the x-axis follow complex arithmetic exactly, z = 0 among them.`),
  },
  {
    id: 'lathe', name: 'Lathe', glsl: GL_LATHE, axis: () => [1, 0, 0],
    tag: 'Multiply the angle from the x-axis. Leave the spin around it alone, or multiply that too.',
    params: [{ type: 'dial', key: 'spin', label: 'Spin multiplier (odd)', min: -7, max: 9, step: 2, def: 1, odd: true }],
    formula: p => 'z² = (x² − y² − z², 2xy, 2xz)' + (p.spin !== 1 ? `, then the angle of (y, z) is multiplied by ${p.spin}` : ''),
    about: 'With spin 1 this is quaternion squaring with one component held at zero, and the set is the flat one turned on a lathe. Any other odd spin also twists directions around the x-axis, which breaks the rings into bulbs while the plane z = 0 stays exact.',
    roundNote: 'The squash is in the spin direction.',
    crush: () => ['no', 'Crushes every direction whose angle from the x-axis, times n, is a multiple of 180°. For n = 2 that is the whole plane x = 0.'],
    smooth: p => (p.spin === 1 ? ['ok', 'A polynomial when n is a whole number.'] : ['no', 'Has a crease along the whole x-axis, where the spin has nothing to be measured from.']),
    slice: (ok, p) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.' : 'The plane z = 0 follows complex arithmetic exactly' + (p.spin === 1 ? ', and so does every other plane through the x-axis.' : '.')),
  },
  {
    id: 'bulb', name: 'Mandelbulb', glsl: GL_BULB, axis: () => [0, 0, 1],
    tag: 'Multiply the latitude and the longitude.',
    formula: () => 'z² = ((ρ² − z²)(x² − y²)/ρ², (ρ² − z²)·2xy/ρ², 2ρz)   with ρ = √(x² + y²)',
    about: 'The Mandelbulb with its up-down angle counted from the equator. That is the version that keeps the flat set in the plane z = 0.',
    roundNote: 'Exact on the equator, but the stretch grows without limit toward the z-axis.',
    crush: () => ['no', 'Crushes the cones where n times the latitude reaches ±90°, ±270° and so on (latitude ±45° for n = 2).'],
    smooth: () => ['no', 'Torn along the z-axis for even n: directions next to the pole are thrown all the way around the equator.'],
    slice: ok => (ok ? 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' : 'The plane z = 0 does not follow complex arithmetic.'),
  },
  {
    id: 'classic', name: 'Mandelbulb, classic', glsl: GL_CLASSIC, axis: () => [0, 0, 1],
    tag: 'Multiply the angle from the z-axis and the angle around it.',
    formula: () => 'zⁿ = rⁿ · (sin nθ cos nφ, sin nθ sin nφ, cos nθ)   with θ from the z-axis and φ around it',
    about: 'White and Nylander’s formula as most renders use it, usually at n = 8. It is here as a rendering benchmark, and it is the one approach whose z = 0 slice is not the flat set: for even n that whole plane is thrown onto the z-axis.',
    roundNote: 'Stretched up to n times too far beside the z-axis, crushed on cones around it.',
    crush: () => ['no', 'Crushes every direction whose angle from the z-axis, times n, is a multiple of 180°.'],
    smooth: () => ['no', 'Has a crease along the whole z-axis, where the angle around it has nothing to be measured from.'],
    slice: ok => (ok ? 'At this n the plane z = 0 happens to follow complex arithmetic.' : 'No. This is the one approach here that does not keep the flat set at z = 0.'),
  },
  {
    id: 'split', name: 'Split', glsl: GL_SPLIT, axis: () => [0, 0, 1],
    tag: 'Treat x + iy as a complex number and z as a real number, each on its own.',
    formula: () => 'z² = (x² − y², 2xy, z²)',
    about: 'Space treated as ℂ × ℝ, the kind of commutative multiplication that does exist in three dimensions. It has zero divisors, and the set is the flat one extruded into a prism.',
    roundNote: 'Each factor keeps shapes on its own. Together they do not.',
    crush: () => ['no', 'Crushes the plane z = 0 and the z-axis.'],
    smooth: () => ['ok', 'A polynomial when n is a whole number.'],
    slice: ok => (ok ? 'The plane z = 0 follows complex arithmetic exactly. So does every level slice of the prism.' : 'The plane z = 0 does not follow complex arithmetic.'),
  },
];
