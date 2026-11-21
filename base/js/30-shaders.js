// ---------- shaders
const VERT = `#version 300 es
void main(){
  vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));
  gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}`;
const GL_HEAD = `#version 300 es
precision highp float;
precision highp int;
uniform vec2 uRes, uOff;
uniform vec3 uCamPos; uniform mat3 uCam; uniform float uFov;
uniform float uPow, uJulia, uBail, uCut, uPx, uDetail, uStepK, uNormEps, uAO, uShadow, uAnalytic, uPick;
uniform vec4 uA;
uniform vec3 uC, uAbs, uSgn, uBg, uCutCol, uCutInk, uLight;
uniform int uIter, uSteps, uNT, uShSteps;
uniform vec3 uKMu, uKInvC; uniform float uKL, uK3, uKInvR;
out vec4 o;
const float PI = 3.14159265358979, BOUND = 8.0;
float gEsc, gIt, gId; vec3 gLast, gGrad; mat3 gB;
vec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }
float at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }
`;
// Distance estimate for an iterated equation. Up to three neighbouring orbits are carried along with
// the point and renormalised every step; how fast they separate is the derivative, for any formula.
const GL_ORBIT = `
vec3 smul(float s, vec3 v){ return s >= 0.0 ? s * v : mul(vec3(s, 0.0, 0.0), v); }
vec3 f(vec3 z, vec3 c){ z = mix(z, abs(z), uAbs) * uSgn; return __F__; }
vec3 start(vec3 c){ return __Z0__; }
float de(vec3 p, int nt){
  vec3 dv[3]; vec3 dc[3]; float ls[3];
  bool jul = uJulia > 0.5;
  float h0 = 1e-3 * (length(p) + 0.05);
  vec3 c = cmap(jul ? uC : p);
  vec3 v = jul ? p : start(c);
  for (int i = 0; i < nt; i++){
    vec3 e = gB[i] * h0;
    if (jul) { dv[i] = e; dc[i] = vec3(0.0); }
    else {
      dc[i] = cmap(p + e) - c;
      if (length(dc[i]) > 4.0 * h0) dc[i] = e;   // the neighbour fell across a fold: keep its size
      dv[i] = start(c + dc[i]) - v;
    }
    ls[i] = -log(h0);
  }
  float pn = max(1.0, abs(uPow));
  float r = length(v), rp = r, it = 0.0;
  trapStart();
  for (int k = 0; k < uIter; k++){
    if (r > uBail) break;
    vec3 w = f(v, c);
    for (int i = 0; i < nt; i++){
      vec3 d = f(v + dv[i], c + dc[i]) - w;
      float m = length(d), was = length(dv[i]) + length(dc[i]), lw = length(w);
      if (m > 8.0 * pn * was * (lw + 1.0) / (r + 0.01)){
        // the neighbour landed on the other side of a seam; assume an ordinary stretch instead
        d = dv[i] * (pn * (lw + 1e-3) / (r + 1e-3)); m = length(d);
      }
      if (m > 0.0){
        float s = clamp(2e-3 * (length(w) + 1e-3) / m, 1e-8, 1e8);
        dv[i] = d * s; dc[i] *= s; ls[i] -= log(s);
      } else dv[i] = vec3(0.0);
    }
    v = w; rp = r; r = length(v); it += 1.0;
    trapAdd(v, it);
  }
  gEsc = r > uBail ? 1.0 : 0.0; gLast = v; gIt = it;
  if (gEsc > 0.5){
    float P = clamp(log(r) / log(max(rp, 1.0001)), 1.5, 32.0);
    gIt = it - log(log(r) / log(uBail)) / log(P);
  }
  if (r <= 1.0) return 0.0;
  vec3 vh = v / r, g = vec3(0.0);
  float lm = ls[0], t2 = 0.0;
  for (int i = 1; i < nt; i++) lm = max(lm, ls[i]);
  for (int i = 0; i < nt; i++){
    float sc = exp(ls[i] - lm);
    g += gB[i] * (dot(dv[i], vh) * sc);
    t2 = max(t2, dot(dv[i], dv[i]) * sc * sc);
  }
  gGrad = g;
  float den = nt == 3 ? length(g) : sqrt(t2);
  float d = 0.5 * r * log(r) * exp(-lm) / max(den, 1e-30);
  return gEsc > 0.5 ? d : min(d, 1e-4);
}`;
// Distance estimate for a Kleinian group with a quaternion parameter, after Jos Leys's method for
// the Maskit groups: carry the point back into one cell with the generators, tracking the scale.
const GL_KLEIN = `
float wrapf(float x, float a, float s){ x -= s; return (x - a * floor(x / a)) + s; }
float kde(vec3 z){
  vec3 mu = uKMu, lz = z + vec3(1.0), llz = z - vec3(1.0);
  float a = mu.y, DF = 1.0, it = 0.0, fs = sign(-mu.x);
  float sx = mu.x / a, sz = mu.z / a;
  trapStart();
  float best = min(z.y, a - z.y);   // distance to the two walls, before any map is applied
  for (int i = 0; i < uIter; i++){
    z.x -= sx * z.y; z.x = wrapf(z.x, 2.0, -1.0); z.x += sx * z.y;
    if (uK3 > 0.5) { z.z -= sz * z.y; z.z = wrapf(z.z, 2.0 * uKL, -uKL); z.z += sz * z.y; }
    float xs = z.x - 0.5 * mu.x;
    if (z.y >= a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * sign(xs) * (1.0 - exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))) z = mu - z;
    float iR = 1.0 / max(dot(z, z), 1e-20);
    z = mu + vec3(z.x, -z.y, -z.z) * iR;   // q -> mu + 1/q
    DF *= iR; it += 1.0;
    best = min(best, min(z.y, a - z.y) / max(DF, 1.0));
    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5) break;
    llz = lz; lz = z;
  }
  gIt = it; gLast = z;
  return min(best, 0.3);
}
float de(vec3 p, int nt){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0);
  float r2 = max(dot(p, p), 1e-12), r = sqrt(r2), R2 = uKInvR * uKInvR;
  vec3 q = uKInvC + (R2 / r2) * p;
  if (q.y < 0.0 || q.y > uKMu.y) { gEsc = 0.0; trapStart(); trapAdd(q, 0.0); gIt = 0.0; gLast = q; return 0.0; }
  float d = kde(q);
  return r2 * d / (R2 + r * d);
}`;
const GL_TAIL = `
float map(vec3 p, int nt, float e){
  float d = de(p, nt), pl = p.z - uCut;
  if (gEsc < 0.5 && pl > -e) d = min(d, 0.0);   // on or above the cut, a point that never escaped is solid
  gId = pl > d ? 1.0 : 0.0;
  return max(d, pl);
}
void main(){
  vec2 uv = (2.0 * (gl_FragCoord.xy + uOff) - uRes) / uRes.y;
  vec3 rd = normalize(uCam * vec3(uv * uFov, 1.0)), ro = uCamPos, col = uBg, p = ro;
  gB = mat3(1.0);
  if (uNT == 1) gB[0] = rd;
  float b = dot(ro, rd), cc = dot(ro, ro) - BOUND * BOUND, h = b * b - cc, t = 0.0, e = 1e-6;
  bool hit = false;
  if (h > 0.0){
    h = sqrt(h);
    t = max(-b - h, 0.0);
    float tMax = -b + h, pix = 2.0 * uFov / uRes.y;
    for (int i = 0; i < uSteps; i++){
      p = ro + rd * t; e = max(uDetail * pix * t, 1e-7);
      float d = map(p, uNT, e);
      if (d < e) break;
      t += d * uStepK;
      if (t > tMax) break;
    }
    hit = t <= tMax;
  }
  if (uPick > 0.5){ o = hit ? vec4(ro + rd * t, 1.0) : vec4(0.0); return; }
  if (hit){
    p = ro + rd * t;
    vec3 grad = gGrad;
    colourCapture();
    if (gId > 0.5){
      // the cut face, hatched the way a section drawing marks cut material
      float s = abs(fract((gl_FragCoord.x + gl_FragCoord.y) / (8.0 * uPx)) - 0.5);
      col = mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s));
    } else {
      vec3 nor = grad;
      if (uAnalytic < 0.5 || uNT != 3){
        float hh = uNormEps * e; nor = vec3(0.0);
        for (int i = 0; i < 4; i++){
          vec3 k = vec3(i == 0 || i == 3 ? 1.0 : -1.0, i == 2 || i == 3 ? 1.0 : -1.0, i == 1 || i == 3 ? 1.0 : -1.0);
          nor += k * de(p + k * hh, uNT);
        }
      }
      nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
      if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
      vec3 alb = surfaceColour(p, nor, t);
      vec3 L = uLight;
      float dif = clamp(dot(nor, L), 0.0, 1.0), sh = 1.0, occ = 1.0;
      if (uShadow > 0.5 && dif > 0.001){
        float res = 1.0, ts = 4.0 * e;
        gB[0] = L;
        for (int i = 0; i < uShSteps; i++){
          float d = map(p + nor * 2.0 * e + L * ts, 1, e);
          res = min(res, 10.0 * d / ts);
          if (res < 0.005 || ts > 5.0) break;
          ts += clamp(d, 2.0 * e, 0.35);
        }
        sh = clamp(res, 0.0, 1.0); sh = sh * sh * (3.0 - 2.0 * sh);
      }
      if (uAO > 0.5){
        float a = 0.0, w = 1.0;
        gB[0] = nor;
        for (int i = 1; i <= 4; i++){
          float hh = 0.006 * t * float(i * i);
          a += w * clamp(1.0 - 1.6 * map(p + nor * hh, 1, e) / hh, 0.0, 1.0);
          w *= 0.7;
        }
        occ = clamp(1.0 - 0.45 * a, 0.0, 1.0);
      }
      float sky = 0.5 + 0.5 * nor.z;
      float bac = clamp(0.3 + 0.7 * dot(nor, normalize(vec3(-L.x, -L.y, 0.3))), 0.0, 1.0);
      float fre = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 3.0);
      float spe = pow(clamp(dot(nor, normalize(L - rd)), 0.0, 1.0), 40.0) * dif * sh;
      vec3 lig = 1.45 * dif * sh * vec3(1.00, 0.94, 0.84) + occ * (0.42 * sky * vec3(0.50, 0.62, 0.80) + 0.20 * bac * vec3(0.80, 0.70, 0.58));
      col = alb * lig + 0.16 * spe + 0.06 * fre * occ * alb;
      if (colourUnlit() > 0.5) col = alb;
    }
  }
  o = vec4(col, 1.0);
}`;
const BLIT = `#version 300 es
precision highp float;
uniform sampler2D uAcc, uPrev; uniform vec2 uSize, uPrevScale, uPrevMax; uniform float uUseAcc;
out vec4 o;
float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main(){
  vec2 uv = gl_FragCoord.xy / uSize;
  vec4 a = texture(uAcc, uv);
  vec3 c = uUseAcc > 0.5 && a.a > 0.5 ? a.rgb / a.a : texture(uPrev, min(uv * uPrevScale, uPrevMax)).rgb;
  c = c / (1.0 + 0.12 * c) * 1.12;
  c = pow(clamp(c, 0.0, 1.0), vec3(0.4545)) + (hash(gl_FragCoord.xy) - 0.5) / 255.0;
  o = vec4(c, 1.0);
}`;
