"""Build out/proto/radial/10-approaches.js: the frozen base2 copy plus the pillow approach as the first entry.
   python out/proto/radial/make_approach.py [--round 0|1] [--profile area|lin] [--out file.js]
Only this script writes that file, so the variants differ by two constants and nothing else."""
import argparse, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ap = argparse.ArgumentParser(); ap.add_argument('--round', type=int, default=1); ap.add_argument('--profile', default='area'); ap.add_argument('--out', default=os.path.join(HERE, '10-approaches.js'))
a = ap.parse_args()
src = open(os.path.join(ROOT, 'base2', 'js', '10-approaches.js'), encoding='utf-8').read().replace('\r\n', '\n')

MATH_JS = r"""
// ---------- the pillow: multiply by n on a flat sheet of triangles that wraps onto the sphere of directions.
// PIL_ROUND and PIL_PROFILE choose the layout of one triangle on its half sphere; the shader text below is
// generated from the same two constants, so the two cannot drift apart.
const PIL_T3 = 2 * PI / 3;
const PIL_ROUND = __ROUND__;       // true: level curves are round near the triangle's centre and triangular at its edge
const PIL_PROFILE = '__PROFILE__';   // 'area': every piece of the triangle keeps its share of the area. 'lin': polar angle in step with the distance from the centre
// Weights (lA, lB, lC) of a point in a triangle -> unit direction with z >= 0. The centre is the pole; the
// edge AB lies on the equator from 0° to 120°, BC from 120° to 240°, CA from 240° to 360°, at constant speed.
function pilLayout(l) {
  const mn = Math.min(l[0], l[1], l[2]), e = 3 * mn, s = 1 - e;        // s: 0 at the centre, 1 on the boundary
  const k = l[2] <= l[0] && l[2] <= l[1] ? 0 : l[0] <= l[1] ? 1 : 2;   // the edge the ray from the centre meets
  const t = s > 1e-12 ? clamp((l[(k + 1) % 3] - mn) / s, 0, 1) : 0.5;  // where on that edge
  const w = 2 * t - 1, lam = Math.sqrt(1 + 3 * w * w);                 // lam: centre-to-edge distance along this ray, over the shortest one
  const ec = PIL_ROUND ? e / (1 + s * (lam - 1)) : e;                  // 1 − (rounded radius); exactly 0 on the boundary
  const z = PIL_PROFILE === 'area' ? ec * (2 - ec) : Math.sin(0.5 * PI * ec);
  const rho = PIL_PROFILE === 'area' ? (1 - ec) * Math.sqrt(1 + z) : Math.cos(0.5 * PI * ec), tau = PIL_T3 * (k + t);
  return [rho * Math.cos(tau), rho * Math.sin(tau), z];
}
// the same backwards: a unit direction (x, y, z) with z >= 0 -> weights
function pilInverse(x, y, z) {
  z = Math.min(z, 1);
  const ec = PIL_PROFILE === 'area' ? z / (1 + Math.sqrt(1 - z)) : Math.asin(z) * 2 / PI;
  let a = (x === 0 && y === 0 ? 0 : Math.atan2(y, x)) / PIL_T3;
  if (a < 0) a += 3;
  const k = Math.min(Math.floor(a), 2), t = a - k, w = 2 * t - 1, lam = Math.sqrt(1 + 3 * w * w);
  const e = PIL_ROUND ? lam * ec / (1 + ec * (lam - 1)) : ec, l = [e / 3, e / 3, e / 3];
  l[k] += (1 - e) * (1 - t); l[(k + 1) % 3] += (1 - e) * t;
  return l;
}
"""
PILLOW_FN = r"""
  // v^n = |v|^n · Φ(n · Φ⁻¹(v/|v|)), n rounded to a whole number. The sheet is described by the three
  // coordinates (XA, XB, XC) that are the weights inside the triangle whose corner A sits at the origin, and
  // run on linearly outside it: lattice lines are where one of them is whole, so the triangle a point is in,
  // and its weights there, are their whole and fractional parts.
  pillow(v, n) {
    const m = Math.round(n), [x, y, z] = v, r = Math.hypot(x, y, z);
    if (m === 0) return [1, 0, 0];
    if (r < 1e-20) return m > 0 ? [0, 0, 0] : [aprPow(r, m), 0, 0];
    const l = pilInverse(x / r, y / r, Math.abs(z) / r);
    const X = z >= 0 ? l : [l[0] + l[2], l[1] + l[2], -l[2]];           // below the equator: the mirror image in the edge AB
    const Y = [m * X[0] - (m - 1), m * X[1], m * X[2]];                 // times m about the corner A
    const i = Y.map(Math.floor), f = Y.map((c, j) => c - i[j]);
    // The fractions add up to 1 in an upright triangle and to 2 in an upside-down one (the lower half sphere).
    // Exactly on a lattice point they are all 0 (or, a rounding error away, all 1): that is a corner.
    const sum = f[0] + f[1] + f[2], flip = sum > 1.5 && sum < 2.5;
    const k = (((i[1] - i[2]) % 3) + 3) % 3, g = sum < 0.5 || sum >= 2.5 ? [1, 0, 0] : flip ? [1 - f[0], 1 - f[2], 1 - f[1]] : f, wt = [0, 0, 0];
    for (let j = 0; j < 3; j++) wt[(k + j) % 3] = g[j];                 // g holds the weights at the corners coloured k, k + 1, k + 2
    const d = pilLayout(wt), R = aprPow(r, m);
    return [R * d[0], R * d[1], flip ? -R * d[2] : R * d[2]];
  },"""
GL = r"""
// The pillow in the shader: the same steps as pilLayout, pilInverse and MATH.pillow. The product of two
// different points is the sphere-inversion product (aprMmul), as in Sphere inversions with one plane.
const GL_PILLOW = GL_APR + `
const float PIL_T3 = 2.0943951024;
vec3 pilLay(vec3 l){
  float mn = min(l.x, min(l.y, l.z)), e = 3.0 * mn, s = 1.0 - e;
  float k = l.z <= l.x && l.z <= l.y ? 0.0 : l.x <= l.y ? 1.0 : 2.0;
  float nx = k < 0.5 ? l.y : k < 1.5 ? l.z : l.x;
  float t = s > 1e-6 ? clamp((nx - mn) / s, 0.0, 1.0) : 0.5;
  float w = 2.0 * t - 1.0, lam = sqrt(1.0 + 3.0 * w * w);
  float ec = ${PIL_ROUND ? 'e / (1.0 + s * (lam - 1.0))' : 'e'};
  ${PIL_PROFILE === 'area' ? 'float z = ec * (2.0 - ec), rho = (1.0 - ec) * sqrt(1.0 + z);' : 'float z = sin(0.5 * PI * ec), rho = cos(0.5 * PI * ec);'}
  float tau = PIL_T3 * (k + t);
  return vec3(rho * cos(tau), rho * sin(tau), z);
}
vec3 pilInv(vec3 d){
  float z = min(d.z, 1.0);
  float ec = ${PIL_PROFILE === 'area' ? 'z / (1.0 + sqrt(1.0 - z))' : 'asin(z) * 2.0 / PI'};
  float a = at2(d.y, d.x) / PIL_T3;
  if (a < 0.0) a += 3.0;
  float k = min(floor(a), 2.0), t = a - k, w = 2.0 * t - 1.0, lam = sqrt(1.0 + 3.0 * w * w);
  float e = ${PIL_ROUND ? 'lam * ec / (1.0 + ec * (lam - 1.0))' : 'ec'};
  vec3 m = k < 0.5 ? vec3(1.0 - t, t, 0.0) : k < 1.5 ? vec3(0.0, 1.0 - t, t) : vec3(t, 0.0, 1.0 - t);
  return vec3(e / 3.0) + (1.0 - e) * m;
}
vec3 pilPw(vec3 v, float n){
  float m = floor(n + 0.5), r = length(v);
  if (m == 0.0) return vec3(1.0, 0.0, 0.0);
  if (r < 1e-20) return m > 0.0 ? vec3(0.0) : vec3(aprPow(r, m), 0.0, 0.0);
  vec3 d = v / r, l = pilInv(vec3(d.xy, abs(d.z)));
  vec3 X = d.z >= 0.0 ? l : vec3(l.x + l.z, l.y + l.z, -l.z);
  X = vec3(m * X.x - (m - 1.0), m * X.y, m * X.z);
  vec3 i = floor(X), f = X - i;
  float sum = f.x + f.y + f.z;
  bool flip = sum > 1.5 && sum < 2.5;
  float k = mod(i.y - i.z + 0.5, 3.0);   // the half keeps a whole multiple of 3 from landing on either side of the wrap
  vec3 g = sum < 0.5 || sum >= 2.5 ? vec3(1.0, 0.0, 0.0) : flip ? vec3(1.0) - f.xzy : f;   // all fractions 0: a lattice point, a corner
  vec3 o = pilLay(k < 1.0 ? g : k < 2.0 ? g.zxy : g.yzx);
  if (flip) o.z = -o.z;
  return aprPow(r, m) * o;
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
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return pilPw(a, n); }
vec3 sqr(vec3 a){ return pilPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
"""
ENTRY = r"""
  {
    id: 'pillow', name: 'Pillow', glsl: GL_PILLOW, axis: () => [0, 0, 1], params: [],
    parts: { layout: pilLayout, inverse: pilInverse },   // the two halves of the wrapping, for the checks in out/proto/radial/checks.js
    tag: 'Unroll the sphere of directions onto a flat sheet of triangles and multiply there.',
    formula: (p, n) => {
      const k = Math.round(n), whole = aprWhole(n) ? '' : ` The power ${aprNum(n)} is rounded to ${aprNum(k)}: the sheet can only be multiplied by a whole number.`;
      if (k === 1) return 'v¹ = v.' + whole;
      if (k === 0) return 'v⁰ = (1, 0, 0).' + whole;
      return `v${aprSup(k)} = |v|${aprSup(k)} · Φ(${aprNum(k)} · Φ⁻¹(d))   with d = v/|v| and Φ the wrapping of the flat sheet onto the sphere.` + whole;
    },
    about: 'Doubling an angle on a circle is multiplying by 2 on the line the circle is rolled up from. The sphere of directions has two angles, so this rule rolls up a plane: a sheet tiled with equilateral triangles wraps onto the sphere as a flat pillow, two triangles sewn along their edges, with the corners at the three cube roots of 1 on the equator. Multiplying the sheet by n multiplies both angles at once, so every direction is stretched and none attracts the others. Each triangle is laid on its half of the sphere along the rays from its centre, which lands on a pole, and each edge lies on the equator at constant speed: that is what makes the plane z = 0 exact. Whole powers only. A product of two different points (c·z, a division) is taken from Sphere inversions with one plane.',
    roundNote: 'Areas keep close to their share, but shapes do not: a small circle of directions comes out as an oval or a rounded triangle.',
    crush: (p, n = S.n) => (Math.abs(Math.round(n)) < 2 ? ['ok', 'Crushes nothing at this power.' + aprPole(n)]
      : ['ok', 'Nothing but the origin is crushed: the sheet is stretched by the same factor everywhere.' + aprPole(n)]),
    smooth: (p, n = S.n) => ['no', (Math.abs(Math.round(n)) < 2 ? 'Smooth at this power.' : 'Continuous everywhere, with creases: the rays from each triangle’s centre to its corners, on the sphere and wherever a multiplied point crosses them.')
      + aprTear(n, ' A power that is not a whole number is rounded, so the picture jumps between whole powers.')],
    slice: (ok, p, n = S.n) => (!aprWhole(n) ? 'The power is rounded to a whole number, and for that power the plane z = 0 follows complex arithmetic exactly.'
      : ok ? 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' : 'The plane z = 0 does not follow complex arithmetic.'),
  },"""


def put(text, anchor, block, before):
    assert text.count(anchor) == 1, anchor
    return text.replace(anchor, block + anchor if before else anchor + block)


out = src
out = put(out, '// The power maps in JavaScript: MATH[id](v, n, q)', MATH_JS.lstrip('\n').replace('__ROUND__', 'true' if a.round else 'false').replace('__PROFILE__', a.profile), True)
out = put(out, 'const MATH = {', PILLOW_FN, False)
out = put(out, '\n// ---------- wording helpers for the approach texts', GL.rstrip('\n'), True)
out = put(out, 'const APPROACHES = [', ENTRY, False)
open(a.out, 'w', encoding='utf-8', newline='\n').write(out)
print('wrote %s (%d bytes), round=%d profile=%s' % (os.path.relpath(a.out, ROOT), len(out), a.round, a.profile))
