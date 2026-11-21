"""Round 20, entry: add the rule "Wind, then square" (id windsq) to src/js/10-approaches.js. Idempotent.
Code only (helper, MATH mirror, shader, entry with draft texts between R20-TEXTS marks); put_texts.py writes the final texts.
Run from the project root: python out/r20/entry/patch1.py"""
import io, sys
p = 'src/js/10-approaches.js'
s = io.open(p, encoding='utf-8', newline='').read()
if 'wsPower' in s:
    print('already patched'); sys.exit(0)
def ins(s, anchor, new, name, before=True):
    if s.count(anchor) != 1:
        sys.exit('PATCH FAILED (%s): anchor found %d times' % (name, s.count(anchor)))
    print('  done:', name)
    return s.replace(anchor, new + anchor if before else anchor + new)

HELPER = r"""// ---------- helper of the rule of round 20, Wind, then square (its checks and pictures: out/r20/entry/)
// The other planes through the x-axis get no arithmetic of their own. The turn a of a point round the x-axis (0 on
// the side y > 0 of the plane z = 0) is first wound, a -> g(a) = k·a − (k − 1)·sin(2k·a)/(2k), and then the one-plane
// power P is taken, with nothing turned back:   F(v) = P(x, ρ·cos g, ρ·sin g),   ρ the distance of v from the x-axis.
// k is a whole odd number: m, the whole number nearest to |n| (at least 1), or m + 1 when m is even (an even count
// would send the half y < 0 of the plane z = 0 onto the half y > 0). g has slope 1 wherever g(a) is a multiple of
// 180°: those 2k half-planes are sent into the plane z = 0 with no squeeze. cos and sin of k·a come from multiplying
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
"""
s = ins(s, "// The power maps in JavaScript: MATH[id](v, n, q) with q the approach's parameter object.", HELPER, 'helper')

s = ins(s, "  turnalong(v, n) { return tpPower(v, n, true); },\n",
        "  // ----- round 20\n  // Wind, then square: the turn round the x-axis is wound a whole odd number of times, then the one-plane power (see wsPower).\n  windsq(v, n) { return wsPower(v, n); },\n", 'MATH', before=False)

GL = r"""// ----- round 20
// Wind, then square (see wsPower): the turn round the x-axis is wound k times, k whole and odd, with slope 1 where the
// wound turn is a multiple of 180°, and then the one-plane power is taken. No dials. The product of two different
// points is the one-plane product (aprMmul).
const GL_WINDSQ = GL_APR + GL_TRIED_MERC + `
float wsCount(float n){ float m = max(1.0, floor(abs(n) + 0.5)); return mod(m, 2.0) > 0.5 ? m : m + 1.0; }
vec3 wsOne(vec3 v, float n){ return n == 2.0 ? aprMsq(v) : aprMpw(v, n); }
vec3 wsPw(vec3 v, float n){
  if (v.z == 0.0){ vec3 w = wsOne(v, n); return vec3(w.xy, 0.0); }
  float k = wsCount(n), rho = length(v.yz);
  if (k < 1.5 || !(rho > 1e-18)) return wsOne(v, n);
  vec2 u = v.yz / rho, e = u;
  int kk = int(k + 0.5);
  for (int i = 1; i < 16; i++){ if (i >= kk) break; e = cmul(e, u); }
  float d = (k - 1.0) * e.x * e.y / k;
  return wsOne(vec3(v.x, rho * cmul(e, vec2(cos(d), -sin(d)))), n);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return wsPw(a, n); }
vec3 sqr(vec3 a){ return wsPw(a, 2.0); }
vec3 cmap(vec3 c){ return c; }`;
"""
s = ins(s, "\n// ---------- wording helpers for the approach texts", "\n" + GL.rstrip("\n"), 'shader')

TEXTS = r"""
// ---------- the words of the entry of round 20 (measured in out/r20/entry/: see checks.txt there)
// R20-TEXTS-BEGIN
const WS_TAG = 'TEXT PENDING';
const WS_NOTE = 'TEXT PENDING';
const WS_ABOUT = 'TEXT PENDING';
const WS_ROUND = 'TEXT PENDING';
const wsCrush = n => 'TEXT PENDING';
const wsSmooth = n => 'TEXT PENDING';
const wsSlice = (ok, n) => 'TEXT PENDING';
const wsFormula = n => 'TEXT PENDING';
// R20-TEXTS-END
"""
s = ins(s, "\nconst APPROACHES = [\n", TEXTS, 'texts')

ENTRY = r"""  // ----- Round 20: one rule built from Sphere inversions, one plane, so it stands in its group, at the end of this
  // list so that the entries before it keep their places. What its texts say was measured in out/r20/entry/.
  {
    id: 'windsq', name: 'Wind, then square', group: 'inversions', glsl: GL_WINDSQ, axis: () => [1, 0, 0],
    tag: WS_TAG,
    params: [{ type: 'note', text: WS_NOTE }],
    formula: (p, n) => wsFormula(n),
    about: WS_ABOUT,
    roundNote: () => WS_ROUND,
    crush: (p, n = S.n) => (aprIs(n, 0) ? aprNone() : ['part', wsCrush(n) + aprPole(n)]),
    smooth: (p, n = S.n) => (aprIs(n, 0) ? aprConstant() : [aprWhole(n) ? 'part' : 'no', wsSmooth(n) + aprTear(n, APR_HALF)]),
    slice: (ok, p, n = S.n) => wsSlice(ok, n),
  },
"""
if not s.rstrip().endswith("];"):
    sys.exit('PATCH FAILED: the file does not end with the APPROACHES list')
i = s.rstrip().rfind("];")
s = s[:i] + ENTRY + s[i:]
print('  done: entry')
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
