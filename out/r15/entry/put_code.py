"""Round 15, entry: put the code of the Square pillow into src/js/10-approaches.js (run once; texts come from put_texts.py)."""
import io, sys
P = 'src/js/10-approaches.js'
s = io.open(P, encoding='utf-8').read()
if 'spPower' in s:
    sys.exit('already there')

HELP = r'''// ---------- helpers of the rule of round 15, Square pillow (its checks and pictures: out/r15/entry/)
// Directions are laid on a square pillowcase: s runs round the pillow (one full turn is 1), t from the south seam
// (0) to the north seam (1/2), and each seam is zipped shut. For the whole power m the belt t0 = 1/(m + 1) is the
// equator, with s the longitude. Each half sphere is laid out the same way: p = (x, y)/(1 + |z|) =
// ((1 + B²)/2 · cos 2πs, B · sin 2πs), B = 1 on the equator and B = 0 on the seam. North of the belt
// B = sinh(bn·(1/2 − t))/sinh(bn·wn), south of it B = sinh(bs·t)/sinh(bs·ws), with wn = 1/2 − t0 and ws = t0 the widths
// of the two strips and b·coth(b·width) = 2π, so that a step along t and a step along s are the same length on the belt.
// The power multiplies s and t by m (with a mirror, s -> −s) and folds the result back onto the pillow.
const SP_MAXN = 2;     // the layout is made for the whole powers 2 to SP_MAXN (b·coth(b·ws) = 2π has no answer above 5)
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
'''
mark = '// The power maps in JavaScript: MATH[id](v, n, q) with q the approach\'s parameter object.'
assert s.count(mark) == 1
s = s.replace(mark, HELP + mark)

M = '''  kleinsq2(v, n) { return kqPower(v, n, true); },
'''
assert s.count(M) == 1
s = s.replace(M, M + '''  // ----- round 15
  // Square pillow: both coordinates of a pillowcase grid are multiplied (see spPower).
  sqpillow(v, n) { return spPower(v, n); },
''')

GL = r'''// ----- round 15 (the same steps as the JavaScript above: spLayout, spBeta, spTurn, spPower)
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
'''
mark = '\n// ---------- wording helpers for the approach texts'
assert s.count(mark) == 1
s = s.replace(mark, GL + mark)

G = "  { id: 'quaternion', title: 'Quaternions' },\n"
assert s.count(G) == 1
s = s.replace(G, G + "  { id: 'pillow', title: 'Doubling on a pillow grid' },\n")

T = '''// R14-TEXTS-END
'''
assert s.count(T) == 1
s = s.replace(T, T + '''
// ---------- the words of the entry of round 15 (measured in out/r15/entry/: see checks.txt there)
// R15-TEXTS-BEGIN
const SP_TAG = 'Lay the directions on a square pillowcase grid and multiply both of its coordinates.';
const SP_NOTE = 'Texts to come.';
const SP_ABOUT = 'Texts to come.';
const SP_ROUND = '';
const SP_CRUSH = 'Nothing but the origin is crushed.';
const SP_SMOOTH = 'Texts to come.';
const SP_SLICE = 'The plane z = 0 follows complex arithmetic exactly, so that slice is the flat set.';
const spFormula = n => 'Texts to come.';
// R15-TEXTS-END
''')

E = '''    slice: () => KQ2_SLICE,
  },
];'''
assert s.count(E) == 1
s = s.replace(E, '''    slice: () => KQ2_SLICE,
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
    crush: (p, n = S.n) => (aprIs(n, 0) ? ['no', 'At n = 0 every point is sent onto the sphere of radius 1.'] : ['part', SP_CRUSH + aprPole(n)]),
    smooth: (p, n = S.n) => ['no', SP_SMOOTH],
    slice: (ok, p, n = S.n) => SP_SLICE,
  },
];''')
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('written')
