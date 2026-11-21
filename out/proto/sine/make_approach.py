"""Write out/proto/sine/10-approaches.js: the frozen base2 copy with the pillow approach added as the first entry.

  python out/proto/sine/make_approach.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
src = open(os.path.join(ROOT, "base2", "js", "10-approaches.js"), encoding="utf-8").read().replace("\r\n", "\n")

JS = r'''// ---------- the pillow. The sphere of directions is a flat sheet of equilateral triangles folded into a
// pillow (two triangles sewn along their edges, corners at the cube roots of 1 on the equator), and a power
// multiplies the flat sheet by n:   v^n = |v|^n * Phi(n * PhiInv(v / |v|)).
// Layout of one triangle ("barycentric sines"): with weights lA, lB, lC at the corners, the horizontal part is
//   H = (2/sqrt 3) * (sin(T lA) eA + sin(T lB) eB + sin(T lC) eC),   T = 120 degrees, e at 0, 120, 240 degrees
// which runs along each edge of the triangle on the equator at constant speed. The lift is the equal-area
// one: z = 1 - |H|^2, (x, y) = H * sqrt(1 + z). A triangle that points up in the sheet takes z < 0.
const PIL_R3 = Math.sqrt(3), PIL_T = 2 * PI / 3;
// The layout seen from its heaviest corner, taken as A: weights w1, w2 of the next two corners -> [hx, hy, 1 - |h|^2].
// Written as products of half-angle sines, so nothing cancels beside the two edges that meet at that corner.
function pilLay(w1, w2) {
  const sb = Math.sin(PIL_T * w1 / 2), sg = Math.sin(PIL_T * w2 / 2), cb = Math.sqrt(1 - sb * sb), cg = Math.sqrt(1 - sg * sg);
  const S = sb * cg + cb * sg, C = cb * cg - sb * sg, D = 2 / PIL_R3 * sb * sg;
  return [1 - 2 * S * (S + D), 2 * C * (sb * cg - cb * sg),
    4 * sb * sg * (4 * C * C * cb * cg + 2 / PIL_R3 * S * (1 - 2 * S * S - S * D))];
}
// flat point -> unit direction
function pilPhi(ux, uy) {
  const b = uy * 2 / PIL_R3, a = ux + b / 2, i = Math.floor(a), j = Math.floor(b), fa = a - i, fb = b - j;
  const up = fa >= fb, k = (((i + j) % 3) + 3) % 3;
  const w = up ? [1 - fa, fa - fb, fb] : [1 - fb, fb - fa, fa];     // weights of the colours k, k + 1, k + 2
  const m = w[2] > Math.max(w[0], w[1]) ? 2 : w[1] > w[0] ? 1 : 0;
  const [hx, hy, q] = pilLay(w[(m + 1) % 3], w[(m + 2) % 3]);
  const c = (k + m) % 3, z = clamp(q, 0, 1), s = Math.sqrt(1 + z);  // c thirds of a turn bring the heaviest corner back
  const cs = c === 0 ? 1 : -0.5, sn = c === 0 ? 0 : c === 1 ? PIL_R3 / 2 : -PIL_R3 / 2;
  return [s * (cs * hx - sn * hy), s * (sn * hx + cs * hy), up ? -z : z];
}
// unit direction -> flat point in the triangle A (0, 0), B (1, 0), C (1/2, -+sqrt(3)/2). After a turn that
// brings the nearest corner to A, one unknown is left, p = sin of half the angle the two far weights add up
// to: Newton from sqrt(T/2), which is exact on the equator and never more than a tenth off elsewhere.
const PIL_NEWTON = 4;   // the shader takes 3, which is already past what its 32-bit numbers can tell apart
function pilPhiInv(dx, dy, dz) {
  const z = Math.min(Math.abs(dz), 1), s = 1 / Math.sqrt(1 + z);
  let hx = dx * s, hy = dy * s, c = 0;
  if (Math.abs(hy) > PIL_R3 * hx) {
    c = hy > 0 ? 1 : 2;
    const t = c === 1 ? PIL_R3 / 2 : -PIL_R3 / 2;
    [hx, hy] = [-0.5 * hx + t * hy, -t * hx - 0.5 * hy];
  }
  const T = (hy * hy + z) / (1 + hx);
  let p = Math.min(Math.sqrt(T / 2), 0.8);
  for (let it = 0; it < PIL_NEWTON; it++) {
    const ss = Math.sqrt(1 - p * p), e = hy * hy / (4 * ss * ss), cc = Math.sqrt(Math.max(1 - e, 1e-12));
    const f = 2 * p * p + 2 / PIL_R3 * p * (cc - ss) - T;
    const df = 4 * p + 2 / PIL_R3 * ((cc - ss) + p * p * (1 / ss - e / (cc * ss * ss)));
    p = clamp(p - f / Math.max(df, 1e-20), 0, 0.8);
  }
  const ss = Math.sqrt(1 - p * p), sh = Math.asin(p), th = Math.asin(clamp(hy / (2 * ss), -p, p));
  const w1 = (sh + th) / PIL_T, w2 = (sh - th) / PIL_T, w0 = 1 - w1 - w2;
  const lB = c === 0 ? w1 : c === 1 ? w0 : w2, lC = c === 0 ? w2 : c === 1 ? w1 : w0;
  return [lB + lC / 2, (dz >= 0 ? -1 : 1) * lC * PIL_R3 / 2];
}
// The whole rule. `raw` leaves out the last line's snap (for the checks: it shows how far rounding alone
// moves a point of the plane z = 0 off that plane).
function pilPower(v, n, raw) {
  const k = Math.round(n), [x, y, z] = v, r = Math.hypot(x, y, z);
  if (r < 1e-20 && k > 0) return [0, 0, 0];
  if (k === 1) return [x, y, z];
  const u = r > 0 ? pilPhiInv(x / r, y / r, z / r) : [0, 0], o = pilPhi(k * u[0], k * u[1]), R = aprPow(r, k);
  // A point of the plane z = 0 stays on it exactly; rounding would otherwise leave it a hair off.
  return [R * o[0], R * o[1], z === 0 && !raw ? 0 : R * o[2]];
}
'''

GL = r'''// The pillow in the shader: the same steps as pilLay, pilPhi, pilPhiInv and pilPower above.
// pilMul is the product of the sphere-inversion approach with one plane (aprMmul), copied.
const GL_PILLOW = GL_APR + `
const float PIL_R3 = 1.7320508075688772, PIL_T = 2.0943951023931953;
// Half angles and square roots only: on some graphics cards cos() and asin() are good to four or five digits,
// while sin() and sqrt() are good to seven. pilAsin (for |x| below 0.8) puts the missing digits back.
float pilAsin(float x){ float y = asin(x), s = sin(y); return y - (s - x) * inversesqrt(1.0 - s * s); }
vec3 pilLay(float w1, float w2){
  float sb = sin(0.5 * PIL_T * w1), sg = sin(0.5 * PIL_T * w2), cb = sqrt(1.0 - sb * sb), cg = sqrt(1.0 - sg * sg);
  float S = sb * cg + cb * sg, C = cb * cg - sb * sg, D = (2.0 / PIL_R3) * sb * sg;
  return vec3(1.0 - 2.0 * S * (S + D), 2.0 * C * (sb * cg - cb * sg),
    4.0 * sb * sg * (4.0 * C * C * cb * cg + (2.0 / PIL_R3) * S * (1.0 - 2.0 * S * S - S * D)));
}
vec3 pilPhi(vec2 u){
  float b = u.y * (2.0 / PIL_R3), a = u.x + 0.5 * b, i = floor(a), j = floor(b), fa = a - i, fb = b - j;
  bool up = fa >= fb;
  vec3 w = up ? vec3(1.0 - fa, fa - fb, fb) : vec3(1.0 - fb, fb - fa, fa);
  float m = w.z > max(w.x, w.y) ? 2.0 : (w.y > w.x ? 1.0 : 0.0);
  vec3 t = m > 1.5 ? w.zxy : (m > 0.5 ? w.yzx : w);
  vec3 h = pilLay(t.y, t.z);
  float c = mod(i + j + m, 3.0), z = clamp(h.z, 0.0, 1.0), s = sqrt(1.0 + z);
  vec2 rot = c < 0.5 ? vec2(1.0, 0.0) : vec2(-0.5, c < 1.5 ? 0.5 * PIL_R3 : -0.5 * PIL_R3);
  return vec3(s * (rot.x * h.x - rot.y * h.y), s * (rot.y * h.x + rot.x * h.y), up ? -z : z);
}
vec2 pilPhiInv(vec3 d){
  float z = min(abs(d.z), 1.0);
  vec2 h = d.xy * inversesqrt(1.0 + z);
  float c = 0.0;
  if (abs(h.y) > PIL_R3 * h.x) {
    c = h.y > 0.0 ? 1.0 : 2.0;
    float t = h.y > 0.0 ? 0.5 * PIL_R3 : -0.5 * PIL_R3;
    h = vec2(-0.5 * h.x + t * h.y, -t * h.x - 0.5 * h.y);
  }
  float T = (h.y * h.y + z) / (1.0 + h.x), p = min(sqrt(0.5 * T), 0.8);
  for (int it = 0; it < 3; it++) {
    float ss = sqrt(1.0 - p * p), e = h.y * h.y / (4.0 * ss * ss), cc = sqrt(max(1.0 - e, 1e-12));
    float f = 2.0 * p * p + (2.0 / PIL_R3) * p * (cc - ss) - T;
    float df = 4.0 * p + (2.0 / PIL_R3) * ((cc - ss) + p * p * (1.0 / ss - e / (cc * ss * ss)));
    p = clamp(p - f / max(df, 1e-20), 0.0, 0.8);
  }
  float ss = sqrt(1.0 - p * p), sh = pilAsin(p), th = pilAsin(clamp(h.y / (2.0 * ss), -p, p));
  float w1 = (sh + th) / PIL_T, w2 = (sh - th) / PIL_T, w0 = 1.0 - w1 - w2;
  float lB = c < 0.5 ? w1 : (c < 1.5 ? w0 : w2), lC = c < 0.5 ? w2 : (c < 1.5 ? w1 : w0);
  return vec2(lB + 0.5 * lC, (d.z >= 0.0 ? -0.5 : 0.5) * PIL_R3 * lC);
}
vec3 pilPower(vec3 v, float n){
  float k = floor(n + 0.5), r = length(v);
  if (r < 1e-20 && k > 0.0) return vec3(0.0);
  if (k == 1.0) return v;
  vec3 o = pilPhi(k * (r > 0.0 ? pilPhiInv(v / r) : vec2(0.0)));
  if (v.z == 0.0) o.z = 0.0;
  return aprPow(r, k) * o;
}
vec3 pilMul(vec3 a, vec3 b){
  float ra = length(a), rb = length(b);
  if (ra < 1e-20 || rb < 1e-20) return vec3(0.0);
  float Za = a.z / ra, Zb = b.z / rb;
  float Z = clamp((Za + Zb) / max(1.0 + Za * Zb, 1e-6), -1.0, 1.0);
  float la = length(a.xy), lb = length(b.xy);
  vec2 u = la > 0.0 && lb > 0.0 ? cmul(a.xy / la, b.xy / lb) : vec2(1.0, 0.0);
  return min(ra * rb, APR_CAP) * vec3(sqrt(max(0.0, 1.0 - Z * Z)) * u, Z);
}
vec3 mul(vec3 a, vec3 b){ return pilMul(a, b); }
vec3 pw(vec3 a, float n){ return pilPower(a, n); }
vec3 sqr(vec3 a){ return pilPower(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;

'''

ENTRY = r'''  {
    id: 'pillow', name: 'Pillow', glsl: GL_PILLOW, axis: () => [0, 0, 1],
    tag: 'Unfold the sphere of directions into a flat sheet of triangles, multiply the sheet by n, fold it back.',
    formula: (p, n) => {
      const k = Math.round(n);
      const s = k === 1 ? 'v¹ = v.' : k === 0 ? 'v⁰ = (1, 0, 0).' : `v${aprSup(k)} = |v|${aprSup(k)} · Φ(${k < 0 ? '−' + (-k) : k}·Φ⁻¹(v/|v|))   with Φ the fold of the flat sheet onto the sphere.`;
      return s + (aprWhole(n) ? '' : ` The power is rounded to ${aprNum(k)}: the sheet can only be multiplied by a whole number.`);
    },
    about: 'A circle is a line rolled up, and doubling an angle is multiplying that line by 2. The sphere of directions is a plane rolled up in the same sense: a sheet of equilateral triangles folds into a pillow, two triangles sewn along their edges, with its corners at the three cube roots of 1 on the equator. Multiplying the sheet by n multiplies both angular directions at once, so nothing is drawn toward a pole and no number of planes has to be chosen. Along the equator the angle is multiplied by n exactly. Each triangle is laid on its half of the sphere with the corner weights passed through sines, then lifted so that areas keep their share. A product of two different points, as in c·z, is taken the way the sphere-inversion approach takes it with one plane.',
    roundNote: 'Circles do not stay circles. The fold stretches unevenly: on average one direction ends up about twice as stretched as the other.',
    crush: (p, n = S.n) => {
      const k = Math.abs(Math.round(n));
      if (k < 2) return ['ok', k === 0 ? 'At this power every point is sent to (1, 0, 0).' : 'Crushes nothing at this power.' + aprPole(n)];
      return ['part', `Crushes nothing but the origin. Where a direction lands on a corner of the pillow without being one${k === 2 ? ' (60°, 180° and 300° in the plane z = 0)' : ''}, the stretch across the plane drops to zero.` + aprPole(n)];
    },
    smooth: (p, n = S.n) => ['no', 'Continuous everywhere, with no seam and no jump. It is creased, though: the slope changes across the plane z = 0 and across every surface that a power sends onto that plane.' + (aprWhole(n) ? '' : ' A power that is not a whole number is rounded.')],
    slice: ok => (ok ? 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' : 'The plane z = 0 does not follow complex arithmetic.'),
  },
'''

a = "// The power maps in JavaScript: MATH[id](v, n, q)"
b = "const MATH = {\n"
c = "// ---------- wording helpers for the approach texts"
d = "const APPROACHES = [\n"
for mark in (a, b, c, d):
    assert src.count(mark) == 1, mark
src = src.replace(a, JS + a)
src = src.replace(b, b + "  pillow(v, n) { return pilPower(v, n); },\n")
src = src.replace(c, GL + c)
src = src.replace(d, d + ENTRY)
with open(os.path.join(HERE, "10-approaches.js"), "w", encoding="utf-8", newline="\n") as f:
    f.write(src)
print("wrote out/proto/sine/10-approaches.js (%d bytes)" % len(src))
