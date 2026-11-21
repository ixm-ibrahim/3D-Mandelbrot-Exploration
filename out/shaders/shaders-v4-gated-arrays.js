// ---------- shaders
// The scene program is GL_HEAD + GL_COLOUR + (approach.glsl + GL_ORBIT | GL_KLEIN) + GL_TAIL.
//
// Two things shape this file.
// 1. Compile time. The D3D compiler behind WebGL on Windows copies a function into every place that calls it,
//    and its time also grows with every value a loop has to carry from one turn to the next. So the formula is
//    written into the shader once (f(), start() and cmap() have one call site each, inside orbitDE(), which
//    has one call site in de(), which has one call site in main()), main() is a state machine around that
//    single call, and whatever can be recomputed each turn is recomputed instead of carried.
// 2. The solid is always the bounded piece. Normally that is the set of points whose orbit never leaves the
//    escape radius. When points far away never leave it either (negative powers do this: a huge z comes
//    straight back to c), that set fills all of space outside a small region, so the picture swaps the roles
//    and draws the region whose orbits do leave. gEsc therefore means "this point is outside the solid".
const VERT = `#version 300 es
void main(){
  vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));
  gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}`;
const GL_HEAD = `#version 300 es
precision highp float;
precision highp int;
uniform vec2 uRes, uOff, uFlatC;
uniform vec3 uCamPos; uniform mat3 uCam; uniform float uFov;
uniform float uPow, uJulia, uBail, uCut, uPx, uDetail, uStepK, uNormEps, uAO, uShadow, uAnalytic, uPick;
uniform float uBound, uMosaic, uFlat, uFlatH, uSliceZ;
uniform vec4 uA;
uniform vec3 uC, uAbs, uSgn, uBg, uCutCol, uCutInk, uLight;
uniform int uIter, uSteps, uNT, uShSteps;
uniform vec3 uKMu, uKInvC; uniform float uKL, uK3, uKInvR;
out vec4 o;
const float PI = 3.14159265358979;
// Results of the latest distance query. gEsc: 1 when the point is outside the solid. gIt: smooth step count.
// gLast: last orbit point. gGrad: outward slope (set only with three neighbouring orbits).
// gId: 1 when the cut plane, not the set, is the nearer surface.
float gEsc, gIt, gId; vec3 gLast, gGrad;
// What a query asks. ASK_PROBE: the far-away point that decides gInsideOut and gPowerLaw. ASK_CELL: is the
// centre gCell of a mosaic cell in the solid. ASK_JULIA: the Julia set drawn inside the cell centred on gCell.
const int ASK_PLAIN = 0, ASK_PROBE = 1, ASK_CELL = 2, ASK_JULIA = 3;
int gAsk; vec3 gCell;
// What the probe found. gInsideOut: far points never escape, so the solid is the region that does.
// gPowerLaw: every step is |z|^n plus c, so the single-number distance estimate can be trusted.
bool gInsideOut, gPowerLaw;
vec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }
float at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }
`;
// Distance estimate for an iterated equation. Up to three neighbouring orbits are carried along with
// the point and renormalised every step; how fast they separate is the derivative, for any formula.
// With no neighbours (the fastest setting) one running number stands in for it: the stretch n|z|^(n-1) of
// a pure power, which is the estimate Mandelbulb renderers use.
const GL_ORBIT = `
const bool ORBIT_SCENE = true;
const float MOSAIC_FIT = 0.225;   // cell widths per unit of a mosaic Julia set: a set of radius 2 spans 90% of its cell
const float MOSAIC_BALL = 2.1;    // each mosaic set is clipped to a ball of this radius, just short of the cell walls
vec3 smul(float s, vec3 v){ return s >= 0.0 ? s * v : mul(vec3(s, 0.0, 0.0), v); }
vec3 f(vec3 z, vec3 c){ z = mix(z, abs(z), uAbs) * uSgn; return __F__; }
vec3 start(vec3 c){ return __Z0__; }
// One orbit and the distance it implies. p: the point asked about. jul: iterate from p with the constant cj
// (otherwise p is the constant and the orbit begins at the start value). nt: neighbouring orbits, 0, 1 or 3
// (three lie along the axes, one along dir). its: steps at most. swap: the solid is the set of points that DO
// escape (see the top of the file).
// An orbit has escaped once a step lands outside the radius uBail. A step that lands on a pole, or anywhere
// a float cannot hold, counts as escaped; a pole at the very start is passed through instead (0 goes to
// infinity, infinity goes to f(infinity)), so that z^-2 + c started from 0 follows the orbit of c.
float orbitDE(vec3 p, vec3 cj, bool jul, int nt, vec3 dir, int its, bool swap){
  // Neighbour i sits at z + dv[i] * exp(-ls[i]) with the constant c + dc[i] * exp(-ls[i]).
  // With no neighbours, slot 0 holds the running stretch instead: dv[0].x * exp(ls[0]), fed by dc[0].x.
  vec3 dv[3]; vec3 dc[3]; float ls[3];
  float h0 = 1e-3 * (length(p) + 0.05), pn = max(1.0, abs(uPow));
  vec3 c = vec3(0.0), v = vec3(0.0);
  for (int i = 0; i <= nt; i++){   // i = 0 is the point itself, the others its neighbours
    vec3 e = vec3(0.0), d = vec3(0.0);
    if (i > 0) e = h0 * (nt == 3 ? vec3(i == 1, i == 2, i == 3) : dir);
    vec3 s = p + e;
    if (!jul || i == 0){
      vec3 ci = cmap(jul ? cj : p + e);
      if (i == 0) c = ci;
      else { d = ci - c; if (length(d) > 4.0 * h0) d = e; }   // the neighbour fell across a fold: keep its size
      if (!jul) s = start(c + d);
    }
    if (i == 0) v = s;
    else { dv[i - 1] = s - v; dc[i - 1] = d; ls[i - 1] = -log(h0); }
  }
  if (nt == 0){ dv[0] = vec3(jul ? 1.0 : 0.0, 0.0, 0.0); dc[0] = vec3(jul ? 0.0 : 1.0, 0.0, 0.0); ls[0] = 0.0; }
  float r = length(v), rp = r, it = 0.0, steps = float(its), best = 1e30, bestIt = 0.0, d = 0.0, P = 2.0;
  bool esc = false;
  trapStart();
  for (int k = 0; k <= its; k++){
    esc = r > uBail;
    bool last = esc || k == its;
    if (last || swap){
      // how fast |z| changes as p moves: gradient g and size den, both without the common factor exp(lm)
      vec3 vh = v / max(r, 1e-30), g = vec3(0.0);
      float lm = ls[0], den = dv[0].x;
      if (nt == 3){
        lm = max(ls[0], max(ls[1], ls[2]));
        g = vec3(dot(dv[0], vh) * exp(ls[0] - lm), dot(dv[1], vh) * exp(ls[1] - lm), dot(dv[2], vh) * exp(ls[2] - lm));
        den = length(g);
      } else if (nt == 1) den = length(dv[0]);
      float perSlope = 0.5 * exp(-lm) / max(den, 1e-30);
      P = clamp(log(r) / log(max(rp, 1.0001)), 1.5, 32.0);   // the power the last step raised |z| to
      if (swap){
        // how far p would have to move for this step to land on the escape radius: the nearest such
        // step is the surface, and past it the same measure, negated, is the depth inside
        float edge = r * log(uBail / r) * perSlope;
        if (esc) d = edge;
        else if (r > 0.0 && edge < best){ best = edge; bestIt = it; }
      } else {
        // The surface is where the last allowed step lands exactly on the escape radius, so the estimate
        // is zero there and negative inside. An orbit that left earlier is measured against the same
        // surface through the potential log|z| / P^steps.
        gGrad = g;
        d = r * (log(r) - log(uBail) * pow(P, it - steps)) * perSlope;
      }
    }
    if (last) break;
    vec3 w = vec3(0.0); float lw = 0.0; bool pole = false;
    for (int i = 0; i <= nt; i++){
      vec3 dz = vec3(0.0), dk = vec3(0.0);
      if (i > 0){ dz = dv[i - 1]; dk = dc[i - 1]; }
      vec3 wi = f(v + dz, c + dk);
      if (i == 0){
        float w2 = dot(wi, wi);
        bool wild = !(w2 < 1e36);   // not a number, infinite, or too large to work with
        if (k == 0){
          float big = 1e3 * (uBail + length(c));
          if (r < 1e-3 && (wild || w2 > big * big)){ pole = true; break; }
        }
        if (wild){ wi = vec3(1e18, 0.0, 0.0); w2 = 1e36; }
        w = wi; lw = sqrt(w2);
      } else {
        vec3 dw = wi - w;
        float m = length(dw), was = length(dz) + length(dk);
        if (!(m <= 8.0 * pn * was * (lw + 1.0) / (r + 0.01))){
          // the neighbour landed across a seam (or on a pole): give it the stretch of a pure power instead
          dw = dz * max(pn * length(w - c) / max(r, 1e-6), 1e-3); m = length(dw);
        }
        if (m > 0.0){
          float s = clamp(2e-3 * (lw + 1e-3) / m, 1e-8, 1e8);
          dv[i - 1] = dw * s; dc[i - 1] = dk * s; ls[i - 1] -= log(s);
        } else dv[i - 1] = vec3(0.0);
      }
    }
    if (pole){   // carry on from the point at infinity; the turn is spent, so one step fewer can follow
      v = vec3(1e9, 0.0, 0.0); r = 0.0; steps -= 1.0;
      for (int i = 0; i < nt; i++) dv[i] = vec3(0.0);
      continue;
    }
    if (nt == 0){
      float lwc = length(w - c);   // the part of the step that came from z
      if (gAsk == ASK_PROBE && lw < 1e17 && r > 1e-3){
        float pr = pow(r, uPow);
        if (abs(lwc - pr) > 0.005 * max(lwc, pr) + 4e-7 * (lw + length(c))) gPowerLaw = false;
      }
      float dr = pn * lwc / max(r, 1e-6) * dv[0].x + dc[0].x;
      if (dr > 1e8){ dr *= 1e-8; dc[0].x *= 1e-8; ls[0] += 18.420681; }
      dv[0].x = dr;
    }
    v = w; rp = r; r = lw; it += 1.0;
    trapAdd(v, it);
  }
  gLast = v; gIt = it;
  if (esc) gIt = it - log(log(r) / log(uBail)) / log(P);
  bool outside = esc != swap;
  gEsc = outside ? 1.0 : 0.0;
  if (swap){
    gGrad = vec3(0.0);
    if (!esc){ gIt = bestIt; d = best; }
  }
  // Far from the set the estimate reads too long (it is exact only close in), so it is capped.
  // The comparisons are written so that a value that is not a number ends up as the cap too.
  float cap = 0.75 * length(p) + 0.5;
  if (outside) return d < cap ? max(d, 0.0) : cap;
  return d > -cap ? min(d, 0.0) : -cap;
}
float de(vec3 p, int nt, vec3 dir){
  bool jul = uJulia > 0.5, swap = gInsideOut;
  vec3 q = p, cj = uC;
  int n = nt, its = uIter;
  float sc = 1.0;
  if (gAsk == ASK_PROBE) swap = false;
  else if (gAsk == ASK_CELL){
    // The centre of a mosaic cell, asked as a point of the ordinary picture. A looser test than the picture's
    // own (half the steps) also keeps the cells just outside, whose Julia sets have only begun to fall apart.
    q = gCell; n = 0;
    if (!swap) its = max(2, (uIter + 1) / 2);
  } else if (gAsk == ASK_JULIA){
    sc = uMosaic * MOSAIC_FIT; q = (p - gCell) / sc; cj = gCell; jul = true; swap = false;
  }
  float d = sc * orbitDE(q, cj, jul, n, dir, its, swap);
  if (gAsk == ASK_JULIA){
    float ball = sc * (length(q) - MOSAIC_BALL);
    if (ball > d){ d = ball; gGrad = q; if (ball > 0.0) gEsc = 1.0; }
  }
  return d;
}`;
// Distance estimate for a Kleinian group with a quaternion parameter, after Jos Leys's method for
// the Maskit groups: carry the point back into one cell with the generators, tracking the scale.
const GL_KLEIN = `
const bool ORBIT_SCENE = false;
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
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0);
  float r2 = max(dot(p, p), 1e-12), r = sqrt(r2), R2 = uKInvR * uKInvR;
  vec3 q = uKInvC + (R2 / r2) * p;
  if (q.y < 0.0 || q.y > uKMu.y) { gEsc = 0.0; trapStart(); trapAdd(q, 0.0); gIt = 0.0; gLast = q; return 0.0; }
  float d = kde(q);
  return r2 * d / (R2 + r * d);
}`;
const GL_TAIL = `
// What main() is doing. The first six are steps; the rest say how the pixel ended.
const int PH_PROBE = 0, PH_MARCH = 1, PH_SLOPE = 2, PH_SHADOW = 3, PH_AO = 4, PH_COLOUR = 5;
const int END_MISS = 6, END_CUT = 7, END_LIT = 8, END_FLAT = 9;
// the four corners of a tetrahedron: the cheapest set of points that gives a slope by sampling
vec3 tetra(int i){ return vec3(i == 0 || i == 3 ? 1.0 : -1.0, i == 2 || i == 3 ? 1.0 : -1.0, i == 1 || i == 3 ? 1.0 : -1.0); }
// the set, cut by the plane z = uCut
float withCut(float d, vec3 q, float e){
  float pl = q.z - uCut;
  if (gEsc < 0.5 && pl > -e) d = min(d, 0.0);   // on or above the cut, a point inside the solid is solid
  gId = pl > d ? 1.0 : 0.0;
  return max(d, pl);
}
// where a ray is inside the drawing sphere of radius R: (enter, leave); leave < enter when it misses
vec2 span(vec3 ro, vec3 rd, float R){
  float b = dot(ro, rd), h = b * b - dot(ro, ro) + R * R;
  if (h <= 0.0) return vec2(1.0, -1.0);
  h = sqrt(h);
  return vec2(max(-b - h, 0.0), -b + h);
}
void main(){
  vec2 uv = (2.0 * (gl_FragCoord.xy + uOff) - uRes) / uRes.y;
  bool flat2 = uFlat > 0.5, picking = uPick > 0.5;
  vec3 ro = uCamPos, rd = normalize(uCam * vec3(uv * uFov, 1.0)), L = uLight, nor = vec3(0.0);
  vec3 slicePoint = vec3(uFlatC + 0.5 * uFlatH * uv, uSliceZ);
  if (flat2 && picking){ o = vec4(slicePoint, 1.0); return; }
  float bound = uBound > 0.0 ? uBound : 8.0, pix = 2.0 * uFov / uRes.y, farLimit = 0.45 * uBail;
  // An inside-out solid would also take in everything beyond the escape radius, so its picture stops short of it.
  vec2 spanOut = span(ro, rd, bound), spanIn = span(ro, rd, min(bound, farLimit));
  bool mosaic = ORBIT_SCENE && uMosaic > 0.0 && uJulia < 0.5, cellKnown = false;
  float t = spanOut.x, tOut = 0.0, dOut = 0.0, tIn = -1.0, gauge = 1.0, ts = 0.0, res = 1.0, ao = 0.0, d = 0.0;
  int phase = ORBIT_SCENE ? PH_PROBE : flat2 ? PH_COLOUR : PH_MARCH, n = 0, nt = uNT;
  // Neighbouring pixels are worked through together by the GPU, a turn of the loop at a time, and a turn
  // costs what its dearest pixel costs. So the light and crevice queries (long orbits, close to the surface)
  // wait at two gates until every ray has finished marching (mostly short orbits, far away) rather than
  // riding along with it. A waiting turn costs next to nothing.
  int turns = mosaic ? 2 : 1, gate1 = turns * uSteps + 1, gate2 = gate1 + turns * (uShSteps + 4);
  int budget = gate2 + turns * 5 + 2;
  if (!ORBIT_SCENE && !flat2 && spanOut.y < spanOut.x){ phase = END_MISS; budget = 0; }
  gInsideOut = false; gPowerLaw = true; gId = 0.0;
  // Every distance query of the picture goes through the one call to de() in this loop.
  for (int i = 0; i < budget; i++){
    if (!flat2 && i < (phase >= PH_AO ? gate2 : phase >= PH_SLOPE ? gate1 : 0)) continue;
    float tMax = gInsideOut ? spanIn.y : spanOut.y, e = max(uDetail * pix * t, 1e-7);
    float reach = 0.006 * t * float((n + 1) * (n + 1)), leave = 1e9;
    vec3 p = flat2 ? slicePoint : ro + rd * t, q = p, dir = rd;
    int qn = nt;
    gAsk = ASK_PLAIN;
    if (phase == PH_PROBE){ q = farLimit * normalize(vec3(0.62, 0.37, 0.69)); qn = 0; gAsk = ASK_PROBE; }
    else if (phase == PH_SLOPE) q = p + tetra(n) * (uNormEps * e);
    else if (phase == PH_SHADOW){ q = p + nor * 2.0 * e + L * ts; qn = min(nt, 1); dir = L; }
    else if (phase == PH_AO){ q = p + nor * reach; qn = min(nt, 1); dir = nor; }
    else if (flat2) qn = 3;
    if (mosaic && phase != PH_PROBE){
      // A mosaic query takes two turns: first the cell's centre, then (if the cell draws anything) its Julia set.
      float a = uMosaic;
      gCell = a * floor(q / a + 0.5);
      vec3 ex = (0.5 * a - (q - gCell) * sign(dir)) / max(abs(dir), 1e-9);
      leave = min(ex.x, min(ex.y, ex.z)) + 0.01 * a;   // along the ray to just past the cell wall
      gAsk = cellKnown ? ASK_JULIA : ASK_CELL;
    }

    d = de(q, qn, dir);

    bool empty = false;
    if (gAsk == ASK_CELL){
      if (gEsc < 0.5){ cellKnown = true; continue; }
      // An empty cell. Nothing is drawn nearer than "skip": the estimate is to the nearest centre that draws
      // something, less the reach of this cell and of that one.
      float skip = 0.5 * d - 1.4 * uMosaic;
      empty = true; leave = max(leave, skip); d = max(skip, 4.0 * uMosaic);
    }
    cellKnown = false;
    if (phase == PH_PROBE){
      gInsideOut = gEsc < 0.5;
      if (nt == 0 && !gPowerLaw) nt = 1;   // the single-number estimate only holds for a pure power plus c
      vec2 sp = gInsideOut ? spanIn : spanOut;
      if (!flat2 && sp.y < sp.x){ phase = END_MISS; break; }
      t = sp.x; phase = flat2 ? PH_COLOUR : PH_MARCH;
      continue;
    }
    if (phase == PH_COLOUR){ phase = flat2 ? END_FLAT : END_LIT; break; }
    // With no neighbouring orbits the estimate can read many times too short, by a factor nobody knows.
    // That mode therefore trusts the sign of the estimate and how fast it falls along the ray, not its
    // size: "ahead" is where the straight line through the last two points outside reaches zero. And gauge
    // (how much too short, measured at the hit) scales the estimate back up for the shadow and crevice queries.
    bool rough = ORBIT_SCENE && nt == 0, settle = false;
    if (phase == PH_SLOPE){
      nor += tetra(n) * d; n++;
      if (n < 4) continue;
      if (rough) gauge = clamp(4.0 * uNormEps * e / max(length(nor), 1e-30), 1.0, 64.0);
      settle = true;
    } else {
      d = withCut(d > 0.0 ? d * gauge : d, q, e);
      if (phase == PH_MARCH){
        n++;
        float tol = rough ? 0.0 : e, ahead = d;
        if (rough) ahead = dOut > d && dOut < 4.0 * d ? d * (t - tOut) / (dOut - d) : 1e9;
        bool conv = false;
        if (tIn >= 0.0 || (d < -tol && dOut > 0.0)){
          // The ray has stepped over the surface: it lies between tOut, the last point outside, and tIn,
          // the nearest point inside. The estimates either side are wrong by about the same factor, so
          // try where the straight line between them crosses zero, or halve the gap when that is not known.
          if (d < 0.0){ tIn = t; t = tOut + (t - tOut) * clamp(dOut / (dOut - d), 0.1, 0.9); }
          else { tOut = t; dOut = d; t = 0.5 * (tOut + tIn); }
          conv = tIn - tOut < 0.5 * e || (!rough && abs(d) < e);
        } else if (d < tol || ahead < e) conv = true;
        else {
          float stride = d * uStepK;
          if (rough){
            // stride toward where the surface seems to be, within limits: a long stride can jump a thin sheet
            if (ahead < 1e8) stride = clamp(0.9 * ahead, stride, (d < 2.0 * e ? 8.0 : 3.0) * stride);
            stride = max(stride, 0.5 * e);
          }
          tOut = t; dOut = d; t += empty ? leave : min(stride, leave);
        }
        if (!conv && t <= tMax && n < uSteps) continue;
        // out of steps still counts as a hit (the ray is grazing a surface), except in an empty mosaic cell
        if (t > tMax || (!conv && empty)){ phase = END_MISS; break; }
        if (gId > 0.5 || picking){ phase = END_CUT; break; }
        n = 0;
        if (uAnalytic < 0.5 || nt != 3 || gInsideOut){ phase = PH_SLOPE; continue; }
        nor = gGrad; settle = true;
      } else if (phase == PH_SHADOW){
        res = min(res, 10.0 * d / ts); n++;
        if (res >= 0.005 && ts <= 5.0 && n < uShSteps){ ts += empty ? leave : min(clamp(d, 2.0 * e, 0.35), leave); continue; }
        n = 0; phase = uAO > 0.5 ? PH_AO : PH_COLOUR;
      } else {
        ao += pow(0.7, float(n)) * clamp(1.0 - 1.6 * d / reach, 0.0, 1.0); n++;
        if (n == 4) phase = PH_COLOUR;
      }
    }
    if (settle){
      nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
      if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
      n = 0; ts = 4.0 * e;
      phase = uShadow > 0.5 && dot(nor, L) > 0.001 ? PH_SHADOW : uAO > 0.5 ? PH_AO : PH_COLOUR;
    }
  }
  vec3 col = uBg, p = ro + rd * t;
  if (picking){ o = phase == END_CUT ? vec4(p, 1.0) : vec4(0.0); return; }
  if (phase == END_FLAT){
    if (gInsideOut && length(slicePoint) > farLimit){ gEsc = 1.0; d = max(d, length(slicePoint) - farLimit); }
    col = flatColour(slicePoint, d, uFlatH / uRes.y);
  } else if (phase == END_CUT){
    // the cut face, hatched the way a section drawing marks cut material
    float s = abs(fract((gl_FragCoord.x + gl_FragCoord.y) / (8.0 * uPx)) - 0.5);
    col = mix(uCutCol, uCutInk, 0.55 * smoothstep(0.36, 0.42, s));
  } else if (phase == END_LIT){
    // the last query was made at the hit itself, so the colour hooks read live values
    colourCapture();
    vec3 alb = surfaceColour(p, nor, t);
    float dif = clamp(dot(nor, L), 0.0, 1.0), sh = clamp(res, 0.0, 1.0), occ = clamp(1.0 - 0.45 * ao, 0.0, 1.0);
    sh = sh * sh * (3.0 - 2.0 * sh);
    float sky = 0.5 + 0.5 * nor.z;
    float bac = clamp(0.3 + 0.7 * dot(nor, normalize(vec3(-L.x, -L.y, 0.3))), 0.0, 1.0);
    float fre = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 3.0);
    float spe = pow(clamp(dot(nor, normalize(L - rd)), 0.0, 1.0), 40.0) * dif * sh;
    vec3 lig = 1.45 * dif * sh * vec3(1.00, 0.94, 0.84) + occ * (0.42 * sky * vec3(0.50, 0.62, 0.80) + 0.20 * bac * vec3(0.80, 0.70, 0.58));
    col = alb * lig + 0.16 * spe + 0.06 * fre * occ * alb;
    if (colourUnlit() > 0.5) col = alb;
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
