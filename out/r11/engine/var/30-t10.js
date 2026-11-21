// ---------- shaders
// The scene program is GL_HEAD + glNeeds(needs) + GL_COLOUR + (approach.glsl + GL_ORBIT | GL_KLEIN) + GL_TAIL.
//
// Three things shape this file.
// 1. Compile time. The D3D compiler behind WebGL on Windows copies a function into every place that calls it,
//    and its time also grows with every value a loop has to carry from one turn to the next. So the formula is
//    written into the shader once (f(), start() and cmap() have one call site each, inside orbitDE(), which
//    has one call site in de(), which has one call site in main()), main() is a state machine around that
//    single call, the colour of a pixel comes from one call to pixelColour() whatever kind of pixel it is, and
//    whatever can be recomputed each turn is recomputed instead of carried.
// 2. The solid is always the bounded piece. Normally that is the set of points whose orbit never leaves the
//    escape radius. When points far away never leave it either (negative powers do this: a huge z comes
//    straight back to c), that set fills all of space outside a small region, so the picture swaps the roles
//    and draws the region whose orbits do leave. gEsc therefore means "this point is outside the solid".
// 3. A program is built for what the picture needs (glNeeds below). Trap solids and inside colouring are left
//    out of the source of a program that does not use them: left in and switched off by a uniform, the trap
//    solid alone doubled the drawing time of the opening picture.
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
uniform float uBound, uMosaic, uFlat, uFlatH, uSliceZ, uRaw;
uniform vec4 uA;
uniform vec3 uC, uAbs, uSgn, uBg, uCutCol, uCutInk, uLight;
uniform int uIter, uSteps, uNT, uShSteps;
uniform vec3 uKMu, uKInvC; uniform float uKL, uK3, uKInvR;
out vec4 o;
const float PI = 3.14159265358979;
// Results of the latest distance query. gEsc: 1 when the point is outside the solid. gIt: smooth step count.
// gLast: last orbit point. gGrad: outward slope (set only with three neighbouring orbits).
// gId: 1 when the cut plane, not the set, is the nearer surface. gOnTrap: the distance returned is to the trap
// solid (see uTrapSolid in the colour module), not to the set.
// gFade is set BEFORE a query: an orbit point with step number "it" counts towards the colour trap with the
// weight clamp(gFade + 1 - it, 0, 1), so 1e9 lets every point count in full. Only the query the surface colour
// of the 3D view or of a 3D model is read from uses anything else: there it is the number of orbit steps the trap
// reads (colourReach() in the colour module), which depends on a dial and on the size of a pixel and on nothing
// else. The Kleinian program has no fading (its trapAdd is built without the weights).
// gPix is also set before a query: the size of a pixel where the point asked about lies, or 0 when the
// answer must not depend on the picture (the 2D view, volume sampling).
// gLand is set before a query too and only the Kleinian search reads it. Above 0 it is a length in the scene:
// the search stops feeding the colour trap at the first step that lands within that length of a pearl or a wall,
// and feeds that last point as if it lay exactly on the wall (the query a hit's trap colour is read from).
float gEsc, gIt, gId, gFade, gPix, gLand; vec3 gLast, gGrad; bool gOnTrap;
// Layers of a trap solid thinner than this many pixels fade out of the picture (orbitDE); the colour module
// follows the same rule when it looks for the step that touched the trap.
const float TRAP_THIN = 2.0;
// That rule is about how finely the layers are folded, which goes with the stretch of the orbit, not about the
// thickness the user has chosen: read literally, a thin trap lost its large first pieces too and the whole solid
// vanished. So a trap thinner than TRAP_REF (where the thickness dial starts) fades where a trap of that thickness
// would, in proportion: the same pieces, with thinner walls. Thicker traps go by their own thickness, as before.
const float TRAP_REF = 0.05;
const float MOSAIC_FIT = 0.225;   // cell widths per unit of a mosaic Julia set: a set of radius 2 spans 90% of its cell
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
// The switches a program is built with, as source text that goes between GL_HEAD and GL_COLOUR. needs is what
// colProgramNeeds() (25-colour.js) returns: { solid, inside }. TRAP_SOLIDS 1: the program can draw the trap as a
// solid. COL_INSIDE 1: it can colour the inside of the set (the 2D view and the cut face). With 0 the code is
// not in the program at all. glNeedsKey is the same answer as a short tag for the program's key.
// The third switch is not a colour setting but the kind of program: COL_KLEIN 1 for the Kleinian search, whose
// trap never fades (gFade is always 1e9 there), so its trapAdd is written without the fading weights.
const glNeeds = (needs, klein) => `#define TRAP_SOLIDS ${needs.solid ? 1 : 0}\n#define COL_INSIDE ${needs.inside ? 1 : 0}\n#define COL_KLEIN ${klein ? 1 : 0}\n#define RAW_FIT ${needs.raw ? 1 : 0}\n`;
// The fourth switch is the use: RAW_FIT 1 in the program a 3D model's samples are drawn with (needs.raw, asked for
// by sampleSlice in 40-render.js; tag 'r'). Only that program carries the code that moves a sample onto the surface
// for its colour and colours the model's cut face: in the program of the picture those branches of main() cost
// about half a second of preparing for nothing (measured in round 7).
const glNeedsKey = needs => (needs.solid ? 's' : '') + (needs.inside ? 'i' : '') + (needs.raw ? 'r' : '');
// Distance estimate for an iterated equation. Up to three neighbouring orbits are carried along with
// the point and renormalised every step; how fast they separate is the derivative, for any formula.
// With no neighbours (the fastest setting) one running number stands in for it: the stretch n|z|^(n-1) of
// a pure power, which is the estimate Mandelbulb renderers use.
const GL_ORBIT = `
const bool ORBIT_SCENE = true;
const float MOSAIC_BALL = 2.1;    // each mosaic set is clipped to a ball of this radius, just short of the cell walls
// Only in the program a 3D model's samples are drawn with (RAW_FIT, see RAW_SLOPE in main()). gThinK is set before
// a query, like gPix: above 0, the layers of a trap solid that the picture does not draw at all are pushed away
// that many times as fast as they fall short of RAW_GONE pixels. The picture's own rule (orbitDE) leaves such a
// layer as a dip in the estimate, never more than four pixels deep: a ray is slowed by it and passes. A sample of a
// model that looks for the picture's surface from a cell away would stop in it. RAW_GONE: half a layer's width, in
// pixels, below which the picture's rule leaves nothing for a ray to stop on (a ray stops where the estimate reads
// 0.8 of a pixel, and the rule adds 2 for each 1 that the half width is short of TRAP_THIN).
#ifndef RAW_FIT
#define RAW_FIT 1
#endif
#if RAW_FIT
float gThinK;
const float RAW_GONE = 1.07;
#endif
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
  // Neighbour i (1 to 3) sits at z + dvI * exp(-lsI) with the constant c + dcI * exp(-lsI).
  // With no neighbours, slot 1 holds the running stretch instead: dv1.x * exp(ls1), fed by dc1.x.
  // These are separate variables picked with "i == 1" tests, not arrays: an array indexed by a loop
  // counter lives in memory on the GPU, and these are read and written in the innermost loop.
  vec3 dv1 = vec3(0.0), dv2 = vec3(0.0), dv3 = vec3(0.0), dc1 = vec3(0.0), dc2 = vec3(0.0), dc3 = vec3(0.0);
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
    else if (i == 1){ dv1 = s - v; dc1 = d; }
    else if (i == 2){ dv2 = s - v; dc2 = d; }
    else { dv3 = s - v; dc3 = d; }
  }
  float ls1 = -log(h0), ls2 = ls1, ls3 = ls1;
  if (nt == 0){ dv1 = vec3(jul ? 1.0 : 0.0, 0.0, 0.0); dc1 = vec3(jul ? 0.0 : 1.0, 0.0, 0.0); ls1 = 0.0; }
  float r = length(v), rp = r, it = 0.0, steps = float(its), best = 1e30, bestIt = 0.0, d = 0.0, P = 2.0;
  bool esc = false, still = false;
  // The trap solid (uTrapSolid 1 or 2): every point that has an orbit point within uTrapW of the trap shape.
  // tbest is its distance estimate: over the orbit, the least of (how far the orbit point is from the
  // thickened trap) divided by (how much the map from p to that orbit point stretches).
  // Only in a program built for it (TRAP_SOLIDS): this sits in the innermost loop of the picture.
#if TRAP_SOLIDS
  bool trapOn = uTrapSolid > 0.5 && gAsk != ASK_PROBE && gAsk != ASK_CELL;
  float tbest = 1e30;
#endif
  trapStart();
  for (int k = 0; k <= its; k++){
    esc = r > uBail;
    bool last = esc || still || k == its;
#if TRAP_SOLIDS
    if (trapOn && !esc && k >= uTrapSkip){
      float lm = ls1, den = dv1.x;
      if (nt == 3){
        // The neighbours are the columns of the derivative. Its greatest stretch is at most the root of the
        // largest row sum of their products with each other, which is exact when the columns are at right
        // angles (a map that keeps shapes) and errs on the large side otherwise.
        lm = max(ls1, max(ls2, ls3));
        vec3 a1 = dv1 * exp(ls1 - lm), a2 = dv2 * exp(ls2 - lm), a3 = dv3 * exp(ls3 - lm);
        float m12 = abs(dot(a1, a2)), m23 = abs(dot(a2, a3)), m31 = abs(dot(a3, a1));
        den = sqrt(max(dot(a1, a1) + m12 + m31, max(dot(a2, a2) + m12 + m23, dot(a3, a3) + m23 + m31)));
      } else if (nt == 1) den = length(dv1);
      // Late steps wrap the set in layer upon layer of this solid, each thinner than the last. Layers thinner
      // than a pixel cannot be drawn: a ray would stop on whichever one it happened to reach, and the picture
      // would show them as ripples and scratches. So a layer loses thickness faster than it naturally would
      // once it is under TRAP_THIN pixels thick (half its width, to be exact), and is gone at about half that.
      float inv = exp(clamp(-lm, -80.0, 80.0)) / max(den, 1e-30), wr = max(uTrapW, TRAP_REF);
      float td = (trapDist(v) - uTrapW) * inv + 2.0 * (uTrapW / wr) * max(TRAP_THIN * gPix - wr * inv, 0.0);
#if RAW_FIT
      td += gThinK * (uTrapW / wr) * max(RAW_GONE * gPix - wr * inv, 0.0);
#endif
      if (td < tbest) tbest = td;
    }
#endif
    if (last || swap){
      // how fast |z| changes as p moves: gradient g and size den, both without the common factor exp(lm)
      vec3 vh = v / max(r, 1e-30), g = vec3(0.0);
      float lm = ls1, den = dv1.x;
      if (nt == 3){
        lm = max(ls1, max(ls2, ls3));
        g = vec3(dot(dv1, vh) * exp(ls1 - lm), dot(dv2, vh) * exp(ls2 - lm), dot(dv3, vh) * exp(ls3 - lm));
        den = length(g);
      } else if (nt == 1) den = length(dv1);
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
      if (i == 1){ dz = dv1; dk = dc1; } else if (i == 2){ dz = dv2; dk = dc2; } else if (i == 3){ dz = dv3; dk = dc3; }
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
        // keep the neighbour a fixed small share of |z| away, and remember the factor in ls
        float lg = 0.0;
        if (m > 0.0){ float s = clamp(2e-3 * (lw + 1e-3) / m, 1e-8, 1e8); dw *= s; dk *= s; lg = log(s); }
        else dw = vec3(0.0);
        if (i == 1){ dv1 = dw; dc1 = dk; ls1 -= lg; } else if (i == 2){ dv2 = dw; dc2 = dk; ls2 -= lg; } else { dv3 = dw; dc3 = dk; ls3 -= lg; }
      }
    }
    if (pole){   // carry on from the point at infinity; the turn is spent, so one step fewer can follow
      v = vec3(1e9, 0.0, 0.0); r = 0.0; steps -= 1.0;
      if (nt > 0){ dv1 = vec3(0.0); dv2 = vec3(0.0); dv3 = vec3(0.0); }
      continue;
    }
    if (nt == 0){
      float lwc = length(w - c);   // the part of the step that came from z
      if (gAsk == ASK_PROBE && lw < 1e17 && r > 1e-3){
        float pr = pow(r, uPow);
        if (abs(lwc - pr) > 0.005 * max(lwc, pr) + 4e-7 * (lw + length(c))) gPowerLaw = false;
      }
      float dr = pn * lwc / max(r, 1e-6) * dv1.x + dc1.x;
      if (dr > 1e8){ dr *= 1e-8; dc1.x *= 1e-8; ls1 += 18.420681; }
      dv1.x = dr;
    }
    // An orbit that has come to rest will never escape, and where far points never escape most orbits
    // come to rest within a few steps: stop there instead of running out the count.
    still = swap && dot(w - v, w - v) < 1e-12 * lw * lw;
    v = w; rp = r; r = lw; it += 1.0;
    trapAdd(v, it);
  }
  gLast = v; gIt = it;
  if (esc) gIt = it - log(log(r) / log(uBail)) / log(P);
  bool outside = esc != swap;
  if (swap){
    gGrad = vec3(0.0);
    if (!esc){ gIt = bestIt; d = best; }
  }
  // Far from the set the estimate reads too long (it is exact only close in), so it is capped.
  // The comparisons are written so that a value that is not a number ends up as the cap too.
  float cap = 0.75 * length(p) + 0.5;
  if (outside) d = d < cap ? max(d, 0.0) : cap;
  else d = d > -cap ? min(d, 0.0) : -cap;
  // The trap solid takes the place of the set (1) or joins it (2: whichever surface is nearer).
  // (Without trap solids gOnTrap stays false, as main() set it.)
#if TRAP_SOLIDS
  gOnTrap = trapOn && (uTrapSolid < 1.5 || tbest < d);
  if (gOnTrap){ outside = tbest > 0.0; d = clamp(tbest, -cap, cap); gGrad = vec3(0.0); }
#endif
  gEsc = outside ? 1.0 : 0.0;
  return d;
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
    // The flat view can afford to be looser still: nothing hides anything there, and dust is cheap to draw.
    // (Volume sampling is for a model of the 3D picture, so it keeps to that picture's test.)
    q = gCell; n = 0;
    if (!swap) its = uFlat > 0.5 && uRaw < 0.5 ? min(3, uIter) : max(2, (uIter + 1) / 2);
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
// The true distance to a pearl, in the units of the wall it has been carried onto. A pearl is the sphere that
// the maps applied so far carry onto a wall. h: how far the mapped point stands from that wall. D: the same for
// W, the image of the point at infinity. kk = 4 / |z - W|^2. Dividing h by the scale factor alone gives
// t (1 + t / 2 rho) for a pearl of radius rho at the true distance t: right beside the pearl, far too long for a
// small pearl seen from open space, where rays then stepped into it (a hollow shell) or over it. This is that
// equation solved for t; the caller still divides by the scale factor.
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
// The search: carry the point back into one cell with the generators, tracking the scale factor DF and W.
// Returns the distance to the nearest pearl it met (negative inside one), or to the trap solid, or to both.
// land: 0, or (for the query a hit's trap colour is read from) the landing length in the units of the cell. A ray
// stops a fraction of a pixel off a pearl, and left alone the search carries that hovering point on past the wall
// the pearl is an image of, to places that depend on how high it hovered: the trap colours then changed with every
// quality setting. So once a step lands within the landing length of a pearl the search is over: that point is
// fed to the trap as a point of the wall itself, and no later one is.
float kde(vec3 z, float land){
  vec3 mu = uKMu, lz = z + vec3(1.0), llz = z - vec3(1.0), W = vec3(1e6);
  float a = mu.y, DF = 1.0, it = 0.0, fs = sign(-mu.x);
  float sx = mu.x / a, sz = mu.z / a;
  trapStart();
  float best = min(z.y, a - z.y);   // the two walls, before any map is applied
#if TRAP_SOLIDS
  bool trapSolid = uTrapSolid > 0.5, out1 = uTrapSkip > 0, out2 = true;
  float bestT = 1e9;
  vec3 kd1 = vec3(1e9), kd2 = vec3(2e9);
  if (trapSolid && uTrapSkip <= 0){ bestT = trapDist(z) - uTrapW; gTouch = vec4(z - uTrapC, bestT + uTrapW); gTouchS = bestT; }
#endif
  for (int i = 0; i < uIter; i++){
    vec3 z0 = z;
    z.x -= sx * z.y; z.x = wrapf(z.x, 2.0, -1.0); z.x += sx * z.y;
    if (uK3 > 0.5) { z.z -= sz * z.y; z.z = wrapf(z.z, 2.0 * uKL, -uKL); z.z += sz * z.y; }
    W += z - z0;
    float xs = z.x - 0.5 * mu.x;
    if (z.y >= a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * sign(xs) * (1.0 - exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))) { z = mu - z; W = mu - W; }
    // The trap as a solid: every point whose orbit, from step uTrapSkip on, comes within uTrapW of the trap shape.
    // To first order the point is that far from it, divided by how much the maps so far have stretched.
    // Step i is the point z0 as the maps left it; z is the same point carried into one copy of the pattern.
    // The search comes to rest in a cycle of two: from there on the point as it lies in its copy is where it was
    // two steps before, and z0 is that earlier point slid or turned by the moves of the pattern. A step that only
    // comes back to a step that was skipped is skipped as well. Left in, it tested the trap shape itself at the
    // starting point (half turned about mu / 2, or slid by 2), which "Orbit steps skipped at the start" is there to
    // leave out: in a group that leans, the half-turned trap reaches under the dividing line, and its part there
    // came into the solid two steps late as huge pieces cut off flat along the edges of the copy.
    // The step that touched is kept here for the colours (the colour module's own record is off in this program).
#if TRAP_SOLIDS
    if (trapSolid){
      bool outNow = i < uTrapSkip || (out2 && dot(z - kd2, z - kd2) < 1e-5);
      if (!outNow && i > 0){
        float dq = trapDist(z0), sc = (dq - uTrapW) / DF;
        if (sc < bestT){ bestT = sc; gTouch = vec4(z0 - uTrapC, dq); gTouchIt = it; gTouchS = sc; gTouchStr = DF; }
      }
      out2 = out1; out1 = outNow; kd2 = kd1; kd1 = z;
    }
#endif
    float iR = 1.0 / max(dot(z, z), 1e-20);
    z = mu + vec3(z.x, -z.y, -z.z) * iR;   // q -> mu + 1/q
    W = mu + vec3(W.x, -W.y, -W.z) / max(dot(W, W), 1e-20);
    DF *= iR; it += 1.0;
    vec3 zw = z - W;
    float kk = 4.0 / max(dot(zw, zw), 1e-30);
    float cand = min(kpearl(z.y, W.y, kk), kpearl(a - z.y, a - W.y, kk)) / DF;
    best = min(best, cand);
    if (land > 0.0 && cand < land){ trapAdd(vec3(z.x, z.y < 0.5 * a ? 0.0 : a, z.z), it); break; }
    trapAdd(z, it);
    if (dot(z - llz, z - llz) < 1e-5) break;
    llz = lz; lz = z;
  }
  // In the 3D view the count is reported 8 steps high. "Escape count" colours come out the same (8 steps are one
  // full turn of the palette), and a fading tail (gFade) set from this count leaves every step of the search in.
  gIt = uFlat > 0.5 ? it : it + 8.0; gLast = z;
  best = min(best, 0.3);
  // The trap solid takes the place of the pearls (1) or joins them (2: whichever surface is nearer).
#if TRAP_SOLIDS
  gOnTrap = trapSolid && (uTrapSolid < 1.5 || bestT < best);
  if (gOnTrap) best = bestT;
#endif
  return best;
}
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float r2 = max(dot(p, p), 1e-12), r = sqrt(r2), R2 = uKInvR * uKInvR;
  vec3 q = uKInvC + (R2 / r2) * p;   // turned out through the sphere
  float wall = min(q.y, uKMu.y - q.y), d = wall;
  // The landing length (see kde) in the units of the cell; none while the trap alone is the solid, because then
  // the pearls and the walls are not in the picture.
  bool walls = uTrapSolid < 0.5 || uTrapSolid > 1.5;
  float land = walls ? gLand * R2 / r2 : 0.0;
  // inside a wall sphere (unless the trap alone is the solid): no search is needed, and the depth is known.
  // A hit on a wall sphere has landed before the first step: its trap colour is read from the wall point alone.
  if (walls && wall < land) {
    if (land > 0.0) q.y = q.y < 0.5 * uKMu.y ? 0.0 : uKMu.y;
    trapStart(); trapAdd(q, 0.0); gIt = land > 0.0 ? 8.0 : 0.0; gLast = q;
  }
  else d = kde(q, land);
  if (d <= 0.0) gEsc = 0.0;
  // back through the sphere: a length d beside q is at least this long beside p
  return d > 0.0 ? r2 * d / (R2 + r * d) : d * r2 / R2;
}`;
const GL_TAIL = `
#ifndef RAW_FIT
#define RAW_FIT 1
#endif
// What main() is doing. The first eight are steps, in the order of the gates they wait at; the rest say how the
// pixel ended.
const int PH_PROBE = 0, PH_MARCH = 1, PH_SLOPE = 2, PH_SHADOW = 3, PH_CUT = 4, PH_AO = 5, PH_FIT = 6, PH_COLOUR = 7;
const int END_MISS = 8, END_CUT = 9, END_LIT = 10, END_FLAT = 11;
// PH_FIT asks for the estimate this share of the way down from the hit to where the surface is expected.
const float FIT_STEP = 0.6;
// With neighbouring orbits a ray has hit where the distance estimate reads this many pixels (see the march).
const float LEVEL = 0.8;
// Volume samples (the 3D model). A model point lies on a grid edge and takes its colour from the samples at the two
// ends, which lie up to a cell off the surface. Read where the sample is, a trap colour drew rings wherever the
// surface crossed a level of the grid, and came from fewer orbit steps than the picture's. So a sample whose
// estimate reads between RAW_IN sample spacings inside and RAW_OUT outside (every end of an edge the surface can
// cross, with the widest surface offset) reads its trap colour from the surface itself, found as PH_FIT finds it
// under a hit, and with the picture's number of steps. A sample deeper inside than that, or inside the solid within
// RAW_CUT spacings of the cut plane (the two slices whose samples the model's cut face is made between), is coloured
// as the cut face (to RAW_ABOVE spacings above the plane: the model's face stands above it by the surface offset,
// which goes up to two cells). RAW_HATCH is the share of ink in the cut face's hatching, taken over the whole face: a model
// has no hatching, so its cut face gets that mix.
const float RAW_OUT = 3.2, RAW_IN = 1.5, RAW_CUT = 1.01, RAW_ABOVE = 3.01, RAW_HATCH = 0.12;
// A sample of a trap solid. The trap solid has no slope of its own to hand over (gGrad is zero on the trap's part),
// and its estimate is the nearest of many layers, most of them far thinner than anything the picture shows: a cell
// off the surface the nearest one is some hair-thin layer of a late step, and read there the colour came from that
// step (a model of smooth rainbow bubbles came out teal and speckled). So such a sample takes four more readings
// round itself, RAW_SLOPE sample spacings off (the corners of a tetrahedron: their mean is the estimate at the
// sample, their differences its slope), steps down that slope to where the surface should be, reads the estimate
// there, and reads the colour where the line through the two readings reaches zero, as every other sample does.
// Those readings are made in the solid as the picture shows it: with the picture's own pixel at the sample (gPix),
// so that the layers the picture thins out are thinned here, and with the layers it does not draw at all pushed
// well away (gThinK = RAW_THIN, see RAW_GONE). The colour is then read by the picture's own rule alone. The
// distance the sample hands back is its first reading, as before: the shape of the model does not change by this.
const float RAW_SLOPE = 0.25, RAW_THIN = 32.0;
// The colour an orbit trap gives a hit must be a property of the surface, not of the ray that found it. A ray
// stops a fraction of a pixel short of the solid, at a height that every quality setting sets differently, and the
// orbit of that hovering point keeps to the surface for a while and then flies off: where the flight passes the
// trap depends on the height, which changes smoothly from pixel to pixel. Read from there, with every step
// counting, the trap painted rings over the solid, one for every extra step, like a stack of slices, and the
// colours moved with the quality settings, the step limit and the distance from the camera. Two things cure it.
// 1. The colour is read from the surface itself: the hit is moved down its own normal by the height it hovers at
//    ("lift"). The estimate at the hit is not that height: beside an iterated set it reads about half of it, by a
//    factor that changes from place to place, and a step of the orbit doubles whatever error is left, so that
//    half a pixel is enough to change the colour. But the estimate falls in a straight line on the way down. So
//    one more query (PH_FIT) reads it part of the way down, and the line through the two readings gives the
//    height. (The Kleinian estimate is the true distance to a pearl and needs no such query.)
// 2. The trap reads a fixed number of orbit steps (gFade = colourReach(pixel), in the colour module): the number
//    on the "Orbit steps the trap reads" dial, or fewer where a pixel cannot show that many. "The nearest the
//    first K orbit points come to the trap" is a continuous function of the starting point, inside and outside
//    the solid alike, so what is left of the height does not show. The pixel meant is one of the page (uPx
//    picture pixels), so the moving preview, every quality setting and a saved picture of any size agree.
// Colours that do not come from a trap are read from the hit point as before, so that they do not change.
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
  float t = spanOut.x, tOut = 0.0, dOut = 0.0, tIn = -1.0, gauge = 1.0, ts = 0.0, res = 1.0, ao = 0.0, d = 0.0, lift = 0.0;
  int phase = ORBIT_SCENE ? PH_PROBE : flat2 ? PH_COLOUR : PH_MARCH, n = 0, nt = uNT, crawl = 0;
  // Neighbouring pixels are worked through together by the GPU, a turn of the loop at a time, and a turn
  // costs what its dearest pixel costs. So the light and crevice queries (long orbits, close to the surface)
  // wait at two gates until every ray has finished marching (mostly short orbits, far away) rather than
  // riding along with it. A waiting turn costs next to nothing.
  int turns = mosaic ? 2 : 1, gate1 = turns * uSteps + 1, gate2 = gate1 + turns * (uShSteps + 4);
  int budget = gate2 + turns * 6 + 2;
  if (!ORBIT_SCENE && !flat2 && spanOut.y < spanOut.x){ phase = END_MISS; budget = 0; }
  gInsideOut = false; gPowerLaw = true; gId = 0.0; gOnTrap = false;
#if RAW_FIT
  // this slice of volume samples is one of those the model's cut face is made between (see RAW_CUT)
  bool rawFace = uSliceZ - uCut > -RAW_CUT * uFlatH / uRes.y && uSliceZ - uCut < RAW_ABOVE * uFlatH / uRes.y;
  // this volume sample lies beside the trap's part of a trap solid and is finding that surface (see RAW_SLOPE)
  bool rawTrap = false;
#endif
  // Every distance query of the picture goes through the one call to de() in this loop.
  for (int i = 0; i < budget; i++){
    if (!flat2 && i < (phase >= PH_AO ? gate2 : phase >= PH_SLOPE ? gate1 : 0)) continue;
    float tMax = gInsideOut ? spanIn.y : spanOut.y, e = max(uDetail * pix * t, 1e-7);
    float reach = 0.006 * t * float((n + 1) * (n + 1)), leave = 1e9;
    vec3 p = flat2 ? slicePoint : ro + rd * t, q = p, dir = rd;
    // The step the colour of a hit begins with: a trap colour first finds the surface under the hit (PH_FIT).
    int qn = nt, hue = ORBIT_SCENE && colourFromTrap() ? PH_FIT : PH_COLOUR;
    // How far down from the hit PH_FIT reads the estimate again: lift holds what it read at the hit, which beside
    // an iterated set is about half the height. The fastest estimate (no neighbouring orbits) cannot be trusted
    // for its size, so there PH_FIT uses one neighbouring orbit along the normal and takes both readings itself.
    float fit1 = 2.0 * FIT_STEP * lift;
    bool fitFirst = ORBIT_SCENE && nt == 0 && crawl == 0;
    gAsk = ASK_PLAIN; gFade = 1e9; gLand = 0.0; gPix = flat2 ? 0.0 : pix * t;
#if RAW_FIT
    gThinK = 0.0;
#endif
    // the size of a page pixel at this point, in the units the orbit runs in (a mosaic set is drawn small)
    // (For a volume sample that is the pixel of the picture the model is made from: uPx then holds the height of
    // that picture in page pixels, and the camera is the picture's, so a model reads as many steps as its picture.)
#if RAW_FIT
    float pagePix = (flat2 ? (uRaw > 0.5 ? 2.0 * uFov * length(p - ro) / uPx : uFlatH / uRes.y) : pix * t * uPx) / (mosaic ? uMosaic * MOSAIC_FIT : 1.0);
#else
    float pagePix = (flat2 ? uFlatH / uRes.y : pix * t * uPx) / (mosaic ? uMosaic * MOSAIC_FIT : 1.0);
#endif
    if (phase == PH_PROBE){ q = farLimit * normalize(vec3(0.62, 0.37, 0.69)); qn = 0; gAsk = ASK_PROBE; }
    else if (phase == PH_SLOPE) q = p + tetra(n) * (uNormEps * e);
    // The shadow ray asks with all the neighbouring orbits the picture has, not with one along the ray. One
    // neighbour measures how fast the orbit moves along the ray alone; where the equation stretches space more
    // across the ray than along it (light that grazes a fold), that read several times too long, the ray strode
    // through the fold it should have stopped at, and the shadowed side came out hatched with fine lit lines.
    else if (phase == PH_SHADOW){ q = p + nor * 2.0 * e + L * ts; dir = L; if (dot(nor, L) > 0.5) qn = min(nt, 1); }
    else if (phase == PH_AO){ q = p + nor * reach; qn = min(nt, 1); dir = nor; }
    // the point of the cut face itself, for its colour ("how deep inside" wants the estimate the 2D view uses)
    else if (phase == PH_CUT){ q.z = uCut; qn = uInMode == 3 ? 3 : 0; }
    else if (flat2){
      // A volume sample for a 3D model is coloured by the rule of the 3D view. crawl counts its queries: the first
      // is made at the sample, the later ones (see RAW_OUT) on the way down to the surface and on it.
      qn = 3;
      if (ORBIT_SCENE && uRaw > 0.5){
        gFade = colourReach(pagePix);
#if RAW_FIT
        if (crawl == 4) q = p + tetra(n) * (RAW_SLOPE * uFlatH / uRes.y);
        else if (crawl == 1) q = p - nor * fit1; else if (crawl > 1) q = p - nor * lift;
        // The readings a trap solid's sample finds its surface with, and the one its colour comes from, are made in
        // the solid as the picture shows it (see RAW_SLOPE): the picture's pixel here is one of the page.
        if (rawTrap){ gPix = 2.0 * uFov * length(p - ro) / uPx; if (crawl != 3) gThinK = RAW_THIN; }
#endif
      }
#if RAW_FIT
      // The second query of a Kleinian sample: the search lands on the pearl the sample stands beside, as it does
      // for a hit in the picture, so the model has that pearl's colour. dOut is how far off the pearl is; the
      // division undoes what de() did to that length on the way back through the turning-out sphere.
      if (!ORBIT_SCENE && uRaw > 0.5 && crawl > 1) gLand = 1.05 * max(dOut, 0.0) / max(1.0 - max(dOut, 0.0) / max(length(p), 1e-6), 0.2) + 1e-6;
#endif
    } else if (phase == PH_FIT){
      if (ORBIT_SCENE && nt == 0){ qn = 1; dir = nor; }
      if (!fitFirst) q = p - nor * fit1;
    }
    else if (phase == PH_COLOUR){
      // the colour needs the orbit, not the distance (but with a trap solid, also which of the two was hit)
      if (!gInsideOut) qn = uTrapSolid > 0.5 ? min(nt, 1) : 0;
      if (colourFromTrap()){
        q = p - nor * lift;
        if (ORBIT_SCENE) gFade = colourReach(pagePix);
        else gLand = max(pix * t * uPx, 0.5 * e);
      }
    }
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
      float skip = gPowerLaw ? 0.5 * d - 1.4 * uMosaic : 0.0;
      empty = true; leave = max(leave, skip); d = max(skip, 4.0 * uMosaic);
    }
    cellKnown = false;
    if (phase == PH_PROBE){
      gInsideOut = gEsc < 0.5;
      // The single-number estimate only holds for a pure power plus c, and the march built on it only for the
      // set itself: a trap solid is made of thin shells, which it would step through.
      if (nt == 0 && (!gPowerLaw || uTrapSolid > 0.5)) nt = 1;
      vec2 sp = gInsideOut ? spanIn : spanOut;
      if (!flat2 && sp.y < sp.x){ phase = END_MISS; break; }
      t = sp.x; phase = flat2 ? PH_COLOUR : PH_MARCH;
      continue;
    }
    if (phase == PH_CUT){ phase = END_CUT; break; }
    if (phase == PH_FIT){
      // The estimate read "lift" at the hit and reads d a length fit1 further down: the straight line through the
      // two reaches zero at the surface. Held within sensible limits, in case the two do not belong together.
      if (fitFirst){ lift = d; crawl = 1; continue; }
#if RAW_FIT
      if (flat2){
        // A volume sample, which may lie a whole grid cell off the surface, inside or outside, so it takes two
        // readings: the same straight line as for a hit, then the line through the last two readings (ts and tIn,
        // which the march is not using here, hold the place and the value of the reading before).
        if (crawl == 1){
          float k = lift - d;
          k = k * lift > 0.2 * lift * lift ? lift / k : 5.0;
          ts = fit1; tIn = d; lift = fit1 * clamp(k, 0.5, 5.0); crawl = 2; continue;
        }
        float gap = abs(lift - ts), den = d - tIn;
        if (abs(den) > 1e-30) lift -= clamp(d * (lift - ts) / den, -gap, gap);
        crawl = 3; phase = PH_COLOUR; continue;
      }
#endif
      if (lift > 0.0) lift = fit1 * clamp(lift / max(lift - d, 0.2 * lift), 0.5, 5.0);
      phase = PH_COLOUR; continue;
    }
    if (phase == PH_COLOUR){
#if RAW_FIT
      // One of the four readings round a trap solid's sample (see RAW_SLOPE). After the fourth, lift holds the
      // estimate at the sample and nor four times the offset times its slope. The estimate of a trap solid is a
      // distance (not half of one, as beside the set), so the surface should lie the estimate divided by the slope
      // away: the next reading is made there, and the line through that reading and the one at the sample (ts and
      // tIn, as for any sample) gives the place the colour is read from. With no slope to follow, the colour is read
      // where the sample is, by the same rule.
      if (crawl == 4){
        nor += tetra(n) * d; lift += 0.25 * d; n++;
        if (n < 4) continue;
        n = 0;
        float steep = length(nor) / (4.0 * RAW_SLOPE * uFlatH / uRes.y);
        if (steep > 1e-6){ nor = normalize(nor); ts = 0.0; tIn = lift; lift *= clamp(1.0 / steep, 0.5, 5.0); crawl = 2; phase = PH_FIT; }
        else crawl = 3;
        continue;
      }
      // A volume sample beside the trap's part of a trap solid, whose colour comes from the trap: it starts the four
      // readings. dOut keeps the distance the sample itself read. (Not a sample that makes the cut face, see below.)
      if (ORBIT_SCENE && flat2 && uRaw > 0.5 && crawl == 0 && colourFromTrap() && gOnTrap
          && d < RAW_OUT * uFlatH / uRes.y && d > -RAW_IN * uFlatH / uRes.y
          && (d > 0.0 || !rawFace)){
        dOut = d; lift = 0.0; nor = vec3(0.0); n = 0; rawTrap = true; crawl = 4; continue;
      }
      // A volume sample near the surface whose colour comes from the trap: the colour is read from the surface
      // under (or over) the sample, as it is for a hit in the picture. dOut keeps the distance the sample itself read.
      // (Not a sample inside the solid in one of the two slices next to the cut plane: that one makes the cut face.)
      if (ORBIT_SCENE && flat2 && uRaw > 0.5 && crawl == 0 && colourFromTrap() && dot(gGrad, gGrad) > 0.0
          && d < RAW_OUT * uFlatH / uRes.y && d > -RAW_IN * uFlatH / uRes.y
          && (d > 0.0 || !rawFace)){
        dOut = d; lift = d; nor = normalize(gGrad); crawl = 1; phase = PH_FIT; continue;
      }
      // A Kleinian sample near a pearl. Its estimate is the true distance, so nothing has to be fitted: one more
      // query at the same place, in which the search lands on that pearl (see gLand above), gives the colour.
      if (!ORBIT_SCENE && flat2 && uRaw > 0.5 && crawl == 0 && colourFromTrap()
          && d < RAW_OUT * uFlatH / uRes.y && d > -RAW_IN * uFlatH / uRes.y
          && (d > 0.0 || !rawFace)){
        dOut = d; crawl = 3; continue;
      }
#endif
      phase = flat2 ? END_FLAT : END_LIT; break;
    }
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
        // With neighbouring orbits the drawn surface is where the estimate reads LEVEL pixels, so that thin
        // parts keep some body. A ray is not left at the first step that happens to fall under that level:
        // rays side by side would stop up to a stride apart, and the light and shadow taken from there would
        // come out as bands, like a stack of slices. Every hit is brought onto the level instead.
        if (!rough) d -= LEVEL * e;
        float ahead = 1e9;
        if (rough) ahead = dOut > d && dOut < 4.0 * d ? d * (t - tOut) / (dOut - d) : 1e9;
        bool conv = false, near = false;
        if (tIn >= 0.0 || (d < 0.0 && dOut > 0.0)){
          // The ray has stepped over the surface: it lies between tOut, the last point outside, and tIn,
          // the nearest point inside. The estimates either side are wrong by about the same factor, so
          // try where the straight line between them crosses zero, or halve the gap when that is not known.
          near = true;
          if (!rough && tIn < 0.0 && gEsc > 0.5){
            // under the level but not in the solid: slide back to where the straight line between the two
            // estimates crosses the level, which costs no further query
            t = tOut + (t - tOut) * clamp(dOut / (dOut - d), 0.0, 1.0); conv = true; d = 0.0;
          } else {
            conv = !rough && abs(d) < 0.15 * e;   // on the level already
            if (!conv){
              if (d < 0.0){ tIn = t; t = tOut + (t - tOut) * clamp(dOut / (dOut - d), 0.1, 0.9); }
              else { tOut = t; dOut = d; t = 0.5 * (tOut + tIn); }
              // Closed in to half a pixel. With neighbouring orbits the hit is the outside end, so that it is
              // coloured from an orbit that leaves, like every other hit on the level.
              if (tIn - tOut < 0.5 * e){ conv = true; if (!rough){ t = tOut; d = dOut; } }
            }
          }
        } else if (d < (rough ? 0.0 : (1.0 - LEVEL) * e) || (rough && ahead < e)) conv = true;
        else {
          float stride = (rough ? d : d + LEVEL * e) * uStepK;
          if (rough){
            // Stride toward where the surface seems to be, within limits either way: shorter when the estimate
            // is falling faster than the ray advances (it reads too long there), longer when it reads too
            // short, but not so long as to jump a thin sheet. No lengthening where the picture is mostly thin
            // sheets (inside-out solids) or changes abruptly (mosaic cell walls).
            float longest = mosaic || gInsideOut ? 1.0 : d < 2.0 * e ? 8.0 : 3.0;
            if (ahead < 1e8) stride = clamp(0.9 * ahead, 0.3 * stride, longest * stride);
            // A ray that runs alongside the solid reads a tiny distance at every step and would use up all its
            // steps without getting past. Each stride in a row that is held at the least stride lets the
            // next one be longer, though never past the point where the surface seems to be.
            float least = 0.5 * e * (1.0 + 0.25 * float(crawl));
            if (stride < least){ stride = min(least, max(0.9 * ahead, 0.5 * e)); crawl++; } else crawl = 0;
            near = ahead < 8.0 * e;
          } else near = d < 3.0 * e;
          // a stride that ends in the next mosaic cell starts afresh there: the two estimates do not belong together
          tOut = t; dOut = empty || stride > leave ? 0.0 : d; t += empty ? leave : min(stride, leave);
        }
        if (!conv && t <= tMax && n < uSteps) continue;
        // A ray that is out of steps has hit only if the surface is within a few pixels of where it stopped.
        // Anywhere else it shows the background: shading thin air draws a glow around the solid.
        if (t > tMax || (!conv && (empty || !near))){ phase = END_MISS; break; }
        if (picking){ phase = END_CUT; break; }
        if (gId > 0.5){
          // the cut face: hatched, unless it is to be coloured, which takes one more query (PH_CUT)
#if COL_INSIDE
          if (uCutFace > 0.5){ phase = PH_CUT; continue; }
#endif
          phase = END_CUT; break;
        }
        n = 0;
        // How high above the solid the ray has stopped: on the level, give or take what is left in d. (A ray that
        // ran out of steps has moved on since its last reading, and the fastest estimate is gauged by the slope
        // samples that follow.)
        lift = rough ? 0.0 : LEVEL * e + (conv ? clamp(d, -e, e) : 0.0);
        // The fastest estimate stops a ray anywhere within half a pixel of the surface, often inside, where
        // nothing says how deep. For a trap colour the hit is the last point outside instead, and PH_FIT starts
        // there (crawl, which the march is done with, counts its readings).
        crawl = 0;
        if (rough && hue == PH_FIT && tIn >= 0.0) t = tOut;
        // the set's own slope says nothing about a trap solid, so with one in the picture the slope is sampled
        if (uAnalytic < 0.5 || nt != 3 || gInsideOut || uTrapSolid > 0.5){ phase = PH_SLOPE; continue; }
        nor = gGrad; settle = true;
      } else if (phase == PH_SHADOW){
        res = min(res, 10.0 * d / ts); n++;
        if (res >= 0.005 && ts <= 5.0 && n < uShSteps){ ts += empty ? leave : min(clamp(d, 2.0 * e, 0.35), leave); continue; }
        n = 0; phase = uAO > 0.5 ? PH_AO : hue;
      } else {
        ao += pow(0.7, float(n)) * clamp(1.0 - 1.6 * d / reach, 0.0, 1.0); n++;
        if (n == 4) phase = hue;
      }
    }
    if (settle){
      nor = dot(nor, nor) > 0.0 ? normalize(nor) : -rd;
      if (dot(nor, rd) > 0.0) nor = normalize(nor - 1.05 * dot(nor, rd) * rd);
      n = 0; ts = 4.0 * e;
      phase = uShadow > 0.5 && dot(nor, L) > 0.001 ? PH_SHADOW : uAO > 0.5 ? PH_AO : hue;
    }
  }
  vec3 col = uBg, p = ro + rd * t;
  if (picking){ o = phase == END_CUT ? vec4(p, 1.0) : vec4(0.0); return; }
  // Volume sampling (the 3D model) wants the unlit surface colour of the slice point and the signed distance
  // estimate, nothing else: it is coloured as a hit.
  bool raw = phase == END_FLAT && uRaw > 0.5, flatPix = phase == END_FLAT && !raw, hit = phase == END_LIT || raw;
#if RAW_FIT
  // a volume sample whose colour was read from the surface (crawl > 0) hands back the distance it read itself
  if (raw && crawl > 0) d = dOut;
#endif
  if (phase == END_FLAT && gInsideOut && length(slicePoint) > farLimit){ gEsc = 1.0; d = max(d, length(slicePoint) - farLimit); }
#if RAW_FIT
  if (raw){ p = slicePoint; if (crawl == 0) nor = dot(gGrad, gGrad) > 0.0 ? normalize(gGrad) : vec3(0.0, 0.0, 1.0); t = 0.0; }
  // (a trap solid's sample is coloured as the point of the surface it found: with no steps skipped the colour module
  // asks whether that point touches the trap shape itself)
  if (raw && rawTrap) p -= nor * lift;
  // A volume sample well inside the solid comes to light only where the model is cut open (at the cut plane, or at
  // the wall of the grid), so it is coloured as the picture colours the cut face: the hatching, evened out, or the
  // inside colouring when the cut face is painted.
  bool rawCut = raw && crawl == 0 && gEsc < 0.5 && (d < -RAW_IN * uFlatH / uRes.y || (d <= 0.0 && rawFace));
  if (rawCut) hit = false;
#else
  if (raw){ p = slicePoint; nor = dot(gGrad, gGrad) > 0.0 ? normalize(gGrad) : vec3(0.0, 0.0, 1.0); t = 0.0; }
  const bool rawCut = false;
#endif
  if (flatPix || hit || rawCut || phase == END_CUT){
    // A slice pixel, a hit or the cut face: one call colours them all, because every call from here is one more
    // copy of the whole colour code for the compiler to work through (three calls took four times as long to
    // prepare). The last query was made at the very point being coloured, so the colour hooks read live values.
    // The cut face is hatched the way a section drawing marks cut material, unless the colour module paints it.
    float s = abs(fract((gl_FragCoord.x + gl_FragCoord.y) / (8.0 * uPx)) - 0.5);
    colourCapture();
    vec3 alb = pixelColour(flatPix ? COL_FLAT : hit ? COL_HIT : COL_CUT, flatPix ? slicePoint : phase == END_CUT ? vec3(p.xy, uCut) : p,
      nor, t, d, uFlatH / uRes.y, mix(uCutCol, uCutInk, raw ? RAW_HATCH : 0.55 * smoothstep(0.36, 0.42, s)));
    if (raw){ o = vec4(alb, d); return; }
    col = alb;
    // In the mosaic the colours around every small set would repeat from cell to cell like wallpaper and drown
    // the shapes. Each set keeps a halo of its colours, and beyond that the plain stage shows.
    if (flatPix && mosaic) col = mix(col, uBg, gEsc * smoothstep(0.02, 0.2, d / uMosaic));
    if (hit && colourUnlit() < 0.5){
      float dif = clamp(dot(nor, L), 0.0, 1.0), sh = clamp(res, 0.0, 1.0), occ = clamp(1.0 - 0.45 * ao, 0.0, 1.0);
      sh = sh * sh * (3.0 - 2.0 * sh);
      float sky = 0.5 + 0.5 * nor.z;
      float bac = clamp(0.3 + 0.7 * dot(nor, normalize(vec3(-L.x, -L.y, 0.3))), 0.0, 1.0);
      float fre = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 3.0);
      float spe = pow(clamp(dot(nor, normalize(L - rd)), 0.0, 1.0), 40.0) * dif * sh;
      vec3 lig = 1.45 * dif * sh * vec3(1.00, 0.94, 0.84) + occ * (0.42 * sky * vec3(0.50, 0.62, 0.80) + 0.20 * bac * vec3(0.80, 0.70, 0.58));
      col = alb * lig + 0.16 * spe + 0.06 * fre * occ * alb;
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
