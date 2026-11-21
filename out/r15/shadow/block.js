// R15B-BEGIN
// ---------- Pillow from 4D (closed form), round 15B. Checks and pictures: out/r15/shadow/ (reference: out/me/r15/shadow_ref.py).
// In 4D, as two complex numbers of the same length ρ: (z1, z2) -> (conj(z1)^m, z2^m). A 3D point stands for the pair
// together with its mirror pair, through three numbers: x1 = Re z1, x2 = Re z2, w = Im z1 · Im z2 / ρ. In them the rule
// is polynomial (Chebyshev T_m and U_(m-1)). The picture's coordinates lay the belt x2 = ρ·cos(2π/(m + 1)) on the plane
// z = 0:  x = x1,  y = s0·ρ·w/(ρ − c0·x2),  z = (c0·ρ − x2)/s0.  They are of degree 1 in ρ, so ρ is a gauge: ρ(v) = |v|·ρ(v/|v|).
const P4_MAXN = 10;                                                             // the largest power on the dial
const p4Whole = n => clamp(Math.floor(Math.abs(n) + 0.5), 2, P4_MAXN);          // the whole power the layout is made for
// cos and sin of the belt angle 2π/(m + 1), exact where they are simple numbers (m = 3 is then mirror-symmetric to the last bit)
function p4Belt(m) {
  if (m === 2) return [-0.5, Math.sqrt(0.75)];
  if (m === 3) return [0, 1];
  if (m === 5) return [0.5, Math.sqrt(0.75)];
  const b = 2 * PI / (m + 1);
  return [Math.cos(b), Math.sin(b)];
}
// The gauge ρ of a unit direction d: the root of the quartic (ρ² − x²)(ρ² − x2²) = y²(s0·ρ + c0·z)², x2 = c0·ρ − s0·z,
// that lies above |x| and above the seam bound rs. Written as (ρ − |x|)(ρ − rs)·K = y²·C² with K and C positive and slowly
// varying, it is the fixed point ρ = mid + √(half² + y²C²/K), found by Newton steps (5 here; 4 already reach 1e-15, measured
// in out/r15/shadow/gauge_proto2.py). Plain Newton on the quartic stalls beside the seams, where two roots run together.
function p4Gauge(d, c0, s0) {
  const aX = Math.abs(d[0]), aZ = Math.abs(d[2]), Y2 = d[1] * d[1];
  const kE = d[2] >= 0 ? 1 + c0 : 1 - c0, dE = d[2] >= 0 ? 1 - c0 : 1 + c0, rs = s0 * aZ / kE;
  const mid = 0.5 * (aX + rs), half = 0.5 * (aX - rs), lo = Math.max(aX, rs), hi = 1.0001 * Math.max((1 - c0) / s0, (1 + c0) / s0);
  if (!(Y2 > 0)) return lo;
  let x = clamp(1, lo, hi);
  for (let i = 0; i < 5; i++) {
    const C = s0 * x + c0 * d[2], E = dE * x + s0 * aZ;
    const K = Math.max((x + aX) * kE * E, 1e-30), R = Y2 * C * C / K, sq = Math.sqrt(half * half + R);
    const dR = R * (2 * s0 / Math.max(C, 1e-30) - 1 / Math.max(x + aX, 1e-30) - dE / Math.max(E, 1e-30));
    const dphi = 1 - dR / Math.max(2 * sq, 1e-30);
    x = clamp(dphi > 0.2 ? x - (x - mid - sq) / dphi : mid + sq, lo, hi);
  }
  return x;
}
// v^n for the whole power m nearest to n (2 to P4_MAXN): ρ^n times the point of the pillow that the direction is sent to.
// A point with z exactly 0 takes the exact complex power and comes out with z exactly 0.
function p4Power(v, n) {
  const m = p4Whole(n), r = Math.hypot(v[0], v[1], v[2]), cap = 1.74e18;
  if (r < 1e-20) return n > 0 ? [0, 0, 0] : [aprPow(r, n), 0, 0];
  if (v[2] === 0 && n === 2) {
    const o = [v[0] * v[0] - v[1] * v[1], 2 * v[0] * v[1], 0], big = Math.max(Math.abs(o[0]), Math.abs(o[1]));
    return big > cap ? [o[0] * cap / big, o[1] * cap / big, 0] : o;
  }
  let h, g = 1;
  if (v[2] === 0) {
    const u = [v[0] / r, v[1] / r];
    let e = u;
    for (let i = 1; i < m; i++) e = [e[0] * u[0] - e[1] * u[1], e[0] * u[1] + e[1] * u[0]];
    h = [e[0], e[1], 0];
  } else {
    const [c0, s0] = p4Belt(m), d = [v[0] / r, v[1] / r, v[2] / r];
    g = p4Gauge(d, c0, s0);
    const u1 = clamp(d[0] / g, -1, 1), u2 = clamp(c0 - s0 * d[2] / g, -1, 1), wr = d[1] * (s0 * g + c0 * d[2]) / (g * g);
    let T = [1, u1, 1, u2], U = [0, 1, 0, 1];             // (T_(k-1), T_k) and (U_(k-2), U_(k-1)) of u1, then the same of u2
    for (let i = 1; i < m; i++) {
      T = [T[1], 2 * u1 * T[1] - T[0], T[3], 2 * u2 * T[3] - T[2]];
      U = [U[1], 2 * u1 * U[1] - U[0], U[3], 2 * u2 * U[3] - U[2]];
    }
    h = [T[1], -s0 * wr * U[1] * U[3] / (1 - c0 * T[3]), (c0 - T[3]) / s0];
  }
  const rho = r * g, R = n === 2 ? Math.min(rho * rho, cap) : aprPow(rho, n);
  if (n < 0) h = [h[0], -h[1], -h[2]];
  return [R * h[0], R * h[1], R * h[2]];
}
MATH.pillow4d = (v, n) => p4Power(v, n);
// The shader: the same steps (p4Belt, p4Gauge with 4 Newton steps, p4Power). No dials. The product of two different
// points is the one-plane product of Sphere inversions (aprMmul).
// About the length: the rule's own length is the gauge ρ, not |v| (ρ² in, ρ^n out). The orbit code tests |v| against
// the escape radius 64 and reads the distance from how fast log|v| changes. |v| lies between 0.29 and 3.5 times ρ at
// every power on the dial, and an orbit that has left ρ = 5 never comes back at n = 2, so the test picks the same points.
// |F(v)| is not |v|^n, so the lab's probe switches the one-number estimate off by itself and neighbouring orbits are used.
const GL_PILLOW4D = GL_APR + GL_TRIED_MERC + `
const float P4_MAXN = ${P4_MAXN}.0;
vec2 p4Belt(float m){
  if (m < 2.5) return vec2(-0.5, 0.8660254037844386);
  if (m < 3.5) return vec2(0.0, 1.0);
  if (m > 4.5 && m < 5.5) return vec2(0.5, 0.8660254037844386);
  float b = 2.0 * PI / (m + 1.0);
  return vec2(cos(b), sin(b));
}
float p4Gauge(vec3 d, float c0, float s0){
  float aX = abs(d.x), aZ = abs(d.z), Y2 = d.y * d.y;
  float kE = d.z >= 0.0 ? 1.0 + c0 : 1.0 - c0, dE = d.z >= 0.0 ? 1.0 - c0 : 1.0 + c0, rs = s0 * aZ / kE;
  float mid = 0.5 * (aX + rs), half_ = 0.5 * (aX - rs), lo = max(aX, rs), hi = 1.0001 * max((1.0 - c0) / s0, (1.0 + c0) / s0);
  if (!(Y2 > 0.0)) return lo;
  float x = clamp(1.0, lo, hi);
  for (int i = 0; i < 4; i++){
    float C = s0 * x + c0 * d.z, E = dE * x + s0 * aZ;
    float K = max((x + aX) * kE * E, 1e-30), R = Y2 * C * C / K, sq = sqrt(half_ * half_ + R);
    float dR = R * (2.0 * s0 / max(C, 1e-30) - 1.0 / max(x + aX, 1e-30) - dE / max(E, 1e-30));
    float dphi = 1.0 - dR / max(2.0 * sq, 1e-30);
    x = clamp(dphi > 0.2 ? x - (x - mid - sq) / dphi : mid + sq, lo, hi);
  }
  return x;
}
vec3 p4Pw(vec3 v, float n){
  float m = clamp(floor(abs(n) + 0.5), 2.0, P4_MAXN), r = length(v), g = 1.0;
  if (r < 1e-20) return n > 0.0 ? vec3(0.0) : vec3(aprPow(r, n), 0.0, 0.0);
  if (v.z == 0.0 && n == 2.0) return aprCap(vec3(v.x * v.x - v.y * v.y, 2.0 * v.x * v.y, 0.0));
  vec3 h;
  if (v.z == 0.0){
    vec2 u = v.xy / r, e = u;
    for (int i = 1; i < 10; i++){ if (float(i) > m - 0.5) break; e = cmul(e, u); }
    h = vec3(e, 0.0);
  } else {
    vec2 cs = p4Belt(m);
    vec3 d = v / r;
    g = p4Gauge(d, cs.x, cs.y);
    float u1 = clamp(d.x / g, -1.0, 1.0), u2 = clamp(cs.x - cs.y * d.z / g, -1.0, 1.0);
    float wr = d.y * (cs.y * g + cs.x * d.z) / (g * g);
    vec4 T = vec4(1.0, u1, 1.0, u2), U = vec4(0.0, 1.0, 0.0, 1.0);
    for (int i = 1; i < 10; i++){
      if (float(i) > m - 0.5) break;
      T = vec4(T.y, 2.0 * u1 * T.y - T.x, T.w, 2.0 * u2 * T.w - T.z);
      U = vec4(U.y, 2.0 * u1 * U.y - U.x, U.w, 2.0 * u2 * U.w - U.z);
    }
    h = vec3(T.y, -cs.y * wr * U.y * U.w / (1.0 - cs.x * T.w), (cs.x - T.w) / cs.y);
  }
  float rho = r * g, R = n == 2.0 ? min(rho * rho, APR_CAP) : aprPow(rho, n);
  if (n < 0.0) h.yz = -h.yz;
  return R * h;
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return p4Pw(a, n); }
vec3 sqr(vec3 a){ return p4Pw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
// ----- the words of the entry (measured in out/r15/shadow/: checks.txt, skin.txt, sheet-pillow4d.png)
const p4Own = n => aprWhole(n) && n >= 2 && n <= P4_MAXN;                        // a power the rule is made for
//__P4_TEXTS__
const P4_ENTRY = {
  id: 'pillow4d', name: 'Pillow from 4D (closed form)', group: 'pillow', glsl: GL_PILLOW4D, axis: () => [0, 0, 1],
  tag: P4_TAG,
  params: [{ type: 'note', text: P4_NOTE }],
  formula: (p, n) => p4Formula(n),
  about: P4_ABOUT,
  roundNote: () => P4_ROUND,
  crush: (p, n = S.n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto one closed surface, the pillow itself.'] : ['part', P4_CRUSH + aprPole(n)]),
  smooth: (p, n = S.n) => ['part', P4_SMOOTH + (p4Own(n) ? '' : P4_OTHER)],
  slice: (ok, p, n = S.n) => (p4Own(n) && ok ? P4_SLICE : p4Own(n) ? 'The plane z = 0 does not follow complex arithmetic.' : P4_SLICE_OTHER),
};
// R15B-END
