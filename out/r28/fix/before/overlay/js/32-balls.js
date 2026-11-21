// ---------- Balls on balls: the second group of the Kleinian view (round 27; round 28: the second sphere's size).
// Not an approach and not a rule "square, then add c": a picture made only of slides by whole numbers and sphere
// inversions. Its state is five numbers in S.k: group (0 the group that was always there, 1 this one), bt (the dial
// t = top / 2), brho (the radius of the second sphere: 1, or 0.02 to 0.5), bgrid (0 square grid, 1 honeycomb grid,
// 2 a line only) and bit (rounds of the recipe).
//
// The recipe, in the object's own coordinates m, with top = 2t and rho = brho (rho = 1 is out/r25/klein/tree.py):
//   repeat: if m.z < 0 or m.z > top: INSIDE. Slide (m.x, m.y) by the nearest whole number of the grid.
//           If |m| < 1: m -> m / |m|^2                              (the first sphere: radius 1 about (0, 0, 0)).
//           Else if |m - (0, 0, top)| < rho: m -> (0, 0, top) + rho^2 (m - (0, 0, top)) / |m - (0, 0, top)|^2
//                                                                   (the second sphere: radius rho about (0, 0, top)).
//           Else: OUTSIDE.
//   A point that is still undecided when the rounds run out counts as INSIDE.
// One sphere inversion at the start (centre (0, 0, 1) in m, radius k, k^2 = 1.05) brings the picture into the lab's
// frame: picture x along the chain, picture y up in the flat plane, picture z out of the flat plane. The middle ball
// is k^2 wide and its two big neighbours k^2 / (top - 1), whatever rho is: the dial "Size of the neighbours" shows
// p = 100 / (top - 1). The first sphere is the mirror x -> -x of the picture, so the picture is always its own
// mirror image left to right.
// The two spheres touch at top = 1 + rho, that is at p = 100 / rho, and must not cut into each other. It is an object
// (no two balls cut into each other) when rho = 1 and p <= 100 (round 27), or when rho <= 1/2 and p rho <= 100
// (round 28: the copies of the second sphere at neighbouring whole numbers must not cut into each other either).
// Between 1/2 and 1 only single values of rho work, and the dial does not offer them. So with two equal spheres the
// neighbours are never larger than the middle ball, and with a second sphere half the size they go up to twice it.
const BALLS_K2 = 1.05, BALLS_T = 1.4, BALLS_ROUNDS = 16, BALLS_ROUNDS_MIN = 1, BALLS_ROUNDS_FEW = 5, BALLS_S3 = Math.sqrt(3);
const BALLS_RHO_MIN = 0.02, BALLS_RHO_MAX = 0.5;   // the second sphere is as large as the first (1) or between these two
const BALLS_NAME = 'Balls on balls', BALLS_TAG = 'a cousin of the flat picture: no c, no power';
const BALLS_GRIDS = [[0, 'Square grid (four-fold)'], [1, 'Honeycomb grid (six-fold)'], [2, 'A line only (buds only round the flat picture)']];
const BALLS_NOTE = 'Made only of slides by whole numbers and sphere inversions, so every body is an exact ball. It is a cousin of the flat picture: its flat cut is a chain of circles. It has no c and no power.';
const ballsOn = () => S.k.group === 1;                 // this group is the one the Kleinian view holds
const ballsShown = () => S.mode === 'k' && ballsOn();  // and it is on show
const ballsGridId = g => (g === 1 || g === 'hex' || g === 'eisen' ? 1 : g === 2 || g === 'line' ? 2 : 0);
// The second sphere's radius as the programs use it: 1 (also for a state that holds nothing), or a number below 1.
const ballsRho = (r = S.k.brho) => (+r < 1 ? Math.max(BALLS_RHO_MIN, +r) : 1);
// t as the programs use it: the two spheres may touch, never cut into each other. (rho = 1: t >= 1, as it always was.)
const ballsT = (t = S.k.bt, rho = ballsRho()) => Math.max((1 + rho) / 2, +t || 1);
// The two spheres touch: the chain never ends.
const ballsTouch = (t = S.k.bt, rho = ballsRho()) => (rho === 1 ? !(t > 1) : !(2 * t - 1 - rho > 1e-9));
// The dial shows t the way the eye meets it: the width of the two big neighbours as a share of the middle ball.
const ballsShare = t => 100 / (2 * t - 1);
const ballsFromShare = (p, rho = ballsRho()) => (Math.abs(p - ballsShare(BALLS_T)) < 0.06 ? BALLS_T : Math.max((1 + rho) / 2, 0.5 * (100 / Math.max(p, 1e-6) + 1)));
// The dial "Second sphere" shows 100 rho. The value it takes for one that is asked for: 2 to 50, or 100; anything
// between 50 and 100 goes to the nearer of the two (75 and below: 50), because there the buds on a neighbour would
// cut into each other.
const ballsRhoShown = () => +(100 * ballsRho()).toFixed(2);
const ballsRhoFrom = v => (v > 75 ? 1 : Math.min(BALLS_RHO_MAX, Math.max(BALLS_RHO_MIN, v / 100)));
// The two dials give way to each other, and the one the user moved wins (docs/ROUND28.md, 1.2, point 4).
// Size set to p: where the two spheres would cut into each other (p rho > 100) the second sphere becomes 50 / p of
// the first, and never more than half of it. From then on it FOLLOWS the size as min(1/2, 50 / p), which is half-way
// to touching: so dragging the size past 100 simply works, the chain keeps its two ends and the picture changes
// evenly. It follows until the user sets the second sphere by its own dial; a value set there stays as it is until
// the size would make the two spheres cut into each other again. Coming back below 100 does not put the second
// sphere back to 100 (it stays at 50): "Reset this section" does, and a sentence says what it is (ballsTrouble).
// (BALLS_DIAL.follows: the second sphere was last set by the size dial. It only says who moved last, so it is kept
//  here and not in the state S. Without it the rule would be the bare "only where p rho > 100": then, dragged from
//  100 to 400, the second sphere would stand still while the chain grew endless at about 200, and jump there.)
const BALLS_DIAL = { follows: false };
function ballsSetShare(p) {
  let rho = ballsRho();
  if (p * rho > 100 * (1 + 1e-9) || (BALLS_DIAL.follows && rho < 1)) { rho = Math.max(BALLS_RHO_MIN, Math.min(BALLS_RHO_MAX, 50 / p)); BALLS_DIAL.follows = true; }
  S.k.brho = rho; S.k.bt = ballsFromShare(p, rho);
}
// Second sphere set to v % of the first: where the two would cut into each other the neighbours become 50 / rho % of
// the middle ball (t = rho + 1/2; so back to 100 gives neighbours of 50).
function ballsSetRho(v) {
  const rho = ballsRhoFrom(v), cut = ballsShare(ballsT(S.k.bt, ballsRho())) * rho > 100 * (1 + 1e-9);
  S.k.brho = rho; S.k.bt = cut ? rho + 0.5 : ballsT(S.k.bt, rho);
  BALLS_DIAL.follows = false;
}
// The numbers the distance is made from (see GL_BALLS for rho = 1 and GL_BALLS_RHO for a smaller second sphere):
// HB, HT the two hull balls; the spindle's circle (centre (a, zm), radius R, d2 = R^2 - a^2) and whether it is used;
// end = z2 - 1, where z2 is the upper of the two fixed points on the middle line (0 when the spheres touch).
function ballsHulls(t, rho) {
  if (rho === 1) { const H = t - Math.sqrt(Math.max(t * t - 1, 0)), s2 = t * t - 1; return { HB: H, HT: H, zm: t, d2: s2, a: 0.25 - s2, R: 0.25 + s2, on: t < BALLS_SPINDLE_T, end: t + Math.sqrt(Math.max(s2, 0)) - 1 }; }
  // (written so that nothing large is taken from something large: D = s - 2, which is 0 when the spheres touch)
  const top = 2 * t, gap = Math.max(top - 1 - rho, 0), D = gap * (top - 1 + rho) / top, sq = Math.sqrt(D * (D + 4));
  const HB = 1 / (1 + 0.5 * (D + sq)), HT = rho * rho / (top - HB), zm = 1 + 0.5 * D, d2 = 0.25 * D * (D + 4), w = Math.min(0.5, top - zm + rho);
  return { HB, HT, zm, d2, a: (w * w - d2) / (2 * w), R: (w * w + d2) / (2 * w), on: d2 < 3, end: 0.5 * (D + sq) };
}
// How far the chain reaches from the middle of the picture, along x (Infinity where the two spheres touch: the chain
// never ends). The chain runs out at the two fixed points on the middle line, which the frame carries to x = +-reach.
function ballsReach(t = S.k.bt, rho = ballsRho()) {
  if (rho === 1) return t > 1 ? BALLS_K2 / (t + Math.sqrt(t * t - 1) - 1) + BALLS_K2 / 2 : Infinity;
  return ballsTouch(t, rho) ? Infinity : BALLS_K2 / ballsHulls(ballsT(t, rho), rho).end + BALLS_K2 / 2;
}

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
// The inside test, in JavaScript: the twin of the shader (and, for rho = 1, of tree.py). Picture coordinates.
// opts = { t, grid ('square' | 'hex' | 'line', or 0 | 1 | 2), rounds, rho }; what is left out is read from the page.
// (rho given here is used as it comes, also a value the dial does not offer: the checks show with it why not.)
function ballsInside(x, y, z, opts) {
  const o = opts || {}, t = o.t === undefined ? S.k.bt : +o.t, grid = ballsGridId(o.grid === undefined ? S.k.bgrid : o.grid);
  const rounds = o.rounds === undefined ? S.k.bit : Math.round(o.rounds), top = 2 * t;
  const rho = o.rho === undefined ? ballsRho() : +o.rho, r2 = rho * rho;
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
    else if (rt < r2) { const s = r2 / (rt > 0 ? rt : 1); mx *= s; my *= s; mz = top + (mz - top) * s; }
    else return false;
  }
  return true;
}
// Room that is certain round the line that joins the two walls (see "the spindle" above GL_BALLS, and above
// GL_BALLS_RHO for a smaller second sphere): how far the point m, which the recipe has just called OUTSIDE, stands
// inside the spindle. Below 0: not inside it. Used while the neighbours are large (rho = 1: t under BALLS_SPINDLE_T;
// rho < 1: delta^2 under 3, which is the same line); for smaller ones the other number is always the larger.
const BALLS_SPINDLE_T = 2;
// (the circle's radius - the distance from the circle's centre, written as the shaders write it)
function ballsSpindle(m, t, rho, hu) {
  if (!hu.on) return -1;
  const q = Math.hypot(m[0], m[1]);
  if (rho === 1) { const s2 = t * t - 1, dz = m[2] - t; return (s2 + q * (0.5 - 2 * s2 - q) - dz * dz) / (0.25 + s2 + Math.hypot(q - 0.25 + s2, dz)); }
  const dz = m[2] - hu.zm;
  return (hu.d2 + q * (2 * hu.a - q) - dz * dz) / (hu.R + Math.hypot(q - hu.a, dz));
}
// The distance the shader hands the ray marcher, in JavaScript (the part that does not depend on the picture: see
// "free" in GL_BALLS). Negative inside a ball. For the checks. With opts.parts it returns both numbers the estimate is the
// smaller of: [the true distance to the nearest ball the search met, the length that is certainly free of balls].
// opts as for ballsInside. (The length that is certainly free is worked out for rho = 1 and for rho <= 1/2 only.)
function ballsEstimate(x, y, z, opts) {
  const o = opts || {}, t = o.t === undefined ? S.k.bt : +o.t, grid = ballsGridId(o.grid === undefined ? S.k.bgrid : o.grid);
  const rounds = o.rounds === undefined ? S.k.bit : Math.round(o.rounds), top = 2 * t;
  const rho = o.rho === undefined ? ballsRho() : +o.rho, r2 = rho * rho, hu = ballsHulls(t, rho), HB = hu.HB, HT = hu.HT;
  // "the rest": how far from a wall the buds reach that do not stand at a whole number (on the top wall of a smaller
  // second sphere: rho^2 HT, for all three grids)
  const restB = grid === 0 ? HB / 2 : grid === 1 ? HB / 3 : HB / 4, restT = rho === 1 ? restB : r2 * HT;
  // (rho < 1: and that rest keeps within rT of the second sphere's centre: see GL_BALLS_RHO)
  const rT = Math.min(rho, 2 * r2 / (1 + Math.sqrt(Math.max(1 - 4 * r2, 0))) + restT);
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
    else if (rt < r2) {
      const s = r2 / Math.max(rt, 1e-300), Wt = [W[0], W[1], W[2] - top], w = r2 / Math.max(dot(Wt, Wt), 1e-300);
      m = [mt[0] * s, mt[1] * s, top + mt[2] * s]; W = [Wt[0] * w, Wt[1] * w, top + Wt[2] * w]; DF *= s;
    } else {
      const cb = Math.hypot(m[0], m[1], hb - HB / 2) - HB / 2, ct = Math.hypot(m[0], m[1], ht - HT / 2) - HT / 2;
      const lo = grid === 2 ? Math.hypot(m[1], hb) : hb, hi = grid === 2 ? Math.hypot(m[1], ht) : ht;
      const hiR = rho === 1 ? hi - restT : Math.max(hi - restT, Math.sqrt(rt) - rT);
      const e = Math.max(Math.min(cb, ct, Math.min(lo - restB, hiR)), ballsSpindle(m, t, rho, hu), 0), L = Math.sqrt(L2);
      const free = e * L / ((L + e) * DF);
      return o.parts ? [best, free] : Math.min(best, free);
    }
  }
  return o.parts ? [-1e-7, -1e-7] : -1e-7;
}
// The start view: the whole chain in the picture, seen from a little above the flat plane so that the buds off the
// flat picture show. { yaw, pitch, dist (at the starting field of view), h (span of the 2D view), room }.
const BALLS_FAR = 40;   // rho < 1: a chain that reaches further than this from the middle is not framed whole
function ballsCam() {
  const w = Math.max(1, stage.clientWidth), h = Math.max(1, stage.clientHeight), asp = w / h, rho = ballsRho();
  if (rho === 1) {
    const r = Math.min(ballsReach(), 4.5);
    return { yaw: -1.25, pitch: 0.5, dist: Math.max(3.3, 3.6 * r / asp), h: Math.max(2.1, 2.25 * r / asp), room: Math.min(r + 0.4, 8) };
  }
  // A smaller second sphere: the neighbours may be larger than the middle ball, so the picture grows taller as well
  // as longer. `tall` is how far it reaches from the middle line: a neighbour's own radius, or the middle ball with
  // the largest bud on its waist (measured on lists of balls for rho <= 1/2: out/r28/dials/NOTES.md). A chain longer
  // than BALLS_FAR (the two spheres touch, or all but) is not framed whole: then the middle ball, its two neighbours
  // and a stretch of what follows are, and ballsTrouble says that the chain goes on.
  const t = ballsT(), p = ballsShare(t), reach = ballsReach(t, rho);
  const whole = reach <= BALLS_FAR, r = whole ? reach : Math.max(4.5, BALLS_K2 * (0.5 + 1.5 * p / 100));
  const tall = Math.max(BALLS_K2 * p / 200, BALLS_K2 / 2 + BALLS_K2 / (4 * t - 1));
  // (room, the Drawing radius the view wants: the whole chain with a little air; for a stretch of an endless chain
  //  so much more that the place where the Drawing radius cuts a ball open lies outside the picture)
  return { yaw: -1.25, pitch: 0.5, dist: Math.max(3.3, 3.6 * r / asp, 3.75 * tall), h: Math.max(2.1, 2.25 * r / asp, 2.4 * tall), room: whole ? r + 0.4 : 2 * r };
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
// What the user should know about the picture as the dials stand, in plain sentences (status, not an error), or ''.
// Where the two spheres touch (at 100 with two equal spheres, at 100 / rho with a smaller second one) the chain is
// endless, in the 2D view as well: nothing the user does shows all of it, so the sentence says what is on the screen
// instead of giving advice that cannot be followed. (The depth: each further ball of the chain costs the search one
// more round, and a point still undecided counts as inside, as in tree.py.)
// Round 28 adds: what the second sphere is while it is not as large as the first (past 100 it has to be smaller), and
// what a depth under BALLS_ROUNDS_FEW does to the picture.
function ballsTrouble() {
  if (!ballsShown()) return '';
  const rho = ballsRho(), t = ballsT(), p = ballsShare(t), out = [], pc = x => dialFmt(+x.toFixed(2));
  if (ballsTouch(S.k.bt, rho)) {
    const what = S.flat ? 'circles' : 'balls';
    // (with a smaller second sphere the chain goes small ball, large ball, small ball, ...: the large ones stand
    //  clear, and it is the small ones and their buds between them that close up; seen on the pictures of round 28)
    const close = rho < 1 ? (S.flat ? ', and the small circles between the large ones stand so close that they read as a band with holes' : ', and the small balls between the large ones stand so close that they read as a bar with round holes')
      : S.flat ? ', and the circles stand so close that they read as one band with holes' : ', and the balls stand so close that they read as one bar with round holes';
    out.push(`At ${rho === 1 ? '100' : pc(p)} the chain never ends, so the picture shows a stretch of it` + (!S.flat && S.k.bgrid === 2 ? '' : close) +
      `; where the depth of the search runs out, the far ${what} and the places where two ${what} kiss come out swollen.`);
  } else if (!S.flat && ballsReach() > S.view.bound) out.push('The chain of balls runs out past the Drawing radius in the View section, so its far ends are not drawn.');
  if (rho < 1) {
    out.push(p > 100 * (1 + 1e-9) ? `Past 100 the second sphere has to be smaller than the first, or the two would cut into each other. It is now ${pc(100 * rho)} % of the first.`
      : `The second sphere is now ${pc(100 * rho)} % of the first. Reset this section puts it back to 100.`);
  }
  if (S.k.bit < BALLS_ROUNDS_FEW) out.push('With so few rounds of the search whole balls are still undecided, and they come out as broken shells.');
  return out.join(' ');
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
// The spindle (added by the fixer of round 27). With large neighbours the two hull balls of diameter H nearly touch
// (at t = 1 they do, where the two unit spheres kiss), and beside that place the room above was far too small: it
// fell off like the square of the distance from the kiss while the nearest ball is as far off as the kiss itself.
// Rays there crept along, ran out of steps and left holes. So a second room is taken, and the larger of the two used.
// The two inversions of the recipe together hold two points of the middle line fixed: z = H and z = 1 / H = 2t - H
// (one point, z = 1, at t = 1). Every circle through both crosses both unit spheres squarely, so each inversion
// carries it onto itself. Take the arcs through both points that reach 1/2 from the line at mid-height z = t: in the
// (distance from the line, z) half-plane, the circle of radius 1/4 + s^2 about (1/4 - s^2, t), s^2 = t^2 - 1. Spun
// round the line they bound a spindle (a ring with no hole at t = 1). Between the two unit spheres the spindle lies
// inside the middle cell, where the recipe says OUTSIDE; the two inversions carry that piece onto the rest of the
// spindle, piece by piece, towards the two fixed points. So no ball reaches into the spindle, for any of the three
// grids, and a point m inside it has the room 1/4 + s^2 - (its distance from that circle's centre).
// One exception, in the 3D picture only (gPix > 0): "free" is not taken below two ray thresholds (one and a quarter
// when the ray takes four fifths of the estimate or more: see the last lines of de). It measures to
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
      float e = max(min(min(cb, ct), min(lo, hi) - rest), 0.0), L = sqrt(L2), s2 = uBT * uBT - 1.0;
      // the spindle round the line that joins the two walls: no ball reaches into it (see the top of this program)
      // (written so that nothing large is taken from something large: beside the kiss the room is as small as the
      //  distance from the middle line, and single precision would lose it in 1/4 - 1/4)
      float rho = length(z.xy), dz = z.z - uBT;
      if (uBT < ${BALLS_SPINDLE_T.toFixed(1)}) e = max(e, (s2 + rho * (0.5 - 2.0 * s2 - rho) - dz * dz) / (0.25 + s2 + length(vec2(rho - 0.25 + s2, dz))));
      free = e * L / ((L + e) * DF);
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // undecided when the rounds ran out: that counts as inside, a hair deep
  // (the hold: two thresholds while a ray takes half of the estimate or less, so that it goes on a threshold a step;
  //  with a longer ray step less, down to one and a quarter)
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
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
// The same program for a second sphere that is smaller than the first (round 28): uBRho = rho < 1, its radius. It is
// a text of its own, with its own key in the cache ('balls2': sceneWant in 40-render.js), so that the program above
// stays exactly what it was and every picture with two equal spheres stays the same to the pixel.
// What differs, and why (each line was checked with numbers on lists of balls: out/r28/dials/mk/derive.py):
//   The second inversion has the scale factor rho^2 / |m - (0, 0, top)|^2 (for DF and for W).
//   The two inversions together hold two points of the middle line fixed: z1 and z2 = 1 / z1, where
//   z1 + z2 = s = top + (1 - rho^2) / top (s = 2 exactly when the two spheres touch). Nothing that grows on the
//   bottom wall reaches higher than HB = z1 and nothing on the top wall hangs lower than HT = top - z2
//   (HB = 1 / (top - HT), HT = rho^2 / (top - HB)). So the two hull balls now differ: diameter HB standing on the
//   bottom wall, diameter HT hanging from the top wall, each at the nearest whole number.
//   "The rest" on the bottom wall is as it was, with HB (HB / 2, HB / 3, a tube of HB / 4). On the top wall a bud
//   that does not stand at a whole number is the image, by the second sphere's inversion, of a hull at a whole
//   number at distance d >= 1 from the sphere's centre, which makes it rho^2 HT / d^2 across; images of images are
//   no larger while rho <= 1/2. So the rest there is rho^2 HT, for all three grids.
//   The top wall is no longer covered by the second sphere and its slid copies, so most of it is bare: nothing
//   grows there, and a rest that lay over the whole wall would leave the ray no room beside a bare wall (it crept
//   along the large neighbours in steps of a pixel, and the slope of their skin came out in faint bands). All that
//   grows on the top wall lies inside the second sphere, and the buds of the rest touch the wall no further than
//   x = (1 - sqrt(1 - 4 rho^2)) / 2 from its centre (x = rho^2 / (1 - x): a bud is the image of one that stands at
//   least 1 - x from the centre). So the rest is the part of its slab within rT = min(rho, x + rho^2 HT) of the
//   centre, and a point is at least max(distance to the slab, distance to that ball) away from it.
//   The spindle. Every circle through z1 and z2 still crosses both spheres squarely, so the argument above GL_BALLS
//   holds for the spindle of any such arc, provided the whole of it lies in the middle cell and between the two
//   walls. With two equal spheres the arc that reaches 1/2 from the line at mid-height does. With a smaller second
//   sphere that spindle can bulge through the top wall beside the second sphere (found with numbers: at 300 %
//   with rho = 1/6 it holds whole balls). So the arc taken reaches w = min(1/2, top - zm + rho) at mid-height
//   zm = s / 2: at the second value it just touches the top wall, on the circle where the second sphere meets it.
//   In the half-plane (distance from the line, z) it is the circle about (a, zm) with radius R, a = (w^2 - d2) / 2w,
//   R = (w^2 + d2) / 2w, d2 = ((z2 - z1) / 2)^2; a point inside has the room R - (its distance from that centre).
//   (All of it is written from D = s - 2 = (top - 1 - rho)(top - 1 + rho) / top, so that nothing large is taken from
//   something large beside the place where the two spheres touch.)
const GL_BALLS_RHO = `
const bool ORBIT_SCENE = false;
uniform float uBT, uBRho; uniform int uBGrid;
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
  float top = 2.0 * uBT, rr = uBRho * uBRho;
  // the two fixed points on the middle line, the two hull balls and the spindle (see above this program)
  float sD = max(top - 1.0 - uBRho, 0.0) * (top - 1.0 + uBRho) / top, sQ = sqrt(sD * (sD + 4.0));
  float HB = 1.0 / (1.0 + 0.5 * (sD + sQ)), HT = rr / (top - HB), zm = 1.0 + 0.5 * sD, d2 = 0.25 * sD * (sD + 4.0);
  float restB = uBGrid == 0 ? 0.5 * HB : uBGrid == 1 ? HB / 3.0 : 0.25 * HB, restT = rr * HT;
  float rT = min(uBRho, 2.0 * rr / (1.0 + sqrt(max(1.0 - 4.0 * rr, 0.0))) + restT);
  float sw = min(0.5, top - zm + uBRho), sa = (sw * sw - d2) / (2.0 * sw), sR = (sw * sw + d2) / (2.0 * sw);
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
    } else if (rt < rr){
      float s = rr / max(rt, 1e-20);
      vec3 Wt = vec3(W.xy, W.z - top);
      z = vec3(0.0, 0.0, top) + zt * s; W = vec3(0.0, 0.0, top) + Wt * (rr / max(dot(Wt, Wt), 1e-20)); DF *= s;
    } else {
      // OUTSIDE, for good. How much room is certain here (see above this program, and the top of GL_BALLS).
      float cb = length(vec3(z.xy, hb - 0.5 * HB)) - 0.5 * HB, ct = length(vec3(z.xy, ht - 0.5 * HT)) - 0.5 * HT;
      float lo = uBGrid == 2 ? length(vec2(z.y, hb)) : hb, hi = uBGrid == 2 ? length(vec2(z.y, ht)) : ht;
      float e = max(min(min(cb, ct), min(lo - restB, max(hi - restT, sqrt(rt) - rT))), 0.0), L = sqrt(L2);
      // the spindle round the line that joins the two walls: no ball reaches into it
      // (written so that nothing large is taken from something large: R^2 - a^2 = d2)
      float q = length(z.xy), dz = z.z - zm;
      if (d2 < 3.0) e = max(e, (d2 + q * (2.0 * sa - q) - dz * dz) / (sR + length(vec2(q - sa, dz))));
      free = e * L / ((L + e) * DF);
      decided = true; break;
    }
  }
  // In the 3D view the count is reported 8 rounds high, as the other Kleinian program does (see kde).
  gIt = uFlat > 0.5 ? it : it + 8.0;
  // undecided when the rounds ran out: that counts as inside, a hair deep
  // (the hold: two thresholds while a ray takes half of the estimate or less, so that it goes on a threshold a step;
  //  with a longer ray step less, down to one and a quarter)
  float d = !decided ? -1e-7 : inside ? best : min(best, max(free, clamp(1.0 / max(uStepK, 0.05), 1.25, 2.0) * uDetail * gPix));
  // (the trap solid: as in GL_BALLS, the page never asks this group for one)
#if TRAP_SOLIDS
  if (trapSolid && uTrapSolid < 1.5) bestT = min(bestT, gPix > 0.0 ? max(abs(d), 2.0 * uDetail * gPix) : 0.3);
  gOnTrap = trapSolid && (uTrapSolid < 1.5 || bestT < d);
  if (gOnTrap) d = bestT;
#endif
  if (d <= 0.0) gEsc = 0.0;
  return d;
}`;
