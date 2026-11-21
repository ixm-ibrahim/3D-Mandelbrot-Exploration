"""Build out/lab2/softfold/10-approaches.js: the frozen base4/js/10-approaches.js with the soft fold added
as the FIRST entry of APPROACHES (JavaScript mirror in MATH, shader code in GL_SOFTFOLD).
   python out/lab2/softfold/make_approach.py [default blend]
then
   python build.py --name lab2-softfold --base base4 --swap js/10-approaches.js=out/lab2/softfold/10-approaches.js
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEF_BLEND = sys.argv[1] if len(sys.argv) > 1 else '0.25'
src = open(os.path.join(ROOT, 'base4', 'js', '10-approaches.js'), encoding='utf-8').read().replace('\r\n', '\n')

HELPERS = r"""// ---------- soft fold (prototype, out/lab2/softfold). The one-plane rule of Sphere inversions is kept exactly on each of
// p planes through the x-axis, and between two neighbouring planes the two rules are blended along the great
// circle between their directions.
// sfDir: the direction of the one-plane power of the unit direction d (longitude and Mercator latitude times n).
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
"""

MIRROR = r"""  softfold(v, n, q = {}) {
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
    else if (q.mix > 0.5 && !pinch) {                                 // straight blend, renormalised
      const m = [A[0] + s * (B[0] - A[0]), A[1] + s * (B[1] - A[1]), A[2] + s * (B[2] - A[2])], lm = Math.hypot(m[0], m[1], m[2]);
      D = lm < 1e-3 ? (s < 0.5 ? A : B) : [m[0] / lm, m[1] / lm, m[2] / lm];
    } else {                                                // along the great circle from A to B
      const c = clamp(A[0] * B[0] + A[1] * B[1] + A[2] * B[2], -1, 1), e = [B[0] - c * A[0], B[1] - c * A[1], B[2] - c * A[2]], le = Math.hypot(e[0], e[1], e[2]);
      if (c < 0 && le < 1e-3) D = s < 0.5 ? A : B;          // opposite directions: no one great circle joins them, take the nearer plane's
      else { const om = Math.atan2(le, c) * s, g = Math.sin(om) / Math.max(le, 1e-30), cs = Math.cos(om); D = [cs * A[0] + g * e[0], cs * A[1] + g * e[1], cs * A[2] + g * e[2]]; }
    }
    return [R * D[0], R * fl * (D[1] * cj - D[2] * sj), R * fl * (D[1] * sj + D[2] * cj)];
  },
"""

GLSL = r"""// Soft fold. uA = (planes, width of each plane's own band, curve: 0 smoothstep 1 smootherstep, mix: 0 great circle 1 straight 2 pinch).
// mul of two different vectors is the one-plane product of Sphere inversions (aprMmul there), copied unchanged;
// cmap is the identity: the constant is not folded.
const GL_SOFTFOLD = GL_APR + `
vec3 mul(vec3 a, vec3 b){
  float ra = length(a), rb = length(b);
  if (ra < 1e-20 || rb < 1e-20) return vec3(0.0);
  float Za = a.z / ra, Zb = b.z / rb;
  float Z = clamp((Za + Zb) / max(1.0 + Za * Zb, 1e-6), -1.0, 1.0);
  float la = length(a.xy), lb = length(b.xy);
  vec2 u = la > 0.0 && lb > 0.0 ? cmul(a.xy / la, b.xy / lb) : vec2(1.0, 0.0);
  return min(ra * rb, APR_CAP) * vec3(sqrt(max(0.0, 1.0 - Z * Z)) * u, Z);
}
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
    // power, the seam's own direction for an odd one (see the JavaScript mirror)
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

"""

ENTRY = r"""  {
    id: 'softfold', name: 'Soft fold', glsl: GL_SOFTFOLD, axis: p => (p.planes > 1 ? [1, 0, 0] : [0, 0, 1]),
    tag: 'Sphere inversions on several planes through the x-axis, joined by a smooth blend instead of a fold.',
    params: [
      { type: 'dial', key: 'planes', label: 'Planes that carry the flat set', min: 1, max: 4, step: 1, def: 2, int: true },
      { type: 'dial', key: 'blend', label: 'Each plane’s own band', min: 0, max: 0.45, step: 0.01, def: __BLEND__, lo: 0, hi: 0.49, when: p => p.planes > 1, help: 'How much of the way to the next plane the rule stays exactly the plane’s own, before the blend starts. At 0 the blend fills the whole gap. Near 0.5 the blend is squeezed into a thin sheet half way and the picture tends to the folded one.' },
      { type: 'select', key: 'curve', label: 'Blend curve', def: 0, options: [[0, 'Smoothstep'], [1, 'Smootherstep']], when: p => p.planes > 1 },
      { type: 'select', key: 'mix', label: 'Blend along', def: 0, options: [[0, 'The great circle between the two answers'], [1, 'The straight line between them'], [2, 'No blend: pinch each seam onto the x-axis']], when: p => p.planes > 1 },
    ],
    formula: (p, n) => (p.planes < 2 ? 'vⁿ = |v|ⁿ · (cos nφ / cosh nm, sin nφ / cosh nm, tanh nm)   with φ the longitude and m the latitude as a Mercator map stretches it: the Sphere inversions rule with one plane.'
      : `vⁿ = |v|ⁿ · blend(Fₖ(d), Fₖ₊₁(d), S(t))   with d the direction of v, Fₖ the Sphere inversions rule built on the k-th of ${p.planes} planes through the x-axis, t how far the half-plane holding v has turned from plane k to plane k + 1, and S a smooth step that stays at 0 for the first ${aprNum(p.blend)} of the way and at 1 for the last ${aprNum(p.blend)}.`),
    about: 'A prototype. The Sphere inversions rule is built on each of several planes through the x-axis, so each of those planes carries the flat set exactly. Between two neighbouring planes the two answers are blended: the result is a point on the great circle between them, moving smoothly from one to the other. Nothing jumps, and the constant c is used as it is.',
    roundNote: (p, n) => (p.planes < 2 ? 'Circles on the sphere stay circles (see the step view).' : 'Inside each plane’s own band circles on the sphere stay circles. In the blend between two bands they do not.'),
    crush: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprNone();
      return ['part', (p.planes < 2 ? 'Crushes the z-axis only.' : 'Crushes the poles of each plane’s own band, when the band is wide enough to hold them.') + aprPole(n)];
    },
    smooth: (p, n = S.n) => {
      if (aprIs(n, 0)) return aprConstant();
      if (p.planes < 2) return aprWhole(n) ? ['part', 'Smooth everywhere except the origin.'] : ['no', 'Smooth for whole powers only.' + aprTear(n, APR_HALF)];
      return ['part', 'No jumps for n = 2. The blend is steep where the bands are wide, and for other powers a few single directions can be torn where the two answers point opposite ways.' + aprTear(n, APR_HALF)];
    },
    slice: (ok, p) => (!ok ? 'The plane z = 0 does not follow complex arithmetic.'
      : p.planes < 2 ? 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.' : `${p.planes} planes through the x-axis follow complex arithmetic exactly, z = 0 among them.`),
  },
"""

def put(text, marker, block, after=False):
    i = text.index(marker)
    if after: i += len(marker)
    return text[:i] + block + text[i:]

out = put(src, 'const MATH = {\n', HELPERS)
out = put(out, '  mercator(v, n, q = {}) {\n', MIRROR)
out = put(out, '// ---------- wording helpers for the approach texts\n', GLSL)
out = put(out, 'const APPROACHES = [\n', ENTRY.replace('__BLEND__', DEF_BLEND), after=True)
with open(os.path.join(HERE, '10-approaches.js'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('wrote out/lab2/softfold/10-approaches.js (%d bytes, default blend %s)' % (len(out), DEF_BLEND))
