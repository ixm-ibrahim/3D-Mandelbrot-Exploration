// The custom approach: a rule the user puts together from steps (S.custom.steps). One pass of the steps is one
// whole step of the orbit, z -> ..., the adding of c included, which is a step like any other.
//
// A rule has three sections (CU_SECS). The steps of "every iteration" are that pass. The steps of "once, before the
// iterations" are taken one time for each orbit, on the point it starts from. The steps of "once, after the
// iterations" are taken one time when the last iteration is done, and a point they land beyond the limit is thrown
// out like any other. A step that moves a point works on z, on c or on a point the rule has named (CU_ON), in
// whichever section it stands.
//
// Everything is written in one small formula language. A line is `name = formula`, and every kind of step is a
// few such lines with its settings put in (CU_BLOCKS[kind].lines). There are three levels of step: a block (a
// sphere inversion, a rotation about an axis, ...), a formula line, and a single operation (add, dot product, sine,
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
const CU_FREE = 121;         // slots 0 .. 120 are for the steps; then CU_ONCE, CU_LAST, CU_BOTH and CU_PLAY_T, _ON, _PASS, _ORD
// CU_ONCE: 1 while the steps taken once before the iterations are in use (the Learn tab leaves them out).
// CU_LAST: the number of the turn that takes the steps of "once, after", or 0 when no turn does.
const CU_ONCE = 121, CU_LAST = 122, CU_BOTH = 123, CU_PLAY_T = 124, CU_PLAY_ON = 125, CU_PLAY_PASS = 126, CU_PLAY_ORD = 127;
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
const CU_NO_ORBIT = 'Before the iterations the orbit has not begun: it has no first point, no point before, no average and no count yet.';
// what a formula may read besides the names it has made itself
const CU_GIVEN = { z: 'v', c: 'v', n: 's', pi: 's', radius: 's', theta: 's', phi: 's', first: 'v', last: 'v', mean: 'v', count: 's' };
// The length and the two angles of any point, written after it: z.radius, z.theta, z.phi, and the same for c or a
// point of the rule's own. Each is the function named here. The bare names of CU_GIVEN are short for those of z.
const CU_POLAR = { radius: 'len', theta: 'lon', phi: 'lat' };
const cuFlt = x => (!Number.isInteger(x) ? String(x) : Math.abs(x) < 1e15 ? x + '.0' : x.toExponential());
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
// A point part of the way from a to b, for a step that does not say itself what lies in between. Where a and b
// are equally far from the middle the step is a rotation, and the point goes round the middle by the shorter way
// (for two opposite points: half way round, about the upright axis where that can be); otherwise it goes straight across.
vec3 cuBlend(vec3 a, vec3 b, float t){
  float la = length(a), lb = length(b);
  if (abs(la - lb) > 1e-3 * max(la, lb) || la < 1e-20) return mix(a, b, t);
  float co = clamp(dot(a, b) / (la * lb), -1.0, 1.0), w = acos(co), sw = sin(w);
  vec3 p;
  if (sw > 1e-3) p = (sin((1.0 - t) * w) * a + sin(t * w) * b) / sw;
  else if (co > 0.0) p = mix(a, b, t);
  else {
    vec3 k = vec3(0.0, 0.0, 1.0) - a * (a.z / (la * la));
    if (dot(k, k) < 1e-12) k = vec3(1.0, 0.0, 0.0) - a * (a.x / (la * la));
    k = normalize(k);
    p = a * cos(PI * t) + cross(k, a) * sin(PI * t);
  }
  return p * (mix(la, lb, t) / max(length(p), 1e-30));
}
// The fold round the x-axis that sends the nearest of k planes through that axis onto the flat plane (foldk in
// 10-approaches.js), and the mirror at the angle b from the flat plane with its corner rounded over w (smFold).
vec3 cuFoldx(vec3 v, float kk){
  float k = max(2.0, floor(kk + 0.5)), rho = length(v.yz);
  if (rho < 1e-30) return v;
  float w = PI / k, psi = at2(v.z, v.y), a = abs(psi), j = floor(a / w + 0.5), d = a - j * w, a2;
  if (2.0 * j < k || (2.0 * j == k && d < 0.0)) a2 = mod(j, 2.0) < 0.5 ? d : -d;
  else a2 = PI + (mod(k - j, 2.0) < 0.5 ? d : -d);
  if (psi < 0.0) a2 = -a2;
  return vec3(v.x, rho * cos(a2), rho * sin(a2));
}
vec3 cuSoftMirror(vec3 v, float b, float w){
  float rho = length(v.yz);
  if (v.z == 0.0 || !(rho > 1e-30)) return v;
  float t = at2(abs(v.z), abs(v.y)) - b, g = !(w > 0.0) || abs(t) >= w ? b - abs(t) : b - (t * t / (2.0 * w) + 0.5 * w);
  return vec3(v.x, (v.y < 0.0 ? -1.0 : 1.0) * rho * cos(g), (v.z < 0.0 ? -1.0 : 1.0) * rho * sin(g));
}`;
// What an orbit carries. gCuPass: how many passes of the point's own orbit have counted, this one included (a play
// reads it). gCuCall: how many turns it has had in all, the one that starts at the origin included. For the names first, last, mean and count (the same steps as CARRY.custom), per orbit: the number of
// steps that have counted, its first point, the point of the step before, and the sum of its points.
const CU_HIST = 16;   // how many points of an orbit are kept by number, for point( )
// What the shader keeps for an orbit, and the three hooks of GL_CARRY that look after it. Always: the c of the step
// under way and the count of the point's own passes. orbit: the rule reads first, last, mean or count. hist: it asks
// for a point by its number, so the first CU_HIST points of each orbit are kept. kept: the values the rule itself
// keeps from one iteration to the next ("A value the orbit keeps"), each { t, gl0 } with gl0 what it starts as.
// cRun: a step of the iterations changes c, so the orbit carries c as its iterations have left it (gCuCk, and
// gCuCh: whether it holds one yet).
function cuCarryGlsl(orbit, hist, kept, cRun) {
  const decl = [], start = [], fit = [];
  if (cRun) {
    decl.push('vec3 gCuCk[4]; float gCuCh[4];');
    start.push('for (int i = 0; i < 4; i++){ gCuCk[i] = vec3(0.0); gCuCh[i] = 0.0; }');
    fit.push('gCuCk[i] = gCuCk[0] + (gCuCk[i] - gCuCk[0]) * s; gCuCh[i] = gCuCh[0];');
  }
  if (orbit) {
    decl.push('float gCuN[4]; vec3 gCuF[4], gCuP[4], gCuL[4], gCuS[4];');
    start.push('for (int i = 0; i < 4; i++){ gCuN[i] = 0.0; gCuF[i] = vec3(0.0); gCuP[i] = vec3(0.0); gCuL[i] = vec3(0.0); gCuS[i] = vec3(0.0); }');
    fit.push('gCuN[i] = gCuN[0];', 'gCuF[i] = gCuF[0] + (gCuF[i] - gCuF[0]) * s; gCuP[i] = gCuP[0] + (gCuP[i] - gCuP[0]) * s;', 'gCuL[i] = gCuL[0] + (gCuL[i] - gCuL[0]) * s; gCuS[i] = gCuS[0] + (gCuS[i] - gCuS[0]) * s;');
  }
  if (hist) {
    decl.push(`vec3 gCuH[${4 * CU_HIST}];`);
    start.push(`for (int i = 0; i < ${4 * CU_HIST}; i++) gCuH[i] = vec3(0.0);`);
    fit.push(`for (int k = 0; k < ${CU_HIST}; k++) gCuH[i * ${CU_HIST} + k] = gCuH[k] + (gCuH[i * ${CU_HIST} + k] - gCuH[k]) * s;`);
  }
  kept.forEach((k, j) => {
    decl.push(`${CU_GLTYPE[k.t]} gCuK${j}[4];`);
    start.push(`for (int i = 0; i < 4; i++) gCuK${j}[i] = ${k.gl0};`);
    fit.push(`gCuK${j}[i] = gCuK${j}[0] + (gCuK${j}[i] - gCuK${j}[0]) * s;`);
  });
  return `
${decl.join('\n')}
void carStart(){
  ${start.join('\n  ')}
  gCuC = vec3(0.0); gCuPass = 0.0; gCuCall = 0.0; gCarI = 0;
}
void carStep(vec3 z, vec3 c){
  gCuC = c;
  if (gCarI == 0) gCuCall += 1.0;
  if (carOrigin(z)) return;
  if (gCarI == 0) gCuPass += 1.0;${orbit ? `
  int i = gCarI;
  gCuN[i] += 1.0;
  if (gCuN[i] == 1.0){ gCuF[i] = z; gCuP[i] = z; }
  gCuL[i] = gCuP[i]; gCuP[i] = z; gCuS[i] += z;` : ''}${hist ? `
  if (gCuN[i] <= ${CU_HIST}.0) gCuH[i * ${CU_HIST} + int(gCuN[i]) - 1] = z;` : ''}
}
void carFit(int i, float s){
  ${fit.join('\n  ')}
}${hist ? `
// The point of this orbit with the number k: 1 is its first point, 2 its second. 0 is the point this iteration
// began with, -1 the one before it. A number the orbit has not reached, or past the ones kept, gives the nearest kept.
vec3 cuPoint(float k){
  float cnt = gCuN[gCarI], j = k > 0.5 ? k : cnt + k;
  j = clamp(floor(j + 0.5), 1.0, max(1.0, min(cnt, ${CU_HIST}.0)));
  return gCuH[gCarI * ${CU_HIST} + int(j) - 1];
}` : ''}`;
}
// the same in JavaScript, from what CARRY.custom keeps (E.hist, E.count)
function cuPointOf(E, k) {
  const j = clamp(Math.floor((k > 0.5 ? k : E.count + k) + 0.5), 1, Math.max(1, Math.min(E.count, CU_HIST)));
  return E.hist[j - 1] || [0, 0, 0];
}

// The functions of the language: CU_FN[name] is a list of forms, each with the kinds of its arguments (args), the
// kind of its answer (ret), its shader text (gl, from the arguments' shader texts) and its JavaScript (js, from values).
const CU_FN = {};
const cuDef = (name, args, ret, gl, js) => { (CU_FN[name] = CU_FN[name] || []).push({ args, ret, gl, js }); };
for (const name of ['sin', 'cos', 'tan', 'atan', 'sinh', 'cosh', 'tanh', 'abs', 'floor', 'ceil', 'sign']) cuDef(name, 's', 's', a => `${name}(${a})`, Math[name]);
cuDef('asinh', 's', 's', a => `asinh(${a})`, Math.asinh);
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
cuDef('foldx', 'vs', 'v', (a, b) => `cuFoldx(${a}, ${b})`, (v, k) => foldk(v, Math.max(2, Math.floor(k + 0.5))));
cuDef('softmirror', 'vss', 'v', (a, b, c) => `cuSoftMirror(${a}, ${b}, ${c})`, (v, b, w) => {
  const rho = Math.hypot(v[1], v[2]);
  if (v[2] === 0 || !(rho > 1e-300)) return v;
  const t = Math.atan2(Math.abs(v[2]), Math.abs(v[1])) - b, g = !(w > 0) || Math.abs(t) >= w ? b - Math.abs(t) : b - (t * t / (2 * w) + 0.5 * w);
  return [v[0], (v[1] < 0 ? -1 : 1) * rho * Math.cos(g), (v[2] < 0 ? -1 : 1) * rho * Math.sin(g)];
});
cuDef('cmul', 'vv', 'v', (a, b) => `vec3(cmul(${a}.xy, ${b}.xy), 0.0)`, (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0], 0]);
cuDef('conj', 'v', 'v', a => `(${a} * vec3(1.0, -1.0, -1.0))`, a => [a[0], -a[1], -a[2]]);
cuDef('quat', 'ssss', 'q', (w, x, y, z) => `vec4(${x}, ${y}, ${z}, ${w})`, (w, x, y, z) => [x, y, z, w]);
cuDef('quat', 'v', 'q', a => `vec4(${a}, 0.0)`, a => [a[0], a[1], a[2], 0]);
cuDef('qrot', 'vs', 'q', (a, b) => `cuQrot(${a}, ${b})`, cuQrot);
cuDef('conj', 'q', 'q', a => `cuQconj(${a})`, cuQconj);
cuDef('inv', 'q', 'q', a => `cuQinv(${a})`, cuQinv);
cuDef('qpow', 'qs', 'q', (a, b) => `cuQpow(${a}, ${b})`, cuQpow);
cuDef('re', 'q', 's', a => `${a}.w`, a => a[3]);
// a point rotated by a quaternion: rot(v, q), beside rot(v, axis, angle). turn(v, q) is its earlier name, which rules kept as text may hold
cuDef('rot', 'vq', 'v', (a, b) => `cuTurn(${a}, ${b})`, cuTurn);
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
      if (a.t === 'v' && CU_POLAR[name]) { a = call(CU_POLAR[name], [a]); continue; }
      if (name.length !== 1 || at < 0 || (a.t === 'v' && at > 2)) fail(a.t === 'v' ? 'A point has the parts .x, .y and .z, and its length and two angles: .radius, .theta and .phi.' : 'A quaternion has the parts .w, .x, .y and .z.');
      a = { t: 's', gl: `${a.gl}.${name}`, tree: { part: name, of: a.tree }, js: E => A(E)[at] };
    }
    return a;
  }
  function call(name, args) {
    if (name === 'point') {   // a point of the orbit by its number: it reads what the orbit carries, not only its arguments
      if (args.length !== 1 || args[0].t !== 's') fail('point( ) takes one number: 1 for the first point of the orbit, 2 for the second; 0 for the point this iteration began with, -1 for the one before it.');
      if (ctx.sec === 'pre') fail(CU_NO_ORBIT);
      ctx.uses.add('orbit'); ctx.uses.add('hist');
      const A = args[0].js;
      return { t: 'v', gl: `cuPoint(${args[0].gl})`, tree: { fn: 'point', a: [args[0].tree] }, js: E => cuPointOf(E, A(E)) };
    }
    if (name === 'same') {
      // The picture's distance estimate follows a few orbits right beside each point. Inside same( ) they take the
      // value the point's own orbit has there, which the point's pass leaves in gCuW (it runs first, see orbitDE).
      if (args.length !== 1 || (args[0].t !== 's' && args[0].t !== 'v')) fail('same( ) takes one number or one point.');
      if (ctx.sec === 'pre') fail('same( ) is for the steps of an iteration.');
      const sites = ctx.same || (ctx.same = []), k = sites.length;
      sites.push(args[0].t);
      return { t: args[0].t, gl: `(gCarI == 0 ? (gCuW${k} = ${args[0].gl}) : gCuW${k})`, tree: { fn: 'same', a: [args[0].tree] }, js: args[0].js };
    }
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
    if (name === '@tt') return { t: 's', gl: 'tt', tree, js: E => E.tt };   // how far a play has taken this step
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
    // z as a length and two angles, as it is when the formula is worked out, by the short names: sph(radius, theta, phi) is z
    if (name === 'radius') return { t: 's', gl: 'length(z)', tree, js: E => len(E.z) };
    if (name === 'theta') return { t: 's', gl: 'at2(z.y, z.x)', tree, js: E => Math.atan2(E.z[1], E.z[0]) };
    if (name === 'phi') return { t: 's', gl: 'cuLat(z)', tree, js: E => cuLat(E.z) };
    if (name === 'first' || name === 'last' || name === 'mean' || name === 'count') {
      if (ctx.sec === 'pre') fail(CU_NO_ORBIT);
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
// Reads one line. Returns { gl, js, z, c, free, needs }: the shader statement, js(E), which carries it out on E, whether
// the line moves the point (z) or changes c (c), and whether its formula can be worked out before the point is known
// (free: it reads neither z nor anything made from z; needs: the first name it reads that is z or made from z). A name that is new is added to ctx.vars; internal: the line
// comes from a block.
function cuLine(line, ctx, internal) {
  const { target, src } = cuHalves(line);
  if (!src.trim()) throw new Error('The formula is empty.');
  ctx.internal = internal;
  const node = cuParse(src, ctx), J = node.js;
  let free = true, needs = '';
  (function walk(tr) {
    if (tr.leaf === undefined) { if (tr.fn === 'point' || tr.fn === 'same') { free = false; needs = needs || tr.fn + '( )'; } (tr.a || [tr.of]).forEach(walk); return; }
    const u = ctx.vars.get(tr.leaf);
    if (['z', 'radius', 'theta', 'phi', 'first', 'last', 'mean', 'count'].includes(tr.leaf) || (u && u.free === false)) { free = false; needs = needs || tr.leaf; }
  })(node.tree);
  if (target === 'z' || target === 'c') {
    if (node.t !== 'v') throw new Error(`${target} is a point, and this formula gives ${CU_KINDS[node.t]}. A point is written vec(x, y, z).`);
    return target === 'z' ? { gl: `z = ${node.gl};`, z: true, free, needs, js: E => { E.z = J(E); } } : { gl: `c = ${node.gl};`, z: false, c: true, free, needs, js: E => { E.c = J(E); } };
  }
  if (target in CU_GIVEN || CU_FN[target] || target === 'point' || target === 'same') throw new Error(`“${target}” already means something here, so it cannot be a name of your own. Pick another.`);
  if (target[0] !== '@' && !CU_NAME.test(target)) throw new Error('A name is made of letters and digits and starts with a letter.');
  let v = ctx.vars.get(target);
  if (v && v.t !== node.t) throw new Error(`“${target}” was ${CU_KINDS[v.t]} in an earlier step and would be ${CU_KINDS[node.t]} here. Use another name.`);
  if (!v) {
    // a name of the user's own is spelt by its section in the shader, since two sections may each have one of the same name
    const sec = ctx.sec || 'main';
    v = { t: node.t, idx: ctx.zero.length, gl: target[0] === '@' ? target.slice(1) : { pre: 'a_', main: 'u_', post: 'p_' }[sec] + target, sec };
    ctx.zero.push(node.t); ctx.vars.set(target, v);
    if (ctx.all) ctx.all.push(v);
  }
  v.free = free;
  const at = v.idx;
  return { gl: `${v.gl} = ${node.gl};`, z: false, free, needs, js: E => { E.v[at] = J(E); } };
}

// The kinds of step. params: the settings a step of that kind has, each { key, label, type, def } with type
//   'num'     a number, the power n, a number of the user's own, or a formula that gives one (min, max, step: the
//             range of its slider; bare: a box alone)
//   'vec'     a point: three numbers, or a formula that gives one (picks: the list its menu offers)
//   'any'     a value of any kind: a name, a number or a formula
//   'choice'  one of options [[value, label], ...]
//   'name'    the name the step gives its answer;   'text'  a whole line, name = formula
// lines(P, v, t): the step as lines of the language. P[key] is the setting, ready to stand inside a formula;
// v(base) is a name for a value the lines keep (the same name for the same base). words(p): the step in a few words.
// tween: the block knows what lies between its start and its end. Its lines are then handed t, the name of how far
// a play has taken the step (0 to 1), and work the in-between out themselves: an angle is multiplied by a number
// that grows from 1, a slide goes part of the way. Without t (a step being broken down) they are the whole step.
// plain: the step is a line already; basic: the step is one operation. Neither is a block.
const CU_AXES = [['the upright axis (z)', 'vec(0, 0, 1)'], ['the x-axis', 'vec(1, 0, 0)'], ['the y-axis', 'vec(0, 1, 0)'],
  ['the point itself, where it is now (z)', 'z'], ['c', 'c'], ['the first point of the orbit', 'first'], ['the point of the iteration before', 'last'],
  ['a point of the orbit by its number: point(2)', 'point(2)'],
  ['the average of the orbit’s points so far', 'mean'], ['square to the point and the upright axis', 'cross(vec(0, 0, 1), z)'],
  ['square to the point and the x-axis', 'cross(vec(1, 0, 0), z)'], ['square to the point and c', 'cross(z, c)'],
  ['square to the point and the iteration before', 'cross(z, last)'], ['from the iteration before to this point', 'z - last']];
const CU_PLACES = [['the middle (0, 0, 0)', 'vec(0, 0, 0)'], ['c', 'c'], ['the point itself, where it is now (z)', 'z'],
  ['the first point of the orbit', 'first'], ['the point of the iteration before', 'last'], ['a point of the orbit by its number: point(2)', 'point(2)'],
  ['the average of the orbit’s points so far', 'mean']];
const cuAxis = (key, label, def) => ({ key, label, type: 'vec', def, picks: CU_AXES });
const cuPlace = (key, label, def) => ({ key, label, type: 'vec', def, picks: CU_PLACES });
// a setting in words: the name its menu has for it, or the formula as typed
const cuCalled = (list, text) => { const t = String(text).replace(/\s+/g, ''), hit = list.find(o => o[1].replace(/\s+/g, '') === t); return hit ? hit[0] : String(text); };
const cuAx = text => cuCalled(CU_AXES, text), cuPl = text => cuCalled(CU_PLACES, text);
const cuTimes = (key, label) => ({ key, label, type: 'num', def: 'n', min: -4, max: 8, step: 0.05 });
const cuDegrees = (key, label, def) => ({ key, label, type: 'num', def, min: -180, max: 180, step: 1, deg: true });   // deg: the setting is an angle in degrees
const cuQuatParts = [['w', 'Real part', '0.7071'], ['x', 'i part', '0'], ['y', 'j part', '0'], ['z', 'k part', '0.7071']]
  .map(([key, label, def]) => ({ key, label, type: 'num', def, min: -2, max: 2, step: 0.01 }));
// Which point a move works on: the point z, c, or a point the rule has named. Every block that moves a point has
// this setting (the key `on`), and its lines, which speak of z, are read for that point (cuLinesOf).
const CU_ON = { key: 'on', label: 'Works on', type: 'target', def: 'z' };
function cuLinesOf(B, P, v, t) {
  const on = P.on === undefined ? 'z' : P.on;
  if (on === 'z') return B.lines(P, v, t);
  // The settings go in after the name has taken the place of z, so that a z typed in a setting is still the orbit's point.
  const hold = {}, back = [];
  for (const sp of B.params) {
    if (sp.type === 'choice' || sp.type === 'target' || typeof P[sp.key] !== 'string') hold[sp.key] = P[sp.key];
    else { hold[sp.key] = `⟦${back.length}⟧`; back.push(P[sp.key]); }
  }
  return B.lines(hold, v, t).map(l => l.replace(/(^|[^\w.@])z(?![\w(])/g, (m, a) => a + on).replace(/⟦(\d+)⟧/g, (m, k) => back[+k]));
}
// a setting on its way: a factor that grows from 1 to x, an amount that grows from 0 to x
const cuTw1 = (x, t) => (t ? `(1 + (${x} - 1)*${t})` : x), cuTw0 = (x, t) => (t ? `((${x})*${t})` : `(${x})`), cuTwBy = t => (t ? '*' + t : '');
// the lines that split z by an axis: h is how far along the axis the point is, w the rest of it
const cuSplitZ = (P, v) => [`${v('axis')} = unit(${P.axis})`, `${v('h')} = dot(z, ${v('axis')})`, `${v('w')} = z - ${v('axis')}*${v('h')}`];
// The ways a length is measured: [value, name in the menu, the formula for z, the words]. Straight is the usual
// length. The Manhattan way adds up how far the point is along each of the three axes, and the third takes the
// largest of those three. Length 1 is a ball for the first, an eight-sided diamond for the second, a cube for the third.
const CU_MEASURES = [['straight', 'straight (the usual way)', 'len(z)', ''],
  ['manhattan', 'the Manhattan way: |x| + |y| + |z|', 'abs(z.x) + abs(z.y) + abs(z.z)', ', measured the Manhattan way,'],
  ['largest', 'by the largest of |x|, |y|, |z|', 'max(abs(z.x), max(abs(z.y), abs(z.z)))', ', measured by its largest part,']];
const cuMeasure = id => CU_MEASURES.find(m => m[0] === id) || CU_MEASURES[0];
const CU_BLOCKS = {
  len: { title: 'Raise the length to a power', group: 'Length and angles',
    params: [cuTimes('p', 'Power'), { key: 'measure', label: 'The length is measured', type: 'choice', def: 'straight', options: CU_MEASURES.map(m => [m[0], m[1]]) }],
    tween: true, lines: (P, v, t) => [`${v('r')} = ${cuMeasure(P.measure)[2]}`, `z = z * ${v('r')}^${cuTw0(`${P.p} - 1`, t)}`],
    words: p => `raise the length${cuMeasure(p.measure)[3]} to the power ${p.p}` },
  lon: { title: 'Multiply the angle round an axis', group: 'Length and angles',
    params: [cuAxis('axis', 'Axis', 'vec(0, 0, 1)'), cuAxis('from', 'Angle counted from', 'vec(1, 0, 0)'), cuTimes('times', 'Multiply by'), cuDegrees('plus', 'Then add, degrees', '0')],
    tween: true, lines: (P, v, t) => [...cuSplitZ(P, v),
      `${v('e1')} = unit(${P.from} - ${v('axis')}*dot(${P.from}, ${v('axis')}))`, `${v('e2')} = cross(${v('axis')}, ${v('e1')})`,
      `${v('ang')} = atan2(dot(${v('w')}, ${v('e2')}), dot(${v('w')}, ${v('e1')}))*${cuTw1(P.times, t)} + rad(${P.plus})${cuTwBy(t)}`,
      `z = ${v('axis')}*${v('h')} + (${v('e1')}*cos(${v('ang')}) + ${v('e2')}*sin(${v('ang')}))*len(${v('w')})`],
    words: p => `multiply the angle round ${cuAx(p.axis)} by ${p.times}` },
  lat: { title: 'Multiply the angle of the height', group: 'Length and angles',
    params: [cuAxis('axis', 'Height along', 'vec(0, 0, 1)'),
      { key: 'from', label: 'Angle counted', type: 'choice', def: 'plane', options: [['plane', 'up from the plane square to the axis'], ['axis', 'down from the axis (the Mandelbulb)']] },
      cuTimes('times', 'Multiply by'), cuDegrees('plus', 'Then add, degrees', '0')],
    tween: true, lines: (P, v, t) => [...cuSplitZ(P, v), `${v('r')} = len(z)`, ...(P.from === 'axis'
      ? [`${v('ang')} = atan2(len(${v('w')}), ${v('h')})*${cuTw1(P.times, t)} + rad(${P.plus})${cuTwBy(t)}`, `z = (unit(${v('w')})*sin(${v('ang')}) + ${v('axis')}*cos(${v('ang')}))*${v('r')}`]
      : [`${v('ang')} = atan2(${v('h')}, len(${v('w')}))*${cuTw1(P.times, t)} + rad(${P.plus})${cuTwBy(t)}`, `z = (unit(${v('w')})*cos(${v('ang')}) + ${v('axis')}*sin(${v('ang')}))*${v('r')}`])],
    words: p => `multiply the angle of the height along ${cuAx(p.axis)} by ${p.times}` + (p.from === 'axis' ? ', counted from the axis' : '') },
  merc: { title: 'Multiply the height the Mercator way', group: 'Length and angles',
    params: [cuAxis('axis', 'Height along', 'vec(0, 0, 1)'), cuTimes('times', 'Multiply by')],
    tween: true, lines: (P, v, t) => [...cuSplitZ(P, v), `${v('r')} = len(z)`, `${v('m')} = atanh(${v('h')} / ${v('r')})*${cuTw1(P.times, t)}`,
      `z = (unit(${v('w')}) / cosh(${v('m')}) + ${v('axis')}*tanh(${v('m')}))*${v('r')}`],
    words: p => `multiply the height along ${cuAx(p.axis)} by ${p.times} on the scale of a Mercator map` },
  inv: { title: 'Sphere inversion', group: 'Moves of space',
    params: [cuPlace('centre', 'Centre of the sphere', 'vec(0, 0, 0)'), { key: 'radius', label: 'Radius', type: 'num', def: '1', min: 0.05, max: 4, step: 0.01 },
      { key: 'side', label: 'It moves', type: 'choice', def: 'all', options: [['all', 'every point'], ['in', 'only the points inside the sphere'], ['out', 'only the points outside the sphere']] }],
    // with one side only, the sphere is a mirror that the other side looks into: the points of that side stay
    lines: (P, v) => { const to = `${P.centre} + ${v('d')}*(${P.radius}*${P.radius} / dot(${v('d')}, ${v('d')}))`;
      return [`${v('d')} = z - ${P.centre}`, P.side === 'in' || P.side === 'out' ? `z = if(dot(${v('d')}, ${v('d')}) ${P.side === 'in' ? '<' : '>'} ${P.radius}*${P.radius}, ${to}, z)` : `z = ${to}`]; },
    words: p => (p.side === 'in' || p.side === 'out' ? `invert what is ${p.side === 'in' ? 'inside' : 'outside'} the sphere of radius ${p.radius} round ${cuPl(p.centre)}, and leave the rest` : `invert space through the sphere of radius ${p.radius} round ${cuPl(p.centre)}`) },
  rot: { title: 'Rotate about an axis', group: 'Moves of space',
    params: [cuAxis('axis', 'Axis', 'vec(0, 0, 1)'), cuDegrees('angle', 'Angle, degrees', '90')],
    tween: true, lines: (P, v, t) => [`${v('axis')} = unit(${P.axis})`, `${v('ang')} = rad(${P.angle})${cuTwBy(t)}`,
      `z = z*cos(${v('ang')}) + cross(${v('axis')}, z)*sin(${v('ang')}) + ${v('axis')}*(dot(${v('axis')}, z)*(1 - cos(${v('ang')})))`],
    words: p => `rotate by ${p.angle}° about ${cuAx(p.axis)}` },
  mirror: { title: 'Mirror in a plane', group: 'Moves of space',
    params: [cuAxis('normal', 'The plane is square to', 'vec(0, 1, 0)'), cuPlace('through', 'and passes through', 'vec(0, 0, 0)')],
    tween: true, lines: (P, v, t) => [`${v('k')} = unit(${P.normal})`, `z = z - ${v('k')}*(2*dot(z - ${P.through}, ${v('k')}))${cuTwBy(t)}`],
    words: p => `mirror in the plane square to ${cuAx(p.normal)}` },
  fold: { title: 'Fold onto one side of a plane', group: 'Moves of space',
    params: [cuAxis('normal', 'The plane is square to', 'vec(0, 1, 0)'), cuPlace('through', 'and passes through', 'vec(0, 0, 0)')],
    tween: true, lines: (P, v, t) => [`${v('k')} = unit(${P.normal})`, `z = z - ${v('k')}*(2*min(0, dot(z - ${P.through}, ${v('k')})))${cuTwBy(t)}`],
    words: p => `fold the far side of the plane square to ${cuAx(p.normal)} onto the near side` },
  // A fan fold. Its creases are planes that all hold the x-axis, as many as `planes`, the first of them half of
  // 180°/planes from the flat plane: what lies between that crease and the flat plane stays, and the rest is folded
  // across the creases into that wedge.
  foldx: { title: 'Fold along the x-axis, towards the flat plane', group: 'Moves of space',
    params: [{ key: 'planes', label: 'Number of creases', type: 'num', def: '2', min: 2, max: 8, step: 1 }],
    // on its way the point goes round the x-axis, from its own angle to the one the fold gives it
    tween: true, lines: (P, v, t) => [`${v('rho')} = len(vec(0, z.y, z.z))`, `${v('gap')} = pi / ${P.planes}`, `${v('psi')} = atan2(z.z, z.y)`, `${v('a')} = abs(${v('psi')})`,
      `${v('j')} = floor(${v('a')} / ${v('gap')} + 0.5)`, `${v('d')} = ${v('a')} - ${v('j')}*${v('gap')}`,
      `${v('near')} = if(2*${v('j')} < ${P.planes}, 1, if(2*${v('j')} == ${P.planes}, ${v('d')} < 0, 0))`,
      `${v('ang')} = if(${v('near')}, if(mod(${v('j')}, 2) < 0.5, ${v('d')}, -${v('d')}), pi + if(mod(${P.planes} - ${v('j')}, 2) < 0.5, ${v('d')}, -${v('d')}))*if(${v('psi')} < 0, -1, 1)`,
      ...(t ? [`${v('ang')} = ${v('psi')}*(1 - ${t}) + ${v('ang')}*${t}`] : []),
      `z = vec(z.x, ${v('rho')}*cos(${v('ang')}), ${v('rho')}*sin(${v('ang')}))`],
    words: p => `fold towards the flat plane, across ${p.planes} creases along the x-axis` },
  softx: { title: 'Mirror at an angle along the x-axis, with a soft corner', group: 'Moves of space',
    params: [{ key: 'angle', label: 'The mirror’s angle from the flat plane, degrees', type: 'num', def: '45', min: 0, max: 90, step: 1, deg: true },
      { key: 'soft', label: 'How wide the soft corner is, degrees', type: 'num', def: '20', min: 0, max: 45, step: 1, deg: true }],
    // on its way the point goes round the x-axis, the short way, to where the mirror puts it; the whole step is the mirror itself
    tween: true, lines: (P, v, t) => (!t ? [`z = softmirror(z, rad(${P.angle}), rad(${P.soft}))`] : [`${v('to')} = softmirror(z, rad(${P.angle}), rad(${P.soft}))`,
      `${v('rho')} = len(vec(0, z.y, z.z))`, `${v('a')} = atan2(z.z, z.y)`, `${v('d')} = atan2(${v('to')}.z, ${v('to')}.y) - ${v('a')}`, `${v('d')} = ${v('d')} - 2*pi*floor(${v('d')}/(2*pi) + 0.5)`,
      `z = if(${t} < 1, vec(z.x, ${v('rho')}*cos(${v('a')} + ${v('d')}*${t}), ${v('rho')}*sin(${v('a')} + ${v('d')}*${t})), ${v('to')})`]),
    words: p => `mirror back towards the flat plane what is steeper than ${p.angle}° from it, with a corner ${p.soft}° soft` },
  scale: { title: 'Stretch', group: 'Moves of space',
    params: [{ key: 'by', label: 'Multiply every length by', type: 'num', def: '2', min: -3, max: 3, step: 0.01 }],
    tween: true, lines: (P, v, t) => [`z = z*${cuTw1(P.by, t)}`],
    words: p => `multiply every length by ${p.by}` },
  shift: { title: 'Slide', group: 'Moves of space',
    params: [cuPlace('by', 'Slide by', 'vec(1, 0, 0)')],
    tween: true, lines: (P, v, t) => [`z = z + ${P.by}${cuTwBy(t)}`],
    words: p => `slide by ${p.by}` },
  quatpow: { title: 'Quaternion power', group: 'Quaternions and matrices',
    params: [cuTimes('p', 'Power')],
    tween: true, lines: (P, v, t) => [`${v('r')} = len(z)`, `${v('side')} = vec(0, z.y, z.z)`, `${v('ang')} = atan2(len(${v('side')}), z.x)*${cuTw1(P.p, t)}`,
      `z = (vec(1, 0, 0)*cos(${v('ang')}) + unit(${v('side')})*sin(${v('ang')}))*${v('r')}^${cuTw1(P.p, t)}`],
    words: p => `take the quaternion power ${p.p} of the point, read as x + yi + zj` },
  quatmul: { title: 'Multiply by a quaternion', group: 'Quaternions and matrices',
    params: [...cuQuatParts, { key: 'side', label: 'The quaternion stands', type: 'choice', def: 'right', options: [['right', 'on the right: z · q'], ['left', 'on the left: q · z']] }],
    lines: P => [`z = aspoint(${P.side === 'left' ? `quat(${P.w}, ${P.x}, ${P.y}, ${P.z}) * asquat(z)` : `asquat(z) * quat(${P.w}, ${P.x}, ${P.y}, ${P.z})`})`],
    words: p => `multiply the point, read as x + yi + zj, by the quaternion ${p.w} + ${p.x}i + ${p.y}j + ${p.z}k` },
  quatturn: { title: 'Rotate by a quaternion', group: 'Quaternions and matrices',
    params: [...cuQuatParts],
    // on its way the point goes round the quaternion's axis, the short way; the whole step is the quaternion's own rotation
    tween: true, lines: (P, v, t) => (!t ? [`z = rot(z, quat(${P.w}, ${P.x}, ${P.y}, ${P.z}))`] : [`${v('q')} = quat(${P.w}, ${P.x}, ${P.y}, ${P.z})`, `${v('ax')} = vec(${v('q')})`,
      `${v('ang')} = 2*atan2(len(${v('ax')}), abs(re(${v('q')})))*if(re(${v('q')}) < 0, -1, 1)`,
      `z = if(${t} < 1, rot(z, ${v('ax')}, ${v('ang')}*${t}), rot(z, ${v('q')}))`]),
    words: p => `rotate by the quaternion ${p.w} + ${p.x}i + ${p.y}j + ${p.z}k (q · z · q⁻¹)` },
  matrix: { title: 'Multiply by a matrix', group: 'Quaternions and matrices', grid: 3,
    params: ['1', '0', '0', '0', '1', '0', '0', '0', '1'].map((def, k) => ({ key: 'm' + k, label: `Row ${Math.floor(k / 3) + 1}, column ${k % 3 + 1}`, type: 'num', def, bare: true, step: 0.05 })),
    lines: P => [`z = mat(${[0, 1, 2, 3, 4, 5, 6, 7, 8].map(k => P['m' + k]).join(', ')}) * z`],
    words: () => 'multiply by the matrix' },
  addc: { title: 'Add c', group: 'Adding',
    params: [cuPlace('what', 'Add', 'c'), { key: 'times', label: 'this many times', type: 'num', def: '1', min: -2, max: 2, step: 0.01 }],
    tween: true, lines: (P, v, t) => [`z = z + ${P.what}*${P.times}${cuTwBy(t)}`],
    words: p => (cuIsNum(p.times) && cuNum(p.times) === 1 ? `add ${cuPl(p.what)}` : `add ${p.times} times ${cuPl(p.what)}`) },
  formula: { title: 'A formula of your own', group: 'Your own', plain: true,
    params: [{ key: 'text', label: 'name = formula', type: 'text', def: 'r = len(z)' }],
    lines: P => [P.text],
    words: p => p.text },
  // What the name holds when an iteration ends is what it holds when the next one comes to this step. The step
  // itself is read by cuBuild, not through lines.
  keep: { title: 'A value the orbit keeps', group: 'Your own', plain: true, basic: true,
    params: [{ key: 'name', label: 'Name', type: 'name', def: 'kept' }, { key: 'start', label: 'It starts as (a number, or a point of numbers)', type: 'text', def: '0' }],
    lines: () => [],
    words: p => `${p.name} is kept from one iteration to the next, and starts as ${p.start}` },
  slider: { title: 'A number with a slider', group: 'Your own', plain: true, basic: true,
    params: [{ key: 'name', label: 'Name', type: 'name', def: 't' }, { key: 'value', label: 'Value', type: 'num', def: '0.5', min: 0, max: 1, step: 0.01, ranged: true, own: true },
      { key: 'min', label: 'Slider from', type: 'num', def: '0', bare: true, fixed: true }, { key: 'max', label: 'to', type: 'num', def: '1', bare: true, fixed: true }],
    lines: P => [`${P.name} = ${P.value}`],
    words: p => `${p.name} = ${p.value}` },
};
// the blocks that move a point: each can be set to work on z, on c, or on a point the rule has named
const CU_MOVES = ['len', 'lon', 'lat', 'merc', 'inv', 'rot', 'mirror', 'fold', 'foldx', 'softx', 'scale', 'shift', 'quatpow', 'quatmul', 'quatturn', 'matrix', 'addc'];
for (const kind of CU_MOVES) CU_BLOCKS[kind].params.unshift(CU_ON);
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
  ['f_rot', 'Rotate a point about an axis', 'Points', 'pt', [['Point', 'z'], ['axis', 'vec(0, 0, 1)'], ['angle, in radians', 'rad(90)']]],
  ['f_invert', 'Invert a point through a sphere', 'Points', 'pt', [['Point', 'z'], ['centre', 'vec(0, 0, 0)'], ['radius', '1']]],
  ['f_mirror', 'Mirror a point in a plane', 'Points', 'pt', [['Point', 'z'], ['the plane is square to', 'vec(0, 1, 0)']]],
  ['f_cpow', 'Flat power of x and y', 'Points', 'pt', [['Point', 'z'], ['power', 'n']]],
  ['f_foldx', 'Fold a point round the x-axis onto the flat plane', 'Points', 'pt', [['Point', 'c'], ['planes that land on the flat plane', '2']]],
  ['f_softmirror', 'Mirror a point at an angle from the flat plane, with a soft corner', 'Points', 'pt', [['Point', 'c'], ['the mirror’s angle, in radians', 'rad(45)'], ['how wide the soft corner is, in radians', 'rad(20)']]],
  ['f_cmul', 'Multiply two flat points, as complex numbers', 'Points', 'pt', [['This', 'flat(z)'], ['times this', 'flat(z)']]],
  ['f_conj', 'Flip the signs of y and z', 'Points', 'pt', [['Of', 'z']]],
  ['f_point', 'A point of the orbit, by its number', 'Points', 'pt', [['Which: 1 the first, 0 this one, −1 the one before', '1']]],
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
  ['f_qrot', 'The quaternion of a rotation about an axis', 'Quaternion and matrix pieces', 'q', [['Axis', 'vec(0, 0, 1)'], ['angle, in radians', 'rad(90)']]],
  ['f_qpow', 'A quaternion to a power', 'Quaternion and matrix pieces', 'q', [['Quaternion', 'asquat(z)'], ['power', 'n']]],
  ['f_inv', 'One over a quaternion or a matrix', 'Quaternion and matrix pieces', 'q', [['Of', 'asquat(z)']]],
  ['f_re', 'Real part of a quaternion', 'Quaternion and matrix pieces', 'real', [['Of', 'asquat(z)']]],
  ['f_turn', 'Rotate a point by a quaternion', 'Quaternion and matrix pieces', 'pt', [['Point', 'z'], ['quaternion', 'qrot(vec(0, 0, 1), rad(90))']]],
  ['f_mat', 'Make a matrix from nine numbers', 'Quaternion and matrix pieces', 'mx', ['1', '0', '0', '0', '1', '0', '0', '0', '1'].map((d, k) => [`Row ${Math.floor(k / 3) + 1}, column ${k % 3 + 1}`, d])],
  ['f_rotmat', 'The matrix of a rotation about an axis', 'Quaternion and matrix pieces', 'mx', [['Axis', 'vec(0, 0, 1)'], ['angle, in radians', 'rad(90)']]],
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
// The sections of a rule, in the order they are taken: the steps taken once before the iterations, the steps of
// every iteration, and the steps taken once after the last one. A step says which it stands in (sec; left out:
// every iteration). Any step can stand in any of them, but for a value the orbit keeps, which belongs to the
// iterations. S.custom.steps holds the steps in the order of their sections.
const CU_SECS = ['pre', 'main', 'post'];
// A kind that a rule's text may name and that is another kind set a certain way: what the step is, from its settings.
const CU_ALSO = {
  cfoldx: p => ({ kind: 'foldx', p: { ...p, on: 'c' }, sec: 'pre' }),
  csoft: p => ({ kind: 'softx', p: { ...p, on: 'c' }, sec: 'pre' }),
  cmap: p => ({ kind: 'formula', p: { text: 'c = ' + (typeof p.text === 'string' && p.text.trim() ? p.text : 'c') }, sec: 'pre' }),
};
const cuSecOf = st => (st.kind === 'keep' ? 'main' : st.sec === 'pre' || st.sec === 'post' ? st.sec : 'main');
const cuSorted = steps => CU_SECS.flatMap(sec => steps.filter(st => cuSecOf(st) === sec));   // each section keeps its own order
// Rules to start from: each a list of [kind, settings that differ from the kind's own, section where it is not the
// iterations]. bail: how far a point may go (CU_BAIL where it is left out). reach: how far out the dots of a play
// start (2 where it is left out). say: a sentence for the moment the rule is loaded.
// lab: the rule is the approach of that id in the Approach list, written as steps (the same numbers, at any power above 0).
const CU_STARTS = [
  { name: 'Sphere inversions, one plane', lab: 'mercator', steps: [['len'], ['lon'], ['merc'], ['addc']] },
  { name: 'Sphere inversions, two planes', lab: 'fold', steps: [['foldx', { on: 'c' }, 'pre'], ['foldx'], ['len'], ['lon'], ['merc'], ['addc']] },
  { name: 'Quaternion square (Lathe)', lab: 'lathe', steps: [['quatpow'], ['addc']] },
  { name: 'Quaternion square, twisted', lab: 'tilt', steps: [['slider', { name: 'tilt', value: '45', min: '-90', max: '90' }], ['rot', { angle: 'tilt' }], ['quatpow'], ['rot', { angle: '-n*tilt' }], ['addc']] },
  { name: 'Mandelbulb', lab: 'bulb', steps: [['len'], ['lon'], ['lat'], ['addc']] },
  { name: 'Mandelbulb, classic', lab: 'classic', steps: [['len'], ['lon'], ['lat', { from: 'axis' }], ['addc']] },
  { name: 'Split', lab: 'split', steps: [['formula', { text: 'z = vec(cpow(z, n).x, cpow(z, n).y, z.z^n)' }], ['addc']] },
  { name: 'Parts of no size', lab: 'partsnone', steps: [
    ['formula', { text: 'lift = atan2((n + 1)*sin(z.phi), (n + 1)*cos(z.phi) - (n - 1)) - atan2(-(n - 1)*sin(z.phi), (n + 1) - (n - 1)*cos(z.phi))' }],
    ['formula', { text: 'z = sph(z.radius^n, z.theta*n, lift)' }], ['addc']] },
  { name: 'Burning ship: two folds, then one plane', steps: [['fold', { normal: 'vec(1, 0, 0)' }], ['fold', { normal: 'vec(0, 1, 0)' }], ['len'], ['lon'], ['merc'], ['addc']] },
  { name: 'Box folds and a sphere fold (the Mandelbox)', bail: 12, reach: 4, say: 'This solid is wide, so the dots of the play start within 4 of the middle. Reset view, at the foot of the picture, shows all of that ball.', steps: [
    ['formula', { text: 'z = vec(clamp(z.x, -1, 1), clamp(z.y, -1, 1), clamp(z.z, -1, 1))*2 - z' }], ['formula', { text: 'rr = dot(z, z)' }],
    ['formula', { text: 'z = z * if(rr < 0.25, 4, if(rr < 1, 1/rr, 1))' }], ['scale', { by: '-1.5' }], ['addc']] },
  { name: 'The two angles by name: z.radius, z.theta, z.phi', steps: [['formula', { text: 'z = sph(z.radius^n, z.theta*n, z.phi*n)' }], ['addc']] },
  { name: 'A bare start: the length, then add c', steps: [['len'], ['addc']] },
];
function cuStepOf(kind, p, id, sec) {
  const st = { id, kind, on: true, p: { ...Object.fromEntries(CU_BLOCKS[kind].params.map(s => [s.key, s.def])), ...p }, sec };
  const at = cuSecOf(st);   // a kind that belongs to one section stands there, whatever was asked
  if (at === 'main') delete st.sec; else st.sec = at;
  return st;
}
const cuStartSteps = k => cuSorted(CU_STARTS[k].steps.map(([kind, p, sec], i) => cuStepOf(kind, p, i + 1, sec)));
// What the play shows and how, apart from the rule: the dots, the surface or both (see), the dots themselves (how
// many, where they start and how far out, what their colour says, whose whole paths are drawn, whether new ones come
// in for those thrown out), how strongly the dots and the surface are drawn (dotsA, skinA: 1 is full), the guides,
// both pictures, the speed, and whether Play runs on from one iteration into the next (through). The starting values are the Learn tab's, but for
// the dots, of which there are many; both pictures stand side by side, and Play runs through every iteration.
const cuShowDefault = () => ({ see: 'dots', guides: true, both: true, speed: 'normal', through: true, dotsA: 1, skinA: 1, count: 'many', lay: 'both', tint: 'mix', orbits: 'few', refill: true, reach: 2 });
const cuDefault = () => { const steps = cuStartSteps(0); return { steps, next: steps.length + 1, rev: 0, bail: CU_BAIL, play: null, ...cuShowDefault(), rough: false }; };
const cuBailOf = x => clamp(+x || CU_BAIL, 1.2, 64);
// A list of steps from text of any origin (a saved rule, pasted text): every step checked, every id made afresh.
// Returns null when the text holds no step that can be used.
function cuClean(list) {
  if (!Array.isArray(list)) return null;
  const steps = [];
  let first = -1;   // the first step that the text names by a kind of CU_ALSO: a change of c before the iterations
  for (const told of list.slice(0, CU_MAX_STEPS)) {
    const also = told && CU_ALSO[told.kind], raw = also ? { ...told, ...also(told.p || {}) } : told, B = raw && CU_BLOCKS[raw.kind];
    if (!B) continue;
    const p = {};
    for (const sp of B.params) { const x = raw.p && raw.p[sp.key]; p[sp.key] = typeof x === 'string' || typeof x === 'number' ? String(x).slice(0, 400) : sp.def; }
    // `what` is another word a rule's text may have for the point a fold or a mirror works on
    if ((raw.kind === 'foldx' || raw.kind === 'softx') && raw.p && raw.p.on === undefined && raw.p.what === 'c') p.on = 'c';
    if (also && first < 0) first = steps.length;
    // a step may carry a name of the user's own: the saved step it was made from
    const name = typeof raw.name === 'string' ? raw.name.trim().slice(0, 40) : '';
    steps.push({ id: steps.length + 1, kind: raw.kind, on: raw.on !== false, p, sec: raw.sec, ...(name ? { name } : {}) });
  }
  // A rule that names no section: a slider that stands before such a change of c is there for it to read, so it
  // goes to the first section with it.
  if (first > 0 && !list.some(told => told && told.sec)) for (const st of steps.slice(0, first)) if (st.kind === 'slider') st.sec = 'pre';
  // each step in its section; a section that is the iterations is not written down
  for (const st of steps) { const sec = cuSecOf(st); if (sec === 'main') delete st.sec; else st.sec = sec; }
  return steps.length ? cuSorted(steps) : null;
}
// A whole rule from such text: the steps alone (a list), or the steps with how far a point may go.
function cuRuleOf(o) {
  const steps = cuClean(Array.isArray(o) ? o : o && o.steps);
  return steps ? { steps, next: steps.length + 1, rev: 0, bail: cuBailOf(o && o.bail), play: null, ...cuShowDefault(), rough: !!(o && o.rough) } : null;
}
function cuStored() {
  try { return cuRuleOf(JSON.parse(localStorage.getItem(CU_KEY) || 'null')); }
  catch (err) { return null; }   // storage is blocked, or what it holds is not a rule
}
const cuRuleText = () => JSON.stringify({ bail: S.custom.bail, rough: !!S.custom.rough, steps: S.custom.steps.map(s => ({ kind: s.kind, on: s.on !== false, p: s.p, ...(cuSecOf(s) === 'main' ? {} : { sec: cuSecOf(s) }), ...(s.name ? { name: s.name } : {}) })) });
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
    if (sp.type === 'target') {
      // the point the step works on: z, c, or a point that an earlier step of its section has named
      if (raw !== 'z' && raw !== 'c') {
        if (!CU_NAME.test(raw) || raw in CU_GIVEN || CU_FN[raw]) throw new Error(`“${sp.label}” takes z, c or the name of a point of your own, and “${raw}” is none of those.`);
        const v = ctx && ctx.vars.get(raw);
        if (ctx && !v) throw new Error(`“${raw}” has no value yet. A step can work on a point that an earlier step of its section has named, as in ${raw} = z.`);
        if (v && v.t !== 'v') throw new Error(`“${raw}” is ${CU_KINDS[v.t]}, and this step works on a point.`);
      }
      P[sp.key] = raw; continue;
    }
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
// What a kept value starts as: a number or a point made of numbers, as { t, value, gl }.
function cuStartValue(text) {
  const node = cuParse(String(text), { vars: new Map(), zero: [], uses: new Set(), K: [], internal: false });
  let plain = node.t === 's' || node.t === 'v';
  (function walk(tr) {
    if (tr.leaf === undefined) { if (tr.fn === 'point') plain = false; (tr.a || [tr.of]).forEach(walk); }
    else if (/^[A-Za-z]/.test(tr.leaf) && tr.leaf !== 'pi') plain = false;
  })(node.tree);
  if (!plain) throw new Error('It starts as a number, or a point made of numbers, as in 0 or vec(0, 0, 1). What it becomes after that is for the steps to say.');
  const value = node.js({ z: [0, 0, 0], c: [0, 0, 0], n: 2, K: [], v: [], tt: 1, first: [0, 0, 0], last: [0, 0, 0], mean: [0, 0, 0], count: 0, hist: [], keptIn: [] });
  return { t: node.t, value, gl: node.t === 's' ? cuFlt(value) : `vec3(${value.map(cuFlt).join(', ')})` };
}
// Reads the whole rule. Returns the shader text (glsl) and its short key, the numbers for uCu (K, and Kd: the same
// numbers as they were typed, for the JavaScript side), the steps as JavaScript (run: [{ id, sw, ord, sec, on, idx,
// moves, tween, fns }]: sw the slot of the step's switch or -1, ord its place in the count that runs through all
// three sections, sec its section, on the point the step changes ('z', 'c', the name of a point of the rule's own,
// with idx its place among the names, or null for a step that only names a value), moves whether that point is z,
// tween whether it works out its own in-between), the same steps by section (lists), the kinds of the names (zero),
// scopes[id]: the names of the user's own that a step can read, as [name, kind] pairs, and errs[id]: why a step
// could not be read. Such a step is left out, and so is one that is off and has no slot. at[ord] is the step of run
// at that place, sliders the steps that are numbers with a slider, varsOf the names each section ends with. cPre: a
// step taken once before the iterations changes c; cRun: a step of the iterations, or one taken after them, does.
//
// c is a point like any other, and a step can change it in any section. Before the iterations the picture needs c
// before it knows the point (the shader's cmap, which also looks after the orbits beside a point that land across a
// fold of it), so a step that changes c there can read nothing that is made from z. A change made in an iteration
// lasts: the orbit carries c on to its next iteration (gCuCk in the shader, cIn and cOut in what CARRY.custom keeps).
//
// The shader gets the sections as two functions. cuPre is the section taken once before the iterations: what it
// makes of c (cmap), and where it carries the point an orbit starts from (cuPreZ: zmap for a Julia picture, the
// entry's `start` for a Mandelbrot one). cuRun is one turn of the orbit: the steps of every iteration, or, in the
// one turn that follows the last iteration, the section taken once after them. The places of the steps (ord) run on
// from section to section, so one number says where a play stands in any of them.
function cuBuild(steps) {
  const ctx = { vars: new Map(), all: [], zero: [], uses: new Set(), K: [], kept: [], same: [], sites: 0, internal: false, sec: 'pre' };
  const bodies = { pre: [], main: [], post: [] }, hoist = [], run = [], errs = {}, scopes = {}, varsOf = {};
  let ord = 0, lastC = 0;   // lastC: how many lines the first section has when its last change of c is done
  steps.slice(0, CU_MAX_STEPS).forEach(st => {
    const B = CU_BLOCKS[st.kind], sec = cuSecOf(st);
    // A section begins with the sliders alone, which are plain numbers. Any other name stays in its own section.
    if (sec !== ctx.sec) { varsOf[ctx.sec] = ctx.vars; ctx.sec = sec; ctx.vars = new Map([...ctx.vars].filter(([, v]) => v.slider)); }
    const keep = { vars: new Map(ctx.vars), all: ctx.all.length, zero: ctx.zero.length, kept: ctx.kept.length, same: ctx.same.length };
    scopes[st.id] = [...ctx.vars].filter(([name]) => name[0] !== '@').map(([name, v]) => [name, v.t]);
    let sw = -1;
    if (ctx.K.length < CU_FREE) { sw = ctx.K.length; ctx.K.push(st.on === false ? 0 : 1); }
    else if (st.on === false) return;
    try {
      if (!B) throw new Error('This kind of step is not known.');
      if (st.kind === 'keep') {
        // The name begins this iteration with what the iteration before left in it (gCuK in the shader, keptIn
        // in JavaScript), and cuRun puts what it holds at the end away for the next one.
        const name = String(st.p.name).trim(), first = cuStartValue(st.p.start);
        if (!CU_NAME.test(name)) throw new Error('Name: a name is made of letters and digits and starts with a letter.');
        if (name in CU_GIVEN || CU_FN[name] || name === 'point') throw new Error(`“${name}” already means something here, so it cannot be a name of your own. Pick another.`);
        if (ctx.vars.has(name)) throw new Error(`“${name}” has a value already. A kept value has to be the first step that names it.`);
        const v = { t: first.t, idx: ctx.zero.length, gl: 'u_' + name, sec }, j = ctx.kept.length, at = v.idx, was = first.value, o = ord++;
        ctx.zero.push(first.t); ctx.vars.set(name, v); ctx.all.push(v); ctx.kept.push({ t: first.t, idx: at, gl: v.gl, gl0: first.gl });
        bodies.main.push(`if (${sw < 0 ? '' : `uCu[${sw}] > 0.5 && `}${o}.0 <= cuAt){ ${v.gl} = gCuK${j}[gCarI]; }`);
        run.push({ id: st.id, sw, ord: o, sec, moves: false, tween: false, fns: [E => { const k = E.keptIn[j]; E.v[at] = k === undefined ? was : k; }] });
        return;
      }
      const P = cuSettings(st, B, ctx), names = {};
      const lines = cuLinesOf(B, P, base => names[base] || (names[base] = '@b' + st.id + '_' + base), B.tween ? '@tt' : null).map(l => cuLine(l, ctx, st.kind !== 'formula'));
      // The point the step changes: the one a block is set to work on, or the one its line gives a new value (z or
      // c). A step that only names a value changes none.
      const on = P.on !== undefined ? P.on : lines.some(l => l.z) ? 'z' : lines.some(l => l.c) ? 'c' : null;
      const tv = on && on !== 'z' && on !== 'c' ? ctx.vars.get(on) : null, T = tv ? tv.gl : on;
      if (on === 'c' && sec === 'pre' && lines.some(l => !l.free)) {
        // say which name it is, and for z's length or angle, how c's own is written
        const name = lines.find(l => !l.free).needs, polar = name in CU_POLAR;
        throw new Error(`“${name}” ${name === 'z' ? 'is the point' : polar ? `is the ${name === 'radius' ? 'length' : 'angle'} of the point z` : 'is made from the point z'}, and before the iterations a step that changes c cannot use z: the picture needs c before it knows the point.`
          + (polar ? ` “${name}” is short for z.${name}: for c’s own, write c.${name}${name === 'radius' ? '' : ` (in degrees: deg(c.${name}))`}.` : '') + ' Among the steps of every iteration it can use anything.');
      }
      const o = ord++, inner = lines.map(l => l.gl).join(' ');
      // A step that is switched off is left out, but for the one a play stands in: that one is taken as far as the
      // play has come, so that it can be tried without being part of the rule.
      const when = sw < 0 ? `${o}.0 <= cuAt` : `(uCu[${sw}] > 0.5 ? ${o}.0 <= cuAt : ${o}.0 == cuAt)`;
      // A step that changes a point can be taken part of the way, for a play that stands in the middle of it. A
      // block that knows its own in-between reads how far from tt; any other step is blended from start to end.
      const core = !on ? inner : B.tween ? `float tt = ${o}.0 == cuAt ? cuT : 1.0; ${inner}` : `vec3 zb = ${T}; ${inner} if (${o}.0 == cuAt) ${T} = cuBlend(zb, ${T}, cuT);`;
      // The picture's distance estimate follows a few orbits right beside each point. One that a change of c in an
      // iteration lands across a fold of c keeps its distance from the point's own c, as cmap sees to for a change
      // made before the iterations. The point's own pass runs first and leaves its c of before and after (gCuCb, gCuCa).
      const q = on === 'c' && sec !== 'pre' ? ctx.sites++ : -1;
      bodies[sec].push(q < 0 ? `if (${when}){ ${core} }`
        : `if (${when}){ vec3 cb = c; ${core} if (gCarI == 0){ gCuCb${q} = cb; gCuCa${q} = c; } else { vec3 d0 = cb - gCuCb${q}, d1 = c - gCuCa${q}; if (dot(d1, d1) > 16.0 * dot(d0, d0)) c = gCuCa${q} + d0; } }`);
      if (on === 'c' && sec === 'pre') lastC = bodies.pre.length;
      // a slider is a plain number for every step after it, in whichever section: each turn begins with it
      if (st.kind === 'slider') { ctx.vars.get(P.name).slider = true; hoist.push(sw < 0 ? inner : `if (uCu[${sw}] > 0.5){ ${inner} }`); }
      run.push({ id: st.id, sw, ord: o, sec, on, idx: tv ? tv.idx : -1, moves: on === 'z', tween: !!B.tween, slider: st.kind === 'slider', fns: lines.map(l => l.js) });
    } catch (e) { errs[st.id] = e.message; ctx.vars = keep.vars; ctx.all.length = keep.all; ctx.zero.length = keep.zero; ctx.kept.length = keep.kept; ctx.same.length = keep.same; }
  });
  // the names each section ends with, for whoever works a setting of one of its steps out (cuValueFor)
  varsOf[ctx.sec] = ctx.vars;
  for (const sec of CU_SECS) if (!varsOf[sec]) varsOf[sec] = new Map([...ctx.vars].filter(([, v]) => v.slider));
  const orbit = ctx.uses.has('orbit'), kept = ctx.kept;
  // the names a function of the shader declares: those of its sections, and every slider
  const decl = secs => ctx.all.filter(v => secs.includes(v.sec) || v.slider).map(v => `${CU_GLTYPE[v.t]} ${v.gl} = ${CU_GLZERO[v.t]};`).join(' ');
  const has = (sec, on) => run.some(r => r.sec === sec && (on ? r.on === on : r.on));
  // preZ, preC: the steps taken once before move the point, change c. post: a step taken once after changes a
  // point, so the orbit has a turn for that section. cRun: c is changed in an iteration or after them.
  const preZ = has('pre', 'z'), preC = has('pre', 'c'), post = has('post'), cRun = has('main', 'c') || has('post', 'c');
  const preBody = bodies.pre.slice();
  preBody.splice(lastC, 0, 'if (!forC) c = cEnd;');
  // APR_FAR: the far-away point of the picture's probe stands where it does for the lab's own escape radius of 64
  const code = `
#define APR_FAR 28.8
uniform float uCu[${CU_SLOTS}];
// Both pictures side by side (the slot CU_BOTH), in the picture's own program only: the left half is the Mandelbrot
// picture and the right half the Julia one, each about the middle of its half. Whatever asks uJulia or uOff after
// these lines gets the answer for its own pixel. Samples of a volume (uRaw) are not a picture and are left alone.
#ifdef RAW_FIT
float cuJuliaNow(){ return uCu[${CU_BOTH}] > 0.5 && uRaw < 0.5 ? step(0.5 * uRes.x, gl_FragCoord.x + uOff.x) : uJulia; }
vec2 cuOffNow(){ return uCu[${CU_BOTH}] > 0.5 && uRaw < 0.5 ? uOff + vec2(gl_FragCoord.x + uOff.x < 0.5 * uRes.x ? 0.25 : -0.25, 0.0) * uRes.x : uOff; }
#define uJulia cuJuliaNow()
#define uOff cuOffNow()
#endif
vec3 gCuC, gCuRaw; float gCuPass, gCuCall; ${ctx.same.map((t, k) => `${CU_GLTYPE[t]} gCuW${k};`).join(' ')}${Array.from({ length: ctx.sites }, (x, k) => ` vec3 gCuCb${k}, gCuCa${k};`).join('')}` + cuCarryGlsl(orbit, ctx.uses.has('hist'), kept, cRun) + (preZ || preC ? `
// The steps taken once, before the iterations, from the point z an orbit starts with and the c of the picture.
// forC: what they make of c is asked (cmap), and they are taken whole. Otherwise the answer is where they carry the
// point, as far as a play stands (cuAt and cuT, as in cuRun: their places come before those of every other step).
// cEnd is c as the orbit has it: what these steps make of c, but for an orbit beside a point that fell across a
// fold of c. From the last change of c on, c is that.
vec3 cuPre(vec3 z, vec3 c, vec3 cEnd, bool forC){
  float n = uPow, cuAt = 1e9, cuT = 1.0;
  if (!forC && uCu[${CU_PLAY_ON}] > 0.5){ cuAt = uCu[${CU_PLAY_ORD}]; cuT = uCu[${CU_PLAY_T}]; }
  ${decl(['pre'])}
  ${preBody.join('\n  ')}
  return forC ? c : aprCap(z);
}` : '') + `
vec3 cuPreZ(vec3 z, vec3 c, vec3 cEnd){ return ${preZ ? `uCu[${CU_ONCE}] < 0.5 ? z : cuPre(z, c, cEnd, false)` : 'z'}; }
vec3 cuRun(vec3 z, vec3 c, float n){${kept.length || cRun ? `
  bool cuKeeps = !carOrigin(z);   // a step that starts at the origin leaves what the orbit keeps as it is` : ''}${cRun ? `
  if (gCuCh[gCarI] > 0.5) c = gCuCk[gCarI];   // c as the iterations before have left it` : ''}
  // where a play stands: steps up to cuAt are taken, the one at cuAt as far as cuT, and the rest are left out
  float cuAt = 1e9, cuT = 1.0;${post ? `
  // the turn that follows the last iteration takes the steps of "once, after" in place of the others
  bool cuPost = uCu[${CU_LAST}] > 0.5 && gCuCall == uCu[${CU_LAST}];` : ''}
  if (uCu[${CU_PLAY_ON}] > 0.5){ if (${post ? 'cuPost || ' : ''}gCuPass == uCu[${CU_PLAY_PASS}]){ cuAt = uCu[${CU_PLAY_ORD}]; cuT = uCu[${CU_PLAY_T}]; } else if (gCuPass > uCu[${CU_PLAY_PASS}]) cuAt = -1.0; }
  ${orbit ? 'vec3 oFirst = gCuF[gCarI], oLast = gCuL[gCarI], oMean = gCuS[gCarI] / max(gCuN[gCarI], 1.0); float oCount = gCuN[gCarI];' : ''}
  ${decl(['main', 'post'])}
  ${hoist.join(' ')}${post ? `
  if (cuPost){
  ${bodies.post.join('\n  ')}
  } else {` : ''}
  ${bodies.main.join('\n  ')}${kept.length || cRun ? `
  if (cuKeeps){ ${kept.map((k, j) => `gCuK${j}[gCarI] = ${k.gl};`).join(' ')}${cRun ? ' gCuCk[gCarI] = c; gCuCh[gCarI] = 1.0;' : ''} }` : ''}${post ? `
  }` : ''}
  return aprCap(z);
}
vec3 mul(vec3 a, vec3 b){ return aprMmul(a, b); }
vec3 pw(vec3 a, float n){ return cuRun(a, gCuC, n) - gCuC; }
vec3 sqr(vec3 a){ return cuRun(a, gCuC, 2.0) - gCuC; }
// c as an orbit gets it: what the steps taken once before the iterations make of the c of the picture, which is
// put by (gCuRaw) for the start of a Mandelbrot orbit
vec3 cmap(vec3 c){ gCuRaw = c; return ${preC ? 'cuPre(vec3(0.0), c, c, true)' : 'c'}; }
// where the orbit of a Julia picture starts for a picture point
#define APR_ZMAP 1
vec3 zmap(vec3 P, vec3 c){ return ${preZ ? 'cuPreZ(P, c, cmap(c))' : 'P'}; }`;
  let h = 5381;
  for (let i = 0; i < code.length; i++) h = ((h << 5) + h + code.charCodeAt(i)) | 0;
  const K = new Float32Array(CU_SLOTS);
  K.set(ctx.K);
  const at = [], lists = { pre: [], main: [], post: [] };
  for (const r of run) { at[r.ord] = r; lists[r.sec].push(r); }
  return { Kd: ctx.K.slice(), cPre: preC, cRun, vars: varsOf.main, varsOf, glsl: GL_APR + GL_MERC_PLAIN + GL_CARRY + CU_GLSL + code, key: (h >>> 0).toString(36) + '.' + code.length,
    K, run, at, lists, sliders: run.filter(r => r.slider), zero: ctx.zero, errs, scopes, orbit, kept };
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
// The twin of cuBlend in the shader.
function cuBlend(a, b, t) {
  const la = len(a), lb = len(b), across = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  if (Math.abs(la - lb) > 1e-3 * Math.max(la, lb) || la < 1e-20) return across;
  const co = clamp(dot(a, b) / (la * lb), -1, 1), w = Math.acos(co), sw = Math.sin(w);
  let p;
  if (sw > 1e-3) p = add(scl(a, Math.sin((1 - t) * w) / sw), scl(b, Math.sin(t * w) / sw));
  else if (co > 0) p = across;
  else {
    let k = sub([0, 0, 1], scl(a, a[2] / (la * la)));
    if (dot(k, k) < 1e-12) k = sub([1, 0, 0], scl(a, a[0] / (la * la)));
    p = add(scl(a, Math.cos(PI * t)), scl(cross(norm(k), a), Math.sin(PI * t)));
  }
  return scl(p, (la + (lb - la) * t) / Math.max(len(p), 1e-30));
}
// One pass through the steps of a section in JavaScript: the twin of cuRun in the shader, and for the section taken
// once before the iterations the twin of cuPreZ. sec: the section ('main' where it is left out). st: what the orbit
// carries (CARRY.custom), or nothing for a point with no orbit behind it. part: { ord, t } stops the pass where a
// play stands, as cuAt and cuT do in the shader; left out, the pass is whole.
function cuEnv(P, z, c, n, st, sec) {   // what a pass begins with: the point, every name at its start, and the sliders
  // c: as the iterations before have left it (cIn), where a step of theirs has changed it
  const k = st ? st.n : 0, E = { z: [z[0], z[1], z[2]], c: (st && st.cIn) || c || [0, 0, 0], n, K: P.Kd, tt: 1, sec: sec || 'main', v: P.zero.map(t => CU_ZERO[t]()),
    first: st ? st.first : [0, 0, 0], last: st ? st.last : [0, 0, 0], mean: k > 0 ? scl(st.sum, 1 / k) : [0, 0, 0], count: k, hist: (st && st.hist) || [], keptIn: (st && st.keptIn) || [] };
  for (const s of P.sliders) if (s.sw < 0 || P.K[s.sw] > 0.5) for (const f of s.fns) f(E);
  return E;
}
function cuRun(z, c, n, st, part, sec) {
  const P = cuProgram(), E = cuEnv(P, z, c, n, st, sec);
  for (const s of P.lists[E.sec]) {
    if (part && s.ord > part.ord) break;
    const here = !!part && s.ord === part.ord;
    if (s.sw >= 0 && !(P.K[s.sw] > 0.5) && !here) continue;   // switched off, and no play stands in it
    const zb = here && s.on && !s.tween ? cuOnOf(E, s) : null;
    E.tt = here ? part.t : 1;
    for (const f of s.fns) f(E);
    if (zb) cuOnSet(E, s, cuBlend(zb, cuOnOf(E, s), part.t));
  }
  // what the rule keeps for the next iteration goes into the orbit's state, which CARRY.custom.step hands on, and
  // so does c where a step of the iterations changes it
  if (st && E.sec === 'main' && !carOrigin(z)) {
    if (P.kept.length) st.keptOut = P.kept.map(k => { const x = E.v[k.idx]; return Array.isArray(x) ? x.slice() : x; });
    if (P.cRun) st.cOut = E.c.slice();
  }
  return cuCapped(E.z);
}
// The point a step changes, among the names E: z, c, or a point of the rule's own. cuOnSet gives it a new value.
const cuOnOf = (E, s) => (s.on === 'c' ? E.c : s.on && s.on !== 'z' ? E.v[s.idx] : E.z);
function cuOnSet(E, s, x) { if (s.on === 'c') E.c = x; else if (s.on && s.on !== 'z') E.v[s.idx] = x; else E.z = x; }
// The point and the names as they are when the step at the place `ord` of a section is about to begin, for a point
// with this orbit behind it; and the value one setting has there (null where its formula cannot be read or is of
// another kind).
function cuEnvAt(z, c, n, st, ord, sec) {
  const P = cuProgram(), E = cuEnv(P, z, c, n, st, sec);
  for (const s of P.lists[E.sec]) {
    if (s.ord >= ord) break;
    if (s.sw < 0 || P.K[s.sw] > 0.5) for (const f of s.fns) f(E);
  }
  return E;
}
// The same, carried on from the names E0 that the step at `from` begins with (from <= ord), and one step alone: where
// a point that stands at the start of the step at `ord` with the names E0 is when t of that step is taken. The two
// together are cuRun with `part`, without the steps before being worked out again for every t.
function cuEnvOn(E0, from, ord) {
  const P = cuProgram(), E = { ...E0, v: E0.v.slice(), tt: 1 };
  for (const s of P.lists[E.sec]) {
    if (s.ord < from) continue;
    if (s.ord >= ord) break;
    if (s.sw < 0 || P.K[s.sw] > 0.5) for (const f of s.fns) f(E);
  }
  return E;
}
// what: left out, where the point z is then; 'on', where the point is that the step changes; 'c', what c is then.
// The step is taken whether it is switched on or not: a play may stand in one that is off.
function cuStepOn(E0, ord, t, what) {
  const P = cuProgram(), s = P.at[ord], of = E => (!s || !what ? E.z : what === 'c' ? E.c : cuOnOf(E, s));
  if (!s) return cuCapped(of(E0));
  const E = { ...E0, v: E0.v.slice(), tt: t };
  for (const f of s.fns) f(E);
  if (s.on && !s.tween) cuOnSet(E, s, cuBlend(cuOnOf(E0, s), cuOnOf(E, s), t));
  return cuCapped(of(E));
}
function cuValueFor(text, kind, E) {
  try {
    const P = cuProgram(), node = cuParse(String(text), { vars: P.varsOf[E.sec] || P.vars, zero: [], uses: new Set(), K: [], internal: false });
    return node.t === kind ? node.js(E) : null;
  } catch (err) { return null; }
}
// c as the orbit gets it: what the steps taken once before the iterations make of the c of the picture, at the
// power of the page. They are taken for a point at the middle: a step that changes c there reads nothing of z.
function cuCmap(c) {
  const P = cuProgram();
  if (!P.cPre) return c;
  const E = cuEnv(P, [0, 0, 0], c, S.n, null, 'pre');
  for (const s of P.lists.pre) if (s.sw < 0 || P.K[s.sw] > 0.5) for (const f of s.fns) f(E);
  return E.c;
}
// Where the steps taken once, before the iterations, carry a point that starts at z, with the c of the picture.
function cuPreZ(z, c) {
  const P = cuProgram();
  return P.lists.pre.some(s => s.moves) ? cuRun(z, c, S.n, null, undefined, 'pre') : z;
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
  // a step that works on another point than z says so
  const what = s => (s.p.on && s.p.on !== 'z' ? `on ${s.p.on}: ` : '') + CU_BLOCKS[s.kind].words(s.p);
  const say = (sec, head) => { const part = on.filter(s => cuSecOf(s) === sec); return part.length ? head + part.map(s => `(${on.indexOf(s) + 1}) ${what(s)}`).join('; ') + '. ' : ''; };
  return (say('pre', 'Once, before the iterations: ') + say('main', 'In every iteration: ') + say('post', 'Once, after the last iteration: ')).trim();
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
  return cuLinesOf(B, cuSettings(st, B, null), base => names[base] || (names[base] = fresh(base))).map(text => ({ kind: 'formula', p: { text } }));
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
      kind = tr.op ? 'o_' + tr.op : tr.fn === 'rot' && args.length === 2 ? 'f_turn' : 'f_' + tr.fn;
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
    if (s.kind === 'slider' || s.kind === 'keep') out.push(String(s.p.name));
    else if (s.kind === 'formula') { const m = /^\s*([A-Za-z][A-Za-z0-9]*)\s*=(?!=)/.exec(String(s.p.text)); if (m) out.push(m[1]); }
    else if (s.p.out !== undefined) out.push(String(s.p.out));
  }
  return out;
}

// Playing the steps. The picture is every starting point that has not been thrown out yet, and a play stops the
// orbits part of the way: S.custom.play = { pass, u } means that the passes before `pass` are done and, of the steps
// of that pass that move the point, u have been taken (u need not be whole). null: every pass, the finished solid.
// A pass is one run through the steps of every iteration. In a Mandelbrot picture that starts z at 0 the first
// iteration finds every point at the middle and puts it on its own c. The shader does not count it (carOrigin),
// so it is the pass 0 (cuLead, cuFirst), and the passes that count are one fewer than the iterations. No step of
// it moves a point that the dots could show: a dot is drawn on its own c from the start, so a play has no place
// to stand in among the steps of the pass 0.
// The steps taken once stand at the two ends: before the first pass u runs below 0, one for each step of "once,
// before" that a play can stand in (cuLow), and after the last pass it runs on above the steps of the pass, one for
// each such step of "once, after" (cuHigh).
// A step that is switched off can be tried: S.custom.play.peek is its id. For as long as it is tried it counts among
// the steps a play can stand in, and it is taken only while the play stands in it (see `when` in cuBuild).
const cuBoth = () => !!S.custom.both && !S.learn && S.mode !== 'k';   // both pictures side by side
// Do the steps taken once before leave the middle where it is? Asked for one c that is no special case. Then the
// first iteration of a Mandelbrot picture finds every point there.
function cuPreRests() {
  const P = cuProgram();
  if (!P.rests || P.rests.n !== S.n) P.rests = { n: S.n, yes: carOrigin(cuPreZ([0, 0, 0], [0.31, -0.42, 0.53])) };
  return P.rests.yes;
}
const cuLead = () => ((S.mode === 'm' || cuBoth()) && S.z0.trim() === '0' && cuPreRests() ? 1 : 0);
const cuFirst = () => 1 - cuLead();
const cuPasses = () => Math.max(1, Math.round(S.iter) - cuLead());
// the steps of a section that a play can stand in: those that change a point, which is z, c or a point of the rule's own
function cuPeek(P = cuProgram()) {
  const id = S.custom && S.custom.play ? S.custom.play.peek : undefined;
  return id !== undefined && P.run.some(s => s.id === id && s.on && s.sw >= 0 && !(P.K[s.sw] > 0.5)) ? id : null;
}
const cuPlayable = (sec, P = cuProgram()) => { const peek = cuPeek(P); return P.lists[sec].filter(s => s.on && (s.sw < 0 || P.K[s.sw] > 0.5 || s.id === peek)); };
const cuMoving = (P = cuProgram()) => cuPlayable('main', P);
const cuCstep = (P = cuProgram()) => cuPlayable('pre', P).find(s => s.on === 'c') || null;   // the first step that changes c before the iterations
const cuLow = pass => (pass === cuFirst() ? -cuPlayable('pre').length : 0);                          // where u begins in this pass
const cuHigh = pass => (pass < 1 ? 0 : cuMoving().length + (pass === cuPasses() ? cuPlayable('post').length : 0));   // and where it ends
// where the play stands, with nothing out of range: { pass, u, end } (end: the finished solid)
function cuPlayAt() {
  const np = cuPasses(), m = cuMoving().length, pl = S.custom.play;
  if (!pl || !m) return { pass: np, u: cuHigh(np), end: true };
  const pass = clamp(Math.round(pl.pass), cuFirst(), np), u = clamp(+pl.u || 0, cuLow(pass), cuHigh(pass));
  // a step that is tried keeps the play, also where it is the last of the last iteration
  return { pass, u, end: pass >= np && u >= cuHigh(np) && cuPeek() === null };
}
// Where the play stands, as the section and the step of it: { sec, pass, list, x } with list the steps of that
// section a play can stand in and x how many of them are taken (0 to list.length; it need not be whole).
function cuPlaySec(at = cuPlayAt()) {
  const m = cuMoving().length, lo = cuLow(at.pass);
  if (lo < 0 && at.u <= 0) { const list = cuPlayable('pre'); return { sec: 'pre', pass: at.pass, list, x: at.u + list.length }; }
  if (at.u > m) return { sec: 'post', pass: at.pass, list: cuPlayable('post'), x: at.u - m };
  return { sec: 'main', pass: at.pass, list: cuMoving(), x: at.u };
}
// what the shader needs for it: null for the finished solid. last: the number of the turn that takes the steps of
// "once, after", or 0 while the play has not come to them.
function cuPlayNow() {
  if (S.learn || !S.custom.play) return null;
  const at = cuPlayAt(), mov = cuMoving(), lead = cuLead(), np = cuPasses();
  if (at.end) return null;
  const w = cuPlaySec(at), j = clamp(Math.floor(w.x), 0, w.list.length - 1), s = w.list[j];
  // Among the steps taken once before, the picture is the points as those steps have moved them so far: no step
  // of an iteration is taken yet, since every one of them has a later place. A Mandelbrot picture cannot lose a
  // point there, nor in the iteration that carries each point from the middle to its own c: it shows the big ball.
  if (w.sec === 'pre') return { pass: 1, ord: s.ord, t: w.x - j, iter: Math.max(2, 1 + lead), last: 0 };
  if (at.pass < 1) return { pass: 1, ord: mov[0].ord, t: 0, iter: Math.max(2, 1 + lead), last: 0 };
  // the steps taken once after have a turn of their own, which follows the last iteration
  if (w.sec === 'post') return { pass: np, ord: s.ord, t: w.x - j, iter: np + lead + 1, last: np + lead + 1 };
  // The picture takes at least two iterations. A pass after the one on show leaves every point where it is (cuAt
  // in the shader), so the second changes nothing.
  return { pass: at.pass, ord: s.ord, t: w.x - j, iter: Math.max(2, at.pass + lead), last: 0 };
}
// What the picture is drawn for in a play. A point is thrown out when a pass is done, not in the middle of it: until
// the last step of the pass on show has been taken whole, the picture is the solid as that pass found it. The dots
// and the guides follow every moment of a step (cuShown in 82-custom-ui.js), and a dot goes by the same rule.
function cuPlayPic() {
  const at = cuPlayNow();
  if (!at) return null;
  const w = cuPlaySec(), list = w.list;
  if (!list.length) return at;
  return w.x >= list.length - 1e-9 ? { ...at, ord: list[list.length - 1].ord, t: 1 } : { ...at, ord: list[0].ord, t: 0 };
}
// Has the rule a turn after the last iteration: a step of "once, after" that moves the point and is on. The Learn
// tab leaves the steps taken once out, but for the step that changes c.
const cuHasPost = () => !S.learn && cuPlayable('post').length > 0;
// The custom approach's own part of the scene's uniforms (see `uniforms` and `scene` in its entry).
function cuUniforms(gl, loc) {
  const K = cuProgram().K, at = cuPlayPic();
  K[CU_PLAY_ON] = at ? 1 : 0; K[CU_PLAY_PASS] = at ? at.pass : 0; K[CU_PLAY_ORD] = at ? at.ord : 0; K[CU_PLAY_T] = at ? at.t : 1;
  K[CU_BOTH] = cuBoth() ? 1 : 0;
  K[CU_ONCE] = S.learn ? 0 : 1;
  K[CU_LAST] = at ? at.last : cuHasPost() ? Math.round(S.iter) + 1 : 0;
  gl.uniform1fv(loc('uCu[0]'), K);
}
// The plain distance estimate (one number in place of neighbouring orbits) for the finished solid, where the rule
// asks for it. It holds only for whole steps of a power, so a play takes the fine one, and so does a rule with a
// step taken once that moves the point.
const cuRough = () => !!(S.custom && S.custom.rough) && !cuPlayNow() && !cuHasPost() && !cuPlayable('pre').some(s => s.moves);
function cuScene() {
  const at = cuPlayPic();
  return { bail: cuBailOf(S.custom.bail), iter: at ? at.iter : cuHasPost() ? Math.round(S.iter) + 1 : 0 };
}
// The ball the dots of a play start in: no further from the middle than a point may go. The start view of the
// camera holds it (the entry's `ball`), in each half when both pictures are side by side (`halves`).
const cuReach = () => Math.min(cuBailOf(S.custom.bail), clamp(+S.custom.reach || 2, 0.25, 16));
