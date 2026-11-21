"""Build out/lab2/pillow2/10-approaches.js: base4's file plus two pillow variants as the first two approaches.
   python out/lab2/pillow2/make_approach.py"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src = io.open(os.path.join(ROOT, 'base4/js/10-approaches.js'), encoding='utf-8').read()

JS_HELPERS = r"""// ---------- lab2 / pillow2: two pillow variants (see out/lab2/pillow2/NOTES.md)
// "pillowsmooth", the angle-true pillow. Direction map w -> (2w^3 - 1) / (w (2 - w^3)), w = (x + iy)/(1 - z).
// Worked in the chart of the lower half sphere, w = (x + iy)/(1 + |z|), |w| <= 1; the map commutes with the
// mirror z -> -z, so the upper half is the mirror image. N/D is kept as a pair, so nothing is ever divided by 0.
function psDir(d) {
  const s = 1 + Math.abs(d[2]), wx = d[0] / s, wy = d[1] / s;
  const ax = wx * wx - wy * wy, ay = 2 * wx * wy, cx = ax * wx - ay * wy, cy = ax * wy + ay * wx;   // w^3
  const Nx = 2 * cx - 1, Ny = 2 * cy, ex = 2 - cx, ey = -cy, Dx = wx * ex - wy * ey, Dy = wx * ey + wy * ex;
  const nn = Nx * Nx + Ny * Ny, dd = Dx * Dx + Dy * Dy, q = nn + dd;
  const Z = d[2] === 0 ? 0 : (d[2] > 0 ? dd - nn : nn - dd) / q;
  return [2 * (Nx * Dx + Ny * Dy) / q, 2 * (Ny * Dx - Nx * Dy) / q, Z];
}
const psReps = n => (n < 1.5 ? 0 : n < 3 ? 1 : n < 6 ? 2 : 3);   // the map is applied 1, 2 or 3 times: powers 2, 4, 8
// "pillowboth": the flat triangle laid along rays from its centre (polar angle in step with the distance from
// the centre), then slid along the half circles through (0, +-1, 0) so that the centre sits at 120 degrees in
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
"""

JS_MATH = r"""  pillowsmooth(v, n) {
    const k = psReps(n), r = Math.hypot(v[0], v[1], v[2]);
    if (k === 0) return [v[0], v[1], v[2]];
    if (r < 1e-20) return [0, 0, 0];
    let d = [v[0] / r, v[1] / r, v[2] / r];
    for (let j = 0; j < k; j++) d = psDir(d);
    const R = aprPow(r, 2 ** k);
    return [R * d[0], R * d[1], R * d[2]];
  },
  // v^n = |v|^n * Phi(n * PhiInv(v/|v|)), n rounded to a whole number; the sheet is held in the three
  // coordinates (XA, XB, XC) of out/proto/radial (weights of the triangle with A at the origin, continued).
  pillowboth(v, n) {
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
  },
"""

GL_NEW = r"""// lab2 / pillow2 shader code: the same steps as psDir, pbLayout, pbInverse and the two MATH entries.
// The product of two different points is the sphere-inversion product with one plane (aprMmul).
const GL_PIL2_MUL = `
vec3 aprMmul(vec3 a, vec3 b){
  float ra = length(a), rb = length(b);
  if (ra < 1e-20 || rb < 1e-20) return vec3(0.0);
  float Za = a.z / ra, Zb = b.z / rb;
  float Z = clamp((Za + Zb) / max(1.0 + Za * Zb, 1e-6), -1.0, 1.0);
  float la = length(a.xy), lb = length(b.xy);
  vec2 u = la > 0.0 && lb > 0.0 ? cmul(a.xy / la, b.xy / lb) : vec2(1.0, 0.0);
  return min(ra * rb, APR_CAP) * vec3(sqrt(max(0.0, 1.0 - Z * Z)) * u, Z);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 cmap(vec3 c){ return c; }`;
const GL_PSMOOTH = GL_APR + `
vec3 psDir(vec3 d){
  float s = 1.0 + abs(d.z);
  vec2 w = d.xy / s, w3 = cmul(cmul(w, w), w);
  vec2 N = 2.0 * w3 - vec2(1.0, 0.0), D = cmul(w, vec2(2.0, 0.0) - w3);
  float nn = dot(N, N), dd = dot(D, D), q = nn + dd;
  float Z = d.z == 0.0 ? 0.0 : (d.z > 0.0 ? dd - nn : nn - dd) / q;
  return vec3(2.0 * vec2(dot(N, D), N.y * D.x - N.x * D.y) / q, Z);
}
vec3 pw(vec3 v, float n){
  if (n < 1.5) return v;
  float r = length(v);
  if (r < 1e-20) return vec3(0.0);
  vec3 d = psDir(v / r);
  float m = 2.0;
  if (n >= 3.0) { d = psDir(d); m = 4.0; }
  if (n >= 6.0) { d = psDir(d); m = 8.0; }
  return aprPow(r, m) * d;
}
vec3 sqr(vec3 v){
  float r2 = dot(v, v);
  if (r2 < 1e-30) return vec3(0.0);
  return aprCap(r2 * psDir(v * inversesqrt(r2)));
}` + GL_PIL2_MUL;
const GL_PBOTH = GL_APR + `
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
vec3 pw(vec3 a, float n){ return pbPw(a, n); }
vec3 sqr(vec3 a){ return pbPw(a, 2.0); }` + GL_PIL2_MUL;
"""

ENTRIES = r"""  {
    id: 'pillowsmooth', name: 'Pillow, angle-true (reference, not exact)', glsl: GL_PSMOOTH, axis: () => [0, 0, 1], params: [],
    tag: 'The pillow with every layout fault removed. Not exact on z = 0: a reference only.',
    formula: (p, n) => {
      const k = psReps(n), note = aprIs(n, 2 ** k) ? '' : ` The power ${aprNum(n)} is replaced by ${2 ** k}: this reference exists for the powers 2, 4 and 8 only.`;
      if (k === 0) return 'v¹ = v.' + note;
      return `v${aprSup(2 ** k)} = |v|${aprSup(2 ** k)} · L(d)   with d = v/|v|, w = (x + iy)/(1 − z) the usual sphere coordinate of d, and L the map w → (2w³ − 1)/(w(2 − w³))${k > 1 ? `, applied ${k} times` : ''}.` + note;
    },
    about: 'Roll a flat sheet of equilateral triangles onto the sphere of directions and double it: when the rolling keeps every angle true, the doubling becomes one closed formula, w → (2w³ − 1)/(w(2 − w³)). It has no triangles, no creases and no seams, it stretches every direction, and it keeps the plane z = 0. But in that plane the angle is doubled with a wobble of up to 60°, so the slice at z = 0 is NOT the flat Mandelbrot or Julia set. It is here only to show what a pillow looks like when nothing is wrong with its layout. Powers 2, 4 and 8 only. A product of two different points is taken from Sphere inversions with one plane.',
    roundNote: 'Circles on the sphere of directions stay circles, except at the three directions half way between the corners, where the map folds three sheets together.',
    crush: () => ['ok', 'Nothing but the origin is crushed.'],
    smooth: () => ['part', 'Smooth everywhere except the origin. Three directions (60°, 180° and 300° in the plane z = 0) are branch points: the map is smooth there but not one-to-one.'],
    slice: () => 'The plane z = 0 is kept, but it does not follow complex arithmetic: the angle is doubled with a wobble of up to 60°. This rule fails the requirement on purpose.',
  },
  {
    id: 'pillowboth', name: 'Pillow, both planes exact', glsl: GL_PBOTH, axis: () => [0, 0, 1], params: [],
    tag: 'The flat-sheet pillow laid so that the planes z = 0 and y = 0 both carry the flat set.',
    formula: (p, n) => {
      const k = Math.round(n), whole = aprWhole(n) ? '' : ` The power ${aprNum(n)} is rounded to ${aprNum(k)}: the sheet can only be multiplied by a whole number.`;
      if (k === 1) return 'v¹ = v.' + whole;
      if (k === 0) return 'v⁰ = (1, 0, 0).' + whole;
      return `v${aprSup(k)} = |v|${aprSup(k)} · Φ(${aprNum(k)} · Φ⁻¹(d))   with d = v/|v| and Φ the wrapping of the flat sheet onto the sphere.` + whole;
    },
    about: 'A sheet tiled with equilateral triangles wraps onto the sphere of directions as a flat pillow, two triangles sewn along their edges, corners at the three cube roots of 1 in the plane z = 0. Multiplying the sheet by n is the power. Each triangle is laid along the rays from its centre, and the centre is then slid to 120° in the x-z plane, which lays the circle y = 0 at constant speed as well as the circle z = 0. So both planes follow complex arithmetic exactly and nothing jumps. The layout is creased. Whole powers only. A product of two different points is taken from Sphere inversions with one plane.',
    roundNote: 'Shapes are not kept: a small circle of directions comes out as an oval or a rounded triangle.',
    crush: (p, n = S.n) => ['ok', Math.abs(Math.round(n)) < 2 ? 'Crushes nothing at this power.' + aprPole(n) : 'Nothing but the origin is crushed.' + aprPole(n)],
    smooth: (p, n = S.n) => ['no', (Math.abs(Math.round(n)) < 2 ? 'Smooth at this power.' : 'Continuous everywhere, with creases along the planes z = 0 and y = 0, the rays from each triangle’s centre, and wherever a multiplied point crosses them.')
      + aprTear(n, ' A power that is not a whole number is rounded, so the picture jumps between whole powers.')],
    slice: (ok, p, n = S.n) => (!aprWhole(n) ? 'The power is rounded to a whole number, and for that power the planes z = 0 and y = 0 follow complex arithmetic exactly.'
      : ok ? 'The planes z = 0 and y = 0 both follow complex arithmetic exactly, so both slices are the flat set.' : 'The plane z = 0 does not follow complex arithmetic.'),
  },
"""


def put_before(text, anchor, block):
    assert text.count(anchor) == 1, anchor
    return text.replace(anchor, block + anchor)


def put_after(text, anchor, block):
    assert text.count(anchor) == 1, anchor
    return text.replace(anchor, anchor + block)


out = src
out = put_before(out, "// The power maps in JavaScript: MATH[id]", JS_HELPERS)
out = put_after(out, "const MATH = {\n", JS_MATH)
out = put_before(out, "// ---------- wording helpers", GL_NEW)
out = put_after(out, "const APPROACHES = [\n", ENTRIES)
dst = os.path.join(ROOT, 'out/lab2/pillow2/10-approaches.js')
io.open(dst, 'w', encoding='utf-8', newline='\n').write(out)
print('wrote', dst, len(out), 'chars')
