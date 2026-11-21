// ---------- Balls on balls: the second group of the Kleinian view (round 27).
// Not an approach and not a rule "square, then add c": a picture made only of slides by whole numbers and sphere
// inversions. Its state is four numbers in S.k: group (0 the group that was always there, 1 this one), bt (the dial
// t >= 1), bgrid (0 square grid, 1 honeycomb grid, 2 a line only) and bit (rounds of the recipe).
//
// The recipe, in the object's own coordinates m, as out/r25/klein/tree.py has it:
//   repeat: if m.z < 0 or m.z > 2t: INSIDE. Slide (m.x, m.y) by the nearest whole number of the grid.
//           If |m| < 1: m -> m / |m|^2. Else if |m - (0, 0, 2t)| < 1: the same about (0, 0, 2t). Else: OUTSIDE.
//   A point that is still undecided when the rounds run out counts as INSIDE.
// One sphere inversion at the start (centre (0, 0, 1) in m, radius k, k^2 = 1.05) brings the picture into the lab's
// frame: picture x along the chain, picture y up in the flat plane, picture z out of the flat plane.
const BALLS_K2 = 1.05, BALLS_T = 1.4, BALLS_ROUNDS = 16, BALLS_S3 = Math.sqrt(3);
const BALLS_NAME = 'Balls on balls', BALLS_TAG = 'a cousin of the flat picture: no c, no power';
const BALLS_GRIDS = [[0, 'Square grid (four-fold)'], [1, 'Honeycomb grid (six-fold)'], [2, 'A line only (buds only round the flat picture)']];
const BALLS_NOTE = 'Made only of slides by whole numbers and sphere inversions, so every body is an exact ball. It is a cousin of the flat picture: its flat cut is a chain of circles. It has no c and no power.';
const ballsOn = () => S.k.group === 1;                 // this group is the one the Kleinian view holds
const ballsShown = () => S.mode === 'k' && ballsOn();  // and it is on show
const ballsGridId = g => (g === 1 || g === 'hex' || g === 'eisen' ? 1 : g === 2 || g === 'line' ? 2 : 0);
// The dial shows t the way the eye meets it: the width of the two big neighbours as a share of the middle ball.
const ballsShare = t => 100 / (2 * t - 1);
const ballsFromShare = p => (Math.abs(p - ballsShare(BALLS_T)) < 0.06 ? BALLS_T : Math.max(1, 0.5 * (100 / Math.max(p, 1e-6) + 1)));
// How far the chain reaches from the middle of the picture, along x (Infinity at t = 1: the chain never ends).
const ballsReach = (t = S.k.bt) => (t > 1 ? BALLS_K2 / (t + Math.sqrt(t * t - 1) - 1) + BALLS_K2 / 2 : Infinity);

// The slide: the whole number of the grid nearest to (x, y), as [a, b] to take away.
function ballsNearest(grid, x, y) {
  if (grid === 2) return [Math.round(x), 0];
  if (grid === 0) return [Math.round(x), Math.round(y)];
  const b0 = Math.round(y / (BALLS_S3 / 2));
  let best = null, bd = Infinity;
  for (let j = -1; j <= 1; j++) {
    const b = b0 + j, a = Math.round(x + b / 2), px = a - b / 2, py = b * BALLS_S3 / 2, d = (x - px) * (x - px) + (y - py) * (y - py);
    if (d < bd) { bd = d; best = [px, py]; }
  }
  return best;
}
// The inside test, in JavaScript: the twin of the shader and of tree.py. Picture coordinates.
// opts = { t, grid ('square' | 'hex' | 'line', or 0 | 1 | 2), rounds }; what is left out is read from the page.
function ballsInside(x, y, z, opts) {
  const o = opts || {}, t = o.t === undefined ? S.k.bt : +o.t, grid = ballsGridId(o.grid === undefined ? S.k.bgrid : o.grid);
  const rounds = o.rounds === undefined ? S.k.bit : Math.round(o.rounds), top = 2 * t;
  const ux = y, uy = z, uz = x - BALLS_K2 / 2;
  let d = ux * ux + uy * uy + uz * uz;
  if (!(d > 0)) d = 1e-300;
  let mx = BALLS_K2 * ux / d, my = BALLS_K2 * uy / d, mz = 1 + BALLS_K2 * uz / d;
  for (let i = 0; i < rounds; i++) {
    if (mz < 0 || mz > top) return true;
    const n = ballsNearest(grid, mx, my);
    mx -= n[0]; my -= n[1];
    const rb = mx * mx + my * my + mz * mz, rt = mx * mx + my * my + (mz - top) * (mz - top);
    if (rb < 1) { const s = 1 / (rb > 0 ? rb : 1); mx *= s; my *= s; mz *= s; }
    else if (rt < 1) { const s = 1 / (rt > 0 ? rt : 1); mx *= s; my *= s; mz = top + (mz - top) * s; }
    else return false;
  }
  return true;
}
// The distance the shader hands the ray marcher, in JavaScript (the part that does not depend on the picture: see
// "free" in GL_BALLS). Negative inside a ball. For the checks. With opts.parts it returns both numbers the estimate is the
// smaller of: [the true distance to the nearest ball the search met, the length that is certainly free of balls].
function ballsEstimate(x, y, z, opts) {
  const o = opts || {}, t = o.t === undefined ? S.k.bt : +o.t, grid = ballsGridId(o.grid === undefined ? S.k.bgrid : o.grid);
  const rounds = o.rounds === undefined ? S.k.bit : Math.round(o.rounds), top = 2 * t, H = t - Math.sqrt(Math.max(t * t - 1, 0));
  const rest = grid === 0 ? H / 2 : grid === 1 ? H / 3 : H / 4;
  const pearl = (h, D, kk) => (h > 0 ? 2 * h / (1 + Math.sqrt(1 + kk * h * Math.max(D, 0))) : h);
  const u = [y, z, x - BALLS_K2 / 2], d2 = Math.max(dot(u, u), 1e-300);
  let DF = BALLS_K2 / d2, m = [DF * u[0], DF * u[1], 1 + DF * u[2]], W = [0, 0, 1], best = 1e9;
  for (let i = 0; i < rounds; i++) {
    const n = ballsNearest(grid, m[0], m[1]);
    m[0] -= n[0]; m[1] -= n[1]; W[0] -= n[0]; W[1] -= n[1];
    const L2 = Math.max(dot(sub(m, W), sub(m, W)), 1e-300), kk = 4 / L2, hb = m[2], ht = top - m[2];
    const cand = Math.min(pearl(hb, W[2], kk), pearl(ht, top - W[2], kk)) / DF;
    best = Math.min(best, cand);
    if (hb < 0 || ht < 0) return o.parts ? [best, best] : best;
    const mt = [m[0], m[1], m[2] - top], rb = dot(m, m), rt = dot(mt, mt);
    if (rb < 1) { const s = 1 / Math.max(rb, 1e-300); m = scl(m, s); W = scl(W, 1 / Math.max(dot(W, W), 1e-300)); DF *= s; }
    else if (rt < 1) {
      const s = 1 / Math.max(rt, 1e-300), Wt = [W[0], W[1], W[2] - top], w = 1 / Math.max(dot(Wt, Wt), 1e-300);
      m = [mt[0] * s, mt[1] * s, top + mt[2] * s]; W = [Wt[0] * w, Wt[1] * w, top + Wt[2] * w]; DF *= s;
    } else {
      const cb = Math.hypot(m[0], m[1], hb - H / 2) - H / 2, ct = Math.hypot(m[0], m[1], ht - H / 2) - H / 2;
      const lo = grid === 2 ? Math.hypot(m[1], hb) : hb, hi = grid === 2 ? Math.hypot(m[1], ht) : ht;
      const e = Math.max(Math.min(cb, ct, Math.min(lo, hi) - rest), 0), L = Math.sqrt(L2);
      const free = e * L / ((L + e) * DF);
      return o.parts ? [best, free] : Math.min(best, free);
    }
  }
  return o.parts ? [-1e-7, -1e-7] : -1e-7;
}
// The start view: the whole chain in the picture, seen from a little above the flat plane so that the buds off the
// flat picture show. { yaw, pitch, dist (at the starting field of view), h (span of the 2D view), room }.
function ballsCam() {
  const r = Math.min(ballsReach(), 4.5), w = Math.max(1, stage.clientWidth), h = Math.max(1, stage.clientHeight), asp = w / h;
  return { yaw: -1.25, pitch: 0.5, dist: Math.max(3.3, 3.6 * r / asp), h: Math.max(2.1, 2.25 * r / asp), room: Math.min(r + 0.4, 8) };
}
// "Frame it", and what the row in the Approach list does to the camera: the start view, with a zoom limit or a
// drawing radius that is in the way moved (a promise to show the whole thing, like the other Frame buttons).
function ballsFrame() {
  const b = ballsCam();
  presetRoom(presetDist(b.dist, 1), b.room);
  if (S.v2.hmax < b.h) S.v2.hmax = b.h;
  resetCam();
  touch();
}
// What is wrong with the picture as the dials stand, in one plain sentence, or ''.
function ballsTrouble() {
  if (!ballsShown() || S.flat) return '';
  return ballsReach() > S.view.bound ? 'The chain of balls runs out past the Drawing radius in the View section, so its far ends are not drawn.' : '';
}

// The scene program of this group. Same interface towards GL_HEAD, GL_COLOUR and GL_TAIL as GL_KLEIN: de() sets
// gEsc, gIt, gLast, gGrad and gOnTrap, feeds the colour trap (trapStart, trapAdd) and keeps the touch record of a
// trap solid (gTouch, gTouchIt, gTouchS, gTouchStr). Its two uniforms are declared here, so no other program
// changes: uBT = t, uBGrid = the grid.
//
// The distance. Every ball of the picture is the sphere that some chain of the moves carries onto one of the two
// walls (m.z = 0 and m.z = 2t). The search follows ONE chain, the recipe's. For each wall it meets, kpearl gives the
// TRUE distance to that ball (see GL_KLEIN: h is how far the mapped point stands from the wall, D the same for W,
// the image of the point at infinity, kk = 4 / |m - W|^2; DF is the scale factor of the maps so far, the frame
// inversion included).
// But the nearest ball need not be on that chain: next to every ball stand buds of every size that the recipe never
// visits from this point. So when the recipe ends OUTSIDE, the place it ends at is used for a second number, "free":
// a length inside which there is certainly no ball at all. There (m in the middle of its cell, outside both unit
// spheres) every ball other than the two walls lies inside
//   the ball of diameter H = t - sqrt(t^2 - 1) that stands on the wall at the nearest whole number (the first bud
//   and everything that grows on it; one on each wall), or
//   within H / 2 of a wall (square grid; H / 3 honeycomb; a tube of radius H / 4 round the line for the line grid):
//   the buds at the fractions that are not whole numbers.
// (The heights: a bud at the fraction p / q is 1 / |q|^2 the size of the one at a whole number, and the highest any
// growth on the bottom wall reaches is H, because H = 1 / (2t - H).) With e the distance from m to all of that, the
// ball of radius e round m is empty, and carried back to the picture it leaves a ball of radius
// e L / ((L + e) DF) round the point, L = |m - W|: an exact statement about sphere inversions, not a first-order one.
// The estimate is the smaller of the two numbers, so it is never longer than the true distance to the nearest ball.
// One exception, in the 3D picture only (gPix > 0): "free" is not taken below two ray thresholds. It measures to
// hulls, not to balls, so close in it would stop every ray a few pixels short and roughen the slope; there the ray
// goes on in steps of about a pixel and is stopped by the exact distances, or by landing inside a ball (the inside
// test is exact at every size). In the 2D view and for a 3D model (gPix = 0) nothing is held up.
const GL_BALLS = `
const bool ORBIT_SCENE = false;
uniform float uBT; uniform int uBGrid;
const float BALLS_K2 = ${BALLS_K2.toFixed(4)};
float kpearl(float h, float D, float kk){ return h > 0.0 ? 2.0 * h / (1.0 + sqrt(1.0 + kk * h * max(D, 0.0))) : h; }
// the whole number of the grid nearest to q (what the slide takes away)
vec2 bnear(vec2 q){
  if (uBGrid == 2) return vec2(floor(q.x + 0.5), 0.0);
  if (uBGrid == 0) return floor(q + 0.5);
  float b0 = floor(q.y / 0.8660254038 + 0.5), bd = 1e30;
  vec2 best = vec2(0.0);
  for (int j = -1; j <= 1; j++){
    float b = b0 + float(j), a = floor(q.x + 0.5 * b + 0.5);
    vec2 s = vec2(a - 0.5 * b, 0.8660254038 * b), w = q - s;
    float d = dot(w, w);
    if (d < bd){ bd = d; best = s; }
  }
  return best;
}
float de(vec3 p, int nt, vec3 dir){
  gEsc = 1.0; gGrad = vec3(0.0, 0.0, 1.0); gOnTrap = false;
  float top = 2.0 * uBT, H = uBT - sqrt(max(uBT * uBT - 1.0, 0.0));
  float rest = uBGrid == 0 ? 0.5 * H : uBGrid == 1 ? H / 3.0 : 0.25 * H;
  // the frame: one sphere inversion about (k^2 / 2, 0, 0), which is the point (0, 0, 1) of the object's own space
  vec3 u = vec3(p.y, p.z, p.x - 0.5 * BALLS_K2);
  float DF = BALLS_K2 / max(dot(u, u), 1e-20), it = 0.0, best = 1e9, free = 0.0;
  vec3 z = vec3(0.0, 0.0, 1.0) + DF * u, W = vec3(0.0, 0.0, 1.0);
  // The landing length (see gLand in GL_HEAD); none while the trap alone is the solid, because then the balls are
  // not in the picture. The distances here are lengths of the picture already, so it is used as it comes.
  bool walls = uTrapSolid < 0.5 || uTrapSolid > 1.5, inside = false, decided = false;
  float land = walls ? gLand : 0.0;
  trapStart();
#if TRAP_SOLIDS
  bool trapSolid = uTrapSolid > 0.5;
  float bestT = 1e9;
#endif
  for (int i = 0; i < uIter; i++){
    vec2 n = bnear(z.xy);
    z.xy -= n; W.xy -= n;
    // the point as the trap sees it: x along the chain (0 half-way between the walls), z out of the flat plane
    vec3 zw = z - W, tv = vec3(z.z - uBT, z.x, z.y);
    float L2 = max(dot(zw, zw), 1e-30), kk = 4.0 / L2, hb = z.z, ht = top - z.z;
    float cand = min(kpearl(hb, W.z, kk), kpearl(ht, top - W.z, kk)) / DF;
    best = min(best, cand); it = float(i);
    // The trap as a solid: every point whose chain, from round uTrapSkip on, comes within uTrapW of the trap shape.
    // The length is carried back to the picture the way "free" is.
#if TRAP_SOLIDS
    if (trapSolid && i >= uTrapSkip){
      float dq = trapDist(tv), et = dq - uTrapW, L = sqrt(L2);
      float sc = (et > 0.0 ? et * L / (L + et) : et) / DF;
      if (sc < bestT){ bestT = sc; gTouch = vec4(tv - uTrapC, dq); gTouchIt = it; gTouchS = sc; gTouchStr = DF; }
    }
#endif
    // a hit's trap colour: the search is over at the first round that lands within the landing length of a ball,
    // and that point is fed to the trap as a point of the wall itself
    bool landed = land > 0.0 && cand < land;
    if (landed){ tv.x = hb < ht ? -uBT : uBT; free = 1e9; }
    trapAdd(tv, it); gLast = tv;
    if (landed || hb < 0.0 || ht < 0.0){ inside = hb < 0.0 || ht < 0.0; decided = true; break; }
    vec3 zt = vec3(z.xy, z.z - top);
    float rb = dot(z, z), rt = dot(zt, zt);
    if (rb < 1.0){
      float s = 1.0 / max(rb, 1e-20);
      z *= s; W /= max(dot(W, W), 1e-20); DF *= s;
    } else if (rt < 1.0){
      float s = 1.0 / max(rt, 1e-20);
      vec3 Wt = vec3(W.xy, W.z - top);
      z = vec3(0.0, 0.0, top) + zt * s; W = vec3(0.0, 0.0, top) + Wt / max(dot(Wt, Wt), 1e-20); DF *= s;
    } else {
      // OUTSIDE, for good. How much room is certain here (see the top of this program).
      float cb = length(vec3(z.xy, hb - 0.5 * H)) - 0.5 * H, ct = length(vec3(z.xy, ht - 0.5 * H)) - 0.5 * H;
      float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
      float e = max(min(min(cb, ct), min(lo, hi) - rest), 0.0), L = sqrt(L2);
      free = e * L / ((L + e) * DF);
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // undecided when the rounds ran out: that counts as inside, a hair deep
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, 2.0 * uDetail * gPix));
  // The trap solid takes the place of the balls (1) or joins them (2: whichever surface is nearer).
  // THE PAGE DOES NOT USE THIS: for this group the colour module never asks for a trap solid (colBalls in
  // 25-colour.js), so this program is always built with TRAP_SOLIDS 0. Tried and put away in round 27: the trap is
  // met inside one cell of the grid, so any trap wider than the cell comes out cut open along the cell's flat
  // faces, and a trap near the point (0, 0, 1), which is the far distance of the picture, grows past the camera.
  // The cap keeps a ray from leaping when no round was tested (a far point is OUTSIDE at once).
#if TRAP_SOLIDS
  if (trapSolid && uTrapSolid < 1.5) bestT = min(bestT, gPix > 0.0 ? max(abs(d), 2.0 * uDetail * gPix) : 0.3);
  gOnTrap = trapSolid && (uTrapSolid < 1.5 || bestT < d);
  if (gOnTrap) d = bestT;
#endif
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
