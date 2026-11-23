// The custom approach: a rule the user puts together from steps (S.custom.steps). One pass of the steps is one
// whole step of the orbit, z -> ..., the adding of c included, which is a step like any other.
//
// Everything is written in one small formula language. A line is `name = formula`, and every kind of step is a
// few such lines with its settings put in (CU_BLOCKS[kind].lines). There are three levels of step: a block (a
// sphere inversion, a turn about an axis, ...), a formula line, and a single operation (add, dot product, sine,
// ...). "Break down" goes one level down: a block becomes its lines, a line becomes its operations.
// A line is read once (cuParse) into both of its forms: shader text, and a JavaScript function that works out the
// same thing, so the picture, the scorecard and the Learn tab all follow one text.
//
// A formula knows four kinds of thing: a number (s), a point or vector (v), a quaternion (q) and a 3 by 3 matrix
// (m). In JavaScript they are a number, [x, y, z], [x, y, z, w] with w the real part, and nine numbers column by
// column; in the shader float, vec3, vec4 (xyz the i, j, k parts, w the real part) and mat3.
//
// A number typed as a setting does not go into the shader text. It goes into a slot of the uniform uCu, and so
// does each step's on/off switch: moving a slider or switching a step never makes a new shader program. The last
// four slots say where a play through the steps stands (cuPlayNow), so playing makes no new program either.
const CU_SLOTS = 128;        // the size of uCu
const CU_FREE = 124;         // slots 0 .. 123 are for the steps; then CU_PLAY_T, _ON, _PASS, _ORD
const CU_PLAY_T = 124, CU_PLAY_ON = 125, CU_PLAY_PASS = 126, CU_PLAY_ORD = 127;
const CU_MAX_STEPS = 80;
const CU_CAP = 1.74e18;      // APR_CAP of the shader
const CU_BAIL = 2;           // a new rule throws a point out when it lands further than this from the middle
const CU_KEY = 'squaringLab.custom';
const CU_KINDS = { s: 'a number', v: 'a point', q: 'a quaternion', m: 'a matrix' };
const CU_GLTYPE = { s: 'float', v: 'vec3', q: 'vec4', m: 'mat3' };
const CU_GLZERO = { s: '0.0', v: 'vec3(0.0)', q: 'vec4(0.0)', m: 'mat3(0.0)' };
const CU_ZERO = { s: () => 0, v: () => [0, 0, 0], q: () => [0, 0, 0, 0], m: () => [0, 0, 0, 0, 0, 0, 0, 0, 0] };
const CU_NUM = '[-+]?(?:\\d+\\.?\\d*|\\.\\d+)(?:e[-+]?\\d+)?';
const CU_NUMBER = new RegExp(`^${CU_NUM}$`, 'i');
const CU_VEC3 = new RegExp(`^vec\\(\\s*(${CU_NUM})\\s*,\\s*(${CU_NUM})\\s*,\\s*(${CU_NUM})\\s*\\)$`, 'i');
const CU_NAME = /^[A-Za-z][A-Za-z0-9]*$/;
// what a formula may read besides the names it has made itself
const CU_GIVEN = { z: 'v', c: 'v', n: 's', pi: 's', first: 'v', last: 'v', mean: 'v', count: 's' };
const cuFlt = x => (Number.isInteger(x) && Math.abs(x) < 1e15 ? x + '.0' : String(x));
const cuDash = text => String(text).replace(/[−–]/g, '-').trim();
const cuNum = text => parseFloat(cuDash(text));
const cuIsNum = text => CU_NUMBER.test(cuDash(text));
// the three numbers of a point typed as vec(1, 0, 0), or null for any other formula
const cuXyz = text => { const m = CU_VEC3.exec(cuDash(text)); return m ? [parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3])] : null; };

// The arithmetic of the JavaScript side. Each function is the twin of the shader function of the same name in CU_GLSL.
const cuDivS = (a, b) => a / (Math.abs(b) < 1e-30 ? (b < 0 ? -1e-30 : 1e-30) : b);
const cuSPow = (a, b) => (Math.abs(a) < 1e-30 && b > 0 ? 0 : aprPow(Math.abs(a), b) * (a < 0 ? Math.cos(PI * b) : 1));
const cuUnit = v => { const l = len(v); return l > 1e-30 ? scl(v, 1 / l) : [0, 0, 0]; };
function cuRot(v, ax, a) {
  const k = cuUnit(ax), c = Math.cos(a), s = Math.sin(a), d = dot(k, v) * (1 - c), x = cross(k, v);
  return [v[0] * c + x[0] * s + k[0] * d, v[1] * c + x[1] * s + k[1] * d, v[2] * c + x[2] * s + k[2] * d];
}
const cuInvert = (v, o, r) => { const d = sub(v, o); return add(o, scl(d, cuDivS(r * r, dot(d, d)))); };
const cuMirror = (v, nrm) => { const k = cuUnit(nrm); return sub(v, scl(k, 2 * dot(v, k))); };
const cuSph = (r, lo, la) => { const cl = Math.cos(la); return [r * cl * Math.cos(lo), r * cl * Math.sin(lo), r * Math.sin(la)]; };
const cuLat = v => { const l = len(v); return l > 1e-30 ? Math.asin(clamp(v[2] / l, -1, 1)) : 0; };
function cuCpow(v, n) {
  const l = Math.hypot(v[0], v[1]);
  if (l < 1e-30 && n > 0) return [0, 0, v[2]];
  const a = Math.atan2(v[1], v[0]) * n, R = aprPow(l, n);
  return [R * Math.cos(a), R * Math.sin(a), v[2]];
}
function cuQmul(a, b) {
  return [a[3] * b[0] + b[3] * a[0] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] + b[3] * a[1] + a[2] * b[0] - a[0] * b[2],
    a[3] * b[2] + b[3] * a[2] + a[0] * b[1] - a[1] * b[0], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
}
const cuQconj = q => [-q[0], -q[1], -q[2], q[3]];
const cuQinv = q => { const k = cuDivS(1, q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]); return [-q[0] * k, -q[1] * k, -q[2] * k, q[3] * k]; };
function cuQpow(q, p) {
  const r = Math.hypot(q[0], q[1], q[2], q[3]);
  if (r < 1e-30 && p > 0) return [0, 0, 0, 0];
  const vn = Math.hypot(q[0], q[1], q[2]), th = Math.atan2(vn, q[3]) * p, R = aprPow(r, p), s = Math.sin(th) * R;
  const u = vn > 1e-30 ? [q[0] / vn, q[1] / vn, q[2] / vn] : [1, 0, 0];
  return [u[0] * s, u[1] * s, u[2] * s, Math.cos(th) * R];
}
const cuTurn = (v, q) => cuQmul(cuQmul(q, [v[0], v[1], v[2], 0]), cuQinv(q)).slice(0, 3);
const cuQrot = (ax, a) => { const k = cuUnit(ax), s = Math.sin(0.5 * a); return [k[0] * s, k[1] * s, k[2] * s, Math.cos(0.5 * a)]; };
function cuRotmat(ax, a) {
  const k = cuUnit(ax), c = Math.cos(a), s = Math.sin(a), t = 1 - c;
  return [t * k[0] * k[0] + c, t * k[0] * k[1] + s * k[2], t * k[0] * k[2] - s * k[1],
    t * k[0] * k[1] - s * k[2], t * k[1] * k[1] + c, t * k[1] * k[2] + s * k[0],
    t * k[0] * k[2] + s * k[1], t * k[1] * k[2] - s * k[0], t * k[2] * k[2] + c];
}
const cuMV = (m, v) => [m[0] * v[0] + m[3] * v[1] + m[6] * v[2], m[1] * v[0] + m[4] * v[1] + m[7] * v[2], m[2] * v[0] + m[5] * v[1] + m[8] * v[2]];
const cuMM = (a, b) => [0, 3, 6].flatMap(j => cuMV(a, [b[j], b[j + 1], b[j + 2]]));
const cuMT = m => [m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]];
const cuDet = m => m[0] * (m[4] * m[8] - m[7] * m[5]) - m[3] * (m[1] * m[8] - m[7] * m[2]) + m[6] * (m[1] * m[5] - m[4] * m[2]);
function cuMinv(m) {
  const d = cuDet(m);
  if (Math.abs(d) < 1e-30) return CU_ZERO.m();
  const k = 1 / d;
  return [(m[4] * m[8] - m[7] * m[5]) * k, (m[7] * m[2] - m[1] * m[8]) * k, (m[1] * m[5] - m[4] * m[2]) * k,
    (m[6] * m[5] - m[3] * m[8]) * k, (m[0] * m[8] - m[6] * m[2]) * k, (m[3] * m[2] - m[0] * m[5]) * k,
    (m[3] * m[7] - m[6] * m[4]) * k, (m[6] * m[1] - m[0] * m[7]) * k, (m[0] * m[4] - m[3] * m[1]) * k];
}
const CU_GLSL = `
float cuDivS(float a, float b){ return a / (abs(b) < 1e-30 ? (b < 0.0 ? -1e-30 : 1e-30) : b); }
vec3 cuUnit(vec3 v){ float l = length(v); return l > 1e-30 ? v / l : vec3(0.0); }
vec3 cuRot(vec3 v, vec3 ax, float a){ vec3 k = cuUnit(ax); float c = cos(a), s = sin(a); return v * c + cross(k, v) * s + k * (dot(k, v) * (1.0 - c)); }
vec3 cuInvert(vec3 v, vec3 o, float r){ vec3 d = v - o; return o + d * cuDivS(r * r, dot(d, d)); }
vec3 cuMirror(vec3 v, vec3 nrm){ vec3 k = cuUnit(nrm); return v - k * (2.0 * dot(v, k)); }
vec3 cuSph(float r, float lo, float la){ float cl = cos(la); return r * vec3(cl * cos(lo), cl * sin(lo), sin(la)); }
float cuLat(vec3 v){ float l = length(v); return l > 1e-30 ? asin(clamp(v.z / l, -1.0, 1.0)) : 0.0; }
vec3 cuCpow(vec3 v, float n){
  float l = length(v.xy);
  if (l < 1e-30 && n > 0.0) return vec3(0.0, 0.0, v.z);
  float a = at2(v.y, v.x) * n;
  return vec3(aprPow(l, n) * vec2(cos(a), sin(a)), v.z);
}
vec4 cuQmul(vec4 a, vec4 b){ return vec4(a.w * b.xyz + b.w * a.xyz + cross(a.xyz, b.xyz), a.w * b.w - dot(a.xyz, b.xyz)); }
vec4 cuQconj(vec4 q){ return vec4(-q.xyz, q.w); }
vec4 cuQinv(vec4 q){ return cuQconj(q) * cuDivS(1.0, dot(q, q)); }
vec4 cuQpow(vec4 q, float p){
  float r = length(q);
  if (r < 1e-30 && p > 0.0) return vec4(0.0);
  float vn = length(q.xyz), th = at2(vn, q.w) * p;
  vec3 u = vn > 1e-30 ? q.xyz / vn : vec3(1.0, 0.0, 0.0);
  return aprPow(r, p) * vec4(u * sin(th), cos(th));
}
vec3 cuTurn(vec3 v, vec4 q){ return cuQmul(cuQmul(q, vec4(v, 0.0)), cuQinv(q)).xyz; }
vec4 cuQrot(vec3 ax, float a){ return vec4(cuUnit(ax) * sin(0.5 * a), cos(0.5 * a)); }
mat3 cuRotmat(vec3 ax, float a){
  vec3 k = cuUnit(ax); float c = cos(a), s = sin(a), t = 1.0 - c;
  return mat3(t * k.x * k.x + c, t * k.x * k.y + s * k.z, t * k.x * k.z - s * k.y,
              t * k.x * k.y - s * k.z, t * k.y * k.y + c, t * k.y * k.z + s * k.x,
              t * k.x * k.z + s * k.y, t * k.y * k.z - s * k.x, t * k.z * k.z + c);
}
mat3 cuMinv(mat3 m){ float d = determinant(m); return abs(d) < 1e-30 ? mat3(0.0) : inverse(m); }
// A point part of the way from a to b. Where a and b are equally far from the middle the step is a turn, and the
// point goes round the middle; otherwise it goes straight across.
vec3 cuBlend(vec3 a, vec3 b, float t){
  vec3 p = mix(a, b, t);
  float la = length(a), lb = length(b), lp = length(p);
  if (abs(la - lb) <= 1e-3 * max(la, lb) && lp > 1e-4 * la) p *= mix(la, lb, t) / lp;
  return p;
}`;
// What an orbit carries. gCuPass: how many passes of the point's own orbit have counted, this one included (a play
// reads it). For the names first, last, mean and count (the same steps as CARRY.custom), per orbit: the number of
// steps that have counted, its first point, the point of the step before, and the sum of its points.
const CU_GLSL_ORBIT = `
float gCuN[4]; vec3 gCuF[4], gCuP[4], gCuL[4], gCuS[4];
void carStart(){
  for (int i = 0; i < 4; i++){ gCuN[i] = 0.0; gCuF[i] = vec3(0.0); gCuP[i] = vec3(0.0); gCuL[i] = vec3(0.0); gCuS[i] = vec3(0.0); }
  gCuC = vec3(0.0); gCuPass = 0.0; gCarI = 0;
}
void carStep(vec3 z, vec3 c){
  gCuC = c;
  if (carOrigin(z)) return;
  if (gCarI == 0) gCuPass += 1.0;
  int i = gCarI;
  gCuN[i] += 1.0;
  if (gCuN[i] == 1.0){ gCuF[i] = z; gCuP[i] = z; }
  gCuL[i] = gCuP[i]; gCuP[i] = z; gCuS[i] += z;
}
void carFit(int i, float s){
  gCuN[i] = gCuN[0];
  gCuF[i] = gCuF[0] + (gCuF[i] - gCuF[0]) * s; gCuP[i] = gCuP[0] + (gCuP[i] - gCuP[0]) * s;
  gCuL[i] = gCuL[0] + (gCuL[i] - gCuL[0]) * s; gCuS[i] = gCuS[0] + (gCuS[i] - gCuS[0]) * s;
}`;
const CU_GLSL_PLAIN = `
void carStart(){ gCuC = vec3(0.0); gCuPass = 0.0; gCarI = 0; }
void carStep(vec3 z, vec3 c){ gCuC = c; if (gCarI == 0 && !carOrigin(z)) gCuPass += 1.0; }
void carFit(int i, float s){ }`;

// The functions of the language: CU_FN[name] is a list of forms, each with the kinds of its arguments (args), the
// kind of its answer (ret), its shader text (gl, from the arguments' shader texts) and its JavaScript (js, from values).
const CU_FN = {};
const cuDef = (name, args, ret, gl, js) => { (CU_FN[name] = CU_FN[name] || []).push({ args, ret, gl, js }); };
for (const name of ['sin', 'cos', 'tan', 'atan', 'sinh', 'cosh', 'tanh', 'abs', 'floor', 'ceil', 'sign']) cuDef(name, 's', 's', a => `${name}(${a})`, Math[name]);
cuDef('asin', 's', 's', a => `asin(clamp(${a}, -1.0, 1.0))`, a => Math.asin(clamp(a, -1, 1)));
cuDef('acos', 's', 's', a => `acos(clamp(${a}, -1.0, 1.0))`, a => Math.acos(clamp(a, -1, 1)));
cuDef('atanh', 's', 's', a => `atanh(clamp(${a}, -0.999999, 0.999999))`, a => Math.atanh(clamp(a, -0.999999, 0.999999)));
cuDef('exp', 's', 's', a => `exp(min(${a}, 80.0))`, a => Math.exp(Math.min(a, 80)));
cuDef('log', 's', 's', a => `log(max(${a}, 1e-30))`, a => Math.log(Math.max(a, 1e-30)));
cuDef('sqrt', 's', 's', a => `sqrt(max(${a}, 0.0))`, a => Math.sqrt(Math.max(a, 0)));
cuDef('round', 's', 's', a => `floor(${a} + 0.5)`, a => Math.floor(a + 0.5));
cuDef('fract', 's', 's', a => `fract(${a})`, a => a - Math.floor(a));
cuDef('rad', 's', 's', a => `radians(${a})`, a => a * PI / 180);
cuDef('deg', 's', 's', a => `degrees(${a})`, a => a * 180 / PI);
cuDef('atan2', 'ss', 's', (a, b) => `at2(${a}, ${b})`, Math.atan2);
cuDef('min', 'ss', 's', (a, b) => `min(${a}, ${b})`, Math.min);
cuDef('max', 'ss', 's', (a, b) => `max(${a}, ${b})`, Math.max);
cuDef('mod', 'ss', 's', (a, b) => `(${a} - ${b} * floor(cuDivS(${a}, ${b})))`, (a, b) => a - b * Math.floor(cuDivS(a, b)));
cuDef('pow', 'ss', 's', (a, b) => `aprSPow(${a}, ${b})`, cuSPow);
cuDef('step', 'ss', 's', (a, b) => `step(${a}, ${b})`, (a, b) => (b < a ? 0 : 1));
cuDef('clamp', 'sss', 's', (a, b, c) => `clamp(${a}, ${b}, ${c})`, (a, b, c) => Math.min(Math.max(a, b), c));
cuDef('smoothstep', 'sss', 's', (a, b, c) => `smoothstep(${a}, ${b}, ${c})`, (a, b, x) => { const t = clamp(cuDivS(x - a, b - a), 0, 1); return t * t * (3 - 2 * t); });
cuDef('mix', 'sss', 's', (a, b, t) => `mix(${a}, ${b}, ${t})`, (a, b, t) => a + (b - a) * t);
for (const k of ['v', 'q']) cuDef('mix', k + k + 's', k, (a, b, t) => `mix(${a}, ${b}, ${t})`, (a, b, t) => a.map((x, i) => x + (b[i] - x) * t));
for (const k of ['s', 'v', 'q', 'm']) cuDef('if', 's' + k + k, k, (c, a, b) => `(${c} > 0.5 ? ${a} : ${b})`, (c, a, b) => (c > 0.5 ? a : b));
cuDef('vec', 'sss', 'v', (a, b, c) => `vec3(${a}, ${b}, ${c})`, (a, b, c) => [a, b, c]);
cuDef('vec', 'q', 'v', a => `${a}.xyz`, a => [a[0], a[1], a[2]]);
cuDef('len', 'v', 's', a => `length(${a})`, len);
cuDef('len', 'q', 's', a => `length(${a})`, a => Math.hypot(a[0], a[1], a[2], a[3]));
cuDef('dot', 'vv', 's', (a, b) => `dot(${a}, ${b})`, dot);
cuDef('cross', 'vv', 'v', (a, b) => `cross(${a}, ${b})`, cross);
cuDef('unit', 'v', 'v', a => `cuUnit(${a})`, cuUnit);
cuDef('abs', 'v', 'v', a => `abs(${a})`, a => a.map(Math.abs));
cuDef('dist', 'vv', 's', (a, b) => `distance(${a}, ${b})`, (a, b) => len(sub(a, b)));
cuDef('each', 'vv', 'v', (a, b) => `(${a} * ${b})`, (a, b) => [a[0] * b[0], a[1] * b[1], a[2] * b[2]]);
cuDef('rot', 'vvs', 'v', (a, b, c) => `cuRot(${a}, ${b}, ${c})`, cuRot);
cuDef('invert', 'vvs', 'v', (a, b, c) => `cuInvert(${a}, ${b}, ${c})`, cuInvert);
cuDef('mirror', 'vv', 'v', (a, b) => `cuMirror(${a}, ${b})`, cuMirror);
cuDef('lon', 'v', 's', a => `at2(${a}.y, ${a}.x)`, a => Math.atan2(a[1], a[0]));
cuDef('lat', 'v', 's', a => `cuLat(${a})`, cuLat);
cuDef('sph', 'sss', 'v', (a, b, c) => `cuSph(${a}, ${b}, ${c})`, cuSph);
cuDef('flat', 'v', 'v', a => `vec3(${a}.xy, 0.0)`, a => [a[0], a[1], 0]);
cuDef('cpow', 'vs', 'v', (a, b) => `cuCpow(${a}, ${b})`, cuCpow);
cuDef('conj', 'v', 'v', a => `(${a} * vec3(1.0, -1.0, -1.0))`, a => [a[0], -a[1], -a[2]]);
cuDef('quat', 'ssss', 'q', (w, x, y, z) => `vec4(${x}, ${y}, ${z}, ${w})`, (w, x, y, z) => [x, y, z, w]);
cuDef('quat', 'v', 'q', a => `vec4(${a}, 0.0)`, a => [a[0], a[1], a[2], 0]);
cuDef('qrot', 'vs', 'q', (a, b) => `cuQrot(${a}, ${b})`, cuQrot);
cuDef('conj', 'q', 'q', a => `cuQconj(${a})`, cuQconj);
cuDef('inv', 'q', 'q', a => `cuQinv(${a})`, cuQinv);
cuDef('qpow', 'qs', 'q', (a, b) => `cuQpow(${a}, ${b})`, cuQpow);
cuDef('re', 'q', 's', a => `${a}.w`, a => a[3]);
cuDef('turn', 'vq', 'v', (a, b) => `cuTurn(${a}, ${b})`, cuTurn);
cuDef('asquat', 'v', 'q', a => `vec4(${a}.y, ${a}.z, 0.0, ${a}.x)`, a => [a[1], a[2], 0, a[0]]);
cuDef('aspoint', 'q', 'v', a => `vec3(${a}.w, ${a}.x, ${a}.y)`, a => [a[3], a[0], a[1]]);
cuDef('mat', 'sssssssss', 'm', (a, b, c, d, e, f, g, h, i) => `mat3(${a}, ${d}, ${g}, ${b}, ${e}, ${h}, ${c}, ${f}, ${i})`, (a, b, c, d, e, f, g, h, i) => [a, d, g, b, e, h, c, f, i]);
cuDef('mat', 'vvv', 'm', (a, b, c) => `mat3(${a}, ${b}, ${c})`, (a, b, c) => [...a, ...b, ...c]);
cuDef('rotmat', 'vs', 'm', (a, b) => `cuRotmat(${a}, ${b})`, cuRotmat);
cuDef('transpose', 'm', 'm', a => `transpose(${a})`, cuMT);
cuDef('det', 'm', 's', a => `determinant(${a})`, cuDet);
cuDef('inv', 'm', 'm', a => `cuMinv(${a})`, cuMinv);

// Reads one formula. ctx: { vars, uses, internal }. vars is the Map of the names made so far (name -> { t, gl, idx }),
// uses collects 'orbit' when the formula reads first, last, mean or count, and internal allows what only a block's
// own lines may hold: a slot $7 and a hidden name @b12_r. Returns { t, gl, js, tree }: the kind, the shader text,
// js(E), which works the value out of E = { z, c, n, K, v, first, last, mean, count }, and the formula as a tree
// for cuSplit: { leaf: text } | { op, a: [trees] } | { part, of: tree } | { fn, a: [trees] }.
const CU_COMPARE = { '<': ['lt', (x, y) => x < y], '>': ['gt', (x, y) => x > y], '<=': ['le', (x, y) => x <= y], '>=': ['ge', (x, y) => x >= y], '==': ['eq', (x, y) => x === y], '!=': ['ne', (x, y) => x !== y] };
function cuParse(text, ctx) {
  const s = aprPlain(String(text));
  let i = 0;
  const fail = m => { throw new Error(m); };
  const peek = () => { while (i < s.length && /\s/.test(s[i])) i++; return s[i]; };
  const need = ch => { if (peek() !== ch) fail(`A “${ch}” is missing.`); i++; };
  const shown = name => name.replace(/^@b\d+_/, '');
  const scale = (A, B) => E => { const k = A(E); return B(E).map(u => u * k); };
  function compare() {
    const a = sum();
    peek();
    const m = /^(<=|>=|==|!=|<|>)/.exec(s.slice(i));
    if (!m) return a;
    i += m[0].length;
    const b = sum(), A = a.js, B = b.js, [name, f] = CU_COMPARE[m[0]];
    if (a.t !== 's' || b.t !== 's') fail('Only two numbers can be compared.');
    return { t: 's', gl: `(${a.gl} ${m[0]} ${b.gl} ? 1.0 : 0.0)`, js: E => (f(A(E), B(E)) ? 1 : 0), tree: { op: name, a: [a.tree, b.tree] } };
  }
  function sum() {
    let a = term();
    for (;;) {
      const ch = peek();
      if (ch !== '+' && ch !== '-') return a;
      i++;
      const b = term(), A = a.js, B = b.js, plus = ch === '+';
      if (a.t !== b.t) fail(`“${ch}” needs two things of one kind, and here it has ${CU_KINDS[a.t]} and ${CU_KINDS[b.t]}.`);
      const gl = `(${a.gl} ${ch} ${b.gl})`, tree = { op: plus ? 'add' : 'sub', a: [a.tree, b.tree] };
      if (a.t === 's') a = { t: 's', gl, tree, js: plus ? E => A(E) + B(E) : E => A(E) - B(E) };
      else a = { t: a.t, gl, tree, js: plus ? E => { const y = B(E); return A(E).map((u, k) => u + y[k]); } : E => { const y = B(E); return A(E).map((u, k) => u - y[k]); } };
    }
  }
  function times(a, b) {
    const gl = `(${a.gl} * ${b.gl})`, A = a.js, B = b.js, tree = { op: 'mul', a: [a.tree, b.tree] };
    if (a.t === 's' && b.t === 's') return { t: 's', gl, tree, js: E => A(E) * B(E) };
    if (a.t === 's') return { t: b.t, gl, tree, js: scale(A, B) };
    if (b.t === 's') return { t: a.t, gl, tree, js: scale(B, A) };
    if (a.t === 'm' && b.t === 'v') return { t: 'v', gl, tree, js: E => cuMV(A(E), B(E)) };
    if (a.t === 'm' && b.t === 'm') return { t: 'm', gl, tree, js: E => cuMM(A(E), B(E)) };
    if (a.t === 'q' && b.t === 'q') return { t: 'q', gl: `cuQmul(${a.gl}, ${b.gl})`, tree, js: E => cuQmul(A(E), B(E)) };
    if (a.t === 'v' && b.t === 'v') fail('Two points cannot be multiplied with *. Use dot(a, b), cross(a, b) or each(a, b), or make them quaternions: asquat(a) * asquat(b).');
    return fail(`“*” cannot multiply ${CU_KINDS[a.t]} by ${CU_KINDS[b.t]}.`);
  }
  function over(a, b) {
    const A = a.js, B = b.js, tree = { op: 'div', a: [a.tree, b.tree] };
    if (b.t === 'q') fail('To divide by a quaternion, multiply by inv( ) of it.');
    if (b.t !== 's') fail(`“/” can divide by a number only, and here it has ${CU_KINDS[b.t]}.`);
    if (b.lit === 0) fail('The formula divides by zero.');
    if (b.lit !== undefined) {
      const k = 1 / b.lit, gl = `(${a.gl} / ${b.gl})`;
      return a.t === 's' ? { t: 's', gl, tree, js: E => A(E) * k } : { t: a.t, gl, tree, js: E => A(E).map(u => u * k) };
    }
    if (a.t === 's') return { t: 's', gl: `cuDivS(${a.gl}, ${b.gl})`, tree, js: E => cuDivS(A(E), B(E)) };
    return { t: a.t, gl: `(${a.gl} * cuDivS(1.0, ${b.gl}))`, tree, js: E => { const k = cuDivS(1, B(E)); return A(E).map(u => u * k); } };
  }
  function term() {
    let a = unary();
    for (;;) {
      const ch = peek();
      if (ch === '*') { i++; a = times(a, unary()); }
      else if (ch === '/') { i++; a = over(a, unary()); }
      else return a;
    }
  }
  function unary() {
    const ch = peek();
    if (ch === '+') { i++; return unary(); }
    if (ch !== '-') return power();
    i++;
    const a = unary(), A = a.js;
    return { t: a.t, gl: `(-${a.gl})`, lit: a.lit === undefined ? undefined : -a.lit, tree: { op: 'neg', a: [a.tree] }, js: a.t === 's' ? E => -A(E) : E => A(E).map(u => -u) };
  }
  function power() {
    const a = part();
    if (peek() !== '^') return a;
    i++;
    const b = unary(), A = a.js, B = b.js, tree = { op: 'pow', a: [a.tree, b.tree] };
    if (b.t !== 's') fail('A power has to be a number, as in r^2 or r^n.');
    if (a.t === 's') return { t: 's', gl: `aprSPow(${a.gl}, ${b.gl})`, tree, js: E => cuSPow(A(E), B(E)) };
    if (a.t === 'q') return { t: 'q', gl: `cuQpow(${a.gl}, ${b.gl})`, tree, js: E => cuQpow(A(E), B(E)) };
    if (a.t === 'v') fail('A point has no power of its own: build one from its length and its angles, or take the quaternion power, aspoint(asquat(z)^n).');
    return fail('A matrix cannot be raised to a power here.');
  }
  function part() {
    let a = atom();
    while (s[i] === '.' && /[A-Za-z]/.test(s[i + 1] || '')) {
      i++;
      const name = /^[A-Za-z]+/.exec(s.slice(i))[0], A = a.js, at = 'xyzw'.indexOf(name);
      i += name.length;
      if (a.t !== 'v' && a.t !== 'q') fail(`“.${name}” needs a point or a quaternion in front of it.`);
      if (name.length !== 1 || at < 0 || (a.t === 'v' && at > 2)) fail(a.t === 'v' ? 'A point has the parts .x, .y and .z.' : 'A quaternion has the parts .w, .x, .y and .z.');
      a = { t: 's', gl: `${a.gl}.${name}`, tree: { part: name, of: a.tree }, js: E => A(E)[at] };
    }
    return a;
  }
  function call(name, args) {
    const forms = CU_FN[name];
    if (!forms) fail(`“${name}( )” is not a function a formula knows.`);
    const sig = args.map(a => a.t).join(''), f = forms.find(o => o.args === sig);
    if (!f) {
      const say = k => [...k].map(t => CU_KINDS[t]).join(', ');
      fail(`${name}( ) is given ${args.length ? say(sig) : 'nothing'}. It takes ${forms.map(o => say(o.args)).join(', or ')}.`);
    }
    const J = args.map(a => a.js), g = f.js, gl = f.gl(...args.map(a => a.gl)), tree = { fn: name, a: args.map(a => a.tree) };
    if (J.length === 1) { const [a] = J; return { t: f.ret, gl, tree, js: E => g(a(E)) }; }
    if (J.length === 2) { const [a, b] = J; return { t: f.ret, gl, tree, js: E => g(a(E), b(E)) }; }
    if (J.length === 3) { const [a, b, c] = J; return { t: f.ret, gl, tree, js: E => g(a(E), b(E), c(E)) }; }
    return { t: f.ret, gl, tree, js: E => g(...J.map(h => h(E))) };
  }
  function atom() {
    const ch = peek();
    if (ch === undefined) fail('The formula stops too early.');
    if (ch === '(') { i++; const a = compare(); need(')'); return a; }
    if (ch === '$' && ctx.internal) {
      const k = +/^\$(\d+)/.exec(s.slice(i))[1];
      i += 1 + String(k).length;
      return { t: 's', gl: `uCu[${k}]`, tree: { leaf: '$' + k }, js: E => E.K[k] };
    }
    const num = /^(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?/.exec(s.slice(i));
    if (num) {
      i += num[0].length;
      const x = parseFloat(num[0]);
      if (!(Math.abs(x) <= 1e30)) fail(`The number ${num[0]} is too large. Numbers up to 1e30 work.`);
      return { t: 's', gl: cuFlt(x), lit: x, tree: { leaf: num[0] }, js: () => x };
    }
    const id = (ctx.internal ? /^@?[A-Za-z][A-Za-z0-9_]*/ : /^[A-Za-z][A-Za-z0-9_]*/).exec(s.slice(i));
    if (!id) fail(`“${ch}” is not something a formula can use here.`);
    i += id[0].length;
    const name = id[0], tree = { leaf: name };
    if (peek() === '(') {
      i++;
      const args = [];
      if (peek() !== ')') for (;;) { args.push(compare()); if (peek() !== ',') break; i++; }
      need(')');
      return call(name, args);
    }
    if (name === 'z') return { t: 'v', gl: 'z', tree, js: E => E.z };
    if (name === 'c') return { t: 'v', gl: 'c', tree, js: E => E.c };
    if (name === 'n') return { t: 's', gl: 'n', tree, js: E => E.n };
    if (name === 'pi') return { t: 's', gl: cuFlt(PI), lit: PI, tree, js: () => PI };
    if (name === 'first' || name === 'last' || name === 'mean' || name === 'count') {
      ctx.uses.add('orbit');
      return { t: CU_GIVEN[name], gl: 'o' + name[0].toUpperCase() + name.slice(1), tree, js: E => E[name] };
    }
    const v = ctx.vars.get(name);
    if (!v) fail(CU_FN[name] ? `“${name}” is a function: write ${name}( ) with what it works on between the brackets.` : `“${shown(name)}” has no value yet. A name gets its value in an earlier step, as in ${shown(name)} = len(z).`);
    const at = v.idx;
    return { t: v.t, gl: v.gl, tree, js: E => E.v[at] };
  }
  const out = compare();
  if (peek() !== undefined) fail(`“${s[i]}” is unexpected here.`);
  return out;
}
// A line, `name = formula`, as its two halves; a formula alone is the new z.
function cuHalves(line) {
  const m = /^\s*(@?[A-Za-z][A-Za-z0-9_]*)\s*=(?!=)([\s\S]*)$/.exec(String(line));
  return m ? { target: m[1], src: m[2] } : { target: 'z', src: String(line) };
}
// Reads one line. Returns { gl, js, z }: the shader statement, js(E), which carries it out on E, and whether the
// line moves the point. A name that is new is added to ctx.vars; internal: the line comes from a block.
function cuLine(line, ctx, internal) {
  const { target, src } = cuHalves(line);
  if (!src.trim()) throw new Error('The formula is empty.');
  ctx.internal = internal;
  const node = cuParse(src, ctx), J = node.js;
  if (target === 'z') {
    if (node.t !== 'v') throw new Error(`z is a point, and this formula gives ${CU_KINDS[node.t]}. A point is written vec(x, y, z).`);
    return { gl: `z = ${node.gl};`, z: true, js: E => { E.z = J(E); } };
  }
  if (target in CU_GIVEN || CU_FN[target]) throw new Error(`“${target}” already means something here, so it cannot be a name of your own. Pick another.`);
  if (target[0] !== '@' && !CU_NAME.test(target)) throw new Error('A name is made of letters and digits and starts with a letter.');
  let v = ctx.vars.get(target);
  if (v && v.t !== node.t) throw new Error(`“${target}” was ${CU_KINDS[v.t]} in an earlier step and would be ${CU_KINDS[node.t]} here. Use another name.`);
  if (!v) {
    v = { t: node.t, idx: ctx.zero.length, gl: target[0] === '@' ? target.slice(1) : 'u_' + target };
    ctx.zero.push(node.t); ctx.vars.set(target, v);
  }
  const at = v.idx;
  return { gl: `${v.gl} = ${node.gl};`, z: false, js: E => { E.v[at] = J(E); } };
}

// The kinds of step. params: the settings a step of that kind has, each { key, label, type, def } with type
//   'num'     a number, the power n, a number of the user's own, or a formula that gives one (min, max, step: the
//             range of its slider; bare: a box alone)
//   'vec'     a point: three numbers, or a formula that gives one (picks: the list its menu offers)
//   'any'     a value of any kind: a name, a number or a formula
//   'choice'  one of options [[value, label], ...]
//   'name'    the name the step gives its answer;   'text'  a whole line, name = formula
// lines(P, v): the step as lines of the language. P[key] is the setting, ready to stand inside a formula; v(base) is
// a name for a value the lines keep (the same name for the same base). words(p): the step in a few words.
// plain: the step is a line already; basic: the step is one operation. Neither is a block.
const CU_AXES = [['the upright axis (z)', 'vec(0, 0, 1)'], ['the x-axis', 'vec(1, 0, 0)'], ['the y-axis', 'vec(0, 1, 0)'],
  ['the point itself', 'z'], ['c', 'c'], ['the first point of the orbit', 'first'], ['the point of the step before', 'last'],
  ['the average of the orbit’s points so far', 'mean'], ['square to the point and the upright axis', 'cross(vec(0, 0, 1), z)'],
  ['square to the point and the x-axis', 'cross(vec(1, 0, 0), z)'], ['square to the point and c', 'cross(z, c)'],
  ['square to the point and the step before', 'cross(z, last)'], ['from the step before to this point', 'z - last']];
const CU_PLACES = [['the middle (0, 0, 0)', 'vec(0, 0, 0)'], ['c', 'c'], ['the point itself', 'z'],
  ['the first point of the orbit', 'first'], ['the point of the step before', 'last'], ['the average of the orbit’s points so far', 'mean']];
const cuAxis = (key, label, def) => ({ key, label, type: 'vec', def, picks: CU_AXES });
const cuPlace = (key, label, def) => ({ key, label, type: 'vec', def, picks: CU_PLACES });
// a setting in words: the name its menu has for it, or the formula as typed
const cuCalled = (list, text) => { const t = String(text).replace(/\s+/g, ''), hit = list.find(o => o[1].replace(/\s+/g, '') === t); return hit ? hit[0] : String(text); };
const cuAx = text => cuCalled(CU_AXES, text), cuPl = text => cuCalled(CU_PLACES, text);
const cuTimes = (key, label) => ({ key, label, type: 'num', def: 'n', min: -4, max: 8, step: 0.05 });
const cuDegrees = (key, label, def) => ({ key, label, type: 'num', def, min: -180, max: 180, step: 1 });
const cuQuatParts = [['w', 'Real part', '0.7071'], ['x', 'i part', '0'], ['y', 'j part', '0'], ['z', 'k part', '0.7071']]
  .map(([key, label, def]) => ({ key, label, type: 'num', def, min: -2, max: 2, step: 0.01 }));
// the lines that split z by an axis: h is how far along the axis the point is, w the rest of it
const cuSplitZ = (P, v) => [`${v('axis')} = unit(${P.axis})`, `${v('h')} = dot(z, ${v('axis')})`, `${v('w')} = z - ${v('axis')}*${v('h')}`];
const CU_BLOCKS = {
  len: { title: 'Raise the length to a power', group: 'Length and angles',
    params: [cuTimes('p', 'Power')],
    lines: (P, v) => [`${v('r')} = len(z)`, `z = z * ${v('r')}^(${P.p} - 1)`],
    words: p => `raise the length to the power ${p.p}` },
  lon: { title: 'Multiply the angle round an axis', group: 'Length and angles',
    params: [cuAxis('axis', 'Axis', 'vec(0, 0, 1)'), cuAxis('from', 'Angle counted from', 'vec(1, 0, 0)'), cuTimes('times', 'Multiply by'), cuDegrees('plus', 'Then add, degrees', '0')],
    lines: (P, v) => [...cuSplitZ(P, v),
      `${v('e1')} = unit(${P.from} - ${v('axis')}*dot(${P.from}, ${v('axis')}))`, `${v('e2')} = cross(${v('axis')}, ${v('e1')})`,
      `${v('ang')} = atan2(dot(${v('w')}, ${v('e2')}), dot(${v('w')}, ${v('e1')}))*${P.times} + rad(${P.plus})`,
      `z = ${v('axis')}*${v('h')} + (${v('e1')}*cos(${v('ang')}) + ${v('e2')}*sin(${v('ang')}))*len(${v('w')})`],
    words: p => `multiply the angle round ${cuAx(p.axis)} by ${p.times}` },
  lat: { title: 'Multiply the angle of the height', group: 'Length and angles',
    params: [cuAxis('axis', 'Height along', 'vec(0, 0, 1)'),
      { key: 'from', label: 'Angle counted', type: 'choice', def: 'plane', options: [['plane', 'up from the plane square to the axis'], ['axis', 'down from the axis (the Mandelbulb)']] },
      cuTimes('times', 'Multiply by'), cuDegrees('plus', 'Then add, degrees', '0')],
    lines: (P, v) => [...cuSplitZ(P, v), `${v('r')} = len(z)`, ...(P.from === 'axis'
      ? [`${v('ang')} = atan2(len(${v('w')}), ${v('h')})*${P.times} + rad(${P.plus})`, `z = (unit(${v('w')})*sin(${v('ang')}) + ${v('axis')}*cos(${v('ang')}))*${v('r')}`]
      : [`${v('ang')} = atan2(${v('h')}, len(${v('w')}))*${P.times} + rad(${P.plus})`, `z = (unit(${v('w')})*cos(${v('ang')}) + ${v('axis')}*sin(${v('ang')}))*${v('r')}`])],
    words: p => `multiply the angle of the height along ${cuAx(p.axis)} by ${p.times}` + (p.from === 'axis' ? ', counted from the axis' : '') },
  merc: { title: 'Multiply the height the Mercator way', group: 'Length and angles',
    params: [cuAxis('axis', 'Height along', 'vec(0, 0, 1)'), cuTimes('times', 'Multiply by')],
    lines: (P, v) => [...cuSplitZ(P, v), `${v('r')} = len(z)`, `${v('m')} = atanh(${v('h')} / ${v('r')})*${P.times}`,
      `z = (unit(${v('w')}) / cosh(${v('m')}) + ${v('axis')}*tanh(${v('m')}))*${v('r')}`],
    words: p => `multiply the height along ${cuAx(p.axis)} by ${p.times} on the scale of a Mercator map` },
  inv: { title: 'Sphere inversion', group: 'Moves of space',
    params: [cuPlace('centre', 'Centre of the sphere', 'vec(0, 0, 0)'), { key: 'radius', label: 'Radius', type: 'num', def: '1', min: 0.05, max: 4, step: 0.01 }],
    lines: (P, v) => [`${v('d')} = z - ${P.centre}`, `z = ${P.centre} + ${v('d')}*(${P.radius}*${P.radius} / dot(${v('d')}, ${v('d')}))`],
    words: p => `turn space inside out through the sphere of radius ${p.radius} round ${cuPl(p.centre)}` },
  rot: { title: 'Turn about an axis', group: 'Moves of space',
    params: [cuAxis('axis', 'Axis', 'vec(0, 0, 1)'), cuDegrees('angle', 'Angle, degrees', '90')],
    lines: (P, v) => [`${v('axis')} = unit(${P.axis})`, `${v('ang')} = rad(${P.angle})`,
      `z = z*cos(${v('ang')}) + cross(${v('axis')}, z)*sin(${v('ang')}) + ${v('axis')}*(dot(${v('axis')}, z)*(1 - cos(${v('ang')})))`],
    words: p => `turn by ${p.angle}° about ${cuAx(p.axis)}` },
  mirror: { title: 'Mirror in a plane', group: 'Moves of space',
    params: [cuAxis('normal', 'The plane is square to', 'vec(0, 1, 0)'), cuPlace('through', 'and passes through', 'vec(0, 0, 0)')],
    lines: (P, v) => [`${v('k')} = unit(${P.normal})`, `z = z - ${v('k')}*(2*dot(z - ${P.through}, ${v('k')}))`],
    words: p => `mirror in the plane square to ${cuAx(p.normal)}` },
  fold: { title: 'Fold onto one side of a plane', group: 'Moves of space',
    params: [cuAxis('normal', 'The plane is square to', 'vec(0, 1, 0)'), cuPlace('through', 'and passes through', 'vec(0, 0, 0)')],
    lines: (P, v) => [`${v('k')} = unit(${P.normal})`, `z = z - ${v('k')}*(2*min(0, dot(z - ${P.through}, ${v('k')})))`],
    words: p => `fold the far side of the plane square to ${cuAx(p.normal)} onto the near side` },
  scale: { title: 'Stretch', group: 'Moves of space',
    params: [{ key: 'by', label: 'Multiply every length by', type: 'num', def: '2', min: -3, max: 3, step: 0.01 }],
    lines: P => [`z = z*${P.by}`],
    words: p => `multiply every length by ${p.by}` },
  shift: { title: 'Slide', group: 'Moves of space',
    params: [cuPlace('by', 'Slide by', 'vec(1, 0, 0)')],
    lines: P => [`z = z + ${P.by}`],
    words: p => `slide by ${p.by}` },
  quatpow: { title: 'Quaternion power', group: 'Quaternions and matrices',
    params: [cuTimes('p', 'Power')],
    lines: (P, v) => [`${v('r')} = len(z)`, `${v('side')} = vec(0, z.y, z.z)`, `${v('ang')} = atan2(len(${v('side')}), z.x)*${P.p}`,
      `z = (vec(1, 0, 0)*cos(${v('ang')}) + unit(${v('side')})*sin(${v('ang')}))*${v('r')}^${P.p}`],
    words: p => `take the quaternion power ${p.p} of the point, read as x + yi + zj` },
  quatmul: { title: 'Multiply by a quaternion', group: 'Quaternions and matrices',
    params: [...cuQuatParts, { key: 'side', label: 'The quaternion stands', type: 'choice', def: 'right', options: [['right', 'on the right: z · q'], ['left', 'on the left: q · z']] }],
    lines: P => [`z = aspoint(${P.side === 'left' ? `quat(${P.w}, ${P.x}, ${P.y}, ${P.z}) * asquat(z)` : `asquat(z) * quat(${P.w}, ${P.x}, ${P.y}, ${P.z})`})`],
    words: p => `multiply the point, read as x + yi + zj, by the quaternion ${p.w} + ${p.x}i + ${p.y}j + ${p.z}k` },
  quatturn: { title: 'Turn by a quaternion', group: 'Quaternions and matrices',
    params: cuQuatParts,
    lines: P => [`z = turn(z, quat(${P.w}, ${P.x}, ${P.y}, ${P.z}))`],
    words: p => `turn by the quaternion ${p.w} + ${p.x}i + ${p.y}j + ${p.z}k (q · z · q⁻¹)` },
  matrix: { title: 'Multiply by a matrix', group: 'Quaternions and matrices', grid: 3,
    params: ['1', '0', '0', '0', '1', '0', '0', '0', '1'].map((def, k) => ({ key: 'm' + k, label: `Row ${Math.floor(k / 3) + 1}, column ${k % 3 + 1}`, type: 'num', def, bare: true, step: 0.05 })),
    lines: P => [`z = mat(${[0, 1, 2, 3, 4, 5, 6, 7, 8].map(k => P['m' + k]).join(', ')}) * z`],
    words: () => 'multiply by the matrix' },
  addc: { title: 'Add c', group: 'Adding',
    params: [cuPlace('what', 'Add', 'c'), { key: 'times', label: 'this many times', type: 'num', def: '1', min: -2, max: 2, step: 0.01 }],
    lines: P => [`z = z + ${P.what}*${P.times}`],
    words: p => (cuIsNum(p.times) && cuNum(p.times) === 1 ? `add ${cuPl(p.what)}` : `add ${p.times} times ${cuPl(p.what)}`) },
  formula: { title: 'A formula of your own', group: 'Your own', plain: true,
    params: [{ key: 'text', label: 'name = formula', type: 'text', def: 'r = len(z)' }],
    lines: P => [P.text],
    words: p => p.text },
  slider: { title: 'A number with a slider', group: 'Your own', plain: true, basic: true,
    params: [{ key: 'name', label: 'Name', type: 'name', def: 't' }, { key: 'value', label: 'Value', type: 'num', def: '0.5', min: 0, max: 1, step: 0.01, ranged: true, own: true },
      { key: 'min', label: 'Slider from', type: 'num', def: '0', bare: true, fixed: true }, { key: 'max', label: 'to', type: 'num', def: '1', bare: true, fixed: true }],
    lines: P => [`${P.name} = ${P.value}`],
    words: p => `${p.name} = ${p.value}` },
};
// The single operations, each a kind of step of its own: [kind, title, group, the name its answer starts with,
// what it works on as [label, starting value] pairs, and the formula]. A kind that starts with f_ is the function
// of that name, and needs no formula here.
const CU_OPS = [
  ['o_copy', 'Give a value a name', 'Arithmetic', 'a', [['The value', 'z']], a => a],
  ['o_add', 'Add', 'Arithmetic', 'sum', [['This', 'z'], ['plus this', 'c']], (a, b) => `${a} + ${b}`],
  ['o_sub', 'Subtract', 'Arithmetic', 'diff', [['This', 'z'], ['minus this', 'c']], (a, b) => `${a} - ${b}`],
  ['o_mul', 'Multiply', 'Arithmetic', 'prod', [['This', 'z'], ['times this', '2']], (a, b) => `${a} * ${b}`],
  ['o_div', 'Divide', 'Arithmetic', 'quot', [['This', 'z'], ['divided by this', '2']], (a, b) => `${a} / ${b}`],
  ['o_pow', 'Raise to a power', 'Arithmetic', 'p', [['This number', '2'], ['to the power', 'n']], (a, b) => `${a} ^ ${b}`],
  ['o_neg', 'Change the sign', 'Arithmetic', 'neg', [['Of this', 'z']], a => `-${a}`],
  ['f_sqrt', 'Square root', 'Arithmetic', 'root', [['Of', '2']]],
  ['f_abs', 'Drop the sign', 'Arithmetic', 'size', [['Of', '-1']]],
  ['f_min', 'The smaller of two', 'Arithmetic', 'low', [['This', '0'], ['or this', '1']]],
  ['f_max', 'The larger of two', 'Arithmetic', 'high', [['This', '0'], ['or this', '1']]],
  ['f_mod', 'What is left after a division', 'Arithmetic', 'rest', [['Of', '5'], ['divided by', '2']]],
  ['f_floor', 'Round down', 'Arithmetic', 'whole', [['This', '1.5']]],
  ['f_ceil', 'Round up', 'Arithmetic', 'whole', [['This', '1.5']]],
  ['f_round', 'Round to the nearest', 'Arithmetic', 'whole', [['This', '1.5']]],
  ['f_fract', 'The part after the point', 'Arithmetic', 'part', [['Of', '1.5']]],
  ['f_sign', 'The sign: −1, 0 or 1', 'Arithmetic', 'sg', [['Of', '-2']]],
  ['f_exp', 'e to a power', 'Arithmetic', 'grown', [['The power', '1']]],
  ['f_log', 'Natural logarithm', 'Arithmetic', 'lg', [['Of', '2']]],
  ['f_clamp', 'Keep between two limits', 'Arithmetic', 'kept', [['This', 'len(z)'], ['no less than', '0'], ['no more than', '1']]],
  ['f_mix', 'Blend two values', 'Arithmetic', 'blend', [['From', '0'], ['to', '1'], ['how far, 0 to 1', '0.5']]],
  ['f_sin', 'Sine of an angle', 'Angles', 's', [['Angle, in radians', 'rad(30)']]],
  ['f_cos', 'Cosine of an angle', 'Angles', 'co', [['Angle, in radians', 'rad(30)']]],
  ['f_tan', 'Tangent of an angle', 'Angles', 'ta', [['Angle, in radians', 'rad(30)']]],
  ['f_asin', 'The angle that has this sine', 'Angles', 'ang', [['Sine', '0.5']]],
  ['f_acos', 'The angle that has this cosine', 'Angles', 'ang', [['Cosine', '0.5']]],
  ['f_atan', 'The angle that has this tangent', 'Angles', 'ang', [['Tangent', '1']]],
  ['f_atan2', 'Angle of a direction', 'Angles', 'ang', [['How far up (y)', 'z.y'], ['how far along (x)', 'z.x']]],
  ['f_rad', 'Degrees to radians', 'Angles', 'ang', [['Degrees', '90']]],
  ['f_deg', 'Radians to degrees', 'Angles', 'degrees', [['Radians', 'pi']]],
  ['f_sinh', 'Hyperbolic sine', 'Angles', 'sh', [['Of', '1']]],
  ['f_cosh', 'Hyperbolic cosine', 'Angles', 'ch', [['Of', '1']]],
  ['f_tanh', 'Hyperbolic tangent', 'Angles', 'th', [['Of', '1']]],
  ['f_atanh', 'Hyperbolic tangent, backwards', 'Angles', 'm', [['Of', '0.5']]],
  ['f_vec', 'Make a point from three numbers', 'Points', 'pt', [['x', '1'], ['y', '0'], ['z', '0']]],
  ['o_part', 'Take one part of a point', 'Points', 'x', [['Of', 'z']]],
  ['f_len', 'Length', 'Points', 'r', [['Of', 'z']]],
  ['f_unit', 'Same direction, length 1', 'Points', 'dir', [['Of', 'z']]],
  ['f_dot', 'Dot product', 'Points', 'd', [['Of', 'z'], ['and', 'c']]],
  ['f_cross', 'Cross product', 'Points', 'side', [['Of', 'z'], ['and', 'c']]],
  ['f_dist', 'Distance between two points', 'Points', 'far', [['From', 'z'], ['to', 'c']]],
  ['f_each', 'Multiply part by part', 'Points', 'pp', [['This', 'z'], ['by this', 'vec(1, 1, 1)']]],
  ['f_flat', 'Drop the height', 'Points', 'fl', [['Of', 'z']]],
  ['f_lon', 'Angle round the upright axis', 'Points', 'ang', [['Of', 'z']]],
  ['f_lat', 'Angle above the flat plane', 'Points', 'ang', [['Of', 'z']]],
  ['f_sph', 'A point from a length and two angles', 'Points', 'pt', [['Length', '1'], ['angle round', 'rad(0)'], ['angle above the plane', 'rad(45)']]],
  ['f_rot', 'Turn a point about an axis', 'Points', 'pt', [['Point', 'z'], ['axis', 'vec(0, 0, 1)'], ['angle, in radians', 'rad(90)']]],
  ['f_invert', 'Turn a point inside out through a sphere', 'Points', 'pt', [['Point', 'z'], ['centre', 'vec(0, 0, 0)'], ['radius', '1']]],
  ['f_mirror', 'Mirror a point in a plane', 'Points', 'pt', [['Point', 'z'], ['the plane is square to', 'vec(0, 1, 0)']]],
  ['f_cpow', 'Flat power of x and y', 'Points', 'pt', [['Point', 'z'], ['power', 'n']]],
  ['f_conj', 'Flip the signs of y and z', 'Points', 'pt', [['Of', 'z']]],
  ['o_lt', 'Is it less?', 'Tests and choices', 'test', [['Is this', 'len(z)'], ['less than this', '1']], (a, b) => `${a} < ${b}`],
  ['o_gt', 'Is it more?', 'Tests and choices', 'test', [['Is this', 'len(z)'], ['more than this', '1']], (a, b) => `${a} > ${b}`],
  ['o_le', 'Is it less or the same?', 'Tests and choices', 'test', [['Is this', 'len(z)'], ['no more than this', '1']], (a, b) => `${a} <= ${b}`],
  ['o_ge', 'Is it more or the same?', 'Tests and choices', 'test', [['Is this', 'len(z)'], ['no less than this', '1']], (a, b) => `${a} >= ${b}`],
  ['o_eq', 'Is it the same?', 'Tests and choices', 'test', [['Is this', 'count'], ['the same as this', '1']], (a, b) => `${a} == ${b}`],
  ['o_ne', 'Is it different?', 'Tests and choices', 'test', [['Is this', 'count'], ['different from this', '1']], (a, b) => `${a} != ${b}`],
  ['f_if', 'Choose one of two', 'Tests and choices', 'pick', [['When this is 1', '1'], ['take', 'z'], ['otherwise', 'c']]],
  ['f_asquat', 'Read a point as a quaternion', 'Quaternion and matrix pieces', 'q', [['Point', 'z']]],
  ['f_aspoint', 'Read a quaternion as a point', 'Quaternion and matrix pieces', 'pt', [['Quaternion', 'asquat(z)']]],
  ['f_quat', 'Make a quaternion from four numbers', 'Quaternion and matrix pieces', 'q', [['Real part', '1'], ['i part', '0'], ['j part', '0'], ['k part', '0']]],
  ['f_qrot', 'The quaternion of a turn about an axis', 'Quaternion and matrix pieces', 'q', [['Axis', 'vec(0, 0, 1)'], ['angle, in radians', 'rad(90)']]],
  ['f_qpow', 'A quaternion to a power', 'Quaternion and matrix pieces', 'q', [['Quaternion', 'asquat(z)'], ['power', 'n']]],
  ['f_inv', 'One over a quaternion or a matrix', 'Quaternion and matrix pieces', 'q', [['Of', 'asquat(z)']]],
  ['f_re', 'Real part of a quaternion', 'Quaternion and matrix pieces', 'real', [['Of', 'asquat(z)']]],
  ['f_turn', 'Turn a point by a quaternion', 'Quaternion and matrix pieces', 'pt', [['Point', 'z'], ['quaternion', 'qrot(vec(0, 0, 1), rad(90))']]],
  ['f_mat', 'Make a matrix from nine numbers', 'Quaternion and matrix pieces', 'mx', ['1', '0', '0', '0', '1', '0', '0', '0', '1'].map((d, k) => [`Row ${Math.floor(k / 3) + 1}, column ${k % 3 + 1}`, d])],
  ['f_rotmat', 'The matrix of a turn about an axis', 'Quaternion and matrix pieces', 'mx', [['Axis', 'vec(0, 0, 1)'], ['angle, in radians', 'rad(90)']]],
  ['f_transpose', 'Swap the rows and columns of a matrix', 'Quaternion and matrix pieces', 'mx', [['Of', 'rotmat(vec(0, 0, 1), rad(90))']]],
  ['f_det', 'Determinant of a matrix', 'Quaternion and matrix pieces', 'det3', [['Of', 'rotmat(vec(0, 0, 1), rad(90))']]],
];
// a function with no row above still gets a step of its own, named as it is written
for (const name of Object.keys(CU_FN)) {
  if (!CU_OPS.some(o => o[0] === 'f_' + name)) CU_OPS.push(['f_' + name, name + '( )', 'More functions', 'v', [...CU_FN[name][0].args].map((t, k) => ['Value ' + (k + 1), { s: '1', v: 'z', q: 'asquat(z)', m: 'rotmat(z, 1)' }[t]])]);
}
for (const [kind, title, group, out, args, make] of CU_OPS) {
  const fn = kind.slice(0, 2) === 'f_' ? kind.slice(2) : '', keys = args.map((a, k) => 'a' + k);
  const form = fn ? (...a) => `${fn}(${a.join(', ')})` : kind === 'o_part' ? (a, part) => `${a}.${part}` : make;
  const params = [{ key: 'out', label: 'Call the answer', type: 'name', def: out }, ...args.map(([label, def], k) => ({ key: keys[k], label, type: 'any', def }))];
  if (kind === 'o_part') params.push({ key: 'part', label: 'Which part', type: 'choice', def: 'x', options: [['x', 'x'], ['y', 'y'], ['z', 'z (the height)'], ['w', 'w (a quaternion’s real part)']] });
  const all = p => keys.map(k => p[k]).concat(kind === 'o_part' ? [p.part] : []);
  CU_BLOCKS[kind] = { title, group, basic: true, arity: args.length, params, lines: P => [`${P.out} = ${form(...all(P))}`], words: p => `${p.out} = ${form(...all(p))}` };
}
const CU_GROUPS = ['Length and angles', 'Moves of space', 'Quaternions and matrices', 'Adding', 'Your own', 'Arithmetic', 'Angles', 'Points', 'Tests and choices', 'Quaternion and matrix pieces', 'More functions'];
// Rules to start from: each a list of [kind, settings that differ from the kind's own]. bail: how far a point may go
// (CU_BAIL where it is left out). say: a sentence for the moment the rule is loaded.
const CU_STARTS = [
  { name: 'Sphere inversions, one plane', steps: [['len'], ['lon'], ['merc'], ['addc']] },
  { name: 'Mandelbulb', steps: [['len'], ['lon'], ['lat', { from: 'axis' }], ['addc']] },
  { name: 'Quaternion power', steps: [['quatpow'], ['addc']] },
  { name: 'Burning ship: two folds, then one plane', steps: [['fold', { normal: 'vec(1, 0, 0)' }], ['fold', { normal: 'vec(0, 1, 0)' }], ['len'], ['lon'], ['merc'], ['addc']] },
  { name: 'Box folds and a sphere fold (the Mandelbox)', bail: 12, say: 'This solid is wide. Zoom out to see all of it: scroll, or press the − button under the picture.', steps: [
    ['formula', { text: 'z = vec(clamp(z.x, -1, 1), clamp(z.y, -1, 1), clamp(z.z, -1, 1))*2 - z' }], ['formula', { text: 'rr = dot(z, z)' }],
    ['formula', { text: 'z = z * if(rr < 0.25, 4, if(rr < 1, 1/rr, 1))' }], ['scale', { by: '-1.5' }], ['addc']] },
  { name: 'A bare start: the length, then add c', steps: [['len'], ['addc']] },
];
const cuStepOf = (kind, p, id) => ({ id, kind, on: true, p: { ...Object.fromEntries(CU_BLOCKS[kind].params.map(s => [s.key, s.def])), ...p } });
const cuStartSteps = k => CU_STARTS[k].steps.map(([kind, p], i) => cuStepOf(kind, p, i + 1));
const cuDefault = () => { const steps = cuStartSteps(0); return { steps, next: steps.length + 1, rev: 0, bail: CU_BAIL, play: null }; };
const cuBailOf = x => clamp(+x || CU_BAIL, 1.2, 64);
// A list of steps from text of any origin (a saved rule, pasted text): every step checked, every id made afresh.
// Returns null when the text holds no step that can be used.
function cuClean(list) {
  if (!Array.isArray(list)) return null;
  const steps = [];
  for (const raw of list.slice(0, CU_MAX_STEPS)) {
    const B = raw && CU_BLOCKS[raw.kind];
    if (!B) continue;
    const p = {};
    for (const sp of B.params) { const x = raw.p && raw.p[sp.key]; p[sp.key] = typeof x === 'string' || typeof x === 'number' ? String(x).slice(0, 400) : sp.def; }
    steps.push({ id: steps.length + 1, kind: raw.kind, on: raw.on !== false, p });
  }
  return steps.length ? steps : null;
}
// A whole rule from such text: the steps alone (a list), or the steps with how far a point may go.
function cuRuleOf(o) {
  const steps = cuClean(Array.isArray(o) ? o : o && o.steps);
  return steps ? { steps, next: steps.length + 1, rev: 0, bail: cuBailOf(o && o.bail), play: null } : null;
}
function cuStored() {
  try { return cuRuleOf(JSON.parse(localStorage.getItem(CU_KEY) || 'null')); }
  catch (err) { return null; }   // storage is blocked, or what it holds is not a rule
}
const cuRuleText = () => JSON.stringify({ bail: S.custom.bail, steps: S.custom.steps.map(s => ({ kind: s.kind, on: s.on !== false, p: s.p })) });
function cuStore() {
  try { localStorage.setItem(CU_KEY, cuRuleText()); } catch (err) { /* storage blocked: the rule lasts for this visit */ }
}

// A step's settings, ready to stand inside its lines. With ctx (the picture's own reading) a plain number goes into
// a slot of uCu while one is free; without ctx (breaking a step down) it stays as typed.
const cuWrapped = raw => (/^[A-Za-z][A-Za-z0-9]*(\.[xyzw])?$|^[A-Za-z][A-Za-z0-9]*\([^()]*\)$/.test(raw) ? raw : `(${raw})`);   // a name or one function stands as it is
function cuSettings(st, B, ctx) {
  const P = {}, slot = x => { ctx.K.push(x); return '$' + (ctx.K.length - 1); }, plain = x => (x < 0 ? `(${x})` : String(x));
  for (const sp of B.params) {
    const raw = String(st.p[sp.key] === undefined ? sp.def : st.p[sp.key]).trim();
    if (sp.type === 'choice') { P[sp.key] = sp.options.some(o => o[0] === raw) ? raw : sp.def; continue; }
    if (sp.type === 'text') { P[sp.key] = raw; continue; }
    if (sp.type === 'name') {
      if (!CU_NAME.test(raw)) throw new Error(`${sp.label}: a name is made of letters and digits and starts with a letter.`);
      P[sp.key] = raw; continue;
    }
    if (!raw) throw new Error(`“${sp.label}” is empty.`);
    if (sp.fixed) { if (!cuIsNum(raw)) throw new Error(`“${sp.label}” has to be a plain number.`); continue; }
    if (sp.type !== 'vec' && cuIsNum(raw)) { const x = cuNum(raw); P[sp.key] = ctx && ctx.K.length < CU_FREE ? slot(x) : plain(x); continue; }
    const xyz = sp.type === 'vec' ? cuXyz(raw) : null;
    if (xyz) { P[sp.key] = ctx && ctx.K.length + 3 <= CU_FREE ? `vec(${xyz.map(slot).join(', ')})` : `vec(${xyz.map(plain).join(', ')})`; continue; }
    if (ctx) {
      let node;
      ctx.internal = false;
      try { node = cuParse(raw, ctx); } catch (e) { throw new Error(`${sp.label}: ${e.message}`); }
      const want = sp.type === 'vec' ? 'v' : sp.type === 'num' ? 's' : node.t;
      if (node.t !== want) throw new Error(`“${sp.label}” has to be ${CU_KINDS[want]}, and this formula gives ${CU_KINDS[node.t]}.` + (want === 'v' ? ' A point is written vec(x, y, z).' : ''));
    }
    P[sp.key] = cuWrapped(raw);
  }
  return P;
}
// Reads the whole rule. Returns the shader text (glsl) and its short key, the numbers for uCu (K), the steps as
// JavaScript (run: [{ id, sw, ord, moves, fns }]: sw the slot of the step's switch or -1, ord its place in the
// shader's own count, moves whether it changes the point), the kinds of the names (zero), scopes[id]: the names
// of the user's own that a step can read, as [name, kind] pairs, and errs[id]: why a step could not be read. Such a
// step is left out, and so is one that is off and has no slot.
function cuBuild(steps) {
  const ctx = { vars: new Map(), zero: [], uses: new Set(), K: [], internal: false };
  const body = [], run = [], errs = {}, scopes = {};
  steps.slice(0, CU_MAX_STEPS).forEach(st => {
    const B = CU_BLOCKS[st.kind], keep = { vars: new Map(ctx.vars), zero: ctx.zero.length };
    scopes[st.id] = [...ctx.vars].filter(([name]) => name[0] !== '@').map(([name, v]) => [name, v.t]);
    let sw = -1;
    if (ctx.K.length < CU_FREE) { sw = ctx.K.length; ctx.K.push(st.on === false ? 0 : 1); }
    else if (st.on === false) return;
    try {
      if (!B) throw new Error('This kind of step is not known.');
      const P = cuSettings(st, B, ctx), names = {};
      const lines = B.lines(P, base => names[base] || (names[base] = '@b' + st.id + '_' + base)).map(l => cuLine(l, ctx, st.kind !== 'formula'));
      const ord = body.length, moves = lines.some(l => l.z), inner = lines.map(l => l.gl).join(' ');
      const when = (sw < 0 ? '' : `uCu[${sw}] > 0.5 && `) + `${ord}.0 <= cuAt`;
      // a step that moves the point can be taken part of the way (cuT), for a play that stands in the middle of it
      body.push(moves ? `if (${when}){ vec3 zb = z; ${inner} if (${ord}.0 == cuAt) z = cuBlend(zb, z, cuT); }` : `if (${when}){ ${inner} }`);
      run.push({ id: st.id, sw, ord, moves, fns: lines.map(l => l.js) });
    } catch (e) { errs[st.id] = e.message; ctx.vars = keep.vars; ctx.zero.length = keep.zero; }
  });
  const orbit = ctx.uses.has('orbit');
  const decl = [...ctx.vars.values()].map(v => `${CU_GLTYPE[v.t]} ${v.gl} = ${CU_GLZERO[v.t]};`).join(' ');
  // APR_FAR: the far-away point of the picture's probe stands where it does for the lab's own escape radius of 64
  const code = `
#define APR_FAR 28.8
uniform float uCu[${CU_SLOTS}];
vec3 gCuC; float gCuPass;` + (orbit ? CU_GLSL_ORBIT : CU_GLSL_PLAIN) + `
vec3 cuRun(vec3 z, vec3 c, float n){
  // where a play stands: steps up to cuAt are taken, the one at cuAt as far as cuT, and the rest are left out
  float cuAt = 1e9, cuT = 1.0;
  if (uCu[${CU_PLAY_ON}] > 0.5){ if (gCuPass > uCu[${CU_PLAY_PASS}]) cuAt = -1.0; else if (gCuPass == uCu[${CU_PLAY_PASS}]){ cuAt = uCu[${CU_PLAY_ORD}]; cuT = uCu[${CU_PLAY_T}]; } }
  ${orbit ? 'vec3 oFirst = gCuF[gCarI], oLast = gCuL[gCarI], oMean = gCuS[gCarI] / max(gCuN[gCarI], 1.0); float oCount = gCuN[gCarI];' : ''}
  ${decl}
  ${body.join('\n  ')}
  return aprCap(z);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return cuRun(a, gCuC, n) - gCuC; }
vec3 sqr(vec3 a){ return cuRun(a, gCuC, 2.0) - gCuC; }
vec3 cmap(vec3 c){ return c; }`;
  let h = 5381;
  for (let i = 0; i < code.length; i++) h = ((h << 5) + h + code.charCodeAt(i)) | 0;
  const K = new Float32Array(CU_SLOTS);
  K.set(ctx.K);
  return { glsl: GL_APR + GL_MERC_PLAIN + GL_CARRY + CU_GLSL + code, key: (h >>> 0).toString(36) + '.' + code.length, K, run, zero: ctx.zero, errs, scopes, orbit };
}
// The rule as the state holds it now, read once and kept (a picture being saved holds an older state, so a few are kept).
const cuKept = new Map();
function cuProgram() {
  // rev counts the changes made through the page (cuChanged); a state without it is read by its text
  const steps = (S.custom && S.custom.steps) || [];
  const sig = S.custom && S.custom.rev !== undefined ? 'rev ' + S.custom.rev : JSON.stringify(steps.map(s => [s.id, s.kind, s.on !== false, s.p]));
  let r = cuKept.get(sig);
  if (!r) {
    r = cuBuild(steps);
    cuKept.set(sig, r);
    if (cuKept.size > 6) cuKept.delete(cuKept.keys().next().value);
  }
  return r;
}
// One whole pass of the rule in JavaScript, the twin of cuRun in the shader. st: what the orbit carries
// (CARRY.custom), or nothing for a point with no orbit behind it.
function cuRun(z, c, n, st) {
  const P = cuProgram(), k = st ? st.n : 0;
  const E = { z: [z[0], z[1], z[2]], c: c || [0, 0, 0], n, K: P.K, v: P.zero.map(t => CU_ZERO[t]()),
    first: st ? st.first : [0, 0, 0], last: st ? st.last : [0, 0, 0], mean: k > 0 ? scl(st.sum, 1 / k) : [0, 0, 0], count: k };
  for (const s of P.run) if (s.sw < 0 || P.K[s.sw] > 0.5) for (const f of s.fns) f(E);
  return cuCapped(E.z);
}
function cuCapped(z) {
  const m = Math.max(Math.abs(z[0]), Math.abs(z[1]), Math.abs(z[2]));
  if (m <= CU_CAP) return z;
  return isFinite(m) ? scl(z, CU_CAP / m) : [CU_CAP, 0, 0];   // not a number, or infinite: the orbit has left
}
// The rule in words, for the line under the Approach menu and the card.
function cuWords() {
  const steps = (S.custom && S.custom.steps) || [], on = steps.filter(s => s.on !== false && CU_BLOCKS[s.kind]);
  if (!on.length) return 'No step is switched on, so every point stays where it is.';
  return 'Each step of an orbit: ' + on.map((s, i) => `(${i + 1}) ${CU_BLOCKS[s.kind].words(s.p)}`).join('; ') + '.';
}

// Breaking a step down, one level at a time. Both return the new steps as [{ kind, p }], or null when the step is
// one operation already. taken: the names the rule has, so that a new name is a new one.
function cuFresh(taken) {
  const used = new Set(taken);
  return base => {
    let name = base, k = 1;
    while (used.has(name) || name in CU_GIVEN || CU_FN[name]) name = base + (++k);
    used.add(name);
    return name;
  };
}
// a block as its lines
function cuBroken(st, taken) {
  const B = CU_BLOCKS[st.kind];
  if (!B || B.plain || B.basic) return null;
  const names = {}, fresh = cuFresh(taken);
  return B.lines(cuSettings(st, B, null), base => names[base] || (names[base] = fresh(base))).map(text => ({ kind: 'formula', p: { text } }));
}
// a line as its single operations, innermost first. scope: the names the line can read, as cuBuild gives them.
function cuSplit(text, scope, taken) {
  const { target, src } = cuHalves(text), fresh = cuFresh(taken), out = [];
  const node = cuParse(src, { vars: new Map(scope.map(([name, t]) => [name, { t, gl: '', idx: 0 }])), zero: [], uses: new Set(), K: [], internal: false });
  // what can stand in a step's box as it is: a name, a number, a part of a name, or one of these with a minus
  const leaf = tr => (tr.leaf !== undefined ? tr.leaf : tr.part && tr.of.leaf !== undefined ? `${tr.of.leaf}.${tr.part}` : tr.op === 'neg' && tr.a[0].leaf !== undefined ? `-${tr.a[0].leaf}` : null);
  const emit = (tr, name) => {
    const as = leaf(tr);
    if (as !== null && name === undefined) return as;
    const p = {};
    let kind;
    if (as !== null) { kind = 'o_copy'; p.a0 = as; }
    else if (tr.part) { kind = 'o_part'; p.a0 = emit(tr.of); p.part = tr.part; }
    else {
      const args = tr.a.map(x => emit(x));
      kind = tr.op ? 'o_' + tr.op : 'f_' + tr.fn;
      if (!CU_BLOCKS[kind] || CU_BLOCKS[kind].arity !== args.length) { kind = 'formula'; p.text = `${name === undefined ? (name = fresh('t')) : name} = ${tr.fn}(${args.join(', ')})`; }
      else args.forEach((x, k) => { p['a' + k] = x; });
    }
    if (name === undefined) name = fresh('t');
    if (kind !== 'formula') p.out = name;
    out.push({ kind, p });
    return name;
  };
  emit(node.tree, target);
  return out.length === 1 && out[0].kind === 'formula' ? null : out;
}
// The names the rule's own steps make, for cuFresh.
function cuTaken(steps) {
  const out = [];
  for (const s of steps) {
    if (s.kind === 'slider') out.push(String(s.p.name));
    else if (s.kind === 'formula') { const m = /^\s*([A-Za-z][A-Za-z0-9]*)\s*=(?!=)/.exec(String(s.p.text)); if (m) out.push(m[1]); }
    else if (s.p.out !== undefined) out.push(String(s.p.out));
  }
  return out;
}

// Playing the steps. The picture is every starting point that has not been thrown out yet, and a play stops the
// orbits part of the way: S.custom.play = { pass, u } means that pass − 1 whole passes are done and, of the steps
// of the next pass that move the point, u have been taken (u need not be whole). null: every pass, the finished solid.
// A pass is one run through the steps. In a Mandelbrot picture that starts z at 0 the first iteration only carries
// each point to its own c, and the shader does not count it (carOrigin), so there the passes are one fewer.
const cuLead = () => (S.mode === 'm' && S.z0.trim() === '0' ? 1 : 0);
const cuPasses = () => Math.max(1, Math.round(S.iter) - cuLead());
const cuMoving = (P = cuProgram()) => P.run.filter(s => s.moves && (s.sw < 0 || P.K[s.sw] > 0.5));
// where the play stands, with nothing out of range: { pass, u, end } (end: the finished solid)
function cuPlayAt() {
  const np = cuPasses(), m = cuMoving().length, pl = S.custom.play;
  if (!pl || !m) return { pass: np, u: m, end: true };
  const pass = clamp(Math.round(pl.pass), 1, np), u = clamp(+pl.u || 0, 0, m);
  return { pass, u, end: pass >= np && u >= m };
}
// what the shader needs for it: null for the finished solid
function cuPlayNow() {
  if (S.learn || !S.custom.play) return null;
  const at = cuPlayAt(), mov = cuMoving();
  if (at.end) return null;
  const j = Math.min(Math.floor(at.u), mov.length - 1);
  // The picture takes at least two iterations. A pass after the one on show leaves every point where it is (cuAt
  // in the shader), so the second changes nothing.
  return { pass: at.pass, ord: mov[j].ord, t: at.u - j, iter: Math.max(2, at.pass + cuLead()) };
}
// The custom approach's own part of the scene's uniforms (see `uniforms` and `scene` in its entry).
function cuUniforms(gl, loc) {
  const K = cuProgram().K, at = cuPlayNow();
  K[CU_PLAY_ON] = at ? 1 : 0; K[CU_PLAY_PASS] = at ? at.pass : 0; K[CU_PLAY_ORD] = at ? at.ord : 0; K[CU_PLAY_T] = at ? at.t : 1;
  gl.uniform1fv(loc('uCu[0]'), K);
}
function cuScene() {
  const at = cuPlayNow();
  return { bail: cuBailOf(S.custom.bail), iter: at ? at.iter : 0 };
}
